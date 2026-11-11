"""Resolve a story's visual plan against its narration timeline and publish it to the Remotion studio.

usage: python pipeline/build_story.py <story>
reads   story.json (images, maps, shots, overlays, sfx, music, nocap) + build/timeline.json (aligned narration)
writes  build/resolved.json, studio/public/stories/<slug>/* (resized images, depth maps), studio/src/reel/stories.ts

ANCHORS (any time field): "line" = line start · "line$" = line end · "line.k" = start of word k (0-based) ·
  "line.k$" = end of word k · a number = seconds · append "+0.2" / "-0.05" to offset.
  Cuts land best ~0.03–0.08 s BEFORE the word they illustrate ("myth.8-0.05").
POSES: "full" | "full@1.05" | "<point>@<zoom>" | "x,y@zoom" | [x, y, z]. z = 1 fills the 9:16 frame (cover);
  z < 1 shows the whole image smaller (use with "frame": true); points are 0..1 image coordinates.
IMAGE "file": path relative to the story folder, or "tex:<name>" for a generated texture in studio/public/tex.
"""
import json, os, re, sys, glob, subprocess
from PIL import Image, ImageFilter
from paths import ROOT, PIPE, PUBLIC, STUDIO, STORIES, story_dir

sdir = story_dir(sys.argv[1])
st = json.load(open(os.path.join(sdir, "story.json")))
slug = st["slug"]
tl = json.load(open(os.path.join(sdir, "build", "timeline.json")))
L = {l["id"]: l for l in tl["lines"]}
pub = os.path.join(PUBLIC, "stories", slug); os.makedirs(pub, exist_ok=True)
MAIN = st["meta"]["image"]
LONG = st.get("format") == "long"   # 16:9 long-form: bigger images, no whoosh on every cut, no NEXT card, 16:9 maps


def T(a):
    if isinstance(a, (int, float)): return float(a)
    m = re.fullmatch(r"\s*([^+\-]+?)\s*(([+-])\s*([\d.]+))?\s*", str(a))
    if not m: raise SystemExit(f"bad anchor: {a}")
    base, off = m.group(1), (float(m.group(4)) * (1 if m.group(3) == "+" else -1) if m.group(2) else 0.0)
    if re.fullmatch(r"[\d.]+", base): return float(base) + off
    end = base.endswith("$"); base = base.rstrip("$")
    try:
        if "." in base:
            lid, k = base.split("."); w = L[lid]["words"][int(k)]
            return round((w["e"] if end else w["s"]) + off, 3)
        return round((L[base]["e"] if end else L[base]["s"]) + off, 3)
    except (KeyError, IndexError):
        raise SystemExit(f"anchor '{a}' does not exist in the timeline (line ids: {list(L)})")


# ---------- images ----------
images = {}
for name, spec in st["images"].items():
    f = spec["file"]
    src = os.path.join(PUBLIC, "tex", f[4:] + ".jpg") if f.startswith("tex:") else os.path.join(sdir, f)
    if (not os.path.exists(src) or os.path.getsize(src) < 1000) and spec.get("fallback_file"):
        print(f"!! {name}: using fallback {spec['fallback_file']}"); src = os.path.join(sdir, spec["fallback_file"])
    if not os.path.exists(src) or os.path.getsize(src) < 1000:
        if spec.get("optional"): print("skip missing optional image", name); continue
        raise SystemExit(f"missing image {name}: {src}  (run pipeline/fetch_images.py)")
    im = Image.open(src).convert("RGB")
    if spec.get("crop"):  # [left, top, right, bottom] fractions to trim (museum labels, inventory numbers, scan borders)
        l, t_, r, b = spec["crop"]
        im = im.crop((round(im.width * l), round(im.height * t_), round(im.width * (1 - r)), round(im.height * (1 - b))))
    s = spec.get("long", 3600 if LONG else 2600) / max(im.size)
    if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    elif spec.get("upscale", 1) > 1:  # small sources: modest upscale + unsharp so close-ups survive
        s = min(s, spec["upscale"]); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    out = os.path.join(pub, f"{name}.jpg"); im.save(out, quality=92)
    rec = {"src": f"stories/{slug}/{name}.jpg", "w": im.width, "h": im.height}
    if spec.get("depth"):
        dp = os.path.join(pub, f"{name}_depth.png")
        if not os.path.exists(dp) or os.path.getmtime(dp) < os.path.getmtime(src):
            subprocess.run([sys.executable, os.path.join(PIPE, "depth.py"), out, dp], check=True)
        rec["depth"] = f"stories/{slug}/{name}_depth.png"
    images[name] = rec
    print(f"image {name}: {im.width}x{im.height}{' +depth' if spec.get('depth') else ''}")


def pose(p, img):
    if isinstance(p, list): return [float(v) for v in p]
    m = re.fullmatch(r"([\w.,\-]+)(@([\d.]+))?", p)
    key, z = m.group(1), float(m.group(3) or 1)
    if key == "full": return [0.5, 0.5, z]
    if "," in key: x, y = key.split(","); return [float(x), float(y), z]
    pts = st["images"][img].get("points", {})
    if key not in pts: raise SystemExit(f"point '{key}' not defined for image '{img}'")
    return [pts[key][0], pts[key][1], z]


# ---------- maps (precomputed SVG paths) ----------
maps = {}
for mid, spec in st.get("maps", {}).items():
    sp, mp = os.path.join(sdir, "build", f"map_{mid}_spec.json"), os.path.join(sdir, "build", f"map_{mid}.json")
    json.dump({**spec, **({"size": [1920, 1080]} if LONG else {})}, open(sp, "w"))
    subprocess.run(["node", "tools/map.mjs", sp, mp], cwd=STUDIO, check=True, capture_output=True)
    maps[mid] = json.load(open(mp))

# ---------- shots ----------
shots, flashes, shakes, cuts = [], [], [], []
for s in st["shots"]:
    img = s.get("img", MAIN)
    if s.get("kind") == "map": img = img if img in images else MAIN
    if img not in images and s.get("fallback"): img = s["fallback"]
    o = {"t": T(s["at"]), "img": img, "from": pose(s.get("from", "full"), img), "to": pose(s.get("to", s.get("from", "full")), img)}
    for k in ("gray", "dim", "contrast", "dolly", "sway", "frame", "kind", "fade", "img2", "labels", "room", "imgs"):
        if k in s: o[k] = s[k]
    if s.get("kind") == "map":
        m = s["map"]
        o["map"] = {"id": m["id"], "pins": [{"city": p["city"], "t": T(p["at"]), **({"label": p["label"]} if "label" in p else {})} for p in m["pins"]]}
        if "route" in m: o["map"]["route"] = {"from": m["route"]["from"], "to": m["route"]["to"], "t0": T(m["route"]["at"]), "t1": T(m["route"]["to_at"]),
                                 **({"path": m["route"]["path"]} if m["route"].get("path") else {})}
    if s.get("kind") == "peel":
        o["peel"] = {"t0": T(s["peel"]["at"]), "t1": T(s["peel"]["to"]), "under": s["peel"]["under"]}
    if s.get("hit") == "big": flashes.append(o["t"]); shakes.append(o["t"])
    shots.append(o); cuts.append((o["t"], s.get("hit"), s.get("whoosh", not LONG)))
shots.sort(key=lambda x: x["t"])
for a, b in zip(shots, shots[1:]):
    if b["t"] - a["t"] < 0.35: print(f"!! very short shot at {a['t']:.2f}s ({b['t'] - a['t']:.2f}s) — intended?")

# ---------- overlays ----------
overlays = []
for ov in st.get("overlays", []):
    o = {k: v for k, v in ov.items() if k not in ("from", "to", "at")}
    o["t0"] = T(ov.get("from", ov.get("at")))
    o["t1"] = T(ov["to"]) if "to" in ov else o["t0"] + 2.5
    if "shade" in ov: o["shade"] = T(ov["shade"])   # cut overlay: when the removed strips get tinted
    if isinstance(ov.get("point"), str):
        pt = st["images"][ov.get("img", MAIN)]["points"][ov["point"]]; o["point"] = {"x": pt[0], "y": pt[1]}
    overlays.append(o)


def next_teaser():
    """Text for the silent NEXT card: the `teaser` of the next story on the schedule (PLAYBOOK §1, 1 Nov).
    story.json "next": "<text>" overrides it; "next": false switches the card off (manual builds outside the schedule)."""
    if "next" in st: return (st["next"] or "").strip() or None
    try: sch = sorted(json.load(open(os.path.join(ROOT, "schedule.json"))), key=lambda e: e["date"])
    except (OSError, ValueError): return None
    idx = [i for i, e in enumerate(sch) if e["slug"] == slug]
    if not idx: return None
    for e in sch[idx[0] + 1:]:                     # the next reel in posting order (two a day: the evening one is "next")
        try: status = json.load(open(os.path.join(STORIES, e["slug"], "state.json"))).get("status", "draft")
        except (OSError, ValueError): status = "draft"
        if status in ("rejected", "skipped", "posted"): continue
        try: return (json.load(open(os.path.join(STORIES, e["slug"], "story.json"))).get("teaser") or "").strip() or None
        except (OSError, ValueError): return None   # the next story isn't written yet: no card (never tease the wrong day)
    return None


teaser = None if LONG else next_teaser()
if teaser:
    t0 = round(tl["lines"][-1]["e"] + 0.6, 3)   # after the last caption has gone
    if tl["duration"] - t0 < 1.2: print(f"!! the NEXT card gets only {tl['duration'] - t0:.1f} s: set \"tail\": 2.2 and re-run from step 1")
    overlays.append({"type": "next", "kicker": "NEXT", "text": teaser, "t0": t0, "t1": tl["duration"] + 1})
    print(f"NEXT card: {teaser}")
else:
    print("NEXT card: none (no teaser for the next scheduled story)")
for f in st.get("flashes", []): flashes.append(T(f))
nocap = [[T(a), T(b)] for a, b in st.get("nocap", [])]
words = [{"line": l["id"], "words": [{"w": w["w"], "s": w["s"], "e": w["e"], **({"em": 1} if w.get("em") else {})} for w in l["words"]]}
         for l in tl["lines"]]
sfx = [{"t": T(x["at"]), "fx": x["fx"], "gain": x.get("gain", 0.5)} for x in st.get("sfx", [])]
music = dict(st.get("music", {}))
if "sections" in music: music["sections"] = {k: [T(a), T(b)] for k, (a, b) in music["sections"].items()}
if "heartbeat" in music: music["heartbeat"] = [T(music["heartbeat"][0]), T(music["heartbeat"][1])]
if "segments" in music: music["segments"] = [{**g, "t": T(g["at"])} for g in music["segments"]]

resolved = {"slug": slug, "format": st.get("format", "reel"), "duration": tl["duration"], "audio": f"stories/{slug}/audio.wav", "images": images, "shots": shots,
            "overlays": overlays, "flashes": sorted(flashes), "shakes": sorted(shakes), "words": words, "nocap": nocap, "maps": maps,
            "style": st.get("style", {}), "cuts": cuts, "sfx": sfx, "music": music}
json.dump(resolved, open(os.path.join(sdir, "build", "resolved.json"), "w"), ensure_ascii=False)

# ---------- publish every built story to the studio (one composition per story: reel-<slug>) ----------
allst = {}
for rj in sorted(glob.glob(os.path.join(STORIES, "*", "build", "resolved.json"))):
    d = json.load(open(rj))
    for k in ("cuts", "sfx", "music"): d.pop(k, None)
    allst[d["slug"]] = d
open(os.path.join(STUDIO, "src", "reel", "stories.ts"), "w").write(
    "// generated by pipeline/build_story.py — do not edit\nexport const STORIES: Record<string, any> = " + json.dumps(allst, ensure_ascii=False) + ";\n")
print(f"resolved {slug}: {len(shots)} shots, {len(overlays)} overlays, {tl['duration']:.1f} s")
