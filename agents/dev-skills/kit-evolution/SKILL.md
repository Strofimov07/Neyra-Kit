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
- **Persist it**: append one line to `agents/neyra-dev-kit/signals.log`
  (`DATE | signal | route | one-off|pattern`). The log is append-only and
  committed — a signal that lives only in the conversation evaporates with the
  session. This applies to insights found mid-work too, not only at retro time
  (bootstrap rule): log first, route later.

**Success criteria**
- The signal is named concretely (not "be better") and classified one-off vs pattern.
- The signal exists as a `signals.log` line before any routing happens.

### 2. Route to the right surface

| Signal | Surface |
|---|---|
| A repeatable workflow worth reusing | `skill-capture` → new dev-skill |
| A recurring mistake or missing rule | AGENTS.md `Lesson → Rule → Checklist hook` |
| A project fact / preference / decision | memory file (+ MEMORY.md pointer); `decisionLog` for the "why" |
| A gate that should be enforced, not hoped for | propose a hook / matrix add-on — don't hand-enforce |
| A skill that didn't fire or over-fired | fix its `description` to a pure "when to load" trigger |

- **Consumer-demand test (NEB-1406):** an explicit user/consumer statement of
  need satisfies the demand test by itself — never reject a routing solely for
  "no consumer asked" when the requester IS the consumer. Organic evidence is
  for prioritization, not for permission.

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
- **A VERSION bump ends with a publish to the external kit repo**
  (`publish.sh <neyra-kit-clone>` — the scope linter gates it). If publishing
  isn't possible in the same sitting, file the publish as a task in the same
  turn; internal and external must not drift silently.
- **File pattern-grade signals in Linear** via `linear-router`: first
  `list_issues` against the kit/harness backlog for an existing open ticket
  covering the same signal — a close match gets a comment/rank-bump, not a
  duplicate; only then `save_issue` (label `harness-evolution` or kit
  tech-debt, project per the routing table). One-offs stay in `signals.log`
  only. Filing the ticket is not landing the change — rule edits still need
  human sign-off.

**Success criteria**
- The change passes the kit's anti-drift checks and (for rules) is surfaced for approval.
- Internal and external kit VERSION match, or a publish task is filed.

## Rules

- Improve in the smallest durable increment; never rewrite the kit on one data point.
- One-offs go to memory, not to rules — only patterns become rules or skills.
- Never silently self-modify an enforced rule; surface the proposed diff for approval.
- Prefer enforcement (hook / check) over exhortation (prose) when the failure is skip-under-pressure.
- This skill proposes and validates kit changes; it does not grant itself authority to land governance changes unreviewed.
