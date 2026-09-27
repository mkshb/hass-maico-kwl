"""Shared fixtures: a simulated Maico unit behind a fake pymodbus client.

Only the pymodbus client is replaced, so the real hub, discovery, coordinator
and entities run against it.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from unittest.mock import patch

import pytest
from pymodbus.exceptions import ConnectionException
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.maico_kwl.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DOMAIN,
)

HOST = "192.0.2.10"
PORT = 502
SLAVE = 10

# Register values of a typical unit (raw words as the device returns them).
DEFAULT_REGISTERS: dict[int, int] = {
    100: 2026,  # unit clock: 2026-09-26 10:30:15
    101: 9,
    102: 26,
    103: 10,
    104: 30,
    105: 15,
    106: 0,  # off level allowed
    107: 0,  # control panel not locked
    108: 0,  # german
    109: 2,  # internal room temperature sensor
    150: 6,
    151: 12,
    152: 3,
    153: 30,
    154: 100,
    155: 150,
    156: 200,
    300: 0xFFF6,  # -1.0 degC offset
    301: 12,
    302: 260,
    401: 0,  # fault code high word
    402: 0,  # fault code low word
    403: 0,
    404: 0,
    550: 3,  # auto_sensor
    551: 0,
    552: 0,  # winter
    553: 215,  # 21.5 degC
    554: 3,  # nominal
    650: 3,  # nominal
    651: 1450,
    652: 1500,
    653: 150,
    654: 148,
    655: 120,
    656: 300,
    657: 60,
    700: 215,
    701: 0,
    702: 0,
    703: 0xFFCE,  # -5.0 degC
    704: 180,
    705: 220,
    706: 10,
    750: 45,  # humidity is not scaled on this unit
    800: 1,
    801: 1,
    802: 0,
    803: 0,
    804: 0,
    850: 0,
    851: 12,
    852: 0,
    853: 300,
    854: 1,  # 65536 + 10 = 65546 h, checks the High/Low word pairing
    855: 10,
    856: 0,
    857: 5,
    858: 1,
    859: 327,
    900: 50,
}

# Registers this simulated unit does not implement (Illegal Data Address):
# EnOcean, the extra sensor inputs and the ZP1 extension module.
DEFAULT_ABSENT: set[int] = (
    set(range(350, 374))
    | set(range(751, 763))
    | set(range(805, 809))
    | set(range(860, 870))
)


class FakeResponse:
    """Successful read/write response."""

    def __init__(self, registers: list[int] | None = None) -> None:
        self.registers = registers or []

    def isError(self) -> bool:  # noqa: N802 (pymodbus API)
        return False


class FakeExceptionResponse:
    """Modbus exception response (the device answered with an error code)."""

    def __init__(self, code: int) -> None:
        self.exception_code = code

    def isError(self) -> bool:  # noqa: N802 (pymodbus API)
        return True

    def __repr__(self) -> str:
        return f"ExceptionResponse(code={self.exception_code})"


@dataclass
class FakeDevice:
    """State of the simulated unit, shared by all fake clients."""

    registers: dict[int, int] = field(default_factory=lambda: dict(DEFAULT_REGISTERS))
    absent: set[int] = field(default_factory=lambda: set(DEFAULT_ABSENT))
    online: bool = True
    # Go offline after this many successful reads (None: never).
    fail_after_reads: int | None = None
    # Exception code returned for writes (None: writes succeed).
    write_exception: int | None = None
    # Answer reads of more than one register with the last one missing, like
    # a faulty gateway.
    short_blocks: bool = False
    reads: int = 0
    writes: list[tuple[int, list[int]]] = field(default_factory=list)
    clients: list[FakeModbusClient] = field(default_factory=list)

    def check_online(self) -> None:
        if self.fail_after_reads is not None and self.reads >= self.fail_after_reads:
            self.online = False
        if not self.online:
            raise ConnectionException("simulated connection loss")

    @property
    def open_connections(self) -> int:
        return sum(1 for client in self.clients if client.connected)


class FakeModbusClient:
    """Stand-in for pymodbus.client.AsyncModbusTcpClient."""

    def __init__(self, device: FakeDevice, **_kwargs) -> None:
        self._device = device
        self.connected = False
        device.clients.append(self)

    async def connect(self) -> bool:
        self.connected = self._device.online
        return self.connected

    def close(self) -> None:
        self.connected = False

    async def read_holding_registers(
        self, *, address: int, count: int, device_id: int
    ) -> FakeResponse | FakeExceptionResponse:
        self._device.check_online()
        self._device.reads += 1
        span = range(address, address + count)
        if any(addr in self._device.absent for addr in span):
            return FakeExceptionResponse(2)
        registers = [self._device.registers.get(addr, 0) for addr in span]
        if self._device.short_blocks and count > 1:
            registers = registers[:-1]
        return FakeResponse(registers)

    async def write_register(
        self, *, address: int, value: int, device_id: int
    ) -> FakeResponse | FakeExceptionResponse:
        return await self.write_registers(
            address=address, values=[value], device_id=device_id
        )

    async def write_registers(
        self, *, address: int, values: list[int], device_id: int
    ) -> FakeResponse | FakeExceptionResponse:
        self._device.check_online()
        if self._device.write_exception is not None:
            return FakeExceptionResponse(self._device.write_exception)
        self._device.writes.append((address, list(values)))
        for offset, value in enumerate(values):
            self._device.registers[address + offset] = value
        return FakeResponse()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading the integration from custom_components."""
    return


@pytest.fixture
def device() -> Generator[FakeDevice]:
    """Replace the pymodbus client with a simulated Maico unit."""
    fake = FakeDevice()
    with patch(
        "custom_components.maico_kwl.modbus_hub.AsyncModbusTcpClient",
        side_effect=lambda **kwargs: FakeModbusClient(fake, **kwargs),
    ):
        yield fake


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A config entry for the simulated unit."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"Maico KWL ({HOST})",
        data={
            CONF_HOST: HOST,
            CONF_PORT: PORT,
            CONF_SLAVE: SLAVE,
            CONF_SCAN_INTERVAL: 30,
        },
        unique_id=f"{HOST}:{PORT}:{SLAVE}",
    )
