#!/usr/bin/env python3
"""Package the browser build for itch.io.

itch.io accepts an HTML game as a zip whose **root** holds ``index.html``. The
GitHub Pages copy cannot be zipped as-is: it links its stylesheets as
``../assets/``, which does not exist inside a zip. This script copies the page
and its runtime, rewrites those links to a local ``assets/`` folder, and writes
``itch_upload/kreml-1991-web.zip``.

Run it after ``python tools/build_web.py`` (or just run this script; it checks
the bundle is present):

    python tools/build_itch.py

Upload the zip at https://itch.io/game/new (project kind: HTML). The public page
URL is set in ``docs/index.html`` and ``docs/play/index.html``; the paste-ready
form copy, cover and screenshots live in ``itch_page/``.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parent.parent
PLAY = REPO / "docs" / "play"
ASSETS = REPO / "docs" / "assets"
OUT_ROOT = REPO / "itch_upload"
OUT = OUT_ROOT / "kreml-1991-web"
ZIP = OUT_ROOT / "kreml-1991-web.zip"
WEB = "https://mahakammoonlightstudio-beep.github.io/kreml-1991/"
RUNTIME = ("app.js", "game_bundle.js", "kreml_web.py")
STYLES = ("fonts.css", "tokens.css", "base.css")
BRAND = ("favicon.svg", "favicon-32.png", "favicon.ico", "icon-192.png",
         "icon-512.png", "apple-touch-icon.png", "site.webmanifest")


def page_html() -> str:
    html = (PLAY / "index.html").read_text(encoding="utf-8")
    html = html.replace('href="../assets/', 'href="assets/')
    html = html.replace('src="../assets/', 'src="assets/')
    html = html.replace('href="../index.html#support"', f'href="{WEB}#support"')
    html = html.replace('href="../index.html"', f'href="{WEB}"')
    html = html.replace("<body>", '<body class="itch-build">')
    marker = "</footer>"
    note = ('<p class="itch-note" style="margin-top:12px">itch.io build of '
            f'<a href="{WEB}">КРЕМЛЬ 1991</a>. The GitHub Pages copy is the same game.</p>\n')
    return html.replace(marker, note + marker)


def build() -> int:
    missing = [name for name in ("index.html", *RUNTIME) if not (PLAY / name).is_file()]
    if missing:
        print(f"missing in docs/play: {missing}", file=sys.stderr)
        return 1

    OUT_ROOT.mkdir(exist_ok=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    if ZIP.exists():
        ZIP.unlink()
    (OUT / "assets").mkdir(parents=True)

    (OUT / "index.html").write_text(page_html(), encoding="utf-8", newline="\n")
    for name in RUNTIME:
        shutil.copy2(PLAY / name, OUT / name)
    for name in STYLES + BRAND:
        shutil.copy2(ASSETS / name, OUT / "assets" / name)

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
