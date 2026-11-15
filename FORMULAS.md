# FORMULAS.md — the Shorts formulas we rotate

Gigi, 15 Nov 2026: the channel must never look like one template, and every formula is judged on the two numbers we
polish, **VVSA** (viewed vs swiped away) and **AVD** (average view duration), plus subscribers per 1,000 views. YouTube
does not monetize "content that looks like it's made with a template, or that may feel repetitive to viewers after
watching several videos in a row from the same channel" (monetization policy clarified July 2026; reviewers judge the
whole channel), so variety is also our insurance for the Partner Program review.

New formulas and changes come from the **breakout safari** (LAB.md): every week Claude studies art-history Shorts that
broke out for other channels and proposes changes here; Gigi's ✅ on Telegram writes them into the last section.

## Rotation (the story writer, CLAUDE.md step 1)

- **The season started on 15 Nov 2026** (Gigi stopped E1 to start it): every story written from that night on follows
  the rotation. The reels already written before it (to 17 Nov, and 19 Nov 14:00) stay F1.
- Order: **F1 → F3 → F4 → F2**, then again. Each new story takes the formula after the one in the bottom row of
  STORY_QUEUE.md **Done** (an empty Formula cell = F1) and appends its own row there with its formula. The two reels of one day are never the same formula.
- Pick the story to fit the formula (some stories only work as F1): if no good story fits the formula today, take the next
  formula and say so in the run notes. Never force a weak story into a formula.
- Every formula keeps the standing rules: a true, sourced story with one throughline; painter dead 70+ years, a visitable
  museum, public-domain images; hook ≤ 12 words making a claim, no date; shot 1 a colour close-up of the main painting;
  `teaser`; `tail` 2.2; the plain ending "It hangs in the …, in …" (F3: as its last caption card); PLAYBOOK §4 rules.
- Record `"formula": "F3"` in story.json, plus the formula's own fields below. The lab compares the formulas on VVSA, AVD
  and subscribers per 1,000 views (LAB.md, "The three numbers we polish").

## F1 — The Story (our classic)

`"format": "reel"`. Narrated by Enceladus, 130–145 words, 59–69 s; hook → painting by 3 s → 4–7 backstory beats with
archive images → back to the painting → payoff → ending line. Everything in PLAYBOOK.md and CLAUDE.md steps 1–10.

## F2 — One Painting, Two Minutes (E2 arm B, approved by Gigi 11 Nov 2026)

`"format": "two-minute"`. 260–340 narrated words (≈ 110–150 s). The MAIN painting only for the whole reel (no archive
images or maps; the past = the same painting with `gray`); 3+ "Look at …" beats that move the eye to a detail; the hook
(≤ 12 words) promises one concrete payoff (two words, one sentence, a name) that the reel delivers at ~70 %; after the
payoff a short coda (a later echo, then one reflective line); the plain ending. Case study: Brushstroke Secrets'
Innocent X Short, 385k. In the rotation it replaces E2's A/B test: the lab compares F2 with F1 directly.

## F3 — The Caption Short (first safari, 15 Nov 2026)

Evidence: the five art-history breakouts studied were 10–37 s long and four had no voice-over at all — one line of
burned-in text per image, over music: Past Cover "Queen Elizabeth make-up" (10.0M views, 9.5 s, 93× its channel's median
Short), "The history of displaying pregnancy" (9.6M, 18 s, 89×), art decoded "This Painting Shows a Different America"
(6.4M, 37 s, 136×) and "The Art Experiment That Revealed Humanity's Dark Side" (2.6M, 25 s, 55×); Nyxie's Charnley
self-portraits Short (11.9M, 20 s, 120×) also carries its whole story in captions. Ours run 61–68 s.

- `"format": "caption"`, `"silent": true` — the narration is muted in the mix; the voice still reads the text (so write
  it as spoken sentences) and its timing paces the cards.
- 35–75 words, 15–32 s including the tail. 5–8 **caption cards**, each ONE sentence of ≤ 12 words (punctuation ends a
  card), and a new shot on every card (a cut every 2–4 s).
- **Card 1, at 0 s, states the whole premise as a plain claim** over the most striking detail of the main painting, so a
  viewer knows instantly what they are watching (the breakouts: "She let strangers do anything to her for six hours.",
  "A schizophrenic painter stopped his medication…", "Today, women show their pregnant bellies but Victorians hid them!"). It is the
  hook: ≤ 12 words, no question, no date.
- Cards 2–5 escalate: each image and fact stronger than the last (the eye follows a progression). Then the payoff card
  (the twist, the cost, the dark fact). Optionally one reflective question to the viewer before the ending card ("If
  nobody was watching, would you still care?" — art decoded's ending). Last card: the plain ending line.
- Style in story.json: `"style": {"captionWords": 14, "captionChars": 72, "captionTop": 1180, "captionSize": 64,
  "captionFont": "Inter", "captionWeight": 800, "captionMode": "card"}` — one full sentence per card (only . ! ? … end a
  card, so commas may stay inside it), shown whole and held until the next card, centred in the lower middle. Keep faces
  ABOVE the caption zone: centre close-ups on a point a little below the face (the reference uses `faceup`).
- Write one line per card in `lines` (ids like `hook`, `parasol`, `death`…); numbers as digits with their `say` form.
- **Reference: `stories/monet-camille-deathbed/story.json`** (Gigi's first F3, 18 Nov 2026): 8 cards, 61 words, 29.7 s,
  Satie's Gymnopédie No. 1 as the only sound (`music.tracks`, `"pad": false`, `music_db` -4), whose credit goes into the
  caption automatically. A recognisable piece of public-domain music suits the format: the breakouts all ran on music. A `heartbeat` before the reveal
  if it helps; no `cold` section needed.
- Best stories: universal human themes that reach people who are not art fans (madness, cruelty, beauty standards, love,
  shame, death, a child). The cover question still follows PLAYBOOK §1 "Cover".

## F4 — The Series (first safari, 15 Nov 2026)

Evidence: Nyxie's 11.9M-view Short (120× its channel) is a sequence: one painter's self-portraits in time order, each more
distorted as he lowers his medication, then the cost ("A few months later…"). The eye follows the change; the story is
the change.

- `"format": "series"`. Narrated by Enceladus, 70–110 words, 28–45 s. 5–8 works by ONE painter (or the versions of one
  subject) in chronological order, each shot with a `label` overlay carrying its year ("1886", "1889"…); the change
  between them IS the story (illness, grief, blindness, ageing, love, war).
- Open in the middle of it: the main image = the most striking work of the series (the end of the change), close-up at
  0 s; the hook names the change ("Watch his self-portraits as the drugs wear off.", ≤ 12 words); then back to the first
  work and forward through the years; the payoff is the human cause or cost; the plain ending (where the main one hangs).
- Ideas to verify (FACTS FIRST — the famous versions of some of these are myths): Monet's Japanese footbridge before and
  after his cataracts (1899 → 1918–24); Rembrandt's self-portraits, 1629 → 1669; Van Gogh's self-portraits, 1886 → 1889;
  Munch's six versions of The Sick Child (1885–1925); Goya, from tapestry cartoons to the Black Paintings. Louis Wain's
  "cats that fall apart" sequence is popular but its order is a later invention: only as a myth-busting story, hedged.

## Candidates (seen in the safari, not in the rotation yet)

- **Then vs now** (Past Cover: 9.6M, 3.0M, 2.6M…): frame 1 quotes a modern belief ("Pink is for girls"), then paintings as
  the evidence that it used to be the opposite, then the why. Caption-only, 12–20 s. Could be F3's angle for some stories.
- **Meme dialogue** (Past Cover's Elizabeth: "Elizabeth, what is the cause of your death?" + rapid answers): very fast,
  9–10 s. It leans on AI reconstructions of faces, which we don't do; a version built only from paintings is untested.

## Results by formula

The lab writes the latest numbers here in its brief (VVSA, AVD in s and %, subs per 1,000, views at 72 h, n per formula).

## Approved changes (Gigi's ✅ on a safari proposal)

<!-- approved formula changes go here -->
