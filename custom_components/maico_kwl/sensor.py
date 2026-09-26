"""Sensor platform for the Maico KWL integration."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .bus_feed import BusFeeder
from .const import BUS_FEEDS
from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .derived import DERIVED_SENSORS, FILTER_DUE, DerivedDef
from .entity import MaicoDerivedEntity, MaicoEntity
from .register_defs import SENSOR, REGISTERS_BY_KEY, RegisterDef

# Read-only: data comes from the coordinator, no per-entity limit needed.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = [
        MaicoSensor(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == SENSOR
    ]
    # When a bus input is fed from a source entity, expose a read-only sensor
    # showing the value last sent (the write-only register can't be read back).
    feeder = entry.runtime_data.feeder
    for reg_key, conf_key, _device_class in BUS_FEEDS:
        source = entry.options.get(conf_key)
        if source and reg_key in coordinator.present:
            entities.append(
                MaicoBusFeedSensor(
                    coordinator, entry, REGISTERS_BY_KEY[reg_key], feeder, source
                )
            )
    # Values the unit does not report, computed from the registers it has.
    entities.extend(
        MaicoDerivedSensor(coordinator, entry, derived)
        for derived in DERIVED_SENSORS
        if all(key in coordinator.present for key in derived.sources)
    )
    filters = tuple(
        source for _key, source in FILTER_DUE if source in coordinator.present
    )
    if filters:
        entities.append(MaicoNextFilterChangeSensor(coordinator, entry, filters))
    async_add_entities(entities)


class MaicoSensor(MaicoEntity, SensorEntity):
    """A read-only Maico register exposed as a sensor."""

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry, reg: RegisterDef
    ) -> None:
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
    def native_value(self) -> StateType | datetime:
        value = self._value
        if value is None:
            return None
        if isinstance(value, datetime):
            # The unit's clock runs in local time; timestamps need a time zone.
            return value.replace(tzinfo=dt_util.get_default_time_zone())
        if self._reg.options is not None:
            return self._reg.label_for(int(value))
        return value

    @property
    def extra_state_attributes(self) -> dict[str, list[str]] | None:
        """For bitfield registers, the meanings of the bits that are set."""
        if self._reg.bits is None or self._number is None:
            return None
        return {"active": self._reg.active_bits(self._number)}


class MaicoBusFeedSensor(MaicoEntity, SensorEntity):
    """The value last written to a write-only bus input register.

    Shows what the unit actually received: nothing before the first successful
    write, the previous value while writes fail, and the value as encoded on
    the wire (e.g. 55 for a humidity source reporting 55.4).
    """

    _unrecorded_attributes = frozenset({"last_written"})

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        entry: MaicoConfigEntry,
        reg: RegisterDef,
        feeder: BusFeeder,
        source_entity_id: str,
    ) -> None:
        super().__init__(coordinator, entry, reg)
        self._feeder = feeder
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
            self._feeder.async_add_listener(self._reg.key, self._handle_sent)
        )

    @callback
    def _handle_sent(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType | datetime:
        sent = self._feeder.sent(self._reg.key)
        return None if sent is None else sent.value

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        sent = self._feeder.sent(self._reg.key)
        return {
            "source_entity": self._source_entity_id,
            "last_written": None if sent is None else sent.written_at.isoformat(),
        }


class MaicoDerivedSensor(MaicoDerivedEntity, SensorEntity):
    """A value computed from several registers (see derived.py)."""

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        entry: MaicoConfigEntry,
        derived: DerivedDef,
    ) -> None:
        super().__init__(coordinator, entry, derived.key, derived.sources)
        self._derived = derived
        self._attr_native_unit_of_measurement = derived.unit
        if derived.device_class:
            self._attr_device_class = SensorDeviceClass(derived.device_class)
        if derived.state_class:
            self._attr_state_class = SensorStateClass(derived.state_class)
        self._attr_suggested_display_precision = derived.precision
        if derived.entity_category:
            self._attr_entity_category = EntityCategory(derived.entity_category)

    @property
    def native_value(self) -> float | None:
        numbers = self._numbers
        return None if numbers is None else self._derived.compute(*numbers)


class MaicoNextFilterChangeSensor(MaicoDerivedEntity, SensorEntity):
    """The date the first of the filters runs out."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        entry: MaicoConfigEntry,
        filters: tuple[str, ...],
    ) -> None:
        super().__init__(coordinator, entry, "filter_next_change", filters)

    @property
    def native_value(self) -> date | None:
        numbers = self._numbers
        if numbers is None:
            return None
        return dt_util.now().date() + timedelta(days=max(0, int(min(numbers))))
