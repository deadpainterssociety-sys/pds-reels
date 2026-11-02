"""Scheduling helpers used by the workflows (and by Claude when it adds a story).

usage:
  python automation/plan.py needed [n]       how many new stories to write now (keeps config.buffer_days of reels ready)
  python automation/plan.py today            the reel to render this morning (step output slug=)
  python automation/plan.py add <slug>       put a finished story on the first free day from tomorrow on
  python automation/plan.py posted           slugs already posted or scheduled (Claude: never repeat these)
  python automation/plan.py missing          render=true when nothing is planned today and there is still time (07-19 h)
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, gh_output, now, save_schedule, schedule, set_state, state, today, upcoming


def needed(override=None):
    if CONFIG.get("paused"): gh_output(n=0); return 0
    if "CLAUDE_CODE_OAUTH_TOKEN" in os.environ and not (os.environ["CLAUDE_CODE_OAUTH_TOKEN"].strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()):
        print("Claude not set up yet (secret CLAUDE_CODE_OAUTH_TOKEN): nothing to do"); gh_output(n=0); return 0
    if override: n = int(override)
    else:
        ready = len(upcoming(("draft", "built", "sent", "revising", "approved")))
        n = max(0, min(CONFIG.get("buffer_days", 3) - ready, CONFIG.get("stories_per_run", 2)))
    gh_output(n=n); return n


def todays():
    if CONFIG.get("paused"): gh_output(slug=""); return
    sch = schedule()
    if any(e["date"] == today() for e in sch):
        for e in sch:
            if e["date"] == today() and state(e["slug"])["status"] in ("draft", "built"):
                gh_output(slug=e["slug"]); return
        gh_output(slug=""); return               # today's reel is already sent/approved/skipped
    for e in sch:                                # nothing planned today: pull the next written story forward (self-healing)
        if e["date"] > today() and state(e["slug"])["status"] == "draft":
            print(f"moving {e['slug']} from {e['date']} to today"); e["date"] = today(); save_schedule(sch)
            gh_output(slug=e["slug"]); return
    gh_output(slug="")


def missing_today():
    """after a late story run: render now when nothing is planned for today and there's still time to review + publish today"""
    has = any(e["date"] == today() and state(e["slug"])["status"] not in ("rejected", "skipped") for e in schedule())
    ok = not has and 7 <= now().hour < 19 and not CONFIG.get("paused")
    print("render a reel for today now:", ok); gh_output(render="true" if ok else "false")


def add(slug):
    sch = schedule()
    if any(e["slug"] == slug for e in sch): print("already scheduled:", slug); return
    taken = {e["date"] for e in sch}
    d = datetime.date.fromisoformat(today()) + datetime.timedelta(days=1)
    while d.isoformat() in taken: d += datetime.timedelta(days=1)
    sch.append({"date": d.isoformat(), "slug": slug}); save_schedule(sch)
    if state(slug)["status"] not in ("draft",): pass
    set_state(slug, status="draft")
    print(f"scheduled {slug} for {d.isoformat()}")


def used():
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stories")
    for s in sorted(os.listdir(root)):
        if os.path.exists(os.path.join(root, s, "story.json")): print(s, "-", state(s)["status"])


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "needed": needed(sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None)
    elif c == "today": todays()
    elif c == "missing": missing_today()
    elif c == "add": add(sys.argv[2])
    elif c == "posted": used()
    else: raise SystemExit(__doc__)
