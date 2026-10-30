"""Replace estimated word times with recognised ones and report what a listener hears, line by line.
usage: python pipeline/align.py <story>      (rewrites build/timeline.json)
Read the printout: every line should come back as written. A wrong word is usually a name (fix with ipa/say)
or a lone word before '...' (rephrase, or give it its own phrase)."""
import json, sys, os, re, difflib
import soundfile as sf
from paths import story_dir
from asr import transcribe

sdir = story_dir(sys.argv[1]); d = os.path.join(sdir, "build")
tl = json.load(open(os.path.join(d, "timeline.json")))
audio, sr = sf.read(os.path.join(d, "voice.wav"), dtype="float32")
norm = lambda s: re.sub(r"[^\w']", "", s.lower())
for ln in tl["lines"]:
    s0 = max(0, ln["s"] - 0.05)
    text, words = transcribe(audio[int(s0 * sr): int((ln["e"] + 0.05) * sr)], sr)
    sw = [norm(w["w"]) for w in ln["words"]]; rw = [norm(w["w"]) for w in words]
    matched = 0
    for blk in difflib.SequenceMatcher(a=sw, b=rw, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            ln["words"][blk.a + k]["s"] = round(words[blk.b + k]["s"] + s0, 3); matched += 1
    for i, w in enumerate(ln["words"]):
        nxt = ln["words"][i + 1]["s"] if i + 1 < len(ln["words"]) else ln["e"]
        w["e"] = round(max(w["s"] + 0.08, min(nxt, w["s"] + 0.9)), 3)
    for i in range(1, len(ln["words"])):   # keep monotonic
        if ln["words"][i]["s"] < ln["words"][i - 1]["s"] + 0.04: ln["words"][i]["s"] = round(ln["words"][i - 1]["s"] + 0.04, 3)
    ln["heard"], ln["match"] = text, round(matched / max(1, len(sw)), 3)   # kept for automation/validate.py
    print(f"{ln['id']:10s} {matched:2d}/{len(sw):2d}  heard: {text}")
json.dump(tl, open(os.path.join(d, "timeline.json"), "w"), indent=1, ensure_ascii=False)
