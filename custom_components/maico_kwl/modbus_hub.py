"""Thin async wrapper around pymodbus for a Maico KWL over Modbus TCP.

The pymodbus call signatures here match pymodbus 3.11 as bundled with current
Home Assistant: registers are addressed by keyword and the slave id is passed as
``device_id`` (not ``slave``).
"""

from __future__ import annotations

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .register_defs import REGISTER_OFFSET

_LOGGER = logging.getLogger(__name__)

# Modbus protocol exception codes that mean "the device understood the request
# but this register is not available" -> treat as absent during discovery.
_ABSENT_CODES = {1, 2, 3}  # illegal function / illegal data address / illegal value


class MaicoModbusError(Exception):
    """Raised when a Modbus read/write fails (connection or transport error)."""


class MaicoModbusHub:
    """Owns the pymodbus client and serializes access to it."""

    def __init__(self, host: str, port: int, slave: int, timeout: int = 5) -> None:
        self._host = host
        self._port = port
        self._slave = slave
        self._client = AsyncModbusTcpClient(host=host, port=port, timeout=timeout)
        self._lock = asyncio.Lock()

    @property
    def slave(self) -> int:
        return self._slave

    async def connect(self) -> bool:
        """Open the TCP connection. Returns True on success."""
        async with self._lock:
            await self._client.connect()
            return self._client.connected

    async def close(self) -> None:
        self._client.close()

    async def _read(self, address: int, count: int):
        async with self._lock:
            if not self._client.connected:
                await self._client.connect()
            try:
                return await self._client.read_holding_registers(
                    address=address + REGISTER_OFFSET,
                    count=count,
                    device_id=self._slave,
                )
            except ModbusException as err:
                raise MaicoModbusError(f"read at {address} failed: {err}") from err

    async def read_block(self, address: int, count: int) -> list[int]:
        """Read ``count`` holding registers starting at ``address``."""
        result = await self._read(address, count)
        if result.isError():
            raise MaicoModbusError(f"read at {address} returned {result}")
        return list(result.registers)

    async def probe(self, address: int, count: int = 1) -> bool:
        """Return True if the register exists on this device.

        A device that answers with a protocol exception (e.g. Illegal Data
        Address) proves the connection works but the register is absent -> False.
        A transport/connection failure is re-raised so discovery can react.
        """
        result = await self._read(address, count)
        if result.isError():
            if getattr(result, "exception_code", None) in _ABSENT_CODES:
                return False
            raise MaicoModbusError(f"probe at {address} returned {result}")
        return True

    async def write(self, address: int, values: list[int]) -> None:
        """Write one or more holding registers (High-Word first)."""
        async with self._lock:
            if not self._client.connected:
                await self._client.connect()
            try:
                if len(values) == 1:
                    result = await self._client.write_register(
                        address=address + REGISTER_OFFSET,
                        value=values[0],
                        device_id=self._slave,
                    )
                else:
                    result = await self._client.write_registers(
                        address=address + REGISTER_OFFSET,
                        values=values,
                        device_id=self._slave,
                    )
            except ModbusException as err:
                raise MaicoModbusError(f"write at {address} failed: {err}") from err
        if result.isError():
            raise MaicoModbusError(f"write at {address} returned {result}")
