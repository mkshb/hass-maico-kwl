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

from dataclasses import dataclass, field

REGISTER_OFFSET = 0

# Platform identifiers (kept as plain strings to stay HA-free).
SENSOR = "sensor"
BINARY_SENSOR = "binary_sensor"
NUMBER = "number"
SELECT = "select"
SWITCH = "switch"
BUTTON = "button"

# Entity categories (match HA's EntityCategory values).
CONFIG = "config"
DIAGNOSTIC = "diagnostic"

# Units (match HA unit constant values).
TEMP_C = "°C"
PERCENT = "%"
PPM = "ppm"
M3H = "m³/h"
RPM = "rpm"
DAYS = "d"
HOURS = "h"
MINUTES = "min"
MONTHS = "mo"
WATT = "W"

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
ZONE_DAMPER = {0: "off", 1: "zone_1", 2: "zone_2", 3: "zone_sensor"}


@dataclass(frozen=True)
class RegisterDef:
    """A single Maico Modbus register mapped to one HA entity."""

    key: str
    address: int
    name: str
    platform: str
    data_type: str = "u16"  # u16 | s16 | u32 | s32
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
    icon: str | None = None
    enabled_default: bool = True
    # For write-only registers that cannot be read-probed: presence is inferred
    # from another register's presence (its key).
    probe_via: str | None = None
    # Write-only registers (read access "-" in the CSV) cannot be polled.
    readable: bool = True
    bits: tuple = field(default=())  # reserved; unused for now

    @property
    def signed(self) -> bool:
        return self.data_type.startswith("s")

    @property
    def word_count(self) -> int:
        return 2 if self.data_type.endswith("32") else 1

    def decode(self, regs: list[int]) -> float | int:
        """Combine raw registers into the real-world value."""
        raw = 0
        for reg in regs[: self.word_count]:
            raw = (raw << 16) | (reg & 0xFFFF)
        total_bits = 16 * self.word_count
        if self.signed and raw >= (1 << (total_bits - 1)):
            raw -= 1 << total_bits
        if self.scale == 1.0:
            return raw
        return round(raw * self.scale, 3)

    def encode(self, value: float) -> list[int]:
        """Turn a real-world value into the raw register words (High-Word first)."""
        raw = int(round(value / self.scale))
        total_bits = 16 * self.word_count
        if raw < 0:
            raw += 1 << total_bits
        raw &= (1 << total_bits) - 1
        return [
            (raw >> (16 * (self.word_count - 1 - i))) & 0xFFFF
            for i in range(self.word_count)
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
):
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
):
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
    RegisterDef("off_lock", 106, "Disable off level", SWITCH, writable=True,
                entity_category=CONFIG, icon="mdi:fan-off"),
    RegisterDef("bde_lock", 107, "Lock control panel", SWITCH, writable=True,
                entity_category=CONFIG, icon="mdi:lock"),
    RegisterDef("language", 108, "Language", SELECT, writable=True,
                entity_category=CONFIG, options=LANGUAGE),
    RegisterDef("room_temp_source", 109, "Room temperature source", SELECT,
                writable=True, entity_category=CONFIG, options=ROOM_TEMP_SOURCE),
    # --- Ventilation settings (150-159) ---
    RegisterDef("filter_runtime_device", 150, "Filter interval device", NUMBER,
                writable=True, unit=MONTHS, native_min=3, native_max=12,
                native_step=1, entity_category=CONFIG, icon="mdi:air-filter"),
    RegisterDef("filter_runtime_outdoor", 151, "Filter interval outdoor", NUMBER,
                writable=True, unit=MONTHS, native_min=3, native_max=18,
                native_step=1, entity_category=CONFIG, icon="mdi:air-filter"),
    RegisterDef("filter_runtime_room", 152, "Filter interval room", NUMBER,
                writable=True, unit=MONTHS, native_min=1, native_max=6,
                native_step=1, entity_category=CONFIG, icon="mdi:air-filter"),
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
                writable=True, entity_category=CONFIG, icon="mdi:restart"),
    RegisterDef("filter_reset_outdoor", 158, "Reset outdoor filter", BUTTON,
                writable=True, entity_category=CONFIG, icon="mdi:restart"),
    RegisterDef("filter_reset_room", 159, "Reset room filter", BUTTON,
                writable=True, entity_category=CONFIG, icon="mdi:restart"),
    # --- Temperature settings (300-302) ---
    RegisterDef("room_temp_offset", 300, "Room temperature offset", NUMBER,
                data_type="s16", scale=0.1, writable=True, unit=TEMP_C,
                device_class="temperature", native_min=-3, native_max=3,
                native_step=0.1, entity_category=CONFIG),
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
                entity_category=DIAGNOSTIC, icon="mdi:alert-circle"),
    RegisterDef("notice_code", 403, "Notice code", SENSOR, data_type="u32",
                entity_category=DIAGNOSTIC, icon="mdi:information"),
    RegisterDef("error_reset", 405, "Reset errors", BUTTON, writable=True,
                entity_category=DIAGNOSTIC, icon="mdi:restart-alert",
                probe_via="fault_code"),
    # --- Main control (550-554) ---
    RegisterDef("operating_mode", 550, "Operating mode", SELECT, writable=True,
                options=OPERATING_MODE, icon="mdi:fan-auto"),
    RegisterDef("boost_ventilation", 551, "Boost ventilation", SWITCH,
                writable=True, icon="mdi:fan-plus"),
    RegisterDef("season", 552, "Season", SELECT, writable=True, options=SEASON),
    RegisterDef("room_setpoint", 553, "Room temperature setpoint", NUMBER,
                data_type="s16", scale=0.1, writable=True, unit=TEMP_C,
                device_class="temperature", native_min=18, native_max=25,
                native_step=0.5),
    RegisterDef("ventilation_level", 554, "Ventilation level", SELECT,
                writable=True, options=VENT_LEVEL, icon="mdi:fan"),
    # --- Ventilation status (650-657) ---
    RegisterDef("current_vent_level", 650, "Current ventilation level", SENSOR,
                device_class="enum", options=VENT_LEVEL, icon="mdi:fan"),
    RegisterDef("fan_speed_supply", 651, "Fan speed supply", SENSOR, unit=RPM,
                state_class="measurement", icon="mdi:fan"),
    RegisterDef("fan_speed_exhaust", 652, "Fan speed exhaust", SENSOR, unit=RPM,
                state_class="measurement", icon="mdi:fan"),
    RegisterDef("airflow_supply", 653, "Airflow supply", SENSOR, unit=M3H,
                device_class="volume_flow_rate", state_class="measurement"),
    RegisterDef("airflow_exhaust", 654, "Airflow exhaust", SENSOR, unit=M3H,
                device_class="volume_flow_rate", state_class="measurement"),
    RegisterDef("filter_remaining_device", 655, "Filter remaining device", SENSOR,
                unit=DAYS, device_class="duration", state_class="measurement",
                icon="mdi:air-filter"),
    RegisterDef("filter_remaining_outdoor", 656, "Filter remaining outdoor",
                SENSOR, unit=DAYS, device_class="duration",
                state_class="measurement", icon="mdi:air-filter"),
    RegisterDef("filter_remaining_room", 657, "Filter remaining room", SENSOR,
                unit=DAYS, device_class="duration", state_class="measurement",
                icon="mdi:air-filter"),
    # --- Live temperatures (700-706) ---
    RegisterDef("temp_room", 700, "Temperature room", SENSOR, data_type="s16",
                scale=0.1, unit=TEMP_C, device_class="temperature",
                state_class="measurement"),
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
                native_max=40, native_step=0.1, probe_via="room_temp_source",
                icon="mdi:thermometer"),
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
                native_step=1, probe_via="room_temp_source",
                icon="mdi:water-percent"),
    RegisterDef("air_quality_bus", 764, "Air quality (bus)", NUMBER,
                data_type="u16", scale=1.0, writable=True, readable=False,
                unit=PPM, native_min=0, native_max=5000, native_step=1,
                probe_via="room_temp_source", icon="mdi:air-filter"),
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
                native_step=1, entity_category=CONFIG, icon="mdi:gauge"),
]

REGISTERS_BY_KEY: dict[str, RegisterDef] = {r.key: r for r in REGISTERS}

# --- Derived entities -------------------------------------------------------
# The Maico Modbus map has no register for the recovered heat, although the
# vendor app displays it. It is computed from the supply airflow and the
# temperature rise across the exchanger, so it is defined here as a pseudo
# register (no address, never polled) and calculated in sensor.py.
HEAT_RECOVERY_SOURCES = ("airflow_supply", "temp_air_intake", "temp_supply_air")

# Volumetric heat capacity of air in Wh/(m3*K); airflow is reported in m3/h,
# so P[W] = flow[m3/h] * 0.34 * dT[K].
AIR_HEAT_CAPACITY = 0.34

DERIVED_HEAT_RECOVERY = RegisterDef(
    "heat_recovery_power", -1, "Heat recovery power", SENSOR, unit=WATT,
    device_class="power", state_class="measurement", readable=False,
    icon="mdi:heat-wave",
)
