"""The browser build ships a copy of the game; this test keeps it honest.

GitHub Pages serves `docs/` only, so `docs/play/game_bundle.js` carries
`main.py` + every `kreml/**.py` file to the browser. If someone edits the game
and forgets `python tools/build_web.py`, the page would quietly play an old
game — this check fails instead.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAY = os.path.join(ROOT, "docs", "play")
BUNDLE = os.path.join(PLAY, "game_bundle.js")

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"[PASS] {name}")
    except AssertionError as exc:
        FAIL.append(name)
        print(f"[FAIL] {name}: {exc}")


def load_bundle() -> dict:
    with open(BUNDLE, encoding="utf-8") as f:
        text = f.read()
    marker = "self.KREML_BUNDLE = "
    start = text.index(marker) + len(marker)
    end = text.rindex(";")
    return json.loads(text[start:end])


def expected_files() -> list[str]:
    files = ["main.py"]
    for base, _dirs, names in os.walk(os.path.join(ROOT, "kreml")):
        for name in sorted(names):
            if name.endswith(".py"):
                rel = os.path.relpath(os.path.join(base, name), ROOT)
                files.append(rel.replace(os.sep, "/"))
    return sorted(files)


def t_bundle_exists() -> None:
    assert os.path.isfile(BUNDLE), "docs/play/game_bundle.js is missing"


def t_bundle_covers_every_source() -> None:
    bundle = load_bundle()
    wanted = expected_files()
    missing = [p for p in wanted if "/game/" + p not in bundle]
    assert not missing, f"not bundled: {missing[:5]} — run python tools/build_web.py"
    extra = [k for k in bundle if k[len("/game/"):] not in wanted]
    assert not extra, f"stale files in the bundle: {extra[:5]}"


def t_bundle_matches_the_sources() -> None:
    bundle = load_bundle()
    stale = []
    for path in expected_files():
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            if bundle.get("/game/" + path) != f.read():
                stale.append(path)
    assert not stale, (f"{len(stale)} file(s) out of date (e.g. {stale[:3]}) — "
                       "run python tools/build_web.py")


def t_page_assets_exist() -> None:
    with open(os.path.join(PLAY, "index.html"), encoding="utf-8") as f:
        html = f.read()
    for name in re.findall(r'(?:src|href)="([^"#:]+\.(?:js|py|css))"', html):
        if name.startswith("http"):
            continue
        assert os.path.isfile(os.path.join(PLAY, name)), f"index.html points at missing {name}"
    for name in ("app.js", "kreml_web.py", "game_bundle.js"):
        assert os.path.isfile(os.path.join(PLAY, name)), f"{name} is missing"


def main() -> int:
    check("web bundle: file present", t_bundle_exists)
    check("web bundle: covers every game source", t_bundle_covers_every_source)
    check("web bundle: matches the sources byte for byte", t_bundle_matches_the_sources)
    check("web page: assets present", t_page_assets_exist)
    print()
    if FAIL:
        print(f"{len(FAIL)} failed, {len(PASS)} passed")
        return 1
    print(f"{len(PASS)}/{len(PASS)} web build checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
