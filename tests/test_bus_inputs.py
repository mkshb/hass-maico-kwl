"""Tests for the write-only bus inputs (bus feed from a source entity)."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

import pytest
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import CoreState, HomeAssistant, State
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    mock_restore_cache_with_extra_data,
)

from custom_components.maico_kwl.const import (
    CONF_AIR_QUALITY_SOURCE_ENTITY,
    CONF_HUMIDITY_SOURCE_ENTITY,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    DOMAIN,
)

from .conftest import FakeDevice
from .helpers import CELSIUS, PERCENT, PPM, entity_id, setup_entry

REWRITE = timedelta(minutes=8, seconds=1)


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


async def _setup_with_air_quality(hass: HomeAssistant, entry) -> None:
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry,
        options={
            CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room",
            CONF_HUMIDITY_SOURCE_ENTITY: "sensor.humidity",
            CONF_AIR_QUALITY_SOURCE_ENTITY: "sensor.air",
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    hass.states.async_set("sensor.humidity", "55", PERCENT)
    await _setup_with_feeds(hass, config_entry)

    assert (707, [215]) in device.writes
    assert (763, [55]) in device.writes
    assert _sent_state(hass, config_entry, "room_temp_bus") == "21.5"

    hass.states.async_set("sensor.room", "22.0", CELSIUS)
    await hass.async_block_till_done()
    assert device.writes[-1] == (707, [220])
    assert _sent_state(hass, config_entry, "room_temp_bus") == "22.0"


async def test_nothing_is_sent_without_a_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Only inputs with a source are written; there is no manual number."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert {reg for reg, _ in device.writes} == {707}
    for key in ("room_temp_bus", "humidity_bus", "air_quality_bus"):
        with pytest.raises(AssertionError):
            entity_id(hass, config_entry, "number", key)


@pytest.mark.parametrize(
    ("source", "state", "attributes", "register", "raw"),
    [
        ("sensor.room", "21.5", {"unit_of_measurement": "°C"}, 707, [215]),
        ("sensor.room", "70.7", {"unit_of_measurement": "°F"}, 707, [215]),
        ("sensor.room", "294.65", {"unit_of_measurement": "K"}, 707, [215]),
        ("sensor.humidity", "100.4", {"unit_of_measurement": "%"}, 763, [100]),
        ("sensor.air", "650", {"unit_of_measurement": "ppm"}, 764, [650]),
        ("sensor.air", "1500", {"unit_of_measurement": "ppb"}, 764, [2]),
    ],
)
async def test_feed_converts_units(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    source: str,
    state: str,
    attributes: dict[str, str],
    register: int,
    raw: list[int],
) -> None:
    """Units HA can convert unambiguously reach the unit in its own unit."""
    hass.states.async_set(source, state, attributes)
    await _setup_with_air_quality(hass, config_entry)
    assert (register, raw) in device.writes


@pytest.mark.parametrize(
    ("source", "state", "attributes"),
    [
        ("sensor.room", "21.5", {}),  # no unit
        ("sensor.room", "50", CELSIUS),  # above 40
        ("sensor.room", "-0.1", CELSIUS),  # below 0
        ("sensor.humidity", "55", {}),
        ("sensor.humidity", "100.6", PERCENT),
        ("sensor.air", "42", {"device_class": "aqi"}),  # AQI has no unit
        ("sensor.air", "12", {"unit_of_measurement": "µg/m³"}),
        ("sensor.air", "55", PERCENT),
        ("sensor.air", "5001", PPM),
    ],
)
async def test_feed_skips_unsuitable_values(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    source: str,
    state: str,
    attributes: dict[str, str],
) -> None:
    """Nothing is sent rather than a wrong value or a limit."""
    hass.states.async_set(source, state, attributes)
    await _setup_with_air_quality(hass, config_entry)
    assert device.writes == []


@pytest.mark.parametrize(
    "value", ["abc", "unavailable", "unknown", "nan", "inf", "-inf"]
)
async def test_feed_ignores_invalid_states(
    hass: HomeAssistant, device: FakeDevice, config_entry, value: str
) -> None:
    hass.states.async_set("sensor.room", value, CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    assert not [w for w in device.writes if w[0] == 707]
    assert _sent_state(hass, config_entry, "room_temp_bus") == STATE_UNKNOWN


async def test_feed_skips_non_finite_values_and_logs_once(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """NaN would stop the feed, infinity would be sent as the register limit."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    writes = len(device.writes)

    with caplog.at_level(logging.INFO):
        for value in ("nan", "inf", "nan"):
            hass.states.async_set("sensor.room", value, CELSIUS)
            await hass.async_block_till_done()
        async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
        await hass.async_block_till_done()
        assert len(device.writes) == writes
        assert _sent_state(hass, config_entry, "room_temp_bus") == "21.5"
        assert caplog.text.count("sensor.room is not sent") == 1

        hass.states.async_set("sensor.room", "22.0", CELSIUS)
        await hass.async_block_till_done()
    assert "sensor.room is sent again" in caplog.text
    assert device.writes[-1] == (707, [220])


async def test_feed_waits_for_missing_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A source that does not exist yet is written once it appears."""
    await _setup_with_feeds(hass, config_entry)
    assert not device.writes

    hass.states.async_set("sensor.room", "20.0", CELSIUS)
    await hass.async_block_till_done()
    assert device.writes == [(707, [200])]


async def test_feed_rewrites_periodically(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    with caplog.at_level(logging.INFO):
        hass.states.async_set("sensor.room", "22.5", CELSIUS)
        await hass.async_block_till_done()
    assert "Bus input room_temp_bus: write failed" in caplog.text


async def test_feed_stops_after_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """After unload nothing is written and no connection is reopened."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    device.writes.clear()

    hass.states.async_set("sensor.room", "23.0", CELSIUS)
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()
    assert device.writes == []
    assert device.open_connections == 0


async def test_feed_cancels_pending_writes_on_stop(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Writes still pending when the feeder stops are cancelled."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    feeder = config_entry.runtime_data.feeder

    connection = device.clients[0]
    original = connection.write_registers
    release = asyncio.Event()

    async def held(**kwargs):  # keep the write waiting for the unit
        await release.wait()
        return await original(**kwargs)

    connection.write_registers = held
    hass.states.async_set("sensor.room", "24.0", CELSIUS)
    await hass.async_block_till_done(wait_background_tasks=False)
    assert feeder._tasks
    feeder.async_stop()
    release.set()
    await hass.async_block_till_done()
    assert (707, [240]) not in device.writes


async def test_hub_sends_nothing_after_close(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The shared connection may stay open for another holder after unload."""
    await setup_entry(hass, config_entry)
    hub = config_entry.runtime_data.hub
    hub.close()
    reads = device.reads
    with pytest.raises(Exception, match="connection is closed"):
        await hub.read_block(700, 1)
    assert device.reads == reads


# --- Manual bus numbers of earlier versions ------------------------------


async def test_old_manual_number_sends_nothing(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A restored manual value is no longer written, and its entity disabled.

    Before 0.4.2 a manual number kept writing the value once set, e.g. an old
    test value from a second Home Assistant instance.
    """
    config_entry.add_to_hass(hass)
    ent_reg = er.async_get(hass)
    eid = ent_reg.async_get_or_create(
        "number",
        DOMAIN,
        f"{config_entry.entry_id}_humidity_bus",
        suggested_object_id="maico_humidity_bus",
        config_entry=config_entry,
    ).entity_id
    mock_restore_cache_with_extra_data(
        hass, [(State(eid, "80.0"), {"native_value": 80.0})]
    )
    await setup_entry(hass, config_entry)
    async_fire_time_changed(hass, dt_util.utcnow() + REWRITE)
    await hass.async_block_till_done()

    assert not device.writes
    assert ent_reg.async_get(eid).disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert hass.states.get(eid) is None


async def test_feed_logs_outage_once_and_recovery(
    hass: HomeAssistant,
    device: FakeDevice,
    config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A lasting outage is logged once, and once more when writes work again."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    with caplog.at_level(logging.INFO):
        for value in ("22.0", "22.5", "23.0"):
            hass.states.async_set("sensor.room", value, CELSIUS)
            await hass.async_block_till_done()
        assert caplog.text.count("Bus input room_temp_bus: write failed") == 1

        device.write_exception = None
        hass.states.async_set("sensor.room", "23.5", CELSIUS)
        await hass.async_block_till_done()
    assert "Bus input room_temp_bus: writes succeed again" in caplog.text
    assert device.writes[-1] == (707, [235])


async def test_feed_skips_unchanged_values(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Changes that encode to the same raw value are not written again."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    device.writes.clear()

    hass.states.async_set("sensor.room", "21.52", CELSIUS)  # still 215 on the wire
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    hass.states.async_set("sensor.room", "22.0", CELSIUS)
    await hass.async_block_till_done()

    device.write_exception = None
    hass.states.async_set("sensor.room", "22.01", CELSIUS)  # same raw value 220
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
    hass.states.async_set("sensor.humidity", "55.4", PERCENT)
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)

    device.write_exception = 4
    hass.states.async_set("sensor.room", "23.0", CELSIUS)
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
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
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    feeder = config_entry.runtime_data.feeder
    assert feeder._listeners["room_temp_bus"]

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert feeder._listeners["room_temp_bus"] == []


async def test_sent_sensor_disabled_with_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Clearing a source disables its "sent" sensor instead of orphaning it."""
    await _setup_with_feeds(hass, config_entry)
    ent_reg = er.async_get(hass)
    eid = ent_reg.async_get_entity_id(
        "sensor", DOMAIN, f"{config_entry.entry_id}_humidity_bus_sent"
    )

    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}
    )
    await hass.async_block_till_done()
    assert ent_reg.async_get(eid).disabled_by is er.RegistryEntryDisabler.INTEGRATION
    room = ent_reg.async_get_entity_id(
        "sensor", DOMAIN, f"{config_entry.entry_id}_room_temp_bus_sent"
    )
    assert ent_reg.async_get(room).disabled_by is None


# --- Source renamed, gone or without data ----------------------------------


def _issue(hass: HomeAssistant, entry, key: str, issue: str):
    return ir.async_get(hass).async_get_issue(
        DOMAIN, f"{entry.entry_id}_{key}_{issue}"
    )


async def _tick(hass: HomeAssistant, freezer, delta: timedelta = REWRITE) -> None:
    freezer.tick(delta)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_feed_follows_a_renamed_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    ent_reg = er.async_get(hass)
    ent_reg.async_get_or_create("sensor", "test", "room", suggested_object_id="room")
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)

    ent_reg.async_update_entity("sensor.room", new_entity_id="sensor.living_room")
    await hass.async_block_till_done()  # options change reloads the entry
    assert config_entry.options[CONF_ROOM_TEMP_SOURCE_ENTITY] == "sensor.living_room"
    assert config_entry.options[CONF_HUMIDITY_SOURCE_ENTITY] == "sensor.humidity"

    hass.states.async_set("sensor.living_room", "23.0", CELSIUS)
    await hass.async_block_till_done()
    assert device.writes[-1] == (707, [230])


async def test_issue_when_the_source_is_removed(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    ent_reg = er.async_get(hass)
    ent_reg.async_get_or_create("sensor", "test", "room", suggested_object_id="room")
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing") is None

    ent_reg.async_remove("sensor.room")
    hass.states.async_remove("sensor.room")
    await hass.async_block_till_done()
    issue = _issue(hass, config_entry, "room_temp_bus", "bus_source_missing")
    assert issue.translation_placeholders["entity"] == "sensor.room"

    hass.states.async_set("sensor.room", "22.0", CELSIUS)  # back again
    await hass.async_block_till_done()
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing") is None


async def test_issue_when_a_source_without_registry_entry_is_gone(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """E.g. a YAML template sensor that was deleted."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    hass.states.async_remove("sensor.room")
    await _tick(hass, freezer)
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing")
    # A missing source does not also count as one without data.
    await _tick(hass, freezer, timedelta(minutes=40))
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data") is None

    hass.config_entries.async_update_entry(config_entry, options={})
    await hass.async_block_till_done()
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing") is None


async def test_no_issue_while_home_assistant_starts(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """A source may just not be loaded yet."""
    await _setup_with_feeds(hass, config_entry)
    hass.set_state(CoreState.starting)
    await _tick(hass, freezer, timedelta(minutes=40))
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing") is None
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data") is None
    hass.set_state(CoreState.running)


async def test_issue_when_the_source_sends_no_data(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """Only after 30 minutes without a usable value; it clears with the next one."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    hass.states.async_set("sensor.room", "70", CELSIUS)  # out of range
    await _tick(hass, freezer, timedelta(minutes=20))
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data") is None

    await _tick(hass, freezer, timedelta(minutes=15))
    issue = _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data")
    assert "outside" in issue.translation_placeholders["reason"]
    # Humidity has no source state at all but a registry-less id: missing.
    assert _issue(hass, config_entry, "humidity_bus", "bus_source_missing")

    hass.states.async_set("sensor.room", "22.0", CELSIUS)
    await hass.async_block_till_done()
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data") is None


async def test_issue_names_an_unavailable_source(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    hass.states.async_set("sensor.room", "unavailable", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    await _tick(hass, freezer, timedelta(minutes=35))
    issue = _issue(hass, config_entry, "room_temp_bus", "bus_source_no_data")
    assert issue.translation_placeholders["reason"] == "state 'unavailable'"


async def test_source_issues_removed_on_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    await _setup_with_feeds(hass, config_entry)
    await _tick(hass, freezer)
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing")
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert _issue(hass, config_entry, "room_temp_bus", "bus_source_missing") is None


# --- Retries and the value the unit no longer gets -------------------------


async def test_feed_retries_every_minute_until_a_write_succeeds(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """The unit keeps a bus value 10 minutes: a missed refresh is retried soon."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    device.writes.clear()

    device.write_exception = 4
    await _tick(hass, freezer)  # 8 min: refresh fails
    await _tick(hass, freezer, timedelta(seconds=61))  # 9 min: fails again
    assert _issue(hass, config_entry, "room_temp_bus", "bus_value_not_delivered") is None
    await _tick(hass, freezer, timedelta(seconds=61))  # 10 min: the value expired
    issue = _issue(hass, config_entry, "room_temp_bus", "bus_value_not_delivered")
    assert issue.translation_placeholders["register"] == "707"
    assert "exception code 4" in issue.translation_placeholders["error"]
    assert not device.writes

    device.write_exception = None
    await _tick(hass, freezer, timedelta(seconds=61))
    assert device.writes == [(707, [215])]
    assert _issue(hass, config_entry, "room_temp_bus", "bus_value_not_delivered") is None

    # Back to the regular refresh: no retry is left over.
    await _tick(hass, freezer, timedelta(minutes=2))
    assert device.writes == [(707, [215])]


async def test_retry_and_issue_end_with_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    device.write_exception = 4
    for delta in (REWRITE, timedelta(seconds=61), timedelta(seconds=61)):
        await _tick(hass, freezer, delta)
    assert _issue(hass, config_entry, "room_temp_bus", "bus_value_not_delivered")

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert _issue(hass, config_entry, "room_temp_bus", "bus_value_not_delivered") is None
    device.write_exception = None
    writes = len(device.writes)
    await _tick(hass, freezer, timedelta(minutes=2))
    assert len(device.writes) == writes


# --- Another device at the address ---------------------------------------


async def test_nothing_is_written_while_the_device_is_no_maico(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """E.g. the IP address went to another device while running."""
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await _setup_with_feeds(hass, config_entry)
    coordinator = config_entry.runtime_data.coordinator
    device.writes.clear()

    device.registers[650] = 300
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"{config_entry.entry_id}_unsupported_device"
    )
    assert issue.translation_placeholders["details"] == (
        "register 650 reads 300, expected 0 to 4"
    )

    hass.states.async_set("sensor.room", "22.0", CELSIUS)
    await _tick(hass, freezer)
    assert not device.writes  # neither the change nor the refresh

    device.registers[650] = 3  # the unit is back
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert ir.async_get(hass).async_get_issue(
        DOMAIN, f"{config_entry.entry_id}_unsupported_device"
    ) is None
    await _tick(hass, freezer, timedelta(seconds=61))  # the pending retry
    assert device.writes == [(707, [220])]
