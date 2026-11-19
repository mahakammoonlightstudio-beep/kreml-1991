#!/usr/bin/env python3
"""Package the browser build for itch.io — the pure-play edition.

itch.io accepts an HTML game as a zip whose **root** holds ``index.html``. The
GitHub Pages copy cannot be zipped as-is: it links its stylesheets and
photograph as ``../assets/`` and ``../media/``, which do not exist inside a zip.
This script copies the page and its runtime, rewrites those links to local
``assets/`` and ``media/`` folders, adds the ``itch-build`` body class (which
strips the landing-page chrome), and writes ``itch_upload/kreml-1991-web.zip``.

Run it after ``python tools/build_web.py``:

    python tools/build_itch.py

Upload the zip as an **HTML** project. The paste-ready form copy, cover and
screenshots live in ``itch_page/``.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import zipfile

REPO = pathlib.Path(__file__).resolve().parent.parent
PLAY = REPO / "docs" / "play"
ASSETS = REPO / "docs" / "assets"
MEDIA = REPO / "docs" / "media"
OUT_ROOT = REPO / "itch_upload"
OUT = OUT_ROOT / "kreml-1991-web"
ZIP = OUT_ROOT / "kreml-1991-web.zip"
WEB = "https://mahakammoonlightstudio-beep.github.io/kreml-1991/"
RUNTIME = ("app.js", "game_bundle.js", "kreml_web.py")
STYLES = ("fonts.css", "editorial.css")
BRAND = ("favicon.svg", "favicon-32.png", "favicon.ico", "icon-192.png",
         "icon-512.png", "apple-touch-icon.png", "site.webmanifest")
PHOTOS = ("kremlin_1991.jpg",)
FONT_DIR = ASSETS / "fonts"


def page_html() -> str:
    html = (PLAY / "index.html").read_text(encoding="utf-8")
    # Localise every relative asset used by the play page.
    for prefix in ("assets", "media"):
        html = html.replace(f'href="../{prefix}/', f'href="{prefix}/')
        html = html.replace(f'src="../{prefix}/', f'src="{prefix}/')
    # Point the case-file links back at the public GitHub page.
    html = html.replace('href="../index.html#support"', f'href="{WEB}#support"')
    html = html.replace('href="../index.html"', f'href="{WEB}"')
    # The itch edition is the game alone: no landing, support or source chrome.
    if "itch-build" not in html:
        html = re.sub(r'<body class="([^"]*)"',
                      lambda m: f'<body class="{m.group(1)} itch-build"',
                      html, count=1)
    return html


def build() -> int:
    missing = [name for name in ("index.html", *RUNTIME)
               if not (PLAY / name).is_file()]
    if missing:
        print(f"missing in docs/play: {missing}", flush=True)
        return 1
    if not FONT_DIR.is_dir():
        print("missing docs/assets/fonts — run the asset copy first", flush=True)
        return 1

    OUT_ROOT.mkdir(exist_ok=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    if ZIP.exists():
        ZIP.unlink()
    (OUT / "assets").mkdir(parents=True)
    (OUT / "media").mkdir(parents=True)

    (OUT / "index.html").write_text(page_html(), encoding="utf-8", newline="\n")
    for name in RUNTIME:
        shutil.copy2(PLAY / name, OUT / name)
    for name in STYLES + BRAND:
        shutil.copy2(ASSETS / name, OUT / "assets" / name)
    shutil.copytree(FONT_DIR, OUT / "assets" / "fonts")
    for name in PHOTOS:
        shutil.copy2(MEDIA / name, OUT / "media" / name)

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(OUT).as_posix())

    size = ZIP.stat().st_size / (1024 * 1024)
    print(f"wrote {OUT.relative_to(REPO).as_posix()}/ "
          f"({len(list(OUT.rglob('*')))} entries)")
    print(f"wrote {ZIP.relative_to(REPO).as_posix()} ({size:.1f} MB)")
    print("Upload the zip as an HTML project; index.html sits at the root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
