"""Tests for the entity platforms: states and write actions."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.maico_kwl.const import CONF_DISCOVERY, DOMAIN
from custom_components.maico_kwl.entity import async_write_register
from custom_components.maico_kwl.register_defs import REGISTERS_BY_KEY

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


async def test_bit_sensors(hass: HomeAssistant, device: FakeDevice, loaded) -> None:
    """Filter and frost sensors follow single bits of the notice code."""
    keys = [
        "device_filter_dirty",
        "outdoor_filter_dirty",
        "room_filter_dirty",
        "frost_protection_active",
    ]
    assert [_state(hass, loaded, "binary_sensor", key) for key in keys] == [
        STATE_OFF
    ] * 4

    device.registers[404] = (1 << 10) | (1 << 6)  # outdoor filter, frost
    await _refresh(hass, loaded)
    assert [_state(hass, loaded, "binary_sensor", key) for key in keys] == [
        STATE_OFF,
        STATE_ON,
        STATE_OFF,
        STATE_ON,
    ]

    ent_reg = er.async_get(hass)
    room = ent_reg.async_get(entity_id(hass, loaded, "binary_sensor", "room_filter_dirty"))
    assert room.original_device_class == "problem"
    assert room.entity_category is None

    device.absent |= {403, 404}
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "binary_sensor", "room_filter_dirty") == STATE_UNAVAILABLE


async def test_code_sensors_list_active_bits(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """Fault and notice code sensors name the bits that are set."""
    notice = entity_id(hass, loaded, "sensor", "notice_code")
    assert hass.states.get(notice).attributes["active"] == []

    device.registers[404] = 0x2010
    device.registers[402] = 2
    await _refresh(hass, loaded)
    assert hass.states.get(notice).state == "8208"
    assert hass.states.get(notice).attributes["active"] == [
        "bypass_active",
        "humidity_protection_active",
    ]
    fault = entity_id(hass, loaded, "sensor", "fault_code")
    assert hass.states.get(fault).attributes["active"] == ["exhaust_fan"]
    temp = entity_id(hass, loaded, "sensor", "temp_room")
    assert "active" not in hass.states.get(temp).attributes


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
    with pytest.raises(HomeAssistantError) as err:
        await hass.services.async_call(
            "switch", "turn_on", {ATTR_ENTITY_ID: boost}, blocking=True
        )
    assert err.value.translation_key == "write_failed"
    assert str(err.value).startswith(f"Writing {boost} to the Maico KWL failed: ")


async def test_value_the_register_cannot_hold_is_not_written(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """A write that fails in encode is a clear error, and nothing reaches the unit."""
    reg = REGISTERS_BY_KEY["filter_dp_allowed"]
    with pytest.raises(HomeAssistantError) as err:
        await async_write_register(
            loaded.runtime_data.coordinator, reg, 70000, "number.test"
        )
    assert err.value.translation_key == "value_out_of_range"
    assert not device.writes


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


async def test_clock_deviation_sensor(
    hass: HomeAssistant, device: FakeDevice, loaded, freezer
) -> None:
    """The unit's local clock is shown as its deviation from HA's clock."""
    local = datetime(2026, 9, 26, 10, 30, 0, tzinfo=dt_util.get_default_time_zone())
    freezer.move_to(local)
    await _refresh(hass, loaded)
    eid = entity_id(hass, loaded, "sensor", "clock_deviation")
    state = hass.states.get(eid)
    assert state.state == "15"  # unit clock 10:30:15, 15 s ahead
    assert state.attributes["unit_of_measurement"] == "s"
    assert state.attributes["state_class"] == "measurement"

    # Read 0.6 s later: 14 s, within the tolerance, so the state stays.
    freezer.move_to(local.replace(microsecond=600000))
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "sensor", "clock_deviation") == "15"

    freezer.move_to(local.replace(minute=32))
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "sensor", "clock_deviation") == "-105"

    device.registers[101] = 0  # month 0: clock not set
    await _refresh(hass, loaded)
    assert _state(hass, loaded, "sensor", "clock_deviation") == STATE_UNKNOWN


async def test_clock_sync_button(
    hass: HomeAssistant, device: FakeDevice, loaded, freezer
) -> None:
    """Pressing the button writes HA's local time to 100-105 in one request."""
    freezer.move_to("2026-09-26T12:00:05+00:00")
    local = dt_util.now()
    button = entity_id(hass, loaded, "button", "clock_sync")
    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: button}, blocking=True
    )
    assert device.writes[-1] == (
        100,
        [local.year, local.month, local.day, local.hour, local.minute, local.second],
    )


async def test_rediscover_button(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """Pressing the button probes the unit again, e.g. after adding EnOcean."""
    assert "enocean_co2_id0" not in loaded.runtime_data.coordinator.present
    device.absent -= set(range(350, 374))  # EnOcean module retrofitted
    device.registers[350] = 6500  # with a CO2 sensor at ID0

    button = entity_id(hass, loaded, "button", "rediscover")
    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: button}, blocking=True
    )
    await hass.async_block_till_done()

    assert loaded.state is ConfigEntryState.LOADED
    assert "enocean_co2_id0" in loaded.runtime_data.coordinator.present
    assert "enocean_co2_id0" in loaded.data[CONF_DISCOVERY]["present"]
    registry_entry = er.async_get(hass).async_get(button)
    assert registry_entry.entity_category is EntityCategory.DIAGNOSTIC


async def _rediscover(hass: HomeAssistant, entry) -> None:
    button = entity_id(hass, entry, "button", "rediscover")
    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: button}, blocking=True
    )
    await hass.async_block_till_done()


async def test_rediscover_disables_entities_of_missing_registers(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Entities of registers the unit no longer answers are disabled, not removed.

    They keep what the user set, and come back with it.
    """
    device.registers[109] = 1  # room temperature from the external sensor
    loaded = config_entry
    await setup_entry(hass, loaded)
    ent_reg = er.async_get(hass)
    humidity = entity_id(hass, loaded, "sensor", "humidity_exhaust")
    dew_point = entity_id(hass, loaded, "sensor", "dew_point_extract")
    # Disabled by default: in the registry without a state, and still wanted.
    external = entity_id(hass, loaded, "sensor", "temp_room_external")
    assert hass.states.get(external) is None
    ent_reg.async_update_entity(humidity, name="Bad", area_id="bathroom")

    device.absent.add(750)  # humidity sensor removed from the unit
    await _rediscover(hass, loaded)

    assert loaded.state is ConfigEntryState.LOADED
    for eid in (humidity, dew_point):  # the dew point is derived from it
        entry = ent_reg.async_get(eid)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
        assert hass.states.get(eid) is None
    assert ent_reg.async_get(humidity).name == "Bad"
    assert ent_reg.async_get(external).disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert ent_reg.async_get(entity_id(hass, loaded, "sensor", "temp_room")).disabled_by is None

    device.absent.discard(750)  # the sensor is back
    await _rediscover(hass, loaded)
    entry = ent_reg.async_get(humidity)
    assert entry.disabled_by is None
    assert (entry.name, entry.area_id) == ("Bad", "bathroom")
    assert DOMAIN not in entry.options
    assert hass.states.get(humidity).state == "45"
    assert hass.states.get(dew_point) is not None
    # Enabling makes HA reload the entry once; the entities stay as they are.
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=31))
    await hass.async_block_till_done()
    assert loaded.state is ConfigEntryState.LOADED
    assert ent_reg.async_get(humidity).disabled_by is None
    assert ent_reg.async_get(external).disabled_by is er.RegistryEntryDisabler.INTEGRATION


async def test_cleanup_leaves_entities_the_user_disabled(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """Only what the cleanup disabled itself is enabled again."""
    ent_reg = er.async_get(hass)
    humidity = entity_id(hass, loaded, "sensor", "humidity_exhaust")
    ent_reg.async_update_entity(
        humidity, disabled_by=er.RegistryEntryDisabler.USER
    )
    device.absent.add(750)
    await _rediscover(hass, loaded)
    assert DOMAIN not in ent_reg.async_get(humidity).options

    device.absent.discard(750)
    await _rediscover(hass, loaded)
    assert ent_reg.async_get(humidity).disabled_by is er.RegistryEntryDisabler.USER
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=31))
    await hass.async_block_till_done()


async def test_filter_that_is_not_fitted_creates_no_entities(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A missing outdoor filter leaves out all of its entities."""
    device.registers[656] = 0
    await setup_entry(hass, config_entry)
    ent_reg = er.async_get(hass)
    unique_ids = {
        entry.unique_id
        for entry in er.async_entries_for_config_entry(ent_reg, config_entry.entry_id)
    }
    prefix = config_entry.entry_id
    for key in (
        "filter_runtime_outdoor",
        "filter_reset_outdoor",
        "filter_remaining_outdoor",
        "filter_due_outdoor",
        "outdoor_filter_dirty",
    ):
        assert f"{prefix}_{key}" not in unique_ids
    for key in ("filter_reset_room", "room_filter_dirty", "filter_due_room"):
        assert f"{prefix}_{key}" in unique_ids


async def test_rediscover_keeps_a_filter_that_ran_out(
    hass: HomeAssistant, device: FakeDevice, loaded
) -> None:
    """At 0 days without a notice bit, a filter detected before stays."""
    due = entity_id(hass, loaded, "binary_sensor", "filter_due_outdoor")
    device.registers[656] = 0
    await _rediscover(hass, loaded)
    assert "outdoor_filter" in loaded.data[CONF_DISCOVERY]["accessories"]
    assert hass.states.get(due).state == "on"
