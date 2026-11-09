#!/usr/bin/env bash
# Chatterbox's Python environment (.venv-cb) and, when the cloned voice is on, its reference clip (models/voice/ref.wav,
# from the private data release). Called by .github/actions/setup; safe to re-run (it skips what is already there).
# usage: automation/voice_env.sh [--no-ref]
set -euo pipefail
cd "$(dirname "$0")/.."
V=.venv-cb
if ! $V/bin/python -c "import chatterbox.tts, chatterbox.tts_turbo, sherpa_onnx" 2>/dev/null; then
  echo "== Chatterbox environment"
  rm -rf $V; python3 -m venv $V
  $V/bin/pip install -q --upgrade pip
  $V/bin/pip install -q --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 torchaudio==2.6.0
  echo "torch==2.6.0" > /tmp/cb-constraints.txt; echo "torchaudio==2.6.0" >> /tmp/cb-constraints.txt
  PIP_CONSTRAINT=/tmp/cb-constraints.txt $V/bin/pip install -q -r requirements-clone.txt
  $V/bin/pip install -q --no-deps chatterbox-tts==0.1.7
  $V/bin/python -c "import chatterbox.tts, chatterbox.tts_turbo, sherpa_onnx; print('chatterbox ok')"
else echo "ok  chatterbox environment"; fi
if [ "${1:-}" != "--no-ref" ] && python3 -c "import json,sys; sys.exit(0 if (json.load(open('config.json')).get('voice_clone') or {}).get('enabled') else 1)"; then
  python3 automation/voice.py fetch-ref
fi
