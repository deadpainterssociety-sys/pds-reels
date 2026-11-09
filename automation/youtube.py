"""YouTube Shorts via the YouTube Data API v3 (plain HTTPS, resumable upload - no Google client libraries needed).

Needs: a Google Cloud project with 'YouTube Data API v3' enabled, an OAuth client (type 'Web application') and a refresh
token for your channel with the scope youtube.upload (get it in the browser with the OAuth Playground - see SETUP.md).
GOTCHA: if the OAuth consent screen stays in 'Testing', refresh tokens die after 7 days -> set it to 'In production'
(for your own channel just click through the 'unverified app' warning once).
A vertical video up to 3 minutes is published as a Short. videos.insert has its own quota bucket (100 uploads/day).
status.containsSyntheticMedia = true discloses the AI voice.

Long videos (16:9, from stories/<slug>/out/): `long <slug> <publish_at>` uploads the master as PRIVATE with publishAt set,
so YouTube makes it public on its own at that time; then thumbnail A and the English subtitles. Test & compare (title B,
thumbnail B) and the end screen can't be set through the API: Gigi adds them in Studio before the slot.

usage: python automation/youtube.py check | publish <slug> | long <slug> <YYYY-MM-DDTHH:MM:SS+01:00>
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, captions, env, out_dir, story

OAUTH = os.environ.get("YT_OAUTH", "https://oauth2.googleapis.com").rstrip("/")
API = os.environ.get("YT_API", "https://www.googleapis.com").rstrip("/")


def http(method, url, headers=None, body=None, want_headers=False):
    rq = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        r = urllib.request.urlopen(rq, timeout=600); txt = r.read()
        data = json.loads(txt) if txt else {}
        return (data, r.headers) if want_headers else data
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"YouTube {url.split('?')[0]}: HTTP {e.code} {e.read().decode()[:600]}")


def token():
    body = urllib.parse.urlencode({"client_id": env("YT_CLIENT_ID"), "client_secret": env("YT_CLIENT_SECRET"),
                                   "refresh_token": env("YT_REFRESH_TOKEN"), "grant_type": "refresh_token"}).encode()
    return http("POST", f"{OAUTH}/token", {"Content-Type": "application/x-www-form-urlencoded"}, body)["access_token"]


def check():
    tok = token()
    try:
        r = http("GET", f"{API}/youtube/v3/channels?part=snippet&mine=true", {"Authorization": f"Bearer {tok}"})
    except RuntimeError as e:
        if "403" in str(e): print("youtube ok: token works (upload-only scope)"); return
        raise
    items = r.get("items", [])
    print("youtube ok:", items[0]["snippet"]["title"] if items else "(token works; channel list needs youtube.readonly — fine)")


def publish(slug):
    tok = token(); c = captions(slug); st = story(slug)
    tags = [w.lstrip("#") for w in st.get("hashtags", []) if w.startswith("#")][:15]
    meta = {"snippet": {"title": c["youtube_title"][:100], "description": c["youtube_desc"][:4900], "tags": tags,
                        "categoryId": CONFIG.get("youtube_category", "27"), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": CONFIG.get("youtube_privacy", "public"), "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}
    path = os.path.join(out_dir(slug), f"{slug}.mp4"); size = os.path.getsize(path)
    _, h = http("POST", f"{API}/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, json.dumps(meta).encode(), want_headers=True)
    loc = h.get("Location") or h.get("location")
    if not loc: raise RuntimeError("YouTube did not return an upload URL")
    r = http("PUT", loc, {"Content-Type": "video/mp4", "Content-Length": str(size)}, open(path, "rb").read())
    vid = r["id"]; priv = r.get("status", {}).get("privacyStatus")
    res = {"id": vid, "url": f"https://youtube.com/shorts/{vid}"}
    if priv and priv != meta["status"]["privacyStatus"]:
        res["warning"] = f"YouTube set it to {priv} (expected {meta['status']['privacyStatus']})"
    return res


def _resumable(tok, url, meta, path, ctype):
    size = os.path.getsize(path)
    _, h = http("POST", url, {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                              "X-Upload-Content-Type": ctype, "X-Upload-Content-Length": str(size)}, json.dumps(meta).encode(), want_headers=True)
    loc = h.get("Location") or h.get("location")
    if not loc: raise RuntimeError("YouTube did not return an upload URL")
    return http("PUT", loc, {"Content-Type": ctype, "Content-Length": str(size)}, open(path, "rb").read())


def publish_long(slug, publish_at):
    import datetime
    when = datetime.datetime.fromisoformat(publish_at)
    if when.tzinfo is None: raise SystemExit("publish_at needs a UTC offset, e.g. 2026-11-12T18:00:00+01:00")
    if when < datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30): raise SystemExit(f"publish_at {publish_at} is too soon")
    tok = token(); od = out_dir(slug); st = story(slug); yt = st.get("youtube", {})
    title = (yt.get("titles") or [st.get("meta", {}).get("painting", slug)])[0][:100]
    desc = open(os.path.join(od, "description.txt")).read()[:4900]
    tags = [w.lstrip("#") for w in yt.get("hashtags", [])] + [st.get("meta", {}).get("painter", ""), st.get("meta", {}).get("painting", ""), "art history", "painting"]
    meta = {"snippet": {"title": title, "description": desc, "tags": [t for t in tags if t][:15], "categoryId": "27",   # 27 = Education
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "private", "publishAt": when.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                       "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    video = next(p for p in [os.path.join(od, f"{slug}.mp4"), os.path.join(od, f"{slug}_upload_1080p.mp4")] if os.path.exists(p))
    r = _resumable(tok, f"{API}/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", meta, video, "video/mp4")
    vid = r["id"]; res = {"id": vid, "url": f"https://youtu.be/{vid}", "studio": f"https://studio.youtube.com/video/{vid}/edit",
                          "publish_at": publish_at, "privacy": r.get("status", {}).get("privacyStatus"), "notes": []}
    thumb = os.path.join(od, "thumb_a.jpg")
    if os.path.exists(thumb):
        try:
            http("POST", f"{API}/upload/youtube/v3/thumbnails/set?videoId={vid}", {"Authorization": f"Bearer {tok}", "Content-Type": "image/jpeg"}, open(thumb, "rb").read())
            res["notes"].append("thumbnail A set")
        except RuntimeError as e: res["notes"].append(f"thumbnail not set ({str(e)[:160]}): upload thumb_a.jpg in Studio")
    srt = os.path.join(od, "captions.srt")
    if os.path.exists(srt):
        try:
            _resumable(tok, f"{API}/upload/youtube/v3/captions?uploadType=resumable&part=snippet",
                       {"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}}, srt, "application/octet-stream")
            res["notes"].append("English subtitles added")
        except RuntimeError as e: res["notes"].append(f"subtitles not added ({str(e)[:160]}): upload captions.srt in Studio")
    return res


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "publish": print(publish(sys.argv[2]))
    elif c == "long": print(json.dumps(publish_long(sys.argv[2], sys.argv[3])))
