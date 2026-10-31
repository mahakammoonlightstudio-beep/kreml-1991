// Replicate sloplint-render check 58's per-window word count and dump contributions.
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
await page.setViewport({ width: 1440, height: 900 });
await page.goto(pathToFileURL(path.resolve('docs/index.html')).href, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(() => (document.fonts ? document.fonts.ready : Promise.resolve()));
await new Promise((r) => setTimeout(r, 1600));
const out = await page.evaluate(() => {
  const vis = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const words = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = tw.nextNode())) {
    const p = n.parentElement;
    if (!p || !vis(p) || p.closest('script, style, noscript, svg, [data-slot], [data-credits]')) continue;
    const t = n.textContent.trim(); if (!t) continue;
    const pr = p.getBoundingClientRect();
    const c = t.split(/\s+/).filter((w) => /[A-Za-z]{2,}/.test(w)).length;
    if (c) words.push({ top: pr.top + scrollY, bottom: pr.bottom + scrollY, c, el: (p.className ? p.tagName + '.' + String(p.className).split(' ')[0] : p.tagName), txt: t.slice(0, 36) });
  }
  const H = document.documentElement.scrollHeight;
  const rows = [];
  let maxWords = 0, at = 0;
  for (let y = 0; y < H; y += 50) {
    const contributions = [];
    let w = 0;
    for (const x of words) {
      const h = Math.max(1, x.bottom - x.top);
      const ov = Math.max(0, Math.min(x.bottom, y + 900) - Math.max(x.top, y));
      if (ov > 0) { const f = +((Math.min(1, ov / h)) * x.c).toFixed(1); w += f; contributions.push([x.el, f, x.top, x.txt]); }
    }
    w = Math.round(w);
    if (w > maxWords) { maxWords = w; at = y; rows.push({ y, w, top: contributions.filter((r) => r[2] >= y && r[2] <= y + 900).slice(0, 40), aboveTop: contributions.filter((r) => r[2] < y).slice(0, 10), belowBot: contributions.filter((r) => r[2] > y + 900).slice(0, 10) }); }
  }
  return { H, maxWords, maxAt: at, trace: rows.slice(-6) };
});
console.log(JSON.stringify(out, null, 1));
console.log(); // eslint-disable-line
await browser.close();
