"""Tests for register discovery and the capability profile."""

from __future__ import annotations

import pytest

from custom_components.maico_kwl.discovery import _derive_profile, async_discover
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

    async def busy_at_700(*, address, count, device_id):
        if address == 700:
            return FakeExceptionResponse(6)  # slave device busy
        return await original(address=address, count=count, device_id=device_id)

    device.clients[0].read_holding_registers = busy_at_700
    present, _ = await async_discover(hub)
    assert "temp_room" not in present
    assert "temp_supply_air" in present


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
        ({"co2_sensor_2"}, ["CO2"]),
        ({"voc_sensor_1"}, ["VOC"]),
        ({"summer_bypass_open", "ptc_heater_active"}, ["Summer bypass", "PTC heater"]),
        ({"zone_damper_state"}, ["ZP1"]),
    ],
)
def test_profile_features(present: set[str], features: list[str]) -> None:
    """Features are derived from the present registers."""
    profile = _derive_profile(present)
    assert profile["features"] == features
    if features:
        assert profile["model"] == f"Maico KWL ({', '.join(features)})"
    else:
        assert profile["model"] == "Maico KWL"
