"""Helpers shared by the tests."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.maico_kwl.const import DOMAIN


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add the entry to HA and set it up."""
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
