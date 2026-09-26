"""Tests for setting up and unloading a config entry."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

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
