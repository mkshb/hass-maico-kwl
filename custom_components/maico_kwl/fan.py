"""Fan platform for the Maico KWL integration.

One fan entity combines the operating mode (550) and the ventilation level
(554): the levels are the speeds, the operating modes the presets. This makes
the unit usable with voice assistants, HomeKit and the standard fan cards.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import Platform
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .const import DOMAIN
from .coordinator import MaicoConfigEntry, MaicoCoordinator
from .entity import (
    MaicoDerivedEntity,
    async_add_maico_entities,
    async_write_register,
)
from .register_defs import OPERATING_MODE, REGISTERS_BY_KEY, VENT_LEVEL

_LOGGER = logging.getLogger(__name__)

# Send actions to the unit one at a time.
PARALLEL_UPDATES = 1

MODE = "operating_mode"
LEVEL = "ventilation_level"
BOOST = "boost_ventilation"
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
    fans: list[MaicoFan] = []
    if {MODE, LEVEL} <= coordinator.present:
        fans.append(MaicoFan(coordinator, entry))
    async_add_maico_entities(entry, Platform.FAN, async_add_entities, fans)


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
        self._end_boost: CALLBACK_TYPE | None = None

    async def async_will_remove_from_hass(self) -> None:
        self._cancel_boost_timer()
        await super().async_will_remove_from_hass()

    def _cancel_boost_timer(self) -> None:
        if self._end_boost is not None:
            self._end_boost()
            self._end_boost = None

    async def async_boost(self, duration: int | None = None) -> None:
        """Start the boost ventilation (551), optionally for a number of minutes.

        Without a duration the unit ends the boost on its own terms. With one,
        Home Assistant switches it off again when the time is up; a new call
        replaces the running timer.
        """
        if BOOST not in self.coordinator.present:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="boost_unavailable"
            )
        reg = REGISTERS_BY_KEY[BOOST]
        self._cancel_boost_timer()
        await async_write_register(self.coordinator, reg, 1, self.entity_id)
        if duration is not None:
            self._end_boost = async_call_later(
                self.hass, duration * 60, self._async_boost_time_up
            )
        await self.coordinator.async_request_refresh()

    async def _async_boost_time_up(self, _now: datetime) -> None:
        self._end_boost = None
        try:
            await async_write_register(
                self.coordinator, REGISTERS_BY_KEY[BOOST], 0, self.entity_id
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Ending the boost failed: %s", err)
            return
        await self.coordinator.async_request_refresh()

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
