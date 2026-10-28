"""The Dossier: the interactive timeline & branch-roadmap view.

Pulls no new data — it re-reads DIRECTIVES, EVENTS, pools and scripted years
from `content/` and re-checks requirements through `ops.check_requires`, then
renders three layers:

  1. DECISION LEDGER   — everything you actually did, year by year
  2. OPEN ROADS        — conditional/one-off directives: done ▸ open ✖ locked
  3. FORKS & TIMETABLE — branching events, pending delayed events, and the
                         future history you know is coming
"""
from __future__ import annotations

from . import ui
from .ops import check_requires
from .state import Kremlin, ERAS
from .content import directives as DR
from .content import events as EV


def _directive_status(g: Kremlin, d) -> tuple[str, str]:
    """One of: done / open / locked(+reason)."""
    if d.once and d.id in g.used_directives:
        return "done", ""
    ok, reason = check_requires(g, d.requires)
    if ok:
        return "open", ""
    return "locked", reason


def _event_status(g: Kremlin, ev) -> tuple[str, str]:
    if ev.once and ev.id in g.used_events:
        return "done", ""
    ok, reason = check_requires(g, ev.requires)
    if ok:
        return "open", ""
    return "locked", reason


def _missed(g: Kremlin, ev) -> bool:
    """True when this event's window has permanently closed."""
    if ev.era and g.year > ERAS[ev.era][1]:
        return True
    if "max_year" in ev.requires and g.year > ev.requires["max_year"]:
        return True
    for year, ids in EV.SCRIPTED.items():
        if ev.id in ids and year < g.year:
            return True
    return False


def show_roadmap(g: Kremlin) -> None:
    W = ui.paint
    print()
    print(W(" ╔" + "═" * 76 + "╗", ui.C.BB))
    print(W(" ║ DOSSIER — the decision ledger & the road map                           ║", ui.C.BB))
    print(W(" ╚" + "═" * 76 + "╝", ui.C.BB))

    # ── 0. v4: the world market & the court weather ───────────────
    from .content import world as _W
    from .state import FACTION_LABEL
    mood_bits = []
    for f in ("old_guard", "reformers", "military"):
        m = g.court.get(f, 50)
        mark = W("⚠", ui.C.BM) if m <= 15 else W("●", ui.C.G) if m >= 70 else W("◐", ui.C.Y)
        mood_bits.append(f"{mark} {FACTION_LABEL[f]} {m}")
    oil_word = _W.oil_status(g.year)
    print(W("  ── THE ROOM & THE MARKET ──", ui.C.Y))
    print(f"   {W('Valas reserve:', ui.C.W)} {W(str(g.hard_currency), ui.C.BB)}"
          f"   {W('Oil market:', ui.C.W)} {W(oil_word, ui.C.BB)}"
          f"   {W(' | '.join(mood_bits), ui.C.W)}")
    if any(eid == "palace_coup" for _, eid in g.pending):
        print(W("   ⚠ A velvet meeting is on this year's docket. Personally.", ui.C.BM))
    print()

    # ── 1. Decision ledger ────────────────────────────────────────
    print(W("  ── DECISION LEDGER (what you did) ──", ui.C.Y))
    if not g.ledger:
        print(W("   (nothing yet — history still untouched)", ui.C.DIM))
    for year, label in g.ledger[-26:]:
        print(f"   {W(f'[{year}]', ui.C.BB)} {W('☭ ' + label, ui.C.W)}")
    if len(g.ledger) > 26:
        print(W(f"   … and {len(g.ledger) - 26} earlier pages", ui.C.DIM))
    print()

    # ── 2. Conditional roads (directives) ─────────────────────────
    print(W("  ── OPEN ROADS (conditional directives) ──", ui.C.Y))
    interesting = [d for d in DR.DIRECTIVES if d.requires or d.once]
    for d in interesting:
        status, reason = _directive_status(g, d)
        if status == "done":
            print(f"   {W('✔', ui.C.G)} {W(d.label, ui.C.DIM)}  {W('— done', ui.C.DIM)}")
        elif status == "open":
            print(f"   {W('▸', ui.C.Y)} {W(d.label, ui.C.W)}"
                  f"  {W(f'— AVAILABLE now · {d.group}', ui.C.DIM)}")
        else:
            print(f"   {W('✖', ui.C.R)} {d.label}  {W('— ' + reason, ui.C.DIM)}")
    print()

    # ── 3a. Branching events not yet ruined or used ───────────────
    in_rotation: set[str] = set()
    for ids in EV.RANDOM_POOLS.values():
        in_rotation.update(ids)
    for ids in EV.SCRIPTED.values():
        in_rotation.update(ids)
    print(W("  ── FORKS (branching events still in play) ──", ui.C.Y))
    shown = 0
    for ev in EV.EVENTS.values():
        if ev.id not in in_rotation or ev.id in EV.CONGRESS_YEARS.values():
            continue
        if not (ev.once or ev.requires):
            continue
        status, reason = _event_status(g, ev)
        if status == "done":
            print(f"   {W('✔', ui.C.G)} {W(ev.title, ui.C.DIM)}  {W('— resolved', ui.C.DIM)}")
            shown += 1
        elif status == "open":
            where = "may fire this year" if ev.era == g.era or ev.id in EV.SCRIPTED.get(g.year, ()) else "gate OPEN — awaits its year"
            print(f"   {W('▸', ui.C.Y)} {W(ev.title, ui.C.W)}  {W(f'— {where}', ui.C.DIM)}")
            shown += 1
        else:
            where = "— missed forever" if _missed(g, ev) else f"— {reason}"
            print(f"   {W('✖', ui.C.R)} {ev.title}  {W(where, ui.C.DIM)}")
            shown += 1
    if not shown:
        print(W("   (no branching events in rotation)", ui.C.DIM))
    print()

    # ── 3b. Pending delayed consequences ──────────────────────────
    if g.pending:
        print(W("  ── IN THE PIPELINE (delayed responses) ──", ui.C.Y))
        for year, eid in sorted(g.pending):
            ev = EV.EVENTS.get(eid)
            title = ev.title if ev else eid
            print(f"   {W('⧗', ui.C.MG)} {W(str(year), ui.C.BB)} — {W(title, ui.C.W)}")
        print()

    # ── 3c. The future history you already know ───────────────────
    print(W("  ── THE KNOWN TIMETABLE (history's plan, unless you bend it) ──", ui.C.Y))
    future_years = [y for y in sorted(EV.SCRIPTED) if y > g.year]
    future_years += [y for y in sorted(EV.CONGRESS_YEARS) if y > g.year]
    for y in sorted(set(future_years)):
        names = []
        for eid in EV.SCRIPTED.get(y, ()):
            if eid not in g.used_events:
                names.append(EV.EVENTS[eid].title)
        if y in EV.CONGRESS_YEARS:
            names.append(EV.EVENTS[EV.CONGRESS_YEARS[y]].title)
        if names:
            print(f"   {W(str(y), ui.C.BB)}  {W(' · '.join(names), ui.C.W)}")
    print()
    print(W("  Prophecies assume the rails. Your ledger shows how far you've already", ui.C.DIM))
    print(W("  steamed off them, Comrade.", ui.C.DIM))
    print()
