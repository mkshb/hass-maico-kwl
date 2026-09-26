"""Checks that every form field is named and described in all languages."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant

from custom_components.maico_kwl.const import DOMAIN

from .conftest import FakeDevice
from .helpers import setup_entry

COMPONENT = Path(__file__).parent.parent / "custom_components" / "maico_kwl"
FILES = ["strings.json", "translations/en.json", "translations/de.json"]


def _load(name: str) -> dict:
    return json.loads((COMPONENT / name).read_text(encoding="utf-8"))


def _steps(data: dict) -> dict[str, dict]:
    steps = {f"config.{k}": v for k, v in data["config"]["step"].items()}
    steps |= {f"options.{k}": v for k, v in data["options"]["step"].items()}
    return steps


@pytest.mark.parametrize("name", FILES)
def test_every_field_has_a_description(name: str) -> None:
    for step_id, step in _steps(_load(name)).items():
        assert set(step["data_description"]) == set(step["data"]), step_id


def test_languages_have_the_same_keys() -> None:
    reference = _steps(_load("strings.json"))
    for name in FILES[1:]:
        steps = _steps(_load(name))
        assert steps.keys() == reference.keys(), name
        for step_id, step in steps.items():
            for part in ("data", "data_description"):
                assert step[part].keys() == reference[step_id][part].keys(), (
                    name,
                    step_id,
                    part,
                )


async def test_form_fields_are_translated(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Every field the flows actually show has a label and a description."""
    steps = _steps(_load("strings.json"))
    await setup_entry(hass, config_entry)

    forms = {
        "config.user": await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        ),
        "config.reconfigure": await config_entry.start_reconfigure_flow(hass),
        "options.init": await hass.config_entries.options.async_init(
            config_entry.entry_id
        ),
    }
    for step_id, result in forms.items():
        fields = {str(key) for key in result["data_schema"].schema}
        assert fields == set(steps[step_id]["data"]), step_id
        assert fields == set(steps[step_id]["data_description"]), step_id
