"""Tests for shipping the dashboard card with the integration."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.maico_kwl import CARD_LOADER, FRONTEND_DIR, FRONTEND_URL
from custom_components.maico_kwl.const import DOMAIN

LOADER_HASH = hashlib.sha256((FRONTEND_DIR / CARD_LOADER).read_bytes()).hexdigest()[:12]


async def test_card_is_served_and_loaded(hass: HomeAssistant) -> None:
    """With the frontend loaded, the card is served and its loader added."""
    hass.config.components.add("frontend")
    hass.http = MagicMock(async_register_static_paths=AsyncMock())
    with patch("custom_components.maico_kwl.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})

    (paths,), _ = hass.http.async_register_static_paths.call_args
    # The loader first and uncached, then the folder with its hashed chunks.
    assert [(p.url_path, p.path, p.cache_headers) for p in paths] == [
        (f"{FRONTEND_URL}/{CARD_LOADER}", str(FRONTEND_DIR / CARD_LOADER), False),
        (FRONTEND_URL, str(FRONTEND_DIR), True),
    ]
    add_js.assert_called_once_with(
        hass, f"/maico_kwl/frontend/maico-kwl-card.js?v={LOADER_HASH}"
    )


def test_static_path_config_from_the_http_package() -> None:
    """http.server only exists from HA 2026.8; hacs.json allows older versions."""
    source = (FRONTEND_DIR.parent / "__init__.py").read_text(encoding="utf-8")
    assert "from homeassistant.components.http import StaticPathConfig" in source
    assert "homeassistant.components.http.server" not in source


async def test_card_is_skipped_without_frontend(hass: HomeAssistant) -> None:
    """Without the frontend (e.g. a headless install) nothing is registered."""
    with patch("custom_components.maico_kwl.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})
    add_js.assert_not_called()


def test_built_card_is_complete() -> None:
    """The committed build has the loader and every chunk it reaches, nothing else."""
    reached: set[str] = set()
    pending = [CARD_LOADER]
    while pending:
        name = pending.pop()
        reached.add(name)
        source = (FRONTEND_DIR / name).read_text(encoding="utf-8")
        for chunk in re.findall(r'(?:import\(|from)"\./([\w-]+\.js)"', source):
            assert (FRONTEND_DIR / chunk).is_file(), f"{name} imports missing {chunk}"
            if chunk not in reached:
                pending.append(chunk)
    assert len(reached) > 1, "the loader imports no card chunk"
    assert {p.name for p in FRONTEND_DIR.iterdir()} == reached


def test_card_uses_existing_entity_keys() -> None:
    """Every translation_key the card looks up is one the integration creates."""
    keys_ts = (
        Path(__file__).parent.parent / "frontend-src" / "src" / "keys.ts"
    ).read_text(encoding="utf-8")
    card_keys = set(re.findall(r'"([a-z0-9_]+)"', keys_ts))
    strings = json.loads((FRONTEND_DIR.parent / "strings.json").read_text())
    entity_keys = {key for platform in strings["entity"].values() for key in platform}
    assert card_keys
    assert card_keys - entity_keys == set()
