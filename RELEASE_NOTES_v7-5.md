# BETA v7-5 — The First-Year Orientation

- **Released:** 17 November 2026
- **Tag:** `v7-5-beta`
- **Game:** КРЕМЛЬ 1991 — General Secretary
- **Builds:** browser, terminal, itch.io HTML ZIP

This patch started with an itch.io review: *“best game ever, but please add tutorial.”* BETA v7-5 adds a proper First-Year Orientation, a regional pressure system for the late Union, event cues, and a final Red Millennium event for runs strong enough to reach it.

## What changed

- **First-Year Orientation** — optional from the title screen or `--tutorial`. Five cynical staff memos cover the board, `d` Dossier, `i` political capital, `o` standing orders, plan fatigue, the court danger line, the 1991 gate, the 1986 oil glut and Republic Unrest. The first year gets margin notes; no resources are spent and difficulty is unchanged.
- **Republic Unrest** — Baltic, Ukraine, Caucasus and Central Asia now have their own pressure track. Low Order, open politics and the 1986–1991 shocks raise it; tours, subsidies, a federal compact and the Union Treaty lower it. A hot republic costs Order and Faith, and at 75 it books a crisis.
- **Red Millennium capstone** — a rare 2001 event for strong runs, with three political answers and an ending that remembers the choice.
- **Event cues** — short terminal tones and browser Web Audio for incidents, agenda results and endings, with a sound toggle. Tests, pipes and recorders stay silent.
- **Harder late game** — regional pressure and the Millennium regional gate make hard and extreme meaningfully harsher, without turning the national arithmetic inside out.
- **Android-ready browser build** — one-column mobile layout, safe-area and dynamic-viewport support, 44px touch targets, 16px input text, and no forced keyboard popup after every answer.
- **New screenshots and devlog** — `itch_devlog/DEVLOG.md` keeps the reviewer note and the design rationale; `itch_page/screenshots/` now includes the v7-5 board and the tutorial memo.

## Balance snapshot

Five seeds per mode, clock off. The bot plays the market path and does not actively manage the republics, so the floor and ceiling bracket the regional problem.

| Mode | Floor | Ceiling |
|---|---:|---:|
| easy | 5/5 | 5/5 |
| medium | 5/5 | 5/5 |
| hard | 3/5 | 3/5 |
| extreme | 2/5 | 3/5 |
| flash | 5/5 | 4/5 |
| historical | 5/5 | 5/5 |

## Play

- **Browser:** <https://mahakammoonlightstudio-beep.github.io/kreml-1991/play/>
- **itch.io:** <https://mahakam-moonlight-studio.itch.io/kreml-1991>
- **Terminal:** clone the repository and run `python main.py` with Python 3.8 or newer.
- **Download:** this release includes `kreml-1991-web.zip`, the same browser build packaged for itch.io with `index.html` at the ZIP root.

## Verification

- 56/56 mechanic checks
- 10/10 browser replay checks
- 4/4 web build checks
- Save/dossier/load/resume flow passes
- Headless smoke run passes
- Browser bundle is current (310 KB)
- Android layout checked at 390×844 with touch emulation: no horizontal overflow, 44px controls, 16px input, mobile hint and placeholder

## Notes

- The first browser visit downloads about 12 MB of Pyodide from a CDN; after that the game runs locally in the tab.
- The browser build is mobile-friendly and can be installed to the Android home screen, but it is not a native APK.
- Existing saves are handled by the normal save schema; old incompatible saves are refused rather than corrupted.
- Full development notes and the reviewer screenshot are in [`itch_devlog/DEVLOG.md`](https://github.com/mahakammoonlightstudio-beep/kreml-1991/blob/main/itch_devlog/DEVLOG.md).
