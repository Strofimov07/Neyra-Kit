---
name: contract-safety
description: >-
  Reviews backend, API, job, analytics, and integration changes for contract
  safety: backward compatibility, idempotency, side effects, failure handling,
  and observability. Use when a change crosses a system boundary.
when_to_use: >-
  Use when modifying API endpoints, webhook handlers, background jobs, data
  contracts, sync flows, analytics payloads, auth behavior, or anything with
  external or cross-layer side effects.
---

# Contract safety

## Goal

Catch breakage at system boundaries before a change is treated as shippable.

## Review pass

### 0. Verify the canon itself before trusting it

- If this review leans on a canonical registry or doc as the list of what currently
  exists, do not take its claims at face value. Cross-check the concrete claims —
  namespaces, endpoints, fields, enum members — against the actual code in the same pass.
- A canon page is a snapshot a human wrote. It drifts silently on deletion, because
  nothing un-lists itself. Code is truth for existence, exactly as it is for behavior.
- A canon claim the code does not back up is **stale canon, not a lead to chase**. Flag
  and fix it (or file the fix) in the same turn. Never investigate or design against
  something that is not in the code.

**Success criteria**
- Every concrete existence claim taken from a canon doc was checked against code.

### 1. Identify the contract boundary

- Name the caller, callee, payload shape, side effects, and failure surfaces.
- Check whether the change affects compatibility for existing clients or flows.

**Success criteria**
- The changed contract surface is explicit.

### 2. Check compatibility

- Verify request/response shape, field semantics, default values, and status behavior.
- Check for schema drift, renamed meanings, or silent removals.
- For analytics, verify payload shape and downstream expectations.
- For dispatch logic keyed on an enum or type field (order type, event type, webhook
  type), verify **every member has a handled branch**. A member that silently no-ops —
  no exception, no warning, no log — is the highest-risk shape there is: nothing signals
  the gap, so it ships and stays broken until someone notices a business outcome is
  missing. Seen in production: a payment fulfiller handled three of five order types;
  the other two marked the order paid, counted the revenue, and granted nothing.

**Success criteria**
- Compatibility risk is understood and either preserved or intentionally versioned.

### 3. Check operational safety

- Verify idempotency, retry behavior, duplicate delivery handling, timeout behavior, and partial failure semantics.
- Check whether the change adds side effects that need ordering, compensation, or stronger guards.

**Success criteria**
- The contract will behave safely under retries, duplicates, and failures.

### 4. Check observability

- Ensure the boundary emits the needed logging, metrics, and error signals.
- Name any missing alert or dashboard coverage.

**Success criteria**
- Operators can detect and diagnose failures on the changed boundary.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's an internal endpoint." | Internal callers break too — silently, in prod. Check compatibility anyway. |
| "It's backwards-compatible enough." | "Enough" is where renamed meanings and silent removals hide. Verify field semantics. |
| "Retries can't happen here." | They can — timeouts, at-least-once delivery, user double-taps. Check idempotency. |
| "We'll add logging later." | Without observability you can't detect the failure you're enabling. Add it with the change. |

## Output

Report:
- changed contract boundary
- compatibility result
- operational risk
- observability coverage
- follow-up debt if any
