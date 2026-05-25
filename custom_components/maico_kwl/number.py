"""Number platform for the Maico KWL integration (writable numeric registers)."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import BUS_FEEDS, DOMAIN
from .entity import MaicoEntity
from .register_defs import NUMBER, REGISTERS_BY_KEY, RegisterDef

# Write-only "bus" inputs must be refreshed periodically (device note: write
# cycle >= 10 min). Re-write just under that so the value stays valid.
REWRITE_INTERVAL = timedelta(minutes=9)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    # Bus inputs driven by a configured source entity: no manual number entity.
    fed_by_source = {
        reg_key for reg_key, conf_key, _dc in BUS_FEEDS if entry.options.get(conf_key)
    }
    entities: list[NumberEntity] = []
    for key in coordinator.present:
        reg = REGISTERS_BY_KEY[key]
        if reg.platform != NUMBER:
            continue
        if reg.readable:
            entities.append(MaicoNumber(coordinator, entry, reg))
        elif reg.key not in fed_by_source:
            entities.append(MaicoBusInputNumber(coordinator, entry, reg))
    async_add_entities(entities)


def _apply_number_attrs(entity: NumberEntity, reg: RegisterDef) -> None:
    if reg.unit:
        entity._attr_native_unit_of_measurement = reg.unit
    if reg.device_class:
        entity._attr_device_class = NumberDeviceClass(reg.device_class)
    if reg.native_min is not None:
        entity._attr_native_min_value = reg.native_min
    if reg.native_max is not None:
        entity._attr_native_max_value = reg.native_max
    if reg.native_step is not None:
        entity._attr_native_step = reg.native_step


class MaicoNumber(MaicoEntity, NumberEntity):
    """A writable, readable numeric Maico register."""

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        _apply_number_attrs(self, reg)

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.hub.write(self._reg.address, self._reg.encode(value))
        await self.coordinator.async_request_refresh()


class MaicoBusInputNumber(MaicoEntity, RestoreNumber):
    """A write-only register the host feeds (e.g. room temperature over the bus).

    The value cannot be read back, so it is held locally (restored across
    restarts) and re-written periodically to satisfy the device's minimum
    write-cycle requirement.
    """

    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, reg: RegisterDef) -> None:
        super().__init__(coordinator, entry, reg)
        _apply_number_attrs(self, reg)
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._attr_native_value = last.native_value
            await self._async_write_value()  # refresh after a restart
        self.async_on_remove(
            async_track_time_interval(self.hass, self._async_rewrite, REWRITE_INTERVAL)
        )

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
        await self._async_write_value()

    async def _async_rewrite(self, _now) -> None:
        if self._attr_native_value is not None:
            await self._async_write_value()

    async def _async_write_value(self) -> None:
        await self.coordinator.hub.write(
            self._reg.address, self._reg.encode(self._attr_native_value)
        )
