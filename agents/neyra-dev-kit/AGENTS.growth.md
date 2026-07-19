<!-- neyra-dev-kit governance fragment — growth kit. Rendered by install.sh.
     Include this file from the repo's AGENTS.md / CLAUDE.md. Do not hand-edit the
     rendered copy — change it in the kit and re-run install. -->

# Neyra growth-kit — execution governance ({{REPO_NAME}})

This repo uses the shared Neyra growth skill stack. Skills live under
`agents/product-skills/` (canonical specs) and are surfaced as auto-invocable
subagents under `.claude/agents/`. The skill is the spec; the subagent is the
auto-trigger surface — invoke whichever the runtime supports.

## Core discipline: proxy metrics + experiment loop
Every growth initiative MUST define a leading proxy metric before implementation
and a falsifiable hypothesis. Ship → measure → decide — never ship without an
observable signal. Use standard analytics event names (Firebase/GA4 standard:
`purchase`, `begin_checkout`, `view_item`, `select_content`, …) with canonical
`value`/`currency` parameters; never invent custom purchase events.

## Default skill flow (most growth tasks)
`growth-product-analytics` (funnel + metric definition) →
`aso-growth-system` (store-facing distribution) →
`finance-business-impact` (revenue + unit-economics validation).

## Skill ↔ subagent map
| neyra-skill | subagent | fires on |
|---|---|---|
| growth-product-analytics | growth-analytics | funnel analysis, metric design, experiment setup |
| aso-growth-system | _(apply inline)_ | keyword research, metadata, screenshot/creative briefs |
| finance-business-impact | _(apply inline)_ | revenue modelling, unit economics, payback period |
| _(analytics instrumentation)_ | analytics-instrumentation | feature behavior / funnel instrumentation change |

## Analytics event standards (non-negotiable)
- Use Firebase/GA4 standard event names: `purchase`, `begin_checkout`, `view_item`, `add_to_cart`, `select_content`, `tutorial_begin`, `tutorial_complete`, etc.
- Always include `value` (numeric) + `currency` (ISO 4217) on revenue events.
- Do NOT invent custom purchase event names (e.g. `subscription_purchased`) — map to the canonical standard equivalent first, add custom params for extra dimensions.
- Every new tracking call requires a corresponding analytics spec (event name, params, trigger condition) reviewed by `analytics-instrumentation`.

## Firebase experiment operations
- Firebase MCP is optional and default-off. When enabled, use it for Remote
  Config and Crashlytics operations; do not represent it as a GA4
  reporting connector.
- Before a live Remote Config publish: define the metric contract, read and
  snapshot the active template, preserve unrelated parameters and condition
  order, show the exact diff, name the rollback version, and get explicit human
  confirmation.
- Use an ETag-aware publisher. If the MCP template does not carry its active
  ETag, prefer Firebase CLI deploy; do not silently replace a failed non-forced
  write with a forced overwrite.
- After publish, verify the active template and a real client fetch separately
  from measurement delivery to GA4, BigQuery, or the product-owned event mirror.
- Before requesting a Crashlytics report, read the bundled
  `crashlytics_reports_guide` through `firebase_read_resources`.
- Credentials remain in Firebase CLI or Application Default Credentials. Never
  put refresh tokens, access tokens, or service-account keys in repo settings.
- `FIREBASE_MCP_ACCESS=full` exposes the complete configured administration
  surface but does not waive per-action confirmation. Before write/delete/send,
  initialization, creation, or deploy, state the target and side effect, obtain
  explicit confirmation, and retain audit plus rollback/containment evidence.

## Transparency rule (mandatory in autonomous, delegated, and `/loop` runs)
- Every turn names the active skill(s)/subagent(s) it used or assumed, and why.
- Distinguish observed metric movement from assumed correlation.
- Skipping a metric-definition step is allowed only with an explicit one-line reason in the same turn.

## Repo facts (used by the subagents)
- Stack: {{STACK}}
- Build / verify command: `{{BUILD_VERIFY_CMD}}`
- Locales: {{LOCALES}}
- Typed-contract convention: {{CONTRACT_STACK}}
- Linear workspace: {{LINEAR_WORKSPACE}} (every issue MUST have a project — see `linear-router`).

<!-- kit-version: 0.28.0 -->
