---
name: data-inventory
description: >-
  Builds and maintains the inventory of personal or sensitive data a system
  holds — subjects, stores, basis, retention, deletion, and every party it is
  sent to — derived from the code rather than from memory. Use before a
  compliance pass, a launch, or any change that adds a data category or recipient.
when_to_use: >-
  Use when preparing to sell or register a product, adding a store, log,
  analytics sink, or third-party recipient, or when asked what data the system
  holds about people and for how long.
tools: Read, Grep, Glob, Bash
---

# Data inventory

## Goal

Answer, from the code, four questions per data category: whose data is it, where
does it sit, why are we allowed to hold it, and when does it go away. Systems
accumulate stores faster than anyone documents them, so the inventory must be
derived and re-derived, not written once.

The lawful bases and required notices are jurisdiction-specific: they come from
`settings/compliance/<jurisdiction>.md`. This skill owns the derivation.

## Protocol

### 1. Enumerate subjects, including the ones who never signed up

- Registered users are the easy category. Also count: invited-but-not-registered
  people, people named inside content users upload, counterparties, staff of
  business customers, and anyone appearing in imported corpora.
- A subject who never agreed to anything still creates obligations.

**Success criteria**
- The subject list includes at least one category that did not register.

### 2. Enumerate stores, including the ones nobody calls a database

- Tables, object storage, uploaded file bytes, request and prompt logs, error
  traces, caches, queues, analytics sinks, third-party processors, and backups.
- Backups and log aggregators hold copies with their own lifetimes — list them
  separately, not as an afterthought of the primary store.

**Success criteria**
- Log/telemetry sinks and backups appear as their own rows.

### 3. Record basis and notice per category

- Each category gets its basis and the notice or consent that supports it, taken
  from the jurisdiction profile. Where a basis is contested or assumed, mark it
  as a decision to be recorded, not as settled.

**Success criteria**
- No category is left with an unstated basis.

### 4. Give every store a retention period, then verify the deletion actually runs

- A store with no stated period is retained forever — that is a decision, and it
  should be a deliberate one.
- Grep for the deletion path. A documented retention with no job behind it is
  worse than none, because it reads as satisfied in an audit.
- Deletion must reach derived copies: search indexes, caches, exports, backups.

**Success criteria**
- Every store has a period, and each period names the code that enforces it.

### 5. Confirm the subject-facing paths exist

- Deletion of an account, export of what is held, correction of what is wrong:
  check whether they exist in code at all, and say so plainly when they do not.

**Success criteria**
- The presence or absence of each subject-facing path is stated as a fact from
  the code.

### 6. Map every hop out of the system

- Third-party APIs, analytics, mail senders, model providers, CDNs — and transit
  hops such as proxies or egress gateways, which are recipients even when they
  only forward.
- Include what fields leave, not only which vendor.

**Success criteria**
- Each recipient is listed with the fields it receives and where it sits.

### 7. Handle free-text and derived stores explicitly

- Prompt logs, request taps, and support transcripts collect personal data in
  free text where field-level rules do not apply. Note masking coverage and be
  explicit about what masking does **not** cover.

**Success criteria**
- Free-text stores state their masking coverage and its gaps.

### 8. Keep it derived

- Re-derive from models and migrations; add a check that fails when a new store
  appears without an inventory row.

**Success criteria**
- A new store cannot land silently.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "That data is already public." | Public availability is not automatically a basis to process it. Record the basis (step 3). |
| "Logs only contain identifiers." | Identifiers identify — that is the definition. Inventory them (step 2). |
| "Backups don't count, they're just copies." | Copies have their own lifetime and their own recipients. List them (step 2, 4). |
| "We'll delete manually if anyone asks." | Manual promises are not enforceable at volume, and derived copies get missed. Verify the job (step 4). |
| "The retention is in the docs." | Docs are not enforcement. Point at the code (step 4). |
| "The proxy just forwards traffic." | A transit hop is a recipient in another location. Map it (step 6). |
| "Masking covers the logs." | Masking covers patterns it knows; names in free text usually survive. State the gap (step 7). |

## Output

- Subjects × stores table with basis, retention, and the code that enforces it.
- The subject-facing paths that exist and the ones that do not.
- Recipients with the fields they receive.
- The rows that are decisions rather than settled facts.
