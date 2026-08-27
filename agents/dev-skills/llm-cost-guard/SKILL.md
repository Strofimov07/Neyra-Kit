---
name: llm-cost-guard
description: >-
  Keeps the unit cost of a metered-API product correct and bounded: a formula
  derived from the vendor's own accounting, reconciled against the invoice, a
  per-request budget, and a regression gate on cost per user action. Use when a
  change affects model calls, prompt size, caching, retries, or pricing.
when_to_use: >-
  Use when adding or changing calls to a metered API, changing prompt or context
  size, enabling caching or retries, quoting a cost figure, or setting a price.
tools: Read, Grep, Glob, Bash
---

# Cost guard for metered APIs

## Goal

Keep the number you charge on and the number you pay in the same reality. A cost
formula that is wrong by a fixed percentage does not look wrong — it looks like
a margin, until the invoice arrives or a price is set on top of it.

Vendors, price tables, thresholds, and keys are **project facts**: keep them in
the consuming repo. This skill owns the method.

## Protocol

### 1. Derive the formula from the vendor's accounting, not from intuition

- Read what each usage field actually counts. Vendors differ on whether cached
  input is **inside** the input count or a **separate** addend — assuming the
  wrong one skews every figure you will ever quote.
- Multi-rate items (cache writes at different retention tiers, batch discounts,
  reasoning tokens) are separate terms with separate rates.

**Success criteria**
- Each usage field maps to exactly one term, with the vendor's own definition cited.

### 2. Reconcile against the invoice before trusting the number

- Compare a period of your computed cost against the vendor's billed amount for
  the same period and keys. A gap is a formula defect, not rounding.
- Know which keys/environments roll into which invoice line; a shared console
  total across environments is not your product's cost.

**Success criteria**
- A reconciliation was run, and the residual gap is stated as a percentage.

### 3. Cost the user-visible action, not the API call

- One user action may fan out into retries, tool loops, sub-calls, and reranks.
  Price the action; per-call figures understate it silently.
- Include the paths that do not reach the user: failed generations, cancelled
  requests, and background jobs still cost money.

**Success criteria**
- The unit is a user action, and fan-out is counted in it.

### 4. Bound the request, fail closed

- Enforce a ceiling on input size and total spend per request, rejecting before
  the call rather than after. An unbounded input path is an unbounded bill.
- Estimation used for the ceiling must be calibrated against the vendor's own
  counter, and kept in sync across every language that implements it.

**Success criteria**
- Oversized requests are rejected before the metered call, and the estimator was
  calibrated.

### 5. Gate cost regressions like correctness regressions

- Track cost per action in the same run that tracks quality, and fail the gate on
  a threshold breach. Quality improvements that quietly triple cost are a
  business regression.

**Success criteria**
- A cost-per-action threshold runs alongside the quality gate.

### 6. Watch prices you do not control

- Vendor prices change outside your release cycle. Run a scheduled comparison of
  your price table against the vendor's published pricing, and treat a parse
  failure as a signal, not noise.
- Confirm a suspected change against a second vendor page before editing the
  table: a rate cell without context is not a decision.

**Success criteria**
- A scheduled check exists and its failures are routed to a human.

### 7. Changing the formula cuts the series

- When the formula changes, historical figures are incomparable. Mark them,
  recompute where it matters, and re-baseline — see `eval-baseline`.

**Success criteria**
- The break in the cost series is visible where costs are reported.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "The provider returns usage, so the total is right." | Usage fields have vendor-specific semantics; summing them wrong is invisible. Map each field (step 1). |
| "Caching only reduces cost." | Cache writes are billed above base rate; a bad cache strategy raises cost. Model each term (step 1). |
| "The console total matches roughly." | Roughly is where a stable percentage error hides. Reconcile a period (step 2). |
| "It's one extra call, it's negligible." | Fan-out compounds per action and per user. Cost the action (step 3). |
| "Users won't send inputs that large." | Some will, and the bill is theirs to trigger and yours to pay. Bound it (step 4). |
| "Prices are stable, the table is fine." | Vendors reprice mid-quarter. Automate the check (step 6). |

## Output

- The formula, term by term, with the vendor definition each term rests on.
- The reconciliation result and residual gap.
- Cost per user action, with fan-out included, and the threshold that gates it.
- Any break in the historical series, marked.
