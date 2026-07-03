---
name: incident-runbook
description: >-
  Diagnose and contain known production incidents from a runbook of encoded
  failure modes, with containment/rollback steps and escalation. Use during a
  production incident, on-call triage, or when a known failure signature recurs.
when_to_use: >-
  Use when a production system is degraded or alerting, when triaging an on-call
  page, or when a previously-seen failure mode (disk fill, false-unhealthy
  service) reappears.
---

# Incident runbook

## Goal

Contain the incident fast using known signatures; don't rediscover root cause from scratch.

## Known failure modes

Failure signatures are per-project facts, not protocol — they live in
`settings/facts/incident-runbook.md` in the consuming repo (create it on the
first incident via `skill-capture`). Read that file first; if it doesn't exist,
treat every mode as new and start capturing. Example entry shape:

- **<signature name>** — symptom → observed cause. Containment: <the fastest
  safe action>; <the monitoring/hardening follow-up to file>.

## Steps

1. **Identify the signature** — match symptoms against `settings/facts/incident-runbook.md` before deep debugging.
2. **Contain** — apply the documented containment for that mode (verify before any blind restart).
3. **Verify recovery** — confirm the real signal (the surface users hit), not just the healthcheck.
4. **Capture** — if it is a NEW mode, append it to `settings/facts/incident-runbook.md` via `skill-capture` and file a hardening task.

## Success criteria

- incident matched to a known mode (or explicitly flagged new)
- containment applied and recovery verified on the real signal
- any new mode captured back into the facts file

## Non-goals

Long-term hardening (file a separate task) and feature work.

## Verification

The degraded signal recovers on the real surface; a new failure mode is appended to `settings/facts/incident-runbook.md`.
