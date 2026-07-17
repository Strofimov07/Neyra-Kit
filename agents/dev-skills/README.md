# Dev skills — canonical source for engineering execution

This directory is the canonical source for reusable engineering skills that guide
implementation quality, verification discipline, and repeatable development
workflows.

These skills are for agent execution during development work. They are not part
of any end-user skill product catalog.

| Skill | Purpose |
|--------|---------|
| [implementation-loop](implementation-loop/SKILL.md) | Default coding loop: inspect, plan, patch, verify, minimal diff |
| [simplify-diff](simplify-diff/SKILL.md) | Post-implementation cleanup for reuse, quality, efficiency, and scope |
| [verify-runtime](verify-runtime/SKILL.md) | Strong runtime verification on the real affected surface |
| [contract-safety](contract-safety/SKILL.md) | Boundary safety for APIs, jobs, analytics, side effects, and retries |
| [release-readiness](release-readiness/SKILL.md) | Final production-readiness and rollout confidence pass |
| [analytics-instrumentation](analytics-instrumentation/SKILL.md) | Event map, proxy metric, blind spot, and runtime analytics coverage |
| [localization-guard](localization-guard/SKILL.md) | Enforce localization contract on user-facing changes |
| [design-system-conformance](design-system-conformance/SKILL.md) | Reuse existing components, tokens, and state patterns |
| [contract-doc-sync](contract-doc-sync/SKILL.md) | Keep backend/platform contract docs synced with code |
| [regression-scout](regression-scout/SKILL.md) | Nearby regression scan for shared state and adjacent flows |
| [trust-boundary-review](trust-boundary-review/SKILL.md) | Permission and side-effect safety for high-trust features |
| [security-review](security-review/SKILL.md) | Adversarial appsec review of a diff: injection, authz/IDOR, secrets, crypto, SSRF, deserialization — exploit-first, false-positive filtered |
| [batch-migration](batch-migration/SKILL.md) | Large parallelizable migrations, only with explicit delegation approval |
| [skill-capture](skill-capture/SKILL.md) | Turn repeatable engineering workflows into reusable skills |
| [pr-hygiene](pr-hygiene/SKILL.md) | Branch / commit / PR mechanics, scoped staging, no AI attribution |
| [incident-runbook](incident-runbook/SKILL.md) | Diagnose & contain known prod incidents from encoded failure modes |
| [knowledge-graph](knowledge-graph/SKILL.md) | Typed memory graph: nodes/edges, single-source, freshness, code→node bridge |
