"""v6: the Politburo agenda — one demand per year, with a price.

At the start of every year the STRONGEST faction tables a demand: hold the
gauge it cares about against the year's drift. Meet it and the Kremlin owes you
(influence); miss it and that faction remembers (court). The strong ask because
they can afford to be refused — a despairing faction withdraws instead, which
is what keeps the court out of a death spiral.

The engine only reads `stat`, `target` and `faction`; the words live here so
the demand can be rewritten without touching logic.
"""
from __future__ import annotations

from .modes import MODES

FACTION_STAT: dict[str, str] = {
    "old_guard": "ORDER",
    "reformers": "ECONOMY",
    "military": "MILITARY",
}

DEMAND_LINES: dict[str, str] = {
    "ECONOMY": "Gosplan wants {target} on the economy line by December, or an explanation.",
    "ORDER": "The Old Guard wants order at {target} by the plenum, or a resignation.",
    "MILITARY": "The general staff wants the army at {target} by the autumn review.",
    "FAITH": "The Party wants the people at {target} by the anniversary, and it is not joking.",
    "PRESTIGE": "The Foreign Ministry wants {target} in the world's eyes before the summit.",
}

REWARD = 5          # fallback influence for meeting the agenda
FAIL_COURT = -5     # patience lost by the faction that tabled it
FAIL_FAITH = 0      # an internal quota is not a public promise

# v6 balance: the favour market tightens with the difficulty. `reward` is what a
# met demand pays; `margin` is how far above current + drift the target sits. A
# flat +5 paid every year was farmable — measured runs survived every mode by
# simply buying the court back, which flattened the ladder.
AGENDA_DEFAULT = {"reward": 5, "margin": 2}


def terms(mode: str | None) -> dict:
    cfg = (MODES.get(mode or "medium", {}) or {}).get("agenda")
    return {**AGENDA_DEFAULT, **(cfg or {})}


def open_agenda(g) -> dict:
    """Table this year's demand from the strongest faction (or a wildcard)."""
    faction = max(("old_guard", "reformers", "military"),
                  key=lambda f: g.court.get(f, 50))
    if g.rng.random() < 0.22:                     # now and then, the country asks
        stat = g.rng.choice(("FAITH", "PRESTIGE"))
    else:
        stat = FACTION_STAT[faction]
    # v6 balance: the demand is "beat inertia", not "grow five points while the
    # plan, the oil market and the court all push the other way". Without this
    # every year was a guaranteed miss and the court died of arithmetic.
    drift = ((MODES.get(g.mode, {}).get("drift") or {})
             .get(g.era, {}).get(stat, 0))
    margin = terms(g.mode)["margin"]
    target = max(18, min(92, int(g.stats[stat]) + int(drift) + margin))
    return {
        "faction": faction,
        "stat": stat,
        "target": target,
        "text": DEMAND_LINES[stat].format(target=target),
        "met": None,
    }


def settle_agenda(g) -> dict:
    """Grade last year's demand and hand back the results (for the briefing)."""
    agenda = getattr(g, "agenda", None)
    if not agenda:
        return {"met": None, "text": "", "reward": 0}
    met = g.stats[agenda["stat"]] >= agenda["target"]
    agenda["met"] = met
    agenda["actual"] = g.stats[agenda["stat"]]
    reward = terms(getattr(g, "mode", "medium"))["reward"]
    return {"met": met, "text": agenda["text"], "reward": reward if met else 0,
            "stat": agenda["stat"], "target": agenda["target"],
            "actual": agenda["actual"], "faction": agenda["faction"],
            "fail_court": FAIL_COURT, "fail_faith": FAIL_FAITH}


def describe(agenda: dict | None) -> str:
    if not agenda:
        return "no agenda tabled"
    return (f"{agenda['stat']} ≥ {agenda['target']} "
            f"({agenda['faction'].replace('_', ' ')})")
