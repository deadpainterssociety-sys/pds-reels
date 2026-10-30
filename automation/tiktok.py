"""TikTok via the Content Posting API (open.tiktokapis.com v2).

Two modes (config.json "tiktok_mode"):
  inbox   (default) scope video.upload: the video lands in your TikTok inbox as a draft; you tap the notification, paste the
          caption the bot sends you, and post. Works before TikTok audits the app. Max 5 pending drafts per 24 h.
  direct  scope video.publish: fully automatic with caption + AI label. BUT until TikTok audits the app every post is forced
          to private (and stays private even after the audit) -> switch to direct only after the audit passes.
Tokens: access tokens last 24 h; the refresh token (365 days) is exchanged at every run, and a rotated one is saved
back to the TIKTOK_REFRESH_TOKEN secret (needs GH_PAT).
Upload: FILE_UPLOAD; chunks 5-64 MB, total_chunk_count = floor(size / chunk), the last chunk takes the remainder,
a file <= 64 MB can go in one chunk. Each PUT carries Content-Range.

usage: python automation/tiktok.py check | publish <slug> | exchange <code> <redirect_uri> | auth-url <redirect_uri>
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, captions, env, out_dir, set_github_secret

BASE = os.environ.get("TIKTOK_API", "https://open.tiktokapis.com").rstrip("/")
SCOPES = "user.info.basic,video.upload,video.publish"


def http(method, url, headers=None, body=None):
    rq = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        r = urllib.request.urlopen(rq, timeout=600); txt = r.read()
        return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"TikTok {url.split('?')[0]}: HTTP {e.code} {e.read().decode()[:600]}")


def oauth(**fields):
    body = urllib.parse.urlencode({"client_key": env("TIKTOK_CLIENT_KEY"), "client_secret": env("TIKTOK_CLIENT_SECRET"), **fields}).encode()
    r = http("POST", f"{BASE}/v2/oauth/token/", {"Content-Type": "application/x-www-form-urlencoded"}, body)
    if "access_token" not in r: raise RuntimeError(f"TikTok OAuth: {r}")
    return r


def access_token():
    old = env("TIKTOK_REFRESH_TOKEN"); r = oauth(grant_type="refresh_token", refresh_token=old)
    if r.get("refresh_token") and r["refresh_token"] != old: set_github_secret("TIKTOK_REFRESH_TOKEN", r["refresh_token"])
    return r["access_token"]


def auth_url(redirect):
    return "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(
        {"client_key": env("TIKTOK_CLIENT_KEY"), "scope": SCOPES, "response_type": "code", "redirect_uri": redirect, "state": "dps"})


def exchange(code, redirect):
    r = oauth(grant_type="authorization_code", code=code, redirect_uri=redirect)
    ok = set_github_secret("TIKTOK_REFRESH_TOKEN", r["refresh_token"])
    print("tiktok linked: scopes", r.get("scope"), "| refresh token saved" if ok else "| NOT saved (add GH_PAT)")


def H(tok): return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"}


def check():
    tok = access_token()
    r = http("GET", f"{BASE}/v2/user/info/?fields=display_name", H(tok))
    print("tiktok ok:", r.get("data", {}).get("user", {}).get("display_name"))


def plan_chunks(size):
    if size <= 64_000_000: return size, 1
    chunk = 10_000_000; return chunk, size // chunk


def publish(slug):
    mode = CONFIG.get("tiktok_mode", "inbox"); tok = access_token()
    path = os.path.join(out_dir(slug), f"{slug}.mp4"); size = os.path.getsize(path)
    chunk, n = plan_chunks(size)
    src = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": n}
    if mode == "direct":
        info = http("POST", f"{BASE}/v2/post/publish/creator_info/query/", H(tok), b"{}")["data"]
        opts = info.get("privacy_level_options", [])
        privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opts else (opts[0] if opts else "SELF_ONLY")
        body = {"post_info": {"title": captions(slug)["tiktok"][:2200], "privacy_level": privacy, "disable_comment": False,
                              "disable_duet": False, "disable_stitch": False, "video_cover_timestamp_ms": 50, "is_aigc": True},
                "source_info": src}
        r = http("POST", f"{BASE}/v2/post/publish/video/init/", H(tok), json.dumps(body).encode())
    else:
        r = http("POST", f"{BASE}/v2/post/publish/inbox/video/init/", H(tok), json.dumps({"source_info": src}).encode())
    if r.get("error", {}).get("code", "ok") != "ok": raise RuntimeError(f"TikTok init: {r['error']}")
    url, pid = r["data"]["upload_url"], r["data"]["publish_id"]
    with open(path, "rb") as f:
        for i in range(n):
            a = i * chunk; b = size - 1 if i == n - 1 else a + chunk - 1
            f.seek(a); part = f.read(b - a + 1)
            http("PUT", url, {"Content-Type": "video/mp4", "Content-Length": str(len(part)), "Content-Range": f"bytes {a}-{b}/{size}"}, part)
    status = "?"
    for _ in range(40):
        time.sleep(float(os.environ.get("POLL_SECONDS", 8)))
        s = http("POST", f"{BASE}/v2/post/publish/status/fetch/", H(tok), json.dumps({"publish_id": pid}).encode()).get("data", {})
        status = s.get("status"); print("  tiktok:", status)
        if status in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"): break
        if status == "FAILED": raise RuntimeError(f"TikTok failed: {s.get('fail_reason')}")
    res = {"id": pid, "mode": mode, "status": status}
    if mode == "direct" and privacy != "PUBLIC_TO_EVERYONE": res["warning"] = f"posted as {privacy} (app not audited yet?)"
    return res


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "publish": print(publish(sys.argv[2]))
    elif c == "exchange": exchange(sys.argv[2], sys.argv[3])
    elif c == "auth-url": print(auth_url(sys.argv[2]))
