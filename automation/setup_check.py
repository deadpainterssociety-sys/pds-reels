"""Check every connection and report a checklist (GitHub job summary + Telegram). Safe to run any time.

usage: python automation/setup_check.py [--weekly]     (--weekly: only speak up on Telegram when something is broken)
Never prints secret values. Also links the Telegram chat if you already sent /start to the bot.
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import today, CONFIG, ROOT

rows, broken = [], []


def row(ok, name, detail=""):
    rows.append(f"| {'✅' if ok is True else ('➖' if ok is None else '❌')} | {name} | {detail} |")
    if ok is False: broken.append(name)


def has(*names): return all(os.environ.get(n, "").strip() for n in names)


def pages_url():
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo: return ""
    owner, name = repo.split("/")
    return f"https://{owner.lower()}.github.io/{name}"


def main(weekly=False):
    # Telegram
    if has("TELEGRAM_BOT_TOKEN"):
        try:
            import telegram as T, bot
            me = T.call("getMe")
            if not bot.chat_id(): bot.poll()   # only to link the chat the first time; afterwards the inbox listener owns Telegram
            chat = bot.chat_id()
            row(True, "Telegram bot", f"@{me['username']}" + ("" if chat else f" — now send <code>/start</code> to @{me['username']} and run this check again"))
            if not chat: broken.append("Telegram chat not linked")
        except Exception as e: row(False, "Telegram bot", str(e)[:150])
    else: row(False, "Telegram bot", "add secret TELEGRAM_BOT_TOKEN (from @BotFather)")
    # Claude
    tok = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", "").strip()
    note = ""
    if tok and re.search(r"\s", tok): note = " (it has a line break from copying; fixed automatically, but re-pasting it on one line is cleaner)"
    if tok and not "".join(tok.split()).startswith("sk-ant-"): note = " — but it doesn't look like a Claude token (should start with sk-ant-): run `claude setup-token` again"
    row(bool(tok or has("ANTHROPIC_API_KEY")) and "doesn't look" not in note, "Claude (writes the stories)",
        ("token present" + note) if tok or has("ANTHROPIC_API_KEY") else "add CLAUDE_CODE_OAUTH_TOKEN (run `claude setup-token`)")
    # GH_PAT
    if has("GH_PAT"):
        r = subprocess.run(["gh", "secret", "list", "--repo", os.environ.get("GITHUB_REPOSITORY", "")], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env={**os.environ, "GH_TOKEN": os.environ["GH_PAT"]})
        row(r.returncode == 0, "GH_PAT (keeps tokens fresh)", "can manage secrets" if r.returncode == 0 else "cannot manage secrets: give it 'Secrets: Read and write' on this repo")
    else: row(False, "GH_PAT (keeps tokens fresh)", "add a fine-grained token with Secrets read/write on this repo")
    # Pages (public video link for Instagram)
    base = pages_url()
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY')}/pages",
                                     headers={"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}", "Accept": "application/vnd.github+json"})
        info = json.load(urllib.request.urlopen(req, timeout=30))
        row(info.get("build_type") == "workflow", "GitHub Pages (public video link)", info.get("html_url", base) if info.get("build_type") == "workflow"
            else "set Settings → Pages → Source = GitHub Actions")
    except Exception:
        row(False, "GitHub Pages (public video link)", "turn on: Settings → Pages → Source = GitHub Actions (repo must be public on the free plan)")
    # Platforms
    import instagram, youtube, tiktok
    for name, need, mod in (("Instagram", ["IG_ACCESS_TOKEN"], instagram), ("YouTube", ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"], youtube)):
        if not CONFIG["platforms"].get(name.lower(), True): row(None, name, "turned off in config.json"); continue
        if not has(*need): row(False, name, "add " + ", ".join(n for n in need if not has(n))); continue
        try:
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf): mod.check()
            row(True, name, buf.getvalue().strip().split(": ", 1)[-1])
        except Exception as e: row(False, name, str(e)[:180])
    # Learning loop: can we READ the numbers? (➖ = posting works, but the brief misses these numbers)
    if has("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        try:
            ana = os.environ.get("YT_ANALYTICS_API", "https://youtubeanalytics.googleapis.com").rstrip("/")
            q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": "2026-10-01", "endDate": today(), "metrics": "views"})
            youtube.http("GET", f"{ana}/v2/reports?{q}", {"Authorization": f"Bearer {youtube.token()}"})
            row(True, "YouTube numbers (learning loop)", "Analytics API readable")
        except Exception as e:
            row(None, "YouTube numbers (learning loop)", "not yet: enable the YouTube Analytics API and get a refresh token with "
                "the yt-analytics.readonly scope (SETUP step 5)" if ("403" in str(e) or "401" in str(e)) else str(e)[:150])
    if has("IG_ACCESS_TOKEN"):
        try:
            instagram.req("GET", f"{instagram.uid()}/insights", metric="reach", period="day")
            row(True, "Instagram numbers (learning loop)", "insights readable")
        except Exception as e:
            row(None, "Instagram numbers (learning loop)", "not yet: add the instagram_manage_insights permission and generate a new token "
                "(SETUP step 6)" if ("permission" in str(e).lower() or "(#10)" in str(e) or "(#200)" in str(e)) else str(e)[:150])
    if CONFIG["platforms"].get("tiktok", True):
        if not has("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"): row(False, "TikTok", "add TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET")
        elif not has("TIKTOK_REFRESH_TOKEN"):
            row(False, "TikTok", "connect your account: open the TikTok login link the bot sent you on Telegram, approve, "
                                 "then run the <b>tiktok-connect</b> workflow with the code shown")
            try:
                import bot, telegram as T
                if bot.chat_id(): T.send(bot.chat_id(), "🎵 <b>Connect TikTok</b>\n1. Open this link and approve:\n" + T.esc(tiktok.auth_url(base + "/tiktok/")) +
                                         "\n2. Copy the code shown on the page.\n3. GitHub → Actions → <b>tiktok-connect</b> → Run workflow → paste the code.")
            except Exception as e: print("could not send the TikTok link:", e)
        else:
            try:
                import io, contextlib
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf): tiktok.check()
                row(True, "TikTok", buf.getvalue().strip().split(": ", 1)[-1] + f" · mode: {CONFIG.get('tiktok_mode')}")
            except Exception as e: row(False, "TikTok", str(e)[:180])
    else: row(None, "TikTok", "turned off in config.json")

    table = "| | Connection | Detail |\n|---|---|---|\n" + "\n".join(r for r in rows if r.startswith("|")) + "\n" + "".join(r for r in rows if not r.startswith("|"))
    if os.environ.get("GITHUB_STEP_SUMMARY"): open(os.environ["GITHUB_STEP_SUMMARY"], "a").write("## Setup check\n\n" + table)
    print(table)
    try:
        import bot
        if bot.chat_id() and (not weekly or broken):
            import telegram as T
            lines = [re.sub(r"^\| (.*?) \| (.*?) \| (.*?) \|$", r"\1 <b>\2</b> — \3", r) for r in rows if r.startswith("|")]
            T.send(bot.chat_id(), ("⚠️ <b>Something needs attention</b>\n" if broken else "🔧 <b>Setup check</b>\n") + "\n".join(lines))
    except Exception as e: print("telegram report failed:", e)
    if weekly and broken: sys.exit(1)


if __name__ == "__main__":
    main("--weekly" in sys.argv)
