# itch.io page — paste-ready sheet

This folder is the source of truth for the itch.io project page. Fields below
follow the current itch.io form, in order. Copy the values; do not retype the
title, because the Cyrillic and the em dash are part of it.

**This edition is pure play.** The GitHub Pages site is the landing page and the
case file. The itch ZIP contains the game only: no landing copy, no support
panel, no site chrome. Keep the itch page description doing the marketing work.

Assets here:

| File | Use |
|---|---|
| `cover.png` | Cover image, exactly **630 × 500** (required) |
| `screenshots/01-board.png` | Screenshot: the situation room |
| `screenshots/02-directive.png` | Screenshot: a yearly directive |
| `screenshots/03-ending.png` | Screenshot: the challenge card |
| `screenshots/04-title.png` | Screenshot: the appointment screen |
| `screenshots/05-tutorial.png` | Screenshot: the guided first year |
| `description.html` | Paste into **Description** (itch accepts HTML) |

---

## 1. Project

| Field | Value |
|---|---|
| **Title** | `КРЕМЛЬ 1991 — General Secretary` |
| **Project URL** | `kreml-1991` — <https://mahakam-moonlight-studio.itch.io/kreml-1991> |
| **Short description** | `27 years, five gauges, one signature. A text-based Soviet alternate-history game, 1964–1991.` |
| **Classification** | `Games` |
| **Kind of project** | `HTML` |
| **Release status** | `Released` |
| **Pricing** | `No payments` |

Notes:

- **Project URL.** The page is live at
  <https://mahakam-moonlight-studio.itch.io/kreml-1991>. If the URL ever changes,
  update the landing page and play page links, then rebuild the ZIP.
- **Kind of project.** Choose **HTML**, not Downloadable. The ZIP contains an
  `index.html` at its root and runs in the itch iframe. The terminal build is
  available from GitHub, not as a separate itch download.
- **Pricing.** Keep **No payments**. The game is free and the donation links are
  external (PayPal, Sociabuzz, Saweria). Do not enable itch's "ask for a
  donation" gate unless you deliberately want a second payment path.
- **Release status.** `Released` is accurate for the current **BETA v8** build;
  the title still says BETA, and updates are expected. The pure-play build
  includes the situation room, the named Politburo cast, the Three Funerals 1982
  opening, the challenge card and the mobile layout.

---

## 2. Uploads

| Field | Value |
|---|---|
| **File** | `../itch_upload/kreml-1991-web.zip` |
| **Embed** | `Click to play` (or `Embed in page` if you prefer inline) |
| **Viewport** | `1280 × 800` |
| **Mobile friendly** | `yes` |
| **Fullscreen button** | `yes` |

`index.html` must sit at the **ZIP root**. The generated zip already does this.
Rebuild it after changing `kreml/`, `docs/play/` or the brand assets:

```bash
python tools/build_web.py
python tools/build_itch.py
```

The ZIP carries the favicon, apple-touch icon, 192/512 app icons, the web
manifest, the local OFL fonts and the licensed Kremlin photograph. Nothing in
the play page depends on the GitHub landing assets.

`body.itch-build` removes the landing chrome, support panel and external-site
links from the play page. The game itself is unchanged.

---

## 3. Details

| Field | Value |
|---|---|
| **Description** | Paste the contents of `description.html` |
| **Genre** | `Strategy` |
| **Tags** | `soviet`, `alternate-history`, `text-based`, `political-sim`, `cold-war`, `terminal`, `python`, `singleplayer`, `historical`, `bleak` |
| **AI generation disclosure** | `Yes — This project contains the output of Generative AI` |
| **App store links** | Leave all blank |
| **Custom noun** | Leave blank (`game` is correct) |
| **Community** | `Comments` |
| **Visibility & access** | `Draft` now; `Public` after the URL and page are checked |
| **Cover image** | `cover.png` (630 × 500) |
| **Gameplay video** | Leave blank — no trailer exists yet |
| **Screenshots** | Upload the five files in `screenshots/` |

### AI disclosure wording

itch asks whether the project contains output from generative AI. Answer **Yes**.
A truthful explanation if itch offers a free-text box:

> This release contains generative-AI output used for code, copy and art
> assistance. All of it was reviewed, edited and integrated by the developers.

### Screenshot captions

1. **01-board.png** — The situation room, 1975: five gauges, valas, the court, political capital, Republic Unrest, and the transcript underneath.
2. **02-directive.png** — The yearly directive: fourteen campaigns on the table for 1964, each one a single order.
3. **03-ending.png** — The challenge card: seed 7, THE UNION SURVIVES, score 361 and the replay link.
4. **04-title.png** — The appointment: difficulty, timeline, optional guidance, and a seeded run waiting to be taken.
5. **05-tutorial.png** — The guided first year: the margin note, ORIENTATION COMPLETE, and the 1964 board it told you to read.

All five are captures of **this itch build**, not of the terminal and not of the
GitHub play page. `python tools/capture_room.py` replays the seed-7 autopilot
through the browser driver, drives the exported page in headless Chromium and
writes them at native size. Re-run it after changing `docs/play/` or the build:

```bash
python tools/build_web.py
python tools/build_itch.py
python tools/capture_room.py
```

`tools/capture_stills.py` still renders terminal plates, but it writes into this
same folder — do not run it after capturing the room.

### Content notes

Add this near the end of the description if itch asks for content warnings:

> Contains historical political violence, death and state collapse. No graphic imagery.

---

## 4. Donation links

The game is free. These are the only donation destinations; they are already in
the landing page, the play page footer and the itch description:

- PayPal — <https://www.paypal.com/paypalme/mrfozan>
- Sociabuzz — <https://sociabuzz.com/mahakam_moonlight_studio/tribe>
- Saweria — <https://saweria.co/MahakamMoonStudio>

Donations never unlock content. Keep that sentence in the description so nobody
thinks there is a paid tier.

---

## 5. Published URL

The page is live at <https://mahakam-moonlight-studio.itch.io/kreml-1991>. The
landing page, play page and footer point there. If the URL ever changes, update
`docs/index.html` (JSON-LD, hero, “Where to play” and “Elsewhere”) and
`docs/play/index.html`, then rebuild the ZIP and push `docs/`.

```bash
python tools/build_itch.py
```

---

## 6. Final checklist

- [ ] Title and URL set
- [ ] Short description under 160 characters
- [ ] Kind = HTML, ZIP has `index.html` at root
- [ ] Pricing = No payments
- [ ] New v8 cover 630 × 500 uploaded
- [ ] Five screenshots uploaded with captions
- [ ] Genre = Strategy, ten tags entered
- [ ] AI disclosure = Yes
- [ ] Community = Comments
- [ ] Description pasted from `description.html`
- [ ] Donation links present in description
- [ ] Visibility = Draft until the page is checked, then Public
- [ ] Landing-page itch URL replaced after publishing
