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
