# Source & attribution

- **Upstream:** [arjitj2/swiftui-design-principles](https://github.com/arjitj2/swiftui-design-principles) — `SKILL.md`
- **Commit vendored:** `791d22d`
- **License:** MIT © arjitj2 (see `LICENSE`)
- **Listed in:** [twostraws/swift-agent-skills](https://github.com/twostraws/swift-agent-skills), Paul Hudson's
  curated directory — which requires human (not AI) authorship and MIT-compatible licensing.
- **Local edits:** added a `when_to_use` frontmatter field to satisfy the kit skill contract
  (explicit trigger + `ios/**` scope, and the boundary against `apple-hig` /
  `design-system-conformance`). Body is verbatim from upstream.

## Why this one

The kit's other design skills emit CSS/React/HTML and are `when_to_use`-gated away from
SwiftUI, so native iOS had no authoring design skill at all. This fills that gap: it is
explicitly about what makes an app "look and feel like quality apps rather than
AI-generated slop" — base-4/8 spacing grid, hierarchy through weight rather than seven
font sizes, system semantic colors over opacity hacks, native grouped content instead of
bespoke cards, and a pre-ship checklist.

Evaluated and rejected as alternatives: `emilkowalski/apple-design` (self-described
"translated for the web" — a CSS/JS rendering of WWDC material, mostly already native API
in SwiftUI) and `wshobson/mobile-ios-design` (cheat-sheet depth; an app can satisfy all of
it and still read as machine-made).

Part of the kit's bundled design skills (`agents/design-skills/`) so it auto-syncs to
`.claude/skills/` via `hooks/session-start.sh`. Applies to **SwiftUI / native Apple
surfaces**, not web.
To update: re-copy from a newer upstream commit, re-apply the `when_to_use` field, bump the SHA.
