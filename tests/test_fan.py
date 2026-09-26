"""Tests for the fan entity (operating mode + ventilation level)."""

from __future__ import annotations

import pytest
from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PRESET_MODE,
    ATTR_PRESET_MODES,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

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
