"""Difficulty modes: pure data.

v5 ships five modes. Four are drift/reserve dials; the fifth is a RAIL mode:

  easy        SWEEPING REFORMS       gentle drift, 5 reserves
  medium      BALANCED              the historical grind, 3 reserves
  hard        OLD GUARD IRON GRASP  the system fights back, 2 reserves
  extreme     THE SYSTEM ITSELF     everything fails at once, 1 reserve
  historical  HISTORICAL RAILS      real decline, alt content locked, and a
                                    score penalty for every divergence

Each mode defines the yearly drift table per era, how many crisis lifelines
the Politburo starts with, whether alternate-history content is locked
(`rail`), and how heavily leaving the rails costs score (`divergence`).
"""
from __future__ import annotations

MODES: dict[str, dict] = {
    "easy": {
        "label": "SWEEPING REFORMS",
        "tag": "REFORM",
        "desc": "Gentle drift (Economy −1, −2 after 1985), 5 crisis reserves. "
                "For architecting the future, not surviving it.",
        "lifelines": 5,
        "rail": False,
        "divergence": 0,
        "drift": {
            "EARLY":  {"ECONOMY": -1, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -1, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -1, "MILITARY": 0, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
        },
    },
    "medium": {
        "label": "BALANCED",
        "tag": "BALANCED",
        "desc": "The historical grind: drift −2/−3 late, 3 crisis reserves. "
                "The Union fell once; the margins are thin.",
        "lifelines": 3,
        "rail": False,
        "divergence": 0,
        "drift": {
            "EARLY":  {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -4, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -3, "MILITARY": 0, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
        },
    },
    "hard": {
        "label": "OLD GUARD IRON GRASP",
        "tag": "IRON",
        "desc": "The system fights back: Economy −3 (−4 after 1985), Order −2/yr, "
                "Faith −2 after 1985, only 2 crisis reserves.",
        "lifelines": 2,
        "rail": False,
        "divergence": 0,
        "drift": {
            "EARLY":  {"ECONOMY": -3, "MILITARY": -1, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -3, "MILITARY": -1, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -4, "MILITARY": -1, "ORDER": -2, "FAITH": -2, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -3, "MILITARY": 0, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
        },
    },
    "extreme": {
        "label": "THE SYSTEM ITSELF",
        "tag": "EXTREME",
        "desc": "Everything fails at once: drift −8/−10, late Economy −5, one "
                "crisis reserve. The Union is a rumour you must keep alive.",
        "lifelines": 1,
        "rail": False,
        "divergence": 0,
        "drift": {
            "EARLY":  {"ECONOMY": -3, "MILITARY": -1, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -4, "MILITARY": -1, "ORDER": -2, "FAITH": -2, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -5, "MILITARY": -2, "ORDER": -2, "FAITH": -2, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -4, "MILITARY": -1, "ORDER": -2, "FAITH": -2, "PRESTIGE": -1},
        },
    },
    "historical": {
        "label": "HISTORICAL RAILS",
        "tag": "HISTORY",
        "desc": "Real decline (Economy −4 after 1985), alternate-history content "
                "locked, 2 reserves. Every divergence you still force costs score.",
        "lifelines": 2,
        "rail": True,
        "divergence": 5,
        "drift": {
            "EARLY":  {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -4, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -3, "MILITARY": 0, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
        },
    },
}

MODE_ORDER: tuple[str, ...] = ("easy", "medium", "hard", "extreme", "historical")

# v4 shipped "normal"; keep the old word working for saves/CLI and the README.
MODE_ALIASES: dict[str, str] = {"normal": "medium", "medium": "medium"}


def mode_of(mode: str | None) -> dict:
    key = MODE_ALIASES.get(mode or "", mode or "medium")
    return MODES.get(key, MODES["medium"])


def normalize(mode: str | None) -> str:
    """Map a CLI/save value onto a real mode key."""
    key = MODE_ALIASES.get(mode or "", mode or "medium")
    return key if key in MODES else "medium"
