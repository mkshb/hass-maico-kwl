"""Fan platform for the Maico KWL integration.

One fan entity combines the operating mode (550) and the ventilation level
(554): the levels are the speeds, the operating modes the presets. This makes
the unit usable with voice assistants, HomeKit and the standard fan cards.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .entity import (
    MaicoDerivedEntity,
    async_add_maico_entities,
    async_write_register,
)
from .register_defs import OPERATING_MODE, REGISTERS_BY_KEY, VENT_LEVEL

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1

MODE = "operating_mode"
LEVEL = "ventilation_level"
CURRENT_LEVEL = "current_vent_level"

# Speeds from low to high; "off" is the fan being off, not a speed.
SPEEDS = [slug for raw, slug in sorted(VENT_LEVEL.items()) if raw > 0]
# Every operating mode except "off" is a preset.
PRESETS = [slug for raw, slug in sorted(OPERATING_MODE.items()) if raw > 0]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    if {MODE, LEVEL} <= coordinator.present:
        async_add_maico_entities(
            entry, async_add_entities, [MaicoFan(coordinator, entry)]
        )


class MaicoFan(MaicoDerivedEntity, FanEntity):
    """The ventilation unit as a fan: levels as speeds, modes as presets."""

    _attr_speed_count = len(SPEEDS)
    _attr_preset_modes = PRESETS
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: MaicoCoordinator, entry: MaicoConfigEntry) -> None:
        super().__init__(coordinator, entry, "ventilation", (MODE, LEVEL))
        # Mode to return to when turned on without a preset.
        mode = self._slug(MODE)
        self._last_mode = mode if mode in PRESETS else "manual"

    def _slug(self, key: str) -> str | None:
        value = self.coordinator.data.get(key)
        if not isinstance(value, (int, float)):
            return None
        return REGISTERS_BY_KEY[key].label_for(int(value))

    @property
    def is_on(self) -> bool | None:
        mode = self._slug(MODE)
        return None if mode is None else mode != "off"

    @callback
    def _handle_coordinator_update(self) -> None:
        if (mode := self._slug(MODE)) in PRESETS:
            self._last_mode = mode
        super()._handle_coordinator_update()

    @property
    def preset_mode(self) -> str | None:
        mode = self._slug(MODE)
        return mode if mode in PRESETS else None

    @property
    def percentage(self) -> int | None:
        if not self.is_on:
            return 0
        # The level actually running (e.g. chosen by an auto mode), else the set one.
        level = self._slug(CURRENT_LEVEL) or self._slug(LEVEL)
        if level not in SPEEDS:
            return 0
        return ordered_list_item_to_percentage(SPEEDS, level)

    async def _async_write(self, key: str, slug: str) -> None:
        reg = REGISTERS_BY_KEY[key]
        raw = reg.raw_for_label(slug)
        assert raw is not None
        await async_write_register(self.coordinator, reg, raw, self.entity_id)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self.async_turn_off()
            return
        # A speed only sticks in manual mode; the auto modes pick their own.
        if self._slug(MODE) != "manual":
            await self._async_write(MODE, "manual")
        level = percentage_to_ordered_list_item(SPEEDS, percentage)
        await self._async_write(LEVEL, level)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self._async_write(MODE, preset_mode)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        elif not self.is_on:
            await self.async_set_preset_mode(self._last_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_write(MODE, "off")
        await self.coordinator.async_request_refresh()
