// Render review stills.  usage: node stills.mjs <slug> <t1,t2,...> <outdir>   (half resolution, ~1 s per still)
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "fs"; import path from "path";
import { findBrowser } from "./browser.mjs";
const [, , slug, times, out] = process.argv;
const browserExecutable = findBrowser(), chromiumOptions = { gl: "swangle" };
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: `reel-${slug}`, inputProps: { slug }, browserExecutable, chromiumOptions });
for (const s of times.split(",").map(Number)) {
  await renderStill({ composition, serveUrl, inputProps: { slug }, output: `${out}/${s.toFixed(2)}.jpg`, frame: Math.min(composition.durationInFrames - 1, Math.round(s * 30)),
    imageFormat: "jpeg", jpegQuality: 80, scale: 0.5, browserExecutable, chromiumOptions });
}
console.log("stills ->", out);
