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

import asyncio
import logging
from collections.abc import Mapping
from typing import Any

from .const import (
    CONF_ACCESSORIES,
    CONF_ACCESSORIES_OFFERED,
    CONF_DISCOVERY,
    MaicoProfile,
)
from .coordinator import build_blocks
from .modbus_hub import MaicoConnectionError, MaicoModbusError, MaicoModbusHub
from .register_defs import (
    ACCESSORIES,
    IDENTITY_RANGES,
    REGISTERS,
    REGISTERS_BY_KEY,
    RegisterDef,
    Values,
    identity_problem,
)

_LOGGER = logging.getLogger(__name__)

# Version of the stored discovery. A stored result of an older version is
# discovered again: 2 adds the detected accessories.
DISCOVERY_VERSION = 2

# An unexpected exception response (e.g. 4, slave device failure) may be
# temporary, e.g. from a gateway whose device did not answer in time. A single
# register only counts as absent if it keeps coming.
PROBE_ATTEMPTS = 3
PROBE_RETRY_DELAY = 1.0  # seconds


async def async_discover(
    hub: MaicoModbusHub, detected_before: set[str] | None = None
) -> tuple[set[str], set[str]]:
    """Probe the device and return (present register keys, fitted accessories).

    detected_before are the accessories the last discovery of this unit found
    fitted; see Accessory.kept_once_detected.

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
    accessories = await _detect_accessories(hub, present, detected_before or set())

    _LOGGER.info(
        "Maico discovery: %d/%d registers present, accessories fitted: %s, "
        "not fitted: %s",
        len(present),
        len(REGISTERS),
        ", ".join(sorted(accessories)) or "-",
        ", ".join(sorted(offered_accessories(present) - accessories)) or "-",
    )
    return present, accessories


async def async_check_identity(hub: MaicoModbusHub) -> str | None:
    """Why the device does not look like a Maico KWL, or None.

    Reads the registers of IDENTITY_RANGES, a rejected block register by
    register: a unit may lack one of them (discovery allows for that), but not
    all. Raises MaicoConnectionError if the device cannot be reached.
    """
    defs = [REGISTERS_BY_KEY[key] for key in IDENTITY_RANGES]
    values = await _read_values(hub, defs, singly=True)
    if not values:
        return "none of its registers 108, 109, 550 to 554 and 650 can be read"
    return identity_problem(values)


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


def data_without_discovery(
    data: Mapping[str, Any], same_unit: bool = True
) -> dict[str, Any]:
    """Entry data without the stored discovery, so the next setup probes again.

    For the same unit, the detected accessories stay for the next discovery
    (detected_accessories); a stored discovery of just these is not valid, so
    it probes again all the same.
    """
    result = {key: value for key, value in data.items() if key != CONF_DISCOVERY}
    if same_unit and (accessories := detected_accessories(data.get(CONF_DISCOVERY))):
        result[CONF_DISCOVERY] = {"accessories": sorted(accessories)}
    return result


def detected_accessories(cache: Any) -> set[str]:
    """The accessories a stored discovery found fitted, of any version."""
    stored = cache.get("accessories") if isinstance(cache, Mapping) else None
    if not isinstance(stored, list):
        return set()
    return {item for item in stored if isinstance(item, str)}


def _valid_cache(cache: Any) -> bool:
    """Whether a stored discovery has the format of this version.

    An older one is discovered again, and so is a newer one (e.g. after a
    downgrade) or a damaged one, rather than read with the wrong meaning or
    failing the setup.
    """
    if not isinstance(cache, Mapping) or cache.get("version") != DISCOVERY_VERSION:
        return False
    return all(
        isinstance(items := cache.get(key), list)
        and all(isinstance(item, str) for item in items)
        for key in ("probed", "present", "accessories")
    )


def present_from_cache(cache: Any) -> set[str] | None:
    """Present registers from a stored discovery, or None to discover again."""
    if not _valid_cache(cache):
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


# All accessories up to 0.4.0, which stored a choice without the offered ones.
# Such a choice was made from these at most.
ACCESSORIES_UNTIL_0_4_0 = frozenset(
    {
        "outdoor_filter",
        "room_filter",
        "wired_sensors",
        "enocean",
        "external_room_sensor",
        "ptc_heater",
        "zp1",
    }
)


def active_accessories(
    cache: Mapping[str, Any], options: Mapping[str, Any]
) -> set[str]:
    """The accessories in use: the user's choice, else the detected ones.

    The choice only covers the accessories offered when it was made. One the
    unit answers to only later (fitted afterwards, or new in a later version)
    is decided by detection, instead of counting as not fitted.
    """
    detected = detected_accessories(cache)
    chosen = options.get(CONF_ACCESSORIES)
    if chosen is None:
        return detected
    offered = set(options.get(CONF_ACCESSORIES_OFFERED, ACCESSORIES_UNTIL_0_4_0))
    return set(chosen) | (detected - offered)


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
        if await _probe(hub, start, count, attempts=1):
            return {reg.key for reg in defs}
    return {
        reg.key
        for reg in defs
        if await _probe(hub, reg.address, reg.word_count, PROBE_ATTEMPTS)
    }


async def _probe(
    hub: MaicoModbusHub, address: int, count: int, attempts: int
) -> bool:
    """Whether the registers answer; 1 to 3 (e.g. Illegal Data Address) is no.

    Any other exception response is asked again up to ``attempts`` times; one
    that stays counts as absent, and is logged as a warning for a single
    register, since its entities are then left out.
    """
    for attempt in range(1, attempts + 1):
        try:
            return await hub.probe(address, count)
        except MaicoConnectionError:
            raise
        except MaicoModbusError as err:
            if attempt < attempts:
                await asyncio.sleep(PROBE_RETRY_DELAY)
                continue
            if attempts > 1:
                _LOGGER.warning(
                    "Register %s did not answer in %d attempts and is left out: %s",
                    address, attempts, err,
                )
            else:
                _LOGGER.debug("Probe of %s+%s failed: %s", address, count, err)
    return False


async def _detect_accessories(
    hub: MaicoModbusHub, present: set[str], detected_before: set[str]
) -> set[str]:
    """Keys of the accessories that answer and are fitted.

    An accessory whose values cannot be read or do not tell counts as fitted,
    and so does one kept_once_detected that was detected before.
    """
    offered = [acc for acc in ACCESSORIES if acc.key in offered_accessories(present)]
    sources = {
        key for acc in offered if acc.detect for key in acc.sources if key in present
    }
    values = await _read_values(hub, [REGISTERS_BY_KEY[key] for key in sources])
    return {
        acc.key
        for acc in offered
        if acc.detect is None
        or acc.detect(values) is not False
        or (acc.kept_once_detected and acc.key in detected_before)
    }


async def _read_values(
    hub: MaicoModbusHub, defs: list[RegisterDef], singly: bool = False
) -> Values:
    """The values of defs that can be read; with singly, a rejected block is
    read again register by register."""
    values: Values = {}
    for start, count, block in build_blocks(defs):
        try:
            regs = await hub.read_block(start, count)
        except MaicoConnectionError:
            raise
        except MaicoModbusError as err:
            _LOGGER.debug("Read %s+%s failed: %s", start, count, err)
            if singly and len(block) > 1:
                for reg in block:
                    values.update(await _read_values(hub, [reg]))
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
