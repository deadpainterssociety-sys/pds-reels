# Setup — Dead Painters Society autopilot

About 1 hour, once. You only need a browser for every step except the Claude token, which needs one Terminal command.
The order is designed so things work as early as possible: after **step 3** you already get reels on Telegram for review,
and you can post them by hand until the platforms are connected (the bot sends you a ready-to-post file + captions).

Secrets are added in GitHub: **your repo → Settings → Secrets and variables → Actions → New repository secret**.
Names must be typed exactly as written here. GitHub encrypts them; nobody can read them back, not even in a public repo.

---

## 1. GitHub (10 min)

1. Create an account at github.com if you don't have one.
2. Create the repo: github.com/new → name **pds-reels** (done) → **Public** → Create.
   *Why public:* unlimited free Actions minutes and 4-CPU machines (renders twice as fast), and GitHub Pages can give
   Instagram the public video link it requires. Your secrets stay encrypted. (Private works too, but you'd need a paid
   plan for Pages or your own storage bucket, and the free 2,000 minutes/month would be tight.)
3. Let Claude push the code: claude.ai → Settings → Connectors → **GitHub** → connect, then install the Claude GitHub
   App on your account: github.com/apps/claude → Install → *deadpainterssociety-sys* → Only select repositories →
   **pds-reels** → Install.
   Then tell Claude "pushed?" — or upload the files yourself.
4. Repo → **Settings → Pages** → Build and deployment → Source: **GitHub Actions**. Then Actions → **site** →
   Run workflow (publishes the privacy/terms pages and the TikTok login page).
5. Repo → **Actions** tab → if asked, click "I understand my workflows, enable them".

## 2. Telegram review bot (3 min)

1. In Telegram, open **@BotFather** → send `/newbot` → name it e.g. *DPS Review* → pick a username ending in `bot`.
2. Copy the token it gives you → secret **`TELEGRAM_BOT_TOKEN`**.
3. Open your new bot (the link BotFather shows) and press **Start**. That links this chat — only you can control it.

## 3. Claude, who writes the stories (5 min) — needs a Claude Pro, Max, Team or Enterprise plan

1. On your computer, open Terminal (Mac) or PowerShell (Windows) and install Claude Code:
   - Mac: `curl -fsSL https://claude.ai/install.sh | bash`
   - Windows (PowerShell): `irm https://claude.ai/install.ps1 | iex`
2. Run `claude setup-token`, log in with your Claude account in the browser, and copy the long token it prints.
3. Secret **`CLAUDE_CODE_OAUTH_TOKEN`** = that token. (Runs use your Claude subscription, about one story a night.)

## 4. A GitHub key so the system can keep its own tokens fresh (3 min)

1. github.com → your photo → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
   Generate new token.
2. Name *dps-bot*, expiration **366 days** (put a reminder in your calendar), Repository access: **Only select
   repositories → pds-reels**, Permissions → Repository → **Secrets: Read and write**. Generate.
3. Secret **`GH_PAT`** = that token.

**Check point:** Actions tab → **setup-check** → Run workflow. In a minute the bot sends you a checklist.
Then Actions → **stories** → Run workflow → count `3`. In ~1 hour you get the covers of the first 3 reels, and every
morning a reel to review. Until steps 5–7 are done, the 18:00 message gives you the file + captions to post by hand.

---

## 5. YouTube (15 min)

1. console.cloud.google.com → top bar → **New project** → name *DPS* → Create (and select it).
2. Menu → APIs & Services → **Library** → search *YouTube Data API v3* → **Enable**.
3. Menu → **Google Auth Platform** (OAuth consent screen) → Get started → app name *DPS Publisher*, your email →
   Audience **External** → finish. Then **Audience → Publish app** → status **In production**.
   ⚠️ Important: if it stays in *Testing*, the connection dies every 7 days.
4. **Clients → Create client** → type **Web application** → under *Authorized redirect URIs* add
   `https://developers.google.com/oauthplayground` → Create. Copy **Client ID** → secret **`YT_CLIENT_ID`**,
   **Client secret** → secret **`YT_CLIENT_SECRET`**.
5. Open developers.google.com/oauthplayground → ⚙ (top right) → tick **Use your own OAuth credentials** → paste the
   Client ID and secret. On the left, in *Input your own scopes*, paste:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly`
   → **Authorize APIs** → sign in with the Google account that owns the channel (pick the DPS channel if asked) →
   on "Google hasn't verified this app" click **Advanced → Go to DPS Publisher** → Allow.
6. Click **Exchange authorization code for tokens** → copy the **Refresh token** → secret **`YT_REFRESH_TOKEN`**.

## 6. Instagram (15–20 min)

Your account must be a **professional** account (Business or Creator): Instagram → Settings → Account type and tools.

1. developers.facebook.com → log in with Facebook → **My Apps → Create app** → name *DPS Publisher* → use case
   **Manage messaging & content on Instagram** (the Instagram use case) → create (no business portfolio needed).
2. In the app: **Instagram → API setup with Instagram login** → section *Generate access tokens* → **Add account** →
   log in as @thedeadpainterssociety → allow. Then click **Generate token** next to it and copy it →
   secret **`IG_ACCESS_TOKEN`**. (It lasts 60 days; the weekly check renews it automatically through GH_PAT.)
3. Leave the app in Development mode — it works for your own account. If Meta says the account isn't a tester:
   App roles → Roles → **Instagram Testers** → add @thedeadpainterssociety, then accept the invite in Instagram
   (Settings → Apps and websites → Tester invites) and generate the token again.

## 7. TikTok (20 min + TikTok's review)

1. developers.tiktok.com → log in with your TikTok account → **Manage apps → Connect an app**.
2. Fill in: name *DPS Publisher*, category *Entertainment*, description *Publishes our own art-history videos to our
   own account*, and these URLs (already filled in for your repo):
   - Terms of Service: `https://deadpainterssociety-sys.github.io/pds-reels/terms.html`
   - Privacy Policy: `https://deadpainterssociety-sys.github.io/pds-reels/privacy.html`
   - Platform **Web**, website: `https://deadpainterssociety-sys.github.io/pds-reels/`
3. **Add products**: **Login Kit** (Redirect URI: `https://deadpainterssociety-sys.github.io/pds-reels/tiktok/`) and
   **Content Posting API** (turn on *Upload*; *Direct Post* too). Scopes: `user.info.basic`, `video.upload`, `video.publish`.
4. Copy **Client key** → secret **`TIKTOK_CLIENT_KEY`**, **Client secret** → secret **`TIKTOK_CLIENT_SECRET`**.
   (Want to start today? Use the **Sandbox** tab: add your TikTok account as a target user and use the sandbox key/secret;
   switch to the production ones once the app is approved.)
5. **Submit for review** (TikTok asks for a short screen recording: record the Telegram bot → approve → TikTok draft).
6. Run **setup-check** again: the bot sends you a TikTok login link. Open it, approve, copy the code shown on the page,
   then Actions → **tiktok-connect** → Run workflow → paste the code (it expires in a few minutes).

Until the app is audited, TikTok reels arrive as **drafts in your TikTok inbox**: tap the notification, paste the caption
the bot sends, post (≈20 seconds). After TikTok approves the Direct Post audit (weeks), change `"tiktok_mode"` to
`"direct"` in `config.json` and TikTok becomes fully automatic. (Never switch to direct before the audit: TikTok makes
those posts private, permanently.)

---

## Daily life

| When (Madrid) | What happens | You |
|---|---|---|
| ~02:30 | Claude writes the next story (keeps 3 days ready) | — |
| ~08:00 | Today's reel arrives on Telegram: cover, video, captions, facts | ✅ / ❌ / ✏️ |
| any time | ✏️ or any message = change request → new version in ~40 min | review again |
| 18:00 | Approved reel goes out on Instagram, YouTube, TikTok (draft) | paste the TikTok caption |

Telegram commands: `/status` · `/post` (publish approved now) · `/stories 3` · `/rule <text>` (a rule for all future
reels) · `/pause` · `/resume`. Settings (times, platforms, buffer) live in `config.json`.

If something breaks, the bot tells you with a link to the failed run. Mondays, setup-check renews the Instagram token
and checks every connection.
