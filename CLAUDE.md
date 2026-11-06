# CLAUDE.md — producer brief for Dead Painters Society

You are the producer of **@thedeadpainterssociety**: daily ~60-second reels that tell one true, surprising story behind a
famous painting, for a Gen-Z audience (Instagram Reels, TikTok, YouTube Shorts). You run unattended inside GitHub
Actions (or locally). Nobody can answer questions: make the best call, keep quality high, and leave clear notes.

**Read `PLAYBOOK.md` first, every run. It is the law** — especially its last section, *Learned from feedback*: those are
Gigi's own corrections and override everything else. `stories/night-watch-cut/story.json` is the reference reel
(approved by Gigi): copy its structure, pacing and level of visual care.

## What you may and may not touch

- Write only: `stories/<slug>/…` (story.json, src/ images, out/), `STORY_QUEUE.md`, `pipeline/pronounce.json`
  (global pronunciation fixes), and the schedule through `python automation/plan.py add <slug>` (never edit
  `schedule.json` by hand). In a revision you may also append a rule to PLAYBOOK.md's last section.
- Never: publish anything, call the Telegram/Instagram/YouTube/TikTok APIs, read or print secrets/env tokens, edit
  `automation/`, `.github/`, `config.json`, or delete other stories. Don't `git commit` / `git push` — the workflow does.

## The job: produce N new reels

For each reel, do steps 1–10 completely before starting the next one. Budget ≈ 20–30 minutes per reel.

### 1. Pick the story
- `python automation/plan.py posted` lists every story already made: never repeat a painting.
- Read `STORY_QUEUE.md` **Pinned** first: a dated row within 5 days of today, or a *next days* row, is your first story
  (a dated one is scheduled ON its date: `python automation/plan.py add <slug> <date>`). Then the Ideas, and the last
  3–5 stories' moods/museums/`hook_type`s; alternate mood and museum (PLAYBOOK §3). Two reels go out each day (14:00
  and 21:00), so the two reels of a day should differ in mood and museum too.
- Hard filters: painter died before 1956 (EU 70-year rule; for works after 1930 also mind the US rule), the painting hangs
  in a visitable museum, and Wikimedia Commons has a public-domain image of it ≥ 2000 px. If an idea fails, take another.
- One throughline only. If you need a second story to explain the first, pick a different angle.
- Decide the `hook_type` first (PLAYBOOK §2: `dark`, `time-gap`, `craft`, `sacred-strange`, `dark-legend`, `damage`,
  `hidden`). Never the same type three reels in a row. If you can't say the promise in one of these, the angle is weak:
  pick another. About one story in four may be a lesser-known painting with a dark or uncanny story.
- Nudity in the painting → `meta.nude: true` and plan safe framing from the start (PLAYBOOK §1 "Nudes").
- **A test running in `EXPERIMENTS.md`?** Give each new story the arm that keeps the two arms balanced (count the
  stories that already have `"experiment": {"id": …}` for it; on a tie take A), follow that arm's instruction, and
  record `"experiment": {"id": "E1", "arm": "A"}` in story.json. Everything else stays as the playbook says.
- Slug: `painter-keyword` in lowercase ASCII (e.g. `caravaggio-goliath`).

### 2. Research and verify (this is what protects the channel)
- WebSearch, then WebFetch the best results: the museum's own page first, then Wikipedia **and its cited sources**,
  then a scholar/catalogue/major newspaper. Every claim you narrate needs ≥ 1 solid source; use 2 when sources differ.
- Numbers, dates, names and quotes must match the source exactly. Quotes must be checked word for word or dropped.
- Where scholars hedge, the narration hedges ("historians think…", "the legend says…"). Never state a legend as fact.
- Write `facts`: `[{"claim": "...", "source": "https://… ; https://…"}]` — one entry per narrated claim (6–10 entries).
- When you are not sure, cut the claim. A shorter true story beats a richer shaky one.

### 3. Images (Wikimedia Commons)
- Search: `python pipeline/commons.py search "<query>" 10` · details/licence: `python pipeline/commons.py info "File:…"`.
- Main painting: the best public-domain file (≥ 2000 px). Then 3–5 supporting images that SHOW the backstory (the
  painter's self-portrait, period views, documents, photos, other works, a copy). Prefer *Public domain* / *CC0*; a CC BY /
  CC BY-SA file is fine only with `"credit"` set on that image (it goes into the caption) and a `credit` overlay.
- Declare each image in story.json with `"file": "src/<name>.jpg"` and `"commons": "File:<exact title>"`, then download
  with `./make_reel.sh <slug> 0 0`. Wikimedia rate-limits CI machines: the downloader waits and falls back to big
  thumbnails by itself — be patient, it can take 5–25 minutes (give that Bash call a timeout of 1800000 ms). Small images (< 1500 px) are shown framed (`z < 1`,
  `"frame": true`), never blown up full-screen.
- Main image gets `"depth": true` (2.5D parallax) and `"long": 3840`.

### 4. Script (`lines`) — read PLAYBOOK §1 "Script and voice" again before writing
- Shape: hook → painting revealed by 3 s → 4–7 short backstory beats in time order → back to the painting →
  payoff that answers the cover question → **last line exactly in this form: "It hangs in the <Museum>, in <City>."**
- **The hook (line 1) is ONE punchy line, ≤ 12 words, making a claim about the painting on screen**: "Nobody was ever
  supposed to see *this.*" Never a date or a scene-setting ("One morning in 1911…", "A woman walks into…"): week-1
  viewers swiped those away in under 2 s. Dates go in the second line.
- `teaser` (≤ 48 characters): how the reel the day BEFORE announces this one on its silent NEXT card, e.g. "The nude the
  Inquisition investigated", "Rembrandt's masterpiece, cut to fit a wall". A plain intriguing phrase: no question mark,
  no "you won't believe", no superlatives.
- `tail`: 2.2 (room for the NEXT card after the last line).
- 130–145 spoken words. Short phrases; each phrase `[text, pause_after_s, speed]` (0.25–0.4 s between clauses,
  0.8–1.0 s after a beat lands; speed 0.9–0.97, 0.78–0.88 for words that must hit). `*word*` = italic caption.
- Years and numbers: write digits in the text and add the spoken form to `say` ("1715": "seventeen fifteen").
  Names the voice may get wrong go to `ipa` (story) or `pipeline/pronounce.json` → `en-us` → `ipa` (if reusable).
- Plain, vivid, spoken English. No clichés ("little did they know"), no rhetorical lists, no jokes at the end.

### 5. Voice check (by ear, via the recogniser)
- `./make_reel.sh <slug> 1 2`. It prints the duration/wpm and, per line, `matched/total heard: …`.
- Every line must come back N/N as written (digits vs words are fine). Fix mishearings: usually a name (add `ipa`), a
  word swallowed before "…" (give it its own phrase or rephrase), or a plural ghost ("hall" heard as "halls" → rephrase).
  Audition alternatives fast: `python pipeline/try_phrase.py af_heart en-us 0.88 "variant one" "variant two"`.
- Duration 59–69 s including the 2.2 s tail, ≈ 130–140 wpm. Too fast → add pauses / lower speed (0.90–0.92 overall); too long → cut words.

### 6. Visual plan (`images.*.points`, `shots`, `overlays`)
- Find coordinates by LOOKING: `python pipeline/grid.py stories/<slug>/src/<img>.jpg` → Read the printed jpg; zoom into
  dark/small areas with `--crop x0,y0,x1,y1 --bright 2.2 --step 0.02`. Name points (`face`, `hand`, `child`…).
- Anchors: `"line.k-0.05"` = 0.05 s before word k (0-based) of that line; `"line$"` = line end. Word indices: check
  `stories/<slug>/build/timeline.json` (words per line, with times).
- **Open on the painting**: shot 1 at 0 s is a close-up (zoom ≥ 1.5) of the MAIN image, in colour, on its most striking
  detail (eyes, a face, the wound, the damage). Until the hook line ends only the main image is on screen; archive photos,
  newspapers and portraits come after. `validate.py` rejects a story that breaks this.
- Nudes (`meta.nude`, while `config.json` → `nude_safe_framing` is true): every shot of the main image stays at
  zoom ≥ 1.5 (and the cover at `span` ≤ 0.45) on a face, hands, an object or the damage, never breasts, buttocks or genitals; no full-painting reveal.
- Shots (see the reference reel): close-up of the painting at 0 s → reveal (`"hit": "big"`) on the hook's key word →
  a new shot on almost every phrase → archival/backstory images (`"gray": 1` for "the past") → back to the painting in
  colour for the payoff (`"hit": "big"` once more) → ending on a face/detail with the museum pin.
  Pose `"<point>@<zoom>"` (z = 1 fills the 9:16 frame; z < 1 + `"frame": true` = small framed picture). Keep motion
  gentle (`from`→`to` zoom change ≤ 0.2). Don't put the caption zone (lower third) over the only face in a shot.
- Overlays: `label` (mono caps top-left: place · date · source), `pin` (museum, on the ending), `title` (a name worth
  reading; add its span to `nocap`), `ring`/`hotspot` (point at a detail), `cut` (dashed keep-line + tinted removed
  strips), `stamp` (max one per reel), `credit` (CC photos, required).
- Music: change `transpose` vs. the last three stories; sections `cold` (backstory), `drop` (a comic beat), `choir`
  (the payoff), `heartbeat` (before the reveal). SFX on key words: `snip`, `tick`, `shutter`, `impact`, `chime`, `pop`.
- Dark paintings or copies: brighten that shot with `"dim": -0.3`.

### 7. Build and LOOK
- `./make_reel.sh <slug> 3 6` (visuals, score, cover, stills). Then Read `stories/<slug>/out/stills.jpg` and
  `stories/<slug>/out/cover.jpg`. Check: subject framed (faces not cut by the edge or hidden by captions), overlays
  readable and not covering faces, nothing blurry, black or empty, labels short (≤ 32 characters), the story is
  readable with the sound off. Extra moments: `python pipeline/preview_stills.py <slug> 12.5,20.1`. Fix and re-run
  `./make_reel.sh <slug> 3 6` until it is clean.
- Cover (PLAYBOOK §1 "Cover" and §2): question ≤ 2 lines (≈ 28 characters max), loaded words in `<i>…</i>`, answered by
  the video, selling the `hook_type`'s promise (never a vague superlative). The cover is a CLOSE-UP, never the whole
  painting: `cover.focus` on the main character's face or bust (or the key scene if the story is about another detail),
  `cover.span` = how much of the painting's height shows (0.3 tight face · 0.45 bust, the default · 0.6 half figure or a
  small scene; ≤ 0.45 for nudes, on a face). The focus lands at 60% of the frame height, under the text (`cover.at` to
  move it). Look at `out/cover.jpg`: the face is not under the question, nothing awkward is cut, it is not blurry (the
  script warns when the close-up is upscaled more than 2.4×).
- The NEXT card: `build/resolved.json` has a `next` overlay when the next scheduled story already has a `teaser` (the
  morning build re-resolves it, so a missing card at night is normal). Check it once you see it:
  `python pipeline/preview_stills.py <slug> <duration − 0.3>`.

### 8. Captions
- `caption` (Instagram/YouTube, 600–1200 characters): retell the story with the facts (numbers, names), end with a
  question to the audience (e.g. "🖤 Would you have noticed?"). An optional "P.S." with one extra verified fact is welcome.
- `caption_short` (TikTok, ≤ 150 characters, the hook), `youtube_title` (≤ 70 characters: the hook or cover question
  first, then the painting's or painter's name, which people search for).
- **Hashtags: Instagram and TikTok accept 5 at most**, so each platform gets its own best five (exactly 5, no more):
  - `hashtags_instagram`: the painter · the painting · `#arthistory` · the museum or city (only if people know it:
    `#prado`, `#louvre`, `#uffizi`; otherwise the city) · one topic tag that fits the story (`#darkart`, `#truecrime`,
    `#mythology`, `#artrestoration`…).
  - `hashtags_tiktok`: `#arthistory` · `#arttok` · the painter · the painting · one topic tag (`#darkhistory`,
    `#truecrime`, `#mystery`, `#historytok`…).
  - Use the spelling people actually search (`#vermeer`, not `#johannesvermeer`; `#thescream`, `#monalisa`). Never
    `#fyp`, `#viral` or `#deadpainterssociety` in these five (nobody searches for those).
  - `hashtags` (YouTube only, 10–12: painter, painting, museum, city, #arthistory, #painting, #museum, #artstory,
    #deadpainterssociety, plus 1–2 topical).
- `python pipeline/finalize.py <slug> --captions-only` → `out/caption.txt` (credits are added automatically from
  `meta` and every image with `"credit"`).

### 9. Schedule and log
- `python automation/plan.py add <slug>` (first free slot; two a day) — or `add <slug> <YYYY-MM-DD>` for a pinned date. Move the idea to **Done** in `STORY_QUEUE.md` with that date,
  or add a new row there if it wasn't on the list.

### 10. Self-check before moving on
- [ ] Every narrated claim has a source in `facts`; hedges where sources hedge.
- [ ] `meta`: painter, born, died, painting, year, museum, city, image, image_credit. `rights.creator_died` set.
- [ ] 130–145 words, 58–68 s, every line heard N/N.
- [ ] Last line: "It hangs in the <Museum>, in <City>."
- [ ] Stills and cover looked at and clean; cover question answered by the video.
- [ ] CC images credited (image `credit` + `credit` overlay).
- [ ] Scheduled; STORY_QUEUE updated.
- [ ] `hook_type` set; hook ≤ 12 words with no date; shot 1 is a colour close-up of the painting; `teaser` written; `tail` 2.2.
- [ ] `python automation/validate.py <slug> --report-only` prints no problems (fix every one it lists, then run it again).
The workflow then runs `automation/validate.py`: a story missing any of these is dropped automatically.

## Revisions (when the task says REVISION)

Gigi watched the reel on Telegram and asked for a change. Do exactly what she asked, as well as you can, and nothing
else; keep everything that wasn't criticised. If the request needs a new fact, verify it like any other. If her
feedback is a general preference ("never…", "always…", "too fast"), ALSO append it as a dated rule to the last section
of PLAYBOOK.md so every future reel follows it. Re-run `./make_reel.sh <slug> 0 6` (or from the first affected step),
look at the stills/cover again, regenerate captions if the text changed, and finish with one line describing what you
changed. Do not reschedule.

## Story file reference (`stories/<slug>/story.json`)

```
slug, voice "af_heart", lang "en-us", speed 0.92, tail 2.2
hook_type "dark"|"time-gap"|"craft"|"sacred-strange"|"dark-legend"|"damage"|"hidden"     (PLAYBOOK §2)
teaser    "≤ 48 characters, shown on the previous reel's NEXT card"
experiment {id, arm} while a test runs (EXPERIMENTS.md)
next      (optional) override the NEXT card text for THIS reel; false = no card (manual builds outside the schedule)
meta      {painter, born, died, painting, year, museum, city, image (main image key), image_credit, nude?}
cover     {question (<i>…</i>), name (PAINTER IN CAPS), work ("Title, year"), focus [x,y], span, at?, answered_by}
rights    {creator_died, note}
say {}  ipa {}  lines [{id, perf: [[text, pause, speed], …]}]   facts [{claim, source}]
caption, caption_short, youtube_title, hashtags [] (YouTube), hashtags_instagram [5], hashtags_tiktok [5]
images    {key: {file, commons, depth?, long?, credit?, points {name: [x,y]}}}
maps      {id: {bbox [[lon,lat],[lon,lat]], focus [...], cities {name: [lon,lat]}}}      (optional)
shots     [{at, img, kind? ("image" = flat, omit for 2.5D on depth images; "map"), from, to, gray?, dim?, frame?,
            dolly?, sway?, hit? ("big"|"small"), whoosh?}]
overlays  [{type, from|at, to, text?, kicker?, img?, point?, rx?, ry?, rot?, box?, shade?}]
nocap [[from, to]]   music {transpose, bar, chords, sections, heartbeat}   sfx [{at, fx, gain}]
```
