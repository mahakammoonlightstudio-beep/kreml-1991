/* КРЕМЛЬ 1991 — BETA v8 browser build.
 *
 * The real game (docs/play/game_bundle.js) runs under Pyodide. The Python
 * driver (kreml_web.py) replays the run from its opening with every answer so
 * far and stops at the next question, so this file only has to: render the
 * transcript, read the room, take one line, repeat.
 *
 * v8 adds the situation room (a live HUD parsed from the printed board), the
 * seed challenge card, URL-seeded runs, and audio that is off by default.
 */
(() => {
  "use strict";

  const PY_URL = "https://cdn.jsdelivr.net/pyodide/v0.28.0/full/";
  const STORE_KEY = "kreml1991.web.run.v1";
  const SOUND_KEY = "kreml1991.sound.v1";
  const TIMEOUT = "__timeout__";      // keep in sync with kreml_web.TIMEOUT_TOKEN

  const $ = (id) => document.getElementById(id);
  const setup = $("setup"), game = $("game"), challenge = $("challenge");
  const screenEl = $("screen"), choicesEl = $("choices"), lineEl = $("line");
  const formEl = $("answer"), statusEl = $("status"), bootnote = $("bootnote");
  const startBtn = $("start"), resumeBtn = $("resume"), restartBtn = $("restart");
  const termTitle = $("termtitle"), tutorialBtn = $("tutorial"), soundBtn = $("sound");
  const hintEl = $("hint"), seedNote = $("seednote");
  const isTouch = () => window.matchMedia("(pointer: coarse)").matches;
  const isCompact = () => window.innerWidth <= 768;

  let call = null;            // Python _call()
  let busy = false, finished = false;
  let soundOn = false;
  let audio = null;
  let clockTimer = null, clockEnd = 0, clockTick = null;
  let plain = "";             // recent output without ANSI, for menus and HUD
  let record = null;          // the run in this tab (answers + config)
  let finalRecord = null;     // the finished run, for the challenge card
  let meta = null;
  let challengeText = "";

  const pick = { mode: "medium", timeline: "rails", tutorial: false, seed: null };

  /* ─────────────────────────── ANSI → HTML ─────────────────────────── */

  const SGR = {
    "0": () => ({ fg: null, bold: false, dim: false }),
    "1": () => ({ bold: true }), "22": () => ({ bold: false, dim: false }),
    "90": () => ({ dim: true }),
    "91": () => ({ fg: "r" }), "92": () => ({ fg: "g" }), "93": () => ({ fg: "y" }),
    "94": () => ({ fg: "b" }), "95": () => ({ fg: "m" }), "96": () => ({ fg: "c" }),
    "97": () => ({ fg: "w" }), "39": () => ({ fg: null }),
  };
  let style = { fg: null, bold: false, dim: false };

  const esc = (s) => String(s).replace(/[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function cssClass() {
    const out = [];
    if (style.fg) out.push(style.fg);
    if (style.bold) out.push("bold");
    if (style.dim) out.push("dim");
    return out.join(" ");
  }

  function toHtml(text) {
    let html = "", buf = "";
    const flush = () => {
      if (!buf) return;
      const cls = cssClass();
      html += cls ? `<span class="${cls}">${esc(buf)}</span>` : esc(buf);
      buf = "";
    };
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === "\u001b" && text[i + 1] === "[") {
        const end = text.indexOf("m", i + 2);
        if (end !== -1) {
          flush();
          for (const code of text.slice(i + 2, end).split(";")) {
            const apply = SGR[code || "0"];
            if (apply) Object.assign(style, apply());
          }
          i = end;
          continue;
        }
      }
      if (ch === "\r") continue;          // animations are off in this build
      buf += ch;
    }
    flush();
    return html;
  }

  const stripAnsi = (s) => s.replace(/\u001b\[[0-9;]*m/g, "");

  function append(text, reset) {
    if (!text) return;
    if (reset) {
      screenEl.innerHTML = "";
      plain = "";
      style = { fg: null, bold: false, dim: false };
    }
    screenEl.insertAdjacentHTML("beforeend", toHtml(text));
    plain = (plain + stripAnsi(text)).slice(-16000);
    screenEl.scrollTop = screenEl.scrollHeight;
    updateHud();
  }

  /* ─────────────────────────── the room ───────────────────────────── */

  function lastMatches(re, text) {
    const flags = re.flags.includes("g") ? re.flags : re.flags + "g";
    const g = new RegExp(re.source, flags);
    let m, last = null;
    while ((m = g.exec(text)) !== null) {
      last = m;
      if (m.index === g.lastIndex) g.lastIndex++;
    }
    return last;
  }

  function setMeter(id, value) {
    const el = document.querySelector(`[data-gauge="${id}"]`);
    if (!el) return;
    const fill = el.querySelector(".meter__bar i");
    const label = el.querySelector(".meter__val");
    if (value === null || Number.isNaN(value)) {
      el.dataset.level = "empty";
      label.textContent = "—";
      fill.style.width = "0%";
      return;
    }
    const v = Math.max(0, Math.min(100, value));
    el.dataset.level = v < 25 ? "critical" : (v < 45 ? "low" : "ok");
    label.textContent = String(v);
    fill.style.width = v + "%";
  }

  function updateHud() {
    const ym = lastMatches(
      /YEAR (\d{4})\s{2,}([^\n]+?)\s{2,}\[([^\]]+)\]/, plain);
    $("hud-year").textContent = ym ? ym[1] : "——";
    $("hud-meta").textContent = ym
      ? `${ym[2]} · ${ym[3]}` : "Waiting for the appointment";

    for (const [id, word] of [
      ["ECONOMY", "Economy"], ["MILITARY", "Military"], ["ORDER", "Order"],
      ["FAITH", "People"], ["PRESTIGE", "Prestige"],
    ]) {
      const m = lastMatches(
        new RegExp(`${word}\\s+\\([^)]*\\)\\s+\\[[^\\]]*\\]\\s+(\\d{1,3})`), plain);
      setMeter(id, m ? Number(m[1]) : null);
    }

    const hc = lastMatches(
      /Valas\s+\(gold &\s*\$\)\s+\[[^\]]*\]\s+(\d{1,3})/, plain);
    $("hud-hc").textContent = hc ? hc[1] : "—";

    const court = lastMatches(
      /Politburo Old Guard \[[^\]]*\]\s+(\d{1,3})\s+Reformers \[[^\]]*\]\s+(\d{1,3})\s+Army \[[^\]]*\]\s+(\d{1,3})/,
      plain);
    $("hud-court").textContent = court
      ? `${court[1]}/${court[2]}/${court[3]}` : "—";

    const inf = lastMatches(
      /Political capital[^\n]*?(\d{1,3})(?=\s*(?:\/|$))/m, plain);
    $("hud-inf").textContent = inf ? `${inf[1]} ❖` : "—";

    const repLine = (plain.match(/^\s*Republics[^\n]*$/gm) || []).pop();
    const reps = repLine ? (repLine.match(/\b\d{1,3}\b/g) || []).slice(0, 4) : [];
    $("hud-rep").textContent = reps.length === 4
      ? `B${reps[0]} U${reps[1]} C${reps[2]} A${reps[3]}` : "—";

    const agenda = lastMatches(/^\s*Agenda\s{2,}([^\n]+)$/m, plain);
    $("hud-agenda").textContent = agenda ? agenda[1].trim() : "No demand tabled.";

    if (ym) termTitle.textContent = `kreml_1991 — ${ym[1]}`;
    if (!clockTimer) {
      statusEl.textContent = finished ? "run over" : (ym ? `year ${ym[1]}` : "ready");
    }
  }

  /* ─────────────────────────── menus & buttons ─────────────────────── */

  const lastLine = () => {
    const lines = plain.split("\n").filter((l) => l.trim() !== "");
    return lines.length ? lines[lines.length - 1] : "";
  };

  function parseNumbers() {
    // Menus always start at "1." — take the LAST such line, then collect the
    // block after it. That skips the numbered lists of screens already passed.
    const lines = plain.split("\n");
    let start = -1;
    for (let i = lines.length - 1; i >= 0 && i > lines.length - 90; i--) {
      if (/^ {1,6}1\. \S/.test(lines[i])) { start = i; break; }
    }
    if (start === -1) return [];
    const seen = new Map();
    for (let i = start; i < lines.length; i++) {
      const m = lines[i].match(/^ {1,6}(\d{1,2})\. (.+)$/);
      if (!m) continue;
      const n = Number(m[1]);
      if (n === 0 || seen.has(n)) continue;
      seen.set(n, m[2].trim());
    }
    const nums = [...seen.keys()].sort((a, b) => a - b);
    const top = nums.length ? nums[nums.length - 1] : 0;
    if (!top || top !== nums.length || top > 30) return [];   // must be 1..N
    return nums.map((n) => [n, seen.get(n)]);
  }

  function drawChoices() {
    choicesEl.textContent = "";
    const choose = (value) => {
      if (isTouch()) lineEl.blur();   // tap the board, not the mobile keyboard
      submitLine(value);
    };
    if (finished) return;

    if (lastLine().includes("[Enter] proceed")) {
      const row = document.createElement("button");
      row.type = "button";
      row.innerHTML = `<span class="n">↵</span>Proceed · dossier · capital · orders`;
      row.addEventListener("click", () => choose(""));
      choicesEl.appendChild(row);
      return;
    }
    for (const [n, label] of parseNumbers()) {
      const short = label.length > 96 ? label.slice(0, 93) + "…" : label;
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = `<span class="n">${n}</span>${esc(short)}`;
      b.addEventListener("click", () => choose(String(n)));
      choicesEl.appendChild(b);
    }
  }

  /* ─────────────────────────── talking to Python ───────────────────── */

  const paint = () => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));

  /* ─────────────────────────── event sound ─────────────────────────── */

  function ensureAudio() {
    if (audio) return audio;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    audio = new AC();
    return audio;
  }

  function cue(kind) {
    if (!soundOn) return;
    const ctx = ensureAudio();
    if (!ctx) return;
    if (ctx.state === "suspended") ctx.resume();
    const notes = {
      event: [[196, 0.22], [294, 0.26]],
      good: [[262, 0.18], [392, 0.22]],
      bad: [[147, 0.24], [110, 0.30]],
      ending: [[196, 0.30], [147, 0.30], [98, 0.46]],
    }[kind] || [[196, 0.20]];
    const now = ctx.currentTime;
    notes.forEach(([freq, duration], i) => {
      const start = now + i * 0.13;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(0.035, start + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start);
      osc.stop(start + duration + 0.04);
    });
  }

  function syncSoundButton() {
    if (!soundBtn) return;
    soundBtn.textContent = soundOn ? "Sound on" : "Sound off";
    soundBtn.setAttribute("aria-pressed", String(soundOn));
  }

  function lock(on) {
    busy = on;
    lineEl.disabled = on || finished;
    startBtn.disabled = on || !call;
    resumeBtn.disabled = on;
  }

  async function invoke(kind, payload) {
    lock(true);
    await paint();
    try {
      return JSON.parse(call(kind, JSON.stringify(payload || {})));
    } finally {
      lock(false);
    }
  }

  /* ─────────────────────────── the clock ───────────────────────────── */

  function clearClock() {
    if (clockTimer !== null) {
      clearInterval(clockTimer);
      clockTimer = null;
    }
    clockTick = null;
    if (!finished) updateHud();
  }

  function armClock() {
    clearClock();
    if (finished || busy || !call) return;
    const m = plain.slice(-500).match(/\u23f1 (\d+)s\)\s*$/);
    if (!m) return;
    clockEnd = Date.now() + Number(m[1]) * 1000;
    const tick = () => {
      const left = Math.max(0, Math.ceil((clockEnd - Date.now()) / 1000));
      statusEl.textContent = `\u23f1 ${left}s`;
      if (left <= 0) {
        clearClock();
        submitLine(TIMEOUT);          // the room moves on without you
      }
    };
    clockTick = tick;
    tick();
    clockTimer = setInterval(tick, 200);
  }

  /* ─────────────────────────── challenge card ─────────────────────── */

  function cleanFate(line) {
    return line.replace(/█+/g, "").replace(/\s+/g, " ").trim();
  }

  function showChallenge(snap) {
    const seed = snap && snap.seed != null ? snap.seed : (pick.seed != null ? pick.seed : "—");
    const scoreM = lastMatches(/Legacy score:\s*(\d+)/, plain);
    const titleM = lastMatches(/Legacy score:\s*\d+\s*—\s*([^\n]+)/, plain);
    const governedM = lastMatches(/Governed years:\s*(\d+)/, plain);
    const fateM = lastMatches(
      /(THE RED MILLENNIUM[^\n]*|THE UNION SURVIVES[^\n]*|REMOVED, \d+|COLLAPSE, \d+|You resigned[^\n]*)/,
      plain);
    const fate = fateM ? cleanFate(fateM[1]) : "THE RUN IS OVER";
    const modeId = snap && snap.mode ? snap.mode : pick.mode;
    const tlId = snap && snap.timeline ? snap.timeline : pick.timeline;
    const modeLabel = meta && meta.modes.find((m) => m.id === modeId)
      ? meta.modes.find((m) => m.id === modeId).label : modeId.toUpperCase();
    const tlLabel = meta && meta.timelines.find((t) => t.id === tlId)
      ? meta.timelines.find((t) => t.id === tlId).label : tlId.toUpperCase();
    const score = scoreM ? scoreM[1] : "—";
    const title = titleM ? titleM[1].trim() : "";
    const years = governedM ? governedM[1] : "—";
    const url = `${location.origin}${location.pathname}?seed=${seed}&mode=${modeId}&timeline=${tlId}`;

    $("card-seed").textContent = `SEED ${seed}`;
    $("card-fate").textContent = fate;
    $("card-score").textContent = score === "—"
      ? "SCORE —" : `SCORE ${score}${title ? " · " + title : ""}`;
    $("card-meta").textContent = `${years} years · ${modeLabel} · ${tlLabel}`;
    $("card-url").textContent = url.replace(/^https?:\/\//, "");
    $("copy-status").textContent = "";

    challengeText = [
      "КРЕМЛЬ 1991 — BETA v8",
      `SEED ${seed} · ${modeLabel} · ${tlLabel}`,
      `${fate} · SCORE ${score}`,
      title ? `${years} years · ${title}` : `${years} years governed`,
      "Can you keep the red flag?",
      url,
    ].join("\n");

    challenge.hidden = false;
    requestAnimationFrame(() => challenge.scrollIntoView({ block: "start", behavior: "smooth" }));
  }

  async function copyCard() {
    const note = $("copy-status");
    try {
      await navigator.clipboard.writeText(challengeText);
      note.textContent = "Copied. Hand it to a friend.";
      return;
    } catch (_) { /* fall through to the old method */ }
    try {
      const ta = document.createElement("textarea");
      ta.value = challengeText;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      note.textContent = "Copied. Hand it to a friend.";
    } catch (_) {
      note.textContent = "The clipboard refused. Select the card text and copy it.";
    }
  }

  /* ─────────────────────────── results ─────────────────────────────── */

  function applyResult(res) {
    append(res.text || "", !!res.reset);
    const fresh = res.text || "";
    if (!res.reset) {
      if (/COLLAPSE|REMOVED|RED MILLENNIUM|Legacy score/.test(fresh)) cue("ending");
      else if (/Agenda met/.test(fresh)) cue("good");
      else if (/Agenda missed/.test(fresh)) cue("bad");
      else if (/INCIDENT|THE REPUBLICS|ORIENTATION/.test(fresh)) cue("event");
    }
    finished = !!res.done;
    drawChoices();
    updateHud();
    if (finished) {
      finalRecord = null;
      try { finalRecord = JSON.parse(call("snapshot", "{}")); } catch (_) {}
      record = null;
      lineEl.disabled = true;
      lineEl.placeholder = "This run is over — take a new appointment.";
      resumeBtn.hidden = true;
      try { localStorage.removeItem(STORE_KEY); } catch (_) {}
      clearClock();
      showChallenge(finalRecord);
    } else {
      lineEl.disabled = false;
      lineEl.placeholder = (isTouch() || isCompact())
        ? "Type an answer"
        : "Type your answer, then Enter";
      if (!isTouch()) lineEl.focus();   // do not pop the Android keyboard every turn
      armClock();
      remember();
    }
  }

  function remember() {
    if (finished) return;
    try {
      record = JSON.parse(call("snapshot", "{}"));
      record.year = (plain.match(/YEAR (\d{4})/g) || []).pop()?.replace("YEAR ", "") || "";
      localStorage.setItem(STORE_KEY, JSON.stringify(record));
    } catch (_) { /* private mode: just no resume button */ }
  }

  async function submitLine(value) {
    if (busy || finished || !call) return;
    clearClock();
    lineEl.value = "";
    applyResult(await invoke("answer", { text: value }));
  }

  /* ─────────────────────────── setup ───────────────────────────────── */

  function readParams() {
    try {
      const p = new URLSearchParams(location.search);
      const s = parseInt(p.get("seed") || "", 10);
      if (Number.isFinite(s) && s > 0) pick.seed = s;
      if (p.get("mode")) pick.mode = p.get("mode");
      if (p.get("timeline")) pick.timeline = p.get("timeline");
      pick.tutorial = p.get("tutorial") === "1" || p.get("tutorial") === "true";
    } catch (_) { /* old browser, no URLSearchParams */ }
  }

  function syncSeedNote() {
    if (!seedNote) return;
    if (pick.seed == null) {
      seedNote.hidden = true;
      seedNote.textContent = "";
      return;
    }
    const mode = meta && meta.modes.find((m) => m.id === pick.mode)
      ? meta.modes.find((m) => m.id === pick.mode).label : pick.mode;
    const tl = meta && meta.timelines.find((t) => t.id === pick.timeline)
      ? meta.timelines.find((t) => t.id === pick.timeline).label : pick.timeline;
    seedNote.hidden = false;
    seedNote.innerHTML = `<b>Challenge seed ${pick.seed}</b> · ${esc(mode)} · ${esc(tl)}. ` +
      "The seed keeps the history; your answers are the variable.";
  }

  function chips(container, items, key, note) {
    container.textContent = "";
    for (const item of items) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "chip";
      b.setAttribute("aria-pressed", String(pick[key] === item.id));
      b.innerHTML = `<span class="chip__label">${esc(item.label)}</span>` +
        `<small>${esc(note(item))}</small>`;
      b.addEventListener("click", () => {
        pick[key] = item.id;
        for (const other of container.children) other.setAttribute("aria-pressed", "false");
        b.setAttribute("aria-pressed", "true");
        syncSeedNote();
      });
      container.appendChild(b);
    }
  }

  function syncSetup() {
    if (tutorialBtn) {
      tutorialBtn.setAttribute("aria-pressed", String(pick.tutorial));
    }
    syncSeedNote();
  }

  function showSetup() {
    setup.hidden = false;
    game.hidden = true;
    challenge.hidden = true;
  }

  function showGame() {
    setup.hidden = true;
    game.hidden = false;
    challenge.hidden = true;
    requestAnimationFrame(() => game.scrollIntoView({ block: "start", behavior: "auto" }));
  }

  async function startRun() {
    clearClock();
    ensureAudio();
    finished = false;
    finalRecord = null;
    showGame();
    append("", true);
    record = null;
    resumeBtn.hidden = true;
    try { localStorage.removeItem(STORE_KEY); } catch (_) {}
    const payload = { mode: pick.mode, timeline: pick.timeline, tutorial: pick.tutorial };
    if (pick.seed != null) payload.seed = pick.seed;
    applyResult(await invoke("start", payload));
  }

  async function resumeRun() {
    if (!record) return;
    clearClock();
    finished = false;
    showGame();
    append("", true);
    applyResult(await invoke("restore", record));
  }

  function newAppointment() {
    clearClock();
    finished = false;
    finalRecord = null;
    record = null;
    pick.seed = null;
    challenge.hidden = true;
    challengeText = "";
    showSetup();
    syncSetup();
    updateHud();
  }

  /* ─────────────────────────── boot ────────────────────────────────── */

  const BOOTSTRAP = `
import json, sys
sys.path.insert(0, "/game")
sys.path.insert(0, "/play")
import kreml_web
from kreml.content.modes import MODES, MODE_ORDER
from kreml.content.timelines import TIMELINES, TIMELINE_ORDER

_session = kreml_web.Session("/game")

def _meta():
    return json.dumps({
        "modes": [{"id": m, "label": MODES[m]["label"],
                   "note": "%d reserves" % MODES[m]["lifelines"]} for m in MODE_ORDER],
        "timelines": [{"id": t, "label": TIMELINES[t].label,
                       "note": "%d–%d" % (TIMELINES[t].year, TIMELINES[t].end_year)}
                      for t in TIMELINE_ORDER],
    })

def _call(kind="snapshot", payload="{}"):
    p = json.loads(payload or "{}")
    if kind == "meta":
        return _meta()
    if kind == "start":
        out = _session.start(p.get("mode"), p.get("timeline"), p.get("seed"),
                             p.get("tutorial", False))
    elif kind == "answer":
        out = _session.answer(p.get("text", ""))
    elif kind == "restore":
        out = _session.restore(p)
    else:
        out = _session.snapshot()
    return json.dumps(out)
`;

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error("could not load " + src));
      document.head.appendChild(s);
    });
  }

  async function boot() {
    try {
      bootnote.textContent = "Loading Python (≈12 MB, once)…";
      await loadScript(PY_URL + "pyodide.js");
      const py = await loadPyodide({ indexURL: PY_URL });

      bootnote.textContent = "Unpacking the Kremlin…";
      for (const [path, src] of Object.entries(self.KREML_BUNDLE || {})) {
        const dir = path.slice(0, path.lastIndexOf("/"));
        py.FS.mkdirTree(dir);
        py.FS.writeFile(path, src, { encoding: "utf8" });
      }
      py.FS.mkdirTree("/play");
      const driver = await (await fetch("kreml_web.py", { cache: "no-cache" })).text();
      py.FS.writeFile("/play/kreml_web.py", driver, { encoding: "utf8" });

      py.runPython(BOOTSTRAP);
      call = py.globals.get("_call");

      meta = JSON.parse(call("meta", "{}"));
      readParams();
      if (!meta.modes.some((m) => m.id === pick.mode)) pick.mode = "medium";
      if (!meta.timelines.some((t) => t.id === pick.timeline)) pick.timeline = "rails";
      chips($("modes"), meta.modes, "mode", (m) => m.note);
      chips($("timelines"), meta.timelines, "timeline", (t) => t.note);
      syncSetup();

      try {
        const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
        if (saved && Array.isArray(saved.answers) && saved.answers.length) {
          record = saved;
          resumeBtn.hidden = false;
          resumeBtn.textContent = saved.year
            ? `Continue the ${saved.year} run · ${saved.answers.length} answers`
            : "Continue last run";
        }
      } catch (_) {}

      bootnote.textContent = "Python ready. The room is waiting.";
      startBtn.disabled = false;
      lock(false);
      if (hintEl && (isTouch() || isCompact())) {
        hintEl.textContent = "Tap a numbered order; the field is for names and shortcuts";
      }
      if ((isTouch() || isCompact()) && !game.hidden) {
        lineEl.placeholder = "Type an answer";
      }
      if (!game.hidden && !isTouch()) lineEl.focus();
    } catch (err) {
      bootnote.textContent = "";
      startBtn.disabled = true;
      const note = document.createElement("p");
      note.className = "note";
      note.innerHTML = "The Python runtime could not be loaded (offline, or a blocked CDN). " +
        "The game itself is fine — <a href=\"https://github.com/mahakammoonlightstudio-beep/kreml-1991\">" +
        "clone the repo</a> and run <b>python main.py</b>.";
      const form = setup.querySelector(".briefing__form");
      if (form) form.appendChild(note);
      console.error(err);
    }
  }

  /* ─────────────────────────── wiring ──────────────────────────────── */

  formEl.addEventListener("submit", (e) => {
    e.preventDefault();
    submitLine(lineEl.value);
  });

  // A background tab throttles timers; on return, settle the clock immediately
  // from its real deadline instead of waiting for the next throttled tick.
  ["visibilitychange", "focus"].forEach((evt) =>
    document.addEventListener(evt, () => {
      if (!document.hidden && clockTick) clockTick();
    }));

  startBtn.addEventListener("click", startRun);
  resumeBtn.addEventListener("click", resumeRun);
  restartBtn.addEventListener("click", newAppointment);
  $("newrun").addEventListener("click", newAppointment);
  $("copy").addEventListener("click", copyCard);
  $("replay").addEventListener("click", () => {
    const snap = finalRecord;
    if (snap) {
      pick.mode = snap.mode || pick.mode;
      pick.timeline = snap.timeline || pick.timeline;
      pick.seed = snap.seed != null ? snap.seed : pick.seed;
      syncSetup();
    }
    startRun();
  });

  if (tutorialBtn) {
    tutorialBtn.addEventListener("click", () => {
      pick.tutorial = !pick.tutorial;
      tutorialBtn.setAttribute("aria-pressed", String(pick.tutorial));
    });
  }
  if (soundBtn) {
    try { soundOn = localStorage.getItem(SOUND_KEY) === "on"; } catch (_) {}
    syncSoundButton();
    soundBtn.addEventListener("click", () => {
      soundOn = !soundOn;
      try { localStorage.setItem(SOUND_KEY, soundOn ? "on" : "off"); } catch (_) {}
      syncSoundButton();
      if (soundOn) cue("good");
    });
  }

  lock(true);
  showSetup();
  updateHud();
  boot();
})();
