# BETA v8 — The Room Has Faces

- **Released:** 19 November 2026
- **Tag:** `v8-beta`
- **Game:** КРЕМЛЬ 1991 — General Secretary
- **Builds:** browser (GitHub Pages), pure-play itch.io HTML ZIP, terminal
- **Previous:** [BETA v7-5](RELEASE_NOTES_v7-5.md)

> “The atmosphere of a country waiting for tomorrow, knowing tomorrow might never come.”
> — the design brief for this release

BETA v8 is the release where the Politburo stops being three meters. Three
people now sit in the room, remember how you treated them, and inherit the desk
when you leave. The run also ends with something you can hand to another player:
a seed, a score, and a dare.

## What changed

### The room has faces

- **Viktor Volkov**, Chief of Staff (Old Guard, Order)
- **Lidia Sorokina**, Gosplan economist (Reformers, Economy)
- **Marshal Arkady Balashov**, Chief of the General Staff (Army, Military)

Six personal memos join the era pools. Each has a real answer, a loyalty cost
and a consequence in the national arithmetic. Loyalty starts at 50 and is shown
in the Dossier. The most trusted member (70+) quietly returns **+1 of their own
gauge every year**; a member abandoned below 20 costs one. At the end, the
succession file names the most loyal survivor.

### A seed is a dare

Every ending now prints a **challenge card**: verdict, score, title, years,
difficulty, timeline and the run seed. The browser edition turns it into a
physical card you can copy, and the play page accepts
`?seed=42&mode=hard&timeline=succession`. Same seed, same history, different
answers. This is the organic sharing loop the release was built around.

### The Three Funerals (1982)

A fifth opening starts in November 1982: Brezhnev dead, Andropov holding the
files, the Afghan war still bleeding, the shelves already thin, and nine winters
left on the calendar. The stagnation is warm. The clock is not.

### The situation room

The browser transcript is now framed by a live room parsed from the real game
output: year, five gauges, valas, the court, political capital, the republics and
the year's agenda. It is not a mock-up and not a second game — when the
transcript changes, the room changes.

### Two editions, on purpose

- **GitHub Pages** is the case file: landing page, art direction, release notes,
  context, support, and the game.
- **itch.io** is the cell: the game alone. The itch ZIP carries the same v8
  situation room with the landing chrome stripped, local fonts and the Kremlin
  photograph included.

### The archive gets thicker

The three Wikimedia files that returned HTTP 429 during the first pass were retried
through the Commons API with a proper User-Agent and are now in the landing-page
archive: **Red Square, 7 November 1977** (Szilas, public domain), **Mikhail
Gorbachev, 2010** (Veni Markovski, CC BY 3.0), and the **1955–1991 flag**
(public domain). They are resized and desaturated on the page, with exact
provenance in `docs/media/photo_credits.json` and the footer.

### Mobile, typography and quiet audio

- The room folds into a compact strip above the orders at 680px and below.
- 44px touch targets, 16px input text, safe-area support, no forced keyboard.
- New editorial type: Bodoni Moda, Playfair Display Italic, Inter and JetBrains
  Mono, all local and OFL.
- Sound is **off by default** in the browser. When enabled, it is sparse event
  cues — no typewriter ticking, no CRT hum.
- The licensed photographs are credited in `docs/media/photo_credits.json` and
  in the landing page footer.

### Saves and compatibility

The save schema is now **v7**. It stores the run seed and cast loyalty. Saves
from v6 and earlier are refused cleanly rather than half-loaded into a different
Union.

## Verification

- **57/57** mechanic checks
- **10/10** browser replay checks
- **4/4** web build checks
- Save / dossier / load / resume flow passes
- Headless smoke run passes across the timeline set
- Browser bundle rebuilt (328 KB, 34 source files)
- Balance matrix re-measured for v8 (5 seeds per mode, floor and ceiling)
- Static audit: every element the browser runtime touches exists; no missing
  local assets
- Pure-play itch ZIP rebuilt at **0.7 MB**, `index.html` at the root, fonts and
  photograph local
- Itch ZIP now carries `body.itch-build`; the guard that was meant to add it
  tested the whole document (where the class name already appears in the CSS)
  and never ran, so the landing chrome had been leaking into the iframe build

## Balance

The cast adds at most **+1 gauge per year** for one trusted member and can cost
**−1 per year** for an abandoned one. It is a political investment, not a free
stat.

The v8 matrix was measured on **19 November 2026**, 5 seeds per mode, clock off.
On the floor (no capital, no doctrine), hard survives **2/5** and extreme **1/5**;
the ceiling lifts both to **3/5**. Scores fall from 372 on easy to 184 on
extreme. The full table and the reading notes live in `README.md`; re-run
`python tools/balance.py` after any content change.

## Play

- **Browser:** <https://mahakammoonlightstudio-beep.github.io/kreml-1991/>
- **Situation room:** <https://mahakammoonlightstudio-beep.github.io/kreml-1991/play/>
- **itch.io (pure play):** <https://mahakam-moonlight-studio.itch.io/kreml-1991>
- **Terminal:** clone the repository and run `python main.py` with Python 3.8+.
- **Download:** the release includes `kreml-1991-web.zip` for itch.io.

## Known limits

- The first browser visit still pulls about 12 MB of Pyodide from a CDN.
- The browser build is installable to a phone home screen, not a native APK.
- Itch screenshots are captures of the exported itch build itself, made by
  `tools/capture_room.py`; they are PNGs at page width, not 16:9 plates.
- Generated AI output was used for code, copy and art assistance; everything was
  reviewed, edited and integrated by the developers.
