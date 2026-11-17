#!/usr/bin/env python3
"""Render the brand assets from the HTML sources in ``tools/brand``.

The game's visual language lives in CSS, so the cover, social card and icon
are rendered with headless Chrome rather than hand-drawn with Pillow. That
keeps the Martian Mono wordmark and the paper/soot palette identical to the
site. Pillow only downsamples the square icon into the browser sizes.

    python tools/build_brand.py

Outputs:
    docs/assets/cover-630x500.png
    docs/assets/social-card-1200x630.png
    docs/assets/icon-192.png
    docs/assets/icon-512.png
    docs/assets/favicon-32.png
    docs/assets/favicon.ico
    docs/assets/apple-touch-icon.png
    itch_page/cover.png                (copy of the itch cover)
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

REPO = pathlib.Path(__file__).resolve().parent.parent
BRAND = REPO / "tools" / "brand"
ASSETS = REPO / "docs" / "assets"
ITCH = REPO / "itch_page"


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        str(pathlib.Path(os.environ.get("LOCALAPPDATA", "")) /
            "Google/Chrome/Application/chrome.exe"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).is_file():
            return str(candidate)
    raise SystemExit("Chrome not found. Set CHROME=/path/to/chrome and rerun.")


def render(html: pathlib.Path, out: pathlib.Path, width: int, height: int,
           chrome: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kreml-brand-") as profile:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            "--allow-file-access-from-files",
            "--force-device-scale-factor=1",
            "--virtual-time-budget=3000",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            f"--screenshot={out.resolve()}",
            html.resolve().as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out.is_file():
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-6:]
        raise SystemExit(f"Chrome could not render {html.name}:\n" + "\n".join(tail))
    with Image.open(out) as image:
        actual = image.size
    if actual != (width, height):
        raise SystemExit(f"{out.name}: expected {width}x{height}, got {actual}")


def icon_set(chrome: str) -> None:
    raw = ASSETS / "icon-512.png"
    render(BRAND / "icon.html", raw, 512, 512, chrome)
    with Image.open(raw) as source:
        icon = source.convert("RGBA")
    icon.resize((192, 192), Image.Resampling.LANCZOS).save(ASSETS / "icon-192.png")
    icon.resize((32, 32), Image.Resampling.LANCZOS).save(ASSETS / "favicon-32.png")
    icon.resize((180, 180), Image.Resampling.LANCZOS).save(
        ASSETS / "apple-touch-icon.png")
    icon.save(ASSETS / "favicon.ico",
              sizes=[(16, 16), (32, 32), (48, 48)])


def main() -> int:
    chrome = find_chrome()
    render(BRAND / "cover.html", ASSETS / "cover-630x500.png", 630, 500, chrome)
    render(BRAND / "social.html", ASSETS / "social-card-1200x630.png",
           1200, 630, chrome)
    icon_set(chrome)

    ITCH.mkdir(exist_ok=True)
    shutil.copy2(ASSETS / "cover-630x500.png", ITCH / "cover.png")

    for name in ("cover-630x500.png", "social-card-1200x630.png",
                 "icon-192.png", "icon-512.png", "favicon-32.png",
                 "favicon.ico", "apple-touch-icon.png"):
        path = ASSETS / name
        print(f"{path.relative_to(REPO).as_posix():44} {path.stat().st_size:>8,} B")
    print(f"{(ITCH / 'cover.png').relative_to(REPO).as_posix():44} "
          f"{(ITCH / 'cover.png').stat().st_size:>8,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
