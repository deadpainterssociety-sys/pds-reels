"""Checks a long video's story before it is voiced and rendered (LONG.md; workflow longform.yml).
usage: python automation/validate_long.py <slug>      prints the problems; exit 1 if there are any
"""
import json, os, re, sys
from common import ROOT


def words(t): return len(re.sub(r"[*_]", "", t).split())


def check(slug, light=False):
    """light: only the story itself (a fresh checkout has no src/, build/ or out/)"""
    d = os.path.join(ROOT, "stories", slug)
    p = []
    try: st = json.load(open(os.path.join(d, "story.json")))
    except (OSError, ValueError) as e: return [f"story.json unreadable: {e}"]
    if st.get("format") != "long": p.append('format must be "long"')
    for f in ("script.py", "plan.py", "visuals.py", "facts.json"):
        if not os.path.exists(os.path.join(d, f)): p.append(f"missing {f}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", st.get("slot", "")): p.append('top-level "slot": "YYYY-MM-DD" missing')
    lines = st.get("lines", [])
    texts = [" ".join(x[0] for x in l["perf"]) for l in lines]
    n = sum(words(t) for t in texts)
    if not 800 <= n <= 1200: p.append(f"{n} spoken words (want 850–1,100)")
    if texts:
        first = re.sub(r"[*_]", "", texts[0])
        if words(first) > 12: p.append(f"line 1 has {words(first)} words (≤ 10: one claim about the painting)")
        if re.search(r"\b1\d{3}\b|\b20\d\d\b", first): p.append("line 1 has a date: dates go later")
        if not re.fullmatch(r"It hangs in the .+, in .+\.", texts[-1].strip()): p.append('last line must be exactly "It hangs in the <Museum>, in <City>."')
    facts = st.get("facts", [])
    if len(facts) < 18: p.append(f"{len(facts)} facts (want 20–30, one per narrated claim)")
    if any(not f.get("source", "").startswith("http") for f in facts): p.append("a fact without a source URL")
    imgs = st.get("images", {})
    main = st.get("meta", {}).get("image")
    if main not in imgs: p.append("meta.image is not one of the images")
    for k, im in imgs.items():
        f = os.path.join(d, im.get("file", ""))
        if not light and not os.path.exists(f): p.append(f"image {k}: {im.get('file')} not downloaded")
    for t in st.get("music", {}).get("tracks", []):
        if not light and not os.path.exists(os.path.join(d, t.get("file", ""))): p.append(f"music {t.get('file')} not downloaded")
        if not t.get("credit"): p.append(f"music {t.get('file')} has no credit line")
    yt = st.get("youtube", {})
    titles = yt.get("titles", [])
    if len(titles) != 2: p.append("youtube.titles: two titles (A and B)")
    for t in titles:
        if len(t) > 60: p.append(f"title over 60 characters: {t}")
    for k in ("description_lead", "hashtags", "credits", "sources", "thumbnail", "intro_chapter", "outro_chapter", "pinned_comment"):
        if not yt.get(k): p.append(f"youtube.{k} missing")
    if re.search("[\\u2764\\u2665\\U0001F5A4\\U0001F90D\\U0001F90E\\U0001F9E1\\U0001F49B-\\U0001F49F\\U0001F493-\\U0001F498\\U0001FA75-\\U0001FA77]", json.dumps(yt, ensure_ascii=False)):
        p.append("a heart emoji in the youtube fields: our signature is 👁️ (PLAYBOOK, 23 Nov)")
    credits = " ".join(yt.get("credits", []))
    for k, im in imgs.items():
        c = im.get("credit")
        if c:
            author = re.search(r"photo (?:by )?([^,]+),", c)
            if author and author.group(1).strip() not in credits: p.append(f"CC image {k}: '{author.group(1).strip()}' missing from youtube.credits")
            if not any(o.get("type") == "credit" for o in st.get("overlays", [])): p.append("CC images need an on-screen credit overlay")
    ov = st.get("overlays", [])
    if any(o.get("type") == "year" for o in ov): p.append("big date cards (year overlays) are not allowed in long videos")
    ch = [o for o in ov if o.get("type") == "chapter"]
    if not 4 <= len(ch) <= 7: p.append(f"{len(ch)} chapter cards (want 4–6)")
    names = {o.get("text") for o in ch}
    if yt.get("outro_chapter") in names: p.append("outro_chapter repeats a chapter name")
    if not any(o.get("type") == "pin" for o in ov): p.append("no museum pin on the ending")
    if not light:
        for f in ("thumb_a.jpg", "thumb_b.jpg"):
            if not os.path.exists(os.path.join(d, "out", f)): p.append(f"out/{f} missing (python pipeline/thumb.py {slug})")
        if not os.path.exists(os.path.join(d, "build", "resolved.json")): p.append("never built (build_story.py)")
    return p


if __name__ == "__main__":
    slug = sys.argv[1]
    probs = check(slug)
    print("PROBLEMS:\n- " + "\n- ".join(probs) if probs else f"{slug}: OK")
    sys.exit(1 if probs else 0)
