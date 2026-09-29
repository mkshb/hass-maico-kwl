"""Logbook descriptions for the bus input activity (EVENT_BUS_INPUT).

The entries appear on the device page under Activity. Logbook messages are not
translated by Home Assistant, so the texts follow the configured language here
(German or English).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.components.logbook.const import (
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const import (
    BUS_EXPIRED,
    BUS_FAILED,
    BUS_RECOVERED,
    BUS_SENT,
    BUS_SKIPPED,
    DEFAULT_NAME,
    DOMAIN,
    EVENT_BUS_INPUT,
)

INPUT_NAMES = {
    "en": {
        "room_temp_bus": "room temperature",
        "humidity_bus": "humidity",
        "air_quality_bus": "air quality",
    },
    "de": {
        "room_temp_bus": "Raumtemperatur",
        "humidity_bus": "Feuchte",
        "air_quality_bus": "Luftgüte",
    },
}

MESSAGES = {
    "en": {
        BUS_SENT: "sent {input} {value} to the bus (source {source})",
        BUS_SKIPPED: "does not send {input} from {source}: {reason}",
        BUS_FAILED: "could not send {input} to the bus: {error}",
        BUS_RECOVERED: "sends {input} to the bus again",
        BUS_EXPIRED: (
            "has had no valid {input} from the bus for 10 minutes, "
            "the unit uses its own sensor"
        ),
    },
    "de": {
        BUS_SENT: "hat {input} {value} an den Bus gesendet (Quelle {source})",
        BUS_SKIPPED: "sendet {input} von {source} nicht: {reason}",
        BUS_FAILED: "konnte {input} nicht an den Bus senden: {error}",
        BUS_RECOVERED: "sendet {input} wieder an den Bus",
        BUS_EXPIRED: (
            "hat seit 10 Minuten keinen gültigen Wert für {input} vom Bus, "
            "das Gerät nutzt seinen eigenen Sensor"
        ),
    },
}


def _format_value(value: Any, unit: Any, language: str) -> str:
    if not isinstance(value, (int, float)):
        return "?"
    text = f"{value:g}"
    if language == "de":
        text = text.replace(".", ",")
    return f"{text} {unit}" if unit else text


def describe_bus_event(
    language: str, name: str, data: Mapping[str, Any]
) -> dict[str, str]:
    """The logbook entry for the data of an EVENT_BUS_INPUT."""
    lang = "de" if language.lower().startswith("de") else "en"
    key = data.get("input", "")
    template = MESSAGES[lang].get(data.get("kind", ""))
    fields = {
        "input": INPUT_NAMES[lang].get(key, key),
        "value": _format_value(data.get("value"), data.get("unit"), lang),
        "source": data.get("source", "?"),
        "reason": data.get("reason", "?"),
        "error": data.get("error", "?"),
    }
    message = template.format(**fields) if template else str(data.get("kind"))
    return {LOGBOOK_ENTRY_NAME: name, LOGBOOK_ENTRY_MESSAGE: message}


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[
        [str, str, Callable[[Event], dict[str, str]]], None
    ],
) -> None:
    """Describe the bus input events for the logbook."""

    @callback
    def describe(event: Event) -> dict[str, str]:
        name = DEFAULT_NAME
        if (device_id := event.data.get("device_id")) and (
            device := dr.async_get(hass).async_get(device_id)
        ):
            name = device.name_by_user or device.name or name
        return describe_bus_event(hass.config.language, name, event.data)

    async_describe_event(DOMAIN, EVENT_BUS_INPUT, describe)
