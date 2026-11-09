"""Writes story.json for long video #2 (16:9): Géricault's Raft of the Medusa. The script lives in script.py; shots
and overlays are anchored to words by text (see A()), so the plan survives script edits.
usage: python stories/gericault-raft-long/plan.py"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import L

WORDS = {lid: " ".join(p[0] for p in perf).replace("...", "…").split() for lid, perf in L}
norm = lambda w: re.sub(r"[^\w']", "", w.replace("*", "").lower())


def A(lid, word=None, nth=1, end=False, off=0.0):
    """anchor: line start, or the start (end=True: end) of the nth occurrence of `word` in line `lid`"""
    if lid not in WORDS: raise SystemExit(f"no line {lid}")
    if word is None: base = lid + ("$" if end else "")
    else:
        hits = [i for i, w in enumerate(WORDS[lid]) if norm(w) == norm(word)]
        if len(hits) < nth: raise SystemExit(f"'{word}' (#{nth}) not in {lid}: {WORDS[lid]}")
        base = f"{lid}.{hits[nth - 1]}" + ("$" if end else "")
    return base + (f"{off:+.2f}" if off else "")


S, O, SFX = [], [], []
def sh(at, img, frm="full", to=None, **kw): S.append({"at": at, "img": img, "from": frm, "to": to or frm, **kw})
def ov(type, at, to, **kw): O.append({"type": type, "from": at, "to": to, **kw})

IM, MUSIC = {}, {}
VISUALS = os.path.join(HERE, "visuals.py")
if os.path.exists(VISUALS): exec(open(VISUALS).read())   # images, shots, overlays, music (written once the voice is timed)

FACTS = json.load(open(os.path.join(HERE, "facts.json"))) if os.path.exists(os.path.join(HERE, "facts.json")) else []

story = {
 "slug": "gericault-raft-long", "format": "long", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Théodore Géricault", "born": 1791, "died": 1824, "painting": "The Raft of the Medusa", "year": "1818–1819",
          "museum": "Musée du Louvre", "city": "Paris", "image": "raft", "image_credit": "Musée du Louvre, via Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1824, "note": "All paintings and prints public domain; check each Commons file's licence in src/sources.json."},
 "say": {"1816": "eighteen sixteen", "1817": "eighteen seventeen", "1819": "eighteen nineteen", "1820": "eighteen twenty", "1824": "eighteen twenty-four"},
 "ipa": {"Géricault": "ʒˌeɪɹɪkˈoʊ", "Géricault's": "ʒˌeɪɹɪkˈoʊz", "Théodore": "tˈeɪoʊdɔːɹ", "Méduse": "meɪdˈuːz", "Chaumareys": "ʃˌoʊmɑːɹˈeɪ",
         "Hugues": "ˈuːɡ", "Duroy": "dʊɹwˈɑː", "Savigny": "sˌævɪnjˈiː", "Corréard": "kˌɔːɹeɪˈɑːɹ", "Arguin": "ɑːɹɡwˈæn",
         "Rochefort": "ɹˈɔʃfɔːɹ", "Beaujon": "boʊʒˈɑːn", "Hôpital": "ˌoʊpiːtˈɑːl", "Montpellier": "mˌɑːnpɛljˈeɪ", "Eugène": "uːʒˈɛn",
         "Delacroix": "dˌɛləkɹwˈɑː", "Scène": "sˈɛn", "naufrage": "noʊfɹˈɑːʒ", "Ugolino": "ˌuːɡoʊlˈiːnoʊ", "Senegal": "sˌɛnɪɡˈɔːl",
         "Mauritania": "mˌɔːɹɪtˈeɪniə", "Argus": "ˈɑːɹɡəs", "Louvre": "lˈuːvɹə", "Charles": "ʃˈɑːɹl"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS,
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
