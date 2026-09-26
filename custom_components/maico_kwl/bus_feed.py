"""Feed external HA entity values into Maico write-only "bus" input registers.

If the user picks a source entity in the options, its value is written to the
matching register on every state change and re-written periodically so it stays
valid for the device (write cycle >= 10 min).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .const import BUS_REWRITE_INTERVAL
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import RegisterDef

_LOGGER = logging.getLogger(__name__)

_INVALID = {None, "", "unknown", "unavailable"}


@dataclass(frozen=True)
class SentValue:
    """The value the unit last received for a bus input."""

    value: float
    written_at: datetime


class BusFeeder:
    """Writes configured source-entity values into bus input registers."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        hub: MaicoModbusHub,
        feeds: list[tuple[RegisterDef, str]],
    ) -> None:
        self.hass = hass
        self._entry = entry
        self._hub = hub
        self._feeds = feeds
        self._unsubs: list = []
        self._tasks: set[asyncio.Task] = set()
        # Registers whose last write failed, so a lasting outage is logged once.
        self._failing: set[str] = set()
        # Last raw words written per register, to skip unchanged values.
        self._written: dict[str, list[int]] = {}
        self._sent: dict[str, SentValue] = {}
        self._listeners: dict[str, list[Callable[[], None]]] = {}

    def sent(self, key: str) -> SentValue | None:
        """Return what was last written successfully to a bus input."""
        return self._sent.get(key)

    @callback
    def async_add_listener(
        self, key: str, listener: Callable[[], None]
    ) -> Callable[[], None]:
        """Call listener after every successful write to key."""
        listeners = self._listeners.setdefault(key, [])
        listeners.append(listener)
        return lambda: listeners.remove(listener)

    async def async_start(self) -> None:
        if not self._feeds:
            return
        for reg, entity_id in self._feeds:
            await self._async_write(reg, self.hass.states.get(entity_id), force=True)
        entity_ids = [entity_id for _reg, entity_id in self._feeds]
        self._unsubs.append(
            async_track_state_change_event(
                self.hass, entity_ids, self._handle_state_event
            )
        )
        self._unsubs.append(
            async_track_time_interval(
                self.hass, self._handle_interval, BUS_REWRITE_INTERVAL
            )
        )

    @callback
    def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        # Pending writes must not run against the hub after it is closed.
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    @callback
    def _schedule_write(
        self, reg: RegisterDef, state: State | None, force: bool = False
    ) -> None:
        task = self._entry.async_create_background_task(
            self.hass,
            self._async_write(reg, state, force),
            f"maico_kwl bus feed {reg.key}",
        )
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    @callback
    def _handle_state_event(self, event: Event) -> None:
        entity_id = event.data["entity_id"]
        new_state = event.data.get("new_state")
        for reg, feed_entity_id in self._feeds:
            if feed_entity_id == entity_id:
                self._schedule_write(reg, new_state)

    @callback
    def _handle_interval(self, _now) -> None:
        # Always write here: the unit needs the value refreshed periodically.
        for reg, entity_id in self._feeds:
            self._schedule_write(reg, self.hass.states.get(entity_id), force=True)

    async def _async_write(
        self, reg: RegisterDef, state: State | None, force: bool = False
    ) -> None:
        if state is None or state.state in _INVALID:
            return
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Bus feed %s: state %r is not numeric", reg.key, state.state
            )
            return
        raw = reg.encode(reg.clamp(value))
        if not force and self._written.get(reg.key) == raw:
            return  # e.g. a source reporting 21.52 after 21.5
        try:
            await self._hub.write(reg.address, raw)
        except MaicoModbusError as err:
            if reg.key not in self._failing:
                self._failing.add(reg.key)
                _LOGGER.info("Bus feed %s write failed: %s", reg.key, err)
            return
        self._written[reg.key] = raw
        # Decode the raw words so the value shows what the unit received.
        self._sent[reg.key] = SentValue(reg.decode(raw), dt_util.utcnow())
        for listener in list(self._listeners.get(reg.key, [])):
            listener()
        if reg.key in self._failing:
            self._failing.discard(reg.key)
            _LOGGER.info("Bus feed %s writes succeed again", reg.key)
