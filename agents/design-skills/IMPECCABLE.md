# Impeccable — bundled skill-only (hook OFF)

Status: **bundled in the common kit**, `agents/design-skills/impeccable/`, as a
skill + commands. The auto-firing design **hook is NOT wired**. Apache-2.0.

## What's active vs off

- **Active:** the `/impeccable <verb> [target]` commands (`audit`, `polish`, `craft`,
  `shape`, `critique`, `animate`, …) and the design-language guidance in `SKILL.md` +
  `reference/*.md`. Auto-injects like the rest of `agents/design-skills/`.
- **Off:** the PreToolUse/PostToolUse **hook** (no `settings.json` manifest wired) — nothing
  runs automatically on file edits.
- **Phone-home:** **removed in code** — `scripts/context.mjs` `fetchLatestSkillVersion()` is
  patched to `return null`, so the vendor version-check to `impeccable.style` never fires for
  anyone (not just where a config disables it). It was the only outbound/non-localhost call.
  Repo-root `.impeccable/config.json {"updateCheck": false}` kept as belt-and-suspenders.
- **Executable footprint:** `scripts/**` is real Node (detector, palette, ~600KB live-server).
  Commands shell out to it (`Bash(node …/scripts/*)`); Node must be on PATH. See
  `impeccable/SOURCE.md` for the full behavior note.

## Coexistence with the rest of the kit

Impeccable overlaps `design-taste-frontend` / `high-end-visual-design` / `emil-design-eng`.
Don't stack them on the same page — pick one lead skill per task. Keep `review-animations`
as the motion-review authority. Web/CSS only; never on SwiftUI.

## If you later want the auto-hook (opt-in, per web project)

Not recommended repo-wide (it fires on every edit and would hit the iOS tree). If you want it
on a specific web project:
1. Register the hook only in that project's `.claude/settings.local.json` (machine-local),
   pointing at `…/skills/impeccable/scripts/hook.mjs`.
2. Constrain the detector to web extensions/dirs via `.impeccable/config.json` (`detector`
   ignores) — exclude `*.swift` and `ios/` so it never nags on the app.
3. Keep `{"updateCheck": false}` unless you want the vendor version-check network call.

## If you want the interactive `live` flow

`live` uses a subagent (`impeccable-manual-edit-applier`) that upstream ships under the skill's
own `.claude/agents/`. It is not wired here. To enable, copy that agent into `.claude/agents/`
and add it to the dev manifest's `PORTABLE_AGENTS` if it should ship to consumers.

## Consumers of the kit

The phone-home is disabled **in the vendored code**, so every consumer gets it off by default —
no per-repo config needed. If you ever re-copy `scripts/context.mjs` from a newer upstream, re-apply
the `fetchLatestSkillVersion() { return null }` patch (or you'll reintroduce the version-check call).
