"""Cloned-voice narration with Chatterbox (Resemble AI, MIT licence): the same job as tts.py, in the voice Gigi picked
on Telegram. Runs in its own virtualenv (torch + chatterbox, see automation/voice_env.sh); tts.py hands over to it when
config.json voice_clone.enabled is true and the reference clip models/voice/ref.wav is present. The clip is never in git
(the repo is public): CI fetches it from the private data release.

usage: <venv>/bin/python pipeline/tts_clone.py <story>        -> build/voice.wav + timeline.json (same format as tts.py)
       <venv>/bin/python pipeline/tts_clone.py <story> --shard k/N   only fill the phrase cache (one of N machines)

How it differs from Kokoro:
- Pronunciation: Chatterbox reads plain text, no phonemes, so `ipa` is ignored. Use `respell` instead
  ({"Sigüenza": "see-GWEN-tha"}) in story.json or pipeline/pronounce.json -> en-us -> respell. `say` works as before.
- Pace: the clone keeps the pace of the reference recording. The story's global `speed` (tuned for Kokoro) is ignored;
  each phrase's speed multiplier is applied relative to 0.95 (0.84 on a hit word = about 12% slower) by time-stretching,
  and config voice_clone.tempo scales everything.
- Every phrase is checked by the recogniser and voiced again with a new seed (up to `tries`) when words go missing or it
  rambles. Phrases are cached in src/voice/ (kept with the images in the private release), so a re-run only re-voices
  changed phrases and the morning build reproduces exactly what the night check heard.
"""
import difflib, hashlib, json, os, random, re, subprocess, sys, tempfile, time
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import MODELS, PIPE, ROOT

SR = 24000
VERSION = 1                       # bump to invalidate every cached phrase
REF = os.path.join(MODELS, "voice", "ref.wav")
norm = lambda s: re.sub(r"[^\w']", "", s.lower())


def settings():
    cv = json.load(open(os.path.join(ROOT, "config.json"))).get("voice_clone") or {}
    return {"model": "original", "exaggeration": 0.5, "cfg": 0.5, "temperature": 0.8, "tempo": 1.0, "tries": 3, **cv}


_models = {}


def model(name):
    """original = Chatterbox 0.5B (exaggeration + cfg controls) · turbo = Chatterbox-Turbo 350M (faster, no controls)"""
    if name in _models: return _models[name]
    import torch
    from huggingface_hub import snapshot_download
    torch.set_num_threads(os.cpu_count() or 4)
    t0 = time.time()
    if name == "turbo":
        from chatterbox.tts_turbo import ChatterboxTurboTTS as M
        p = snapshot_download("ResembleAI/chatterbox-turbo", allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model"])
    else:
        from chatterbox.tts import ChatterboxTTS as M
        p = snapshot_download("ResembleAI/chatterbox", allow_patterns=["ve.safetensors", "t3_cfg.safetensors", "s3gen.safetensors",
                                                                        "tokenizer.json", "conds.pt"])
    _models[name] = M.from_local(p, "cpu"); print(f"chatterbox {name} loaded in {time.time() - t0:.0f} s", flush=True)
    return _models[name]


_conds = {}


def condition(m, name, ref, ex):
    key = (name, ref, ex)
    if _conds.get(name) != key:
        if name == "turbo": m.prepare_conditionals(ref)
        else: m.prepare_conditionals(ref, exaggeration=ex)
        _conds[name] = key


def generate(cv, ref, text, seed):
    m = model(cv["model"]); condition(m, cv["model"], ref, cv["exaggeration"])
    import torch
    torch.manual_seed(seed); random.seed(seed); np.random.seed(seed % 2 ** 32)
    kw = {"temperature": cv["temperature"]}
    if cv["model"] != "turbo": kw.update(exaggeration=cv["exaggeration"], cfg_weight=cv["cfg"])
    return m.generate(text, **kw).squeeze(0).numpy().astype(np.float32)


def trim(a, thr=0.006):
    idx = np.where(np.abs(a) > thr)[0]
    return a if len(idx) == 0 else a[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.06 * SR)]


def stretch(a, f):
    """tempo change without a pitch change (rubberband, else atempo); f < 1 = slower"""
    if abs(f - 1) < 0.02: return a
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "i.wav"), os.path.join(d, "o.wav"); sf.write(i, a, SR)
        for af in (f"rubberband=tempo={f:.4f}:pitchq=quality:transients=smooth", f"atempo={f:.4f}"):
            if subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", i, "-af", af, o]).returncode == 0:
                return sf.read(o, dtype="float32")[0]
    return a


_asr = None


def heard(a):
    global _asr
    if _asr is None:
        try: import asr as _asr
        except Exception as e: print("(no recogniser in this environment:", e, ")"); _asr = False
    return _asr.transcribe(a, SR)[0] if _asr else None


def _chars(words): return "".join(norm(w) for w in words)


_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _num(n):
    """15 -> fifteen, 150 -> one hundred and fifty (the recogniser writes numbers as digits, scripts often as words)"""
    if n < 20: return _ONES[n]
    if n < 100: return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000: return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " and " + _num(n % 100))
    if n < 1000000: return _num(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + _num(n % 1000))
    return str(n)


def _spell_numbers(t): return re.sub(r"\d+", lambda m: _num(int(m.group())), t.replace(",", ""))


def score(a, variants, skip, said=""):
    """1.0 = every word heard, nothing extra. Compared letter by letter (so "onto" = "on to") against each way of writing
    the phrase (digits or words: "1816" = "eighteen sixteen"); names the recogniser can't know (respelled/ipa) don't count"""
    text = heard(a)
    if text is None: return 1.0, ""
    got = [w for w in text.split() if norm(w)]
    best = 0.0
    for G in {_chars(got), _chars(_spell_numbers(text).split())}:
        for v in variants:
            W = _chars(w for w in v.split() if norm(w) and norm(w) not in skip)
            hit = sum(b.size for b in difflib.SequenceMatcher(a=W, b=G, autojunk=False).get_matching_blocks())
            best = max(best, hit / max(1, len(W)))
    n = max(len(v.split()) for v in variants + [said.replace("-", " ")])   # a respelled name can be heard as several words
    extra = max(0, len(got) - n - 1)                         # rambling / a repeated phrase
    slow = max(0.0, len(a) / SR - (0.9 * n + 1.0))            # far longer than the words need: babble or a long hum
    return round(best - 0.15 * extra - 0.1 * slow, 3), text


class Voice:
    """phrase synthesis with recogniser retries and a disk cache"""
    def __init__(self, cv, ref, cache, say=None, respell=None, skip=()):
        self.cv, self.ref, self.cache = cv, ref, cache
        self.say, self.respell, self.skip = say or {}, respell or {}, {norm(w) for w in skip}
        self.refhash = hashlib.sha1(open(ref, "rb").read()).hexdigest()[:12]
        self.made = self.cached = 0; self.secs = 0.0; self.audio_s = 0.0
        os.makedirs(cache, exist_ok=True)

    def texts(self, text):
        raw = t = text.replace("*", "").replace("…", "...")
        for k, v in self.say.items(): t = re.sub(rf"\b{re.escape(k)}\b", v, t)
        heard_as = [t, raw]                                   # what a listener should hear (for the check)
        for k, v in self.respell.items(): t = re.sub(rf"\b{re.escape(k)}\b", v, t)
        return heard_as, t

    def key(self, text):
        cv = self.cv; t = self.texts(text)[1]
        return hashlib.sha1(json.dumps([VERSION, cv["model"], self.refhash, cv["exaggeration"], cv["cfg"], cv["temperature"], t]).encode()).hexdigest()[:16]

    def has(self, text): return os.path.exists(os.path.join(self.cache, self.key(text) + ".wav"))

    def phrase(self, text):
        spoken, t = self.texts(text)
        cv = self.cv; key = self.key(text)
        path = os.path.join(self.cache, key + ".wav")
        if os.path.exists(path):
            self.cached += 1; return sf.read(path, dtype="float32")[0], None
        best = None; t0 = time.time()
        for k in range(int(cv["tries"])):
            a = trim(generate(cv, self.ref, t, int(key[:8], 16) + k))
            s, h = score(a, spoken, self.skip, t)
            if best is None or s > best[0]: best = (s, a, h)
            if s >= 0.9: break
            print(f"   retry ({s:.2f}) {t!r} heard {h!r}", flush=True)
        self.made += 1; self.secs += time.time() - t0; self.audio_s += len(best[1]) / SR
        sf.write(path, best[1], SR)
        return best[1], best


def syl(w, say):
    w = re.sub(r"[^\w']", "", w.replace("*", "")); w = say.get(w, w)
    return max(1, len(re.findall(r"[aeiouy]+", w.lower())))


def words_of(story):
    """say / respell / words the recogniser can't be held to, for a story (pronounce.json + the story's own)"""
    G = json.load(open(os.path.join(PIPE, "pronounce.json"))).get(story.get("lang", "en-us"), {})
    say = {**G.get("say", {}), **story.get("say", {})}
    respell = {**G.get("respell", {}), **story.get("respell", {})}
    skip = set(respell) | set(G.get("ipa", {})) | set(story.get("ipa", {}))
    return say, respell, {w for k in skip for w in k.split()}


def render(v, lines, say, cv, tail):
    """-> (audio, timeline lines, weak phrases): phrases + pauses, exactly like tts.py"""
    audio = [np.zeros(int(0.2 * SR), np.float32)]; t = 0.2; tl = []; weak = []
    for ln in lines:
        words_all, l_s = [], t
        for text, pause, sp in ln["perf"]:
            a, info = v.phrase(text)
            if info and info[0] < 0.9: weak.append((ln["id"], text, info[0], info[2]))
            a = stretch(a, max(0.8, min(1.1, float(sp) / 0.95)) * float(cv["tempo"]))
            f = int(0.008 * SR); a = a.copy(); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
            dur = len(a) / SR
            ws = text.replace("...", "…").split(); tot = sum(syl(w, say) for w in ws); p = 0.0
            for w in ws:
                d = dur * syl(w, say) / tot
                words_all.append({"w": w.replace("*", "").replace("…", "..."), "s": round(t + p, 3), "e": round(t + p + d, 3),
                                  **({"em": 1} if w.count("*") >= 2 else {})})
                p += d
            audio.append(a); audio.append(np.zeros(int(pause * SR), np.float32))
            t += dur + pause; l_e = t - pause
        tl.append({"id": ln["id"], "text": " ".join(x[0] for x in ln["perf"]).replace("*", ""), "s": round(l_s, 3), "e": round(l_e, 3),
                   "words": words_all})
        print(f"  {ln['id']:10s} {t:6.1f} s", flush=True)
    audio.append(np.zeros(int(float(tail) * SR), np.float32))
    full = np.concatenate(audio)
    return full / np.abs(full).max() * 0.89, tl, weak


def story_voice(slug_or_dir, shard=None):
    """shard "k/N": only voice (into the cache) the phrases i with i % N == k that aren't cached yet; no voice.wav.
    The voice workflow runs N shards on N machines, then one plain run assembles everything from the cache."""
    from paths import story_dir
    sdir = story_dir(slug_or_dir)
    story = json.load(open(os.path.join(sdir, "story.json")))
    out = os.path.join(sdir, "build"); os.makedirs(out, exist_ok=True)
    cv = settings(); lang = story.get("lang", "en-us"); t0 = time.time()
    say, respell, skip = words_of(story)
    v = Voice(cv, REF, os.path.join(sdir, "src", "voice"), say, respell, skip)
    if shard:
        k, n = map(int, shard.split("/"))
        todo = [p[0] for i, p in enumerate(x for ln in story["lines"] for x in ln["perf"]) if i % n == k]
        for text in todo:
            if not v.has(text): v.phrase(text)
        print(f"shard {shard}: {v.made} phrases voiced ({v.audio_s:.0f} s of speech, {v.secs:.0f} s), {len(todo) - v.made} already cached")
        return
    full, tl, weak = render(v, story["lines"], say, cv, story.get("tail", 2.2))
    sf.write(os.path.join(out, "voice.wav"), full, SR)
    json.dump({"voice": f"clone:{cv['model']}", "lang": lang, "duration": round(len(full) / SR, 3), "lines": tl},
              open(os.path.join(out, "timeline.json"), "w"), indent=1, ensure_ascii=False)
    nw = sum(len(l["words"]) for l in tl)
    rtf = f", {v.secs / max(0.1, v.audio_s):.1f} s of CPU per second of speech" if v.made else ""
    print(f"voice clone:{cv['model']} ({lang}): {len(full) / SR:.1f} s, {nw} words, {nw / (len(full) / SR) * 60:.0f} wpm overall · "
          f"{v.made} phrases voiced, {v.cached} from cache, {time.time() - t0:.0f} s{rtf}")
    for lid, text, s, h in weak: print(f"  ⚠ {lid}: best try {s:.2f} for {text!r} — heard {h!r} (respell a name, or rephrase)")


if __name__ == "__main__":
    story_voice(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--shard" else None)
