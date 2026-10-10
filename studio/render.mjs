// node render.mjs --project=sample_opt1 --range=35.4:40.4 [--fps=30] [--workers=3]   -> out/<project>/NNNNN.jpg
// node render.mjs --project=sample_opt1 --stills=36,38.8
import puppeteer from 'puppeteer-core';
import fs from 'fs';
const arg = k => (process.argv.find(a => a.startsWith(`--${k}=`)) || '').split('=')[1];
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const proj = arg('project');
const URL0 = `http://localhost:8766/index.html?project=${proj}`;
const launch = () => puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'], defaultViewport: { width: 1920, height: 1080 } });
async function page(b) { const p = await b.newPage(); p.on('console', m => { if (m.type() === 'error' || m.type()==='warn') console.log('PAGE', m.text()); }); p.on('pageerror', e => console.log('PAGEERR', e.message)); await p.goto(URL0, { waitUntil: 'networkidle0', timeout: 120000 }); await p.waitForFunction('window.ready === true', { timeout: 120000 }); return p; }
const save = (f, d) => fs.writeFileSync(f, Buffer.from(d.split(',')[1], 'base64'));
const out = `out/${proj}`; fs.mkdirSync(out, { recursive: true });
const b = await launch();
if (arg('stills')) {
  const p = await page(b);
  for (const t of arg('stills').split(',').map(Number)) save(`${out}/still_${t.toFixed(2)}.png`, await p.evaluate(t => window.renderFrame(t, 'image/png'), t));
} else {
  const [a, z] = arg('range').split(':').map(Number); const FPS = +(arg('fps') || 30), N = +(arg('workers') || 3);
  const todo = []; for (let f = Math.round(a * FPS); f < Math.round(z * FPS); f++) if (!fs.existsSync(`${out}/${String(f).padStart(5, '0')}.jpg`)) todo.push(f);
  console.log('frames', todo.length); const t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: N }, async (_, w) => { const p = await page(b);
    for (let i = w; i < todo.length; i += N) { const f = todo[i]; save(`${out}/${String(f).padStart(5, '0')}.jpg`, await p.evaluate(t => window.renderFrame(t, 'image/jpeg', 0.93), f / FPS));
      if (++done % 30 === 0) console.log(done, '/', todo.length, ((Date.now() - t0) / done).toFixed(0), 'ms/frame'); } }));
  console.log('done', ((Date.now() - t0) / 1000).toFixed(0), 's');
}
await b.close();
