// Probe: why does the gate-79 walk stop at y400? Replicate its loop and dump per-element verdicts.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';

const roots = [process.cwd(), 'C:/Users/Acer/.agents/skills/hallmark/scripts'];
try { roots.push(path.dirname(execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim())); } catch {}
let puppeteer = null;
outer: for (const root of roots) {
  for (const name of ['puppeteer-core', 'puppeteer']) {
    try {
      const req = createRequire(path.join(root, 'noop.js'));
      const resolved = req.resolve(name);
      puppeteer = (await import(pathToFileURL(resolved).href)).default;
      if (puppeteer) break outer;
    } catch {}
  }
}
console.log('puppeteer?', !!puppeteer);
const CHROMES = ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'];
let chrome = [process.env.CHROME_PATH, ...CHROMES].find((p) => p && fs.existsSync(p)) || null;
console.log('chrome:', chrome);
const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
const url = pathToFileURL(path.resolve('docs/index.html')).href;
await page.goto(url, { waitUntil: 'networkidle0' });
await new Promise((r) => setTimeout(r, 800));
const out = await page.evaluate(() => {
  const vis = (el) => { const s = getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false; const r = el.getBoundingClientRect(); return r.width > 1 && r.height > 1; };
  const abs = (el) => { const r = el.getBoundingClientRect(); return { top: r.top + scrollY, bottom: r.bottom + scrollY, left: r.left, right: r.right, w: r.width, h: r.height }; };
  const hero = document.querySelector('section.hero');
  const hb = abs(hero);
  const rows = [];
  let cTop = Infinity, cBottom = -Infinity;
  for (const c of hero.querySelectorAll('*')) {
    const nv = c.closest('nav');
    if (!vis(c) || (nv && abs(nv).top <= hb.top + 220) || c === hero) { rows.push([c.tagName + '.' + (c.className.baseVal ?? c.className), 'SKIP-vis/nav', abs(c).bottom.toFixed(0)]); continue; }
    const cs = getComputedStyle(c);
    const painted = ((c.innerText || '').trim()) || /^(SVG|IMG|CANVAS|VIDEO|PICTURE)$/.test(c.tagName) || cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.backgroundImage !== 'none' || parseFloat(cs.borderTopWidth) > 0;
    const b = abs(c);
    if (!painted || /fixed|sticky/.test(cs.position)) { rows.push([c.tagName + '.' + (c.className.baseVal ?? c.className), 'skip-painted/pos', `top=${b.top.toFixed(0)} bottom=${b.bottom.toFixed(0)} painted=${!!painted} text="${(c.innerText || '').slice(0, 24)}"`]); continue; }
    cTop = Math.min(cTop, b.top); cBottom = Math.max(cBottom, Math.min(b.bottom, hb.bottom));
    rows.push([c.tagName + '.' + (c.className.baseVal ?? c.className), 'COUNT', `top=${b.top.toFixed(0)} bottom=${b.bottom.toFixed(0)} (clamped ${Math.min(b.bottom, hb.bottom).toFixed(0)}) text="${(c.innerText || '').slice(0, 24).replace(/\n/g, ' ')}"`]);
  }
  return { heroTop: hb.top, heroBottom: hb.bottom, heroH: hb.h, vh: innerHeight, svhTest: CSS.supports('min-height', 'calc(100svh - 56px)'), cTop: cTop === Infinity ? null : cTop.toFixed(0), cBottom: cBottom === -Infinity ? null : cBottom.toFixed(0), rows: rows.slice(-30) };
});
console.log(JSON.stringify(out, null, 1));
await browser.close();
