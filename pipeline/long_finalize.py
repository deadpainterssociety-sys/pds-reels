"""Finish a long-form video: YouTube chapters, description (sources + image credits), subtitles (.srt), a review copy.

usage: python pipeline/long_finalize.py <story>
reads   build/resolved.json, build/timeline.json, build/video.mp4, story.json (youtube.titles, facts, src/sources.json)
writes  out/<slug>.mp4 (the master, moov at the front), out/<slug>_review_720p.mp4, out/<slug>_upload_1080p.mp4 (only when
        the master is over 380 MB: chat attachments stop at 400 MiB), out/captions.srt,
        out/description.txt, out/chapters.txt, out/titles.txt
"""
import glob, json, os, re, shutil, subprocess, sys
from paths import story_dir

sdir = story_dir(sys.argv[1]); st = json.load(open(f"{sdir}/story.json")); slug = st["slug"]
rs = json.load(open(f"{sdir}/build/resolved.json")); tl = json.load(open(f"{sdir}/build/timeline.json"))
out = f"{sdir}/out"; os.makedirs(out, exist_ok=True)


def mmss(t):
    t = int(t); return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


# ---------- chapters (from the chapter cards; YouTube needs 0:00 first, 3+ chapters, each 10 s+)
ch = [(0.0, st.get("youtube", {}).get("intro_chapter", "Nobody was supposed to see these"))]
for o in sorted(rs["overlays"], key=lambda o: o["t0"]):
    if o["type"] == "chapter":
        num = (o.get("kicker") or "").replace("CHAPTER", "").strip()
        ch.append((max(0.0, o["t0"]), f"{num}. {re.sub('<[^>]+>', '', o['text'])}" if num else re.sub("<[^>]+>", "", o["text"])))
ending = [l for l in tl["lines"] if l["id"].startswith("end")]
if ending: ch.append((ending[0]["s"] - 0.3, st.get("youtube", {}).get("outro_chapter", "The Dog")))
chapters = "\n".join(f"{mmss(t)} {name}" for t, name in ch)
for (a, _), (b, n) in zip(ch, ch[1:]):
    if b - a < 10: print(f"!! chapter '{n}' starts less than 10 s after the previous one")
open(f"{out}/chapters.txt", "w").write(chapters + "\n")

# ---------- subtitles: one cue per spoken phrase (from story.json), short phrases merged, long ones split in two
perf = {l["id"]: [ph[0] for ph in l["perf"]] for l in st["lines"]}
cues = []
for l in tl["lines"]:
    words = l["words"]; k = 0; groups = []
    for ph in perf.get(l["id"], []):
        n = len(ph.replace("...", "…").split()); groups.append(words[k:k + n]); k += n
    if k < len(words): groups.append(words[k:])
    merged = []
    for g in groups:
        if not g: continue
        if merged and len(" ".join(x["w"] for x in merged[-1] + g)) <= 84 and g[-1]["e"] - merged[-1][0]["s"] <= 6.5 \
                and not re.search(r"[.?!…]$|\.\.\.$", merged[-1][-1]["w"]):
            merged[-1] = merged[-1] + g
        else: merged.append(g)
    for g in merged:
        if len(" ".join(x["w"] for x in g)) > 84:   # split at the word boundary nearest the middle
            best = min(range(1, len(g)), key=lambda i: abs(len(" ".join(x["w"] for x in g[:i])) - len(" ".join(x["w"] for x in g[i:]))))
            cues += [g[:best], g[best:]]
        else: cues.append(g)


def srt_t(t):
    ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def wrap(s):
    if len(s) <= 42: return s
    words = s.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:]); d = abs(len(a) - len(b))
        if best is None or d < best[0]: best = (d, a + "\n" + b)
    return best[1]


lines = []
for i, c in enumerate(cues):
    s = c[0]["s"]; e = max(c[-1]["e"], s + 1.0)
    if i + 1 < len(cues): e = min(e + 0.25, cues[i + 1][0]["s"] - 0.02)
    text = " ".join(w["w"] for w in c).replace("*", "").replace("...", "…")
    lines.append(f"{i + 1}\n{srt_t(s)} --> {srt_t(e)}\n{wrap(text)}\n")
open(f"{out}/captions.srt", "w").write("\n".join(lines))

# ---------- description
yt = st.get("youtube", {})
src = json.load(open(f"{sdir}/src/sources.json")) if os.path.exists(f"{sdir}/src/sources.json") else {}
used = set()
for s in rs["shots"]:
    used |= {x for x in [s.get("img"), s.get("img2")] + list(s.get("imgs") or []) if x}
    for k in ("back", "left", "right", "front"): used |= set((s.get("room") or {}).get(k) or [])
credits_pd, credits_cc = [], []
custom = yt.get("credits")
for k in sorted(used):
    m = src.get(k)
    if not m: continue
    title = re.sub(r"^File:|\.(jpg|jpeg|png)$", "", m["title"], flags=re.I)
    artist = re.sub("<[^>]+>", "", m.get("artist") or "").strip().split("\n")[0][:80]
    lic = m.get("license") or "?"
    line = f"{title} — {artist} — {lic}"
    (credits_pd if re.search(r"public domain|cc0|pd", lic, re.I) else credits_cc).append(line)
sources = []
for f in st.get("facts", []):
    for u in re.split(r"\s*;\s*", f["source"]):
        if u and u not in sources: sources.append(u)
_cv = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"))).get("voice_clone") or {}
narration = "AI voice cloned from a real recording (Chatterbox)" if _cv.get("enabled") else "synthetic voice"
_tracks = (st.get("music") or {}).get("tracks") or []
_mc = list(dict.fromkeys(t["credit"] for t in _tracks if t.get("credit")))
music_block = (f"Narration: {narration}.\n\nMusic (Wikimedia Commons)\n" + "\n".join(f"- {c}" for c in _mc)) if _mc else \
              f"Narration: {narration}. Music and sound: original, made for this channel."
desc = f"""{yt.get('description_lead', '')}

Chapters
{chapters}

Sources
""" + "\n".join(f"- {u}" for u in sources) + """

Images (Wikimedia Commons)
""" + "\n".join(f"- {c}" for c in (custom or credits_cc + ([f"Paintings, prints and photographs by {st.get('meta', {}).get('painter', 'the artist')} "
                                                                  "and others: public domain."] if credits_pd else []))) + f"""

{music_block}
{' '.join(yt.get('hashtags', []))}
"""
open(f"{out}/description.txt", "w").write(desc)
open(f"{out}/titles.txt", "w").write("\n".join(yt.get("titles", [])) + "\n")

# ---------- master + review copy
video = f"{sdir}/build/video.mp4"
if os.path.exists(video):
    master = f"{out}/{slug}.mp4"   # render_long.mjs already wrote the moov atom first: a hard link costs no disk space
    if os.path.exists(master): os.remove(master)
    try: os.link(video, master)
    except OSError: shutil.copy(video, master)
    fresh = lambda p: os.path.exists(p) and os.path.getmtime(p) > os.path.getmtime(video)   # made from this render already
    review = f"{out}/{slug}_review_720p.mp4"
    if not fresh(review):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                        "-maxrate", "2200k", "-bufsize", "4400k", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", review], check=True)
    print("master ->", master, f"({os.path.getsize(master) / 1e6:.0f} MB)")
    # Files sent in the chat must stay under 400 MiB. A bigger master also gets a 1080p upload copy sized to ~370 MB
    # (two-pass x264 'slow', sound copied; YouTube re-encodes everything anyway, so the difference is hard to see).
    upload = f"{out}/{slug}_upload_1080p.mp4"
    if os.path.getsize(master) > 380e6 and not fresh(upload):
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", master],
                                   capture_output=True, text=True).stdout)
        vk = int((370e6 * 8 / dur - 330e3) / 1000)   # kb/s for the picture, leaving room for the 320k sound
        log = os.path.join(sdir, "build", "x264pass")
        common = ["-map", "0:v", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-pix_fmt", "yuv420p", "-passlogfile", log,
                  "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", master, *common, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", master, *common, "-pass", "2", "-maxrate", f"{int(vk * 1.6)}k",
                        "-bufsize", f"{vk * 2}k", "-map", "0:a", "-c:a", "copy", "-movflags", "+faststart", upload], check=True)
        for f in glob.glob(log + "*"): os.remove(f)
    if os.path.exists(upload): print("upload copy ->", upload, f"({os.path.getsize(upload) / 1e6:.0f} MB)")
else:
    print("(no build/video.mp4 yet: render first)")
print(f"chapters: {len(ch)} · subtitles: {len(lines)} cues · description: {len(desc)} characters")
print(chapters)
