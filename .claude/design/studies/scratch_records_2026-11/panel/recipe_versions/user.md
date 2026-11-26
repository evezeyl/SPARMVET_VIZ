# Versions of recipes: the USER viewpoint (panel-user, 2026-11-20; saved by the coordinator from its report)

It read FACTS.md only; it checked no code. Every screen sentence is a PROPOSAL.

## Flagged first (hidden steps, silent wrong results)
A. Today the app warns and opens a session on an edited recipe: the audit steps run on a recipe that now does something else. The refusal (D-0362) fixes it and must be built first.
B. The upload of a same-named YAML overwrites a recipe silently, and Blueprint saves overwrite in place: the author can change a recipe with no trace. No option except V3 (and only if git is used) prevents the overwrite.
C. `info.version` is free text that no logic reads. If the screen shows "version 1.2" the user trusts it, but the author may have edited without changing it. Any version shown must come from the content, not from the author's text.
D. The session folder holds no recipe text. After a refusal the app cannot show what changed, nor the user's own steps in plain words, unless the steps with their reasons are kept in the session.
E. The audit copy lives in memory only today; the audit folder is not built: Monday's work may be gone before Wednesday.

## Wednesday morning, option by option
**V0 no versions (the refusal).** Screen: "Your session was saved with the recipe 'X' as it was on Monday. The recipe has been modified since. The app cannot reopen it, because the result could be different. What you can do: (1) see your audit steps and their reasons below, (2) save this list as a file, (3) open the recipe as it is now, reanalyse, and add the steps again."
- She knows only "changed", not what, nor whether it matters to her figure: the weak point. The least: the sentence of D-0339 (changed in what it does / only in comments), if the fingerprint of the resolved content is built: "only comments" tells her she can redo the work with confidence.
- The list of steps with reasons (each step, its table, its reason, the date) must be on the refusal screen, with "Save this list" and "Print". The same list as in the session file, not a summary.
- She may think "my work is lost": the screen must say nothing was deleted.
- Lost: the figure as it was, unless she exported.
**V1 the session keeps its own copy of the recipe.** Screen: "This session uses the recipe 'X' as it was saved on Monday (an older version). The current recipe is different. [Continue on the older version] [Move my audit steps to the current recipe and check them] [Keep the list only]."
- One sentence explains it: "my session carries the recipe it was made with." It also gives what V0 lacks: what changed (a comparison between her copy and the current file).
- Hidden: the copy may be the resolved recipe (comments gone, fragments merged), not the author's file: it must be said.
- Risk: publishing from the old recipe by mistake, or from a recipe the author corrected because it was wrong.
- She wants BOTH: continue on the old version (to finish or reproduce) and move the steps to the new one, as a visible rerun step by step ("kept / no longer applies / gives other rows"), never automatic.
**V2 the app keeps all versions.** A bigger idea: every save makes a version, the selector grows, which versions count? Too complicated for one sentence; a long list of nearly identical versions and a wrong pick.
**V3 git by the maintainer.** Nothing on her screen; she cannot reopen anything herself; it protects the maintainer, not her. A good practice, not the answer to her Wednesday.

## On an old version: how she knows, every time
A fixed band that cannot be closed, on every figure, in the Audit view, on the export dialog, in the export's README and metadata: "OLD RECIPE VERSION (saved Monday 17 Nov; the current recipe is different)". Export from an old version: allowed after a plain confirmation ("You are exporting from an older version of the recipe. The current recipe would give a different result. The export will say so."), default button Cancel; the statement travels inside the export (and in the figure metadata, since a Publication export holds no recipe).

## Selector words
One entry per recipe, as today; old versions never in the selector for a new analysis, only inside a session made with them. Dates, not numbers: "as saved on 17 November 2026, 14:32". Not "version 1.2"; not "hash", "fingerprint", "spec_version", "format".

## A colleague sends a session or an export
The screen says who made it, with which recipe state, and whether her recipe is the same ("identical / changed only in comments / changed in what it does"). A recipe she does not have: "this recipe is not installed here", not an unknown error.

## Recommendation
V0 now (decided; removes flag A), with the refusal screen enriched (steps with reasons kept and saveable; the sentence on the kind of change). Then V1 as the next step. Not V2. V3 as maintainers' practice only. V1 is not acceptable without the fixed band and the export statement.

## The three sentences the screen cannot do without
1. "The recipe 'X' has been modified since you saved this session on [date], so the app cannot reopen it: the same steps could give a different result."
2. "Nothing was deleted: your [N] audit steps with their reasons are listed below. Save the list, then reanalyse with the current recipe and add the steps again."
3. "What changed in the recipe: [it changed in what it does / only in comments / the app cannot tell]." If the app cannot tell, it says so.

## What none of the options gives
- An author-side rule: a change that changes results is a new name or a new declared version, not a silent overwrite.
- "What changed" in a scientist's words (a threshold went from 5 to 10), not a text difference.
- Re-applying the step list on the new recipe, step by step, with the effect per step shown before she accepts.
- A reminder to the author before editing: "3 saved sessions use this recipe".
