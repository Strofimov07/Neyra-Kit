---
name: security-review
description: >-
  Adversarial application-security review of a code diff — traces untrusted
  input to dangerous sinks and reports only exploitable vulnerabilities
  (injection, broken authz/IDOR, secret & PII exposure, weak crypto, SSRF,
  insecure deserialization), each with a concrete exploit path, severity, and
  fix. Signal over noise: no generic best-practice nags. Use when a diff touches
  auth, crypto, secrets, user input, file/network I/O, deserialization,
  WebView/JS bridges, deep links, raw SQL, or anything handling untrusted data.
when_to_use: >-
  Use before closing a change that parses untrusted input, checks permissions,
  handles tokens/secrets/PII, builds SQL or shell commands, renders HTML,
  makes outbound requests, deserializes data, exposes a new endpoint, or wires
  a WebView / deep-link / URL-scheme handler.
tools: Read, Grep, Glob, Bash
---

# Security review

## Goal

Find the vulnerabilities an attacker could actually exploit in **this diff** —
and *only* those. A security review that drowns a real SQL injection in twenty
"consider adding rate limiting" notes has failed. Every reported finding must
have a plausible path from attacker-controlled input to impact.

## Scope to the diff first

- Get the change: `git diff --merge-base origin/main` (or the branch's base) and
  the list of touched files. Review the changed lines plus enough surrounding
  code to judge reachability — not the whole repo.
- Read enough context to answer *"can untrusted data reach this line?"* — the
  caller, the route/permission decorator, the serializer, the sanitizer (if any).

## Where this skill sits (don't duplicate the neighbors)

- **`security-review` (this)** — the attacker's view: can input be weaponized?
- **`trust-boundary-review`** — the user's view: is a destructive/on-behalf
  action confirmed, visible, auditable? Defer UX-trust findings there.
- **`contract-safety`** — the caller's view: compatibility, idempotency,
  observability. Defer boundary-compat findings there.
  If a finding fits a neighbor better, route it there instead of double-reporting.

## Review pass

### 1. Map untrusted input → dangerous sinks

- List the attacker-controlled sources the diff reads: request params/body/headers,
  URL-scheme & deep-link params, WebView `postMessage` / JS-bridge payloads,
  pasteboard, filenames, webhook bodies, third-party API responses, env in
  multi-tenant contexts.
- List the sinks the diff introduces or feeds: SQL/ORM raw queries, shell/
  `subprocess`, HTML/template rendering, file paths, outbound URLs, deserializers,
  auth/permission decisions, redirect targets, log/analytics calls.

**Success criteria** — every source and sink the diff touches is named.

### 2. Trace reachability (the taint test)

- For each sink, decide whether an untrusted source can reach it **without an
  effective sanitizer** on the path. If there's no reachable path, it is **not a
  finding** — say so and move on.
- Client-side validation is not a sanitizer: clients are attacker-controlled.
  Only server-/trust-side checks count.

**Success criteria** — each candidate has an explicit reachable-or-not verdict.

### 3. Classify against the taxonomy

Check the diff for each, using the technologies present in the target repo:

- **Injection** — SQL (`.raw()`, `.extra()`, `RawSQL`, string-built queries),
  command (`os.system`, `subprocess(..., shell=True)`), template/log injection.
- **Broken access control / IDOR** — object fetched by id without an owner/tenant
  check; DRF view missing `permission_classes` or using `AllowAny`; `@csrf_exempt`;
  mass-assignment via serializer `fields = '__all__'`; privilege escalation.
- **XSS / output rendering** — `mark_safe`, `|safe`, `dangerouslySetInnerHTML`,
  building HTML from input; WebView with JS enabled + untrusted content.
- **Secrets & sensitive-data exposure** — hardcoded keys/tokens/passwords;
  `SECRET_KEY`/creds in committed settings; tokens or PII written to logs or
  analytics; iOS secrets in `UserDefaults`/plist instead of Keychain; missing
  data-protection class; `NSAllowsArbitraryLoads` / disabled ATS.
- **Crypto** — weak/legacy algorithms (MD5/SHA1 for auth, ECB, static IV),
  hardcoded keys, non-CSPRNG randomness for tokens, JWT with `alg=none` or
  `verify=False`.
- **SSRF / open redirect** — outbound request to a user-supplied URL (image/
  link preview, webhook) without host allow-listing; `next=`/redirect from input.
- **Insecure deserialization** — `pickle`, `yaml.load` (non-safe), unsafe
  `NSKeyedUnarchiver`, eval-like decoding of untrusted data.
- **Path traversal** — file path built from input without normalization/containment.
- **Auth/session** — token in URL, missing expiry/rotation, TOCTOU on auth checks,
  overly broad CORS (`*` with credentials), missing `postMessage` origin check.

**Success criteria** — each applicable category is checked and marked
present/absent, not skipped.

### 4. Adversarially verify each finding before reporting

For every candidate, actively try to **refute** it:
- Is there an upstream auth check, sanitizer, ORM parameterization, or allow-list
  that already neutralizes it?
- Is the "input" actually trusted (server-generated, constant)?
- Is the sink actually reachable in a deployed build (not dead/test/example code)?

Keep it only if it survives. Mark each survivor **CONFIRMED** (you traced the
exploit path) or **PLAUSIBLE** (real risk, one assumption unverified).

**Success criteria** — no finding is reported without a stated exploit path;
refuted candidates are dropped, not listed.

### 5. Assign severity

Severity = impact × exploitability. **HIGH** = remote, unauth, or data/account
compromise. **MED** = needs auth or specific conditions. **LOW** = limited blast
radius / hard preconditions. Rank output most-severe first.

## Do NOT report (false-positive suppression)

- Generic best-practice suggestions with no concrete exploit ("add rate limiting",
  "consider defense in depth", "should use HTTPS everywhere").
- Findings in test fixtures, examples, generated code, or unreachable branches.
- DoS without clear amplification, or purely theoretical issues with no reachable
  path from untrusted input.
- Missing hardening headers/config unless the diff introduced a concrete exposure.
- Style, naming, or non-security correctness — that's `code-reviewer`'s lane.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's an internal / admin-only endpoint." | Internal auth is bypassed and abused too; IDOR & priv-esc are exactly here. Check authz anyway. |
| "The input comes from our own app." | Every client is attacker-controlled; client-side validation is not a control. Trace the server-side path. |
| "It's a tiny diff, no security code changed." | One added line can be the whole injection. A new sink on an old tainted path is new exposure. Review it. |
| "We'll do a security pass before launch." | This diff ships now. Review now, not against a launch that may never get a pass. |
| "It's probably fine / low risk." | "Probably" isn't a taint analysis. Either trace the path and refute it, or report it. |

## Output

- **Findings** (most-severe first), each: `file:line` · category · severity ·
  CONFIRMED/PLAUSIBLE · one-line exploit/failure scenario (input → impact) ·
  concrete fix.
- **Checked and clean** — the sinks/categories you verified are safe, so an empty
  or short list is meaningful evidence, not silence.
- **Routed elsewhere** — anything handed to `trust-boundary-review` /
  `contract-safety` instead of reported here.
- If nothing exploitable: say so explicitly, and list what you checked.
