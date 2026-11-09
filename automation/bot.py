"""The Telegram review bot: sends each reel for review and reads your answers.

usage:
  python automation/bot.py review <slug> [--revised]   cover + 540p video with ✅ Publish / ❌ Skip / ✏️ Changes + captions + facts
  python automation/bot.py poll                        read button presses and messages -> update states; step outputs:
                                                         revise=[{"slug","feedback"}]  post_now=1  stories=<n>
  python automation/bot.py brief [date]                the lab's latest brief, one ✅/❌ message per proposal
  python automation/bot.py listen [minutes]            the same, staying on the line (answers within seconds); starts
                                                         revisions/stories itself; stops early when a reel is due
  python automation/bot.py plan                        the upcoming reels (covers) after Claude writes new ones
  python automation/bot.py posted <slug>               links after publishing (+ TikTok caption to paste in inbox mode)
  python automation/bot.py say "<html text>"           any message (alerts from the workflows)

What you can send the bot:
  buttons on each reel        ✅ Publish · ❌ Skip · ✏️ Changes (then type what to change)
  "yes" / "ok" / "sí"         approve the reel waiting for review       "no" / "skip"  skip it
  any other text              treated as a change request for the reel waiting for review
  /status  what is scheduled   /post  publish approved reels now   /stories 3  write 3 more stories now
  /idea <painting — angle>  have Claude write that one next
  /pause /resume  stop or restart everything   /rule <text>  a rule for all future reels (added to PLAYBOOK.md)
  a voice message / audio file   clone that voice: test versions come back with ✅ buttons (automation/voice.py)
  /voice [on|off|help]           the narration voice
The chat is linked the first time someone sends /start (or set TELEGRAM_CHAT_ID).
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import telegram as T
from common import (CONFIG, ROOT, captions, date_for, gh_output, jload, jsave, now, out_dir, publish_until, schedule, set_state,
                    slot_time, slots, state, story,
                    title_of, today, upcoming)

BS = "automation/bot_state.json"
YES = {"yes", "y", "ok", "okay", "sí", "si", "yep", "yeah", "publish", "post it", "go", "approve", "approved", "👍", "✅", "dale", "vale"}
NO = {"no", "skip", "nope", "❌", "👎", "descartar"}


def bstate(): return jload(BS, {"offset": 0, "chat_id": None, "awaiting": None})
def chat_id(): return os.environ.get("TELEGRAM_CHAT_ID", "").strip() or bstate().get("chat_id")


def when_text(slug):
    """human 'when will this go out' for an approved reel"""
    d = date_for(slug) or today(); t = slot_time(slug)
    if d > today():
        return f"on {datetime.date.fromisoformat(d).strftime('%a %d %b')} at {t}"
    hm = now().strftime("%H:%M")
    if hm < t: return f"today at {t}"
    if hm <= publish_until(): return "in the next few minutes"
    return f"tomorrow at {slots()[0]}"


def nice_date(d): return datetime.date.fromisoformat(d).strftime("%a %d %b") if d else "unscheduled"


def review(slug, revised=False):
    chat = chat_id()
    if not chat: raise SystemExit("no Telegram chat linked yet: send /start to the bot, then run the setup-check workflow")
    st, out = story(slug), out_dir(slug)
    m, s = st.get("meta", {}), state(slug)
    q = re.sub(r"<[^>]+>", "", st.get("cover", {}).get("question", ""))
    qa = open(os.path.join(out, "qa.txt")).read() if os.path.exists(os.path.join(out, "qa.txt")) else ""
    dur = re.search(r"([\d.]+) s", qa); heard = re.search(r"recogniser match on the final file: ([\d.]+)", qa)
    head = ("✏️ <b>Revised version</b>" + (f" — you asked: <i>{T.esc(s.get('feedback', [''])[-1])}</i>" if s.get("feedback") else "")
            if revised else f"🎨 <b>Reel for {nice_date(date_for(slug))} · {slot_time(slug)}</b>")
    nxt = ""
    try:
        rs = json.load(open(os.path.join(out, "..", "build", "resolved.json")))
        nxt = next((o.get("text", "") for o in rs.get("overlays", []) if o.get("type") == "next"), "")
    except (OSError, ValueError): pass
    cap = (f"{head}\n\n<b>{T.esc(m.get('painter', ''))}</b>, <i>{T.esc(m.get('painting', ''))}</i> ({T.esc(m.get('year', ''))})\n"
           f"📍 {T.esc(m.get('museum', ''))}, {T.esc(m.get('city', ''))}\n“{T.esc(q)}”\n"
           f"🎣 {T.esc(st.get('hook_type', '?'))} · ⏭ NEXT card: {T.esc(nxt) if nxt else 'none'}\n\n"
           f"⏱ {dur.group(1) if dur else '?'} s · 🗣 voice check {heard.group(1) if heard else '?'} · 📚 {len(st.get('facts', []))} sourced facts")
    T.photo(chat, os.path.join(out, "cover.jpg"), cap)
    kb = [[{"text": "✅ Publish", "callback_data": f"ok:{slug}"}, {"text": "❌ Skip", "callback_data": f"no:{slug}"}],
          [{"text": "✏️ Changes", "callback_data": f"ch:{slug}"}]]
    msg = T.video(chat, os.path.join(out, f"{slug}-preview.mp4"), "▶️ Watch, then choose:", kb)
    c = captions(slug)
    facts = "\n".join(f"• {T.esc(f['claim'])}" for f in st.get("facts", []))
    T.send(chat, f"<b>Instagram caption</b><blockquote expandable>{T.esc(c['instagram'][:1700])}</blockquote>\n"
                 f"<b>TikTok</b><blockquote expandable>{T.esc(c['tiktok'][:600])}</blockquote>\n"
                 f"<b>YouTube title</b>\n{T.esc(c['youtube_title'])}\n\n<b>Facts checked</b><blockquote expandable>{facts[:1200]}</blockquote>")
    set_state(slug, status="sent", review_message=msg["message_id"], sent_at=now().isoformat(timespec="seconds"))
    print("review sent:", slug)


def pending():
    """reels waiting for your answer, the most recently sent first ("yes" / a change request applies to that one;
    older unanswered reels keep their buttons and can still be approved - they then go out at the next window)"""
    sent = [e["slug"] for e in schedule() if state(e["slug"])["status"] == "sent"]
    return sorted(sent, key=lambda s: state(s).get("sent_at", ""), reverse=True)


def approve(chat, slug, msg_id=None):
    set_state(slug, status="approved", approved_at=now().isoformat(timespec="seconds"))
    if msg_id: T.buttons_only(chat, msg_id, [[{"text": "✅ Approved", "callback_data": "noop"}]])
    T.send(chat, f"✅ Approved: {T.esc(title_of(slug))}\nIt goes out {when_text(slug)}.")


def skip(chat, slug, msg_id=None):
    set_state(slug, status="skipped")
    if msg_id: T.buttons_only(chat, msg_id, [[{"text": "❌ Skipped", "callback_data": "noop"}]])
    T.send(chat, f"❌ Skipped: {T.esc(title_of(slug))}. Nothing will be posted that day.")


def status_text():
    rows = []
    for e in schedule()[-12:]:
        s = state(e["slug"]); icon = {"draft": "📝", "built": "🎬", "sent": "👀", "revising": "✏️", "approved": "✅", "skipped": "❌",
                                       "posted": "📣", "failed": "⚠️"}.get(s["status"], "•")
        rows.append(f"{icon} {nice_date(e['date'])} — {T.esc(title_of(e['slug']))} <i>({s['status']})</i>")
    paused = "\n⏸ <b>Paused</b> (send /resume)" if CONFIG.get("paused") else ""
    return ("<b>Schedule</b>\n" + ("\n".join(rows) or "nothing scheduled yet") + paused +
            "\n\n📝 written · 🎬 rendered · 👀 waiting for you · ✅ approved · 📣 posted")


HELP = ("Commands:\n/status — what's scheduled\n/post — publish approved reels now\n/stories 3 — write 3 more stories now\n"
        "/idea &lt;painting — angle&gt; — have Claude write that one next\n"
        "/rule &lt;text&gt; — a rule for all future reels\n/brief — the latest analysis brief again\n/pause, /resume\n"
        "/voice — the narration voice (on, off, help)\n\n"
        "🎙 Send a voice message (1–3 min, reading in English) to clone that voice: you get test versions to choose from.\n"
        "📊 Send a screenshot of TikTok Studio → Analytics → Content any time: it goes into the next brief.\n\nOn a reel: ✅ / ❌ / ✏️ buttons, or just reply "
        "<i>yes</i>, <i>no</i>, or what you want changed.")


def poll(emit=True):
    bs = bstate(); chat = chat_id(); revise, post_now, stories, idea = [], False, 0, ""
    if not os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():          # not set up yet: stay quiet instead of failing
        print("Telegram not set up yet (secret TELEGRAM_BOT_TOKEN)"); gh_output(revise="[]", post_now="", stories="", idea=""); return {}
    ups = T.updates(bs.get("offset", 0))
    print(f"telegram: {len(ups)} update(s) from offset {bs.get('offset', 0)}:",
          ", ".join("button " + u["callback_query"].get("data", "") if "callback_query" in u else "message" for u in ups) or "none")
    for u in ups:
        bs["offset"] = u["update_id"] + 1
        if "callback_query" in u:
            q = u["callback_query"]; cid = str(q["message"]["chat"]["id"])
            if cid != str(chat): T.answer(q["id"]); continue
            act, _, slug = q.get("data", "").partition(":")
            if act == "lab":                                   # a proposal of the analysis brief: lab:<date>:<id>:y|n
                d, pid, yn = (slug.split(":") + ["", "", ""])[:3]
                T.answer(q["id"], "Applying…" if yn == "y" else "Dropped")
                decide_proposal(chat, d, pid, yn == "y", q["message"]["message_id"]); continue
            if act == "vc":                                    # a voice test version: vc:<run>:<n>
                import voice
                run, _, n = slug.partition(":"); T.answer(q["id"], "Setting the voice…")
                voice.choose(chat, run, n, q["message"]["message_id"]); continue
            if act == "noop" or not slug: T.answer(q["id"]); continue
            stt = state(slug)["status"]
            if stt not in ("sent", "built", "approved", "skipped"):
                T.answer(q["id"], f"This reel is {stt} now"); continue
            if act == "ok": T.answer(q["id"], "Approved ✅"); approve(chat, slug, q["message"]["message_id"])
            elif act == "no": T.answer(q["id"], "Skipped"); skip(chat, slug, q["message"]["message_id"])
            elif act == "ch":
                T.answer(q["id"], "Tell me what to change"); bs["awaiting"] = slug
                T.send(chat, f"✏️ What should change in <b>{T.esc(title_of(slug))}</b>?\nReply with one message, e.g. "
                             "<i>shorter hook</i>, <i>slower voice at the end</i>, <i>use a different painting for the cover</i>.")
            continue
        msg = u.get("message") or {}
        text = (msg.get("text") or "").strip(); cid = str(msg.get("chat", {}).get("id", ""))
        if (msg.get("photo") or (msg.get("document") or {}).get("mime_type", "").startswith("image/")) and cid == str(chat):
            save_screenshot(chat, msg); continue
        if (msg.get("voice") or msg.get("audio") or msg.get("video_note") or msg.get("video")
                or (msg.get("document") or {}).get("mime_type", "").startswith(("audio/", "video/"))) and cid == str(chat):
            import voice
            voice.intake(chat, msg); continue          # a recording for the cloned voice
        if not text: continue
        if not chat and msg.get("chat", {}).get("type") == "private" and text.startswith("/start"):
            chat = bs["chat_id"] = cid
            T.send(chat, "🖤 Linked. This chat will get every reel for review.\n\n" + HELP); continue
        if cid != str(chat): continue
        low = text.lower().strip(" .!")
        if text.startswith("/start") or text.startswith("/help"): T.send(chat, HELP); continue
        if text.startswith("/status"): T.send(chat, status_text()); continue
        if text.startswith("/voice"):
            import voice
            arg = text[6:].strip().lower()
            if arg in ("on", "off"): voice.switch(chat, arg == "on")
            elif arg.startswith("help"): T.send(chat, voice.TIPS)
            else: T.send(chat, voice.status_text())
            continue
        if text.startswith("/brief"): send_brief(None); continue
        if text.startswith("/post"): post_now = True; T.send(chat, "📣 Publishing approved reels now…"); continue
        if text.startswith("/stories"):
            n = re.findall(r"\d+", text); stories = min(int(n[0]) if n else 2, 7)
            T.send(chat, f"📝 Writing {stories} new stor{'y' if stories == 1 else 'ies'} now (≈20 min each). I'll show you the covers."); continue
        if text.startswith("/idea"):
            idea = text[5:].strip()
            if idea: stories = max(stories, 1); T.send(chat, f"💡 Got it — Claude will write this one now (≈30 min), if it passes the rules:\n<i>{T.esc(idea)}</i>")
            else: T.send(chat, "Send it like this: <code>/idea Holbein, The Ambassadors — the hidden skull</code>")
            continue
        if text.startswith("/pause") or text.startswith("/resume"):
            cfg = jload("config.json", {}); cfg["paused"] = text.startswith("/pause"); jsave("config.json", cfg)
            T.send(chat, "⏸ Paused: nothing will be written, rendered or posted." if cfg["paused"] else "▶️ Resumed."); continue
        if text.startswith("/rule"):
            rule = text[5:].strip()
            if rule:
                pb = os.path.join(ROOT, "PLAYBOOK.md"); txt = open(pb).read()
                txt = txt.replace("<!-- new rules go here -->", f"- ({today()}) {rule}\n<!-- new rules go here -->")
                open(pb, "w").write(txt); T.send(chat, f"📌 Added to the playbook for every future reel:\n<i>{T.esc(rule)}</i>")
            continue
        target = bs.get("awaiting") or (pending()[0] if pending() else None)
        if not target:
            T.send(chat, "Nothing is waiting for review right now.\n\n" + HELP); continue
        if not bs.get("awaiting") and low in YES: approve(chat, target, state(target).get("review_message")); continue
        if not bs.get("awaiting") and low in NO: skip(chat, target, state(target).get("review_message")); continue
        fb = state(target).get("feedback", []) + [text]
        set_state(target, status="revising", feedback=fb); bs["awaiting"] = None
        revise.append({"slug": target, "feedback": text})
        T.send(chat, f"✏️ Got it — reworking <b>{T.esc(title_of(target))}</b>:\n<i>{T.esc(text)}</i>\nThe new version arrives in ≈40 min.")
    jsave(BS, bs)
    if emit: gh_output(revise=json.dumps(revise), post_now="1" if post_now else "", stories=str(stories) if stories else "", idea=idea.replace("\n", " "))
    return {"revise": revise, "post_now": post_now, "stories": stories, "idea": idea}


# ---------------------------------------------------------------- learning loop (lab briefs, TikTok screenshots)
def save_screenshot(chat, msg):
    """a TikTok analytics screenshot -> private data release, read by the next brief"""
    import release, urllib.request
    fid = (msg["photo"][-1] if msg.get("photo") else msg["document"])["file_id"]
    path = T.call("getFile", {"file_id": fid})["file_path"]
    data = urllib.request.urlopen(f"{T.BASE}/file/bot{os.environ['TELEGRAM_BOT_TOKEN'].strip()}/{path}", timeout=60).read()
    name = f"tiktok-{now().strftime('%Y-%m-%dT%H%M%S')}-{fid[-6:]}.jpg"
    try: release.data_put(name, data, "image/jpeg")
    except SystemExit as e: T.send(chat, f"⚠️ Couldn't store the screenshot: {T.esc(str(e)[:200])}"); return
    T.send(chat, "📊 Got it. Those TikTok numbers go into the next brief (Mon/Thu).")


def _brief(d):
    import release
    if not d:
        names = sorted(release.data_list("brief-"))
        if not names: return None, None
        d = names[-1][len("brief-"):-len(".json")]
    raw = release.data_get(f"brief-{d}.json")
    return (d, json.loads(raw)) if raw else (d, None)


def send_brief(d):
    """the lab's brief: a summary, then one message per proposal with ✅ / ❌"""
    d, b = _brief(d)
    if not b: T.send(chat_id(), "No brief yet. The first one comes on the next Monday or Thursday."); return
    T.send(chat_id(), f"🧪 <b>Brief · {nice_date(d)}</b>\n\n{T.esc(b.get('summary', ''))}")
    for p in b.get("proposals", []):
        dec = p.get("decision")
        txt = (f"<b>{T.esc(p['id'])} · {T.esc(p.get('title', ''))}</b>"
               + (f"  <i>({'test' if p.get('kind') == 'experiment' else 'rule'}, confidence: {T.esc(p.get('confidence', '?'))})</i>")
               + f"\n\n<b>Change:</b> {T.esc(p.get('change', ''))}\n<b>Why:</b> {T.esc(p.get('why', ''))}"
               + (f"\n<b>Data:</b> {T.esc(p['evidence'])}" if p.get("evidence") else "")
               + (f"\n\n{'✅ applied' if dec == 'yes' else '❌ dropped'}" if dec else ""))
        kb = None if dec else [[{"text": "✅ Apply", "callback_data": f"lab:{d}:{p['id']}:y"},
                                {"text": "❌ No", "callback_data": f"lab:{d}:{p['id']}:n"}]]
        T.send(chat_id(), txt, kb)


def decide_proposal(chat, d, pid, yes, message_id=None):
    import release
    d, b = _brief(d)
    p = next((x for x in (b or {}).get("proposals", []) if x["id"] == pid), None)
    if not p: T.send(chat, "That proposal isn't in the brief any more."); return
    if p.get("decision"):
        T.send(chat, f"{pid} was already {'applied' if p['decision'] == 'yes' else 'dropped'}."); return
    p["decision"] = "yes" if yes else "no"; p["decided_at"] = now().isoformat(timespec="seconds")
    if yes:
        if p.get("kind") == "experiment": start_experiment(d, p)
        else:
            pb = os.path.join(ROOT, "PLAYBOOK.md"); txt = open(pb).read()
            line = f"- ({today()}, from data · brief {d} {pid}) {p['change']}"
            txt = txt.replace("<!-- new rules go here -->", line + "\n<!-- new rules go here -->"); open(pb, "w").write(txt)
            if p.get("concludes"): finish_experiment(p["concludes"], f"{p['change']} (brief {d})")
    release.data_put(f"brief-{d}.json", json.dumps(b, indent=1, ensure_ascii=False).encode())
    if message_id:
        try: T.buttons_only(chat, message_id, [[{"text": "✅ applied" if yes else "❌ dropped", "callback_data": "noop"}]])
        except Exception: pass
    T.send(chat, ("🧪 Test started: tonight's stories alternate the two versions." if p.get("kind") == "experiment"
                  else "📌 In the playbook: every new reel follows it from tonight.") if yes else f"❌ {pid} dropped.")


EXP = "EXPERIMENTS.md"


def start_experiment(d, p):
    e = p.get("experiment") or {}
    path = os.path.join(ROOT, EXP); txt = open(path).read() if os.path.exists(path) else ""
    row = (f"| {e.get('id', p['id'])} | {e.get('question', p.get('title', ''))} | {e.get('a', '')} | {e.get('b', '')} | "
           f"{e.get('metric', '')} | {today()} | {e.get('reels', 14)} reels |")
    txt = txt.replace("<!-- running -->", row + "\n<!-- running -->"); open(path, "w").write(txt)


def finish_experiment(eid, result):
    path = os.path.join(ROOT, EXP)
    if not os.path.exists(path): return
    lines = open(path).read().split("\n"); keep, done = [], None
    for l in lines:
        if l.startswith(f"| {eid} |") and done is None: done = l; continue
        keep.append(l)
    txt = "\n".join(keep)
    if done: txt = txt.replace("<!-- finished -->", done.rstrip(" |") + f" | {today()}: {result} |\n<!-- finished -->")
    open(path, "w").write(txt)


def _git(*a):
    import subprocess
    return subprocess.run(list(a), cwd=ROOT, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def sync():
    """pick up what other jobs pushed meanwhile (new reels sent for review, revisions, posts) before acting on a tap"""
    if os.path.isdir(os.path.join(ROOT, ".git")):
        br = os.environ.get("GITHUB_REF_NAME", "main")
        _git("git", "fetch", "-q", "--depth=50", "origin", br); _git("git", "rebase", "-q", "--autostash", f"origin/{br}")
    global CONFIG
    CONFIG.clear(); CONFIG.update(jload("config.json", {}))


def listen(minutes):
    """Stay on the line for `minutes`: Telegram long polling, so a button or a message gets an answer within seconds
    (GitHub's schedule only starts this workflow about once an hour). Revisions and new stories start at once; when an
    approved reel is due (or /post), stop so the workflow's publish job runs right away."""
    import subprocess, time
    import publish
    if not os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():
        print("Telegram not set up yet (secret TELEGRAM_BOT_TOKEN)"); gh_output(revise="[]", post_now="", stories="", idea=""); return
    end = time.time() + float(minutes) * 60; post_now = False; last_sync = 0
    while True:
        if time.time() - last_sync > 300: sync(); last_sync = time.time()
        nudge()
        if publish.due() or post_now: break
        left = end - time.time()
        if left <= 0: break
        if not T.updates(bstate().get("offset", 0), wait=min(25, max(1, left))): continue
        sync(); last_sync = time.time()
        r = poll(emit=False)
        post_now = post_now or r.get("post_now", False)
        for x in r.get("revise", []):
            subprocess.run(["gh", "workflow", "run", "revise.yml", "-f", f"slug={x['slug']}", "-f", f"feedback={x['feedback']}"], check=False)
        if r.get("stories"):
            subprocess.run(["gh", "workflow", "run", "stories.yml", "-f", f"count={r['stories']}", "-f", f"idea={r.get('idea', '')}"], check=False)
        if os.path.isdir(os.path.join(ROOT, ".git")):   # save the new state now, so other jobs see your answer
            subprocess.run([os.path.join(ROOT, "automation", "commit.sh"), f"inbox {now().strftime('%Y-%m-%dT%H:%M')}"], cwd=ROOT, check=False)
    gh_output(revise="[]", post_now="1" if post_now else "", stories="", idea="")


def nudge():
    """one reminder ~1 h before each posting slot if that slot's reel is still waiting for an answer"""
    if CONFIG.get("paused") or not chat_id(): return
    n = now(); hm = n.strftime("%H:%M")
    for e in schedule():
        if e["date"] != today(): continue
        s = state(e["slug"]); t = slot_time(e["slug"])
        h, m = map(int, t.split(":")); lead = (n.replace(hour=h, minute=m, second=0, microsecond=0) - n).total_seconds() / 60
        if s["status"] == "sent" and not s.get("nudged") and 30 <= lead <= 60:
            T.send(chat_id(), f"⏰ The {t} reel is still waiting for you: {T.esc(title_of(e['slug']))}\n"
                              f"Approve it and it goes out at {t} (buttons on the video above).")
            set_state(e["slug"], nudged=True)


def plan():
    chat = chat_id(); items = []
    for e in upcoming(("draft", "built", "sent", "approved")):
        cov = os.path.join(out_dir(e["slug"]), "cover.jpg")
        if os.path.exists(cov): items.append((cov, f"{nice_date(e['date'])} — {T.esc(title_of(e['slug']))}"))
    if len(items) >= 2: T.album(chat, items[:10])
    elif items: T.photo(chat, *items[0])
    T.send(chat, "🗓 " + status_text())


def posted(slug):
    s, c = state(slug), captions(slug); lines = [f"📣 <b>Posted:</b> {T.esc(title_of(slug))}"]
    for k, name in (("instagram", "Instagram"), ("youtube", "YouTube"), ("tiktok", "TikTok")):
        r = s.get(k) or {}
        if r.get("url"): lines.append(f"• {name}: {r['url']}")
        elif r.get("mode") == "inbox": lines.append(f"• {name}: draft is in your TikTok inbox — open TikTok, tap the notification, paste the caption below, post")
        elif r.get("error"): lines.append(f"• {name}: ⚠️ {T.esc(r['error'][:200])}")
        elif r.get("manual"): lines.append(f"• {name}: 📲 not connected yet — file + caption below, post it by hand")
        elif r.get("skipped"): lines.append(f"• {name}: off ({T.esc(r['skipped'])})")
    T.send(chat_id(), "\n".join(lines))
    if (s.get("tiktok") or {}).get("mode") == "inbox":
        T.send(chat_id(), f"<code>{T.esc(c['tiktok'][:2000])}</code>")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "review": review(sys.argv[2], "--revised" in sys.argv)
    elif cmd == "poll": poll(); nudge()
    elif cmd == "listen": listen(sys.argv[2] if len(sys.argv) > 2 else 45)
    elif cmd == "plan": plan()
    elif cmd == "brief": send_brief(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "posted": posted(sys.argv[2])
    elif cmd == "say":
        if chat_id(): T.send(chat_id(), sys.argv[2])
        else: print("no chat linked; message was:", sys.argv[2])
    else: raise SystemExit(__doc__)
