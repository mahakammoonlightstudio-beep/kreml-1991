"""Personal focus actions: small, quiet levers pulled every year.

These give the player daily-life freedom beyond big public policy:
one evening of attention, spent where the Secretary wishes.
"""
from ..model import Action
from ..ops import check_requires
from ..state import Kremlin


def make_action(id: str, label: str, desc: str, ops: dict, *,
                requires: dict | None = None, once: bool = False) -> Action:
    return Action(id=id, label=label, desc=desc, ops=ops,
                  requires=requires or {}, once=once)


FOCUS_ACTIONS: tuple[Action, ...] = (
    make_action("factory_visit", "Inspect a factory floor",
                "Wear the rubber boots. Talk to the foundry workers.",
                {"stats": {"ECONOMY": (2, 3)}}),
    make_action("space_check", "Check on the space programme",
                "Baikonur's designers brief you over strong tea.",
                {"stats": {"PRESTIGE": (1, 2), "ECONOMY": -1}},
                requires={"stats": {"MILITARY": 50}}),
    make_action("farms_visit", "Chat with collective farmers",
                "You hear more truth at a tractor shed than in any politburo hall.",
                {"stats": {"FAITH": (1, 2), "ORDER": -1}}),
    make_action("thunder_speech", "Deliver a thunderous speech",
                "The hall erupts; the nation listens disturbed but moved.",
                {"stats": {"FAITH": (1, 3), "ORDER": -1}}),
    make_action("dacha_rest", "A quiet weekend at the dacha",
                "Bearskin rug, tea, silence. You will face the next crisis rested.",
                {"stats": {"FAITH": 1}, "flag_add": "rested"}),
    make_action("republic_call", "Call a republic's first secretary",
                "A friendly call recalibrates eight provinces at once.",
                {"stats": {"ORDER": (1, 2)}}),
    make_action("enemy_papers", "Read the enemy newspapers",
                "You know exactly what the Pentagon lent the Times to print.",
                {"stats": {"PRESTIGE": 2, "ORDER": -1}}),
    make_action("audit_ministries", "Sit with the state auditors",
                "An hour with ledgers finds money the ministries lost.",
                {"stats": {"ECONOMY": 2, "ORDER": 1}}, once=True),
    make_action("private_diary", "Write one page of a private diary",
                "Future historians would kill for this page.",
                {"stats": {"FAITH": 1}, "flag_add": "diary"}),
    # ── v4: the court & the vault ───────────────────────────────────────
    make_action("politburo_dinners", "Dinner with the Politburo families",
                "Caviar diplomacy: olives, sturgeon, and very quiet arithmetic.",
                {"stats": {"ECONOMY": -1}, "court": {"old_guard": 4}}),
    make_action("reform_tea", "Tea with the young economists",
                "Institute tables full of charts you would go to prison to see.",
                {"stats": {"FAITH": 1}, "court": {"reformers": 5, "old_guard": -2}}),
    make_action("war_games", "Weekend at the general staff's war games",
                "Sand tables, red arrows, and much veneration of your chair.",
                {"stats": {"ECONOMY": -1}, "court": {"military": 6}}),
    make_action("western_districts", "Tour the western military districts",
                "Garrison towns, new tanks under tarpaulins, and generals who "
                "count your motorcade as a promotion.",
                {"stats": {"MILITARY": 2, "ECONOMY": -1},
                 "court": {"military": 3}}),
    make_action("republic_tour", "Walk the republics' party schools",
                "Cadres in nine capitals hear your voice live for once.",
                {"stats": {"FAITH": 1, "ORDER": 1}, "court": {"reformers": 1}}),
    make_action("vault_inspect", "Inspect the gold vault by lamplight",
                "Bars, seals, and a keeper who talks only in loan words.",
                {"hc": (2, 5)}),
    # ── v6: evenings that pay in political capital ─────────────────
    make_action("television_address", "Address the nation on television",
                "Nine minutes, no notes, and a promise you will have to keep.",
                {"stats": {"FAITH": (1, 2), "ORDER": -1, "PRESTIGE": 1}}),
    make_action("party_archive", "Read the Party archive",
                "Who owed whom in 1956 is still useful in 1979.",
                {"influence": 2}),
    make_action("governors_call", "Ring three provincial governors",
                "Two favours, one warning, and a very good line about the harvest.",
                {"stats": {"ORDER": 2}, "court": {"old_guard": 2}}),
    make_action("kitchen_table", "Sit at a worker's kitchen table",
                "Tea, jam, and the only reliable reporting in the country.",
                {"stats": {"FAITH": 2, "ECONOMY": -1}, "influence": 1}),
    make_action("valas_audit", "Audit the valas accounts",
                "The accountants find a drawer everybody had forgotten.",
                {"hc": (2, 4), "court": {"reformers": 1}}),
)


def available_actions(g: Kremlin) -> list[Action]:
    out: list[Action] = []
    for a in FOCUS_ACTIONS:
        if a.once and a.id in g.used_focus:
            continue
        ok, _ = check_requires(g, a.requires)
        if ok:
            out.append(a)
    return out
