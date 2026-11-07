// Render one story reel.  usage: node render_reel.mjs <slug> <out.mp4> [startFrame-endFrame]
// Headless Linux has no GPU: WebGL (the 2.5D depth shader) only works with chromiumOptions.gl = "swangle".
// Browser: see browser.mjs (BROWSER_EXECUTABLE, else Playwright headless shell, else Remotion download).
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "path";
import { findBrowser } from "./browser.mjs";
import { compId } from "./comp.mjs";
const [, , slug, out, range] = process.argv;
const browserExecutable = findBrowser();
const chromiumOptions = { gl: "swangle" };
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const id = compId(slug);
const composition = await selectComposition({ serveUrl, id, inputProps: { slug }, browserExecutable, chromiumOptions });
const frameRange = range ? range.split("-").map(Number) : null;
const t0 = Date.now(); let last = -1;
await renderMedia({ composition, serveUrl, codec: "h264", outputLocation: out, inputProps: { slug }, browserExecutable, chromiumOptions,
  frameRange, concurrency: Number(process.env.CONCURRENCY || 2), crf: Number(process.env.CRF || 18), x264Preset: "veryfast", audioBitrate: "192k", pixelFormat: "yuv420p", logLevel: "error",
  onProgress: ({ progress }) => { const p = Math.floor(progress * 10) * 10; if (p !== last) { last = p; console.log(`${id} ${p}% ${((Date.now() - t0) / 1000).toFixed(0)}s`); } } });
console.log(`${id} done in ${((Date.now() - t0) / 1000).toFixed(0)}s -> ${out}`);
