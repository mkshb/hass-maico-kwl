"""Sensor platform for the Maico KWL integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import BUS_FEEDS, DOMAIN
from .entity import MaicoEntity
from .register_defs import (
    AIR_HEAT_CAPACITY,
    DERIVED_HEAT_RECOVERY,
    HEAT_RECOVERY_SOURCES,
    REGISTERS_BY_KEY,
    SENSOR,
    RegisterDef,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    entities: list[SensorEntity] = [
        MaicoSensor(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == SENSOR
    ]
    # When a bus input is fed from a source entity, expose a read-only sensor
    # showing the value being sent (the write-only register can't be read back).
    for reg_key, conf_key, _device_class in BUS_FEEDS:
        source = entry.options.get(conf_key)
        if source and reg_key in coordinator.present:
            entities.append(
                MaicoBusFeedSensor(
                    coordinator, entry, REGISTERS_BY_KEY[reg_key], source
                )
            )
    # Recovered heat is not a register; derive it when all inputs are present.
    if all(key in coordinator.present for key in HEAT_RECOVERY_SOURCES):
        entities.append(MaicoHeatRecoverySensor(coordinator, entry))
    async_add_entities(entities)


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


class MaicoBusFeedSensor(MaicoEntity, SensorEntity):
    """Read-only mirror of the value fed into a write-only bus input register."""

    def __init__(self, coordinator, entry, reg: RegisterDef, source_entity_id: str) -> None:
        super().__init__(coordinator, entry, reg)
        self._source_entity_id = source_entity_id
        self._attr_unique_id = f"{entry.entry_id}_{reg.key}_sent"
        self._attr_translation_key = f"{reg.key}_sent"
        if reg.unit:
            self._attr_native_unit_of_measurement = reg.unit
        if reg.device_class:
            self._attr_device_class = SensorDeviceClass(reg.device_class)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source_entity_id], self._handle_source_event
            )
        )

    @callback
    def _handle_source_event(self, _event) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self):
        state = self.hass.states.get(self._source_entity_id)
        if state is None or state.state in ("unknown", "unavailable", "", None):
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        if self._reg.native_min is not None:
            value = max(value, self._reg.native_min)
        if self._reg.native_max is not None:
            value = min(value, self._reg.native_max)
        return value


class MaicoHeatRecoverySensor(MaicoEntity, SensorEntity):
    """Heat recovered by the exchanger, derived from airflow and temperatures.

    The Modbus map exposes no register for this, so it is computed the same way
    the vendor app does: the supply airflow times the temperature rise the air
    gains while passing through the heat exchanger.
    """

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, DERIVED_HEAT_RECOVERY)
        self._attr_native_unit_of_measurement = DERIVED_HEAT_RECOVERY.unit
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and all(
            key in self.coordinator.data for key in HEAT_RECOVERY_SOURCES
        )

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        try:
            airflow = float(data["airflow_supply"])
            intake = float(data["temp_air_intake"])
            supply = float(data["temp_supply_air"])
        except (KeyError, TypeError, ValueError):
            return None
        # Negative during bypass/cooling operation: the exchanger then removes
        # heat from the supply air rather than adding it.
        return round(airflow * AIR_HEAT_CAPACITY * (supply - intake))
