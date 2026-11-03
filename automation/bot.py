"""The Telegram review bot: sends each reel for review and reads your answers.

usage:
  python automation/bot.py review <slug> [--revised]   cover + 540p video with ✅ Publish / ❌ Skip / ✏️ Changes + captions + facts
  python automation/bot.py poll                        read button presses and messages -> update states; step outputs:
                                                         revise=[{"slug","feedback"}]  post_now=1  stories=<n>
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
The chat is linked the first time someone sends /start (or set TELEGRAM_CHAT_ID).
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import telegram as T
from common import (CONFIG, ROOT, captions, date_for, gh_output, jload, jsave, now, out_dir, schedule, set_state, state, story,
                    title_of, today, upcoming)

BS = "automation/bot_state.json"
YES = {"yes", "y", "ok", "okay", "sí", "si", "yep", "yeah", "publish", "post it", "go", "approve", "approved", "👍", "✅", "dale", "vale"}
NO = {"no", "skip", "nope", "❌", "👎", "descartar"}


def bstate(): return jload(BS, {"offset": 0, "chat_id": None, "awaiting": None})
def chat_id(): return os.environ.get("TELEGRAM_CHAT_ID", "").strip() or bstate().get("chat_id")


def when_text(slug):
    """human 'when will this go out' for an approved reel"""
    d = date_for(slug) or today(); w0, w1 = CONFIG["publish_window"]
    if d > today():
        return f"on {datetime.date.fromisoformat(d).strftime('%a %d %b')} at {w0}"
    hm = now().strftime("%H:%M")
    if hm < w0: return f"today at {w0}"
    if hm <= w1: return "within the next 15 minutes"
    return f"tomorrow at {w0}"


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
            if revised else f"🎨 <b>Reel for {nice_date(date_for(slug))}</b>")
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
        "/rule &lt;text&gt; — a rule for all future reels\n/pause, /resume\n\nOn a reel: ✅ / ❌ / ✏️ buttons, or just reply "
        "<i>yes</i>, <i>no</i>, or what you want changed.")


def poll(emit=True):
    bs = bstate(); chat = chat_id(); revise, post_now, stories, idea = [], False, 0, ""
    if not os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():          # not set up yet: stay quiet instead of failing
        print("Telegram not set up yet (secret TELEGRAM_BOT_TOKEN)"); gh_output(revise="[]", post_now="", stories="", idea=""); return {}
    for u in T.updates(bs.get("offset", 0)):
        bs["offset"] = u["update_id"] + 1
        if "callback_query" in u:
            q = u["callback_query"]; cid = str(q["message"]["chat"]["id"])
            if cid != str(chat): T.answer(q["id"]); continue
            act, _, slug = q.get("data", "").partition(":")
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
        if not text: continue
        if not chat and msg.get("chat", {}).get("type") == "private" and text.startswith("/start"):
            chat = bs["chat_id"] = cid
            T.send(chat, "🖤 Linked. This chat will get every reel for review.\n\n" + HELP); continue
        if cid != str(chat): continue
        low = text.lower().strip(" .!")
        if text.startswith("/start") or text.startswith("/help"): T.send(chat, HELP); continue
        if text.startswith("/status"): T.send(chat, status_text()); continue
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
    """17:30: one reminder if today's reel is still waiting for an answer"""
    hm = now().strftime("%H:%M")
    if not ("17:30" <= hm <= "17:59") or CONFIG.get("paused") or not chat_id(): return
    for e in schedule():
        s = state(e["slug"])
        if e["date"] == today() and s["status"] == "sent" and not s.get("nudged"):
            T.send(chat_id(), f"⏰ Today's reel is still waiting for you: {T.esc(title_of(e['slug']))}\n"
                              f"Approve it before {CONFIG['publish_window'][1]} and it goes out today (buttons on the video above).")
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
    elif cmd == "posted": posted(sys.argv[2])
    elif cmd == "say":
        if chat_id(): T.send(chat_id(), sys.argv[2])
        else: print("no chat linked; message was:", sys.argv[2])
    else: raise SystemExit(__doc__)
