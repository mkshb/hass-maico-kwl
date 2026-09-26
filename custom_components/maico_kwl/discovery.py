"""Autonomous discovery of the registers a Maico KWL actually implements.

The documented register map (docs/modbus.csv) covers the whole product family,
but a given unit only implements a subset. At setup we probe the registers and
keep only the ones the device answers to, then derive a capability profile from
that subset (there is no dedicated model/type register on the device).

Probing is done in blocks of adjacent registers, since each request costs a
round trip (about 100 ms through a typical Modbus TCP proxy). Only the
registers of a block the device rejects are probed one by one.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from .const import CONF_DISCOVERY, MaicoProfile
from .coordinator import build_blocks
from .modbus_hub import MaicoConnectionError, MaicoModbusError, MaicoModbusHub
from .register_defs import OPTIONAL_FILTERS, REGISTERS, REGISTERS_BY_KEY, RegisterDef

_LOGGER = logging.getLogger(__name__)

# Version of the stored discovery. A stored result of an older version is
# discovered again: 2 leaves out the filters the unit does not have.
DISCOVERY_VERSION = 2


async def async_discover(hub: MaicoModbusHub) -> tuple[set[str], MaicoProfile]:
    """Probe the device and return (present register keys, capability profile).

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

    # Third pass: registers that answer, but whose accessory is not fitted.
    present -= await _unfitted_filter_keys(hub, present)

    profile = derive_profile(present)
    _LOGGER.info(
        "Maico discovery: %d/%d registers present, profile=%s",
        len(present),
        len(REGISTERS),
        profile["model"],
    )
    return present, profile


def cache_data(present: set[str]) -> dict[str, Any]:
    """Discovery result to store in the config entry.

    "probed" records which registers this version knew, so a later version
    that adds registers discovers again instead of never finding them.
    """
    return {
        "version": DISCOVERY_VERSION,
        "probed": sorted(reg.key for reg in REGISTERS if reg.probe_via is None),
        "present": sorted(present),
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


async def _unfitted_filter_keys(hub: MaicoModbusHub, present: set[str]) -> set[str]:
    """Keys of the optional filters the unit does not have.

    Their registers answer on every unit, so only the values tell: see
    OptionalFilter.fitted. A filter that cannot be checked is kept.
    """
    if "notice_code" not in present:
        return set()
    try:
        notice = await _read_value(hub, "notice_code")
        unfitted: set[str] = set()
        for flt in OPTIONAL_FILTERS:
            if flt.remaining not in present:
                continue
            if not flt.fitted(await _read_value(hub, flt.remaining), notice):
                _LOGGER.info(
                    "Maico discovery: %s not fitted (0 days left, no notice), "
                    "skipping %s",
                    flt.remaining,
                    ", ".join(flt.keys),
                )
                unfitted.update(flt.keys)
    except MaicoConnectionError:
        raise
    except MaicoModbusError as err:
        _LOGGER.debug("Filter check failed, keeping all filters: %s", err)
        return set()
    return unfitted


async def _read_value(hub: MaicoModbusHub, key: str) -> float:
    reg = REGISTERS_BY_KEY[key]
    value = reg.decode(await hub.read_block(reg.address, reg.word_count))
    if not isinstance(value, (int, float)):
        raise MaicoModbusError(f"{key} has no numeric value: {value!r}")
    return value


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
