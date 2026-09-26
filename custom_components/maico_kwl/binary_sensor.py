"""Binary sensor platform for the Maico KWL integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MaicoConfigEntry
from .entity import MaicoEntity
from .register_defs import BINARY_SENSOR, BIT_SENSORS, REGISTERS_BY_KEY, RegisterDef

# Read-only: data comes from the coordinator, no per-entity limit needed.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[BinarySensorEntity] = [
        MaicoBinarySensor(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == BINARY_SENSOR
    ]
    # Derived "problem" sensor from the fault code register, if present.
    if "fault_code" in coordinator.present:
        entities.append(MaicoProblemSensor(coordinator, entry))
    # Single bits of the fault and notice codes.
    entities.extend(
        MaicoBitSensor(coordinator, entry, REGISTERS_BY_KEY[reg_key], slug, dev_class)
        for reg_key, slug, dev_class in BIT_SENSORS
        if reg_key in coordinator.present
    )
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


class MaicoProblemSensor(MaicoEntity, BinarySensorEntity):
    """On when the device reports a non-zero fault code."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry: MaicoConfigEntry) -> None:
        # Device info and availability come from the fault code register.
        super().__init__(coordinator, entry, REGISTERS_BY_KEY["fault_code"])
        self._attr_unique_id = f"{entry.entry_id}_problem"
        self._attr_translation_key = "problem"

    @property
    def is_on(self) -> bool | None:
        value = self._value
        return None if value is None else value != 0


class MaicoBitSensor(MaicoEntity, BinarySensorEntity):
    """On while one bit of a bitfield register is set."""

    def __init__(
        self,
        coordinator,
        entry: MaicoConfigEntry,
        reg: RegisterDef,
        slug: str,
        device_class: str | None,
    ) -> None:
        super().__init__(coordinator, entry, reg)
        self._bit = next(bit for bit, name in reg.bits.items() if name == slug)
        self._attr_unique_id = f"{entry.entry_id}_{slug}"
        self._attr_translation_key = slug
        self._attr_entity_category = None
        if device_class:
            self._attr_device_class = BinarySensorDeviceClass(device_class)

    @property
    def is_on(self) -> bool | None:
        value = self._value
        return None if value is None else bool(int(value) >> self._bit & 1)
