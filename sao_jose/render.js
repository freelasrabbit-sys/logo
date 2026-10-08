// Renderiza logo.html quadro a quadro (tempo determinístico) e envia ao ffmpeg.
// Uso: node render.js saida.mp4            -> vídeo 10 s, 1080x1920, 60 fps (sem áudio)
//      node render.js --stills dir t1 t2.. -> PNGs nos tempos dados (prévia)
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const FPS = 60, DUR = 10, W = 1080, H = 1920;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "logo.html"));
  await page.waitForFunction(() => window.ready === true);
  const stage = await page.$("#stage");

  if (process.argv[2] === "--stills") {
    const dir = process.argv[3];
    fs.mkdirSync(dir, { recursive: true });
    for (const t of process.argv.slice(4).map(Number)) {
      await page.evaluate((t) => window.renderAt(t), t);
      await stage.screenshot({ path: path.join(dir, `t${t.toFixed(2)}.png`) });
    }
  } else {
    const out = process.argv[2] || "build/video_sem_audio.mp4";
    const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
      "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
      { stdio: ["pipe", "inherit", "inherit"] });
    const n = FPS * DUR;
    for (let i = 0; i < n; i++) {
      await page.evaluate((t) => window.renderAt(t), i / FPS);
      const buf = await stage.screenshot({ type: "png" });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
      if (i % 60 === 0) process.stdout.write(`frame ${i}/${n}\n`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on("close", r));
  }
  await browser.close();
})();
