"""Publish approved reels inside the evening window, one platform at a time, never twice.

usage:
  python automation/publish.py decide [--now]          step output slug= (oldest approved reel that is due; '' if none)
  python automation/publish.py run <slug> <public_base>  Instagram (needs the public URL), YouTube, TikTok; then Telegram links
Each platform's result is stored in stories/<slug>/state.json ({"instagram": {"id","url"}, ...}), so a re-run only
retries what failed (max 3 attempts each). A platform whose secrets are missing is marked "off" and skipped.
"""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, date_for, gh_output, now, publish_until, schedule, set_state, slots, state, today

NEEDS = {"instagram": ["IG_ACCESS_TOKEN"], "youtube": ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"],
         "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"]}


def posted_today():
    return sum(1 for e in schedule() if (state(e["slug"]).get("posted_at") or "").startswith(today()))


def due(force=False):
    """the oldest approved reel that should go out now ('' if none)"""
    if CONFIG.get("paused"): return ""
    hm = now().strftime("%H:%M")
    if not force:
        if hm > publish_until(): return ""
        opened = sum(1 for t in slots() if hm >= t)          # slots already reached today
        if posted_today() >= opened: return ""               # 14:00 → first reel, 21:00 → second reel
    for e in schedule():
        if e["date"] <= today() and state(e["slug"])["status"] == "approved": return e["slug"]
    return ""


def decide(force=False):
    gh_output(slug=due(force))


def run(slug, base):
    import instagram, youtube, tiktok
    s = state(slug); base = (base or "").rstrip("/"); manual = []
    jobs = {"instagram": lambda: instagram.publish(slug, f"{base}/media/{slug}.mp4", f"{base}/media/{slug}-cover.jpg"),
            "youtube": lambda: youtube.publish(slug), "tiktok": lambda: tiktok.publish(slug)}
    for name, fn in jobs.items():
        r = s.get(name) or {}
        if r.get("id") or r.get("skipped"): continue
        if not CONFIG["platforms"].get(name, True): s = set_state(slug, **{name: {"skipped": "turned off in config.json"}}); continue
        missing = [k for k in NEEDS[name] if not os.environ.get(k, "").strip()]
        if name == "tiktok" and CONFIG.get("tiktok_mode") == "manual": missing = ["manual mode"]
        if missing:
            s = set_state(slug, **{name: {"skipped": "not set up yet (" + ", ".join(missing) + ")", "manual": True}}); manual.append(name); continue
        if name == "instagram" and not base: s = set_state(slug, **{name: {"error": "no public URL for the video", "attempts": r.get("attempts", 0) + 1}}); continue
        if r.get("attempts", 0) >= 3: continue
        print(f"-> {name}")
        try:
            res = fn(); print(f"   {name}: {res}"); s = set_state(slug, **{name: res})
        except Exception as e:
            traceback.print_exc()
            s = set_state(slug, **{name: {"error": str(e)[:500], "attempts": r.get("attempts", 0) + 1}})
    done = all((s.get(n) or {}).get("id") or (s.get(n) or {}).get("skipped") for n in jobs)
    gave_up = all((s.get(n) or {}).get("id") or (s.get(n) or {}).get("skipped") or (s.get(n) or {}).get("attempts", 0) >= 3 for n in jobs)
    if done or gave_up:
        set_state(slug, status="posted", posted_at=now().isoformat(timespec="seconds"))
    import bot
    bot.posted(slug)
    if manual: manual_package(slug, manual)
    gh_output(done="1" if (done or gave_up) else "")


def _where(slug):
    from common import story
    m = story(slug).get("meta", {})
    return f"\n📍 Location: add <b>{m['museum']}, {m.get('city', '')}</b>" if m.get("museum") else ""


def manual_package(slug, platforms):
    """platforms that are not connected yet: send Gigi a ready-to-post file (< 50 MB, the Telegram bot limit) + captions"""
    import subprocess, bot, telegram as T
    from common import captions, out_dir
    if state(slug).get("manual_sent") or not bot.chat_id(): return
    master, share = os.path.join(out_dir(slug), f"{slug}.mp4"), os.path.join(out_dir(slug), f"{slug}-1080p.mp4")
    for rate in ("6M", "4M", "2.8M"):
        subprocess.run(["ffmpeg", "-y", "-i", master, "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", rate, "-bufsize", "12M",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", share], check=True, capture_output=True)
        if os.path.getsize(share) < 48 * 1024 * 1024: break
    names = {"instagram": "Instagram", "youtube": "YouTube", "tiktok": "TikTok"}
    T.document(bot.chat_id(), share, "📲 <b>Post this one by hand on " + ", ".join(names[p] for p in platforms) +
               "</b> (not connected yet). Save the file, upload it, use the cover/first frame, and paste the caption below. "
               "Turn on the AI-content label." + _where(slug))
    c = captions(slug)
    for p in platforms:
        txt = c["instagram"] if p == "instagram" else c["tiktok"] if p == "tiktok" else f"{c['youtube_title']}\n\n{c['youtube_desc']}"
        T.send(bot.chat_id(), f"<b>{names[p]}</b>\n<code>{T.esc(txt[:3900])}</code>")
    set_state(slug, manual_sent=True)


if __name__ == "__main__":
    if sys.argv[1] == "decide": decide("--now" in sys.argv)
    elif sys.argv[1] == "run": run(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    else: raise SystemExit(__doc__)
