// Renderiza abertura.html quadro a quadro (Playwright + Chromium) e envia ao ffmpeg.
// Uso: node render.js [saida.mp4]            -> vídeo 5 s, 60 fps
//      node render.js prefixo --stills 0.5,2,4.8  -> PNGs desses instantes
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const FPS = 60, DUR = 5.0, W = 1080, H = 1920;
const ROOT = __dirname;
const TYPES = { '.html': 'text/html', '.png': 'image/png', '.ttf': 'font/ttf', '.js': 'text/javascript', '.json': 'application/json' };

function serve() {
  const srv = http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) {
      res.writeHead(404); res.end(); return;
    }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  });
  return new Promise(r => srv.listen(0, '127.0.0.1', () => r(srv)));
}

(async () => {
  const out = process.argv[2] || 'build/video_sem_audio.mp4';
  const si = process.argv.indexOf('--stills');
  const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;

  const srv = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto(`http://127.0.0.1:${srv.address().port}/abertura.html`);
  await page.evaluate(() => window.ready);

  const grab = async t => {
    const b64 = await page.evaluate(tt => {
      render(tt);
      return document.getElementById('c').toDataURL('image/png').split(',')[1];
    }, t);
    return Buffer.from(b64, 'base64');
  };

  if (stills) {
    for (const t of stills) fs.writeFileSync(`${out}_${t.toFixed(2)}.png`, await grab(t));
  } else {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS),
      '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
      '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(FPS * DUR);
    for (let i = 0; i < N; i++) {
      const buf = await grab(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${N}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
  srv.close();
})();
