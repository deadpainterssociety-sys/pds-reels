"""Original files from Wikimedia Commons for a long video, fetched on a GitHub runner (workflow long-src.yml).

Long videos are rendered by Claude outside CI, where Wikimedia answers HTTP 429 to almost every original download from
the shared cloud address. A runner gets them patiently, and the files are kept with the story's sources in its private
release (reel-<slug> src.tar, `release.py upload-src`), so they are not lost when a session ends. Claude then restores
them with `python automation/release.py download-src <slug>` (or `gh api` for a large src.tar).

usage (CI): python automation/long_src.py <slug> "name=File:Title.jpg|music/m_x=File:Piece.ogg|…" [--minutes 40]
  each file lands in stories/<slug>/src/<name><extension of the original>; images that stay refused after half the time
  fall back to the largest standard-width thumbnail (audio has none: originals only). Prints what it got.
"""
import os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import commons as C

slug, spec = sys.argv[1], sys.argv[2]
limit = 60 * (float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else 40)
src = os.path.join(ROOT, "stories", slug, "src")
jobs = {}
for item in filter(None, (x.strip() for x in spec.split("|"))):
    name, title = item.split("=", 1)
    jobs[name.strip()] = title.strip()
info = {}
for name, title in jobs.items():
    try: info[name] = C.info(title)
    except SystemExit as e: print(f"!! {name}: {e}")
    time.sleep(1)
todo = {n: t for n, t in jobs.items() if n in info}
t0 = time.time()
while todo and time.time() - t0 < limit:
    for name in list(todo):
        i = info[name]; ext = os.path.splitext(i["url"])[1].lower()
        path = os.path.join(src, name + ext)
        if os.path.exists(path) and os.path.getsize(path) > 1000: del todo[name]; continue
        data, how = None, "original"
        try: data = C.fetch(i["url"], tries=1)
        except Exception: data = None
        if data is None and ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff") and time.time() - t0 > limit / 2:
            for w in C.STD_WIDTHS:
                if w >= i["w"]: continue
                try:
                    data = C.fetch(C.thumb_url(i["url"], w) + (".jpg" if ext in (".tif", ".tiff") else ""), tries=1)
                    how = f"thumb {w}px"; path = os.path.join(src, name + (".jpg" if ext in (".tif", ".tiff") else ext)); break
                except Exception: time.sleep(3)
        if data and len(data) > 1000:
            os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "wb").write(data); del todo[name]
            print(f"{name}{ext}: {how}, {len(data) // 1024} KB, {i['w']}x{i['h']} ({i['license']}) {i['title']}", flush=True)
        time.sleep(6)
    if todo: time.sleep(15)
print("missing:", list(todo) or "none")
