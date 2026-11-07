"""Check a finished long-form video before it goes to Gigi.

usage: python pipeline/long_qa.py <story> [video]      (default: build/video.mp4)
checks  - streams: 1920x1080, 24 fps, yuv420p H.264 + AAC, moov atom first, picture and sound as long as the story
        - every build/stills/<t>.jpg (rendered straight from the composition) matches the video's frame at t,
          so a bad chunk or a broken join shows up as a mismatch
        - the sound lines up with build/mix.wav (no offset), and its loudness / true peak
        - black stretches longer than 0.4 s (listed, not always an error: fades are meant to go dark)
writes  out/qa/contact.jpg: frames just after each chapter card and on both sides of every chunk seam
"""
import glob, json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from scipy import signal
from PIL import Image, ImageDraw, ImageFont
from paths import story_dir

sdir = story_dir(sys.argv[1]); video = sys.argv[2] if len(sys.argv) > 2 else f"{sdir}/build/video.mp4"
rs = json.load(open(f"{sdir}/build/resolved.json")); FPS = 24; D = rs["duration"]
qa = f"{sdir}/out/qa"; os.makedirs(qa, exist_ok=True); tmp = tempfile.mkdtemp()
problems = []


def run(args): return subprocess.run(args, capture_output=True, text=True)


# ---------- streams
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video]).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
fps = eval(v["r_frame_rate"]); vd = float(v.get("duration", 0)); ad = float(a.get("duration", 0)) if a else 0
print(f"video {v['codec_name']} {v['width']}x{v['height']} {fps:g} fps {v['pix_fmt']} {vd:.2f} s, {v.get('nb_frames')} frames, "
      f"{int(v.get('bit_rate', 0)) / 1e6:.1f} Mb/s · audio {a and a['codec_name']} {a and a['sample_rate']} Hz {a and a['channels']} ch {ad:.2f} s · "
      f"file {int(pr['format']['size']) / 1e6:.0f} MB")
print(f"colour: range {v.get('color_range')}, matrix {v.get('color_space')}, primaries {v.get('color_primaries')}, transfer {v.get('color_transfer')}")
if (v["codec_name"], v["width"], v["height"], round(fps, 3), v["pix_fmt"]) != ("h264", 1920, 1080, 24.0, "yuv420p"): problems.append("video stream is not 1080p24 yuv420p H.264")
if (v.get("color_range"), v.get("color_space"), v.get("color_primaries"), v.get("color_transfer")) != ("tv", "bt709", "bt709", "bt709"):
    problems.append("colour is not tagged limited-range BT.709")
if not a or a["codec_name"] != "aac": problems.append("no AAC audio")
if abs(vd - D) > 0.1 or abs(ad - D) > 0.1: problems.append(f"length: video {vd:.2f} s, audio {ad:.2f} s, story {D:.2f} s")
with open(video, "rb") as f:   # top-level boxes: moov must come before mdat (YouTube starts processing sooner)
    order = []
    while len(order) < 8:
        h = f.read(8)
        if len(h) < 8: break
        size, kind = int.from_bytes(h[:4], "big"), h[4:].decode("latin-1"); order.append(kind)
        if size == 1: size = int.from_bytes(f.read(8), "big") - 8
        f.seek(size - 8, 1)
if "moov" not in order or "mdat" in order and order.index("moov") > order.index("mdat"): problems.append(f"moov atom not first ({order})")

# ---------- frames vs. the stills rendered straight from the composition
stills = sorted(glob.glob(f"{sdir}/build/stills/*.jpg"), key=lambda p: float(os.path.basename(p)[:-4]))
want = {round(float(os.path.basename(p)[:-4]) * FPS): p for p in stills}
cuts = sorted(int(m.group(1)) for m in (re.search(r"part-\d+-(\d+)-\d+\.mp4$", p) for p in glob.glob(f"{sdir}/build/chunks/part-*.mp4")) if m)
seams = [f for c in cuts if c > 0 for f in (c - 1, c)]
chap = [round((o["t0"] + 1.6) * FPS) for o in rs["overlays"] if o["type"] == "chapter"]
frames = sorted(set(want) | set(seams) | set(chap))
sel = "+".join(f"eq(n\\,{n})" for n in frames)
run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"select='{sel}',scale=480:270,format=rgb24", "-fps_mode", "passthrough", f"{tmp}/f%04d.png"])
got = sorted(glob.glob(f"{tmp}/f*.png"))
if len(got) != len(frames): problems.append(f"extracted {len(got)} frames, wanted {len(frames)}")
grab = dict(zip(frames, got)); scores = []
for n, p in want.items():
    if n not in grab: continue
    x = np.asarray(Image.open(grab[n]).convert("RGB"), np.float32); y = np.asarray(Image.open(p).convert("RGB").resize((480, 270), Image.BILINEAR), np.float32)
    mse = float(((x - y) ** 2).mean()); psnr = 99 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
    scores.append((psnr, n / FPS, float(x.mean() - y.mean())))
scores.sort()
med = scores[len(scores) // 2][0]
print(f"frames vs stills: {len(scores)} compared, worst {scores[0][0]:.1f} dB at {scores[0][1]:.2f} s, median {med:.1f} dB, "
      f"largest brightness shift {max(abs(d) for *_, d in scores):.1f}/255")
for s, t, d in scores:   # a stale still also shows up here: re-run preview_stills.py, then look again
    if s < min(24, med - 9) or abs(d) > 4: problems.append(f"frame at {t:.2f} s differs from its still ({s:.1f} dB, brightness {d:+.1f})")

# ---------- sound: offset against the mix, loudness
if a: run(["ffmpeg", "-v", "error", "-y", "-i", video, "-map", "0:a", "-ac", "1", "-ar", "44100", f"{tmp}/a.wav"])
if not a: print("(no sound to check)")
else:
    x, sr = sf.read(f"{tmp}/a.wav", dtype="float32"); m, _ = sf.read(f"{sdir}/build/mix.wav", dtype="float32"); m = m[:, 0] if m.ndim > 1 else m
    lags = []
    for t in (D * 0.1, D * 0.5, D * 0.9):
        i = int(t * sr); w = m[i:i + sr * 4]; seg = x[i - sr // 2:i + sr * 4 + sr // 2]
        c = signal.correlate(seg, w, mode="valid", method="fft"); lags.append((int(np.argmax(c)) - sr // 2) / sr * 1000)
    print("sound offset vs mix (ms):", [round(l, 1) for l in lags])
    if max(abs(l) for l in lags) > 10: problems.append(f"sound is offset from the mix by {lags} ms")
    meter = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summ = meter[meter.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)); TP = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    print(f"loudness {I:.1f} LUFS, true peak {TP:.1f} dBTP")
    if TP > -0.5: problems.append(f"true peak {TP:.1f} dBTP")

# ---------- black stretches
bd = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vf", "scale=320:-2,blackdetect=d=0.4:pix_th=0.06", "-an", "-f", "null", "-"]).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
print("black stretches:", ", ".join(f"{float(s):.1f}-{float(e):.1f}" for s, e in blacks) or "none")

# ---------- contact sheet: chapter starts + chunk seams
show = [n for n in sorted(set(chap) | set(seams)) if n in grab]
cols = 4; rows = (len(show) + cols - 1) // cols; sheet = Image.new("RGB", (cols * 480, rows * 300), "#111")
dr = ImageDraw.Draw(sheet); font = ImageFont.load_default()
for k, n in enumerate(show):
    im = Image.open(grab[n]); x0, y0 = (k % cols) * 480, (k // cols) * 300; sheet.paste(im, (x0, y0))
    tag = ("seam " if n in seams else "chapter ") + f"{n / FPS:.2f} s (frame {n})"
    dr.text((x0 + 8, y0 + 276), tag, fill="#ddd", font=font)
sheet.save(f"{qa}/contact.jpg", quality=88)
print("contact sheet ->", f"{qa}/contact.jpg")
print("PROBLEMS:\n- " + "\n- ".join(problems) if problems else "ALL GOOD")
