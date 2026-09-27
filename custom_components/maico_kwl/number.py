"""Number platform for the Maico KWL integration (writable numeric registers)."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
    RestoreNumber,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import BUS_FEEDS, BUS_REWRITE_INTERVAL
from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .bus_feed import BusDelivery
from .entity import MaicoEntity, async_add_maico_entities
from .register_defs import NUMBER, REGISTERS_BY_KEY, RegisterDef

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
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
    async_add_maico_entities(entry, Platform.NUMBER, async_add_entities, entities)


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

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry, reg: RegisterDef
    ) -> None:
        super().__init__(coordinator, entry, reg)
        _apply_number_attrs(self, reg)

    @property
    def native_value(self) -> float | None:
        return self._number

    async def async_set_native_value(self, value: float) -> None:
        await self._async_write(value)
        await self.coordinator.async_request_refresh()


class MaicoBusInputNumber(MaicoEntity, RestoreNumber):
    """A write-only register the host feeds (e.g. room temperature over the bus).

    The value cannot be read back, so it is held locally (restored across
    restarts) and re-written periodically, since the unit only keeps it for
    10 minutes (see BusDelivery for retries after a failed write).
    """

    _attr_mode = NumberMode.BOX

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry, reg: RegisterDef
    ) -> None:
        super().__init__(coordinator, entry, reg)
        _apply_number_attrs(self, reg)
        self._attr_native_value = None
        self._entry = entry
        self._delivery: BusDelivery | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._delivery = BusDelivery(
            self.hass,
            self._entry,
            self._reg,
            lambda: self._entry.async_create_background_task(
                self.hass, self._async_rewrite(None), f"maico_kwl retry {self._reg.key}"
            ),
        )
        self.async_on_remove(self._delivery.stop)
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._attr_native_value = last.native_value
            await self._async_rewrite(None)  # refresh after a restart
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_rewrite, BUS_REWRITE_INTERVAL
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        # Only keep the value once the device has accepted it.
        await self._async_write(value)
        self._attr_native_value = value
        self.async_write_ha_state()
        if self._delivery is not None:
            self._delivery.succeeded()

    async def _async_rewrite(self, _now: datetime | None) -> None:
        if self._attr_native_value is None:
            return
        assert self._delivery is not None
        try:
            await self._async_write(self._attr_native_value)
        except HomeAssistantError as err:
            # Retried soon; must not break entity setup.
            self._delivery.failed(err)
            return
        self._delivery.succeeded()
