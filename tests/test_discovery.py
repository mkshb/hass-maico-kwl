"""Tests for register discovery and the capability profile."""

from __future__ import annotations

import pytest

from custom_components.maico_kwl.coordinator import build_blocks
from custom_components.maico_kwl.discovery import async_discover, derive_profile
from custom_components.maico_kwl.modbus_hub import MaicoConnectionError, MaicoModbusHub
from custom_components.maico_kwl.register_defs import REGISTERS

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
    present, profile = await async_discover(hub)

    assert "temp_room" in present
    assert "op_hours_total" in present
    assert "enocean_co2_id0" not in present
    assert "co2_sensor_1" not in present
    assert "brine_pump_state" not in present
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
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Any other exception response marks just that register as absent."""
    original = device.clients[0].read_holding_registers

    async def failure_at_700(*, address, count, device_id):
        if address == 700:
            return FakeExceptionResponse(4)  # slave device failure
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = failure_at_700
    present, _ = await async_discover(hub)
    assert "temp_room" not in present
    assert "temp_supply_air" in present


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
    # Plus the notice code and the remaining days of the two optional filters.
    assert device.reads == len(build_blocks(readable)) + 3
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


OUTDOOR_FILTER = {"filter_runtime_outdoor", "filter_reset_outdoor", "filter_remaining_outdoor"}
ROOM_FILTER = {"filter_runtime_room", "filter_reset_room", "filter_remaining_room"}


async def test_discovery_skips_filters_that_are_not_fitted(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """0 days left without a notice: the unit has no such filter."""
    device.registers[656] = 0
    present, _ = await async_discover(hub)
    assert not OUTDOOR_FILTER & present
    assert ROOM_FILTER <= present
    assert {"filter_runtime_device", "filter_reset_device"} <= present

    device.registers[657] = 0
    present, _ = await async_discover(hub)
    assert not (OUTDOOR_FILTER | ROOM_FILTER) & present
    assert "filter_remaining_device" in present


async def test_discovery_keeps_filters_that_ran_out(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A fitted filter that ran out sets its notice bit and is kept."""
    device.registers[656] = 0
    device.registers[657] = 0
    device.registers[404] = (1 << 10) | (1 << 11)  # outdoor and room filter dirty
    present, _ = await async_discover(hub)
    assert (OUTDOOR_FILTER | ROOM_FILTER) <= present


async def test_discovery_keeps_filters_it_cannot_check(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Without the notice code, or if a value cannot be read, all filters stay."""
    device.registers[656] = 0
    device.absent |= {403, 404}
    present, _ = await async_discover(hub)
    assert "notice_code" not in present
    assert OUTDOOR_FILTER <= present

    device.absent -= {403, 404}
    original = device.clients[0].read_holding_registers

    async def failure_at_656(*, address, count, device_id):
        if address == 656 and count == 1:
            return FakeExceptionResponse(4)
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = failure_at_656
    present, _ = await async_discover(hub)
    assert OUTDOOR_FILTER <= present


async def test_discovery_filter_check_aborts_on_connection_loss(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A connection loss while checking the filters aborts the discovery."""
    readable = [reg for reg in REGISTERS if reg.probe_via is None]
    device.fail_after_reads = len(build_blocks(readable)) + 1
    device.absent = set()
    with pytest.raises(MaicoConnectionError):
        await async_discover(hub)
