"""The Spanish edition (test approved by Gigi, 12 Nov 2026): a Spanish twin of an English story, voiced by Google's
es-ES-Chirp3-HD-Gacrux and published on the Spanish channel. Same images, shots, music and effects; Spanish script,
captions, cover, overlays and texts.

usage: python automation/edition.py make <slug> <es.json>    -> stories/<slug>-es/story.json (+ schedule_es.json entry)
       python automation/edition.py check <slug>-es           the anchors that moved, for a look at the stills

<es.json> (written by Claude): {"lines": [{"id", "perf"}] (the SAME line ids, in order), "cover": {"question", "work"?},
  "overlays": {"<index in the English overlays list>": {"text"?, "kicker"?}}, "anchors": {"hook.4": "hook.3", ...}
  (English word anchor -> Spanish word anchor, for the moments that must land on a word: hits, rings, sfx),
  "teaser", "caption", "caption_short", "youtube_title", "hashtags" [YouTube, ~10], "meta_es": {"painting", "museum", "city"}}
Every other anchor "line.k" moves to the same relative position in the Spanish line (word k of n -> word k*m/n of m);
line starts and ends ("line", "line$") stay exact.
"""
import copy, datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, jload, jsave, story

ANCHOR = re.compile(r"^([A-Za-z][\w-]*)(?:\.(\d+))?(\$?)([+-][\d.]+)?$")
SCHED = "schedule_es.json"


def words(line): return " ".join(p[0] for p in line["perf"]).replace("...", "…").split()


def remap(value, n_en, n_es, overrides, moved):
    if not isinstance(value, str): return value
    m = ANCHOR.match(value)
    if not m or m.group(1) not in n_en: return value
    lid, k, end, off = m.group(1), m.group(2), m.group(3), m.group(4) or ""
    if k is None: return value                                   # "line" / "line$" (+offset): exact in any language
    base = f"{lid}.{k}"
    if base in overrides: new = overrides[base]
    else:
        kk = min(n_es[lid] - 1, round(int(k) * n_es[lid] / max(1, n_en[lid]))); new = f"{lid}.{kk}"
    moved.append((value, new + end + off))
    return new + end + off


def walk(o, f):
    if isinstance(o, dict): return {k: walk(v, f) for k, v in o.items()}
    if isinstance(o, list): return [walk(v, f) for v in o]
    return f(o)


def make(slug, patch_path):
    en = story(slug); es = json.load(open(patch_path))
    ids_en = [l["id"] for l in en["lines"]]; ids_es = [l["id"] for l in es["lines"]]
    if ids_en != ids_es: sys.exit(f"line ids differ: {ids_en} vs {ids_es}")
    n_en = {l["id"]: len(words(l)) for l in en["lines"]}; n_es = {l["id"]: len(words(l)) for l in es["lines"]}
    st = copy.deepcopy(en); moved = []; ov = es.get("anchors", {})
    f = lambda v: remap(v, n_en, n_es, ov, moved)
    for k in ("shots", "overlays", "nocap", "sfx", "music"):
        if k in st: st[k] = walk(st[k], f)
    if "cover" in st and st["cover"].get("answered_by"): st["cover"]["answered_by"] = es.get("cover", {}).get("answered_by", "")
    for i, o in es.get("overlays", {}).items(): st["overlays"][int(i)].update(o)
    st["cover"].update({k: v for k, v in es.get("cover", {}).items()})
    for k in ("say", "ipa", "respell", "experiment", "speed"): st.pop(k, None)
    st.update(slug=f"{slug}-es", edition_of=slug, lang="es", voice="chirp", lines=es["lines"], next=False,
              teaser=es.get("teaser", ""), caption=es["caption"], caption_short=es.get("caption_short", ""),
              youtube_title=es["youtube_title"], hashtags=es.get("hashtags", []), meta_es=es.get("meta_es", {}),
              ai_voice_line="🎙️ Narración con voz de IA")
    st.pop("hashtags_instagram", None); st.pop("hashtags_tiktok", None)
    d = os.path.join(ROOT, "stories", f"{slug}-es"); os.makedirs(d, exist_ok=True)
    json.dump(st, open(os.path.join(d, "story.json"), "w"), indent=1, ensure_ascii=False)
    sch = jload(SCHED, [])
    if not any(e["slug"] == f"{slug}-es" for e in sch):
        sch.append({"slug": f"{slug}-es", "added": datetime.date.today().isoformat()}); jsave(SCHED, sch)
    print(f"stories/{slug}-es/story.json: {sum(n_es.values())} words (English {sum(n_en.values())}), {len(moved)} anchors moved")
    for a, b in moved:
        if a != b: print(f"   {a:>16} -> {b}")


if __name__ == "__main__":
    if sys.argv[1] == "make": make(sys.argv[2], sys.argv[3])
    else: sys.exit(__doc__)
