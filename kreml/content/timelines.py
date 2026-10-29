"""Timelines: the four starting scenarios of v5.

Each entry hands the player a different Union, a different first year and a
different ending year. The engine applies the opening state before year one;
the content layer then reacts to the flags a timeline plants.

  rails        1964 — the standard run ("the rails of history")
  reform      1964 — Kosygin's memo won in 1965; the reformers are already in
  flashpoint  1980 — Afghanistan is bleeding, the oil peak has arrived
  millennium  1992 — the Union survived 1991; now the last decade is yours
"""
from __future__ import annotations

from ..model import Timeline

TIMELINES: dict[str, Timeline] = {
    "rails": Timeline(
        id="rails",
        label="RAILS OF HISTORY",
        desc="October 1964, the standard appointment. The Union as history "
             "actually left it: five gauges, three factions, one oil market.",
        year=1964,
        end_year=1991,
        hc=50,
    ),
    "reform": Timeline(
        id="reform",
        label="THE REFORMERS' WINDOW",
        desc="Kosygin's profit memo won in 1965. The institutes are hopeful, "
             "the Old Guard is counting votes, and the pilot plots are running.",
        year=1964,
        end_year=1991,
        stats={"ECONOMY": 58, "MILITARY": 66, "ORDER": 60, "FAITH": 58, "PRESTIGE": 60},
        flags=("kosygin_pilot", "reformer"),
        court={"old_guard": 36, "reformers": 66, "military": 48},
        hc=52,
    ),
    "flashpoint": Timeline(
        id="flashpoint",
        label="COLD WAR FLASHPOINT",
        desc="1980: the 40th Army is already in the mountains, the Olympics are "
             "coming, and Moscow's oil is at its peak price. Twelve years left.",
        year=1980,
        end_year=1991,
        stats={"ECONOMY": 52, "MILITARY": 76, "ORDER": 66, "FAITH": 48, "PRESTIGE": 54},
        flags=("at_war", "siberian"),
        court={"old_guard": 62, "reformers": 30, "military": 64},
        hc=55,
        mandate=False,
    ),
    "millennium": Timeline(
        id="millennium",
        label="THE RED MILLENNIUM",
        desc="1992: the treaty held, the flag stayed red, and the century has "
             "ten years left. Play the extended era from its first morning.",
        year=1992,
        end_year=2001,
        stats={"ECONOMY": 58, "MILITARY": 62, "ORDER": 56, "FAITH": 60, "PRESTIGE": 66},
        flags=("treaty_signed", "perestroika", "pipelines"),
        court={"old_guard": 40, "reformers": 64, "military": 50},
        hc=34,
        mandate=False,
    ),
}

TIMELINE_ORDER: tuple[str, ...] = ("rails", "reform", "flashpoint", "millennium")


def get(timeline_id: str | None) -> Timeline:
    return TIMELINES.get(timeline_id or "rails", TIMELINES["rails"])
