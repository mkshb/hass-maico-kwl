"""Feed external HA entity values into Maico write-only "bus" input registers.

If the user picks a source entity in the options, its value is written to the
matching register on every state change and re-written periodically so it stays
valid for the device (write cycle >= 10 min).

A value is only sent when it is a finite number in a unit the register takes
(converted where that is unambiguous) and within the register's range. Anything
else is skipped rather than sent as a limit, so a faulty or unsuitable source
does not reach the unit as a plausible looking value.

A source that is renamed is followed (the options are updated). One that is
gone, or gives nothing usable for a while, gets a repair issue.

What reaches the unit, and what does not, is shown in the device's logbook
(BusLog, logbook.py).
"""

from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT
from homeassistant.core import (
    CALLBACK_TYPE,
    CoreState,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    issue_registry as ir,
)
from homeassistant.helpers.event import (
    async_call_later,
    async_track_entity_registry_updated_event,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import (
    BUS_EXPIRED,
    BUS_FAILED,
    BUS_FEEDS,
    BUS_RECOVERED,
    BUS_RETRY_INTERVAL,
    BUS_REWRITE_INTERVAL,
    BUS_SENT,
    BUS_SKIPPED,
    BUS_VALUE_VALID,
    DOMAIN,
    EVENT_BUS_INPUT,
)
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import PPM, RegisterDef, RegisterValue, to_raw

_LOGGER = logging.getLogger(__name__)

_INVALID = {None, "", "unknown", "unavailable"}

# Repair issues (translation keys) of a configured source.
_MISSING = "bus_source_missing"
_NO_DATA = "bus_source_no_data"
# Repair issue of a bus input the unit gets no valid value for.
_NOT_DELIVERED = "bus_value_not_delivered"

PPB = "ppb"

# A source that gives nothing usable for this long gets a repair issue. Shorter
# gaps are normal, e.g. a radio sensor that is quiet for a while or a restart.
SOURCE_NO_DATA_AFTER = timedelta(minutes=30)

# Option keys that hold a source entity.
_SOURCE_OPTIONS = {conf_key for _reg_key, conf_key, _device_class in BUS_FEEDS}


def source_raw(reg: RegisterDef, state: State) -> tuple[list[int] | None, str]:
    """The raw words to send for a source state, or None and why it is skipped.

    Temperatures are converted from any unit HA knows, ppb to ppm; other units
    and sources without a unit are skipped. The value is rounded to the
    register's resolution first, so e.g. 100.4 % still counts as 100 %.
    """
    try:
        value = float(state.state)
    except (TypeError, ValueError):
        value = math.nan
    if not math.isfinite(value):
        return None, f"state {state.state!r} is no number"
    unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
    if unit != reg.unit:
        if (
            reg.unit in TemperatureConverter.VALID_UNITS
            and unit in TemperatureConverter.VALID_UNITS
        ):
            value = TemperatureConverter.convert(value, unit, reg.unit)
        elif reg.unit == PPM and unit == PPB:
            value /= 1000
        else:
            return None, f"unit {unit!r} is not {reg.unit}"
    raw = to_raw(value, reg.scale)
    low = None if reg.native_min is None else to_raw(reg.native_min, reg.scale)
    high = None if reg.native_max is None else to_raw(reg.native_max, reg.scale)
    if (low is not None and raw < low) or (high is not None and raw > high):
        return None, (
            f"{value:g} {reg.unit} is outside {reg.native_min} to {reg.native_max}"
        )
    return reg.encode(raw * reg.scale), ""


class BusLog:
    """Bus input activity for the device's logbook (EVENT_BUS_INPUT).

    A sent value is logged the first time, then only when it changed, and at
    most once per BUS_REWRITE_INTERVAL and input: a change within that time is
    logged with the latest value once it has passed. The regular refresh of an
    unchanged value is not logged, so the logbook is not flooded by a source
    that changes often.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._logged: dict[str, RegisterValue | None] = {}
        self._logged_at: dict[str, datetime] = {}
        # Latest value per input not logged yet because of the throttle.
        self._pending: dict[str, tuple[RegisterDef, RegisterValue | None, str]] = {}
        self._timers: dict[str, CALLBACK_TYPE] = {}

    @callback
    def sent(self, reg: RegisterDef, value: RegisterValue | None, source: str) -> None:
        key = reg.key
        if key in self._logged and self._logged[key] == value:
            self._pending.pop(key, None)  # back at the value logged last
            return
        now = dt_util.utcnow()
        last = self._logged_at.get(key)
        if last is None or now - last >= BUS_REWRITE_INTERVAL:
            self._log_sent(reg, value, source)
            return
        self._pending[key] = (reg, value, source)
        if key not in self._timers:
            self._timers[key] = async_call_later(
                self._hass,
                last + BUS_REWRITE_INTERVAL - now,
                callback(lambda _now: self._flush(key)),
            )

    @callback
    def forget(self, key: str) -> None:
        """Log the next sent value even if it equals the last one logged."""
        self._logged.pop(key, None)

    @callback
    def fire(self, kind: str, reg: RegisterDef, **data: object) -> None:
        # The entry has one device (entity.maico_device_info).
        devices = dr.async_entries_for_config_entry(
            dr.async_get(self._hass), self._entry.entry_id
        )
        self._hass.bus.async_fire(
            EVENT_BUS_INPUT,
            {
                "device_id": devices[0].id if devices else None,
                "entry_id": self._entry.entry_id,
                "input": reg.key,
                "kind": kind,
                **data,
            },
        )

    @callback
    def stop(self) -> None:
        for unsub in self._timers.values():
            unsub()
        self._timers.clear()
        self._pending.clear()

    @callback
    def _flush(self, key: str) -> None:
        self._timers.pop(key, None)
        if (pending := self._pending.pop(key, None)) is not None:
            self._log_sent(*pending)

    def _log_sent(
        self, reg: RegisterDef, value: RegisterValue | None, source: str
    ) -> None:
        # A value waiting for the throttle is replaced by this one.
        self._pending.pop(reg.key, None)
        if (unsub := self._timers.pop(reg.key, None)) is not None:
            unsub()
        self._logged[reg.key] = value
        self._logged_at[reg.key] = dt_util.utcnow()
        self.fire(BUS_SENT, reg, value=value, unit=reg.unit, source=source)


class BusDelivery:
    """Keeps a bus input valid on the unit: retries, logging and its issue.

    After a failed write, ``retry`` is called every BUS_RETRY_INTERVAL until a
    write succeeds. Once the last successful write is older than
    BUS_VALUE_VALID, the unit uses its own sensor again, and a repair issue
    says so until the next write succeeds. The start and end of an outage go
    to the logbook.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        reg: RegisterDef,
        retry: Callable[[], object],
        log: BusLog,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._reg = reg
        self._retry = retry
        self._log = log
        self._last_success = dt_util.utcnow()
        self._retry_unsub: CALLBACK_TYPE | None = None
        self._failing = False
        self._expired = False

    @property
    def _issue_id(self) -> str:
        return f"{self._entry.entry_id}_{self._reg.key}_{_NOT_DELIVERED}"

    @callback
    def succeeded(self) -> None:
        self._last_success = dt_util.utcnow()
        self._cancel_retry()
        ir.async_delete_issue(self._hass, DOMAIN, self._issue_id)
        self._expired = False
        if self._failing:
            self._failing = False
            _LOGGER.info("Bus input %s: writes succeed again", self._reg.key)
            self._log.fire(BUS_RECOVERED, self._reg)

    @callback
    def failed(self, err: Exception) -> None:
        if not self._failing:
            # A lasting outage is logged once.
            self._failing = True
            _LOGGER.info("Bus input %s: write failed: %s", self._reg.key, err)
            self._log.fire(BUS_FAILED, self._reg, error=str(err))
        if dt_util.utcnow() - self._last_success >= BUS_VALUE_VALID:
            if not self._expired:
                self._expired = True
                self._log.fire(BUS_EXPIRED, self._reg)
            ir.async_create_issue(
                self._hass,
                DOMAIN,
                self._issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=_NOT_DELIVERED,
                translation_placeholders={
                    "name": self._entry.title,
                    "register": str(self._reg.address),
                    "error": str(err),
                },
            )
        if self._retry_unsub is None:
            self._retry_unsub = async_call_later(
                self._hass, BUS_RETRY_INTERVAL, self._handle_retry
            )

    @callback
    def stop(self) -> None:
        self._cancel_retry()
        ir.async_delete_issue(self._hass, DOMAIN, self._issue_id)

    @callback
    def _handle_retry(self, _now: datetime) -> None:
        self._retry_unsub = None
        self._retry()

    def _cancel_retry(self) -> None:
        if self._retry_unsub is not None:
            self._retry_unsub()
            self._retry_unsub = None


@dataclass(frozen=True)
class SentValue:
    """The value the unit last received for a bus input."""

    value: RegisterValue | None
    written_at: datetime


class BusFeeder:
    """Writes configured source-entity values into bus input registers."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        hub: MaicoModbusHub,
        feeds: list[tuple[RegisterDef, str]],
        identity_problem: Callable[[], str | None],
    ) -> None:
        self.hass = hass
        self._entry = entry
        self._hub = hub
        # Why the device does not look like a Maico KWL; nothing is written then.
        self._identity_problem = identity_problem
        self._feeds = feeds
        self._unsubs: list[CALLBACK_TYPE] = []
        self._tasks: set[asyncio.Task[None]] = set()
        self._log = BusLog(hass, entry)
        self._delivery = {
            reg.key: BusDelivery(
                hass, entry, reg, self._retry_callback(reg, entity_id), self._log
            )
            for reg, entity_id in feeds
        }
        # Registers whose source value is skipped, and why, so that is logged
        # once (see source_raw).
        self._skipped: dict[str, str] = {}
        # Last raw words written per register, to skip unchanged values.
        self._written: dict[str, list[int]] = {}
        self._sent: dict[str, SentValue] = {}
        self._listeners: dict[str, list[Callable[[], None]]] = {}
        # When each source last gave a value that could be sent.
        self._usable_at: dict[str, datetime] = {}
        self._started_at = dt_util.utcnow()

    def sent(self, key: str) -> SentValue | None:
        """Return what was last written successfully to a bus input."""
        return self._sent.get(key)

    def _retry_callback(self, reg: RegisterDef, entity_id: str) -> Callable[[], None]:
        return lambda: self._schedule_write(
            reg, self.hass.states.get(entity_id), force=True
        )

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
        self._started_at = dt_util.utcnow()
        for reg, entity_id in self._feeds:
            await self._async_write(reg, self.hass.states.get(entity_id), force=True)
        entity_ids = [entity_id for _reg, entity_id in self._feeds]
        self._unsubs.append(
            async_track_state_change_event(
                self.hass, entity_ids, self._handle_state_event
            )
        )
        self._unsubs.append(
            async_track_entity_registry_updated_event(
                self.hass, entity_ids, self._handle_registry_event
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
        for reg, _entity_id in self._feeds:
            for issue in (_MISSING, _NO_DATA):
                ir.async_delete_issue(self.hass, DOMAIN, self._issue_id(reg, issue))
        for delivery in self._delivery.values():
            delivery.stop()
        self._log.stop()

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
    def _handle_state_event(self, event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        new_state = event.data.get("new_state")
        for reg, feed_entity_id in self._feeds:
            if feed_entity_id == entity_id:
                self._schedule_write(reg, new_state)

    @callback
    def _handle_registry_event(
        self, event: Event[er.EventEntityRegistryUpdatedData]
    ) -> None:
        data = event.data
        if data["action"] == "update" and "old_entity_id" in data:
            # Renamed: follow it. The options change reloads the entry.
            old, new = data["old_entity_id"], data["entity_id"]
            options = {
                key: new if key in _SOURCE_OPTIONS and value == old else value
                for key, value in self._entry.options.items()
            }
            self.hass.config_entries.async_update_entry(self._entry, options=options)
        elif data["action"] == "remove":
            for reg, entity_id in self._feeds:
                if entity_id == data["entity_id"]:
                    self._set_issue(reg, _MISSING, True, entity_id)

    @callback
    def _handle_interval(self, now: datetime) -> None:
        self._check_sources(now)
        # Always write here: the unit needs the value refreshed periodically.
        for reg, entity_id in self._feeds:
            self._schedule_write(reg, self.hass.states.get(entity_id), force=True)

    @callback
    def _check_sources(self, now: datetime) -> None:
        """Raise or clear the issues of sources that are gone or give nothing.

        Only once HA has started: until then a source may just not be loaded.
        """
        if self.hass.state is not CoreState.running:
            return
        ent_reg = er.async_get(self.hass)
        for reg, entity_id in self._feeds:
            state = self.hass.states.get(entity_id)
            missing = state is None and ent_reg.async_get(entity_id) is None
            self._set_issue(reg, _MISSING, missing, entity_id)
            since = self._usable_at.get(reg.key, self._started_at)
            stale = not missing and now - since > SOURCE_NO_DATA_AFTER
            if state is None:
                reason = "no state"
            elif state.state in _INVALID:
                reason = f"state {state.state!r}"
            else:
                reason = self._skipped.get(reg.key, "no usable value")
            self._set_issue(reg, _NO_DATA, stale, entity_id, reason)

    def _issue_id(self, reg: RegisterDef, issue: str) -> str:
        return f"{self._entry.entry_id}_{reg.key}_{issue}"

    @callback
    def _set_issue(
        self,
        reg: RegisterDef,
        issue: str,
        active: bool,
        entity_id: str,
        reason: str = "",
    ) -> None:
        issue_id = self._issue_id(reg, issue)
        if not active:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)
            return
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=issue,
            translation_placeholders={
                "name": self._entry.title,
                "entity": entity_id,
                "reason": reason,
            },
        )

    def _source_raw(self, reg: RegisterDef, state: State | None) -> list[int] | None:
        """The raw words to send, or None; logs when a source starts and stops being skipped."""
        if state is None or state.state in _INVALID:
            return None
        raw, reason = source_raw(reg, state)
        if raw is None:
            if reg.key not in self._skipped:
                _LOGGER.info(
                    "Bus feed %s: %s is not sent, %s", reg.key, state.entity_id, reason
                )
                self._log.fire(
                    BUS_SKIPPED, reg, source=state.entity_id, reason=reason
                )
                self._log.forget(reg.key)
            self._skipped[reg.key] = reason
            return None
        if self._skipped.pop(reg.key, None) is not None:
            _LOGGER.info("Bus feed %s: %s is sent again", reg.key, state.entity_id)
        self._usable_at[reg.key] = dt_util.utcnow()
        for issue in (_MISSING, _NO_DATA):
            self._set_issue(reg, issue, False, state.entity_id)
        return raw

    async def _async_write(
        self, reg: RegisterDef, state: State | None, force: bool = False
    ) -> None:
        raw = self._source_raw(reg, state)
        if raw is None:
            return
        if not force and self._written.get(reg.key) == raw:
            return  # e.g. a source reporting 21.52 after 21.5
        if problem := self._identity_problem():
            self._delivery[reg.key].failed(
                MaicoModbusError(f"not written, no Maico KWL: {problem}")
            )
            return
        try:
            await self._hub.write(reg.address, raw)
        except MaicoModbusError as err:
            self._delivery[reg.key].failed(err)
            return
        self._written[reg.key] = raw
        # Decode the raw words so the value shows what the unit received.
        self._sent[reg.key] = SentValue(reg.decode(raw), dt_util.utcnow())
        assert state is not None  # raw came from it
        self._log.sent(reg, self._sent[reg.key].value, state.entity_id)
        for listener in list(self._listeners.get(reg.key, [])):
            listener()
        self._delivery[reg.key].succeeded()
