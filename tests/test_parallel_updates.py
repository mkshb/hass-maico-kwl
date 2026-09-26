"""PARALLEL_UPDATES per platform (quality scale rule parallel-updates)."""

from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    ("platform", "expected"),
    [
        ("sensor", 0),
        ("binary_sensor", 0),
        ("number", 1),
        ("select", 1),
        ("switch", 1),
        ("button", 1),
        ("fan", 1),
    ],
)
def test_parallel_updates(platform: str, expected: int) -> None:
    """Read-only platforms are unlimited, actions go to the unit one at a time."""
    module = importlib.import_module(f"custom_components.maico_kwl.{platform}")
    assert module.PARALLEL_UPDATES == expected
