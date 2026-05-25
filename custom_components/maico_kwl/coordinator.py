"""Data update coordinator for the Maico KWL integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MAX_BLOCK_SIZE
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import BUTTON, REGISTERS_BY_KEY, RegisterDef

_LOGGER = logging.getLogger(__name__)

Block = tuple[int, int, list[RegisterDef]]  # (start, count, defs)


def build_blocks(defs: list[RegisterDef]) -> list[Block]:
    """Group readable registers into contiguous block reads.

    Only registers that are directly adjacent are merged, so a block never spans
    an address the device would reject (which would fail the whole request).
    """
    blocks: list[Block] = []
    current: list[RegisterDef] = []
    start = 0
    end = 0  # exclusive
    for reg in sorted(defs, key=lambda d: d.address):
        reg_end = reg.address + reg.word_count
        if current and reg.address == end and (reg_end - start) <= MAX_BLOCK_SIZE:
            current.append(reg)
            end = reg_end
        else:
            if current:
                blocks.append((start, end - start, current))
            current = [reg]
            start = reg.address
            end = reg_end
    if current:
        blocks.append((start, end - start, current))
    return blocks


class MaicoCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Polls the present registers and exposes decoded values keyed by register."""

    def __init__(
        self,
        hass: HomeAssistant,
        hub: MaicoModbusHub,
        present: set[str],
        profile: dict,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.hub = hub
        self.present = present
        self.profile = profile
        # Buttons / write-only registers carry no readable state.
        read_defs = [
            REGISTERS_BY_KEY[key]
            for key in present
            if REGISTERS_BY_KEY[key].platform != BUTTON
        ]
        self._blocks = build_blocks(read_defs)

    async def _async_update_data(self) -> dict[str, float]:
        data: dict[str, float] = {}
        for start, count, defs in self._blocks:
            try:
                regs = await self.hub.read_block(start, count)
            except MaicoModbusError as err:
                _LOGGER.debug("Block read %s+%s failed, retrying singly: %s",
                              start, count, err)
                await self._read_singly(defs, data)
                continue
            for reg in defs:
                offset = reg.address - start
                data[reg.key] = reg.decode(regs[offset:offset + reg.word_count])
        if not data:
            raise UpdateFailed("No registers could be read from the device")
        return data

    async def _read_singly(
        self, defs: list[RegisterDef], data: dict[str, float]
    ) -> None:
        for reg in defs:
            try:
                regs = await self.hub.read_block(reg.address, reg.word_count)
            except MaicoModbusError:
                continue  # leave key absent -> entity becomes unavailable
            data[reg.key] = reg.decode(regs)
