#!/usr/bin/env python3
"""Assert the dev-skill ↔ subagent mapping has no drift (NEB-1232).

Single source of truth: the mapping is DERIVED from `.claude/agents/*.md`
(each subagent body references its source `agents/dev-skills/<skill>`), not a
hand-maintained table. Then:
  - every dev-skill must be referenced by some subagent OR be explicitly manual;
  - every referenced skill must actually exist (no dangling reference).

Exits non-zero on any violation. Pure stdlib.
"""

import os
import re
import sys

# dev-skills intentionally without an auto-invocable subagent (documented manual).
# batch-migration stays manual: it's approval-gated (only on explicit delegation).
# goal-mode is opt-in autonomous orchestration — invoked explicitly, never auto.
MANUAL = {"batch-migration", "goal-mode", "backlog-fleet"}
# Rendered per-repo by install.sh only when enabled in the consumer's config —
# keep in sync with TEMPLATED_AGENTS in manifests/*.sh.
TEMPLATED = {"linear-router", "localization-checker", "contract-checker"}

REF_RE = re.compile(r"agents/dev-skills/([a-z0-9-]+)")


def check_agents_table(root, dev_skills, agents_dir, is_consumer=False):
    """The AGENTS.md '| dev-skill | subagent |' table must match reality:
    every listed subagent exists, every dev-skill is listed, manual rows match MANUAL."""
    errs = []
    # The table lives in AGENTS.md in the canonical repo, but in a consumer repo the kit
    # renders it into AGENTS.neyra-devkit.md (or it may be in CLAUDE.md). Use the
    # first candidate that actually contains the table header.
    lines = []
    start = None
    for cand in (
        "AGENTS.md",
        "AGENTS.neyra-devkit.md",
        "agents/neyra-dev-kit/AGENTS.devkit.md",
        "CLAUDE.md",
    ):
        p = os.path.join(root, cand)
        if not os.path.isfile(p):
            continue
        ls = open(p, encoding="utf-8").read().splitlines()
        s = next(
            (
                i
                for i, ln in enumerate(ls)
                if ln.startswith("|") and "dev-skill" in ln and "subagent" in ln
            ),
            None,
        )
        if s is not None:
            lines, start = ls, s
            break
    if start is None:
        if is_consumer:
            # Published/installed consumers do not own the canonical mapping
            # table. Their shipped subagents are validated from typed file
            # references below, so absence of host governance docs is expected.
            return []
        return [
            "mapping table (| dev-skill | subagent | …) not found in AGENTS.md / AGENTS.neyra-devkit.md / CLAUDE.md"
        ]
    listed = set()
    for ln in lines[start + 2 :]:  # skip header + |---| separator
        if not ln.startswith("|"):
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        skill = cells[0].strip("`").strip()
        target = cells[1]
        listed.add(skill)
        if skill not in dev_skills:
            errs.append("AGENTS table lists unknown dev-skill '%s'" % skill)
        if target.startswith("("):  # (manual …)
            if skill not in MANUAL:
                errs.append(
                    "AGENTS table marks '%s' manual, but it's not in MANUAL" % skill
                )
        else:
            sub = target.strip("`").strip()
            if not os.path.isfile(os.path.join(agents_dir, sub + ".md")):
                template = os.path.join(
                    root,
                    "agents/neyra-dev-kit/templates/agents",
                    sub + ".md.tmpl",
                )
                if sub in TEMPLATED and (is_consumer or os.path.isfile(template)):
                    # Templated agents are rendered per consumer config. In the
                    # canonical repo the template itself is the source; in a
                    # consumer absence means the agent was disabled at install.
                    print(
                        "note: templated agent '%s' validated from its template/config"
                        % sub
                    )
                else:
                    errs.append(
                        "AGENTS table maps '%s' → '%s' but .claude/agents/%s.md is missing"
                        % (skill, sub, sub)
                    )
    if not is_consumer:
        for s in sorted(dev_skills):
            if s not in listed:
                errs.append(
                    "dev-skill '%s' is missing from the AGENTS.md mapping table" % s
                )
    return errs


def check_readme_index(root, dev_skills):
    """agents/dev-skills/README.md must list every dev-skill directory.

    This is a plain directory index, not a curated subagent surface, so it gets no
    consumer-mode relaxation. Nothing validated it before: the AGENTS table check has
    an is_consumer escape hatch and this file had no check at all, so one consumer
    drifted to 16 of 29 entries — and its AGENTS table listed a *different* 23 — with
    neither index agreeing on what it omitted.
    """
    path = os.path.join(root, "agents/dev-skills/README.md")
    if not os.path.isfile(path):
        return ["agents/dev-skills/README.md not found"]
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # Key off the link target (the skill dir), not the display text: the path is the
    # real identity, and a mislabeled link text would otherwise false-flag drift.
    listed = set(re.findall(r"^\|\s*\[[^\]]+\]\(([a-z0-9-]+)/SKILL\.md\)", text, re.M))
    if not listed:
        return ["agents/dev-skills/README.md has no skill table rows"]
    errs = [
        "agents/dev-skills/README.md is missing a row for '%s'" % s
        for s in sorted(dev_skills - listed)
    ]
    errs += [
        "agents/dev-skills/README.md lists '%s' but no such skill dir exists" % s
        for s in sorted(listed - dev_skills)
    ]
    return errs


def _repo_root():
    """Repo root from this script's own location (three parents up), so a standalone
    run from any cwd validates the same tree as doctor.sh. Falls back to cwd if the
    layout isn't recognized."""
    cand = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return cand if os.path.isdir(os.path.join(cand, "agents")) else os.getcwd()


def main():
    root = _repo_root()
    skills_dir = os.path.join(root, "agents/dev-skills")
    agents_dir = os.path.join(root, ".claude/agents")
    if not os.path.isdir(skills_dir) or not os.path.isdir(agents_dir):
        # Fail closed. Previously returned 0 ("skip"), so a standalone run from the
        # wrong cwd — where these dirs didn't resolve — passed vacuously (NEB-1486).
        # With root resolved from the script's own location, a real kit tree always
        # has both; their absence means wrong location or broken install.
        print("FAIL: agents/dev-skills and/or .claude/agents not found under %s — "
              "wrong location or broken install; refusing to pass vacuously." % root)
        return 1

    dev_skills = {
        d
        for d in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
    }

    referenced = set()
    for f in os.listdir(agents_dir):
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(agents_dir, f), encoding="utf-8").read()
        referenced.update(REF_RE.findall(text))

    templates_dir = os.path.join(root, "agents/neyra-dev-kit/templates/agents")
    if os.path.isdir(templates_dir):
        for f in os.listdir(templates_dir):
            if not f.endswith(".md.tmpl"):
                continue
            text = open(os.path.join(templates_dir, f), encoding="utf-8").read()
            referenced.update(REF_RE.findall(text))

    # In a consumer repo (kit installed via install.sh) skills are copied wholesale
    # but only a curated subset of subagents is — so "orphan skill" and "every skill
    # must be in the table" are expected, not drift. Detect the consumer by the
    # canonical source stamp and absence of the canonical marker. Version alone is
    # insufficient: the canonical repo also carries VERSION metadata and must stay
    # strict rather than silently relaxing its authoring checks.
    is_consumer = os.path.isfile(
        os.path.join(root, ".neyra-dev-kit.source")
    ) and not os.path.isfile(os.path.join(root, ".neyra-kit-canonical"))

    errs = []
    # 1. orphan dev-skills (no subagent, not manual) — canonical repo only
    if not is_consumer:
        for s in sorted(dev_skills):
            if s not in referenced and s not in MANUAL:
                errs.append(
                    "orphan dev-skill '%s' — add a .claude/agents subagent that "
                    "references it, or add it to MANUAL in check-skill-mapping.py" % s
                )
    # 2. dangling references (subagent points at a non-existent skill) — always
    for r in sorted(referenced):
        if r not in dev_skills:
            errs.append(
                "dangling reference 'agents/dev-skills/%s' in a subagent — "
                "skill dir does not exist" % r
            )
    # 3. MANUAL entries that no longer exist — canonical repo only
    if not is_consumer:
        for m in sorted(MANUAL):
            if m not in dev_skills:
                errs.append(
                    "MANUAL lists '%s' but the dev-skill is gone — update MANUAL" % m
                )

    # 4. mapping table must match reality (relaxed in a consumer).
    errs += check_agents_table(root, dev_skills, agents_dir, is_consumer)

    # 5. README is a plain directory index — always checked, no consumer relaxation.
    errs += check_readme_index(root, dev_skills)

    if errs:
        print("FAIL skill↔subagent mapping:")
        for e in errs:
            print("   ✗ %s" % e)
        return 1
    mode = " [consumer mode: orphan/table checks relaxed]" if is_consumer else ""
    print(
        "ok: %d dev-skills — %d mapped to subagents, %d manual%s"
        % (
            len(dev_skills),
            len(dev_skills) - len(MANUAL & dev_skills),
            len(MANUAL & dev_skills),
            mode,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
