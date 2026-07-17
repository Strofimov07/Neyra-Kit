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
code path. Ship the regression suite into consumers and run it from `doctor.sh`.

**Consequence.** Multi-file Codex edits now receive the same protection and
formatting coverage as separate Claude Code edits. Invalid or unparsable hook
payloads remain fail-open, preserving the existing anti-wedge contract.
