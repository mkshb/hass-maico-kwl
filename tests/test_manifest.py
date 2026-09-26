"""Checks on manifest.json that hassfest and HACS rely on."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = json.loads(
    (Path(__file__).parent.parent / "custom_components" / "maico_kwl" / "manifest.json")
    .read_text(encoding="utf-8")
)


def test_manifest_fields() -> None:
    assert MANIFEST["domain"] == "maico_kwl"
    assert MANIFEST["integration_type"] == "device"
    assert MANIFEST["iot_class"] == "local_polling"
    assert MANIFEST["config_flow"] is True
    assert MANIFEST["loggers"] == ["pymodbus"]
    assert "version" in MANIFEST  # required for custom integrations


def test_manifest_key_order() -> None:
    """hassfest wants domain and name first, the rest sorted."""
    keys = list(MANIFEST)
    assert keys[:2] == ["domain", "name"]
    assert keys[2:] == sorted(keys[2:])
