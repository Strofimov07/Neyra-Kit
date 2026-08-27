---
name: grounding-gate
description: >-
  Enforces that every factual claim a product emits is bound to a retrieved
  source with an effective date, and that unsupported claims are refused rather
  than generated. Use when a change touches generated answers, summaries,
  advice, or any output that asserts facts a user will act on.
when_to_use: >-
  Use whenever a diff changes prompts, answer assembly, retrieval wiring, or the
  source corpus of a product that answers questions from a body of knowledge —
  and before shipping any model, prompt, or corpus swap.
tools: Read, Grep, Glob, Bash
---

# Grounding gate

## Goal

Make it structurally impossible for the product to state a fact it did not
retrieve. A fluent answer built from model memory is indistinguishable from a
sourced one at the surface — only a gate at assembly time separates them.

The corpus, its identifier fields, its effective-date field, and the refusal
copy are **project facts**: read them from `settings/facts/grounding.md` in the
consuming repo (create it on first use). This skill owns the procedure only.

## Protocol

### 1. Classify the claims the surface can emit

- Separate claims that need a source (facts, figures, rules, entity attributes,
  anything time-varying) from claims that do not (restating the user's input,
  arithmetic on given numbers, formatting).
- Any claim a user could act on and be harmed by belongs in the first class.

**Success criteria**
- The claim classes are named, and the sourced class is explicit.

### 2. Bind each sourced claim to a retrieved record

- Every sourced claim carries the identifier of a record that was actually
  retrieved in this request — not one the model recalls, and not one retrieved
  in an earlier turn unless it is still in the request context.
- If assembly can emit a claim with no bound record, that is the defect. Fix the
  assembly, not the prompt wording.

**Success criteria**
- Each sourced claim maps to a record id present in this request's retrieval set.

### 3. Carry the effective date, and say it

- A record that can be superseded carries its effective / valid-until date into
  the answer. State the as-of date the answer is true for.
- A corpus with no effective-date field cannot support time-varying claims —
  say so and treat it as a gap, not a detail.

**Success criteria**
- The output states what date its facts are current as of, or the surface is
  documented as not carrying time-varying claims.

### 4. Refuse instead of guessing

- No retrieved support → an explicit "not found in the sources" path, not a
  plausible answer with hedged wording. Hedging reads as an answer.
- The refusal path must be reachable in production, not only in tests: name the
  condition that triggers it and verify it fires.

**Success criteria**
- The refusal path exists, is reachable, and was exercised at least once.

### 5. Gate it deterministically, in CI

- Add a check that does not need a judge model: extract the identifiers the
  answer cites, assert each exists in the corpus. A cited-but-absent identifier
  is a fabrication and fails the build.
- Judge-model scoring is a complement, never the gate — it cannot be the only
  thing standing between a fabricated citation and a user.

**Success criteria**
- A deterministic citation-existence check runs in CI on a pinned case set.

### 6. Pin every wrong answer you find

- Each discovered wrong or stale answer becomes a pinned regression case with
  the expected source, before the fix. Fixes without pins regress silently once
  the retrieval path changes underneath them.

**Success criteria**
- The defect is represented as a pinned case that fails before the fix.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "The model reliably knows this one." | Model memory has no effective date and no audit trail; it silently ages. Retrieve it (step 2). |
| "The source is almost certainly still current." | "Almost certainly" is the exact failure that reaches a user as fact. Carry the date (step 3). |
| "It hedges, so it's not really a claim." | Users read hedged text as an answer. Refuse explicitly (step 4). |
| "The judge model will catch fabrications." | A judge is sampled, non-deterministic, and can share the generator's blind spot. Deterministic existence check first (step 5). |
| "It's a prompt tweak, not a behavior change." | Prompt tweaks move exactly the boundary this gate protects. Run the pinned set (step 6). |
| "We'll add pins after the fix ships." | A fix without a pin is a coincidence waiting to be undone. Pin first. |

## Output

- The claim classes, and where binding happens in the code path.
- The as-of date the surface reports, or the gap.
- Whether the refusal path was exercised, and how.
- The deterministic check and the pinned cases it runs.
