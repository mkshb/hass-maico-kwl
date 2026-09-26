"""Tests for the repair issues."""

from __future__ import annotations

from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from custom_components.maico_kwl.const import DOMAIN

from .conftest import FakeDevice
from .helpers import setup_entry


async def _refresh(hass: HomeAssistant, entry) -> None:
    await entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()


def _issue(hass: HomeAssistant, entry, key: str) -> ir.IssueEntry | None:
    return ir.async_get(hass).async_get_issue(DOMAIN, f"{entry.entry_id}_{key}")


async def test_fault_issue(hass: HomeAssistant, device: FakeDevice, config_entry, freezer) -> None:
    freezer.move_to(datetime(2026, 9, 26, 10, 30, 15, tzinfo=dt_util.get_default_time_zone()))
    await setup_entry(hass, config_entry)
    assert _issue(hass, config_entry, "fault_active") is None

    device.registers[402] = 0b11  # supply and exhaust fan
    await _refresh(hass, config_entry)
    issue = _issue(hass, config_entry, "fault_active")
    assert issue.severity is ir.IssueSeverity.ERROR
    assert issue.translation_placeholders["faults"] == "supply_fan, exhaust_fan"
    assert issue.translation_placeholders["name"] == config_entry.title

    device.registers[402] = 0
    await _refresh(hass, config_entry)
    assert _issue(hass, config_entry, "fault_active") is None


async def test_filter_issues(hass: HomeAssistant, device: FakeDevice, config_entry, freezer) -> None:
    freezer.move_to(datetime(2026, 9, 26, 10, 30, 15, tzinfo=dt_util.get_default_time_zone()))
    await setup_entry(hass, config_entry)
    device.registers[656] = 0  # outdoor filter
    await _refresh(hass, config_entry)
    assert _issue(hass, config_entry, "filter_due_outdoor").severity is ir.IssueSeverity.WARNING
    assert _issue(hass, config_entry, "filter_due_room") is None

    # A register missing from a poll keeps the issue as it is.
    device.absent.add(656)
    await _refresh(hass, config_entry)
    assert _issue(hass, config_entry, "filter_due_outdoor") is not None

    device.absent.discard(656)
    device.registers[656] = 180  # filter replaced and reset
    await _refresh(hass, config_entry)
    assert _issue(hass, config_entry, "filter_due_outdoor") is None


async def test_clock_issue(hass: HomeAssistant, device: FakeDevice, config_entry, freezer) -> None:
    """The unit clock reads 10:30:15."""
    freezer.move_to(datetime(2026, 9, 26, 10, 29, 0, tzinfo=dt_util.get_default_time_zone()))
    await setup_entry(hass, config_entry)
    assert _issue(hass, config_entry, "clock_drift") is None  # 75 s ahead

    freezer.move_to(datetime(2026, 9, 26, 10, 20, 0, tzinfo=dt_util.get_default_time_zone()))
    await _refresh(hass, config_entry)
    issue = _issue(hass, config_entry, "clock_drift")
    assert issue.translation_placeholders["minutes"] == "10"


async def test_issues_removed_on_unload(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    device.registers[402] = 1
    await setup_entry(hass, config_entry)
    assert _issue(hass, config_entry, "fault_active") is not None
    await hass.config_entries.async_unload(config_entry.entry_id)
    assert _issue(hass, config_entry, "fault_active") is None
