"""Data update coordinator for the Maico KWL integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .bus_feed import BusFeeder
from .const import DOMAIN, MAX_BLOCK_SIZE, MaicoProfile
from .modbus_hub import MaicoConnectionError, MaicoModbusError, MaicoModbusHub
from .register_defs import (
    BUTTON,
    REGISTERS_BY_KEY,
    RegisterDef,
    RegisterValue,
    identity_problem,
)

_LOGGER = logging.getLogger(__name__)

Block = tuple[int, int, list[RegisterDef]]  # (start, count, defs)

type MaicoConfigEntry = ConfigEntry[MaicoRuntimeData]
# Decoded values keyed by register; a key is missing while its read fails.
type MaicoData = dict[str, RegisterValue | None]


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


class MaicoCoordinator(DataUpdateCoordinator[MaicoData]):
    """Polls the present registers and exposes decoded values keyed by register."""

    def __init__(
        self,
        hass: HomeAssistant,
        hub: MaicoModbusHub,
        present: set[str],
        profile: MaicoProfile,
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
            and REGISTERS_BY_KEY[key].readable
        ]
        self._blocks = build_blocks(read_defs)
        # Set while the last poll did not look like a Maico KWL; nothing is
        # written to the device then (see register_defs.IDENTITY_RANGES).
        self.identity_problem: str | None = None
        self._write_listeners: list[Callable[[str, float | datetime], None]] = []

    @callback
    def async_add_write_listener(
        self, listener: Callable[[str, float | datetime], None]
    ) -> Callable[[], None]:
        """Call listener(key, value) after every successful write by an entity.

        A write shows up in the data only with a later poll; the refresh after
        a write may be held back by the debouncer.
        """
        self._write_listeners.append(listener)
        return lambda: self._write_listeners.remove(listener)

    @callback
    def async_notify_write(self, key: str, value: float | datetime) -> None:
        for listener in list(self._write_listeners):
            listener(key, value)

    async def _async_update_data(self) -> MaicoData:
        try:
            data = await self._read_all()
        except MaicoConnectionError as err:
            # Retrying register by register would only multiply the timeouts.
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="device_unreachable",
                translation_placeholders={"error": str(err)},
            ) from err
        self.identity_problem = identity_problem(data)
        return data

    async def _read_all(self) -> MaicoData:
        data: MaicoData = {}
        for start, count, defs in self._blocks:
            try:
                regs = await self.hub.read_block(start, count)
            except MaicoConnectionError:
                raise
            except MaicoModbusError as err:
                _LOGGER.debug("Block read %s+%s failed, retrying singly: %s",
                              start, count, err)
                await self._read_singly(defs, data)
                continue
            for reg in defs:
                offset = reg.address - start
                data[reg.key] = reg.decode(regs[offset:offset + reg.word_count])
        if not data:
            raise UpdateFailed(translation_domain=DOMAIN, translation_key="no_data")
        return data

    async def _read_singly(
        self, defs: list[RegisterDef], data: MaicoData
    ) -> None:
        for reg in defs:
            try:
                regs = await self.hub.read_block(reg.address, reg.word_count)
            except MaicoConnectionError:
                raise
            except MaicoModbusError:
                continue  # leave key absent -> entity becomes unavailable
            data[reg.key] = reg.decode(regs)


@dataclass
class MaicoRuntimeData:
    """Per-entry runtime objects, stored in entry.runtime_data."""

    hub: MaicoModbusHub
    coordinator: MaicoCoordinator
    feeder: BusFeeder
    # Unique ids of the entities the platforms created in this setup.
    unique_ids: set[str] = field(default_factory=set)
    # Platforms whose setup ran through; only their entities are cleaned up.
    platforms: set[str] = field(default_factory=set)
