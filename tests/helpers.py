"""Helpers shared by the tests."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.maico_kwl.const import DOMAIN, REFRESH_AFTER_WRITE

# Attributes of bus feed sources in the unit of their register.
CELSIUS = {"unit_of_measurement": "°C"}
PERCENT = {"unit_of_measurement": "%"}
PPM = {"unit_of_measurement": "ppm"}


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add the entry to HA (unless already added) and set it up."""
    if hass.config_entries.async_get_entry(entry.entry_id) is None:
        entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def entity_id(
    hass: HomeAssistant, entry: MockConfigEntry, platform: str, key: str
) -> str:
    """Look up the entity id of a register entity by its unique id."""
    eid = er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{entry.entry_id}_{key}"
    )
    assert eid is not None, f"no {platform} entity for {key}"
    return eid


async def refresh_after_write(hass: HomeAssistant) -> None:
    """Let the delayed refresh after a write run."""
    async_fire_time_changed(
        hass, dt_util.utcnow() + timedelta(seconds=REFRESH_AFTER_WRITE + 1)
    )
    await hass.async_block_till_done()
