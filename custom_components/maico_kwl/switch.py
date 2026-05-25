"""Switch platform for the Maico KWL integration (writable 0/1 registers)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MaicoEntity
from .register_defs import SWITCH, REGISTERS_BY_KEY


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities(
        MaicoSwitch(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == SWITCH
    )


class MaicoSwitch(MaicoEntity, SwitchEntity):
    """A writable 0/1 Maico register."""

    @property
    def is_on(self) -> bool | None:
        value = self._value
        return None if value is None else bool(value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.hub.write(self._reg.address, self._reg.encode(1))
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.hub.write(self._reg.address, self._reg.encode(0))
        await self.coordinator.async_request_refresh()
