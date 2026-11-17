# itch.io page — paste-ready sheet

This folder is the source of truth for the itch.io project page. Fields below
follow the current itch.io form, in order. Copy the values; do not retype the
title, because the Cyrillic and the em dash are part of it.

Assets here:

| File | Use |
|---|---|
| `cover.png` | Cover image, exactly **630 × 500** (required) |
| `screenshots/01-board.png` | Screenshot: the v7 board |
| `screenshots/02-directive.png` | Screenshot: a yearly directive |
| `screenshots/03-ending.png` | Screenshot: the 1991 report |
| `screenshots/04-title.png` | Screenshot: the appointment screen |
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
- **Release status.** `Released` is accurate for the current BETA v7 build; the
  title still says BETA, and updates are expected.

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

The ZIP now carries the favicon, apple-touch icon, 192/512 app icons and the
web manifest, so the embedded page matches the GitHub Pages copy.

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
| **Screenshots** | Upload the four files in `screenshots/` |

### AI disclosure wording

itch asks whether the project contains output from generative AI. Answer **Yes**.
A truthful explanation if itch offers a free-text box:

> This release contains generative-AI output used for code, copy and art
> assistance. All of it was reviewed, edited and integrated by the developers.

### Screenshot captions

1. **01-board.png** — The v7 board: five gauges, the valas reserve, the court and the year's agenda.
2. **02-directive.png** — The yearly directive: one public campaign, chosen from the groups on the table.
3. **03-ending.png** — The 1991 divergence report: what your century changed, and what it cost.
4. **04-title.png** — The appointment: difficulty, timeline and the name for the history books.

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
- [ ] Cover 630 × 500 uploaded
- [ ] Four screenshots uploaded with captions
- [ ] Genre = Strategy, ten tags entered
- [ ] AI disclosure = Yes
- [ ] Community = Comments
- [ ] Description pasted from `description.html`
- [ ] Donation links present in description
- [ ] Visibility = Draft until the page is checked, then Public
- [ ] Landing-page itch URL replaced after publishing
