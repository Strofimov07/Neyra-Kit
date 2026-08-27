#!/usr/bin/env python3
"""Read settings/product.yml and report which kit gates this product requires.

A product declares what it *is*; the kit answers which disciplines are not
optional for it and which project-fact files must exist to make them real. This
is what stops the second product in a workspace from rebuilding the first
product's hard-won discipline from scratch.

Deliberately a minimal flat-key reader, not a YAML implementation: the profile
is a short list of booleans and one list, and depending on a YAML library would
put a package install between a repo and its gates.

Usage: product-profile.py [repo] [--strict]
  --strict: missing profile or missing required fact files exit non-zero.
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
]

TRUE = {"true", "yes", "on", "1"}

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--seed", action="store_true",
                    help="print a starter profile to stdout (redirect it into settings/product.yml)")
    a = ap.parse_args()
    if a.seed:
        print(TEMPLATE, end="")
        return 0
    root = os.path.abspath(a.repo)
    path = os.path.join(root, "settings", "product.yml")

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

    if a.strict and missing:
        print("product-profile: FAIL (--strict)")
        return 1
    print("product-profile: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
