// Probe 375 c: dump every token of every row as (text, left, right), plus the crop edges.
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
await new Promise((r) => setTimeout(r, 1500));
const out = await page.evaluate(() => {
  const pre = document.querySelector('.hero .session pre');
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
  const rows = [...pre.querySelectorAll('.ln')];
  const dump = [];
  rows.forEach((row, i) => {
    const text = row.textContent;
    const pos = caret(row);
    const marks = [];
    let s = 0;
    const runs = [];
    const flush = (e) => { if (e > s) runs.push([s, e]); };
    for (let k = 0; k < text.length; k++) if (text[k] === ' ') { flush(k); s = k + 1; }
    flush(text.length);
    for (const [a, b] of runs) {
      range.setStart(pos[a][0], pos[a][1]);
      range.setEnd(pos[b][0], pos[b][1]);
      const r = range.getBoundingClientRect();
      const piece = text.slice(a, b);
      marks.push(piece + '@' + (r.left - origin).toFixed(1) + '..' + (r.right - origin).toFixed(1));
    }
    dump.push('row' + i + ': ' + marks.join(' | '));
  });
  return { scrollLeft: pre.scrollLeft, clientWidth: pre.clientWidth, scrollWidth: pre.scrollWidth, dump };
});
console.log(out.dump.join('\n'));
console.log('scrollLeft', out.scrollLeft, 'window', out.scrollLeft, '..', out.scrollLeft + out.clientWidth, 'scrollWidth', out.scrollWidth);
await browser.close();
