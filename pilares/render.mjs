// Renderiza pilares/index.html em PNGs: um por selo (fundo transparente) + uma prancha por opção.
// Uso: NODE_PATH=$(npm root -g) node pilares/render.mjs
import { createRequire } from "module";
import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const dir = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(dir, "png");
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1800, height: 1200 }, deviceScaleFactor: 2 });
await page.goto("file://" + path.join(dir, "index.html"));
await page.evaluate(() => document.fonts.ready);

await page.addStyleTag({ content: "body,section{background:transparent!important}" });
for (const el of await page.$$(".selo")) {
  const nome = await el.getAttribute("data-nome");
  await el.$eval("svg", (s) => (s.style.width = "600px"));
  await (await el.$("svg")).screenshot({ path: path.join(outDir, `${nome}.png`), omitBackground: true });
  await el.$eval("svg", (s) => (s.style.width = ""));
}
await page.addStyleTag({ content: "body,section{background:#F7F7F7!important}" });
for (const sec of await page.$$("section")) {
  const op = await sec.getAttribute("data-opcao");
  await sec.screenshot({ path: path.join(outDir, `prancha_opcao-${op}.png`) });
}
await browser.close();
console.log("png ok");
