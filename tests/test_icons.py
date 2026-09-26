"""Checks on icons.json (quality scale rule icon-translations)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant.helpers.icon import async_get_icons

from custom_components.maico_kwl.register_defs import REGISTERS

from .helpers import setup_entry

COMPONENT = Path(__file__).parent.parent / "custom_components" / "maico_kwl"
ICONS = json.loads((COMPONENT / "icons.json").read_text(encoding="utf-8"))["entity"]
REGS = {(reg.platform, reg.key): reg for reg in REGISTERS}

ICON_ENTRIES = [
    (platform, key, entry)
    for platform, entries in ICONS.items()
    for key, entry in entries.items()
]


@pytest.mark.parametrize(("platform", "key", "entry"), ICON_ENTRIES)
def test_icon_belongs_to_an_entity(platform: str, key: str, entry: dict) -> None:
    """Every icon entry matches a register entity and uses mdi icons."""
    assert (platform, key) in REGS
    assert entry["default"].startswith("mdi:")
    assert all(icon.startswith("mdi:") for icon in entry.get("state", {}).values())


@pytest.mark.parametrize(("platform", "key", "entry"), ICON_ENTRIES)
def test_state_icons_match_states(platform: str, key: str, entry: dict) -> None:
    """State icons only use states the entity can actually have."""
    states = set(entry.get("state", {}))
    reg = REGS[(platform, key)]
    if reg.options is not None:
        assert states <= set(reg.options.values())
    else:
        assert states <= {"on", "off"}


def test_enum_controls_have_state_icons() -> None:
    """Operating mode and ventilation level show their state in the icon."""
    for platform, key in [
        ("select", "operating_mode"),
        ("select", "ventilation_level"),
        ("sensor", "current_vent_level"),
    ]:
        assert set(ICONS[platform][key]["state"]) == set(
            REGS[(platform, key)].options.values()
        )


async def test_home_assistant_loads_icons(hass, device, config_entry) -> None:
    """HA reads icons.json for the integration (as the frontend will)."""
    await setup_entry(hass, config_entry)
    icons = await async_get_icons(hass, "entity", ["maico_kwl"])
    mode = icons["maico_kwl"]["select"]["operating_mode"]
    assert mode["state"]["off"] == "mdi:fan-off"
