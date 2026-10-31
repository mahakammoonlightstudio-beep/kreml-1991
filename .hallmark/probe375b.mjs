// Probe 375 v2: reimplement the page's own scan exactly, dump tokens/gauges/best,
// and compare with the scrollLeft the page itself settled on.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';

let puppeteer = null;
const roots = [process.cwd(), 'C:/Users/Acer/.agents/skills/hallmark/scripts'];
try { roots.push(execSync('npm root -g', { encoding: 'utf8' }).trim()); } catch {}
outer: for (const root of roots) {
  for (const name of ['puppeteer-core', 'puppeteer']) {
    try {
      const req = createRequire(path.join(root, 'noop.js'));
      puppeteer = (await import(pathToFileURL(req.resolve(name)).href)).default;
      break outer;
    } catch {}
  }
}
if (!puppeteer) { console.log('no puppeteer'); process.exit(1); }
const chrome = [process.env.CHROME_PATH, 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'].find((p) => p && fs.existsSync(p));
const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(String(e && e.message || e).split('\n')[0]));
await page.setViewport({ width: 375, height: 812 });
await page.goto(pathToFileURL(path.resolve('docs/index.html')).href, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(() => (document.fonts ? document.fonts.ready : Promise.resolve()));
await new Promise((r) => setTimeout(r, 1500));
const out = await page.evaluate(() => {
  const pre = document.querySelector('.hero .session pre');
  const mark = (c) => '━▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▏░▒▓'.includes(c);
  const rows = [...pre.querySelectorAll('.ln')];
  const span = pre.clientWidth;
  const origin = pre.getBoundingClientRect().left - pre.scrollLeft;
  const caret = (row) => {
    const pos = [];
    let g = 0;
    const walk = (n) => { for (const c of n.childNodes) {
      if (c.nodeType === 3) { for (let j = 0; j <= c.data.length; j++) pos[g + j] = [c, j]; g += c.data.length; }
      else if (c.nodeType === 1) walk(c);
    } };
    walk(row);
    pos.len = g;
    return pos;
  };
  const range = document.createRange();
  const px = (ca, cb) => {
    range.setStart(ca[0], ca[1]);
    range.setEnd(cb[0], cb[1]);
    const r = range.getBoundingClientRect();
    return { l: r.left - origin, r: r.right - origin };
  };
  const tokens = [], gauges = [], edges = new Set([0]);
  const dump = [];
  for (const row of rows) {
    const text = row.textContent;
    const pos = caret(row);
    if (pos.len !== text.length) { dump.push('CARET MISMATCH ' + text.length + '/' + pos.len); continue; }
    const runs = [];
    let s = 0;
    const flush = (e) => { if (e > s) runs.push({ s, e, bar: mark(text[s]) }); };
    for (let i = 0; i < text.length; i++) if (text[i] === ' ') { flush(i); s = i + 1; }
    flush(text.length);
    let bar = null;
    for (const run of runs) {
      if (run.bar) { if (!bar) bar = run; continue; }
      const t = px(pos[run.s], pos[run.e]);
      tokens.push(t);
      edges.add(Math.round(t.l)); edges.add(Math.round(t.r));
      if (bar) {
        const b = px(pos[bar.s], pos[bar.e]);
        gauges.push({ l: b.l, r: t.r });
        edges.add(Math.round(b.l));
        bar = null;
      }
    }
  }
  const inside = (x) => tokens.some((t) => t.l + 0.5 < x && x < t.r - 0.5);
  const maxL = Math.max(0, pre.scrollWidth - span);
  const cands = [...edges].filter((x) => x >= 0 && x <= maxL).sort((a, b) => a - b);
  let best = null;
  for (const l of cands) {
    if (inside(l)) continue;
    let r = l + span;
    if (inside(r)) {
      const stops = [...edges].filter((x) => x <= r - 1 && x >= l + span * 0.5);
      r = stops.reverse().find((x) => !inside(x));
      if (r == null) continue;
    }
    if (r - l < span * 0.5) continue;
    const hit = gauges.filter((g) => l <= g.l + 0.5 && g.r <= r + 0.5).length;
    if (!best || hit > best.hit) best = { hit, l, w: r - l };
  }
  return {
    span, scrollWidth: pre.scrollWidth, scrollLeft: pre.scrollLeft,
    gaugeCount: gauges.length, tokenCount: tokens.length,
    gaugeSample: gauges.slice(0, 8).map((g) => g.l.toFixed(0) + '..' + g.r.toFixed(0)),
    candSample: cands.slice(0, 30).join(','),
    best: best ? { hit: best.hit, l: best.l.toFixed(1), w: best.w.toFixed(1) } : null,
    dump: dump.slice(0, 3),
  };
});
console.log(JSON.stringify(out, null, 1));
console.log('pageerrors:', JSON.stringify(errors));
await browser.close();
