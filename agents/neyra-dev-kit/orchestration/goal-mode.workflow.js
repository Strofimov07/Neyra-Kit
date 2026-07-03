// neyra-dev-kit — goal-mode deterministic batch driver (Claude Code / Workflow engine).
//
// Runs ONE approved batch of a goal-mode iteration: implement each task in its own
// git worktree (lane isolation), then run the post-implementation gate on it, and
// return per-task verdicts. It deliberately does NOT merge, push, or act outward —
// checkpoints 1 (approve plan) and 2 (approve integration) live in the main loop,
// per agents/dev-skills/goal-mode/SKILL.md. Cursor/Codex have no Workflow engine;
// they follow the protocol skill via their host /loop instead.
//
// Invoke (after checkpoint 1 approval):
//   Workflow({ scriptPath: "agents/neyra-dev-kit/orchestration/goal-mode.workflow.js",
//              args: { goal, lanes, tasks: [{ id, ticket, title, brief }] } })

export const meta = {
  name: 'goal-mode-batch',
  description:
    'Execute one approved goal-mode task batch: implement each task in an isolated worktree, run the post-implementation gate, return per-task verdicts. Never merges or acts outward — checkpoints stay in the main loop.',
  phases: [{ title: 'Implement' }, { title: 'Gate' }],
}

const tasks = (args && args.tasks) || []
const goal = (args && args.goal) || '(goal unspecified)'
if (!tasks.length) {
  log('goal-mode: args.tasks is empty — nothing to execute')
  return { results: [], note: 'no tasks provided' }
}
log(`goal-mode batch: ${tasks.length} task(s) toward: ${goal}`)

const IMPL_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    status: { type: 'string', enum: ['DONE', 'BLOCKED', 'NEEDS_CONTEXT'] },
    summary: { type: 'string' },
    baseCommit: { type: 'string' },
    headCommit: { type: 'string' },
    // Per-round observable (z.ai long-horizon borrow, NEB-1373): the measurable
    // thing this task moved — a scalar delta ("p95 320ms -> 180ms") when one exists,
    // else an explicit binary/observable proxy ("crash on empty query: repro -> fixed").
    // "none" is a valid, honest answer — it marks the task as non-productive.
    observable: { type: 'string' },
  },
  required: ['status', 'summary', 'observable'],
}
const GATE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    pass: { type: 'boolean' },
    summary: { type: 'string' },
    blocking: { type: 'array', items: { type: 'string' } },
    // Intra-batch goal re-anchor (NEB-1373): does the result advance the *goal*,
    // not merely pass its own brief? Catches drift where a task is locally green
    // but does not serve the stated goal.
    advancesGoal: { type: 'boolean' },
  },
  required: ['pass', 'summary', 'blocking', 'advancesGoal'],
}

// Each task flows implement -> gate independently (pipeline, no barrier). The
// implement stage runs in its own worktree so concurrent lanes cannot collide.
const results = await pipeline(
  tasks,
  (t, _orig, i) =>
    agent(
      `You are lane ${i + 1} in a goal-mode batch. Goal: ${goal}\n` +
        `Task ${t.id || i + 1} (Linear ${t.ticket || 'n/a'}): ${t.title || ''}\n${t.brief || ''}\n\n` +
        `Implement ONLY this task in the current worktree. Use implementation-loop; ` +
        `for logic/bug fixes use test-first (failing test first). Record the BASE commit ` +
        `before you start and the HEAD after. Report a per-round observable: the concrete ` +
        `measurable this task moved (a scalar delta if one exists, else a binary/observable ` +
        `proxy) — or "none" if nothing measurable changed. Do NOT merge, push, or open a PR. ` +
        `If you cannot proceed, return status BLOCKED or NEEDS_CONTEXT with the reason.`,
      { label: `impl:${t.id || i + 1}`, phase: 'Implement', schema: IMPL_SCHEMA, isolation: 'worktree' },
    ),
  (impl, t, i) => {
    if (!impl || impl.status !== 'DONE') return { task: t, impl, gate: null }
    return agent(
      `Run the post-implementation gate on task ${t.id || i + 1} (${t.title || ''}) in this worktree: ` +
        `code-reviewer (reuse/scope/redundancy) + spec-review (diff matches the brief) + ` +
        `verify-runtime (strongest practical check on the real surface). Return pass=false ` +
        `with blocking items if any dimension fails.\n\n` +
        `Then re-anchor to the goal — "${goal}": set advancesGoal=true only if this result ` +
        `genuinely moves the goal forward (its observable was "${(impl && impl.observable) || 'none'}"), ` +
        `not merely that it passes its own brief. A locally-green task that does not serve the goal ` +
        `is drift — return advancesGoal=false and say so in the summary.`,
      { label: `gate:${t.id || i + 1}`, phase: 'Gate', schema: GATE_SCHEMA },
    ).then((gate) => ({ task: t, impl, gate }))
  },
)

const clean = results.filter(Boolean)
const ready = clean.filter((r) => r.gate && r.gate.pass)
const blocked = clean.filter((r) => !r.impl || r.impl.status !== 'DONE')

// A task is productive only if it passed the gate, advances the goal (re-anchor),
// AND reported a real observable — a locally-green task that moves no metric and
// does not serve the goal is drift, not progress.
const observed = (r) => r.impl && r.impl.observable && r.impl.observable.trim().toLowerCase() !== 'none'
const productiveTasks = ready.filter((r) => r.gate.advancesGoal && observed(r))
const productive = productiveTasks.length > 0
log(
  `goal-mode batch complete: ${ready.length}/${tasks.length} passed the gate; ` +
    `${productiveTasks.length} productive (advanced the goal + moved a metric); ${blocked.length} blocked`,
)
if (!productive) {
  log('goal-mode: NON-PRODUCTIVE round — no task both advanced the goal and moved a metric. Counts toward early stop.')
}

// Compact state-of-goal (NEB-1373): a small, durable summary the main loop persists
// to .neyra/goal-<id>/STATE.md each round so goal state survives context compaction —
// distinct from the per-task dispatch ledger. Kept intentionally small.
const stateOfGoal = {
  goal,
  metricThisRound: productiveTasks.map((r) => `${r.task.ticket || r.task.id}: ${r.impl.observable}`),
  done: ready.map((r) => r.task.ticket || r.task.id),
  open: blocked.map((r) => r.task.ticket || r.task.id),
  drift: ready.filter((r) => !r.gate.advancesGoal).map((r) => r.task.ticket || r.task.id),
}

return {
  results: clean,
  productive, // false => the main loop counts this toward the early-stop heuristic
  stateOfGoal, // the main loop MUST persist this to the compaction-surviving STATE.md
  readyForIntegration: ready.map((r) => ({
    id: r.task.id,
    ticket: r.task.ticket,
    commits: r.impl ? [r.impl.baseCommit, r.impl.headCommit] : null,
    observable: r.impl ? r.impl.observable : null,
    advancesGoal: r.gate.advancesGoal,
  })),
  blocked: blocked.map((r) => ({ id: r.task.id, reason: r.impl ? r.impl.summary : 'no result' })),
  note: 'NOT merged. The main loop must run checkpoint 2 (approve) before integrating via pr-hygiene.',
}
