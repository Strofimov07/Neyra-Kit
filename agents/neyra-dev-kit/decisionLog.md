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
