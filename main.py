#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kreml_1991 v3 — General Secretary: A Soviet Union alternate-history simulator.

Run:
    python main.py                   # normal game
    python main.py --drama           # slow typewriter printing
    python main.py --seed 42         # fixed randomness
    python main.py --mode easy       # SWEEPING REFORMS | BALANCED | IRON GRASP

(The v1 single-file version is kept for reference in v1_kreml.py.)
"""
from __future__ import annotations

import sys

from kreml import engine, ui

VALID_MODES = ("easy", "normal", "hard")


def parse_args(argv: list[str]) -> tuple[int | None, str | None]:
    seed: int | None = None
    mode: str | None = None
    if "--drama" in argv:
        ui.DRAMA = True
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
    return seed, mode


def main() -> None:
    seed, mode = parse_args(sys.argv[1:])
    try:
        engine.run(seed, mode=mode)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
