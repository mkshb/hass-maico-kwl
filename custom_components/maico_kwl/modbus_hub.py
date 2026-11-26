"""Thin async wrapper around a Modbus unit of Home Assistant's Modbus integration.

The connection is Home Assistant's (``homeassistant.components.modbus``): it is
shared with every integration that asks for the same host and port, opens on
the first request, reopens after a drop and closes with the last holder. The
hub only maps its errors onto the two kinds the integration tells apart.
"""

from __future__ import annotations

import asyncio
import logging

from modbus_connection import (
    AcknowledgeError,
    GatewayPathUnavailableError,
    GatewayTargetError,
    IllegalDataAddressError,
    IllegalDataValueError,
    IllegalFunctionError,
    ModbusError,
    ModbusExceptionError,
    ModbusUnit,
    ServerDeviceBusyError,
)

from .register_defs import REGISTER_OFFSET

_LOGGER = logging.getLogger(__name__)

# Modbus exceptions that mean "the device understood the request but this
# register is not available" -> treat as absent during discovery.
# Illegal function / illegal data address / illegal value (0x01 to 0x03).
_ABSENT_ERRORS = (IllegalFunctionError, IllegalDataAddressError, IllegalDataValueError)
# Exceptions that say "try again later" (acknowledge, device busy, gateway path
# unavailable, gateway target did not respond: 0x05, 0x06, 0x0A, 0x0B): nothing
# is known about the register, so discovery must not store it as absent.
_TRANSIENT_ERRORS = (
    AcknowledgeError,
    ServerDeviceBusyError,
    GatewayPathUnavailableError,
    GatewayTargetError,
)


class MaicoModbusError(Exception):
    """Raised when a Modbus read/write fails."""


class MaicoConnectionError(MaicoModbusError):
    """Raised when the device can't be reached (no connection, timeout).

    Distinct from a Modbus exception response, where the device did answer but
    rejected the request (e.g. Illegal Data Address).
    """


def _checked_registers(registers: list[int], address: int, count: int) -> list[int]:
    """The registers of a response, if it holds exactly the ones requested.

    A short answer (e.g. from a gateway) would otherwise decode the missing
    registers as 0. Raised as a rejected read: polling falls back to single
    reads, discovery to single probes.
    """
    if len(registers) != count:
        raise MaicoModbusError(
            f"read at {address} returned {len(registers)} of {count} registers"
        )
    return registers


class MaicoModbusHub:
    """Reads and writes the registers of one unit.

    Writes go out one at a time, at least ``write_gap`` seconds apart. Some
    units drop the connection when a write follows the previous one within a
    few seconds and then discard the values they had not stored yet, also
    ones that already read back as written.
    """

    def __init__(self, unit: ModbusUnit, write_gap: float = 0) -> None:
        self._unit = unit
        self._closed = asyncio.Event()
        self._write_gap = write_gap
        self._write_lock = asyncio.Lock()
        # Loop time when the last write ended, None before the first one.
        self._last_write: float | None = None

    def close(self) -> None:
        """Send nothing more (entry unloaded).

        The connection itself is Home Assistant's and may stay open for other
        holders, so the hub has to refuse further requests on its own. A
        write waiting for its turn gives up at once.
        """
        self._closed.set()

    def _check_open(self) -> None:
        if self._closed.is_set():
            raise MaicoConnectionError("connection is closed")

    async def _read(self, address: int, count: int) -> list[int]:
        """Read registers; a rejected read raises the ModbusExceptionError."""
        self._check_open()
        try:
            registers = await self._unit.read_holding_registers(
                address + REGISTER_OFFSET, count
            )
        except ModbusExceptionError:
            raise
        except ModbusError as err:
            raise MaicoConnectionError(f"read at {address} failed: {err}") from err
        return _checked_registers(registers, address, count)

    async def read_block(self, address: int, count: int) -> list[int]:
        """Read ``count`` holding registers starting at ``address``."""
        try:
            return await self._read(address, count)
        except ModbusExceptionError as err:
            raise MaicoModbusError(f"read at {address} rejected: {err}") from err

    async def probe(self, address: int, count: int = 1) -> bool:
        """Return True if the register exists on this device.

        A device that answers with a protocol exception (e.g. Illegal Data
        Address) proves the connection works but the register is absent -> False.
        A transport/connection failure, or a busy unit or gateway, raises
        MaicoConnectionError so discovery can abort instead of marking every
        register as absent.
        """
        try:
            await self._read(address, count)
        except _ABSENT_ERRORS:
            return False
        except _TRANSIENT_ERRORS as err:
            raise MaicoConnectionError(f"probe at {address} rejected: {err}") from err
        except ModbusExceptionError as err:
            raise MaicoModbusError(f"probe at {address} rejected: {err}") from err
        return True

    async def write(self, address: int, values: list[int]) -> None:
        """Write one or more holding registers (High-Word first).

        Waits until the write gap since the previous write is over.
        """
        async with self._write_lock:
            await self._wait_for_gap(address)
            self._check_open()
            try:
                if len(values) == 1:
                    await self._unit.write_register(
                        address + REGISTER_OFFSET, values[0]
                    )
                else:
                    await self._unit.write_registers(address + REGISTER_OFFSET, values)
            except ModbusExceptionError as err:
                raise MaicoModbusError(f"write at {address} rejected: {err}") from err
            except ModbusError as err:
                raise MaicoConnectionError(f"write at {address} failed: {err}") from err
            finally:
                # Also after a failed write: the unit may have received it.
                self._last_write = asyncio.get_running_loop().time()

    async def _wait_for_gap(self, address: int) -> None:
        if self._last_write is None:
            return
        remaining = (
            self._last_write + self._write_gap - asyncio.get_running_loop().time()
        )
        if remaining <= 0:
            return
        _LOGGER.debug("Write at %s waits %.1f s for the write gap", address, remaining)
        try:
            async with asyncio.timeout(remaining):
                await self._closed.wait()
        except TimeoutError:
            pass
