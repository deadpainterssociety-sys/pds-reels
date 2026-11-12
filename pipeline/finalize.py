"""Package a rendered reel for posting, and QA it.

usage: python pipeline/finalize.py <story> [--captions-only]
needs  build/video.mp4 (render) and out/cover.jpg (cover.py)
writes out/<slug>.mp4           cover as the first frame (0.1 s) + the reel: ONE file for Instagram, TikTok and YouTube
       out/<slug>-preview.mp4   540p copy (small enough for a Telegram bot: bots can only send files <= 50 MB)
       out/caption.txt          Instagram / TikTok / YouTube texts with credits
       out/qa.txt, out/frames.jpg   loudness, what a listener hears (recogniser on the FINAL file), frame sheet, rights, facts
The master is re-encoded until it is under 95 MB (third-party Instagram API guides cite 100 MB for Reels).
"""
import json, os, re, subprocess, sys, difflib, datetime
import numpy as np, soundfile as sf
import pyloudnorm as pyln
from PIL import Image, ImageDraw
from paths import story_dir
from asr import transcribe

sdir = story_dir(sys.argv[1]); st = json.load(open(os.path.join(sdir, "story.json"))); slug = st["slug"]
out = os.path.join(sdir, "out"); os.makedirs(out, exist_ok=True)
vid, cover, final = os.path.join(sdir, "build", "video.mp4"), os.path.join(out, "cover.jpg"), os.path.join(out, f"{slug}.mp4")
run = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True)
ONLY_CAPTIONS = "--captions-only" in sys.argv

if not ONLY_CAPTIONS:
    for crf in (21, 23, 25):
        run("ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-t", "0.1", "-i", cover, "-i", vid, "-filter_complex",
            "[0:v]scale=1080:1920,format=yuv420p,setsar=1,fps=30[c];[1:v]setsar=1,fps=30[v];[c][v]concat=n=2:v=1:a=0[vo];"
            "[1:a]adelay=100|100,apad=pad_dur=0[ao]",
            "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-maxrate", "10.5M", "-bufsize", "21M", "-pix_fmt", "yuv420p",  # cap ~80 MB/min
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final)
        if os.path.getsize(final) < 95 * 1024 * 1024: break
    run("ffmpeg", "-y", "-i", final, "-vf", "scale=540:960", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", os.path.join(out, f"{slug}-preview.mp4"))

# ---- captions ----
m = {**st["meta"], **(st.get("meta_es") or {})}   # the Spanish edition shows the Spanish names
if m.get("museum"):   # Dead Painters Society format
    credits = [f"📍 {m['museum']}, {m['city']}", f"🎨 {m['painter']}, {m['painting']}, {m['year']}"]
else:
    credits = [x for x in [f"📍 {m['place']}" if m.get("place") else "", m.get("credit_line", "")] if x]
for k, im in st["images"].items():
    if im.get("credit"): credits.append("📷 " + im["credit"])
if st.get("ai_voice", True): credits.append(st.get("ai_voice_line") or "🎙️ AI voice narration")
tags = " ".join(st.get("hashtags", []))   # YouTube: the full list
# Instagram and TikTok accept 5 hashtags at most (2 Nov 2026): each gets its own best five
tags_ig = " ".join((st.get("hashtags_instagram") or st.get("hashtags", []))[:5])
tags_tt = " ".join((st.get("hashtags_tiktok") or st.get("hashtags", []))[:5])
yt_title = st.get("youtube_title") or re.sub(r"<[^>]+>", "", st["cover"]["question"])
cred = "\n".join(credits)
urls = []   # accuracy is the brand (PLAYBOOK §2): YouTube descriptions list the sources (links are clickable there only)
for f in st.get("facts", []):
    for u in re.findall(r"https?://[^\s;,)\]]+", f.get("source", "")):
        if u.rstrip(".") not in urls: urls.append(u.rstrip("."))
srcs = ("\n\nSources:\n" + "\n".join(urls[:8])) if urls else ""
txt = (f"=== INSTAGRAM (Reel) ===\n{st['caption']}\n\n{cred}\n\n{tags_ig}\n\n"
       f"=== TIKTOK ===\n{st.get('caption_short') or st['caption'].splitlines()[0]}\n{tags_tt}\n\n"
       f"=== YOUTUBE SHORTS ===\nTitle: {yt_title[:90]}{"" if st.get("lang", "en").startswith("es") else " #shorts"}\nDescription:\n{st['caption']}{srcs}\n\n{cred}\n\n{tags}\n")
open(os.path.join(out, "caption.txt"), "w").write(txt)
if ONLY_CAPTIONS: print(txt); sys.exit(0)

# ---- QA ----
run("ffmpeg", "-y", "-i", final, "-ac", "1", "-ar", "16000", os.path.join(sdir, "build", "final16k.wav"))
a, sr = sf.read(os.path.join(sdir, "build", "final16k.wav"), dtype="float32")
mix, msr = sf.read(os.path.join(sdir, "build", "mix.wav"), dtype="float32")
lufs = pyln.Meter(msr).integrated_loudness(mix)
tl = json.load(open(os.path.join(sdir, "build", "timeline.json")))
norm = lambda s: re.sub(r"[^\w ]", "", s.lower().replace("-", " "))
lines, scores = [], []
for l in tl["lines"]:   # +0.1 s: the cover frame shifts everything
    heard, _ = transcribe(a[int((l["s"] + 0.05) * sr): int((l["e"] + 0.2) * sr)], sr)
    r = difflib.SequenceMatcher(a=norm(l["text"]).split(), b=norm(heard).split()).ratio(); scores.append(r)
    lines.append(f"{l['id']:10s} {r:4.2f}  {heard}")
dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", final).stdout)
rights = dict(st.get("rights", {})); rights.setdefault("creator_died", m.get("died")) if m.get("died") else None
if "creator_died" in rights:
    yrs = datetime.date.today().year - rights["creator_died"]
    rights_line = f"creator died {rights['creator_died']} -> {yrs} years ({'OK: public domain (>70)' if yrs > 70 else 'NOT OK: still in copyright'})"
else:
    rights_line = f"rights: {rights.get('note', 'NOT DOCUMENTED — fill story.rights before posting')}"
qa = [f"{slug}: {dur:.1f} s · {os.path.getsize(final) / 1e6:.0f} MB · loudness {lufs:.1f} LUFS (stereo; mono-normalised -14)",
      rights_line, f"recogniser match on the final file: {np.mean(scores):.2f} (min {min(scores):.2f}; digits vs words score lower)",
      *lines, "", "facts:", *[f"- {f['claim']}  [{f['source']}]" for f in st.get("facts", [])]]
open(os.path.join(out, "qa.txt"), "w").write("\n".join(qa) + "\n"); print("\n".join(qa[:3 + len(lines)]))

fdir = os.path.join(sdir, "build", "frames"); os.makedirs(fdir, exist_ok=True)
times = np.linspace(0.05, dur - 0.5, 24)
sheet = Image.new("RGB", (12 * 216, 2 * 404), (16, 16, 16)); d = ImageDraw.Draw(sheet)
for i, tt in enumerate(times):
    fp = os.path.join(fdir, f"{i:02d}.jpg")
    run("ffmpeg", "-y", "-ss", f"{tt:.2f}", "-i", final, "-frames:v", "1", "-vf", "scale=216:384", fp)
    x, y = (i % 12) * 216, (i // 12) * 404
    sheet.paste(Image.open(fp), (x, y + 20)); d.text((x + 4, y + 4), f"{tt:.1f}s", fill=(255, 220, 0))
sheet.save(os.path.join(out, "frames.jpg"), quality=85)
print("final ->", final)
