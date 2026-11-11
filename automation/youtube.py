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
`after` (long-after.yml, 18:10 Madrid on Mondays and Thursdays): the subtitles if they couldn't be added at upload (also
before the slot), and after the slot the question comment (story.json youtube.pinned_comment) posted as the channel. The API can't
pin a comment: Telegram sends Gigi a link straight to it, and she pins it in two taps.
Subtitles and comments need the scope youtube.force-ssl on the refresh token (SETUP.md step 5); `check` lists the scopes.

usage: python automation/youtube.py check | publish <slug> | long <slug> <YYYY-MM-DDTHH:MM:SS+01:00> | after [<slug>]
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
    try: sc = " · scopes: " + " ".join(x.rsplit("/", 1)[-1] for x in http("GET", f"{OAUTH}/tokeninfo?access_token={tok}").get("scope", "").split())
    except RuntimeError: sc = ""
    print("youtube ok:", (items[0]["snippet"]["title"] if items else "(token works; channel list needs youtube.readonly — fine)") + sc)


def place(slug):
    """recordingDetails: the museum where the painting hangs (automation/places.py); {} if unknown"""
    try:
        import places
        p = places.get(slug)
    except Exception as e: print("youtube: no location:", e); return {}
    if not p: return {}
    d = {"locationDescription": p["name"]}
    if p.get("lat") is not None: d["location"] = {"latitude": p["lat"], "longitude": p["lon"]}
    return {"recordingDetails": d}


def publish(slug):
    tok = token(); c = captions(slug); st = story(slug)
    tags = [w.lstrip("#") for w in st.get("hashtags", []) if w.startswith("#")][:15]
    meta = {"snippet": {"title": c["youtube_title"][:100], "description": c["youtube_desc"][:4900], "tags": tags,
                        "categoryId": CONFIG.get("youtube_category", "27"), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": CONFIG.get("youtube_privacy", "public"), "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}, **place(slug)}
    path = os.path.join(out_dir(slug), f"{slug}.mp4"); size = os.path.getsize(path)
    parts = "snippet,status" + (",recordingDetails" if "recordingDetails" in meta else "")
    _, h = http("POST", f"{API}/upload/youtube/v3/videos?uploadType=resumable&part={parts}",
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
                       "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}, **place(slug)}
    video = next(p for p in [os.path.join(od, f"{slug}.mp4"), os.path.join(od, f"{slug}_upload_1080p.mp4")] if os.path.exists(p))
    parts = "snippet,status" + (",recordingDetails" if "recordingDetails" in meta else "")
    r = _resumable(tok, f"{API}/upload/youtube/v3/videos?uploadType=resumable&part={parts}", meta, video, "video/mp4")
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
            res["notes"].append("English subtitles added"); res["captions"] = True
        except RuntimeError as e: res["notes"].append(f"subtitles not added ({str(e)[:160]}): upload captions.srt in Studio")
    return res


def _captions(tok, slug, vid):
    srt = os.path.join(out_dir(slug), "captions.srt")
    if not os.path.exists(srt): return None
    _resumable(tok, f"{API}/upload/youtube/v3/captions?uploadType=resumable&part=snippet",
               {"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}}, srt, "application/octet-stream")
    return True


def _comment(tok, vid, text):
    r = http("POST", f"{API}/youtube/v3/commentThreads?part=snippet", {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
             json.dumps({"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).encode())
    return r["id"]


def after(only=None):
    """for every long video that has gone public: subtitles (if missing) + the question comment (once). Prints one JSON
    line per thing done or failed: {"slug", "did", "link"?, "error"?}"""
    import datetime, glob
    from common import set_state, state
    now_ = datetime.datetime.now(datetime.timezone.utc); tok = None
    for path in sorted(glob.glob("stories/*/state.json")):
        slug = path.split("/")[1]
        if only and slug != only: continue
        sta = state(slug); vid = sta.get("youtube_id"); pa = sta.get("publish_at")
        if not vid or not pa: continue
        live = datetime.datetime.fromisoformat(pa) <= now_   # subtitles can go on a scheduled (private) video; the comment can't
        if datetime.datetime.fromisoformat(pa) < now_ - datetime.timedelta(days=14) and not only: continue
        if not live and sta.get("captions"): continue
        tok = tok or token(); yt = story(slug).get("youtube", {})
        if not sta.get("captions"):
            try:
                if _captions(tok, slug, vid): set_state(slug, captions=True); print(json.dumps({"slug": slug, "did": "subtitles"}))
            except RuntimeError as e: print(json.dumps({"slug": slug, "did": "subtitles", "error": str(e)[:300]}))
        text = (yt.get("pinned_comment") or "").strip()
        if live and text and not sta.get("comment_id"):
            try:
                cid = _comment(tok, vid, text); set_state(slug, comment_id=cid)
                print(json.dumps({"slug": slug, "did": "comment", "title": (yt.get("titles") or [slug])[0],
                                  "link": f"https://www.youtube.com/watch?v={vid}&lc={cid}"}))
            except RuntimeError as e: print(json.dumps({"slug": slug, "did": "comment", "error": str(e)[:300]}))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "check": check()
    elif c == "publish": print(publish(sys.argv[2]))
    elif c == "long": print(json.dumps(publish_long(sys.argv[2], sys.argv[3])))
    elif c == "after": after(sys.argv[2] if len(sys.argv) > 2 else None)
