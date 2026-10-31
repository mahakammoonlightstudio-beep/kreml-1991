"""Record a full scripted playthrough of КРЕМЛЬ 1991 to a video.

How it works:
  1. An adaptive "autopilot" bot answers every menu via builtins.input —
     it pursues the market path (Kosygin -> coops -> price reform -> treaty)
     and otherwise maximises gauges weighted by how low they are.
  2. The whole terminal output (ANSI colours ON) is captured into a log,
     then split into frames at every year marker (☭ YYYY ☭).
  3. Each frame is rendered to PNG with a CRT-ish palette (Consolas for the
     grid, Segoe UI Symbol for ☭ ★ ⚑ ✖ ✔ ❯ ⧗), then muxed to MP4 via ffmpeg.

Usage:
    python tools\record_gameplay.py            # record + render video
    python tools\record_gameplay.py --dry      # just run the bot, print the outcome
"""
from __future__ import annotations

import builtins
import io
import math
import os
import pathlib
import re
import sys
import shutil
from collections import deque

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from kreml import ui, engine, ops, persistence
from kreml.state import STATS
from kreml.content import events as EV
from kreml.content import directives as DR
from kreml.content import actions as AC
from kreml.content import capital as CAP
from kreml.content import orders as OR

# ─────────────────────────────────────────────────────────────────────
# The autopilot bot
# ─────────────────────────────────────────────────────────────────────
BOT_NAME = "Nikolai Vetrov"

FLAG_BONUS = {
    # the market path is the video's narrative spine
    "kosygin_pilot": 10, "kosygin_full": 16, "coops": 14, "price_done": 14,
    "sez": 10, "free_port": 8, "perestroika": 9, "treaty_signed": 24,
    "glasnost_early": 6, "china_thaw": 5, "helsinki": 3, "micro": 6,
    "pipelines": 3, "reformer": 2, "stability_law": 2, "siberian": 2,
    "afghan_withdraw": 10, "mr_admitted": 2,
    # things a sane general secretary avoids
    "at_war": -18, "afghan_deep": -14, "chernobyl_hidden": -16,
    "purge": -12, "brink": -22, "dry_decade": -8, "atomic_ultimatum": -14,
}

FLAG_RM_BONUS = {"at_war": 22, "coops": 0, "brink": 20}

LABEL_BONUS = {
    "Withdraw and cut losses": 14,
    "Wash your hands of Kabul": 20,
    "Admit the disaster immediately": 16,
    "Accept Western aid openly": 6,
    "Support pilot reforms": 18,
    "Sign the full Kosygin package": 18,
    "Order non-intervention, publicly": 8,
}

LABEL_BOOST_DIRECTIVES = {
    "UNLEASH Kosygin 2.0 market reforms": 30,
    "Legalize private cooperatives": 26,
    "Price reform: the rouble retrains": 30,
    "Special economic zones (Nakhodka model)": 24,
    "Sign the Renewed Union Treaty": 34,
    "Regenerate the nomenklatura": 12,
    "Relax censorship (soft glasnost)": 4,
}

SPECIAL_BONUS = {"coup_defy": 60, "coup_join": -60, "coup_absent": -2}


def _flag_bonus(g, f: str) -> float:
    if f == "rested":
        return 6.0 if "rested" not in g.flags else 0.0
    return FLAG_BONUS.get(f, 1.0)


def _flags(oplist) -> list:
    if oplist is None:
        return []
    return oplist if isinstance(oplist, str) else list(oplist)


def _ops_of(item) -> dict:
    """Options are `Option` objects; v6 capital moves are plain dicts."""
    if isinstance(item, dict):
        return item.get("ops") or {}
    return getattr(item, "ops", None) or {}


def _label_of(item) -> str:
    if isinstance(item, dict):
        return item.get("label", "") or ""
    return getattr(item, "label", "") or ""


def score_option(g, item) -> float:
    """Weighted score: stat deltas weighted by how low the gauge is, plus flags."""
    op = _ops_of(item)
    sc = 0.0
    for s, dv in (op.get("stats") or {}).items():
        if dv is None:
            continue
        if isinstance(dv, tuple):                      # random roll → expectation
            dv = (dv[0] + dv[1]) / 2.0
        w = 1.0 + max(0.0, (55.0 - g.stats[s])) / 25.0  # deficits weigh more
        sc += dv * w
    for f, dv in (op.get("court") or {}).items():        # v6: a court costs too
        sc += dv * (1.0 + max(0.0, 50.0 - g.court.get(f, 50)) / 25.0)
    for f in _flags(op.get("flag_add")):
        sc += _flag_bonus(g, f)
    for f in _flags(op.get("flag_rm")):
        sc += FLAG_RM_BONUS.get(f, 0)
    for sp in _flags(op.get("special")):
        sc += SPECIAL_BONUS.get(sp, 0)
    cost = item.get("cost", 0) if isinstance(item, dict) else 0
    if cost:                                          # capital: value per point
        sc -= cost * 0.9
    label = _label_of(item)
    sc += LABEL_BONUS.get(label, 0) * 1.0
    sc += LABEL_BOOST_DIRECTIVES.get(label, 0)
    # the coup: only defy if the tanks can be bribed back
    if label == "Defy the coup from the radio":
        sc += 60 if (g.stats["MILITARY"] + g.stats["ORDER"] >= 110) else -70
    if label == "Remain carefully absent":
        sc += 4
    if label == "Back the Emergency Committee":
        sc += -50
    # keep faith alive with consumer goods when it's low
    if g.stats["FAITH"] < 45 and label in ("Consumer goods & light industry",
                                           "Agriculture reform", "Culture, sport & education"):
        sc += 10
    if g.stats["MILITARY"] < 45 and label in ("Military buildup", "Espionage & intelligence ops"):
        sc += 8
    return sc


def argmax(scores: list) -> int:
    best, best_i = scores[0], 0
    for i, s in enumerate(scores[1:], 1):
        if s > best:
            best, best_i = s, i
    return best_i


def _lifeline_pick(g) -> int:
    """Reserve index by lowest gauge: gold→ECO, sweep→ORDER, payout→FAITH, missile→MIL."""
    order = [("ECONOMY", 0), ("ORDER", 1), ("FAITH", 2), ("MILITARY", 3)]
    lowest = min(order, key=lambda t: g.stats[t[0]])[1]
    return lowest


# ─────────────────────────────────────────────────────────────────────
# Recording harness
# ─────────────────────────────────────────────────────────────────────
CUR_G: dict = {}
# Research switches: `tools/balance.py --no-capital / --no-doctrine` turns one
# subsystem off, so the survival it buys can be measured instead of assumed.
USE_CAPITAL = True
USE_DOCTRINE = True
EVENT_QUEUE = deque()
OUTCOME: dict = {"survived": False, "collapsed": False, "retired": False}


def _patch_engine() -> None:
    _orig_year = engine.year_step

    def year_wrap(g):
        CUR_G["g"] = g
        return _orig_year(g)
    engine.year_step = year_wrap

    _orig_collect = engine.collect_events

    def collect_wrap(g):
        out = _orig_collect(g)
        EVENT_QUEUE.clear()
        EVENT_QUEUE.extend(out)
        return out
    engine.collect_events = collect_wrap

    _mod = __import__("kreml.content.endings", fromlist=["x"])
    _orig_end_surv = _mod.ending_union_survives
    _orig_end_coll = _mod.ending_collapse
    _orig_end_red = _mod.ending_red_millennium

    def surv_wrap(g):
        OUTCOME["survived"] = True
        return _orig_end_surv(g)

    def red_wrap(g):
        OUTCOME["survived"] = True      # 2001 counts: the bot did not collapse
        return _orig_end_red(g)

    def coll_wrap(g):
        OUTCOME["collapsed"] = True
        return _orig_end_coll(g)

    END = _mod
    END.ending_union_survives = surv_wrap
    END.ending_collapse = coll_wrap
    END.ending_red_millennium = red_wrap
    # engine.run resolves END via its own import binding — rebind it there too
    engine.END = END


def _avail_options(g, ev) -> list:
    avail = [o for o in ev.options if ops.check_requires(g, o.requires)[0]]
    if not avail:
        avail = [ev.options[0]]
    return avail


def bot_input(prompt: str = "") -> str:
    p = prompt
    if "name for the history books" in p:
        return BOT_NAME
    if "How harsh" in p:
        return "2"                       # BALANCED (v5: 5 modes, 2 = medium)
    if "Which timeline" in p:
        return "1"                       # rails of history
    if "Your mandate" in p:
        return "3"                       # dark-horse reformer
    if "Resume" in p:
        return "0"
    if "Continue into the new era" in p:
        return "1"                      # take the Red Millennium when offered
    if "proceed" in p or "[Enter] " in p:
        g = CUR_G.get("g")
        if g is not None:
            if USE_DOCTRINE and getattr(g, "order", None) is None:
                return "o"               # v6: a doctrine, once
            if (USE_CAPITAL and getattr(g, "capital_year", 0) != g.year
                    and getattr(g, "influence", 0) >= 8
                    and min(g.court.values()) <= 32 and CAP.available(g)):
                return "i"               # v6: repair the angriest faction
        return ""                        # year boundary → go
    g = CUR_G.get("g")
    if g is None:
        return ""
    if "Spend capital:" in p:
        if not USE_CAPITAL:
            return "0"
        moves = CAP.available(g)
        if not moves:
            return "0"
        return str(1 + argmax([score_option(g, m) for m in moves]))
    if "Doctrine:" in p:
        if not USE_DOCTRINE:
            return "0"
        best, best_i = -1e9, 0
        for i, order in enumerate(OR.ORDERS, 1):
            sc = 0.0
            for stat, dv in (order.get("drift") or {}).items():
                sc += dv * (1.0 + max(0.0, (55.0 - g.stats[stat])) / 25.0)
            for f, dv in (order.get("court") or {}).items():
                sc += dv * (1.0 + max(0.0, (50.0 - g.court.get(f, 50))) / 25.0)
            sc += (order.get("yearly") or {}).get("influence", 0) * 1.5
            if sc > best:
                best, best_i = sc, i
        return str(best_i)
    if "Focus on:" in p:
        acts = AC.available_actions(g)
        return str(1 + argmax([score_option(g, a) for a in acts]))
    if "Directive of the year:" in p:
        groups = DR.available_directives(g)
        flat = [d for _, ds in groups for d in ds]
        return str(1 + argmax([score_option(g, d) for d in flat]))
    if "Reserve decision:" in p:
        return str(1 + _lifeline_pick(g))
    if "Your decision:" in p:
        ev = EVENT_QUEUE[0]
        avail = _avail_options(g, ev)
        EVENT_QUEUE.popleft()
        return str(1 + argmax([score_option(g, o) for o in avail]))
    return ""


def run_bot(seed: int, dry: bool = False) -> str:
    """Runs one full playthrough. Returns the captured log (ANSI colours ON)."""
    for k in OUTCOME:
        OUTCOME[k] = False
    CUR_G.clear()
    EVENT_QUEUE.clear()

    ui._use_colour = True          # keep ANSI codes in the captured log
    old_anim = ui.ANIM
    ui.ANIM = False                # no \r frames or sleeps in a captured log
    _patch_engine()
    builtins.input = bot_input

    log = io.StringIO()
    from contextlib import redirect_stdout
    try:
        with redirect_stdout(log):
            engine.run(seed)
    finally:
        ui.ANIM = old_anim

    text = log.getvalue()
    if dry:
        outcome = ("SURVIVED" if OUTCOME["survived"]
                   else "COLLAPSED" if OUTCOME["collapsed"] else "ended")
        m = re.search(r"Legacy score: (\d+)", text)
        print(f"[dry] outcome = {outcome}, score = {m.group(1) if m else '?'}")
        g = CUR_G.get("g")
        if g is not None:
            print("[dry] gauges:", {s: g.stats[s] for s in STATS})
            print("[dry] flags :", sorted(g.flags))
    return text


def main() -> int:
    argv = sys.argv[1:]
    dry = "--dry" in argv
    seed = 7
    if "--seed" in argv:
        idx = argv.index("--seed")
        seed = int(argv[idx + 1])
    text = run_bot(seed, dry=dry)
    if dry:
        return 0
    if not OUTCOME["survived"]:
        print("Bot collapsed — not worth recording. Tweak strategy or seed.")
        return 1

    from render_video import render_video     # the renderer lives beside this file
    render_video(text, seed)
    return 0


if __name__ == "__main__":
    hall = os.path.join(pathlib.Path(__file__).resolve().parent.parent,
                        "hall_of_fame.txt")
    # a recording session must not eat the player's record book
    backup = pathlib.Path(hall).read_bytes() if os.path.exists(hall) else None
    try:
        raise SystemExit(main())
    finally:
        try:
            os.remove(persistence.SAVE_FILE)
        except OSError:
            pass
        if backup is not None:
            pathlib.Path(hall).write_bytes(backup)
