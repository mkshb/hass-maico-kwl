"""Tests for polling: block building, fallbacks and connection loss."""

from __future__ import annotations

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from custom_components.maico_kwl.const import MAX_BLOCK_SIZE
from custom_components.maico_kwl.coordinator import build_blocks
from custom_components.maico_kwl.register_defs import REGISTERS_BY_KEY, RegisterDef

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry


def _defs(*keys: str) -> list[RegisterDef]:
    return [REGISTERS_BY_KEY[key] for key in keys]


def _spans(blocks) -> list[tuple[int, int]]:
    return [(start, count) for start, count, _defs in blocks]


def test_build_blocks_merges_only_adjacent_registers() -> None:
    """Adjacent registers share a block, a gap starts a new one."""
    blocks = build_blocks(_defs("temp_room", "temp_supply_air", "temp_air_intake"))
    assert _spans(blocks) == [(700, 1), (703, 2)]


def test_build_blocks_sorts_and_counts_32_bit_registers() -> None:
    """Unsorted input is ordered, and u32 registers take two words."""
    blocks = build_blocks(_defs("op_hours_reduced", "op_hours_humidity_protection"))
    assert _spans(blocks) == [(850, 4)]
    assert [reg.key for reg in blocks[0][2]] == [
        "op_hours_humidity_protection",
        "op_hours_reduced",
    ]


def test_build_blocks_respects_max_block_size() -> None:
    """A contiguous run longer than MAX_BLOCK_SIZE is split."""
    defs = [
        RegisterDef(f"reg_{i}", 1000 + i, f"Reg {i}", "sensor")
        for i in range(MAX_BLOCK_SIZE + 5)
    ]
    assert _spans(build_blocks(defs)) == [(1000, MAX_BLOCK_SIZE), (1100, 5)]


def test_build_blocks_empty() -> None:
    assert build_blocks([]) == []


async def test_rejected_block_falls_back_to_single_reads(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """If the unit rejects a block, the other registers are still read."""
    await setup_entry(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator

    device.absent.add(704)  # temp_supply_air disappears after discovery
    device.registers[700] = 230
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success
    assert "temp_supply_air" not in coordinator.data
    assert coordinator.data["temp_room"] == 23.0
    assert (
        hass.states.get(entity_id(hass, config_entry, "sensor", "temp_supply_air")).state
        == STATE_UNAVAILABLE
    )
    assert hass.states.get(entity_id(hass, config_entry, "sensor", "temp_room")).state == "23.0"


async def test_connection_loss_fails_update_without_single_reads(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A connection loss fails the update at once and entities go unavailable."""
    await setup_entry(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator
    temp_room = entity_id(hass, config_entry, "sensor", "temp_room")

    device.online = False
    reads_before = device.reads
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert not coordinator.last_update_success
    assert device.reads == reads_before  # no per-register retries
    assert hass.states.get(temp_room).state == STATE_UNAVAILABLE

    device.online = True
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert coordinator.last_update_success
    assert hass.states.get(temp_room).state == "21.5"


async def test_update_fails_when_nothing_readable(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """If every register is rejected, the update fails."""
    await setup_entry(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator

    device.absent = set(range(0, 1000))
    await coordinator.async_refresh()
    assert not coordinator.last_update_success


async def test_connection_loss_during_single_reads(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A connection loss while reading singly also fails the update."""
    await setup_entry(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator

    device.absent.add(106)  # first block is rejected ...
    device.fail_after_reads = device.reads + 1  # ... then the link drops
    await coordinator.async_refresh()
    assert not coordinator.last_update_success
