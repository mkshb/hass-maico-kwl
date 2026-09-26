"""Tests for shipping the dashboard card with the integration."""

from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.maico_kwl import CARD_LOADER, FRONTEND_DIR, FRONTEND_URL
from custom_components.maico_kwl.const import DOMAIN

VERSION = json.loads((FRONTEND_DIR.parent / "manifest.json").read_text())["version"]


async def test_card_is_served_and_loaded(hass: HomeAssistant) -> None:
    """With the frontend loaded, the card folder is served and the loader added."""
    hass.config.components.add("frontend")
    hass.http = MagicMock(async_register_static_paths=AsyncMock())
    with patch("custom_components.maico_kwl.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})

    (paths,), _ = hass.http.async_register_static_paths.call_args
    assert [(p.url_path, p.path) for p in paths] == [
        (FRONTEND_URL, str(FRONTEND_DIR))
    ]
    add_js.assert_called_once_with(
        hass, f"/maico_kwl/frontend/maico-kwl-card.js?v={VERSION}"
    )


async def test_card_is_skipped_without_frontend(hass: HomeAssistant) -> None:
    """Without the frontend (e.g. a headless install) nothing is registered."""
    with patch("custom_components.maico_kwl.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})
    add_js.assert_not_called()


def test_built_card_is_complete() -> None:
    """The committed build has the loader and the chunk it imports."""
    loader = (FRONTEND_DIR / CARD_LOADER).read_text(encoding="utf-8")
    chunks = re.findall(r'import\("\./([\w-]+\.js)"\)', loader)
    assert chunks, "the loader imports no card chunk"
    for chunk in chunks:
        assert (FRONTEND_DIR / chunk).is_file(), f"missing chunk {chunk}"
    assert {p.name for p in Path(FRONTEND_DIR).iterdir()} == {CARD_LOADER, *chunks}
