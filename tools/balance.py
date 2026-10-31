#!/usr/bin/env python3
"""Measure balance headlessly: survival and score per mode.

The bot is `tools/record_gameplay.py`'s autopilot — it plays the market path and
weights each gauge by how low it is. It is **not** an optimal player, so read
these numbers as a floor, not as the game's ceiling. What the table is good for:
spotting a mode that is broken (nobody survives) or free (everybody survives).

    python tools/balance.py               # 6 modes x 5 seeds
    python tools/balance.py --seeds 20
    python tools/balance.py --timed       # arm the wall clock for every run
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import record_gameplay as RG                       # noqa: E402
from kreml import persistence, ui                  # noqa: E402
from kreml.content.modes import MODE_ORDER         # noqa: E402

HALL = REPO / "hall_of_fame.txt"
SCORE = re.compile(r"Legacy score: (\d+)")


def play(mode: str, seed: int) -> tuple[str, int]:
    """One full autopilot run in `mode`; returns (outcome, score)."""
    RG.OUTCOME.update({"survived": False, "collapsed": False, "retired": False})
    index = str(MODE_ORDER.index(mode) + 1)
    real_bot = RG.bot_input

    def bot(prompt: str = "") -> str:
        if "How harsh" in prompt:
            return index                 # pick this row's difficulty
        if "Which timeline" in prompt:
            return "1"
        return real_bot(prompt)

    RG.bot_input = bot
    try:
        # run_bot() captures the game's own output and hands it back; wrapping
        # it in another redirect would return an empty log and score 0.
        log = RG.run_bot(seed)
    finally:
        RG.bot_input = real_bot
    match = SCORE.search(log)
    score = int(match.group(1)) if match else 0
    outcome = ("SURVIVED" if RG.OUTCOME["survived"]
               else "COLLAPSED" if RG.OUTCOME["collapsed"] else "ENDED")
    return outcome, score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--timed", action="store_true",
                    help="arm the wall clock (the autopilot answers instantly)")
    ap.add_argument("--no-capital", action="store_true",
                    help="autopilot never spends influence (isolate its value)")
    ap.add_argument("--no-doctrine", action="store_true",
                    help="autopilot never adopts a standing order")
    args = ap.parse_args()
    RG.USE_CAPITAL = not args.no_capital
    RG.USE_DOCTRINE = not args.no_doctrine

    backup = HALL.read_bytes() if HALL.exists() else None
    ui.TIMED = bool(args.timed)
    print(f"clock: {'armed' if ui.TIMED else 'off'}   seeds: 1..{args.seeds}   "
          f"capital: {'on' if RG.USE_CAPITAL else 'off'}   "
          f"doctrine: {'on' if RG.USE_DOCTRINE else 'off'}")
    print(f"{'mode':<12} {'runs':>4} {'survived':>8} {'collapsed':>9} "
          f"{'avg score':>9}")
    try:
        for mode in MODE_ORDER:
            outcomes, scores = [], []
            for seed in range(1, args.seeds + 1):
                outcome, score = play(mode, seed)
                outcomes.append(outcome)
                scores.append(score)
            print(f"{mode:<12} {len(outcomes):>4} {outcomes.count('SURVIVED'):>8} "
                  f"{outcomes.count('COLLAPSED'):>9} "
                  f"{sum(scores) / max(1, len(scores)):>9.0f}")
    finally:
        if backup is not None:
            HALL.write_bytes(backup)
        try:
            os.remove(persistence.SAVE_FILE)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
