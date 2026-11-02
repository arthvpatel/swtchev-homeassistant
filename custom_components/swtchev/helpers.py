"""Helper functions for nested charger data."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


METER_PATH = ("data", "csInfo", "evses", 0, "connectors", 0, "Meter")


def meter_wh(data: Any) -> float | None:
    """Return the charger meter in Wh (it reports 0.1 Wh), or None if unusable.

    A zero reading is a firmware glitch, not a real reset.
    """
    try:
        value = float(nested_get(data, METER_PATH))
    except (TypeError, ValueError):
        return None
    return value / 10 if value > 0 else None


def energy_offset_wh(meter: float | None, app_kwh: float) -> float | None:
    """Offset (Wh) that makes the meter read the same as the app."""
    if meter is None:
        return None
    return app_kwh * 1000 - meter


def nested_get(data: Any, path: Iterable[Any], default: Any = None) -> Any:
    """Safely get a nested value from dict/list structures."""
    current = data
    try:
        for key in path:
            current = current[key]
    except (KeyError, IndexError, TypeError):
        return default
    return current
