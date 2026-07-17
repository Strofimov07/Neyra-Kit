---
name: kit-evolution
description: >-
  Closes the kit's learning loop — turns friction, corrections, and skipped
  gates observed during real work into a concrete, validated kit change (a new
  skill, a rule, a memory, or an enforced check). The mechanism that lets the
  kit evolve within a project instead of repeating the same mistakes.
when_to_use: >-
  Use at the end of a non-trivial task or `/loop` iteration, when the same
  mistake or correction recurs, when a gate was skipped, when a skill failed to
  fire (or over-fired), or when the user says the kit should "learn" / "remember"
  something about how to work in this project.
tools: Read, Grep, Glob
---

# Kit evolution

## Goal

Convert what went wrong or felt repetitive this session into a durable, validated
improvement to the kit — so the next run is better without anyone re-teaching it.
This operationalizes the `Self-Improvement Rule` in AGENTS.md as a triggerable loop.

## Loop

### 1. Capture the signal

- What got corrected, what gate was skipped (and the stated reason), where the
  agent guessed or struggled, what the user had to repeat.
- One-off or pattern? Check memory + AGENTS.md "Current lessons" before deciding.
- **Identify the authoring boundary first:** run
  `python3 agents/neyra-dev-kit/source-policy.py --require-canonical`.
  - In the canonical Neyra-Kit repo, append one line to
    `agents/neyra-dev-kit/signals.log`
    (`DATE | signal | route | one-off|pattern`) before routing.
  - In a consumer repo, the expected failure means its kit paths are generated:
    do **not** edit or append inside them. Persist the signal directly in the
    Neyra Skills Kit Linear project after dedup. If Linear is unavailable, append
    it to local-only `.neyra/kit-evolution-pending.log`, report the sync debt, and
    move it to the canonical ledger when access returns.
- This applies to insights found mid-work too, not only at retro time: persist
  first, route later.

**Success criteria**
- The signal is named concretely (not "be better") and classified one-off vs pattern.
- The signal is durable before routing: canonical `signals.log`, Linear from a
  consumer, or an explicitly reported local pending entry.

### 2. Route to the right surface

| Signal | Surface |
|---|---|
| A repeatable workflow worth reusing | canonical Neyra-Kit: `skill-capture` → new dev-skill |
| A recurring mistake or missing rule | canonical Neyra-Kit: AGENTS.md `Lesson → Rule → Checklist hook` |
| A project fact / preference / decision | consumer memory/settings; canonical `decisionLog` only for shared kit decisions |
| A gate that should be enforced, not hoped for | canonical Neyra-Kit hook/check — don't hand-enforce in a consumer |
| A skill that didn't fire or over-fired | canonical Neyra-Kit: fix its `description` to a pure "when to load" trigger |

- **Consumer-demand test (NEB-1406):** an explicit user/consumer statement of
  need satisfies the demand test by itself — never reject a routing solely for
  "no consumer asked" when the requester IS the consumer. Organic evidence is
  for prioritization, not for permission.
- A consumer may own project-specific facts under `settings/`; that exception
  never grants it authority to modify shared kit paths.

**Success criteria**
- The change is routed to exactly one surface, with a one-line justification.

### 3. Validate before landing

- Pressure-test it: would this change actually have prevented the observed
  failure? Run the scenario in your head (or for real) against the proposed rule.
- A rule the model can rationalize around is not a fix — add an
  anti-rationalization block (see `SKILL_CONTRACT.md`) for skip-under-pressure failures.

**Success criteria**
- There is a concrete reason to believe the change prevents recurrence, not just documents it.

### 4. Land through the kit's own checks

- Run `lint-skills.py` + `check-skill-mapping.py`; keep the mapping table and
  manifests in sync (no drift).
- Behavior-changing rule / AGENTS.md edits need human sign-off — **propose the
  diff, do not self-merge.**
- The exact mechanics (source vs. synced copy, registration, VERSION bump,
  re-install, dirty-tree caution) live in `EVOLVING-THE-KIT.md` — follow it.
- Require canonical identity again before landing. A VERSION bump is authored,
  checked, pushed, and reviewed directly in `Strofimov07/Neyra-Kit`; the legacy
  `publish.sh` path is retired and must fail closed.
- Consumer upgrades happen only after the canonical revision is reviewed. Do
  not copy a consumer diff back and call it a release.
- **File pattern-grade signals in Linear** via `linear-router`: first
  `list_issues` against the kit/harness backlog for an existing open ticket
  covering the same signal — a close match gets a comment/rank-bump, not a
  duplicate; only then `save_issue` (label `harness-evolution` or kit
  tech-debt, project per the routing table). One-offs stay in `signals.log`
  only. Filing the ticket is not landing the change — rule edits still need
  human sign-off.

**Success criteria**
- The change passes the kit's anti-drift checks and (for rules) is surfaced for approval.
- The canonical PR contains the VERSION, decision, tests, and signal; any
  requested consumer rollout is linked as a separate task.

## Rules

- Improve in the smallest durable increment; never rewrite the kit on one data point.
- One-offs go to memory, not to rules — only patterns become rules or skills.
- Never silently self-modify an enforced rule; surface the proposed diff for approval.
- Prefer enforcement (hook / check) over exhortation (prose) when the failure is skip-under-pressure.
- Never author shared kit behavior in a product repository, even when its copy
  is newer, easier to reach, or the original historical source. Route to the
  canonical repo first; convenience does not create ownership.
- This skill proposes and validates kit changes; it does not grant itself authority to land governance changes unreviewed.
