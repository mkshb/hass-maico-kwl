"""Repair issues for problems the unit reports.

Shown under Settings > System > Repairs while the problem lasts and removed
automatically once it is gone.
"""

from __future__ import annotations

from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import MaicoConfigEntry
from .register_defs import REGISTERS_BY_KEY

# Clock deviation from which the unit's schedules are noticeably off.
CLOCK_DRIFT_LIMIT = 300  # seconds

FILTERS = {
    "filter_due_device": "filter_remaining_device",
    "filter_due_outdoor": "filter_remaining_outdoor",
    "filter_due_room": "filter_remaining_room",
}
ISSUES = ["fault_active", "clock_drift", *FILTERS]


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
    data = entry.runtime_data.coordinator.data or {}

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
def async_delete_issues(hass: HomeAssistant, entry: MaicoConfigEntry) -> None:
    """Remove all issues of an entry, e.g. when it is unloaded."""
    for key in ISSUES:
        ir.async_delete_issue(hass, DOMAIN, _issue_id(entry, key))
