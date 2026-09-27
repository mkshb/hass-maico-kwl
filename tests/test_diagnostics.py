"""Tests for the config entry diagnostics."""

from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)

from custom_components.maico_kwl.const import CONF_HOST, CONF_ROOM_TEMP_SOURCE_ENTITY

from .conftest import HOST, FakeDevice
from .helpers import CELSIUS, setup_entry


async def test_diagnostics(
    hass: HomeAssistant, hass_client, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}
    )
    assert await async_setup_component(hass, "diagnostics", {})
    await setup_entry(hass, config_entry)

    diag = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    # The host does not leak, neither directly nor through title or unique_id.
    assert diag["entry"]["data"][CONF_HOST] == REDACTED
    assert diag["entry"]["title"] == REDACTED
    assert diag["entry"]["unique_id"] == REDACTED
    assert HOST not in str(diag)
    assert diag["entry"]["options"] == {CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}

    assert diag["profile"]["model"].startswith("Maico KWL")
    assert diag["last_update_success"] is True
    assert diag["registers"]["temp_room"] == {
        "address": 700,
        "value": 21.5,
        "raw": [215],
    }
    assert diag["registers"]["temp_air_intake"]["raw"] == [0xFFCE]  # signed
    assert diag["registers"]["op_hours_nominal"]["raw"] == [1, 10]  # u32 pair
    assert diag["registers"]["clock_deviation"] == {
        "address": 100,
        "value": "2026-09-26T10:30:15",
        "raw": [2026, 9, 26, 10, 30, 15],
    }
    assert diag["registers"]["error_reset"] == {"address": 405, "polled": False}
    assert diag["registers"]["room_temp_bus"] == {"address": 707, "polled": False}
    assert diag["absent_registers"]["brine_pump_state"] == 806
    assert "brine_pump_state" not in diag["registers"]

    assert diag["bus_inputs"]["room_temp_bus"]["value"] == 21.5
    assert "written_at" in diag["bus_inputs"]["room_temp_bus"]


async def test_diagnostics_register_missing_this_cycle(
    hass: HomeAssistant, hass_client, device: FakeDevice, config_entry
) -> None:
    """A present register without a value this cycle has no value entry."""
    assert await async_setup_component(hass, "diagnostics", {})
    await setup_entry(hass, config_entry)
    device.absent.add(704)
    device.registers[101] = 0  # clock not set
    await config_entry.runtime_data.coordinator.async_refresh()

    diag = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)
    assert diag["registers"]["temp_supply_air"] == {"address": 704}
    assert diag["registers"]["clock_deviation"] == {"address": 100, "value": None}
    assert diag["bus_inputs"] == {}
