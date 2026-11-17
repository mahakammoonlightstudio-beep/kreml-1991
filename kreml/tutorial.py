"""New General Secretary Orientation — the optional first-year briefing.

The tutorial is a set of cynical staff memos, not a wall of pop-ups. It runs
before the first year and teaches the controls the game actually uses:

  * the five gauges and yearly drift,
  * the Dossier (`d`), political capital (`i`) and standing orders (`o`),
  * plan fatigue, the court's danger line and the 1991 arithmetic,
  * the valas warning for 1986 and the new Republic Unrest board.

After the memos, the first year is "coached": one short margin note appears
before the focus, the directive, the event and the year-end settlement. The
notes never change the arithmetic and never spend resources.
"""
from __future__ import annotations

from . import ui
from .state import STATS, clamp
from .content.modes import MODES
from .content import world as WORLD
from .content import orders as ORDERS
from .content import capital as CAP
from .content import republics as REP
from . import ops

HEADER = "  ┌─ NEW GENERAL SECRETARY ORIENTATION · OCTOBER 1964 ─────────┐"
FOOTER = "  └──────────────────────────────────────────────────────────────┘"


def _memo(title: str, lines: tuple[str, ...] | list[str]) -> None:
    print()
    print(ui.paint(HEADER, ui.C.BB))
    print(ui.paint("  │ MEMO · " + title, ui.C.BM))
    for line in lines:
        print(ui.paint("  │ " + line, ui.C.W))
    print(ui.paint(FOOTER, ui.C.DIM))


def _ask(prompt: str, limit: int) -> int:
    """Tutorial menu: numbers, plus the real d/i/o keys as shortcuts."""
    shortcuts = {"d": 2, "i": 3, "o": 4}
    while True:
        try:
            raw = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 6
        if raw in {"", "enter"}:
            return 6
        if raw in {"q", "skip", "0"}:
            return 0
        if raw in shortcuts:
            return shortcuts[raw]
        try:
            n = int(raw)
        except ValueError:
            n = -1
        if 1 <= n <= limit:
            return n
        print(ui.paint("  ✗ The orientation form accepts 0–6, d, i or o.", ui.C.R))


def _memo_gauges(g) -> None:
    m = MODES[g.mode]
    drift = m["drift"][g.era]
    rows = []
    for stat in STATS:
        now = g.stats[stat]
        nxt = clamp(now + drift.get(stat, 0))
        rows.append(f"{stat:<9} {now:>3}  →  {nxt:>3}   drift {drift.get(stat, 0):+d}")
    _memo(
        "01 / THE BOARD AND THE FIVE GAUGES",
        (
            "Comrade, the board is not decoration. Five gauges, and every one",
            "of them is being lowered while you read this. That is drift.",
            "",
            *rows,
            "",
            "The yearly directive is your hand on the lever. The personal focus",
            "is the smaller hand. Neither stops drift; they buy you margin.",
            "Any gauge at zero ends the appointment. No exceptions, no appeal.",
            "",
            "Read the Dossier with `d` whenever you feel clever. It is free,",
            "which is the only free thing in this building.",
        ),
    )


def _memo_dossier(g) -> None:
    _memo(
        "02 / THE DOSSIER (`d`)",
        (
            "The Dossier is the archive that tells you what you have done, what",
            "is still open, and which doors history is about to nail shut.",
            "",
            "Your staff have opened it below. This is the real thing, not a",
            "training copy. Try not to sign anything while reading.",
        ),
    )
    from . import dossier
    dossier.show_roadmap(g)


def _memo_capital(g) -> None:
    moves = []
    for move in CAP.MOVES:
        price = CAP.cost_of(g, move)
        moves.append(f"{price:>2} ❖  {move['label']}")
    _memo(
        "03 / POLITICAL CAPITAL (`i`)",
        (
            f"The ledger says you have {getattr(g, 'influence', 0)} ❖. This is not money;",
            "it is the number of people who will answer the telephone at midnight.",
            "",
            *moves,
            "",
            "One favour per year. Repeat the same favour and the price rises,",
            "because even gratitude has a ministry and a markup.",
            "Press `i` at the year boundary to spend it. Do not hoard it forever;",
            "a capital account is not a monument.",
        ),
    )


def _memo_orders(g) -> None:
    current = ORDERS.get(getattr(g, "order", None))
    lines = [
        "A standing order is the doctrine the Kremlin follows when you freeze.",
        "It nudges yearly drift, colours the court, and answers the clock for you.",
        "",
    ]
    if current:
        lines.append(f"Current doctrine: {current['label']}.")
        lines.append("")
    for order in ORDERS.ORDERS:
        lines.append(f"· {order['label']} — {order['desc']}")
    lines += [
        "",
        "Press `o` at the year boundary. With `--timed`, this is the difference",
        "between a policy and an accidental policy.",
    ]
    _memo("04 / STANDING ORDERS (`o`)", tuple(lines))


def _memo_first_year(g) -> None:
    fatigue = " → ".join(f"{int(x * 100)}%" for x in ops.FATIGUE)
    court_line = "  ".join(
        f"{name} {g.court.get(key, 50)}" for key, name in
        (("old_guard", "Old Guard"), ("reformers", "Reformers"), ("military", "Army"))
    )
    unrest = "  ".join(
        f"{REP.SHORT[r]} {g.republic_unrest.get(r, 0)}" for r in REP.REPUBLICS
    )
    _memo(
        "05 / THE FIRST-YEAR ARITHMETIC",
        (
            f"Plan fatigue: {fatigue}. The costs stay whole. Repeating the same",
            "directive is how a plan becomes a rumour with stationery.",
            "",
            f"Court: {court_line}.",
            f"The room is booked at {WORLD.COUP_THRESHOLD} or below. At 15 or",
            "below, the agenda is already typed and the ink is dry.",
            "",
            f"1991 gate: MILITARY + ORDER ≥ {ops.COUP_SAFE}. Yours is",
            f"{g.stats['MILITARY'] + g.stats['ORDER']} today. Drift is patient.",
            "",
            f"Valas: the 1986 glut drops oil to {WORLD.oil_price(1986)} and the",
            "reserve starts bleeding. A Millennium needs 30; hoard before 1986.",
            "",
            f"Republics: {unrest}.",
            "Unrest feeds on low Order and open politics, and it poisons the",
            "late Union. Tour the republics, subsidise them, or sign the treaty.",
            f"At {REP.CRISIS_THRESHOLD} they stop sending memoranda.",
            "",
            "That is the whole secret: the game is not hiding the arithmetic.",
            "It is hiding it under a committee. Read the board every year.",
        ),
    )


def coach(g, stage: str) -> None:
    """One margin note during the first guided year."""
    if not getattr(g, "tutorial", False):
        return
    if getattr(g, "tutorial_year", g.year) != g.year:
        return
    notes = {
        "focus": "ORIENTATION: pick the focus that patches your weakest gauge; a habit also goes stale.",
        "directive": "ORIENTATION: check the fatigue line. A repeated plan still charges full price.",
        "event": "ORIENTATION: after the decision, look at the court, the valas and Republic Unrest.",
        "year_end": "ORIENTATION: drift applies after your choices. Read the new board before 1965.",
    }
    note = notes.get(stage)
    if note:
        print(ui.paint("  ▸ " + note, ui.C.DIM))


def finish(g) -> None:
    if not getattr(g, "tutorial", False):
        return
    g.tutorial = False
    print()
    print(ui.paint("  ★ ORIENTATION COMPLETE. The staff have stopped holding your hand.", ui.C.Y))
    print(ui.paint("    They are now holding your file. The first year is yours.", ui.C.DIM))
    print()


def orientation(g) -> None:
    """Run the optional pre-game briefing. Returns when the player begins."""
    print()
    print(ui.paint("  ╔══════════════════════════════════════════════════════════════╗", ui.C.BB))
    print(ui.paint("  ║ NEW GENERAL SECRETARY ORIENTATION · VOLUNTARY, LIKE ALL SOVIET FORMS ║", ui.C.BB))
    print(ui.paint("  ╚══════════════════════════════════════════════════════════════╝", ui.C.BB))
    print(ui.paint("  Chief of Staff Volkov has left five memos and one door open.", ui.C.W))
    print(ui.paint("  The memos are cynical. The door is not.", ui.C.DIM))
    print()
    while True:
        print(ui.paint("  ── ORIENTATION FILE ──", ui.C.Y))
        print("   1. Memo 01 — the board and the five gauges")
        print("   2. Memo 02 — the Dossier (d)")
        print("   3. Memo 03 — political capital (i)")
        print("   4. Memo 04 — standing orders (o)")
        print("   5. Memo 05 — the first-year arithmetic & Republic Unrest")
        print("   6. Begin the first year")
        print("   0. Skip the orientation")
        pick = _ask("  ❯ Orientation: ", 6)
        if pick == 0:
            print(ui.paint("  The memos go back in the safe. The Union does not.", ui.C.DIM))
            return
        if pick == 6:
            g.tutorial = True
            g.tutorial_year = g.year
            print()
            print(ui.paint("  ▸ The first year will be guided. Margin notes, no training wheels.", ui.C.G))
            print(ui.paint("  ▸ Use d, i and o at the year boundary. The rest is arithmetic.", ui.C.DIM))
            return
        if pick == 1:
            _memo_gauges(g)
        elif pick == 2:
            _memo_dossier(g)
        elif pick == 3:
            _memo_capital(g)
        elif pick == 4:
            _memo_orders(g)
        elif pick == 5:
            _memo_first_year(g)
        print()
        print(ui.paint("  (The file stays open. Choose another memo, or 6 to begin.)", ui.C.DIM))


def tutorial_requested(argv: list[str]) -> bool:
    return "--tutorial" in argv or "-tutorial" in argv
