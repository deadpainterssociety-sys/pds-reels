"""Which long-video slot to produce next (workflow longform.yml).

Long videos go public on Mondays and Thursdays at 19:00 Madrid (config.json long_days / long_time). A slot is taken
when a *-long story is scheduled for that date (its state.json publish_at) or already written for it (story.json slot).
usage: python automation/long_plan.py next [YYYY-MM-DD]   prints and writes need/date/publish_at to $GITHUB_OUTPUT
       python automation/long_plan.py list                 the coming slots and what fills them
       python automation/long_plan.py written YYYY-MM-DD   the long story Claude wrote for that slot -> slug
       python automation/long_plan.py slot <slug>          its publish_at -> $GITHUB_OUTPUT
       python automation/long_plan.py stills <slug>        QA still times (every few shots), comma-separated
       python automation/long_plan.py tell <slug>          thumbnails + preview + notes to Gigi on Telegram (after the upload)
"""
import datetime, glob, json, os, sys
from common import CONFIG, ROOT, TZ, now

DAYS = CONFIG.get("long_days", [0, 3])                 # Monday, Thursday
TIME = CONFIG.get("long_time", "19:00")
LEAD_H = CONFIG.get("long_min_lead_hours", 20)         # the slot must leave time to render, upload and review
HORIZON = CONFIG.get("long_horizon_days", 10)


def taken():
    """{date: (slug, how)}: how = "scheduled" (uploaded), "ready" (written and valid, not produced yet) or "draft"
    (an unfinished story for that slot: the next run finishes it)"""
    from validate_long import check
    t = {}
    for d in glob.glob(os.path.join(ROOT, "stories", "*-long")):
        slug = os.path.basename(d)
        try: st = json.load(open(os.path.join(d, "state.json")))
        except (OSError, ValueError): st = {}
        try: story = json.load(open(os.path.join(d, "story.json")))
        except (OSError, ValueError): story = {}
        if st.get("publish_at"): t[st["publish_at"][:10]] = (slug, "scheduled")
        elif story.get("slot"): t[story["slot"]] = (slug, "draft" if check(slug, light=True) else "ready")
    return t


def publish_at(day):
    h, m = map(int, TIME.split(":"))
    return datetime.datetime.combine(datetime.date.fromisoformat(day), datetime.time(h, m), TZ).isoformat()


def slots():
    n = now()
    for i in range(HORIZON + 1):
        d = n.date() + datetime.timedelta(days=i)
        if d.weekday() in DAYS:
            yield d.isoformat()


def gh_out(**kv):
    print(json.dumps(kv))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for k, v in kv.items(): f.write(f"{k}={v}\n")


def written(day):
    for d in sorted(glob.glob(os.path.join(ROOT, "stories", "*-long")), key=os.path.getmtime, reverse=True):
        try: story = json.load(open(os.path.join(d, "story.json")))
        except (OSError, ValueError): continue
        if story.get("slot") == day: return os.path.basename(d)
    return ""


def stills(slug):
    r = json.load(open(os.path.join(ROOT, "stories", slug, "build", "resolved.json")))
    sh, D = r["shots"], r["duration"]
    ts = [round(s["t"] + min(1.5, ((sh[i + 1]["t"] if i + 1 < len(sh) else D) - s["t"]) * 0.5), 2) for i, s in enumerate(sh)]
    step = max(1, len(ts) // 28)
    return ",".join(str(t) for t in ts[::step])


def tell(slug):
    import html, subprocess
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import telegram as T
    from bot import chat_id
    chat = chat_id()
    d = os.path.join(ROOT, "stories", slug); out = os.path.join(d, "out")
    st = json.load(open(os.path.join(d, "story.json"))); yt = st.get("youtube", {}); m = st.get("meta", {})
    r = json.load(open("yt.json")) if os.path.exists("yt.json") else {}
    titles = yt.get("titles", ["", ""]) + ["", ""]
    when = datetime.datetime.fromisoformat(r.get("publish_at") or publish_at(st["slot"])).strftime("%a %d %b, %H:%M")
    notes = open(os.path.join(d, "notes.txt")).read().strip() if os.path.exists(os.path.join(d, "notes.txt")) else ""
    T.album(chat, [(os.path.join(out, "thumb_a.jpg"), "Thumbnail A (set)"), (os.path.join(out, "thumb_b.jpg"), f"Thumbnail B: {html.escape(yt.get('thumbnail', {}).get('words', ''))}")])
    prev = os.path.join(out, f"{slug}_review_720p.mp4")
    if os.path.exists(prev) and os.path.getsize(prev) > 48e6:     # Telegram bots send up to 50 MB
        small = os.path.join(out, f"{slug}_tg.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", prev, "-vf", "scale=-2:540", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "30", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", small], check=True)
        prev = small
    words = sum(len(" ".join(x[0] for x in l["perf"]).split()) for l in st.get("lines", []))
    cap = (f"🎬 <b>Long video ready</b>: {html.escape(titles[0])}\n<b>{html.escape(m.get('painter', ''))}</b>, <i>{html.escape(m.get('painting', ''))}</i>\n"
           f"Goes public <b>{when}</b> (private until then) · {words} words · {len(st.get('facts', []))} sourced facts")
    T.call("sendVideo", {"chat_id": chat, "caption": cap[:1024], "parse_mode": "HTML", "supports_streaming": "true", "width": 960, "height": 540},
           {"video": prev}, timeout=600)
    T.send(chat, (f"<b>Title B</b> (Test &amp; compare): {html.escape(titles[1])}\n"
                  + (f"\n<b>Claude's notes</b>\n{html.escape(notes)}\n" if notes else "")
                  + f"\nIn Studio before it goes public: Test &amp; compare (title B + thumbnail B) and the end screen; pin the comment after it posts.\n"
                  f"Something wrong? Set it to Private in Studio and tell Claude in a chat.\n{r.get('studio', '')}"))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    if cmd == "written": return gh_out(slug=written(sys.argv[2]))
    if cmd == "slot":
        st = json.load(open(os.path.join(ROOT, "stories", sys.argv[2], "story.json")))
        return gh_out(publish_at=publish_at(st["slot"]))
    if cmd == "stills": return print(stills(sys.argv[2]))
    if cmd == "tell": return tell(sys.argv[2])
    t = taken()
    if cmd == "list":
        for d in slots(): print(d, *t.get(d, ("-",)))
        return
    want = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    day, resume, draft = None, "", ""
    for d in ([want] if want else slots()):
        lead = (datetime.datetime.fromisoformat(publish_at(d)) - now()).total_seconds() / 3600
        if lead < LEAD_H: continue
        slug, how = t.get(d, ("", ""))
        if how == "scheduled": continue
        day = d
        if how == "ready": resume = slug          # written and valid: only produce it
        if how == "draft": draft = slug           # unfinished: Claude finishes this one
        break
    gh_out(need="true" if day else "false", date=day or "", publish_at=publish_at(day) if day else "", resume=resume, draft=draft)


if __name__ == "__main__":
    main()
