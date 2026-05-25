"""Unit tests for the HA-free register decode/encode logic."""

import pathlib
import sys

# Import the module directly (not via the package) so the HA-dependent
# custom_components/maico_kwl/__init__.py is not executed.
_PKG = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "maico_kwl"
sys.path.insert(0, str(_PKG))

import register_defs as rd  # noqa: E402


def test_unsigned_scaling():
    reg = rd.REGISTERS_BY_KEY["co2_sensor_1"]  # u16, scale 0.1
    assert reg.decode([523]) == 52.3
    assert reg.encode(52.3) == [523]


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


if __name__ == "__main__":
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in funcs:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(funcs)} tests passed")
