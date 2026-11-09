"""Store each rendered reel as a DRAFT GitHub release named reel-<slug> (drafts are private even in a public repo),
so the evening publish job can fetch the exact file you approved.

usage: python automation/release.py upload <slug>        mp4 + preview + cover + caption + qa + frames (replaces old assets)
       python automation/release.py upload-long <slug>   a long video's master + thumbnails + captions.srt + texts (draft long-<slug>)
       python automation/release.py download-long <slug> -> stories/<slug>/out/ (what the YouTube upload needs)
       python automation/release.py download <slug>      -> stories/<slug>/out/
       python automation/release.py download-publish <slug>  only what publishing needs (video, cover, captions)
       python automation/release.py upload-src <slug>    the story's source images as src.tar (kept out of git to keep the repo small)
       python automation/release.py download-src <slug>  -> stories/<slug>/src/ (skipped if already there)
env:   GITHUB_TOKEN, GITHUB_REPOSITORY (set automatically in Actions)
"""
import json, os, sys, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import out_dir, title_of

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
FILES = ["{s}.mp4", "{s}-preview.mp4", "cover.jpg", "caption.txt", "qa.txt", "frames.jpg", "stills.jpg", "src.tar"]


def gh(method, url, body=None, headers=None, raw=False):
    h = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json", **(headers or {})}
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    if isinstance(body, dict): h["Content-Type"] = "application/json"
    rq = urllib.request.Request(url if url.startswith("http") else API + url, data=data, method=method, headers=h)
    try:
        r = urllib.request.urlopen(rq, timeout=600); txt = r.read()
        return txt if raw else (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        raise SystemExit(f"GitHub {method} {url}: {e.code} {e.read().decode()[:300]}")


def find(slug):
    for page in range(1, 6):
        for r in gh("GET", f"/repos/{REPO}/releases?per_page=100&page={page}"):
            if r.get("name") == f"reel-{slug}" or r.get("tag_name") == f"reel-{slug}": return r
    return None


def upload(slug):
    rel = find(slug) or gh("POST", f"/repos/{REPO}/releases", {"tag_name": f"reel-{slug}", "name": f"reel-{slug}", "draft": True,
                                                                "body": title_of(slug)})
    have = {a["name"]: a["id"] for a in rel.get("assets", [])}
    base = rel["upload_url"].split("{")[0]
    for f in FILES:
        name = f.format(s=slug); path = os.path.join(out_dir(slug), name)
        if not os.path.exists(path): continue
        if name in have: gh("DELETE", f"/repos/{REPO}/releases/assets/{have[name]}")
        ct = {"mp4": "video/mp4", "jpg": "image/jpeg", "txt": "text/plain", "tar": "application/x-tar"}[name.rsplit(".", 1)[1]]
        gh("POST", f"{base}?name={name}", open(path, "rb").read(), {"Content-Type": ct})
        print("uploaded", name)


def upload_src(slug):
    import tarfile
    sd = os.path.join(os.path.dirname(out_dir(slug)), "src"); os.makedirs(out_dir(slug), exist_ok=True)
    with tarfile.open(os.path.join(out_dir(slug), "src.tar"), "w") as t: t.add(sd, arcname="src")
    upload(slug)


def download_src(slug):
    import tarfile, glob
    sd = os.path.join(os.path.dirname(out_dir(slug)), "src")
    if glob.glob(os.path.join(sd, "*.jpg")) or glob.glob(os.path.join(sd, "*.png")): print("src already present"); return
    download(slug, only="src.tar")
    with tarfile.open(os.path.join(out_dir(slug), "src.tar")) as t: t.extractall(os.path.dirname(out_dir(slug)), filter="data")
    print("src restored")


LONG_FILES = ["{s}.mp4", "thumb_a.jpg", "thumb_b.jpg", "captions.srt", "description.txt", "titles.txt"]


def upload_long(slug):
    """long videos are rendered outside CI: park the master (≤ 2 GB per asset) and its texts in a private draft release"""
    tag = f"long-{slug}"
    rel = next((r for page in range(1, 6) for r in gh("GET", f"/repos/{REPO}/releases?per_page=100&page={page}") if r.get("tag_name") == tag), None) \
        or gh("POST", f"/repos/{REPO}/releases", {"tag_name": tag, "name": tag, "draft": True, "body": "long video (private draft)"})
    have = {a["name"]: a["id"] for a in rel.get("assets", [])}; base = rel["upload_url"].split("{")[0]
    for f in LONG_FILES:
        name = f.format(s=slug); path = os.path.join(out_dir(slug), name)
        if not os.path.exists(path): print("missing", name); continue
        if name in have: gh("DELETE", f"/repos/{REPO}/releases/assets/{have[name]}")
        ct = {"mp4": "video/mp4", "jpg": "image/jpeg", "txt": "text/plain", "srt": "application/x-subrip"}[name.rsplit(".", 1)[1]]
        gh("POST", f"{base}?name={name}", open(path, "rb").read(), {"Content-Type": ct}); print("uploaded", name)


PUBLISH_FILES = ["{s}.mp4", "cover.jpg", "caption.txt"]      # all that publishing needs (not src.tar, stills, …)


def _fetch(url, headers=None, total=420):
    """stream a file with a hard overall deadline (a stalled transfer can't hang the job) — 3 tries"""
    import time
    for attempt in range(3):
        t0 = time.time(); buf = bytearray()
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=60)
            while True:
                chunk = r.read(1 << 20)
                if not chunk: return bytes(buf)
                buf += chunk
                if time.time() - t0 > total: raise TimeoutError(f"download too slow ({len(buf) // 1024} KB in {total} s)")
        except Exception as e:
            print(f"download attempt {attempt + 1} failed: {e}"); time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not download {url.split('?')[0]}")


def download(slug, only=None, files=None, tag=None):
    rel = next((r for page in range(1, 6) for r in gh("GET", f"/repos/{REPO}/releases?per_page=100&page={page}") if r.get("tag_name") == tag), None) \
        if tag else find(slug)
    if not rel: raise SystemExit(f"no release {tag or 'reel-' + slug}")
    os.makedirs(out_dir(slug), exist_ok=True)
    want = {f.format(s=slug) for f in files} if files else None
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    op = urllib.request.build_opener(NoRedirect)
    for a in rel["assets"]:   # the API answers 302 to a signed URL that must be fetched WITHOUT our token
        if only and a["name"] != only: continue
        if want and a["name"] not in want: continue
        rq = urllib.request.Request(a["url"], headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/octet-stream"})
        try:
            loc = None; data = op.open(rq, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code not in (301, 302, 303, 307, 308): raise
            loc = e.headers["Location"]
        if loc: data = _fetch(loc, total=1800 if a.get("size", 0) > 200e6 else 420)
        open(os.path.join(out_dir(slug), a["name"]), "wb").write(data); print("downloaded", a["name"], len(data) // 1024, "KB")


# ---------- private data store (draft release "dps-data"): metrics, briefs, TikTok screenshots ----------
DATA = "dps-data"


def data_release():
    for page in range(1, 6):
        for r in gh("GET", f"/repos/{REPO}/releases?per_page=100&page={page}"):
            if r.get("name") == DATA or r.get("tag_name") == DATA: return r
    return gh("POST", f"/repos/{REPO}/releases", {"tag_name": DATA, "name": DATA, "draft": True,
                                                   "body": "Private data of the learning loop (metrics, briefs, TikTok screenshots). Draft = not public."})


def data_list(prefix=""):
    return [a["name"] for a in data_release().get("assets", []) if a["name"].startswith(prefix)]


def data_get(name):
    """bytes of a data file, or None"""
    rel = data_release()
    a = next((a for a in rel.get("assets", []) if a["name"] == name), None)
    if not a: return None
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    rq = urllib.request.Request(a["url"], headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/octet-stream"})
    try: return urllib.request.build_opener(NoRedirect).open(rq, timeout=60).read()
    except urllib.error.HTTPError as e:
        if e.code not in (301, 302, 303, 307, 308): raise
        return _fetch(e.headers["Location"])


def data_put(name, data, ctype="application/json"):
    rel = data_release()
    for a in rel.get("assets", []):
        if a["name"] == name: gh("DELETE", f"/repos/{REPO}/releases/assets/{a['id']}")
    gh("POST", f"{rel['upload_url'].split('{')[0]}?name={name}", data, {"Content-Type": ctype})


def data_delete(name):
    for a in data_release().get("assets", []):
        if a["name"] == name: gh("DELETE", f"/repos/{REPO}/releases/assets/{a['id']}")


if __name__ == "__main__":
    if sys.argv[1] == "download-publish": download(sys.argv[2], files=PUBLISH_FILES)
    elif sys.argv[1] == "upload-long": upload_long(sys.argv[2])
    elif sys.argv[1] == "download-long": download(sys.argv[2], files=LONG_FILES, tag=f"long-{sys.argv[2]}")
    else: {"upload": upload, "download": download, "upload-src": upload_src, "download-src": download_src}[sys.argv[1]](sys.argv[2])
