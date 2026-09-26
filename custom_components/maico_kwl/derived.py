"""Values the unit does not report, derived from the registers it does.

This module is free of Home Assistant imports so it can be unit tested on its
own. Each DerivedDef names the registers it needs; its entity is only created
when all of them are present, and ``compute`` gets their values in that order.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

# Volumetric heat capacity of air in Wh/(m3*K). The airflow is reported in m3/h,
# so P[W] = flow[m3/h] * 0.34 * dT[K].
AIR_HEAT_CAPACITY = 0.34

# Below this difference between extract and intake air the efficiency is mostly
# sensor tolerance (e.g. on mild days), so it is not reported.
MIN_EFFICIENCY_SPREAD = 5.0

# Magnus formula constants over water (Sonntag 1990), for -45 to 60 degC.
MAGNUS_A = 17.62
MAGNUS_B = 243.12  # degC
MAGNUS_E0 = 6.112  # hPa


def heat_recovery_power(airflow_supply: float, intake: float, supply: float) -> float:
    """Heat the exchanger adds to the supply air, in W.

    Negative while the exchanger cools the supply air (e.g. in summer), which is
    kept on purpose instead of clamping to zero.
    """
    return round(airflow_supply * AIR_HEAT_CAPACITY * (supply - intake))


def heat_recovery_efficiency(
    intake: float, supply: float, extract: float
) -> float | None:
    """Supply-side temperature efficiency of the exchanger, in %.

    The share of the difference between extract and intake air that the supply
    air gains. Close to 0 while the summer bypass is open; fan heat can push it
    slightly above 100.
    """
    spread = extract - intake
    if abs(spread) < MIN_EFFICIENCY_SPREAD:
        return None
    return round((supply - intake) / spread * 100, 1)


def airflow_imbalance(airflow_supply: float, airflow_exhaust: float) -> float:
    """Supply minus exhaust airflow, in m3/h (positive: more air goes in)."""
    return round(airflow_supply - airflow_exhaust)


def _vapour_pressure(temp: float, humidity: float) -> float:
    """Partial pressure of water vapour in hPa."""
    saturation = MAGNUS_E0 * math.exp(MAGNUS_A * temp / (MAGNUS_B + temp))
    return saturation * humidity / 100


def absolute_humidity(temp: float, humidity: float) -> float:
    """Water content of the air in g/m3, from temperature and relative humidity."""
    # 216.7 g*K/(m3*hPa) = molar mass of water / gas constant.
    return round(216.7 * _vapour_pressure(temp, humidity) / (273.15 + temp), 2)


def dew_point(temp: float, humidity: float) -> float | None:
    """Temperature at which the air would start to condense, in degC."""
    if humidity <= 0:
        return None
    gamma = math.log(_vapour_pressure(temp, humidity) / MAGNUS_E0)
    return round(MAGNUS_B * gamma / (MAGNUS_A - gamma), 1)


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
    entity_category: str | None = None


HEAT_RECOVERY_SOURCES = ("airflow_supply", "temp_air_intake", "temp_supply_air")

DERIVED_SENSORS: list[DerivedDef] = [
    DerivedDef(
        "heat_recovery_power",
        HEAT_RECOVERY_SOURCES,
        heat_recovery_power,
        unit="W",
        device_class="power",
        precision=0,
    ),
    DerivedDef(
        "heat_recovery_efficiency",
        ("temp_air_intake", "temp_supply_air", "temp_extract_air"),
        heat_recovery_efficiency,
        unit="%",
        precision=0,
    ),
    DerivedDef(
        "airflow_imbalance",
        ("airflow_supply", "airflow_exhaust"),
        airflow_imbalance,
        unit="m³/h",
        device_class="volume_flow_rate",
        precision=0,
        entity_category="diagnostic",
    ),
    # humidity_exhaust (750) is the humidity of the extract air ("Abluft").
    DerivedDef(
        "absolute_humidity_extract",
        ("temp_extract_air", "humidity_exhaust"),
        absolute_humidity,
        unit="g/m³",
        device_class="absolute_humidity",
        precision=1,
    ),
    DerivedDef(
        "dew_point_extract",
        ("temp_extract_air", "humidity_exhaust"),
        dew_point,
        unit="°C",
        device_class="temperature",
        precision=1,
    ),
]

# "Filter change due" binary sensors: (entity key, remaining-days register).
# The unit counts the days down to 0; its filter bits in the notice code stay
# off on some units, so these follow the remaining days instead.
FILTER_DUE: list[tuple[str, str]] = [
    ("filter_due_device", "filter_remaining_device"),
    ("filter_due_outdoor", "filter_remaining_outdoor"),
    ("filter_due_room", "filter_remaining_room"),
]
