#!/usr/bin/env bash
# One reel, end to end.   usage: ./make_reel.sh <slug> [from_step] [to_step]
#  0 images   download everything story.json declares (Wikimedia Commons / direct URLs)
#  1 voice    phrase-by-phrase TTS            -> build/voice.wav, timeline.json
#  2 align    recogniser word times + "what a listener hears" check (READ IT)
#  3 visuals  resolve shots/overlays, depth maps, maps -> studio
#  4 score    music + SFX + mix               -> build/mix.wav
#  5 cover    cover.jpg (Classic style)
#  6 stills   one still per shot -> out/stills.jpg (LOOK AT IT before the long render)
#  7 render   Remotion, ~10–30 min depending on CPU -> build/video.mp4
#  8 finalize cover-first master + preview + caption.txt + qa.txt + frames.jpg
set -euo pipefail
cd "$(dirname "$0")"; S=$1; from=${2:-0}; to=${3:-8}
step() { [ "$from" -le "$1" ] && [ "$1" -le "$to" ]; }
P="python3 pipeline"
step 0 && $P/fetch_images.py $S
step 1 && $P/tts.py $S
step 2 && $P/align.py $S
step 3 && $P/build_story.py $S
step 4 && $P/score.py $S
step 5 && $P/cover.py $S
step 6 && $P/preview_stills.py $S
step 7 && (cd studio && node render_reel.mjs $S ../stories/$S/build/video.mp4)
step 8 && $P/finalize.py $S
echo "done: stories/$S/out"
