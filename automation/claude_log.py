"""Turn Claude Code's --output-format stream-json into a readable Actions log; exit 1 if the run ended in an error.
usage: claude -p ... --output-format stream-json --verbose | python automation/claude_log.py"""
import json, sys

ok = True
for line in sys.stdin:
    try: ev = json.loads(line)
    except Exception: print(line, end=""); continue
    t = ev.get("type")
    if t == "assistant":
        for b in ev.get("message", {}).get("content", []):
            if b.get("type") == "text" and b["text"].strip(): print("💬", b["text"].strip()[:1500], flush=True)
            elif b.get("type") == "tool_use":
                i = b.get("input", {})
                arg = i.get("command") or i.get("file_path") or i.get("url") or i.get("query") or i.get("pattern") or ""
                print(f"🔧 {b['name']}: {str(arg)[:300]}", flush=True)
    elif t == "result":
        ok = not ev.get("is_error") and ev.get("subtype") == "success"
        print(f"\n=== Claude finished: {ev.get('subtype')} · {ev.get('num_turns')} turns · {round(ev.get('duration_ms', 0) / 60000, 1)} min")
        if ev.get("result"): print(ev["result"][:3000])
sys.exit(0 if ok else 1)
