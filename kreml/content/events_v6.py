"""v6 content: flash crises and the political catalogue.

A v6 event may declare two extra fields:

  clock=8          seconds on the wall. Enforced only when the player runs
                   `python main.py --timed` (or plays the FLASH CRISIS mode) —
                   the terminal build times the decision, the web build does not.
  hesitate={...}   the ops applied when nobody decides: the crisis decides for
                   you. A standing order overrides this with its own instinct.

Everything else is an ordinary Event: the pools below decide when it appears,
and the engine needs no special case for any single one of them.
"""
from __future__ import annotations

from .builders import ev, opt

V6_EVENTS: dict[str, object] = {}

# ══════════════════════════════════════════════════════════════════
# FLASH CRISES — the clock is the antagonist
# ══════════════════════════════════════════════════════════════════
V6_EVENTS["flash_phone"] = ev(
    "flash_phone", "03:12 — The Telephone",
    "The duty officer's voice is very calm. The screen shows three tracks "
    "over the Arctic and the second confirmation has not arrived.",
    [
        opt("Order the regiments up, wake nobody",
            {"stats": {"MILITARY": 2, "ECONOMY": -1}, "flag_add": "night_alarm"},
            "Tanks start in the snow. Nobody in the Politburo knows why."),
        opt("Wake the Politburo and confirm together",
            {"stats": {"ORDER": -1, "PRESTIGE": 2}, "influence": 2},
            "Forty minutes of dialling; the tracks turn out to be weather."),
        opt("Demand the raw telemetry first",
            {"stats": {"ORDER": 1, "PRESTIGE": -1}, "hc": 1},
            "A colonel reads numbers aloud until the sun comes up."),
    ],
    era="MIDDLE", once=True, clock=8,
    hesitate={"stats": {"ORDER": -2, "PRESTIGE": -2}, "flag_add": "night_alarm"})

V6_EVENTS["flash_grain"] = ev(
    "flash_grain", "The Grain Train Is Blocked",
    "Eleven wagons of imported wheat stand at a junction while a district "
    "committee argues about whose plan they belong to.",
    [
        opt("Send a plenipotentiary with a rifle",
            {"stats": {"ORDER": 3, "FAITH": -2}, "court": {"old_guard": 2}},
            "The wagons move within the hour, and so do three resignations."),
        opt("Bribe the junction with a fuel allocation",
            {"stats": {"ECONOMY": -2, "FAITH": 2}, "influence": 1},
            "Diesel is political currency; the bread arrives warm."),
        opt("Let the local committee decide",
            {"stats": {"ORDER": -1, "FAITH": -1}},
            "The argument becomes a precedent, and the precedent becomes a habit."),
    ],
    era="MIDDLE", clock=12,
    hesitate={"stats": {"FAITH": -2, "ECONOMY": -2}, "hc": -2})

V6_EVENTS["flash_border"] = ev(
    "flash_border", "The Border Post Reports Movement",
    "A NATO reconnaissance troop has crossed the line by four hundred metres. "
    "The local colonel is asking Moscow for one word.",
    [
        opt("Authorise a warning shot",
            {"stats": {"MILITARY": 2, "PRESTIGE": -3}},
            "One burst into the snow ends the incident and starts a file."),
        opt("Order him to escort them back, smiling",
            {"stats": {"PRESTIGE": 2, "ORDER": -1}, "influence": 2},
            "Two officers share cigarettes at the marker post."),
        opt("Say nothing; let the staff handle it",
            {"stats": {"ORDER": 1, "PRESTIGE": -1}},
            "By evening the staff has handled it into a communique."),
    ],
    era="LATE", clock=8,
    hesitate={"stats": {"ORDER": -2, "MILITARY": -1}, "flag_add": "brink"})

V6_EVENTS["flash_tass"] = ev(
    "flash_tass", "TASS Has Quoted You Incorrectly",
    "The evening bulletin attributes to you a sentence you did not say, and "
    "four foreign ministries have already asked for clarification.",
    [
        opt("Correct it at once, on television",
            {"stats": {"FAITH": 2, "PRESTIGE": 1, "ORDER": -1}, "influence": 1},
            "You read your own transcript; the country believes the second version."),
        opt("Stand by the sentence — it sounds better",
            {"stats": {"PRESTIGE": -2, "ORDER": 2}, "flag_add": "tass_gaffe"},
            "The quotation becomes policy by Thursday."),
        opt("Blame the duty editor",
            {"stats": {"ORDER": 1, "FAITH": -2}},
            "One career ends quietly; the sentence keeps circulating."),
    ],
    era="LATE", clock=10,
    hesitate={"stats": {"PRESTIGE": -2, "FAITH": -1}, "flag_add": "tass_gaffe"})

V6_EVENTS["flash_walkout"] = ev(
    "flash_walkout", "The Night Shift Walks Out",
    "At the Volga plant the night shift has stopped the line and is standing "
    "in the yard, politely, in the snow.",
    [
        opt("Go there yourself, tonight",
            {"stats": {"FAITH": 3, "ORDER": -1}, "flag_add": "walkout", "influence": 2},
            "You stand in the snow and listen for forty minutes. The line restarts."),
        opt("Send the director out to talk",
            {"stats": {"ECONOMY": 1, "FAITH": -1}},
            "He promises boots and a canteen; the yard empties slowly."),
        opt("Send the militia to clear the yard",
            {"stats": {"ORDER": 2, "FAITH": -3}, "flag_add": "walkout"},
            "The line restarts; the story does not stop."),
    ],
    era="LATE", once=True, clock=12,
    hesitate={"stats": {"FAITH": -2, "ECONOMY": -1}, "flag_add": "walkout"})

# ══════════════════════════════════════════════════════════════════
# POLITICAL EVENTS — the slow ones
# ══════════════════════════════════════════════════════════════════
V6_EVENTS["emigre_letter"] = ev(
    "emigre_letter", "A Letter From the Emigres",
    "A Paris newspaper prints an open letter: come home, they write, and we "
    "will bring the patents with us.",
    [
        opt("Answer in Pravda, invite them publicly",
            {"stats": {"PRESTIGE": 3, "FAITH": 2, "ORDER": -2}, "influence": 3},
            "Three families arrive; the rest watch the next six months."),
        opt("Offer amnesty quietly through the embassy",
            {"stats": {"PRESTIGE": 2, "ECONOMY": 1}, "hc": -2},
            "Nothing is announced and two engineers return."),
        opt("Call them traitors in the same paper",
            {"stats": {"ORDER": 2, "PRESTIGE": -2}},
            "The letter is answered, which was the point of writing it."),
    ],
    era="EARLY", once=True)

V6_EVENTS["factory_rota"] = ev(
    "factory_rota", "The Three-Shift Experiment",
    "A young director proposes running the plant around the clock, with the "
    "profits staying in the plant. Two ministries have opinions.",
    [
        opt("Let him try it for a year",
            {"stats": {"ECONOMY": 4, "ORDER": -1}, "flag_add": "rota",
             "court": {"reformers": 3}},
            "Output climbs; the ministry's statistics climb more slowly."),
        opt("Approve it, but take the profits",
            {"stats": {"ECONOMY": 2, "ORDER": 1, "FAITH": -1}},
            "The plant works nights and the budget works days."),
        opt("Decline: the plan is the plan",
            {"stats": {"ORDER": 2, "ECONOMY": -1}},
            "The director is promoted sideways, with a diploma."),
    ],
    era="EARLY", once=True)

V6_EVENTS["oil_spill"] = ev(
    "oil_spill", "A Pipeline Weeps Into the River",
    "A seam in the export line has been losing crude for eleven days. The "
    "district says the fish are fine.",
    [
        opt("Stop the line, lose the quarter",
            {"stats": {"ECONOMY": -4, "FAITH": 2, "PRESTIGE": 1}, "influence": 1},
            "The river survives; the plan does not."),
        opt("Patch it at night and say nothing",
            {"stats": {"ECONOMY": 2, "FAITH": -2, "PRESTIGE": -1},
             "flag_add": "oil_cover"},
            "The patch holds until the spring."),
        opt("Announce a modernisation programme",
            {"stats": {"ECONOMY": -1, "PRESTIGE": 2}, "hc": -3},
            "A committee is appointed before the river freezes."),
    ],
    era="MIDDLE", once=True)

V6_EVENTS["church_council"] = ev(
    "church_council", "The Church Asks For a Signature",
    "The Patriarch's office requests legal registration, a seminary and the "
    "return of three cathedrals. The building is on the list either way.",
    [
        opt("Register the Church, return one cathedral",
            {"stats": {"FAITH": 4, "PRESTIGE": 2, "ORDER": -3},
             "court": {"old_guard": -5, "reformers": 3}, "flag_add": "church_legal"},
            "A thousand years of architecture reopens with a ribbon."),
        opt("Return the buildings, refuse the seminary",
            {"stats": {"FAITH": 2, "ORDER": 1}, "influence": 1},
            "Bells return; the classrooms stay secular."),
        opt("Refuse all three requests",
            {"stats": {"ORDER": 3, "FAITH": -3, "PRESTIGE": -2}},
            "The request is filed under 'religious survivals'."),
    ],
    era="LATE", once=True, requires={"min_year": 1988})

V6_EVENTS["digital_hunger"] = ev(
    "digital_hunger", "The Ministry Discovers Software",
    "A ministry report admits that the Union imports its accounting. The "
    "authors recommend one academy, one factory and one standard.",
    [
        opt("Fund the academy and the standard",
            {"stats": {"ECONOMY": 4, "PRESTIGE": 2}, "hc": -5, "influence": 2},
            "One language for the machines, one language for the meetings."),
        opt("Buy the software and the licences",
            {"stats": {"ECONOMY": 2}, "hc": -6, "flag_add": "imported_bits"},
            "It works immediately, which is suspicious."),
        opt("Declare the gap a Western provocation",
            {"stats": {"ORDER": 2, "ECONOMY": -3}},
            "The report is reclassified and the factories keep counting by hand."),
    ],
    era="LATE", once=True, requires={"min_year": 1989})

V6_EVENTS["veterans_march"] = ev(
    "veterans_march", "The Afghan Generation Marches",
    "A thousand men with medals and no apartments walk to the Kremlin wall, "
    "carrying a list of names and a second list of addresses.",
    [
        opt("Meet them at the wall and take the list",
            {"stats": {"FAITH": 4, "ORDER": -1}, "influence": 4,
             "flag_add": "veterans_heard"},
            "Two ministers are handed housing warrants before the cameras."),
        opt("Offer pensions and a monument",
            {"stats": {"ECONOMY": -3, "FAITH": 2}, "flag_add": "veterans_paid"},
            "The monument is bronze; the pensions are paper."),
        opt("Clear the square before the evening news",
            {"stats": {"ORDER": 2, "FAITH": -4, "PRESTIGE": -2},
             "flag_add": "veterans_cleared"},
            "The wall is empty by 18:00 and the list circulates by 19:00."),
    ],
    era="NEW", once=True, requires={"any_flags": ["afghan_withdraw", "afghan_deep"]})

# Pools gain these ids on top of their v5 contents (the engine never notices).
V6_POOL_ADDITIONS: dict[str, tuple[str, ...]] = {
    "EARLY": ("emigre_letter", "factory_rota"),
    "MIDDLE": ("oil_spill", "flash_phone", "flash_grain"),
    "LATE": ("flash_border", "flash_tass", "flash_walkout",
             "church_council", "digital_hunger"),
    "NEW": ("veterans_march",),
}
