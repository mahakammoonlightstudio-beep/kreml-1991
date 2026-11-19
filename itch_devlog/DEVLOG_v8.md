# BETA v8 — The Room Has Faces

**Release:** BETA v8 · **Date:** 19 November 2026 · **Game:** КРЕМЛЬ 1991 — General Secretary

> “The atmosphere of a country waiting for tomorrow, knowing tomorrow might never come.”

That sentence arrived with the brief for this release, and it is the reason the
whole thing looks different. Not Soviet nostalgia. Not a museum of badges and
posters. A government inside a history that gets heavier every year, run by
people who can already feel the century closing.

## Why the room needed faces

The old Politburo was three moods: Old Guard, Reformers, Army. That is a good
piece of arithmetic and a bad piece of theatre. A player cannot betray a number.

v8 gives each faction one person:

- **Viktor Volkov**, Chief of Staff, who has outlived four General Secretaries
  and remembers where the files are.
- **Lidia Sorokina**, Gosplan economist, who keeps two sets of figures: the ones
  she reports and the ones she believes.
- **Marshal Arkady Balashov**, Chief of the General Staff, who speaks in weather
  reports and whose forecast is always snow.

They send memos. They ask you to choose them. They remember. The most trusted
one returns a point to their own sector every year; the one you abandon starts
costing you. At the end, the succession file names the survivor — and the
epilogue tells you what that inheritance looks like.

This is the Suzerain/Crisis in the Kremlin lesson applied without copying either:
the personal layer has to touch the national arithmetic, or it is just flavour
text with a portrait.

## Why the run ends with a seed

The divergence report was already the most shareable thing in the game. v8 turns
it into a card: **seed, fate, score, title, years, difficulty, timeline**, plus a
URL that replays the same history.

The card is built from the real ending, not a separate API. The browser edition
copy button writes a plain-text challenge; the play page accepts
`?seed=42&mode=hard&timeline=succession`. A friend can play the exact Union you
failed to keep, with the same shocks and the same arithmetic.

That is the loop: finish → copy → dare → watch someone else discover that the
shelves were always going to be the problem.

## Why 1982

The Three Funerals is the shortest, bleakest opening. Brezhnev is dead.
Andropov has the files. The Afghan war is still bleeding. The shelves are thin.
Nine winters remain. It begins mid-drift, with the Old Guard warm and the
reformers already suspicious, and it has no mandate screen to hide behind.

It is also the best argument for the game's thesis: the Union did not fall
because one man made one mistake. It fell because a system kept choosing the
same winter.

## Why the browser stopped looking like a terminal

The transcript is still the game. That is the point. But a black rectangle with
green text is a costume, not a design.

v8 wraps the transcript in a **situation room**: a large year in Bodoni, five
gauges with hairline meters, valas, the court, capital, the republics and the
agenda. The values are parsed live from the printed board. No fake HUD, no
duplicated state, no second engine.

The rest of the visual language is deliberately editorial: ash and oxblood,
Bodoni headlines, Playfair whispers, Inter for the record, JetBrains Mono for
figures. Photographs are desaturated and credited. There are no scanlines, no
phosphor glow, no typewriter ticking. Sound is off by default; when enabled it is
sparse, low event cues.

The itch edition is the pure-play cut: the same room with the landing page,
support panel and site chrome removed. GitHub is the case file. itch is the cell.

## Mobile

The room folds into a compact strip above the orders. Gauges become five short
labels with hairline bars. Choices become full-width numbered orders. The input
is 16px so the phone does not zoom; the keyboard does not pop open after every
turn; safe areas are respected. The desktop run is still the better way to read
twenty-seven years, but the phone is now a legitimate place to lose the Union.

## What is still true

- Pure Python, standard library, no build step for the terminal game.
- 129 events, 37 directives, five openings, six difficulties.
- Historical rails still lock alternate content and charge for detours.
- Old saves are refused rather than corrupted. The schema is v7 now.
- The game is free. Donations unlock nothing.

The Union is fictional. The timetable is not. The chief of staff is,
unfortunately, a composite.
