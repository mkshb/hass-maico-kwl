"""Unit tests for the HA-free register decode/encode logic."""

import pathlib
import sys
from datetime import datetime

# Import the module directly (not via the package) so the HA-dependent
# custom_components/maico_kwl/__init__.py is not executed.
_PKG = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "maico_kwl"
sys.path.insert(0, str(_PKG))

import register_defs as rd  # noqa: E402


def test_unsigned_scaling():
    reg = rd.REGISTERS_BY_KEY["co2_sensor_1"]  # u16, scale 0.1
    assert reg.decode([523]) == 52.3
    assert reg.encode(52.3) == [523]


def test_room_temp_bus_write_only():
    reg = rd.REGISTERS_BY_KEY["room_temp_bus"]  # write-only s16, scale 0.1
    assert reg.readable is False
    assert reg.writable is True
    assert reg.platform == rd.NUMBER
    assert reg.scale == 0.1
    assert reg.encode(21.5) == [215]
    assert reg.decode([0xFFD3]) == -4.5  # signed decode still works


def test_bus_inputs_write_only_unscaled():
    hum = rd.REGISTERS_BY_KEY["humidity_bus"]  # u16, scale 1.0
    assert hum.readable is False and hum.platform == rd.NUMBER
    assert hum.encode(44) == [44] and hum.decode([44]) == 44
    aq = rd.REGISTERS_BY_KEY["air_quality_bus"]  # u16, scale 1.0
    assert aq.readable is False and aq.platform == rd.NUMBER
    assert aq.encode(800) == [800] and aq.decode([800]) == 800


def test_humidity_unscaled():
    # This device returns humidity as a plain percent (not x10); see device memory.
    reg = rd.REGISTERS_BY_KEY["humidity_exhaust"]
    assert reg.scale == 1.0
    assert reg.decode([44]) == 44


def test_signed_negative_temperature():
    reg = rd.REGISTERS_BY_KEY["temp_room"]  # s16, scale 0.1
    assert reg.decode([0xFFD3]) == -4.5  # -45 raw
    assert reg.encode(-4.5) == [0xFFD3]


def test_signed_positive_temperature():
    reg = rd.REGISTERS_BY_KEY["temp_room"]
    assert reg.decode([215]) == 21.5
    assert reg.encode(21.5) == [215]


def test_u32_high_low_pair():
    reg = rd.REGISTERS_BY_KEY["op_hours_total"]  # u32
    assert reg.word_count == 2
    assert reg.decode([1, 5000]) == 70536  # (1<<16) + 5000
    assert reg.encode(70536) == [1, 5000]


def test_enum_roundtrip():
    reg = rd.REGISTERS_BY_KEY["operating_mode"]
    assert reg.label_for(3) == "auto_sensor"
    assert reg.raw_for_label("auto_sensor") == 3
    assert reg.raw_for_label("does not exist") is None


def test_all_keys_unique_and_addresses_valid():
    keys = [r.key for r in rd.REGISTERS]
    assert len(keys) == len(set(keys))
    for r in rd.REGISTERS:
        assert r.platform in {
            rd.SENSOR, rd.BINARY_SENSOR, rd.NUMBER, rd.SELECT, rd.SWITCH, rd.BUTTON
        }
        assert 0 <= r.address <= 65535
        if r.platform in {rd.SELECT}:
            assert r.options is not None


def test_writable_flags_match_platform():
    for r in rd.REGISTERS:
        if r.platform in {rd.NUMBER, rd.SELECT, rd.SWITCH, rd.BUTTON}:
            assert r.writable, f"{r.key} should be writable"


def test_probe_via_only_for_write_only_registers():
    """Registers that can't be read-probed are exactly the write-only ones."""
    for r in rd.REGISTERS:
        assert (r.probe_via is not None) == (not r.readable), r.key
        if r.probe_via is not None:
            assert rd.REGISTERS_BY_KEY[r.probe_via].readable, r.key


def test_clock_decode_encode():
    reg = rd.REGISTERS_BY_KEY["clock_deviation"]
    assert reg.word_count == 6
    words = [2026, 9, 26, 10, 30, 15]
    assert reg.decode(words) == datetime(2026, 9, 26, 10, 30, 15)
    assert reg.encode(datetime(2026, 9, 26, 10, 30, 15)) == words
    assert reg.decode([0, 0, 0, 0, 0, 0]) is None  # clock not set


def test_active_bits_of_bitfields():
    notice = rd.REGISTERS_BY_KEY["notice_code"]
    fault = rd.REGISTERS_BY_KEY["fault_code"]
    # Live unit: bit 4 (bypass) plus bit 13 in the low word (404).
    assert notice.active_bits(notice.decode([0, 0x2010])) == [
        "bypass_active",
        "humidity_protection_active",
    ]
    # High word (403) holds bits 16-31; undocumented bits keep their number.
    assert notice.active_bits(notice.decode([0x8001, 0x8000])) == [
        "bit_15",
        "door_contact_triggered",
        "bit_31",
    ]
    assert fault.active_bits(fault.decode([0x0040, 0x0001])) == [
        "supply_fan",
        "external_safety_shutdown",
    ]
    assert notice.active_bits(0) == []
    assert rd.REGISTERS_BY_KEY["temp_room"].active_bits(5) == []


def test_bit_sensors_use_documented_bits():
    for reg_key, slug, _dev_class in rd.BIT_SENSORS:
        assert slug in rd.REGISTERS_BY_KEY[reg_key].bits.values(), slug


if __name__ == "__main__":
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in funcs:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(funcs)} tests passed")
