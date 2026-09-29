"""Tests for register discovery and the capability profile."""

from __future__ import annotations

import pytest

from custom_components.maico_kwl.coordinator import build_blocks
from custom_components.maico_kwl.const import (
    CONF_ACCESSORIES,
    CONF_ACCESSORIES_OFFERED,
    CONF_DISCOVERY,
)
from custom_components.maico_kwl.discovery import (
    ACCESSORIES_UNTIL_0_4_0,
    active_accessories,
    async_discover,
    data_without_discovery,
    derive_profile,
    detected_accessories,
    offered_accessories,
    present_from_cache,
    registers_in_use,
)
from custom_components.maico_kwl.modbus_hub import MaicoConnectionError, MaicoModbusHub
from custom_components.maico_kwl.register_defs import (
    ACCESSORIES,
    REGISTERS,
    REGISTERS_BY_KEY,
)

from .conftest import HOST, PORT, SLAVE, FakeDevice, FakeExceptionResponse


@pytest.fixture
async def hub(device: FakeDevice) -> MaicoModbusHub:
    hub = MaicoModbusHub(HOST, PORT, SLAVE)
    assert await hub.connect()
    return hub


async def test_discovery_skips_absent_registers(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Registers answered with Illegal Data Address are not present."""
    present, accessories = await async_discover(hub)

    assert "temp_room" in present
    assert "op_hours_total" in present
    assert "enocean_co2_id0" not in present
    assert "co2_sensor_1" not in present
    assert "brine_pump_state" not in present
    # Accessories whose registers the unit rejects all are not offered, the
    # external room sensor is not used (source "internal"), ZP1 keeps 702.
    assert accessories == {"outdoor_filter", "room_filter", "ptc_heater", "zp1"}
    profile = derive_profile(present)
    assert profile["present_count"] == len(present)
    assert profile["total_count"] == len(REGISTERS)


async def test_discovery_write_only_registers_follow_sibling(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Write-only registers inherit presence from their probe_via sibling."""
    present, _ = await async_discover(hub)
    assert {"error_reset", "room_temp_bus", "humidity_bus"} <= present

    device.absent |= {401, 402, 109}
    present, _ = await async_discover(hub)
    assert "error_reset" not in present
    assert "room_temp_bus" not in present


async def test_discovery_unexpected_exception_code(
    hub: MaicoModbusHub, device: FakeDevice, caplog: pytest.LogCaptureFixture
) -> None:
    """An exception response that stays marks just that register as absent."""
    original = device.clients[0].read_holding_registers
    asked: list[int] = []

    async def failure_at_700(*, address, count, device_id):
        if address == 700:
            asked.append(count)
            return FakeExceptionResponse(4)  # slave device failure
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = failure_at_700
    present, _ = await async_discover(hub)
    assert "temp_room" not in present
    assert "temp_supply_air" in present
    assert asked == [7, 1, 1, 1]  # the block, then the register three times
    assert "Register 700 did not answer in 3 attempts" in caplog.text


async def test_discovery_asks_again_after_a_temporary_exception(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A gateway that fails once must not cost the register its entities."""
    original = device.clients[0].read_holding_registers
    failures = {700: 2}  # the block and the first single probe fail

    async def flaky(*, address, count, device_id):
        if failures.get(address):
            failures[address] -= 1
            return FakeExceptionResponse(4)
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = flaky
    present, _ = await async_discover(hub)
    assert "temp_room" in present


@pytest.mark.parametrize("code", [5, 6, 10, 11])
async def test_discovery_aborts_when_unit_or_gateway_is_busy(
    hub: MaicoModbusHub, device: FakeDevice, code: int
) -> None:
    """A busy unit or gateway says nothing about the register: retry later."""
    original = device.clients[0].read_holding_registers

    async def busy_at_650(*, address, count, device_id):
        if address == 650:
            return FakeExceptionResponse(code)
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = busy_at_650
    with pytest.raises(MaicoConnectionError):
        await async_discover(hub)


async def test_discovery_aborts_on_connection_loss(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A connection loss is raised instead of treated as absent."""
    device.fail_after_reads = 5
    with pytest.raises(MaicoConnectionError):
        await async_discover(hub)
    assert device.reads == 5


@pytest.mark.parametrize(
    ("present", "features"),
    [
        (set(), []),
        ({"enocean_humidity_id3"}, ["EnOcean"]),
        ({"enocean_co2_id0"}, ["EnOcean", "CO2"]),
        ({"enocean_co2_id5"}, ["EnOcean", "CO2"]),
        ({"enocean_voc_id2"}, ["EnOcean", "VOC"]),
        ({"co2_sensor_2"}, ["CO2"]),
        ({"voc_sensor_1"}, ["VOC"]),
        ({"summer_bypass_open", "ptc_heater_active"}, ["Summer bypass", "PTC heater"]),
        ({"zone_damper_state"}, ["ZP1"]),
    ],
)
def test_profile_features(present: set[str], features: list[str]) -> None:
    """Features are derived from the present registers."""
    profile = derive_profile(present)
    assert profile["features"] == features
    if features:
        assert profile["model"] == f"Maico KWL ({', '.join(features)})"
    else:
        assert profile["model"] == "Maico KWL"


async def test_discovery_reads_blocks(hub: MaicoModbusHub, device: FakeDevice) -> None:
    """A unit that answers everything is probed with one request per block."""
    device.absent = set()
    present, _ = await async_discover(hub)
    readable = [reg for reg in REGISTERS if reg.probe_via is None]
    assert present == {reg.key for reg in REGISTERS}
    # Plus one read per block of the values the accessories are detected by.
    sources = {key for acc in ACCESSORIES for key in acc.sources}
    detect_blocks = build_blocks([REGISTERS_BY_KEY[key] for key in sources])
    assert device.reads == len(build_blocks(readable)) + len(detect_blocks)
    assert device.reads < 20


async def test_discovery_rejected_block_probes_registers_singly(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """One missing register in a block does not hide its neighbours."""
    device.absent = {803}
    present, _ = await async_discover(hub)
    assert "ptc_heater_active" not in present
    assert {"fan_supply_active", "base_board_contact", "zone_damper_state"} <= present


async def test_discovery_probes_32_bit_registers_whole(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A missing low word drops the whole 32-bit counter, not half of it."""
    device.absent = {853}
    present, _ = await async_discover(hub)
    assert "op_hours_reduced" not in present
    assert {"op_hours_humidity_protection", "op_hours_nominal"} <= present



async def test_discovery_detects_filters_that_are_not_fitted(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """0 days left without a notice: the unit has no such filter."""
    device.registers[656] = 0
    present, accessories = await async_discover(hub)
    assert "filter_remaining_outdoor" in present  # it answers, but ...
    assert "outdoor_filter" not in accessories
    assert "room_filter" in accessories

    device.registers[657] = 0
    _, accessories = await async_discover(hub)
    assert not {"outdoor_filter", "room_filter"} & accessories


async def test_discovery_with_short_block_answers(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Short answers are probed singly and cannot mark an accessory as missing.

    With 0 days left the filters would count as not fitted, but the notice
    code (two registers) cannot be read, so the check cannot tell.
    """
    expected, _ = await async_discover(hub)
    device.registers[656] = 0
    device.registers[657] = 0
    device.short_blocks = True
    present, accessories = await async_discover(hub)
    assert present == expected - {
        reg.key for reg in REGISTERS if reg.word_count > 1 and reg.probe_via is None
    } - {"error_reset", "clock_sync"}
    assert {"outdoor_filter", "room_filter"} <= accessories


async def test_discovery_keeps_filters_that_ran_out(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A fitted filter that ran out sets its notice bit and is kept."""
    device.registers[656] = 0
    device.registers[657] = 0
    device.registers[404] = (1 << 10) | (1 << 11)  # outdoor and room filter dirty
    _, accessories = await async_discover(hub)
    assert {"outdoor_filter", "room_filter"} <= accessories


async def test_discovery_keeps_filters_detected_before(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """0 days without a notice bit: a filter detected before has run out.

    Sensors reading 0 are not kept: a reading tells them apart.
    """
    device.registers[656] = 0
    device.registers[657] = 0
    before = {"outdoor_filter", "room_filter", "wired_sensors"}
    _, accessories = await async_discover(hub, {"outdoor_filter", "wired_sensors"})
    assert "outdoor_filter" in accessories
    assert "room_filter" not in accessories
    assert "wired_sensors" not in accessories  # its registers answer, all 0
    _, accessories = await async_discover(hub, before)
    assert {"outdoor_filter", "room_filter"} <= accessories


def test_data_without_discovery_keeps_the_detected_accessories() -> None:
    """For the same unit only; what stays is no valid discovery."""
    data = {
        "host": HOST,
        CONF_DISCOVERY: {"version": 2, "present": ["temp_room"], "accessories": ["room_filter"]},
    }
    kept = data_without_discovery(data)
    assert kept == {"host": HOST, CONF_DISCOVERY: {"accessories": ["room_filter"]}}
    assert present_from_cache(kept[CONF_DISCOVERY]) is None
    assert detected_accessories(kept[CONF_DISCOVERY]) == {"room_filter"}
    assert data_without_discovery(data, same_unit=False) == {"host": HOST}
    assert data_without_discovery({"host": HOST}) == {"host": HOST}
    assert detected_accessories({"accessories": "room_filter"}) == set()


async def test_discovery_detects_sensors_and_room_temp_source(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Sensors count as fitted once one of them reports a value."""
    device.absent = set()
    _, accessories = await async_discover(hub)
    # All sensor readings 0, room temperature from the internal sensor.
    assert not {"wired_sensors", "enocean", "external_room_sensor"} & accessories
    # Not detectable from values: kept.
    assert {"ptc_heater", "zp1"} <= accessories

    device.registers[758] = 6500  # CO2 sensor 4: 650 ppm
    device.registers[361] = 48  # EnOcean humidity ID3
    device.registers[109] = 1  # room temperature from the external sensor
    _, accessories = await async_discover(hub)
    assert {"wired_sensors", "enocean", "external_room_sensor"} <= accessories


async def test_discovery_keeps_accessories_it_cannot_check(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Without the notice code, or if a value cannot be read, they are kept."""
    device.registers[656] = 0
    device.absent |= {403, 404}
    present, accessories = await async_discover(hub)
    assert "notice_code" not in present
    assert "outdoor_filter" in accessories

    device.absent -= {403, 404}
    original = device.clients[0].read_holding_registers

    async def failure_at_656(*, address, count, device_id):
        if address == 656:
            return FakeExceptionResponse(4)
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = failure_at_656
    _, accessories = await async_discover(hub)
    assert "outdoor_filter" in accessories


async def test_discovery_accessory_check_aborts_on_connection_loss(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A connection loss while checking the accessories aborts the discovery."""
    readable = [reg for reg in REGISTERS if reg.probe_via is None]
    device.fail_after_reads = len(build_blocks(readable)) + 1
    device.absent = set()
    with pytest.raises(MaicoConnectionError):
        await async_discover(hub)


def test_registers_in_use_and_active_accessories() -> None:
    """The user's choice wins over the detected accessories."""
    cache = {"accessories": ["room_filter", "zp1"]}
    assert active_accessories(cache, {}) == {"room_filter", "zp1"}
    assert active_accessories({}, {}) == set()
    # A choice made with 0.4.0 or older covers all accessories known then.
    assert active_accessories(cache, {CONF_ACCESSORIES: []}) == set()


def test_choice_covers_only_the_accessories_offered_with_it() -> None:
    """What the unit answers to only later is decided by detection."""
    cache = {"accessories": ["room_filter", "enocean", "future"]}
    options = {
        CONF_ACCESSORIES: ["outdoor_filter"],
        CONF_ACCESSORIES_OFFERED: ["outdoor_filter", "room_filter"],
    }
    # room_filter was offered and left out: stays out. enocean was not
    # offered then (fitted later), "future" is new in a later version.
    assert active_accessories(cache, options) == {"outdoor_filter", "enocean", "future"}
    # Without the offered ones (choice from 0.4.0 or older) only new
    # accessories are left to detection.
    del options[CONF_ACCESSORIES_OFFERED]
    assert active_accessories(cache, options) == {"outdoor_filter", "future"}


def test_accessories_until_0_4_0_exist() -> None:
    """The list must name real accessories, or old choices would widen."""
    assert ACCESSORIES_UNTIL_0_4_0 <= {acc.key for acc in ACCESSORIES}

    present = {"temp_room", "filter_remaining_outdoor", "filter_remaining_room"}
    assert registers_in_use(present, {"room_filter"}) == {
        "temp_room",
        "filter_remaining_room",
    }
    assert offered_accessories(present) == {"outdoor_filter", "room_filter"}
