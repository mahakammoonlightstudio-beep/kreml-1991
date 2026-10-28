"""Difficulty modes: pure data.

Each mode defines the yearly drift table per era, plus how many crisis
lifelines the Politburo starts with. Everything else (bonuses, war
attrition, event pain) stays identical across modes.
"""

MODES: dict[str, dict] = {
    "easy": {
        "label": "SWEEPING REFORMS",
        "tag": "REFORM",
        "desc": "Gentle drift (Economy −1, −2 after 1985), 5 crisis reserves. "
                "For architecting the future, not surviving it.",
        "lifelines": 5,
        "drift": {
            "EARLY":  {"ECONOMY": -1, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -1, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -1, "MILITARY": 0, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
        },
    },
    "normal": {
        "label": "BALANCED",
        "tag": "BALANCED",
        "desc": "The historical grind: drift −2/−3 late, 3 crisis reserves. "
                "The Union fell once; the margins are thin.",
        "lifelines": 3,
        "drift": {
            "EARLY":  {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -2, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -3, "MILITARY": -1, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -2, "MILITARY": 0, "ORDER": -1, "FAITH": -1, "PRESTIGE": -1},
        },
    },
    "hard": {
        "label": "OLD GUARD IRON GRASP",
        "tag": "IRON",
        "desc": "The system fights back: Economy −3 (−4 after 1985), Order −2/yr, "
                "Faith −2 after 1985, only 2 crisis reserves. For Stalins with a death wish.",
        "lifelines": 2,
        "drift": {
            "EARLY":  {"ECONOMY": -3, "MILITARY": -1, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
            "MIDDLE": {"ECONOMY": -3, "MILITARY": -1, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
            "LATE":   {"ECONOMY": -4, "MILITARY": -1, "ORDER": -2, "FAITH": -2, "PRESTIGE": -1},
            "NEW":    {"ECONOMY": -3, "MILITARY": 0, "ORDER": -2, "FAITH": -1, "PRESTIGE": -1},
        },
    },
}

MODE_ORDER: tuple[str, ...] = ("easy", "normal", "hard")


def mode_of(mode: str | None) -> dict:
    return MODES.get(mode or "normal", MODES["normal"])
