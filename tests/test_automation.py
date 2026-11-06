"""End-to-end test of the automation against local mock APIs (no real accounts needed).

usage: python tests/test_automation.py <dir with a finished reel's out/ files> [<slug of that reel>]
Copies the repo to a temp folder, fakes two built reels from those files, then walks through a few days:
plan -> release upload/download -> Telegram review -> approve / change request / yes -> publish window -> posted.
"""
import csv, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from mock_apis import MockAPIs, CALLS, STATE

src_out = os.path.abspath(sys.argv[1]); src_slug = sys.argv[2] if len(sys.argv) > 2 else "night-watch-cut"
srv = MockAPIs().start()
tmp = tempfile.mkdtemp(prefix="dps-test-"); W = os.path.join(tmp, "repo")
shutil.copytree(REPO, W, ignore=shutil.ignore_patterns("node_modules", "models", "build", ".git", "public"))
for f in ("automation/bot_state.json", "schedule.json"):   # start from a clean slate, not the live system's state
    if os.path.exists(os.path.join(W, f)): os.remove(os.path.join(W, f))
def set_cfg(**kv):
    c = json.load(open(os.path.join(W, "config.json"))); c.update(kv); json.dump(c, open(os.path.join(W, "config.json"), "w"), indent=1)
set_cfg(slots=["18:00"], publish_until="22:30", stories_per_run=2, paused=False)   # sections 1-12: one reel a day at 18:00
bin_dir = os.path.join(tmp, "bin"); os.makedirs(bin_dir)
open(os.path.join(bin_dir, "gh"), "w").write("#!/bin/sh\necho \"gh $*\" >> %s/gh.log\ncase \"$*\" in *\"secret set\"*) cat >> %s/gh.log;; esac\necho >> %s/gh.log\n" % (tmp, tmp, tmp))
os.chmod(os.path.join(bin_dir, "gh"), 0o755)

ENV = {**os.environ, "PATH": bin_dir + ":" + os.environ["PATH"], "TELEGRAM_API": srv.url, "TELEGRAM_BOT_TOKEN": "123:abc",
       "TELEGRAM_CHAT_ID": "42", "IG_API": srv.url, "IG_ACCESS_TOKEN": "IGOLD", "YT_OAUTH": srv.url, "YT_API": srv.url, "YT_ANALYTICS_API": srv.url,
       "YT_CLIENT_ID": "cid", "YT_CLIENT_SECRET": "cs", "YT_REFRESH_TOKEN": "rt", "TIKTOK_API": srv.url, "TIKTOK_CLIENT_KEY": "ck",
       "TIKTOK_CLIENT_SECRET": "tcs", "TIKTOK_REFRESH_TOKEN": "rft.OLD", "GITHUB_API_URL": srv.url, "GITHUB_REPOSITORY": "o/r",
       "GITHUB_TOKEN": "ghs_test", "GH_PAT": "github_pat_test", "CLAUDE_CODE_OAUTH_TOKEN": "sk-ant-oat01-test\nwrapped", "POLL_SECONDS": "0.05", "GITHUB_OUTPUT": os.path.join(tmp, "out.txt")}
fails = []


def run(*args, now=None, ok=True):
    open(ENV["GITHUB_OUTPUT"], "w").close()
    r = subprocess.run(["python3", *args], cwd=W, env={**ENV, **({"DPS_NOW": now} if now else {})}, capture_output=True, text=True)
    if ok and r.returncode: print(r.stdout, r.stderr); raise SystemExit(f"FAILED: {' '.join(args)}")
    outs = dict(l.split("=", 1) for l in open(ENV["GITHUB_OUTPUT"]).read().splitlines() if "=" in l)
    return r, outs


def check(cond, what):
    print(("  ✅ " if cond else "  ❌ ") + what)
    if not cond: fails.append(what)


def state(slug): return json.load(open(os.path.join(W, "stories", slug, "state.json")))


def fake_story(slug, painter):
    d = os.path.join(W, "stories", slug); os.makedirs(os.path.join(d, "out"), exist_ok=True)
    st = json.load(open(os.path.join(W, "stories", src_slug, "story.json"))); st["slug"] = slug; st["meta"]["painter"] = painter
    json.dump(st, open(os.path.join(d, "story.json"), "w"))
    for f in os.listdir(src_out):
        if f.endswith((".mp4", ".jpg", ".txt")): shutil.copy(os.path.join(src_out, f), os.path.join(d, "out", f.replace(src_slug, slug)))
    json.dump({"status": "draft"}, open(os.path.join(d, "state.json"), "w"))


print("\n1. Planning")
fake_story("test-a", "Painter A"); fake_story("test-b", "Painter B")
_, o = run("automation/plan.py", "needed", now="2026-11-01T02:20"); check(o.get("n") == "2", f"buffer empty -> write 2 per night (got {o.get('n')})")
run("automation/plan.py", "add", "test-a", now="2026-11-01T10:30"); run("automation/plan.py", "add", "test-b", now="2026-11-01T10:31")
sch = json.load(open(os.path.join(W, "schedule.json")))
check([e["date"] for e in sch] == ["2026-11-02", "2026-11-03"], f"scheduled on the next free days: {sch}")
_, o = run("automation/plan.py", "needed", now="2026-11-01T02:40"); check(o.get("n") == "1", f"2 ready of 3 -> 1 more (got {o.get('n')})")
_, o = run("automation/plan.py", "today", now="2026-11-02T07:41"); check(o.get("slug") == "test-a", "morning build picks today's reel")

print("\n2. Draft release round trip (no token leak on the signed download URL)")
run("automation/release.py", "upload", "test-a")
names = [a["name"] for a in STATE["releases"][0]["assets"]]
check("test-a.mp4" in names and "cover.jpg" in names and STATE["releases"][0]["draft"], f"draft release with {len(names)} files")
os.remove(os.path.join(W, "stories/test-a/out/test-a.mp4"))
run("automation/release.py", "download", "test-a")
check(os.path.getsize(os.path.join(W, "stories/test-a/out/test-a.mp4")) == os.path.getsize(os.path.join(src_out, f"{src_slug}.mp4")), "master downloaded intact")
for f in ("test-a.mp4", "stills.jpg", "qa.txt"):
    if os.path.exists(os.path.join(W, "stories/test-a/out", f)): os.remove(os.path.join(W, "stories/test-a/out", f))
run("automation/release.py", "download-publish", "test-a")
check(os.path.exists(os.path.join(W, "stories/test-a/out/test-a.mp4")) and not os.path.exists(os.path.join(W, "stories/test-a/out/qa.txt")),
      "publishing fetches only the video, cover and captions")

print("\n3. Review on Telegram")
run("automation/bot.py", "review", "test-a", now="2026-11-02T08:05")
v = srv.tg("sendVideo")[-1]["body"]; kb = json.loads(v["reply_markup"])["inline_keyboard"]
check(srv.tg("sendPhoto") and "preview" in v["video"], "cover photo + 540p preview sent")
check([b["callback_data"] for row in kb for b in row] == ["ok:test-a", "no:test-a", "ch:test-a"], "✅ / ❌ / ✏️ buttons")
check("Instagram caption" in srv.tg("sendMessage")[-1]["body"]["text"], "captions + facts message")
check(state("test-a")["status"] == "sent", "state = sent")

print("\n4. You press ✅ at 09:12 -> approved, posts at 18:00")
srv.push({"callback_query": {"id": "cb1", "data": "ok:test-a", "message": {"message_id": 101, "chat": {"id": 42}}}})
srv.push({"message": {"chat": {"id": 999, "type": "private"}, "text": "yes"}})        # a stranger: ignored
_, o = run("automation/bot.py", "poll", now="2026-11-02T09:12")
check(state("test-a")["status"] == "approved", "approved")
check("today at 18:00" in srv.tg("sendMessage")[-1]["body"]["text"], "bot says when it will go out")
_, o = run("automation/publish.py", "decide", now="2026-11-02T12:00"); check(o.get("slug") == "", "noon: outside the window -> nothing")
_, o = run("automation/publish.py", "decide", now="2026-11-02T18:04"); check(o.get("slug") == "test-a", "18:04: publish test-a")

print("\n5. Publishing (Instagram via public URL, YouTube, TikTok inbox)")
run("automation/publish.py", "run", "test-a", "https://o.github.io/r/", now="2026-11-02T18:06")
s = state("test-a")
check(s["status"] == "posted", "state = posted")
check(s["instagram"]["url"].startswith("https://www.instagram.com/reel/"), "Instagram permalink stored")
ig = srv.calls("/me/media")[0]["body"]
check(ig["video_url"] == "https://o.github.io/r/media/test-a.mp4" and ig["cover_url"].endswith("test-a-cover.jpg") and ig["media_type"] == "REELS", "IG container: REELS + video_url + cover_url")
check(ig["caption"].startswith("In 1715") and "#rembrandt" in ig["caption"], "IG caption = Instagram section of caption.txt")
yt = srv.calls("/upload/youtube/v3/videos")[0]["body"]
check(yt["status"]["containsSyntheticMedia"] is True and yt["snippet"]["title"].endswith("#shorts"), "YouTube: title + AI disclosure")
check(srv.calls("/yt-session/1")[0]["size"] == os.path.getsize(os.path.join(src_out, f"{src_slug}.mp4")), "YouTube got the whole file")
puts = srv.calls("/tt-upload/1"); total = sum(c["size"] for c in puts)
check(total == os.path.getsize(os.path.join(src_out, f"{src_slug}.mp4")) and all("Content-Range" in c["headers"] for c in puts), f"TikTok upload complete in {len(puts)} chunk(s)")
check(s["tiktok"]["mode"] == "inbox", "TikTok in inbox (draft) mode")
gh = open(os.path.join(tmp, "gh.log")).read()
check("gh secret set TIKTOK_REFRESH_TOKEN" in gh and "rft.NEW" in gh, "rotated TikTok refresh token saved via GH_PAT (stdin)")
msgs = [c["body"]["text"] for c in srv.tg("sendMessage")[-2:]]
check("Posted" in msgs[0] and "youtube.com/shorts/YTVID1" in msgs[0] and msgs[1].startswith("<code>"), "Telegram: links + TikTok caption to paste")
_, o = run("automation/publish.py", "decide", now="2026-11-02T18:30"); check(o.get("slug") == "", "never twice: nothing left to post today")
n_ig = len(srv.calls("/me/media_publish")); run("automation/publish.py", "run", "test-a", "https://o.github.io/r/", now="2026-11-02T18:31")
check(len(srv.calls("/me/media_publish")) == n_ig, "re-running publish does not post again")

print("\n6. Next day: ✏️ change request, then 'yes'")
run("automation/bot.py", "review", "test-b", now="2026-11-03T08:05")
srv.push({"callback_query": {"id": "cb2", "data": "ch:test-b", "message": {"message_id": 102, "chat": {"id": 42}}}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "Make the hook shorter and slow down the ending"}})
_, o = run("automation/bot.py", "poll", now="2026-11-03T09:00")
rv = json.loads(o.get("revise", "[]"))
check(rv == [{"slug": "test-b", "feedback": "Make the hook shorter and slow down the ending"}], "change request -> revise workflow input")
check(state("test-b")["status"] == "revising", "state = revising")
json.dump({**state("test-b"), "status": "sent"}, open(os.path.join(W, "stories/test-b/state.json"), "w"))   # (revise workflow re-sends)
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "Yes!"}})
run("automation/bot.py", "poll", now="2026-11-03T10:00")
check(state("test-b")["status"] == "approved", "'Yes!' approves the reel waiting for review")

print("\n7. Commands")
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/status"}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/rule Never use maps"}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/stories 3"}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/post"}})
_, o = run("automation/bot.py", "poll", now="2026-11-03T11:00")
check("Schedule" in [c["body"]["text"] for c in srv.tg("sendMessage")][-4], "/status lists the schedule")
check("Never use maps" in open(os.path.join(W, "PLAYBOOK.md")).read(), "/rule appended to PLAYBOOK.md")
check(o.get("stories") == "3" and o.get("post_now") == "1", "/stories 3 and /post become workflow actions")
_, o = run("automation/publish.py", "decide", "--now", now="2026-11-03T11:00"); check(o.get("slug") == "test-b", "/post publishes outside the window")
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/pause"}})
run("automation/bot.py", "poll", now="2026-11-03T11:15")
_, o = run("automation/plan.py", "needed", now="2026-11-04T02:20"); check(o.get("n") == "0", "/pause stops the story writer")

print("\n8. Missing platform secrets are skipped, not fatal")
fake_story("test-c", "Painter C"); json.dump({"status": "approved"}, open(os.path.join(W, "stories/test-c/state.json"), "w"))
env_keep = dict(ENV); [ENV.pop(k) for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN")]
run("automation/publish.py", "run", "test-c", "https://o.github.io/r/", now="2026-11-04T18:05"); ENV.update(env_keep)
s = state("test-c"); check(s["status"] == "posted" and "not set up" in s["tiktok"]["skipped"], "TikTok not configured -> skipped, others posted")
doc = srv.tg("sendDocument")
check(doc and "1080p" in doc[-1]["body"]["document"] and s.get("manual_sent"), "…and a < 50 MB file + TikTok caption sent for posting by hand")
check(os.path.getsize(os.path.join(W, "stories/test-c/out/test-c-1080p.mp4")) < 48 * 1024 * 1024, "hand-posting file under the Telegram bot limit")

print("\n9. Setup check + Instagram token refresh")
r, _ = run("automation/setup_check.py", ok=False)
check("✅ | Instagram" in r.stdout and "✅ | YouTube" in r.stdout and "✅ | TikTok" in r.stdout and "✅ | Telegram bot" in r.stdout, "all connections green")
run("automation/instagram.py", "refresh")
check("gh secret set IG_ACCESS_TOKEN" in open(os.path.join(tmp, "gh.log")).read(), "new Instagram token saved via GH_PAT")

print("\n10. Captions parser")
sys.path.insert(0, os.path.join(W, "automation"))
os.chdir(W); import importlib, common; importlib.reload(common)
c = common.captions("test-a")
check(len(c["instagram"]) > 300 and c["youtube_title"].endswith("#shorts") and len(c["tiktok"]) < 300, "Instagram / TikTok / YouTube sections parsed")

print("\n11. Quality gate: week-1 rules (hook, opening shot, nudes)")
import validate as V
good = {"hook_type": "dark", "teaser": "The painting Goya hid on his wall", "tail": 2.2,
        "hashtags_instagram": ["#goya", "#saturn", "#arthistory", "#prado", "#darkart"], "hashtags_tiktok": ["#arthistory", "#arttok", "#goya", "#saturn", "#darkhistory"],
        "lines": [{"perf": [["*Nobody* was ever supposed to see *this.*", 0.6, 0.93]]}]}
bad = {"hook_type": "insane", "tail": 1.0, "lines": [{"perf": [["One morning in 1911,", 0.3, 0.95], ["a man walked out of the Louvre...", 0.4, 0.95], ["with *this* under his smock.", 0.8, 0.9]]}]}
check(V.hook_problems(good) == [], "a one-line hook with type + teaser passes")
bad["hashtags_tiktok"] = ["#a", "#b", "#c", "#d", "#e", "#f"]
pb = " | ".join(V.hook_problems(bad))
check(all(k in pb for k in ("hook_type", "teaser missing", "words", "date or a scene-setting", "tail", "hashtags_instagram missing", "(max 5)")), "date opening, long hook, no type/teaser, short tail, hashtags: all caught")
sd = os.path.join(tmp, "vis"); os.makedirs(os.path.join(sd, "build"))
json.dump({"lines": [{"e": 3.0}]}, open(os.path.join(sd, "build", "timeline.json"), "w"))
def shots_ok(shots, nude=False, span=0.6):
    json.dump({"shots": shots}, open(os.path.join(sd, "build", "resolved.json"), "w"))
    return V.visual_problems({"meta": {"image": "main", "nude": nude}, "cover": {"span": span}}, sd)
check(shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2.5], "to": [0.5, 0.3, 2.7]}, {"t": 3.1, "img": "photo", "gray": 1, "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}]) == [],
      "opening on a painting close-up, archive after the hook: passes")
check(any("open on the painting" in p for p in shots_ok([{"t": 0, "img": "photo", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}])), "opening on an archive photo: rejected")
check(any("until the hook ends" in p for p in shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2], "to": [0.5, 0.3, 2]}, {"t": 1.5, "img": "photo", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}])),
      "archive image during the hook: rejected")
check(len([p for p in shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2], "to": [0.5, 0.3, 2]}, {"t": 4, "img": "main", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1.05]}], nude=True) if "nude" in p]) == 2,
      "nude: wide shot and wide cover rejected")

print("\n11b. Instagram with a Facebook-login / system-user token (EAA…)")
r, _ = run("automation/instagram.py", "check")
ENV["IG_ACCESS_TOKEN"] = "EAAsystemuser"
r, _ = run("automation/instagram.py", "check")
check("thedeadpainterssociety" in r.stdout and "Facebook login" in r.stdout, "EAA token: finds the Instagram account through the Facebook Page")
r, _ = run("automation/instagram.py", "publish", "test-a", "https://o.github.io/r/media/test-a.mp4")
check("instagram.com/reel/" in r.stdout and srv.calls("/17841/media"), "EAA token: publishes as the business account")
r, _ = run("automation/instagram.py", "refresh"); check("nothing to refresh" in r.stdout, "EAA token: no refresh needed")
STATE["no_pages"] = True; r, _ = run("automation/instagram.py", "check"); STATE["no_pages"] = False
check("from the token's permissions" in r.stdout and "thedeadpainterssociety" in r.stdout, "system-user token without a Page: account found from the token")
ENV["IG_ACCESS_TOKEN"] = "IGOLD"

print("\n12. Listening mode: a tap is answered at once, a due reel stops the listener")
import time as _t
fake_story("test-l", "Painter L")
cfg = json.load(open(os.path.join(W, "config.json"))); cfg["paused"] = False; json.dump(cfg, open(os.path.join(W, "config.json"), "w"))   # section 7 paused it
sch = json.load(open(os.path.join(W, "schedule.json"))); sch.append({"date": "2026-11-09", "slug": "test-l"})
json.dump(sch, open(os.path.join(W, "schedule.json"), "w"))
json.dump({"status": "sent", "sent_at": "2026-11-09T09:00:00+01:00"}, open(os.path.join(W, "stories", "test-l", "state.json"), "w"))
srv.push({"callback_query": {"id": "cbL", "data": "ok:test-l", "message": {"message_id": 140, "chat": {"id": 42}}}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "text": "/stories 2"}})
t0 = _t.time(); _, o = run("automation/bot.py", "listen", "0.03", now="2026-11-09T12:00")
check(state("test-l")["status"] == "approved" and any(c["body"].get("callback_query_id") == "cbL" for c in srv.tg("answerCallbackQuery")), "✅ tap answered and approved while listening")
check("workflow run stories.yml -f count=2" in open(os.path.join(tmp, "gh.log")).read(), "/stories starts the story writer straight away")
check(o.get("post_now") == "" and _t.time() - t0 < 30, "outside the window: listens until its time is up")
t0 = _t.time(); _, o = run("automation/bot.py", "listen", "5", now="2026-11-09T18:03")
check(_t.time() - t0 < 20, "18:03 with an approved reel: stops at once so the publish job runs")
_, o = run("automation/publish.py", "decide", now="2026-11-09T18:03"); check(o.get("slug") in ("test-l", "test-b"), "…and an approved reel is picked for publishing (oldest first)")

print("\n13. Two reels a day (14:00 and 21:00), pinned dates")
set_cfg(slots=["14:00", "21:00"], publish_until="23:00", stories_per_run=3, buffer_days=3, paused=False)
json.dump([], open(os.path.join(W, "schedule.json"), "w"))
for x in ("t2-a", "t2-b", "t2-c", "t2-pin"): fake_story(x, "Painter " + x)
_, o = run("automation/plan.py", "needed", now="2026-12-01T02:20"); check(o.get("n") == "3", f"empty buffer: 3 per run towards 6 ready (got {o.get('n')})")
for x in ("t2-a", "t2-b", "t2-c"): run("automation/plan.py", "add", x, now="2026-12-01T10:30")
sch = json.load(open(os.path.join(W, "schedule.json")))
check([e["date"] for e in sch] == ["2026-12-02", "2026-12-02", "2026-12-03"], f"two per day: {[(e['slug'], e['date']) for e in sch]}")
r, _ = run("automation/plan.py", "add", "t2-pin", "2026-12-02", now="2026-12-01T10:40")
sch = json.load(open(os.path.join(W, "schedule.json"))); day = [e["slug"] for e in sch if e["date"] == "2026-12-02"]
check("t2-pin" in day and len(day) == 2 and "t2-b" not in day, f"pinned onto a full day: the last unpinned reel moves on ({[(e['slug'], e['date']) for e in sch]})")
_, o = run("automation/plan.py", "today", now="2026-12-02T07:41"); check(json.loads(o.get("slugs", "[]")) == ["t2-a", "t2-pin"], f"morning: both of today's reels rendered ({o.get('slugs')})")
for x in ("t2-a", "t2-pin"): json.dump({"status": "approved"}, open(os.path.join(W, "stories", x, "state.json"), "w"))
_, o = run("automation/publish.py", "decide", now="2026-12-02T13:50"); check(o.get("slug") == "", "13:50: nothing yet")
_, o = run("automation/publish.py", "decide", now="2026-12-02T14:02"); check(o.get("slug") == "t2-a", "14:02: the first reel")
json.dump({"status": "posted", "posted_at": "2026-12-02T14:03:00+01:00"}, open(os.path.join(W, "stories", "t2-a", "state.json"), "w"))
_, o = run("automation/publish.py", "decide", now="2026-12-02T17:00"); check(o.get("slug") == "", "17:00: the second one waits for its slot")
_, o = run("automation/publish.py", "decide", now="2026-12-02T21:01"); check(o.get("slug") == "t2-pin", "21:01: the second reel")
json.dump({"status": "sent"}, open(os.path.join(W, "stories", "t2-pin", "state.json"), "w"))
n0 = len(srv.tg("sendMessage")); run("automation/bot.py", "poll", now="2026-12-02T20:15")
check(len(srv.tg("sendMessage")) > n0 and "21:00" in srv.tg("sendMessage")[-1]["body"]["text"], "20:15: reminder for the 21:00 reel still waiting")

print("\n14. A story written at night goes out the same day; the night run only re-checks its own stories")
fake_story("t3-night", "Painter N")
run("automation/plan.py", "add", "t3-night", now="2026-12-10T02:45")
sch = json.load(open(os.path.join(W, "schedule.json")))
check(any(e["slug"] == "t3-night" and e["date"] == "2026-12-10" for e in sch), "written at 02:45 -> scheduled today, not tomorrow")
json.dump({"status": "draft", "validated_at": "2026-12-09T03:00:00+01:00"}, open(os.path.join(W, "stories", "t2-c", "state.json"), "w"))
shutil.rmtree(os.path.join(W, "stories", "t2-c", "out"), ignore_errors=True)    # like a fresh runner: no files of older stories
r, o = run("automation/validate.py", now="2026-12-10T03:00")
check(state("t2-c")["status"] == "draft" and "t2-c" not in r.stdout, "an older, already-checked story is left alone")

print("\n15. Learning loop: metrics -> table -> brief -> ✅ applies it")
sch = json.load(open(os.path.join(W, "schedule.json")))
for i in range(5):
    x = f"t5-{i}"; fake_story(x, f"Painter {i}")
    sch.append({"date": "2026-12-20", "slug": x})
    json.dump({"status": "posted", "posted_at": "2026-12-20T14:00:00+01:00", "youtube": {"id": f"YT{i}"}, "instagram": {"id": f"IGM{i}"}},
              open(os.path.join(W, "stories", x, "state.json"), "w"))
json.dump(sch, open(os.path.join(W, "schedule.json"), "w"))
STATE["yt_views"] = {"YT0": 900, "YT1": 1000, "YT2": 1100, "YT3": 950, "YT4": 6000}
r, _ = run("automation/metrics.py", "collect", now="2026-12-21T10:00")          # 20 h after posting
check(r.returncode == 0 and re.search(r"collected \d+ reels", r.stdout) and "t5-4" in json.dumps(json.loads(STATE["assets"][max(a["id"] for rel in STATE["releases"] if rel["name"] == "dps-data" for a in rel["assets"] if a["name"] == "metrics.json")])["reels"]), f"collect: reels from YouTube + Instagram ({r.stdout[-160:]} {r.stderr[-200:]})")
r, _ = run("automation/metrics.py", "collect", now="2026-12-21T18:00")          # 28 h
check(any("taking off" in c["body"].get("text", "") for c in srv.tg("sendMessage")), "🔥 alert for the reel at 5× the usual views")
d = os.path.join(W, "lab"); r, _ = run("automation/metrics.py", "pull", d, now="2026-12-21T18:05")
m = json.load(open(os.path.join(d, "metrics.json")))
yt = m["reels"]["t5-4"]["youtube"]["snapshots"]; ig = m["reels"]["t5-4"]["instagram"]["snapshots"]
check(len(yt) == 2 and yt[-1]["avg_view_pct"] == 41.5 and ig[-1]["shares"] is not None and ig[-1]["avg_watch_s"] == 15.5,
      "snapshots carry views, % viewed, shares, saves, watch time")
r, _ = run("automation/metrics.py", "tiktok-add", "t5-1", '{"views": 2000, "likes": 90, "shares": 12, "watched_full_pct": 22.5}', d, now="2026-12-22T10:00")
r, _ = run("automation/metrics.py", "table", d)
rows = list(csv.DictReader(open(os.path.join(d, "table.csv"))))
r4 = next(x for x in rows if x["slug"] == "t5-4")
check(len(rows) >= 5 and r4["youtube_views_24h"] and r4["hook_type"] and rows and any(x.get("tiktok_views_24h") or x.get("tiktok_shares_saves_per_1k") for x in rows),
      f"table.csv: {len(rows)} reels, views at 24 h interpolated, TikTok numbers included")
STATE["yt_no_analytics"] = True; STATE["ig_no_insights"] = True
r, _ = run("automation/metrics.py", "collect", now="2026-12-21T21:00")
m = json.loads(STATE["assets"][max(a["id"] for rel in STATE["releases"] if rel["name"] == "dps-data" for a in rel["assets"] if a["name"] == "metrics.json")])
check("yt-analytics.readonly" in m["notes"].get("youtube_analytics", "") and "instagram_manage_insights" in m["notes"].get("instagram_insights", ""),
      "missing permissions are noted (and the brief will say what to do)")
STATE["yt_no_analytics"] = False; STATE["ig_no_insights"] = False
json.dump({"summary": "Two strong days. t5-4 did 6,000 views in a day.", "proposals": [
    {"kind": "rule", "title": "Open on the face", "change": "The first shot is a face close-up.", "why": "faces hold", "evidence": "n=5", "confidence": "medium"},
    {"kind": "experiment", "title": "Question vs statement hook", "change": "Alternate", "why": "unclear", "confidence": "low",
     "experiment": {"id": "E1", "question": "Question or statement hook?", "a": "hook as a question", "b": "hook as a statement", "metric": "YouTube avg % viewed"}}]},
          open(os.path.join(d, "brief.json"), "w"))
n0 = len(srv.tg("sendMessage")); r, _ = run("automation/lab.py", "publish", d, now="2026-12-24T10:20")
msgs = srv.tg("sendMessage")[n0:]
check(r.returncode == 0 and len(msgs) == 3 and "lab:2026-12-24:P1:y" in json.dumps(msgs[1]["body"]), f"brief sent: summary + 2 proposals with ✅/❌ ({r.stderr[-200:]})")
srv.push({"callback_query": {"id": "cbP1", "data": "lab:2026-12-24:P1:y", "message": {"message_id": 300, "chat": {"id": 42}}}})
srv.push({"callback_query": {"id": "cbP2", "data": "lab:2026-12-24:P2:y", "message": {"message_id": 301, "chat": {"id": 42}}}})
srv.push({"message": {"chat": {"id": 42, "type": "private"}, "photo": [{"file_id": "small"}, {"file_id": "AgACbigfile123"}]}})
run("automation/bot.py", "poll", now="2026-12-24T11:00")
pb = open(os.path.join(W, "PLAYBOOK.md")).read(); ex = open(os.path.join(W, "EXPERIMENTS.md")).read()
check("brief 2026-12-24 P1) The first shot is a face close-up." in pb, "✅ on a rule: added to the playbook")
check("| E1 | Question or statement hook? | hook as a question | hook as a statement |" in ex, "✅ on a test: it starts in EXPERIMENTS.md")
names = [a["name"] for rel in STATE["releases"] if rel["name"] == "dps-data" for a in rel["assets"]]
check(any(n.startswith("tiktok-") for n in names) and "brief-2026-12-24.json" in names, "TikTok screenshot and brief stored privately")
srv.push({"callback_query": {"id": "cbP1b", "data": "lab:2026-12-24:P1:y", "message": {"message_id": 300, "chat": {"id": 42}}}})
run("automation/bot.py", "poll", now="2026-12-24T11:05")
check(open(os.path.join(W, "PLAYBOOK.md")).read().count("The first shot is a face close-up.") == 1, "a second tap doesn't add it twice")

print(f"\n{'ALL GOOD' if not fails else str(len(fails)) + ' FAILED'} — temp repo: {W}")
sys.exit(1 if fails else 0)
