"""Writes story.json for the long video of 30 Nov 2026 (16:9): Böcklin's Isle of the Dead (third version, 1883, the one
Hitler owned). The script lives in script.py; shots and overlays are anchored to words by text (see A()), so the plan
survives script edits.
usage: python stories/bocklin-isle-long/plan.py"""
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
 "slug": "bocklin-isle-long", "format": "long", "slot": "2026-11-30", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Arnold Böcklin", "born": 1827, "died": 1901, "painting": "Isle of the Dead (third version)", "year": "1883",
          "museum": "Alte Nationalgalerie", "city": "Berlin", "image": "isle",
          "image_credit": "Alte Nationalgalerie, Staatliche Museen zu Berlin, via Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1901, "note": "Böcklin d. 1901, Klinger d. 1920, Sterl d. 1932: public domain. Period photographs before 1925 public domain; "
            "Bundesarchiv photos CC BY-SA 3.0 de. Dalí's works (in copyright) are narrated, never shown; no photos of Dalí. "
            "CC photos (Bundesarchiv, museum and place photos, the 1901 version) credited on screen and in the description. "
            "Music: Mahler, Schumann, Chopin, Rachmaninoff (his own 1920s recording), Beethoven: public-domain / CC0 recordings from Commons."},
 "say": {},
 "ipa": {},
 "chirp_say": {},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS, "next": False,
 "youtube": {"titles": ["The Painting Hitler and Dalí Couldn't Stop Looking At", "A Widow Asked for This Painting. Hitler Bought It."],
             "description_lead": "In the spring of 1880, the young widow Marie Berna asked Arnold Böcklin for \"a picture to dream on\" in memory of her husband, who had died of diphtheria at 29. He painted her an island of tombs and cypresses, with a coffin and a figure in white arriving by boat. Böcklin called it the Tomb Island; his dealer Fritz Gurlitt named it Die Toteninsel, the Isle of the Dead. There are five versions (1880–1886) and one more finished by his son Carlo in 1901. Rachmaninoff wrote a symphonic poem after a black-and-white reproduction, Salvador Dalí painted \"The True Painting of the Isle of the Dead by Arnold Böcklin at the Hour of the Angelus\" (1932) and called his 1934 versions a \"reconstructive obsession\", and in 1936 the third version, the one with Böcklin's own initials on a tomb, was bought for Adolf Hitler's Reich Chancellery. It vanished in 1945 and came back to Berlin's Nationalgalerie in 1980.",
             "hashtags": ["#arthistory", "#bocklin", "#isleofthedead"],
             "credits": ["Paintings by Arnold Böcklin (Alte Nationalgalerie, Berlin; Kunstmuseum Basel; Metropolitan Museum of Art, New York; Museum der bildenden Künste, Leipzig), the lost fourth version (photograph), Max Klinger's etching after Böcklin (1890), Robert Sterl's drawing of Rachmaninoff (1909), the photograph of Marie von Oriola (Hessisches Staatsarchiv Darmstadt) and photographs of Böcklin at Fiesole by Carlo Brogi: public domain, via Wikimedia Commons.",
                         "Arnold and Carlo Böcklin, Isle of the Dead, 1901: photo Sailko, CC BY-SA 3.0, via Wikimedia Commons.",
                         "Adolf Hitler: Bundesarchiv, Bild 183-S33882, CC BY-SA 3.0 de. The Berghof: Bundesarchiv, Bild 183-1999-0412-502, photo Heinrich Hoffmann, CC BY-SA 3.0 de. Hitler's study in the New Reich Chancellery, 1939: Bundesarchiv, Bild 183-H26034, photo Heinrich Hoffmann, CC BY-SA 3.0 de.",
                         "Alte Nationalgalerie, Berlin: photo Mathias Krumbholz, CC BY-SA 3.0, via Wikimedia Commons.",
                         "The Isle of the Dead in the Alte Nationalgalerie: photo Dguendel, CC BY 4.0, via Wikimedia Commons.",
                         "Pontikonisi, Corfu: photo GualdimG, CC BY-SA 4.0, via Wikimedia Commons.",
                         "The English Cemetery, Florence: photo Txllxt TxllxT, CC BY-SA 4.0, via Wikimedia Commons.",
                         "August Strindberg, 1911: photo Axel Malmström, CC BY 4.0, via Wikimedia Commons.",
                         "Castello Aragonese, Ischia: photo Dudva, CC0, via Wikimedia Commons.",
                         "Salvador Dalí's paintings are described, not shown."],
             "thumbnail": {"image": "isle", "focus": [0.40, 0.72], "span": 0.45, "words": "HITLER'S Island"},
             "intro_chapter": "The Island", "outro_chapter": "Where It Hangs Today",
             "sources": ["https://recherche.smb.museum/detail/967648",
                         "https://www.metmuseum.org/art/collection/search/435683",
                         "https://en.wikipedia.org/wiki/Island_of_the_Dead_(paintings)",
                         "https://de.wikipedia.org/wiki/Die_Toteninsel",
                         "https://de.wikipedia.org/wiki/Marie_von_Oriola",
                         "https://de.wikipedia.org/wiki/Georg_Berna",
                         "https://en.wikipedia.org/wiki/Arnold_B%C3%B6cklin",
                         "https://en.wikipedia.org/wiki/Self-Portrait_with_Death_Playing_the_Fiddle",
                         "http://www.florin.ms/IslandDead.html",
                         "https://en.wikipedia.org/wiki/Isle_of_the_Dead_(Rachmaninoff)",
                         "https://www.berliner-philharmoniker.de/en/programme-notes/sergei-rachmaninoff-isle-of-the-dead-symphonic-poem-op-29",
                         "https://catalogues.salvador-dali.org/catalogues/en/heritageobject/391-0f20/",
                         "https://salvador-dali.org/fr/oeuvre/catalogue-raisonne-peinture/obra/340/print/cour-centrale-de-l-ile-des-morts-obsession-reconstitutive-d-apres-boecklin",
                         "https://reactormag.com/a-picture-to-dream-over-the-isle-of-the-dead/",
                         "https://germanhistorydocs.org/en/wilhelmine-germany-and-the-first-world-war-1890-1918/arnold-boecklin-the-isle-of-the-dead-1883",
                         "https://www.smb.museum/presse/pressemitteilungen/detail/museumsinsel-berlin-alte-nationalgalerie-ausstellung-boecklin-jenseits-des-mythos-fuehrt-2027-alle-vier-noch-erhaltenen-versionen-der-toteninsel-zusammen/"],
             "pinned_comment": "Look at the rock on the right in the 1883 version: from that version on, Böcklin painted his own initials, A.B., above one of the tombs.\n\n"
                               "Who do you think is in the coffin? 👁️"},
}
try: from script import SAY, IPA, CHIRP
except ImportError: SAY, IPA, CHIRP = {}, {}, {}
story["say"].update(SAY); story["ipa"].update(IPA); story["chirp_say"].update(CHIRP)
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
