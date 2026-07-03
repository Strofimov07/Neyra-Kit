# goal-mode orchestration

The kit-side driver for **goal-mode** (opt-in autonomous orchestration). The
canonical protocol is the skill `agents/dev-skills/goal-mode/SKILL.md`; this dir
holds the deterministic Claude Code driver that runs the non-interactive batch.

## Split of responsibilities

| Piece | Where | Runs the checkpoints? |
|---|---|---|
| Protocol (the loop + caps + stop contract) | `goal-mode/SKILL.md` | yes — in the main loop |
| Batch executor (implement + gate, per task, parallel, worktree-isolated) | `goal-mode.workflow.js` | no — returns for checkpoint 2 |

The driver never merges, pushes, or acts outward. Checkpoint 1 (approve the plan)
and checkpoint 2 (approve integration) happen in the main loop, between batches.

## Long-horizon anti-drift (NEB-1373)

Borrowed from z.ai's GLM-5.x long-horizon framing — the hard part of a long run is
holding the goal, not adding steps. The driver returns signals the main loop acts on
(Workflow scripts have no filesystem, so persistence is the main loop's job):

| Signal | Field | What the main loop does |
|---|---|---|
| Per-round observable | `readyForIntegration[].observable` | require a measurable per task (scalar delta or binary proxy); "none" = non-productive |
| Goal re-anchor | `readyForIntegration[].advancesGoal` | drop locally-green-but-off-goal work as drift, not progress |
| Compact state-of-goal | `stateOfGoal` | persist to `.neyra/goal-<id>/STATE.md` (compaction-surviving); re-read each round |
| Productivity | `productive` | `false` counts toward the early stop — two non-productive rounds stop the loop |

`STATE.md` (where the goal stands, one screen) is distinct from the dispatch ledger
(how the run is reconstructed). See `goal-mode/SKILL.md` steps 7–8.

## How to run

**Claude Code (deterministic driver):**
1. Ask the agent: `goal-mode: <your goal>` (or `/goal <your goal>`).
2. It runs `spec-elicitation` + `writing-plans`, creates Linear tickets, and stops at
   **checkpoint 1** with the plan + caps. You approve.
3. It executes the approved batch via the driver:
   ```
   Workflow({ scriptPath: "agents/neyra-dev-kit/orchestration/goal-mode.workflow.js",
              args: { goal: "<goal>", lanes: 2,
                      tasks: [{ id: "t1", ticket: "NEB-123", title: "...", brief: "..." }] } })
   ```
   Each task implements in its own worktree, then passes the gate.
4. It stops at **checkpoint 2** with what passed the gate. You approve; it integrates
   via `pr-hygiene`, re-evaluates the goal, and loops or stops.
5. `loop` resumes the active goal ledger for another bounded iteration.

**Cursor / Codex (no Workflow engine):** invoke the `goal-mode` skill (`/goal-mode`
or `@goal-mode`) and drive iterations with the host `/loop`. Same protocol, same
checkpoints — the batch runs as ordinary skill-guided steps instead of the driver.

## Caps & stop (defaults)
`--max-iter 5`, `--lanes 2` (cap 4), `--budget` (tokens/$). Reaching a cap, meeting
the acceptance criteria, two consecutive non-productive rounds (no metric moved), or a
`BLOCKED` task stops the loop with a resumable summary.
The run ledger lives under `.neyra/goal-<id>/` (gitignored) — Linear holds the real tasks.
