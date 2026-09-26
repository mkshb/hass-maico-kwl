"""Tests for values derived from several registers."""

from __future__ import annotations

import pytest
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.maico_kwl import derived

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
