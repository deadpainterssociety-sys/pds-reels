"""Market study helper, run on GitHub Actions by research.yml: public YouTube numbers for art-history channels (read-only
Data API calls with the channel's youtube.readonly token), their thumbnails, topic-demand searches, and Wikimedia
Commons downloads for long-form videos. Nothing here posts or changes anything.

usage: python automation/yt_research.py run research/request.json <out_dir>
request.json keys (all optional):
  seeds:      [{"handle": "@x"} | {"id": "UC..."}, + "name", "group"]   channels to study in depth
  searches:   [{"q": "...", "duration": "medium|long|short|any", "after": "2025-01-01", "lang": "en", "tag": "discover"}]
  channel_searches: ["art history", ...]                               find channels by name/description
  max_units:  hard cap on API quota spent by this run (search = 100 units, everything else 1)
  commons:    [{"title": "File:....jpg", "name": "saturn", "width": 3840}]   downloaded into <out>/commons/
Quota matters: the channel's daily quota is 10,000 units and each upload costs 1,600, so the cap stays well below.
"""
import datetime, json, os, re, statistics, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

UNITS = {"spent": 0, "cap": 4000}
H = {}
NOW = datetime.datetime.now(datetime.timezone.utc)
ART = re.compile(r"(?i)paint|art\b|artist|arte\b|museum|museo|masterpiece|renaissance|baroque|gallery|sculpt|fresco|canvas|"
                 r"van gogh|da vinci|leonardo|caravaggio|goya|bosch|rembrandt|vermeer|monet|picasso|dal[ií]|klimt|michelangelo|"
                 r"raphael|botticelli|bruegel|velázquez|velazquez|frida|munch|cuadro|pintor|pintura|louvre|prado|mona lisa")


class Budget(Exception): pass


def api(path, cost=1, **q):
    import youtube as Y
    if UNITS["spent"] + cost > UNITS["cap"]: raise Budget(path)
    q = {k: v for k, v in q.items() if v not in (None, "", "any")}
    url = f"{Y.API}/youtube/v3/{path}?" + urllib.parse.urlencode(q)
    for i in range(3):
        try:
            r = Y.http("GET", url, H); UNITS["spent"] += cost; return r
        except RuntimeError as e:
            if "quotaExceeded" in str(e) or "HTTP 404" in str(e) or i == 2: raise
            time.sleep(2 + 3 * i)


def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m: return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def age_days(v): return (NOW - datetime.datetime.fromisoformat(v["published"].replace("Z", "+00:00"))).days


SPONSOR = re.compile(r"(?i)sponsor|use code|promo code|brilliant\.org|squarespace|nordvpn|audible|ground ?news|skillshare|"
                     r"curiositystream|nebula|raid|honey|surfshark|blinkist|magellan|odoo|incogni|aura\.com|masterclass")


def videos(ids):
    out = []
    ids = list(dict.fromkeys(ids))
    for k in range(0, len(ids), 50):
        r = api("videos", part="snippet,statistics,contentDetails", id=",".join(ids[k:k + 50]))
        for v in r.get("items", []):
            sn, st, cd = v["snippet"], v.get("statistics", {}), v["contentDetails"]
            desc = sn.get("description", "")
            out.append({"id": v["id"], "channel": sn["channelId"], "ctitle": sn.get("channelTitle"), "title": sn["title"],
                        "published": sn["publishedAt"], "dur": dur(cd.get("duration")), "views": int(st.get("viewCount", 0) or 0),
                        "likes": int(st.get("likeCount", 0) or 0), "comments": int(st.get("commentCount", 0) or 0),
                        "tags": (sn.get("tags") or [])[:12], "lang": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
                        "chapters": bool(re.search(r"(?m)^\s*\(?0?0:00", desc)), "desc_len": len(desc), "desc_head": desc[:300],
                        "sponsor": bool(SPONSOR.search(desc)), "patreon": "patreon.com" in desc.lower(),
                        "shop": bool(re.search(r"(?i)\bshop\b|\bstore\b|merch|\bprints?\b", desc)),
                        "thumb": (sn.get("thumbnails", {}).get("medium") or {}).get("url"), "cat": sn.get("categoryId"),
                        "live": sn.get("liveBroadcastContent")})
    return out


def playlist(pl, pages):
    ids, tok, total = [], None, None
    for _ in range(pages):
        try: r = api("playlistItems", part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok)
        except RuntimeError as e:
            if "404" in str(e) or "playlistNotFound" in str(e): return ids, None
            raise
        total = r.get("pageInfo", {}).get("totalResults", total)
        ids += [x["contentDetails"]["videoId"] for x in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok: break
    return ids, total


def med(xs): return statistics.median(xs) if xs else None


def channel_info(items):
    out = []
    for it in items:
        sn, st = it["snippet"], it.get("statistics", {})
        out.append({"id": it["id"], "title": sn["title"], "handle": sn.get("customUrl"), "created": sn.get("publishedAt"),
                    "country": sn.get("country"), "desc": sn.get("description", "")[:400],
                    "subs": int(st.get("subscriberCount", 0) or 0), "views": int(st.get("viewCount", 0) or 0),
                    "videos": int(st.get("videoCount", 0) or 0), "hidden_subs": st.get("hiddenSubscriberCount"),
                    "uploads": it.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads"),
                    "topics": [t.rsplit("/", 1)[-1] for t in it.get("topicDetails", {}).get("topicCategories", [])],
                    "keywords": it.get("brandingSettings", {}).get("channel", {}).get("keywords", "")[:300]})
    return out


def deep(ch, seed):
    """Long-form uploads (UULF playlist = long videos only), Shorts count (UUSH), and the numbers we compare."""
    up = ch["uploads"] or ("UU" + ch["id"][2:])
    big = ch["videos"] > 1500
    long_ids, n_long = playlist("UULF" + ch["id"][2:], 3 if big else 8)
    if not long_ids and n_long is None:   # hidden playlists unavailable: plain uploads, split by duration below
        long_ids, n_long = playlist(up, 3 if big else 8)
    sh_ids, n_short = playlist("UUSH" + ch["id"][2:], 1)
    longs = [v for v in videos(long_ids) if v["dur"] > 60 and v["live"] in (None, "none")]
    shorts = videos(sh_ids[:50])
    longs.sort(key=lambda v: v["published"], reverse=True)
    last = longs[:50]
    m50 = med([v["views"] for v in last])
    for v in longs: v["ratio"] = round(v["views"] / m50, 2) if m50 else None
    recent = [v["views"] for v in longs if 30 <= age_days(v) <= 180]
    older = [v["views"] for v in longs if 180 < age_days(v) <= 540]
    gaps = [(datetime.datetime.fromisoformat(a["published"][:19]) - datetime.datetime.fromisoformat(b["published"][:19])).days
            for a, b in zip(longs[:21], longs[1:21])]
    s = {**ch, **{k: seed.get(k) for k in ("group", "note") if seed.get(k)},
         "n_long": n_long, "n_short": n_short, "sampled_long": len(longs),
         "median_views_last50": m50, "median_views_30_180d": med(recent), "median_views_180_540d": med(older),
         "trend": round(med(recent) / med(older), 2) if recent and older and med(older) else None,
         "uploads_90d": sum(1 for v in longs if age_days(v) <= 90), "shorts_90d": sum(1 for v in shorts if age_days(v) <= 90),
         "median_gap_days": med(gaps), "median_dur_s_last20": med([v["dur"] for v in longs[:20]]),
         "median_short_views": med([v["views"] for v in shorts[:30]]),
         "last_upload": longs[0]["published"] if longs else None,
         "subs_per_1k_views": round(ch["subs"] / ch["views"] * 1000, 2) if ch["views"] else None,
         "sponsor_share_last20": round(sum(v["sponsor"] for v in longs[:20]) / max(1, len(longs[:20])), 2),
         "chapters_share_last20": round(sum(v["chapters"] for v in longs[:20]) / max(1, len(longs[:20])), 2)}
    top = sorted(longs, key=lambda v: -v["views"])[:25]
    keep = {v["id"]: v for v in longs[:200] + top}
    return s, list(keep.values()), shorts[:30]


def discover(searches):
    hits = []
    for s in searches:
        try:
            r = api("search", cost=100, part="snippet", type="video", q=s["q"], order=s.get("order", "viewCount"), maxResults=50,
                    publishedAfter=(s["after"] + "T00:00:00Z") if s.get("after") else None, relevanceLanguage=s.get("lang"),
                    videoDuration=s.get("duration"), regionCode=s.get("region"))
        except Budget: print("budget reached before search:", s["q"]); break
        for it in r.get("items", []):
            hits.append({"q": s["q"], "tag": s.get("tag", "discover"), "duration_filter": s.get("duration"), "after": s.get("after"),
                         "id": it["id"]["videoId"], "channel": it["snippet"]["channelId"]})
        print(f"search '{s['q']}' ({s.get('duration')}, after {s.get('after')}): {len(r.get('items', []))} results", flush=True)
    vs = {v["id"]: v for v in videos([h["id"] for h in hits])}
    for h in hits: h.update(vs.get(h["id"], {}))
    return hits


def find_channels(queries):
    ids = []
    for q in queries:
        try: r = api("search", cost=100, part="snippet", type="channel", q=q, maxResults=50)
        except Budget: break
        ids += [it["snippet"]["channelId"] for it in r.get("items", [])]
    out = []
    ids = list(dict.fromkeys(ids))
    for k in range(0, len(ids), 50):
        out += channel_info(api("channels", part="snippet,statistics,contentDetails,brandingSettings,topicDetails",
                                id=",".join(ids[k:k + 50])).get("items", []))
    return out


def thumbs(vids, d):
    os.makedirs(d, exist_ok=True); n = 0
    for v in vids:
        p = os.path.join(d, v["id"] + ".jpg")
        if os.path.exists(p) or not v.get("thumb"): continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(v["thumb"], headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
            open(p, "wb").write(data); n += 1
        except Exception as e: print("thumb", v["id"], e)
    print("thumbnails:", n)


def commons(items, d, deadline):
    import importlib.util
    spec = importlib.util.spec_from_file_location("commons", os.path.join(os.path.dirname(__file__), "..", "pipeline", "commons.py"))
    C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
    os.makedirs(d, exist_ok=True); meta = {}
    for it in items:
        if time.time() > deadline: meta[it["name"]] = {"error": "time limit", "requested": it.get("queries") or it.get("search") or it.get("title")}; continue
        try:
            if it.get("search") or it.get("queries"):   # best match: biggest JPEG/PNG whose title has every "must" word,
                cands, seen = [], set()                    # none of the "exclude" words, and an aspect ratio (w/h) in range
                for q in it.get("queries") or [it["search"]]:
                    r = C.api(action="query", generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=20, prop="imageinfo", iiprop="size|mime")
                    pages = sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
                    lo, hi = it.get("aspect", [0, 99])
                    for p in pages:
                        if "imageinfo" not in p or p["title"] in seen: continue
                        ii = p["imageinfo"][0]; t = p["title"].lower(); seen.add(p["title"])
                        if ii.get("mime") not in ("image/jpeg", "image/png"): continue
                        if not all(w.lower() in t for w in it.get("must", [])) or any(w.lower() in t for w in it.get("exclude", [])): continue
                        if not lo <= ii["width"] / max(1, ii["height"]) <= hi: continue
                        cands.append((p["title"], ii["width"], ii["height"]))
                    time.sleep(1)
                    if cands: break
                big = [c for c in cands if c[1] >= it.get("min_w", 1200)] or cands
                if not big: raise RuntimeError(f"no match for {it.get('queries') or it['search']}")
                it = {**it, "title": max(big[:6], key=lambda c: c[1] * c[2])[0], "alternatives": cands[:8]}
            inf = C.info(it["title"]); time.sleep(1)
            w = it.get("width", 3840); data = None
            tries = [C.thumb_url(inf["url"], x) for x in C.STD_WIDTHS if x <= w and x < inf["w"]] if inf["w"] > w else [inf["url"]]
            tries += [inf["url"]] if inf["url"] not in tries else []
            for u in tries:
                try: data = C.fetch(u, tries=6); break
                except Exception as e: print("  retry", it["name"], str(e)[:80]); time.sleep(5)
            if data:
                ext = ".png" if data[:4] == b"\x89PNG" else ".jpg"
                open(os.path.join(d, it["name"] + ext), "wb").write(data)
                meta[it["name"]] = {**inf, "requested": it.get("queries") or it.get("search") or it["title"], "alternatives": it.get("alternatives"), "bytes": len(data)}
                print(f"commons {it['name']}: {inf['w']}x{inf['h']} {inf['license']} ({len(data) // 1024} KB)", flush=True)
            time.sleep(2)
        except Exception as e:
            meta[it["name"]] = {"error": str(e)[:300], "requested": it.get("queries") or it.get("search") or it.get("title")}; print("commons FAIL", it["name"], e)
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1, ensure_ascii=False)


def run(req_path, out):
    import youtube as Y
    req = json.load(open(req_path)); os.makedirs(out, exist_ok=True)
    UNITS["cap"] = int(req.get("max_units", UNITS["cap"]))
    try:
        if req.get("seeds") or req.get("searches") or req.get("channel_searches"): youtube_part(req, out)
    finally:
        if req.get("commons"): commons(req["commons"], os.path.join(out, "commons"), time.time() + 60 * req.get("commons_minutes", 18))


def youtube_part(req, out):
    import youtube as Y
    H["Authorization"] = f"Bearer {Y.token()}"
    log = {"started": NOW.isoformat(), "errors": []}
    # 1) seeds
    seeds = req.get("seeds", [])
    chans = {}
    for sd in seeds:
        try:
            q = {"id": sd["id"]} if sd.get("id") else {"forHandle": sd["handle"]}
            items = api("channels", part="snippet,statistics,contentDetails,brandingSettings,topicDetails", **q).get("items", [])
            if not items: log["errors"].append(f"not found: {sd}"); continue
            c = channel_info(items)[0]; chans[c["id"]] = (c, sd)
        except Budget: break
        except Exception as e: log["errors"].append(f"{sd}: {str(e)[:200]}")
    # 2) discovery (videos) and channel search
    hits = discover(req.get("searches", []))
    json.dump(hits, open(os.path.join(out, "discovery.json"), "w"), ensure_ascii=False)
    found = find_channels(req.get("channel_searches", []))
    json.dump(found, open(os.path.join(out, "channel_search.json"), "w"), ensure_ascii=False)
    # channels worth a deep look: art-related, from discovery (sum of views of their hits) or the channel search (subs)
    score = {}
    for h in hits:
        if h.get("views") and h.get("tag", "discover") == "discover" and ART.search(h.get("title", "")):
            score[h["channel"]] = score.get(h["channel"], 0) + h["views"]
    extra = [cid for cid, _ in sorted(score.items(), key=lambda x: -x[1]) if cid not in chans][: int(req.get("max_discovered", 30))]
    extra += [c["id"] for c in sorted(found, key=lambda c: -c["subs"]) if c["subs"] >= 20000 and c["id"] not in chans and
              c["id"] not in extra and ART.search(c["title"] + " " + c["desc"] + " " + c["keywords"])][: int(req.get("max_found", 15))]
    for k in range(0, len(extra), 50):
        try:
            for c in channel_info(api("channels", part="snippet,statistics,contentDetails,brandingSettings,topicDetails",
                                      id=",".join(extra[k:k + 50])).get("items", [])):
                chans[c["id"]] = (c, {"group": "discovered"})
        except Budget: break
    # 3) deep dives
    summary, allv, shorts = [], [], []
    for cid, (c, sd) in chans.items():
        try:
            s, vs, sh = deep(c, sd); summary.append(s); allv += vs; shorts += sh
            print(f"{c['title'][:40]:40} subs {c['subs']:>9,}  long {s['n_long']}  median50 {s['median_views_last50']}  "
                  f"trend {s['trend']}  units {UNITS['spent']}", flush=True)
        except Budget: print("budget reached at", c["title"]); summary.append({**c, "group": sd.get("group"), "skipped": "budget"}); break
        except Exception as e: log["errors"].append(f"{c['title']}: {str(e)[:200]}")
    json.dump(summary, open(os.path.join(out, "channels.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(allv, open(os.path.join(out, "videos.json"), "w"), ensure_ascii=False)
    json.dump(shorts, open(os.path.join(out, "shorts.json"), "w"), ensure_ascii=False)
    # 4) thumbnails: each channel's 10 most viewed + 4 latest long videos, the biggest outliers, the discovery hits
    pick = []
    by = {}
    for v in allv: by.setdefault(v["channel"], []).append(v)
    for cid, vs in by.items():
        pick += sorted(vs, key=lambda v: -v["views"])[:10] + sorted(vs, key=lambda v: v["published"], reverse=True)[:4]
    pick += sorted([v for v in allv if (v.get("ratio") or 0) >= 3 and v["views"] >= 50000], key=lambda v: -(v["ratio"] or 0))[:150]
    pick += sorted([h for h in hits if h.get("views")], key=lambda h: -h["views"])[:250]
    thumbs(pick, os.path.join(out, "thumbs"))
    log.update(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), units=UNITS["spent"], channels=len(summary),
               videos=len(allv), hits=len(hits))
    json.dump(log, open(os.path.join(out, "log.json"), "w"), indent=1)
    print(json.dumps(log, indent=1))


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    else: raise SystemExit(__doc__)
