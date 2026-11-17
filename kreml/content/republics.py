"""Republic Unrest: the four fault lines of the Union.

v7-5 adds a second, regional pressure board next to the five national gauges.
The Union can look stable in Moscow while the Baltic, Ukraine, the Caucasus and
Central Asia are already reading the exits. The numbers are deliberately hard
to see from the centre: the board shows them, but drift, censorship and the
oil market keep pulling them away from you.

Content is data. The engine applies the yearly pressure and the consequences;
events, directives and personal actions can move a republic with the
``unrest`` ops key.
"""
from __future__ import annotations

REPUBLICS: tuple[str, ...] = ("baltic", "ukraine", "caucasus", "central_asia")

LABELS: dict[str, str] = {
    "baltic": "Baltic",
    "ukraine": "Ukraine",
    "caucasus": "Caucasus",
    "central_asia": "Central Asia",
}

SHORT: dict[str, str] = {
    "baltic": "BAL",
    "ukraine": "UKR",
    "caucasus": "CAU",
    "central_asia": "C.AS",
}

DEFAULT_UNREST: dict[str, int] = {
    "baltic": 10,
    "ukraine": 12,
    "caucasus": 14,
    "central_asia": 8,
}

# Timelines already past the first cracks inherit a more flammable map.
TIMELINE_UNREST: dict[str, dict[str, int]] = {
    "rails": {},
    "reform": {"baltic": 14, "ukraine": 14, "caucasus": 16, "central_asia": 10},
    "flashpoint": {"baltic": 24, "ukraine": 18, "caucasus": 38, "central_asia": 18},
    "millennium": {"baltic": 26, "ukraine": 20, "caucasus": 42, "central_asia": 24},
}

# Average points per republic per year, before difficulty and events.
YEARLY_PRESSURE: dict[str, float] = {
    "EARLY": 0.9,
    "MIDDLE": 1.3,
    "LATE": 1.8,
    "NEW": 1.1,
}

# The same board is harder on the modes that already fight back.
MODE_SCALE: dict[str, float] = {
    "easy": 0.30,
    "medium": 0.75,
    "hard": 1.00,
    "extreme": 1.25,
    "flash": 1.00,
    "historical": 0.80,
}

# Historical flashpoints. These are added on top of the yearly pressure.
SHOCK_YEARS: dict[int, dict[str, int]] = {
    1986: {"baltic": 2, "ukraine": 2, "caucasus": 2, "central_asia": 2},
    1988: {"baltic": 4, "ukraine": 3, "caucasus": 5, "central_asia": 2},
    1989: {"baltic": 7, "ukraine": 4, "caucasus": 6, "central_asia": 3},
    1990: {"baltic": 6, "ukraine": 5, "caucasus": 6, "central_asia": 4},
    1991: {"baltic": 6, "ukraine": 6, "caucasus": 5, "central_asia": 4},
}

# At this level a republic stops sending memoranda and starts sending a crisis.
CRISIS_THRESHOLD = 75
# Below this, the centre can still call the first secretary by name.
QUIET_THRESHOLD = 25
# A signed union treaty buys down the temperature, once.
TREATY_REDUCTION = 10
