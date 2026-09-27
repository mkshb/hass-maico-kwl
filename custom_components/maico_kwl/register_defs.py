"""Register definitions for the Maico KWL Modbus map.

This module is intentionally free of Home Assistant imports so it can be unit
tested on its own. Everything here is derived from ``docs/modbus.csv``.

Conventions:
- All registers are holding registers, read with FC 03.
- The documented decimal "Modbus Code" is used directly as the protocol address
  (0-based). If a device turns out to be 1-based, adjust REGISTER_OFFSET.
- 32-bit values span two registers, High-Word first (big-endian).
- Many values are stored x10 and must be divided by 10 (``scale = 0.1``).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

REGISTER_OFFSET = 0

# Platform identifiers (kept as plain strings to stay HA-free).
SENSOR = "sensor"
BINARY_SENSOR = "binary_sensor"
NUMBER = "number"
SELECT = "select"
SWITCH = "switch"
BUTTON = "button"

# Date and time as six registers (year, month, day, hour, minute, second).
CLOCK = "clock"

# Entity categories (match HA's EntityCategory values).
CONFIG = "config"
DIAGNOSTIC = "diagnostic"

# Units (match HA unit constant values).
TEMP_C = "°C"
PERCENT = "%"
PPM = "ppm"
M3H = "m³/h"
RPM = "rpm"
SECONDS = "s"
DAYS = "d"
HOURS = "h"
MINUTES = "min"
MONTHS = "mo"

# A decoded register value: a number, or the unit's clock.
type RegisterValue = float | int | datetime

# Enum maps (raw value -> option slug). The slug is the canonical state stored by
# HA; its display text is translated via entity .../state/<slug> in the translation
# files (translations/en.json, translations/de.json).
LANGUAGE = {0: "german", 1: "english", 2: "french", 3: "italian"}
ROOM_TEMP_SOURCE = {0: "comfort_bde", 1: "external", 2: "internal", 3: "bus"}
OPERATING_MODE = {
    0: "off",
    1: "manual",
    2: "auto_time",
    3: "auto_sensor",
    4: "eco_supply_air",
    5: "eco_exhaust_air",
}
SEASON = {0: "winter", 1: "summer"}
VENT_LEVEL = {
    0: "off",
    1: "humidity_protection",
    2: "reduced",
    3: "nominal",
    4: "intensive",
}
PUMP_STATE = {0: "off", 1: "heating", 2: "cooling"}

# Bit meanings of the fault (401/402) and notice (403/404) codes (bit -> slug).
# The u32 value holds the High-Word (401/403) in bits 16-31. modbus.csv only says
# "Bitfeld"; the meanings come from docs/geniovent-modbus.csv, where list entry n
# is bit n-1 of its word. Verified on a live unit: notice bit 4 (bypass_active)
# follows the summer bypass.
FAULT_BITS = {
    0: "supply_fan",
    1: "exhaust_fan",
    2: "sensor_air_intake",
    3: "sensor_supply",
    4: "sensor_exhaust",
    5: "sensor_room_bde",
    6: "sensor_room",
    7: "sensor_outdoor_before_ehx",
    8: "bypass",
    9: "zone_damper",
    10: "combi_sensor",
    11: "frost_protection",
    12: "external_preheater",
    13: "supply_exhaust_too_cold",
    14: "sensor_room_bus",
    15: "communication_zp1",
    16: "communication_zp2",
    17: "sensor_extract",
    18: "communication_bde",
    19: "system_memory",
    20: "system_bus",
    21: "unknown_fault",
    22: "external_safety_shutdown",
}
NOTICE_BITS = {
    0: "brine_ehx_low_cooling",
    1: "communication_enocean",
    2: "communication_knx",
    3: "communication_air_at_home",
    4: "bypass_active",
    5: "zone_ventilation_active",
    6: "frost_protection_active",
    7: "frost_protection_airflow_reduced",
    8: "keypad_locked",
    9: "device_filter_dirty",
    10: "outdoor_filter_dirty",
    11: "room_filter_dirty",
    12: "airflow_calibration_active",
    13: "humidity_protection_active",
    14: "reheating_active",
    16: "door_contact_triggered",
    17: "external_safety_shutdown",
    18: "forced_ventilation_active",
    19: "communication_modbus",
    20: "switch_test_active",
    21: "filter_pressure_init_active",
    22: "pressure_setpoint_not_reached",
    23: "external_start_stop_active",
    24: "night_cooling_active",
    25: "purge_active",
    26: "motion_detector_active",
    27: "external_control_active",
    28: "airflow_balancing_active",
    29: "holiday_program_active",
    30: "sensor_mode_active",
}
ZONE_DAMPER = {0: "off", 1: "zone_1", 2: "zone_2", 3: "zone_sensor"}


@dataclass(frozen=True)
class RegisterDef:
    """A single Maico Modbus register mapped to one HA entity."""

    key: str
    address: int
    name: str
    platform: str
    data_type: str = "u16"  # u16 | s16 | u32 | s32 | clock
    scale: float = 1.0  # value = raw * scale
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    entity_category: str | None = None
    options: dict[int, str] | None = None
    writable: bool = False
    native_min: float | None = None
    native_max: float | None = None
    native_step: float | None = None
    press_value: int = 1  # value written by button entities
    enabled_default: bool = True
    # For write-only registers that cannot be read-probed: presence is inferred
    # from another register's presence (its key).
    probe_via: str | None = None
    # Write-only registers (read access "-" in the CSV) cannot be polled.
    readable: bool = True
    bits: dict[int, str] | None = None  # bitfield registers: bit -> slug

    @property
    def signed(self) -> bool:
        return self.data_type.startswith("s")

    @property
    def word_count(self) -> int:
        if self.data_type == CLOCK:
            return 6
        return 2 if self.data_type.endswith("32") else 1

    def decode(self, regs: list[int]) -> RegisterValue | None:
        """Combine raw registers into the real-world value."""
        if self.data_type == CLOCK:
            # Year, month, day, hour, minute, second in local time of the unit.
            try:
                year, month, day, hour, minute, second = regs[:6]
                return datetime(year, month, day, hour, minute, second)
            except (TypeError, ValueError):
                return None  # clock not set or invalid
        raw = 0
        for reg in regs[: self.word_count]:
            raw = (raw << 16) | (reg & 0xFFFF)
        total_bits = 16 * self.word_count
        if self.signed and raw >= (1 << (total_bits - 1)):
            raw -= 1 << total_bits
        if self.scale == 1.0:
            return raw
        return round(raw * self.scale, 3)

    @property
    def raw_range(self) -> tuple[int, int]:
        """The raw values the register's data type can hold."""
        total_bits = 16 * self.word_count
        if self.signed:
            return -(1 << (total_bits - 1)), (1 << (total_bits - 1)) - 1
        return 0, (1 << total_bits) - 1

    def encode(self, value: float | datetime) -> list[int]:
        """Turn a real-world value into the raw register words (High-Word first).

        Raises ValueError for a value the data type cannot hold, rather than
        cutting it to the register width and writing something else.
        """
        if isinstance(value, datetime):
            return [
                value.year, value.month, value.day,
                value.hour, value.minute, value.second,
            ]
        raw = int(round(value / self.scale))
        low, high = self.raw_range
        if not low <= raw <= high:
            raise ValueError(
                f"{value:g} does not fit register {self.address} ({self.data_type})"
            )
        total_bits = 16 * self.word_count
        if raw < 0:
            raw += 1 << total_bits
        return [
            (raw >> (16 * (self.word_count - 1 - i))) & 0xFFFF
            for i in range(self.word_count)
        ]

    def active_bits(self, value: float) -> list[str]:
        """Slugs of the set bits of a bitfield register, in bit order.

        Set bits without a documented meaning show up as ``bit_<n>``.
        """
        if self.bits is None:
            return []
        return [
            self.bits.get(bit, f"bit_{bit}")
            for bit in range(16 * self.word_count)
            if int(value) >> bit & 1
        ]

    def label_for(self, raw: int) -> str | None:
        """Map a raw enum value to its label (for select/enum sensors)."""
        if self.options is None:
            return None
        return self.options.get(raw)

    def raw_for_label(self, label: str) -> int | None:
        """Map an enum label back to its raw value (for select writes)."""
        if self.options is None:
            return None
        for raw, text in self.options.items():
            if text == label:
                return raw
        return None


def _enocean_bank(
    start: int, prefix: str, name: str, unit: str, dev_class: str, scale: float = 0.1
) -> list[RegisterDef]:
    return [
        RegisterDef(
            key=f"{prefix}_id{i}",
            address=start + i,
            name=f"{name} ID{i}",
            platform=SENSOR,
            scale=scale,
            unit=unit,
            device_class=dev_class,
            state_class="measurement",
            enabled_default=False,
        )
        for i in range(8)
    ]


def _sensor_bank(
    start: int, prefix: str, name: str, unit: str, dev_class: str, scale: float = 0.1
) -> list[RegisterDef]:
    return [
        RegisterDef(
            key=f"{prefix}_{i + 1}",
            address=start + i,
            name=f"{name} {i + 1}",
            platform=SENSOR,
            scale=scale,
            unit=unit,
            device_class=dev_class,
            state_class="measurement",
            enabled_default=False,
        )
        for i in range(4)
    ]


VOC = "volatile_organic_compounds_parts"

REGISTERS: list[RegisterDef] = [
    # --- Base settings (100-109) ---
    # Shown as the deviation from Home Assistant's clock: the time itself would
    # change the state on every poll and fill the logbook.
    RegisterDef("clock_deviation", 100, "Clock deviation", SENSOR,
                data_type=CLOCK, unit=SECONDS, device_class="duration",
                state_class="measurement", entity_category=DIAGNOSTIC),
    # Writes the current Home Assistant time to 100-105 in one FC 16 request.
    RegisterDef("clock_sync", 100, "Sync clock", BUTTON, data_type=CLOCK,
                writable=True, readable=False, entity_category=CONFIG,
                probe_via="clock_deviation"),
    RegisterDef("off_lock", 106, "Disable off level", SWITCH, writable=True,
                entity_category=CONFIG),
    RegisterDef("bde_lock", 107, "Lock control panel", SWITCH, writable=True,
                entity_category=CONFIG),
    RegisterDef("language", 108, "Language", SELECT, writable=True,
                entity_category=CONFIG, options=LANGUAGE),
    RegisterDef("room_temp_source", 109, "Room temperature source", SELECT,
                writable=True, entity_category=CONFIG, options=ROOM_TEMP_SOURCE),
    # --- Ventilation settings (150-159) ---
    RegisterDef("filter_runtime_device", 150, "Filter interval device", NUMBER,
                writable=True, unit=MONTHS, native_min=3, native_max=12,
                native_step=1, entity_category=CONFIG),
    RegisterDef("filter_runtime_outdoor", 151, "Filter interval outdoor", NUMBER,
                writable=True, unit=MONTHS, native_min=3, native_max=18,
                native_step=1, entity_category=CONFIG),
    RegisterDef("filter_runtime_room", 152, "Filter interval room", NUMBER,
                writable=True, unit=MONTHS, native_min=1, native_max=6,
                native_step=1, entity_category=CONFIG),
    RegisterDef("vent_level_duration", 153, "Ventilation level duration", NUMBER,
                writable=True, unit=MINUTES, native_min=5, native_max=90,
                native_step=1, entity_category=CONFIG),
    RegisterDef("airflow_reduced", 154, "Airflow reduced", NUMBER, writable=True,
                unit=M3H, device_class="volume_flow_rate", native_min=80,
                native_max=300, native_step=1, entity_category=CONFIG),
    RegisterDef("airflow_nominal", 155, "Airflow nominal", NUMBER, writable=True,
                unit=M3H, device_class="volume_flow_rate", native_min=80,
                native_max=300, native_step=1, entity_category=CONFIG),
    RegisterDef("airflow_intensive", 156, "Airflow intensive", NUMBER,
                writable=True, unit=M3H, device_class="volume_flow_rate",
                native_min=80, native_max=300, native_step=1,
                entity_category=CONFIG),
    RegisterDef("filter_reset_device", 157, "Reset device filter", BUTTON,
                writable=True, entity_category=CONFIG),
    RegisterDef("filter_reset_outdoor", 158, "Reset outdoor filter", BUTTON,
                writable=True, entity_category=CONFIG),
    RegisterDef("filter_reset_room", 159, "Reset room filter", BUTTON,
                writable=True, entity_category=CONFIG),
    # --- Temperature settings (300-302) ---
    RegisterDef("room_temp_offset", 300, "Room temperature offset", NUMBER,
                data_type="s16", scale=0.1, writable=True, unit=TEMP_C,
                device_class="temperature", native_min=-3, native_max=3,
                native_step=0.1, entity_category=CONFIG),
    # The CSV says "Schrittweite 1 (= 0,1°C)" here, but the Format column is
    # plain degC and a live unit reports 14 (= 14 degC in the range 8..29), so
    # the value is not scaled.
    RegisterDef("supply_temp_min_cooling", 301, "Supply temp min cooling", NUMBER,
                data_type="s16", writable=True, unit=TEMP_C,
                device_class="temperature", native_min=8, native_max=29,
                native_step=1, entity_category=CONFIG),
    RegisterDef("room_temp_max", 302, "Room temperature max", NUMBER,
                data_type="s16", scale=0.1, writable=True, unit=TEMP_C,
                device_class="temperature", native_min=18, native_max=30,
                native_step=0.5, entity_category=CONFIG),
    # --- EnOcean wireless sensors (350-373) ---
    *_enocean_bank(350, "enocean_co2", "EnOcean CO2", PPM, "carbon_dioxide"),
    *_enocean_bank(358, "enocean_humidity", "EnOcean humidity", PERCENT, "humidity",
                   scale=1.0),
    *_enocean_bank(366, "enocean_voc", "EnOcean VOC", PPM, VOC),
    # --- Errors / notices (401-405) ---
    RegisterDef("fault_code", 401, "Fault code", SENSOR, data_type="u32",
                entity_category=DIAGNOSTIC, bits=FAULT_BITS),
    RegisterDef("notice_code", 403, "Notice code", SENSOR, data_type="u32",
                entity_category=DIAGNOSTIC, bits=NOTICE_BITS),
    RegisterDef("error_reset", 405, "Reset errors", BUTTON, writable=True,
                readable=False, entity_category=DIAGNOSTIC,
                probe_via="fault_code"),
    # --- Main control (550-554) ---
    RegisterDef("operating_mode", 550, "Operating mode", SELECT, writable=True,
                options=OPERATING_MODE),
    RegisterDef("boost_ventilation", 551, "Boost ventilation", SWITCH,
                writable=True),
    RegisterDef("season", 552, "Season", SELECT, writable=True, options=SEASON),
    RegisterDef("room_setpoint", 553, "Room temperature setpoint", NUMBER,
                data_type="s16", scale=0.1, writable=True, unit=TEMP_C,
                device_class="temperature", native_min=18, native_max=25,
                native_step=0.5),
    RegisterDef("ventilation_level", 554, "Ventilation level", SELECT,
                writable=True, options=VENT_LEVEL),
    # --- Ventilation status (650-657) ---
    RegisterDef("current_vent_level", 650, "Current ventilation level", SENSOR,
                device_class="enum", options=VENT_LEVEL),
    RegisterDef("fan_speed_supply", 651, "Fan speed supply", SENSOR, unit=RPM,
                state_class="measurement"),
    RegisterDef("fan_speed_exhaust", 652, "Fan speed exhaust", SENSOR, unit=RPM,
                state_class="measurement"),
    RegisterDef("airflow_supply", 653, "Airflow supply", SENSOR, unit=M3H,
                device_class="volume_flow_rate", state_class="measurement"),
    RegisterDef("airflow_exhaust", 654, "Airflow exhaust", SENSOR, unit=M3H,
                device_class="volume_flow_rate", state_class="measurement"),
    RegisterDef("filter_remaining_device", 655, "Filter remaining device", SENSOR,
                unit=DAYS, device_class="duration", state_class="measurement"),
    RegisterDef("filter_remaining_outdoor", 656, "Filter remaining outdoor",
                SENSOR, unit=DAYS, device_class="duration",
                state_class="measurement"),
    RegisterDef("filter_remaining_room", 657, "Filter remaining room", SENSOR,
                unit=DAYS, device_class="duration", state_class="measurement"),
    # --- Live temperatures (700-706) ---
    RegisterDef("temp_room", 700, "Temperature room", SENSOR, data_type="s16",
                scale=0.1, unit=TEMP_C, device_class="temperature",
                state_class="measurement"),
    # Reading of a wired external room sensor (valid with room temperature
    # source "external"). The CSV lists it as writable, but a written value
    # would be overwritten by the sensor, so it stays read-only. Room
    # temperature fed over Modbus goes to 707 (room_temp_bus) instead.
    RegisterDef("temp_room_external", 701, "Temperature room external", SENSOR,
                data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement",
                enabled_default=False),
    RegisterDef("temp_outdoor_pre_egh", 702, "Temperature outdoor before EGH",
                SENSOR, data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement",
                enabled_default=False),
    RegisterDef("temp_air_intake", 703, "Temperature air intake", SENSOR,
                data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement"),
    RegisterDef("temp_supply_air", 704, "Temperature supply air", SENSOR,
                data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement"),
    RegisterDef("temp_extract_air", 705, "Temperature extract air", SENSOR,
                data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement"),
    RegisterDef("temp_exhaust_air", 706, "Temperature exhaust air", SENSOR,
                data_type="s16", scale=0.1, unit=TEMP_C,
                device_class="temperature", state_class="measurement"),
    # Write-only: room temperature fed in over Modbus ("Bus" source). Only used
    # by the device when room_temp_source (109) is set to "bus". Needs periodic
    # rewrites (device note: write cycle >= 10 min) -> handled in number.py.
    RegisterDef("room_temp_bus", 707, "Room temperature (bus)", NUMBER,
                data_type="s16", scale=0.1, writable=True, readable=False,
                unit=TEMP_C, device_class="temperature", native_min=0,
                native_max=40, native_step=0.1, probe_via="room_temp_source"),
    # --- Sensor data (750-762) ---
    RegisterDef("humidity_exhaust", 750, "Humidity exhaust", SENSOR, scale=1.0,
                unit=PERCENT, device_class="humidity", state_class="measurement"),
    *_sensor_bank(751, "humidity_sensor", "Humidity sensor", PERCENT, "humidity",
                  scale=1.0),
    *_sensor_bank(755, "co2_sensor", "CO2 sensor", PPM, "carbon_dioxide"),
    *_sensor_bank(759, "voc_sensor", "VOC sensor", PPM, VOC),
    # Write-only bus inputs (host feeds these; only used in "bus" sensor modes).
    # Note: humidity/air-quality here are NOT x10 (raw = real value).
    RegisterDef("humidity_bus", 763, "Humidity (bus)", NUMBER, data_type="u16",
                scale=1.0, writable=True, readable=False, unit=PERCENT,
                device_class="humidity", native_min=0, native_max=100,
                native_step=1, probe_via="room_temp_source"),
    RegisterDef("air_quality_bus", 764, "Air quality (bus)", NUMBER,
                data_type="u16", scale=1.0, writable=True, readable=False,
                unit=PPM, native_min=0, native_max=5000, native_step=1,
                probe_via="room_temp_source"),
    # --- Switch states (800-808) ---
    RegisterDef("fan_supply_active", 800, "Fan supply active", BINARY_SENSOR,
                device_class="running"),
    RegisterDef("fan_exhaust_active", 801, "Fan exhaust active", BINARY_SENSOR,
                device_class="running"),
    RegisterDef("summer_bypass_open", 802, "Summer bypass open", BINARY_SENSOR,
                device_class="opening"),
    RegisterDef("ptc_heater_active", 803, "PTC heater active", BINARY_SENSOR,
                device_class="running"),
    RegisterDef("base_board_contact", 804, "Base board contact", BINARY_SENSOR,
                entity_category=DIAGNOSTIC),
    RegisterDef("reheating_relay_active", 805, "Reheating relay active",
                BINARY_SENSOR, device_class="running", enabled_default=False),
    RegisterDef("brine_pump_state", 806, "Brine pump state", SENSOR,
                device_class="enum", options=PUMP_STATE, enabled_default=False),
    RegisterDef("three_way_damper_state", 807, "Three-way damper state", SENSOR,
                device_class="enum", options=PUMP_STATE, enabled_default=False),
    RegisterDef("zone_damper_state", 808, "Zone damper state", SENSOR,
                device_class="enum", options=ZONE_DAMPER, enabled_default=False),
    # --- Operating hours (850-869, u32 High/Low pairs) ---
    RegisterDef("op_hours_humidity_protection", 850,
                "Operating hours humidity protection", SENSOR, data_type="u32",
                unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC),
    RegisterDef("op_hours_reduced", 852, "Operating hours reduced", SENSOR,
                data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC),
    RegisterDef("op_hours_nominal", 854, "Operating hours nominal", SENSOR,
                data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC),
    RegisterDef("op_hours_intensive", 856, "Operating hours intensive", SENSOR,
                data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC),
    RegisterDef("op_hours_total", 858, "Operating hours total", SENSOR,
                data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC),
    RegisterDef("op_hours_reheating_relay", 860,
                "Operating hours reheating relay", SENSOR, data_type="u32",
                unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC,
                enabled_default=False),
    RegisterDef("op_hours_brine_pump", 862, "Operating hours brine pump", SENSOR,
                data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC,
                enabled_default=False),
    RegisterDef("op_hours_three_way_damper", 864,
                "Operating hours three-way damper", SENSOR, data_type="u32",
                unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC,
                enabled_default=False),
    RegisterDef("op_hours_zone_damper", 866, "Operating hours zone damper",
                SENSOR, data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC,
                enabled_default=False),
    RegisterDef("op_hours_switch_contact", 868, "Operating hours switch contact",
                SENSOR, data_type="u32", unit=HOURS, device_class="duration",
                state_class="total_increasing", entity_category=DIAGNOSTIC,
                enabled_default=False),
    # --- Filter monitoring (900) ---
    RegisterDef("filter_dp_allowed", 900, "Allowed filter delta-p", NUMBER,
                writable=True, unit=PERCENT, native_min=10, native_max=200,
                native_step=1, entity_category=CONFIG),
]

REGISTERS_BY_KEY: dict[str, RegisterDef] = {r.key: r for r in REGISTERS}

# Binary sensors for single bits of a bitfield register:
# (register key, bit slug, device class). The slug is also the entity key.
BIT_SENSORS: list[tuple[str, str, str | None]] = [
    ("notice_code", "device_filter_dirty", "problem"),
    ("notice_code", "outdoor_filter_dirty", "problem"),
    ("notice_code", "room_filter_dirty", "problem"),
    ("notice_code", "frost_protection_active", None),
]



# --- Accessories -------------------------------------------------------------
# Parts that are not fitted to every unit. Their registers answer on every
# unit, so the probe keeps them; the values tell whether the part is there
# (read once at discovery), and the user can correct that in the options.

type Values = dict[str, RegisterValue | None]


# Registers every Maico KWL has, with the values its documentation allows. A
# device at the configured address that reports others is not taken for a
# Maico KWL (e.g. another Modbus device got its IP address): it is not set up,
# and nothing is written to it.
IDENTITY_RANGES: dict[str, tuple[int, int]] = {
    "language": (0, 3),
    "room_temp_source": (0, 3),
    "operating_mode": (0, 5),
    "boost_ventilation": (0, 1),
    "season": (0, 1),
    "ventilation_level": (0, 4),
    "current_vent_level": (0, 4),
}


def identity_problem(values: Values) -> str | None:
    """Why the values do not look like a Maico KWL, or None.

    A missing value is no reason: it may just have failed to read.
    """
    for key, (low, high) in IDENTITY_RANGES.items():
        value = values.get(key)
        if isinstance(value, (int, float)) and not low <= value <= high:
            address = REGISTERS_BY_KEY[key].address
            return f"register {address} reads {value:g}, expected {low} to {high}"
    return None


def _filter_fitted(remaining: str, notice_bit: str) -> Callable[[Values], bool | None]:
    """A monitored filter has days left, or has run out and sets its notice bit.

    Without the filter the unit keeps the days at 0, never sets the bit and
    ignores a filter change.
    """

    def detect(values: Values) -> bool | None:
        days = values.get(remaining)
        notice = values.get("notice_code")
        if not isinstance(days, (int, float)) or not isinstance(notice, (int, float)):
            return None
        bits = REGISTERS_BY_KEY["notice_code"].active_bits(notice)
        return days > 0 or notice_bit in bits

    return detect


def _any_reading(keys: tuple[str, ...]) -> Callable[[Values], bool | None]:
    """A connected sensor reports a value; 0 % or 0 ppm means none is there."""

    def detect(values: Values) -> bool | None:
        readings = [values.get(key) for key in keys]
        if not all(isinstance(value, (int, float)) for value in readings):
            return None
        return any(readings)

    return detect


def _room_temp_external(values: Values) -> bool | None:
    """The external room sensor is only read with room temperature source "external"."""
    source = values.get("room_temp_source")
    if not isinstance(source, (int, float)):
        return None
    return ROOM_TEMP_SOURCE.get(int(source)) == "external"


@dataclass(frozen=True)
class Accessory:
    """A part that may not be fitted, and the registers that belong to it."""

    key: str  # option value and translation key
    keys: tuple[str, ...]
    # Registers read at discovery to detect the part, and the check on their
    # values: True/False, or None if it cannot tell (the part is kept then).
    sources: tuple[str, ...] = ()
    detect: Callable[[Values], bool | None] | None = None


_WIRED_SENSORS = tuple(
    f"{kind}_sensor_{i}" for kind in ("humidity", "co2", "voc") for i in range(1, 5)
)
_ENOCEAN = tuple(
    f"enocean_{kind}_id{i}" for kind in ("co2", "humidity", "voc") for i in range(8)
)

ACCESSORIES: list[Accessory] = [
    Accessory(
        "outdoor_filter",
        ("filter_runtime_outdoor", "filter_reset_outdoor", "filter_remaining_outdoor"),
        ("filter_remaining_outdoor", "notice_code"),
        _filter_fitted("filter_remaining_outdoor", "outdoor_filter_dirty"),
    ),
    Accessory(
        "room_filter",
        ("filter_runtime_room", "filter_reset_room", "filter_remaining_room"),
        ("filter_remaining_room", "notice_code"),
        _filter_fitted("filter_remaining_room", "room_filter_dirty"),
    ),
    Accessory("wired_sensors", _WIRED_SENSORS, _WIRED_SENSORS, _any_reading(_WIRED_SENSORS)),
    Accessory("enocean", _ENOCEAN, _ENOCEAN, _any_reading(_ENOCEAN)),
    Accessory(
        "external_room_sensor",
        ("temp_room_external",),
        ("room_temp_source",),
        _room_temp_external,
    ),
    Accessory("ptc_heater", ("ptc_heater_active",)),
    # ZP1 extension module, including the air ground heat exchanger sensor.
    Accessory(
        "zp1",
        (
            "temp_outdoor_pre_egh",
            "reheating_relay_active",
            "brine_pump_state",
            "three_way_damper_state",
            "zone_damper_state",
            "op_hours_reheating_relay",
            "op_hours_brine_pump",
            "op_hours_three_way_damper",
            "op_hours_zone_damper",
        ),
    ),
]
ACCESSORIES_BY_KEY: dict[str, Accessory] = {a.key: a for a in ACCESSORIES}

# Bit sensors that only exist together with another register.
BIT_SENSOR_REQUIRES: dict[str, str] = {
    "outdoor_filter_dirty": "filter_remaining_outdoor",
    "room_filter_dirty": "filter_remaining_room",
}
