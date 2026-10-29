"""The ops DSL: the single place where content effects touch the state.

Content declares WHAT must happen (data). This module declares HOW.

Ops vocabulary (dict keys):
  "stats"     : {"ECONOMY": +3}             (int, or (min, max) for a random roll)
  "flag_add"  : "name" | ["a", "b"]
  "flag_rm"   : same shapes
  "queue"     : [(delay_years, event_id)]
  "hc"        : +10 | (min, max)            (hard currency / valas reserve)
  "court"     : {"old_guard": +5, ...}      (faction moods, clamped 0-100)
  "special"   : "handler_name" | ["a", "b"] (custom logic, via SPECIALS registry)
  "path"      : "path_reform"             (divergence line; replaces any previous)

Requirements vocabulary (dict keys):
  "stats"     : {"MILITARY": 60}            (stat must be >= value)
  "flags"     : ["f1"]                      (ALL of them must exist)
  "any_flags" : ["a", "b"]                  (at least ONE must exist)
  "not_flags" : ["x"]                       (must NOT exist)
  "min_year" / "max_year" : int
  "hc"        : 20                          (valas reserve must be >= value)
  "hc_max"    : 35                          (valas reserve must be <= value)
  "court_min" : {"old_guard": 60}           (each faction must be >= value)
  "court_max" : {"old_guard": 15}           (each faction must be <= value)

Anything new in the game = new content data + maybe one new op key here.
"""
from __future__ import annotations

from typing import Callable

from .state import Kremlin, STATS, clamp, FACTIONS
from . import ui

SPECIALS: dict[str, Callable[[Kremlin], None]] = {}

# ── v5: plan fatigue ───────────────────────────────────────────────────
# Repeating the same lever every year stops working: gains shrink with every
# previous use (in this run), down to a floor. Costs are never softened.
FATIGUE: tuple[float, ...] = (1.0, 0.85, 0.70, 0.55, 0.45, 0.35)
FATIGUE_FLOOR = FATIGUE[-1]


def fatigue_multiplier(uses: int) -> float:
    return FATIGUE[min(max(0, int(uses)), len(FATIGUE) - 1)]


def _scaled(value, mult: float):
    if isinstance(value, tuple):
        lo, hi = value
        if lo > 0:
            lo = max(1, int(round(lo * mult)))
        if hi > 0:
            hi = max(lo, int(round(hi * mult)))
        return (lo, hi)
    if isinstance(value, int) and value > 0:
        return max(1, int(round(value * mult)))
    return value


def scale_ops(ops: dict | None, mult: float) -> dict | None:
    """Copy of `ops` whose POSITIVE gains are multiplied by `mult`.

    Penalties, flags, queues and specials are untouched: a stale plan still
    costs what it costs, it just no longer pays.
    """
    if not ops or mult >= 1.0:
        return ops
    out = dict(ops)
    if "stats" in ops:
        out["stats"] = {k: _scaled(v, mult) for k, v in ops["stats"].items()}
    if "hc" in ops:
        out["hc"] = _scaled(ops["hc"], mult)
    if "court" in ops:
        out["court"] = {k: _scaled(v, mult) for k, v in ops["court"].items()}
    return out


def _special(name: str):
    def deco(fn):
        SPECIALS[name] = fn
        return fn
    return deco


def _as_list(x) -> list:
    if x is None:
        return []
    return [x] if isinstance(x, str) else list(x)


def _court_clamp(g: Kremlin) -> None:
    for f in FACTIONS:
        g.court[f] = max(0, min(100, g.court[f]))


# ---------------------------------------------------------------
# Requirement checking (used by engine to filter menus)
# ---------------------------------------------------------------
def check_requires(g: Kremlin, req: dict | None) -> tuple[bool, str]:
    if not req:
        return True, ""
    for stat, minimum in (req.get("stats") or {}).items():
        if g.stats.get(stat, 0) < minimum:
            return False, f"needs {stat} ≥ {minimum}"
    for f in req.get("flags", []):
        if f not in g.flags:
            return False, f"requires earlier decision: {f.replace('_', ' ')}"
    anyf = req.get("any_flags", [])
    if anyf and not (set(anyf) & g.flags):
        return False, "requires a path not taken"
    for f in req.get("not_flags", []):
        if f in g.flags:
            return False, "this road is already travelled"
    if "min_year" in req and g.year < req["min_year"]:
        return False, f"only after {req['min_year']}"
    if "max_year" in req and g.year > req["max_year"]:
        return False, f"only until {req['max_year']}"
    if "hc" in req and g.hard_currency < req["hc"]:
        return False, f"needs valas reserve ≥ {req['hc']}"
    if "hc_max" in req and g.hard_currency > req["hc_max"]:
        return False, f"only while valas reserve ≤ {req['hc_max']}"
    for f, minimum in (req.get("court_min") or {}).items():
        if g.court.get(f, 50) < minimum:
            return False, f"needs {f.replace('_', ' ')} warming"
    for f, maximum in (req.get("court_max") or {}).items():
        if g.court.get(f, 50) > maximum:
            return False, f"needs {f.replace('_', ' ')} enraged"
    return True, ""


# ---------------------------------------------------------------
# Effect application
# ---------------------------------------------------------------
def apply_ops(g: Kremlin, ops: dict | None) -> list[str]:
    """Apply an ops dict. Returns human-readable change notes."""
    if not ops:
        return []
    changes: list[str] = []
    for stat, val in (ops.get("stats") or {}).items():
        if stat not in STATS:
            raise ValueError(f"content bug: unknown stat '{stat}'")
        if isinstance(val, tuple):
            val = g.rng.randint(val[0], val[1])
        g.stats[stat] = clamp(g.stats[stat] + val)
        changes.append(f"{stat} {val:+d}")
    hc = ops.get("hc")
    if hc is not None:
        if isinstance(hc, tuple):
            hc = g.rng.randint(hc[0], hc[1])
        g.hard_currency = max(0, min(100, g.hard_currency + int(hc)))
        changes.append(f"VALAS {int(hc):+d}")
    court = ops.get("court") or {}
    for f, val in court.items():
        if f not in FACTIONS:
            raise ValueError(f"content bug: unknown faction '{f}'")
        g.court[f] = max(0, min(100, g.court[f] + int(val)))
        changes.append(f"COURT {f} {int(val):+d}")
    path = ops.get("path")
    if path:
        from .content.forks import PATH_FLAGS
        for old in PATH_FLAGS:
            if old != path:
                g.flags.discard(old)
        g.path = path
        if path not in g.flags:
            g.flags.add(path)
            changes.append(f"⚑ line: {path}")
    for f in _as_list(ops.get("flag_add")):
        if f not in g.flags:
            g.flags.add(f)
            changes.append(f"⚑ new: {f}")
    for f in _as_list(ops.get("flag_rm")):
        if f in g.flags:
            g.flags.discard(f)
            changes.append(f"⚑ revoked: {f}")
    for delay, event_id in ops.get("queue", []):
        g.pending.append((g.year + int(delay), event_id))
        changes.append(f"⧗ response expected in {int(delay)} year(s)")
    for sp in _as_list(ops.get("special")):
        fn = SPECIALS.get(sp)
        if fn is None:
            raise ValueError(f"content bug: unknown special '{sp}'")
        fn(g)
    return changes


def consume_rest(g: Kremlin, ops_dict: dict | None) -> tuple[dict, bool]:
    """If the player spent an evening at the dacha, next event's damage halves."""
    if "rested" not in g.flags or not ops_dict or "stats" not in ops_dict:
        return ops_dict, False
    g.flags.remove("rested")
    softened = dict(ops_dict)
    softened["stats"] = {
        k: (int(v / 2) if (not isinstance(v, tuple) and v < 0) else v)
        for k, v in softened["stats"].items()
    }
    return softened, True


# ---------------------------------------------------------------
# Custom special handlers (rare, high-impact logic)
# ---------------------------------------------------------------
def coup_sum(g: Kremlin) -> int:
    """The August Coup's yardstick, exposed so the UI can show it."""
    return g.stats["MILITARY"] + g.stats["ORDER"]


COUP_SAFE = 110      # at or above: the Committee hesitates
COUP_SCARRED = 95    # at or above: the Union survives, wounded and watched


@_special("coup_defy")
def _coup_defy(g: Kremlin) -> None:
    total = coup_sum(g)
    if total >= COUP_SAFE:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 6)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 5)
        g.flags.add("survived_coup")
        print()
        print(ui.paint("  ★ The Committee hesitates. Radio waves carry your voice for three days;", ui.C.BG))
        print(ui.paint("    drunken sailors defect; armoured convoys park and drink tea. THE UNION HOLDS.", ui.C.BG))
    elif total >= COUP_SCARRED:
        g.stats["ORDER"] = clamp(g.stats["ORDER"] - 12)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 10)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] - 6)
        for f in FACTIONS:
            g.court[f] = max(0, g.court[f] - 5)
        g.flags.add("coup_scarred")
        g.flags.add("survived_coup")
        print()
        print(ui.paint("  ! The Committee blinks — but only after the tanks have parked.", ui.C.Y))
        print(ui.paint("    You keep the office, the Committee keeps the keys, and every", ui.C.Y))
        print(ui.paint("    ministry knows the arithmetic was close. The Union survives, watched.", ui.C.Y))
    else:
        g.stats["FAITH"] = 0
        g.stats["ORDER"] = 0
        g.death_reason = (f"The August Coup succeeded ({total} against a yardstick of "
                          f"{COUP_SAFE}). Your voice was one of many, then none.")


@_special("coup_join")
def _coup_join(g: Kremlin) -> None:
    g.putschist = True
    g.stats["ORDER"] = clamp(g.stats["ORDER"] + 8)
    g.stats["FAITH"] = clamp(g.stats["FAITH"] - 12)
    g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] - 12)


@_special("coup_absent")
def _coup_absent(g: Kremlin) -> None:
    g.stats["ORDER"] = clamp(g.stats["ORDER"] - 4)
    g.stats["FAITH"] = clamp(g.stats["FAITH"] - 4)
    g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] - 3)


# ─────── v4: the velvet palace coup (queued when a faction despairs) ───────

@_special("coup_fight")
def _coup_fight(g: Kremlin) -> None:
    """Face the plenum in your own conference room. Brinkmanship vs arithmetic."""
    strong = g.stats["ORDER"] + g.stats["MILITARY"]
    if strong >= 115 or g.court["old_guard"] >= 30:
        g.stats["ORDER"] = clamp(g.stats["ORDER"] + 3)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 4)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 2)
        g.flags.add("survived_plot")
        g.court["old_guard"] = max(g.court["old_guard"], 45)
        g.court["reformers"] = max(g.court["reformers"], 30)
        g.court["military"] = max(g.court["military"], 40)
        _court_clamp(g)
        print()
        print(ui.paint("  ★ You walk into your own conference room and simply sit down.", ui.C.BG))
        print(ui.paint("    The room re-decides, in eleven minutes, that this was always", ui.C.BG))
        print(ui.paint("    the plan. The apparatus obeys. You remain General Secretary.", ui.C.BG))
    else:
        g.deposed = True
        g.death_reason = ("The plenum voted by a show of hands, then a silence. "
                          "Your photograph becomes archival material the same week.")
        print()
        print(ui.paint("  ✗ Twelve hands rise before you finish the sentence. In the corridor,", ui.C.BM))
        print(ui.paint("    two very polite gentlemen are already carrying a briefcase for your papers.", ui.C.BM))


@_special("coup_people")
def _coup_people(g: Kremlin) -> None:
    """Appeal over their heads — to the miners, the youth, the kitchens."""
    if g.stats["FAITH"] >= 55:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 5)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 3)
        g.flags.add("survived_plot")
        g.court["reformers"] = max(g.court["reformers"], 55)
        g.court["old_guard"] = max(g.court["old_guard"], 35)
        g.court["military"] = max(g.court["military"], 35)
        _court_clamp(g)
        print()
        print(ui.paint("  ★ You appeal directly to the miners and the Party youth. By morning,", ui.C.BG))
        print(ui.paint("    the plenum members find their homes ringed by telephoned friendship.", ui.C.BG))
    else:
        g.deposed = True
        g.death_reason = ("Nobody rallied. The kitchens stayed quiet, the miners dig, "
                          "and your signature stops being printed on anything important.")
        print()
        print(ui.paint("  ✗ The appeal is broadcast, answered by silence and one weather report.", ui.C.BM))
