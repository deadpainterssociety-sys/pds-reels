"""Quality gate run after Claude writes stories: anything that fails is taken off the schedule (status "rejected")
and reported, so a weak story never reaches your phone.

usage: python automation/validate.py [slug ...] [--report-only]   (default: every scheduled draft; --report-only: just exit 1 on problems)
step output: ok=<slugs> rejected=<json [{slug, problems}]>
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONFIG, ROOT, now, gh_output, save_schedule, schedule, set_state, state, story

MIN_YEARS = 70
HOOK_TYPES = ("dark", "time-gap", "craft", "sacred-strange", "dark-legend", "damage", "hidden")   # PLAYBOOK §2
HOOK_MAX_WORDS = 12
SCENE_SETTING = re.compile(r"^(one (morning|day|night|evening|afternoon)|in (the )?\d|on \w+ \d|once\b|it was\b|"
                           r"(a|an|the) (man|woman|boy|girl|young|old|painter|artist|guard|visitor)\b.{0,20}\b(walk|walked|walks|enter|entered|enters))", re.I)
CLOSE_UP = 1.5          # minimum zoom for the opening shot (and for every shot of a nude while nude_safe_framing is on)


def visual_problems(st, sd):
    """PLAYBOOK §1 (1 Nov): open on the painting in colour, close-up; only the painting until the hook ends; nudes stay close."""
    p, m = [], st.get("meta", {})
    rp, tp = os.path.join(sd, "build", "resolved.json"), os.path.join(sd, "build", "timeline.json")
    if not (os.path.exists(rp) and os.path.exists(tp)): return p
    r, t = json.load(open(rp)), json.load(open(tp))
    shots, main = r.get("shots", []), m.get("image")
    if not shots: return ["no shots"]
    first = shots[0]
    if first["img"] != main or first.get("gray") or first.get("kind") == "map":
        p.append(f"the reel must open on the painting itself, in colour (shot 1 shows '{first['img']}')")
    elif min(first["from"][2], first["to"][2]) < CLOSE_UP:
        p.append(f"shot 1 must be a close-up of the painting (zoom ≥ {CLOSE_UP}, got {min(first['from'][2], first['to'][2]):.2f})")
    hook_end = t["lines"][0]["e"] if t.get("lines") else 0
    early = sorted({s["img"] for s in shots[1:] if s["t"] < hook_end - 0.05 and (s["img"] != main or s.get("gray"))})
    if early: p.append(f"only the painting, in colour, until the hook ends at {hook_end:.1f} s (also shown: {', '.join(early)})")
    if m.get("nude") and CONFIG.get("nude_safe_framing", True):
        wide = [f"{s['t']:.1f}s" for s in shots if s["img"] == main and min(s["from"][2], s["to"][2]) < CLOSE_UP]
        if wide: p.append(f"nude: shots of the painting must stay close-up (zoom ≥ {CLOSE_UP}) on safe details (wide at {', '.join(wide[:5])})")
        if float(st.get("cover", {}).get("span", 0.45)) > 0.45: p.append("nude: cover.span must be ≤ 0.45, on a face or safe detail")
    return p


def hook_problems(st):
    """PLAYBOOK §1–2 (1 Nov): one punchy hook line, a hook_type, a teaser for the NEXT card, room for the card."""
    p = []
    if st.get("hook_type") not in HOOK_TYPES: p.append(f"hook_type must be one of: {', '.join(HOOK_TYPES)}")
    tz = (st.get("teaser") or "").strip()
    if not tz: p.append("teaser missing (≤ 48 characters, shown on the previous reel's NEXT card)")
    elif len(tz) > 48: p.append(f"teaser is {len(tz)} characters (max 48)")
    lines = st.get("lines") or [{}]
    hook = " ".join(re.sub(r"\*", "", ph[0]) for ph in lines[0].get("perf", [])).strip()
    if len(hook.split()) > HOOK_MAX_WORDS: p.append(f"hook is {len(hook.split())} words (max {HOOK_MAX_WORDS}: one punchy line)")
    if re.search(r"\b1\d{3}\b", hook) or SCENE_SETTING.match(hook):
        p.append("hook opens with a date or a scene-setting: start with a claim about the painting on screen")
    if float(st.get("tail", 1.0)) < 2.0: p.append("tail must be ≥ 2.0 s (room for the NEXT card)")
    for k in ("hashtags_instagram", "hashtags_tiktok"):   # Instagram and TikTok accept 5 hashtags at most (2 Nov 2026)
        tags = st.get(k) or []
        if not tags: p.append(f"{k} missing (the best 5 for that platform)")
        elif len(tags) > 5: p.append(f"{k} has {len(tags)} hashtags (max 5)")
    return p


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
    two = st.get("format") == "two-minute"   # E2 arm B (EXPERIMENTS.md): a 2-minute single-painting reel
    if not ((230 <= words <= 360) if two else (110 <= words <= 165)): p.append(f"{words} spoken words (want {'260-340' if two else '125-150'})")
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
        lo, hi = (95, 170) if two else (48, 80)
        if not lo <= t.get("duration", 0) <= hi: p.append(f"duration {t.get('duration')} s (want {'110-150' if two else '55-70'})")
        bad = [f"{l['id']} ({l.get('match')})" for l in t["lines"] if l.get("match") is not None and l["match"] < 0.85]
        if bad: p.append("voice check failed on: " + ", ".join(bad))
    if not st.get("caption") or not st.get("hashtags"): p.append("caption/hashtags missing")
    p += hook_problems(st) + visual_problems(st, sd)
    if not any(e["slug"] == slug for e in schedule()): p.append("not on the schedule (run automation/plan.py add)")
    return p


def main(slugs, report_only=False):
    # by default only the stories written in THIS run: earlier ones already passed, and their source images live in a
    # release, not on this machine (checking them again here wrongly dropped david-marat and holbein-ambassadors)
    slugs = slugs or [e["slug"] for e in schedule() if state(e["slug"])["status"] == "draft" and not state(e["slug"]).get("validated_at")]
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
            if not report_only: set_state(s, validated_at=now().isoformat(timespec="seconds"))
    gh_output(ok=" ".join(ok), rejected=json.dumps(rejected))
    if rejected and not report_only and os.environ.get("TELEGRAM_BOT_TOKEN"):   # a dry check never alerts Gigi
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
