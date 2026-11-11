"""Topic waves: paintings that just went viral for some art channel, in any language. A topic that breaks out for one
channel keeps breaking out for others for months (Isle of the Dead + Hitler, 2024-2026: Inspiraggio 295k, Velum 733k,
Secessio 1.13M, a Russian channel 974k...), so the best next long video is often a wave we can join with a sharper
angle. Runs every other Monday before the lab brief (lab.yml); Claude reads lab/waves/waves.json (LAB.md, "Topic waves").

usage: python automation/waves.py collect <out_dir>     (needs the YouTube secrets; ~1,500 of the 10,000 daily units)
"""
import datetime, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

QUERIES = [  # long-form art storytelling, several languages; YouTube search ranks by views within the window
    ("this painting", "en"), ("painting history dark mystery", "en"), ("art history painting story", "en"),
    ("esta pintura historia", "es"), ("este cuadro", "es"), ("esta pintura história", "pt"),
    ("картина история", "ru"), ("ce tableau histoire", "fr"), ("dieses Gemälde Geschichte", "de"),
    ("questo dipinto storia", "it"), ("絵画 怖い", "ja"),
]


def collect(out, days=60):
    import yt_research as R
    after = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    req = {"max_units": 2200, "max_discovered": 40, "max_found": 0,
           "searches": [{"q": q, "lang": lang, "after": after, "duration": dur, "tag": "discover"}
                        for q, lang in QUERIES for dur in (("medium",) if lang != "en" else ("medium", "long"))]}
    os.makedirs(out, exist_ok=True); json.dump(req, open(os.path.join(out, "request.json"), "w"), indent=1)
    R.youtube_part(req, out)
    hits = json.load(open(os.path.join(out, "discovery.json")))
    chans = {c["id"]: c for c in json.load(open(os.path.join(out, "channels.json")))}
    vids = {v["id"]: v for v in json.load(open(os.path.join(out, "videos.json")))}
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days + 30)).isoformat()
    waves = {}
    for h in hits:
        if not h.get("views") or h.get("published", "") < cutoff or h.get("dur", 0) < 240: continue
        c = chans.get(h["channel"], {}); med = c.get("median_views_last50")
        ratio = round(h["views"] / med, 1) if med else None
        if h["views"] < 50000 or (ratio is not None and ratio < 4): continue
        waves[h["id"]] = {"id": h["id"], "url": f"https://youtu.be/{h['id']}", "title": h["title"], "channel": h.get("ctitle"),
                          "subs": c.get("subs"), "channel_median": med, "ratio": ratio, "views": h["views"],
                          "published": h["published"][:10], "minutes": round(h["dur"] / 60, 1), "lang": h.get("lang"),
                          "query": h["q"], "thumb": f"thumbs/{h['id']}.jpg"}
    # older videos of the same channels that also broke out recently (the deep dives see them)
    for v in vids.values():
        if v["id"] in waves or v.get("published", "") < cutoff or (v.get("ratio") or 0) < 4 or v["views"] < 50000: continue
        c = chans.get(v["channel"], {})
        waves[v["id"]] = {"id": v["id"], "url": f"https://youtu.be/{v['id']}", "title": v["title"], "channel": v.get("ctitle"),
                          "subs": c.get("subs"), "channel_median": c.get("median_views_last50"), "ratio": v.get("ratio"),
                          "views": v["views"], "published": v["published"][:10], "minutes": round(v["dur"] / 60, 1),
                          "lang": v.get("lang"), "query": "channel deep dive", "thumb": f"thumbs/{v['id']}.jpg"}
    out_list = sorted(waves.values(), key=lambda w: -w["views"])[:80]
    json.dump({"made": datetime.date.today().isoformat(), "window_days": days, "videos": out_list}, open(os.path.join(out, "waves.json"), "w"),
              indent=1, ensure_ascii=False)
    print(f"topic waves: {len(out_list)} breakout videos from {len(chans)} channels")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "collect": collect(sys.argv[2])
    else: raise SystemExit(__doc__)
