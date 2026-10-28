"""Game state: numbers, flags, queues. No presentation logic lives here."""
from __future__ import annotations

import random

from .content.modes import MODES

STATS = ("ECONOMY", "MILITARY", "ORDER", "FAITH", "PRESTIGE")

STAT_LABEL = {
    "ECONOMY":  "Economy   (Gosplan)",
    "MILITARY": "Military  (Red Army)",
    "ORDER":    "Order     (Control)",
    "FAITH":    "People    (Belief)",
    "PRESTIGE": "Prestige  (World)",
}

FACTIONS = ("old_guard", "reformers", "military")

FACTION_LABEL = {
    "old_guard": "Old Guard",
    "reformers": "Reformers",
    "military":  "Army",
}

ERAS = {"EARLY": (1964, 1975), "MIDDLE": (1976, 1984), "LATE": (1985, 1991),
        "NEW": (1992, 2001)}        # NEW: the v4 extended era, if you earn it


def clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


class Kremlin:
    """Everything mutable in the game lives here. Engine reads, ops writes."""

    def __init__(self, seed: int | None = None, mode: str | None = "normal"):
        if mode not in MODES:
            mode = "normal"
        self.mode = mode
        self.year = 1964
        self.end_year = 1991
        self.name = "Comrade Secretary"
        self.stats = {"ECONOMY": 55, "MILITARY": 70, "ORDER": 75,
                      "FAITH": 52, "PRESTIGE": 62}
        self.flags: set[str] = set()
        self.pending: list[tuple[int, str]] = []   # (due_year, event_id)
        self.used_events: set[str] = set()
        self.used_directives: set[str] = set()
        self.used_focus: set[str] = set()
        self.lifelines = MODES[mode]["lifelines"]
        self.death_reason: str | None = None
        self.putschist = False
        self.ledger: list[tuple[int, str]] = []    # (year, what happened)
        self.shown_press: set[str] = set()         # conditional headlines used
        # ── v4 systems ─────────────────────────────────────────────
        self.hard_currency = 40                    # gold & valas reserve 0-100
        self.court: dict[str, int] = {f: 50 for f in FACTIONS}
        self.deposed = False                       # removed by palace intrigue
        self.rng = random.Random(seed)

    @property
    def era(self) -> str:
        for name, (lo, hi) in ERAS.items():
            if lo <= self.year <= hi:
                return name
        return "LATE"

    def dead_stat(self) -> str | None:
        for s in STATS:
            if self.stats[s] <= 0:
                return s
        return None
