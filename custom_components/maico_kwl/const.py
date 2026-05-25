"""Constants for the Maico KWL integration."""

from __future__ import annotations

DOMAIN = "maico_kwl"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_SCAN_INTERVAL = "scan_interval"

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

DEFAULT_PORT = 502
DEFAULT_SLAVE = 10
DEFAULT_SCAN_INTERVAL = 30  # seconds

MANUFACTURER = "Maico"
DEFAULT_NAME = "Maico KWL"

# Largest contiguous block of registers to read in one Modbus request.
MAX_BLOCK_SIZE = 100

PLATFORMS: list[str] = [
    "binary_sensor",
    "button",
    "number",
    "select",
    "sensor",
    "switch",
]
