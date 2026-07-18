# Evolving the kit — operational how-to

`kit-evolution` decides **what** to change and **whether** it's a durable pattern.
This file is the **how**: the exact mechanics of landing a change in the kit and
propagating it to consumer repos. If you are about to edit a skill, rule, or hook,
read this first.

## 1. Where the kit lives — source vs. synced copy

- **Canonical editable source:** `git@github.com:Strofimov07/Neyra-Kit.git` —
  this repo. Before editing, require both its marker and Git origin:
  `python3 agents/neyra-dev-kit/source-policy.py --require-canonical`.
- **Editable paths here:** `agents/dev-skills/<id>/SKILL.md`,
  `.claude/agents/<id>.md` (portable subagents), `agents/neyra-dev-kit/` (tooling,
  manifests, governance, VERSION, hooks).
- **Installed copy in a consumer repo (do NOT hand-edit):** `<repo>/agents/dev-skills/`
  and `<repo>/.claude/agents/` are written by `install.sh`. Its `rsync --delete`
  **overwrites** them — any hand-edit in a consumer repo is lost on the next
  install. Consumer roots carry `.neyra-dev-kit.source`, never the canonical
  marker. Route the signal and fix to Neyra-Kit, then upgrade the consumer from
  a reviewed canonical revision.

## 2. Add or change a skill

1. Create/edit `agents/dev-skills/<id>/SKILL.md` (frontmatter `name` /
   `description` / `when_to_use` / `tools` / `model`, then `## Goal` and
   `## Protocol` steps each with **Success criteria**; see `SKILL_CONTRACT.md`).
2. If it ships as an auto-invocable subagent, add the portable wrapper
   `.claude/agents/<id>.md` (short: frontmatter + `Reference:
   agents/dev-skills/<id>/SKILL.md` + condensed Protocol/Rules/Output).
3. Register it: add `<id>` to `PORTABLE_AGENTS` in `manifests/dev.sh` (or the
   right kit manifest) **and** add a row to the skill↔subagent table in
   `AGENTS.devkit.md`.
4. If it's a templated subagent (repo-specific values), add it to
   `TEMPLATED_AGENTS` instead and use `{{TOKENS}}`.

## 3. Add or change a rule / governance

- Session-start rules go in `KIT_BOOTSTRAP.md` (compact, imperative — injected
  every session). Keep new rules to a few lines.
- Skill↔subagent map + gate/transparency rules live in `AGENTS.devkit.md`.
- **Behavior-changing rule / governance edits need human sign-off** — propose the
  diff, do not self-merge (see `kit-evolution` step 4).

## 4. Version + decision record

- Append the signal to `signals.log` before routing it. The ledger exists only
  in the canonical repo; consumers file/link the signal in the Neyra Skills Kit
  Linear project instead of editing their generated kit tree.
- Bump `agents/neyra-dev-kit/VERSION` (semver): **minor** for a new skill or new
  rule (new observable behaviour), **patch** for a bug fix or prose-only change.
- Update the literal `<!-- kit-version: X.Y.Z -->` footer in `AGENTS.devkit.md`.
- Append a `decisionLog.md` entry (`## DATE — <decision>` + **Context** /
  **Decision** / **Consequence**) — the *why*; Linear holds the *what/when*.

## 5. Validate before install

From `agents/neyra-dev-kit/`:

```bash
python3 lint-skills.py ../../agents/dev-skills    # frontmatter + structure
python3 lint-scope.py                             # generic layers carry zero project facts
python3 lint-plans.py                             # plan-format checks (if touched)
python3 check-skill-mapping.py                    # map ↔ manifest ↔ skills, no drift
bash doctor.sh                                    # overall status
```

## 6. Re-install into a consumer repo

```bash
./install.sh dev <repo-path> <repo-path>/settings/configs/<repo>.sh
# (examples for new consumers: configs/_growth.example.sh / _product.example.sh)
# --dry-run first; --doctor for a no-write status check. Idempotent; writes .bak.
```

After install, validate in the consumer repo with `agents/neyra-dev-kit/doctor.sh`
and `check-skill-mapping.py` (consumer-mode relaxes orphan/full-table checks).

> **CAUTION — never re-install over a dirty consumer tree.** `install.sh`'s
> `rsync --delete` rewrites `agents/dev-skills/` and `.claude/agents/`. If the
> consumer repo has uncommitted work (including a *parallel agent's* WIP), those
> files can be deleted. Commit/push every lane's WIP first, then install. See the
> `parallel-lanes` skill.

## 7. Release from the canonical repository

[github.com/Strofimov07/Neyra-Kit](https://github.com/Strofimov07/Neyra-Kit)
is both the authoring source and the install source. A kit change is ready only
after its branch passes the canonical checks and a reviewable PR is open here:

```bash
python3 agents/neyra-dev-kit/source-policy.py --require-canonical
bash agents/neyra-dev-kit/doctor.sh
git push -u origin <branch>
# open a PR against Neyra-Kit/main; merge remains a human decision
```

`publish.sh` is a fail-closed compatibility tombstone. Do not recreate a
product-repo → Neyra-Kit sync path. Consumer rollout is a separate install or
upgrade task after the canonical revision is reviewed.

## 8. Anti-drift invariants

- One source of truth per fact; consumer copies are generated, never authored.
- Canonical marker + canonical Git origin are both required for shared authoring.
- Generic layers (`dev-skills/`, `product-skills/`) carry zero project facts —
  facts live in `settings/` (`lint-scope.py` enforces; see `settings/README.md`).
- Consumers record the exact source in `.neyra-dev-kit.source`; the canonical
  repo carries `.neyra-kit-canonical` and never a consumer stamp.
- The skill↔subagent table is hand-written but CI-checked (`check-skill-mapping.py`).
- One change = one branch = one PR (`pr-hygiene`); for simultaneous agents,
  isolate lanes (`parallel-lanes`).
