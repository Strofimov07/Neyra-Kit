# Source & attribution

- **Upstream:** [pbakaus/impeccable](https://github.com/pbakaus/impeccable) — `.claude/skills/impeccable/` (v3.9.1)
- **Commit vendored:** `depth-1 clone HEAD` (2026-07, tag/version 3.9.1)
- **License:** **Apache-2.0** © Paul Bakaus / Renaissance Geek (see `LICENSE`)

## What was vendored vs upstream

- **Included:** `SKILL.md`, `reference/*.md` (command playbooks), `scripts/**` (detector,
  palette, live-browser). Verbatim from upstream **except one local edit** (below).
- **Local edit — phone-home killed in code:** `scripts/context.mjs` →
  `fetchLatestSkillVersion()` is patched to `return null` before the network call, so the
  vendor version-check to `impeccable.style` never fires for anyone (not just where a config
  disables it). Diff is commented in-place with a restore note.
- **NOT included / NOT wired:** the **design hook**. Upstream's `npx impeccable install`
  registers a PreToolUse/PostToolUse hook in `.claude/settings.json` that runs the detector
  on every UI edit. We did **not** copy that settings manifest and did **not** wire any hook,
  so nothing fires automatically. The `scripts/hook*.mjs` files are present (some are shared
  libs used by commands) but inert unless a hook is manually registered.
- **Also not wired:** the `impeccable-manual-edit-applier` subagent (upstream ships it under
  the skill's `.claude/agents/`); the interactive `live` manual-edit flow may be degraded
  without it. Core commands (`audit`, `polish`, `craft`, `critique`, …) do not need it.

## Behavior to know (executable third-party code)

- **Phone-home: removed.** Upstream `context.mjs` fetched `https://impeccable.style/api/version`
  on command context build (a version/update check — not needed for any functionality). We
  **hard-disabled it in the code** (see local edit above), so it never fires for any consumer.
  The repo-root `.impeccable/config.json {"updateCheck": false}` is kept as belt-and-suspenders.
  This was the ONLY outbound (non-localhost) call — `net.Socket`/`live-*` traffic is all `127.0.0.1`
  (local dev-server probing / live-preview), and the `developers.openai.com` string is a comment.
- **Subprocess / server:** `scripts/live*.mjs` use `execSync` and start a local HTTP server
  that injects a `<script>` into pages for the `live` browser-iteration feature. Only runs
  when a `live` command is invoked.
- **Runtime:** commands shell out to Node (`Bash(node .claude/skills/impeccable/scripts/*)`
  per SKILL.md `allowed-tools`); Node must be on PATH.

## Scope & updating

Web/CSS surfaces only (like the rest of `agents/design-skills/`). To update: re-clone
upstream, re-copy `.claude/skills/impeccable/` + `LICENSE`, keep the hook unwired, re-confirm
`.impeccable/config.json` still disables the phone-home. To enable the hook or the `live`
subagent later, see `../IMPECCABLE.md`.
