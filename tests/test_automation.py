"""End-to-end test of the automation against local mock APIs (no real accounts needed).

usage: python tests/test_automation.py <dir with a finished reel's out/ files> [<slug of that reel>]
Copies the repo to a temp folder, fakes two built reels from those files, then walks through a few days:
plan -> release upload/download -> Telegram review -> approve / change request / yes -> publish window -> posted.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from mock_apis import MockAPIs, CALLS, STATE

src_out = os.path.abspath(sys.argv[1]); src_slug = sys.argv[2] if len(sys.argv) > 2 else "night-watch-cut"
srv = MockAPIs().start()
tmp = tempfile.mkdtemp(prefix="dps-test-"); W = os.path.join(tmp, "repo")
shutil.copytree(REPO, W, ignore=shutil.ignore_patterns("node_modules", "models", "build", ".git", "public"))
for f in ("automation/bot_state.json", "schedule.json"):   # start from a clean slate, not the live system's state
    if os.path.exists(os.path.join(W, f)): os.remove(os.path.join(W, f))
bin_dir = os.path.join(tmp, "bin"); os.makedirs(bin_dir)
open(os.path.join(bin_dir, "gh"), "w").write("#!/bin/sh\necho \"gh $*\" >> %s/gh.log\ncase \"$*\" in *\"secret set\"*) cat >> %s/gh.log;; esac\necho >> %s/gh.log\n" % (tmp, tmp, tmp))
os.chmod(os.path.join(bin_dir, "gh"), 0o755)

ENV = {**os.environ, "PATH": bin_dir + ":" + os.environ["PATH"], "TELEGRAM_API": srv.url, "TELEGRAM_BOT_TOKEN": "123:abc",
       "TELEGRAM_CHAT_ID": "42", "IG_API": srv.url, "IG_ACCESS_TOKEN": "IGOLD", "YT_OAUTH": srv.url, "YT_API": srv.url,
       "YT_CLIENT_ID": "cid", "YT_CLIENT_SECRET": "cs", "YT_REFRESH_TOKEN": "rt", "TIKTOK_API": srv.url, "TIKTOK_CLIENT_KEY": "ck",
       "TIKTOK_CLIENT_SECRET": "tcs", "TIKTOK_REFRESH_TOKEN": "rft.OLD", "GITHUB_API_URL": srv.url, "GITHUB_REPOSITORY": "o/r",
       "GITHUB_TOKEN": "ghs_test", "GH_PAT": "github_pat_test", "POLL_SECONDS": "0.05", "GITHUB_OUTPUT": os.path.join(tmp, "out.txt")}
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
run("automation/plan.py", "add", "test-a", now="2026-11-01T02:30"); run("automation/plan.py", "add", "test-b", now="2026-11-01T02:31")
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
        "lines": [{"perf": [["*Nobody* was ever supposed to see *this.*", 0.6, 0.93]]}]}
bad = {"hook_type": "insane", "tail": 1.0, "lines": [{"perf": [["One morning in 1911,", 0.3, 0.95], ["a man walked out of the Louvre...", 0.4, 0.95], ["with *this* under his smock.", 0.8, 0.9]]}]}
check(V.hook_problems(good) == [], "a one-line hook with type + teaser passes")
pb = " | ".join(V.hook_problems(bad))
check(all(k in pb for k in ("hook_type", "teaser missing", "words", "date or a scene-setting", "tail")), "date opening, long hook, no type/teaser, short tail: all caught")
sd = os.path.join(tmp, "vis"); os.makedirs(os.path.join(sd, "build"))
json.dump({"lines": [{"e": 3.0}]}, open(os.path.join(sd, "build", "timeline.json"), "w"))
def shots_ok(shots, nude=False, zoom=1.0):
    json.dump({"shots": shots}, open(os.path.join(sd, "build", "resolved.json"), "w"))
    return V.visual_problems({"meta": {"image": "main", "nude": nude}, "cover": {"zoom": zoom}}, sd)
check(shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2.5], "to": [0.5, 0.3, 2.7]}, {"t": 3.1, "img": "photo", "gray": 1, "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}]) == [],
      "opening on a painting close-up, archive after the hook: passes")
check(any("open on the painting" in p for p in shots_ok([{"t": 0, "img": "photo", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}])), "opening on an archive photo: rejected")
check(any("until the hook ends" in p for p in shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2], "to": [0.5, 0.3, 2]}, {"t": 1.5, "img": "photo", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1]}])),
      "archive image during the hook: rejected")
check(len([p for p in shots_ok([{"t": 0, "img": "main", "from": [0.5, 0.3, 2], "to": [0.5, 0.3, 2]}, {"t": 4, "img": "main", "from": [0.5, 0.5, 1], "to": [0.5, 0.5, 1.05]}], nude=True) if "nude" in p]) == 2,
      "nude: wide shot and wide cover rejected")

print(f"\n{'ALL GOOD' if not fails else str(len(fails)) + ' FAILED'} — temp repo: {W}")
sys.exit(1 if fails else 0)
