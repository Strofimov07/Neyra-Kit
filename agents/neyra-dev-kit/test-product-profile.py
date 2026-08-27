#!/usr/bin/env python3
"""Regressions for product-profile.py: gates, freshness, and declaration-vs-code drift.

The drift check is the one that must not rot: it exists because a profile written
once and never revisited silently turns gates off. A test that only asserts the
happy path would let that regress unnoticed.
"""
import datetime
import os
import pathlib
import subprocess
import sys
import tempfile

TOOL = pathlib.Path(__file__).parent / "product-profile.py"
FAILURES = []


def check(cond, label):
    print(("ok: " if cond else "FAIL: ") + label)
    if not cond:
        FAILURES.append(label)


def run(repo, *args):
    r = subprocess.run([sys.executable, str(TOOL), repo, *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def make_repo(profile, files=None):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    os.makedirs(os.path.join(d, "settings"), exist_ok=True)
    pathlib.Path(d, "settings", "product.yml").write_text(profile, encoding="utf-8")
    for rel, body in (files or {}).items():
        p = pathlib.Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    return d


ALL_FALSE = """name: t
sells: false
jurisdictions: []
personal_data: false
metered_apis: false
generates_claims: false
retrieval: false
long_jobs: false
in_production: false
last_reviewed: {today}
review_after_days: 90
""".format(today=datetime.date.today().isoformat())

# 1. no profile at all
d = tempfile.mkdtemp()
subprocess.run(["git", "-C", d, "init", "-q"], check=True)
code, out = run(d)
check(code == 0 and "no settings/product.yml" in out, "missing profile reports and does not fail by default")
code, _ = run(d, "--strict")
check(code == 1, "missing profile fails under --strict")

# 2. clean profile, nothing declared, nothing in the code
d = make_repo(ALL_FALSE)
code, out = run(d)
check(code == 0 and "no undeclared capabilities found" in out, "empty repo shows no drift")
check("reviewed" in out and "days ago" in out, "fresh review date is reported as such")

# 3. drift: the code shows a metered API the profile denies
d = make_repo(ALL_FALSE, {"src/client.py": "import anthropic\nclient = anthropic.Anthropic()\n"})
code, out = run(d)
check("metered_apis: false" in out and "src/client.py" in out, "metered_apis drift is detected and located")
code, _ = run(d, "--strict")
check(code == 1, "drift fails under --strict")

# 4. drift direction: declared true with no evidence is NOT reported
d = make_repo(ALL_FALSE.replace("metered_apis: false", "metered_apis: true"))
code, out = run(d)
check("metered_apis" not in out.split("── declaration vs code")[1], "declared-true-without-evidence is not reported")

# 5. personal_data signature is scoped to data-shape files
d = make_repo(ALL_FALSE, {"docs/support.md": "write to email support\n"})
code, out = run(d)
check("personal_data: false" not in out, "prose mentioning email does not trip personal_data")
d = make_repo(ALL_FALSE, {"src/models.py": "class User:\n    email: str\n"})
code, out = run(d)
check("personal_data: false" in out, "a model field does trip personal_data")

# 6. staleness
stale = ALL_FALSE.replace(datetime.date.today().isoformat(),
                          (datetime.date.today() - datetime.timedelta(days=200)).isoformat())
d = make_repo(stale)
code, out = run(d)
check("STALE" in out, "an old review date is reported stale")
code, _ = run(d, "--strict")
check(code == 1, "stale review fails under --strict")

d = make_repo(ALL_FALSE.replace("last_reviewed: %s" % datetime.date.today().isoformat(),
                                "last_reviewed: unset"))
code, out = run(d)
check("WARN no last_reviewed date" in out, "unset review date warns")

# 7. --skip-agents: what the installer consumes
d = make_repo(ALL_FALSE)
code, out = run(d, "--skip-agents")
off = set(out.split())
check(code == 0 and off == {"grounding-gate", "eval-baseline", "retrieval-review",
                            "llm-cost-guard", "data-inventory", "long-job-discipline"},
      "all-false profile switches off exactly the conditional layer")
check("incident-runbook" not in off,
      "an agent that predates the launch layer is never switched off")

d = make_repo(ALL_FALSE.replace("generates_claims: false", "generates_claims: true"))
code, out = run(d, "--skip-agents")
off = set(out.split())
check("grounding-gate" not in off and "eval-baseline" not in off,
      "a true flag keeps both of its agents")
check("retrieval-review" in off, "unrelated flags stay off")

# absent flag != false: an older profile must not silently uninstall an agent
partial = "name: t\nsells: false\n"
d = make_repo(partial)
code, out = run(d, "--skip-agents")
check(code == 0 and out.strip() == "",
      "a profile that does not mention a flag switches nothing off")

dd = tempfile.mkdtemp()
subprocess.run(["git", "-C", dd, "init", "-q"], check=True)
code, out = run(dd, "--skip-agents")
check(code == 0 and out.strip() == "", "no profile switches nothing off (install everything)")

# 8. --seed emits a profile this tool can read back
r = subprocess.run([sys.executable, str(TOOL), "--seed"], capture_output=True, text=True)
d = make_repo(r.stdout)
code, out = run(d)
check(code == 0 and "product profile:" in out, "--seed output parses as a profile")
check("last_reviewed" in r.stdout and "review_after_days" in r.stdout, "seed carries the freshness contract")

print("")
if FAILURES:
    print("test-product-profile: %d FAILURE(S)" % len(FAILURES))
    sys.exit(1)
print("test-product-profile: all passed")
