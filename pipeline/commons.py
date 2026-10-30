"""Wikimedia Commons helper (search, licence info, download).

usage:
  python pipeline/commons.py search "<query>" [n]      list files, biggest first: WxH  title
  python pipeline/commons.py info "File:Name.jpg"       url, size, licence, author, date
Wikimedia requires a descriptive User-Agent with a contact URL. Shared cloud IPs get HTTP 429 often:
see fetch_images.py for the patient downloader. Thumbnails only exist at standard widths (w.wiki/GHai).
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error

# Put your channel/profile URL here (or export REELS_UA): Wikimedia blocks anonymous or generic agents.
UA = os.environ.get("REELS_UA", "DeadPaintersSocietyBot/1.0 (https://www.instagram.com/thedeadpainterssociety/; art-history reels) python-urllib")
API = "https://commons.wikimedia.org/w/api.php?"
STD_WIDTHS = [3840, 2560, 1920, 1280, 960, 500, 330, 250]


def fetch(url, tries=8, ua=None):
    delay = 2.0
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua or UA}), timeout=90).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k < tries - 1:
                ra = e.headers.get("Retry-After")
                time.sleep(float(ra) if ra and ra.isdigit() else delay); delay = min(delay * 2, 60); continue
            raise


def api(**params):
    return json.loads(fetch(API + urllib.parse.urlencode({**params, "format": "json", "maxlag": 5})))


def info(title):
    page = next(iter(api(action="query", prop="imageinfo", iiprop="url|size|extmetadata", titles=title,
                         iiextmetadatafilter="LicenseShortName|Artist|DateTimeOriginal")["query"]["pages"].values()))
    if "imageinfo" not in page: raise SystemExit(f"not found on Commons: {title}")
    ii = page["imageinfo"][0]; md = {k: v["value"] for k, v in ii.get("extmetadata", {}).items()}
    return {"title": page["title"], "url": ii["url"].split("?")[0], "w": ii["width"], "h": ii["height"],
            "license": md.get("LicenseShortName", "?"), "artist": md.get("Artist", ""), "date": md.get("DateTimeOriginal", "")}


def search(q, n=10):
    r = api(action="query", generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=n, prop="imageinfo", iiprop="size")
    pages = r.get("query", {}).get("pages", {}).values()
    return sorted(([p["imageinfo"][0]["width"], p["imageinfo"][0]["height"], p["title"]] for p in pages if "imageinfo" in p),
                  key=lambda x: -x[0] * x[1])


def thumb_url(url, width):
    base, fn = url.split("/wikipedia/commons/")[1].rsplit("/", 1)
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{base}/{fn}/{width}px-{fn}"


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for w, h, t in search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10): print(f"{w}x{h}  {t}")
    elif sys.argv[1] == "info":
        print(json.dumps(info(sys.argv[2]), indent=1, ensure_ascii=False))
