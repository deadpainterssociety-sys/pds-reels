"""The Spanish channel's daily job (Spanish edition test, Gigi 12 Nov 2026). Two Shorts a day, at 19:00 and 01:00 Madrid
(18:00 in Mexico City), from schedule_es.json in order. No review step (Gigi: as little work for her as possible): the
English original was approved, the Spanish twin is checked by the pipeline (recogniser, loudness, validate). Telegram
gets the link after each post. Until the Spanish channel is connected (secret YT_REFRESH_TOKEN_ES), the rendered video
is kept in the private data release (es-ready-<slug>.mp4) and Telegram says it's waiting.

usage: python automation/es.py pick              -> slug=<next Spanish story> (GitHub output), or nothing to do
       python automation/es.py publish <slug>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import gh_output, jload, now, set_state, state, story

SCHED = "schedule_es.json"


def pick(slug=None):
    if not slug:
        for e in jload(SCHED, []):
            st = state(e["slug"]).get("status")
            if st in ("posted", "skipped"): continue
            if st == "waiting" and not os.environ.get("YT_REFRESH_TOKEN_ES", "").strip():
                print("still waiting for the Spanish channel:", e["slug"]); gh_output(slug=""); return
            slug = e["slug"]; break
    print("next Spanish story:", slug or "none"); gh_output(slug=slug or "")
    if os.environ.get("ES_PRINT"): print(f"SLUG={slug or ''}", file=sys.stderr)


def skip(slug, reason):
    """a twin that can't be rendered (e.g. an early story whose images were never saved) is skipped for good"""
    set_state(slug, status="skipped", skipped_reason=reason, updated=now().isoformat(timespec="seconds"))
    print(f"skipped {slug}: {reason}")


def say(msg):
    import subprocess; subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py"), "say", msg])


def publish(slug):
    title = story(slug).get("youtube_title", slug)
    if not os.environ.get("YT_REFRESH_TOKEN_ES", "").strip():
        import release
        release.data_put(f"es-ready-{slug}.mp4", open(f"stories/{slug}/out/{slug}.mp4", "rb").read(), "video/mp4")
        set_state(slug, status="waiting", rendered_at=now().isoformat(timespec="seconds"))
        say(f"🇪🇸 Listo: «{title}». Waiting for the Spanish channel to be connected (secret YT_REFRESH_TOKEN_ES), then it goes out.")
        return
    import youtube
    r = youtube.publish(slug)
    set_state(slug, status="posted", posted_at=now().isoformat(timespec="seconds"), youtube_id=r.get("id"), youtube_url=r.get("url"))
    say(f"🇪🇸 Publicado en el canal español: «{title}»\n{r.get('url', '')}")


if __name__ == "__main__":
    if sys.argv[1] == "pick": pick(sys.argv[2] if len(sys.argv) > 2 else None)
    elif sys.argv[1] == "publish": publish(sys.argv[2])
    elif sys.argv[1] == "skip": skip(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "render failed")
    else: sys.exit(__doc__)
