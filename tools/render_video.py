"""Render a captured terminal log to a stylised CRT-ish gameplay video.

Frames are split at every year marker, parsed with a tiny ANSI parser,
drawn to PNG (Consolas grid + Segoe UI Symbol for ☭★⚑✖✔❯⧗), then muxed
with ffmpeg's concat demuxer.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import pathlib

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

WINF = r"C:\Windows\Fonts"
MAIN_FONT = os.path.join(WINF, "consola.ttf")
MAIN_BOLD = os.path.join(WINF, "consolab.ttf")
SYM_FONT = os.path.join(WINF, "seguisym.ttf")

FONT_SIZE = 20
CELL_W = 13
CELL_H = 27
PAD = 14

BG = (12, 12, 15)

# game codes → RGB
PAL = {
    "90": (110, 110, 120),   # dim
    "91": (255, 82, 82),     # bright red
    "92": (90, 240, 110),    # green
    "93": (250, 224, 110),   # yellow
    "94": (110, 150, 255),   # blue
    "95": (240, 120, 240),   # magenta
    "96": (110, 240, 240),   # cyan
    "97": (238, 238, 244),   # white
    "31": (205, 60, 60),
    "32": (70, 200, 80),
    "33": (215, 195, 70),
    "34": (90, 120, 230),
    "35": (200, 90, 200),
    "36": (70, 190, 190),
    "37": (225, 225, 230),
}
DEFAULT_FG = (200, 200, 210)

YEAR_MARKER = re.compile(r"\n(?:\x1b\[\d+m)*\s*☭\s*(\d{4})\s*☭")
ANSI = re.compile(r"\x1b\[(\d+)m")
SUB_CUTS = (
    re.compile(r"(?=\x1b\[1m  ── PERSONAL FOCUS)"),
    re.compile(r"(?=\x1b\[1m  ── YEARLY DIRECTIVE)"),
    re.compile(r"(?=\x1b\[1m  ┌─)"),
)


def _cmap_covered(path: str) -> set:
    t = TTFont(path)
    return set(t.getBestCmap().keys())


MAIN_COVER = _cmap_covered(MAIN_FONT)
SYM_COVER = _cmap_covered(SYM_FONT)


def parse_line(line: str) -> list:
    """[(char, rgb, bold)] for one line with ANSI state tracking."""
    cells, bold, fg = [], False, DEFAULT_FG
    pos = 0
    for m in ANSI.finditer(line):
        chunk = line[pos:m.start()]
        for ch in chunk:
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
    return cells


def _title_card(seed: int) -> str:
    a = "\x1b[91m"
    w = "\x1b[97m"
    d = "\x1b[90m"
    b = "\x1b[1m"
    return (
        f"{b}{a}\n        ★  ☭  ★\n   К Р Е М Л Ь\n      1 9 9 1\x1b[0m\n\n"
        f"{b}{w}   G A M E P L A Y   R E C O R D I N G\x1b[0m\n\n"
        f"{d}   {a}☭{d} Kremlin v5 · seed {seed} · BALANCED · autopilot: market path\n"
        f"   {a}☭{d} Generous Secretary: Nikolai Vetrov, 1964 → 1991 (or 2001)\x1b[0m\n\n\n\n\n\n"
    )


def split_frames(text: str, seed: int) -> list:
    """[(image_text, duration_seconds)]"""
    frames = [(_title_card(seed), 3.4)]
    marks = list(YEAR_MARKER.finditer(text))
    first = marks[0].start() if marks else len(text)
    frames.append((text[:first], 3.2))                        # title intro
    for i, m in enumerate(marks):
        start = m.start()                                     # keep the marker line
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        chunk = text[start:end]
        # break the year into focus / directive / event scenes
        parts = [chunk]
        for rx in SUB_CUTS:
            nxt = []
            for p in parts:
                nxt.extend(x for x in rx.split(p) if x.strip())
            parts = nxt
        last_of_game = i == len(marks) - 1
        for j, part in enumerate(parts):
            if not part.strip():
                continue
            is_ending = last_of_game and j == len(parts) - 1
            dur = 6.5 if is_ending else (1.1 if j == 0 else (1.7 if j > 1 else 1.4))
            frames.append((part, dur))
    return frames


def render_frame(cells_per_line: list, cols: int, rows: int, path: str) -> None:
    W = cols * CELL_W + PAD * 2
    H = rows * CELL_H + PAD * 2
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    mono_r = ImageFont.truetype(MAIN_FONT, FONT_SIZE)
    mono_b = ImageFont.truetype(MAIN_BOLD, FONT_SIZE)
    sym = ImageFont.truetype(SYM_FONT, FONT_SIZE - 4)
    for r, cells in enumerate(cells_per_line):
        for c, (ch, rgb, bold) in enumerate(cells):
            if ch == " " or ch == "":
                continue
            x = PAD + c * CELL_W
            y = PAD + r * CELL_H + 1
            if ord(ch) in MAIN_COVER:
                d.text((x, y), ch, font=mono_b if bold else mono_r, fill=rgb)
            elif ord(ch) in SYM_COVER:
                try:
                    bb = sym.getbbox(ch)
                except Exception:
                    bb = None
                if bb:
                    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
                    dx = x + max(0, (CELL_W - gw) // 2) - bb[0]
                    dy = y + max(0, (CELL_H - gh) // 2) - bb[1]
                    d.text((dx, dy), ch, font=sym, fill=rgb)
    img.save(path)


def render_video(text: str, seed: int) -> str:
    repo = pathlib.Path(__file__).resolve().parent.parent
    frames_dir = repo / "tools" / "frames"
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    frames = split_frames(text, seed)
    widths, heights = [], []
    parsed = []
    for ftext, dur in frames:
        lines = [parse_line(ln) for ln in ftext.split("\n")]
        cols = max((len(c) for c in lines), default=10)
        widths.append(cols)
        heights.append(len(lines))
        parsed.append((lines, cols, len(lines), dur))
    cols = max(min(max(widths), 160), 90)     # widen to fit, don't truncate
    rows = max(min(max(heights), 58), 40)

    paths = []
    for i, (lines, cw, lh, dur) in enumerate(parsed):
        pad_bottom = [""] * (rows - lh) if lh < rows else []
        pad_side = (cols,) * 0  # width fixed via cols clamp
        asset = str(frames_dir / f"f{i:03d}.png")
        clamped = [ln[:cols] for ln in lines] + [parse_line("") for _ in pad_bottom]
        render_frame(clamped, cols, rows, asset)
        paths.append((asset, dur))

    # ffmpeg concat list
    lst = frames_dir / "list.ffmpeg"
    with open(lst, "w", encoding="utf8") as f:
        f.write("ffconcat version 1.0\n")
        for asset, dur in paths:
            f.write(f"file '{pathlib.Path(asset).name}'\nduration {dur}\n")
        f.write(f"file '{pathlib.Path(paths[-1][0]).name}'\n")
    out = repo / "gameplay_v3.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
           "-i", str(lst), "-vf",
           "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=8,format=yuv420p",
           "-c:v", "libx264", "-crf", "21", "-preset", "medium",
           str(out)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"video written: {out}  ({out.stat().st_size / 1e6:.1f} MB, "
          f"{len(paths)} scenes)")
    return str(out)
