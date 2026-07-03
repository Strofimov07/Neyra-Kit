<!-- neyra-dev-kit governance fragment (v0.1.0). Rendered by install.sh.
     Include this file from the repo's AGENTS.md / CLAUDE.md. Do not hand-edit the
     rendered copy — change it in the kit and re-run install. -->

# Neyra dev-kit — execution governance ({{REPO_NAME}})

This repo uses the shared Neyra engineering skill stack. Skills live under
`agents/dev-skills/` (canonical specs) and are surfaced as auto-invocable
subagents under `.claude/agents/`. The skill is the spec; the subagent is the
auto-trigger surface — invoke whichever the runtime supports.

## Default skill stack (most coding tasks)
`implementation-loop` → `simplify-diff`/`code-reviewer` → `verify-runtime`,
plus matrix add-ons below for the touched surface. For logic and bug fixes,
start with `test-first` — a failing test (RED) before the change.

## Skill ↔ subagent map
| dev-skill | subagent | fires on |
|---|---|---|
| implementation-loop | implementation-loop | default coding loop |
| test-first | test-first | logic / bug fix — failing test before the change |
| systematic-debugging | systematic-debugging | novel bug / failing or flaky test |
| simplify-diff | code-reviewer | post-implementation, before closure |
| verify-runtime | verify-runtime | real-surface verification before done |
| contract-safety | contract-checker | new/modified typed HTTP endpoint |
| localization-guard | localization-checker | user-facing string change |
| regression-scout | regression-scout | shared UI / lifecycle / nav / auth change |
| release-readiness | release-readiness | before declaring runtime work done |
| analytics-instrumentation | analytics-instrumentation | feature behavior / funnel change |
| trust-boundary-review | trust-boundary-review | AI action / sensitive data / destructive flow |
| kit-evolution | kit-evolution | end of task / recurring correction — evolve the kit |
| spec-elicitation | spec-elicitation | fuzzy task — elicit a developer-ready spec (EARS) |
| writing-plans | writing-plans | multi-step change — granular plan artifact before code |
| spec-review | spec-review | post-impl conformance — diff matches the plan/criteria |
| subagent-dispatch | subagent-dispatch | delegated multi-task plan — ledger + commit-range |
| parallel-lanes | parallel-lanes | simultaneous agents in one repo — worktree/branch isolation |
| receiving-code-review | receiving-code-review | responding to review findings — verify, no sycophancy |
| knowledge-graph | knowledge-graph | curating canonical docs/wiki, doc drifts from code, siloed/duplicated knowledge |
| goal-mode | (manual — opt-in) | autonomous goal orchestration — checkpointed, capped, Linear-anchored |

## Transparency rule (mandatory in autonomous, delegated, and `/loop` runs)
- Every iteration/turn names the active skill(s)/subagent(s) it used or assumed, and why — per step when running unattended, not only at the end.
- Report subagent results faithfully: distinguish what was verified from what is still assumed. A green subagent report is not a substitute for the required final checks.
- Skipping a matrix-required check is allowed only with an explicit one-line reason in the same turn (e.g. "no runtime here, deferred `verify-runtime`").

## Post-implementation gate (before declaring a code slice done)
1. `simplify-diff` / `code-reviewer` (quality) — reuse, scope, redundancy; plus `spec-review` (conformance — diff matches the plan/EARS criteria) when a plan or criteria exist.
2. matrix add-ons for the touched surface (e.g. `localization-checker` for copy → locales **{{LOCALES}}**; `contract-checker` for endpoints → **{{CONTRACT_STACK}}**).
3. `verify-runtime` — strongest practical check on the real surface. For this repo: `{{BUILD_VERIFY_CMD}}`.
4. `release-readiness` + `regression-scout` for high-risk or cross-layer changes.

## Repo facts (used by the subagents)
- Stack: {{STACK}}
- Build / verify command: `{{BUILD_VERIFY_CMD}}`
- Locales: {{LOCALES}}
- Typed-contract convention: {{CONTRACT_STACK}}
- Linear workspace: {{LINEAR_WORKSPACE}} (every issue MUST have a project — see `linear-router`).

<!-- kit-version: 0.14.0 -->
