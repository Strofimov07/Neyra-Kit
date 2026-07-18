KIT_NAME="dev"
SKILLS_SRC="agents/dev-skills"
SKILLS=( ALL )
# Bundled auto-inject Skills (frontend/design craft) → synced to .claude/skills/ on install +
# session-start. Opt-in per kit; only the dev kit ships them. Empty/unset in other manifests.
BUNDLED_SKILLS_SRC="agents/design-skills"
PORTABLE_AGENTS=( implementation-loop test-first systematic-debugging spec-elicitation writing-plans spec-review subagent-dispatch parallel-lanes knowledge-graph receiving-code-review code-reviewer verify-runtime regression-scout release-readiness trust-boundary-review security-reviewer analytics-instrumentation kit-evolution post-merge-watch pr-review-watch migration-safety kit-onboarding contract-doc-sync design-system-conformance incident-runbook pr-hygiene skill-capture )
TEMPLATED_AGENTS=( linear-router localization-checker contract-checker )
MCP_SERVERS=( neyra )
GOVERNANCE_TMPL="AGENTS.devkit.md"
CURSOR_SKILLS=1
