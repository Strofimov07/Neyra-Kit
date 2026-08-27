---
name: launch-compliance
description: >-
  Surfaces the non-code requirements that stand between a working product and a
  sellable one — contracting entity, agreement shape, data handling, money,
  disclosure, sector rules — and classifies each as blocker, gap, or satisfied
  with evidence. Use before selling, not before shipping.
when_to_use: >-
  Use at the start of a product that will be sold, when entering a new market or
  jurisdiction, when adding payments, a new data category, or a new
  subprocessor — and to re-audit before a launch date.
tools: Read, Grep, Glob, Bash
---

# Launch compliance

## Goal

Separate "the code works" from "we may sell this". These requirements change
architecture — how the agreement is framed, where data may live, what must be
logged and shown — so discovering them late means rebuilding, not paperwork.

This skill owns the **procedure and the requirement taxonomy only**. The
jurisdiction-specific content lives in `settings/compliance/<jurisdiction>.md`
in the consuming repo and is authored or reviewed by a qualified person — an
agent may organise and trace it, never author the legal position.

## Protocol

### 1. Run it at the start of the product, not before the launch date

- Requirements in classes 2b, 2c, and 2d below change system design. Running
  this pass after the product works converts findings into rework.
- If the product already exists, run it now and accept that some findings are
  rework — that is the cost being measured, not a reason to defer again.

**Success criteria**
- The pass has an owner and a date, and its findings are in the tracker.

### 2. Enumerate the requirement classes

Walk all seven; skipping one because "that's obviously fine" is how blockers are
found by someone else later.

- **a. Contracting party** — which legal entity sells, what identifying details
  must be published to buyers, and what that entity is permitted to do.
- **b. The agreement** — what is actually sold (a right to use software, a
  service, a subscription), the document that grants it, and how it is accepted.
  The framing has tax and eligibility consequences; decide it before drafting.
- **c. Data handling** — lawful basis per data category, notices, consents,
  transfers across borders (including transit hops), retention, deletion, and
  the internal records an operator must keep. See `data-inventory`.
- **d. Money** — how payment is accepted, what proof of purchase must be issued,
  refund rules that cannot be contracted away, taxes the seller must charge or
  withhold, and obligations created by paying foreign suppliers.
- **e. Disclosure** — what the product must tell users about itself: automated
  processing, limits of its output, who is responsible for decisions taken on it.
- **f. Sector rules** — if the domain is regulated: who may offer this, required
  qualifications or registrations, restricted terminology in naming and copy.
- **g. Records** — the internal documents the operator must be able to produce on
  request, independent of anything the user sees.

**Success criteria**
- All seven classes are addressed, each with a named status.

### 3. Classify with evidence, not confidence

- Each requirement is **blocker** (cannot sell), **gap** (can sell, must fix by a
  date), or **satisfied** — and satisfied requires a pointer to the artifact:
  a file, a page, a database field, a registration number.
- "Probably fine" is a gap, not a satisfied item.

**Success criteria**
- Every satisfied item names its artifact; every blocker names what unblocks it.

### 4. Trace each requirement to code or content

- A requirement with no artifact in the repo is not implemented. Grep for it:
  the consent record, the retention job, the receipt, the footer identifiers,
  the disclosure string.
- Note which are content (a page someone must write) and which are code (a
  behavior someone must build) — they have different lead times.

**Success criteria**
- Requirements are split into content and code work with owners.

### 5. Decide architecture-forcing forks before drafting documents

- Some choices cannot be reversed cheaply once documents exist: the contracting
  entity, the agreement shape, where data is stored and processed, who the
  payment provider is, which suppliers are in the path.
- Surface these as explicit decisions with consequences, and get them decided.

**Success criteria**
- Each fork is recorded as a decision with its consequence, not left implicit.

### 6. Route what needs a qualified human

- Anything requiring legal, tax, or accounting judgment leaves the engineering
  track with a named owner and a date. Do not let an agent's summary stand in
  for that review.

**Success criteria**
- External dependencies are listed with owner and date, and are visible as
  blockers where they block.

### 7. Re-run on trigger, and update the declaration

- New market, new data category, new payment method, new subprocessor, or a
  material change in what the product claims to do.
- Update `settings/product.yml` in the same change — the flags and the
  jurisdiction list are what turn these gates on for everyone after you, and a
  profile that still describes last year's product turns them off silently.
  Stamp `last_reviewed` when you re-read it.

**Success criteria**
- The triggers are written down where the team will meet them, and the profile
  reflects what the product does now.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "We'll handle the legal side right before launch." | These items change architecture and need third parties with their own lead times. Run the pass now (step 1). |
| "We don't take payments yet, so class d is N/A." | The payment design constrains the agreement and the entity. Decide it before drafting (step 5). |
| "We're small, nobody will check." | Requirements bind on the first sale, not at a size threshold. Classify honestly (step 3). |
| "There's a template online for this." | A template that does not match your entity, data flow, and pricing is a liability with a signature on it. Route it to a qualified owner (step 6). |
| "The agent read the rules and it's fine." | An agent organises and traces; it does not hold a legal position. Get the review (step 6). |
| "It's satisfied — I remember doing it." | Memory is not an artifact. Point at the file, field, or number (step 3). |

## Output

- A table of requirements by class, each blocker / gap / satisfied with evidence.
- Content work and code work split, with owners.
- Architecture-forcing forks as recorded decisions.
- The external-review dependencies with owners and dates.
