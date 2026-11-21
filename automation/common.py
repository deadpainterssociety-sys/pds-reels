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
def save_schedule(s): jsave("schedule.json", sorted(s, key=lambda e: e["date"]))   # stable: same-day order = slot order


# Posting slots (Madrid time). Two a day from 5 Nov 2026: the first scheduled reel of a day goes out at slots[0],
# the second at slots[1]. A reel approved late goes out as soon as it's approved (until publish_until).
def slots(): return list(CONFIG.get("slots") or [CONFIG.get("publish_window", ["18:00"])[0]])
def per_day(): return len(slots())
def publish_until(): return CONFIG.get("publish_until") or CONFIG.get("publish_window", ["", "22:30"])[1]
DROPPED = ("rejected", "skipped")


def day_entries(date, sch=None):
    """that day's reels that still count (not rejected/skipped), in slot order"""
    return [e for e in (sch if sch is not None else schedule()) if e["date"] == date and state(e["slug"])["status"] not in DROPPED]


def slot_time(slug):
    d = date_for(slug)
    if not d: return slots()[0]
    names = [e["slug"] for e in day_entries(d)]
    i = names.index(slug) if slug in names else 0
    return slots()[min(i, per_day() - 1)]


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


# ---------------------------------------------------------------- Shorts <-> long videos (YouTube "Related video" links)
def _norm_title(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", re.sub(r"\(.*?\)", "", t or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^(the|a|an|portrait of( the)?) ", "", t)


def same_painting(a, b):
    """two story.json dicts about the same painting: same painter's surname and the same title (a Short's title may add
    a detail in brackets or after the long one's: 'The Garden of Earthly Delights (right panel, Hell)'), or the same main file"""
    ma, mb = a.get("meta", {}), b.get("meta", {})
    main = lambda st, m: (st.get("images", {}).get(m.get("image"), {}) or {}).get("commons")
    if main(a, ma) and main(a, ma) == main(b, mb): return True
    sur = lambda m: (_norm_title(m.get("painter", "")).split() or [""])[-1]
    if not sur(ma) or sur(ma) != sur(mb): return False
    ta, tb = _norm_title(ma.get("painting")), _norm_title(mb.get("painting"))
    return bool(ta and tb) and (ta == tb or ta.startswith(tb + " ") or tb.startswith(ta + " "))


def _story_slugs(): return sorted(d for d in os.listdir(os.path.join(ROOT, "stories")) if os.path.isfile(os.path.join(ROOT, "stories", d, "story.json")))
def is_long(slug): return slug.endswith("-long") or story(slug).get("format") == "long"
def is_main_short(slug):   # an English Short of the main channel (not a long video, not the Spanish edition)
    return not is_long(slug) and not slug.endswith("-es") and not str(story(slug).get("lang", "en")).startswith("es")


def long_public(slug):
    s = state(slug)
    try: return bool(s.get("youtube_url")) and datetime.datetime.fromisoformat(s["publish_at"]) <= now()
    except (KeyError, ValueError, TypeError): return False


def long_title(slug):
    t = story(slug).get("youtube", {}).get("titles") or [""]
    return t[0] or story(slug).get("meta", {}).get("painting", slug)


def long_for_short(slug):
    """the long video a Short belongs to: story.json "related_long" (a trailer Short; false = none), else the long video
    of the same painting (newest first)"""
    st = story(slug)
    if "related_long" in st: return st["related_long"] or None
    for d in sorted((d for d in _story_slugs() if is_long(d)), reverse=True):
        if same_painting(st, story(d)): return d
    return None


def shorts_for_long(slug):
    """English main-channel Shorts of the same painting as this long video (any status), oldest first"""
    lg = story(slug)
    return [d for d in _story_slugs() if is_main_short(d) and long_for_short(d) == slug
            and (story(d).get("related_long") == slug or same_painting(story(d), lg))]


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
