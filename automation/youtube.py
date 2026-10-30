"""YouTube Shorts via the YouTube Data API v3 (plain HTTPS, resumable upload - no Google client libraries needed).

Needs: a Google Cloud project with 'YouTube Data API v3' enabled, an OAuth client (type 'Web application') and a refresh
token for your channel with the scope youtube.upload (get it in the browser with the OAuth Playground - see SETUP.md).
GOTCHA: if the OAuth consent screen stays in 'Testing', refresh tokens die after 7 days -> set it to 'In production'
(for your own channel just click through the 'unverified app' warning once).
A vertical video up to 3 minutes is published as a Short. videos.insert has its own quota bucket (100 uploads/day).
status.containsSyntheticMedia = true discloses the AI voice.

usage: python automation/youtube.py check | publish <slug>
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


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "publish": print(publish(sys.argv[2]))
