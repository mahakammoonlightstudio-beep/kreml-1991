"""Collects real КРЕМЛЬ 1991 screens (seed-locked, verbatim) for the landing.

Crops happen later; nothing is retouched. An adaptive bot reads the last
prompt in the transcript and answers like a player would: directive 10 (the
KGB crackdown), event option 1, Enter at the yearly bar - a hard, faith-draining
run that should reach a real ending in a handful of years.
"""
from __future__ import annotations

import re
import sys

sys.path.insert(0, "docs/play")

from kreml_web import Session  # noqa: E402

ANSI = re.compile(r"\u001b\[[0-9;]*m")


def strip(t: str) -> str:
    return ANSI.sub("", t)


def decide(tail: str) -> str:
    """One answer for the next prompt, from the text after the last printed line."""
    if "That dossier is off the table" in tail or "not recognised" in tail \
            or "Choose again" in tail:
        return "1"                     # last answer was rejected; take the first
    low = tail.lower()
    if low.rstrip().endswith("proceed │ s save │ l load │ d dossier │ i capital │ o orders │ q resign :".rstrip()):
        return ""
    if "your mandate" in low:
        return "3"                     # the dark-horse reformer
    if "directive of the year" in low:
        return "10"                    # the crackdown: spends order, drains faith
    if "your decision" in low or "authorise" in low or "the court asks" in low:
        return "1"
    if "focus on" in low:
        return "1"
    if "name" in low and "history books" in low:
        return "Lazar Fiend"           # a name played under, echoes nowhere
    return ""                          # bare [Enter] wherever the press asks


def play(mode, timeline, seed, limit=900):
    s = Session(".", seed=seed)
    r = s.start(mode, timeline, seed)
    text = strip(r["text"])
    n = 0
    while not r.get("done") and n < limit:
        tail = text.tail if False else text[-400:]          # noqa: F841
        tail = text[-400:]
        r = s.answer(decide(tail))
        text += strip(r.get("text", ""))
        n += 1
    return text, r.get("done"), n, len(s.answers)


t, done, n, kept = play("medium", "rails", 1964)
open(".hallmark/death.txt", "w", encoding="utf-8").write(t)
print("death: done", done, "replays", n, file=sys.stderr)

t, done, n, kept = play("flash", "rails", 1964, limit=60)
open(".hallmark/flash.txt", "w", encoding="utf-8").write(t)
print("flash: done", done, "replays", n, file=sys.stderr)
