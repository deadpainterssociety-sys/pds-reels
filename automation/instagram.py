"""Instagram Reels. Works with either kind of token Meta's dashboard hands out (detected automatically):
  - Instagram Login token (starts with "IG…")  -> graph.instagram.com, account "me"
  - Facebook Login / unified login / system-user token (starts with "EAA…") -> graph.facebook.com, the Instagram business
    account id found through the connected Facebook Page (or the IG_USER_ID secret, if set)

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

V = CONFIG.get("instagram_api_version", "v23.0")


def fb_token(): return not env("IG_ACCESS_TOKEN").strip().startswith("IG")


def base():
    if os.environ.get("IG_API"): return os.environ["IG_API"].rstrip("/")
    return "https://graph.facebook.com" if fb_token() else "https://graph.instagram.com"


def req(method, path, **params):
    BASE = base()
    params["access_token"] = env("IG_ACCESS_TOKEN").strip()
    data = urllib.parse.urlencode(params).encode() if method == "POST" else None
    url = f"{BASE}/{V}/{path}" + ("" if data else "?" + urllib.parse.urlencode(params))
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:600]
        raise RuntimeError(f"Instagram {path}: HTTP {e.code} {body}")


_UID = None


def uid():
    """the account to post as: "me" for Instagram Login tokens; the Instagram business account id for Facebook tokens"""
    global _UID
    if _UID: return _UID
    if not fb_token(): _UID = "me"; return _UID
    if os.environ.get("IG_USER_ID", "").strip(): _UID = os.environ["IG_USER_ID"].strip(); return _UID
    for pg in req("GET", "me/accounts", fields="name,instagram_business_account{id,username}").get("data", []):
        ig = pg.get("instagram_business_account")
        if ig: _UID = ig["id"]; print(f"instagram: posting as @{ig.get('username')} (via the Facebook Page {pg.get('name')})"); return _UID
    raise RuntimeError("This Facebook token sees no Instagram business account: connect @thedeadpainterssociety to a Facebook Page "
                       "(or add the IG_USER_ID secret with the account's id)")


def me():
    if fb_token():
        m = req("GET", uid(), fields="id,username"); m["account_type"] = "BUSINESS (Facebook login)"; return m
    return req("GET", "me", fields="user_id,username,account_type")


def check():
    m = me(); print(f"instagram ok: @{m.get('username')} ({m.get('account_type')})"); return m


def refresh():
    """long-lived tokens last 60 days and can be refreshed once they are > 24 h old"""
    if fb_token():
        print("instagram: Facebook/system-user token — nothing to refresh (system-user tokens never expire)"); return True
    url = f"{base()}/refresh_access_token?" + urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": env("IG_ACCESS_TOKEN")})
    r = json.load(urllib.request.urlopen(url, timeout=60))
    days = int(r.get("expires_in", 0)) // 86400
    saved = set_github_secret("IG_ACCESS_TOKEN", r["access_token"])
    print(f"instagram token refreshed (valid {days} days){'' if saved else ' — NOT saved, add GH_PAT'}"); return saved


def publish(slug, video_url, cover_url=None, wait=600):
    uid_ = uid()
    params = {"media_type": "REELS", "video_url": video_url, "caption": captions(slug)["instagram"][:2200], "share_to_feed": "true"}
    if cover_url: params["cover_url"] = cover_url
    cid = req("POST", f"{uid_}/media", **params)["id"]
    t0 = time.time()
    while True:
        time.sleep(float(os.environ.get("POLL_SECONDS", 15)))
        st = req("GET", cid, fields="status_code,status")
        code = st.get("status_code"); print("  instagram container:", code)
        if code == "FINISHED": break
        if code in ("ERROR", "EXPIRED"): raise RuntimeError(f"Instagram processing failed: {st.get('status')}")
        if time.time() - t0 > wait: raise RuntimeError("Instagram container not ready after 10 min")
    mid = req("POST", f"{uid_}/media_publish", creation_id=cid)["id"]
    link = req("GET", mid, fields="permalink").get("permalink")
    return {"id": mid, "url": link}


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "refresh": refresh()
    elif c == "publish": print(publish(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
