"""Sensor platform for the Maico KWL integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MaicoEntity
from .register_defs import SENSOR, REGISTERS_BY_KEY, RegisterDef


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities(
        MaicoSensor(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == SENSOR
    )


class MaicoSensor(MaicoEntity, SensorEntity):
    """A read-only Maico register exposed as a sensor."""

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        if reg.unit:
            self._attr_native_unit_of_measurement = reg.unit
        if reg.device_class:
            self._attr_device_class = SensorDeviceClass(reg.device_class)
        if reg.state_class:
            self._attr_state_class = SensorStateClass(reg.state_class)
        if reg.options is not None:
            self._attr_options = list(reg.options.values())

    @property
    def native_value(self):
        value = self._value
        if value is None:
            return None
        if self._reg.options is not None:
            return self._reg.label_for(int(value))
        return value
