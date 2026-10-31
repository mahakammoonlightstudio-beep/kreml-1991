// Probe 2: page drive exactly like the plugin (reduced motion, 375 -> 1280 -> 1440),
// then run the REAL observeSpace source in-page and report its gate-79 internals.
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
      puppeteer = (await import(pathToFileURL(req.resolve(name)).href)).default;
      if (puppeteer) break outer;
    } catch {}
  }
}
const chrome = [process.env.CHROME_PATH, 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'].find((p) => p && fs.existsSync(p));
const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage();

const src = fs.readFileSync('C:/Users/Acer/.agents/skills/hallmark/scripts/sloplint-render.mjs', 'utf8');
const s = src.indexOf('function observeSpace');
let depth = 0, eIdx = s;
for (let i = src.indexOf('{', s); i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') { depth--; if (depth === 0) { eIdx = i + 1; break; } }
}
const observeSpaceSrc = src.slice(s, eIdx);
const debugSrc = observeSpaceSrc.replace(
  'return out;',
  `out.push({ gate: 'DBG', grade: 'DEBUG', evidence: JSON.stringify({ vh: innerHeight, heroBottom: hero ? abs(hero).bottom : null, heroTop: hero ? abs(hero).top : null, secs: secs.length, after: (function(){ const hb2 = abs(hero); const a = secs.find((x) => x !== hero && !hero.contains(x) && abs(x).top >= hb2.bottom - 4); return a ? abs(a).top : null; })(), heroPosture: heroPosture, heroOnly: heroOnly }) }); return out;`
);
if (debugSrc === observeSpaceSrc) console.log('WARN: debug injection missed (no bare `return out;`)');

await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]).catch(() => {});
const url = pathToFileURL(path.resolve('docs/index.html')).href;
await page.goto(url, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; }).catch(() => {});
const frames = () => page.evaluate(async () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))).catch(() => {});

for (const width of [375, 1280]) {
  await page.setViewport({ width, height: width === 375 ? 812 : 800 });
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  await frames();
  console.log(`drove ${width}`);
}
for (const [w, h] of [[1440, 900], [1920, 1080]]) {
  await page.setViewport({ width: w, height: h });
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  await frames();
  const evalFn = (fnSrc) => page.evaluate(new Function(`return (${fnSrc})`)(), true, true, '', false, '').catch((er) => [{ gate: 'THROW', grade: 'DEBUG', evidence: String(er).slice(0, 300) }]);
  const res = await evalFn(observeSpaceSrc);
  console.log(`observeSpace(w=${w}) REAL ->`);
  for (const f of res) console.log(`   ${f.gate} ${f.grade} | ${f.evidence.slice(0, 110)} ${f.gate === 'DBG' ? f.evidence : ''}`);
  if (w === 1440) {
    const res2 = await evalFn(debugSrc);
    console.log('observeSpace DEBUG ->');
    for (const f of res2) console.log(`   ${f.gate} ${f.grade} | ${f.evidence.slice(0, 220)}`);
  }
}
await browser.close();
