"""Finish a long-form video: YouTube chapters, description (sources + image credits), subtitles (.srt), a review copy.

usage: python pipeline/long_finalize.py <story>
reads   build/resolved.json, build/timeline.json, build/video.mp4, story.json (youtube.titles, facts, src/sources.json)
writes  out/<slug>.mp4 (the master, moov at the front), out/<slug>_review_720p.mp4, out/captions.srt,
        out/description.txt, out/chapters.txt, out/titles.txt
"""
import json, os, re, subprocess, sys
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

# ---------- subtitles: phrase-sized cues from the aligned words (<= 42 characters a line, <= 2 lines, 1-6 s)
cues = []
for l in tl["lines"]:
    cur = []
    for w in l["words"]:
        txt = " ".join(x["w"] for x in cur + [w]).replace("*", "")
        if cur and (len(txt) > 84 or w["s"] - cur[0]["s"] > 6): cues.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.?!…]$|\.\.\.$", w["w"]) and len(" ".join(x["w"] for x in cur)) > 18: cues.append(cur); cur = []
    if cur: cues.append(cur)


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
desc = f"""{yt.get('description_lead', '')}

Chapters
{chapters}

Sources
""" + "\n".join(f"- {u}" for u in sources) + """

Images (Wikimedia Commons)
""" + "\n".join(f"- {c}" for c in credits_cc) + ("\n- Paintings and prints by Francisco de Goya and others: public domain (Museo del Prado, Minneapolis Institute of Art, The Met)." if credits_pd else "") + f"""

Narration: synthetic voice. Music and sound: original, made for this channel.
{' '.join(yt.get('hashtags', []))}
"""
open(f"{out}/description.txt", "w").write(desc)
open(f"{out}/titles.txt", "w").write("\n".join(yt.get("titles", [])) + "\n")

# ---------- master + review copy
video = f"{sdir}/build/video.mp4"
if os.path.exists(video):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-c", "copy", "-movflags", "+faststart", f"{out}/{slug}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{out}/{slug}_review_720p.mp4"], check=True)
    print("master ->", f"{out}/{slug}.mp4")
else:
    print("(no build/video.mp4 yet: render first)")
print(f"chapters: {len(ch)} · subtitles: {len(lines)} cues · description: {len(desc)} characters")
print(chapters)
