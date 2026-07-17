# Source & attribution

- **Upstream:** [emilkowalski/skill](https://github.com/emilkowalski/skill) — `skills/review-animations/` (`SKILL.md` + `STANDARDS.md`)
- **Commit vendored:** `1274a05`
- **License:** MIT © 2026 Matt Pocock (see `LICENSE`)
- **Local edits:** added a `when_to_use` frontmatter field to satisfy the kit skill
  contract. `disable-model-invocation: true` is kept from upstream (call it explicitly
  in the UI review pass). Bodies are verbatim from upstream.

Part of the kit's bundled design skills (`agents/design-skills/`) so it auto-syncs to `.claude/skills/`
via `hooks/session-start.sh`. Applies to **web/CSS surfaces**, not SwiftUI.
To update: re-copy from a newer upstream commit, re-apply the `when_to_use` field, bump the SHA.
