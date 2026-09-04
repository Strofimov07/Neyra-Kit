# Source & attribution

- **Upstream:** [emilkowalski/skill](https://github.com/emilkowalski/skill) — `skills/pick-ui-library/SKILL.md`
- **Commit vendored:** `d23d7f8` (2026-08-21)
- **License:** MIT © 2026 Emil Kowalski (see `LICENSE`)
- **Local edits:** upstream ships this as explicit-invoke only (`disable-model-invocation: true`
  plus an "only runs when explicitly invoked" sentence in the description). The kit wants it
  to fire on its own whenever a frontend library decision is being made, so that key is
  **removed**, the sentence is dropped from the description, and a `when_to_use` field is added
  (kit skill contract: explicit trigger + surface scope). Body is verbatim from upstream.

Part of the kit's bundled design skills (`agents/design-skills/`) so it auto-syncs to `.claude/skills/`
via `hooks/session-start.sh`. Curated npm picks for **web/React** surfaces; not iOS.
To update: re-copy from a newer upstream commit, re-apply the frontmatter edits above, bump the SHA.
