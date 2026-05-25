"""Number platform for the Maico KWL integration (writable numeric registers)."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MaicoEntity
from .register_defs import NUMBER, REGISTERS_BY_KEY, RegisterDef


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities(
        MaicoNumber(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == NUMBER
    )


class MaicoNumber(MaicoEntity, NumberEntity):
    """A writable numeric Maico register."""

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        if reg.unit:
            self._attr_native_unit_of_measurement = reg.unit
        if reg.device_class:
            self._attr_device_class = NumberDeviceClass(reg.device_class)
        if reg.native_min is not None:
            self._attr_native_min_value = reg.native_min
        if reg.native_max is not None:
            self._attr_native_max_value = reg.native_max
        if reg.native_step is not None:
            self._attr_native_step = reg.native_step

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.hub.write(self._reg.address, self._reg.encode(value))
        await self.coordinator.async_request_refresh()
