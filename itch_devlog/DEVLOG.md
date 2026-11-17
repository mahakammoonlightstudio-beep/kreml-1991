# BETA v7-5 — The First-Year Orientation

**Release:** BETA v7-5 · **Date:** 17 November 2026 · **Game:** КРЕМЛЬ 1991 — General Secretary

This patch started with a reviewer note. We are keeping the note here, unedited,
because it says exactly what the board was missing:

![itch.io reviewer note: four stars, "best game ever, but please add tutorial"](<Screenshot 2026-11-17 121813.png>)

> “best game ever, but please add tutorial”
> — muhammadfauzan-sketch, itch.io

So v7-5 adds a tutorial that belongs in this game: not a pop-up with a cartoon
arrow, but a stack of memos from a chief of staff who has watched too many
General Secretaries confuse a telephone with a policy.

## The First-Year Orientation

It is optional. Pick it from the title screen in the browser or run:

```bash
python main.py --tutorial
```

Chief of Staff Volkov walks you through:

- the five gauges and the yearly drift that eats them;
- the Dossier (`d`), political capital (`i`) and standing orders (`o`);
- plan fatigue — 100%, 85%, 70%, and down to 35%, while the costs stay whole;
- the court’s danger line and the 1991 `MILITARY + ORDER` gate;
- the 1986 oil glut and why the valas reserve has to be hoarded early;
- the new Republic Unrest board.

The first year is then coached with one-line margin notes before the focus,
directive, event and year-end settlement. The notes do not spend resources and
do not soften the difficulty. They just stop a new player from mistaking the
console for a spreadsheet with a flag on it.

## The new mechanic: Republic Unrest

The old Union had one Order gauge. That was always a polite fiction. v7-5 adds
four regional fault lines: **Baltic**, **Ukraine**, **Caucasus** and **Central
Asia**.

- Low Order, low Faith and glasnost raise unrest.
- The 1986–1991 shocks hit the regions differently.
- A tour of the republics, federal subsidies, a federal compact and the Union
  Treaty are real levers.
- A hot republic costs Order and Faith. At 75 it stops sending memoranda and
  books a crisis event.
- The Red Millennium gate now checks the regional map as well as the valas and
  the five national gauges.

It makes 1989–1991 feel like a union of arguments rather than a single bar
going down. It also makes the tutorial’s last memo honest: the game is not
hiding the arithmetic. It is hiding it under a committee.

## The Red Millennium capstone

Players who survive 1991 and earn the extra decade can now reach a final event
that only strong runs qualify for. It is not a participation trophy: it needs
the gauges, the valas and a real political achievement. The three answers give
the Red Millennium a different first sentence — federation, Party centre, or
nuclear retirement — and the ending remembers which one you chose.

## Event cues

Incidents, agenda results and endings now get short synthesized tones. The
terminal uses the system bell or `winsound`; the browser uses Web Audio, with a
sound toggle in the toolbar. Tests, pipes and video captures stay silent.

## Difficulty

The republics are not decorative. Ignoring them now costs Order and Faith late,
and can block the Millennium. The old “just keep the five bars alive” line still
works, but it is no longer the whole job.

## Files for this devlog

- `Screenshot 2026-11-17 121813.png` — the reviewer note that prompted the patch.
- this file — release notes ready to paste into itch.io.

*The Union is fictional. The reviewer note is not. The chief of staff is,
unfortunately, a composite.*
