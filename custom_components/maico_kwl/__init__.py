"""The Maico KWL integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .bus_feed import BusFeeder
from .const import (
    BUS_FEEDS,
    CONF_DISCOVERY,
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
from .discovery import (
    async_discover,
    cache_data,
    derive_profile,
    present_from_cache,
)
from .issues import async_delete_issues, async_update_issues
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import REGISTERS_BY_KEY
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the actions, so they exist even while no unit is loaded."""
    async_setup_services(hass)
    return True


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
        coordinator = await _async_discover_and_refresh(
            hass, entry, hub, scan_interval
        )
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
    _async_remove_orphaned_entities(hass, entry)

    async_update_issues(hass, entry)
    entry.async_on_unload(
        coordinator.async_add_listener(lambda: async_update_issues(hass, entry))
    )
    entry.async_on_unload(lambda: async_delete_issues(hass, entry))
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_discover_and_refresh(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    hub: MaicoModbusHub,
    scan_interval: int,
) -> MaicoCoordinator:
    """Connect, find the present registers and run the first poll.

    The registers come from the discovery stored in the entry; the unit is
    only probed when there is none (first setup, after reconfigure or a
    rediscovery request) or when this version knows registers it lacks.
    """
    if not await hub.connect():
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="cannot_connect",
            translation_placeholders={"host": hub.host, "port": str(hub.port)},
        )

    present = present_from_cache(entry.data.get(CONF_DISCOVERY))
    if present is not None:
        profile = derive_profile(present)
    else:
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
        # Stored before the update listener is added, so no reload follows.
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_DISCOVERY: cache_data(present)}
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


@callback
def _async_remove_orphaned_entities(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Remove entities this setup no longer creates.

    E.g. registers a rediscovery did not find again, or the "sent" sensor of a
    bus input whose source entity was removed. They would stay unavailable.
    """
    ent_reg = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
        if reg_entry.unique_id not in entry.runtime_data.unique_ids:
            ent_reg.async_remove(reg_entry.entity_id)


async def _async_update_listener(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Reload the entry when options (e.g. scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
