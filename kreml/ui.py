"""Everything the player sees or types goes through this module."""
from __future__ import annotations

import os
import sys
import time
import random

from .state import STAT_LABEL, FACTIONS, FACTION_LABEL

FACTION_ITEMS = tuple((f, FACTION_LABEL[f]) for f in FACTIONS)

DRAMA = False

# Animations only when a human is actually watching a terminal. Redirected
# output (tests, recorders) gets the plain, deterministic text.
ANIM = bool(getattr(sys.stdout, "isatty", lambda: False)()) if sys.stdout else False

# v6: the wall clock. Off unless `python main.py --timed` is used (or the FLASH
# CRISIS mode is chosen with --timed). The terminal draws a live countdown on
# Windows (msvcrt) and Linux/macOS (termios cbreak); the browser page owns its
# own clock. Tests never arm it, so a (seed, answers) pair is always one run.
TIMED = False
CLOCK_DEFAULT = 10.0


def pause(seconds: float) -> None:
    if ANIM and seconds > 0:
        time.sleep(seconds)

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

     V E R S I O N  6
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


_SUB = " ▏▎▍▌▋▊▉█"       # eight sub-cells for a smooth fill
_SPARK = "▁▂▃▄▅▆▇█"      # sparkline heights (ASCII-safe, one cell each)


def bar(v: int, width: int = 30) -> str:
    """A gauge bar with a fractional last cell (no ANSI, no dependencies)."""
    v = max(0, min(100, int(v)))
    filled = v * width / 100.0
    whole = int(filled)
    idx = int(round((filled - whole) * 8))
    if idx == 8:
        whole += 1
        idx = 0
    body = "█" * min(whole, width)
    if idx and len(body) < width:
        body += _SUB[idx]
    return body + "░" * max(0, width - len(body))


def sparkline(values, width: int = 24) -> str:
    """A tiny trend line: min..max of the last `width` samples."""
    vals = [v for v in (values or []) if v is not None][-width:]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return _SPARK[3] * len(vals)
    return "".join(_SPARK[min(7, int((v - lo) / (hi - lo) * 7 + 0.5))]
                   for v in vals)


def arrow(delta: int) -> str:
    if delta > 0:
        return "▲"
    if delta < 0:
        return "▼"
    return "·"


def year_banner(year: int, note: str = "") -> None:
    """The year plate. Three dim frames that settle into the real header."""
    tail = paint(f"  {note}", C.DIM) if note else ""
    if not ANIM:
        print(paint(f"  ☭ {year} ☭", C.BM) + tail)
        return
    for frame in ("░", "▒", "▓"):
        sys.stdout.write("\r" + paint(f"  {frame * 3} {year} {frame * 3}", C.DIM))
        sys.stdout.flush()
        time.sleep(0.06)
    sys.stdout.write("\r" + " " * 32 + "\r")
    print(paint(f"  ☭ {year} ☭", C.BM) + tail)
    sys.stdout.flush()


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
                reserves_cap: int = 3, hc: int = 50, court: dict | None = None,
                world: str = "", timeline: str = "",
                history: list | None = None, influence: int = 0,
                order: str = "", agenda: str = "") -> None:
    hist = history or []
    print(paint(f"  ━━━━━━━━━━━━━━━ ☭  YEAR {year}  ☭  [{era} · {mode_tag}] ━━━━━━━━━━━━━━", C.BB))
    if timeline:
        print(paint(f"   {timeline}", C.DIM))
    for stat in ("ECONOMY", "MILITARY", "ORDER", "FAITH", "PRESTIGE"):
        v = get_stats()[stat]
        col = C.BM if v < 25 else (C.Y if v < 45 else STAT_COLOUR[stat])
        warn = paint("  ⚠ CRITICAL", C.BM) if v < 25 else ""
        trend = sparkline([h["stats"][stat] for h in hist], 10)
        trend_txt = paint(" " + trend + arrow(v - hist[-1]["stats"][stat]), C.DIM) \
            if trend else ""
        row = f"   {STAT_LABEL[stat]:<22} {paint(bar(v), col)} {v:>3}{trend_txt}{warn}"
        print(row)
    dots = '● ' * lifelines + '◦ ' * max(0, reserves_cap - lifelines)
    print(paint(f"   Kremlin reserves (lifelines · {mode_tag}): {dots}", C.DIM))
    market = f" oil {world}" if world else ""
    warn_hc = paint("  ⚠ DRY", C.BM) if hc < 15 else ""
    col_hc = C.BM if hc < 15 else (C.Y if hc < 40 else C.CY)
    hc_trend = sparkline([h["hc"] for h in hist], 10)
    oil_trend = sparkline([h["oil"] for h in hist], 10)
    print(f"   {'Valas     (gold & $)':<22} {paint(bar(hc), col_hc)} {hc:>3}"
          f"{paint(' ' + hc_trend, C.DIM) if hc_trend else ''}"
          f"{paint(' · ' + market + ' ' + oil_trend, C.DIM) if market else ''}{warn_hc}")
    if court:
        bits = []
        for f, label in FACTION_ITEMS:
            m = court.get(f, 50)
            col = C.BM if m <= 22 else (C.Y if m <= 34 else C.G)
            warn = paint(" ⚠PLOT", C.BM) if m <= 22 else ""
            bits.append(paint(f"{label} {bar(m, 6)} {m:>3}", col) + warn)
        print("   Politburo " + " · ".join(bits))
    bar_inf = "❖" * min(10, influence // 10) + "·" * max(0, 10 - influence // 10)
    print(paint(f"   {'Political capital':<22} {bar_inf} {influence:>3}"
                f"{paint('  · ' + order, C.DIM) if order else ''}", C.Y))
    if agenda:
        print(paint(f"   {'Agenda':<22} {agenda}", C.DIM))
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


# The host may supply its own clock reader. The browser build does: the page
# draws the countdown and submits a sentinel when the seconds run out.
TIMED_READER = None


def _read_timed_thread(prompt: str, seconds: float) -> str | None:
    """Fallback clock: a daemon reader on stdin, no live countdown."""
    import queue
    import threading

    box: "queue.Queue[str | None]" = queue.Queue(maxsize=1)

    def reader() -> None:
        try:
            box.put(input(f"{prompt}(\u23f1 {seconds:.0f}s) "))
        except (EOFError, KeyboardInterrupt):
            box.put(None)

    threading.Thread(target=reader, daemon=True).start()
    try:
        return box.get(timeout=seconds)
    except queue.Empty:
        print()
        return None


def _read_timed_msvcrt(prompt: str, seconds: float, *, kb=None,
                       now=None) -> str | None:
    """Windows console clock: a live countdown, edited in place, no threads.

    `kb` and `now` are injectable so the countdown can be tested without a
    keyboard or a real second passing.
    """
    import time as _time
    if kb is None:
        import msvcrt
        kb = msvcrt
    now = now or _time.monotonic
    deadline = now() + float(seconds)
    buf: list[str] = []
    sys.stdout.write(prompt)
    sys.stdout.flush()
    shown = None
    while True:
        left = deadline - now()
        if left <= 0:
            sys.stdout.write("\r" + prompt + "(\u23f1  0s) \u2014 time.        \n")
            sys.stdout.flush()
            return None
        secs = int(left + 0.999)
        if secs != shown:
            sys.stdout.write("\r" + prompt + f"(\u23f1 {secs:>2}s) " + "".join(buf))
            sys.stdout.flush()
            shown = secs
        if kb.kbhit():
            ch = kb.getwch()
            if ch == "\r":
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(buf)
            if ch == "\x08":
                if buf:
                    buf.pop()
            elif ch == "\x03":
                raise KeyboardInterrupt
            elif ch in ("\x00", "\xe0"):
                if kb.kbhit():
                    kb.getwch()                # extended key: swallow the pair
            elif ch >= " ":
                buf.append(ch)
            continue
        _time.sleep(0.05)


def _read_timed_posix(prompt: str, seconds: float, *, read_char=None,
                      now=None) -> str | None:
    """Linux/macOS clock: cbreak mode, one character at a time, live countdown.

    `read_char` and `now` are injectable, so the loop is testable on any OS
    without touching a real terminal or waiting a real second.
    """
    import time as _time

    now = now or _time.monotonic
    deadline = now() + float(seconds)
    buf: list[str] = []
    fd = None
    old = None
    termios = None
    if read_char is None:
        import select
        import termios as _termios
        import tty

        termios = _termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        def read_char(timeout: float) -> str:
            ready, _, _ = select.select([fd], [], [], timeout)
            if not ready:
                return ""
            return os.read(fd, 1).decode("utf-8", "ignore")

    sys.stdout.write(prompt)
    sys.stdout.flush()
    shown = None
    try:
        while True:
            left = deadline - now()
            if left <= 0:
                sys.stdout.write("\r" + prompt + "(\u23f1  0s) \u2014 time.        \n")
                sys.stdout.flush()
                return None
            secs = int(left + 0.999)
            if secs != shown:
                sys.stdout.write("\r" + prompt + f"(\u23f1 {secs:>2}s) " + "".join(buf))
                sys.stdout.flush()
                shown = secs
            ch = read_char(0.05)
            if not ch:
                _time.sleep(0.02)
                continue
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(buf)
            if ch in ("\x7f", "\x08"):
                if buf:
                    buf.pop()
            elif ch == "\x03":
                raise KeyboardInterrupt
            elif ch == "\x1b":
                continue                    # escape sequence: ignore it
            elif ch >= " ":
                buf.append(ch)
    finally:
        if termios is not None and old is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_timed_select(prompt: str, seconds: float) -> str | None:
    """POSIX terminal clock: wait for a whole line, then read it."""
    import select
    import time as _time

    fd = sys.stdin.fileno()
    deadline = _time.monotonic() + float(seconds)
    sys.stdout.write(f"{prompt}(\u23f1 {int(seconds)}s) ")
    sys.stdout.flush()
    while True:
        left = deadline - _time.monotonic()
        if left <= 0:
            sys.stdout.write("\n  \u23f1 time.\n")
            sys.stdout.flush()
            return None
        ready, _, _ = select.select([fd], [], [], min(0.1, left))
        if not ready:
            continue
        line = sys.stdin.readline()
        if line == "":
            return None
        return line.rstrip("\r\n")


def _pick_clock_reader():
    """A real terminal can be timed without threads; anything else cannot."""
    if not (sys.stdin and getattr(sys.stdin, "isatty", lambda: False)()):
        return None
    if os.name == "nt":
        return _read_timed_msvcrt
    try:
        import select      # noqa: F401
        import termios     # noqa: F401
        import tty         # noqa: F401
    except ImportError:    # a terminal without termios still gets a clock
        return _read_timed_select
    return _read_timed_posix


_KEYBOARD_READER = _pick_clock_reader()


def _read_timed(prompt: str, seconds: float) -> str | None:
    """One decision under a wall clock; None when the clock wins.

    Priority: the host's reader (browser page), then the terminal's own
    countdown, then a daemon-thread fallback for pipes and odd consoles.
    """
    if TIMED_READER is not None:
        return TIMED_READER(prompt, seconds)
    if _KEYBOARD_READER is not None:
        return _KEYBOARD_READER(prompt, seconds)
    return _read_timed_thread(prompt, seconds)


def _parse_choice(raw: str, limit: int) -> int | None:
    """0 = retire, 1..limit = choice, None = not a valid answer."""
    raw = raw.strip().lower()
    if raw in {"q", "quit", "retire", "0"}:
        return 0
    try:
        n = int(raw)
    except ValueError:
        return None
    return n if 1 <= n <= limit else None


def ask_choice(prompt: str, limit: int, rng: random.Random,
               seconds: float | None = None) -> int:
    """0 = retire / decline, 1..limit = choice, EOF (piped tests) = random.

    v6: when `seconds` is set and the wall clock is armed (--timed), the answer
    is waited for under the clock and -1 means "nobody decided in time".
    Without a clock the prompt is exactly the v5 prompt.
    """
    if seconds and TIMED:
        raw = _read_timed(prompt, float(seconds))
        if raw is None:
            return -1
        n = _parse_choice(raw, limit)
        if n is not None:
            return n
        print(paint("  ✗ Comrade, that is not on the form — and the clock is gone.", C.R))
    while True:
        try:
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            return rng.randint(1, limit)
        n = _parse_choice(raw, limit)
        if n is not None:
            return n
        if raw.strip().lower() in {"q", "quit", "retire", "0"}:
            return 0
        print(paint("  ✗ That dossier is off the table. Choose again.", C.R))


def ask_command(rng: random.Random) -> str:
    """The year-boundary command bar.

    Returns one of: 'go' | 'save' | 'load' | 'dossier' | 'quit'.
    EOF (piped tests) behaves like Enter → 'go'.
    """
    while True:
        prompt = ("  ❯ [Enter] proceed │ s save │ l load │ d dossier │ "
                  "i capital │ o orders │ q resign : ")
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
        if raw in {"i", "influence", "capital", "spend"}:
            return "capital"
        if raw in {"o", "order", "orders", "doctrine"}:
            return "orders"
        if raw in {"q", "quit", "resign", "0"}:
            return "quit"
        print(paint("  ✗ That stamp is not recognised. Try Enter, s, l, d, i, o or q.", C.R))


def show_changes(before, after, flags_before, flags_after) -> None:
    """Compact line showing what actually changed; printed dim."""
    parts = [f"{s} {arrow(after[s] - before[s])}{abs(after[s] - before[s])}"
             for s in before if after[s] != before[s]]
    new_flags = [f"⚑{f}" for f in flags_after - flags_before]
    lost_flags = [f"⚑-{f}" for f in flags_before - flags_after]
    if parts:
        print(paint("   ( " + " | ".join(parts) + " )", C.Y))
    for f in new_flags + lost_flags:
        print(paint("   ( " + f + " )", C.MG))
