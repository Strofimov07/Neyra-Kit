---
name: knowledge-graph
description: >-
  Treats a project's durable knowledge as a typed memory graph instead of a pile
  of pages — typed nodes (Requirement, Decision/ADR, Risk, Component, Event/Metric,
  Runbook), typed edges, single-source-per-fact, a freshness contract
  (Owner / Last-verified / Cadence / drift-vs-code), and a code→node bridge so a
  code change updates the right canonical node. Keeps the wiki navigable, current,
  and connected to code and execution.
when_to_use: >-
  Use when adding or curating canonical docs/wiki, when documentation has drifted
  from code (a "plan" is already implemented), when knowledge is siloed or
  duplicated across pages, when a decision/risk needs to be recorded as a real
  record (not a checklist line), or when the user wants the wiki to behave like a
  graph of memory rather than a set of pages. Pairs with kit-evolution (routing a
  fact to the right surface) and the repo's knowledge-map manifest.
tools: Read, Grep, Glob
---

# Knowledge graph

## Goal

Keep durable project knowledge as a **navigable, current, connected graph**, not a
tree of free-text pages. Every durable fact has exactly one owner-node; everything
else links to it. A reader (human or agent) can traverse from any node to its
decisions, risks, code, metrics, and execution.

## The model (repo-agnostic)

**Typed nodes** (stable slug each): `REQ`/`UXC` (requirement/contract — typed
Business / Functional / System / UX-contract / NFR, so business- and
system-analysis requirements have a home), `ADR` (decision), `RSK` (risk), `COMP`
(code component), `EVT`/`MET` (event/metric), `RUN` (runbook). Group
glossary/surface/epic the same way.

**Typed edges:** `implements` (REQ→COMP), `verified-by` (REQ→EVT/eval),
`shapes` (ADR→REQ), `supersedes` (ADR→ADR), `mitigates` (ADR→RSK),
`observed-by` (COMP→MET), `recovers` (RUN→COMP), `traces-to` (REQ→Linear→PR),
`anchored-in` (COMP→code-anchor).

**Layer contract:** one owner-layer per fact — code = runtime truth; canonical
wiki = product/arch/UX/ops/security/decisions; tracker = execution status; repo
docs = runtime-proximal only; legacy mirrors = archive. Conflict order:
code → wiki → tracker → legacy.

**Freshness engine:** every node carries `Owner · Last-verified · Cadence ·
drift-vs-code`. Review is event-driven — a merged change updates the touched
nodes; calendar cadence is only a backstop. A rollup surfaces overdue/drifted nodes.

**Code→node bridge:** a manifest maps code-path globs → node slugs + the canon
page to update. Editing a mapped file obliges updating its node(s).

## Triggers (what fires a doc/canon update)

Freshness depends on four triggers — strongest to softest. A durable change is not
done until its strongest applicable trigger has fired; the cadence sweep is
insurance, not the mechanism.

1. **Code → node (event-driven, primary).** Changing a file mapped in the repo's
   `knowledge-map` obliges updating the mapped node in the same change. **DoD:** the
   change isn't complete until each touched mapped node is updated (or explicitly
   marked still-valid). Enforce with a changed-paths-vs-manifest check in the
   post-implementation gate / CI.
2. **Cadence sweep (calendar backstop).** Every node carries `Last-verified` +
   `Cadence`; a scheduled sweep flags overdue nodes (a freshness checker over the
   memory layer + a read of the canonical hubs' review dates). Catches the tail only.
3. **Issue close → canon.** When a tracker issue referenced by a node closes, update
   the node it affects (requirement done, risk mitigated). A closed issue whose node
   still says "planned" is drift — close the loop in the same cycle.
4. **Verify vs running system (drift).** Periodically verify the canon against the
   actually deployed/running system (staging/prod e2e), not just source — code can
   ship ahead of docs. A scheduled or pre-release pass that exercises the real
   surface and flags canon that no longer matches behaviour.
5. **Skill auto-fire (agent-side, softest).** This skill fires on doc curation or
   noticed drift; `kit-evolution` routes friction to the right surface. Never the
   only trigger for a durable fact.

## Loop

1. **Locate the owner-node.** For the fact at hand, find the single node that owns
   it (by type + layer contract). If none exists, the change is "create one node",
   not "add a paragraph to whatever page".
2. **Check for drift & duplication.** Does code already contradict the node
   (`plan` that is now implemented)? Is the same fact written in two pages? Prefer
   one owner + relation over a second copy.
3. **Type the edges.** Connect the node to its REQ/ADR/RSK/COMP/EVT and to
   Linear/PR/code-anchor — not a prose mention, a real link/relation.
4. **Stamp freshness.** Set `Last-verified`; set `drift-vs-code` honestly
   (`Fresh`/`Stale`/`Drift`). Use stable code-anchors (module/function), not line
   numbers.
5. **Bridge.** If the touched code is in the knowledge-map manifest, update the
   mapped node in the same change; if it isn't but should be, add the mapping.

## Rules

- One owner-node per fact; everything else links. Duplication is a defect, not redundancy.
- **Don't mirror the tracker.** Current focus, task/epic status, active work, and
  ownership live in the issue tracker (e.g. Linear), not the wiki. A "current focus /
  active tracks / component status" section in a canonical page is duplication that
  drifts — collapse it to a tracker link/view. The wiki owns only what the tracker
  doesn't: decisions, risks, contracts, architecture.
- A decision is an ADR record (context / decision / alternatives / consequences /
  status / date / owner), not a checklist line. A risk is severity × likelihood +
  owner + status, not a bullet.
- Stable anchors over line numbers; relations over prose mentions.
- `Drift` (code ahead of canon) is a first-class state — flag it, don't hide it.
- This skill governs structure and freshness; it does not invent product facts —
  unknowns get an explicit `open question`, not a guess.
- Writes to the external canon (Notion/wiki) are outward-facing — propose first,
  land after approval; never bulk-mutate the canon unprompted.

## Success criteria

- The fact landed on exactly one owner-node, correctly typed.
- Its edges connect it to code, decision, risk, metric, and execution as applicable.
- `Last-verified` and `drift-vs-code` are set; no silent duplication introduced.
- If code was touched, the mapped node was updated in the same change.
