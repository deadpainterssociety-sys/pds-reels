#!/usr/bin/env bash
# One-time setup on a fresh machine (Ubuntu/Debian, macOS with Homebrew, or a GitHub Actions ubuntu runner).
# Needs: python3 >= 3.10, node >= 18, ffmpeg, ~2 GB free disk (models ~1.1 GB + node_modules).
# usage: ./setup.sh            (DEPTH_MODEL=vitb|vitl: bigger but NON-COMMERCIAL licence; ASR=v2 for English-only ASR)
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd); MODELS=${REELS_MODELS:-$ROOT/models}
echo "== checking tools"; for b in python3 node npm ffmpeg ffprobe curl tar; do command -v $b >/dev/null || { echo "missing: $b"; exit 1; }; done

echo "== python packages"
python3 -m pip install -q -r requirements.txt 2>/dev/null || python3 -m pip install -q --break-system-packages -r requirements.txt
if [ "${CI:-}" = "true" ]; then python3 -m playwright install --with-deps chromium >/dev/null; \
else python3 -m playwright install chromium >/dev/null 2>&1 || echo "(playwright browser install skipped — fine if one is already present)"; fi

echo "== node packages (Remotion)"
(cd studio && if [ -f package-lock.json ]; then npm ci --no-audit --no-fund --loglevel=error; else npm install --no-audit --no-fund --loglevel=error; fi)

echo "== fonts (copied from @fontsource packages)"
mkdir -p studio/public/fonts
for fam in newsreader inter space-mono anton playfair-display; do cp studio/node_modules/@fontsource/$fam/files/*-latin-*.woff2 studio/public/fonts/ 2>/dev/null || true; done
ls studio/public/fonts | wc -l | xargs echo "font files:"

echo "== models -> $MODELS"
dl() { [ -s "$2" ] && { echo "ok  $(basename $2)"; return; }; mkdir -p "$(dirname $2)"; echo "get $(basename $2)"; curl -sSL --fail --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; }
dl https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx "$MODELS/kokoro/kokoro-v1.0.onnx"
dl https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin "$MODELS/kokoro/voices-v1.0.bin"
D=${DEPTH_MODEL:-vits}   # vits = Apache-2.0 (commercial OK); vitb/vitl are CC-BY-NC-4.0 (non-commercial only)
dl https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/depth_anything_v2_$D.onnx "$MODELS/depth/depth_anything_v2_$D.onnx"
if [ ! -s "$MODELS/asr/encoder.int8.onnx" ]; then
  V=${ASR:-v2}   # v2 = English only (best for this channel), v3 = multilingual (25 European languages)
  A=sherpa-onnx-nemo-parakeet-tdt-0.6b-$V-int8
  mkdir -p "$MODELS/asr"; echo "get $A"
  curl -sSL --fail --retry 3 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$A.tar.bz2 | tar xj -C "$MODELS/asr"
  mv "$MODELS/asr/$A"/{encoder.int8.onnx,decoder.int8.onnx,joiner.int8.onnx,tokens.txt} "$MODELS/asr/" && rm -rf "$MODELS/asr/$A"
else echo "ok  asr"; fi

echo "== textures"; python3 pipeline/textures.py
echo "== done. Next: ./make_reel.sh <slug>   (reference reel: stories/night-watch-cut)"
