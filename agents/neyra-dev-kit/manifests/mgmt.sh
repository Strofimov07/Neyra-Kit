KIT_NAME="mgmt"
SKILLS_SRC="agents/mgmt-skills"
SKILLS=( ALL )
PORTABLE_AGENTS=( team-health-check delivery-audit portfolio-pmo goal-okr kit-onboarding )
TEMPLATED_AGENTS=( linear-router )
MCP_SERVERS=( none )
GOVERNANCE_TMPL="AGENTS.mgmt.md"
CURSOR_SKILLS=1
# Manager's workspace kit — installs into a leader's repo/workspace (use
# --allow-non-git for a plain notes workspace). Personal-mode data stays in
# the consumer's settings/private/ (gitignored) — never part of this kit.
