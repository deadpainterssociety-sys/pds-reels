# LONG.md — producer brief for the long videos (8–12 minutes, 16:9, YouTube)

You run unattended in GitHub Actions (workflow `longform.yml`). Nobody can answer questions: make the best call, keep
quality at the level of the reference, and leave clear notes. **This file replaces steps 1–10 of CLAUDE.md for this
task**; CLAUDE.md's rules on what you may touch, sources and honesty still apply. Read PLAYBOOK.md (§3b "Long-form videos"
and the whole last section, *Learned from feedback*: Gigi's corrections override everything).

**The reference is `stories/repin-cossacks-long/`** (Gigi, 21 Nov 2026: "10/10 video. THIS IS THE QUALITY I EXPECT").
Open its `script.py`, `plan.py`, `visuals.py`, `facts.json` first and copy their structure, density and care. Your story
lives in `stories/<painter-keyword>-long/` with the same four files; `plan.py` writes `story.json`.

Your task names the slot: the date it goes public (Monday or Thursday, 19:00 Madrid). The workflow, not you, voices the
final narration (Chirp 3 HD "Enceladus"), renders, uploads it as private scheduled, and sends Gigi the preview on
Telegram. You never publish, never call YouTube/Telegram, never read secrets. Budget: about 2.5–3.5 hours of work.

## 1. Pick the story
- `STORY_QUEUE.md` → "Long videos (to plan)": take the row whose date is your slot; else the first row without a date
  or "MADE". Hard filters as for Shorts (painter died before 1956, visitable museum, a public-domain image ≥ 3000 px).
  If it fails, take the next row. Mark the row `<date> — MADE (<slug>)`, and keep at least 3 unmade rows in that table
  (add new ones from the best-performing Shorts and SAFARI.md; one line each with the angle).
- One throughline with a turn in the middle and a payoff that answers the title. The long version of a Short we posted
  is good (the Short then funnels to it); a fresh story is fine too.

## 2. Research (this protects the channel)
- Museum page first, then Wikipedia (read via wikiwand.com if wikipedia.org refuses) **and its cited sources**, then
  scholars, catalogues, major newspapers; Russian/Ukrainian/Spanish/… sources are fine (translate yourself).
- `facts.json`: 30–40 entries `{"claim", "source": "url ; url"}`, one per narrated claim; two sources wherever they
  differ. Numbers, dates, names, quotes exactly as the source has them. Legends and anecdotes are narrated as such
  ("the story goes", "he supposedly said"). Where sources conflict on a date, narrate the season or the year only.
- Quotes on screen: the words of a cited source (for a translation, a translation a source prints), under ~20 words.
- Current events (wars, lawsuits, thefts): state facts plainly, name who did what as the sources do, no opinions.

## 3. Script (`script.py`: `L = [(id, [[text, pause_s, speed], …]), …]`)
- **1,250–1,450 words** (≈ 9–10.5 min with Enceladus), plain spoken English, short phrases, no clichés, no jokes at the end.
- **Cold open ≤ 35 s**: line 1 is ONE claim about the painting on screen, ≤ 10 words, no date ("These men are laughing at
  an emperor."). Then the stakes, the human angle, the promise. (Bosch lost 57 % of viewers in its first 25 s.)
- 6–7 chapters, each a step of the story with its own small turn; time order; a "Look closely" moment on the painting;
  the twist about two thirds in; the last chapter answers the title and the cold open, then ends with a reflective
  line and **exactly**: "It hangs in the <Museum>, in <City>."
- Hedges where the facts are legends. Dates said normally; years in `say` ("1891": "eighteen ninety-one").
- Pauses: 0.15–0.3 between clauses, 0.6–1.0 after a beat, 2.2 at the end of a chapter (the chapter card needs it).
- `chirp_say`: plain respellings for names Chirp may anglicise ("Yavornytsky": "Yavor-nitsky"); `ipa` for Kokoro.

## 4. Images and music (CI downloads directly: be patient, give these Bash calls a 1800000 ms timeout)
- `python pipeline/commons.py search "<query>" 10` and `info "File:…"` (licence, author, size). 20–30 images: the
  painting (≥ 3000 px, `depth: True`, `long: 3840`), its versions and studies, the people (portraits/photos), places,
  documents, other works mentioned. Public domain preferred; CC BY/BY-SA only with the author's name: image `credit`,
  an on-screen `credit` overlay, and a line in `youtube.credits`.
- Music: 4–8 public-domain recordings from Commons (Musopen and similar; composer died before 1956, check the
  recording's licence) that fit the country/period/mood; declare them in `MUSIC["tracks"]` with `commons` titles.
- Declare all of them in `visuals.py` (`IM`), run `python stories/<slug>/plan.py`, then
  `python pipeline/fetch_images.py <slug> --minutes 40` (it downloads images and music; it falls back to big
  thumbnails when Wikimedia rate-limits). Check every file exists and is large enough; replace what failed.

## 5. Visual plan (`visuals.py`) — find every point by LOOKING
- `python pipeline/grid.py stories/<slug>/src/<img>.jpg` → Read the jpg; `--crop x0,y0,x1,y1 --step 0.02` to zoom.
  Name the points (faces, hands, the signature, the detail the script talks about). Tall portraits that are shown
  framed (`frame=True`, `z ≈ 0.62`) need a point near the head (`[x, 0.25]`), or the head is cut.
- About one shot per phrase group (~5 s); slow moves (zoom change ≤ 0.15); hard cuts with `hit="big"` only on the
  reveal (after line 1) and on the finished painting; `gray=` for the past/backstory, colour for the painting.
- Overlays: `title` after the cold open, a `chapter` card per chapter, `lower` thirds for people (only over THAT
  person's picture — check), `label` (small, top-left: what the picture is), `quote` cards (≤ 3–4), one `stamp` at
  most, `ring` on details, `credit` for CC photos, `pin` on the ending, `end` for the end screen.
  **Never a big `year` date card** (Gigi, 21 Nov 2026; build_story.py drops them anyway).
- Light backgrounds (maps, sketches on paper, skies) get `dim=0.2–0.35` so labels stay readable.
- Anchors: `A(line, "word", nth)` matches lowercase words: "And"/"The"/"In" often need `nth` > 1 — check each one.
- Music cue sheet: one recording per chapter mood, crossfades at chapter cards; measure each recording's loudness
  (5-s windows, as in the reference notes) and set `start` so a climax lands on the reveal or the payoff.

## 6. Timing pass, stills, thumbnails (your timeline is Kokoro; the final Chirp voice is ~5 % faster, anchors follow words)
- `VOICE=kokoro python pipeline/tts.py <slug> && python pipeline/align.py <slug>` (≈ 10 min), then
  `python pipeline/build_story.py <slug> && python pipeline/score.py <slug>`.
- One still per shot: `python pipeline/preview_stills.py <slug> t1,t2,…` (shot start + ~1.5 s, from
  `build/resolved.json`), assemble contact sheets of 20 and **Read every sheet**. Check: faces not cut, the right person
  under each lower third, labels readable, nothing blurry/black/empty, CC credits present, no awkward crops. Fix and
  re-check the fixed shots. Expect two or three rounds.
- `python pipeline/thumb.py <slug>`: thumb A (no text) and B (`youtube.thumbnail.words`, ≤ 4 words, one in caps).
  Read both: a close-up on the most expressive face(s), span ≈ 0.3–0.45, nothing cut awkwardly.
- **Packaging sells a question, not a mood (Gigi, 25 Nov 2026: Repin's "These Men Are Laughing at an Emperor" +
  "INSULTING an Empire" got 147 impressions and 0 clicks).** The thumbnail shows ONE action or oddity a stranger can
  read at phone size (the scribe writing the letter, not a crowd), and its words pose the question or claim the video
  answers ("RUDEST Letter in History", "Why Are They LAUGHING?"), never a vague label. The title makes a concrete claim
  about what is on screen BEFORE naming the painting (Inspiraggio's pattern: "This Painting Terrified an Entire
  Government"); title and thumbnail words complement each other, never repeat each other.

## 7. YouTube fields (`plan.py` → `story["youtube"]`) and checks
- `titles`: A and B, ≤ 60 characters, a concrete claim or question about what is on screen (see the packaging rule in
  step 6), no numbers, no "you won't believe"; borrowed fame when there is one. `description_lead` (facts, names), `hashtags` (3), `credits` (all images: PD lines + every CC author/licence),
  `sources` (12–18 best public URLs), `thumbnail`, `intro_chapter`, `outro_chapter` (not a chapter name),
  `pinned_comment` (one line of extra fact + a question, ending with our signature 👁️, never a heart). `"next": False`. Add `"slot": "<YYYY-MM-DD>"` at the top level.
- `python automation/validate_long.py <slug>` must print no problems. Fix everything it lists and run it again.
- Do NOT render (the workflow renders on a bigger machine), do not commit or push, do not schedule anything.
## 8. The trailer Short (sends Shorts viewers to this film; Gigi, 21 Nov 2026)
- `python automation/long_plan.py shorts <slug>` lists our Shorts of the same painting. If it lists any, do nothing
  more: the bot reminds Gigi to link them to the film in Studio when it goes public.
- If it prints `none`: add a row at the TOP of `STORY_QUEUE.md` **Pinned** dated the day after your slot (`YYYY-MM-DD`),
  so the night shift makes the trailer: Painting (museum) | the angle: ONE anecdote from your film, complete in itself
  and NOT its throughline or payoff (a side story with a face or a detail on screen: a model, a prank, an object), 1–2
  sentences with its facts | its `hook_type` | notes: "Trailer Short for `<slug>`" (exactly these words, CLAUDE.md step 1
  has the rules), a slug `<painter>-<keyword>`, the leads (your facts.json entry numbers, the main image's Commons file,
  the points from visuals.py it needs). The reference row is the one for `repin-cossacks-long` (in Done once made).

- Write `stories/<slug>/notes.txt` (3 short lines, sent to Gigi with the preview): the story in one line, anything
  you were unsure about, anything she should check, and the trailer's angle (or which Short will link to the film). Then stop.
