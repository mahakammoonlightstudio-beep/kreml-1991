#!/usr/bin/env python3
"""Capture the itch page screenshots from the real v8 situation room.

The earlier stills (tools/capture_stills.py) are terminal plates: the itch build
is pure play, so its page should show the thing players actually see — the
browser room, HUD and challenge card.

This tool does not invent a screen. It:

  1. replays the seed-7 autopilot in CPython and records every (prompt, answer),
  2. re-runs that answer list through docs/play/kreml_web.py — the same driver
     the browser uses — to prove the run arrives at the same states and to find
     the five screenshot moments,
  3. serves itch_upload/kreml-1991-web over http and drives the real page in
     headless Chromium, answering with those exact lines,
  4. writes 1600×900 PNGs into itch_page/screenshots/.

    python tools/build_itch.py          # refresh the exported build first
    python tools/capture_room.py        # capture
    python tools/capture_room.py --dry  # offline alignment check, no browser

Requires Playwright (``python -m pip install playwright`` then
``python -m playwright install chromium``). The page pulls Pyodide from a CDN,
so the first boot needs network.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import pathlib
import socketserver
import subprocess
import sys
import tempfile
import threading

from PIL import Image

REPO = pathlib.Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
PLAY = REPO / "docs" / "play"
BUILD = REPO / "itch_upload" / "kreml-1991-web"
OUT = REPO / "itch_page" / "screenshots"
SEED = 7
VIEW = {"width": 1600, "height": 900}
# The card prints location.origin, which is 127.0.0.1 when captured locally.
# Swap in the public play URL so the still shows the link a player would share.
PUBLIC_CARD = ("mahakammoonlightstudio-beep.github.io/kreml-1991/play/"
               "?seed=7&mode=medium&timeline=rails")

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(PLAY))

SKIP_PROMPTS = ("How harsh", "Which timeline", "Resume")


# ─────────────────────── 1. the autopilot's answers ────────────────────

def _record(seed: int, tutorial: bool) -> list[list[str]]:
    """Child-process body: run the autopilot and return (prompt, answer)."""
    sys.path.insert(0, str(TOOLS))
    import record_gameplay as RG
    from kreml import persistence
    from kreml.content import endings

    tmp = tempfile.mkdtemp()
    persistence.SAVE_FILE = os.path.join(tmp, "save.json")
    endings.HALL_FILE = os.path.join(tmp, "hall.txt")

    pairs: list[list[str]] = []
    original = RG.bot_input

    def rec(prompt: str = "") -> str:
        answer = original(prompt)
        pairs.append([prompt, answer])
        return answer

    RG.bot_input = rec
    try:
        RG.run_bot(seed, tutorial=tutorial)
    finally:
        RG.bot_input = original
    return pairs


def answers(seed: int, tutorial: bool) -> list[str]:
    """The autopilot's lines, minus prompts the browser setup skips."""
    raw = subprocess.run(
        [sys.executable, str(pathlib.Path(__file__).resolve()),
         "--record", str(seed), "--tutorial", "1" if tutorial else "0"],
        capture_output=True, text=True, check=True, timeout=300,
    )
    pairs = json.loads(raw.stdout)
    return [a for p, a in pairs if not any(k in p for k in SKIP_PROMPTS)]


# ─────────────────────── 2. replay through the web driver ──────────────

def replay(lines: list[str], tutorial: bool) -> list[str]:
    """Feed the lines to the browser driver; returns the transcript per step."""
    import kreml_web

    tmp = tempfile.mkdtemp()
    from kreml import persistence
    from kreml.content import endings
    persistence.SAVE_FILE = os.path.join(tmp, "save.json")
    endings.HALL_FILE = os.path.join(tmp, "hall.txt")

    session = kreml_web.Session(game_root=str(REPO), seed=SEED)
    session.start("medium", "rails", tutorial=tutorial)
    states = [session.transcript]
    for line in lines:
        session.answer(line)
        states.append(session.transcript)
    if "Traceback" in states[-1]:
        raise SystemExit("the replay crashed — check the answer alignment")
    return states


def marks_for(states: list[str], tutorial: bool) -> dict[str, int]:
    """Answer index after which each screenshot is taken."""
    found: dict[str, int] = {}
    if tutorial:
        # Prefer the guided first year: the room has numbers by then, and the
        # margin note is the tutorial doing its job, not an empty HUD.
        for needle in ("ORIENTATION: drift applies", "MEMO · 05"):
            for i, text in enumerate(states):
                if needle in text:
                    found["05-tutorial.png"] = i - 1
                    break
            if "05-tutorial.png" in found:
                break
        if "05-tutorial.png" not in found:
            raise SystemExit("tutorial moment never appeared")
        return found

    for i, text in enumerate(states):
        if "02-directive.png" not in found and "Directive of the year:" in text[-400:]:
            found["02-directive.png"] = i - 1
        if "01-board.png" not in found:
            lines = text[-600:].splitlines()
            at_bar = bool(lines) and "[Enter] proceed" in lines[-1]
            years = [y for y in ("1975", "1976", "1977", "1978")
                     if f"YEAR {y}" in text]
            if at_bar and years:
                found["01-board.png"] = i - 1

    found["03-ending.png"] = len(states) - 2
    for name in ("01-board.png", "02-directive.png", "03-ending.png"):
        if name not in found:
            raise SystemExit(f"could not find a moment for {name}")
    return found


# ─────────────────────── 3. drive the real itch build ─────────────────

class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):        # keep the console readable
        pass


def serve(root: pathlib.Path) -> tuple[socketserver.TCPServer, str]:
    # Threaded on purpose: Chrome opens idle preconnects, and a single-threaded
    # server can park on one of them while Pyodide waits for its files.
    handler = functools.partial(_Quiet, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    return server, f"http://127.0.0.1:{port}/index.html"


def send(page, text: str, final: bool = False) -> None:
    page.wait_for_function(
        "() => !document.getElementById('line').disabled", timeout=180_000)
    before = page.eval_on_selector("#screen", "el => el.textContent.length")
    page.fill("#line", text)
    page.press("#line", "Enter")
    if final:
        page.wait_for_selector("#challenge:not([hidden])", timeout=180_000)
        return
    page.wait_for_function(
        "n => document.getElementById('screen').textContent.length > n"
        " && !document.getElementById('line').disabled",
        arg=before, timeout=180_000)


def settle_scroll(page) -> None:
    """Wait until window.scrollY stops moving (the app uses smooth scrolling)."""
    last, stable = None, 0
    for _ in range(40):
        y = page.evaluate("window.scrollY")
        stable = stable + 1 if y == last else 0
        if stable >= 2:
            return
        last = y
        page.wait_for_timeout(120)


def shoot_region(page, name: str, selector: str) -> None:
    """Crop a section out of a full-page shot.

    locator.screenshot() clips to the layout box and can slice a rotated card;
    a full-page capture plus an explicit crop keeps the whole section.
    """
    box = page.evaluate(
        "sel => { const el = document.querySelector(sel);"
        " const r = el.getBoundingClientRect();"
        " return { x: Math.floor(r.left + window.scrollX),"
        "          y: Math.floor(r.top + window.scrollY),"
        "          w: Math.ceil(r.width),"
        "          h: Math.ceil(Math.max(r.height, el.scrollHeight)) + 12 }; }",
        selector)
    full = OUT / "_full.png"
    page.screenshot(path=str(full), full_page=True)
    image = Image.open(full)
    image.crop((max(0, box["x"]), max(0, box["y"]),
                min(image.width, box["x"] + box["w"]),
                min(image.height, box["y"] + box["h"]))).save(OUT / name)
    full.unlink()
    print(f"{name:22} {pathlib.Path(OUT / name).stat().st_size // 1024} KB")


def shoot(page, name: str, anchor: str) -> None:
    """Shoot one section whole: the itch room stacks, so a viewport would clip it."""
    page.evaluate("() => document.fonts.ready.then(() => true)")
    settle_scroll(page)                  # the app scrolls smoothly; let it stop
    page.wait_for_timeout(350)
    page.locator(anchor).screenshot(path=str(OUT / name))
    print(f"{name:22} {pathlib.Path(OUT / name).stat().st_size // 1024} KB")


CAPTURE_CSS = """
.playbar { position: static !important; }   /* stop it bleeding into tall shots */
body { padding-bottom: 140px; }            /* room for the last section's box */
"""


def drive(page, url: str, lines: list[str], marks: dict[str, int],
          tutorial: bool) -> None:
    for attempt in (1, 2):
        page.goto(url, wait_until="domcontentloaded")
        page.add_style_tag(content=CAPTURE_CSS)
        try:
            page.wait_for_selector("#start:not([disabled])", timeout=240_000)
            break
        except Exception:
            if attempt == 2:
                note = page.eval_on_selector("#bootnote", "el => el.textContent")
                raise SystemExit(f"Pyodide never booted: {note}")
            print("boot timed out, retrying", flush=True)

    if tutorial:
        page.click("#start")
        page.wait_for_selector("#game:not([hidden])", timeout=60_000)
        for i, line in enumerate(lines):
            final = i == len(lines) - 1
            send(page, line, final=final)
            if i == marks.get("05-tutorial.png"):
                shoot(page, "05-tutorial.png", "#game")
        return

    shoot(page, "04-title.png", "main")
    page.click("#start")
    page.wait_for_selector("#game:not([hidden])", timeout=60_000)

    for i, line in enumerate(lines):
        final = i == len(lines) - 1
        send(page, line, final=final)
        if marks["01-board.png"] == i:
            shoot(page, "01-board.png", "#game")
        if marks["02-directive.png"] == i:
            shoot(page, "02-directive.png", "#game")
        if marks["03-ending.png"] == i:
            page.evaluate(
                "u => { const el = document.getElementById('card-url');"
                " if (el) el.textContent = u; }", PUBLIC_CARD)
            page.evaluate("() => document.fonts.ready.then(() => true)")
            settle_scroll(page)
            page.wait_for_timeout(350)
            shoot_region(page, "03-ending.png", "#challenge")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry", action="store_true",
                        help="check the answer alignment without a browser")
    parser.add_argument("--record", type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument("--tutorial", default="0", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.record:                       # child-process recording mode
        pairs = _record(args.record, args.tutorial == "1")
        print(json.dumps(pairs))
        return 0

    if not (BUILD / "index.html").is_file():
        print("missing itch build — run python tools/build_itch.py", flush=True)
        return 1

    main_lines = answers(SEED, tutorial=False)
    states = replay(main_lines, tutorial=False)
    marks = marks_for(states, tutorial=False)
    print(f"main run: {len(main_lines)} answers, "
          f"{'survived' if 'Legacy score' in states[-1] else 'ended'}")
    print("moments:", ", ".join(f"{k}@{v}" for k, v in sorted(marks.items())))

    tut_lines = answers(SEED, tutorial=True)
    tut_states = replay(tut_lines, tutorial=True)
    tut_marks = marks_for(tut_states, tutorial=True)
    print(f"tutorial: {len(tut_lines)} answers, "
          f"memo at {tut_marks['05-tutorial.png']}")

    if args.dry:
        return 0

    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    server, url = serve(BUILD)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport=VIEW, device_scale_factor=1)
            page.set_default_timeout(60_000)
            drive(page, f"{url}?seed={SEED}&mode=medium&timeline=rails",
                  main_lines, marks, tutorial=False)
            drive(page,
                  f"{url}?seed={SEED}&mode=medium&timeline=rails&tutorial=1",
                  tut_lines, tut_marks, tutorial=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
