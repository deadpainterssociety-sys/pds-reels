# Experiments — one controlled test at a time

The analysis brief (LAB.md) proposes tests; Gigi starts one with ✅ on Telegram, and the row appears here. While a test
is running, the story writer (CLAUDE.md step 1) alternates its two versions so the two arms stay balanced, and records
`"experiment": {"id": "E1", "arm": "A"}` in story.json. Everything else follows the playbook as usual. The brief
compares the arms once both have enough reels with 3 days of data, and proposes the winner as a playbook rule.

## Running

| id | Question | Arm A | Arm B | Main metric | Started | Length |
|---|---|---|---|---|---|---|
| E3 | Do silent caption Shorts (F3) beat our other formats when they get half the slots? (Gigi, 25 Nov: "proceed with the F3 2-week test, 1/day") | F3 silent caption Short (FORMULAS.md F3) | Not F3: the rotation F1 → F4 → F2 without F3 (the formula after the last F1/F4/F2 row in STORY_QUEUE.md Done) | YouTube engaged views at 72 h; then subscribers per 1,000 views | 27 Nov 2026 | 2 weeks, to 10 Dec (one F3 a day; the day's other reel is arm B) |
<!-- running -->

## Next

| id | Question | Arm A | Arm B | Main metric | Length |
|---|---|---|---|---|---|
<!-- next -->

## Finished

| id | Question | Arm A | Arm B | Main metric | Started | Length | Result |
|---|---|---|---|---|---|---|---|
| E1 | Does a 'Who + verb…?' cover question about a person get more YouTube views than other question forms? | Write the cover question as 'Who' + verb, about a person the video reveals (e.g. 'Who erased her name?'), ≤ 28 characters, loaded words in <i>…</i>; start youtube_title with that exact question. | Write the cover question in any form other than 'Who…' (Why/Where/What/Was/Did/Whose), about an object, act or event (e.g. 'Why was this strap repainted?'), ≤ 28 characters, loaded words in <i>…</i>; start youtube_title with that exact question. | YouTube views at 72 h | 2026-11-09 | 14 reels | **Stopped by Gigi on 15 Nov 2026** to start the formula season (FORMULAS.md). No verdict: only 2 of its reels had 72-h data (A Repin 1,594 views; B Whistler 1,079). The 7 E1 reels already written keep their covers. |
| E2 | Does a 2-minute single-painting Short get more YouTube views than our 60-s format? (case study: Brushstroke Secrets' Innocent X Short, 385k, project doc competitor-brushstroke-secrets) | Our current format (PLAYBOOK §1: 130-145 words, 61-67 s, backstory images allowed). | `"format": "two-minute"` in story.json: 260-340 spoken words (≈ 110-150 s); the MAIN painting only for the whole reel (no archive images or maps; the past = the same painting with `gray`); 3+ "Look at …" beats that move the eye to a detail; the hook (still ≤ 12 words) promises one concrete payoff (two words, one sentence, a name) that the reel delivers at ~70 %; after the payoff a short coda (a later echo, then one reflective line); then the plain ending "It hangs in the …, in …". | YouTube views at 72 h (and engaged views) | — | 14 reels | **Never run as an A/B test**: on 15 Nov 2026 Gigi folded it into the formula rotation as F2 (FORMULAS.md); the lab compares F2 with F1 directly. |
<!-- finished -->
