"""Narration with Google Cloud Text-to-Speech "Chirp 3: HD" voices, Gigi's pick on 12 Nov 2026:
English en-GB-Chirp3-HD-Enceladus (male, British) · Spanish es-ES-Chirp3-HD-Gacrux (female, Spain).
config.json voice_engine.<en|es> = {"engine": "chirp", "voice": "...", "rate": 1.0}. tts.py hands over to this file when
the story's language has a chirp engine and the key GOOGLE_TTS_KEY is set (the build and revise jobs; Claude's own voice
checks keep the fast Kokoro voice with VOICE=kokoro). Same output as tts.py: build/voice.wav + timeline.json.

- Phrase by phrase, exactly like tts.py: our pauses, our order, each phrase's speed multiplier sent as Chirp's own
  speakingRate (base rate × multiplier ÷ 0.95), so no time-stretching.
- Plain text: Chirp knows most painter names. `say` applies; `ipa` and `respell` (made for Kokoro and Chatterbox) don't.
  A name it gets wrong: story.json "chirp_say": {"Gautreau": "Go-tro"} rewrites it for this voice only.
- Chirp is deterministic, so every phrase is cached in src/voice-chirp/ (kept with the images in the private release):
  the morning build and a revision reuse what was already voiced and only pay for changed phrases.
- The recogniser checks each new phrase; a weak one is reported (a retry would sound the same).

usage: python pipeline/tts_chirp.py <story>
"""
import base64, hashlib, io, json, os, re, sys, time, urllib.error, urllib.request
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import PIPE, ROOT, story_dir
import tts_clone as C

SR = 24000
VERSION = 1
URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


def engine(lang):
    """the chirp settings for a story language, or None"""
    e = (json.load(open(os.path.join(ROOT, "config.json"))).get("voice_engine") or {}).get("es" if lang.startswith("es") else "en")
    return e if e and e.get("engine") == "chirp" else None


def synth(voice, text, rate):
    body = {"input": {"text": text}, "voice": {"languageCode": voice.split("-Chirp")[0], "name": voice},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": SR, "speakingRate": round(rate, 3)}}
    rq = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json", "X-Goog-Api-Key": os.environ["GOOGLE_TTS_KEY"]})
    for k in range(4):
        try:
            b = base64.b64decode(json.load(urllib.request.urlopen(rq, timeout=120))["audioContent"])
            a, sr = sf.read(io.BytesIO(b), dtype="float32"); assert sr == SR
            return a if a.ndim == 1 else a.mean(1)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 503) and k < 3: time.sleep(5 * (k + 1)); continue
            raise RuntimeError(f"Text-to-Speech HTTP {e.code}: {msg}")   # the key is in a header: never in this message


class Voice:
    def __init__(self, cfg, cache, say, chirp_say, lang):
        self.cfg, self.cache, self.say, self.cs, self.lang = cfg, cache, say, chirp_say, lang
        self.made = self.cached = self.chars = 0; os.makedirs(cache, exist_ok=True)

    def text(self, t):
        t = t.replace("*", "").replace("…", "...")
        for k, v in {**self.say, **self.cs}.items(): t = re.sub(rf"\b{re.escape(k)}\b", v, t)
        return t

    def phrase(self, raw, sp):
        rate = float(self.cfg.get("rate", 1.0)) * max(0.8, min(1.1, float(sp) / 0.95))
        t = self.text(raw); voice = self.cfg["voice"]
        key = hashlib.sha1(json.dumps([VERSION, voice, round(rate, 3), t]).encode()).hexdigest()[:16]
        path = os.path.join(self.cache, key + ".wav")
        if os.path.exists(path): self.cached += 1; return sf.read(path, dtype="float32")[0], None
        a = C.trim(synth(voice, t, rate)); sf.write(path, a, SR); self.made += 1; self.chars += len(t)
        check = None
        if self.lang.startswith("en"):
            s, h = C.score(a, [t, raw.replace("*", "")], set(), t); check = (s, h)
        return a, check


def story_voice(slug):
    sdir = story_dir(slug); st = json.load(open(os.path.join(sdir, "story.json")))
    lang = st.get("lang", "en-us"); cfg = engine(lang)
    if not cfg: sys.exit(f"no chirp voice configured for {lang} (config.json voice_engine)")
    G = json.load(open(os.path.join(PIPE, "pronounce.json"))).get(lang, {})
    say = {**G.get("say", {}), **st.get("say", {})}
    v = Voice(cfg, os.path.join(sdir, "src", "voice-chirp"), say, st.get("chirp_say", {}), lang)
    out = os.path.join(sdir, "build"); os.makedirs(out, exist_ok=True)
    audio = [np.zeros(int(0.2 * SR), np.float32)]; t = 0.2; tl = []; weak = []; t0 = time.time()
    for ln in st["lines"]:
        words_all, l_s = [], t
        for text, pause, sp in ln["perf"]:
            a, chk = v.phrase(text, sp)
            if chk and chk[0] < 0.85: weak.append((ln["id"], text, chk[0], chk[1]))
            f = int(0.008 * SR); a = a.copy(); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
            dur = len(a) / SR
            ws = text.replace("...", "…").split(); tot = sum(C.syl(w, say) for w in ws); p = 0.0
            for w in ws:   # rough word times inside the phrase; align.py refines them on the final mix
                d = dur * C.syl(w, say) / tot
                words_all.append({"w": w.replace("*", "").replace("…", "..."), "s": round(t + p, 3), "e": round(t + p + d, 3),
                                  **({"em": 1} if w.count("*") >= 2 else {})})
                p += d
            audio.append(a); audio.append(np.zeros(int(pause * SR), np.float32))
            t += dur + pause; l_e = t - pause
        tl.append({"id": ln["id"], "text": " ".join(x[0] for x in ln["perf"]).replace("*", ""), "s": round(l_s, 3), "e": round(l_e, 3),
                   "words": words_all})
    audio.append(np.zeros(int(float(st.get("tail", 2.2)) * SR), np.float32))
    full = np.concatenate(audio); full = full / np.abs(full).max() * 0.89
    sf.write(os.path.join(out, "voice.wav"), full, SR)
    json.dump({"voice": f"chirp:{cfg['voice']}", "lang": lang, "duration": round(len(full) / SR, 3), "lines": tl},
              open(os.path.join(out, "timeline.json"), "w"), indent=1, ensure_ascii=False)
    nw = sum(len(l["words"]) for l in tl)
    print(f"voice chirp:{cfg['voice']} ({lang}): {len(full) / SR:.1f} s, {nw} words, {nw / (len(full) / SR) * 60:.0f} wpm overall · "
          f"{v.made} phrases voiced ({v.chars} characters), {v.cached} from cache, {time.time() - t0:.0f} s")
    for lid, text, s, h in weak: print(f"  ⚠ {lid}: {s:.2f} for {text!r} — heard {h!r} (add a chirp_say respelling, or rephrase)")


if __name__ == "__main__":
    story_voice(sys.argv[1])
