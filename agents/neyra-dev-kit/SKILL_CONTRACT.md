# Canonical SKILL.md contract (v1)

One skill format, validated by `lint-skills.py`, consumed by **two runtimes**:
- **kit** (team-facing) — Claude Code `.claude/agents` + `agents/*/SKILL.md`, Cursor `.cursor/skills`.
- **AssistantUI** (user-facing, NEB-944) — in-app NeyraAgentKit descriptor-only loader (NEB-933).

The libraries are independent (different skills/audiences); only this **format** is shared. See Linear NEB-1249.

## File shape
A skill is a directory containing `SKILL.md`. The file starts with a `---`-fenced YAML frontmatter, then a markdown body (the system-prompt-style instructions).

```markdown
---
name: kebab-case-id
description: >-
  What the skill does + an explicit "Use when …" / "Trigger with …" phrase so
  it can be auto-selected. First ~1–2 sentences are the descriptor shown in the
  base prompt (descriptor-only loading); the body loads on invocation.
when_to_use: >-            # optional if the trigger is already in `description`
  Use when …
tools: Read, Grep, Glob   # optional — restrict to the minimum the skill needs
model: sonnet             # optional — alias tracks current model; omit to inherit
requires_memory: []       # optional — NEB-751 memory contract
connectors: []            # optional — MCP/connector dependencies
---

# Title
You are an expert at … (rubrics, taxonomies, steps, success criteria)
```

## Rules (enforced by the linter)
1. **Frontmatter** — file MUST begin with a `---` fence and contain a closing `---`.
2. **`name`** — required; kebab-case `^[a-z0-9]+(-[a-z0-9]+)*$`; SHOULD match the directory name.
3. **`description`** — required; non-trivial (≥ 40 chars); this is the descriptor surfaced to the model.
4. **Trigger** — the skill MUST carry an explicit "when to use" signal so auto-invocation works in both runtimes: either a non-empty `when_to_use` field, or a `use when` / `trigger with` / `when …` phrase in `description`.
5. **Optional fields** — `when_to_use`, `tools`, `model`, `requires_memory`, `connectors` are allowed; unknown keys warn, don't fail.

## Recommended: anti-rationalization block

A skill changes behavior only if the agent doesn't talk itself out of using it.
For any skill that an agent is tempted to skip under pressure ("it's small", "I
already know", "I'll do it after"), add a section that **names the excuse and
forbids the workaround** — don't just state the rule:

```markdown
## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's a tiny change." | Tiny changes regress silently. Do the step anyway. |
| "I'll do it after." | After-the-fact work rubber-stamps the result. Do it first. |
| "There's no harness here." | Check first; if truly none, say so and fall back — never silently skip. |
```

Rationale (borrowed from obra/superpowers' pressure-testing): stating a rule
isn't enough — the model rationalizes around it. Enumerating the specific
escape hatches and closing each one is what makes the discipline stick. See
`test-first` and `verify-runtime` for live examples. Not linted — a convention.

## Writing rules that actually fire

A rule the model can reason its way around won't change behavior. When authoring
or editing a skill:

- **No nuance clauses.** "Don't X *unless it matters*" reopens negotiation — the
  model decides it doesn't matter. State the rule flat, then carve explicit,
  closed exceptions if truly needed.
- **Match form to failure.** A skip-under-pressure failure needs an
  anti-rationalization table (above); a wrong-output failure needs a worked
  example; a missing-step failure needs an ordered checklist with success criteria.
- **Mandatory, with an announce.** Frame applicable skills as not optional, and
  require the one-line "Using `<skill>` to `<purpose>`" announce — commitment
  makes the discipline stick (the 1% rule in `KIT_BOOTSTRAP.md`).

Borrowed from obra/superpowers' skill-authoring discipline. Not linted — conventions.

## Loader contract (both runtimes)
- Base prompt carries **descriptors only** (frontmatter); the body is fetched on invocation via a discover-skill tool (NEB-933).
- Source priority: `policy > user > project > bundled`; symlink-aware dedup via realpath (NEB-941).
- Verify-gate: a skill's claimed outcome is checked before "done" — kit `verify-runtime`, AssistantUI verify-subagent (NEB-934).

## Lint
`python3 agents/neyra-dev-kit/lint-skills.py [dir ...]`  → exits non-zero on any violation. Default dirs: `agents/dev-skills`, `agents/product-skills`.
