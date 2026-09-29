"""Tests for the bus input activity in the device's logbook."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.maico_kwl.const import (
    CONF_HUMIDITY_SOURCE_ENTITY,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    DOMAIN,
    EVENT_BUS_INPUT,
)
from custom_components.maico_kwl.logbook import (
    async_describe_events,
    describe_bus_event,
)

from .conftest import FakeDevice
from .helpers import CELSIUS, PERCENT, setup_entry

REWRITE = timedelta(minutes=8, seconds=1)


async def _setup(hass: HomeAssistant, entry) -> list[Event]:
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    hass.states.async_set("sensor.humidity", "49", PERCENT)
    events = async_capture_events(hass, EVENT_BUS_INPUT)
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry,
        options={
            CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room",
            CONF_HUMIDITY_SOURCE_ENTITY: "sensor.humidity",
        },
    )
    await setup_entry(hass, entry)
    return events


def _kinds(events: list[Event], key: str) -> list[tuple]:
    return [
        (e.data["kind"], e.data.get("value"))
        for e in events
        if e.data["input"] == key
    ]


async def _tick(hass: HomeAssistant, freezer, delta: timedelta) -> None:
    freezer.tick(delta)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_first_value_is_logged_with_the_device(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    events = await _setup(hass, config_entry)
    (device_entry,) = dr.async_entries_for_config_entry(
        dr.async_get(hass), config_entry.entry_id
    )
    device_id = device_entry.id
    humidity = [e for e in events if e.data["input"] == "humidity_bus"]
    assert len(humidity) == 1
    assert humidity[0].data == {
        "device_id": device_id,
        "entry_id": config_entry.entry_id,
        "input": "humidity_bus",
        "kind": "sent",
        "value": 49.0,
        "unit": "%",
        "source": "sensor.humidity",
    }


async def test_refresh_is_not_logged_and_changes_are_throttled(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    """At most one entry per input every 8 minutes, with the latest value."""
    events = await _setup(hass, config_entry)
    events.clear()

    await _tick(hass, freezer, REWRITE)  # refresh, unchanged
    assert events == []

    for value in ("50", "51", "52"):
        hass.states.async_set("sensor.humidity", value, PERCENT)
        await hass.async_block_till_done()
    # The first change is logged at once, 8 minutes after the first entry.
    assert _kinds(events, "humidity_bus") == [("sent", 50.0)]
    await _tick(hass, freezer, timedelta(minutes=4))
    assert _kinds(events, "humidity_bus") == [("sent", 50.0)]
    await _tick(hass, freezer, timedelta(minutes=4, seconds=1))
    assert _kinds(events, "humidity_bus") == [("sent", 50.0), ("sent", 52.0)]


async def test_change_back_within_the_throttle_is_not_logged(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    events = await _setup(hass, config_entry)
    events.clear()
    hass.states.async_set("sensor.humidity", "50", PERCENT)
    await hass.async_block_till_done()
    hass.states.async_set("sensor.humidity", "49", PERCENT)
    await hass.async_block_till_done()
    await _tick(hass, freezer, REWRITE)
    assert events == []


async def test_skipped_source_is_logged_once_with_the_reason(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    events = await _setup(hass, config_entry)
    events.clear()
    for value in ("22", "23"):
        hass.states.async_set("sensor.room", value, {"unit_of_measurement": "bar"})
        await hass.async_block_till_done()
    skipped = [e.data for e in events if e.data["kind"] == "skipped"]
    assert len(skipped) == 1
    assert skipped[0]["source"] == "sensor.room"
    assert skipped[0]["reason"] == "unit 'bar' is not °C"

    # Usable again: the next value sent is logged, even if it equals the last
    # one logged (here with the next refresh).
    hass.states.async_set("sensor.room", "21.5", CELSIUS)
    await hass.async_block_till_done()
    await _tick(hass, freezer, REWRITE)
    assert _kinds(events, "room_temp_bus")[-1] == ("sent", 21.5)


async def test_outage_is_logged_at_start_expiry_and_end(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    events = await _setup(hass, config_entry)
    events.clear()

    device.write_exception = 4
    await _tick(hass, freezer, REWRITE)  # 8 min: refresh fails
    await _tick(hass, freezer, timedelta(seconds=61))  # 9 min: retry fails
    await _tick(hass, freezer, timedelta(seconds=61))  # 10 min: value expired
    await _tick(hass, freezer, timedelta(seconds=61))  # still failing
    kinds = _kinds(events, "room_temp_bus")
    assert kinds == [("failed", None), ("expired", None)]
    failed = next(e for e in events if e.data["kind"] == "failed")
    assert "code=4" in failed.data["error"]

    device.write_exception = None
    await _tick(hass, freezer, timedelta(seconds=61))
    assert _kinds(events, "room_temp_bus")[2:] == [("recovered", None)]


async def test_pending_entry_ends_with_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry, freezer
) -> None:
    events = await _setup(hass, config_entry)
    hass.states.async_set("sensor.humidity", "50", PERCENT)
    await hass.async_block_till_done()
    hass.states.async_set("sensor.humidity", "51", PERCENT)
    await hass.async_block_till_done()
    events.clear()
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    await _tick(hass, freezer, REWRITE)
    assert events == []


def test_messages_in_german_and_english() -> None:
    data = {
        "input": "humidity_bus",
        "kind": "sent",
        "value": 49.5,
        "unit": "%",
        "source": "sensor.bad",
    }
    assert describe_bus_event("de", "KWL", data) == {
        "name": "KWL",
        "message": "hat Feuchte 49,5 % an den Bus gesendet (Quelle sensor.bad)",
    }
    assert describe_bus_event("en-GB", "KWL", data)["message"] == (
        "sent humidity 49.5 % to the bus (source sensor.bad)"
    )
    expired = {"input": "room_temp_bus", "kind": "expired"}
    assert describe_bus_event("de", "KWL", expired)["message"] == (
        "hat seit 10 Minuten keinen gültigen Wert für Raumtemperatur vom Bus, "
        "das Gerät nutzt seinen eigenen Sensor"
    )
    failed = {"input": "air_quality_bus", "kind": "failed", "error": "timeout"}
    assert describe_bus_event("en", "KWL", failed)["message"] == (
        "could not send air quality to the bus: timeout"
    )


async def test_logbook_names_the_device(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    events = await _setup(hass, config_entry)
    described = {}
    async_describe_events(
        hass, lambda domain, event, fn: described.update({(domain, event): fn})
    )
    describe = described[(DOMAIN, EVENT_BUS_INPUT)]
    device_entry = dr.async_get(hass).async_get(events[0].data["device_id"])
    dr.async_get(hass).async_update_device(device_entry.id, name_by_user="Keller")
    assert describe(events[0])["name"] == "Keller"
    assert describe(Event(EVENT_BUS_INPUT, {"kind": "recovered"}))["name"] == "Maico KWL"
