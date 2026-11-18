"""Core constants and types for the Heritage Atlas data contract."""

from __future__ import annotations

CATEGORIES: tuple[str, ...] = (
    "ancient",
    "sacred",
    "castles",
    "towns",
    "palaces",
    "landscapes",
    "modern",
    "natural",
)

SPREAD_LEVELS: tuple[str, ...] = ("compact", "moderate", "spread")
