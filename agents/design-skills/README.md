# Design skills — bundled auto-inject frontend/design craft

Canonical source for the kit's **bundled Skills**: third-party, anti-"AI-slop"
frontend/design skills that auto-inject into the main agent's context (Claude Code
Skill-tool skills), so web UI comes out at studio quality without being explicitly
dispatched.

## How they surface (differs from `agents/dev-skills/`)

| Layer | Home | Surfaces as | Loaded |
|---|---|---|---|
| `agents/dev-skills/` | engineering process | **subagents** (`.claude/agents/*.md`) | dispatched via Task |
| `agents/design-skills/` (this dir) | frontend/design craft | **Skills** (`.claude/skills/*`) | auto-invoked by `when_to_use` |
| `settings/skills/` | project-only | Skills | auto-invoked; **overrides** a same-named bundled skill |

Sync path: `install.sh` (manifest opt-in `BUNDLED_SKILLS_SRC`, dev kit only) +
`hooks/session-start.sh` copy each `<id>/` → `.claude/skills/<id>/` every session.
Precedence: `project (settings/skills) > bundled (this dir)`. The `.claude/skills/`
copy is generated and gitignored — **edit here, never there.**

## Scope

These emit **CSS/React/HTML**, not SwiftUI. They are `when_to_use`-gated to web
surfaces (`aso/frontend-web`, `backend/ops-console`, `screenshots/generator`,
marketing/landing pages). They do not fire on the iOS app. Complements
`design-system-conformance` (reuse the shipped design system) — taste skills lead
on greenfield web, conformance leads inside an existing system.

## Contents

**Core (always relevant):**
- `design-taste-frontend` — anti-slop landing pages / portfolios / redesigns (Taste v2)
- `redesign-existing-projects` — audit + upgrade an existing site to premium
- `high-end-visual-design` — agency-grade fonts/spacing/shadows/cards/motion
- `emil-design-eng` — Emil Kowalski's UI-polish & component-craft philosophy
- `review-animations` — motion-code review pass (explicit-invoke; `disable-model-invocation`)
- `animation-vocabulary` — reverse-lookup glossary for naming motion effects

**Style variants (pick by brief):** `minimalist-ui`, `industrial-brutalist-ui`, `brandkit`

**Image-gen / cross-harness (situational):** `imagegen-frontend-web`,
`imagegen-frontend-mobile`, `image-to-code`, `stitch-design-taste` (Google Stitch),
`gpt-taste` (Codex/GSAP variant), `full-output-enforcement`

**Impeccable (`impeccable`)** — `/impeccable audit|polish|craft|…` + design-language
guidance, from [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) (Apache-2.0).
Bundled **skill-only: the auto-hook is NOT wired** and the vendor version-check phone-home is
disabled via repo-root `.impeccable/config.json`. Unlike the others it ships executable Node
`scripts/**` (detector/palette/live-server) that commands shell out to. See `IMPECCABLE.md`.

## Provenance

All third-party MIT. Each skill dir carries `LICENSE` + `SOURCE.md` (upstream repo,
pinned commit, local edits). Sources:
- [`Leonxlnx/taste-skill@b177427`](https://github.com/Leonxlnx/taste-skill) (MIT)
- [`emilkowalski/skill@1274a05`](https://github.com/emilkowalski/skill) (MIT)

Only local edit vs upstream: a `when_to_use` frontmatter field added where the
upstream description lacked an explicit trigger (kit `SKILL_CONTRACT` requires one).
Update = re-copy from a newer upstream commit + bump the SHA in `SOURCE.md`.

**Impeccable posture:** bundled **skill-only, hook OFF** (see `IMPECCABLE.md`). The auto-hook
is deliberately not wired (it would fire on every edit incl. the iOS tree); enable it per
web-project only if wanted.
