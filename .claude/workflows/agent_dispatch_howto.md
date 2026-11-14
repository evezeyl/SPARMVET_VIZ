# Agent dispatch: how to (short)

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

## 4. Changing model or effort in the middle of a task

A worker stops (budget, wrong tag, a harder part found). The coordinator:
1. reads the worker's `tmpAI/progress.md` in its worktree (done, next, findings);
2. starts a **new** worker of the right agent and effort in the **same worktree**, with a new brief: what is done, what is next, the instructions for the new part;
3. never has two workers on one worktree at once.

## 5. The decision panel (open choices only)

Use it when a choice has two or more valid approaches, not for routine work.
1. A `scout` first collects what is already decided (ADRs, design files, `tasks.md`). The coordinator writes a brief (aim for 10 lines, never more than 20, the extra only for a complex problem): the question, the options, the files to read, the facts tagged DECIDED / CONFIRM / OPEN.
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
- The guard hook (only for a session in coordinator mode) refuses: Edit/Write outside `tmpAI/`; Bash commands that run test suites, audits, scripts, the app or renders (git stays allowed, because the coordinator merges); starting an agent that would run on Fable (any agent that is neither a named worker nor called with `model: haiku` or `sonnet`, a `fork`, or a named worker called with another model such as opus).
- Not enforced by any tool: "do not read big files" and "do not do work in a Bash command the hook does not know". Those are rules: if the coordinator does it anyway, tell it to delegate.
- There is no `.claude/models` folder in Claude Code; the model is a line in each agent file.
