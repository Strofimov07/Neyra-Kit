---
name: launch-ops-baseline
description: >-
  Establishes the operational floor a product needs before it has paying users:
  a probe that sits outside what it watches, expiry alerts, one alert channel
  with one line per failure, a rehearsed restore, and a named owner. Use before
  first sale and on a recurring cadence after.
when_to_use: >-
  Use before a product starts carrying real users or revenue, when it moves to
  its own infrastructure, and as a recurring readiness pass — not on every diff.
tools: Read, Grep, Glob, Bash
---

# Launch ops baseline

## Goal

Reach the floor below which an outage is discovered by a customer. Each item
here is cheap to build before launch and expensive to retrofit during an
incident.

Hosts, channels, schedules, and thresholds are **project facts**: keep them in
`settings/facts/` in the consuming repo.

## Protocol

### 1. Probe from outside what it watches

- A check running on the same host as the service cannot report that the host is
  gone. Put at least one probe on independent infrastructure, hitting the same
  entry point a user does.
- The probe exercises a real path — one that touches the app and its data — not
  a static file that a stale cache can serve.

**Success criteria**
- One probe runs off-host against a real path, and its failure is observed.

### 2. Alert on predictable expiries

- Certificates, domains, credentials, and paid quotas expire on a known date.
  Alert with enough lead time to act, not on the day.

**Success criteria**
- Each expiring asset has an alert with a stated lead time.

### 3. One channel, one line per failure

- Alerts land where a human actually looks. A failure produces exactly one
  canonical line — duplicates train people to ignore the channel, and a silenced
  channel is the same as no monitoring.
- Every alert says what broke, where, and what to do or look at next.

**Success criteria**
- A test failure produced exactly one actionable message in the channel.

### 4. Rehearse the restore, do not just take backups

- "Backups exist" is not a recovery capability. Restore into a scratch
  environment, measure how long it took, and record what was missing.
- Verify the schedule runs on its own, the retention is what you think, and the
  restore credentials are reachable by whoever will be awake.

**Success criteria**
- A restore was performed end to end, with a recorded duration and gaps.

### 5. Name the owner and the reachability path

- Who receives the alert outside working hours, and on what device. An alert
  routed to an unread inbox is decoration.

**Success criteria**
- The owner is named and confirmed reachable through the actual channel.

### 6. State the blast radius of a single failure

- List what shares a host, a database, a network path. When a component is
  shared between environments, note that a staging mistake can take production
  with it.

**Success criteria**
- The shared components are enumerated, with the worst-case scope stated.

### 7. Re-run on a cadence

- Infrastructure drifts: probes decay, schedules stop, channels get muted. Set a
  recurring pass and treat its findings as work, not as a status report.

**Success criteria**
- The cadence exists and the last run has a date.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "We have monitoring on the server." | On-host monitoring dies with the host. Probe from outside (step 1). |
| "The dashboard would show it." | Dashboards need a viewer; incidents happen while nobody looks. Push one alert (step 3). |
| "Backups are configured." | Configured is not restored. Rehearse it and time it (step 4). |
| "The certificate auto-renews." | Auto-renewal fails silently more often than certificates expire loudly. Alert on the date (step 2). |
| "I'd notice quickly." | Not while asleep, and not while travelling. Name the reachability path (step 5). |
| "Staging is isolated." | Verify it — shared hosts and shared data stores are common and invisible in code (step 6). |

## Output

- The probe, where it runs from, and the path it exercises.
- Expiry alerts with lead times, and the alert channel's one-line-per-failure proof.
- The restore rehearsal: duration, gaps, schedule, retention.
- The owner, the reachability path, and the blast radius.
