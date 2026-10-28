"""Everything the player sees or types goes through this module."""
from __future__ import annotations

import os
import sys
import time
import random

from .state import STAT_LABEL, FACTIONS, FACTION_LABEL

FACTION_ITEMS = tuple((f, FACTION_LABEL[f]) for f in FACTIONS)

DRAMA = False

# Force UTF-8 + enable ANSI on Windows so ☭ never dies in cp1252.
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
_use_colour = bool(sys.stdout.isatty()) if sys.stdout else False
if os.name == "nt":
    os.system("")          # enables ANSI escape codes on Windows 10+


class C:
    R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; BL = "\033[94m"
    MG = "\033[95m"; CY = "\033[96m"; W = "\033[97m"
    BM = "\033[1m\033[91m"; BG = "\033[1m\033[92m"
    BB = "\033[1m"; DIM = "\033[90m"; X = "\033[0m"


STAT_COLOUR = {
    "ECONOMY": C.Y, "MILITARY": C.R, "ORDER": C.MG,
    "FAITH": C.G, "PRESTIGE": C.CY,
}

BANNER = r"""
        ★  ☭  ★
   К Р Е М Л Ь
      1 9 9 1

     V E R S I O N  4
"""


def paint(text: str, code: str) -> str:
    if _use_colour:
        return f"{code}{text}{C.X}"
    return text


def slow(text: str, delay: float = 0.012) -> None:
    if DRAMA:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
    else:
        print(text)


def bar(v: int, width: int = 30) -> str:
    filled = int(round(v * width / 100))
    return "█" * filled + "░" * (width - filled)


def sep(char: str = "─", width: int = 78) -> str:
    return char * width


def banner() -> None:
    print()
    print(paint(BANNER, C.BM))
    print(paint("  A GENERAL SECRETARY ALTERNATE-HISTORY SIMULATOR", C.BB))
    print(paint("  1964 ────────────── ► 1991   (+ the RED MILLENNIUM, 2001)", C.DIM))
    print()
    print(paint("  The Politburo awaits your signature, Comrade.", C.W))
    print()


def stats_panel(get_stats, year: int, lifelines: int, era: str, mode_tag: str = "BALANCED",
                reserves_cap: int = 3, hc: int = 40, court: dict | None = None,
                world: str = "") -> None:
    print(paint(f"  ━━━━━━━━━━━━━━━ ☭  YEAR {year}  ☭  [{era} · {mode_tag}] ━━━━━━━━━━━━━━", C.BB))
    for stat in ("ECONOMY", "MILITARY", "ORDER", "FAITH", "PRESTIGE"):
        v = get_stats()[stat]
        col = C.BM if v < 25 else (C.Y if v < 45 else STAT_COLOUR[stat])
        warn = paint("  ⚠ CRITICAL", C.BM) if v < 25 else ""
        row = f"   {STAT_LABEL[stat]:<22} {paint(bar(v), col)} {v:>3}{warn}"
        print(row)
    dots = '● ' * lifelines + '◦ ' * max(0, reserves_cap - lifelines)
    print(paint(f"   Kremlin reserves (lifelines · {mode_tag}): {dots}", C.DIM))
    market = f" · oil {world}" if world else ""
    warn_hc = paint("  ⚠ DRY", C.BM) if hc < 15 else ""
    col_hc = C.BM if hc < 15 else (C.Y if hc < 40 else C.CY)
    print(f"   {'Valas     (gold & $)':<22} {paint(bar(hc, 30), col_hc)} {hc:>3}"
          f"{paint(market, C.DIM)}{warn_hc}")
    if court:
        bits = []
        for f, label in FACTION_ITEMS:
            m = court.get(f, 50)
            col = C.BM if m <= 15 else (C.Y if m <= 30 else C.G)
            warn = paint("⚠ PLOT", C.BM) if m <= 15 else ""
            bits.append(paint(f"{label} {m:>3}", col) + warn)
        print("   Politburo                          " + "  ·  ".join(bits))
    print()


def event_header(title: str, text: str, note: str = "") -> None:
    print()
    print(paint("  ┌────────────── EVENT ───────────────────┐", C.BB))
    slow(paint("  ☈ " + title, C.BM))
    slow(paint("  " + text, C.W))
    if note:
        slow(paint("  " + note, C.DIM))
    print(paint("  └────────────────────────────────────────┘", C.DIM))


def list_options(options) -> None:
    for i, (label, outcomes) in enumerate(options, 1):
        print(f"   {paint(f'{i:>2}', C.BB)}. {paint(label, C.W)}")
        if outcomes:
            print(f"       {paint(outcomes, C.DIM)}")


def ask_choice(prompt: str, limit: int, rng: random.Random) -> int:
    """0 = retire / decline, 1..limit = choice, EOF (piped tests) = random valid."""
    while True:
        try:
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            return rng.randint(1, limit)
        raw = raw.strip().lower()
        if raw in {"q", "quit", "retire", "0"}:
            return 0
        try:
            n = int(raw)
        except ValueError:
            print(paint("  ✗ Comrade, that is not on the form.", C.R))
            continue
        if 1 <= n <= limit:
            return n
        print(paint("  ✗ That dossier is off the table. Choose again.", C.R))


def ask_command(rng: random.Random) -> str:
    """The year-boundary command bar.

    Returns one of: 'go' | 'save' | 'load' | 'dossier' | 'quit'.
    EOF (piped tests) behaves like Enter → 'go'.
    """
    while True:
        prompt = "  ❯ [Enter] proceed │ s save │ l load │ d dossier │ q resign : "
        try:
            raw = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "go"
        if raw in {"", "go", "enter"}:
            return "go"
        if raw in {"s", "save"}:
            return "save"
        if raw in {"l", "load"}:
            return "load"
        if raw in {"d", "dossier", "map", "db"}:
            return "dossier"
        if raw in {"q", "quit", "resign", "0"}:
            return "quit"
        print(paint("  ✗ That stamp is not recognised. Try Enter, s, l, d or q.", C.R))


def show_changes(before, after, flags_before, flags_after) -> None:
    """Compact line showing what actually changed; printed dim."""
    parts = [f"{s} {after[s] - before[s]:+d}" for s in before if after[s] != before[s]]
    new_flags = [f"⚑{f}" for f in flags_after - flags_before]
    lost_flags = [f"⚑-{f}" for f in flags_before - flags_after]
    if parts:
        print(paint("   ( " + " | ".join(parts) + " )", C.Y))
    for f in new_flags + lost_flags:
        print(paint("   ( " + f + " )", C.MG))
