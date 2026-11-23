"""Writes story.json for the long video of 26 Nov 2026 (16:9): Holman Hunt's The Awakening Conscience. The script lives in script.py; shots
and overlays are anchored to words by text (see A()), so the plan survives script edits.
usage: python stories/hunt-conscience-long/plan.py"""
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
 "slug": "hunt-conscience-long", "format": "long", "slot": "2026-11-26", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "William Holman Hunt", "born": 1827, "died": 1910, "painting": "The Awakening Conscience", "year": "1853",
          "museum": "Tate Britain", "city": "London", "image": "conscience",
          "image_credit": "Tate, London, via Google Art Project / Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1910, "note": "Hunt d. 1910: public domain. Paintings and drawings by Hunt, Rossetti (d. 1882), Millais (d. 1896), Egg (d. 1863), Lawrence, Cozens, Levin, Phiz, Pellegrini: public domain. CC photos (Sailko's photos of the framed painting, Tate Britain by Julian Herzog) credited on screen and in the description. Music: Schumann (Musopen, public domain) and Chopin nocturnes (Musopen, Constantin Stephan, CC0)."},
 "say": {"1851": "eighteen fifty-one", "1853": "eighteen fifty-three", "1854": "eighteen fifty-four", "1835": "eighteen thirty-five",
         "1850": "eighteen fifty", "1856": "eighteen fifty-six", "1859": "eighteen fifty-nine", "1863": "eighteen sixty-three",
         "1925": "nineteen twenty-five"},
 "ipa": {"Millais": "mˈɪleɪ", "Rossetti": "ɹəzˈɛti", "Ranelagh": "ɹˈænələ", "Combe": "kˈuːm", "Cremorne": "kɹəmˈɔːɹn",
         "Peggotty": "pˈɛɡəti", "Fairbairn": "fˈɛɹbɛɹn", "Athenaeum": "ˌæθənˈiːəm", "convenance": "kɔ̃vnˈɑ̃s", "maison": "mɛzˈɔ̃",
         "Shoreham": "ʃˈɔːɹəm", "Pancras": "pˈæŋkɹəs"},
 # Chirp 3 HD (Enceladus): plain respellings for the names it may anglicise
 "chirp_say": {"Millais": "Millay", "Ranelagh": "Rannela", "Combe": "Coom", "Cremorne": "Cre-morn", "maison de convenance": "mezzon de convenahnce"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS, "next": False,
 "youtube": {"titles": ["It Looks Innocent Until You See Her Hands", "The Painter Who Tried to Remake His Model"],
             "description_lead": "William Holman Hunt's The Awakening Conscience (1853, Tate Britain) looks like a couple at the piano, until you see her hands: rings on every finger but the wedding finger. She is a kept woman, and a song has just woken her conscience. Hunt painted it in a rented room at Woodbine Villa in St John's Wood, a 'maison de convenance', and his model was Annie Miller, a Chelsea barmaid he had met when she was fifteen and planned to educate and marry. While he was in the Holy Land she sat for Rossetti and danced at Cremorne; the buyer, Thomas Fairbairn, couldn't bear her painful expression and Hunt repainted her face; in 1863 Annie married Captain Thomas Thomson. John Ruskin defended the painting in The Times: 'not a single object in all that room… but it becomes tragical, if rightly read.'",
             "hashtags": ["#arthistory", "#preraphaelites", "#tatebritain"],
             "credits": ["The Awakening Conscience (1853), The Light of the World, Our English Coasts, The Scapegoat, The Finding of the Saviour in the Temple and a self-portrait by William Holman Hunt: public domain, via Wikimedia Commons (Tate; Keble College, Oxford; Lady Lever Art Gallery; Birmingham Museums; and other collections).",
                         "Drawings and paintings of Annie Miller by Dante Gabriel Rossetti (Helen of Troy, Hamburger Kunsthalle, photo Ad Meskens, released into the public domain); Rossetti's self-portrait, 1847; John Ruskin and Thomas Combe by John Everett Millais; Augustus Egg, Past and Present No. 1 (Tate); Thomas Moore by Thomas Lawrence; Phiz's illustration for David Copperfield; Phoebus Levin, The Dancing Platform at Cremorne Gardens (London Museum); Viscount Ranelagh by Carlo Pellegrini, Vanity Fair 1870 (Yale Center for British Art); John Robert Cozens, The Thames from Richmond Hill; Oft in the Stilly Night, sheet music, 1826 (Library of Congress); Edward Lear, photograph: public domain, via Wikimedia Commons.",
                         "The Awakening Conscience in its frame, and the clock detail: photos Sailko, CC BY 3.0, via Wikimedia Commons.",
                         "Tate Britain, London: photo Julian Herzog, CC BY 4.0, via Wikimedia Commons.",
                         "Music: Robert Schumann, Scenes from Childhood (Musopen, public domain); Frédéric Chopin, Nocturnes Op. 37 No. 1, Op. 55 No. 1 and Op. 72 No. 1 (Musopen, Constantin Stephan, CC0)."],
             "thumbnail": {"image": "conscience", "focus": [0.53, 0.30], "span": 0.42, "words": "Not His WIFE"},
             "intro_chapter": "Not His Wife", "outro_chapter": "Where It Hangs Today",
             "sources": ["https://www.tate.org.uk/art/artworks/hunt-the-awakening-conscience-t02075",
                         "https://web.archive.org/web/2008/http://www.tate.org.uk/servlet/ViewWork?cgroupid=-1&workid=6996&searchid=false&roomid=false&tabview=text&texttype=8",
                         "https://www.tate.org.uk/art/art-terms/p/pre-raphaelite/why-were-pre-raphaelites-so-shocking",
                         "https://www.tate.org.uk/visit/tate-britain/display/historic-early-modern-british-art/1845-1904",
                         "https://en.wikipedia.org/wiki/The_Awakening_Conscience",
                         "https://en.wikipedia.org/wiki/Annie_Miller",
                         "https://archive.org/details/preraphaelitism01hunt",
                         "https://archive.org/details/preraphaelitismp02huntuoft",
                         "https://victorianweb.org/painting/whh/paintings/9.html",
                         "https://victorianweb.org/painting/dgr/drawings/18.html",
                         "https://guggums.com/the-pre-raphaelites/the-pre-raphaelite-brotherhood/women-of-the-pre-raphaelite-circle/annie-miller/",
                         "https://web.archive.org/web/20111008111654/http://preraphaelites.net/anniemiller.html",
                         "https://shafe.co.uk/?p=6136",
                         "https://en.wikipedia.org/wiki/William_Holman_Hunt"],
             "pinned_comment": "Hunt's own title for the painting was 'The Still Small Voice'. His friend Thomas Combe renamed it.\n\n"
                               "Which detail gave it away for you: the hands, the cat, or the glove? 👁️"},
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
