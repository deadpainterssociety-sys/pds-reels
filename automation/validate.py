"""Quality gate run after Claude writes stories: anything that fails is taken off the schedule (status "rejected")
and reported, so a weak story never reaches your phone.

usage: python automation/validate.py [slug ...] [--report-only]   (default: every scheduled draft; --report-only: just exit 1 on problems)
step output: ok=<slugs> rejected=<json [{slug, problems}]>
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, gh_output, save_schedule, schedule, set_state, state, story

MIN_YEARS = 70


def problems(slug):
    p, sd = [], os.path.join(ROOT, "stories", slug)
    st = story(slug)
    if not st: return ["story.json missing or invalid"]
    m = st.get("meta", {})
    for k in ("painter", "painting", "year", "museum", "city", "image", "died"):
        if not m.get(k): p.append(f"meta.{k} missing")
    if m.get("died") and datetime.date.today().year - int(m["died"]) <= MIN_YEARS: p.append(f"painter died {m['died']}: NOT public domain")
    cv = st.get("cover", {})
    for k in ("question", "name", "work"):
        if not cv.get(k): p.append(f"cover.{k} missing")
    words = sum(len(re.sub(r"\*", "", ph[0]).split()) for l in st.get("lines", []) for ph in l.get("perf", []))
    if not 110 <= words <= 165: p.append(f"{words} spoken words (want 125-150)")
    facts = st.get("facts", [])
    if len(facts) < 4: p.append(f"only {len(facts)} facts listed")
    if any("http" not in f.get("source", "") and "Wikipedia" not in f.get("source", "") for f in facts): p.append("a fact without a source URL")
    ending = " ".join(ph[0] for ph in (st.get("lines") or [{}])[-1].get("perf", []))
    if m.get("museum") and m["museum"].split()[-1].lower() not in ending.lower() and m.get("city", "").lower() not in ending.lower():
        p.append("last line does not say where the painting hangs")
    for k, im in st.get("images", {}).items():
        if not os.path.exists(os.path.join(sd, im.get("file", ""))): p.append(f"image {k} not downloaded")
    for f in ("out/cover.jpg", "out/stills.jpg", "out/caption.txt", "build/timeline.json"):
        if not os.path.exists(os.path.join(sd, f)): p.append(f"{f} missing (pipeline steps not run?)")
    tl = os.path.join(sd, "build", "timeline.json")
    if os.path.exists(tl):
        t = json.load(open(tl))
        if not 48 <= t.get("duration", 0) <= 80: p.append(f"duration {t.get('duration')} s (want 55-70)")
        bad = [f"{l['id']} ({l.get('match')})" for l in t["lines"] if l.get("match") is not None and l["match"] < 0.85]
        if bad: p.append("voice check failed on: " + ", ".join(bad))
    if not st.get("caption") or not st.get("hashtags"): p.append("caption/hashtags missing")
    if not any(e["slug"] == slug for e in schedule()): p.append("not on the schedule (run automation/plan.py add)")
    return p


def main(slugs, report_only=False):
    slugs = slugs or [e["slug"] for e in schedule() if state(e["slug"])["status"] == "draft"]
    ok, rejected = [], []
    for s in slugs:
        pr = problems(s)
        if pr and report_only:
            rejected.append({"slug": s, "problems": pr}); print(f"PROBLEMS {s}:", *pr, sep="\n  - "); continue
        if pr:
            rejected.append({"slug": s, "problems": pr}); set_state(s, status="rejected", problems=pr)
            save_schedule([e for e in schedule() if e["slug"] != s])
            print(f"REJECTED {s}:", *pr, sep="\n  - ")
        else:
            ok.append(s); print("ok", s)
    gh_output(ok=" ".join(ok), rejected=json.dumps(rejected))
    if rejected and os.environ.get("TELEGRAM_BOT_TOKEN"):
        try:
            import bot, telegram as T
            T.send(bot.chat_id(), "⚠️ <b>Dropped a story that failed the quality check</b>\n" + "\n".join(
                f"• {T.esc(r['slug'])}: {T.esc('; '.join(r['problems'][:4]))}" for r in rejected))
        except Exception as e: print("telegram:", e)
    return ok, rejected


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ok, bad = main(args, "--report-only" in sys.argv)
    if "--report-only" in sys.argv and bad: sys.exit(1)
