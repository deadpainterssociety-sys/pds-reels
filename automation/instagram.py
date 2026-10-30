"""Instagram Reels via the Instagram API with Instagram Login (graph.instagram.com).

Needs: an Instagram professional account (Business or Creator) and a Meta app with the Instagram product
('API setup with Instagram login'), permissions instagram_business_basic + instagram_business_content_publish.
While the app is in Development mode it works for accounts that have a role on the app (you) - no App Review needed.
IG_ACCESS_TOKEN = the long-lived token generated in the app dashboard (60 days; refreshed weekly by tokens.yml).

Meta downloads the video itself, so it must be at a PUBLIC https URL (we deploy it to GitHub Pages just before posting).
Limits: 100 API posts per 24 h. Reels: 9:16, 5-90 s, <= 100 MB, H.264 + AAC 48 kHz (our master fits).
Flow: POST /me/media (REELS) -> poll status_code until FINISHED -> POST /me/media_publish -> permalink.

usage: python automation/instagram.py check | refresh | publish <slug> <video_url> <cover_url>
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, captions, env, set_github_secret

BASE = os.environ.get("IG_API", "https://graph.instagram.com").rstrip("/")
V = CONFIG.get("instagram_api_version", "v23.0")


def req(method, path, **params):
    params["access_token"] = env("IG_ACCESS_TOKEN")
    data = urllib.parse.urlencode(params).encode() if method == "POST" else None
    url = f"{BASE}/{V}/{path}" + ("" if data else "?" + urllib.parse.urlencode(params))
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:600]
        raise RuntimeError(f"Instagram {path}: HTTP {e.code} {body}")


def me():
    return req("GET", "me", fields="user_id,username,account_type")


def check():
    m = me(); print(f"instagram ok: @{m.get('username')} ({m.get('account_type')})"); return m


def refresh():
    """long-lived tokens last 60 days and can be refreshed once they are > 24 h old"""
    url = f"{BASE}/refresh_access_token?" + urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": env("IG_ACCESS_TOKEN")})
    r = json.load(urllib.request.urlopen(url, timeout=60))
    days = int(r.get("expires_in", 0)) // 86400
    saved = set_github_secret("IG_ACCESS_TOKEN", r["access_token"])
    print(f"instagram token refreshed (valid {days} days){'' if saved else ' — NOT saved, add GH_PAT'}"); return saved


def publish(slug, video_url, cover_url=None, wait=600):
    uid = "me"
    params = {"media_type": "REELS", "video_url": video_url, "caption": captions(slug)["instagram"][:2200], "share_to_feed": "true"}
    if cover_url: params["cover_url"] = cover_url
    cid = req("POST", f"{uid}/media", **params)["id"]
    t0 = time.time()
    while True:
        time.sleep(float(os.environ.get("POLL_SECONDS", 15)))
        st = req("GET", cid, fields="status_code,status")
        code = st.get("status_code"); print("  instagram container:", code)
        if code == "FINISHED": break
        if code in ("ERROR", "EXPIRED"): raise RuntimeError(f"Instagram processing failed: {st.get('status')}")
        if time.time() - t0 > wait: raise RuntimeError("Instagram container not ready after 10 min")
    mid = req("POST", f"{uid}/media_publish", creation_id=cid)["id"]
    link = req("GET", mid, fields="permalink").get("permalink")
    return {"id": mid, "url": link}


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "refresh": refresh()
    elif c == "publish": print(publish(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
