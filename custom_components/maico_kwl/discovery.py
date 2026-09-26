"""Autonomous discovery of the registers a Maico KWL actually implements.

The documented register map (docs/modbus.csv) covers the whole product family,
but a given unit only implements a subset. At setup we probe the registers and
keep only the ones the device answers to, then derive a capability profile from
that subset (there is no dedicated model/type register on the device).

Accessories (register_defs.ACCESSORIES) answer on every unit, so the probe
cannot tell whether they are fitted. Their values are read once to detect
that, and the user can correct the result in the options.

Probing is done in blocks of adjacent registers, since each request costs a
round trip (about 100 ms through a typical Modbus TCP proxy). Only the
registers of a block the device rejects are probed one by one.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from .const import CONF_ACCESSORIES, CONF_DISCOVERY, MaicoProfile
from .coordinator import build_blocks
from .modbus_hub import MaicoConnectionError, MaicoModbusError, MaicoModbusHub
from .register_defs import (
    ACCESSORIES,
    REGISTERS,
    REGISTERS_BY_KEY,
    RegisterDef,
    Values,
)

_LOGGER = logging.getLogger(__name__)

# Version of the stored discovery. A stored result of an older version is
# discovered again: 2 adds the detected accessories.
DISCOVERY_VERSION = 2


async def async_discover(hub: MaicoModbusHub) -> tuple[set[str], set[str]]:
    """Probe the device and return (present register keys, fitted accessories).

    Raises MaicoConnectionError if the device becomes unreachable while probing,
    so setup is retried instead of continuing with an incomplete register set.
    """
    present: set[str] = set()

    # First pass: probe every register that can be read, block by block.
    readable = [reg for reg in REGISTERS if reg.probe_via is None]
    for _start, _count, defs in build_blocks(readable):
        present |= await _probe_group(hub, defs)

    # Second pass: write-only registers inherit presence from a sibling.
    present = _resolve_probe_via(present)

    # Third pass: which of the accessories that answer are fitted.
    accessories = await _detect_accessories(hub, present)

    _LOGGER.info(
        "Maico discovery: %d/%d registers present, accessories fitted: %s, "
        "not fitted: %s",
        len(present),
        len(REGISTERS),
        ", ".join(sorted(accessories)) or "-",
        ", ".join(sorted(offered_accessories(present) - accessories)) or "-",
    )
    return present, accessories


def cache_data(present: set[str], accessories: set[str]) -> dict[str, Any]:
    """Discovery result to store in the config entry.

    "probed" records which registers this version knew, so a later version
    that adds registers discovers again instead of never finding them.
    """
    return {
        "version": DISCOVERY_VERSION,
        "probed": sorted(reg.key for reg in REGISTERS if reg.probe_via is None),
        "present": sorted(present),
        "accessories": sorted(accessories),
    }


def data_without_discovery(data: Mapping[str, Any]) -> dict[str, Any]:
    """Entry data without the stored discovery, so the next setup probes again."""
    return {key: value for key, value in data.items() if key != CONF_DISCOVERY}


def present_from_cache(cache: dict[str, Any] | None) -> set[str] | None:
    """Present registers from a stored discovery, or None to discover again."""
    if not cache or cache.get("version", 1) < DISCOVERY_VERSION:
        return None
    probed = set(cache.get("probed", []))
    if any(reg.probe_via is None and reg.key not in probed for reg in REGISTERS):
        return None  # a register was added since the last discovery
    present = {
        key
        for key in cache.get("present", [])
        if key in REGISTERS_BY_KEY and REGISTERS_BY_KEY[key].probe_via is None
    }
    return _resolve_probe_via(present) or None


def offered_accessories(present: set[str]) -> set[str]:
    """Accessories the unit answers to, so the user can choose them."""
    return {acc.key for acc in ACCESSORIES if present.intersection(acc.keys)}


def active_accessories(
    cache: Mapping[str, Any], options: Mapping[str, Any]
) -> set[str]:
    """The accessories in use: the user's choice, else the detected ones."""
    chosen = options.get(CONF_ACCESSORIES)
    if chosen is not None:
        return set(chosen)
    return set(cache.get("accessories", []))


def registers_in_use(present: set[str], accessories: set[str]) -> set[str]:
    """The present registers without those of accessories not in use."""
    unused = {
        key for acc in ACCESSORIES if acc.key not in accessories for key in acc.keys
    }
    return present - unused


async def _probe_group(hub: MaicoModbusHub, defs: list[RegisterDef]) -> set[str]:
    """Return the keys of the adjacent registers in defs the device answers to.

    Reads the whole group at once. If the device rejects it, each register is
    probed on its own: absent registers usually come as whole banks (EnOcean,
    ZP1), where halving the block would need more requests than this.
    """
    if len(defs) > 1:
        start = defs[0].address
        count = defs[-1].address + defs[-1].word_count - start
        if await _probe(hub, start, count):
            return {reg.key for reg in defs}
    return {
        reg.key for reg in defs if await _probe(hub, reg.address, reg.word_count)
    }


async def _probe(hub: MaicoModbusHub, address: int, count: int) -> bool:
    try:
        return await hub.probe(address, count)
    except MaicoConnectionError:
        raise
    except MaicoModbusError as err:
        # An unexpected exception code: handle it like a rejected read.
        _LOGGER.debug("Probe of %s+%s failed: %s", address, count, err)
        return False


async def _detect_accessories(hub: MaicoModbusHub, present: set[str]) -> set[str]:
    """Keys of the accessories that answer and are fitted.

    An accessory whose values cannot be read or do not tell counts as fitted.
    """
    offered = [acc for acc in ACCESSORIES if acc.key in offered_accessories(present)]
    sources = {
        key for acc in offered if acc.detect for key in acc.sources if key in present
    }
    values = await _read_values(hub, [REGISTERS_BY_KEY[key] for key in sources])
    return {
        acc.key
        for acc in offered
        if acc.detect is None or acc.detect(values) is not False
    }


async def _read_values(hub: MaicoModbusHub, defs: list[RegisterDef]) -> Values:
    values: Values = {}
    for start, count, block in build_blocks(defs):
        try:
            regs = await hub.read_block(start, count)
        except MaicoConnectionError:
            raise
        except MaicoModbusError as err:
            _LOGGER.debug("Accessory check read %s+%s failed: %s", start, count, err)
            continue
        for reg in block:
            offset = reg.address - start
            values[reg.key] = reg.decode(regs[offset : offset + reg.word_count])
    return values


def _resolve_probe_via(present: set[str]) -> set[str]:
    """Add the write-only registers whose readable sibling is present."""
    return present | {
        reg.key
        for reg in REGISTERS
        if reg.probe_via is not None and reg.probe_via in present
    }


def derive_profile(present: set[str]) -> MaicoProfile:
    """Infer a capability profile from the set of present registers."""
    features: list[str] = []

    if any(k.startswith("enocean_") for k in present):
        features.append("EnOcean")
    # Wired sensor inputs or any of the eight EnOcean IDs.
    if any(k.startswith(("co2_sensor", "enocean_co2_")) for k in present):
        features.append("CO2")
    if any(k.startswith(("voc_sensor", "enocean_voc_")) for k in present):
        features.append("VOC")
    if "summer_bypass_open" in present:
        features.append("Summer bypass")
    if "ptc_heater_active" in present:
        features.append("PTC heater")
    # ZP1 extension module (geothermal heat exchanger / zones / reheating).
    if present & {
        "brine_pump_state",
        "three_way_damper_state",
        "zone_damper_state",
        "reheating_relay_active",
    }:
        features.append("ZP1")

    model = "Maico KWL"
    if features:
        model = f"Maico KWL ({', '.join(features)})"

    return {
        "model": model,
        "features": features,
        "present_count": len(present),
        "total_count": len(REGISTERS),
    }
