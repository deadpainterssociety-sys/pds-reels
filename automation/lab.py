"""After Claude wrote lab/brief.json (LAB.md): check it, store it privately, save the TikTok numbers it added, and send
the brief to Telegram with a ✅ / ❌ per proposal.

usage: python automation/lab.py publish [dir]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import today

KINDS = ("rule", "experiment", "story")


def check(b):
    p = []
    if not str(b.get("summary", "")).strip(): p.append("summary missing")
    for i, x in enumerate(b.get("proposals", [])):
        for k in ("id", "kind", "title", "change", "why"):
            if not str(x.get(k, "")).strip(): p.append(f"proposal {i + 1}: {k} missing")
        if x.get("kind") not in KINDS: p.append(f"proposal {i + 1}: kind must be rule, experiment or story")
        if x.get("kind") == "story":
            st = x.get("story") or {}
            for k in ("painting", "museum", "angle", "format"):
                if not str(st.get(k, "")).strip(): p.append(f"proposal {i + 1}: story.{k} missing")
        if x.get("kind") == "experiment":
            e = x.get("experiment") or {}
            for k in ("id", "question", "a", "b", "metric"):
                if not str(e.get(k, "")).strip(): p.append(f"proposal {i + 1}: experiment.{k} missing")
    return p


def publish(d="lab"):
    import release, metrics, bot
    path = os.path.join(d, "brief.json")
    if not os.path.exists(path): raise SystemExit("Claude didn't write lab/brief.json")
    b = json.load(open(path)); b["date"] = today()
    ps = b.get("proposals", [])   # up to 3 formula proposals + up to 3 story ideas (topic waves)
    ps = [x for x in ps if x.get("kind") != "story"][:3] + [x for x in ps if x.get("kind") == "story"][:3]
    b["proposals"] = [dict(x, id=f"P{i + 1}") for i, x in enumerate(ps)]
    probs = check(b)
    if probs: raise SystemExit("brief.json: " + "; ".join(probs))
    release.data_put(f"brief-{b['date']}.json", json.dumps(b, indent=1, ensure_ascii=False).encode())
    if os.path.exists(os.path.join(d, "waves", "waves.json")):
        release.data_put(f"waves-{b['date']}.json", open(os.path.join(d, "waves", "waves.json"), "rb").read())
    if os.path.exists(os.path.join(d, "brief.md")):
        release.data_put(f"brief-{b['date']}.md", open(os.path.join(d, "brief.md"), "rb").read(), "text/markdown")
    metrics.push(d)
    bot.send_brief(b["date"])
    print(f"brief {b['date']}: {len(b['proposals'])} proposal(s) sent")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "publish": publish(sys.argv[2] if len(sys.argv) > 2 else "lab")
    else: raise SystemExit(__doc__)
