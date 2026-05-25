"""Feed external HA entity values into Maico write-only "bus" input registers.

If the user picks a source entity in the options, its value is written to the
matching register on every state change and re-written periodically so it stays
valid for the device (write cycle >= 10 min).
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import RegisterDef

_LOGGER = logging.getLogger(__name__)

REWRITE_INTERVAL = timedelta(minutes=9)
_INVALID = {None, "", "unknown", "unavailable"}


class BusFeeder:
    """Writes configured source-entity values into bus input registers."""

    def __init__(
        self,
        hass: HomeAssistant,
        hub: MaicoModbusHub,
        feeds: list[tuple[RegisterDef, str]],
    ) -> None:
        self.hass = hass
        self._hub = hub
        self._feeds = feeds
        self._unsubs: list = []

    async def async_start(self) -> None:
        if not self._feeds:
            return
        for reg, entity_id in self._feeds:
            await self._async_write(reg, self.hass.states.get(entity_id))
        entity_ids = [entity_id for _reg, entity_id in self._feeds]
        self._unsubs.append(
            async_track_state_change_event(
                self.hass, entity_ids, self._handle_state_event
            )
        )
        self._unsubs.append(
            async_track_time_interval(
                self.hass, self._handle_interval, REWRITE_INTERVAL
            )
        )

    @callback
    def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    @callback
    def _handle_state_event(self, event: Event) -> None:
        entity_id = event.data["entity_id"]
        new_state = event.data.get("new_state")
        for reg, feed_entity_id in self._feeds:
            if feed_entity_id == entity_id:
                self.hass.async_create_task(self._async_write(reg, new_state))

    async def _handle_interval(self, _now) -> None:
        for reg, entity_id in self._feeds:
            await self._async_write(reg, self.hass.states.get(entity_id))

    async def _async_write(self, reg: RegisterDef, state: State | None) -> None:
        if state is None or state.state in _INVALID:
            return
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Bus feed %s: state %r is not numeric", reg.key, state.state
            )
            return
        if reg.native_min is not None:
            value = max(value, reg.native_min)
        if reg.native_max is not None:
            value = min(value, reg.native_max)
        try:
            await self._hub.write(reg.address, reg.encode(value))
        except MaicoModbusError as err:
            _LOGGER.warning("Bus feed %s write failed: %s", reg.key, err)
