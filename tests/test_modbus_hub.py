"""Tests for the Modbus hub on top of the fake Modbus connection."""

from __future__ import annotations

import pytest
from modbus_connection import ModbusDesyncError

from custom_components.maico_kwl.modbus_hub import (
    MaicoConnectionError,
    MaicoModbusError,
    MaicoModbusHub,
)

from .conftest import FakeDevice, FakeExceptionResponse, fake_hub


@pytest.fixture
async def hub(device: FakeDevice) -> MaicoModbusHub:
    return fake_hub(device)


async def test_read_block(hub: MaicoModbusHub) -> None:
    assert await hub.read_block(553, 2) == [215, 3]


async def test_read_block_exception_response(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A rejected read is a MaicoModbusError, not a connection error."""
    with pytest.raises(MaicoModbusError) as err:
        await hub.read_block(350, 1)
    assert not isinstance(err.value, MaicoConnectionError)


@pytest.mark.parametrize(
    ("code", "result"),
    [
        (1, False),
        (2, False),
        (3, False),
        (4, MaicoModbusError),
        (5, MaicoConnectionError),
        (6, MaicoConnectionError),
        (10, MaicoConnectionError),
        (11, MaicoConnectionError),
        (99, MaicoModbusError),
    ],
)
async def test_probe_exception_codes(
    hub: MaicoModbusHub, device: FakeDevice, code: int, result: object
) -> None:
    """0x01 to 0x03: absent; busy or gateway codes: try again; others: rejected."""

    async def answer(*, address, count, device_id):
        return FakeExceptionResponse(code)

    device.clients[0].read_holding_registers = answer
    if result is False:
        assert await hub.probe(700) is False
        return
    with pytest.raises(MaicoModbusError) as err:
        await hub.probe(700)
    assert isinstance(err.value, MaicoConnectionError) is (
        result is MaicoConnectionError
    )


async def test_protocol_error_is_a_connection_error(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """An answer that does not fit the request says nothing about the register."""

    async def garbled(*, address, count, device_id):
        raise ModbusDesyncError("simulated: transaction id mismatch")

    device.clients[0].read_holding_registers = garbled
    with pytest.raises(MaicoConnectionError):
        await hub.probe(700)


async def test_write_single_and_multiple(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """One value uses FC 06, several values FC 16 (High-Word first)."""
    await hub.write(553, [220])
    await hub.write(858, [0x0001, 0x0002])
    assert device.writes == [(553, [220]), (858, [1, 2])]


async def test_write_exception_response(hub: MaicoModbusHub, device: FakeDevice) -> None:
    device.write_exception = 4
    with pytest.raises(MaicoModbusError) as err:
        await hub.write(553, [220])
    assert not isinstance(err.value, MaicoConnectionError)


async def test_reconnects_after_connection_loss(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A dropped link is reopened on the next request, or reported."""
    assert await hub.read_block(700, 1) == [215]
    device.clients[0].drop()
    assert await hub.read_block(700, 1) == [215]

    device.clients[0].drop()
    device.online = False
    with pytest.raises(MaicoConnectionError, match="cannot connect"):
        await hub.write(553, [220])
    with pytest.raises(MaicoConnectionError, match="cannot connect"):
        await hub.read_block(700, 1)


async def test_closed_hub_sends_nothing(hub: MaicoModbusHub, device: FakeDevice) -> None:
    """After unload, the shared connection may stay open for another holder."""
    hub.close()
    with pytest.raises(MaicoConnectionError, match="closed"):
        await hub.read_block(700, 1)
    with pytest.raises(MaicoConnectionError, match="closed"):
        await hub.write(553, [220])
    assert device.reads == 0
    assert not device.writes


async def test_short_answer_is_a_rejected_read(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """Missing registers must not decode as 0, and are no connection loss."""
    device.short_blocks = True
    with pytest.raises(MaicoModbusError) as err:
        await hub.read_block(553, 2)
    assert not isinstance(err.value, MaicoConnectionError)
    with pytest.raises(MaicoModbusError) as err:
        await hub.probe(553, 2)
    assert not isinstance(err.value, MaicoConnectionError)
    assert await hub.read_block(553, 1) == [215]
