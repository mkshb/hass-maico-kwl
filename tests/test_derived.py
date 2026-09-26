"""Tests for values derived from several registers."""

from __future__ import annotations

import pytest
from datetime import timedelta

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache_with_extra_data,
)

from custom_components.maico_kwl import derived
from custom_components.maico_kwl.const import CONF_SCAN_INTERVAL, DOMAIN

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry


@pytest.fixture
async def loaded(hass: HomeAssistant, device: FakeDevice, config_entry):
    await setup_entry(hass, config_entry)
    return config_entry


async def _refresh(hass: HomeAssistant, entry) -> None:
    await entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()


def test_heat_recovery_power() -> None:
    # Values from PR #2: the vendor app showed 236 W.
    assert derived.heat_recovery_power(122, 16.7, 22.4) == 236
    # The exchanger cools the supply air: negative on purpose.
    assert derived.heat_recovery_power(100, 25.0, 22.0) == -102


def test_heat_recovery_efficiency() -> None:
    assert derived.heat_recovery_efficiency(-5.0, 18.0, 22.0) == 85.2
    # Summer: intake warmer than extract air, the formula still holds.
    assert derived.heat_recovery_efficiency(30.0, 24.0, 22.0) == 75.0
    # Too little spread to say anything.
    assert derived.heat_recovery_efficiency(19.0, 20.0, 22.0) is None


async def test_heat_recovery_efficiency_sensor(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    eid = entity_id(hass, loaded, "sensor", "heat_recovery_efficiency")
    assert hass.states.get(eid).state == "85.2"
    assert hass.states.get(eid).attributes["unit_of_measurement"] == "%"

    device.registers[703] = 190  # 19.0 degC, 3 K below the extract air
    await _refresh(hass, loaded)
    assert hass.states.get(eid).state == STATE_UNKNOWN


async def test_airflow_imbalance_sensor(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    eid = entity_id(hass, loaded, "sensor", "airflow_imbalance")
    assert hass.states.get(eid).state == "2"  # 150 - 148 m3/h
    assert er.async_get(hass).async_get(eid).entity_category is EntityCategory.DIAGNOSTIC

    device.registers[654] = 160
    await _refresh(hass, loaded)
    assert hass.states.get(eid).state == "-10"


def test_absolute_humidity_and_dew_point() -> None:
    # Reference values from common psychrometric tables.
    assert derived.absolute_humidity(20.0, 50.0) == pytest.approx(8.6, abs=0.05)
    assert derived.absolute_humidity(0.0, 100.0) == pytest.approx(4.85, abs=0.05)
    assert derived.dew_point(20.0, 50.0) == 9.3
    assert derived.dew_point(15.0, 100.0) == 15.0
    assert derived.dew_point(-5.0, 80.0) == -7.9
    assert derived.dew_point(20.0, 0.0) is None


async def test_humidity_sensors(hass: HomeAssistant, loaded) -> None:
    """Extract air at 22.0 degC and 45 %."""
    absolute = hass.states.get(entity_id(hass, loaded, "sensor", "absolute_humidity_extract"))
    assert absolute.state == "8.71"
    assert absolute.attributes["unit_of_measurement"] == "g/m³"
    assert absolute.attributes["device_class"] == "absolute_humidity"
    dew = hass.states.get(entity_id(hass, loaded, "sensor", "dew_point_extract"))
    assert dew.state == "9.5"
    assert dew.attributes["device_class"] == "temperature"


async def test_filter_due(hass: HomeAssistant, device: FakeDevice, loaded) -> None:
    """Filters are due once their remaining days reach 0."""
    keys = ["filter_due_device", "filter_due_outdoor", "filter_due_room"]

    def states() -> list[str]:
        return [
            hass.states.get(entity_id(hass, loaded, "binary_sensor", key)).state
            for key in keys
        ]

    assert states() == [STATE_OFF] * 3
    due = hass.states.get(entity_id(hass, loaded, "binary_sensor", "filter_due_room"))
    assert due.attributes["device_class"] == "problem"

    device.registers[656] = 0
    await _refresh(hass, loaded)
    assert states() == [STATE_OFF, STATE_ON, STATE_OFF]


async def test_filter_next_change(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """The date the first filter runs out (device 120, outdoor 300, room 60 days)."""
    eid = entity_id(hass, loaded, "sensor", "filter_next_change")
    today = dt_util.now().date()
    assert hass.states.get(eid).state == (today + timedelta(days=60)).isoformat()
    assert hass.states.get(eid).attributes["device_class"] == "date"

    device.registers[655] = 0
    await _refresh(hass, loaded)
    assert hass.states.get(eid).state == today.isoformat()

    device.absent.add(657)
    await _refresh(hass, loaded)
    assert hass.states.get(eid).state == STATE_UNAVAILABLE


async def test_heat_recovery_power_sensor(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    eid = entity_id(hass, loaded, "sensor", "heat_recovery_power")
    state = hass.states.get(eid)
    # 150 m3/h * 0.34 * (18.0 - -5.0) K
    assert state.state == "1173"
    assert state.attributes["unit_of_measurement"] == "W"
    assert state.attributes["device_class"] == "power"
    assert state.attributes["state_class"] == "measurement"
    assert er.async_get(hass).async_get(eid).translation_key == "heat_recovery_power"

    device.absent.add(704)
    await _refresh(hass, loaded)
    assert hass.states.get(eid).state == STATE_UNAVAILABLE


async def test_derived_sensor_needs_all_sources(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Without one of its registers the derived sensor is not created."""
    device.absent.add(653)
    await setup_entry(hass, config_entry)
    with pytest.raises(AssertionError):
        entity_id(hass, config_entry, "sensor", "heat_recovery_power")


# --- Recovered heat energy -------------------------------------------------


def _energy(hass: HomeAssistant, entry) -> float:
    return float(
        hass.states.get(entity_id(hass, entry, "sensor", "heat_recovery_energy")).state
    )


async def test_heat_recovery_energy(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """1173 W for 30 min, then 0 W for 30 min, then cooling for 30 min."""
    await setup_entry(hass, config_entry)
    eid = entity_id(hass, config_entry, "sensor", "heat_recovery_energy")
    state = hass.states.get(eid)
    assert state.state == "0.0"
    assert state.attributes["state_class"] == "total_increasing"
    assert state.attributes["unit_of_measurement"] == "kWh"

    freezer.tick(timedelta(minutes=5))
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == pytest.approx(1173 / 12 / 1000, abs=0.001)

    device.registers[704] = device.registers[703]  # supply = intake: 0 W
    freezer.tick(timedelta(minutes=5))
    await _refresh(hass, config_entry)  # ramp 1173 W -> 0 W: half of it
    assert _energy(hass, config_entry) == pytest.approx(1.5 * 1173 / 12 / 1000, abs=0.001)

    device.registers[704] = 0xFFC4  # -6.0 degC: cooling, counts as 0 W
    freezer.tick(timedelta(minutes=5))
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == pytest.approx(1.5 * 1173 / 12 / 1000, abs=0.001)


async def test_heat_recovery_energy_skips_gaps(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    await setup_entry(hass, config_entry)
    device.absent.add(704)
    freezer.tick(timedelta(minutes=5))
    await _refresh(hass, config_entry)  # unavailable: no reading
    device.absent.discard(704)
    freezer.tick(timedelta(minutes=5))
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == 0.0  # nothing across the gap

    freezer.tick(timedelta(minutes=30))  # longer than the maximum gap
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == 0.0


async def test_heat_recovery_energy_with_a_long_scan_interval(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """Polls 15 min apart still count; only a missed poll is a gap."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=config_entry.title,
        data={**config_entry.data, CONF_SCAN_INTERVAL: 900},
        unique_id=config_entry.unique_id,
    )
    await setup_entry(hass, config_entry)
    freezer.tick(timedelta(minutes=15))
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == pytest.approx(1173 / 4 / 1000, abs=0.001)

    freezer.tick(timedelta(minutes=31))  # more than two intervals: a gap
    await _refresh(hass, config_entry)
    assert _energy(hass, config_entry) == pytest.approx(1173 / 4 / 1000, abs=0.001)


async def test_heat_recovery_energy_restored(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    config_entry.add_to_hass(hass)
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State("sensor.maico_kwl_192_0_2_10_heat_recovery_energy", "12.5"),
                {"native_value": 12.5, "native_unit_of_measurement": "kWh"},
            )
        ],
    )
    await setup_entry(hass, config_entry)
    assert _energy(hass, config_entry) == 12.5
