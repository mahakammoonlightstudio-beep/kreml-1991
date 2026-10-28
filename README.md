<div align="center">

# ☭ КРЕМЛЬ 1991 — General Secretary

**A text-based terminal game.** An **alternate-history simulator** in which you
are General Secretary of the CPSU from **1964 to 1991** — and, if you end the
first act strong, into the daring **Red Millennium (1992–2001)**.

*Bend history anywhere you like. Keep five gauges above zero, keep the valas
reserve breathing, and keep three Politburo factions from despairing.*

![release](https://img.shields.io/badge/release-BETA%20v4-cb0000?labelColor=6a0000&color=c8102e&style=flat-square)
![python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![platform](https://img.shields.io/badge/platform-Windows%20·%20Linux%20·%20macOS-lightgrey?style=flat-square)
![play online](https://img.shields.io/badge/web-GitHub%20Pages-c8102e?style=flat-square&logo=github&logoColor=white)
**Made by Mahakam Moonlight Studio ☭ [`mahakammoonlightstudio-beep`] & Mr. Fozan**

[⬇ Download BETA v4](https://github.com/mahakammoonlightstudio-beep/kreml-1991/releases) ·
[🌐 Web page](https://mahakammoonlightstudio-beep.github.io/kreml-1991/) ·
[🎥 Gameplay video (60 fps)](https://github.com/mahakammoonlightstudio-beep/kreml-1991/releases)

![teaser](docs/media/teaser.gif)

</div>

---

## What you are signing for

Five gauges rule your fate — **Economy · Military · Order · People's Faith ·
World Prestige** — plus the v4 extras: a hard-currency **valas reserve** driven
by the world oil market, and the **three moods of the Politburo**
(*Old Guard · Reformers · Army*). Bottom out a gauge → a themed collapse
ending. Let a faction despair → they book your conference room for a
**velvet coup**.

| | |
|---|---|
| ![The court & the yardstick](docs/media/shot_panel.jpg) | ![Yearly directives](docs/media/shot_directives.jpg) |
| *The yardstick: gauges, valas, factions* | *The yearly directive — 13 public levers* |
| ![Oil boom years](docs/media/shot_boom.jpg) | ![The late era](docs/media/shot_finalyears.jpg) |
| *«Oil: BOOM» — the valas pays for dinner* | *1990: the PLOT flickers in the court line* |

## How to play (it's a `.py`, comrades)

Requires **Python 3.8+** — nothing else, pure standard library:

```bash
git clone https://github.com/mahakammoonlightstudio-beep/kreml-1991.git
cd kreml-1991
python main.py
```

Or grab `main.py` + the `kreml/` folder from the
[**BETA v4 release**](https://github.com/mahakammoonlightstudio-beep/kreml-1991/releases),
then just:

```
python main.py
```

```
python main.py                    # normal game
python main.py --drama            # slow typewriter printing
python main.py --seed 42          # fixed randomness
python main.py --mode easy        # SWEEPING REFORMS | BALANCED | IRON GRASP
```

*(The v1 single-file version is kept for archaeologists in `v1_kreml.py`.
Saves from v3 are politely refused — the state now carries v4 systems.)*

## Developer & studio tools

```
python tests\test_mechanics.py    # mechanic-level self checks (28 checks)
python tests\test_io_flow.py      # save/load/dossier flow via scripted input
python tests\run_smoke.py         # headless full-game smoke tests
python tools\render_gameplay.py   # smooth 60fps "real gameplay" video render
```

## Video render (tools/render_gameplay.py)

Unlike the older `tools/render_video.py` (one static PNG per scene, 8 fps
slideshow), this renderer produces a *visualised live recording*: the
autopilot plays the game while every `print` and every `input` prompt is
captured, then everything is replayed as continuous 60 fps motion —
screens print line by line and scroll like a real console, a mouse pointer
glides to each menu option, answers are typed on camera, a `REC ●` timer
runs in the corner, and — if the Soviet anthem `edit video/National Anthem
of USSR.mp4` is present locally — it is looped in as the soundtrack
(no anthem file? the render finishes silent). Output: `gameplay_60fps.mp4`
(1600×900, H.264, AAC). The BETA v4 trailer on the
[releases page](https://github.com/mahakammoonlightstudio-beep/kreml-1991/releases)
was produced with it.

Useful flags: `--seed N` (must survive), `--out FILE.mp4`,
`--max-acts N` / `--only-last N` (short test renders), `--fps 30`.

Specifications for tooling: `pip install -r requirements-dev.txt`
(Pillow + fonttools) and have `ffmpeg` on PATH.

## Survival notes (declassified by the Ministry, 1964–1991)

*Soviet difficulty is fair, comrade — it is merely not explained. The Partburo
keeps the arithmetic in a locked drawer. Two options:
(a) die honourably and reverse-engineer it, or (b) read this once.*

- **The survival budget.** Drift (BALANCED) eats ≈ **−175 gauge points** over
  27 years (EARLY −6/yr, MIDDLE −6/yr, LATE −7/yr). Starting total 314.
  You must therefore *earn* ≈ +6.5 per year, every year, on average.
  Directives are the engine — repeating the same comfortable week is how the
  Revolution failed at paperwork.
- **1991 is a paywall.** The August Coup's defying option is fatal unless
  **MILITARY + ORDER ≥ 110**. You start at 145 and drift claws ~2/yr off that
  sum — do the arithmetic by ~1980 and buy the general staff some dinners.
  Or plan the quiet path (back the Committee) and budget Faith for it.
- **The valas is a third economy.** From the 1986 oil glut the reserve bleeds
  ~8–11/yr until 1991; the dry penalty grounds Economy. Repeatable answers:
  *Oil & gas exports* (+6 valas), the *second pipeline*, *Western loans*,
  *quiet gold sales*, and Beryozka hard-currency shops. Playing to extend the
  game into 2001 **requires valas ≥ 15 at the 1991 border** — start hoarding
  by 1985 or don't dream of the Millennium.
- **The court keeps scores.** Any faction that bottoms out (≤ 15) books the
  velvet room for the following year. Reformers starve in the 1970s (−1/yr
  drift); the Old Guard panics whenever you legislate honesty. One private
  dinner per bad year is usually enough.
- **Lifelines are strategic ammunition.** They trigger under 35, but saving
  them for the 1986–1991 squeeze is how strong runs are built.
- **The Dossier is free.** Read it every few years; the forks page lists
  events whose gates are about to close forever.

*Reading these notes makes you a planner. Ignoring them makes you history.
Both are legitimate strategies; one of them scores better.*

## What you do every year

1. **Command bar** — `[Enter]` proceed · `s` save · `l` load · `d` dossier · `q` resign
2. **Personal focus** — a small, private lever (inspect a factory, give a
   speech, rest at the dacha, dine with the Politburo families, inspect the
   gold vault by lamplight...)
3. **Yearly directive** — big public policy across five menu groups
   *(Economy, Defense, Society, Foreign, Science)*
4. **Crisis events** — historically scripted, era-random, or congressional
   (some years bring two: 1986 runs the congress *and* Chernobyl, 1989 the
   Wall *and* the coal miners' summer)

## New in BETA v4

| System | What it does |
|---|---|
| **The court & the velvet coup** | Three faction moods — *Old Guard · Reformers · Army* — shown in the stats panel. Policies, events and your private dinners shift them yearly. A faction that bottoms out **books your conference room**: a palace coup with three answers (face them, buy them, appeal to the people). Fail and a new **DEPOSED** ending removes you from the portraits without a single gauge touching zero. |
| **Valas & the world market** | A yearly **oil price index** (the 1973 boom, the 1980 peak, the 1986 glut, the late-90s trough) drives a **hard-currency reserve**. Imports and debt service drain it; dry reserves pain Economy & Faith. New money levers: the second pipeline, quiet gold sales, Western loans (watch the interest turn), Beryozka shops, grain bills in valas. |
| **The Red Millennium** | End 1991 strong (gauges ≥ 25, valas ≥ 15, and either the Union Treaty or Faith ≥ 55) and the Politburo offers **ten more years, 1992–2001**: the rouble-zone question, the Union Charter, the 1996 Red Millennium Congress, the Asian flu, NATO stepping east, the millennium broadcast. Two fresh crisis reserves are granted. Survive to 2001 for the **RED MILLENNIUM** ending and the *Author of the Red Millennium* legacy. |
| Verify the court from the dossier | New dossier section *The Room & the Market*: valas, oil status, faction moods, and a warning when a velvet meeting is on the docket. |
| Hall of fame tags | New tags: `MILLENNIUM` (the red 2001), `DEPOSED` (outvoted, not collapsed). |

## New in v3

| System | What it does |
|---|---|
| **Difficulty modes** | *SWEEPING REFORMS* (gentle drift, 5 reserves) · *BALANCED* (historical grind, 3 reserves) · *OLD GUARD IRON GRASP* (the system fights back, 2 reserves). Also settable with `--mode`. |
| **Save / load** | The year-boundary command bar saves the whole state (including RNG) to `kreml_save.json`; the title screen offers to resume it. Loadable mid-run with `l`. |
| **The Dossier (`d`)** | Interactive timeline: your full **decision ledger**, every **conditional road** (done ▸ open ✖ locked reasons), branching **forks** still in play, delayed consequences **in the pipeline**, and history's **known timetable**. |
| **Western press** | Every year, a foreign-paper headline reacts to what you've done and to the gauges (Afghanistan, show trials, rouble float, treaty...). Weighted & one-shot per headline. |
| **Surprise scripted double-years** | 1989 fires *The Berlin Wall Falls* **and** *The Coal Miners' Summer*; 1986 already fires congress + Chernobyl. |
| **Union Treaty chain** | `new_union_treaty` (1989+, Faith ≥ 55) → `special_economic_zone`, plus regenerating the nomenklatura, an anti-alcohol campaign, the Helsinki accords and the "Singapore envelope" events. |
| **"Survived by a prayer"** | End 1991 with any gauge under 10 and the ending re-flavours itself (inertia got the credit, not you) and scores 25 lower; signing the treaty pays +6. |
| Hall of fame tags | Records now include the difficulty mode (`SURVIVED · IRON GRASP ...`). |

## Carried over from v2

| System | What it does |
|---|---|
| **Conditional directives** | Big levers unlock only through earlier decisions — e.g. *Legalize cooperatives* requires the Kosygin or perestroika path; *price reform* requires cooperatives. |
| **Great congresses (1970/1978/1986)** | Strategic plenums that plant long-lived flags. |
| **Crisis lifelines** | Spend a reserve when a gauge hits the red line. |
| **Delayed consequences** | Choices can `queue` follow-up events (e.g. the atomic ultimatum gets a NATO reply a year later). |
| **Dacha rest** | Softens the *next* event's damage. |
| **Divergence report** | At the end: exactly where your timeline left real history. |

## The five gauges — and the two extra skies

**Economy · Military · Order · People's Faith · World Prestige** — all erode
every year (per your difficulty mode); war attrition, era drift (worse after
1985), and superpower bonuses apply automatically. Honestly, warmly, the
Union exports oil and gas **when the market pays** — the v4 panel adds the
**valas reserve** and the three **Politburo moods** beside them. Any gauge at
0 → themed collapse ending; a despairing faction → the velvet room.

## Architecture (why it isn't spaghetti)

```
main.py                 entry point (args → engine.run)
kreml/
  model.py              frozen dataclasses: Event/Option/Directive/Action
  state.py              the single mutable game state (gauges, flags, queues,
                        ledger, shown_press, mode, valas, court moods)
  ops.py                the effects DSL: all content → state writes happen HERE
  ui.py                 all rendering + input (colours, bars, menus, prompts,
                        year-boundary command bar)
  engine.py             turn orchestration only (menus → ops → drift →
                        systems → endings)
  persistence.py        save/load (whole state + RNG as JSON, v4 format)
  dossier.py            the interactive timeline & branch-roadmap viewer
  content/              PURE DATA, no logic:
    events.py           all events + pools + scripted years + congresses
    directives.py       directives, menu groups, lifelines
    actions.py          personal focus actions
    modes.py            difficulty presets (drift tables, reserve counts)
    world.py            v4 data: yearly oil index & court drift tables
    press.py            Western press headline reactions
    history.py          yearly flavour lines
    endings.py          endings, scoring, divergence report, hall of fame
tests/
  run_smoke.py          headless full-game runs (3 modes)
  test_mechanics.py     unit checks: queues, gating, coups, drift, valas,
                        court, palace coup, era extension, save/load...
  test_io_flow.py       scripted-input flow: save, dossier, load, resume
```

Key idea: **content is data, logic is one generic engine.** Adding a new
event, directive, or even a new effect type means adding data (or one op key
in `ops.py`) — you never rewire the loop. Requirements on options/directives
(`flags` / `any_flags` / `not_flags` / `stats` / `min_year` / `max_year` /
`hc` / `hc_max` / `court_min` / `court_max`) drive the branching
alternate-history layer declaratively.

## Endings

- Survive to **1991** → the flag stays red; score = gauges + 2 per year
  governed (−25 if any gauge is under 10, +6 for the Union Treaty, +4 for a
  golden valas cushion); titles up to *GENERALISSIMUS OF HISTORY ★*.
- Then, if strong: play into the Red Millennium — survive **2001** for
  *THE RED MILLENNIUM — THE UNION NEVER LEFT* (+8 score).
- Any gauge 0 → collapse, portraiture removal, half score.
- Lose a palace coup → slight variation: **removed by the plenum, not the
  arithmetic** — the same portraiture fate, a different epitaph.
- Resign from the command bar (`q`) or any menu — keeps score.
- Every game lands in `hall_of_fame.txt` with its difficulty tag.

---

<div align="center">

**☭ СТРАНЫ, УХОДЯЩИЕ В ИСТОРИЮ — SALAM DARI KREML, COMRADE. ☭**

*A Mahakam Moonlight Studio production — beep edition.*
*Directed & written by mahakammoonlightstudio-beep and Mr. Fozan.*

*Code licensed MIT. Historical recordings and the musical soundtrack featured
in the rendered videos belong to their respective owners.*

</div>
