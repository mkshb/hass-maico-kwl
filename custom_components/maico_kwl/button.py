"""Button platform for the Maico KWL integration (commands and rediscovery)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .discovery import data_without_discovery
from .entity import MaicoEntity, maico_device_info
from .register_defs import BUTTON, CLOCK, REGISTERS_BY_KEY, RegisterValue

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[ButtonEntity] = [
        MaicoButton(coordinator, entry, REGISTERS_BY_KEY[key])
        for key in coordinator.present
        if REGISTERS_BY_KEY[key].platform == BUTTON
    ]
    entities.append(MaicoRediscoverButton(coordinator, entry))
    async_add_entities(entities)


class MaicoButton(MaicoEntity, ButtonEntity):
    """A momentary command: writes a fixed value to a register on press."""

    async def async_press(self) -> None:
        value: RegisterValue
        if self._reg.data_type == CLOCK:
            # The unit keeps local time without a time zone.
            value = dt_util.now().replace(tzinfo=None, microsecond=0)
        else:
            value = self._reg.press_value
        await self._async_write(value)
        await self.coordinator.async_request_refresh()


class MaicoRediscoverButton(CoordinatorEntity[MaicoCoordinator], ButtonEntity):
    """Probe the unit again, e.g. after a module or sensor was added to it."""

    _attr_has_entity_name = True
    _attr_translation_key = "rediscover"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_rediscover"
        self._attr_device_info = maico_device_info(entry, coordinator)

    async def async_press(self) -> None:
        # Dropping the stored discovery reloads the entry (update listener),
        # and the setup then probes the unit again.
        self.hass.config_entries.async_update_entry(
            self._entry, data=data_without_discovery(self._entry.data)
        )
