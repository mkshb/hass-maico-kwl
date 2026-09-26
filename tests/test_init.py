"""Tests for setting up and unloading a config entry."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.maico_kwl.const import CONF_DISCOVERY
from custom_components.maico_kwl.discovery import async_discover
from custom_components.maico_kwl.modbus_hub import MaicoModbusHub

from .conftest import HOST, PORT, SLAVE, FakeDevice
from .helpers import setup_entry


async def _discovery_reads(device: FakeDevice) -> int:
    """Number of requests a discovery of the simulated unit takes."""
    hub = MaicoModbusHub(HOST, PORT, SLAVE)
    await hub.connect()
    await async_discover(hub)
    await hub.close()
    reads, device.reads = device.reads, 0
    return reads


async def test_setup_and_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The entry loads, keeps one connection and closes it on unload."""
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED

    runtime = config_entry.runtime_data
    assert runtime.coordinator.data["temp_room"] == 21.5
    assert device.open_connections == 1

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert device.open_connections == 0


async def test_setup_retry_when_unreachable(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """An unreachable unit makes HA retry the setup."""
    device.online = False
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert config_entry.reason == "Cannot connect to the Maico KWL at 192.0.2.10:502"
    assert device.open_connections == 0


async def test_setup_retry_when_connection_drops_during_discovery(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A connection loss while probing aborts discovery instead of pruning."""
    device.fail_after_reads = 10
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert config_entry.reason.startswith("Discovering the registers")
    # Discovery stopped at the first failed probe.
    assert device.reads == 10
    assert device.open_connections == 0


async def test_setup_retry_when_first_refresh_fails(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A failing first poll retries the setup and closes the connection."""
    device.fail_after_reads = await _discovery_reads(device)
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert device.open_connections == 0


async def test_setup_retry_when_nothing_discovered(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A device that rejects every register is not set up."""
    device.absent = set(range(0, 1000))
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert config_entry.reason == "The unit did not answer any known Maico KWL register"
    assert device.open_connections == 0


async def test_setup_recovers_after_retry(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Retries do not pile up connections, and the entry loads once back."""
    device.online = False
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY

    device.online = True
    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert device.open_connections == 1


# --- Stored discovery -----------------------------------------------------


async def _reload(hass: HomeAssistant, entry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()


async def test_discovery_is_stored_and_reused(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The first setup stores the discovery, later setups only poll."""
    await setup_entry(hass, config_entry)
    cache = config_entry.data[CONF_DISCOVERY]
    assert "temp_room" in cache["present"]
    assert "brine_pump_state" not in cache["present"]
    assert "brine_pump_state" in cache["probed"]

    device.reads = 0
    await _reload(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED
    blocks = len(config_entry.runtime_data.coordinator._blocks)
    assert device.reads == blocks  # first poll only, no probing
    # Write-only registers are resolved from the stored readable ones.
    assert "error_reset" in config_entry.runtime_data.coordinator.present


async def test_discovery_runs_again_for_new_registers(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A stored discovery that lacks a register of this version is redone."""
    await setup_entry(hass, config_entry)
    cache = config_entry.data[CONF_DISCOVERY]
    old = {
        "version": cache["version"],
        "probed": [key for key in cache["probed"] if key != "clock_deviation"],
        "present": [key for key in cache["present"] if key != "clock_deviation"],
    }
    hass.config_entries.async_update_entry(
        config_entry, data={**config_entry.data, CONF_DISCOVERY: old}
    )
    await hass.async_block_till_done()  # the data change reloads the entry

    assert config_entry.state is ConfigEntryState.LOADED
    assert "clock_deviation" in config_entry.runtime_data.coordinator.present
    assert "clock_deviation" in config_entry.data[CONF_DISCOVERY]["present"]


async def test_stored_discovery_ignores_unknown_keys(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Keys of registers that no longer exist are dropped."""
    await setup_entry(hass, config_entry)
    cache = dict(config_entry.data[CONF_DISCOVERY])
    cache["present"] = [*cache["present"], "removed_register"]
    hass.config_entries.async_update_entry(
        config_entry, data={**config_entry.data, CONF_DISCOVERY: cache}
    )
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert "removed_register" not in config_entry.runtime_data.coordinator.present


async def test_empty_stored_discovery_probes_again(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry,
        data={**config_entry.data, CONF_DISCOVERY: {"probed": [], "present": []}},
    )
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED
    assert "temp_room" in config_entry.data[CONF_DISCOVERY]["present"]


async def test_discovery_of_an_older_version_runs_again(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A stored discovery without the filter check is redone once."""
    device.registers[656] = 0  # no outdoor filter fitted
    await setup_entry(hass, config_entry)
    cache = config_entry.data[CONF_DISCOVERY]
    assert "filter_remaining_outdoor" not in cache["present"]

    old = {
        "probed": cache["probed"],
        "present": [*cache["present"], "filter_remaining_outdoor"],
    }
    hass.config_entries.async_update_entry(
        config_entry, data={**config_entry.data, CONF_DISCOVERY: old}
    )
    await hass.async_block_till_done()  # the data change reloads the entry

    assert config_entry.state is ConfigEntryState.LOADED
    present = config_entry.runtime_data.coordinator.present
    assert "filter_remaining_outdoor" not in present
    assert config_entry.data[CONF_DISCOVERY]["version"] == 2
