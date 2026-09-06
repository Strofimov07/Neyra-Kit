# Source & attribution

- **Upstream:** [prisma-labs-dev/apple-skills](https://github.com/prisma-labs-dev/apple-skills) — `skills/hig/`
- **Commit vendored:** `a76633b`
- **License:** MIT (see `LICENSE`)
- **Content origin:** the corpus is a markdown mirror of Apple's public
  [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/).
  Apple's documentation remains Apple's; the MIT license covers the packaging, not the
  underlying text.

## Local edits

1. **Renamed** `hig` → `apple-hig` (dir + `name`), so the skill reads unambiguously alongside
   the kit's other skills.
2. **Frontmatter rewritten** for the kit contract: added `when_to_use` and `tools`; dropped
   `user-invocable`, `context: fork` and `agent: Explore`, which are upstream's own runtime
   conventions and have no meaning in this kit's loader.
3. **Dropped all 12 `*.videos.md` files** (~56KB). They contain no guidance — only lists of
   `docs-assets.developer.apple.com` video URLs with their alt text repeated verbatim. No
   file in the retained corpus links to them, so nothing dangles.

Body of `SKILL.md` and the 41 retained reference files are otherwise verbatim.

## Size note

676KB across 42 files — the largest bundled skill after `impeccable`. It is a **grep target,
not context**: `SKILL.md` is small and the corpus is queried on demand, so it costs disk in
each consumer repo rather than tokens. Repos that don't want it can disable the whole bundled
layer with `ENABLE_BUNDLED_SKILLS=0` (the per-repo toggle added in v0.37.0 for exactly this
kind of payload).

## Boundary

Facts, not taste — upstream states it directly: *"Consult the HIG for facts, never for
aesthetics."* Visual direction on native surfaces belongs to `swiftui-design-principles`.

Not vendored from the same upstream: `apple-aso` (operates on a `store.config.json` file
Neyra does not use — Neyra drives App Store Connect through its own typed backend), and the
framework reference skills (`swiftui`, `uikit`, `storekit`, …), which overlap Apple's official
Xcode 27 skills.

Part of the kit's bundled design skills (`agents/design-skills/`) so it auto-syncs to
`.claude/skills/` via `hooks/session-start.sh`.
To update: re-copy from a newer upstream commit, re-apply the edits above, bump the SHA.
