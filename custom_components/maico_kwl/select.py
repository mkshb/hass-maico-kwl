"""Select platform for the Maico KWL integration (writable enum registers)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MaicoEntity
from .register_defs import SELECT, REGISTERS_BY_KEY, RegisterDef


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities(
        MaicoSelect(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == SELECT
    )


class MaicoSelect(MaicoEntity, SelectEntity):
    """A writable enum Maico register."""

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        self._attr_options = list(reg.options.values())

    @property
    def current_option(self) -> str | None:
        value = self._value
        if value is None:
            return None
        return self._reg.label_for(int(value))

    async def async_select_option(self, option: str) -> None:
        raw = self._reg.raw_for_label(option)
        if raw is None:
            return
        await self.coordinator.hub.write(self._reg.address, self._reg.encode(raw))
        await self.coordinator.async_request_refresh()
