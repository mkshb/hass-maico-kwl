"""Repair issues for problems the unit reports.

Shown under Settings > System > Repairs while the problem lasts and removed
automatically once it is gone.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import MaicoConfigEntry
from .register_defs import REGISTERS_BY_KEY

_LOGGER = logging.getLogger(__name__)

# Clock deviation from which the unit's schedules are noticeably off.
CLOCK_DRIFT_LIMIT = 300  # seconds

# How long the unit may not answer before it is shown as a repair issue: a
# poll that fails now and then (e.g. while a backup keeps HA busy) is none.
UNREACHABLE_AFTER = timedelta(minutes=10)

FILTERS = {
    "filter_due_device": "filter_remaining_device",
    "filter_due_outdoor": "filter_remaining_outdoor",
    "filter_due_room": "filter_remaining_room",
}
ISSUES = [
    "fault_active",
    "clock_drift",
    "unsupported_device",
    "unit_unreachable",
    *FILTERS,
]


def _issue_id(entry: MaicoConfigEntry, key: str) -> str:
    return f"{entry.entry_id}_{key}"


@callback
def _async_set(
    hass: HomeAssistant,
    entry: MaicoConfigEntry,
    key: str,
    active: bool,
    severity: ir.IssueSeverity,
    placeholders: dict[str, str] | None = None,
) -> None:
    if not active:
        ir.async_delete_issue(hass, DOMAIN, _issue_id(entry, key))
        return
    ir.async_create_issue(
        hass,
        DOMAIN,
        _issue_id(entry, key),
        is_fixable=False,
        severity=severity,
        translation_key=key,
        translation_placeholders={"name": entry.title, **(placeholders or {})},
    )


@callback
def async_update_issues(hass: HomeAssistant, entry: MaicoConfigEntry) -> None:
    """Create or remove the issues from the latest data.

    A register missing from this poll leaves its issue as it is.
    """
    coordinator = entry.runtime_data.coordinator
    data = coordinator.data or {}

    problem = coordinator.identity_problem
    _async_set(
        hass,
        entry,
        "unsupported_device",
        problem is not None,
        ir.IssueSeverity.ERROR,
        {"details": problem or ""},
    )

    fault = data.get("fault_code")
    if isinstance(fault, (int, float)):
        faults = REGISTERS_BY_KEY["fault_code"].active_bits(fault)
        _async_set(
            hass,
            entry,
            "fault_active",
            bool(fault),
            ir.IssueSeverity.ERROR,
            {"faults": ", ".join(faults)},
        )

    for key, source in FILTERS.items():
        days = data.get(source)
        if isinstance(days, (int, float)):
            _async_set(hass, entry, key, days <= 0, ir.IssueSeverity.WARNING)

    clock = data.get("clock_deviation")
    if isinstance(clock, datetime):
        unit_time = clock.replace(tzinfo=dt_util.get_default_time_zone())
        deviation = (unit_time - dt_util.now()).total_seconds()
        _async_set(
            hass,
            entry,
            "clock_drift",
            abs(deviation) > CLOCK_DRIFT_LIMIT,
            ir.IssueSeverity.WARNING,
            {"minutes": str(round(deviation / 60))},
        )


@callback
def async_update_unreachable_issue(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> None:
    """Show a unit that has not answered for a while, once in the log too.

    Called after every poll. Home Assistant logs only the first failed poll,
    as an error that is easily missed among others, so an outage of days
    could go unnoticed.
    """
    coordinator = entry.runtime_data.coordinator
    since = coordinator.unreachable_since
    unreachable = since is not None and dt_util.utcnow() - since >= UNREACHABLE_AFTER
    shown = (
        ir.async_get(hass).async_get_issue(DOMAIN, _issue_id(entry, "unit_unreachable"))
        is not None
    )
    if unreachable and not shown:
        _LOGGER.warning(
            "%s has not answered since %s: %s",
            entry.title,
            since,
            coordinator.last_exception,
        )
    elif shown and not unreachable:
        _LOGGER.info("%s answers again", entry.title)
    _async_set(
        hass,
        entry,
        "unit_unreachable",
        unreachable,
        ir.IssueSeverity.ERROR,
        {"since": dt_util.as_local(since).strftime("%Y-%m-%d %H:%M") if since else ""},
    )


@callback
def async_delete_issues(hass: HomeAssistant, entry: MaicoConfigEntry) -> None:
    """Remove all issues of an entry, e.g. when it is unloaded."""
    for key in ISSUES:
        ir.async_delete_issue(hass, DOMAIN, _issue_id(entry, key))
