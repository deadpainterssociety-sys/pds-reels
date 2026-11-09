"""The cloned voice (Chatterbox): recordings in, test versions out, Gigi's pick becomes the channel's voice.

Recordings, reference clips and phrase caches live ONLY in the private data release (dps-data, a draft): the repo is
public, and a clean recording of someone's voice is enough to clone it.

  bot  -> intake(chat, msg)          a voice message / audio file sent to the bot -> voice-sample-<time>.<ext>; starts the
                                     voice workflow (mode test)
  bot  -> choose(chat, run, n, id)   a ✅ tap: that version's clip -> voice-ref.wav, its settings -> config.json voice_clone
  bot  -> status_text() / switch()   /voice, /voice on|off
  CI   sample [name] <file>          a stored recording (empty name = the latest)
       prep <dir> <run>              after pipeline/voice_ref.py: store the candidate clips, tell Gigi, print the matrix
       get-refs <run> <dir>          (one machine per version) the candidate clips
       send-one <dir> <run> <n>      that version -> Telegram with its ✅ button        test-done <run>   the closing note
       fetch-ref                     voice-ref.wav -> models/voice/ref.wav (setup action, when voice_clone is on)
  long videos (rendered by Claude outside CI, where Chatterbox can't run; voiced on N machines at once):
       park <slug>                   (Claude) story.json -> branch voice-in-<slug>, start the workflow (mode story)
       ci-in <slug>                  (CI) story.json + the cached phrases of earlier runs
       shard-put <slug> <run> <k>    (CI, machine k) its new phrases     shard-get <slug> <run>  (CI) all of them
       ci-out <slug>                 (CI) voice-out-<slug>.tar + voice-cache-<slug>.tar, delete the branch
       unpark <slug>                 (Claude) voice-out-<slug>.tar -> stories/<slug>/build/
"""
import datetime, glob, hashlib, json, os, shutil, subprocess, sys, tempfile, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, jload, jsave, now, today

REF = os.path.join(ROOT, "models", "voice", "ref.wav")
TEST_STORY = "gericault-medusa"


def T():
    import telegram
    return telegram


def R():
    import release
    return release


def dispatch(**inputs):
    """start the voice workflow (REST call: works from CI and from Claude's session)"""
    args = [x for k, v in inputs.items() for x in ("-F", f"inputs[{k}]={v}")]
    return subprocess.run(["gh", "api", "-X", "POST", "repos/{owner}/{repo}/actions/workflows/voice.yml/dispatches", "-f", "ref=main", *args],
                          cwd=ROOT, capture_output=True, text=True)


# ---------------------------------------------------------------- Telegram side
def intake(chat, msg):
    t = T()
    f = msg.get("voice") or msg.get("audio") or msg.get("document") or msg.get("video_note") or msg.get("video") or {}
    if (f.get("file_size") or 0) > 20_000_000:
        t.send(chat, "🎙 That file is over 20 MB, the most a Telegram bot can download. Send it as a voice message instead, "
                     "or as an .m4a / .mp3 (3 minutes from Voice Memos is about 3 MB).")
        return
    try:
        path = t.call("getFile", {"file_id": f["file_id"]})["file_path"]
        data = urllib.request.urlopen(f"{t.BASE}/file/bot{os.environ['TELEGRAM_BOT_TOKEN'].strip()}/{path}", timeout=120).read()
    except Exception as e:
        t.send(chat, f"⚠️ Couldn't download the recording: {t.esc(str(e)[:200])}"); return
    ext = os.path.splitext(path)[1].lower() or ".ogg"
    name = f"voice-sample-{now().strftime('%Y-%m-%dT%H%M%S')}{ext}"
    try: R().data_put(name, data, f.get("mime_type") or "application/octet-stream")
    except SystemExit as e: t.send(chat, f"⚠️ Couldn't store the recording: {t.esc(str(e)[:200])}"); return
    dur = int(f.get("duration") or 0)
    if dur and dur < 20:
        t.send(chat, f"🎙 Got it, but it's only {dur} s. Send at least 30 s (1–3 min is ideal) so I can pick the cleanest stretch.")
        return
    r = dispatch(mode="test", sample=name)
    if r.returncode:
        t.send(chat, f"⚠️ Stored the recording but couldn't start the voice test: {t.esc((r.stderr or r.stdout)[:200])}"); return
    t.send(chat, f"🎙 Got your recording{f' ({dur // 60}:{dur % 60:02d})' if dur else ''}. I'm making four versions of the cloned voice "
                 f"reading the start of the Medusa Short (so you can compare it with the current voice). They arrive here in about "
                 f"30 min. Nothing changes until you tap ✅ under one.")


def choose(chat, run, n, message_id=None):
    t, r = T(), R()
    raw = r.data_get(f"voice-test-{run}-{n}.json")
    if not raw: t.send(chat, "⚠️ I can't find that voice test any more. Send the recording again."); return
    v = json.loads(raw)
    ref = r.data_get(f"voice-cand-{run}-{v['ref']}")
    if not ref: t.send(chat, "⚠️ That version's clip is missing. Send the recording again."); return
    r.data_put("voice-ref.wav", ref, "audio/wav")
    cfg = jload("config.json", {})
    cfg["voice_clone"] = {"enabled": True, "model": v["model"], "exaggeration": v["exaggeration"], "cfg": v["cfg"], "temperature": 0.8,
                          "tempo": 1.0, "tries": 3, "ref_sha": hashlib.sha1(ref).hexdigest()[:12],
                          "picked": f"{today()}, version {v['label']} of voice test {run}"}
    cfg["_voice_clone"] = ("Gigi's cloned voice (Chatterbox, pipeline/tts_clone.py). The reference clip is voice-ref.wav in the private "
                           "data release, never in git. enabled false = the old Kokoro voice. Set by tapping ✅ under a voice test on Telegram.")
    jsave("config.json", cfg)
    if message_id: t.buttons_only(chat, message_id, [[{"text": f"✅ {v['label']} is the voice now", "callback_data": "noop"}]])
    t.send(chat, f"🎙 Version <b>{v['label']}</b> is the channel's voice now. Every reel and long video made from now on uses it, "
                 f"starting with tomorrow morning's renders. Reels already rendered keep the old voice (✏️ Changes on one re-voices it).\n"
                 f"/voice shows the setting · /voice off goes back to the old voice · a new recording starts a new test.")


def status_text():
    cv = jload("config.json", {}).get("voice_clone") or {}
    if not cv: return "🎙 Voice: the original synthetic voice (Kokoro). Send a voice message of 1–3 min to clone yours."
    on = "🎙 Voice: <b>your cloned voice</b>" if cv.get("enabled") else "🎙 Voice: the original synthetic voice (the clone is switched off)"
    return (f"{on}\nPicked: {cv.get('picked', '?')}\nModel: Chatterbox {cv.get('model')} · expressiveness {cv.get('exaggeration')} · "
            f"pace {cv.get('cfg')}\n/voice on · /voice off · a new recording starts a new test")


def switch(chat, on):
    cfg = jload("config.json", {}); cv = cfg.get("voice_clone")
    if not cv: T().send(chat, "🎙 There's no cloned voice yet: send a voice message of 1–3 min first."); return
    cv["enabled"] = on; jsave("config.json", cfg)
    T().send(chat, "🎙 Cloned voice ON for every reel made from now on." if on else "🎙 Back to the original synthetic voice for every reel made from now on.")


# ---------------------------------------------------------------- CI side
def sample(name, dest):
    r = R()
    if not name:
        names = sorted(r.data_list("voice-sample-"))
        if not names: raise SystemExit("no recording in the data release")
        name = names[-1]
    data = r.data_get(name)
    if not data: raise SystemExit(f"no {name} in the data release")
    open(dest, "wb").write(data); print(f"{name}: {len(data) // 1024} KB")


def _noise(rep):
    snr = rep.get("snr_db", 0)
    return "very clean" if snr > 45 else "clean" if snr > 32 else "a little background noise" if snr > 22 else "noisy: re-record somewhere quieter"


def prep(out, run):
    """after voice_ref.py: keep the candidate clips in the private release, tell Gigi what's coming. Prints the versions
    to make as a JSON list (the workflow's matrix)."""
    t, r = T(), R()
    from bot import chat_id
    chat = chat_id(); rep = json.load(open(os.path.join(out, "report.json")))
    if rep.get("error") or not rep.get("clips"):
        if os.environ.get("MODE") == "test":
            t.send(chat, f"🎙 I couldn't use that recording: {t.esc(rep.get('error', 'no usable stretch of speech'))}.\n\n" + TIPS)
        print("versions=[]"); return
    refs = [c["file"] for c in rep["clips"]]
    for ref in refs: r.data_put(f"voice-cand-{run}-{ref}", open(os.path.join(out, ref), "rb").read(), "audio/wav")
    r.data_put(f"voice-test-{run}.json", json.dumps({"report": rep, "sample": os.environ.get("SAMPLE", "")}))
    if os.environ.get("MODE") == "test":
        t.send(chat, f"🎙 <b>Voice test</b>: {rep['speech_s']:.0f} s of speech in your recording, {_noise(rep)}. Four versions of your cloned "
                     f"voice reading the start of the Medusa Short (the same words as the posted Short, so you can compare) arrive here "
                     f"one by one in the next 10–20 min.")
    print("versions=" + json.dumps([1, 2, 3, 4] if "ref2.wav" in refs else [1, 2, 3]))


def get_refs(run, dest):
    """(a test machine) the candidate clips from the private release"""
    os.makedirs(dest, exist_ok=True); r = R()
    for name in r.data_list(f"voice-cand-{run}-"):
        open(os.path.join(dest, name[len(f"voice-cand-{run}-"):]), "wb").write(r.data_get(name))


def send_one(out, run, n):
    """(a test machine) one finished version -> Telegram with its ✅ button"""
    t, r = T(), R()
    from bot import chat_id
    v = next((x for x in json.load(open(os.path.join(out, "variants.json"))) if str(x["n"]) == str(n)), None)
    if not v: raise SystemExit(f"version {n} was not made")
    r.data_put(f"voice-test-{run}-{n}.json", json.dumps(v))
    kb = [[{"text": f"✅ Use {v['label']}", "callback_data": f"vc:{run}:{n}"}]]
    t.call("sendAudio", {"chat_id": chat_id(), "caption": f"<b>{v['label']}</b>: {t.esc(v['note'])}", "parse_mode": "HTML",
                         "title": f"Voice test {v['label']}", "performer": "Dead Painters Society", "reply_markup": {"inline_keyboard": kb}},
           {"audio": os.path.join(out, v["file"])}, timeout=300)


def test_done(run):
    from bot import chat_id
    T().send(chat_id(), "Tap ✅ under the version you like: it becomes the voice of every reel and long video from then on. "
                        "None sounds like you? Send another recording (/voice help has tips).")


TIPS = ("How to record (1–3 min is plenty: the model listens to about 10 s, the rest lets me pick the best stretch):\n"
        "• a quiet room with soft things around (a bedroom, a wardrobe), phone 20–30 cm from your mouth, no music or fan\n"
        "• read a story out loud in English, in the voice you want for the channel: calm, warm, unhurried, like telling a friend "
        "something strange. Read one of the Shorts' scripts, or anything\n"
        "• whole sentences, no long pauses, no laughing or coughing\n"
        "• send it as a voice message (hold the mic button), or the Voice Memos file")


def fetch_ref():
    data = R().data_get("voice-ref.wav")
    if not data: raise SystemExit("voice_clone is on but voice-ref.wav is missing from the data release")
    want = (jload("config.json", {}).get("voice_clone") or {}).get("ref_sha")
    got = hashlib.sha1(data).hexdigest()[:12]
    if want and want != got: print(f"warning: voice-ref.wav is {got}, config.json expects {want} (a newer pick?)")
    os.makedirs(os.path.dirname(REF), exist_ok=True); open(REF, "wb").write(data); print("reference clip ready", got)


# ---------------------------------------------------------------- long videos (voiced in CI, rendered by Claude)
def _git(*a, cwd=ROOT, **kw): return subprocess.run(["git", *a], cwd=cwd, check=True, **kw)
def _url():
    if os.environ.get("GITHUB_ACTIONS") and os.environ.get("GITHUB_TOKEN"):     # a fresh repo in CI has no checkout credentials
        return f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git"
    return subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _push_dir(src, branch, msg):
    _git("init", "-q", "-b", branch, cwd=src); _git("add", "-A", cwd=src)
    _git("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", "commit", "-qm", msg, cwd=src)
    _git("push", "-qf", _url(), branch, cwd=src)


def _pull(branch, dest):
    _git("fetch", "-q", "--depth", "1", "origin", branch)
    os.makedirs(dest, exist_ok=True)
    subprocess.run(f"git archive FETCH_HEAD | tar -x -C '{dest}'", shell=True, cwd=ROOT, check=True)


def _tar_put(name, src_dir, files=None):
    import io, tarfile
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for f in (files if files is not None else sorted(os.listdir(src_dir))): tf.add(os.path.join(src_dir, f), arcname=f)
    R().data_put(name, buf.getvalue(), "application/x-tar"); return len(files if files is not None else os.listdir(src_dir))


def _tar_get(name, dest):
    import io, tarfile
    data = R().data_get(name)
    if not data: return False
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tf: tf.extractall(dest, filter="data")
    return True


def park(slug):
    """(Claude) story.json -> branch voice-in-<slug> (story.json is public anyway), then start the voice workflow"""
    sd = os.path.join(ROOT, "stories", slug)
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "..")) as tmp:
        shutil.copy(os.path.join(sd, "story.json"), tmp)
        _push_dir(tmp, f"voice-in-{slug}", f"voice {slug} (temporary)")
    r = dispatch(mode="story", slug=slug)
    print(r.stderr or f"parked story.json on voice-in-{slug} and started the voice workflow")


def ci_in(slug):
    """(CI) story.json from the branch + the phrases voiced in earlier runs (private release) -> stories/<slug>/"""
    sd = os.path.join(ROOT, "stories", slug); os.makedirs(os.path.join(sd, "src", "voice"), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        _pull(f"voice-in-{slug}", tmp); shutil.copy(os.path.join(tmp, "story.json"), sd)
    print("cached phrases from earlier runs:", "yes" if _tar_get(f"voice-cache-{slug}.tar", os.path.join(sd, "src", "voice")) else "none")


def shard_put(slug, run, k):
    """(CI, one of N machines) the phrases this machine voiced -> private release"""
    cache = os.path.join(ROOT, "stories", slug, "src", "voice")
    new = [f for f in os.listdir(cache) if os.path.getmtime(os.path.join(cache, f)) > float(os.environ.get("SHARD_T0", 0))]
    print(_tar_put(f"voice-shard-{slug}-{run}-{k}.tar", cache, new), "new phrases stored")


def shard_get(slug, run):
    """(CI, the assembling machine) every machine's phrases -> the cache; the shard files are deleted"""
    r = R(); cache = os.path.join(ROOT, "stories", slug, "src", "voice")
    for name in r.data_list(f"voice-shard-{slug}-{run}-"):
        _tar_get(name, cache); r.data_delete(name)
    print(len(os.listdir(cache)), "phrases in the cache")


def ci_out(slug):
    """(CI) voice.wav + timeline.json -> private release (voice-out-<slug>.tar), the whole phrase cache kept for re-runs"""
    sd = os.path.join(ROOT, "stories", slug)
    _tar_put(f"voice-cache-{slug}.tar", os.path.join(sd, "src", "voice"))
    _tar_put(f"voice-out-{slug}.tar", os.path.join(sd, "build"), ["voice.wav", "timeline.json"])
    subprocess.run(["git", "push", "-q", "origin", "--delete", f"voice-in-{slug}"], cwd=ROOT)
    print("voiced:", json.load(open(os.path.join(sd, "build", "timeline.json")))["duration"], "s")


def unpark(slug):
    """(Claude) voice-out-<slug>.tar from the private release -> stories/<slug>/build/ (then run pipeline/align.py)"""
    sd = os.path.join(ROOT, "stories", slug); b = os.path.join(sd, "build")
    rel = json.loads(subprocess.run(["gh", "api", "repos/{owner}/{repo}/releases?per_page=100"], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    a = next((a for x in rel if x.get("tag_name") == "dps-data" for a in x.get("assets", []) if a["name"] == f"voice-out-{slug}.tar"), None)
    if not a: raise SystemExit(f"voice-out-{slug}.tar isn't there yet (is the voice workflow still running?)")
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "..")) as tmp:
        tp = os.path.join(tmp, "o.tar")
        with open(tp, "wb") as fo:
            subprocess.run(["gh", "api", "-H", "Accept: application/octet-stream", f"repos/{{owner}}/{{repo}}/releases/assets/{a['id']}"], cwd=ROOT, stdout=fo, check=True)
        os.makedirs(b, exist_ok=True); subprocess.run(["tar", "-xf", tp, "-C", b], check=True)
    tl = json.load(open(os.path.join(b, "timeline.json")))
    print(f"{slug}: {tl['voice']} {tl['duration']} s -> build/voice.wav + timeline.json (run pipeline/align.py next)")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0]
    if cmd == "prep": prep(a[1], a[2])
    elif cmd == "get-refs": get_refs(a[1], a[2])
    elif cmd == "send-one": send_one(a[1], a[2], a[3])
    elif cmd == "test-done": test_done(a[1])
    elif cmd == "shard-put": shard_put(a[1], a[2], a[3])
    elif cmd == "shard-get": shard_get(a[1], a[2])
    elif cmd == "fetch-ref": fetch_ref()
    elif cmd == "sample": sample(a[1] if len(a) > 2 else "", a[-1])
    elif cmd == "park": park(a[1])
    elif cmd == "ci-in": ci_in(a[1])
    elif cmd == "ci-out": ci_out(a[1])
    elif cmd == "unpark": unpark(a[1])
    else: raise SystemExit(__doc__)
