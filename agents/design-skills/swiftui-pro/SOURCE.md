# Source & attribution

- **Upstream:** [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) — `swiftui-pro/`
- **Commit vendored:** `be297ff`
- **License:** MIT © Paul Hudson (see `LICENSE`)
- **Listed in:** [twostraws/swift-agent-skills](https://github.com/twostraws/swift-agent-skills) (same author's
  curated directory).
- **Local edits:** added a `when_to_use` frontmatter field for the kit skill contract
  (explicit trigger, `ios/**` scope, boundary against `swiftui-design-principles` and
  `code-reviewer`). `SKILL.md` + `references/**` are verbatim from upstream.

## What was taken

`swiftui-pro/SKILL.md` plus its nine `references/*.md` (api, views, navigation, data,
swift, performance, accessibility, design, hygiene). Upstream also ships a duplicate nested
copy at `swiftui-pro/skills/swiftui-pro/` and plugin/marketplace manifests — those are not
vendored; the kit has its own distribution path.

## Why this one

Deliberately covers what LLMs get wrong — "edge cases, surprises, soft deprecations" —
rather than restating SwiftUI basics, explicitly to respect the reader's token budget. That
makes it complementary to `swiftui-design-principles` (how it looks) and to the kit's
`code-reviewer` (general diff quality) instead of overlapping either.

Overlaps Apple's own official `swiftui-specialist` skill, which ships with Xcode 27 and is
exportable via `xcrun agent skills export ~/.agents/skills`. Reconcile the two once Xcode 27
is in use rather than carrying both.

Part of the kit's bundled design skills (`agents/design-skills/`) so it auto-syncs to
`.claude/skills/` via `hooks/session-start.sh`.
To update: re-copy from a newer upstream commit, re-apply the `when_to_use` field, bump the SHA.
