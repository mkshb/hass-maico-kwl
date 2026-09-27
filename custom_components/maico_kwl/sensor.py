"""Sensor platform for the Maico KWL integration."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .bus_feed import BusFeeder
from .const import BUS_FEEDS
from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .derived import (
    DERIVED_SENSORS,
    FILTER_DUE,
    HEAT_RECOVERY_SOURCES,
    DerivedDef,
    heat_recovery_power,
)
from .entity import (
    MaicoDerivedEntity,
    MaicoEntity,
    async_add_maico_entities,
)
from .register_defs import SENSOR, REGISTERS_BY_KEY, RegisterDef

# Read-only: data comes from the coordinator, no per-entity limit needed.
PARALLEL_UPDATES = 0

# The unit reports whole seconds and a read takes a moment, so the difference
# to Home Assistant's clock flips by 1 s between polls. Smaller changes than
# this are not shown, so the state does not change on every poll.
CLOCK_TOLERANCE = 2  # seconds

# Longer gaps between two readings (e.g. missed polls) are not integrated,
# since the power in between is unknown. A long scan interval widens the gap:
# two polls are always one interval apart.
MAX_ENERGY_GAP = timedelta(minutes=10)
MAX_ENERGY_GAP_INTERVALS = 2


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
    if all(key in coordinator.present for key in HEAT_RECOVERY_SOURCES):
        entities.append(MaicoHeatRecoveryEnergySensor(coordinator, entry))
    filters = tuple(
        source for _key, source in FILTER_DUE if source in coordinator.present
    )
    if filters:
        entities.append(MaicoNextFilterChangeSensor(coordinator, entry, filters))
    async_add_maico_entities(entry, Platform.SENSOR, async_add_entities, entities)


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
        self._clock_deviation: int | None = None

    @property
    def native_value(self) -> StateType | datetime:
        value = self._value
        if value is None:
            return None
        if isinstance(value, datetime):
            # The unit's clock runs in local time; positive means it is ahead.
            unit_time = value.replace(tzinfo=dt_util.get_default_time_zone())
            deviation = round((unit_time - dt_util.now()).total_seconds())
            if (
                self._clock_deviation is None
                or abs(deviation - self._clock_deviation) >= CLOCK_TOLERANCE
            ):
                self._clock_deviation = deviation
            return self._clock_deviation
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


class MaicoHeatRecoveryEnergySensor(MaicoDerivedEntity, RestoreSensor):
    """Heat recovered by the exchanger over time, in kWh.

    Integrates the heat recovery power between two polls (trapezoidal rule).
    Only recovered heat counts: negative power (the exchanger cooling the
    supply air) adds nothing, so the total only ever increases.
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_suggested_display_precision = 2

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry
    ) -> None:
        super().__init__(
            coordinator, entry, "heat_recovery_energy", HEAT_RECOVERY_SOURCES
        )
        self._energy = 0.0  # kWh
        self._last: tuple[datetime, float] | None = None  # time, power in W

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_sensor_data()
        if last is not None and isinstance(last.native_value, (int, float)):
            self._energy = float(last.native_value)
        self._add_reading()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._add_reading()
        super()._handle_coordinator_update()

    def _max_gap(self) -> timedelta:
        interval = self.coordinator.update_interval or timedelta(0)
        return max(MAX_ENERGY_GAP, interval * MAX_ENERGY_GAP_INTERVALS)

    def _add_reading(self) -> None:
        if not self.coordinator.last_update_success:
            # A failed poll keeps the previous data; it is no new reading. The
            # last real one stays, so a short outage is bridged between real
            # readings, a long one is a gap (see _max_gap).
            return
        numbers = self._numbers
        if numbers is None:
            self._last = None  # a gap: start over with the next reading
            return
        now = dt_util.utcnow()
        power = max(0.0, heat_recovery_power(*numbers))
        if self._last is not None:
            last_time, last_power = self._last
            elapsed = now - last_time
            if elapsed <= self._max_gap():
                hours = elapsed.total_seconds() / 3600
                self._energy += (last_power + power) / 2 * hours / 1000
        self._last = (now, power)

    @property
    def native_value(self) -> float:
        return round(self._energy, 3)
