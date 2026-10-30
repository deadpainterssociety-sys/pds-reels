"""Performance TTS: phrase-by-phrase Kokoro synthesis with explicit pauses and per-phrase tempo.
This is THE fix for robotic narration: never synthesise a whole script in one go.

usage: python pipeline/tts.py <story>      -> stories/<slug>/build/voice.wav + timeline.json

story.json fields: voice (e.g. af_heart), lang (en-us | en-gb | es | fr-fr | it | pt-br ...), speed, tail,
  say {"1819": "eighteen nineteen"}   rewrite before phonemizing (years, numbers, abbreviations)
  ipa {"Goya": "ɡˈɔɪə"}               replace a word's phonemes (names the model gets wrong)
  lines [{id, perf: [[text, pause_after_s, speed_mult], ...]}]
*word* marks caption emphasis only (stripped before synthesis). pipeline/pronounce.json holds global fixes.
"""
import json, re, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from paths import KOKORO_MODEL, KOKORO_VOICES, PIPE, story_dir

sdir = story_dir(sys.argv[1])
story = json.load(open(os.path.join(sdir, "story.json")))
out = os.path.join(sdir, "build"); os.makedirs(out, exist_ok=True)
voice, speed = story.get("voice", "af_heart"), float(story.get("speed", 1.0))
lang = story.get("lang") or ("en-gb" if voice.startswith("b") else "en-us")
kk = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
SR = 24000
G = json.load(open(os.path.join(PIPE, "pronounce.json"))).get(lang, {})
IPA = {**G.get("ipa", {}), **story.get("ipa", {})}
SAY = {**G.get("say", {}), **story.get("say", {})}


def strip(t): return t.replace("*", "")


def phon(text):
    t = strip(text)
    for k, v in SAY.items(): t = re.sub(rf"\b{re.escape(k)}\b", v, t)
    ph = kk.tokenizer.phonemize(t, lang)
    for n, ipa in IPA.items():
        if re.search(rf"\b{re.escape(n)}\b", t):
            ph = ph.replace(kk.tokenizer.phonemize(n, lang).strip().rstrip("."), ipa)
    return ph


def trim(a, thr=0.004):
    idx = np.where(np.abs(a) > thr)[0]
    return a if len(idx) == 0 else a[max(0, idx[0] - int(0.015 * SR)): idx[-1] + int(0.05 * SR)]


def weight(w):  # rough share of the phrase's duration, refined later by align.py
    w = re.sub(r"[^\w']", "", strip(w)); w = SAY.get(w, w)
    try: return max(2, len(kk.tokenizer.phonemize(w, lang)))
    except Exception: return max(2, len(w))


audio = [np.zeros(int(0.2 * SR), np.float32)]; t = 0.2; tl = []
for ln in story["lines"]:
    words_all, l_s = [], t
    for text, pause, sp in ln["perf"]:
        a, _ = kk.create(phon(text), voice=voice, speed=speed * sp, lang=lang, is_phonemes=True)
        a = trim(a.astype(np.float32))
        f = int(0.008 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)   # no clicks between phrases
        dur = len(a) / SR
        ws = text.replace("...", "…").split(); tot = sum(weight(w) for w in ws); p = 0.0
        for w in ws:
            d = dur * weight(w) / tot
            words_all.append({"w": strip(w).replace("…", "..."), "s": round(t + p, 3), "e": round(t + p + d, 3), **({"em": 1} if w.count("*") >= 2 else {})})
            p += d
        audio.append(a); audio.append(np.zeros(int(pause * SR), np.float32))
        t += dur + pause; l_e = t - pause
    tl.append({"id": ln["id"], "text": strip(" ".join(x[0] for x in ln["perf"])), "s": round(l_s, 3), "e": round(l_e, 3), "words": words_all})
audio.append(np.zeros(int(float(story.get("tail", 1.0)) * SR), np.float32))
full = np.concatenate(audio); full = full / np.abs(full).max() * 0.89
sf.write(os.path.join(out, "voice.wav"), full, SR)
json.dump({"voice": voice, "lang": lang, "duration": round(len(full) / SR, 3), "lines": tl},
          open(os.path.join(out, "timeline.json"), "w"), indent=1, ensure_ascii=False)
nw = sum(len(l["words"]) for l in tl)
print(f"voice {voice} ({lang}): {len(full) / SR:.1f} s, {nw} words, {nw / (len(full) / SR) * 60:.0f} wpm overall")
