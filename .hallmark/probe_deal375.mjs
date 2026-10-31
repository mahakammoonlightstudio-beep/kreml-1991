// Probe the two deal tables at 375 to find which cell forces the 6px spill.
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
await page.setViewport({ width: 375, height: 812 });
await page.goto(pathToFileURL(path.resolve('docs/index.html')).href, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(() => (document.fonts ? document.fonts.ready : Promise.resolve()));
await new Promise((r) => setTimeout(r, 1200));
const out = await page.evaluate(() => {
  const res = [];
  document.querySelectorAll('.deal table').forEach((tb, i) => {
    const r = tb.getBoundingClientRect();
    const deal = tb.closest('.deal');
    const dr = deal.getBoundingClientRect();
    const cs = getComputedStyle(tb);
    // per-column widths
    const cols = [...tb.rows[0].cells].map((c) => {
      const cr = c.getBoundingClientRect();
      return Math.round(cr.width);
    });
    // min content: measure the widest row by scrolling? use table.scrollWidth
    res.push({
      i, width: Math.round(r.width), right: Math.round(r.right),
      dealRight: Math.round(dr.right), dealWidth: Math.round(dr.width),
      scrollW: tb.scrollWidth,
      cols, maxWidth: cs.maxWidth, tableLayout: cs.tableLayout,
      fs: getComputedStyle(tb).fontSize,
    });
  });
  // also any cell wider than its table?
  const wideCells = [];
  document.querySelectorAll('.deal td, .deal th').forEach((c, k) => {
    const r = c.getBoundingClientRect();
    if (r.right > 381) wideCells.push({ k, text: c.textContent.slice(0, 30), right: Math.round(r.right) });
  });
  return { res, wideCells, inner: window.innerWidth };
});
console.log(JSON.stringify(out, null, 1));
await browser.close();
