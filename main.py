#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kreml_1991 v5 — General Secretary: A Soviet Union alternate-history simulator.

Run:
    python main.py                        # normal game (asks difficulty + timeline)
    python main.py --drama                # slow typewriter printing
    python main.py --seed 42              # fixed randomness
    python main.py --mode medium          # easy | medium | hard | extreme | historical
    python main.py --timeline flashpoint  # rails | reform | flashpoint | millennium
    python main.py --no-anim              # plain text (no bars/animations)
    python main.py --timed                # v6: decisions run on a wall clock

(The v1 single-file version is kept for reference in v1_kreml.py.)
"""
from __future__ import annotations

import sys

from kreml import engine, ui
from kreml.content.modes import MODE_ORDER
from kreml.content.timelines import TIMELINE_ORDER

VALID_MODES = tuple(MODE_ORDER) + ("normal",)      # "normal" is the v4 alias of medium


def parse_args(argv: list[str]) -> tuple[int | None, str | None, str | None]:
    seed: int | None = None
    mode: str | None = None
    timeline: str | None = None
    if "--drama" in argv:
        ui.DRAMA = True
    if "--no-anim" in argv:
        ui.ANIM = False
    if "--anim" in argv:
        ui.ANIM = True
    # v6: the wall clock. Opt-in on purpose: pipes, tests, recorders and the
    # browser build must stay deterministic, so nothing times out by accident.
    if "--timed" in argv:
        ui.TIMED = True
    if "--no-timed" in argv:
        ui.TIMED = False
    for flag in ("-seed", "--seed"):
        if flag in argv:
            idx = argv.index(flag)
            try:
                seed = int(argv[idx + 1])
            except (IndexError, ValueError):
                pass
    for flag in ("-mode", "--mode"):
        if flag in argv:
            idx = argv.index(flag)
            if idx + 1 < len(argv) and argv[idx + 1].lower() in VALID_MODES:
                mode = argv[idx + 1].lower()
    for flag in ("-timeline", "--timeline"):
        if flag in argv:
            idx = argv.index(flag)
            if idx + 1 < len(argv) and argv[idx + 1].lower() in TIMELINE_ORDER:
                timeline = argv[idx + 1].lower()
    return seed, mode, timeline


HELP = """КРЕМЛЬ 1991 v6 — General Secretary

Usage: python main.py [flags]

  --mode <easy|medium|hard|extreme|flash|historical>
  --timeline <rails|reform|flashpoint|millennium>
  --seed <int>     reproducible run
  --timed          decisions run on a wall clock (flash crises breathe)
  --no-timed       force the clock off (default)
  --anim/--no-anim terminal visuals on/off
  --drama          slow typewriter printing

At the year boundary: s save · l load · d dossier · i political capital ·
                     o standing order · q resign
"""


def main() -> None:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(HELP)
        return
    seed, mode, timeline = parse_args(sys.argv[1:])
    try:
        engine.run(seed, mode=mode, timeline=timeline)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
