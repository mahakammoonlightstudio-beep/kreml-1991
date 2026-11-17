КРЕМЛЬ 1991 — itch.io upload sheet
==================================

WHAT TO UPLOAD
  kreml-1991-web.zip          (project kind: HTML)
  index.html is at the ZIP ROOT. Do not zip the folder that contains it.

  The paste-ready form answers, cover, screenshots and description are in:
  ../itch_page/README.md
  ../itch_page/cover.png            (630 x 500)
  ../itch_page/screenshots/         (five stills)
  ../itch_page/description.html     (paste into Description)

WHERE TO CLICK
  https://itch.io/game/new
  Kind of project: HTML
  Uploads: kreml-1991-web.zip
  Embed: "Click to play" (or "Embed in page" if you want it inline)
  Viewport: 1280 x 800, mobile friendly: yes
  Fullscreen button: yes

PAGE
  Title:       КРЕМЛЬ 1991 — General Secretary
  URL:         kreml-1991
  Published:   https://mahakam-moonlight-studio.itch.io/kreml-1991
  Short:       27 years, five gauges, one signature. A text-based Soviet
               alternate-history game, 1964–1991, with an optional tutorial.
  Genre:       Strategy
  Tags:        soviet, alternate-history, text-based, political-sim,
               cold-war, terminal, python, singleplayer, historical, bleak
  Price:       No payments (the game is free; donations are external links)
  Platforms:   HTML5
  AI:          Yes — contains generative-AI output, reviewed by the developers

DONATIONS (already in the description and on the website)
  https://www.paypal.com/paypalme/mrfozan
  https://sociabuzz.com/mahakam_moonlight_studio/tribe
  https://saweria.co/MahakamMoonStudio

SUGGESTED DESCRIPTION
  Use ../itch_page/description.html. It covers the loop, the six difficulties,
  the four timelines, the First-Year Orientation, Republic Unrest, browser and
  terminal requirements, content notes and the donation links. Paste it as HTML.

AFTER PUBLISHING
  The page is live at
  https://mahakam-moonlight-studio.itch.io/kreml-1991
  docs/index.html and docs/play/index.html already point there.
  If the URL changes, update both files, rebuild the ZIP and push docs/.

REBUILD
  python tools/build_brand.py   # cover, social card, favicon set (needs Chrome)
  python tools/build_web.py     # refresh the game bundle after editing kreml/
  python tools/build_itch.py    # regenerate this zip, with brand assets inside

License: code MIT. Photographs on the landing page are CC BY / CC BY-SA,
credited in the page footer. The game itself ships no photographs.
