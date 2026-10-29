"""Save / load: the whole Kremlin state serialised to one JSON file.

Saves happen only at YEAR BOUNDARIES (via the command bar between years),
which keeps the format trivial and halfway-applied turns impossible.
The RNG state is serialised too, so a loaded run continues identically.

v5 adds the chosen timeline and the fatigue counters; v4 files are refused
politely (the state now carries scenarios and plan fatigue).
"""
from __future__ import annotations

import json
import os

from .state import Kremlin, STATS, FACTIONS
from .content.modes import normalize

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "kreml_save.json")
SAVE_VERSION = 5


def _rng_pack(rng) -> dict:
    """random.Random.getstate() -> JSON-friendly nested lists (layout-agnostic)."""
    return _to_jsonable(rng.getstate())


def _to_jsonable(x):
    if isinstance(x, (tuple, list)):
        return [_to_jsonable(i) for i in x]
    return x


def _from_jsonable(x):
    if isinstance(x, list):
        return tuple(_from_jsonable(i) for i in x)
    return x


def _rng_unpack(data) -> object:
    import random
    rng = random.Random()
    rng.setstate(_from_jsonable(data))
    return rng


def save_game(g: Kremlin, path: str | None = None) -> bool:
    path = path or SAVE_FILE
    payload = {
        "version": SAVE_VERSION,
        "mode": g.mode,
        "timeline": g.timeline,
        "year": g.year,
        "end_year": g.end_year,
        "name": g.name,
        "stats": dict(g.stats),
        "flags": sorted(g.flags),
        "pending": [list(p) for p in g.pending],
        "used_events": sorted(g.used_events),
        "used_directives": sorted(g.used_directives),
        "used_focus": sorted(g.used_focus),
        "lifelines": g.lifelines,
        "death_reason": g.death_reason,
        "putschist": g.putschist,
        "ledger": _to_jsonable(g.ledger),
        "shown_press": sorted(g.shown_press),
        "hard_currency": g.hard_currency,
        "court": dict(g.court),
        "deposed": g.deposed,
        "directive_uses": dict(g.directive_uses),
        "focus_uses": dict(g.focus_uses),
        "path": g.path,
        "history": g.history,
        "rng": _rng_pack(g.rng),
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1)
        return True
    except OSError:
        return False


def load_game(path: str | None = None) -> Kremlin | None:
    """Returns a rebuilt Kremlin, or None if the save is missing/corrupt."""
    path = path or SAVE_FILE
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != SAVE_VERSION:
            return None
        g = Kremlin.__new__(Kremlin)
        g.mode = normalize(data["mode"])
        g.timeline = data.get("timeline", "rails")
        g.year = int(data["year"])
        g.end_year = int(data["end_year"])
        g.name = data["name"]
        g.stats = {s: int(data["stats"].get(s, 50)) for s in STATS}
        g.flags = set(data["flags"])
        g.pending = [(int(a), str(b)) for a, b in data["pending"]]
        g.used_events = set(data["used_events"])
        g.used_directives = set(data["used_directives"])
        g.used_focus = set(data["used_focus"])
        g.lifelines = int(data["lifelines"])
        g.death_reason = data["death_reason"]
        g.putschist = bool(data["putschist"])
        g.ledger = [(int(a), str(b)) for a, b in data["ledger"]]
        g.shown_press = set(data["shown_press"])
        g.hard_currency = int(data.get("hard_currency", 50))
        g.court = {f: int(data.get("court", {}).get(f, 50)) for f in FACTIONS}
        g.deposed = bool(data.get("deposed", False))
        g.directive_uses = {str(k): int(v) for k, v in
                            (data.get("directive_uses") or {}).items()}
        g.focus_uses = {str(k): int(v) for k, v in
                        (data.get("focus_uses") or {}).items()}
        g.path = data.get("path")
        g.history = list(data.get("history") or [])
        g.rng = _rng_unpack(data["rng"])
        return g
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def has_save(path: str | None = None) -> bool:
    return os.path.exists(path or SAVE_FILE)
