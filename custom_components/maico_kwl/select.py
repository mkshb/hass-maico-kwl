"""Select platform for the Maico KWL integration (writable enum registers)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .entity import MaicoEntity, async_add_maico_entities
from .register_defs import SELECT, REGISTERS_BY_KEY, RegisterDef

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_maico_entities(
        entry,
        Platform.SELECT,
        async_add_entities,
        (
            MaicoSelect(coordinator, entry, REGISTERS_BY_KEY[key])
            for key in coordinator.present
            if REGISTERS_BY_KEY[key].platform == SELECT
        ),
    )


class MaicoSelect(MaicoEntity, SelectEntity):
    """A writable enum Maico register."""

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry, reg: RegisterDef
    ) -> None:
        super().__init__(coordinator, entry, reg)
        self._attr_options = list((reg.options or {}).values())

    @property
    def current_option(self) -> str | None:
        value = self._number
        if value is None:
            return None
        return self._reg.label_for(int(value))

    async def async_select_option(self, option: str) -> None:
        raw = self._reg.raw_for_label(option)
        if raw is None:
            return
        await self._async_write(raw)
        await self.coordinator.async_request_refresh()
