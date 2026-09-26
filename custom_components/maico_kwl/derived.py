"""Values the unit does not report, derived from the registers it does.

This module is free of Home Assistant imports so it can be unit tested on its
own. Each DerivedDef names the registers it needs; its entity is only created
when all of them are present, and ``compute`` gets their values in that order.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

# Volumetric heat capacity of air in Wh/(m3*K). The airflow is reported in m3/h,
# so P[W] = flow[m3/h] * 0.34 * dT[K].
AIR_HEAT_CAPACITY = 0.34


def heat_recovery_power(airflow_supply: float, intake: float, supply: float) -> float:
    """Heat the exchanger adds to the supply air, in W.

    Negative while the exchanger cools the supply air (e.g. in summer), which is
    kept on purpose instead of clamping to zero.
    """
    return round(airflow_supply * AIR_HEAT_CAPACITY * (supply - intake))


@dataclass(frozen=True)
class DerivedDef:
    """A sensor computed from one or more registers."""

    key: str
    sources: tuple[str, ...]
    compute: Callable[..., float | None]
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = "measurement"
    precision: int | None = None


DERIVED_SENSORS: list[DerivedDef] = [
    DerivedDef(
        "heat_recovery_power",
        ("airflow_supply", "temp_air_intake", "temp_supply_air"),
        heat_recovery_power,
        unit="W",
        device_class="power",
        precision=0,
    ),
]
