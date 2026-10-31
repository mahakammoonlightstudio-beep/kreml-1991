"""v6: standing orders — the doctrine you fall back on.

An order is chosen once, and may be changed at any year boundary with `o`.
It is three things at once:

  * a small, permanent nudge to yearly drift (and a yearly influence trickle),
  * a colouring of the court's mood when you adopt it,
  * the INSTINCT used when a flash crisis freezes you (`hesitate` ops).

That last one is the point: with `--timed`, a crisis has seconds, and the
order you chose months earlier is what the Kremlin does when you say nothing.
"""
from __future__ import annotations

ORDERS: tuple[dict, ...] = (
    {
        "id": "order_discipline",
        "label": "Party discipline",
        "desc": "Posters, punctuality, and a plenum that never votes twice. "
                "Order rises; the shelves do not.",
        "drift": {"ORDER": 1, "FAITH": -1},
        "court": {"old_guard": 4, "reformers": -2},
        "yearly": {"influence": 1},
        "hesitate": {"stats": {"ORDER": 2, "FAITH": -3},
                     "court": {"old_guard": 3}},
    },
    {
        "id": "order_reform",
        "label": "Reform by memorandum",
        "desc": "The institutes draft, Gosplan resists, the economy moves "
                "half a step. The reformers answer your telephone first.",
        "drift": {"ECONOMY": 1, "ORDER": -1},
        "court": {"reformers": 4, "old_guard": -2},
        "yearly": {"influence": 1},
        "hesitate": {"stats": {"ECONOMY": 2, "ORDER": -1, "FAITH": -1},
                     "court": {"reformers": 2}},
    },
    {
        "id": "order_force",
        "label": "The mailed fist",
        "desc": "Decisions arrive by armoured column. The Army loves you; "
                "the world files a protest and the streets learn silence.",
        "drift": {"MILITARY": 1, "PRESTIGE": -1},
        "court": {"military": 5, "reformers": -3},
        "yearly": {"influence": 1},
        "hesitate": {"stats": {"ORDER": 2, "FAITH": -2, "PRESTIGE": -1},
                     "court": {"military": 3}},
    },
    {
        "id": "order_patience",
        "label": "Wait for the next plenum",
        "desc": "Nothing is decided until everything is. Quiet, careful, and "
                "occasionally late — but the machinery keeps its balance.",
        "drift": {},
        "court": {"old_guard": 1, "reformers": 1, "military": 1},
        "yearly": {"influence": 3},
        "hesitate": {"stats": {"PRESTIGE": -1}, "influence": 1},
    },
)

ORDER_BY_ID: dict[str, dict] = {o["id"]: o for o in ORDERS}


def get(order_id: str | None) -> dict | None:
    """The order behind an id that survived a save file, or None."""
    return ORDER_BY_ID.get(order_id or "")


def instinct(g, ev) -> dict:
    """What the Kremlin does when the clock runs out on `ev`.

    The event's own hesitation is the baseline; a standing order replaces it
    (that is what a doctrine is for), but only for the gauges it names.
    """
    order = get(getattr(g, "order", None))
    if order is None:
        return dict(getattr(ev, "hesitate", {}) or {})
    return {k: (dict(v) if isinstance(v, dict) else v)
            for k, v in (order.get("hesitate") or {}).items()}
