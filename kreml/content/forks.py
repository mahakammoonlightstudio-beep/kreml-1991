"""Divergence forks: the three mid-game doors of v5.

A fork is an ORDINARY event that the engine appends to the year's events when
that year comes up and the player has not yet chosen a path. Each option
plants one `path_*` flag; that flag then

  * nudges yearly drift (PATH_DRIFT),
  * gates a few options/directives elsewhere in the content (requires flags),
  * adds a line to the ending epilogue (PATH_EPILOGUE),
  * counts as divergence on the historical rails.

Nothing here needs new engine logic: forks are data + one lookup in the
engine's `collect_events`.
"""
from __future__ import annotations

from .builders import ev, opt

PATH_FLAGS: tuple[str, ...] = (
    "path_hardline", "path_reform", "path_neutral",
    "path_accel", "path_glasnost", "path_iron",
    "path_letgo", "path_hold", "path_market",
)

PATH_LABELS: dict[str, str] = {
    "path_hardline": "the hard line",
    "path_reform": "the reform line",
    "path_neutral": "the quiet line",
    "path_accel": "acceleration",
    "path_glasnost": "glasnost first",
    "path_iron": "iron discipline",
    "path_letgo": "the quiet empire",
    "path_hold": "the held line",
    "path_market": "the market bargain",
}

# Small yearly drift nudges: one path is active at most, so these stay gentle.
PATH_DRIFT: dict[str, dict[str, int]] = {
    "path_hardline": {"ORDER": +1, "FAITH": -1},
    "path_reform": {"FAITH": +1, "ORDER": -1},
    "path_neutral": {},
    "path_accel": {"ECONOMY": -1},
    "path_glasnost": {"FAITH": +1, "PRESTIGE": +1, "ORDER": -1},
    "path_iron": {"ORDER": +1, "FAITH": -1},
    "path_letgo": {"PRESTIGE": +1, "ORDER": -1},
    "path_hold": {"ORDER": +1, "PRESTIGE": -1},
    "path_market": {"ECONOMY": +1, "FAITH": -1},
}

# One closing line per path, added to the ending text when that path is open.
PATH_EPILOGUE: dict[str, str] = {
    "path_hardline": "The doctrine of the hard line outlived the tanks that taught it.",
    "path_reform": "The reform line became the Union's second official language.",
    "path_neutral": "You said nothing at the right moment, twice, and history forgave it.",
    "path_accel": "Acceleration was taught for decades as the decade that almost worked.",
    "path_glasnost": "Glasnost arrived early, and never entirely left the newspapers.",
    "path_iron": "Iron discipline held the corridors and emptied the shelves, in that order.",
    "path_letgo": "The quiet empire let go of its edges and kept its centre.",
    "path_hold": "The held line cost the Pact and bought the decade.",
    "path_market": "The empire was traded for the market, and both sides kept receipts.",
}

FORK_EVENTS: dict[str, object] = {}

FORK_EVENTS["fork_1968"] = ev(
    "fork_1968", "FORK: WHAT PRAGUE MEANS",
    "The tanks are gone or never went. The Politburo wants one sentence that "
    "defines the next twenty years of doctrine.",
    [
        opt("Follow the tanks with a doctrine",
            {"stats": {"ORDER": 4, "FAITH": -3, "PRESTIGE": -2},
             "path": "path_hardline",
             "court": {"old_guard": 6, "reformers": -6}},
            "The Brezhnev Doctrine gets a name, a border, and a budget line."),
        opt("Turn Prague into a negotiation table",
            {"stats": {"PRESTIGE": 3, "FAITH": 4, "ORDER": -4},
             "path": "path_reform",
             "court": {"reformers": 8, "old_guard": -6}},
            "Socialism keeps its human face; the apparatus keeps its doubts."),
        opt("Say nothing and let the dust settle",
            {"stats": {"ORDER": 1, "PRESTIGE": -1},
             "path": "path_neutral"},
            "Silence, filed under 'doctrine, provisional'."),
    ], once=True, alt=True)

FORK_EVENTS["fork_1985"] = ev(
    "fork_1985", "FORK: THE NEW SECRETARY'S FIRST HUNDRED DAYS",
    "A younger hand at the table, a leaking ceiling, and three folders: "
    "machines, newspapers, or discipline. The room waits for you to choose.",
    [
        opt("Acceleration: machines before markets",
            {"stats": {"ECONOMY": 3, "MILITARY": 2, "ORDER": -2},
             "path": "path_accel"},
            "New lathes arrive before new prices do."),
        opt("Openness first, shelves later",
            {"stats": {"FAITH": 5, "PRESTIGE": 3, "ORDER": -4},
             "path": "path_glasnost"},
            "The press breathes; Gosplan holds its breath."),
        opt("Discipline, and the plan",
            {"stats": {"ORDER": 6, "FAITH": -4, "ECONOMY": -2},
             "path": "path_iron",
             "court": {"old_guard": 5, "reformers": -5}},
            "Posters, punctuality, and a fifth column of economists."),
    ], once=True, alt=True)

FORK_EVENTS["fork_1989"] = ev(
    "fork_1989", "FORK: WHAT THE WALL MEANS",
    "Crowds are dancing on the Wall on live television. Your foreign policy "
    "consists, for one evening, entirely of what you say next.",
    [
        opt("Let the empire go quietly",
            {"stats": {"PRESTIGE": 4, "FAITH": 3, "ORDER": -4},
             "path": "path_letgo",
             "court": {"reformers": 6, "military": -6}},
            "The Pact becomes a memory with a shared railway timetable."),
        opt("Hold the line in the Pact",
            {"stats": {"ORDER": 5, "PRESTIGE": -5, "FAITH": -3},
             "path": "path_hold",
             "court": {"military": 6, "old_guard": 4}},
            "Garrisons stay; the world's cameras stay longer."),
        opt("Trade the empire for the market",
            {"stats": {"ECONOMY": 5, "PRESTIGE": -1, "ORDER": -2},
             "path": "path_market",
             "court": {"reformers": 4, "old_guard": -3}},
            "Every concession becomes an invoice with a delivery date."),
    ], once=True, alt=True)

# year → fork event id (engine appends it after that year's main events)
FORKS: dict[int, str] = {1968: "fork_1968", 1985: "fork_1985", 1989: "fork_1989"}
