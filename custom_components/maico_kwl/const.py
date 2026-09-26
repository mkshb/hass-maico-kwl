"""Constants for the Maico KWL integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TypedDict

DOMAIN = "maico_kwl"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_SCAN_INTERVAL = "scan_interval"

# Result of the last discovery, stored in the entry data (see discovery.py).
CONF_DISCOVERY = "discovery"

# Accessories the user marked as fitted (option). Only stored while it differs
# from the detected ones, so a later rediscovery still applies otherwise.
CONF_ACCESSORIES = "accessories"

# Optional source entities whose value is fed cyclically into a write-only
# "bus" input register.
CONF_ROOM_TEMP_SOURCE_ENTITY = "room_temp_source_entity"
CONF_HUMIDITY_SOURCE_ENTITY = "humidity_source_entity"
CONF_AIR_QUALITY_SOURCE_ENTITY = "air_quality_source_entity"

# (register key, option key, entity-selector device_class filter or None).
BUS_FEEDS: list[tuple[str, str, str | None]] = [
    ("room_temp_bus", CONF_ROOM_TEMP_SOURCE_ENTITY, "temperature"),
    ("humidity_bus", CONF_HUMIDITY_SOURCE_ENTITY, "humidity"),
    ("air_quality_bus", CONF_AIR_QUALITY_SOURCE_ENTITY, None),
]

# Bus input values expire on the unit unless written at least every 10
# minutes. Rewrite just under that so the value stays valid.
BUS_REWRITE_INTERVAL = timedelta(minutes=9)

DEFAULT_PORT = 502
DEFAULT_SLAVE = 10
DEFAULT_SCAN_INTERVAL = 30  # seconds


class MaicoProfile(TypedDict):
    """Capability profile derived from the present registers (discovery.py)."""

    model: str
    features: list[str]
    present_count: int
    total_count: int


MANUFACTURER = "Maico"
DEFAULT_NAME = "Maico KWL"

# Largest contiguous block of registers to read in one Modbus request.
MAX_BLOCK_SIZE = 100

PLATFORMS: list[str] = [
    "binary_sensor",
    "button",
    "fan",
    "number",
    "select",
    "sensor",
    "switch",
]
