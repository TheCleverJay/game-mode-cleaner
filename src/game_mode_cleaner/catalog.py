"""Load interrupter catalog + never-kill list (shared JSON)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent / "data" / "catalog.json"


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    with _DATA.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or "never_kill" not in data or "groups" not in data:
        raise ValueError("catalog.json missing required keys")
    return data


def never_kill_names() -> set[str]:
    cat = load_catalog()
    return {_norm(n) for n in cat["never_kill"]}


def preset_group_names(preset: str) -> list[str]:
    cat = load_catalog()
    presets = cat.get("presets") or {}
    if preset not in presets:
        known = ", ".join(sorted(presets))
        raise ValueError(f"unknown preset {preset!r}; choose one of: {known}")
    return list(presets[preset].get("groups") or [])


def interrupter_names_for_groups(groups: list[str]) -> set[str]:
    cat = load_catalog()
    all_groups = cat.get("groups") or {}
    out: set[str] = set()
    for g in groups:
        if g not in all_groups:
            raise ValueError(f"unknown interrupter group {g!r}")
        for name in all_groups[g].get("names") or []:
            out.add(_norm(name))
    return out


def restore_hints() -> dict[str, str]:
    cat = load_catalog()
    raw = cat.get("restore_hints") or {}
    return {_norm(k): str(v) for k, v in raw.items()}


def list_presets() -> dict[str, str]:
    cat = load_catalog()
    return {
        name: str(meta.get("description") or "")
        for name, meta in (cat.get("presets") or {}).items()
    }


def _norm(name: str) -> str:
    return name.strip().lower()
