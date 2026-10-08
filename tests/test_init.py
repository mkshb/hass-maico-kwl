"""Tests for setting up and unloading a config entry."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.maico_kwl.const import (
    CONF_DISCOVERY,
    CONF_HOST,
    CONF_PORT,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    CONF_SLAVE,
    DOMAIN,
)
from custom_components.maico_kwl.coordinator import build_blocks
from custom_components.maico_kwl.discovery import async_discover
from custom_components.maico_kwl.register_defs import IDENTITY_RANGES, REGISTERS_BY_KEY

from .conftest import HOST, PORT, FakeDevice, fake_hub
from .helpers import CELSIUS, setup_entry


async def _discovery_reads(device: FakeDevice) -> int:
    """Number of requests a discovery of the simulated unit takes."""
    await async_discover(fake_hub(device))
    await device.clients.pop().close()
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
    assert config_entry.reason.startswith(
        "Cannot connect to the Maico KWL at 192.0.2.10:502; it accepts only one"
    )
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
    assert config_entry.reason == (
        "The device at the configured address does not look like a Maico KWL: "
        "none of its registers 108, 109, 550 to 554 and 650 can be read"
    )
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


async def test_entries_of_one_unit_share_the_connection(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The unit accepts one connection: a second Modbus address uses the same."""
    device.max_connections = 1
    other = MockConfigEntry(
        domain=DOMAIN,
        title=f"Maico KWL ({HOST})",
        data={CONF_HOST: HOST, CONF_PORT: PORT, CONF_SLAVE: 11},
    )
    await setup_entry(hass, config_entry)
    await setup_entry(hass, other)
    assert config_entry.state is ConfigEntryState.LOADED
    assert other.state is ConfigEntryState.LOADED
    assert len(device.clients) == 1

    # Open until the last entry on it unloads.
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert device.open_connections == 1
    assert other.runtime_data.coordinator.last_update_success
    assert await hass.config_entries.async_unload(other.entry_id)
    assert device.open_connections == 0


async def test_setup_error_when_connection_used_with_other_settings(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """E.g. a Modbus hub in YAML that reaches the unit over other link settings."""
    with patch(
        "custom_components.maico_kwl.async_get_unit",
        side_effect=HomeAssistantError("in use over other settings"),
    ):
        await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_ERROR
    assert config_entry.reason == (
        "The Modbus connection to the Maico KWL is already used with other "
        "settings: in use over other settings"
    )
    assert not device.clients


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
    identity = len(build_blocks([REGISTERS_BY_KEY[key] for key in IDENTITY_RANGES]))
    assert device.reads == identity + blocks  # identity check and first poll only
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
    """A stored discovery without the accessories is redone once."""
    device.registers[656] = 0  # no outdoor filter fitted
    await setup_entry(hass, config_entry)
    cache = config_entry.data[CONF_DISCOVERY]
    assert "filter_remaining_outdoor" in cache["present"]
    assert "outdoor_filter" not in cache["accessories"]
    assert "room_filter" in cache["accessories"]
    present = config_entry.runtime_data.coordinator.present
    assert "filter_remaining_outdoor" not in present
    assert "filter_remaining_room" in present

    old = {"probed": cache["probed"], "present": cache["present"]}
    hass.config_entries.async_update_entry(
        config_entry, data={**config_entry.data, CONF_DISCOVERY: old}
    )
    await hass.async_block_till_done()  # the data change reloads the entry

    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.data[CONF_DISCOVERY]["version"] == 2
    assert "outdoor_filter" not in config_entry.data[CONF_DISCOVERY]["accessories"]
    assert "filter_remaining_outdoor" not in config_entry.runtime_data.coordinator.present


async def test_failed_platform_keeps_its_entities(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A platform that raises during setup must not lose its registry entries.

    They carry the user's names and areas; the cleanup only removes entities
    of platforms that set up completely.
    """
    await setup_entry(hass, config_entry)
    ent_reg = er.async_get(hass)

    def entity_ids(domain: str) -> set[str]:
        return {
            e.entity_id
            for e in er.async_entries_for_config_entry(ent_reg, config_entry.entry_id)
            if e.domain == domain
        }

    switches = entity_ids("switch")
    sensors = entity_ids("sensor")
    assert switches
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    with patch(
        "custom_components.maico_kwl.switch.async_setup_entry",
        side_effect=RuntimeError("platform failed"),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    assert entity_ids("switch") == switches
    assert entity_ids("sensor") == sensors


async def test_failed_setup_after_discovery_closes_the_connection(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """HA does not unload a failed entry, so the setup has to close the hub."""
    with patch(
        "custom_components.maico_kwl.BusFeeder.async_start",
        side_effect=RuntimeError("boom"),
    ):
        await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_ERROR
    assert device.open_connections == 0


async def test_failed_platform_setup_stops_the_bus_feed(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A feeder started before the failure must not keep writing."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}
    )
    with patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        side_effect=RuntimeError("boom"),
    ):
        await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_ERROR
    assert device.open_connections == 0
    assert device.writes == [(707, [215])]  # written once while starting

    hass.states.async_set("sensor.room", "22.0", CELSIUS)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=10))
    await hass.async_block_till_done()
    assert device.writes == [(707, [215])]


async def test_setup_retry_when_another_device_answers(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Nothing is probed, stored or written; retried in case it is temporary."""
    device.registers[550] = 42
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert config_entry.reason == (
        "The device at the configured address does not look like a Maico KWL: "
        "register 550 reads 42, expected 0 to 5"
    )
    assert CONF_DISCOVERY not in config_entry.data
    assert not device.writes
    assert device.open_connections == 0


@pytest.mark.parametrize(
    "damage",
    [
        "not a dict",
        ["a", "list"],
        {"present": 5},
        {"accessories": "enocean"},
        {"probed": [1, 2]},
        {"version": 3},  # written by a newer version, e.g. before a downgrade
    ],
)
async def test_damaged_or_newer_discovery_is_probed_again(
    hass: HomeAssistant, device: FakeDevice, config_entry, damage
) -> None:
    """Instead of failing the setup or reading it with the wrong meaning."""
    await setup_entry(hass, config_entry)
    cache = config_entry.data[CONF_DISCOVERY]
    stored = {**cache, **damage} if isinstance(damage, dict) else damage
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    hass.config_entries.async_update_entry(
        config_entry, data={**config_entry.data, CONF_DISCOVERY: stored}
    )
    device.reads = 0
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.data[CONF_DISCOVERY] == cache  # probed and stored anew
    identity = len(build_blocks([REGISTERS_BY_KEY[key] for key in IDENTITY_RANGES]))
    assert device.reads > identity + len(config_entry.runtime_data.coordinator._blocks)
