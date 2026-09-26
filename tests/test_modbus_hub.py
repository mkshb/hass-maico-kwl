"""Tests for the Modbus hub on top of the fake pymodbus client."""

from __future__ import annotations

import pytest

from custom_components.maico_kwl.modbus_hub import (
    MaicoConnectionError,
    MaicoModbusError,
    MaicoModbusHub,
)

from .conftest import HOST, PORT, SLAVE, FakeDevice


@pytest.fixture
async def hub(device: FakeDevice) -> MaicoModbusHub:
    hub = MaicoModbusHub(HOST, PORT, SLAVE)
    assert await hub.connect()
    return hub


async def test_properties(hub: MaicoModbusHub) -> None:
    assert (hub.host, hub.port, hub.slave) == (HOST, PORT, SLAVE)


async def test_read_block(hub: MaicoModbusHub) -> None:
    assert await hub.read_block(553, 2) == [215, 3]


async def test_read_block_exception_response(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A rejected read is a MaicoModbusError, not a connection error."""
    with pytest.raises(MaicoModbusError) as err:
        await hub.read_block(350, 1)
    assert not isinstance(err.value, MaicoConnectionError)


async def test_write_single_and_multiple(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """One value uses FC 06, several values FC 16 (High-Word first)."""
    await hub.write(553, [220])
    await hub.write(858, [0x0001, 0x0002])
    assert device.writes == [(553, [220]), (858, [1, 2])]


async def test_write_exception_response(hub: MaicoModbusHub, device: FakeDevice) -> None:
    device.write_exception = 4
    with pytest.raises(MaicoModbusError):
        await hub.write(553, [220])


async def test_reconnects_after_connection_loss(
    hub: MaicoModbusHub, device: FakeDevice
) -> None:
    """A dropped link is reopened on the next request, or reported."""
    device.clients[0].close()
    assert await hub.read_block(700, 1) == [215]

    device.clients[0].close()
    device.online = False
    with pytest.raises(MaicoConnectionError, match="cannot connect"):
        await hub.write(553, [220])
