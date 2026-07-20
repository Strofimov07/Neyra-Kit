# neyra-dev-kit

Portable engineering skill stack for **every Neyra-adjacent repo** (TradingCoreModules, Pravo, Tea Farm, Britanika, News Bot, …). Write the development discipline once here; inherit it everywhere.

## What it ships

**Layer A — portable (copied verbatim).** Works in any repo unchanged:
- all `agents/dev-skills/` SKILL.md — the full engineering catalogue (implement / verify / gate, contracts, release, spec + plan, debugging, orchestration). Run `kit doctor` or see the skill↔subagent map in `AGENTS.devkit.md` for the current list.
- the portable subagents in `.claude/agents/` (the auto-invocable surface for those skills — see the `AGENTS.devkit.md` map)

**Layer B — templated (rendered per repo).** Encode each repo's conventions via config:
- `linear-router` — the repo's Linear projects + routing table
- `localization-checker` — the repo's required locales + i18n mechanism
- `contract-checker` — the repo's typed-contract convention

**Governance fragment** — `AGENTS.neyra-devkit.md`: the skill↔subagent map, the transparency rule (name the active skill each step in `/loop`/autonomous runs), and the post-implementation gate. Include it from the target repo's `AGENTS.md` / `CLAUDE.md`.

**MCP layer** — wires opt-in project-scoped servers into the repo's `.mcp.json` via jq deep-merge (existing servers preserved). The Neyra bridge uses `${ENV}` placeholders; the official Firebase growth connector uses Firebase CLI login or Application Default Credentials and stores no credential in the repo. Global MCPs (Linear, Notion, Figma) remain user-level. Toggle per repo with `ENABLE_NEYRA_MCP` and `ENABLE_FIREBASE_MCP`.

## Why this design
- **Single source of truth.** The canonical skills/subagents live in this standalone Neyra-Kit repository; the installer copies from them, so there are no vendored duplicates to drift. Re-run install to refresh.
- **Two layers.** Generic discipline is shared as-is; repo-specific conventions live in a small per-repo config, not forked files.

## Kits
The engine is manifest-driven (`manifests/<kit>.sh`); install any kit with `install.sh <kit> <repo> <config>` (default kit `dev`).

| Kit | Skills | Subagents | For |
|---|---|---|---|
| **dev** | all `agents/dev-skills/*` (engineering: implement/verify/gate, contracts, release, spec+plan, debug, orchestration) | portable subagents in `.claude/agents/` (see `AGENTS.devkit.md` map) + Layer-B | engineers building any repo |
| **product** | research-insights / discovery / solution-design / delivery-planning / knowledge-memory profiles | product-brainstormer, solution-designer, delivery-planner (+ linear-router) | PM / discovery work |
| **growth** | growth-analytics / aso / finance-business-impact profiles | growth-analytics, analytics-instrumentation (+ linear-router) | growth / ASO work |

**The core is MCP-independent.** Every kit's core = skills + subagents + governance and installs with **no MCP** (`ENABLE_NEYRA_MCP=0` and `ENABLE_FIREBASE_MCP=0` in example configs; verified). MCP is an **additive** layer of extra data/capabilities — opt in per repo, never required for the core to work. The Firebase connector exposes Remote Config and Crashlytics growth operations; GA4/BigQuery remains a separate measurement source.

## Multi-tool surfaces (Claude Code + Cursor + Codex)
`SKILL.md` is an open standard read by all three tools, and each exposes
SessionStart/PreToolUse/PostToolUse/Stop hooks — so the kit installs a near-identical
setup in each, from **one** canonical content layer:

| Surface | Claude Code | Cursor | Codex |
|---|---|---|---|
| Skills | `.claude/agents/*` | `.cursor/skills/` | `.agents/skills/` |
| Hooks | `.claude/settings.json` | `.cursor/hooks.json` | `.codex/hooks.json` |
| Bootstrap | SessionStart hook | always-apply `.cursor/rules/*.mdc` | AGENTS.md + SessionStart |

The four hook scripts are shared bash; `hooks/lib/host-io.sh` translates each tool's
stdin payload and block protocol, keyed by `NEYRA_HOOK_HOST` (unset = Claude Code, so
that surface is unchanged). Toggles: `ENABLE_CURSOR_HOOKS`, `ENABLE_CODEX` (default on).
Claude Code stays the richest surface (subagents + maturest hooks). The Codex
`hooks.json` uses the current nested lifecycle schema. Codex requires each new or
changed project hook definition to be reviewed and trusted in `/hooks` before it runs.

## Install into a repo
```bash
# 1. write a config for the repo (see configs/*.sh for examples)
cp configs/pravo.sh configs/<repo>.sh && $EDITOR configs/<repo>.sh

# 2. dry-run to preview, then install
agents/neyra-dev-kit/install.sh --dry-run /path/to/<repo> configs/<repo>.sh
agents/neyra-dev-kit/install.sh           /path/to/<repo> configs/<repo>.sh

# 3. in <repo>/AGENTS.md (or CLAUDE.md) add:
#    See [AGENTS.neyra-devkit.md](AGENTS.neyra-devkit.md) for the shared skill stack.
```
Idempotent — re-running overwrites only kit-managed files and bumps `.neyra-dev-kit.version`.

## Config fields
See [config.example.yml](config.example.yml) for the documented field list; the real config is a sourced shell file (`configs/<repo>.sh`) so multi-line routing tables work without extra deps.

## Sharing with someone else
Most of the kit works for anyone with **zero setup** — the dev-skills and 9 of the 10 subagents use only `Read/Grep/Glob/Bash` (no accounts, no Notion, no Linear).

The one exception is **`linear-router`**, which calls a Linear MCP whose tool ids are per-user. So before sharing:
- The recipient sets `LINEAR_MCP_PREFIX` in their config to **their own** Linear MCP id (find it in Claude Code via `/mcp`). If they leave it empty, `linear-router` is simply skipped — nothing breaks.
- **Notion is not required** by the kit at all.

Run `install.sh --doctor <repo> <config.sh>` to print exactly which components work out-of-the-box and which need external setup, before installing.

For Firebase growth operations, set `ENABLE_FIREBASE_MCP=1`, point
`FIREBASE_PROJECT_DIR` at a consumer-owned directory containing `firebase.json`,
and choose an explicit access profile. `FIREBASE_MCP_ACCESS=limited` is the
reusable default and uses the exact `FIREBASE_MCP_TOOLS` allowlist. An operator
who owns the whole Firebase surface can opt into `full`, which enables every
feature group listed in `FIREBASE_MCP_FEATURES`, including administrative and
side-effecting tools. Tool availability is not blanket execution approval:
live writes, deletes, sends, initialization, and deploys still require a visible
target, per-action confirmation, audit evidence, and a rollback or containment
path. Authenticate
with `firebase login` for an interactive workstation or Application Default
Credentials for headless use. Grant `roles/cloudconfig.viewer` for inspection
and `roles/cloudconfig.admin` only to identities that publish live templates.
Use [FIREBASE_GROWTH_ADOPTION.md](FIREBASE_GROWTH_ADOPTION.md) for the reusable
cross-product path from connector setup through analytics delivery, guarded
Remote Config activation, production measurement, and rollback evidence.

## Safety notes
- **Configs are executed as shell** (the installer `source`s `configs/<repo>.sh`). Only run the installer with a config you have reviewed.
- The installer **refuses to write** unless `$TARGET` is a git repo.
- When `ENABLE_NEYRA_MCP=1`, the written `.mcp.json` contains a **machine-local absolute path** and is auto-added to the target's `.gitignore` — don't commit it. Secrets stay as `${ENV}` placeholders (never written to disk).
- When `ENABLE_FIREBASE_MCP=1`, `.mcp.json` contains the consumer's absolute Firebase project path and is gitignored. Authentication remains in Firebase CLI or ADC; legacy `FIREBASE_TOKEN` and service-account key files are not supported by the template.
- The `full` Firebase profile expands the MCP surface, not the authenticated identity's IAM. Firebase and Google Cloud permissions still decide which operations can succeed.
- Re-running is idempotent; the skill sync uses `rsync --delete` (when available) so skills removed upstream are pruned in the target.

## Updating the kit
Edit the canonical skills/subagents or templates here, bump [VERSION](VERSION), open a reviewed Neyra-Kit PR, and then re-run `install.sh` for each selected consumer repo. Shared behavior is never authored in a product repository.
