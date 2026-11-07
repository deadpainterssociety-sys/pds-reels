// Render a long-form (16:9) story in resumable chunks, then join them and lay the final mix under the picture.
// usage: node render_long.mjs <slug> <out.mp4> [chunks=6]
//        PATCH=3247-3553,11324-11434 node render_long.mjs …   after a small fix (e.g. an overlay's text): re-render only
//        those frames (composition frame numbers, inclusive) and lay them over the old chunks in the final encode.
// Chunks are rendered muted into ../stories/<slug>/build/chunks/ (a finished chunk is never redone, so a killed run
// simply resumes), joined, converted to standard colour and muxed with build/mix.wav as AAC 320k (trimmed to -14 LUFS / -1 dBTP).
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
const N = Number(nArg || 6), total = composition.durationInFrames, per = Math.ceil(total / N), fps = composition.fps;
const opts = { composition, serveUrl, codec: "h264", inputProps: { slug }, browserExecutable, chromiumOptions, muted: true,
  concurrency: Number(process.env.CONCURRENCY || 2), crf: Number(process.env.CRF || 19), x264Preset: "veryfast", pixelFormat: "yuv420p", logLevel: "error" };
async function render(file, a, b, tag) {
  const t0 = Date.now(); let last = -1; const tmp = file + ".part.mp4";
  await renderMedia({ ...opts, outputLocation: tmp, frameRange: [a, b],
    onProgress: ({ progress }) => { const p = Math.floor(progress * 10) * 10; if (p !== last) { last = p; console.log(`${tag} ${p}% ${((Date.now() - t0) / 1000).toFixed(0)}s`); } } });
  fs.renameSync(tmp, file);
  console.log(`${tag} done in ${((Date.now() - t0) / 1000).toFixed(0)}s (frames ${a}-${b})`);
}
const parts = [];
for (let i = 0; i < N; i++) {
  const a = i * per, b = Math.min(total - 1, (i + 1) * per - 1); if (a > b) break;
  const f = path.join(cdir, `part-${String(i).padStart(2, "0")}-${a}-${b}.mp4`); parts.push(f);
  if (fs.existsSync(f) && fs.statSync(f).size > 1000) { console.log(`chunk ${i + 1}/${N} already done`); continue; }
  await render(f, a, b, `chunk ${i + 1}/${N}`);
}
const patches = (process.env.PATCH || "").split(",").filter(Boolean).map((r) => r.split("-").map(Number));
const built = fs.statSync(path.join(sdir, "build", "resolved.json")).mtimeMs;
for (const [a, b] of patches) {
  if (!(a >= 0 && b >= a && b < total)) throw new Error(`bad PATCH range ${a}-${b} (the video has ${total} frames)`);
  const f = path.join(cdir, `patch-${a}-${b}.mp4`);   // a patch rendered after the last build_story is current: keep it
  if (fs.existsSync(f) && fs.statSync(f).mtimeMs > built) { console.log(`patch ${a}-${b} already done`); continue; }
  await render(f, a, b, `patch ${a}-${b}`);
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
// Remotion's chunks come out full-range BT.601 (its frames are JPEGs). YouTube and most players expect limited-range
// BT.709, so convert once here (exact colour math, one x264 "medium" pass of ~20 min for 10 minutes; the Shorts are
// brought to limited range by finalize.py's re-encode). Standard chunks without patches are copied untouched.
const probe = JSON.parse(spawnSync("ffprobe", ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_range,color_space",
  "-of", "json", joined], { encoding: "utf8" }).stdout || "{}");
const cs = (probe.streams || [])[0] || {}, full = cs.color_range === "pc";
const graph = []; let cur = "0:v";
// Each patch starts exactly on its frame; outside it the old picture passes through. overlay wants yuva420p for the
// patch: convert with the range stated, or swscale squeezes full-range values into limited range (washed-out blacks).
const rng = full ? "pc" : "tv";
patches.forEach(([a], i) => {
  graph.push(`[${i + 2}:v]setpts=PTS-STARTPTS+(${a}/${fps})/TB,scale=in_range=${rng}:out_range=${rng},format=yuva420p[p${i}]`,
    `[${cur}][p${i}]overlay=eof_action=pass:repeatlast=0[o${i}]`); cur = `o${i}`;
});
if (full) {
  graph.push(`[${cur}]colorspace=space=bt709:ispace=${cs.color_space === "bt709" ? "bt709" : "bt470bg"}:range=tv:irange=pc:primaries=bt709:iprimaries=bt709:trc=bt709:itrc=bt709:format=yuv420p[v]`);
  cur = "v";
}
const video = graph.length
  ? ["-filter_complex", graph.join(";"), "-map", `[${cur}]`, "-c:v", "libx264", "-preset", "medium", "-crf", String(process.env.CRF_FINAL || 19), "-pix_fmt", "yuv420p",
     ...(full ? ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"] : [])]
  : ["-map", "0:v", "-c:v", "copy"];
console.log(`video: ${patches.length} patch(es), ${full ? "full-range BT.601 -> limited BT.709" : "standard colour"}, ${graph.length ? "one x264 pass" : "copied"}`);
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", joined, "-i", mix, ...patches.flatMap(([a, b]) => ["-i", path.join(cdir, `patch-${a}-${b}.mp4`)]),
  ...video, "-map", "1:a", ...(gain < -0.05 ? ["-af", `volume=${gain.toFixed(2)}dB`] : []), "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", out]);
fs.rmSync(joined, { force: true });   // the chunks stay (a fix re-renders only its frames); the silent join is not needed again
console.log(`${id}: ${parts.length} chunks${patches.length ? ` + ${patches.length} patch(es)` : ""} joined -> ${out}`);
