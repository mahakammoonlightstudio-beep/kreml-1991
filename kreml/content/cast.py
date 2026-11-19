"""The Politburo cast: the three people who outlast the portraits.

v8 gives the three court factions a face each. They are not the historical
Politburo — they are composites with names, files and opinions — and they work
exactly like the rest of the content layer: pure data, plus one loyalty number.

  Viktor Volkov      Chief of Staff        Old Guard   (ORDER)
  Lidia Sorokina     Gosplan economist     Reformers   (ECONOMY)
  Marshal Balashov   Chief of the Staff    Army        (MILITARY)

Loyalty runs 0-100 and starts at 50. Backing a person in their memo raises it;
humiliating them lowers it. The most trusted member (70+) quietly returns one
point of their own gauge every year. A member abandoned below 20 costs one.
The highest loyalty at the end also names your successor.

The memos join the ordinary era pools, so no engine branch knows they exist.
"""
from __future__ import annotations

from ..model import Character
from .builders import ev, opt

CAST: tuple[Character, ...] = (
    Character(
        id="volkov",
        name="Viktor Volkov",
        role="Chief of Staff",
        faction="old_guard",
        stat="ORDER",
        line="He has outlived four General Secretaries and has opinions about all of them.",
    ),
    Character(
        id="sorokina",
        name="Lidia Sorokina",
        role="Gosplan economist",
        faction="reformers",
        stat="ECONOMY",
        line="She keeps two sets of figures: the ones she reports and the ones she believes.",
    ),
    Character(
        id="balashov",
        name="Marshal Arkady Balashov",
        role="Chief of the General Staff",
        faction="military",
        stat="MILITARY",
        line="He speaks in weather reports. The forecast is always snow.",
    ),
)

CAST_BY_ID: dict[str, Character] = {member.id: member for member in CAST}
CAST_IDS: tuple[str, ...] = tuple(member.id for member in CAST)
DEFAULT_LOYALTY: dict[str, int] = {member.id: 50 for member in CAST}


def get(member_id: str | None) -> Character | None:
    return CAST_BY_ID.get(member_id or "")


def loyalty_map(g) -> dict[str, int]:
    return getattr(g, "cast", None) or dict(DEFAULT_LOYALTY)


def loyalty_status(value: int) -> str:
    if value >= 75:
        return "trusted"
    if value >= 55:
        return "steady"
    if value >= 35:
        return "watchful"
    if value >= 20:
        return "restless"
    return "finished"


def successor(g) -> tuple[Character, int, dict[str, int]]:
    """The room's arithmetic: the most loyal survivor inherits the desk."""
    scores = {member.id: int(loyalty_map(g).get(member.id, 50)) for member in CAST}
    best = max(CAST, key=lambda member: scores[member.id])
    return best, scores[best.id], scores


def successor_line(g) -> str:
    member, value, _ = successor(g)
    if value >= 70:
        return (f"The succession file names {member.name}: loyal, known, and "
                f"already familiar with the locks.")
    if value >= 45:
        return (f"Power passes to {member.name} by default. The furniture stays; "
                f"the handwriting changes.")
    return (f"{member.name} takes the office without thanking you. By morning the "
            f"portraits have been rearranged.")


CAST_EVENTS: dict[str, object] = {}

# ══════════════════════════════════════════════════════════════════
# VOLKOV — the man who remembers where the files are
# ══════════════════════════════════════════════════════════════════
CAST_EVENTS["memo_volkov_cadres"] = ev(
    "memo_volkov_cadres", "The Cadres File",
    "Volkov sets a folder on your desk without sitting down. Eleven regional "
    "secretaries have held their posts since the war. Eleven younger ones have "
    "read a book. 'The Party is a building,' he says. 'Buildings need new "
    "windows. Or they need to be sealed.'",
    [
        opt("Let Volkov draft the replacements",
            {"loyalty": {"volkov": 5}, "stats": {"ORDER": 3, "FAITH": -1},
             "court": {"old_guard": 3, "reformers": -1},
             "flag_add": "cadres_volkov"},
            "The new windows are his windows. They open on his corridor."),
        opt("Protect the old names",
            {"loyalty": {"volkov": 2}, "stats": {"ORDER": 2, "ECONOMY": -2},
             "court": {"old_guard": 5, "reformers": -4},
             "flag_add": "old_cadres"},
            "The building stays warm, dark and exactly the right height."),
        opt("Appoint Sorokina's technocrats instead",
            {"loyalty": {"volkov": -5, "sorokina": 3},
             "stats": {"ECONOMY": 3, "ORDER": -2},
             "court": {"reformers": 5, "old_guard": -4},
             "flag_add": "cadres_technocrats"},
            "Volkov closes the folder. He has a list of your names too."),
    ],
    era="EARLY", once=True, requires={"min_year": 1969})

CAST_EVENTS["memo_volkov_succession"] = ev(
    "memo_volkov_succession", "Volkov's Succession Memorandum",
    "Three envelopes lie on the desk, one for each man who might replace you. "
    "Volkov would like you to initial the one with his name on it. 'Not because "
    "I want the office,' he says. 'Because the office will need someone who "
    "knows where the files are.'",
    [
        opt("Initial Volkov's envelope",
            {"loyalty": {"volkov": 6},
             "stats": {"ORDER": 3, "PRESTIGE": -1},
             "court": {"old_guard": 4}, "flag_add": "volkov_heir"},
            "He files it in a drawer that locks from his side."),
        opt("Refuse to name an heir",
            {"loyalty": {"volkov": -4}, "stats": {"ORDER": -1}, "influence": 2,
             "court": {"old_guard": -2, "reformers": -2, "military": -2}},
            "The room respects the refusal and begins drafting alternatives."),
        opt("Name Sorokina in writing",
            {"loyalty": {"volkov": -6, "sorokina": 6},
             "stats": {"ECONOMY": 1, "ORDER": -1},
             "court": {"reformers": 4, "old_guard": -4},
             "flag_add": "sorokina_heir"},
            "Volkov congratulates her warmly, then starts a new envelope."),
    ],
    era="LATE", once=True, requires={"min_year": 1985})

# ══════════════════════════════════════════════════════════════════
# SOROKINA — the only person in Gosplan who believes her own figures
# ══════════════════════════════════════════════════════════════════
CAST_EVENTS["memo_sorokina_pilot"] = ev(
    "memo_sorokina_pilot", "The Pilot Ledger",
    "Sorokina has found a furniture factory that made a profit and did not "
    "report it. She wants the accounting legal for one year, in one city, with "
    "your signature on a single page. 'If it fails, the page can be lost,' she "
    "says. 'If it works, the page becomes a precedent.'",
    [
        opt("Sign the single page",
            {"loyalty": {"sorokina": 5},
             "stats": {"ECONOMY": 4, "ORDER": -1},
             "court": {"reformers": 4, "old_guard": -4},
             "flag_add": "sorokina_pilot"},
            "The factory buys new lathes in March and a second set in June."),
        opt("Sign it, with a Party auditor attached",
            {"loyalty": {"sorokina": 2}, "stats": {"ECONOMY": 2, "ORDER": 1},
             "court": {"old_guard": 1, "reformers": 1}},
            "The profit is real; so is the paperwork built around it."),
        opt("File it under 'experiments, rejected'",
            {"loyalty": {"sorokina": -5}, "stats": {"ORDER": 2, "ECONOMY": -1},
             "court": {"old_guard": 2, "reformers": -3}},
            "The factory returns to making chairs at a loss, beautifully."),
    ],
    era="EARLY", once=True, requires={"min_year": 1968})

CAST_EVENTS["memo_sorokina_coops"] = ev(
    "memo_sorokina_coops", "The Cooperative Question",
    "A cooperative restaurant has opened near the university. The food is good, "
    "the prices are better, and the district committee has asked whether it "
    "should exist. Sorokina brings the receipts and a proposed tax schedule. "
    "'Either they are criminals,' she says, 'or they are the only people in "
    "Moscow who know what a menu is.'",
    [
        opt("Legalise them, and tax them properly",
            {"loyalty": {"sorokina": 5},
             "stats": {"ECONOMY": 4, "FAITH": 3},
             "court": {"reformers": 5, "old_guard": -5},
             "flag_add": "coops_legal"},
            "The restaurant takes reservations. The queue becomes a waiting list."),
        opt("Allow them, quietly, in three cities",
            {"loyalty": {"sorokina": 3}, "stats": {"ECONOMY": 2, "ORDER": -1},
             "influence": 2, "court": {"reformers": 2}},
            "Nothing is announced. Everything is available."),
        opt("Close them before the example spreads",
            {"loyalty": {"sorokina": -6},
             "stats": {"ORDER": 3, "ECONOMY": -3, "FAITH": -2},
             "court": {"old_guard": 3, "reformers": -5}},
            "The menu is confiscated as evidence."),
    ],
    era="LATE", once=True, requires={"min_year": 1987})

# ══════════════════════════════════════════════════════════════════
# BALASHOV — the army's weather
# ══════════════════════════════════════════════════════════════════
CAST_EVENTS["memo_balashov_budget"] = ev(
    "memo_balashov_budget", "The Budget He Did Not Ask For",
    "Balashov spreads a map over the table. The army's ration is down, the "
    "trucks are being cannibalised, and the General Staff has begun counting "
    "NATO divisions aloud in meetings. He does not ask for more money. He asks "
    "whether you have decided the army is no longer necessary.",
    [
        opt("Restore the ration, quietly",
            {"loyalty": {"balashov": 5}, "stats": {"MILITARY": 4}, "hc": -5,
             "court": {"military": 4, "old_guard": 2}},
            "The trucks get tyres. The count stops being read aloud."),
        opt("Give him a parade instead",
            {"loyalty": {"balashov": 1},
             "stats": {"PRESTIGE": 2, "MILITARY": 1, "ECONOMY": -2}},
            "The divisions look magnificent and remain hungry."),
        opt("Tell him the army will wait",
            {"loyalty": {"balashov": -5},
             "stats": {"MILITARY": -3, "ECONOMY": 3},
             "court": {"reformers": 3, "military": -4}},
            "He folds the map along its old creases."),
    ],
    era="MIDDLE", once=True, requires={"min_year": 1976})

CAST_EVENTS["memo_balashov_troops"] = ev(
    "memo_balashov_troops", "The Troops in the Snow",
    "Balashov has orders ready for three cities and would like to know which "
    "one to use them in. 'The young officers are asking,' he says. 'Not whether "
    "we will be ordered. Whether we will be ordered to do something we can "
    "explain to our mothers.'",
    [
        opt("No troops. Let the streets argue",
            {"loyalty": {"balashov": -4},
             "stats": {"ORDER": -4, "FAITH": 5, "PRESTIGE": 2, "MILITARY": -3},
             "court": {"military": -3, "reformers": 4},
             "flag_add": "no_troops_1989"},
            "The officers go home. Some of them write letters."),
        opt("Keep them in barracks, visible",
            {"loyalty": {"balashov": 3}, "stats": {"ORDER": 2, "FAITH": -1},
             "court": {"military": 2}},
            "The trucks are seen. The orders stay folded."),
        opt("Authorise the plans",
            {"loyalty": {"balashov": 5},
             "stats": {"ORDER": 4, "FAITH": -6, "PRESTIGE": -4},
             "court": {"military": 5, "reformers": -5},
             "flag_add": "troops_authorised"},
            "The snow is disturbed in three cities before morning."),
    ],
    era="LATE", once=True, requires={"min_year": 1989})

CAST_POOL_ADDITIONS: dict[str, tuple[str, ...]] = {
    "EARLY": ("memo_volkov_cadres", "memo_sorokina_pilot"),
    "MIDDLE": ("memo_balashov_budget",),
    "LATE": ("memo_volkov_succession", "memo_sorokina_coops",
             "memo_balashov_troops"),
}
