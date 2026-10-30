"""Download every image a story declares with a "commons" title (or a direct "url"), patiently.

usage: python pipeline/fetch_images.py <story> [--minutes 25]
story.json images: {"name": {"file": "src/name.jpg", "commons": "File:Exact title.jpg"}}  or  {"url": "https://..."}
Writes src/<file> and src/sources.json (licence + author for every file, needed for the caption credits).

Why patient: Wikimedia rate-limits busy shared IPs (cloud machines, CI runners) with HTTP 429 on originals.
Strategy: try the original every ~30 s; after 6 minutes accept the largest standard-width thumbnail that is
smaller than the original (3840/2560/1920/1280...). Already-downloaded files (>1 KB) are skipped.
"""
import json, os, sys, time
from paths import story_dir
import commons as C

sdir = story_dir(sys.argv[1])
limit = 60 * (float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else 25)
st = json.load(open(os.path.join(sdir, "story.json")))
srcf = os.path.join(sdir, "src", "sources.json"); os.makedirs(os.path.dirname(srcf), exist_ok=True)
sources = json.load(open(srcf)) if os.path.exists(srcf) else {}
jobs = {}
for name, im in st["images"].items():
    if not (im.get("commons") or im.get("url")): continue
    path = os.path.join(sdir, im["file"])
    if os.path.exists(path) and os.path.getsize(path) > 1000: continue
    jobs[name] = (im, path)
for name, im in st["images"].items():   # licence/author for every Commons image, downloaded or not (caption credits)
    if im.get("commons") and name not in sources:
        sources[name] = C.info(im["commons"]); time.sleep(1)
t0 = time.time()
while jobs and time.time() - t0 < limit:
    for name, (im, path) in list(jobs.items()):
        data, how = None, "original"
        try:
            url = im.get("url") or sources[name]["url"]
            data = C.fetch(url, tries=1)
        except Exception:
            data = None
        if data is None and im.get("commons") and time.time() - t0 > 360:
            for w in C.STD_WIDTHS:
                if w >= sources[name]["w"]: continue
                try: data = C.fetch(C.thumb_url(sources[name]["url"], w), tries=1); how = f"thumb {w}px"; break
                except Exception: time.sleep(3)
        if data and data[:2] in (b"\xff\xd8", b"\x89P"):
            os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "wb").write(data); del jobs[name]
            s = sources.get(name, {}); print(f"{name}: {how}, {len(data) // 1024} KB ({s.get('license', 'direct url')})", flush=True)
        time.sleep(8)
    if jobs: time.sleep(20)
json.dump(sources, open(srcf, "w"), indent=1, ensure_ascii=False)
for name, s in sources.items():
    lic = s.get("license", "?")
    if "public domain" not in lic.lower() and "cc0" not in lic.lower() and "pd" not in lic.lower():
        print(f"NOTE {name}: licence '{lic}' -> credit it in the caption (story images.{name}.credit)")
print("missing:", list(jobs) or "none")
