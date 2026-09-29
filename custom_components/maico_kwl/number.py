"""Number platform for the Maico KWL integration (writable numeric registers)."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MaicoConfigEntry, MaicoCoordinator
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
    # The bus inputs (write-only) are only fed from a source entity set in the
    # options (bus_feed.py): without one, nothing is sent to the unit.
    entities: list[NumberEntity] = [
        MaicoNumber(coordinator, entry, reg)
        for key in coordinator.present
        if (reg := REGISTERS_BY_KEY[key]).platform == NUMBER and reg.readable
    ]
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
