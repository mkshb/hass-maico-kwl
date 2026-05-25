"""Constants for the Maico KWL integration."""

from __future__ import annotations

DOMAIN = "maico_kwl"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_SCAN_INTERVAL = "scan_interval"

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
