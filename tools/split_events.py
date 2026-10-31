#!/usr/bin/env python3
"""One-shot refactor: split the v5 event catalogue into per-era modules.

`kreml/content/events.py` had grown past 1,300 lines, which made one event
hard to find among ninety. This script reads the LIVE catalogue (so nothing is
re-typed by hand), writes one data module per era plus the fixed calendar
events, and regenerates `events.py` as a small index: pools, scripted years,
congresses, and the imports that assemble everything.

It is a developer tool, not part of the game, and it is kept for provenance:
it reads the LIVE catalogue, so running it again would re-emit the era
modules from whatever is in memory and overwrite hand edits. Run it only if
you are re-splitting a single-file catalogue from scratch:

    python tools/split_events.py
"""
from __future__ import annotations

import pathlib
import pprint
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from kreml.content import events as EV      # noqa: E402
from kreml.content import chains, forks     # noqa: E402

CONTENT = REPO / "kreml" / "content"

MODULES = {
    "EARLY": ("events_early.py", "EARLY era events (1964-1975)."),
    "MIDDLE": ("events_middle.py", "MIDDLE era events (1976-1984)."),
    "LATE": ("events_late.py", "LATE era events (1985-1991)."),
    "NEW": ("events_new.py", "The extended era (1992-2001)."),
    "": ("events_fixed.py", "Calendar events: scripted years, congresses, queues."),
}
VAR = {
    "EARLY": "EVENTS_EARLY", "MIDDLE": "EVENTS_MIDDLE", "LATE": "EVENTS_LATE",
    "NEW": "EVENTS_NEW", "": "EVENTS_FIXED",
}


def _dict_src(x: dict) -> str:
    if not x:
        return "{}"
    return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in x.items()) + "}"


def _opt_src(o) -> str:
    parts = [repr(o.label), _dict_src(o.ops), repr(o.outcomes)]
    if o.requires:
        parts.append(_dict_src(o.requires))
    return "    opt(" + ", ".join(parts) + "),"


def _ev_src(ev) -> str:
    opts = "\n".join(_opt_src(o) for o in ev.options)
    kwargs = []
    if ev.era:
        kwargs.append(f"era={ev.era!r}")
    if ev.once:
        kwargs.append("once=True")
    if ev.requires:
        kwargs.append(f"requires={_dict_src(ev.requires)}")
    if ev.alt:
        kwargs.append("alt=True")
    if getattr(ev, "clock", 0):
        kwargs.append(f"clock={ev.clock!r}")
    if getattr(ev, "hesitate", None):
        kwargs.append(f"hesitate={_dict_src(ev.hesitate)}")
    tail = ""
    if kwargs:
        tail = ",\n    " + ", ".join(kwargs)
    return (f'{VAR[ev.era]}["{ev.id}"] = ev(\n'
            f'    "{ev.id}", {ev.title!r}, {ev.text!r},\n'
            f'    [\n{opts}\n    ]{tail},\n)\n')


def write_module(era: str) -> int:
    name, blurb = MODULES[era]
    owned = [ev for ev in EV.EVENTS.values()
             if ev.era == era
             and ev.id not in chains.CHAIN_EVENTS
             and ev.id not in chains.EXTRA_EVENTS
             and ev.id not in forks.FORK_EVENTS]
    var = VAR[era]
    head = (
        f'"""{blurb}\n\n'
        "Content is pure data: `builders.ev` / `builders.opt` keep the literals\n"
        "short. Split out of the single v5 catalogue by tools/split_events.py;\n"
        "add new events here, in the era they belong to.\n"
        '"""\n'
        "from __future__ import annotations\n\n"
        "from .builders import ev, opt\n\n"
        f"{var}: dict[str, object] = {{}}\n\n"
    )
    body = "\n".join(_ev_src(ev) for ev in owned)
    (CONTENT / name).write_text(head + body, encoding="utf-8", newline="\n")
    return len(owned)


def write_index() -> None:
    pools = pprint.pformat(EV.RANDOM_POOLS, width=88, sort_dicts=False)
    scripted = pprint.pformat(EV.SCRIPTED, width=88, sort_dicts=False)
    congress = pprint.pformat(EV.CONGRESS_YEARS, width=88, sort_dicts=False)
    text = f'''"""All game events: the catalogue index.

Content lives in era modules, so a single event is easy to find:

  events_early.py   1964-1975          events_late.py    1985-1991
  events_middle.py  1976-1984          events_new.py     1992-2001
  events_fixed.py   scripted years, congresses and queued consequences
  events_v6.py      flash crises and the political additions
  chains.py         the five chain reactions
  forks.py          the three divergence forks

This module only assembles them and declares WHEN they may appear:

  1. RANDOM_POOLS  — era-flavoured, drawn each unscripted year
  2. SCRIPTED      — pinned to a specific historical year
  3. QUEUED        — triggered by earlier choices' "queue" ops
"""
from __future__ import annotations

from .chains import CHAIN_EVENTS, EXTRA_EVENTS
from .events_early import EVENTS_EARLY
from .events_fixed import EVENTS_FIXED
from .events_late import EVENTS_LATE
from .events_middle import EVENTS_MIDDLE
from .events_new import EVENTS_NEW
from .events_v6 import V6_EVENTS, V6_POOL_ADDITIONS
from .forks import FORK_EVENTS, FORKS

EVENTS: dict[str, object] = {{}}
for _group in (EVENTS_EARLY, EVENTS_MIDDLE, EVENTS_LATE, EVENTS_NEW,
               EVENTS_FIXED, EXTRA_EVENTS, CHAIN_EVENTS, FORK_EVENTS,
               V6_EVENTS):
    EVENTS.update(_group)

RANDOM_POOLS: dict[str, tuple[str, ...]] = {pools}

# v6 additions are appended, never rewritten, so the v5 draw probabilities hold.
for _era, _ids in V6_POOL_ADDITIONS.items():
    RANDOM_POOLS[_era] = RANDOM_POOLS[_era] + tuple(_ids)

# Congress years: the congress event replaces the regular random event.
CONGRESS_YEARS: dict[int, str] = {congress}

# Historical crises pinned to their years.
SCRIPTED: dict[int, tuple[str, ...]] = {scripted}

FORKS = FORKS
'''
    (CONTENT / "events.py").write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if "--force" not in sys.argv:
        print("refusing: this rewrites the era modules from the live catalogue,\n"
              "so it would overwrite hand edits. Re-run with --force only when\n"
              "re-splitting a single-file catalogue from scratch.", file=sys.stderr)
        return 2
    counts = {era: write_module(era) for era in MODULES}
    write_index()
    total = sum(counts.values())
    for era, n in counts.items():
        label = era or "FIXED"
        print(f"  {MODULES[era][0]:<20} {n:>3} events  ({label})")
    print(f"  {'TOTAL':<20} {total:>3} events")
    print("wrote kreml/content/events.py as the index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
