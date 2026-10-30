r"""Shared helpers for the automatic pipeline. Everything is stored in the repo, so every GitHub Actions job is stateless:

  config.json                    settings (timezone, publish window, platforms, buffer...)
  schedule.json                  [{"date": "2026-11-03", "slug": "caravaggio-goliath"}]   one reel per day
  stories/<slug>/state.json      {"status": ..., per-platform ids/urls, revision notes}
  automation/bot_state.json      Telegram update offset, linked chat id, pending "changes" request

Story status flow:
  draft -> built -> sent -> approved -> posted          (draft = written + checked by Claude, not rendered yet)
                     |  \-> skipped                     (you pressed Skip)
                     \-> revising -> sent               (you asked for changes; Claude redoes it and sends it again)
"""
import datetime, json, os, re, sys, zoneinfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = json.load(open(os.path.join(ROOT, "config.json")))
TZ = zoneinfo.ZoneInfo(CONFIG.get("timezone", "Europe/Madrid"))
ACTIVE = ("draft", "built", "sent", "revising", "approved")


def now():
    fake = os.environ.get("DPS_NOW")          # tests: pretend it is this local time ("2026-11-02T18:05")
    return datetime.datetime.fromisoformat(fake).replace(tzinfo=TZ) if fake else datetime.datetime.now(TZ)
def today(): return now().date().isoformat()


def jload(path, default):
    p = os.path.join(ROOT, path)
    return json.load(open(p)) if os.path.exists(p) else default


def jsave(path, data):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    tmp = p + ".tmp"; json.dump(data, open(tmp, "w"), indent=1, ensure_ascii=False); os.replace(tmp, p)


def schedule(): return jload("schedule.json", [])
def save_schedule(s): jsave("schedule.json", sorted(s, key=lambda e: e["date"]))


def slug_for(date):
    for e in schedule():
        if e["date"] == date: return e["slug"]
    return None


def date_for(slug):
    for e in schedule():
        if e["slug"] == slug: return e["date"]
    return None


def state(slug): return jload(f"stories/{slug}/state.json", {"status": "draft"})


def set_state(slug, **kv):
    s = state(slug); s.update(kv); s["updated"] = now().isoformat(timespec="seconds")
    jsave(f"stories/{slug}/state.json", s); return s


def story(slug): return jload(f"stories/{slug}/story.json", {})


def upcoming(statuses=ACTIVE, from_date=None):
    """scheduled stories from a date on (default today) whose status is in `statuses`, in date order"""
    d0 = from_date or today()
    return [e for e in schedule() if e["date"] >= d0 and state(e["slug"])["status"] in statuses]


def out_dir(slug): return os.path.join(ROOT, "stories", slug, "out")


def captions(slug):
    """parse out/caption.txt (written by pipeline/finalize.py) -> {instagram, tiktok, youtube_title, youtube_desc}"""
    txt = open(os.path.join(out_dir(slug), "caption.txt")).read()
    sec = {m.group(1): m.group(2).strip() for m in re.finditer(r"=== (INSTAGRAM|TIKTOK|YOUTUBE)[^\n]*===\n(.*?)(?=\n=== |\Z)", txt, re.S)}
    yt = sec.get("YOUTUBE", "")
    title = yt.splitlines()[0].replace("Title:", "").strip() if yt else ""
    desc = yt.split("Description:\n", 1)[1].strip() if "Description:\n" in yt else ""
    return {"instagram": sec.get("INSTAGRAM", ""), "tiktok": sec.get("TIKTOK", ""), "youtube_title": title, "youtube_desc": desc}


def title_of(slug):
    st = story(slug); m = st.get("meta", {})
    q = re.sub(r"<[^>]+>", "", st.get("cover", {}).get("question", ""))
    return f"{m.get('painter', slug)}, {m.get('painting', '')} — “{q}”".strip()


def env(name, required=True):
    v = os.environ.get(name, "").strip()
    if required and not v: raise SystemExit(f"missing secret/env {name}")
    return v


def gh_output(**kv):
    """write step outputs for GitHub Actions (or print when run by hand)"""
    path = os.environ.get("GITHUB_OUTPUT")
    lines = "".join(f"{k}={v}\n" for k, v in kv.items())
    if path: open(path, "a").write(lines)
    print(lines, end="")


def set_github_secret(name, value):
    """store/rotate a token as an Actions secret. Needs GH_PAT (fine-grained token on this repo with Secrets: read & write).
    The value goes through stdin, never the command line or the log."""
    import subprocess
    pat = os.environ.get("GH_PAT", "").strip()
    if not pat: print(f"!! cannot save {name}: add the GH_PAT secret (see SETUP.md)"); return False
    repo = os.environ.get("GITHUB_REPOSITORY")
    cmd = ["gh", "secret", "set", name] + (["--repo", repo] if repo else [])
    subprocess.run(cmd, input=value, text=True, check=True, env={**os.environ, "GH_TOKEN": pat}, capture_output=True)
    print(f"saved secret {name}"); return True


def die(msg): print("ERROR:", msg, file=sys.stderr); sys.exit(1)
