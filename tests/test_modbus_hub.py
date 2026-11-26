"""Tests for the Modbus hub on top of the fake Modbus connection."""

from __future__ import annotations

import asyncio

import pytest
from modbus_connection import ModbusDesyncError

from custom_components.maico_kwl.modbus_hub import (
    MaicoConnectionError,
    MaicoModbusError,
    MaicoModbusHub,
)

from .conftest import SLAVE, FakeConnection, FakeDevice, FakeExceptionResponse, fake_hub


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


def _gap_hub(device: FakeDevice, gap: float) -> MaicoModbusHub:
    return MaicoModbusHub(FakeConnection(device).for_unit(SLAVE), gap)


async def test_writes_wait_for_the_gap(device: FakeDevice) -> None:
    """The first write goes out at once, the next one after the gap."""
    hub = _gap_hub(device, 0.2)
    loop = asyncio.get_running_loop()
    start = loop.time()
    await hub.write(154, [80])
    assert loop.time() - start < 0.1
    # Reads are not held back.
    assert await hub.read_block(154, 1) == [80]
    assert loop.time() - start < 0.1
    await hub.write(155, [120])
    assert loop.time() - start >= 0.2
    assert device.writes == [(154, [80]), (155, [120])]


async def test_writes_go_out_one_at_a_time(device: FakeDevice) -> None:
    """Writes started together are sent in turn, each after the gap."""
    hub = _gap_hub(device, 0.1)
    loop = asyncio.get_running_loop()
    start = loop.time()
    await asyncio.gather(
        hub.write(154, [80]), hub.write(155, [120]), hub.write(156, [160])
    )
    assert loop.time() - start >= 0.2
    assert device.writes == [(154, [80]), (155, [120]), (156, [160])]


async def test_failed_write_counts_for_the_gap(device: FakeDevice) -> None:
    """The unit may have received a write that ended in an error."""
    hub = _gap_hub(device, 0.2)
    loop = asyncio.get_running_loop()
    device.write_exception = 4
    with pytest.raises(MaicoModbusError):
        await hub.write(154, [80])
    device.write_exception = None
    start = loop.time()
    await hub.write(154, [80])
    assert loop.time() - start >= 0.15


async def test_close_ends_the_wait(device: FakeDevice) -> None:
    """A write waiting for its turn gives up when the entry is unloaded."""
    hub = _gap_hub(device, 30)
    await hub.write(154, [80])
    waiting = asyncio.ensure_future(hub.write(155, [120]))
    await asyncio.sleep(0)
    assert not waiting.done()
    hub.close()
    with pytest.raises(MaicoConnectionError, match="closed"):
        await asyncio.wait_for(waiting, 1)
    assert device.writes == [(154, [80])]
