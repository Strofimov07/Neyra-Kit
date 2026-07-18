# Neyra-Kit authoring governance

This repository is the canonical source for the shared Neyra skill kits,
subagents, hooks, installer, governance, version, decisions, and evolution
signals. Product repositories, including AI Browser, are consumers.

Before changing a shared kit path:

1. Run `python3 agents/neyra-dev-kit/source-policy.py --require-canonical`.
2. Follow `agents/dev-skills/kit-evolution/SKILL.md` and
   `agents/neyra-dev-kit/EVOLVING-THE-KIT.md`.
3. Append the observed signal before routing it, add the decision rationale,
   and bump `VERSION` plus the `AGENTS.devkit.md` footer together.
4. Run `bash agents/neyra-dev-kit/doctor.sh` before opening a PR.

Installed copies in consumer repositories are generated state. Do not accept a
shared kit implementation in a product repository; route it back here. Keep
project facts out of generic layers — consumers own those under `settings/`.
