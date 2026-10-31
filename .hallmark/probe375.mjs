// Probe 375: drive the real page, report what fit() itself decided and what is visible.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';

let puppeteer = null;
const roots = [process.cwd(), 'C:/Users/Acer/.agents/skills/hallmark/scripts'];
try { roots.push(execSync('npm root -g', { encoding: 'utf8' }).trim()); } catch {}
for (const root of roots) {
  for (const name of ['puppeteer-core', 'puppeteer']) {
    try {
      const req = createRequire(path.join(root, 'noop.js'));
      puppeteer = (await import(pathToFileURL(req.resolve(name)).href)).default;
      break;
    } catch {}
  }
  if (puppeteer) break;
}
const chrome = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(String(e && e.message || e).split('\n')[0]));
page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await page.setViewport({ width: 375, height: 812 });
const url = pathToFileURL(path.resolve('docs/index.html')).href;
await page.goto(url, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(() => (document.fonts ? document.fonts.ready : Promise.resolve()));
await new Promise((r) => setTimeout(r, 1200));
const out = await page.evaluate(() => {
  const pre = document.querySelector('.hero .session pre');
  const cs = getComputedStyle(pre);
  const rows = [...pre.querySelectorAll('.ln')].map((el) => el.textContent);
  const cols = Math.max(...rows.map((l) => l.length));
  // measure u the same way fit() does
  const probeEl = document.createElement('span');
  probeEl.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;';
  probeEl.textContent = '\u2588'.repeat(cols);
  pre.appendChild(probeEl);
  const w = probeEl.getBoundingClientRect().width;
  probeEl.remove();
  const u = w / cols;
  const lo = pre.scrollLeft, hi = pre.scrollLeft + pre.clientWidth;
  const lines = rows.map((l) => {
    const a = Math.max(0, Math.floor(lo / u)), b = Math.min(l.length, Math.ceil(hi / u));
    return { vis: l.slice(a, b), a, b };
  });
  return {
    fontLoaded: [...document.fonts].some((f) => f.family.includes('Martian') || f.family.toLowerCase().includes('martian')),
    fontFamily: cs.fontFamily, fontSize: cs.fontSize,
    clientWidth: pre.clientWidth, scrollWidth: pre.scrollWidth, scrollLeft: pre.scrollLeft,
    marginRight: getComputedStyle(pre).marginRight,
    u, cols, visLo: lo / u, visHi: hi / u,
    lines: lines.map((x) => x.a + '..' + x.b + ' ' + JSON.stringify(x.vis)),
    overflowX: cs.overflowX, errors: window.__err || null,
  };
});
console.log(JSON.stringify(out, null, 1));
console.log('pageerrors:', JSON.stringify(errors));
await browser.close();
