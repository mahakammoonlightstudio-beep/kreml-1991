"""Engine: walks through years, menus, events, and endings.

Flow of ONE year:
  briefing → (crisis lifeline offer?) → stats → personal focus → directive →
  event(s) (queued, congress, scripted, or random) → drift → death check

The engine contains no content and no rendering details: it only wires
`content/*` DATA through `ops.py` and shows it via `ui.py`.
"""
from __future__ import annotations

from . import ui, ops
from . import dossier, persistence
from .state import Kremlin, STATS, clamp
from .content.modes import MODES, MODE_ORDER, normalize
from .content import world as WORLD
from .content import events as EV
from .content import directives as DR
from .content import actions as AC
from .content import history as HIST
from .content import press as PR
from .content import endings as END
from .content.timelines import TIMELINES, TIMELINE_ORDER
from .content.forks import FORKS, PATH_DRIFT

# ---------------------------------------------------------------
# Introduction
# ---------------------------------------------------------------
MANDATES = (
    ("Appointed by the Old Guard",
     "Order +6, Faith −4, Economy +2. Stalinesque paperwork welcomes you.",
     {"stats": {"ORDER": 6, "FAITH": -4, "ECONOMY": 2}, "flag_add": "old_guard",
      "court": {"old_guard": 12, "reformers": -6}}),
    ("Balanced committee choice",
     "A quiet vote. The dacha stays as it is.",
     {"court": {"old_guard": 2, "reformers": 2, "military": 2}}),
    ("Dark-horse reformer",
     "Faith +6, Prestige +4, Order −8. The Old Guard sharpens its teeth.",
     {"stats": {"FAITH": 6, "PRESTIGE": 4, "ORDER": -8}, "flag_add": "reformer",
      "court": {"reformers": 8, "old_guard": -12}}),
)


def introduction(g: Kremlin, mode: str | None = None,
                 timeline: str | None = None) -> dict | None:
    """Pick difficulty, timeline, name and (for 1964) mandate.

    Returns a setup dict, or None if the player declined. The engine builds
    the actual Kremlin from this dict, so the chosen timeline is applied once.
    """
    ui.banner()
    END.show_hall_top()
    print(ui.paint("  Before the year begins, the Politburo asks a few questions.", ui.C.W))
    # ── difficulty (skipped if set from the command line) ──────────
    cli_mode = normalize(mode) if mode else None
    if mode and mode not in MODES and normalize(mode) != mode:
        cli_mode = normalize(mode)
    if cli_mode is None:
        print()
        mdata = [MODES[m] for m in MODE_ORDER]
        for i, m in enumerate(mdata, 1):
            reserve_note = f'(reserves x{m["lifelines"]})'
            print(f"   {ui.paint(str(i), ui.C.BB)}. {ui.paint(m['label'], ui.C.W)}"
                  f"  {ui.paint(reserve_note, ui.C.DIM)}")
            print(f"      {ui.paint(m['desc'], ui.C.DIM)}")
        pick = ui.ask_choice("  ❯ How harsh should history be? ", len(mdata), g.rng)
        if pick == 0:
            return None
        cli_mode = MODE_ORDER[pick - 1]
    m = MODES[cli_mode]
    print()
    print(ui.paint(f"  ✦ Difficulty set: {m['label']} — {m['lifelines']} crisis reserves.", ui.C.Y))

    # ── timeline (v5) ──────────────────────────────────────────────
    tl_id = timeline if timeline in TIMELINES else None
    if tl_id is None:
        print()
        for i, tid in enumerate(TIMELINE_ORDER, 1):
            tl = TIMELINES[tid]
            span = f"{tl.year}–{tl.end_year}"
            print(f"   {ui.paint(str(i), ui.C.BB)}. {ui.paint(tl.label, ui.C.W)}"
                  f"  {ui.paint('(' + span + ')', ui.C.DIM)}")
            print(f"      {ui.paint(tl.desc, ui.C.DIM)}")
        pick = ui.ask_choice("  ❯ Which timeline? ", len(TIMELINE_ORDER), g.rng)
        if pick == 0:
            return None
        tl_id = TIMELINE_ORDER[pick - 1]
    tl = TIMELINES[tl_id]
    print()
    print(ui.paint(f"  ✦ Timeline: {tl.label} — {tl.year} to {tl.end_year}.", ui.C.Y))
    print()
    try:
        name = input("  Your name for the history books: ").strip()
    except (EOFError, KeyboardInterrupt):
        name = ""
    name = name or "Comrade Secretary"

    # ── mandate (only where the 1964 appointment still happens) ────
    mandate = 0
    if tl.mandate:
        print()
        for i, (title, desc, _ops) in enumerate(MANDATES, 1):
            print(f"   {ui.paint(str(i), ui.C.BB)}. {ui.paint(title, ui.C.W)}")
            print(f"      {ui.paint(desc, ui.C.DIM)}")
        pick = ui.ask_choice("  ❯ Your mandate: ", len(MANDATES), g.rng)
        if pick == 0:
            return None
        mandate = pick

    print()
    ui.slow(ui.paint(f"  ☭ Welcome, {name}. The Union is yours. Try not to lose it.", ui.C.BG))
    print()
    ui.slow(ui.paint("  EVERY YEAR: a personal focus, a public directive, and the year's", ui.C.W))
    ui.slow(ui.paint("  crisis event(s). The command bar between years: s = save game,", ui.C.W))
    ui.slow(ui.paint("  l = load, d = dossier (timeline & road map), q = retire.", ui.C.W))
    ui.slow(ui.paint("  Watch TWO extra skies: the valas reserve (the world market pays/hauls)", ui.C.W))
    ui.slow(ui.paint("  and the Politburo moods (Old Guard · Reformers · Army). A faction in", ui.C.W))
    ui.slow(ui.paint("  despair will book the velvet meeting room. Keep all gauges alive.", ui.C.W))
    ui.slow(ui.paint("  Repeating one lever every year goes STALE: vary the plan, or it pays less.", ui.C.DIM))
    print()
    return {"mode": cli_mode, "timeline": tl_id, "name": name, "mandate": mandate}


# ---------------------------------------------------------------
# Event drawing
# ---------------------------------------------------------------
def _eligible(g: Kremlin, ev) -> bool:
    if getattr(ev, "alt", False) and MODES[g.mode]["rail"]:
        return False                       # historical rails: no alt history
    if ev.once and ev.id in g.used_events:
        return False
    ok, _ = ops.check_requires(g, ev.requires)
    return ok


def _main_events(g: Kremlin) -> list:
    """All eligible scripted historical events for this year; otherwise one random pick."""
    out = []
    for event_id in EV.SCRIPTED.get(g.year, ()):
        if _eligible(g, EV.EVENTS[event_id]):
            g.used_events.add(event_id)
            out.append(EV.EVENTS[event_id])
    if out:
        return out
    pool = [EV.EVENTS[eid] for eid in EV.RANDOM_POOLS[g.era] if _eligible(g, EV.EVENTS[eid])]
    if not pool:
        return []
    chosen = g.rng.choice(pool)
    g.used_events.add(chosen.id)
    return [chosen]


def collect_events(g: Kremlin) -> list:
    """Events for this year, in order:
         congress (if due) → main scripted/random event(s) → up to 2 queued delayed events.
    """
    out = []
    congregation = EV.CONGRESS_YEARS.get(g.year)
    if congregation is not None and _eligible(g, EV.EVENTS[congregation]):
        g.used_events.add(congregation)
        out.append(EV.EVENTS[congregation])
    out.extend(_main_events(g))
    # ── v5: divergence fork, once per game, after the historical events ──
    fork_id = FORKS.get(g.year)
    if fork_id and not MODES[g.mode]["rail"]:
        fork = EV.EVENTS.get(fork_id)
        if fork is not None and _eligible(g, fork):
            g.used_events.add(fork.id)
            out.append(fork)
    for _ in range(2):
        due = sorted(e for e in g.pending if e[0] <= g.year)
        if not due:
            break
        _, event_id = due[0]
        g.pending.remove(due[0])
        g.used_events.add(event_id)
        out.append(EV.EVENTS[event_id])
    return out


# ---------------------------------------------------------------
# Turn pieces
# ---------------------------------------------------------------
def briefing(g: Kremlin) -> None:
    print()
    ui.year_banner(g.year)
    line = HIST.HISTORY.get(g.year)
    if line:
        ui.slow(ui.paint("  " + line, ui.C.W))
    note = HIST.WORLD_NOTES.get(g.year)
    if note:
        print(ui.paint("  ┌─ REAL LIFE ──────────────────────────────────────────", ui.C.DIM))
        print(ui.paint("  │ 🌍 " + note[0], ui.C.W))
        print(ui.paint("  │ 🏠 " + note[1], ui.C.DIM))
        print(ui.paint("  └──────────────────────────────────────────────────────", ui.C.DIM))
    _press_line(g)


def _press_line(g: Kremlin) -> None:
    """One Western headline reacting to the current state; conditional ones fire once."""
    candidates = []
    for p in PR.PRESS:
        ok, _ = ops.check_requires(g, p["requires"])
        if not ok:
            continue
        if not p.get("fallback") and p["id"] in g.shown_press:
            continue
        candidates.append(p)
    if not candidates:
        return
    best_w = max(p.get("w", 1) for p in candidates)
    pool = [p for p in candidates if p.get("w", 1) >= best_w - 1]
    headline = g.rng.choice(pool)
    if not headline.get("fallback"):
        g.shown_press.add(headline["id"])
    print()
    print(ui.paint(f"  ┌── FOREIGN PRESS ──", ui.C.DIM))
    print(ui.paint(f"  🗞 «{headline['organ']}» — {headline['headline']}", ui.C.Y))
    if headline.get("sub"):
        print(ui.paint(f"    {headline['sub']}", ui.C.W))
    print(ui.paint("  └───", ui.C.DIM))


def maybe_lifeline(g: Kremlin) -> bool:
    """Offers one crisis reserve if a gauge is critical. Returns False on retire."""
    if g.lifelines <= 0:
        return True
    low = [s for s in STATS if g.stats[s] <= 35]
    if not low:
        return True
    print()
    print(ui.paint(f"  ⚠ A gauge met the red line ({', '.join(low)}).", ui.C.BM))
    print(ui.paint(f"  The Politburo still holds {g.lifelines} reserve(s). Spend one?", ui.C.W))
    for i, opt in enumerate(DR.LIFELINES, 1):
        print(f"   {ui.paint(str(i), ui.C.BB)}. {ui.paint(opt.label, ui.C.W)}")
        print(f"       {ui.paint(opt.outcomes, ui.C.DIM)}")
    print(f"   {ui.paint(' 0', ui.C.DIM)}. Keep the reserve")
    choice = ui.ask_choice("  ❯ Reserve decision: ", len(DR.LIFELINES), g.rng)
    if choice == 0:
        return True
    opt = DR.LIFELINES[choice - 1]
    before, flags0 = dict(g.stats), set(g.flags)
    ops.apply_ops(g, opt.ops)
    g.lifelines -= 1
    ui.show_changes(before, g.stats, flags0, g.flags)
    g.ledger.append((g.year, "lifeline: " + opt.label))
    print(ui.paint(f"  ▸ Reserve spent. {g.lifelines} left.", ui.C.G))
    return True


def run_action(g: Kremlin) -> bool:
    """Personal focus (small lever). Returns False on retire."""
    focus = AC.available_actions(g)
    if not focus:
        return True
    print(ui.paint("  ── PERSONAL FOCUS (a small matter of one evening) ──", ui.C.BB))
    ui.list_options([(a.label, a.desc) for a in focus])
    pick = ui.ask_choice("  ❯ Focus on: ", len(focus), g.rng)
    if pick == 0:
        return False
    act = focus[pick - 1]
    uses = g.focus_uses.get(act.id, 0)
    mult = ops.fatigue_multiplier(uses)
    before, flags0 = dict(g.stats), set(g.flags)
    ops.apply_ops(g, ops.scale_ops(act.ops, mult))
    g.focus_uses[act.id] = uses + 1
    if act.once:
        g.used_focus.add(act.id)
    g.ledger.append((g.year, "focus: " + act.label))
    ui.show_changes(before, g.stats, flags0, g.flags)
    return True


def run_directive(g: Kremlin) -> bool:
    """Public yearly campaign. Returns False on retire."""
    groups = DR.available_directives(g)
    flat = [d for _, ds in groups for d in ds]
    if not flat:
        print(ui.paint("  ✗ No directives on the table this year.", ui.C.R))
        return True
    print(ui.paint("  ── YEARLY DIRECTIVE ──", ui.C.BB))
    n = 0
    for name, ds in groups:
        print(ui.paint(f"   {name}", ui.C.MG))
        for d in ds:
            n += 1
            print(f"    {ui.paint(f'{n:>2}', ui.C.BB)}. {ui.paint(d.label, ui.C.W)}"
                  f"  {ui.paint('· ' + d.desc, ui.C.DIM)}")
    print(ui.paint("    ( 0. Retire / resign )", ui.C.DIM))
    pick = ui.ask_choice("  ❯ Directive of the year: ", len(flat), g.rng)
    if pick == 0:
        return False
    d = flat[pick - 1]
    # v5: a repeated plan goes stale — the gains shrink, the costs do not
    uses = g.directive_uses.get(d.id, 0)
    mult = ops.fatigue_multiplier(uses)
    before, flags0 = dict(g.stats), set(g.flags)
    ops.apply_ops(g, ops.scale_ops(d.ops, mult))
    g.directive_uses[d.id] = uses + 1
    if d.once:
        g.used_directives.add(d.id)
    # Small Gosplan wobble on heavy plans (unpredictable weather & mood)
    g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] + g.rng.randint(-1, 1))
    ui.show_changes(before, g.stats, flags0, g.flags)
    g.ledger.append((g.year, "directive: " + d.label))
    if mult < 1.0:
        ui.slow(ui.paint(f"  ▸ Directive issued: {d.label}", ui.C.G))
        print(ui.paint(f"  ▸ The plan is stale (used {uses + 1}x): gains at "
                       f"{int(mult * 100)}%, costs unchanged.", ui.C.DIM))
    else:
        ui.slow(ui.paint(f"  ▸ Directive issued: {d.label}", ui.C.G))
    return True


# v5: the two decisions that used to kill you without saying why.
REQUIREMENT_HINTS: dict[str, dict] = {
    "august_coup": {
        "Defy the coup from the radio":
            lambda g: (f"needs MILITARY+ORDER >= {ops.COUP_SAFE} "
                       f"(yours: {ops.coup_sum(g)})"),
    },
    "palace_coup": {
        "Walk in and face the plenum":
            lambda g: (f"needs ORDER+MILITARY >= 115 or Old Guard >= 30 "
                       f"(yours: {g.stats['ORDER'] + g.stats['MILITARY']}"
                       f"/{g.court['old_guard']})"),
        "Appeal over their heads":
            lambda g: f"needs FAITH >= 55 (yours: {g.stats['FAITH']})",
    },
}


def run_event(g: Kremlin, ev) -> str:
    """Runs one event; returns 'quit' if the player chose to retire"""
    avail = []
    for o in ev.options:
        ok, _ = ops.check_requires(g, o.requires)
        if ok:
            avail.append(o)
    if not avail:
        avail = [ev.options[0]]
    ui.event_header(ev.title, ev.text)
    hints = REQUIREMENT_HINTS.get(ev.id, {})
    rows = []
    for o in avail:
        hint = hints.get(o.label)
        desc = o.outcomes
        if hint is not None:
            desc = f"{desc}  ·  {hint(g)}" if desc else hint(g)
        rows.append((o.label, desc))
    ui.list_options(rows)
    pick = ui.ask_choice("  ❯ Your decision: ", len(avail), g.rng)
    if pick == 0:
        return "quit"
    before, flags0 = dict(g.stats), set(g.flags)
    chosen = avail[pick - 1]
    chosen_ops, rested = ops.consume_rest(g, chosen.ops)
    notes = ops.apply_ops(g, chosen_ops)
    g.ledger.append((g.year, f"event: {ev.title} → {chosen.label}"))
    if rested:
        print(ui.paint("   (your dacha rest softened the impact)", ui.C.DIM))
    ui.show_changes(before, g.stats, flags0, g.flags)
    return "ok"


def apply_drift(g: Kremlin) -> None:
    """Yearly erosion (difficulty-scaled) + standing bonuses and attrition."""
    base = MODES[g.mode]["drift"][g.era]
    for s, v in base.items():
        g.stats[s] = clamp(g.stats[s] + v)
    # ── v5: the path chosen at a fork nudges the weather ──────────
    if g.path:
        for s, v in PATH_DRIFT.get(g.path, {}).items():
            g.stats[s] = clamp(g.stats[s] + v)
    # Superpower health --------------------------------------------
    if g.stats["MILITARY"] >= 80 and g.stats["ECONOMY"] >= 60:
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 1)
    if g.stats["ECONOMY"] >= 65:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 1)
    # Rule tendencies ----------------------------------------------
    if "old_guard" in g.flags:
        g.stats["ORDER"] = clamp(g.stats["ORDER"] + 1)
    if "perestroika" in g.flags and g.stats["ORDER"] >= 40:
        g.stats["FAITH"] = clamp(g.stats["FAITH"] + 1)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 1)
    # War attrition -------------------------------------------------
    if "at_war" in g.flags:
        g.stats["MILITARY"] = clamp(g.stats["MILITARY"] - 2)
        g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] - 1)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 1)


# ---------------------------------------------------------------
# v4: the world market & the court weather (applied after drift)
# ---------------------------------------------------------------
_FACTION_TITLES = {"old_guard": "Old Guard", "reformers": "Reformers",
                   "military": "Army"}


def apply_systems(g: Kremlin) -> None:
    """Yearly valas & faction bookkeeping. Runs after apply_drift.

    1. WORLD MARKET — the oil index sets export income; imports and debt
       service always bill. The Union's reserve resonates on the gauges.
    2. COURT        — faction moods soak up era drift plus a little noise;
       blessings from a loving faction, cost from a despairing one, and a
       queued velvet coup when a faction bottoms out.
    """
    # ── world market ──────────────────────────────────────────────
    price = WORLD.oil_price(g.year)
    drain = 3                                                # imports, storage, upkeep
    if "debt_trap" in g.flags:
        drain += 3                                           # interest on silent loans
    bonus = WORLD.oil_bonus(g.year)                          # 0..7 by price band
    if price >= 45 and "pipelines" in g.flags:
        bonus += 2                                           # more barrels, more valves
    if price <= 30:
        drain += 7                                           # the glut is expensive
    g.hard_currency = max(0, min(100, g.hard_currency + bonus - drain))
    if g.hard_currency <= 10:
        g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] - 3)
        g.stats["FAITH"] = clamp(g.stats["FAITH"] - 1)
        print(ui.paint("  (the valas reserve is an echo — imports grow speculative)", ui.C.DIM))
    elif g.hard_currency >= 75:
        g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] + 2)
        g.stats["PRESTIGE"] = clamp(g.stats["PRESTIGE"] + 1)

    # ── court weather ─────────────────────────────────────────────
    drift = WORLD.COURT_DRIFT.get(g.era, {})
    for f in ("old_guard", "reformers", "military"):
        mood = g.court[f] + drift.get(f, 0) + g.rng.randint(-1, 1)
        g.court[f] = max(0, min(100, mood))
    if "cadres_refresh" in g.flags:                          # technocrats hold the hall
        g.court["old_guard"] = max(0, g.court["old_guard"] - 1)
    # blessings — v5: ONE per year in total, from the warmest faction
    lovers = [f for f in ("old_guard", "reformers", "military")
              if g.court[f] >= WORLD.LOVE_THRESHOLD]
    if lovers:
        warmest = max(lovers, key=lambda f: g.court[f])
        stat = {"old_guard": "ORDER", "reformers": "FAITH",
                "military": "MILITARY"}[warmest]
        g.stats[stat] = clamp(g.stats[stat] + 1)
    # costs — a grumbling faction quietly costs a point before it plots
    if g.court["old_guard"] <= WORLD.GRUMBLE_THRESHOLD:
        g.stats["ORDER"] = clamp(g.stats["ORDER"] - 1)
    if g.court["reformers"] <= WORLD.GRUMBLE_THRESHOLD:
        g.stats["ECONOMY"] = clamp(g.stats["ECONOMY"] - 1)
    if g.court["military"] <= WORLD.GRUMBLE_THRESHOLD:
        g.stats["MILITARY"] = clamp(g.stats["MILITARY"] - 1)
    # the velvet meeting room
    despairing = [f for f in ("old_guard", "reformers", "military")
                  if g.court[f] <= WORLD.COUP_THRESHOLD]
    if despairing and not any(eid == "palace_coup" for _, eid in g.pending):
        g.pending.append((g.year + 1, "palace_coup"))
        print(ui.paint(f"  ⚠ The {_FACTION_TITLES[despairing[0]]} are booking "
                       f"your conference room. Whispers, Thursday.", ui.C.BM))


# ---------------------------------------------------------------
# A single year
# ---------------------------------------------------------------
def year_step(g: Kremlin) -> str:
    """Returns 'ok' | 'quit'."""
    briefing(g)
    if not maybe_lifeline(g):
        return "quit"
    m = MODES[g.mode]
    ui.stats_panel(lambda: g.stats, g.year, g.lifelines, g.era,
                   mode_tag=m["tag"], reserves_cap=m["lifelines"],
                   hc=g.hard_currency, court=g.court,
                   world=WORLD.oil_status(g.year),
                   timeline=g.timeline_def.label, history=g.history)
    if not run_action(g):
        return "quit"
    if not run_directive(g):
        return "quit"
    for ev in collect_events(g):
        if run_event(g, ev) == "quit":
            return "quit"
    apply_drift(g)
    apply_systems(g)
    # v5 visuals: keep a small end-of-year series for the sparklines
    g.history.append({"year": g.year, "stats": dict(g.stats),
                      "hc": g.hard_currency, "oil": WORLD.oil_price(g.year)})
    if len(g.history) > 40:
        g.history = g.history[-40:]
    ui.pause(0.12)
    return "ok"


# ---------------------------------------------------------------
# v4: the extended era
# ---------------------------------------------------------------
def qualifies_for_new_era(g: Kremlin) -> bool:
    """1991 must end strong enough to argue for one more decade.

    v5 raises the valas gate to 30: the Millennium has to be paid for, which
    finally makes hoarding from 1985 a real decision.
    """
    return (min(g.stats.values()) >= 25 and g.hard_currency >= 30
            and ("treaty_signed" in g.flags or g.stats["FAITH"] >= 55))


def offer_new_era(g: Kremlin) -> bool:
    """The 1991 boundary: offer to play the Red Millennium (1992-2001)."""
    print()
    print(ui.paint("  ┌───────────────────── THE ANSWER ─────────────────────┐", ui.C.BB))
    print(ui.paint("  ☭ December 1991: the flag is still red, and the Politburo knows", ui.C.BG))
    print(ui.paint("  ☭ something the obituaries don't. Ten more years, Comrade —", ui.C.BG))
    print(ui.paint("  ☭ 1992…2001, the Red Millennium — into the new century?", ui.C.BG))
    print(ui.paint("  └──────────────────────────────────────────────────────┘", ui.C.DIM))
    print()
    pick = ui.ask_choice("  ❯ Continue into the new era? (1 yes / 0, tidy ending) ", 1, g.rng)
    return pick == 1


# ---------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------
def run(seed: int | None = None, mode: str | None = None,
        timeline: str | None = None) -> None:
    g = Kremlin(seed, mode=mode, timeline=timeline)
    resumed = False
    existing = persistence.load_game()
    if existing is not None:
        print(ui.paint(f"  ══ A saved game exists (year {existing.year} · "
                       f"{MODES[existing.mode]['label']} · "
                       f"{existing.timeline_def.label}).", ui.C.Y))
        pick = ui.ask_choice("  ❯ Resume it? (1 yes / other: fresh start) ", 1, g.rng)
        if pick == 1:
            g = existing
            resumed = True
            print(ui.paint(f"  ☭ Welcome back, {g.name}. The Union never noticed you left.", ui.C.BG))
    if not resumed:
        setup = introduction(g, mode=mode, timeline=timeline)
        if setup is None:
            print(ui.paint("  You declined the appointment. History notices briefly.", ui.C.Y))
            return
        g = Kremlin(seed, mode=setup["mode"], timeline=setup["timeline"])
        g.name = setup["name"]
        if setup["mandate"]:
            ops.apply_ops(g, MANDATES[setup["mandate"] - 1][2])
    while g.year <= g.end_year:
        if g.dead_stat() or g.deposed:
            END.ending_collapse(g)
            return
        cmd = ui.ask_command(g.rng)
        if cmd == "quit":
            END.ending_retire(g)
            return
        if cmd == "dossier":
            dossier.show_roadmap(g)
            continue
        if cmd == "save":
            if persistence.save_game(g):
                print(ui.paint(f"  ▸ Save filed for {g.year} ({MODES[g.mode]['label']}). "
                               f"Resume it from the title screen, or 'l' anytime.", ui.C.G))
            else:
                print(ui.paint("  ✗ The vault refused the file. Save failed.", ui.C.R))
            continue
        if cmd == "load":
            loaded = persistence.load_game()
            if loaded is None:
                print(ui.paint("  ✗ No intact save found (wrong version or damaged file).", ui.C.R))
                continue
            g = loaded
            print(ui.paint(f"  ☭ State restored: {g.year} · {MODES[g.mode]['label']} · "
                           f"{g.name}'s gauges are back in place.", ui.C.BG))
            continue
        if year_step(g) == "quit":
            END.ending_retire(g)
            return
        if g.dead_stat() or g.deposed:
            END.ending_collapse(g)
            return
        if g.year == g.end_year:
            # ── v4: the boundary year. If 1991 ended strong, history offers
            #    one more decade; otherwise the classic endings speak. ──
            if g.end_year == 1991 and qualifies_for_new_era(g) and offer_new_era(g):
                g.end_year = 2001
                g.lifelines += 2          # the new era extends the reserves
                print()
                print(ui.paint("  ══ THE RED MILLENNIUM ══  a new decade enters the ledger:", ui.C.BM))
                print(ui.paint("     1992–2001: the market question, the network question,", ui.C.W))
                print(ui.paint("     NATO's weekend, the Asian flu — two fresh reserves granted.", ui.C.W))
                print()
                g.year += 1
                continue
            if g.end_year >= 2001:
                END.ending_red_millennium(g)
            else:
                END.ending_union_survives(g)
            return
        g.year += 1
    END.ending_union_survives(g)
