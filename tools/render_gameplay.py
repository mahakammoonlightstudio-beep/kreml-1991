"""Render КРЕМЛЬ 1991 as a real-feeling gameplay recording at 1080p 60 FPS.

Why this exists (the old tools/render_video.py was a slideshow: one static
PNG per scene at fps=8).  This renderer instead behaves like a picked-up
screen recording of someone actually playing the game:

  * every screen is animated at 60 FPS — lines print in fast bursts,
    a block caret blinks, and screens SCROLL like a real console,
  * prompts are answered on-camera: the digit (or the Secretary's name)
    echoes char by char, then an Enter flash, then the repaint,
  * an animated mouse pointer (Bezier paths + overshoot + idle jitter)
    travels to the option the autopilot clicks,
  * a "REC ●" overlay and session timer, like an OBS capture,
  * acts dissolve into each other instead of hard PNG cuts,
  * the Soviet anthem from "edit video/" is muxed as soundtrack — optional:
    with no anthem file present the render finishes silent
    (looped when the video runs longer, fade-out at the end).

Pipeline
  1. dry-run the autopilot to find a seed that survives 1964-1991
  2. replay that seed while intercepting print() and input(); every prompt
     plus the screen it was shown on plus the exact answer becomes an "act"
  3. pre-bake each act's full screen once, then emit 60 fps frames
  4. pipe rawvideo into ffmpeg (x264), then mux the anthem audio track.

Usage:
    python tools\\render_gameplay.py                 # full auto
    python tools\\render_gameplay.py --seed 42       # fixed seed (must survive)
    python tools\\render_gameplay.py --max-acts 12   # short “does it render” test
    python tools\\render_gameplay.py --out name.mp4 --fps 30
"""
from __future__ import annotations

import builtins
import io
import math
import os
import pathlib
import random
import re
import subprocess
import sys
import time
from contextlib import redirect_stdout

from PIL import ImageFilter          # noqa: F401  (used lazily)
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

_TOOLS = pathlib.Path(__file__).resolve().parent
_REPO = _TOOLS.parent
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_REPO))

from render_video import (          # reuse ANSI parser + font coverage sets
    parse_line, MAIN_FONT, MAIN_BOLD, SYM_FONT, MAIN_COVER, SYM_COVER,
    PAL, DEFAULT_FG, BG,
)
import record_gameplay as RG        # the autopilot
from kreml import persistence       # to guarantee a clean save slot

# ─────────────────────────────── tuning ───────────────────────────────
FPS        = 60
CANW, CANH = 1600, 900
PADX, PADY = 24, 12
CELL_W, CELL_H, FSZ = 10, 22, 16
SYM_FSZ    = 14
COLS       = 120           # wrap width (like a ~120-col console)
ROWS       = 39            # visible terminal rows (scrolls beyond)
WAVE_MAX   = 170           # hard cap of baked lines (long endings)

REVEAL_MIN  = 0.42
REVEAL_MAX  = 1.5
SETTLE      = 0.22
HOVER_MIN, HOVER_RAND = 0.28, 0.34
TYPE_DIGIT  = 0.34
TYPE_CHAR   = 0.085        # seconds per char when typing the name
ENTER_HOLD  = 0.18
ENTER_TAIL  = 0.30
FINAL_HOLD  = 4.5
FADE_OUT    = 1.6
XFADE_FR    = 7            # cross-dissolve frames between acts

OPT_RX  = re.compile(r"""^\s{0,6}(\d{1,2})\.\s""")     # "   12. label"
ZERO_RX = re.compile(r"""^\s*\(?\s*(\d{1,2})\. """)    # "( 0. Retire / resign )"
ANSI    = re.compile(r"""\x1b\[\d+m""")
ANSI_RX = re.compile(r"""\x1b\[(\d+)m""")              # colour spans (kept)


def parse_lines(text: str) -> list:
    """ANSI→(char,rgb,bold) cells, carrying colour state ACROSS lines the way
    a real terminal does (the game's banner paints three lines in one colour)."""
    rows, fg, bold = [], DEFAULT_FG, False
    for line in text.split("\n"):
        cells, pos = [], 0
        for m in ANSI_RX.finditer(line):
            for ch in line[pos:m.start()]:
                cells.append((ch, fg, bold))
            code = m.group(1)
            if code == "0":
                bold, fg = False, DEFAULT_FG
            elif code == "1":
                bold = True
            elif code in PAL:
                fg = PAL[code]
            pos = m.end()
        for ch in line[pos:]:
            cells.append((ch, fg, bold))
        rows.append(cells)
    return rows

def log(msg: str) -> None:
    print(f"[{time.time() - EPOCH:6.1f}s] {msg}", flush=True)

EPOCH = time.time()
ANTHEM = _REPO / "edit video" / "National Anthem of USSR.mp4"
OUT_DEFAULT = _REPO / "gameplay_60fps.mp4"


def find_anthem(path: pathlib.Path = ANTHEM) -> pathlib.Path | None:
    """Locate the soundtrack (the repo stays lean — audio ships with renders)."""
    if path.exists():
        return path
    return None


# ─────────────────────────────── capture ──────────────────────────────
EVENTS: list = []          # ("c", text) | ("p", prompt, answer)
_ORIG_PRINT = builtins.print
_ORIG_BOT = RG.bot_input
_HOOKED = False


def _hook_stdlib() -> None:
    """Intercept print() + the autopilot's input() exactly once."""
    global _HOOKED
    if _HOOKED:
        return
    _HOOKED = True

    def rec_print(*a, **k):
        end = k.get("end", "\n")
        sep = k.get("sep", " ")
        EVENTS.append(("c", sep.join(str(x) for x in a) + end))
        return _ORIG_PRINT(*a, **k)

    def rec_input(prompt=""):
        if isinstance(prompt, bytes):
            prompt = prompt.decode("utf-8", "replace")
        p = prompt
        # The old autopilot never handled the 1991 boundary prompt
        # "Continue into the new era? (1 yes / 0, tidy ending)" and hung
        # there in an invalid-answer loop.  We answer: tidy ending.
        if "Continue into the new era" in p:
            ans = "0"
        else:
            ans = _ORIG_BOT(p)            # the autopilot answers instantly
        EVENTS.append(("p", p, ans))
        return ans

    builtins.print = rec_print
    RG.bot_input = rec_input          # run_bot rebinds builtins.input = RG.bot_input


class Act:
    """One interactive moment: the screen shown, the prompt, the answer."""

    __slots__ = ("raw", "prompt", "answer", "kind", "lines", "rows",
                 "offs", "offs_row", "n_rows", "opt_line", "image", "h")

    def __init__(self, raw: str, prompt: str | None, answer):
        self.raw, self.prompt, self.answer = raw, prompt, answer
        p = prompt or ""
        self.kind = ("final"    if prompt is None
                     else "name" if "history books" in p
                     else "enter" if "[Enter]" in p
                     else "decision")
        text = raw if raw.endswith("\n") else raw + "\n"
        if p:
            text += p                      # input() shows the prompt on-screen
        self.lines = text.split("\n")
        self.opt_line = (self._find_option_line() if self.kind == "decision"
                         else None)
        # ── display rows: parse ANSI (state carried across lines) → wrap ──
        raw_rows = parse_lines(text)
        self.rows, self.offs = [], []
        for cs in raw_rows:
            self.offs.append(len(self.rows))
            if not cs:
                cs = [("", DEFAULT_FG, False)]
            for k in range(0, len(cs), COLS):
                self.rows.append(cs[k:k + COLS])
        self.n_rows = len(self.rows)
        self.offs_row = self.offs          # raw-line index -> display row
        if self.n_rows > WAVE_MAX:         # very long endings: keep the tail
            cut = self.n_rows - WAVE_MAX
            self.rows = self.rows[cut:]
            self.offs = [max(0, o - cut) for o in self.offs]
            self.n_rows = len(self.rows)
        self.image = None                  # baked plate (tall canvas)
        self.h = (min(max(self.n_rows, ROWS), WAVE_MAX) * CELL_H) + 2 * PADY

    def _find_option_line(self):
        try:
            n = int(str(self.answer))
        except (TypeError, ValueError):
            return None
        if n <= 0:
            return None
        want = re.compile(rf"^\s{{0,6}}{n}\.\s")
        zero = re.compile(rf"^\s*\(?\s*{n}\s*\. ")
        for i in range(len(self.lines) - 1, -1, -1):
            clean = ANSI.sub("", self.lines[i])
            if want.match(clean):
                return i
        for i in range(len(self.lines) - 1, -1, -1):
            if zero.match(ANSI.sub("", self.lines[i])):
                return i
        return None


def capture_run(seed: int, clean_after: bool = False) -> tuple:
    """Replay one playthrough. Returns (acts, outcome)."""
    EVENTS.clear()
    for f in (persistence.SAVE_FILE,
              os.path.join(str(_REPO), "hall_of_fame.txt")):
        try:
            os.remove(f)
        except OSError:
            pass
    _hook_stdlib()
    buf = io.StringIO()
    with redirect_stdout(buf):
        RG.run_bot(seed)
    outcome = ("SURVIVED" if RG.OUTCOME["survived"]
               else "COLLAPSED" if RG.OUTCOME["collapsed"] else "ended")
    acts, pending = [], ""
    for ev in EVENTS:
        if ev[0] == "c":
            pending += ev[1]
        else:
            acts.append(Act(pending, ev[1], ev[2]))
            pending = ""
    if pending.strip():
        acts.append(Act(pending, None, None))       # closing/ending screen
    if not acts:
        raise SystemExit("capture produced no acts — capture bug?")
    return acts, outcome


# ─────────────────────────────── fonts/paint ──────────────────────────
_cache: dict = {}


def _font(spec: str, size: int):
    key = (spec, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(spec, size)
    return _cache[key]


def _cmap(path: str) -> set:
    t = TTFont(path)
    cov = set(t.getBestCmap().keys())
    t.close()
    return cov


BOLD_COVER = _cmap(MAIN_BOLD)      # Consolas Bold lacks ━ ┃ etc.


def draw_cells(d: ImageDraw.ImageDraw, cells, col: int, row: int,
               fgr: tuple | None = None) -> None:
    """Draw one parsed line at a grid slot (col,row) in cells coords.
    Font routing: bold→Consolas Bold (tested coverage; heavy box-drawing
    glyphs missing there fall back to regular Consolas), symbols→Segoe."""
    mono_r = _font(MAIN_FONT, FSZ)
    mono_b = _font(MAIN_BOLD, FSZ)
    sym    = _font(SYM_FONT, SYM_FSZ)
    x0 = PADX + col * CELL_W
    y0 = PADY + row * CELL_H + 1
    for c, (ch, rgb, bold) in enumerate(cells[:COLS]):
        if ch == " " or ch == "":
            continue
        x, y = x0 + c * CELL_W, y0
        if fgr is not None:
            rgb = fgr
        o = ord(ch)
        if bold and o in BOLD_COVER:
            d.text((x, y), ch, font=mono_b, fill=rgb)
        elif o in MAIN_COVER:
            d.text((x, y), ch, font=mono_r, fill=rgb)
        elif o in SYM_COVER:
            _sym_draw(d, sym, ch, x, y, rgb)
        elif o in BOLD_COVER:
            d.text((x, y), ch, font=mono_b, fill=rgb)
        else:
            _sym_draw(d, sym, ch, x, y, rgb)   # last try; missing → blank


def _sym_draw(d, sym, ch, x, y, rgb):
    try:
        bb = sym.getbbox(ch)
    except Exception:
        bb = None
    if not bb:
        return
    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x + max(0, (CELL_W - gw) // 2) - bb[0],
            y + max(0, (CELL_H - gh) // 2) - bb[1]),
           ch, font=sym, fill=rgb)


def plate_for(act: Act) -> Image.Image:
    """Bake the act's whole screen once (tall when the screen is long)."""
    img = Image.new("RGB", (CANW, act.h), BG)
    d = ImageDraw.Draw(img)
    for i, row_cells in enumerate(act.rows):
        draw_cells(d, row_cells, 0, i)
    return img


def _scanlines(img: Image.Image) -> Image.Image:
    pat = Image.new("L", (2, 2), 255)
    px = pat.load()
    px[0, 1] = 226
    scaled = pat.resize(img.size)          # tiles the 2-row pattern
    rgb = Image.merge("RGB", (scaled, scaled, scaled))
    return ImageChops.multiply(img, rgb)


# ─────────────────────────────── cursor sprite ────────────────────────
def build_cursor() -> Image.Image:
    from PIL import ImageFilter as _F
    S = 4
    sc = 2.6 * S                      # arrow ~ 26x40 in output
    poly = [(4, 2), (4, 33), (12, 26), (17, 37), (22, 35), (17, 24), (26, 24)]
    pts = [(x * sc, y * sc) for x, y in poly]
    W = int(max(p[0] for p in pts)) + 3
    H = int(max(p[1] for p in pts)) + 3
    raised = [(x - 2 * S, y - 2 * S) for x, y in pts]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(img).polygon(pts, fill=(0, 0, 0, 170))
    shadow = img.filter(_F.GaussianBlur(2.0 * S))
    arrow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(arrow).polygon(raised, fill=(255, 255, 255, 250),
                                  outline=(10, 10, 14, 255), width=int(1.8 * S))
    arrow = arrow.resize((W // S, H // S), Image.LANCZOS)
    shadow = shadow.resize((W // S, H // S), Image.LANCZOS)
    out = Image.new("RGBA", (W // S + 4, H // S + 4), (0, 0, 0, 0))
    out.alpha_composite(shadow, (3, 2))
    out.alpha_composite(arrow, (0, 0))
    return out


# ─────────────────────────────── helpers ──────────────────────────────
def ease_io(u: float) -> float:
    return 3 * u * u - 2 * u * u * u if u < 1 else 1.0


def bezier(p0, p3, u: float, rng: random.Random, over: float) -> tuple:
    e = ease_io(u)
    c1 = (p0[0] + (p3[0] - p0[0]) * (0.26 + 0.14 * rng.random()),
          p0[1] + (p3[1] - p0[1]) * (0.12 + 0.30 * rng.random())
          + 30 * rng.choice((-1, 1)))
    c2 = (p0[0] + (p3[0] - p0[0]) * (0.62 + 0.22 * rng.random()),
          p0[1] + (p3[1] - p0[1]) * (0.70 + 0.24 * rng.random()))
    def b(a, b4, c, d4):
        e2 = 1 - u
        return e2**3 * a + 3 * e2 * e2 * u * b4 + 3 * e2 * u * u * c + u**3 * d4
    x = b(p0[0], c1[0], c2[0], p3[0])
    y = b(p0[1], c1[1], c2[1], p3[1])
    if over and u > 0.60:                       # tiny overshoot & settle-back
        v = (u - 0.60) / 0.40
        k = math.exp(-5.5 * v) * math.sin(10.0 * v) * over
        dx, dy = (p3[0] - p0[0]), (p3[1] - p0[1])
        L = max(1.0, math.hypot(dx, dy))
        x += dx / L * k
        y += dy / L * k
    return x, y


def drift(t: float, cx: float, cy: float, seed: float) -> tuple:
    return (cx + 2.2 * math.sin(0.9 * t + seed) + 1.1 * math.sin(1.7 * t + 2.0 * seed),
            cy + 2.0 * math.cos(0.7 * t + seed) + 1.2 * math.sin(1.3 * t + seed))


# ─────────────────────────────── composer ─────────────────────────────
class Composer:
    """Emits 60 fps frames: bake plates, then reveal/hover/type/enter."""

    def __init__(self, pipe):
        self.pipe = pipe
        self.rng = random.Random(1991)
        self.cursor = build_cursor()
        self.dot = self._make_dot()
        self.hud_font = _font(r"C:\Windows\Fonts\segoeuib.ttf", 19)
        self.mcur = (CANW * 0.70, CANH * 0.80)
        self._msx = self.mcur

    # ---------- plates ------------------------------------------------
    @staticmethod
    def bake(act: Act) -> None:
        if act.image is None:
            act.image = plate_for(act)

    # ---------- per-frame drawing helpers -----------------------------
    def paste_window(self, img: Image.Image, act: Act, top: int, vis: int) -> None:
        if vis <= 0:
            return
        y0 = PADY + top * CELL_H
        y1 = min(act.h, y0 + vis * CELL_H)
        piece = act.image.crop((0, PADY + top * CELL_H, CANW, y1))
        img.paste(piece, (0, PADY))

    def caret(self, img, act, disp_row: int, col: int, rgb, on: bool) -> None:
        if not on:
            return
        d = ImageDraw.Draw(img)
        x = PADX + col * CELL_W + 1
        y = PADY + disp_row * CELL_H
        d.rectangle((x, y, x + CELL_W - 4, y + CELL_H - 5), fill=rgb)

    def typed(self, img, act, typed: str) -> None:
        """Echo the answer text right after the on-screen prompt text."""
        if not typed:
            return
        d = ImageDraw.Draw(img)
        pl = act.n_rows - 1
        col = len(act.rows[pl]) if pl < len(act.rows) else 0
        disp_row = min(pl, ROWS - 1)  # the prompt line is always visible
        cells = [(ch, DEFAULT_FG, False) for ch in typed[:COLS - col]]
        draw_cells(d, cells, col, disp_row)

    def hud(self, img, t_now: float) -> None:
        blink = (int(t_now * 4) % 2) == 0
        if blink:
            img.paste(self.dot, (CANW - 182, PADY), self.dot)
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((CANW - 158, PADY, CANW - 68, PADY + 28),
                            6, fill=(0, 0, 0, 105))
        txt = f"REC {int(t_now // 60):02d}:{int(t_now % 60):02d}"
        d.text((CANW - 152, PADY + 3), txt, font=self.hud_font,
               fill=(235, 235, 240, 240))

    def mouse_draw(self, img) -> None:
        img.paste(self.cursor, (int(self._msx[0]), int(self._msx[1])), self.cursor)

    # ---------- one act ------------------------------------------------
    def act_frames(self, act: Act, prev_img, t_start: float) -> int:
        rng = self.rng
        self.bake(act)
        n = act.n_rows
        final_top = max(0, n - ROWS)

        # ---- target pixel (where the human would be looking/clicking) --
        t_xy = (CANW * 0.70, CANH * 0.60)
        if act.kind == "decision" and act.opt_line is not None:
            li = act.opt_line
            m = OPT_RX.match(ANSI.sub("", act.lines[li])) or \
                ZERO_RX.match(ANSI.sub("", act.lines[li]))
            col = (m.start() if m else 0) or 6
            disp = act.offs[li]
            t_xy = (PADX + col * CELL_W - 10,
                    PADY + (disp - final_top) * CELL_H + CELL_H // 2)
        elif act.kind in ("decision", "enter", "name"):
            pl = act.n_rows - 1
            col = min(len(act.rows[pl]), COLS - 6) if pl < len(act.rows) else 6
            t_xy = (PADX + (col + 2) * CELL_W,
                    PADY + min(pl, ROWS - 1) * CELL_H + CELL_H // 2)
        t_xy = (min(max(40, t_xy[0]), CANW - 70),
                min(max(PADY, t_xy[1]), CANH - 60))
        if act.kind == "final":
            t_xy = (CANW * 0.30, CANH * 0.34)
        if act.kind == "name":
            t_xy = (CANW * 0.68, CANH * 0.42)      # hands move to the keyboard

        # ---- timing plan ----------------------------------------------
        rate = max(60.0, min(150.0, n / 0.55))
        reveal_t = max(REVEAL_MIN, min(REVEAL_MAX, n / rate))
        if act.kind == "enter":
            reveal_t = max(0.30, reveal_t * 0.8)
        if act.kind == "final":
            reveal_t = max(reveal_t, 1.6)
        move_t = 0.0
        if act.kind in ("decision", "enter"):
            dist = math.hypot(t_xy[0] - self.mcur[0], t_xy[1] - self.mcur[1])
            move_t = min(0.78, max(0.35, dist / 1550.0))
        hover_t = (HOVER_MIN + rng.random() * HOVER_RAND
                   if act.kind == "decision" else 0.16)
        type_t = 0.0
        if act.kind == "decision":
            type_t = TYPE_DIGIT * len(str(act.answer))
        elif act.kind == "name":
            type_t = TYPE_CHAR * len(act.answer)
        elif act.kind == "enter":
            type_t = 0.12                          # the bare Enter press
        enter_t, tail = ENTER_HOLD, (0.26 if act.kind != "final" else FINAL_HOLD)
        if act.kind == "enter":
            tail = max(0.55, 0.28 + rng.random() * 0.25)   # pause between years
        if act.kind == "final":
            move_t, hover_t, type_t, enter_t = 0.0, 0.30, 0.0, 0.55

        phases = [
            ("xfade", XFADE_FR / FPS if prev_img is not None else 0.0),
            ("reveal", reveal_t),
            ("settle", SETTLE if act.kind != "enter" else 0.12),
            ("move", move_t),
            ("hover", hover_t),
            ("type", type_t),
            ("enter", enter_t),
            ("enter2", ENTER_TAIL),
            ("tail", tail),
        ]
        emitted = 0
        for phase, dur in phases:
            if dur <= 0:
                continue
            nfr = max(1, int(round(dur * FPS)))
            for f in range(nfr):
                u = (f + 1.0) / nfr
                img = self.frame(act, phase, u, f,
                                 prev_img if phase == "xfade" else None,
                                 t_now=t_start + (emitted + f) / FPS,
                                 target=t_xy)
                self.pipe.write(img.tobytes())
                if phase != "xfade":
                    self.last = img
                elif f == nfr - 1:
                    self.last = img
            emitted += nfr
        # recompute cursor position at act end (continuity)
        self.mcur = tuple(v for v in self._msx)
        return emitted

    # ---------- phrase engine -----------------------------------------
    def frame(self, act: Act, phase: str, u: float, f: int, prev_img,
              t_now: float, target) -> Image.Image:
        n = act.n_rows
        final_top = max(0, n - ROWS)
        on_blink = (f // 4) % 2 == 0

        # ---- how many lines are on screen this frame --------------------
        if phase == "reveal":
            shown = min(n, max(1, int(math.ceil(n * ease_io(u)))))
        else:
            shown = n
        top = max(0, shown - ROWS)
        vis = min(shown, ROWS)

        img = Image.new("RGB", (CANW, CANH), BG)
        self.paste_window(img, act, top, vis)

        # ---- cross-dissolve at act boundary -----------------------------
        if phase == "xfade" and prev_img is not None:
            img = Image.blend(prev_img.copy(), img, u)

        # ---- caret & typed echo -----------------------------------------
        pl = n - 1
        disp_pl = min(pl, ROWS - 1)
        prompt_col = min(len(act.rows[pl]), COLS) if pl < len(act.rows) else 1
        echo = str(act.answer or "")
        if act.kind in ("final", "enter"):
            echo = ""
        if phase == "reveal":
            if vis > 0:
                self.caret(img, act, vis - 1,
                           min(len(act.rows[top + vis - 1]), COLS),
                           DEFAULT_FG, on_blink)
        elif phase in ("settle", "move", "hover") and act.kind != "final":
            self.caret(img, act, disp_pl, prompt_col, DEFAULT_FG, on_blink)
        elif phase == "type" and act.kind != "final":
            typed_n = int(math.ceil(len(echo) * u))
            self.typed(img, act, echo[:typed_n])
            self.caret(img, act, disp_pl, prompt_col + typed_n,
                       DEFAULT_FG, on_blink)
        elif phase == "enter" and act.kind != "final":
            self.typed(img, act, echo)
            self.caret(img, act, disp_pl, prompt_col + len(echo),
                       DEFAULT_FG, on_blink)
        elif phase == "enter2" and act.kind != "final":
            self.typed(img, act, echo)
            if f < 4:   # accepted: the caret drops one line, listening again
                self.caret(img, act, min(ROWS - 1, disp_pl + 1),
                           prompt_col + len(echo), DEFAULT_FG, True)
        elif phase == "tail" and act.kind != "final":
            self.typed(img, act, echo)
            col = prompt_col + (len(echo) if echo else 0)
            self.caret(img, act, disp_pl, col, DEFAULT_FG, on_blink)

        # ---- mouse ------------------------------------------------------
        if phase == "reveal":
            self._msx = drift(t_now, CANW * 0.74, CANH * 0.82, 3.1)
        elif phase == "settle":
            self._msx = drift(t_now, self.mcur[0], self.mcur[1], 1.7)
        elif phase == "move":
            self._msx = bezier(self.mcur, target, u, self.rng,
                               16 if act.kind == "decision" else 7)
        elif phase == "hover":
            self._msx = drift(t_now, target[0] - 7, target[1] - 9, 0.9)
        elif phase in ("type", "enter", "enter2"):
            self._msx = drift(t_now, target[0] - 7, target[1] - 9, 0.55)
        elif phase == "tail":
            if act.kind == "final":
                self._msx = drift(t_now, CANW * 0.66, CANH * 0.35, 2.2)
            else:
                self._msx = drift(t_now,
                                  target[0] - 7 + (24 - 24 * math.sin(u * math.pi)),
                                  target[1] - 9 + 18 * u, 0.4)
        elif phase == "xfade":
            self._msx = self.mcur
        self.mouse_draw(img)

        # ---- REC overlay --------------------------------------------------
        self.hud(img, max(0.0, t_now))
        return img

    # ---------- fade to black at the very end ---------------------------
    def fadeout(self, dur: float) -> None:
        nfr = max(1, int(dur * FPS))
        for i in range(nfr):
            u = (i + 1) / nfr
            out = Image.blend(self.last.copy(),
                              Image.new("RGB", (CANW, CANH), (0, 0, 0)), u * u)
            self.pipe.write(out.tobytes())
            self.last = out

    # "@staticmethod" unused
    def _make_dot(self) -> Image.Image:
        D = 22
        img = Image.new("RGBA", (D, D), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, D - 1, D - 1), fill=(235, 30, 42, 255))
        return img


def fadeout_frames(comp: Composer, dur: float) -> None:
    comp.fadeout(dur)


# ─────────────────────────────── main ────────────────────────────────
def pick_seed(want: int | None) -> int:
    if want is not None:
        log(f"dry-check seed {want} ...")
        _, outcome = capture_run(want)
        if outcome == "SURVIVED":
            log(f"seed {want} survives - using it.")
            return want
        log(f"seed {want} -> {outcome}; scanning other seeds ...")
    for s in range(7, 80):
        _, outcome = capture_run(s)
        if outcome == "SURVIVED":
            log(f"seed {s} survives - using it.")
            return s
        log(f"seed {s} -> {outcome}")
    raise SystemExit("no surviving seed in 7..79")


def build() -> None:
    import argparse
    global FPS
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", type=str, default=str(OUT_DEFAULT))
    ap.add_argument("--max-acts", type=int, default=0)
    ap.add_argument("--only-last", type=int, default=0)
    ap.add_argument("--fps", type=int, default=FPS)
    args = ap.parse_args()

    FPS = args.fps

    seed = pick_seed(args.seed)
    log("final capture pass ...")
    acts, outcome = capture_run(seed)
    assert outcome == "SURVIVED", outcome
    cols_max = max(len(ANSI.sub("", ln)) for a in acts for ln in a.lines)
    rows_max = max(a.n_rows for a in acts)
    log(f"acts={len(acts)}  cols={cols_max}  rows_max={rows_max}")
    if args.max_acts:
        acts = acts[:args.max_acts]
        log(f"--max-acts: rendering only first {len(acts)} acts (test render)")
    if args.only_last:
        acts = acts[-args.only_last:]
        log(f"--only-last: rendering only last {len(acts)} acts (test render)")

    out_video = pathlib.Path(args.out).with_suffix(".silent.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{CANW}x{CANH}", "-r", str(FPS), "-i", "pipe:0",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-fps_mode", "cfr",
           "-movflags", "+faststart", str(out_video)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    comp = Composer(proc.stdin)
    comp.last = Image.new("RGB", (CANW, CANH), (0, 0, 0))

    t0 = time.time()
    try:
        total, idx = 0, 0
        prev_img = None
        for act in acts:
            n = comp.act_frames(act, prev_img, total / FPS)
            prev_img = comp.last
            total += n
            idx += 1
            if idx % 10 == 0 or idx == len(acts):
                rate = total / max(1e-3, time.time() - t0)
                log(f"act {idx}/{len(acts)}  t={total / FPS:6.1f}s  "
                    f"out_fps={rate:4.1f}")
        fadeout_frames(comp, FADE_OUT)
        total += int(FADE_OUT * FPS)
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.wait()
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg failed ({proc.returncode})")
    dur = total / FPS
    log(f"silent video: {out_video.name}  {dur:.1f}s / {total} frames "
        f"(encode wall {time.time() - t0:.0f}s)")

    # -- mux the anthem --
    final = pathlib.Path(args.out)
    anthem = find_anthem()
    if anthem is None:
        shutil.move(str(out_video), str(final))
        mb = final.stat().st_size / 1e6
        log(f"DONE -> {final.name}  ({mb:.1f} MB, {dur:.1f}s, {FPS} fps, silent — "
            f"no soundtrack found in 'edit video/')")
        return
    loop = ["-stream_loop", "-1"] if dur > 224 else []
    af = f"afade=t=out:st={max(0.0, dur - 3.6)}:d=3.6"
    cmd2 = (["ffmpeg", "-y", "-loglevel", "error", "-i", str(out_video)]
            + loop + ["-i", str(ANTHEM),
                      "-map", "0:v:0", "-map", "1:a:0",
                      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                      "-af", af, "-t", f"{dur:.3f}",
                      "-movflags", "+faststart", str(final)])
    subprocess.run(cmd2, check=True)
    out_video.unlink(missing_ok=True)
    mb = final.stat().st_size / 1e6
    log(f"DONE -> {final.name}  ({mb:.1f} MB, {dur:.1f}s, {FPS} fps, anthem muxed)")

if __name__ == "__main__":
    build()
