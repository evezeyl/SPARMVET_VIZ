+# Agent dispatch: how to (short)

Rules: `CLAUDE.md` section 2.1. Agents: `.claude/agents/`. Guard: `.claude/hooks/coordinator_guard.py` (registered in `.claude/settings.json`). Eve, 2026-11-14.

## 1. Start a coordinator session (VS Code)

1. Choose **Fable** in the model drop-down.
2. Type `-coordinate` (a Fable session also does this by itself as its first action, CLAUDE.md 2.1).
   It creates `tmpAI/coordinator/<session id>`; from then on the hook refuses Edit/Write by that session (writes under `tmpAI/` stay allowed). Workers are not blocked.
3. Describe the work. The coordinator splits it, orders it, dispatches, reviews, merges, reports.
4. `-solo` removes the marker (the session may edit again). A Sonnet or Opus session needs nothing: work as usual.

Command line instead of VS Code: `claude --agent coordinator` (the agent file removes Edit and Write from the session).

## 2. The workers (`.claude/agents/`)

| Agent | Model | Default effort | Tools | Use |
|---|---|---|---|---|
| `coordinator` | fable | high | Agent, Read, Grep, Glob, Bash | only the lead session |
| `scout` | haiku | low | read-only | search, sweep, survey |
| `scribe` | haiku | low | read + edit | records: tasks.md, handoff, channel, notes |
| `builder` | sonnet | medium | all | code and tests, in a worktree |
| `builder-opus` | opus | high | all | only `opus` tags, one at a time |
| `reviewer` | sonnet | medium | read + Bash | diff review, test suites, audits (never edits) |
| `panel-scientist` | sonnet | medium | read + Bash (scratch only) | viewpoint: scientist and data scientist |
| `panel-architect` | sonnet | high | read + Bash (scratch only) | viewpoint: software architect, ADRs |
| `panel-developer` | sonnet | medium | read + Bash (scratch only) | viewpoint: developer, effort and order |
| `panel-user` | sonnet | medium | read-only | viewpoint: a user who is not a developer |

All agents follow `.claude/workflows/agent_principles.md` (verify, transparent and reproducible science, inform the user and do not choose for them, no half fixes or shims, tests that can fail, check what is decided). The viewpoints and the `reviewer` use the method of `.claude/workflows/design_review_personas.md`.

## 3. Which model and effort for which task

The coordinator reads the tag of the task (CLAUDE.md section 2) and picks the worker and passes `effort`:

| Tag | Worker | Effort passed |
|---|---|---|
| `haiku/low` | scout or scribe; for a mechanical code edit `builder` with `model: haiku` | low |
| `sonnet/low` | builder | low |
| `sonnet/medium` | builder | medium |
| `sonnet/high` | builder | high |
| `opus/high` | builder-opus | high |
| `opus/max` | builder-opus | max (ask Eve first) |

**Use the cheapest agent that can do the task** (you do not send the director to clean the floor): look-ups and records on haiku, code on sonnet, review and panels only when needed, opus only for an `opus` tag, never a Fable worker. Any other agent (for example `Explore`) may be used if the call names `model: haiku` or `model: sonnet`.

Effort levels: low, medium, high, xhigh, max (what exists depends on the model). Precedence, highest first: the effort the coordinator passes in the Agent call, then the `effort` in the agent file, then the session effort. The environment variable `CLAUDE_CODE_EFFORT_LEVEL`, if set, overrides all of them: leave it unset.
The model follows the same order: the model the coordinator passes, the `model` in the agent file, `CLAUDE_CODE_SUBAGENT_MODEL` (set to `sonnet` in `settings.json`, so an agent without a definition is never Fable), the main model.

A study, a panel or a search that the owner requests in order to answer a question that blocks a build is started first, before builds and records that do not need her answer; the worker is told it is the priority; the result is put before her as soon as it is ready (Eve, 2026-11-22, ledger `D-0476`; her words: "I want the agent to prioritize the search I request - when I need additional information to answer questions that are blocking the build"; the "started first" wording is the review session's reading).

## 4. Changing model or effort in the middle of a task

A worker stops (budget, wrong tag, a harder part found). The coordinator:
1. reads the worker's `tmpAI/progress.md` in its worktree (done, next, findings);
2. starts a **new** worker of the right agent and effort in the **same worktree**, with a new brief: what is done, what is next, the instructions for the new part;
3. never has two workers on one worktree at once.

## 5. The decision panel (open choices only)

Use it when a choice has two or more valid approaches, not for routine work.
1. A `scout` first collects what is already decided (ADRs, design files, `tasks.md`). The coordinator writes a brief (no length limit; Eve, 2026-11-16, `D-0154`: "try to stay concise but do not sacrify to clarity"): the question, the options, the files to read, the facts tagged DECIDED / CONFIRM / OPEN.
2. It starts at most 3 viewpoints **at once**, one round. Choose by the question:
   - affects results or data: `panel-scientist` + `panel-architect` (+ `panel-developer` if the build is big);
   - affects what the user sees or decides: `panel-user` + `panel-scientist` + `panel-architect`;
   - small technical choice: `panel-architect` (it also covers the developer) + `panel-scientist`.
   Each answers in at most 250 words.
3. The coordinator puts them in one tab-delimited table (option, viewpoint, pro, con, evidence class), adds its recommendation, and **stops**. Eve decides. No agent decides.
Flag first, even if all viewpoints like the option: anything that changes a result silently, hides a step from the user, or reconsiders a decision (ADR) already taken.

## 6. Check that the guard works (once, after a restart)

1. Restart the Claude session (hooks load at start). Choose Fable, type `-coordinate`.
2. Ask it to edit any `.py` file itself: it must be refused with "Coordinator mode...". Ask for the same through a builder: it must work.
3. If the coordinator is refused but a worker is also refused, the hook cannot tell them apart: tell Claude, and remove the `hooks` block of `settings.json` until fixed.
4. Already verified on 2026-11-14 with `claude -p` in a throwaway project (fixed session id, marker present): a main-thread call has no `agent_id` and a subagent's call has one; the coordinator's `pytest`, Write outside `tmpAI/`, generic agent without model, and Fable worker were refused; its `echo`, a haiku agent and the named workers ran; a worker's own `pytest` was not blocked; `scout` ran on haiku and `builder` on sonnet; `CLAUDE_CODE_SUBAGENT_MODEL` set in `settings.json` made a generic agent run on the named model (control without it ran on the session model). What is not tested: the VS Code extension itself (the same hooks and settings are read, but only a live session proves it: steps 1-3 above).
5. Quick test without a session: `echo '{"session_id":"x","tool_name":"Edit","tool_input":{}}' | python3 .claude/hooks/coordinator_guard.py; echo $?` gives 0 (no marker).

## 7. Where it is not enforced

- `.claude/agents/*.md` fixes each worker's model and tools; the settings fix the default model and refuse `Agent(model:fable)`.
- The guard hook (only for a session in coordinator mode) refuses: Edit/Write outside `tmpAI/`; Bash commands that run test suites, audits, scripts, the app or renders (git stays allowed, because the coordinator merges); starting an agent that would run on Fable (any agent that is neither a named worker nor called with `model: haiku` or `sonnet`, a `fork`, or a named worker called with another model such as opus); starting any agent except `scout`, `scribe` and the `panel-*` agents (a general agent included) with a brief that has no "Decisions" block of ledger lines that are DECIDED and taken by EVE (`D-0156`, `D-0159`) and no `NONE-CHECKED: <path>` line (the path is a scout's report saved by the coordinator or a scribe under `tmpAI/`, `D-0155`). The block may follow the heading after empty lines (`D-0157`); a ledger that is missing or unreadable refuses the call (`D-0158`). The form and an example are in `.claude/workflows/decision_compliance.md` section 6.
- Not enforced by any tool: "do not read big files" and "do not do work in a Bash command the hook does not know". Those are rules: if the coordinator does it anyway, tell it to delegate.
- There is no `.claude/models` folder in Claude Code; the model is a line in each agent file.

- **Waiting for a process (owner's order, channel block M625; found 2026-11-23: nine loops, 14 to 19 hours old).** An agent that waits for a process never loops on `pgrep -f <pattern>`: the pattern is in the loop's own command line, so the loop matches itself and never ends. It waits on the process id it started (`wait <PID>`, or `while kill -0 <PID> 2>/dev/null; do sleep 10; done`), or runs the command in the foreground, or uses the harness's own background notification. Every waiting loop has an upper time limit (`timeout`). Before it reports, an agent checks that it leaves no process behind and says so in its report. The brief of every worker that runs something says this.

## 8. The "Decisions" block of a brief (Eve, 2026-11-16: point 5 = A, `D-0164`; her addition `D-0165`; point 6 = C, `D-0166`)

**[ADDED by an agent, not Eve's words]** The wording of this section is an agent's; the decisions are hers and are named by number. The full definition is in `.claude/workflows/decision_compliance.md` section 6.

- **Who needs it.** Every agent the coordinator starts, except `scout`, `scribe` and the `panel-*` agents (`D-0156`), a general agent included.
- **What it holds.** A line `Decisions`, then one list item per decision: its number, then words of THAT ledger line between quotation marks (a contiguous piece of its decision or of her words, at least 12 characters; `...` marks a cut). Only lines that are DECIDED and taken by EVE can be quoted (`D-0159`). Example: `- D-0050: "No silent error that is the rule."`. A bare number, a number on the heading line, and words of another line are refused (`D-0166`).
- **`NONE-CHECKED: <path>`.** The line says that no decision applies and none is needed (wording of the review session, M158, not Eve's words); the path is the saved report of the scout that checked (a regular file inside the project, saved by the coordinator or a scribe under `tmpAI/`, `D-0155`). Her addition (`D-0165`): "no decisions that to be reported when one needed". So, **where no decision exists and one is needed, that is an open point: it goes to the numbered list for her and is not hidden behind `NONE-CHECKED`.**
- **Who checks what.** The hook checks the form; the reviewer checks the content (rule E, checkpoint 3 of `decision_compliance.md`).
- **When the hook refuses.** The refusal names the number and says what to add; it shows the start of the ledger line. The ledger is read first: a missing or unreadable ledger refuses the call, also with a valid `NONE-CHECKED` line (`D-0158`).

## 8. New session or compact? (written 2026-11-25 for Eve; a rule of thumb from practice, not measured)

In VS Code the model and effort of the session are the ones chosen in the drop-down. The `model` and `effort` in `.claude/agents/coordinator.md` apply only to `claude --agent coordinator` on the command line. Any model can coordinate: type `-coordinate` once at the start of a session (only a Fable session does it by itself). No worker is ever Fable.

| Situation | Choice | Why |
|---|---|---|
| Same goal, context less than about half full | keep going | nothing to gain |
| Same goal, context crowded, state files current (see below) | compact | the plan survives in the files |
| A phase ended (a batch of merges, a round of decisions) | new session | cheapest and cleanest restart |
| You want another model (Fable for detail, Opus for the overview) | new session | the model is per session |
| The coordinator repeats questions, forgets decisions or makes records errors | new session | the context is too long |
| One long research or design question | independent agent in its own session; its result goes in a file | the coordinator does not carry it |

Before ending or compacting, a scribe brings these up to date (the standing rules of CLAUDE.md section 2.1 and section 7 already require it):
1. `.claude/logs/handoffs/handoff_active.md`: the open state at the TOP, done items removed or archived the same day.
2. `.claude/tasks/tasks.md`: the status of the tasks.
3. `tmpAI/coordinator/progress_<date>.md`: one screen: done, running (worktree and branch), next.
4. `tmpAI/agent_channel.md`: your row of "Working on now" and the messages you handled.
5. Big picture: `.claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md`.

A new session starts by reading, in this order: CLAUDE.md section 3.1 files, the top of the handoff, the progress note, the channel. Do not read the whole handoff: it is very large (316 KB on 2026-11-25), which makes a fresh session expensive; cleaning it is the owner's job (CLAUDE.md, trigger `-handoff`).

### Panel viewpoints on Opus, and measuring (Eve, 2026-11-25)
- The `panel-*` agents run on Sonnet by default and have web search. A call may name `model: opus` for them (the guard allows it for these four only); Opus is an explicit choice of Eve, so when a brief does not name the model, the coordinator asks. Never Fable.
- Research without a coordinator: type `-researcher <persona>` (CLAUDE.md section 4.3) in a session on the model you want.
- Per coordinated week, a scribe adds one line to the handoff: coordinator model, quota percentage at start and end, work done, mistakes the checks caught.
