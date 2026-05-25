"""The Maico KWL integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .bus_feed import BusFeeder
from .const import (
    BUS_FEEDS,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import MaicoCoordinator
from .discovery import async_discover
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import REGISTERS_BY_KEY

_LOGGER = logging.getLogger(__name__)


@dataclass
class MaicoRuntimeData:
    """Per-entry runtime objects."""

    hub: MaicoModbusHub
    coordinator: MaicoCoordinator
    feeder: BusFeeder


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maico KWL from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    slave = entry.data.get(CONF_SLAVE, DEFAULT_SLAVE)
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    hub = MaicoModbusHub(host, port, slave)
    if not await hub.connect():
        raise ConfigEntryNotReady(f"Cannot connect to Maico KWL at {host}:{port}")

    try:
        present, profile = await async_discover(hub)
    except MaicoModbusError as err:
        await hub.close()
        raise ConfigEntryNotReady(f"Discovery failed: {err}") from err

    if not present:
        await hub.close()
        raise ConfigEntryNotReady("No Maico registers discovered on the device")

    coordinator = MaicoCoordinator(hass, hub, present, profile, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    feeds = [
        (REGISTERS_BY_KEY[reg_key], entity_id)
        for reg_key, conf_key, _device_class in BUS_FEEDS
        if (entity_id := entry.options.get(conf_key)) and reg_key in present
    ]
    feeder = BusFeeder(hass, hub, feeds)
    await feeder.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = MaicoRuntimeData(
        hub=hub, coordinator=coordinator, feeder=feeder
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime: MaicoRuntimeData = hass.data[DOMAIN].pop(entry.entry_id)
        runtime.feeder.async_stop()
        await runtime.hub.close()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options (e.g. scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
