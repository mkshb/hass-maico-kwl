"""Tests for the fan entity (operating mode + ventilation level)."""

from __future__ import annotations

from datetime import timedelta

import pytest
import voluptuous as vol
from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PRESET_MODE,
    ATTR_PRESET_MODES,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.maico_kwl.const import DOMAIN

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry


@pytest.fixture
async def fan(hass: HomeAssistant, device: FakeDevice, config_entry) -> str:
    await setup_entry(hass, config_entry)
    return entity_id(hass, config_entry, "fan", "ventilation")


async def _call(hass: HomeAssistant, service: str, eid: str, **data) -> None:
    await hass.services.async_call(
        "fan", service, {ATTR_ENTITY_ID: eid, **data}, blocking=True
    )
    await hass.async_block_till_done()


async def test_fan_state(hass: HomeAssistant, fan: str) -> None:
    """auto_sensor at nominal level: on, 75 % (3 of 4 speeds), preset auto_sensor."""
    state = hass.states.get(fan)
    assert state.state == STATE_ON
    assert state.attributes[ATTR_PERCENTAGE] == 75
    assert state.attributes[ATTR_PRESET_MODE] == "auto_sensor"
    assert "off" not in state.attributes[ATTR_PRESET_MODES]


async def test_fan_percentage_switches_to_manual(
    hass: HomeAssistant, device: FakeDevice, fan: str
) -> None:
    await _call(hass, "set_percentage", fan, percentage=100)
    assert device.writes[-2:] == [(550, [1]), (554, [4])]  # manual, intensive

    device.writes.clear()
    await _call(hass, "set_percentage", fan, percentage=40)
    assert device.writes == [(554, [2])]  # already manual: reduced only


async def test_fan_preset(hass: HomeAssistant, device: FakeDevice, fan: str) -> None:
    await _call(hass, "set_preset_mode", fan, preset_mode="eco_supply_air")
    assert device.writes[-1] == (550, [4])
    assert hass.states.get(fan).attributes[ATTR_PRESET_MODE] == "eco_supply_air"


async def test_fan_off_and_on_again(
    hass: HomeAssistant, device: FakeDevice, fan: str
) -> None:
    """Turning on without arguments returns to the mode before turning off."""
    await _call(hass, "turn_off", fan)
    assert device.writes[-1] == (550, [0])
    state = hass.states.get(fan)
    assert state.state == STATE_OFF
    assert state.attributes[ATTR_PERCENTAGE] == 0

    await _call(hass, "turn_on", fan)
    assert device.writes[-1] == (550, [3])  # auto_sensor again

    await _call(hass, "turn_on", fan, percentage=25)
    assert device.writes[-2:] == [(550, [1]), (554, [1])]  # humidity protection

    await _call(hass, "set_percentage", fan, percentage=0)
    assert device.writes[-1] == (550, [0])


async def test_fan_turn_on_with_preset(
    hass: HomeAssistant, device: FakeDevice, fan: str
) -> None:
    await _call(hass, "turn_on", fan, preset_mode="auto_time")
    assert device.writes[-1] == (550, [2])
    device.writes.clear()
    await _call(hass, "turn_on", fan)  # already on: nothing to do
    assert device.writes == []


async def test_fan_write_error(hass: HomeAssistant, device: FakeDevice, fan: str) -> None:
    device.write_exception = 4
    with pytest.raises(HomeAssistantError):
        await _call(hass, "set_preset_mode", fan, preset_mode="manual")


async def test_fan_needs_mode_and_level(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    device.absent.add(554)
    await setup_entry(hass, config_entry)
    with pytest.raises(AssertionError):
        entity_id(hass, config_entry, "fan", "ventilation")


# --- Boost action ----------------------------------------------------------


async def _boost(hass: HomeAssistant, eid: str, **data) -> None:
    await hass.services.async_call(
        DOMAIN, "boost", {ATTR_ENTITY_ID: eid, **data}, blocking=True
    )
    await hass.async_block_till_done()


async def _after(hass: HomeAssistant, minutes: float) -> None:
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=minutes))
    await hass.async_block_till_done()


async def test_boost_for_a_duration(
    hass: HomeAssistant, device: FakeDevice, fan: str
) -> None:
    await _boost(hass, fan, duration=15)
    assert device.writes[-1] == (551, [1])
    await _after(hass, 14)
    assert device.writes[-1] == (551, [1])
    await _after(hass, 16)
    assert device.writes[-1] == (551, [0])


async def test_boost_new_call_replaces_timer(
    hass: HomeAssistant, device: FakeDevice, fan: str, freezer
) -> None:
    await _boost(hass, fan, duration=10)
    freezer.tick(timedelta(minutes=5))
    await _boost(hass, fan, duration=30)
    await _after(hass, 20)  # the first timer would have ended by now
    assert device.writes[-1] == (551, [1])
    await _after(hass, 31)
    assert device.writes[-1] == (551, [0])
    assert device.writes.count((551, [0])) == 1


async def test_boost_without_duration(
    hass: HomeAssistant, device: FakeDevice, fan: str
) -> None:
    """Without a duration the unit decides when the boost ends."""
    await _boost(hass, fan)
    await _after(hass, 24 * 60)
    assert device.writes == [(551, [1])]


async def test_boost_timer_cancelled_on_unload(
    hass: HomeAssistant, device: FakeDevice, fan: str, config_entry
) -> None:
    await _boost(hass, fan, duration=5)
    await hass.config_entries.async_unload(config_entry.entry_id)
    await _after(hass, 10)
    assert device.writes == [(551, [1])]


async def test_boost_end_failure_is_logged(
    hass: HomeAssistant, device: FakeDevice, fan: str, caplog
) -> None:
    await _boost(hass, fan, duration=5)
    device.write_exception = 4
    await _after(hass, 6)
    assert "Ending the boost failed" in caplog.text


async def test_boost_validation(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    device.absent.add(551)
    await setup_entry(hass, config_entry)
    eid = entity_id(hass, config_entry, "fan", "ventilation")
    with pytest.raises(ServiceValidationError) as err:
        await _boost(hass, eid)
    assert err.value.translation_key == "boost_unavailable"
    with pytest.raises(vol.Invalid):
        await _boost(hass, eid, duration=0)
