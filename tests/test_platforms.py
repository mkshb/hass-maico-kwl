"""Tests for the entity platforms: states and write actions."""

from __future__ import annotations

import pytest
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry


@pytest.fixture
async def loaded(hass: HomeAssistant, device: FakeDevice, config_entry):
    await setup_entry(hass, config_entry)
    return config_entry


def _state(hass: HomeAssistant, entry, platform: str, key: str) -> str:
    return hass.states.get(entity_id(hass, entry, platform, key)).state


async def _refresh(hass: HomeAssistant, entry) -> None:
    await entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("temp_room", "21.5"),
        ("temp_air_intake", "-5.0"),  # signed
        ("humidity_exhaust", "45"),  # not scaled on this unit
        ("fan_speed_supply", "1450"),
        ("op_hours_nominal", "65546"),  # High/Low word pair
        ("current_vent_level", "nominal"),  # enum
        ("fault_code", "0"),
    ],
)
async def test_sensor_states(hass: HomeAssistant, loaded, key: str, expected: str) -> None:
    assert _state(hass, loaded, "sensor", key) == expected


async def test_enum_sensor_unknown_raw_value(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """A raw value outside the documented enum shows as unknown."""
    device.registers[650] = 9
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "sensor", "current_vent_level") == STATE_UNKNOWN


async def test_absent_registers_create_no_entities(hass: HomeAssistant, loaded) -> None:
    """Registers the unit does not implement get no entity."""
    with pytest.raises(AssertionError):
        entity_id(hass, loaded, "sensor", "brine_pump_state")


async def test_binary_sensor_states(hass: HomeAssistant, loaded) -> None:
    assert _state(hass, loaded, "binary_sensor", "fan_supply_active") == STATE_ON
    assert _state(hass, loaded, "binary_sensor", "summer_bypass_open") == STATE_OFF


async def test_problem_sensor(hass: HomeAssistant, device: FakeDevice, loaded) -> None:
    """The problem sensor follows the fault code and its availability."""
    assert _state(hass, loaded, "binary_sensor", "problem") == STATE_OFF

    device.registers[402] = 4
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "binary_sensor", "problem") == STATE_ON

    device.absent |= {401, 402}
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "binary_sensor", "problem") == STATE_UNAVAILABLE


async def test_number_state_and_write(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """Numbers show the scaled value and write the encoded raw value."""
    setpoint = entity_id(hass, loaded, "number", "room_setpoint")
    offset = entity_id(hass, loaded, "number", "room_temp_offset")
    assert hass.states.get(setpoint).state == "21.5"
    assert hass.states.get(offset).state == "-1.0"

    await hass.services.async_call(
        "number", "set_value", {ATTR_ENTITY_ID: setpoint, "value": 22.5}, blocking=True
    )
    await hass.services.async_call(
        "number", "set_value", {ATTR_ENTITY_ID: offset, "value": -1.5}, blocking=True
    )
    await hass.async_block_till_done()
    assert (553, [225]) in device.writes
    assert (300, [0xFFF1]) in device.writes
    assert hass.states.get(setpoint).state == "22.5"


async def test_select_state_and_write(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    mode = entity_id(hass, loaded, "select", "operating_mode")
    assert hass.states.get(mode).state == "auto_sensor"

    await hass.services.async_call(
        "select", "select_option", {ATTR_ENTITY_ID: mode, "option": "manual"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert device.writes[-1] == (550, [1])
    assert hass.states.get(mode).state == "manual"


async def test_select_unknown_option_is_ignored(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """An option without a raw value is not written (defensive path)."""
    select = hass.data["entity_components"]["select"].get_entity(
        entity_id(hass, loaded, "select", "operating_mode")
    )
    await select.async_select_option("not_an_option")
    assert device.writes == []


async def test_switch_turn_on_and_off(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    boost = entity_id(hass, loaded, "switch", "boost_ventilation")
    assert hass.states.get(boost).state == STATE_OFF

    await hass.services.async_call(
        "switch", "turn_on", {ATTR_ENTITY_ID: boost}, blocking=True
    )
    await hass.async_block_till_done()
    assert device.writes[-1] == (551, [1])
    assert hass.states.get(boost).state == STATE_ON

    await hass.services.async_call(
        "switch", "turn_off", {ATTR_ENTITY_ID: boost}, blocking=True
    )
    assert device.writes[-1] == (551, [0])


@pytest.mark.parametrize(
    ("key", "address"), [("filter_reset_device", 157), ("error_reset", 405)]
)
async def test_button_press(
    hass: HomeAssistant, device: FakeDevice, loaded, key: str, address: int
) -> None:
    button = entity_id(hass, loaded, "button", key)
    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: button}, blocking=True
    )
    assert device.writes[-1] == (address, [1])


@pytest.mark.parametrize("failure", ["rejected", "offline"])
async def test_failed_write_raises_home_assistant_error(
    hass: HomeAssistant, device: FakeDevice, loaded, failure: str
) -> None:
    """Rejected writes and connection loss surface as HomeAssistantError."""
    if failure == "rejected":
        device.write_exception = 4
    else:
        device.online = False
    boost = entity_id(hass, loaded, "switch", "boost_ventilation")
    with pytest.raises(HomeAssistantError, match="boost_ventilation"):
        await hass.services.async_call(
            "switch", "turn_on", {ATTR_ENTITY_ID: boost}, blocking=True
        )


async def test_problem_sensor_attributes(hass: HomeAssistant, loaded) -> None:
    """The problem sensor sits on the unit's device as a diagnostic entity."""
    ent_reg = er.async_get(hass)
    problem = ent_reg.async_get(entity_id(hass, loaded, "binary_sensor", "problem"))
    fault = ent_reg.async_get(entity_id(hass, loaded, "sensor", "fault_code"))

    assert problem.device_id == fault.device_id
    assert problem.entity_category is EntityCategory.DIAGNOSTIC
    assert problem.original_device_class == "problem"
    assert problem.original_icon is None
    assert problem.translation_key == "problem"
