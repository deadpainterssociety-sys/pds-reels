// Render a long-form (16:9) story in resumable chunks, then join them and lay the final mix under the picture.
// usage: node render_long.mjs <slug> <out.mp4> [chunks=6]
// Chunks are rendered muted into ../stories/<slug>/build/chunks/ (a finished chunk is never redone, so a killed run
// simply resumes), joined without re-encoding, and muxed with build/mix.wav as AAC 320k.
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { execFileSync } from "child_process";
import fs from "fs"; import path from "path";
import { findBrowser } from "./browser.mjs";
import { compId } from "./comp.mjs";
const [, , slug, out, nArg] = process.argv;
const browserExecutable = findBrowser(), chromiumOptions = { gl: "swangle" };
const sdir = path.resolve("../stories", slug), cdir = path.join(sdir, "build", "chunks");
fs.mkdirSync(cdir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const id = compId(slug);
const composition = await selectComposition({ serveUrl, id, inputProps: { slug }, browserExecutable, chromiumOptions });
const N = Number(nArg || 6), total = composition.durationInFrames, per = Math.ceil(total / N);
const parts = [];
for (let i = 0; i < N; i++) {
  const a = i * per, b = Math.min(total - 1, (i + 1) * per - 1); if (a > b) break;
  const f = path.join(cdir, `part-${String(i).padStart(2, "0")}-${a}-${b}.mp4`); parts.push(f);
  if (fs.existsSync(f) && fs.statSync(f).size > 1000) { console.log(`chunk ${i + 1}/${N} already done`); continue; }
  const t0 = Date.now(); let last = -1; const tmp = f + ".part.mp4";
  await renderMedia({ composition, serveUrl, codec: "h264", outputLocation: tmp, inputProps: { slug }, browserExecutable, chromiumOptions,
    frameRange: [a, b], muted: true, concurrency: Number(process.env.CONCURRENCY || 2), crf: Number(process.env.CRF || 19), x264Preset: "veryfast",
    pixelFormat: "yuv420p", logLevel: "error",
    onProgress: ({ progress }) => { const p = Math.floor(progress * 10) * 10; if (p !== last) { last = p; console.log(`chunk ${i + 1}/${N} ${p}% ${((Date.now() - t0) / 1000).toFixed(0)}s`); } } });
  fs.renameSync(tmp, f);
  console.log(`chunk ${i + 1}/${N} done in ${((Date.now() - t0) / 1000).toFixed(0)}s (frames ${a}-${b})`);
}
const list = path.join(cdir, "list.txt"); fs.writeFileSync(list, parts.map((p) => `file '${p}'`).join("\n") + "\n");
const joined = path.join(cdir, "joined.mp4");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", joined]);
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", joined, "-i", path.join(sdir, "build", "mix.wav"), "-map", "0:v", "-map", "1:a",
  "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", out]);
console.log(`${id}: ${parts.length} chunks joined -> ${out}`);
