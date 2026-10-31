"""v6: political capital — what influence is actually spent on.

Influence is the second currency of the Kremlin. It is not money (that is the
valas) and not legitimacy (that is Faith): it is the number of people who will
take your call at midnight. The engine offers these moves in the command bar
under `i`; each one costs influence and pays in court, gauges or hard currency.

Pure data: `cost` is checked by the engine, `ops` is applied through ops.py,
and `requires` uses the same vocabulary as every other menu in the game.
"""
from __future__ import annotations

MOVES: tuple[dict, ...] = (
    {
        "id": "army_dinner",
        "label": "Dine the general staff",
        "cost": 8,
        "desc": "Sand tables, brandy, and a promotion list you are allowed to read.",
        "ops": {"court": {"military": 12}, "stats": {"ECONOMY": -1}},
    },
    {
        "id": "old_guard_silence",
        "label": "Buy the Old Guard's silence",
        "cost": 8,
        "desc": "Dachas are cheaper than plenums, and quieter.",
        "ops": {"court": {"old_guard": 12, "reformers": -3}},
    },
    {
        "id": "reform_institutes",
        "label": "Fund the reformers' institutes",
        "cost": 8,
        "desc": "Charts, calculators, and one telephone that is not tapped yet.",
        "ops": {"court": {"reformers": 12, "old_guard": -4}, "stats": {"FAITH": 1}},
    },
    {
        "id": "valas_draw",
        "label": "Draw on the special account",
        "cost": 10,
        "desc": "The vault answers to one signature, and it is yours.",
        "ops": {"hc": 6},
        "requires": {"hc_max": 94},
    },
    {
        "id": "press_management",
        "label": "Manage the evening bulletin",
        "cost": 6,
        "desc": "Two paragraphs move; one editor is promoted out of the way.",
        "ops": {"stats": {"ORDER": 3, "FAITH": -1}},
    },
    {
        "id": "crisis_team",
        "label": "Keep a crisis team awake",
        "cost": 5,
        "desc": "Six men, three telephones and a samovar: they buy you seconds.",
        "ops": {"flag_add": "crisis_team"},
        "requires": {"not_flags": ["crisis_team"]},
    },
    {
        "id": "emergency_package",
        "label": "Override Gosplan: emergency package",
        "cost": 14,
        "desc": "Money and priorities to the two weakest sectors, tonight.",
        "ops": {"special": "emergency_package"},
    },
)


# v6 balance: favours inflate. Measured runs showed that a flat 8 ❖ for +12
# court made the whole difficulty ladder purchasable — every mode survived once
# the autopilot spent influence. The same general does not sell his loyalty
# twice at the same price, so each repeat of a move costs more.
INFLATION = 3


def note_use(g, move_id: str) -> None:
    uses = getattr(g, "capital_uses", None)
    if uses is None:
        g.capital_uses = uses = {}
    uses[move_id] = int(uses.get(move_id, 0)) + 1


def cost_of(g, move: dict) -> int:
    """Today's price for this favour, after every earlier purchase."""
    uses = (getattr(g, "capital_uses", None) or {}).get(move["id"], 0)
    return int(move["cost"]) + INFLATION * int(uses)


def available(g) -> list[dict]:
    """The moves the Secretary can actually pay for right now, at today's price."""
    from ..ops import check_requires
    out = []
    for move in MOVES:
        price = cost_of(g, move)
        if g.influence < price:
            continue
        ok, _ = check_requires(g, move.get("requires"))
        if ok:
            out.append({**move, "cost": price, "base_cost": move["cost"],
                        "uses": price - int(move["cost"])})
    return out
