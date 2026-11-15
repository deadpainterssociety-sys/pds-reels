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
# Digits are spoken through story.json "say" ("1879" -> "eighteen seventy-nine") and the recogniser writes US spelling:
# compare spoken tokens, so a short line like "She died in 1879, at only 32." is not failed for its numbers (15 Nov 2026).
_st = json.load(open(os.path.join(sdir, "story.json")))
_say = {norm(k): v for k, v in (_st.get("say") or {}).items()}
_US = {"colour": "color", "colours": "colors", "grey": "gray", "favourite": "favorite", "centre": "center", "honour": "honor",
       "theatre": "theater", "metre": "meter", "metres": "meters", "jewellery": "jewelry", "armour": "armor", "neighbour": "neighbor",
       "rumour": "rumor", "labour": "labor", "vigour": "vigor", "realised": "realized", "recognised": "recognized"}
def toks(w):
    k = norm(w)
    if k in _say: return [_US.get(x, x) for x in (norm(y) for y in re.split(r"[\s-]+", _say[k])) if x]
    return [_US.get(k, k)]
for ln in tl["lines"]:
    s0 = max(0, ln["s"] - 0.05)
    text, words = transcribe(audio[int(s0 * sr): int((ln["e"] + 0.05) * sr)], sr)
    flat = [(i, j, t) for i, w in enumerate(ln["words"]) for j, t in enumerate(toks(w["w"]))]   # (script word, token no., token)
    sw = [t for _, _, t in flat]; sw_n = len(ln["words"])
    rflat = [(i, t) for i, w in enumerate(words) for t in toks(w["w"])]
    rw = [t for _, t in rflat]
    hit = {}
    for blk in difflib.SequenceMatcher(a=sw, b=rw, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            i, j, _ = flat[blk.a + k]; hit.setdefault(i, set()).add(j)
            if j == 0: ln["words"][i]["s"] = round(words[rflat[blk.b + k][0]]["s"] + s0, 3)
    matched = sum(1 for i, w in enumerate(ln["words"]) if len(hit.get(i, ())) == len(toks(w["w"])))
    for i, w in enumerate(ln["words"]):
        nxt = ln["words"][i + 1]["s"] if i + 1 < len(ln["words"]) else ln["e"]
        w["e"] = round(max(w["s"] + 0.08, min(nxt, w["s"] + 0.9)), 3)
    for i in range(1, len(ln["words"])):   # keep monotonic
        if ln["words"][i]["s"] < ln["words"][i - 1]["s"] + 0.04: ln["words"][i]["s"] = round(ln["words"][i - 1]["s"] + 0.04, 3)
    ln["heard"], ln["match"] = text, round(matched / max(1, sw_n), 3)   # kept for automation/validate.py
    print(f"{ln['id']:10s} {matched:2d}/{sw_n:2d}  heard: {text}")
json.dump(tl, open(os.path.join(d, "timeline.json"), "w"), indent=1, ensure_ascii=False)
