"""Run the bundled blueprints against the simulated unit."""

from __future__ import annotations

import shutil
from datetime import timedelta
from pathlib import Path

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry

BLUEPRINTS = Path(__file__).parent.parent / "blueprints" / "automation" / "maico_kwl"
SENSOR = "sensor.co2"
WINDOW = "binary_sensor.window"


@pytest.fixture
async def unit(hass: HomeAssistant, device: FakeDevice, config_entry):
    """The unit in auto_sensor mode at nominal level, plus the blueprints."""
    target = Path(hass.config.path("blueprints/automation/maico_kwl"))
    target.mkdir(parents=True, exist_ok=True)
    for blueprint in BLUEPRINTS.glob("*.yaml"):
        shutil.copy(blueprint, target / blueprint.name)
    await setup_entry(hass, config_entry)
    assert await async_setup_component(hass, "scene", {})
    return {
        "mode": entity_id(hass, config_entry, "select", "operating_mode"),
        "level": entity_id(hass, config_entry, "select", "ventilation_level"),
    }


async def _automation(hass: HomeAssistant, path: str, inputs: dict) -> None:
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": {
                "id": "maico_test",
                "use_blueprint": {"path": f"maico_kwl/{path}", "input": inputs},
            }
        },
    )
    await hass.async_block_till_done()


async def _settle(hass: HomeAssistant) -> None:
    """Let the debounced refresh after a write update the entities."""
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11))
    await hass.async_block_till_done()


async def _set(hass: HomeAssistant, entity: str, state: str) -> None:
    hass.states.async_set(entity, state)
    await _settle(hass)


def _unit(hass: HomeAssistant, unit: dict) -> tuple[str, str]:
    return hass.states.get(unit["mode"]).state, hass.states.get(unit["level"]).state


async def _select(hass: HomeAssistant, entity: str, option: str) -> None:
    await hass.services.async_call(
        "select", "select_option", {"entity_id": entity, "option": option}, blocking=True
    )
    await _settle(hass)


@pytest.fixture
async def boost(hass: HomeAssistant, unit: dict) -> dict:
    await _set(hass, SENSOR, "600")
    await _automation(
        hass,
        "demand_boost.yaml",
        {
            "operating_mode": unit["mode"],
            "level": unit["level"],
            "sensor": SENSOR,
            "revert_mode": "auto_time",
        },
    )
    return unit


async def test_boost_and_restore(hass: HomeAssistant, boost: dict) -> None:
    await _set(hass, SENSOR, "1200")
    assert _unit(hass, boost) == ("manual", "intensive")
    await _set(hass, SENSOR, "700")
    assert _unit(hass, boost) == ("auto_sensor", "nominal")


async def test_boost_keeps_a_change_by_the_user(hass: HomeAssistant, boost: dict) -> None:
    await _set(hass, SENSOR, "1200")
    await _select(hass, boost["level"], "reduced")
    await _set(hass, SENSOR, "1300")  # still high: no second boost
    assert _unit(hass, boost) == ("manual", "reduced")
    await _set(hass, SENSOR, "700")  # no restore over the user's setting
    assert _unit(hass, boost) == ("manual", "reduced")
    await _set(hass, SENSOR, "1200")  # a new boost works again
    assert _unit(hass, boost) == ("manual", "intensive")


async def test_boost_leaves_a_manual_boost_alone(hass: HomeAssistant, boost: dict) -> None:
    await _select(hass, boost["mode"], "manual")
    await _select(hass, boost["level"], "intensive")
    await _set(hass, SENSOR, "1200")
    await _set(hass, SENSOR, "700")
    assert _unit(hass, boost) == ("manual", "intensive")


async def test_boost_ends_after_a_restart(hass: HomeAssistant, boost: dict) -> None:
    """The snapshot is lost; a restart during the boost still ends it later."""
    await _set(hass, SENSOR, "1200")
    await hass.services.async_call(
        "scene", "delete", {"entity_id": "scene.maico_kwl_boost_maico_test"}, blocking=True
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await _settle(hass)
    assert _unit(hass, boost) == ("manual", "intensive")  # value still high
    await _set(hass, SENSOR, "700")
    assert _unit(hass, boost)[0] == "auto_time"  # fallback revert mode


async def test_boost_ends_after_a_restart_in_manual(hass: HomeAssistant, unit: dict) -> None:
    """With the fallback mode manual, the fallback level ends the boost too."""
    await _set(hass, SENSOR, "600")
    await _automation(
        hass,
        "demand_boost.yaml",
        {
            "operating_mode": unit["mode"],
            "level": unit["level"],
            "sensor": SENSOR,
            "revert_mode": "manual",
            "revert_level": "reduced",
        },
    )
    await _set(hass, SENSOR, "1200")
    await hass.services.async_call(
        "scene", "delete", {"entity_id": "scene.maico_kwl_boost_maico_test"}, blocking=True
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await _settle(hass)
    await _set(hass, SENSOR, "700")
    assert _unit(hass, unit) == ("manual", "reduced")


@pytest.fixture
async def window(hass: HomeAssistant, unit: dict) -> dict:
    await _set(hass, WINDOW, "off")
    await _automation(
        hass,
        "window_open_reduce.yaml",
        {
            "operating_mode": unit["mode"],
            "level": unit["level"],
            "windows": [WINDOW],
            "restore_mode": "auto_time",
        },
    )
    return unit


async def test_window_reduce_and_restore(hass: HomeAssistant, window: dict) -> None:
    await _set(hass, WINDOW, "on")
    assert _unit(hass, window) == ("manual", "reduced")
    await _set(hass, WINDOW, "off")
    assert _unit(hass, window) == ("auto_sensor", "nominal")


async def test_window_keeps_a_change_by_the_user(hass: HomeAssistant, window: dict) -> None:
    await _set(hass, WINDOW, "on")
    await _select(hass, window["level"], "nominal")
    await _set(hass, WINDOW, "off")
    assert _unit(hass, window) == ("manual", "nominal")


async def test_window_restores_after_a_restart(hass: HomeAssistant, window: dict) -> None:
    await _set(hass, WINDOW, "on")
    await hass.services.async_call(
        "scene", "delete", {"entity_id": "scene.maico_kwl_window_maico_test"}, blocking=True
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await _settle(hass)
    assert _unit(hass, window) == ("manual", "reduced")  # window still open
    await _set(hass, WINDOW, "off")
    assert _unit(hass, window)[0] == "auto_time"


async def test_window_restores_after_a_restart_in_manual(
    hass: HomeAssistant, unit: dict
) -> None:
    """With the fallback mode manual, the unit does not stay at the open level."""
    await _set(hass, WINDOW, "off")
    await _automation(
        hass,
        "window_open_reduce.yaml",
        {
            "operating_mode": unit["mode"],
            "level": unit["level"],
            "windows": [WINDOW],
            "open_level": "off",
            "restore_mode": "manual",
        },
    )
    await _set(hass, WINDOW, "on")
    assert _unit(hass, unit) == ("manual", "off")
    await hass.services.async_call(
        "scene", "delete", {"entity_id": "scene.maico_kwl_window_maico_test"}, blocking=True
    )
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STARTED)
    await _settle(hass)
    await _set(hass, WINDOW, "off")
    assert _unit(hass, unit) == ("manual", "nominal")  # the default fallback level
