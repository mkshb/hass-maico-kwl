"""Autonomous discovery of the registers a Maico KWL actually implements.

The documented register map (docs/modbus.csv) covers the whole product family,
but a given unit only implements a subset. At setup we probe each register and
keep only the ones the device answers to, then derive a capability profile from
that subset (there is no dedicated model/type register on the device).
"""

from __future__ import annotations

import logging

from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import REGISTERS

_LOGGER = logging.getLogger(__name__)


async def async_discover(hub: MaicoModbusHub) -> tuple[set[str], dict]:
    """Probe the device and return (present register keys, capability profile)."""
    present: set[str] = set()

    # First pass: read-probe every register that can be read.
    for reg in REGISTERS:
        if reg.probe_via is not None:
            continue  # resolved in the second pass
        try:
            if await hub.probe(reg.address, reg.word_count):
                present.add(reg.key)
        except MaicoModbusError as err:
            # A transport error here is unexpected (connection was just tested);
            # log and treat the single register as absent rather than aborting.
            _LOGGER.debug("Probe failed for %s (%s): %s", reg.key, reg.address, err)

    # Second pass: write-only registers inherit presence from a sibling.
    for reg in REGISTERS:
        if reg.probe_via is not None and reg.probe_via in present:
            present.add(reg.key)

    profile = _derive_profile(present)
    _LOGGER.info(
        "Maico discovery: %d/%d registers present, profile=%s",
        len(present),
        len(REGISTERS),
        profile["model"],
    )
    return present, profile


def _derive_profile(present: set[str]) -> dict:
    """Infer a capability profile from the set of present registers."""
    features: list[str] = []

    if any(k.startswith("enocean_") for k in present):
        features.append("EnOcean")
    if any(k.startswith("co2_sensor") for k in present) or "enocean_co2_id0" in present:
        features.append("CO2")
    if any(k.startswith("voc_sensor") for k in present):
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
