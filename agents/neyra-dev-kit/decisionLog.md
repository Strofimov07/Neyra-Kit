# Neyra-Kit decision log

This append-only log is authoritative from v0.27.0 onward. Historical decisions
before the source cutover remain frozen in the legacy AI Browser checkout and
are not an authoring surface.

## 2026-07-18 — Standalone Neyra-Kit becomes the canonical source (v0.27.0)

**Context.** A shared Codex hooks correction had to be authored in the AI Browser
product monorepo and then copied here. That coupled general harness evolution to
a product repository, created two PRs for one shared change, and made this repo's
own authoring instructions self-contradictory.

**Decision.** `Strofimov07/Neyra-Kit` is the sole authoring and release source for
shared skills, agents, hooks, installer code, governance, decisions, and signals.
The root marker plus `source-policy.py` enforce that identity against the Git
origin. The former monorepo publisher is retained only as a fail-closed tombstone.
Consumer installs receive a source stamp and route evolution signals back to the
canonical repository instead of editing their generated copies.

**Consequence.** Shared changes now require one canonical PR. Product repositories
remain free to own project facts under `settings/`, but cannot become competing kit
sources. The pre-v0.27 decision history remains archive-only to avoid copying
product-specific facts into the shared repository.

## 2026-07-18 — Codex hook path handling becomes multi-file safe (v0.27.1)

**Context.** Codex sends a complete `apply_patch` operation as one hook payload.
The shared host I/O shim returned only the first file header, so a later managed
file bypassed `PreToolUse` and later code files skipped `PostToolUse` formatting.
Move destinations had the same blind spot.

**Decision.** Treat edited paths as a collection at the shared host boundary.
Enumerate every Add/Update/Delete header and move destination, make guards reject
the operation when any path is managed, and make formatters visit every existing
code path. Run the full regression suite from canonical `doctor.sh`; ship a
self-contained multi-file smoke in the consumer `doctor.sh` copy.

**Consequence.** Multi-file Codex edits now receive the same protection and
formatting coverage as separate Claude Code edits. Invalid or unparsable hook
payloads remain fail-open, preserving the existing anti-wedge contract.

## 2026-07-19 — Firebase becomes an opt-in growth control plane (v0.28.0)

**Context.** A Browser Remote Config migration reached a verified client merge
but could not complete the live template gate because the growth kit provided
neither a Firebase MCP connector nor a safe experiment-operations protocol.
Firebase's official MCP can operate Remote Config and Crashlytics, but it does
not replace GA4, BigQuery, or a product event mirror for outcome measurement.

**Decision.** Add the official Firebase MCP as a default-off connector for dev
and growth kit consumers. Use an exact tool allowlist, keep project directories
and Firebase project IDs in consumer settings, and keep authentication in
Firebase CLI or Application Default Credentials. Growth work must separate
control and measurement planes, read and snapshot before writes, show an exact
diff, require human confirmation, and retain a rollback version.

**Consequence.** Consumers can run repeatable Remote Config experiments without
making Firebase mandatory or storing credentials in the kit. A configured arm
is no longer treated as analytics evidence; metric source, owner, guard metrics,
observation window, and blind spot remain mandatory before launch.

## 2026-07-19 — Firebase gains an owner-operated full profile (v0.29.0)

**Context.** The reusable v0.28.0 connector intentionally exposed a narrow
eight-tool surface. The Browser owner needs the complete Firebase administration
surface for project operations, while the shared default still needs to remain
least privilege for consumers that did not request that authority.

**Decision.** Keep the exact allowlist as the `limited` default and add an
explicit `full` profile that enables the complete known Firebase feature-group
surface. Full availability does not waive per-action confirmation, audit, or
rollback/containment requirements for live side effects.

**Consequence.** Owner-operated consumers can read, write, create, delete, send,
initialize, and deploy through the official Firebase MCP without broadening the
default consumer surface. Firebase and Google Cloud IAM still decide which
discovered operations can execute.

## 2026-07-20 — Firebase adoption gets explicit readiness states (v0.29.1)

**Context.** The connector and full administration profile made Firebase tools
reusable, but consumers still had to reconstruct the product path from tool
setup through event ownership, Remote Config safety, runtime measurement, and
experiment activation. That made “MCP is configured” easy to overstate as
“growth analytics is production-ready.”

**Decision.** Add one generic adoption guide that separates tool-ready,
contract-ready, measurement-verified, experiment-ready, and experiment-live
states. Pin the required control/measurement boundary, correlation evidence,
safe defaults, assignment denominator, exact diff, approval, ETag-aware publish,
and rollback gates in the Firebase regression suite. Product facts remain in
consumer repositories.

**Consequence.** Every Neyra product can adopt the same guarded workflow without
copying Browser-specific configuration into the Kit, and delivery summaries must
state which readiness level is actually proven.

## 2026-07-25 — Consumer-signal batch: gate rules from a product repo (v0.30.0)

**Context.** A `kit-evolution` pass over a consumer's signal ledger (Быстрое Право,
12 signals) surfaced six failures the shared gates did not catch, each with a
concrete cost already paid: a signature change that left sibling test mocks stale
turned `dev` CI red after merge; two "green locally, red in CI" runs where an
in-memory fallback stood in for the CI's Redis/Postgres; six PRs whose automated
reviewer was usage-limited while `pr-review-watch` reported the skip as a status
rather than an absent control; a hardened client-IP primitive added for logging
while the per-IP limiters stayed on the spoofable one; an issue moved to Done still
carrying its own unresolved acceptance list, whose follow-ups lived only in a merged
commit body and resurfaced three weeks later; and a `git checkout` blocked by another
worktree whose non-zero exit went unchecked, landing three commits on the wrong branch.

**Decision.** Land the six as rules inside the gates that own them — `verify-runtime`
(mock-drift grep + infra-parity), `pr-review-watch` (skipping ≠ reviewed; escalate to
the manual gate), `security-review` (migrate every consumer of a superseded trusted
primitive), `release-readiness` (no unticketed follow-ups), `parallel-lanes` (worktree
check before destructive git; verify the checkout actually landed) — each with a
matching anti-rationalization row and a synchronized portable subagent wrapper. Fix two
defects found in the same pass: `kit-evolution`'s step-1 anchor pointed at an "AGENTS.md
Current lessons" section that exists in no consumer (the skill and its portable wrapper
both carried it), and `goal-mode` — the highest-risk of the 12 dev-skills still missing
an anti-rationalization block, since skipping its checkpoints is what the block exists
to prevent — got one.

**Consequence.** Rules sit where the agent already reads them at the moment of the
action rather than in a changelog nobody re-reads while deciding. Product-specific facts
from the same pass (pre-commit formatter behavior, which backends that repo's CI runs)
stayed in the consumer's `AGENTS.md`, per the settings-owns-facts boundary. `goal-mode`'s
hook-level enforcement stays open — the hooks have no goal-mode awareness at all — and is
tracked as NEB-1589 instead of being claimed here; anti-rationalization blocks for the
remaining 11 skills are a separate sweep. This batch's own review found the first cut of
these rules had landed the `kit-evolution` fix in the skill but not its wrapper, so the
defect would have survived the release that claimed it.
