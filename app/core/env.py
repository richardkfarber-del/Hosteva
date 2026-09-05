"""Environment helpers for Hosteva."""
from __future__ import annotations

import os


def get_environment() -> str:
    """Return ENVIRONMENT (default development), trimmed and lowercased for comparisons."""
    return (os.getenv("ENVIRONMENT") or "development").strip().lower()


def is_production() -> bool:
    return get_environment() == "production"
