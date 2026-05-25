"""Button platform for the Maico KWL integration (write-command registers)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MaicoEntity
from .register_defs import BUTTON, REGISTERS_BY_KEY


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities(
        MaicoButton(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == BUTTON
    )


class MaicoButton(MaicoEntity, ButtonEntity):
    """A momentary command: writes a fixed value to a register on press."""

    async def async_press(self) -> None:
        await self.coordinator.hub.write(
            self._reg.address, self._reg.encode(self._reg.press_value)
        )
        await self.coordinator.async_request_refresh()
