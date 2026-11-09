"""The cloned voice (Chatterbox): recordings in, test versions out, Gigi's pick becomes the channel's voice.

Recordings and reference clips live ONLY in the private data release (dps-data, a draft): the repo is public, and a clean
recording of someone's voice is enough to clone it.

  bot  -> intake(chat, msg)                 a voice message / audio file sent to the bot: stored as voice-sample-<time>.<ext>,
                                            starts the voice workflow (mode test)
  python automation/voice.py send <dir> <run>      (CI) store the candidate clips, send the test versions with ✅ buttons
  bot  -> choose(chat, run, n, message_id)  a ✅ tap: that clip -> voice-ref.wav, its settings -> config.json voice_clone
  python automation/voice.py fetch-ref             (CI) voice-ref.wav -> models/voice/ref.wav (used by pipeline/tts_clone.py)
  python automation/voice.py sample [name] <file>  (CI) a stored recording -> file (empty name = the latest)
  python automation/voice.py park <slug>           (Claude, outside CI) a long video's story.json + phrase cache -> branch voice-in-<slug>
  python automation/voice.py ci-in <slug> / ci-out <slug>    (CI) unpack it / push the voiced result to voice-out-<slug>
  python automation/voice.py unpark <slug>         (Claude) fetch voice-out-<slug> into stories/<slug>/, delete both branches
  bot  -> status_text()                     /voice
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
    raw = r.data_get(f"voice-test-{run}.json")
    if not raw: t.send(chat, "⚠️ I can't find that voice test any more. Send the recording again."); return
    test = json.loads(raw); v = next((x for x in test["variants"] if str(x["n"]) == str(n)), None)
    ref = r.data_get(f"voice-cand-{run}-{v['ref']}") if v else None
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


def send(out, run):
    t, r = T(), R()
    from bot import chat_id
    chat = chat_id(); rep = json.load(open(os.path.join(out, "report.json")))
    if rep.get("error") or not os.path.exists(os.path.join(out, "variants.json")):
        t.send(chat, f"🎙 I couldn't use that recording: {t.esc(rep.get('error', 'the voice test failed'))}.\n\n" + TIPS); return
    variants = json.load(open(os.path.join(out, "variants.json")))
    for ref in sorted({v["ref"] for v in variants}):
        r.data_put(f"voice-cand-{run}-{ref}", open(os.path.join(out, "refs", ref), "rb").read(), "audio/wav")
    r.data_put(f"voice-test-{run}.json", json.dumps({"variants": variants, "report": rep, "sample": os.environ.get("SAMPLE", "")}))
    snr = rep.get("snr_db", 0)
    noise = "very clean" if snr > 45 else "clean" if snr > 32 else "a little background noise" if snr > 22 else "noisy: re-record somewhere quieter"
    t.send(chat, f"🎙 <b>Voice test</b>: {rep['speech_s']:.0f} s of speech in your recording, {noise}. Here are the first lines of the "
                 f"Medusa Short in four versions of your cloned voice (same words as the posted Short, so you can compare).")
    for v in variants:
        kb = [[{"text": f"✅ Use {v['label']}", "callback_data": f"vc:{run}:{v['n']}"}]]
        cap = f"<b>{v['label']}</b>: {t.esc(v['note'])}"
        t.call("sendAudio", {"chat_id": chat, "caption": cap, "parse_mode": "HTML", "title": f"Voice test {v['label']}",
                             "performer": "Dead Painters Society", "reply_markup": {"inline_keyboard": kb}},
               {"audio": os.path.join(out, v["file"])}, timeout=300)
    t.send(chat, "Tap ✅ under the one you like and it becomes the voice of every reel and long video from then on. "
                 "Not quite you? Send another recording (tips: /voice help).")


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


def park(slug):
    sd = os.path.join(ROOT, "stories", slug)
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "..")) as tmp:
        shutil.copy(os.path.join(sd, "story.json"), tmp)
        cache = os.path.join(sd, "src", "voice")
        if os.path.isdir(cache): shutil.copytree(cache, os.path.join(tmp, "voice"))
        _push_dir(tmp, f"voice-in-{slug}", f"voice {slug} (temporary)")
    r = dispatch(mode="story", slug=slug)
    print(r.stdout or r.stderr or f"parked and dispatched: voice-in-{slug}")


def ci_in(slug):
    sd = os.path.join(ROOT, "stories", slug); os.makedirs(os.path.join(sd, "src"), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        _pull(f"voice-in-{slug}", tmp)
        shutil.copy(os.path.join(tmp, "story.json"), sd)
        if os.path.isdir(os.path.join(tmp, "voice")): shutil.copytree(os.path.join(tmp, "voice"), os.path.join(sd, "src", "voice"), dirs_exist_ok=True)
    subprocess.run(["git", "push", "-q", "origin", "--delete", f"voice-in-{slug}"], cwd=ROOT)


def ci_out(slug):
    sd = os.path.join(ROOT, "stories", slug)
    with tempfile.TemporaryDirectory() as tmp:
        for f in ("voice.wav", "timeline.json"): shutil.copy(os.path.join(sd, "build", f), tmp)
        shutil.copytree(os.path.join(sd, "src", "voice"), os.path.join(tmp, "voice"))
        _push_dir(tmp, f"voice-out-{slug}", f"voiced {slug} (temporary)")


def unpark(slug):
    sd = os.path.join(ROOT, "stories", slug)
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "..")) as tmp:
        _pull(f"voice-out-{slug}", tmp)
        os.makedirs(os.path.join(sd, "build"), exist_ok=True)
        for f in ("voice.wav", "timeline.json"): shutil.move(os.path.join(tmp, f), os.path.join(sd, "build", f))
        shutil.copytree(os.path.join(tmp, "voice"), os.path.join(sd, "src", "voice"), dirs_exist_ok=True)
    subprocess.run(["git", "push", "-q", "origin", "--delete", f"voice-out-{slug}"], cwd=ROOT)
    tl = json.load(open(os.path.join(sd, "build", "timeline.json")))
    print(f"{slug}: {tl['voice']} {tl['duration']} s -> build/voice.wav + timeline.json (run pipeline/align.py next)")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0]
    if cmd == "send": send(a[1], a[2])
    elif cmd == "fetch-ref": fetch_ref()
    elif cmd == "sample": sample(a[1] if len(a) > 2 else "", a[-1])
    elif cmd == "park": park(a[1])
    elif cmd == "ci-in": ci_in(a[1])
    elif cmd == "ci-out": ci_out(a[1])
    elif cmd == "unpark": unpark(a[1])
    else: raise SystemExit(__doc__)
