"""Tests for the write-only bus inputs (bus feed and manual bus numbers)."""

from __future__ import annotations

from datetime import timedelta
import logging

import pytest
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    mock_restore_cache_with_extra_data,
)

from custom_components.maico_kwl.const import (
    CONF_HUMIDITY_SOURCE_ENTITY,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    DOMAIN,
)

from .conftest import FakeDevice
from .helpers import entity_id, setup_entry

REWRITE = timedelta(minutes=9, seconds=1)


async def _setup_with_feeds(hass: HomeAssistant, entry) -> None:
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry,
        options={
            CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room",
            CONF_HUMIDITY_SOURCE_ENTITY: "sensor.humidity",
        },
    )
    await setup_entry(hass, entry)


def _sent_state(hass: HomeAssistant, entry, key: str) -> str:
    eid = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{key}_sent"
    )
    return hass.states.get(eid).state


# --- Bus feed from a source entity ---------------------------------------


async def test_feed_writes_on_setup_and_on_change(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "21.5")
    hass.states.async_set("sensor.humidity", "55")
    await _setup_with_feeds(hass, config_entry)

    assert (707, [215]) in device.writes
    assert (763, [55]) in device.writes
    assert _sent_state(hass, config_entry, "room_temp_bus") == "21.5"

    hass.states.async_set("sensor.room", "22.0")
    await hass.async_block_till_done()
    assert device.writes[-1] == (707, [220])
    assert _sent_state(hass, config_entry, "room_temp_bus") == "22.0"


async def test_feed_replaces_manual_number(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A fed bus input has no manual number, the others keep theirs."""
    await _setup_with_feeds(hass, config_entry)
    with pytest.raises(AssertionError):
        entity_id(hass, config_entry, "number", "room_temp_bus")
    assert entity_id(hass, config_entry, "number", "air_quality_bus")


async def test_feed_clamps_to_register_range(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "50")
    await _setup_with_feeds(hass, config_entry)
    assert (707, [400]) in device.writes
    assert float(_sent_state(hass, config_entry, "room_temp_bus")) == 40.0


@pytest.mark.parametrize("value", ["abc", "unavailable", "unknown"])
async def test_feed_ignores_invalid_states(
    hass: HomeAssistant, device: FakeDevice, config_entry, value: str
) -> None:
    hass.states.async_set("sensor.room", value)
    await _setup_with_feeds(hass, config_entry)
    assert not [w for w in device.writes if w[0] == 707]
    assert _sent_state(hass, config_entry, "room_temp_bus") == STATE_UNKNOWN


async def test_feed_waits_for_missing_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A source that does not exist yet is written once it appears."""
    await _setup_with_feeds(hass, config_entry)
    assert not device.writes

    hass.states.async_set("sensor.room", "20.0")
    await hass.async_block_till_done()
    assert device.writes == [(707, [200])]


async def test_feed_rewrites_periodically(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    device.writes.clear()

    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert (707, [215]) in device.writes


async def test_feed_write_failure_is_logged(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    with caplog.at_level(logging.INFO):
        hass.states.async_set("sensor.room", "22.5")
        await hass.async_block_till_done()
    assert "Bus feed room_temp_bus write failed" in caplog.text


async def test_feed_stops_after_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """After unload nothing is written and no connection is reopened."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    device.writes.clear()

    hass.states.async_set("sensor.room", "23.0")
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert device.writes == []
    assert device.open_connections == 0


async def test_feed_cancels_pending_writes_on_stop(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Writes still pending when the feeder stops are cancelled."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    feeder = config_entry.runtime_data.feeder
    hub = config_entry.runtime_data.hub

    async with hub._lock:  # keep the write waiting for the hub
        hass.states.async_set("sensor.room", "24.0")
        await hass.async_block_till_done(wait_background_tasks=False)
        assert feeder._tasks
        feeder.async_stop()
    await hass.async_block_till_done()
    assert (707, [240]) not in device.writes


async def test_hub_does_not_reconnect_after_close(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    hub = config_entry.runtime_data.hub
    await hub.close()
    with pytest.raises(Exception, match="connection is closed"):
        await hub.read_block(700, 1)
    assert device.open_connections == 0


# --- Manual bus number (no source entity) --------------------------------


async def test_bus_number_writes_value(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    number = entity_id(hass, config_entry, "number", "room_temp_bus")
    assert hass.states.get(number).state == STATE_UNKNOWN

    await hass.services.async_call(
        "number", "set_value", {ATTR_ENTITY_ID: number, "value": 21.0}, blocking=True
    )
    assert device.writes[-1] == (707, [210])
    assert hass.states.get(number).state == "21.0"

    device.writes.clear()
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert device.writes == [(707, [210])]


async def test_bus_number_keeps_value_when_write_fails(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    number = entity_id(hass, config_entry, "number", "room_temp_bus")

    device.write_exception = 4
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "number", "set_value", {ATTR_ENTITY_ID: number, "value": 21.0},
            blocking=True,
        )
    assert hass.states.get(number).state == STATE_UNKNOWN


async def test_bus_number_skips_rewrite_without_value(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert device.writes == []


def _restore(hass: HomeAssistant, entry, value: float) -> str:
    """Pre-register the bus number and give it a restored value."""
    entry.add_to_hass(hass)
    eid = er.async_get(hass).async_get_or_create(
        "number",
        DOMAIN,
        f"{entry.entry_id}_room_temp_bus",
        suggested_object_id="maico_room_temp_bus",
        config_entry=entry,
    ).entity_id
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(eid, str(value)),
                {
                    "native_max_value": 40.0,
                    "native_min_value": 0.0,
                    "native_step": 0.1,
                    "native_unit_of_measurement": "°C",
                    "native_value": value,
                },
            )
        ],
    )
    return eid


async def test_bus_number_restores_and_rewrites_after_restart(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    eid = _restore(hass, config_entry, 19.5)
    await setup_entry(hass, config_entry)
    assert hass.states.get(eid).state == "19.5"
    assert (707, [195]) in device.writes


async def test_bus_number_restore_survives_failed_write(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A rejected write after a restart is only logged."""
    eid = _restore(hass, config_entry, 19.5)
    device.write_exception = 4
    with caplog.at_level(logging.INFO):
        await setup_entry(hass, config_entry)
    assert hass.states.get(eid).state == "19.5"
    assert "Rewrite of room_temp_bus failed" in caplog.text


async def test_feed_logs_outage_once_and_recovery(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A lasting outage is logged once, and once more when writes work again."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    with caplog.at_level(logging.INFO):
        for value in ("22.0", "22.5", "23.0"):
            hass.states.async_set("sensor.room", value)
            await hass.async_block_till_done()
        assert caplog.text.count("Bus feed room_temp_bus write failed") == 1

        device.write_exception = None
        hass.states.async_set("sensor.room", "23.5")
        await hass.async_block_till_done()
    assert "Bus feed room_temp_bus writes succeed again" in caplog.text
    assert device.writes[-1] == (707, [235])


async def test_bus_number_logs_rewrite_outage_once_and_recovery(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    await setup_entry(hass, config_entry)
    number = entity_id(hass, config_entry, "number", "room_temp_bus")
    await hass.services.async_call(
        "number", "set_value", {ATTR_ENTITY_ID: number, "value": 21.0}, blocking=True
    )

    device.write_exception = 4
    now = dt_util.utcnow()
    with caplog.at_level(logging.INFO):
        for step in (1, 2, 3):
            async_fire_time_changed(hass, now + REWRITE * step)
            await hass.async_block_till_done()
        assert caplog.text.count("Rewrite of room_temp_bus failed") == 1

        device.write_exception = None
        async_fire_time_changed(hass, now + REWRITE * 4)
        await hass.async_block_till_done()
    assert "Rewrite of room_temp_bus succeeds again" in caplog.text


async def test_feed_skips_unchanged_values(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Changes that encode to the same raw value are not written again."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    device.writes.clear()

    hass.states.async_set("sensor.room", "21.52")  # still 215 on the wire
    await hass.async_block_till_done()
    assert device.writes == []

    # The periodic refresh always writes.
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert device.writes == [(707, [215])]


async def test_feed_retries_value_after_failed_write(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A value that could not be written is not treated as sent."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    hass.states.async_set("sensor.room", "22.0")
    await hass.async_block_till_done()

    device.write_exception = None
    hass.states.async_set("sensor.room", "22.01")  # same raw value 220
    await hass.async_block_till_done()
    assert device.writes[-1] == (707, [220])


# --- "Sent" sensor ---------------------------------------------------------


def _sent(hass: HomeAssistant, entry, key: str) -> State:
    eid = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{key}_sent"
    )
    return hass.states.get(eid)


async def test_sent_sensor_shows_value_as_written(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The sensor shows the value on the wire, not the raw source value."""
    hass.states.async_set("sensor.humidity", "55.4")
    await _setup_with_feeds(hass, config_entry)

    state = _sent(hass, config_entry, "humidity_bus")
    assert (763, [55]) in device.writes
    assert state.state == "55"
    assert state.attributes["source_entity"] == "sensor.humidity"
    assert state.attributes["last_written"] is not None


async def test_sent_sensor_keeps_value_when_write_fails(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A failed write does not show up as sent."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    hass.states.async_set("sensor.room", "23.0")
    await hass.async_block_till_done()
    assert _sent(hass, config_entry, "room_temp_bus").state == "21.5"


async def test_sent_sensor_unknown_before_first_write(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await _setup_with_feeds(hass, config_entry)
    state = _sent(hass, config_entry, "room_temp_bus")
    assert state.state == STATE_UNKNOWN
    assert state.attributes["last_written"] is None


async def test_sent_sensor_updates_time_on_rewrite(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """The periodic refresh updates the time of the last write."""
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    first = _sent(hass, config_entry, "room_temp_bus").attributes["last_written"]

    freezer.tick(REWRITE)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    state = _sent(hass, config_entry, "room_temp_bus")
    assert state.state == "21.5"
    assert state.attributes["last_written"] > first


async def test_sent_sensor_stops_listening_on_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "21.5")
    await _setup_with_feeds(hass, config_entry)
    feeder = config_entry.runtime_data.feeder
    assert feeder._listeners["room_temp_bus"]

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert feeder._listeners["room_temp_bus"] == []


async def test_manual_number_removed_and_restored_with_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Configuring a source removes the manual number, clearing it restores it."""
    await setup_entry(hass, config_entry)
    unique_id = f"{config_entry.entry_id}_room_temp_bus"
    ent_reg = er.async_get(hass)
    assert ent_reg.async_get_entity_id("number", DOMAIN, unique_id)

    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}
    )
    await hass.async_block_till_done()  # options change reloads the entry
    assert ent_reg.async_get_entity_id("number", DOMAIN, unique_id) is None
    # The other bus inputs keep their manual number.
    assert entity_id(hass, config_entry, "number", "humidity_bus")

    hass.config_entries.async_update_entry(config_entry, options={})
    await hass.async_block_till_done()
    eid = ent_reg.async_get_entity_id("number", DOMAIN, unique_id)
    assert eid is not None
    assert hass.states.get(eid).state == STATE_UNKNOWN
