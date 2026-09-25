"""Tests for setting up and unloading a config entry."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.maico_kwl.register_defs import REGISTERS

from .conftest import FakeDevice
from .helpers import setup_entry

# Discovery reads each register once, except the write-only ones that inherit
# their presence from a sibling.
PROBE_READS = sum(1 for reg in REGISTERS if reg.probe_via is None)


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
    assert device.open_connections == 0


async def test_setup_retry_when_connection_drops_during_discovery(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A connection loss while probing aborts discovery instead of pruning."""
    device.fail_after_reads = 10
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    # Discovery stopped at the first failed probe.
    assert device.reads == 10
    assert device.open_connections == 0


async def test_setup_retry_when_first_refresh_fails(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A failing first poll retries the setup and closes the connection."""
    device.fail_after_reads = PROBE_READS
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
