#!/usr/bin/env bash
# Run Claude Code headless on this repo (it reads CLAUDE.md automatically).  usage: automation/run_claude.sh "<task>"
# Auth: CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`, uses your Claude subscription) or ANTHROPIC_API_KEY.
set -euo pipefail
cd "$(dirname "$0")/.."
# Tokens never contain spaces or line breaks; a copy from a terminal often adds a line break where the window wrapped it.
for v in CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_API_KEY; do
  if [ -n "${!v:-}" ]; then clean=$(printf '%s' "${!v}" | tr -d '[:space:]'); echo "::add-mask::$clean"; export "$v=$clean"; fi
done
[ -z "${ANTHROPIC_API_KEY:-}" ] && unset ANTHROPIC_API_KEY
[ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && unset CLAUDE_CODE_OAUTH_TOKEN
command -v claude >/dev/null || npm install -g @anthropic-ai/claude-code >/dev/null 2>&1
export BASH_DEFAULT_TIMEOUT_MS=900000 BASH_MAX_TIMEOUT_MS=1800000   # image downloads can take ~10-25 min on CI IPs
MODEL=$(python3 -c "import json; print(json.load(open('config.json')).get('claude_model', 'opus'))")
# Claude never talks to Gigi or the platforms directly (CLAUDE.md): hide those secrets from its shell
env -u TELEGRAM_BOT_TOKEN -u TELEGRAM_CHAT_ID -u GH_PAT -u GITHUB_TOKEN -u GH_TOKEN claude -p "$1" --model "$MODEL" --fallback-model sonnet --permission-mode acceptEdits --max-turns 400 \
  --allowedTools "Bash Read Write Edit Glob Grep WebSearch WebFetch TodoWrite" \
  --output-format stream-json --verbose | python3 automation/claude_log.py
