"""Button platform for the Maico KWL integration (write-command registers)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MaicoConfigEntry
from .entity import MaicoEntity
from .register_defs import BUTTON, REGISTERS_BY_KEY

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        MaicoButton(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == BUTTON
    )


class MaicoButton(MaicoEntity, ButtonEntity):
    """A momentary command: writes a fixed value to a register on press."""

    async def async_press(self) -> None:
        await self._async_write(self._reg.press_value)
        await self.coordinator.async_request_refresh()
