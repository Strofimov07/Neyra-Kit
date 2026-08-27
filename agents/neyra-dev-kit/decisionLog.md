# Neyra-Kit decision log

This append-only log is authoritative from v0.27.0 onward. Historical decisions
before the source cutover remain frozen in the legacy AI Browser checkout and
are not an authoring surface.

## 2026-08-27 — Product-launch gates: the kit learns that shipping is not selling (v0.40.0)

**Context.** A consumer product passed every gate the kit had — plans, tests,
reviews, contracts, migrations, release readiness — and was still not sellable.
An independent audit and two internal structure audits landed the same verdict
from three directions: the product answered from model memory instead of its own
corpus and quoted superseded rules; measurements were compared across a silently
changed instrument twice; unit cost was computed with a formula that misread the
vendor's usage semantics by a fixed ~19%; thirteen non-code requirements
(contracting entity, agreement shape, data handling, payment proof, disclosures)
surfaced only after a year of development; retention existed on 2 of 15 stores
and account deletion did not exist in code at all; the first backup of the
primary datastore was taken a year in and never restored from; multi-hour jobs
died on ordinary deploys; and one module reached 17k lines with 121 private
symbols pinned by 98 test files, making a split a precondition for hiring. None
of these classes had a skill, a rule, or a check anywhere in the kit — the
existing 31 skills all assume the hard part is writing correct code.

**Decision.** Add the missing layer as eight skills, three amendments, three
checks, and one profile. New skills: `grounding-gate`, `eval-baseline`,
`retrieval-review`, `llm-cost-guard` (product truthfulness and unit economics);
`launch-compliance`, `data-inventory` (the non-code path to a first sale);
`launch-ops-baseline`, `long-job-discipline` (operating it). Amendments:
`security-review` gains untrusted-content-into-prompt as a taxonomy class,
`regression-scout` requires replaying parser/extractor changes over populated
real data, `verify-runtime` requires naming the suites that were not run.
Enforcement over exhortation for the two failures that are structural rather
than cognitive: `check-module-size.py` (module growth + tests pinning private
symbols) and `check-repo-hygiene.py` (host addresses in tracked docs, committed
build output, gitignore directory traps, broken relative links). `settings/product.yml`
plus `product-profile.py` (which carries its own starter template under `--seed`) let a product declare what it is — sells, holds personal
data, calls metered APIs, emits claims, has retrieval, runs long jobs, is in
production — and the kit answers which gates are mandatory and which project-fact
files are missing. `launch-compliance` and `launch-ops-baseline` are cadence
skills with no auto-trigger surface, so they join MANUAL rather than shipping a
subagent that would fire on unrelated diffs.

The profile itself needed the same treatment it was built to give: a declaration
with no freshness contract rots exactly like a runbook naming a decommissioned
host. So it carries `last_reviewed` + `review_after_days` (default 90), and
`product-profile.py` reads the code back — reporting capabilities the repository
demonstrably has while the profile denies them (a metered-API SDK, a payment
integration, a personal-data field in a model, a deploy pipeline). The check runs
in one direction only: declared-false-but-present is a finding, declared-true-
without-evidence is not, because a gate switched on early is the safe side. Three
skills now carry the update trigger at the moments a capability actually appears:
`launch-compliance` (new market, data category, payment method, subprocessor),
`data-inventory` (first personal-data store or first recipient abroad), and
`release-readiness` (the release that turns any of them on). `test-product-profile.py`
pins all of it, including the scoping that keeps the word "email" in prose from
tripping the personal-data signature.

**Consequence.** The kit now covers "is this sellable and operable", not only "is
this correct". Jurisdiction and domain stay out of the shared layer by
construction: `launch-compliance` owns the requirement taxonomy while the legal
position lives in `settings/compliance/<jurisdiction>.md` authored by a qualified
person, and `grounding-gate` / `retrieval-review` / `long-job-discipline` read
their corpus, index, and runtime facts from `settings/facts/` — the same
delegation the kit already applied to locales in v0.30. `lint-scope` confirms the
new layer carries zero project facts. doctor gained two advisory reports (product
profile, missing facts directory) that warn and never fail, so no existing
consumer breaks on upgrade. The three new checks are advisory by default and fail
only under `--strict`, because their thresholds are per-repo judgment, not policy.

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

## 2026-07-29 — anti-rationalization sweep across 12 dev-skills (v0.34.0)

**Context.** A manual `code-reviewer` gate on an earlier kit PR found 12 of 31 dev-skills
lacked a `Common rationalizations` block (NEB-1590) — including gate-path skills where a
skipped step costs the most (`spec-review`, `pr-hygiene`, `post-merge-watch`,
`subagent-dispatch`). `SKILL_CONTRACT.md` prescribes the block precisely for "skipped
under pressure" failures: a rule the agent can rationalize around is not a fix until the
excuse that bypasses it is named. The asymmetry was live — `pr-review-watch` had a block,
its post-merge twin `post-merge-watch` did not, though the failure mode is identical.

**Decision.** Add a `## Common rationalizations (and why they're invalid)` table (3–5 rows)
to all 12, each row a real excuse + "why wrong → what to do" naming the skill's own
step/rule, grounded in `signals.log` and each skill's documented failure modes — not
manufactured formality. Every one of the 12 had a genuine skip-under-pressure mode, so no
one-line justification was needed. Drafted by a subagent, then reviewed row-by-row for
authenticity against the source signals.

**Consequence.** Every gate-path skill now names the excuse that would bypass it, closing
the `pr-review-watch`/`post-merge-watch` asymmetry. `lint-skills.py` stays green
(46 · 0 failed). Content-only across skills; no gate or behavior change.

## 2026-07-29 — Cursor hook behavioural smoke closes the doctor false-green (v0.34.1)

**Context.** NEB-1613: `.cursor/hooks.json` wires the PreToolUse guard to `preToolUse`,
flagged as inert because `preToolUse` wasn't a documented Cursor event. Cursor's current
hook docs now list it (with `allow`/`deny`), so the config is valid. The real remaining
defect was `doctor.sh` reporting the Cursor config OK from file existence alone — it can't
detect a config the host silently ignores. Same false-green class NEB-1483 fixed for Codex.

**Decision.** Add a Cursor behavioural smoke to the full `doctor.sh` run, mirroring the
Codex one: the guard must ALLOW a normal edit and DENY a kit-managed path. Cursor denies
with `{"permission":"deny"}` on exit 0, so the smoke asserts on the emitted JSON, not the
exit code. The config is unchanged — it is correct; "present" now means "verified working".

**Consequence.** The Cursor guard can no longer regress to a silent no-op behind a green
doctor. Full-run only (behavioural), so the Stop gate stays `--fast`.

## 2026-07-29 — dead cross-file anchor lint + drop stale version stamp (v0.34.2)

**Context.** NEB-1591, two silent-drift classes no validator caught. (1) `kit-evolution`
routed "a recurring mistake or missing rule" to `` AGENTS.md `Lesson → Rule → Checklist
hook` `` — a heading present in neither the shipped governance template nor the canonical
`AGENTS.md`, so the route silently no-opped. (2) `.neyra-dev-kit.version` sat in the
canonical repo root at `0.27.0` (VERSION was well ahead) — monorepo-sync residue that
`EVOLVING-THE-KIT.md` §8 says canon must never carry; only `session-start.sh:57` reads it,
and only as a boolean "installed" marker, never the value.

**Decision.** Reformulate the `kit-evolution` route to `` AGENTS.md `Current lessons` ``
(which the template has, promoted via the `Self-Improvement Rule`). Delete
`.neyra-dev-kit.version` from canon (session-start's `[ -f ]` guard handles absence). Add
`check-cross-refs.py`: a dev-skill reference to a backticked AGENTS.md section that is not
a heading in the shipped governance fails in canon and warns in a consumer — wired into
the full `doctor.sh` run with a regression test, and copied to consumers by `install.sh`.

**Consequence.** A fresh consumer's `kit-evolution` routing targets all exist, and a future
dead anchor fails `doctor` instead of silently no-opping. The third unvalidated version
copy is gone. Full-run only; the Stop gate stays `--fast`.

## 2026-07-29 — auto-memory freshness in the Self-Improvement loop (v0.34.3)

**Context.** NEB-1366's port already landed — `knowledge/memory_freshness.py` (generic:
memory dir from arg → `CLAUDE_MEMORY_DIR` → CWD, no hardcoded path) and `check_code_node.py`
are in kit-source, and the freshness contract (`Owner · Last-verified · drift-vs-code ·
Cadence`) lives in the `knowledge-graph` skill. The one open non-optional item: the
Self-Improvement Rule didn't connect auto-memory to that contract, so a changed fact could
be re-stored without re-stamping `last_verified` and the checker couldn't sweep it.

**Decision.** Extend the Self-Improvement Rule (shipped governance template) so auto-memory
is part of the loop: on a fact change, update the node AND re-stamp `last_verified`, so
`memory_freshness.py` can flag staleness. The optional Stop-gate/`doctor` enforcement is
deferred by design — the memory layer is CWD/env-resolved and absent in canon and most
consumers, so a `doctor` call needs guarded warn-only wiring; tracked as a follow-up if wanted.

**Consequence.** The freshness checker now has an authored obligation feeding it. Doc-only;
no gate or behavior change.

## 2026-07-29 — doctor profile-aware + governance footer renders from VERSION (v0.34.4)

**Context.** NEB-1484: a non-dev bundle (product/growth/mgmt) ships a different skills
layer (`agents/{mgmt,product}-skills`, no `agents/dev-skills`) and none of the dev-only
`pr-review-watch`/`security-review`. Running the installed `doctor.sh` in such a consumer
failed three ways — surfaced by installing product + mgmt profiles into temp repos and
running their doctor: (1) `test-portable-reviewers.py` raised `FileNotFoundError`;
(2) the gate-hardening from v0.33.0/v0.34.2 (`check-skill-mapping`, `check-cross-refs`)
fail-closed on a missing `agents/dev-skills` — a regression those PRs introduced for
non-dev bundles; (3) the version-stamp check compared VERSION against each profile
governance's own literal footer, which had drifted (product 0.4.0, growth 0.28.0, mgmt
0.12.0) because only `AGENTS.devkit.md` ever got bumped.

**Decision.**
- `install.sh` stamps `kit=<profile>` in `.neyra-dev-kit.source`; `doctor.sh` runs the
  portable-reviewer regression only for canonical or `kit=dev`, else notes a skip.
- `check-skill-mapping.py` and `check-cross-refs.py` treat "no `agents/dev-skills` but
  another skills layer present" as **N/A** (return 0); they still fail closed when NO
  skills layer exists at all (preserves the NEB-1486 anti-vacuous-pass guard).
- The governance footer is now `{{KIT_VERSION}}`, rendered from VERSION at install for
  every profile, so a consumer's fragment always matches its installed version. `doctor`
  accepts the unrendered placeholder in canon. **No manual per-release footer bump.**
- `test-gate-resolution.py` no longer asserts the absence of "skip" (a non-dev bundle
  legitimately skips layers it doesn't ship); exit code + the fail-closed case are the signal.

**Consequence.** `doctor.sh` passes in temp product / mgmt / dev consumers (all verified),
the reviewer test still fail-closes for dev/canonical, and the four governance footers can
no longer drift. `test-check-skill-mapping.py` gains regressions for the non-dev-N/A and
no-layer-fail paths.

## 2026-07-30 — installer retires stale kit-managed files on upgrade (v0.34.5)

**Context.** NEB-1487: upgrading a long-lived consumer left files the current installer no
longer writes (the signal: stale `agents/neyra-dev-kit/AGENTS.devkit.md` and
`templates/codex/hooks.json` from a v0.26.1 layout), which then tripped the newer
doctor/version/Codex checks until removed by hand. Copy/sync covered current files but had
no retirement pass.

**Decision.** `install.sh` records a manifest (`.neyra/kit-manifest.tsv`) of the files it
manages under `agents/neyra-dev-kit/` — the fully kit-owned tooling tree — with sha256. On
the next install it prunes any manifest path the new managed set no longer includes, **only
when the file's checksum still matches the recorded one** (an unmodified kit file); a file
changed since install is kept and reported, never deleted (RET-2). `--dry-run` lists without
changing (RET-3); only manifest paths are ever considered (RET-5). The managed set is
derived from the SOURCE via a single `NK_TOOL_FILES` list shared with the copy loop, so the
two can't drift and stale files can't masquerade as current.

**Consequence.** An upgraded consumer no longer accumulates orphaned kit files. Scope is the
kit's own `agents/neyra-dev-kit/` tree (where the drift occurs and no user files live); the
skill/agent mirrors already self-prune via `rsync --delete`, and single files (governance,
hooks configs) are overwritten each install. `test-retire.py` installs into a temp repo and
asserts RET-1/2/3/5; canonical-only in `doctor.sh`.

## 2026-07-30 — goal-mode checkpoint-1 enforced by a hook (v0.34.6)

**Context.** NEB-1589 (split from NEB-1588, which fixed only the prose half): goal-mode's
"checkpoints are mandatory" was exhortation, not enforcement — nothing under
`hooks/` knew about goal-mode, so nothing stopped a dispatch before checkpoint-1 approval.
That is exactly the skip-under-pressure the kit's own rule says to enforce over exhort.

**Decision.** A gate file `.neyra/goal-mode.gate` carries the run phase: the goal-mode skill
arms it `awaiting-checkpoint-1` on entry (step 1), flips it to `approved` at checkpoint 1
(step 3), and removes it on stop (step 8). The PreToolUse hook `count-task.sh` — now wired on
`Task|Workflow` — blocks any dispatch while the gate reads `awaiting-checkpoint-1`. The four
design questions from the issue: (1) active-and-unapproved is read from the gate *content*,
not mere run presence; (2) it blocks `Task` and `Workflow` dispatch (both paths) and nothing
else; (3) it is **Claude-Code-only** — Cursor/Codex dispatch differently and rely on the
protocol prose, named explicitly in the skill; (4) a gate older than 6h is treated as stale
and ignored (fail-open) so a crashed run can't wedge normal work, and the block message says
how to clear it. No gate = not goal-mode = normal dispatch, never blocked (no false positives).

**Consequence.** Checkpoint 1 is enforced, not hoped for, on Claude Code. A canonical
`doctor.sh` smoke asserts block-while-awaiting / allow-after-approval /
no-false-positive-when-inactive. Cursor/Codex enforcement stays protocol-prose (documented).

## 2026-07-30 — kit-evolution: promote two sprint signals to rules (v0.34.7)

**Context.** The 10-task kit sprint surfaced two recurring, costly patterns, captured via the
kit-evolution loop. (1) Two issues (NEB-1486, NEB-1502) were closed as Done before their full
DoD was met — worked from the title/summary, not the body's acceptance criteria (both caught
and fixed in follow-up PRs). (2) Hardening two gates to fail-closed on a missing
`agents/dev-skills` silently broke `doctor` for non-dev bundles, caught only by empirically
installing those profiles (NEB-1484). Three lighter one-offs (governance-footer drift,
destructive-op list drift, a commit-on-main slip) were already closed structurally during the
sprint and are logged for the record.

**Decision.** Promote the two patterns. `release-readiness` §6 gains a bullet + a
rationalization row: read the full issue body, enumerate its acceptance criteria, and confirm
each before Done — the title is not the DoD. `EVOLVING-THE-KIT.md` §5 gains a gate-authoring
rule with a runnable per-profile `install + doctor` loop, distinguishing "not shipped by this
profile" (N/A) from "broken" (fail). All five signals recorded in `signals.log`. Also fixed a
drift introduced by NEB-1484: §4 still instructed authors to bump a literal footer that is now
the `{{KIT_VERSION}}` render.

**Consequence.** The two failure modes that recurred this session now have a named rule the
next run trips over, not just hindsight. Prose/rule-only; no code or gate behaviour change.

## 2026-07-30 — installer reconciles kit-owned blocks on upgrade (v0.35.0)

**Context.** NEB-1651 + NEB-1648, both found upgrading a real consumer (Pravo/TCM) to
0.34.7. `install.sh` copied files idempotently, but two kit-owned *in-place* blocks were
written once and never updated: the `AGENTS.md` inline governance block (skipped if its
heading was present) and the `.claude/settings.json` hook wiring (skipped if any kit hook
was present). On upgrade this meant new template sections — the `Current lessons` landing
zone `kit-evolution` routes promoted rules to — never reached consumers, and the v0.34.6
goal-mode `Task|Workflow` hook matcher arrived **inert** (the enforcement shipped that same
day did not actually reach an upgraded consumer).

**Decision.** Both blocks reconcile in place. The `AGENTS.md` block is wrapped in
`<!-- neyra-dev-kit:begin/end -->` markers and its content replaced between them on every
install; an unmarked legacy block is migrated once (replace from its first managed heading
to EOF); repo content outside the markers is untouched; a managed heading the repo also
owns outside the block is reported, not clobbered; `--dry-run` prints the diff. The
`settings.json` hooks reconcile via `jq`: per event, drop existing kit-owned hook groups
(command references `neyra-dev-kit/hooks`) and add the current ones, preserving the
consumer's own hooks. Both are idempotent.

**Consequence.** An upgraded consumer now receives current governance sections and current
hook wiring — kit changes stop arriving inert. Verified empirically (fresh → drift →
upgrade, consumer content preserved) and by `test-reconcile.py` (reconcile + legacy
migration), canonical-only in `doctor.sh`. This closes the exact gap that neutered the
goal-mode enforcement on the Pravo upgrade.

## 2026-07-30 — check-cross-refs resolves against AGENTS.md in consumers (v0.35.1)

**Context.** NEB-1647: the cross-ref lint (shipped v0.34.2) resolved anchors in a consumer
against `AGENTS.neyra-devkit.md`, but the referenced sections (`Self-Improvement Rule`,
`Current lessons`) live in the repo's own `AGENTS.md` — `install.sh` appends the kit block
there, while the render is built from `$GOVERNANCE_TMPL` and carries no such sections.
Result: a guaranteed false-WARN in every dev consumer (found upgrading Pravo). The canonical
check was green because it resolves against the template — the exact "test the gate on every
profile / a real consumer" gap promoted to a rule the same day (EVOLVING-THE-KIT §5).

**Decision.** In consumer mode, resolve against the union of `AGENTS.md` + `CLAUDE.md` +
`AGENTS.neyra-devkit.md` (a skill saying "`X` in AGENTS.md" means AGENTS.md); warn, never
fail (a consumer may rename headings). Canon unchanged (template, fail on a dead anchor). A
section absent from all three still WARNs — not evergreen.

**Consequence.** No more false-WARN in consumers; the check stays meaningful. Verified by
`test-cross-refs.py` (consumer layout, both directions) and empirically on a dev-consumer
install (`doctor` without the WARN). Patch bump.

## 2026-07-30 — port six hook robustness fixes upstream (v0.36.0)

**Context.** NEB-1650: six hook defects were fixed only locally in the TradingCoreModules
consumer because the hooks fire on every tool-call for anyone cloning the repo — none
reached canonical Neyra-Kit, so every kit upgrade silently reverted them. The kit's own
doctrine ("shared behavior is never authored in a product repository") makes the defect the
fact that these lived downstream.

**Decision.** Port all six to canon: (1) `post-tool-use-format` formats only when the repo
has a formatter config (`has_cfg` over pyproject.toml/ruff.toml/.ruff.toml/setup.cfg,
.swiftformat, .prettierrc*) — without it the hook imposed the tool's default style on a repo
that never opted in (79/146 tracked `.py` rewritten from a one-line edit). (2) It only
touches files inside the repo — a caller's absolute path could point anywhere. (3) All five
hooks guard the shim source (`. lib/host-io.sh 2>/dev/null || exit 0`) — without it a missing
shim made `stop-gate` exit 127 and block the agent. (4) The `host-io` bare `+++`/`---`
fallback is bound to an actual `apply_patch` invocation, so a read-only `git apply` diff is
no longer misread as an edit, while a real `apply_patch` (with or without the `*** Begin
Patch` envelope) still blocks. (5) The guard's block message points at re-installing from
canon (a consumer has no `install.sh`). (6) `check_code_node` catches `FileNotFoundError` in
both `default_base()` guards and `changed_files()` — it crashed with a traceback when git
was absent from PATH.

**Consequence.** The six fixes now live upstream and survive every upgrade; consumers can
drop their local re-patching. Each verified before/after (config-gated formatting,
external-path skip, missing-shim → exit 0, read-only `git apply` allowed + `apply_patch`
blocked both ways, graceful no-git). `test-codex-hooks.py` updated for the config gate;
`doctor: OK`.

## 2026-07-30 — npm-lock CI-parity rules in verify-runtime / pr-hygiene (v0.36.1)

**Context.** NEB-1649: three signals from a real consumer (Pravo miniapp frontend) with one
root — a `package-lock.json` generated on the dev machine lies about CI. A macOS-built lock
omits the Linux native-binding `packages` entries (rollup/esbuild), so `npm ci` on CI-Linux
can't find them; a newer local npm dedupes differently than CI's; and a `^`-ranged engine
with a native binding (vitest → rolldown) minor-bumps on regen. `verify-runtime` passed this
whole class (a green local `npm ci` is not a green CI).

**Decision.** Add **checkable** steps, not "be careful" prose. `verify-runtime` step 3 + a
rationalization row: a green local `npm ci` is not proof; reproduce CI's npm
(`npx npm@<CI ver> ci`) or grep the Linux binding entry. `pr-hygiene` step 9 + a
rationalization row: don't regenerate the lock from scratch on the dev OS; base off the
CI-green lock and `npm install --package-lock-only`; pin native-binding engines to the
CI-green version; pre-push `grep -c '"node_modules/@rollup/rollup-linux-x64-gnu"'
package-lock.json` ≥ 1. Scoping honored: the mechanic lives in the skills; CI's npm version
is a consumer fact in `settings/` (no version hardcoded).

**Consequence.** The green-local-`npm ci` failure mode now has a checkable gate and a named
excuse. Verified: the grep-check distinguishes a CI-green lock (≥1) from a macOS-regen one
(0); `lint-scope` stays green (no project facts leaked); `lint-skills` clean.

## 2026-07-30 — ENABLE_BUNDLED_SKILLS per-repo toggle (v0.37.0)

**Context.** NEB-1652: `manifests/dev.sh` sets `BUNDLED_SKILLS_SRC=agents/design-skills` at
the **kit** level, so every dev-kit consumer received 16 web/UI design skills (2.7M, 149
files) whether or not it has any UI — inert weight and list-noise in a headless repo (e.g.
a Go trading runtime). Other install surfaces (`ENABLE_LOCALIZATION_CHECKER`,
`ENABLE_CONTRACT_CHECKER`, `ENABLE_CURSOR_SKILLS`) are already per-repo; bundled skills were
the exception.

**Decision.** Add `ENABLE_BUNDLED_SKILLS` (default 1, behavior-preserving) to the install
config. The bundled-skills copy is gated on it; a headless repo sets 0 and the installer
reports the skip. Documented in `config.example.yml`.

**Consequence.** A UI-less consumer opts out of ~2.7M / 149 files with one config line;
default installs are unchanged. Verified: dev install with the toggle 0 → no
`agents/design-skills` and a "disabled" note; default → 16 skills synced; `doctor: OK`.
