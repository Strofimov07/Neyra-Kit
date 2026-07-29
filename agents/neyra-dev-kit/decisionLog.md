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

## 2026-07-25 — Five shipped kit defects found by a Tea Farm audit (v0.31.0)

**Context.** A full documentation and monetization audit in the Tea Farm consumer
surfaced nine signals. Five were not consumer misconfiguration but defects in the
shared kit itself, each shipped and silent:

- the `doc-freshness` workflow template triggered on `paths: src/**`, a directory no
  consumer has, so the only automated anti-staleness mechanism never fired anywhere;
- `check_code_node.py` hardcoded `origin/main` as its diff base, silently degrading to
  `HEAD~1` in any repo that integrates on `dev` or `master`;
- `localization-guard/SKILL.md` hardcoded `For Browser, at least en and ru`, leaking one
  product's name and locale scope into a shared skill;
- `check-skill-mapping.py` never validated `agents/dev-skills/README.md` against the
  directory, and the AGENTS-table check it does run has an `is_consumer` relaxation — so
  index drift was invisible by design (this kit's own README was missing 14 of 31 rows);
- `kit-evolution` cited a `Self-Improvement Rule` and a `Current lessons` section in the
  consumer AGENTS include that the template never created, leaving the learning loop
  with no landing zone.

The common shape of the first four: a mechanism that fails open. Nothing raises, nothing
warns, and absence of output is indistinguishable from a clean result.

**Decision.** Fix all five at the source, and promote four cross-cutting lessons from the
same audit into the skills that should have caught them:

- `contract-safety` gains step 0 — verify a canonical registry against code before
  trusting it as the list of what exists, because canon drifts silently on deletion;
- `contract-safety` gains an enum-exhaustiveness rule — a dispatch branch that silently
  no-ops is the highest-risk shape in a codebase;
- `release-readiness` requires the smoke path to include the grant, not just the status
  transition, for payment/reward/entitlement flows;
- `knowledge-graph` makes `Drift` bidirectional: canon ahead of code is an unresolved
  build-or-descope decision, not a stale doc, and needs the opposite response.

The `linear-router` template additionally gains a duplicate check keyed on defect rather
than title, with a required quoted root cause, after a title-similarity verdict nearly
discarded three distinct defects. Its model moves from `haiku` to `sonnet`: comparing
root causes is not tag routing.

**Sequencing vs the v0.30.0 batch.** This batch was authored as v0.30.0 in parallel with
the consumer-signal batch above; that one merged first and claimed 0.30.0, so this one
re-bumps to 0.31.0. The two touch the same `kit-evolution` "Current lessons" anchor from
opposite directions, and the merged result is complementary rather than conflicting: the
v0.30.0 batch removed the step-1 *dedup* pointer to "Current lessons" (routing dedup to
the `signals.log` ledger), while this batch gives the `Self-Improvement Rule` the skill
still cites — plus a `Current lessons` promotion landing zone — real sections in the
consumer `AGENTS.include` template. The skill reference and its landing zone now agree.

**Consequence.** Consumers must upgrade to pick these up; installed copies are generated
state and are overwritten by `install.sh`. The widened workflow trigger makes the
freshness job run on every PR — this is intentional, since the script itself reports
`no mapped paths touched` and the step is non-blocking.

## 2026-07-29 — linear-router gains label hygiene (v0.32.0)

**Context.** A Linear workspace was found to have accreted a label mess: two naming
conventions side by side (Capitalized bare `Bug`/`Feature`/`Improvement` vs lowercase
`prefix:value`), Linear's seed labels left undescribed, no real label groups (the `:` in
names only imitates grouping), and colors reused across unrelated axes. Labels are a
controlled vocabulary, but the kit had no rule governing them — `linear-router` enforced
project-required and defect-based dedup, yet said nothing about labels — so drift was
inevitable wherever the router is installed.

**Decision.** Extend the `linear-router` template with a **Label hygiene** section:
reuse-before-create (match by meaning via `list_issue_labels`, not by string), one axis
per label from an approved set, a required one-line description, naming and color fixed by
the axis, and propose-don't-proliferate (a new label or axis is an approved proposal, never
a silent mid-issue creation; superseded labels are marked `obsolete`/archived). Mutually-
exclusive axes (type, status) are Linear **label groups**; cross-cutting marks stay
`flag:value`. The concrete taxonomy is delegated to a new `{{LINEAR_LABELS}}` placeholder
rendered from consumer config — the skill owns the shape, `settings/` owns the label set,
per the scoping rule. `list_issue_labels` is added to the router's tool set for the
reuse check. A companion rule — **native fields over label-encodings** — was added after a
live migration showed priority, hierarchy, and time-horizon encoded as labels (`prio:*`,
`type:task/subtask/epic`, `horizon:*`) duplicating native tracker fields that were already
populated (priority set on ~99% of tagged issues, sub-issues natively parented): labels are
reserved for work **nature** and **domain**, while priority, hierarchy, dependencies, and
portfolio grouping live in their native homes (Priority, parent/sub-issue, blocking
relations, Initiatives).

**Consequence.** The router now gates labels at create/relabel time and can drive a
cleanup pass, but never deletes or bulk-relabels without per-item approval. Consumers
declare their approved axes and labels in the install config (`LINEAR_LABELS`); leaving it
empty keeps the generic rules with no enumerated set, so nothing breaks on upgrade. The
example configs carry a generic `type`/`status`/`area`/flags taxonomy with `area:*` left
for the consumer to fill. Migrating an existing workspace's labels into groups is a
separate, human-approved action against the live tracker, not part of this kit change.

## 2026-07-29 — kit gates hardened: fast Stop gate + repo-root resolution (v0.33.0)

**Context.** Two gate defects surfaced in the TradingCoreModules kit audit (NEB-1612,
NEB-1486). (1) The Stop hook ran the **full** `doctor.sh` fail-closed on every turn, and
doctor transitively runs prose/frontmatter linters — `lint-plans.py` flags a quoted
`TODO`, `lint-skills.py` rejects a UTF-8 BOM, none handle a non-UTF-8 byte — so one benign
markdown could exit non-zero and block **every** agent in the repo until the file was
edited, plus a ~2.6s per-turn tax. (2) The standalone gates (`lint-scope.py`,
`lint-skills.py`, `check-skill-mapping.py`) resolved their targets from the cwd, so
running them the way EVOLVING-THE-KIT documents — from `agents/neyra-dev-kit/` — left
every default dir unresolved and they printed `skip … / OK`, passing vacuously. A gate
that greenlights from the wrong directory is worse than no gate.

**Decision.** (1) `doctor.sh` gained a `--fast` mode — structural integrity only (source
identity, hook wiring, decisionLog, version stamp, multi-tool surfaces), none of which a
document's content can trip — and the Stop gate (`hooks/stop-gate.sh`) now calls
`doctor.sh --fast`. The full run (linters, regressions, egress, Codex/Firebase/Impeccable
smokes, branch hygiene) stays on CI and manual `doctor.sh`. (2) The three standalone gates
now resolve the repo root from their own file location (three parents up), so any cwd
validates the same tree, and they **fail closed** — a default invocation that finds no
skill layer exits non-zero instead of printing OK.

**Consequence.** A malformed markdown can no longer wedge every turn in a consumer repo,
and the documented EVOLVING-THE-KIT gate commands now validate instead of silently
skipping. `--fast` runs in <1s vs ~2.6s. Explicit-arg invocations are unchanged (still
cwd-relative), so the unit tests and any target-directory callers keep working. Consumers
pick this up on the next `install.sh`.

## 2026-07-29 — gate-resolution regression coverage (v0.33.1)

**Context.** v0.33.0 hardened the standalone gates (NEB-1486) but shipped without the
automated regression its DoD required — the fail-closed and wrong-cwd behavior was only
checked by hand. Closing an issue with an unmet DoD item is the exact antipattern the
signal ledger already records ("no unticketed follow-ups before closure").

**Decision.** Add `test-gate-resolution.py`: the three gates validate (not skip) when run
from `agents/neyra-dev-kit/` and from an unrelated cwd, and a gate copied outside a kit
tree fails closed. Wired into the full `doctor.sh` run and the installer's copy list so
consumers carry it.

**Consequence.** NEB-1486's DoD is fully met; a regression back to cwd-relative resolution
or a vacuous pass now fails `doctor`. Patch bump only — no behavior change to the gates.

## 2026-07-29 — goal-mode tolerates stringified Workflow args (v0.33.2)

**Context.** `goal-mode.workflow.js` read `args.tasks` directly. When a caller (or a
resumed run) hands Workflow args over stringified — a documented foot-gun of the Workflow
tool — `args` is a string, `args.tasks` is `undefined`, and the batch silently returned
"no tasks provided", hiding the mistake instead of surfacing it.

**Decision.** Parse a stringified `args` payload before use, and throw a clear error when
it is a string that is not valid JSON (NEB-1502). A genuine empty-tasks object still
returns gracefully.

**Consequence.** A mis-shaped invocation now either works (valid stringified JSON) or
fails loudly with a fix hint, never no-ops silently. Driver-only change; no protocol change.

## 2026-07-29 — goal-mode: empty batch fails loudly + robust-invocation docs (v0.33.3)

**Context.** NEB-1502 carried three DoD items; v0.33.2 shipped only the stringified-arg
parse. Two remained: an empty batch should fail loudly (post-checkpoint-1 an empty batch
is always a caller error), and the robust wrapper-invocation pattern should be documented.
Closing the issue at v0.33.2 left both unmet — the same premature-closure antipattern the
ledger warns about.

**Decision.** The empty-tasks guard now throws instead of returning `{ results: [] }` — a
silent no-op reads as "round ran, nothing to do" and burns an approved round.
`orchestration/README.md` gains a **Robust invocation** section: dispatch the driver from a
thin wrapper via `workflow(ref, argsObject)` to guarantee the child receives a real object.

**Consequence.** NEB-1502's DoD is fully met. Behavior change from v0.33.2: a caller that
dispatches an empty batch now gets a clear error instead of a benign empty result.
