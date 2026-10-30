# Dead Painters Society — Reel Playbook

The channel's rules. Claude follows them for every reel (see `CLAUDE.md` for the step-by-step method); Gigi can add
rules from Telegram with `/rule <text>`, which appends them to the last section. Handle everywhere:
**@thedeadpainterssociety** (Instagram, TikTok, YouTube Shorts). English only for now.

Phase 1 (manual posting, 26–30 Oct 2026): Artemisia, Goya *Saturn*, Rokeby Venus, Mona Lisa theft, Night Watch.
Phase 2 (from 31 Oct 2026): this repo does everything; Gigi only reviews on Telegram.

---

## 1. The format (non-negotiable rules)

**Story**
- One true, sourced story with a single throughline and a punchline. No tangents. If a fact needs a second story to explain it, cut it.
- Shape: **hook (≤2 s) → early reveal of the painting (≤3 s) → backstory in 4–7 short beats → return to the painting → payoff.** The payoff answers the cover question.
- **Ending (29 Oct): just say plainly where it hangs** ("It hangs in the Louvre, in Paris."). No jokes, puns or wink lines (no "maybe not after lunch" / "don't gape").
- Gossip and scandal are welcome, but every claim must be checked against at least one solid source: museum page, Wikipedia with its references, a foundation catalogue or a scholar. Use two sources when they differ.
- Hedge in the narration whenever scholars hedge ("historians think…", "the legend says…"). Never state a legend as fact.
- **Painter dead more than 70 years** (EU public domain). Images from Wikimedia Commons, preferring files tagged *Public domain*. A scan of a public-domain original tagged CC BY-SA is acceptable only with a credit line in the caption.
- Prefer paintings in live, visitable museums (Prado, Uffizi, Thyssen, Louvre, National Gallery, and so on), so the "go see it" ending works.

**Script and voice**
- Length: 130–145 spoken words, about 60–66 s.
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
- Main painting in 2.5D (depth-map parallax), with a camera cut on almost every phrase. Cuts are timed to spoken words (anchors like `"myth.8-0.05"`).
- Tease a detail at 0 s; reveal the whole painting with a flash and impact on the hook's last word.
- Backstory in archival images (other works, period photos, maps), greyed when it is "the past". Return to colour for the payoff.
- Overlays:
  - Mono labels top-left for place, date or source.
  - Pin pill for the museum.
  - A title card for a name worth reading.
  - Stamps sparingly: at most one per reel.
  - Credits for archival photos.
  - `cut` (added 29 Oct): a dashed red line around the part that was kept, with the removed strips tinted red (`box` = kept area in image fractions, `shade` = when the tint comes in). Pair it with the `snip` sound.
- Captions: Newsreader 86 px, 3-word chunks, emphasis in italics.
- Dark copies or low-light paintings: brighten with a negative `dim` (e.g. `-0.3`) on that shot.
- No Vincent branding, watermark or end card for now.

**Sound**
- Dark pad (transposed per story so reels don't sound identical), ducked under the voice.
- A "cold" section (thin high drone) for the backstory.
- A heartbeat before the big return; a choir for the painting's big moment; a near-silence "drop" for a comic beat.
- Whoosh on every cut, reverse sting + impact on reveals, ticks on map pins.
- Final mix normalised to −14 LUFS mono (≈ −11 LUFS measured as stereo), the same as the Artemisia reel.

**Cover (Classic style, chosen 25 Oct; layout updated 27 Oct)**
- The painting fills the **full width** and the whole lower part of the frame (≈ bottom 2/3, from just under the title to the bottom edge). **No side margins, ever.** Vertical paintings are zoomed to the width (top/bottom cropped); horizontal ones to the height (sides cropped). `cover.focus` = the point to keep in view (face, key detail). The top fades to black behind the text.
- Painter in caps (Inter); painting and year in italic (Newsreader); an intriguing question in Newsreader 106 px with the loaded words in italics.
- **The video must answer the question.**
- The cover is also the first frame of the video (0.1 s), so TikTok and YouTube can use it as the thumbnail. On Instagram, upload `cover.jpg` as the cover as well.

---

## 2. Picking stories

- Alternate museums and moods (horror / romance / crime / comedy / mystery); avoid two dark ones in a row and two from the
  same museum in a row. Look at the last 5 posted (`python automation/plan.py posted`, `STORY_QUEUE.md`).
- Never repeat a painting that is already in `stories/`.
- Painter dead more than 70 years (died before 1956 for 2026). Picasso (†1973), Dalí (†1989), Hopper and Magritte (†1967)
  are out; Matisse and Frida Kahlo (†1954) entered the EU public domain on 1 Jan 2025. For late works also check the US
  rule: in 2026, works published before 1931 are free there.
- The painting must hang in a museum people can visit, and there must be a public-domain image of it on Wikimedia Commons
  at 2000 px or more.
- Best hooks: a crime, a scandal, a hidden detail, a lie everybody believes, something done TO the painting.

## 3. Learned from feedback

Rules Gigi added after watching reels (newest last). They override anything above.

- (29 Oct 2026) The ending says plainly where the painting hangs. No jokes, puns or wink lines.
- (27 Oct 2026) Cover: the painting fills the whole lower part edge to edge — never side margins.
- (26 Oct 2026) One linear story, never "all over the place"; human pacing with real pauses, never rushed (≈130–140 wpm).
<!-- new rules go here -->
