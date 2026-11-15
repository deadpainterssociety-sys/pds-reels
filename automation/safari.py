"""Breakout safari: art-history Shorts that broke out for other channels lately, studied to keep polishing our formulas.

Gigi, 15 Nov 2026: VVSA (viewed vs swiped away) and AVD (average view duration) are the two numbers to polish, and the
channel rotates at least 3 formulas so it never looks like one template. Every Thursday before the lab brief (lab.yml), and
on demand (safari.yml), this finds Shorts in our niche that beat their own channel's median by a wide margin and builds a
dossier for each one; Claude studies the dossiers (LAB.md, "Breakout safari") and proposes formula changes or new formulas.

usage: python automation/safari.py collect <out_dir> [--max 8] [--days 60]   breakouts (Data API, ~1,300 units) + dossiers
       python automation/safari.py dossier <out_dir> <video_id> [...]         dossiers for given Shorts only
       python automation/safari.py save <out_dir>                             -> private release: safari-<date>.tar + seen list

A dossier (<out>/dossiers/<id>/): meta.json (numbers, title, channel median, ratio, cuts per minute, words per minute,
first spoken words and when), sheet.jpg (one frame every 1-3 s, timestamped), opening.jpg (the first 3 s at 4 frames per
second: the moment a viewer decides to stay or swipe), transcript.txt (auto-captions with times).
Media are downloaded at 360p for analysis only and deleted once the frames and transcript exist; nothing of another
creator's video is ever reused. Dossiers live only in the private data release, never in this public repo; the notebook of patterns is SAFARI.md.
"""
import datetime, glob, json, math, os, re, shutil, statistics, subprocess, sys, tarfile, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

QUERIES = [  # Shorts (< 4 min) about paintings; YouTube search ordered by views within the window
    ("painting", "en"), ("this painting", "en"), ("art history", "en"), ("famous painting", "en"),
    ("painting hidden detail", "en"), ("dark history painting", "en"), ("painting story museum", "en"),
    ("the story behind this painting", "en"), ("este cuadro", "es"), ("pintura historia", "es"),
]
MIN_VIEWS, MIN_RATIO = 100_000, 5.0
NOTES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SAFARI.md")
# art HISTORY storytelling, not painting tutorials, crafts, spray-paint shows or paint ads (the first run, 15 Nov 2026,
# found 261 "painting" breakouts and only ~30 were stories about art or history)
HIST = re.compile(r"(?i)histor|museum|museo|painter|masterpiece|famous painting|this painting|behind|secret|hidden|mystery|story|"
                  r"cuadro|pintor|historia|van gogh|da vinci|leonardo|caravaggio|goya|bosch|rembrandt|vermeer|monet|picasso|"
                  r"dal[ií]|klimt|michelangelo|raphael|botticelli|bruegel|vel[aá]zquez|munch|frida|mona lisa|louvre|prado|"
                  r"renaissance|baroque|medieval|victorian|queen|king|portrait of|cursed|banned|stolen|experiment")
NOT_HIST = re.compile(r"(?i)how to draw|drawing tutorial|step by step|diy|craft|spray|calligraph|satisfying|asian paints|truck|"
                      r"nail|for kids|easy art|one stroke|chalk|rangoli|hack|clay|challenge|navratri|diwali|durga|kaaba|allah|"
                      r"muhammad|cricket|speed paint|timelapse|art supplies|tutorial|beginner")


def _ffprobe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return None


def channel_shorts(cid):
    """a channel's latest ~50 Shorts with their numbers (UUSH = the channel's Shorts playlist)"""
    import yt_research as R
    ids, _ = R.playlist("UUSH" + cid[2:], 1)
    return [v for v in R.videos(ids[:50]) if v["dur"] <= 180]


def find(out, days=60):
    import youtube as Y, yt_research as R
    R.H["Authorization"] = f"Bearer {Y.token()}"; R.UNITS["cap"] = 2500
    after = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    hits = R.discover([{"q": q, "lang": lang, "after": after, "duration": "short", "tag": "discover"} for q, lang in QUERIES])
    hits = [h for h in hits if h.get("views") and h.get("dur", 999) <= 180]
    score = {}
    for h in hits:
        if R.ART.search(h.get("title", "") + " " + " ".join(h.get("tags", [])) + " " + (h.get("ctitle") or "")):
            score[h["channel"]] = score.get(h["channel"], 0) + h["views"]
    chans = {}
    for cid in [c for c, _ in sorted(score.items(), key=lambda x: -x[1])][:45]:
        try:
            info = R.channel_info(R.api("channels", part="snippet,statistics,contentDetails,brandingSettings,topicDetails", id=cid).get("items", []))
            if not info: continue
            sh = channel_shorts(cid)
            med = statistics.median([v["views"] for v in sh]) if len(sh) >= 8 else None
            chans[cid] = {**{k: info[0][k] for k in ("id", "title", "handle", "subs", "videos", "country")}, "median_short_views": med,
                          "n_shorts_sampled": len(sh)}
            for v in sh:   # this channel's own breakouts too, not only the ones search surfaced
                if not any(h["id"] == v["id"] for h in hits): hits.append({**v, "q": "channel", "tag": "channel"})
        except R.Budget: break
        except Exception as e: print("channel", cid, str(e)[:150])
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days + 30)).isoformat()
    found = {}
    for h in hits:
        c = chans.get(h["channel"])
        if not c or h.get("published", "") < cutoff or h["views"] < MIN_VIEWS: continue
        text = h.get("title", "") + " " + " ".join(h.get("tags", [])) + " " + c["title"]
        if not R.ART.search(text) or not HIST.search(text) or NOT_HIST.search(text): continue
        ratio = round(h["views"] / c["median_short_views"], 1) if c["median_short_views"] else None
        if (ratio is not None and ratio < MIN_RATIO) or (ratio is None and h["views"] < 1_000_000): continue
        found[h["id"]] = {"id": h["id"], "url": f"https://www.youtube.com/shorts/{h['id']}", "title": h["title"],
                          "channel": c["title"], "handle": c["handle"], "subs": c["subs"], "channel_median": c["median_short_views"],
                          "ratio": ratio, "views": h["views"], "likes": h.get("likes"), "comments": h.get("comments"),
                          "published": h["published"][:10], "dur_s": h["dur"], "lang": h.get("lang"), "query": h.get("q"),
                          "desc_head": h.get("desc_head", "")[:200],
                          "score": round(min(ratio or 10, 60) * math.log10(h["views"]), 1)}
    ranked = sorted(found.values(), key=lambda b: -b["score"])
    os.makedirs(out, exist_ok=True)
    json.dump({"made": datetime.date.today().isoformat(), "window_days": days, "units": R.UNITS["spent"],
               "channels": sorted(chans.values(), key=lambda c: -(c["subs"] or 0)), "breakouts": ranked},
              open(os.path.join(out, "safari.json"), "w"), indent=1, ensure_ascii=False)
    print(f"safari: {len(ranked)} breakouts from {len(chans)} channels ({R.UNITS['spent']} units)")
    return ranked


def _download(vid, d):
    """360p video + auto-captions; YouTube often asks datacenter machines to sign in, so try several player clients"""
    for pc in ("default", "tv", "web_safari", "mweb", "ios", "android_vr"):
        r = subprocess.run(["yt-dlp", "-q", "--no-warnings", "--no-playlist", "--extractor-args", f"youtube:player_client={pc}",
                            "-f", "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480]/b", "--write-auto-subs", "--write-subs",
                            "--sub-langs", "en.*,es.*", "--sub-format", "vtt", "-o", os.path.join(d, "%(id)s.%(ext)s"),
                            f"https://www.youtube.com/shorts/{vid}"], capture_output=True, text=True)
        mp4 = [p for p in glob.glob(os.path.join(d, vid + ".*")) if p.endswith((".mp4", ".mkv", ".webm"))]
        if mp4: return mp4[0], pc
    return None, (r.stderr or "")[-300:]


def _vtt(path):
    """auto-caption VTT -> [(seconds, text)] without the rolling duplicates"""
    out, last = [], ""
    t = None
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"(\d+):(\d+):(\d+)\.(\d+) -->", line)
        if m: t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000; continue
        txt = re.sub(r"<[^>]+>", "", line).strip()
        if t is None or not txt or txt == last or "-->" in txt or txt.startswith(("WEBVTT", "Kind:", "Language:")): continue
        out.append((round(t, 2), txt)); last = txt
    return out


def _transcript_api(vid):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        t = YouTubeTranscriptApi().fetch(vid, languages=["en", "es"])
        return [(round(s.start, 2), s.text) for s in t]
    except Exception as e:
        print("  transcript api:", str(e)[:120]); return []


def _sheet(frames, cols, out, label_every=True):
    from PIL import Image, ImageDraw, ImageFont
    ims = [(t, Image.open(p).convert("RGB")) for t, p in frames]
    if not ims: return
    w, h = ims[0][1].size; s = 240 / w; tw, th = 240, int(h * s)
    rows = math.ceil(len(ims) / cols); sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (16, 16, 16))
    try: font = ImageFont.load_default(size=14)
    except TypeError: font = ImageFont.load_default()
    for i, (t, im) in enumerate(ims):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(im.resize((tw, th)), (x, y + 18))
        ImageDraw.Draw(sheet).text((x + 4, y + 2), f"{t:.2f}s", fill=(255, 220, 0), font=font)
    sheet.save(out, quality=82)


def dossier(out, b):
    vid = b["id"]; d = os.path.join(out, "dossiers", vid); os.makedirs(d, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        media, how = _download(vid, tmp)
        meta = dict(b, got_video=bool(media), download=how)
        lines = []
        subs = sorted(glob.glob(os.path.join(tmp, vid + "*.vtt")), key=lambda p: (".en" not in p, p))
        if subs: lines = _vtt(subs[0]); meta["captions"] = os.path.basename(subs[0]).split(".", 1)[1]
        if not lines: lines = _transcript_api(vid); meta["captions"] = "transcript api" if lines else None
        if media:
            dur = _ffprobe_dur(media) or b.get("dur_s") or 60; meta["dur_s"] = round(dur, 2)
            step = 1 if dur <= 50 else 2 if dur <= 100 else 3
            fr = os.path.join(tmp, "f"); os.makedirs(fr)
            subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-vf", f"fps=1/{step},scale=320:-2", os.path.join(fr, "%04d.jpg")], check=True)
            _sheet([(i * step, p) for i, p in enumerate(sorted(glob.glob(os.path.join(fr, "*.jpg"))))], 8, os.path.join(d, "sheet.jpg"))
            op = os.path.join(tmp, "o"); os.makedirs(op)
            subprocess.run(["ffmpeg", "-v", "error", "-t", "3", "-i", media, "-vf", "fps=4,scale=320:-2", os.path.join(op, "%03d.jpg")], check=True)
            _sheet([(i * 0.25, p) for i, p in enumerate(sorted(glob.glob(os.path.join(op, "*.jpg"))))], 6, os.path.join(d, "opening.jpg"))
            sc = subprocess.run(["ffmpeg", "-v", "info", "-i", media, "-vf", "select='gt(scene,0.32)',showinfo", "-an", "-f", "null", "-"],
                                capture_output=True, text=True).stderr
            cuts = [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", sc)]
            shots = [b2 - a for a, b2 in zip([0] + cuts, cuts + [dur])]
            meta.update(cuts=cuts, cuts_per_min=round(len(cuts) / dur * 60, 1), median_shot_s=round(statistics.median(shots), 2) if shots else None,
                        first_cut_s=cuts[0] if cuts else None)
            w = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", media],
                               capture_output=True, text=True).stdout.strip()
            meta["frame"] = w
        if lines:
            words = sum(len(t.split()) for _, t in lines); span = max(1.0, (lines[-1][0] - lines[0][0]) + 2)
            meta.update(words=words, wpm=round(words / span * 60), first_words_at_s=lines[0][0], first_line=lines[0][1],
                        opening_words=" ".join(t for s, t in lines if s < 3.5)[:200])
            open(os.path.join(d, "transcript.txt"), "w").write("\n".join(f"[{s:6.2f}] {t}" for s, t in lines))
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1, ensure_ascii=False)
        print(f"  {vid}: video {'yes (' + str(how) + ')' if media else 'no'}, transcript {len(lines)} lines, "
              f"{meta.get('cuts_per_min', '?')} cuts/min, {meta.get('wpm', '?')} wpm")
        return meta
    finally:
        shutil.rmtree(tmp, ignore_errors=True)   # the downloaded media never leaves this machine


def collect(out, n=8, days=60):
    import release
    try: seen = set(json.loads(release.data_get("safari-seen.json") or "[]"))
    except Exception: seen = set()
    os.makedirs(out, exist_ok=True)   # the running notebook (SAFARI.md, LAB.md "Breakout safari"), carried week to week
    if os.path.exists(NOTES): shutil.copy(NOTES, os.path.join(out, "notes.md"))
    ranked = find(out, days)
    picks = [b for b in ranked if b["id"] not in seen][:n]
    for b in picks:
        try: dossier(out, b)
        except Exception as e: print("  dossier", b["id"], "failed:", str(e)[:200])
    json.dump(sorted(seen | {b["id"] for b in picks}), open(os.path.join(out, "seen.json"), "w"))


def save(out):
    import release
    day = datetime.date.today().isoformat(); tarp = os.path.join(tempfile.mkdtemp(), "safari.tar")
    with tarfile.open(tarp, "w") as t: t.add(out, arcname=f"safari-{day}")
    release.data_put(f"safari-{day}.tar", open(tarp, "rb").read(), "application/x-tar")
    if os.path.exists(os.path.join(out, "seen.json")):
        release.data_put("safari-seen.json", open(os.path.join(out, "seen.json"), "rb").read())
    if os.path.exists(os.path.join(out, "notes.md")):   # Claude's running notebook -> SAFARI.md (lab.yml commits it)
        shutil.copy(os.path.join(out, "notes.md"), NOTES)
    print("saved", f"safari-{day}.tar")


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, dflt: type(dflt)(a[a.index(k) + 1]) if k in a else dflt
    if len(a) >= 2 and a[0] == "collect": collect(a[1], opt("--max", 8), opt("--days", 60))
    elif len(a) >= 3 and a[0] == "dossier":
        for v in a[2:]: dossier(a[1], {"id": v})
    elif len(a) >= 2 and a[0] == "save": save(a[1])
    else: raise SystemExit(__doc__)
