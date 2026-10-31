"""One more real screen for the landing: the Dossier (answer 'd' at the bar)."""
from __future__ import annotations

import re
import sys

sys.path.insert(0, "docs/play")

from kreml_web import Session  # noqa: E402

ANSI = re.compile(r"\u001b\[[0-9;]*m")
strip = ANSI.sub


s = Session(".", seed=1964)
r = s.start("medium", "rails", 1964)
out = strip("", r["text"])
outs = [r["text"]]
bar = "o orders │ q resign :"
step = 0
while step < 6:
    tail = out[-300:].lower()
    if bar.rstrip() in tail.rstrip():
        r = s.answer("d")
    elif "your mandate" in tail or "wants your signature" in tail:
        r = s.answer("3")
    elif "directive of the year" in tail:
        r = s.answer("2")
    elif "focus on" in tail:
        r = s.answer("1")
    elif "decision" in tail:
        r = s.answer("1")
    else:
        r = s.answer("")
    outs.append(r.get("text", ""))
    out += r.get("text", "")
    step += 1
open(".hallmark/dossier.txt", "w", encoding="utf-8").write(strip("", out))
print("answers:", len(s.answers), "done:", r.get("done"), file=sys.stderr)
