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
average view duration, shares, subscribers gained, engaged views, watch time; scope yt-analytics.readonly, ~1-2 days
late). Long videos (state.json youtube_id + publish_at, 60 days) are collected too, in m["long"], with their retention
curve and traffic sources every run. Once a day: each Short's traffic sources, the channel's daily totals (Shorts vs
long videos), and the audience (age, gender, country, last 28 days). Impressions and impressions CTR come from the
Reporting API's daily "reach" reports (jobs created once; the first reports arrive ~2 days later), in m["reach"].
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
            "posted_hour": pt.hour if pt else None, "manual": bool(s.get("manual")), "format": st.get("format", "reel")}


# ---------------------------------------------------------------- YouTube
def youtube_numbers(ids, notes):
    import youtube as Y
    if not ids or not os.environ.get("YT_REFRESH_TOKEN", "").strip(): return {}
    tok = Y.token(); H = {"Authorization": f"Bearer {tok}"}; out = {i: {} for i in ids}
    global _H; _H = H
    for k in range(0, len(ids), 50):
        r = Y.http("GET", f"{Y.API}/youtube/v3/videos?part=statistics&id={','.join(ids[k:k + 50])}", H)
        for it in r.get("items", []):
            st = it.get("statistics", {})
            out[it["id"]].update(views=int(st.get("viewCount", 0)), likes=int(st.get("likeCount", 0)), comments=int(st.get("commentCount", 0)))
    base = "views,averageViewPercentage,averageViewDuration,shares,subscribersGained,likes,comments"
    try:
        try: r = analytics(H, "video", base + ",engagedViews,estimatedMinutesWatched", "video==" + ",".join(ids[:200]), maxResults=200)
        except RuntimeError as e:
            if "400" not in str(e): raise
            notes["youtube_engaged"] = str(e)[:200]; r = analytics(H, "video", base, "video==" + ",".join(ids[:200]), maxResults=200)
        notes.pop("youtube_analytics", None)
        for d in r:
            v = out.setdefault(d["video"], {})
            v.update(avg_view_pct=d.get("averageViewPercentage"), avg_view_s=d.get("averageViewDuration"), shares=d.get("shares"),
                     subs=d.get("subscribersGained"), analytics_views=d.get("views"), engaged_views=d.get("engagedViews"),
                     watch_min=d.get("estimatedMinutesWatched"))
            if d.get("engagedViews") is not None and d.get("views"):   # ≈ Studio's "stayed to watch" for Shorts
                v["engaged_pct"] = round(100 * d["engagedViews"] / d["views"], 1)
    except RuntimeError as e:
        notes["youtube_analytics"] = ("needs the yt-analytics.readonly permission (SETUP: redo the OAuth Playground step with it)"
                                      if ("403" in str(e) or "401" in str(e)) else str(e)[:200])
    return out


_H = None
ANA = os.environ.get("YT_ANALYTICS_API", "https://youtubeanalytics.googleapis.com").rstrip("/")
REP = os.environ.get("YT_REPORTING_API", "https://youtubereporting.googleapis.com").rstrip("/")
REACH_JOBS = ("channel_reach_basic_a1", "channel_reach_combined_a1")


def analytics(H, dimensions, metrics, filters=None, start="2026-10-01", **extra):
    """one YouTube Analytics report -> list of row dicts"""
    import youtube as Y
    q = {"ids": "channel==MINE", "startDate": start, "endDate": (now() + datetime.timedelta(days=1)).date().isoformat(),
         "metrics": metrics, **({"dimensions": dimensions} if dimensions else {}), **({"filters": filters} if filters else {}), **extra}
    r = Y.http("GET", f"{ANA}/v2/reports?{urllib.parse.urlencode(q)}", H)
    cols = [c["name"] for c in r.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in r.get("rows", [])]


def retention(H, vid):
    """the audience retention curve: 100 points (share of the video elapsed -> share of viewers still watching, and
    YouTube's comparison with videos of similar length: relative 0.5 = typical)"""
    rows = analytics(H, "elapsedVideoTimeRatio", "audienceWatchRatio,relativeRetentionPerformance", f"video=={vid}")
    return [[round(d["elapsedVideoTimeRatio"], 2), round(d["audienceWatchRatio"], 3), round(d.get("relativeRetentionPerformance") or 0, 3)]
            for d in rows]


def traffic(H, vid):
    """views and watch minutes by traffic source (SHORTS feed, browse features, suggested, search, external…)"""
    rows = analytics(H, "insightTrafficSourceType", "views,estimatedMinutesWatched", f"video=={vid}")
    return {d["insightTrafficSourceType"]: {"views": d["views"], "minutes": d.get("estimatedMinutesWatched")} for d in rows}


def channel_daily(H, notes):
    """the channel's daily totals for the last 35 days, split Shorts / long videos when YouTube allows it"""
    start = (now() - datetime.timedelta(days=35)).date().isoformat(); met = "views,estimatedMinutesWatched,subscribersGained,subscribersLost"
    try: rows = analytics(H, "day,creatorContentType", met, start=start); split = True
    except RuntimeError as e: notes["channel_split"] = str(e)[:160]; rows = analytics(H, "day", met, start=start); split = False
    days = {}
    for d in rows:
        k = (d.get("creatorContentType") or "ALL").lower() if split else "all"
        days.setdefault(d["day"], {})[k] = {"views": d["views"], "minutes": d["estimatedMinutesWatched"],
                                            "subs": d["subscribersGained"] - d["subscribersLost"]}
    return days


def audience(H):
    """who watches (last 28 days): age x gender share of viewers, and the top countries by views"""
    start = (now() - datetime.timedelta(days=28)).date().isoformat()
    ag = analytics(H, "ageGroup,gender", "viewerPercentage", start=start)
    ct = analytics(H, "country", "views,estimatedMinutesWatched", start=start, sort="-views", maxResults=15)
    age = {}
    for d in ag: age[d["ageGroup"].replace("age", "")] = round(age.get(d["ageGroup"].replace("age", ""), 0) + d["viewerPercentage"], 1)
    gender = {}
    for d in ag: gender[d["gender"]] = round(gender.get(d["gender"], 0) + d["viewerPercentage"], 1)
    return {"days": 28, "age_pct": age, "gender_pct": gender, "countries": {d["country"]: d["views"] for d in ct}}


def _raw(url, H):
    import gzip, urllib.request
    r = urllib.request.urlopen(urllib.request.Request(url, headers={**H, "Accept-Encoding": "gzip"}), timeout=120); b = r.read()
    return (gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" or b[:2] == b"\x1f\x8b" else b).decode()


def reach(m, H, notes):
    """impressions and impressions CTR per video and day (Reporting API). Creates the two reach jobs the first time;
    then downloads every new daily report. m["reach"][video][date] = {"impr", "ctr"} (ctr in %, as Studio shows it);
    m["reach_src"][video][date][traffic source] = {"impr", "ctr"}"""
    import youtube as Y
    st = m.setdefault("reach_state", {"jobs": {}, "seen": []})
    try:
        if len(st["jobs"]) < len(REACH_JOBS):
            have = {j["reportTypeId"]: j["id"] for j in Y.http("GET", f"{REP}/v1/jobs", H).get("jobs", [])}
            for rt in REACH_JOBS:
                if rt not in have:
                    j = Y.http("POST", f"{REP}/v1/jobs", {**H, "Content-Type": "application/json"},
                               json.dumps({"reportTypeId": rt, "name": f"dps {rt}"}).encode()); have[rt] = j["id"]
                    print("reach: created job", rt)
            st["jobs"] = {rt: have[rt] for rt in REACH_JOBS}; st.setdefault("since", now().date().isoformat())
        seen = set(st["seen"]); new = 0
        for rt, jid in st["jobs"].items():
            reps = Y.http("GET", f"{REP}/v1/jobs/{jid}/reports", H).get("reports", [])
            for rp in sorted(reps, key=lambda x: x.get("startTime", "")):
                if rp["id"] in seen: continue
                rows = list(csv.DictReader(io.StringIO(_raw(rp["downloadUrl"], H))))
                agg = {}
                for x in rows:
                    imp = float(x.get("video_thumbnail_impressions") or 0); ctr = float(x.get("video_thumbnail_impressions_ctr") or 0)
                    key = (x["video_id"], x["date"], x.get("traffic_source_type") if rt.endswith("combined_a1") else None)
                    a = agg.setdefault(key, [0.0, 0.0]); a[0] += imp; a[1] += imp * ctr
                for (vid, day, src), (imp, clicks) in agg.items():
                    val = {"impr": int(imp), "ctr": round(100 * clicks / imp, 2) if imp else None}
                    day = f"{day[:4]}-{day[4:6]}-{day[6:]}" if len(day) == 8 else day
                    if src is None: m.setdefault("reach", {}).setdefault(vid, {})[day] = val
                    else: m.setdefault("reach_src", {}).setdefault(vid, {}).setdefault(day, {})[TRAFFIC.get(src, src)] = val
                seen.add(rp["id"]); new += 1
        st["seen"] = sorted(seen)[-400:]; notes.pop("youtube_reach", None)
        print(f"reach: {new} new report(s)")
    except RuntimeError as e:
        notes["youtube_reach"] = str(e)[:200]; print("reach:", str(e)[:200])


TRAFFIC = {"0": "direct", "1": "advertising", "3": "browse", "4": "channel", "5": "search", "7": "suggested",
           "8": "other_youtube", "9": "external", "11": "cards", "14": "playlists", "17": "notifications",
           "18": "playlist_pages", "19": "claimed_content", "20": "end_screen", "23": "stories", "24": "shorts_feed",
           "25": "product_pages", "26": "hashtag_pages", "27": "sound_pages", "28": "live_redirect", "29": "podcasts",
           "30": "remix", "31": "vertical_live", "32": "related_video"}   # Reporting API numeric traffic_source_type codes


def long_videos(days=60):
    """the long videos already public: slug -> (video id, publish time)"""
    import glob
    out = {}; t = now()
    for p in sorted(glob.glob(os.path.join(ROOT, "stories", "*", "state.json"))):
        slug = os.path.basename(os.path.dirname(p)); s = state(slug)
        vid, pa = s.get("youtube_id"), s.get("publish_at")
        if vid and pa and t - datetime.timedelta(days=days) <= _parse(pa) <= t: out[slug] = (vid, pa)
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
    longs = long_videos(); long_ids = {vid: slug for slug, (vid, _) in longs.items()}
    try: yt = youtube_numbers(list(yt_ids) + list(long_ids), notes)
    except Exception as e: yt = {}; notes["youtube"] = str(e)[:200]; print("youtube:", e)
    for vid, nums in yt.items():
        if vid in long_ids:
            slug = long_ids[vid]; L = m.setdefault("long", {}).setdefault(slug, {"youtube": {"id": vid}})
            st_ = story(slug); L["features"] = {"slug": slug, "painting": st_.get("meta", {}).get("painting"), "painter": st_.get("meta", {}).get("painter"),
                                                "titles": st_.get("youtube", {}).get("titles"), "posted_at": longs[slug][1], "format": "long"}
            age = (t - _parse(longs[slug][1])).total_seconds() / 3600
            L["youtube"].setdefault("snapshots", []).append({"at": _iso(t), "age_h": round(age, 1), **nums})
            continue
        slug = yt_ids[vid]; r = m["reels"][slug]
        age = (t - _parse(r["features"]["posted_at"])).total_seconds() / 3600
        r["youtube"].setdefault("snapshots", []).append({"at": _iso(t), "age_h": round(age, 1), **nums})
    if _H:
        daily = m.get("daily_on") != t.date().isoformat()
        for slug, (vid, _) in longs.items():   # every run: long videos are few and their first days matter
            L = m["long"].get(slug)
            if not L: continue
            try: L["retention"] = retention(_H, vid); L["traffic"] = traffic(_H, vid); L["detail_at"] = _iso(t)
            except RuntimeError as e: print("long detail:", slug, str(e)[:160])
        if daily:
            for vid, slug in yt_ids.items():
                try: m["reels"][slug]["youtube"]["traffic"] = traffic(_H, vid)
                except RuntimeError as e: print("traffic:", slug, str(e)[:160])
            try: m["channel"] = {"daily": channel_daily(_H, notes), "audience": audience(_H), "at": _iso(t)}
            except RuntimeError as e: notes["youtube_channel"] = str(e)[:200]; print("channel:", str(e)[:200])
            reach(m, _H, notes)
            m["daily_on"] = t.date().isoformat()
    for slug in slugs:   # Instagram numbers only when config.json "learning_platforms" lists it (6 Nov 2026: YouTube decides)
        r = m["reels"][slug]; mid = r.get("instagram", {}).get("id")
        if "instagram" not in CONFIG.get("learning_platforms", ["youtube"]): notes.pop("instagram_insights", None); break
        if not mid or not os.environ.get("IG_ACCESS_TOKEN", "").strip(): continue
        try: nums = instagram_numbers(mid, notes)
        except Exception as e: print("instagram:", slug, e); continue
        age = (t - _parse(r["features"]["posted_at"])).total_seconds() / 3600
        r["instagram"].setdefault("snapshots", []).append({"at": _iso(t), "age_h": round(age, 1), **nums})
    alerts = hits(m)
    save(m)
    print(f"collected {len(slugs)} reels + {len(longs)} long videos · notes: {notes or 'none'}")
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
                      "watched_full_pct", "reach", "engaged_pct", "watch_min"):
                if last.get(k) is not None: row[f"{p}_{k}"] = last[k]
            v = last.get("views")
            row[f"{p}_age_h"] = last.get("age_h")
            row[f"{p}_shares_saves_per_1k"] = per_k((last.get("shares") or 0) + (last.get("saves") or 0), v) if v else None
            row[f"{p}_follows_per_1k"] = per_k(last.get("subs") if p == "youtube" else last.get("follows"), v)
            row[f"{p}_comments_per_1k"] = per_k(last.get("comments"), v)
        yid = r.get("youtube", {}).get("id")
        row.update(reach_cols(m, yid, "youtube")); row.update(traffic_cols(r.get("youtube", {}).get("traffic"), "youtube"))
        rows.append(row)
    long_table(m, d)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("slug", "posted_at", "slot", "hook_type"), k))
    out = os.path.join(d, "table.csv"); os.makedirs(d, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in sorted(rows, key=lambda r: r.get("posted_at") or "")]
    print(f"{out}: {len(rows)} reels × {len(keys)} columns"); return out


def reach_cols(m, vid, p):
    """total impressions and impressions CTR (impression-weighted) for one video, and the first 2 days' numbers"""
    days = (m.get("reach") or {}).get(vid) or {}
    if not days: return {}
    tot = sum(v["impr"] for v in days.values()); clicks = sum(v["impr"] * (v["ctr"] or 0) / 100 for v in days.values())
    first = sorted(days)[:2]; f_imp = sum(days[k]["impr"] for k in first); f_clk = sum(days[k]["impr"] * (days[k]["ctr"] or 0) / 100 for k in first)
    return {f"{p}_impressions": tot, f"{p}_ctr_pct": round(100 * clicks / tot, 2) if tot else None,
            f"{p}_impressions_2d": f_imp, f"{p}_ctr_2d_pct": round(100 * f_clk / f_imp, 2) if f_imp else None}


def traffic_cols(tr, p):
    """share of views by traffic source, in %"""
    if not tr: return {}
    tot = sum(v["views"] for v in tr.values()) or 1
    return {f"{p}_src_{k.lower()}_pct": round(100 * v["views"] / tot, 1) for k, v in tr.items()}


def long_table(m, d):
    """<d>/long.csv: one row per long video: views at 24 h / 72 h / 7 d / 28 d, impressions + CTR, retention at 30 s and
    at 25/50/75 %, average % viewed, subscribers per 1,000 views, traffic sources"""
    rows = []
    for slug, L in (m.get("long") or {}).items():
        sn = L.get("youtube", {}).get("snapshots"); last = (sn or [{}])[-1]; f = L.get("features", {})
        row = {"slug": slug, "painting": f.get("painting"), "title_a": (f.get("titles") or [""])[0], "posted_at": f.get("posted_at"),
               "age_h": last.get("age_h")}
        for h in (24, 72, 168, 672): row[f"views_{h}h"] = at_age(sn, "views", h)
        for k in ("views", "likes", "comments", "avg_view_pct", "avg_view_s", "watch_min", "subs", "shares"): row[k] = last.get(k)
        row["subs_per_1k"] = per_k(last.get("subs"), last.get("views"))
        row.update(reach_cols(m, L.get("youtube", {}).get("id"), "yt"))
        ret = L.get("retention") or []
        for frac in (0.25, 0.5, 0.75):
            pt = min(ret, key=lambda x: abs(x[0] - frac)) if ret else None
            row[f"still_watching_{int(frac * 100)}pct"] = round(100 * pt[1], 1) if pt else None
        if ret and last.get("avg_view_s") and last.get("avg_view_pct"):   # video length from YouTube's own two averages
            secs = last["avg_view_s"] / (last["avg_view_pct"] / 100); pt = min(ret, key=lambda x: abs(x[0] - 30 / secs))
            row["still_watching_30s"] = round(100 * pt[1], 1)
        row.update(traffic_cols(L.get("traffic"), "yt"))
        rows.append(row)
    if not rows: return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(os.path.join(d, "long.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in sorted(rows, key=lambda r: r.get("posted_at") or "")]
    print(f"{d}/long.csv: {len(rows)} long videos")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "collect": collect()
    elif c == "backfill": backfill()
    elif c == "pull": pull(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "push": push(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "table": table(sys.argv[2] if len(sys.argv) > 2 else "lab")
    elif c == "tiktok-add": tiktok_add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "lab")
    else: raise SystemExit(__doc__)
