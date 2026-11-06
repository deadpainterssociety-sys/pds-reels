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


_MODE = None   # "instagram" (graph.instagram.com, account "me") or "facebook" (graph.facebook.com, business account id)


def fb_token():
    """which API this token speaks. "IG…" tokens are Instagram Login; others are tried on Instagram first
    (some dashboards now hand out Instagram tokens that don't start with IG), then on Facebook."""
    global _MODE
    if _MODE: return _MODE == "facebook"
    tok = env("IG_ACCESS_TOKEN").strip()
    if tok.startswith("IG"): _MODE = "instagram"; return False
    if os.environ.get("IG_API"): _MODE = "facebook"; return True     # tests: one mock serves both APIs, decide by prefix
    try:
        json.load(urllib.request.urlopen(f"https://graph.instagram.com/{V}/me?" + urllib.parse.urlencode(
            {"fields": "user_id,username", "access_token": tok}), timeout=60)); _MODE = "instagram"
    except Exception: _MODE = "facebook"
    print("instagram: token works with the", "Instagram Login API" if _MODE == "instagram" else "Facebook Graph API")
    return _MODE == "facebook"


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
    try: pages = req("GET", "me/accounts", fields="name,instagram_business_account{id,username}").get("data", [])
    except RuntimeError: pages = []
    for pg in pages:
        ig = pg.get("instagram_business_account")
        if ig: _UID = ig["id"]; print(f"instagram: posting as @{ig.get('username')} (via the Facebook Page {pg.get('name')})"); return _UID
    try:   # a system-user token (unified login) may have no Page: the token itself names the Instagram account it covers
        d = req("GET", "debug_token", input_token=env("IG_ACCESS_TOKEN").strip()).get("data", {})
        for g in d.get("granular_scopes", []):
            if g.get("scope") in ("instagram_content_publish", "instagram_basic") and g.get("target_ids"):
                _UID = g["target_ids"][0]; print(f"instagram: posting as account {_UID} (from the token's permissions)"); return _UID
    except RuntimeError as e: print("instagram: debug_token:", e)
    try: bizs = req("GET", "me/businesses", fields="id,name").get("data", [])
    except RuntimeError: bizs = []                                          # token without business permissions
    for b in bizs:   # accounts owned by the business portfolio
        for edge in ("owned_instagram_accounts", "instagram_business_accounts"):
            try: accts = req("GET", f"{b['id']}/{edge}", fields="id,username").get("data", [])
            except RuntimeError: continue
            if accts:
                _UID = accts[0]["id"]; print(f"instagram: posting as @{accts[0].get('username')} (portfolio {b.get('name')})"); return _UID
    try: who = req("GET", "me", fields="id,name").get("name", "?")
    except RuntimeError: who = "?"
    raise RuntimeError(f"This token (it belongs to '{who}') sees no Instagram account: add the IG_USER_ID secret "
                       "with the Instagram account's ID (Meta app dashboard → Instagram API → step 2, the number under the username)")


def me():
    if fb_token():
        m = req("GET", uid(), fields="id,username"); m["account_type"] = "BUSINESS (Facebook login)"; return m
    return req("GET", "me", fields="user_id,username,account_type")


def token_info():
    """Facebook-style tokens: type, app, permissions granted (debug_token); {} for Instagram-login tokens"""
    if not fb_token(): return {}
    try: d = req("GET", "debug_token", input_token=env("IG_ACCESS_TOKEN").strip()).get("data", {})
    except RuntimeError as e: return {"error": str(e)[:200]}
    return {"type": d.get("type"), "app": d.get("application"), "scopes": d.get("scopes") or [g.get("scope") for g in d.get("granular_scopes", [])],
            "expires_at": d.get("expires_at"), "valid": d.get("is_valid")}


def expiry():
    """Facebook-style tokens: when does this one expire? ('never' for system-user tokens)"""
    try: d = req("GET", "debug_token", input_token=env("IG_ACCESS_TOKEN").strip()).get("data", {})
    except RuntimeError: return None
    exp = int(d.get("expires_at") or 0)
    if not exp: return "never"
    import datetime
    return datetime.datetime.fromtimestamp(exp, datetime.timezone.utc).date().isoformat()


def check():
    m = me(); note = ""
    if fb_token():
        e = expiry()
        if e and e != "never":
            import datetime
            left = (datetime.date.fromisoformat(e) - datetime.date.today()).days
            note = f" · token expires {e} ({left} days)" + (" — generate a new one in the Meta app and replace IG_ACCESS_TOKEN" if left < 14 else "")
            if left < 0: raise RuntimeError(f"Instagram token expired on {e}: generate a new one in the Meta app (step 2) and replace IG_ACCESS_TOKEN")
        elif e == "never": note = " · token never expires"
    print(f"instagram ok: @{m.get('username')} ({m.get('account_type')}){note}"); return m


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
