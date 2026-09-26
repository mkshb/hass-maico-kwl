"""Checks that every form field is named and described in all languages."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant

from custom_components.maico_kwl.const import DOMAIN
from custom_components.maico_kwl.register_defs import (
    ACCESSORIES,
    FAULT_BITS,
    NOTICE_BITS,
)

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


def _placeholders(message: str) -> set[str]:
    return set(re.findall(r"{(\w+)}", message))


def test_exception_messages_complete() -> None:
    """Every exception has a message with the same placeholders in all files."""
    reference = _load("strings.json")["exceptions"]
    for name in FILES:
        exceptions = _load(name)["exceptions"]
        assert exceptions.keys() == reference.keys(), name
        for key, entry in exceptions.items():
            # HA strips a trailing period when it shows the message.
            assert not entry["message"].endswith("."), (name, key)
            assert _placeholders(entry["message"]) == _placeholders(
                reference[key]["message"]
            ), (name, key)


def test_code_only_uses_known_exception_keys() -> None:
    """Every translation_key raised in the code has a message."""
    known = set(_load("strings.json")["exceptions"])
    used: set[str] = set()
    for path in COMPONENT.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for block in re.findall(r"raise \w+\((.*?)\)", text, re.S):
            used |= set(re.findall(r'translation_key="(\w+)"', block))
    assert used
    assert used <= known


@pytest.mark.parametrize("name", FILES)
def test_every_accessory_is_named(name: str) -> None:
    options = _load(name)["selector"]["accessory"]["options"]
    assert options.keys() == {acc.key for acc in ACCESSORIES}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize(
    ("key", "bits"), [("fault_code", FAULT_BITS), ("notice_code", NOTICE_BITS)]
)
def test_every_code_bit_is_named(name: str, key: str, bits: dict[int, str]) -> None:
    """Each fault and notice bit reads as text in the "active" attribute."""
    active = _load(name)["entity"]["sensor"][key]["state_attributes"]["active"]
    assert active["state"].keys() == set(bits.values())
