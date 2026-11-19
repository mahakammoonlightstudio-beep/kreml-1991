#!/usr/bin/env python3
"""Render the five itch.io screenshots from a real v8 playthrough.

The old JPGs in docs/media were captured in v4 and show the wrong interface.
This tool replays the deterministic autopilot run with seed 7, picks the title,
board, directive and ending screens, plus a second tutorial run for the
First-Year Orientation memo, and writes 1600×900 stills into
``itch_page/screenshots/``.

    python tools/capture_stills.py

Requires Pillow and the Windows console fonts used by the renderer (the same
requirements as tools/render_gameplay.py). No ffmpeg is needed for stills.
"""
from __future__ import annotations

import pathlib
import re
import sys

from PIL import Image, ImageDraw

REPO = pathlib.Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
OUT = REPO / "itch_page" / "screenshots"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO))

import render_gameplay as R  # noqa: E402

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(text: str) -> str:
    return ANSI.sub("", text)


def pick(acts: list, needle: str, field: str = "raw"):
    for act in acts:
        value = act.raw if field == "raw" else (act.prompt or "")
        if needle in plain(value):
            return act
    raise SystemExit(f"no act containing {needle!r}")


def still(act, name: str, top: int = 0, rows: int = R.ROWS) -> None:
    """Crop the content box from the act's plate and centre it on 1600×900."""
    plate = R.plate_for(act)
    take = min(rows, act.n_rows - top)
    content_w = R.COLS * R.CELL_W + 2 * R.PADX
    crop = plate.crop((
        0,
        R.PADY + top * R.CELL_H,
        content_w,
        R.PADY + (top + take) * R.CELL_H,
    ))
    canvas = Image.new("RGB", (R.CANW, R.CANH), R.BG)
    x = (R.CANW - content_w) // 2
    y = (R.CANH - crop.height) // 2
    canvas.paste(crop, (x, y))
    ImageDraw.Draw(canvas).rectangle(
        (x - 1, y - 1, x + content_w, y + crop.height),
        outline=(58, 52, 44), width=1)
    canvas.save(OUT / name, optimize=True)
    print(f"{name:22} {canvas.width}x{canvas.height}  {take} rows")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    hall = REPO / "hall_of_fame.txt"
    backup = hall.read_bytes() if hall.exists() else None
    R.COLS = 140               # fewer wraps on a 1600px screenshot
    try:
        acts, outcome = R.capture_run(7)
        if outcome != "SURVIVED":
            raise SystemExit(f"seed 7 ended as {outcome}; pick a surviving seed")
        title = acts[0]
        board = pick(acts, "PERSONAL FOCUS")
        directive = pick(acts, "Directive of the year", "prompt")
        ending = next(a for a in reversed(acts) if a.kind == "final")

        tutorial_acts, _ = R.capture_run(7, tutorial=True)
        tutorial = pick(tutorial_acts, "MEMO · 05 / THE FIRST-YEAR ARITHMETIC")

        still(title, "04-title.png")
        still(board, "01-board.png", top=0, rows=R.ROWS)
        still(directive, "02-directive.png")
        still(ending, "03-ending.png", top=max(0, ending.n_rows - R.ROWS))
        still(tutorial, "05-tutorial.png", top=0, rows=R.ROWS)
    finally:
        try:
            (REPO / "kreml_save.json").unlink()
        except OSError:
            pass
        if backup is not None:
            hall.write_bytes(backup)
        elif hall.exists():
            hall.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
