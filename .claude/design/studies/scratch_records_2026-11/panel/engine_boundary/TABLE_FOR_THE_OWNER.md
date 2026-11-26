# The engine boundary: one table for the owner (coordinator, 2026-11-21)

Ordered by D-0455, D-0456. A study: nothing is built, nothing is decided. Sources: `FACTS.md` (the map), `architect.md` (Opus), `scientist.md`, `developer.md`, all in this folder. The sizes are estimates from file counts; no prototype was built and no test suite was run.

## Your time question, answered first
"how much [time] so the app works with the engines we have now but with the rewrite that would allow insertion later of new engines" and "before or after my demo".

| | What | Size | Changes what the app does? | When |
|---|---|---|---|---|
| Stage 0 | Every file says which engine it belongs to. A list of the places allowed to use Polars or plotnine. A test that fails when they are used elsewhere. | about 2 work sessions | no | BEFORE the demo (all three viewpoints) |
| Stage 1 | The list of services an engine must provide, written as types and tests. No running code changes. | 1 to 2 sessions | no | before the demo (architect); after (developer). Your choice |
| The rewrite | The app files that reach inside the engine libraries go through the one entry. Engine knowledge moves out of the base library (filters, missing values, formulas, what a step writes, join kinds). Errors in one place. Texts. | about 11 to 18 sessions (architect, 6 stages) or 14 to 22 (developer, 8 stages) | it must not: each stage is checked against the reference pictures and tables | AFTER the demo |
| A neutral table and picture at the boundary | The app no longer holds the engine's own objects. HOME's plot display changes visibly. | 8 sessions or more, not sure | yes, HOME's plot display: needs your eyes | after the demo, last |
**What a "work session" is (added 2026-11-21 after her question "What you mean by work session - days ?").** Not a day. One work session = one task handed to one builder agent, from its brief to its report: the tests written first, the code, its own test runs. On this machine that is about 20 minutes to 1 hour. It is NOT yet usable then: each session is followed by a review by another agent (30 to 60 minutes; the review of today's drop branch took 52 minutes because the full test suite ran on a busy machine), often one round of fixes, the merge, and the full test suite again.
In CALENDAR time, measured on today's work (the coordinator's estimate, not a promise): about 2 finished sessions per day when the stages must go one after the other, 3 to 4 per day when stages can run side by side.
| | Sessions | Calendar time, if it is the main work |
|---|---|---|
| Stage 0 | about 2 | about 1 day |
| The rewrite | 11 to 22 | about 1 to 2 weeks side by side where possible; up to 3 weeks one after the other |
| The neutral table and picture | 8 or more | about 1 week, not sure |
What the calendar time depends on: the reviews and their fix rounds; the load of the machine (no test run above a load of 10, and the full suite takes 15 to 45 minutes); how many stages can run side by side (at most 3 builders; the stage on filters and missing values runs alone); your answers where a stage meets a choice; and whatever else is being built at the same time.

**Her principle (2026-11-21, her words):** "the recipe needs to be adapted to the specific of each engine ... To do exactly the same thing ... the language of the recipe will be the language of each engine". So the differences between engines listed below are expected, not defects: a recipe is written in the language of its engine (already the rule: the engine is in the step's name and in its registry field, D-0036, D-0238). What stays a question of this study is only what the APP tells the user when a recipe is moved to another engine. Her order: the demo first; other engines after.

How sure: medium. The two estimates overlap (about 14 to 18 sessions). Either could be off by about 40 %.
The demo needs none of it: one data engine and one plot engine, as today.

Should we decide fast? Deciding stage 0 fast costs little and stops the problem from growing: from that day a new line that uses Polars in an unmarked place fails a test. Waiting costs more rewrite for every such line written meanwhile. The target boundary itself (choice 1 below) does not have to be decided before the demo: stage 0 is the same under every option.

## What can change a result (flag first)
1. TODAY, not caused by the engines question: a plot leaves out rows whose number column for x or y is empty or "not a number", with only a console line. No shipped recipe is affected. Report: `tmpAI/coordinator/plot_rows_dropped/REPORT.md` (options A to E).
2. TODAY: the export records the versions of Polars, Shiny and plotnine, not of pandas, numpy and pyarrow, which sit between the table and the picture (`app/handlers/export_handlers.py:120-126`).
3. Where the plot's table passes to the plot library, a whole-number column with an empty value becomes decimal, and "missing" and "not a number" become one value (RUN; `libs/viz_factory/src/viz_factory/viz_factory.py:267`).
4. FOR A LATER ENGINE: the same recipe on another engine does NOT give the same result. Run, Polars against pandas: filters "not equal" and "not in" on missing values, means and sums with "not a number", joins on missing keys, a group of missing values, the default quantile (2.0 against 1.9), a seeded sample. Never promisable: identical last digits, the same sample from one seed on two engines, the same picture with other fonts.
5. FOR A LATER ENGINE: a filter tried in the Polars preview could keep other rows when another engine runs it as an audit step. The audit dialog must show the rows computed by the engine that will run the step.

## What exists already (the good news)
- One place chooses the engine (`app/modules/engine_registry.py`), from a two-row table; one entry file per engine library; every step and plot component carries its engine; the cache keys and the export record know the engine. All decided by you (D-0219, D-0238 to D-0240, D-0247, D-0248).
- What is Polars in the lineage is mostly DATA (step names, join kinds), not code.
What is missing: 17 app files reach inside the engine libraries instead of going through the one entry; the base library holds Polars knowledge; no test guards any of it.

## The choices, ranked
| # | Choice | Options | The panel | Reconsiders (information only) |
|---|---|---|---|---|
| 1 | The target boundary | (a) mark only: files say their engine, a test guards it, no code moves; (b) each engine gives a fixed list of services and everything else calls only those; (c) as b, plus a neutral table and picture crossing the boundary, reached in stages | architect: c. Scientist: b, c as the end state. Developer: b, c as a separate later decision. All three: not (a) alone, which leaves the whole rewrite for the day a second engine comes | ADR-010 in part |
| 2 | Polars in two roles | (a) Polars is also the app's own table library (reading files, storing tables, the preview), and `python-polars` is one data engine among future ones; (b) each data engine reads its own files and makes its own preview; (c) no such role | architect: a. Pitfall: point 5 above | ADR-010 |
| 3 | Stage 0 before the demo | yes / no | all three: yes | - |
| 4 | Stage 1 before the demo | yes / after | architect: yes (so that the audit dialog is written against services); developer: after | - |
| 5 | What another engine must respect | (a) it must give the same result as today's rules (missing values, filters, row order), proven by a set of small tests every engine passes, or the step is not offered on it; (b) a difference is allowed when declared, shown and recorded in the export; (c) no rule | architect and scientist: a, with b only where equality is impossible (last digits, pictures) | D-0042, ADR-103 (they say "follows Polars") |
| 6 | Where the lineage learns what a step writes | (a) a field of each step's registry entry, as data; (b) a table per engine in the base library; (c) the plan of columns only | architect: a (same pattern as the engine field); developer: the two existing lists become the engine's declared profile | D-0351 keeps its closed list; only its home moves |
| 7 | A recipe moved to another engine | a new recipe with a reviewed list of the steps that differ, never a silent translation | scientist | agrees with your remark (ledger M216) |
| 8 | Record more in the export | the versions of pandas, numpy, pyarrow; the count of rows a plot does not draw | scientist | see flag 1, 2 |
| 9 | The list of today's files that use Polars outside the engine library | allowed for now, each with the stage that removes it; or a permanent list | developer: with a removal stage per entry (a permanent list is only a map) | - |
| 10 | Later, when a second engine is planned | whose seed a plot's random layers use; tiers of different engines in one recipe; BLUEPRINT by engine (your remark, D-0395) | not now | - |

## The work in flight
All three: the join warning, the uncertain column drop, the tables no plot reads, the names pass and the deployment specification can go on now. Rule for new code from today: read join kinds and step names from the existing lists (`FOLLOWED_JOINS`, `READINGS` in `libs/utils/src/utils/step_effects.py`, `action_names.py`), do not spell Polars in a new place. Architect: the audit dialog should wait for stage 1 only; nothing new is added to today's audit path in the app (`audited_frame`), which the audit copy run will replace.

## Suggestion (the coordinator's, not decided)
Stage 0 now, before the demo. Choice 1: b, with c as the end state. Choice 5: a. The rest after the demo.

## Not verified
The stage sizes (no prototype); the test suites and the reference pictures were not run; how other engines (R, SQL) treat the types; whether the plot-settings rules split cleanly; whether the dependency tool accepts a new header line for the engine (a 10-minute check before stage 0).
