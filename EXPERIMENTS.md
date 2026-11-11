# Experiments — one controlled test at a time

The analysis brief (LAB.md) proposes tests; Gigi starts one with ✅ on Telegram, and the row appears here. While a test
is running, the story writer (CLAUDE.md step 1) alternates its two versions so the two arms stay balanced, and records
`"experiment": {"id": "E1", "arm": "A"}` in story.json. Everything else follows the playbook as usual. The brief
compares the arms once both have enough reels with 3 days of data, and proposes the winner as a playbook rule.

## Running

| id | Question | Arm A | Arm B | Main metric | Started | Length |
|---|---|---|---|---|---|---|
| E1 | Does a 'Who + verb…?' cover question about a person get more YouTube views than other question forms? | Write the cover question as 'Who' + verb, about a person the video reveals (e.g. 'Who erased her name?'), ≤ 28 characters, loaded words in <i>…</i>; start youtube_title with that exact question. | Write the cover question in any form other than 'Who…' (Why/Where/What/Was/Did/Whose), about an object, act or event (e.g. 'Why was this strap repainted?'), ≤ 28 characters, loaded words in <i>…</i>; start youtube_title with that exact question. | YouTube views at 72 h | 2026-11-09 | 14 reels |
<!-- running -->

## Next (approved by Gigi, 11 Nov 2026: starts when E1 is concluded)

| id | Question | Arm A | Arm B | Main metric | Length |
|---|---|---|---|---|---|
| E2 | Does a 2-minute single-painting Short get more YouTube views than our 60-s format? (case study: Brushstroke Secrets' Innocent X Short, 385k, project doc competitor-brushstroke-secrets) | Our current format (PLAYBOOK §1: 130-145 words, 61-67 s, backstory images allowed). | `"format": "two-minute"` in story.json: 260-340 spoken words (≈ 110-150 s); the MAIN painting only for the whole reel (no archive images or maps; the past = the same painting with `gray`); 3+ "Look at …" beats that move the eye to a detail; the hook (still ≤ 12 words) promises one concrete payoff (two words, one sentence, a name) that the reel delivers at ~70 %; after the payoff a short coda (a later echo, then one reflective line); then the plain ending "It hangs in the …, in …". | YouTube views at 72 h (and engaged views) | 14 reels |
<!-- next -->

## Finished

| id | Question | Arm A | Arm B | Main metric | Started | Length | Result |
|---|---|---|---|---|---|---|---|
<!-- finished -->
