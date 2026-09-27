"""The Maico KWL integration."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
# Defined in http/__init__ up to HA 2026.7 and re-exported there from
# http/server since 2026.8, without marking it as exported for mypy.
from homeassistant.components.http import StaticPathConfig  # type: ignore[attr-defined]
from homeassistant.const import ATTR_RESTORED
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
    active_accessories,
    async_discover,
    cache_data,
    derive_profile,
    present_from_cache,
    registers_in_use,
)
from .entity import ORPHANED
from .issues import async_delete_issues, async_update_issues
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import REGISTERS_BY_KEY
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

FRONTEND_URL = f"/{DOMAIN}/frontend"
FRONTEND_DIR = Path(__file__).parent / "frontend"
CARD_LOADER = "maico-kwl-card.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the actions, so they exist even while no unit is loaded."""
    async_setup_services(hass)
    await _async_register_card(hass)
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the dashboard card and load it in every frontend.

    The loader is tiny and served without cache headers, and its URL carries a
    hash of its content, so a browser never keeps running an old card. The
    chunks it loads have a content hash in their names and are cached.
    """
    if "frontend" not in hass.config.components:
        return
    loader = FRONTEND_DIR / CARD_LOADER
    try:
        digest = await hass.async_add_executor_job(_content_hash, loader)
    except OSError as err:
        # The card is optional: a partial install must not stop the unit.
        _LOGGER.warning("Dashboard card not available, %s is missing: %s", loader, err)
        return
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(f"{FRONTEND_URL}/{CARD_LOADER}", str(loader), False),
            StaticPathConfig(FRONTEND_URL, str(FRONTEND_DIR), True),
        ]
    )
    add_extra_js_url(hass, f"{FRONTEND_URL}/{CARD_LOADER}?v={digest}")


def _content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


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
    feeder: BusFeeder | None = None
    try:
        coordinator = await _async_discover_and_refresh(
            hass, entry, hub, scan_interval
        )

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
    except BaseException:
        # Close on any failure, including cancellation. pymodbus reconnects in
        # the background, so an unclosed client would keep a connection open
        # for every retry of the setup. HA does not unload an entry whose
        # setup failed, so a started feeder would keep writing as well.
        if feeder is not None:
            feeder.async_stop()
        await hub.close()
        raise

    _async_disable_orphaned_entities(hass, entry)

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
    Registers of accessories that are not in use are left out.
    """
    if not await hub.connect():
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="cannot_connect",
            translation_placeholders={"host": hub.host, "port": str(hub.port)},
        )

    present = present_from_cache(entry.data.get(CONF_DISCOVERY))
    if present is None:
        try:
            present, accessories = await async_discover(hub)
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
            entry,
            data={**entry.data, CONF_DISCOVERY: cache_data(present, accessories)},
        )

    present = registers_in_use(
        present, active_accessories(entry.data[CONF_DISCOVERY], entry.options)
    )
    profile = derive_profile(present)
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
def _async_disable_orphaned_entities(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Disable the entities this setup no longer creates.

    E.g. registers a rediscovery did not find, accessories no longer selected,
    or the "sent" sensor of a bus input without a source. They would stay
    unavailable. Disabled rather than removed, so their names, areas and
    entity ids are still there when they come back (see
    async_add_maico_entities); only entities that were enabled are marked, so
    ones the user or the defaults disabled stay as they are.
    A platform whose setup failed recorded nothing, so its entities are kept.
    """
    runtime = entry.runtime_data
    ent_reg = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
        if (
            reg_entry.domain in runtime.platforms
            and reg_entry.unique_id not in runtime.unique_ids
            and reg_entry.disabled_by is None
        ):
            ent_reg.async_update_entity_options(
                reg_entry.entity_id, DOMAIN, {ORPHANED: True}
            )
            ent_reg.async_update_entity(
                reg_entry.entity_id,
                disabled_by=er.RegistryEntryDisabler.INTEGRATION,
            )
            # The placeholder HA leaves when an entity is removed would show
            # it as unavailable until the next restart.
            state = hass.states.get(reg_entry.entity_id)
            if state is not None and state.attributes.get(ATTR_RESTORED):
                hass.states.async_remove(reg_entry.entity_id)


async def _async_update_listener(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Reload the entry when options (e.g. scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
