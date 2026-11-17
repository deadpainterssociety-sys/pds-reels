"""Writes story.json for long video #4 (16:9): Klimt's Adele Bloch-Bauer I, the Woman in Gold. The script lives in script.py; shots
and overlays are anchored to words by text (see A()), so the plan survives script edits.
usage: python stories/klimt-adele-long/plan.py"""
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
 "slug": "klimt-adele-long", "format": "long", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Gustav Klimt", "born": 1862, "died": 1918, "painting": "Portrait of Adele Bloch-Bauer I", "year": "1903–1907",
          "museum": "Neue Galerie", "city": "New York", "image": "adele", "image_credit": "Neue Galerie New York, via Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1918, "note": "Klimt d. 1918: public domain. Period photographs public domain (Nähr 1911, Adele c. 1910, Hoffmann 1938, Highsmith). CC photos (Belvedere, Neue Galerie, Theodora mosaic) credited on screen and in the description. Music: Mahler recordings CC0 / public domain."},
 "say": {"1899": "eighteen ninety-nine", "1903": "nineteen oh three", "1907": "nineteen oh seven", "1912": "nineteen twelve",
         "1918": "nineteen eighteen", "1923": "nineteen twenty-three", "1925": "nineteen twenty-five", "1937": "nineteen thirty-seven",
         "1941": "nineteen forty-one", "1945": "nineteen forty-five", "1948": "nineteen forty-eight", "1998": "nineteen ninety-eight",
         "1999": "nineteen ninety-nine", "2004": "two thousand and four", "2006": "two thousand and six", "2011": "twenty eleven",
         "82-year-old": "eighty-two-year-old", "55": "fifty-five", "43": "forty-three", "82": "eighty-two", "94": "ninety-four",
         "135": "a hundred and thirty-five", "300": "three hundred"},
 "ipa": {"Adele": "ɑːdˈeɪlə", "Adele's": "ɑːdˈeɪləz", "Bloch-Bauer": "blˈɔːx bˈaʊɚ", "Bloch": "blˈɔːx", "Bauer": "bˈaʊɚ",
         "Klimt": "klˈɪmt", "Klimt's": "klˈɪmts", "Klimts": "klˈɪmts", "Ucicky": "ˈuːtʃɪtski", "Czernin": "tʃˈɛɹniːn", "Führer": "fjˈʊɹɚ",
         "Belvedere": "bˈɛlvədɪɹ", "Neue": "nˈɔɪə", "Galerie": "ɡˌæləɹˈiː", "Altmann": "ˈɑːltmən", "Mehr": "mˈɛɹ", "Blech": "blˈɛx"},
 # Chirp 3 HD (Enceladus): plain respellings for the names it may anglicise
 "chirp_say": {"Adele's": "Ah-day-leh's", "Adele": "Ah-day-leh", "Ucicky": "Oo-chits-kee", "Czernin": "Chair-neen", "Führer": "Fyoo-rer",
               "Neue": "Noy-eh", "Mehr": "Mair", "Blech": "Blekh", "Bloch": "Blokh"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS, "next": False,
 "youtube": {"titles": ["The True Story Behind Woman in Gold", "The Nazis Renamed Her. Her Niece Took Her Back."],
             "description_lead": "In 1903 a Viennese sugar industrialist asked Gustav Klimt to paint his wife, Adele Bloch-Bauer. Four years and more than a hundred drawings later, Klimt delivered the golden portrait that became his masterpiece. In 1941 a Nazi lawyer handed it to Austria's national gallery with a letter signed 'Heil Hitler', and the gallery renamed it 'The Lady in Gold'. For sixty years it was Austria's Mona Lisa, until Adele's niece Maria Altmann, a refugee in Los Angeles, took the Republic of Austria all the way to the United States Supreme Court. This is the true story behind the film Woman in Gold.",
             "hashtags": ["#arthistory", "#klimt", "#womaningold"],
             "credits": ["Paintings and drawings by Gustav Klimt (Neue Galerie New York; Belvedere, Vienna; private collections): public domain, via Wikimedia Commons.",
                         "Gustav Klimt with a cat, Moriz Nähr, 1911; Adele Bloch-Bauer, c. 1910; Ferdinand Bloch-Bauer, 1935; Vienna, c. 1900; Heldenplatz, Vienna, 15 March 1938 (Heinrich Hoffmann); Bruno Walter, 1937; U.S. Supreme Court, Carol M. Highsmith; Bloch-Bauer sugar factory, Bruck an der Leitha: public domain, via Wikimedia Commons.",
                         "Mosaic of Theodora, San Vitale, Ravenna: photo Petar Milošević, CC BY-SA 4.0, via Wikimedia Commons.",
                         "Upper Belvedere, Vienna: photo Murdockcrc, CC BY 3.0, via Wikimedia Commons.",
                         "The Neue Galerie, New York: photo Francesca.hyanna19, CC BY-SA 4.0, via Wikimedia Commons."],
             "thumbnail": {"image": "adele", "focus": [0.60, 0.17], "span": 0.42, "words": "RENAMED by Nazis"},
             "intro_chapter": "The Lady in Gold", "outro_chapter": "Where She Hangs Today",
             "sources": ["https://www.neuegalerie.org/content/adele-bloch-bauer-i",
                         "https://neuegalerie.org/sites/default/files/inline-files/PORTRAIT%20OF%20ADELE%20BLOCH-BAUER%20I_Didactic.pdf",
                         "https://artsandculture.google.com/asset/study-for-portrait-of-adele-bloch-bauer-i/ggE65qzvhJqf1A",
                         "https://en.wikipedia.org/wiki/Portrait_of_Adele_Bloch-Bauer_I",
                         "https://en.wikipedia.org/wiki/Maria_Altmann",
                         "https://en.wikipedia.org/wiki/Republic_of_Austria_v._Altmann",
                         "https://www.law.cornell.edu/supct/html/03-13.ZC1.html",
                         "https://plone.unige.ch/art-adr/cases-affaires/6-klimt-paintings-2013-maria-altmann-and-austria",
                         "https://www.theartnewspaper.com/2001/09/01/austria-can-be-sued-in-the-us-in-claim-that-it-forced-jew-to-give-klimts-after-world-war-ii",
                         "https://www.theartnewspaper.com/archive/morally-this-is-a-gain-for-austria-not-a-loss-says-maria-altmann",
                         "https://www.npr.org/transcripts/148542712",
                         "https://paw.princeton.edu/node/84271",
                         "https://www.nysun.com/article/national-refugee-91-recalls-battle-to-regain-klimts",
                         "https://www.cbsnews.com/news/austria-gives-up-on-looted-nazi-art",
                         "https://www.cbsnews.com/news/maria-altmann-who-won-return-of-looted-art-dies",
                         "https://www.jewishjournal.com/judaism/obituaries/88984/",
                         "https://jpost.com/israel-news/culture/how-e-randol-schoenberg-fought-for-the-woman-in-gold-408162",
                         "https://klimt-database.com/en/network-vienna-1900/family-and-environment/the-ucicka-family",
                         "https://www.thelocal.com/20141120/nazi-era-director-given-retrospective-in-vienna",
                         "https://collections.ushmm.org/search/catalog/pa1182548",
                         "https://www.pristineclassical.com/products/pasc389",
                         "https://www.irishtimes.com/culture/figures-of-expression-1.1022560"],
             "pinned_comment": "Adele asked, in her will, for her portraits to go to a museum. The Nazis used that sentence to take one; "
                               "today it hangs in a museum under her own name.\n\nShould it have stayed in Vienna? 🖤"},
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
