# Modding КРЕМЛЬ 1991

**BETA v8 keeps the promise the engine was built on: content is data, logic is a
single engine.** Every event, directive, focus, timeline, fork and memo is a
frozen dataclass in `kreml/content/`. Adding a road does not mean editing the
traffic.

There is no JSON hot-loader and no mod menu. A scenario is a Python data module
that ships with the game. This is deliberate: the whole game is standard
library, deterministic, and auditable, and a save is a seed plus a list of
answers. If you want to fork a century, fork the content folder.

---

## The map

```text
kreml/
  model.py           Event / Option / Directive / Action / Timeline / Character
  state.py           the one mutable state (gauges, flags, queues, cast, seed...)
  ops.py             the effects DSL: every content → state write
  engine.py          one year: briefing → focus → directive → events → systems
  content/
    events.py        the index: pools, scripted years, congresses
    timelines.py     the five openings
    cast.py          v8: three faces, six memos, loyalty, succession
    directives.py    the yearly public campaigns
    actions.py       the personal evening
    chains.py        delayed consequences
    forks.py         the three divergence doors
    republics.py     the four regional pressure lines
    endings.py       scoring, epilogues, challenge card
    modes.py         difficulty presets
```

A content module contains no loop logic. The engine discovers events through
`events.py` and directives through `directives.py`.

---

## Add an event

Create a module or append to an existing one:

```python
from .builders import ev, opt

EVENTS = {}

EVENTS["my_crisis"] = ev(
    "my_crisis",
    "The Committee Has a Question",
    "Three men and one folder are waiting outside your office.",
    [
        opt("Hear them out",
            {"stats": {"ORDER": 2, "FAITH": -1},
             "court": {"old_guard": 3},
             "flag_add": "committee_heard"},
            "The folder stays. The question does not."),
        opt("Send them to Gosplan",
            {"stats": {"ECONOMY": 1, "ORDER": -1},
             "influence": 1},
            "The question becomes a sub-committee."),
        opt("Refuse the folder",
            {"stats": {"ORDER": 1, "PRESTIGE": -1},
             "loyalty": {"volkov": -3}},
            "Volkov learns something about you."),
    ],
    era="MIDDLE",          # EARLY 1964-75, MIDDLE 76-84, LATE 85-91, NEW 92-2001
    once=True,
    requires={"min_year": 1972},
)
```

Register it in `kreml/content/events.py`:

```python
from .my_module import EVENTS as MY_EVENTS
# add MY_EVENTS to the _group tuple in events.py
# add "my_crisis" to RANDOM_POOLS["MIDDLE"]
```

For a pinned historical year, add it to `SCRIPTED` instead:

```python
SCRIPTED[1972] = ("my_crisis",)
```

For a delayed consequence, any option can queue it:

```python
{"queue": [(3, "my_followup")]}
```

The target id must exist in `EVENTS`; `tests/test_mechanics.py` checks every
queue target.

---

## Add a directive or a personal focus

```python
# in kreml/content/directives.py, after the existing tuple
from .builders import directive

DIRECTIVES = (*DIRECTIVES, directive(
    "my_reform", "A Small Legal Revolution", "One paragraph, one ministry.",
    "Economy",
    {"stats": {"ECONOMY": 3, "ORDER": -1}, "flag_add": "my_reform"},
    requires={"flags": ["kosygin_pilot"]}, once=True,
))

# in kreml/content/actions.py, after the existing tuple
from .builders import action

FOCUS_ACTIONS = (*FOCUS_ACTIONS, action(
    "my_walk", "Walk the embankment", "Forty minutes without a telephone.",
    {"stats": {"FAITH": 1}}, requires={"min_year": 1970},
))
```

Use `once=True` for one-shot roads. Use fatigue deliberately: repeating the same
lever shrinks positive gains, never costs.

---

## Add a timeline (a new scenario)

```python
from ..model import Timeline
from .timelines import TIMELINES, TIMELINE_ORDER

TIMELINES["thaw"] = Timeline(
    id="thaw",
    label="THE THAW",
    desc="1956: the secret speech, the Polish October, and a thaw that may not last.",
    year=1956,
    end_year=1991,
    stats={"ECONOMY": 60, "MILITARY": 68, "ORDER": 64,
           "FAITH": 66, "PRESTIGE": 58},
    flags=("thaw",),
    court={"old_guard": 42, "reformers": 62, "military": 50},
    hc=44,
    mandate=False,
)
TIMELINE_ORDER = (*TIMELINE_ORDER, "thaw")
```

Then add epilogues for `("thaw", "survived")`, `("thaw", "millennium")` and
`("thaw", "collapse")` in `endings.py`, and add starting unrest in
`republics.TIMELINE_UNREST` if the opening is late enough to need it.

The era bands are fixed in `state.ERAS`. A scenario outside 1964–2001 still
plays, but it will use the nearest band for drift and event pools; add an era
band and content if you want a full new century.

---

## Add a cast member (v8)

1. Add a `Character` to `CAST` in `content/cast.py` (`id`, `name`, `role`,
   `faction`, `stat`, `line`).
2. Its loyalty starts at 50 via `DEFAULT_LOYALTY`.
3. Write a memo event with `loyalty: {"your_id": +4}` and add the id to
   `CAST_POOL_ADDITIONS` for the right era.
4. The yearly room logic in `engine.apply_systems` already gives the most
   trusted member (70+) **+1** of their own gauge and charges **−1** for any
   member abandoned below 20.
5. `cast.successor()` names the most loyal member in the ending; the Dossier
   shows the room and the succession file.

---

## The ops vocabulary

| Key | Shape | Effect |
|---|---|---|
| `stats` | `{"ECONOMY": 3}` or `(2, 4)` | gauge delta, clamped 0–100 |
| `flag_add` / `flag_rm` | string or list | permanent run flags |
| `queue` | `[(years, event_id)]` | delayed event |
| `hc` | int or `(min, max)` | valas reserve |
| `influence` | int | political capital |
| `court` | `{"old_guard": 4}` | faction mood |
| `unrest` | `{"baltic": 5}` | republic pressure |
| `loyalty` | `{"volkov": 4}` | v8 cast loyalty |
| `path` | `"path_reform"` | divergence line (replaces the old one) |
| `special` | `"coup_defy"` | registered handler in `ops.SPECIALS` |

Requirements (`requires=`) accept `stats`, `flags`, `any_flags`, `not_flags`,
`min_year`, `max_year`, `hc`, `hc_max`, `influence`, `court_min`, `court_max`,
`unrest_min`, `unrest_max`. `influence` is political capital; `hc` and `hc_max`
are the valas reserve.

---

## Test and ship

```bash
python tests/test_mechanics.py    # 57 checks; add one for your content
python tests/test_io_flow.py     # save/dossier/load/resume
python tests/run_smoke.py        # full headless runs across modes
python tools/build_web.py        # rebuild the browser bundle
python tools/build_itch.py       # rebuild the pure-play itch zip
```

If you add a new event id to a pool, the dossier's roadmap and the smoke run
will find it automatically. If you add a new mechanic, add an ops key and a
mechanics check; do not grow a special case in the engine.

---

## Licences

Code is MIT. Content you add is yours to license, but it ships inside an MIT
project. Photographs and fonts are **not** covered by the MIT licence; keep the
credits and licence files beside any asset you add. `docs/media/photo_credits.json`
is the machine-readable record for the website's photographs.
