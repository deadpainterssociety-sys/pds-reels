"""Writes story.json for long video #3 (16:9): Bosch's Garden of Earthly Delights. The script lives in script.py; shots
and overlays are anchored to words by text (see A()), so the plan survives script edits.
usage: python stories/bosch-garden-long/plan.py"""
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
 "slug": "bosch-garden-long", "format": "long", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Hieronymus Bosch", "born": 1450, "died": 1516, "painting": "The Garden of Earthly Delights", "year": "c. 1490–1500",
          "museum": "Museo del Prado", "city": "Madrid", "image": "garden", "image_credit": "Museo del Prado, via Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1516, "note": "Paintings public domain; three CC BY-SA 4.0 photos (hell panel scan, Harrewijn print, Sigüenza portrait) credited in the description and on screen."},
 "say": {"1450": "fourteen fifty", "1486": "fourteen eighty-six", "1516": "fifteen sixteen", "1517": "fifteen seventeen", "1504": "fifteen oh four",
         "1560s": "fifteen sixties", "1568": "fifteen sixty-eight", "1591": "fifteen ninety-one", "1593": "fifteen ninety-three",
         "1605": "sixteen oh five", "1947": "nineteen forty-seven", "2014": "twenty fourteen", "1961": "nineteen sixty-one", "1978": "nineteen seventy-eight",
         "500-year-old": "five-hundred-year-old"},
 "ipa": {"'s-Hertogenbosch": "sˌɛɹtoʊxənbˈɑːs", "Jheronimus": "jɛɹˈoʊnɪməs", "Aken": "ˈɑːkən", "Bosch": "bˈɑːʃ", "Bosch's": "bˈɑːʃɪz",
         "Beatis": "beɪˈɑːtɪs", "Nassau": "nˈæsɔː", "Engelbert": "ˈɛŋɡəlbɜːɹt", "Alba": "ˈælbə", "Escorial": "ˌɛskɔːɹiˈɑːl",
         "Fray": "fɹˈaɪ", "José": "hoʊsˈeɪ", "Sigüenza": "sɪɡwˈɛnθə", "Fraenger": "fɹˈɛŋɚ", "Adamites": "ˈædəmˌaɪts",
         "Hamrick": "hˈæmɹɪk", "Prado": "pɹˈɑːdoʊ", "triptych": "tɹˈɪptɪk", "spake": "spˈeɪk"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS, "next": False,
 "maps": {"journey": {"bbox": [[-9.5, 39.0], [9.0, 53.5]], "focus": ["0", "0"],
                      "cities": {"hertogenbosch": [5.30, 51.69], "brussels": [4.35, 50.85], "escorial": [-4.15, 40.59]}}},
 "youtube": {"titles": ["Nobody Knows What This Painting Means", "500 Years of Arguing About One Painting"],
             "description_lead": "Hieronymus Bosch left no letters, no diary and no title. For five hundred years, the people who owned and studied The Garden of Earthly Delights have read it as a party, a wedding gift, a sermon against lust, a secret heresy and, in 2014, a song written on a sinner's backside. This is the true story of the painting and of everyone who tried to read it: the Nassau counts in Brussels, the Duke of Alba, Philip II and the monks of El Escorial, Wilhelm Fraenger, and the student who turned the 'butt music' into a viral tune.",
             "hashtags": ["#arthistory", "#bosch", "#prado"],
             "credits": [],
             "thumbnail": {"image": "owl_boy", "focus": [0.42, 0.40], "span": 0.62, "words": "NOBODY KNOWS"},
             "intro_chapter": "Nobody knows what this painting means", "outro_chapter": "The Owls"},
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
