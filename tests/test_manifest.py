"""Checks on manifest.json that hassfest and HACS rely on."""

from __future__ import annotations

import json
import re
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


def test_changelog_describes_this_version() -> None:
    """The newest section of CHANGELOG.md is the version in the manifest."""
    changelog = (Path(__file__).parent.parent / "CHANGELOG.md").read_text(encoding="utf-8")
    newest = re.search(r"^## (\d+\.\d+\.\d+) \(", changelog, re.M)
    assert newest, "no version section in CHANGELOG.md"
    assert newest.group(1) == MANIFEST["version"]


def test_hacs_downloads_the_zip_the_release_workflow_builds() -> None:
    """hacs.json names the zip that .github/workflows/release.yml attaches."""
    root = Path(__file__).parent.parent
    hacs = json.loads((root / "hacs.json").read_text(encoding="utf-8"))
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert hacs["zip_release"] is True
    assert f'"${{GITHUB_WORKSPACE}}/{hacs['filename']}"' in workflow
    assert f"gh release upload \"${{TAG}}\" {hacs['filename']}" in workflow
