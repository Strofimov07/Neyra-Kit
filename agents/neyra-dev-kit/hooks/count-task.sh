#!/usr/bin/env bash
# neyra-dev-kit Task/Workflow PreToolUse hook.
#
# Two jobs:
#  1. goal-mode checkpoint-1 enforcement (NEB-1589) — while a goal-mode run is
#     awaiting checkpoint-1 approval, block any task/workflow dispatch. Prose in
#     goal-mode/SKILL.md said "checkpoints are mandatory" but nothing enforced it.
#  2. subagent-launch counting (observational) — which subagent types actually fire.
#
# The gate file `.neyra/goal-mode.gate` is written by the goal-mode skill
# (`awaiting-checkpoint-1` on entry → `approved` at checkpoint 1 → removed on stop).
# No gate file = not a goal-mode run = normal dispatch, never blocked (no false
# positives). A gate older than 6h is treated as stale (a crashed run) and ignored,
# so a leftover marker can never wedge ordinary work.
#
# Host note: this hook is wired on Claude Code (PreToolUse Task|Workflow). Cursor/Codex
# dispatch differently and rely on the goal-mode protocol prose — see goal-mode/SKILL.md.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
nk_load

ROOT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$DIR/../../.." && pwd)}"
gate="$ROOT_DIR/.neyra/goal-mode.gate"
if [ -f "$gate" ] && [ -z "$(find "$gate" -mmin +360 2>/dev/null)" ] &&
   grep -q 'awaiting-checkpoint-1' "$gate" 2>/dev/null; then
  nk_metric goal_gate result blocked
  nk_block_edit "goal-mode: checkpoint 1 is not approved — task/workflow dispatch is blocked until the plan is approved (goal-mode step 3). If no goal-mode run is active, remove $gate."
fi

agent_type="$(nk_json tool_input.subagent_type)"
[ -z "$agent_type" ] && agent_type="unknown"
nk_metric subagent_launch type "$agent_type"
exit 0
