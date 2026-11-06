"""The learning loop's data: every posted reel's numbers on each platform over time, joined with what the reel was
(hook type, hook wording, cover question, painting, slot, weekday, length, experiment arm). Kept PRIVATE in the draft
release "dps-data" as metrics.json — never in the public repo.

usage: python automation/metrics.py collect          pull fresh numbers for reels posted in the last 21 days (+ hit alert)
       python automation/metrics.py backfill         find YouTube/Instagram ids of reels that were posted by hand
       python automation/metrics.py pull <dir>        metrics.json + new TikTok screenshots + past briefs -> <dir> (for the lab)
       python automation/metrics.py table [dir]      <dir>/table.csv: one row per reel, numbers at 24 h / 72 h / 7 d
       python automation/metrics.py tiktok-add <slug> '<json>' [dir]   numbers read from a TikTok screenshot
       python automation/metrics.py push <dir>        save <dir>/metrics.json back (after the lab added TikTok numbers)

YouTube: Data API statistics (fresh views/likes/comments, scope youtube.readonly) + Analytics API (average % viewed,
average view duration, shares, subscribers gained; scope yt-analytics.readonly, ~1-2 days late).
Instagram: media insights (views, reach, likes, comments, shares, saved, average watch time; permission
instagram_manage_insights). Missing permissions are noted in metrics.json["notes"] and the brief says so.
"""
import csv, datetime, io, json, os, re, statistics, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, ROOT, now, schedule, slot_time, state, story

AGES = (24, 72, 168)                      # hours at which reels are compared
ACTIVE_DAYS = 21                          # stop polling a reel after this


def _iso(t): return t.isoformat(timespec="seconds")
def _parse(s): return datetime.datetime.fromisoformat(s)


def load():
    import release
    raw = release.data_get("metrics.json")
    return json.loads(raw) if raw else {"reels": {}, "notes": {}}


def save(m):
    import release
    m["updated"] = _iso(now())
    release.data_put("metrics.json", json.dumps(m, indent=1, ensure_ascii=False).encode())


def features(slug):
    """what the reel WAS — the variables the lab compares"""
    st, s = story(slug), state(slug)
    lines = st.get("lines") or [{}]
    hook = " ".join(re.sub(r"\*", "", ph[0]) for ph in lines[0].get("perf", [])).strip()
    words = sum(len(re.sub(r"\*", "", ph[0]).split()) for ln in lines for ph in ln.get("perf", []))
    posted = s.get("posted_at")
    pt = _parse(posted) if posted else None
    m = st.get("meta", {})
    return {"slug": slug, "painter": m.get("painter"), "painting": m.get("painting"), "year": m.get("year"),
            "museum": m.get("museum"), "city": m.get("city"), "hook_type": st.get("hook_type"), "hook": hook,
            "hook_words": len(hook.split()), "cover_question": re.sub(r"</?i>", "", st.get("cover", {}).get("question", "")),
            "youtube_title": st.get("youtube_title"), "nude": bool(m.get("nude")), "words": words,
            "duration_s": s.get("duration_s"), "experiment": st.get("experiment"),
            "slot": slot_time(slug), "posted_at": posted, "weekday": pt.strftime("%a") if pt else None,
            "posted_hour": pt.hour if pt else None, "manual": bool(s.get("manual"))}


# ---------------------------------------------------------------- YouTube
def youtube_numbers(ids, notes):
    import youtube as Y
    if not ids or not os.environ.get("YT_REFRESH_TOKEN", "").strip(): return {}
    tok = Y.token(); H = {"Authorization": f"Bearer {tok}"}; out = {i: {} for i in ids}
    for k in range(0, len(ids), 50):
        r = Y.http("GET", f"{Y.API}/youtube/v3/videos?part=statistics&id={','.join(ids[k:k + 50])}", H)
        for it in r.get("items", []):
            st = it.get("statistics", {})
            out[it["id"]].update(views=int(st.get("viewCount", 0)), likes=int(st.get("likeCount", 0)), comments=int(st.get("commentCount", 0)))
    ana = os.environ.get("YT_ANALYTICS_API", "https://youtubeanalytics.googleapis.com").rstrip("/")
    q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": "2026-10-01", "endDate": (now() + datetime.timedelta(days=1)).date().isoformat(),
                                "metrics": "views,averageViewPercentage,averageViewDuration,shares,subscribersGained,likes,comments",
                                "dimensions": "video", "filters": "video==" + ",".join(ids[:200]), "maxResults": 200})
    try:
        r = Y.http("GET", f"{ana}/v2/reports?{q}", H); notes.pop("youtube_analytics", None)
        cols = [c["name"] for c in r.get("columnHeaders", [])]
        for row in r.get("rows", []):
            d = dict(zip(cols, row)); v = out.setdefault(d["video"], {})
            v.update(avg_view_pct=d.get("averageViewPercentage"), avg_view_s=d.get("averageViewDuration"), shares=d.get("shares"),
                     subs=d.get("subscribersGained"), analytics_views=d.get("views"))
    except RuntimeError as e:
        notes["youtube_analytics"] = ("needs the yt-analytics.readonly permission (SETUP: redo the OAuth Playground step with it)"
                                      if ("403" in str(e) or "401" in str(e)) else str(e)[:200])
    return out


# ---------------------------------------------------------------- Instagram
IG_METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions", "ig_reels_avg_watch_time"]


def instagram_numbers(media_id, notes):
    import instagram as I
    try:
        r = I.req("GET", f"{media_id}/insights", metric=",".join(IG_METRICS)); notes.pop("instagram_insights", None)
    except RuntimeError as e:
        if "permission" in str(e).lower() or "(#10)" in str(e) or "(#200)" in str(e):
            notes["instagram_insights"] = "needs the instagram_manage_insights permission (Meta app → Permisos y funciones, then a new token)"
        else:   # one metric this media type doesn't support: ask one by one
            r = {"data": []}
            for mt in IG_METRICS:
                try: r["data"] += I.req("GET", f"{media_id}/insights", metric=mt).get("data", [])
                except RuntimeError: pass
        if notes.get("instagram_insights"):
            b = I.req("GET", media_id, fields="like_count,comments_count")
            return {"likes": b.get("like_count"), "comments": b.get("comments_count")}
    out = {}
    for d in r.get("data", []):
        v = (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
        out[d["name"]] = v
    if "ig_reels_avg_watch_time" in out: out["avg_watch_s"] = round((out.pop("ig_reels_avg_watch_time") or 0) / 1000, 2)
    if "saved" in out: out["saves"] = out.pop("saved")
    return out


# ---------------------------------------------------------------- collect
def posted_slugs(days=ACTIVE_DAYS):
    lim = now() - datetime.timedelta(days=days); out = []
    for e in schedule():
        s = state(e["slug"])
        if s.get("status") == "posted" and s.get("posted_at") and _parse(s["posted_at"]) >= lim: out.append(e["slug"])
    return out


def collect():
    m = load(); notes = m.setdefault("notes", {}); t = now()
    if m.get("backfilled_on") != t.date().isoformat():
        try: backfill(m)
        except Exception as e: print("backfill:", e)
    slugs = posted_slugs(); yt_ids = {}
    for slug in slugs:
        r = m["reels"].setdefault(slug, {}); r["features"] = features(slug); s = state(slug)
        for p in ("youtube", "instagram"):
            pid = (s.get(p) or {}).get("id") or (r.get(p) or {}).get("id")
            if pid: r.setdefault(p, {})["id"] = pid
        if r.get("youtube", {}).get("id"): yt_ids[r["youtube"]["id"]] = slug
    try: yt = youtube_numbers(list(yt_ids), notes)
    except Exception as e: yt = {}; notes["youtube"] = str(e)[:200]; print("youtube:", e)
    for vid, nums in yt.items():
        slug = yt_ids[vid]; r = m["reels"][slug]
        age = (t - _parse(r["features"]["posted_at"])).total_seconds() / 3600
        r["youtube"].setdefault("snapshots", []).append({"at": _iso(t), "age_h": round(age, 1), **nums})
    for slug in slugs:
        r = m["reels"][slug]; mid = r.get("instagram", {}).get("id")
        if not mid or not os.environ.get("IG_ACCESS_TOKEN", "").strip(): continue
        try: nums = instagram_numbers(mid, notes)
        except Exception as e: print("instagram:", slug, e); continue
        age = (t - _parse(r["features"]["posted_at"])).total_seconds() / 3600
        r["instagram"].setdefault("snapshots", []).append({"at": _iso(t), "age_h": round(age, 1), **nums})
    alerts = hits(m)
    save(m)
    print(f"collected {len(slugs)} reels · notes: {notes or 'none'}")
    if alerts and os.environ.get("TELEGRAM_BOT_TOKEN"):
        import bot, telegram as T
        for a in alerts: T.send(bot.chat_id(), a)
    return m


def at_age(snaps, key, h):
    """value of `key` at `h` hours after posting (interpolated between snapshots; None if not reached yet)"""
    pts = sorted((s["age_h"], s[key]) for s in snaps or [] if s.get(key) is not None)
    if not pts or pts[-1][0] < h * 0.9: return None
    for (a0, v0), (a1, v1) in zip(pts, pts[1:]):
        if a0 <= h <= a1: return v0 if a1 == a0 else round(v0 + (v1 - v0) * (h - a0) / (a1 - a0), 1)
    return pts[0][1] if h <= pts[0][0] else pts[-1][1]


def hits(m):
    """a reel at ~1 day with 3x the usual views (platform by platform) -> one alert"""
    out = []
    for p in ("youtube", "instagram"):
        base = [at_age(r.get(p, {}).get("snapshots"), "views", 24) for r in m["reels"].values()]
        base = [b for b in base if b]
        if len(base) < 4: continue
        med = statistics.median(base)
        for slug, r in m["reels"].items():
            v = at_age(r.get(p, {}).get("snapshots"), "views", 24)
            if v and med and v >= 3 * med and not r.get(p, {}).get("alerted"):
                r[p]["alerted"] = True
                out.append(f"🔥 <b>{r['features'].get('painting')}</b> is taking off on {p.capitalize()}: {int(v):,} views in 24 h, "
                           f"{v / med:.1f}× our usual ({int(med):,}). The next brief will look at why; a follow-up story while "
                           f"it's hot is worth considering (/idea …).")
    return out


# ---------------------------------------------------------------- backfill (reels posted by hand)
def _norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def backfill(m=None):
    """match reels posted by hand to their YouTube/Instagram ids (by title/caption); runs once a day inside collect"""
    import youtube as Y, instagram as I
    own = m is None; m = m or load(); found = 0
    posted = [e["slug"] for e in schedule() if state(e["slug"]).get("status") == "posted"]
    try:
        tok = Y.token(); H = {"Authorization": f"Bearer {tok}"}
        ch = Y.http("GET", f"{Y.API}/youtube/v3/channels?part=contentDetails&mine=true", H)
        up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        vids = Y.http("GET", f"{Y.API}/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={up}", H).get("items", [])
        for slug in posted:
            r = m["reels"].setdefault(slug, {"features": features(slug)})
            if r.get("youtube", {}).get("id"): continue
            want = _norm(story(slug).get("youtube_title"))[:40]
            for v in vids:
                if want and _norm(v["snippet"]["title"]).startswith(want[:30]):
                    r.setdefault("youtube", {})["id"] = v["snippet"]["resourceId"]["videoId"]; found += 1; break
    except Exception as e: print("youtube backfill:", str(e)[:200])
    try:
        media = I.req("GET", f"{I.uid()}/media", fields="id,caption,timestamp,media_type", limit=50).get("data", [])
        for slug in posted:
            r = m["reels"].setdefault(slug, {"features": features(slug)})
            if r.get("instagram", {}).get("id"): continue
            want = _norm(story(slug).get("caption"))[:40]
            for x in media:
                if want and _norm(x.get("caption"))[:40] == want:
                    r.setdefault("instagram", {})["id"] = x["id"]; found += 1; break
    except Exception as e: print("instagram backfill:", str(e)[:200])
    m["backfilled_on"] = now().date().isoformat()
    if own: save(m)
    print("backfilled ids:", found)


# ---------------------------------------------------------------- lab helpers
def pull(d):
    import release
    os.makedirs(os.path.join(d, "tiktok"), exist_ok=True); os.makedirs(os.path.join(d, "history"), exist_ok=True)
    m = load(); json.dump(m, open(os.path.join(d, "metrics.json"), "w"), indent=1, ensure_ascii=False)
    seen = set(m.get("tiktok_seen", []))
    for name in release.data_list("tiktok-"):
        if name not in seen:
            open(os.path.join(d, "tiktok", name), "wb").write(release.data_get(name))
    for name in sorted(release.data_list("brief-"))[-6:]:
        open(os.path.join(d, "history", name), "wb").write(release.data_get(name))
    print("pulled metrics for", len(m["reels"]), "reels;", len(os.listdir(os.path.join(d, "tiktok"))), "new TikTok screenshot(s)")


def push(d):
    m = json.load(open(os.path.join(d, "metrics.json")))
    m["tiktok_seen"] = sorted(set(m.get("tiktok_seen", [])) | set(os.listdir(os.path.join(d, "tiktok"))))
    save(m)


def tiktok_add(slug, nums, d):
    p = os.path.join(d, "metrics.json"); m = json.load(open(p))
    r = m["reels"].setdefault(slug, {"features": features(slug)})
    nums = json.loads(nums) if isinstance(nums, str) else nums
    posted = r["features"].get("posted_at") or features(slug).get("posted_at")
    at = nums.pop("at", None) or _iso(now())
    age = round((_parse(at) - _parse(posted)).total_seconds() / 3600, 1) if posted else None
    r.setdefault("tiktok", {}).setdefault("snapshots", []).append({"at": at, "age_h": age, **nums})
    json.dump(m, open(p, "w"), indent=1, ensure_ascii=False); print("tiktok", slug, nums)


def per_k(a, b): return round(1000 * a / b, 1) if a is not None and b else None


def table(d="lab"):
    """one row per reel: features + each platform's numbers at 24 h / 72 h / 7 d + per-1,000-view rates"""
    src = os.path.join(d, "metrics.json"); m = json.load(open(src)) if os.path.exists(src) else load()
    rows = []
    for slug, r in m["reels"].items():
        row = dict(r.get("features") or features(slug)); row.pop("experiment", None)
        exp = (r.get("features") or {}).get("experiment") or {}
        row["experiment"] = f"{exp.get('id')}:{exp.get('arm')}" if exp else ""
        for p in ("youtube", "instagram", "tiktok"):
            sn = r.get(p, {}).get("snapshots")
            for h in AGES: row[f"{p}_views_{h}h"] = at_age(sn, "views", h)
            last = (sn or [{}])[-1]
            for k in ("likes", "comments", "shares", "saves", "subs", "follows", "avg_view_pct", "avg_view_s", "avg_watch_s",
                      "watched_full_pct", "reach"):
                if last.get(k) is not None: row[f"{p}_{k}"] = last[k]
            v = last.get("views")
            row[f"{p}_age_h"] = last.get("age_h")
            row[f"{p}_shares_saves_per_1k"] = per_k((last.get("shares") or 0) + (last.get("saves") or 0), v) if v else None
            row[f"{p}_follows_per_1k"] = per_k(last.get("subs") if p == "youtube" else last.get("follows"), v)
            row[f"{p}_comments_per_1k"] = per_k(last.get("comments"), v)
        rows.append(row)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("slug", "posted_at", "slot", "hook_type"), k))
    out = os.path.join(d, "table.csv"); os.makedirs(d, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in sorted(rows, key=lambda r: r.get("posted_at") or "")]
    print(f"{out}: {len(rows)} reels × {len(keys)} columns"); return out


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "collect": collect()
    elif c == "backfill": backfill()
    elif c == "pull": pull(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "push": push(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "table": table(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "tiktok-add": tiktok_add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "lab")
    else: raise SystemExit(__doc__)
