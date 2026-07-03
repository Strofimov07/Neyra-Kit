# Evolving the kit — operational how-to

`kit-evolution` decides **what** to change and **whether** it's a durable pattern.
This file is the **how**: the exact mechanics of landing a change in the kit and
propagating it to consumer repos. If you are about to edit a skill, rule, or hook,
read this first.

## 1. Where the kit lives — source vs. synced copy

- **Editable source (edit here):** this repo — `agents/dev-skills/<id>/SKILL.md`,
  `.claude/agents/<id>.md` (portable subagents), `agents/neyra-dev-kit/` (tooling,
  manifests, governance, VERSION, hooks).
- **Synced copy in a consumer repo (do NOT hand-edit):** `<repo>/agents/dev-skills/`
  and `<repo>/.claude/agents/` are written by `install.sh`. Its `rsync --delete`
  **overwrites** them — any hand-edit in a consumer repo is lost on the next
  install. Fix the source here, then re-install.

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
./install.sh dev <repo-path> "$MONOREPO/settings/configs/<repo>.sh"   # e.g. settings/configs/pravo.sh
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

## 7. Publish to the external kit repo — part of the change, not a follow-up

The monorepo is the canon; [github.com/Strofimov07/Neyra-Kit](https://github.com/Strofimov07/Neyra-Kit)
is the published artifact consumers outside the monorepo install from. **Every
VERSION bump ends with a publish** — a kit change is not done until internal and
external carry the same version:

```bash
./publish.sh <path-to-neyra-kit-clone>   # --dry-run first
# gate: lint-scope.py runs inside — a project fact in a generic layer blocks it
git -C <path-to-neyra-kit-clone> push
```

If you cannot publish in the same sitting (no clone at hand), file it — don't
let the repos drift silently. `kit-evolution` step 4 carries the same rule.

## 8. Anti-drift invariants

- One source of truth per fact; consumer copies are generated, never authored.
- Generic layers (`dev-skills/`, `product-skills/`) carry zero project facts —
  facts live in `settings/` (`lint-scope.py` enforces; see `settings/README.md`).
- Internal VERSION == external VERSION after every kit change (`publish.sh`).
- The skill↔subagent table is hand-written but CI-checked (`check-skill-mapping.py`).
- One change = one branch = one PR (`pr-hygiene`); for simultaneous agents,
  isolate lanes (`parallel-lanes`).
