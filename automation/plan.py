"""Scheduling helpers used by the workflows (and by Claude when it adds a story).

usage:
  python automation/plan.py needed [n]       how many new stories to write now (keeps config.buffer_days of reels ready)
  python automation/plan.py today            today's reels to render this morning (step outputs slugs=[…], slug=first)
  python automation/plan.py add <slug> [date] put a finished story in the first free slot from tomorrow on
                                             (date = YYYY-MM-DD: pin it to that day, e.g. a film release or anniversary)
  python automation/plan.py posted           slugs already posted or scheduled (Claude: never repeat these)
  python automation/plan.py missing          render=true when today still has a free slot and there is still time (07-19 h)
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, re
from common import (CONFIG, DROPPED, ROOT, day_entries, gh_output, now, per_day, save_schedule, schedule, set_state, state,
                    today, upcoming)


def pinned_due(days=5):
    """STORY_QUEUE.md "Pinned" rows with a date in the next `days` days that nothing is scheduled on yet as pinned"""
    try: q = open(os.path.join(ROOT, "STORY_QUEUE.md")).read()
    except OSError: return []
    sec = q.split("## Pinned", 1)[1].split("\n## ", 1)[0] if "## Pinned" in q else ""
    t0 = datetime.date.fromisoformat(today()); out = []
    pinned_dates = {e["date"] for e in schedule() if e.get("pinned")}
    for d in re.findall(r"\b(20\d\d-\d\d-\d\d)\b", sec):
        if 0 <= (datetime.date.fromisoformat(d) - t0).days <= days and d not in pinned_dates: out.append(d)
    return sorted(set(out))


def needed(override=None):
    if CONFIG.get("paused"): gh_output(n=0); return 0
    if "CLAUDE_CODE_OAUTH_TOKEN" in os.environ and not (os.environ["CLAUDE_CODE_OAUTH_TOKEN"].strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()):
        print("Claude not set up yet (secret CLAUDE_CODE_OAUTH_TOKEN): nothing to do"); gh_output(n=0); return 0
    if override: n = int(override)
    else:   # keep buffer_days × reels-per-day ready (pinned stories further ahead don't count)
        horizon = (datetime.date.fromisoformat(today()) + datetime.timedelta(days=CONFIG.get("buffer_days", 3))).isoformat()
        ready = len([e for e in upcoming(("draft", "built", "sent", "revising", "approved")) if e["date"] < horizon])
        n = max(0, min(CONFIG.get("buffer_days", 3) * per_day() - ready, CONFIG.get("stories_per_run", 3)))
        if pinned_due() and n == 0: n = 1                 # a pinned date is coming up: write it even if the buffer is full
    print(f"stories to write now: {n}" + (f" (pinned dates coming up: {', '.join(pinned_due())})" if pinned_due() else ""))
    gh_output(n=n); return n


def todays():
    """today's reels to render (up to one per slot). Missing ones are pulled forward from later drafts (never pinned ones)."""
    if CONFIG.get("paused"): gh_output(slugs="[]", slug=""); return []
    sch = schedule(); live = day_entries(today(), sch); moved = False
    for e in sch:
        if len(live) >= per_day(): break
        if e["date"] > today() and not e.get("pinned") and state(e["slug"])["status"] == "draft":
            print(f"moving {e['slug']} from {e['date']} to today"); e["date"] = today(); live.append(e); moved = True
    if moved: save_schedule(sch)
    render = [e["slug"] for e in live if state(e["slug"])["status"] in ("draft", "built")]
    print("today's reels to render:", render or "none")
    gh_output(slugs=json.dumps(render), slug=render[0] if render else ""); return render


def missing_today():
    """after a late story run: render now when today still has a free slot and there's time to review + publish today"""
    short = len(day_entries(today())) < per_day()
    ok = short and 7 <= now().hour < 19 and not CONFIG.get("paused")
    print("render reels for today now:", ok); gh_output(render="true" if ok else "false")


def add(slug, date=None):
    sch = schedule()
    if any(e["slug"] == slug for e in sch): print("already scheduled:", slug); return
    if date:
        datetime.date.fromisoformat(date)
        e = {"date": date, "slug": slug, "pinned": True}
        day = day_entries(date, sch)
        if len(day) >= per_day():                    # make room: the day's last unpinned reel moves to the next free day
            mv = next((x for x in reversed(day) if not x.get("pinned")), None)
            if mv:
                d = datetime.date.fromisoformat(date) + datetime.timedelta(days=1)
                while len(day_entries(d.isoformat(), sch)) >= per_day(): d += datetime.timedelta(days=1)
                print(f"moving {mv['slug']} from {date} to {d.isoformat()} to make room"); sch.remove(mv); mv["date"] = d.isoformat(); sch.append(mv)
    else:
        d = datetime.date.fromisoformat(today()) + datetime.timedelta(days=1)
        while len(day_entries(d.isoformat(), sch)) >= per_day(): d += datetime.timedelta(days=1)
        e = {"date": d.isoformat(), "slug": slug}
    sch.append(e); save_schedule(sch)
    set_state(slug, status="draft")
    print(f"scheduled {slug} for {e['date']}" + (" (pinned)" if e.get("pinned") else ""))


def used():
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stories")
    for s in sorted(os.listdir(root)):
        if os.path.exists(os.path.join(root, s, "story.json")): print(s, "-", state(s)["status"])


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "needed": needed(sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None)
    elif c == "today": todays()
    elif c == "missing": missing_today()
    elif c == "add": add(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif c == "posted": used()
    else: raise SystemExit(__doc__)
