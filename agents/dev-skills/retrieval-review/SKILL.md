---
name: retrieval-review
description: >-
  Reviews changes to a search or retrieval path against two independent
  verdicts — findability and relevance — and forbids tuning coupled parameters
  one at a time. Use when a diff touches queries, filters, ranking, reranking,
  chunking, or the indexed fields behind them.
when_to_use: >-
  Use whenever retrieval behavior changes: query construction, analyzers,
  filters, boosts, rerank stages, result caps, chunking, or index mappings.
tools: Read, Grep, Glob, Bash
---

# Retrieval review

## Goal

Prevent the two failure modes that look identical in a diff: a change that finds
more but returns worse, and a change that scores better because it silently
stopped returning anything hard.

Index names, field names, caps, and analyzer behavior are **project facts**:
read them from `settings/facts/retrieval.md` in the consuming repo (create it on
first use).

## Protocol

### 1. Hold two verdicts, never one

- **Findability**: can a known item be retrieved at all, by the identifiers real
  users type?
- **Relevance**: is what comes back actually usable for the request?
- A drop in one is not redeemed by a rise in the other. Report both, always.
- Low findability can be a *correct* filter doing its job — verify which it is
  before "fixing" it.

**Success criteria**
- Both verdicts are stated, with the case sets each was measured on.

### 2. Move coupled parameters together

- Candidate pool size, rerank window, and result cap are coupled and usually
  non-linear: raising one alone starves or floods the next stage.
- Before tuning, name the coupled set. Change the set, measure, then decompose.

**Success criteria**
- No single-parameter tuning claim on a parameter with a named partner.

### 3. Verify the query on live data, not only in unit tests

- Unit tests assert query *shape*; they cannot see that an analyzer, tokenizer,
  or normalizer makes a clause match nothing.
- Confirm any new or changed clause returns a non-zero, sane count against a
  real index before merge — a clause that silently matches zero is the most
  common retrieval defect and it passes every unit test.

**Success criteria**
- Each new/changed clause has a live count, and the number is in the report.

### 4. Replay real requests, not fixtures

- Score against a captured set of real requests. Fixtures encode what the author
  already thought of.
- Include the requests that previously failed.

**Success criteria**
- The replay set includes prior production failures.

### 5. Check what the change removed

- Every filter, dedup, or cap is also a deletion. Name what stopped being
  returned and confirm it should have.

**Success criteria**
- The removed set is inspected, not assumed empty.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "Recall went up, so it's better." | Recall rises when a filter stops filtering. Read relevance too (step 1). |
| "Recall went down, so I broke it." | It may be a correct filter finally working. Inspect the removed set (step 5). |
| "The unit tests are green." | They assert query shape, not that it matches anything. Get a live count (step 3). |
| "I only raised one limit." | Coupled stages starve or flood each other. Move the set (step 2). |
| "My test queries all work." | Author-written queries encode the author's assumptions. Replay real ones (step 4). |
| "It's just a mapping/analyzer tweak." | Analyzer changes silently zero out existing clauses. Count them again (step 3). |

## Output

- Both verdicts with their case sets, before and after.
- The coupled parameter set that was moved, and the live counts per changed clause.
- What the change stopped returning, and why that is correct.
