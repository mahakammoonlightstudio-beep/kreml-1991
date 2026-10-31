"""Records real КРЕМЛЬ 1991 output via the test-covered web driver (ahead of
tools/record_gameplay.py). Feeds a real, deterministic answer script and dumps
the transcript, so the landing shows the actual game, not a mock of it."""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "docs/play")

from kreml_web import Session  # noqa: E402

# medium mode, Rails of History timeline, fixed seed — deterministic.
s = Session(".", seed=1964)
batches = {"start": s.start("medium", "rails", 1964)}

script = [
    "",          # [Enter] proceed
    "12",        # first directive menu pick: detente diplomacy (hand-tuned later)
    "1",         # answer the first event
    "",          # proceed
    "5",         # next year directive
    "2",         # answer
    "",
]
for i, a in enumerate(script, 1):
    r = s.answer(a)
    batches[f"a{i}:{a!r}"] = r
    if r.get("done"):
        break

text = re.sub(r"\u001b\[[0-9;]*m", "", s.transcript)
print(text)
print("\n===SNAPSHOT===", file=sys.stderr)
print(json.dumps(s.snapshot())[:400], file=sys.stderr)
