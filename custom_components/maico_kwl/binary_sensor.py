"""Binary sensor platform for the Maico KWL integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .entity import MaicoEntity
from .register_defs import BINARY_SENSOR, REGISTERS_BY_KEY, RegisterDef


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    entities: list[BinarySensorEntity] = [
        MaicoBinarySensor(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == BINARY_SENSOR
    ]
    # Derived "problem" sensor from the fault code register, if present.
    if "fault_code" in coordinator.present:
        entities.append(MaicoProblemSensor(coordinator, entry))
    async_add_entities(entities)


class MaicoBinarySensor(MaicoEntity, BinarySensorEntity):
    """A read-only 0/1 Maico register exposed as a binary sensor."""

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        if reg.device_class:
            self._attr_device_class = BinarySensorDeviceClass(reg.device_class)

    @property
    def is_on(self) -> bool | None:
        value = self._value
        return None if value is None else bool(value)


class MaicoProblemSensor(CoordinatorEntity, BinarySensorEntity):
    """On when the device reports a non-zero fault code."""

    _attr_has_entity_name = True
    _attr_translation_key = "problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_problem"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            name=entry.title or DEFAULT_NAME,
            model=coordinator.profile.get("model", DEFAULT_NAME),
        )

    @property
    def available(self) -> bool:
        return super().available and "fault_code" in self.coordinator.data

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get("fault_code")
        return None if value is None else value != 0
