/* КРЕМЛЬ 1991 — browser build.
 *
 * The real game (docs/play/game_bundle.js) runs under Pyodide. The Python
 * driver (kreml_web.py) replays the run from 1964 with every answer so far and
 * stops at the next question, so this file only has to: render the text, take
 * one line, repeat.
 */
(() => {
  "use strict";

  const PY_URL = "https://cdn.jsdelivr.net/pyodide/v0.28.0/full/";
  const STORE_KEY = "kreml1991.web.run.v1";

  const $ = (id) => document.getElementById(id);
  const setup = $("setup"), game = $("game"), screenEl = $("screen");
  const choicesEl = $("choices"), lineEl = $("line"), formEl = $("answer");
  const statusEl = $("status"), bootnote = $("bootnote"), startBtn = $("start");
  const resumeBtn = $("resume"), restartBtn = $("restart"), termTitle = $("termtitle");

  let call = null;            // Python _call()
  let busy = false, finished = false;
  let plain = "";             // recent output without ANSI, for parsing menus
  let record = null;          // the run in this tab (answers + config)

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

  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

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
    plain = (plain + stripAnsi(text)).slice(-12000);
    screenEl.scrollTop = screenEl.scrollHeight;
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
    const add = (label, value, hint) => {
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = hint ? `<span class="n">${esc(label)}</span><span class="d">${esc(hint)}</span>`
                         : esc(label);
      b.addEventListener("click", () => submitLine(value));
      choicesEl.appendChild(b);
    };
    if (finished) return;

    if (lastLine().includes("[Enter] proceed")) {
      add("Continue ▸", "");
      add("d", "dossier");
      add("s", "save");
      add("l", "load");
      add("q", "resign");
      return;
    }
    for (const [n, label] of parseNumbers()) {
      const short = label.length > 92 ? label.slice(0, 89) + "…" : label;
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = `<span class="n">${n}</span>${esc(short)}`;
      b.addEventListener("click", () => submitLine(String(n)));
      choicesEl.appendChild(b);
    }
  }

  function statusFromTranscript() {
    const m = plain.match(/YEAR (\d{4})/g);
    const year = m ? m[m.length - 1].replace("YEAR ", "") : "";
    statusEl.textContent = finished ? "run over" : (year ? `year ${year}` : "ready");
    if (year) termTitle.textContent = `kreml_1991 — ${year}`;
  }

  /* ─────────────────────────── talking to Python ───────────────────── */

  const paint = () => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));

  function lock(on) {
    busy = on;
    lineEl.disabled = on || finished;
    startBtn.disabled = on;
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

  function applyResult(res) {
    append(res.text || "", !!res.reset);
    finished = !!res.done;
    drawChoices();
    statusFromTranscript();
    if (finished) {
      lineEl.disabled = true;
      lineEl.placeholder = "This run is over — start a new appointment.";
      record = null;
      resumeBtn.hidden = true;
      try { localStorage.removeItem(STORE_KEY); } catch (_) {}
    } else {
      lineEl.disabled = false;
      lineEl.placeholder = "Type your answer, then Enter";
      lineEl.focus();
    }
    remember();
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
    lineEl.value = "";
    applyResult(await invoke("answer", { text: value }));
  }

  /* ─────────────────────────── setup screen ────────────────────────── */

  const pick = { mode: "medium", timeline: "rails" };

  function chips(container, items, key, note) {
    container.textContent = "";
    for (const item of items) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "chip";
      b.setAttribute("aria-pressed", String(pick[key] === item.id));
      b.innerHTML = `${esc(item.label)}<small>${esc(note(item))}</small>`;
      b.addEventListener("click", () => {
        pick[key] = item.id;
        for (const other of container.children) other.setAttribute("aria-pressed", "false");
        b.setAttribute("aria-pressed", "true");
      });
      container.appendChild(b);
    }
  }

  function showSetup() {
    setup.hidden = false;
    game.hidden = true;
  }

  function showGame() {
    setup.hidden = true;
    game.hidden = false;
    startBtn.disabled = true;
    resumeBtn.disabled = false;
  }

  async function startRun() {
    showGame();
    append("", true);
    record = null;
    resumeBtn.hidden = true;
    try { localStorage.removeItem(STORE_KEY); } catch (_) {}
    applyResult(await invoke("start", { mode: pick.mode, timeline: pick.timeline }));
  }

  async function resumeRun() {
    if (!record) return;
    showGame();
    append("", true);
    applyResult(await invoke("restore", record));
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
        out = _session.start(p.get("mode"), p.get("timeline"), p.get("seed"))
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

      const meta = JSON.parse(call("meta", "{}"));
      chips($("modes"), meta.modes, "mode", (m) => m.note);
      chips($("timelines"), meta.timelines, "timeline", (t) => t.note);

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

      bootnote.textContent = "Python ready.";
      startBtn.disabled = false;
      lock(false);
      if (!game.hidden) lineEl.focus();
    } catch (err) {
      bootnote.textContent = "";
      startBtn.disabled = true;
      const note = document.createElement("p");
      note.className = "note";
      note.innerHTML = "The Python runtime could not be loaded (offline, or a blocked CDN). " +
        "The game itself is fine — <a href=\"https://github.com/mahakammoonlightstudio-beep/kreml-1991\">" +
        "clone the repo</a> and run <b>python main.py</b>.";
      setup.querySelector(".card").appendChild(note);
      console.error(err);
    }
  }

  /* ─────────────────────────── wiring ──────────────────────────────── */

  formEl.addEventListener("submit", (e) => {
    e.preventDefault();
    submitLine(lineEl.value);
  });
  startBtn.addEventListener("click", startRun);
  resumeBtn.addEventListener("click", resumeRun);
  restartBtn.addEventListener("click", () => {
    finished = false;
    record = null;
    resumeBtn.hidden = true;
    showSetup();
    statusEl.textContent = "";
    termTitle.textContent = "kreml_1991 — python in the browser";
  });

  lock(true);
  showSetup();
  boot();
})();
