"""The Maico KWL integration."""

from __future__ import annotations

import logging

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
from .coordinator import MaicoConfigEntry, MaicoCoordinator, MaicoRuntimeData
from .discovery import async_discover
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import REGISTERS_BY_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: MaicoConfigEntry) -> bool:
    """Set up Maico KWL from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    slave = entry.data.get(CONF_SLAVE, DEFAULT_SLAVE)
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    hub = MaicoModbusHub(host, port, slave)
    try:
        coordinator = await _async_discover_and_refresh(hass, hub, scan_interval)
    except BaseException:
        # Close on any failure, including cancellation. pymodbus reconnects in
        # the background, so an unclosed client would keep a connection open
        # for every retry of the setup.
        await hub.close()
        raise

    feeds = [
        (REGISTERS_BY_KEY[reg_key], entity_id)
        for reg_key, conf_key, _device_class in BUS_FEEDS
        if (entity_id := entry.options.get(conf_key))
        and reg_key in coordinator.present
    ]
    feeder = BusFeeder(hass, entry, hub, feeds)
    await feeder.async_start()

    entry.runtime_data = MaicoRuntimeData(
        hub=hub, coordinator=coordinator, feeder=feeder
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_discover_and_refresh(
    hass: HomeAssistant, hub: MaicoModbusHub, scan_interval: int
) -> MaicoCoordinator:
    """Connect, discover the present registers and run the first poll."""
    if not await hub.connect():
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="cannot_connect",
            translation_placeholders={"host": hub.host, "port": str(hub.port)},
        )

    try:
        present, profile = await async_discover(hub)
    except MaicoModbusError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="discovery_failed",
            translation_placeholders={"error": str(err)},
        ) from err

    if not present:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="no_registers"
        )

    coordinator = MaicoCoordinator(hass, hub, present, profile, scan_interval)
    await coordinator.async_config_entry_first_refresh()
    return coordinator


async def async_unload_entry(hass: HomeAssistant, entry: MaicoConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime = entry.runtime_data
        runtime.feeder.async_stop()
        await runtime.hub.close()
    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Reload the entry when options (e.g. scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
