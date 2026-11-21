"""Writes story.json for long video #5 (16:9): Repin's Reply of the Zaporozhian Cossacks. The script lives in script.py; shots
and overlays are anchored to words by text (see A()), so the plan survives script edits.
usage: python stories/repin-cossacks-long/plan.py"""
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
 "slug": "repin-cossacks-long", "format": "long", "slot": "2026-11-23", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Ilya Repin", "born": 1844, "died": 1930, "painting": "Reply of the Zaporozhian Cossacks", "year": "1880–1891",
          "museum": "State Russian Museum", "city": "St Petersburg", "image": "cossacks",
          "image_credit": "State Russian Museum, St Petersburg, via Wikimedia Commons (public domain)"},
 "rights": {"creator_died": 1930, "note": "Repin d. 1930: public domain. Period portraits and photographs public domain (Kramskoi 1886, Repin's portraits, photographs before 1910). CC photos (Mikhailovsky Palace, Kharkiv Art Museum, Kachanivka) credited on screen and in the description. Music: Mussorgsky, Musopen recordings, public domain."},
 "say": {"1670s": "sixteen-seventies", "1878": "eighteen seventy-eight", "1880": "eighteen eighty", "1885": "eighteen eighty-five",
         "1888": "eighteen eighty-eight", "1891": "eighteen ninety-one", "1897": "eighteen ninety-seven", "1907": "nineteen oh seven",
         "2014": "twenty fourteen", "2022": "twenty twenty-two"},
 "ipa": {"Repin": "ɹˈɛpɪn", "Repin's": "ɹˈɛpɪnz", "Zaporozhian": "zˌæpəɹˈoʊʒiən", "Zaporozhians": "zˌæpəɹˈoʊʒiənz", "Mehmed": "mˈɛmɛd",
         "Dnieper": "nˈiːpɚ", "Khortytsia": "xɔɹtˈɪtsjə", "Mamontov": "mˈɑːməntɔf", "Abramtsevo": "ɐbɹˈɑːmtsɨvə", "Serov": "sɛɹˈɔf",
         "Tarnovsky": "tɑːɹnˈɔfski", "Yavornytsky": "jɑːvɔɹnˈɪtski", "Sirko": "sˈiːɹkoʊ", "Dragomirov": "dɹɑːɡəmˈiːɹɔf",
         "Stravinsky": "stɹəvˈɪnski", "Alekseyev": "ɐlɛksˈeɪɛf", "Kuban": "kuːbˈɑːn", "Benois": "bɛnwˈɑː", "Vitebsk": "vˈiːtɛpsk",
         "Kharkiv": "xˈɑːɹkɪf", "Chuhuiv": "tʃuːhˈuːjɪf", "Kyiv": "kˈiːɪf", "Dmytro": "dmˈɪtɹoʊ", "Vasyl": "vˈɑːsɪl", "Savva": "sˈɑːvə",
         "Fyodor": "fjˈɔːdɚ", "Bulba": "bˈʊlbə", "Ilya": "ɪljˈɑː"},
 # Chirp 3 HD (Enceladus): plain respellings for the names it may anglicise
 "chirp_say": {"Yavornytsky": "Yavor-nitsky", "Khortytsia": "Khor-titsya", "Abramtsevo": "Ah-bram-tsevo", "Chuhuiv": "Choo-hoo-yiv",
               "Alekseyev": "Alek-say-ev", "Dragomirov": "Drago-meerov", "Sirko": "Seerko", "Benois": "Ben-wah", "Mamontov": "Mamon-tov"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC, "facts": FACTS, "next": False,
 "youtube": {"titles": ["These Men Are Laughing at an Emperor", "A Tsar Paid a Fortune for This Insult"],
             "description_lead": "Ilya Repin spent eleven years (1880–1891) painting the Zaporozhian Cossacks writing their legendary, very rude reply to the Ottoman sultan Mehmed IV, a letter that historians think was probably never written as we know it. Almost every laughing face is a real person Repin knew: the historian Dmytro Yavornytsky is the scribe, General Mikhail Dragomirov is the ataman Ivan Sirko, the opera bass Fyodor Stravinsky is somewhere in the crowd, and a court official who refused to pose lent the back of his bald head without knowing it. Tsar Alexander III paid 35,000 rubles for the painting. Repin's second version survives in Kharkiv, Ukraine.",
             "hashtags": ["#arthistory", "#repin", "#cossacks"],
             "credits": ["Paintings and drawings by Ilya Repin (State Russian Museum, St Petersburg; Tretyakov Gallery, Moscow; Kharkiv Art Museum; Ateneum, Helsinki; other collections): public domain, via Wikimedia Commons.",
                         "Alexander III by Ivan Kramskoi, 1886; Sultan Mehmed IV, c. 1682; self-portrait of Valentin Serov; plan of the Zaporozhian Sich, 1742; photographs of Dmytro Yavornytsky, Mikhail Dragomirov and Fyodor Stravinsky; Palace Square, St Petersburg, 1890s: public domain, via Wikimedia Commons.",
                         "The Mikhailovsky Palace (State Russian Museum), St Petersburg: photo Andrey Korzun, CC BY-SA 4.0, via Wikimedia Commons.",
                         "Kharkiv Art Museum: photo San4oss, CC BY-SA 4.0, via Wikimedia Commons.",
                         "Kachanivka palace: photo Dmytro Petishkin, CC BY 4.0, via Wikimedia Commons.",
                         "Zdravnevo, Repin's estate near Vitebsk: photo GAlexandrova, CC BY-SA 4.0, via Wikimedia Commons."],
             "thumbnail": {"image": "cossacks", "focus": [0.70, 0.30], "span": 0.34, "words": "INSULTING an Empire"},
             "intro_chapter": "The Laugh", "outro_chapter": "Where It Hangs Today",
             "sources": ["https://rusmuseumvrm.ru/data/collections/painting/19_20/zh_4005/?lang=en",
                         "https://en.wikipedia.org/wiki/Reply_of_the_Zaporozhian_Cossacks",
                         "https://en.wikipedia.org/wiki/Correspondence_between_the_Ottoman_sultan_and_the_Cossacks",
                         "https://mail.19thc-artworldwide.org/spring02/the-legendary-cossacks-anarchy-and-nationalism-in-the-conceptions-of-ilya-repin-and-nikolai-gogol",
                         "https://www.rbth.com/arts/333391-ilya-repin-cossacks-letter-real-fake",
                         "https://www.birmingham.ac.uk/documents/college-artslaw/cmr1900/9789004309173-125-waugh.pdf",
                         "https://www.vokrugsveta.ru/article/235851",
                         "https://job.gorod.dp.ua/history/doc/zaporozhtsi.pdf",
                         "https://www.sgu.ru/archive/old.sgu.ru/files/nodes/9850/08.pdf",
                         "https://www.encyclopediaofukraine.com/pages/Z/A/ZaporizhiaThe.htm",
                         "https://encyclopediaofukraine.com/pages%5CZ%5CA%5CZaporozhianSich.htm",
                         "https://www.britannica.com/biography/Mehmed-IV",
                         "https://en.wikipedia.org/wiki/Kharkiv_Art_Museum",
                         "https://www.theartnewspaper.com/2022/03/25/ukraine-culture-in-peril",
                         "https://kyivindependent.com/kharkiv-art-museum-in-flames-after-cynical-russian-drone-attack/",
                         "https://www.humanrightsfirst.org/russian-attack-devastates-kharkiv-art-museum",
                         "https://www.rferl.org/a/ukraine-wartime--trend-ilya-repin-painting-cossacks-reply-recreation/33612657.html"],
             "pinned_comment": "Historians think the Cossacks' letter is probably a legend. Repin painted the laugh anyway, with his friends in costume.\n\n"
                               "If you could add one real person to this crowd, who would it be? 🖤"},
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
print(f"story.json: {len(L)} lines, {sum(len(w) for w in WORDS.values())} words, {len(S)} shots, {len(O)} overlays")
