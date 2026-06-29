"""Helper functions for nested charger data."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def nested_get(data: Any, path: Iterable[Any], default: Any = None) -> Any:
    """Safely get a nested value from dict/list structures."""
    current = data
    try:
        for key in path:
            current = current[key]
    except (KeyError, IndexError, TypeError):
        return default
    return current
