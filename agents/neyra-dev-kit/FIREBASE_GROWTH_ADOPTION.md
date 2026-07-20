# Firebase growth adoption guide

Use this guide when a Neyra product adopts the official Firebase MCP for
administration, Remote Config, Crashlytics, or experiment operations. It is a
shared execution contract, not a product event catalog. Project IDs, credentials,
event names, Remote Config keys, metrics, and rollback evidence remain owned by
the consumer repository.

## Readiness states

Never collapse these states into a single “Firebase is done” claim:

| State | Evidence required |
|---|---|
| Tool-ready | Firebase MCP is installed, authenticated, authorized by IAM, and its expected tools are discoverable. |
| Contract-ready | The product owns an event catalog, payload/privacy rules, destinations, owners, Remote Config key registry, and safe defaults. |
| Measurement-verified | A real runtime event is observed in every declared measurement destination with correlation evidence. |
| Experiment-ready | Eligible builds, assignment denominator, guard metrics, exact template diff, approval, observation window, and rollback are recorded. |
| Experiment-live | The approved template and experiment are active, the client assignment is observed, and monitoring is running. |

Tool-ready is necessary but does not prove analytics delivery, production revenue,
or a live experiment.

## Ownership boundary

The canonical Neyra Kit owns:

- the opt-in Firebase MCP template;
- limited and full access profiles;
- install, doctor, and regression coverage;
- this reusable adoption and safety workflow.

Each consumer owns:

- `settings/firebase/firebase.json` and its Firebase project binding;
- its selected access profile and IAM identity;
- event and metric contracts;
- Remote Config parameters, conditions, safe defaults, and release eligibility;
- production measurement evidence and rollback artifacts.

Do not put product IDs, credentials, customer data, or product-specific experiment
values in the Kit.

## 1. Bind the consumer

Create a credential-free Firebase directory in the consumer and select an
explicit profile in its Kit config:

```bash
ENABLE_FIREBASE_MCP=1
FIREBASE_PROJECT_DIR="settings/firebase"
FIREBASE_MCP_ACCESS="limited"
FIREBASE_MCP_TOOLS="firebase_read_resources,remoteconfig_get_template,crashlytics_get_report"
```

`limited` is the reusable default and uses the exact tool allowlist. Use `full`
only when the operator owns the complete Firebase surface and the consumer lists
the intended feature groups in `FIREBASE_MCP_FEATURES`.

From the canonical Kit checkout, inspect before installing:

```bash
bash agents/neyra-dev-kit/install.sh --doctor growth <consumer-path> <consumer-config.sh>
bash agents/neyra-dev-kit/install.sh --dry-run growth <consumer-path> <consumer-config.sh>
```

Install only into a clean consumer tree. After installation, verify that the
consumer source stamp points to the reviewed canonical revision.

## 2. Authenticate and verify authority

Use an interactive Firebase CLI login on a workstation or Application Default
Credentials in a headless environment. Do not commit a service-account key or use
legacy `FIREBASE_TOKEN` authentication.

```bash
npx -y firebase-tools@latest login
npx -y firebase-tools@latest projects:list
```

Grant only the IAM roles needed by the selected tools. Remote Config inspection
needs viewer authority; publishing needs admin authority. A discovered MCP tool
does not bypass IAM and is not blanket permission to execute a side effect.

Record tool-ready evidence:

- authenticated identity type;
- target Firebase project;
- selected `limited` or `full` profile;
- discovered tool names or feature groups;
- missing IAM permissions;
- date and operator.

## 3. Define the measurement contract

Before changing Remote Config or starting an experiment, define:

| Field | Required content |
|---|---|
| Product outcome | The decision the team wants to make. |
| Observable proxy | The closest runtime behavior that can actually be measured. |
| Event map | Trigger, success, failure/cancel/fallback, payload, destination, and owner. |
| Correlation | A stable event or transaction identifier shared across declared destinations. |
| Guard metrics | Reliability, latency, crash, refund, or trust regressions that can stop the rollout. |
| Observation window | Cohort maturity and the earliest valid decision time. |
| Blind spot | What the available data cannot prove. |

Prefer standard GA4 ecommerce or promotion events when their semantics match.
Product-specific events still need a product-owned naming convention. Never send
raw prompts, response text, full URLs, page contents, credentials, customer data,
or localized error messages as analytics properties.

Firebase MCP is a control plane. GA4, BigQuery, a backend event mirror, or another
declared store is the measurement plane. Define which system owns each event so a
server-authoritative event is not double-counted by a client mirror.

## 4. Define the Remote Config contract

For every parameter, record:

- type and allowed values;
- safe local default when fetch or activation fails;
- owning product capability;
- eligible app version/build and release channel;
- assignment event and denominator;
- experiment identifier and arm field;
- rollback value or previous template version.

An assignment denominator must represent eligible assigned identities. A paywall
view, screen impression, or later conversion event is not a valid denominator
unless the experiment explicitly assigns at that point.

Before publishing:

1. Read the active template and record its current version.
2. Preserve unrelated parameters, conditional values, and condition ordering.
3. Produce the exact full-template diff.
4. Confirm eligible released builds use the declared safe defaults.
5. Name guard metrics, owner, observation window, and rollback version.
6. Obtain explicit approval for the target and visible side effect.
7. Publish through an ETag-aware path.

If the MCP response does not expose the active ETag, use an ETag-aware Firebase
CLI deployment. Do not silently convert a failed non-forced update into a forced
write.

## 5. Verify the real measurement path

Contract tests prove shape; they do not prove production delivery. Exercise a
real build and capture:

1. the runtime trigger in the product;
2. the event in Firebase DebugView or the declared Firebase destination;
3. the same correlation identifier in the backend mirror when one is declared;
4. the event in GA4 reporting after processing;
5. verified purchase/revenue data for monetization flows;
6. BigQuery or another reproducible cohort source when longitudinal analysis is
   required;
7. failure/cancel/fallback and guard-metric visibility.

Mark absent destinations as blocked or intentionally out of scope. Never report
measurement-verified from an event catalog, SDK call, or MCP read alone.

## 6. Activate and monitor

An experiment can move from experiment-ready to experiment-live only when:

- the reviewed template has been published to the named project;
- eligible builds fetch and activate the expected assignment;
- assignment events appear in the measurement plane;
- dashboards use the registered identity/cohort denominator;
- guard metrics and rollback ownership are visible;
- the team respects the pre-registered observation window and avoids unplanned
  early peeking.

After activation, re-read the active template, record the resulting version, and
retain the previous version as the rollback target. Publishing a template and
proving outcomes remain separate checks.

## Consumer completion record

A consumer adoption summary is complete when it reports each state separately:

```text
tool-ready: yes|no — evidence
contract-ready: yes|no — catalog and key registry
measurement-verified: yes|no — runtime destinations and correlation
experiment-ready: yes|no — reviewed diff, approval, window, rollback
experiment-live: yes|no — active assignment and monitoring
known gaps: explicit blocked or manual gates
```

This record belongs in the consumer repository or canonical product workspace,
not in the shared Kit.
