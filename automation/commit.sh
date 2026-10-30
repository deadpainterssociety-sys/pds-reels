#!/usr/bin/env bash
# Commit and push whatever the job changed, retrying if another job pushed meanwhile.
# usage: automation/commit.sh "message" [paths...]     (default paths: stories schedule.json config.json automation/bot_state.json ...)
set -uo pipefail
cd "$(dirname "$0")/.."
msg=$1; shift
paths=${*:-"stories schedule.json config.json automation/bot_state.json STORY_QUEUE.md PLAYBOOK.md pipeline/pronounce.json"}
git config user.name "dps-bot"; git config user.email "dps-bot@users.noreply.github.com"
for p in $paths; do [ -e "$p" ] && git add -A "$p"; done
git diff --cached --quiet && { echo "nothing to commit"; exit 0; }
git commit -q -m "$msg"
BR=${GITHUB_REF_NAME:-main}
for i in 1 2 3 4 5; do   # another job may have pushed meanwhile: replay our commit on top (ours wins on conflicts)
  git fetch -q --depth=50 origin "$BR" && git rebase -q -X theirs "origin/$BR" && git push -q origin "HEAD:$BR" && { echo "pushed: $msg"; exit 0; }
  git rebase --abort 2>/dev/null; sleep $((i * 5))
done
echo "push failed after 5 tries"; exit 1
