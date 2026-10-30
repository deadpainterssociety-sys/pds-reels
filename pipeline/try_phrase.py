"""Audition phrase variants before committing them to the script: synthesise each and print what the recogniser hears.
usage: python pipeline/try_phrase.py <voice> <lang> <speed> "phrase one" "phrase two" ...
A phrase starting with '/' is raw IPA, e.g. "/ɔnðə wˈɔl…".  Writes scratch WAVs to /tmp/try_N.wav so you can listen."""
import sys, re, json, os
import soundfile as sf
from kokoro_onnx import Kokoro
from paths import KOKORO_MODEL, KOKORO_VOICES, PIPE
from asr import transcribe

voice, lang, speed = sys.argv[1], sys.argv[2], float(sys.argv[3])
kk = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
G = json.load(open(os.path.join(PIPE, "pronounce.json"))).get(lang, {})
for i, text in enumerate(sys.argv[4:]):
    if text.startswith("/"): ph = text[1:]
    else:
        t = text.replace("*", "")
        for k, v in G.get("say", {}).items(): t = re.sub(rf"\b{re.escape(k)}\b", v, t)
        ph = kk.tokenizer.phonemize(t, lang)
    a, sr = kk.create(ph, voice=voice, speed=speed, lang=lang, is_phonemes=True)
    sf.write(f"/tmp/try_{i}.wav", a, sr)
    heard, _ = transcribe(a, sr)
    print(f"{len(a) / sr:5.2f}s | {text:40s} | {ph:45s} | heard: {heard}")
