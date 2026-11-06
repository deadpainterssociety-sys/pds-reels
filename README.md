# Dead Painters Society — autopilot

Daily ~60-second art-history reels for **@thedeadpainterssociety**, made and published automatically, with one human
check on Telegram. Free to run (GitHub Actions + open-source models); the stories are written by Claude.

```
02:30  stories   Claude picks a painting, verifies every fact, writes the script, fetches public-domain images,
                 voices it, checks it by ear (speech recogniser) and by eye (stills + cover), schedules it (2 a day)
08:00  build     today's two reels are rendered side by side and sent to Telegram: cover + video + captions + facts, ✅ ❌ ✏️
any    inbox     listens to Telegram (answers in seconds); ✏️ / any text = Claude revises and re-sends (revise workflow)
14:00  inbox     first approved reel -> Instagram Reels, YouTube Shorts, TikTok (inbox draft until TikTok's audit)
21:00  inbox     second approved reel -> same
every 3 h  metrics  each reel's numbers -> private data store (🔥 alert when one takes off)
Mon+Thu  lab     Claude analyses the numbers (LAB.md) -> brief on Telegram with ✅/❌ per proposed formula change
Mon    setup-check   renews the Instagram token, checks every connection, tells you if anything is broken
```

**Start here: [SETUP.md](SETUP.md).** The channel's rules: [PLAYBOOK.md](PLAYBOOK.md). Claude's brief: [CLAUDE.md](CLAUDE.md).
Ideas and history: [STORY_QUEUE.md](STORY_QUEUE.md). Settings: [config.json](config.json).

| Folder | What |
|---|---|
| `pipeline/` | the reel factory: TTS (Kokoro), recogniser check (Parakeet), story resolver, depth maps, music/SFX, cover, packaging |
| `studio/` | Remotion project — `src/reel/Reel.tsx` is the video engine, driven entirely by `story.json` |
| `stories/<slug>/` | one folder per reel (`story.json`, `state.json`, cover + captions); `night-watch-cut` is the reference |
| `automation/` | Telegram bot, publishers (Instagram, YouTube, TikTok), scheduling, quality gate, releases |
| `.github/workflows/` | `stories`, `build`, `inbox`, `revise`, `setup-check`, `tiktok-connect`, `site` |
| `site/` | tiny public site on GitHub Pages: privacy/terms pages, TikTok login page, and the day's video link for Instagram |
| `tests/` | `python tests/test_automation.py <out dir>` — the whole review → publish flow against mock APIs |

Local use: `./setup.sh` once, then `./make_reel.sh night-watch-cut` renders the reference reel end to end.

Rendered videos are kept as **draft releases** (private, even in a public repo) named `reel-<slug>`; source images too,
so the git history stays small.
