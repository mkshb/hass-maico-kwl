"""Diagnostics for the Maico KWL integration.

Meant to be attached to bug reports and to requests for supporting other
Maico models: it shows which registers the unit answers to and what it
returned for them.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_HOST
from .coordinator import MaicoConfigEntry
from .register_defs import BUTTON, REGISTERS

# The default title contains the host as well.
TO_REDACT = {CONF_HOST, "title", "unique_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MaicoConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    data = coordinator.data or {}

    registers: dict[str, dict[str, Any]] = {}
    for reg in REGISTERS:
        if reg.key not in coordinator.present:
            continue
        info: dict[str, Any] = {"address": reg.address}
        if reg.platform == BUTTON or not reg.readable:
            info["polled"] = False  # commands and write-only bus inputs
        elif reg.key in data:
            value = data[reg.key]
            info["value"] = (
                value.isoformat() if isinstance(value, datetime) else value
            )
            if value is not None:
                # Raw words make scaling questions answerable from a report.
                info["raw"] = reg.encode(value)
        registers[reg.key] = info

    bus_inputs: dict[str, Any] = {}
    for reg in REGISTERS:
        sent = runtime.feeder.sent(reg.key)
        if sent is not None:
            bus_inputs[reg.key] = {
                "value": sent.value,
                "written_at": sent.written_at.isoformat(),
            }

    return {
        "entry": async_redact_data(
            {
                "title": entry.title,
                "unique_id": entry.unique_id,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            TO_REDACT,
        ),
        "profile": coordinator.profile,
        "last_update_success": coordinator.last_update_success,
        "registers": registers,
        "absent_registers": {
            reg.key: reg.address
            for reg in REGISTERS
            if reg.key not in coordinator.present
        },
        "bus_inputs": bus_inputs,
    }
