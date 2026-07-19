KIT_NAME="growth"
SKILLS_SRC="agents/product-skills"
SKILLS=( growth-product-analytics finance-business-impact )
# aso-growth-system is a Neyra-internal overlay (hardcoded aso/ paths) — lives in
# settings/skills/, never ships with the generic kit. See settings/README.md.
PORTABLE_AGENTS=( growth-analytics analytics-instrumentation kit-onboarding )
TEMPLATED_AGENTS=( linear-router )
MCP_SERVERS=( neyra firebase )
GOVERNANCE_TMPL="AGENTS.growth.md"
CURSOR_SKILLS=1
