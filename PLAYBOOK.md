# Dead Painters Society — Reel Playbook

The channel's rules. Claude follows them for every reel (see `CLAUDE.md` for the step-by-step method); Gigi can add
rules from Telegram with `/rule <text>`, which appends them to the last section. Handle everywhere:
**@thedeadpainterssociety** (Instagram, TikTok, YouTube Shorts). English only for now.

Phase 1 (manual posting, 26–30 Oct 2026): Artemisia, Goya *Saturn*, Rokeby Venus, Mona Lisa theft, Night Watch.
Phase 2 (from 31 Oct 2026): this repo does everything; Gigi only reviews on Telegram.
Week-1 review (1 Nov 2026): ~10,650 views across the three platforms. On YouTube the three reels that opened on the
painting with a one-line hook got ~1,250 views each; the two that opened on an archive photo got 1 and 34. The rules
marked "(1 Nov)" below come from that review and from the Inspiraggio competitor study.

---

## 1. The format (non-negotiable rules)

**Story**
- One true, sourced story with a single throughline and a punchline. No tangents. If a fact needs a second story to explain it, cut it.
- Shape: **hook (one line) → early reveal of the painting (≤3 s) → backstory in 4–7 short beats → return to the painting → payoff.** The payoff answers the cover question.
- **The hook (1 Nov): one punchy line, at most 12 words, that makes a claim about the painting on screen.** "Nobody was ever supposed to see this." / "Someone wrote on The Scream itself. In pencil." Never open with a date or a scene-setting ("One morning in 1911…", "A woman walks into the National Gallery…"): viewers swiped those away in under 2 seconds.
- **Ending (29 Oct): just say plainly where it hangs** ("It hangs in the Louvre, in Paris."). No jokes, puns or wink lines (no "maybe not after lunch" / "don't gape").
- Gossip and scandal are welcome, but every claim must be checked against at least one solid source: museum page, Wikipedia with its references, a foundation catalogue or a scholar. Use two sources when they differ.
- Hedge in the narration whenever scholars hedge ("historians think…", "the legend says…"). Never state a legend as fact.
- **Painter dead more than 70 years** (EU public domain). Images from Wikimedia Commons, preferring files tagged *Public domain*. A scan of a public-domain original tagged CC BY-SA is acceptable only with a credit line in the caption.
- Prefer paintings in live, visitable museums (Prado, Uffizi, Thyssen, Louvre, National Gallery, and so on), so the "go see it" ending works.

**Script and voice**
- Length: 130–145 spoken words, about 61–67 s including the 2.2 s end card (`tail` 2.2).
- Short phrases. Every phrase is written as `[text, pause_after_seconds, speed]`:
  - 0.25–0.4 s pause between clauses.
  - 0.8–1.0 s after a beat lands.
  - Speed 0.9–0.97 for normal lines; 0.78–0.88 for the words that must hit ("this.", "him.").
- Kokoro voice **af_heart**, phrase-by-phrase synthesis (`pipeline/tts.py`). Captions mark emphasis with `*word*`.
- Pronunciation:
  - Every proper name and year goes through `say` (spoken form) or `ipa`, in the story file or in the global `pipeline/pronounce.json` (under `en-us`).
  - The recogniser check must read every line back correctly. Fix anything it mishears: it is usually a name, or a lone word before "…".
- Label the content as AI on every platform while the voice is synthetic.

**Visuals** (`studio/src/reel/Reel.tsx`, driven by the story file)
- **Open on the painting itself (1 Nov).** The first shot (0 s) is a close-up (zoom ≥ 1.5) of the main painting, in colour, on its most striking detail: eyes, a face, the wound, the damage. Until the hook line ends, nothing but the main painting is on screen. Archive photos, newspapers and portraits come after the hook.
- Main painting in 2.5D (depth-map parallax), with a camera cut on almost every phrase. Cuts are timed to spoken words (anchors like `"myth.8-0.05"`).
- Reveal the whole painting with a flash and impact on the hook's key word (not for nudes, see below).
- Backstory in archival images (other works, period photos, maps), greyed when it is "the past". Return to colour for the payoff.
- **Nudes (1 Nov).** YouTube can age-restrict nudity, which hides a Short from under-18s and signed-out viewers (the Rokeby Venus got 1 view on YouTube). While `nude_safe_framing` is `true` in `config.json`: set `meta.nude: true`; the cover and every shot of the painting stay close-up (zoom ≥ 1.5) on a face, hands, an object or the damage, never on breasts, buttocks or genitals; no full-painting reveal. Prefer stories whose hook isn't the nudity itself.
- Overlays:
  - Mono labels top-left for place, date or source.
  - Pin pill for the museum.
  - A title card for a name worth reading.
  - Stamps sparingly: at most one per reel.
  - Credits for archival photos.
  - `cut` (added 29 Oct): a dashed red line around the part that was kept, with the removed strips tinted red (`box` = kept area in image fractions, `shade` = when the tint comes in). Pair it with the `snip` sound.
- **Silent NEXT card (1 Nov).** The last ~1.6 s show a small "NEXT" over the next scheduled story's `teaser`, added automatically at build time (`pipeline/build_story.py`). It is a quiet promise of tomorrow, so viewers have a reason to follow. No voice, no slogan, no branding; the spoken ending stays plain. Each story writes its own `teaser` (≤ 48 characters, e.g. "The nude the Inquisition investigated") for the reel before it to show.
- Captions: Newsreader 86 px, 3-word chunks, emphasis in italics.
- Dark copies or low-light paintings: brighten with a negative `dim` (e.g. `-0.3`) on that shot.
- No Vincent branding or watermark for now.

**Sound**
- Dark pad (transposed per story so reels don't sound identical), ducked under the voice.
- A "cold" section (thin high drone) for the backstory.
- A heartbeat before the big return; a choir for the painting's big moment; a near-silence "drop" for a comic beat.
- Whoosh on every cut, reverse sting + impact on reveals, ticks on map pins.
- Final mix normalised to −14 LUFS mono (≈ −11 LUFS measured as stereo), the same as the Artemisia reel.

**Cover (Classic style, chosen 25 Oct; layout updated 27 Oct)**
- The painting fills the **full width** and the whole lower part of the frame (≈ bottom 2/3, from just under the title to the bottom edge). **No side margins, ever.** Vertical paintings are zoomed to the width (top/bottom cropped); horizontal ones to the height (sides cropped). `cover.focus` = the point to keep in view (face, key detail). The top fades to black behind the text.
- **The image decides as much as the words (1 Nov).** Focus and zoom the cover on the most striking detail, big enough to read at thumbnail size on a phone. (Inspiraggio: "This Painting Is Beyond Insane" got 2.25M views, "This Painting Is Absolutely Insane" got 32.8k. Same words; the picture made the difference.)
- Painter in caps (Inter); painting and year in italic (Newsreader); an intriguing question in Newsreader 106 px with the loaded words in italics.
- **The video must answer the question.**
- The cover is also the first frame of the video (0.1 s), so TikTok and YouTube can use it as the thumbnail. On Instagram, upload `cover.jpg` as the cover as well.

---

## 2. Hooks, titles and covers (1 Nov, from the Inspiraggio study and our week 1)

Inspiraggio (647k subscribers) is the art-history channel we want to compete with by the end of 2028. His hits and flops
sort cleanly by the promise the title makes. Every story declares one `hook_type`:

| `hook_type` | The promise | Proof |
|---|---|---|
| `dark` | dread: death, the devil, madness, cruelty | our Goya *Saturn* (best all-round reel of week 1); his "Most Disturbing Painting of Satan" 989k |
| `time-gap` | a mystery hidden or unsolved for centuries, with the number in the title | his "How did we miss this for 350 years?" 1.32M |
| `craft` | "how could a human paint this?" | his "How was this painted 600 years ago?" 822k |
| `sacred-strange` | a sacred or famous figure shown in an unexpected way | his "The Strangest Painting of Jesus" 1.17M |
| `dark-legend` | the painter's own dark life | his Caravaggio video 684k vs the same title for Raphael 29.6k |
| `damage` | something done TO the painting: cut, attacked, stolen, painted over | our *Night Watch* (1,266 on YouTube, best retention) |
| `hidden` | a hidden detail, or a lie everybody believes | our *Scream* note (1,284 on its first day) |

- The cover question and the YouTube title sell a feeling or an open question, never information.
- Specific beats general: a number ("350 years"), a crime, a body part. **Never vague superlatives** ("the most insane painting", "changed history forever", "the most beautiful painting ever"): they flop for him and they break our rule that the video answers the cover.
- Dread beats sadness: never build the hook on melancholy ("The Saddest Painting Ever" got 48.6k).
- A small detail needs stakes: danger, a crime or a mystery attached to it.
- YouTube title: the hook first, then the painting or the painter's name. People search for them: 64% of our TikTok search traffic in week 1 was "goya wall painting".
- About one story in four: a lesser-known painting with a dark or uncanny story. The hook must work without the name.
- Accuracy is the brand. Every YouTube description lists the sources (added automatically from `facts`); legends are called legends.
- Don't use the same `hook_type` three reels in a row. The weekly review compares views by `hook_type`, so the label must be honest.

## 3. Picking stories

- Alternate museums and moods (horror / romance / crime / comedy / mystery); avoid two dark ones in a row and two from the
  same museum in a row. Look at the last 5 posted (`python automation/plan.py posted`, `STORY_QUEUE.md`).
- Never repeat a painting that is already in `stories/`.
- Painter dead more than 70 years (died before 1956 for 2026). Picasso (†1973), Dalí (†1989), Hopper and Magritte (†1967)
  are out; Matisse and Frida Kahlo (†1954) entered the EU public domain on 1 Jan 2025. For late works also check the US
  rule: in 2026, works published before 1931 are free there.
- The painting must hang in a museum people can visit, and there must be a public-domain image of it on Wikimedia Commons
  at 2000 px or more.
- Best hooks: the seven `hook_type`s in §2. A crime, a scandal, a hidden detail, a lie everybody believes, something done TO the painting.

## 4. Learned from feedback

Rules Gigi added after watching reels or reading the analytics. They override anything above.

- (29 Oct 2026) The ending says plainly where the painting hangs. No jokes, puns or wink lines.
- (27 Oct 2026) Cover: the painting fills the whole lower part edge to edge — never side margins.
- (26 Oct 2026) One linear story, never "all over the place"; human pacing with real pauses, never rushed (≈130–140 wpm).
- (1 Nov 2026) Open every reel on the painting itself, close-up and in colour; nothing else on screen until the hook line ends.
- (1 Nov 2026) The hook is one punchy line (≤ 12 words) that makes a claim about the painting on screen: no dates, no "One morning in…", no "A woman walks into…".
- (1 Nov 2026) Nudes get safe framing (close-ups on faces, hands, objects) until we know YouTube didn't restrict the Rokeby Venus.
- (1 Nov 2026) Every reel ends with the silent NEXT card showing the next story's teaser. The spoken ending stays plain.
- (1 Nov 2026) Titles and covers follow the seven hook types in §2; never vague superlatives.
<!-- new rules go here -->
