# Subagents (published set)

Auto-invocable Claude Code wrappers around the kit's skills — the
portable set from the kit manifests. Templated agents (linear-router,
localization-checker, contract-checker) are rendered into your repo by
install.sh from agents/neyra-dev-kit/templates/, not stored here.

| Subagent | Fires on |
|---|---|
| [analytics-instrumentation](analytics-instrumentation.md) | Defines and verifies analytics coverage for a feature — event map, payload, owner, observable proxy, blind spots, runtime trigger coverage |
| [code-reviewer](code-reviewer.md) | Senior code reviewer for Swift/iOS and Python/Django diffs. Performs a simplify-pass focused on reuse, redundant state, scope creep, and avo |
| [delivery-audit](delivery-audit.md) | Period audit of what a team actually shipped, in business terms — investment distribution (feature/bug/tech-debt/KTLO/unplanned), diff-vs- |
| [delivery-planner](delivery-planner.md) | Decomposes work into executable units, slices roadmaps, enforces task-anchor discipline (every issue has a project, owner, and clear DoD), a |
| [goal-alignment](goal-alignment.md) | Traces active and planned work to the goal set (Objectives/KRs) and estimates each item's expected effect on its goal — direct/enabling/KT |
| [goal-okr](goal-okr.md) | Goal-setting and OKR tracking for a senior leader — forms OKRs from strategy and projects, falsifiable KRs (EARS), 0.0–1.0 grading, expe |
| [growth-analytics](growth-analytics.md) | Growth and product analytics framing — metrics, experiments, proxy instrumentation, funnel thinking, retention/growth loops. |
| [implementation-loop](implementation-loop.md) | Default coding loop — inspect → plan → patch → verify, minimal diffs, explicit assumptions, strong repo-pattern reuse. Use for most  |
| [kit-evolution](kit-evolution.md) | Closes the kit's learning loop — turns friction, corrections, and skipped gates from real work into a concrete, validated kit change (new  |
| [kit-onboarding](kit-onboarding.md) | Interactive kit setup interview after install — fills everything the kit needs to work at full quality in this repo/workspace: install con |
| [knowledge-graph](knowledge-graph.md) | Treats durable project knowledge as a typed memory graph (typed nodes + typed edges + single-source-per-fact + freshness contract + code→n |
| [migration-safety](migration-safety.md) | Reviews database schema migrations for production safety — rolling-deploy backward compatibility (expand/contract), lock behavior on large |
| [parallel-lanes](parallel-lanes.md) | Gives each simultaneously-running agent its own isolated lane — one git worktree (or at least one branch + explicit-path commits), one Lin |
| [portfolio-pmo](portfolio-pmo.md) | Portfolio-level PMO for cross-team planning — dependency graph from the tracker, deduplicated RAID register (Risks/Assumptions/Issues/Depe |
| [post-merge-watch](post-merge-watch.md) | Watches CI/CD after a human-approved merge lands — polls the triggered pipelines for a bounded window, surfaces failures in the same turn, |
| [product-brainstormer](product-brainstormer.md) | Frames problems before solutions — separates symptoms from root cause, produces explicit hypotheses and assumptions, maintains an open-que |
| [receiving-code-review](receiving-code-review.md) | Disciplined consumption of code-review findings — read without reacting, verify each against the actual code, then implement by severity ( |
| [regression-scout](regression-scout.md) | Scans for likely regressions adjacent to a change — permissions, loading/empty/error states, caching, polling, navigation return paths, an |
| [release-readiness](release-readiness.md) | Final production-readiness pass before declaring a change done — smoke path, rollback thinking, feature flags, monitoring, owner visibilit |
| [solution-designer](solution-designer.md) | Converts problem framing into solution structure — user flows, UX states, interaction semantics, surface fit. |
| [spec-elicitation](spec-elicitation.md) | Turns a vague request into a developer-ready spec via one-question-at-a-time elicitation, ending in a structured spec with EARS acceptance c |
| [spec-review](spec-review.md) | Reviews an implementation against its plan / acceptance criteria — every requirement mapped, nothing unrequested added (YAGNI). The confor |
| [subagent-dispatch](subagent-dispatch.md) | Dispatches a multi-task plan across fresh subagents with a compaction-proof protocol — a durable ledger, the BASE commit recorded per task |
| [systematic-debugging](systematic-debugging.md) | Roots out a novel bug by investigation before any fix — reproduce, find the root cause (not the symptom), compare against a working exampl |
| [team-health-check](team-health-check.md) | Recurring engineering-org health report for leadership — DORA delivery metrics, SPACE-lite team effectiveness, squad-health morale, infra  |
| [test-first](test-first.md) | Drives logic changes test-first — writes a failing test that encodes the intended behavior (RED), makes it pass with minimal code (GREEN), |
| [trust-boundary-review](trust-boundary-review.md) | Reviews high-trust changes for permission boundaries, user confirmation, destructive actions, hidden side effects, data exposure, and audita |
| [verify-runtime](verify-runtime.md) | Verifies code changes on the strongest practical runtime path for the affected surface (real browser flow for web UI, real endpoint for back |
| [writing-plans](writing-plans.md) | Produces a granular, reviewable implementation plan artifact before any code — exact file paths, per-step real code, the command + expecte |
