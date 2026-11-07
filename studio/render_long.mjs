// Render a long-form (16:9) story in resumable chunks, then join them and lay the final mix under the picture.
// usage: node render_long.mjs <slug> <out.mp4> [chunks=6]
// Chunks are rendered muted into ../stories/<slug>/build/chunks/ (a finished chunk is never redone, so a killed run
// simply resumes), joined without re-encoding, and muxed with build/mix.wav as AAC 320k (trimmed to -14 LUFS / -1 dBTP).
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { execFileSync, spawnSync } from "child_process";
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
// YouTube plays every video at about -14 LUFS and only ever turns loud ones down. The reel mix sits near -11 LUFS with
// inter-sample peaks above 0 dBTP, so trim it (never boost) to -14 LUFS / -1 dBTP: it sounds the same in the player and
// YouTube's encoder never meets an over. A plain gain change, nothing else in the sound is touched.
const mix = path.join(sdir, "build", "mix.wav");
const meter = spawnSync("ffmpeg", ["-hide_banner", "-nostats", "-i", mix, "-af", "ebur128=peak=true", "-f", "null", "-"], { encoding: "utf8" }).stderr || "";
const summary = meter.slice(meter.lastIndexOf("Summary:"));
const I = Number((summary.match(/I:\s+(-?[\d.]+) LUFS/) || [])[1]), TP = Number((summary.match(/Peak:\s+(-?[\d.]+) dBFS/) || [])[1]);
const gain = Number.isFinite(I) && Number.isFinite(TP) ? Math.min(0, -14 - I, -1 - TP) : 0;
console.log(`mix ${I} LUFS, true peak ${TP} dBTP -> gain ${gain.toFixed(1)} dB`);
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", joined, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
  ...(gain < -0.05 ? ["-af", `volume=${gain.toFixed(2)}dB`] : []), "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", out]);
fs.rmSync(joined, { force: true });   // the chunks stay (a fix re-renders only its chunk); the silent join is not needed again
console.log(`${id}: ${parts.length} chunks joined -> ${out}`);
