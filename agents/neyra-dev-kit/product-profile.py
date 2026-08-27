#!/usr/bin/env python3
"""Read settings/product.yml and report which kit gates this product requires.

A product declares what it *is*; the kit answers which disciplines are not
optional for it and which project-fact files must exist to make them real. This
is what stops the second product in a workspace from rebuilding the first
product's hard-won discipline from scratch.

Deliberately a minimal flat-key reader, not a YAML implementation: the profile
is a short list of booleans and one list, and depending on a YAML library would
put a package install between a repo and its gates.

A declaration with no freshness contract rots exactly like a runbook naming a
decommissioned host: the flags stay as someone typed them the day the repo was
young, the gates they imply stay off, and nothing says a word. So the profile
also carries a review date, and this tool reads the code back to see whether the
declaration still matches what the repository actually contains.

Usage: product-profile.py [repo] [--strict] [--seed] [--skip-agents]
  --strict:      missing profile, missing fact files, a stale review, or an
                 undeclared capability found in the code exit non-zero.
  --skip-agents: machine-readable list of the conditional subagents this profile
                 switches off, consumed by install.sh so a declaration actually
                 selects what gets installed instead of only reporting it.
"""
import argparse
import os
import re
import sys

# flag -> (skills it makes mandatory, project files those skills read)
GATES = [
    ("generates_claims", ["grounding-gate", "eval-baseline"], ["settings/facts/grounding.md"]),
    ("retrieval",        ["retrieval-review"],                ["settings/facts/retrieval.md"]),
    ("metered_apis",     ["llm-cost-guard"],                  []),
    ("personal_data",    ["data-inventory"],                  []),
    ("long_jobs",        ["long-job-discipline"],             ["settings/facts/long-jobs.md"]),
    ("sells",            ["launch-compliance"],               []),
    ("in_production",    ["launch-ops-baseline", "incident-runbook"], ["settings/facts/incident-runbook.md"]),
    # Properties that predate the launch layer. Their gates used to install
    # everywhere: a repo with no migrations still got migration-safety, a repo with
    # no UI still got design-system-conformance. Same problem the profile exists for.
    ("db_migrations",     ["migration-safety"],                  []),
    ("user_facing_ui",    ["design-system-conformance"],         []),
    ("typed_api_contract", ["contract-doc-sync", "contract-checker"], []),
    ("analytics",         ["analytics-instrumentation"],         []),
    ("ci_cd",             ["post-merge-watch", "pr-review-watch"], []),
    ("locales",           ["localization-checker"],              []),
]

# Subagents this profile may switch OFF at install time. Deliberately restricted to
# the domain-scoped agents introduced with the launch layer (v0.40.0): each is useful
# only to a product that has the corresponding capability, and shipping it to a repo
# that does not have one adds an auto-invocable agent that can only mis-fire.
#
# Everything that predates the launch layer stays unconditional — `incident-runbook`
# appears in GATES under in_production but is a universal agent, so it is NOT here.
# The install-time answer is derived from GATES, so the flag→agent mapping cannot
# drift away from the flag→skill mapping the report prints.
CONDITIONAL_LAYER = {
    # launch layer (v0.41.0)
    "grounding-gate", "eval-baseline", "retrieval-review", "llm-cost-guard",
    "data-inventory", "long-job-discipline",
    # pre-existing agents whose relevance is also a property of the product (v0.43.0).
    # `incident-runbook` is deliberately NOT here: it predates the layer and stays
    # unconditional, as v0.41.0 decided.
    "migration-safety", "design-system-conformance", "contract-doc-sync",
    "contract-checker", "analytics-instrumentation", "post-merge-watch",
    "pr-review-watch", "localization-checker",
}
CONDITIONAL_AGENTS = {
    flag: [s for s in skills if s in CONDITIONAL_LAYER]
    for flag, skills, _files in GATES
    if any(s in CONDITIONAL_LAYER for s in skills)
}

TRUE = {"true", "yes", "on", "1"}

DEFAULT_REVIEW_AFTER_DAYS = 90

# Evidence that a capability exists in the repository, used only in the direction
# that matters: the profile says false while the code says otherwise. The reverse
# (declared true, no evidence) is not reported — a product may be days away from
# shipping the thing, and the gate being on early is the safe side.
CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".swift", ".kt", ".go", ".rb", ".java",
            ".cs", ".php", ".rs", ".sql", ".yml", ".yaml", ".toml", ".tf"}
SIGNATURES = {
    "metered_apis": (
        re.compile(r"\b(anthropic|openai|vertexai|generativeai|bedrock|cohere|mistralai|"
                   r"replicate|togetherai)\b|\b(input_tokens|prompt_tokens|completion_tokens)\b", re.I),
        None),
    "generates_claims": (
        re.compile(r"\b(system_prompt|prompt_template|chat_completion|messages\.create|"
                   r"generate_content|completion\.create)\b", re.I),
        None),
    "retrieval": (
        re.compile(r"\b(elasticsearch|opensearch|meilisearch|typesense|qdrant|weaviate|"
                   r"pinecone|pgvector|faiss|bm25|vector_store|embeddings?)\b", re.I),
        None),
    "long_jobs": (
        re.compile(r"\b(celery|sidekiq|resque|apscheduler|backfill|reindex|batch_job|"
                   r"job_queue|worker_loop)\b", re.I),
        None),
    "sells": (
        re.compile(r"\b(stripe|paddle|braintree|checkout_session|invoice|billing|"
                   r"subscription_plan|payment_intent)\b", re.I),
        None),
    "personal_data": (
        re.compile(r"\b(email|phone_number|first_name|last_name|passport|date_of_birth|"
                   r"ip_address|user_agent)\b", re.I),
        # only where a data shape is defined — the word "email" appears everywhere
        re.compile(r"(models?|schema|entity|entities|migrations?|serializers?)", re.I)),
    "db_migrations": (
        None,
        re.compile(r"(^|/)(migrations?|alembic|db/migrate|prisma/migrations)/", re.I)),
    "user_facing_ui": (
        None,
        re.compile(r"\.(tsx|jsx|vue|svelte)$|(^|/)(components?|views?|screens?|pages?)/", re.I)),
    "typed_api_contract": (
        re.compile(r"\b(openapi|swagger|drf.spectacular|extend_schema|graphql_schema|"
                   r"generated.client|zod|pydantic\.BaseModel)\b", re.I),
        None),
    "analytics": (
        re.compile(r"\b(gtag|ga4|firebase/analytics|amplitude|mixpanel|posthog|segment|"
                   r"appmetrica|track_event|logEvent)\b", re.I),
        None),
    "ci_cd": (
        None,
        re.compile(r"(^|/)(\.github/workflows|\.gitlab-ci\.yml|Jenkinsfile|\.circleci)", re.I)),
    "locales": (
        None,
        re.compile(r"\.(po|mo|xliff|arb)$|(^|/)(locales?|i18n|translations?|lang)/", re.I)),
    "in_production": (
        None,
        re.compile(r"(\.github/workflows/.*deploy|docker-compose[.-].*prod|"
                   r"(^|/)(k8s|kubernetes|helm|terraform|ansible)/)", re.I)),
}

TEMPLATE = """# Product profile — what this product IS, so the kit knows which gates apply.
# Repo-owned: the kit reads it, never rewrites it. Validate with:
#   python3 agents/neyra-dev-kit/product-profile.py
#
# Each flag turns a class of work from "someone should think about it" into a
# named gate with a place to put its facts.

name: your-product

# Money changes hands for this product (now or on a known date).
sells: false

# Markets it is sold into. Each entry needs settings/compliance/<value>.md,
# authored or reviewed by a qualified person — never by an agent.
jurisdictions: []

# Holds data about identifiable people (users, invitees, people named in
# uploaded content, staff of business customers).
personal_data: false

# Calls APIs billed per token / per request.
metered_apis: false

# Emits factual claims a user could act on (answers, summaries, advice).
generates_claims: false

# Has a search or retrieval path feeding those claims.
retrieval: false

# Runs work that outlives a request (backfills, reindexes, batch imports).
long_jobs: false

# Carries real users or revenue on infrastructure you operate.
in_production: false

# --- Properties of the codebase. Each one turns its gate on; leaving a flag out
# --- means "not answered yet", and the gate installs as it did before profiles.

# Has database schema migrations.
db_migrations: false

# Has a user-facing interface (web, mobile, desktop).
user_facing_ui: false

# Exposes an API consumed through a typed contract (schema, generated client).
typed_api_contract: false

# Emits product analytics events.
analytics: false

# Has CI/CD pipelines whose result someone must watch.
ci_cd: false

# Locales the product ships. Empty list = nothing to localize.
locales: []

# Freshness contract. A profile nobody revisits is a profile that lies:
# re-read the flags on this cadence and whenever a release turns one of them on.
# ISO date, or "unset" until the first review.
last_reviewed: unset
review_after_days: 90
"""


def parse_profile(path):
    """Flat `key: value` reader. Values: booleans, bare scalars, [a, b] lists."""
    data = {}
    for raw in open(path, encoding="utf-8", errors="ignore").read().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if not re.match(r"^[a-z_]+$", key):
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [v.strip().strip("'\"") for v in inner.split(",") if v.strip()] if inner else []
        elif val.lower() in TRUE or val.lower() in {"false", "no", "off", "0"}:
            data[key] = val.lower() in TRUE
        else:
            data[key] = val.strip("'\"")
    return data


def _tracked(root):
    import subprocess
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                             capture_output=True, text=True, check=True).stdout
        return [f for f in out.split("\0") if f]
    except Exception:
        return []


def detect_drift(root, prof):
    """Capabilities the code shows but the profile does not claim.

    Distinguishes the two cases, because they call for different fixes and the kit's
    own rule is that an absent flag is unknown, not false:
      * declared false — the declaration contradicts the repository;
      * absent — the profile predates the flag and has never been asked the question.
    Returns [(flag, declared, [paths])] where declared is "false" or "absent".
    """
    files = _tracked(root)
    if not files:
        return []
    undeclared = [f for f, _sk, _fx in GATES if not prof.get(f) and f in SIGNATURES]
    declared_as = {f: ("false" if f in prof else "absent") for f in undeclared}
    if not undeclared:
        return []
    hits = {f: [] for f in undeclared}
    for rel in files:
        low = rel.lower()
        for flag in undeclared:
            if len(hits[flag]) >= 3:
                continue
            body_re, path_re = SIGNATURES[flag]
            if body_re is None:                      # path-only signature
                if path_re.search(low):
                    hits[flag].append(rel)
                continue
            if path_re is not None and not path_re.search(low):
                continue                             # body signature scoped to matching paths
            if os.path.splitext(rel)[1] not in CODE_EXT:
                continue
            try:
                text = open(os.path.join(root, rel), encoding="utf-8", errors="ignore").read(200_000)
            except OSError:
                continue
            if body_re.search(text):
                hits[flag].append(rel)
    return [(f, declared_as[f], v) for f, v in hits.items() if v]


def skip_agents(prof):
    """Conditional subagents this profile switches off, sorted.

    Conservative by construction: a flag that is *absent* from the profile is
    unknown, not false — an older profile written before a flag existed must never
    silently uninstall the agent that flag governs. Only an explicit false skips.
    """
    off = []
    for flag, agents in CONDITIONAL_AGENTS.items():
        if flag not in prof:
            continue
        value = prof[flag]
        # `locales` is a list; an empty one is a real statement ("nothing to localize"),
        # the same way `false` is for a boolean. Both mean: this gate does not apply.
        if not value:
            off.extend(agents)
    return sorted(set(off))


def review_status(prof):
    """(state, detail) where state is 'ok' | 'unset' | 'stale' | 'unreadable'."""
    import datetime
    raw = str(prof.get("last_reviewed") or "").strip()
    if not raw or raw.lower() in {"unset", "never", "none"}:
        return "unset", "no last_reviewed date"
    try:
        reviewed = datetime.date.fromisoformat(raw)
    except ValueError:
        return "unreadable", "last_reviewed is not an ISO date: %r" % raw
    try:
        after = int(prof.get("review_after_days") or DEFAULT_REVIEW_AFTER_DAYS)
    except (TypeError, ValueError):
        after = DEFAULT_REVIEW_AFTER_DAYS
    age = (datetime.date.today() - reviewed).days
    if age > after:
        return "stale", "reviewed %s, %d days ago (cadence %d)" % (raw, age, after)
    return "ok", "reviewed %s, %d days ago (cadence %d)" % (raw, age, after)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--seed", action="store_true",
                    help="print a starter profile to stdout (redirect it into settings/product.yml)")
    ap.add_argument("--skip-agents", action="store_true",
                    help="print the conditional subagents this profile switches off, one per "
                         "line (empty when there is no profile — absent means install everything)")
    a = ap.parse_args()
    if a.seed:
        print(TEMPLATE, end="")
        return 0
    root = os.path.abspath(a.repo)
    path = os.path.join(root, "settings", "product.yml")

    if a.skip_agents:
        # Machine-readable, silent on every failure path: no profile, unreadable
        # profile, or nothing switched off all print nothing and exit 0, so a caller
        # can never mistake a broken read for "the product has no capabilities".
        if os.path.isfile(path):
            try:
                for name in skip_agents(parse_profile(path)):
                    print(name)
            except OSError:
                pass
        return 0

    if not os.path.isfile(path):
        print("no settings/product.yml — the kit cannot tell which gates this product needs.")
        print("  seed one:  python3 agents/neyra-dev-kit/product-profile.py --seed > settings/product.yml")
        return 1 if a.strict else 0

    prof = parse_profile(path)
    print("product profile: %s" % (prof.get("name") or os.path.basename(root)))

    required, missing = [], []
    for flag, skills, files in GATES:
        if not prof.get(flag):
            continue
        required.extend(skills)
        for rel in files:
            if not os.path.exists(os.path.join(root, rel)):
                missing.append((rel, flag))

    for j in prof.get("jurisdictions") or []:
        rel = "settings/compliance/%s.md" % j
        if not os.path.exists(os.path.join(root, rel)):
            missing.append((rel, "jurisdictions"))

    print("── mandatory gates for this profile")
    if required:
        for s in sorted(set(required)):
            print("  %s" % s)
    else:
        print("  none declared — every flag in the profile is false")

    print("── project facts these gates read")
    if missing:
        for rel, flag in missing:
            print("  MISSING %-40s (required by %s: true)" % (rel, flag))
        print("  a gate whose facts file is absent degrades to generic advice")
    else:
        print("  all present")

    state, detail = review_status(prof)
    print("── freshness")
    if state == "ok":
        print("  %s" % detail)
    elif state == "unset":
        print("  WARN %s — set last_reviewed (ISO date) so staleness becomes visible" % detail)
    elif state == "unreadable":
        print("  WARN %s" % detail)
    else:
        print("  STALE %s — re-read the flags against what the product does now" % detail)

    drift = detect_drift(root, prof)
    print("── declaration vs code")
    if drift:
        for flag, declared, paths in drift:
            if declared == "false":
                print("  %s: false — but the repository shows it, e.g.:" % flag)
            else:
                print("  %s: not declared — but the repository shows it, e.g.:" % flag)
            for rel in paths:
                print("      %s" % rel)
        print("  a false flag that the code contradicts is out of date; an undeclared one")
        print("  has never been answered — add it. If the evidence is incidental, say so")
        print("  in the profile's comments and set the flag deliberately.")
    else:
        print("  no undeclared capabilities found")

    failed = bool(missing) or state == "stale" or bool(drift)
    if a.strict and failed:
        print("product-profile: FAIL (--strict)")
        return 1
    print("product-profile: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
