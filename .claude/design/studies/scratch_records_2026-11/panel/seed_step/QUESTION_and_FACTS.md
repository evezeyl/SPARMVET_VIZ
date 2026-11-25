# A reshuffle as an audit step: question and facts for the panel (coordinator, 2026-11-20; scout READ on dev)

## Her words (2026-11-20; a study, not critical now; nothing built)
"A - but then we need to be able to add it as a step at the correct place in audit - which means the reshuffle option appears when it is possible based on the recipe - can we have in the @actions fields options for actions that need such special treatment? I think we already decided of some keys ... This would allow maybe to have the seed requirements for example and link to what will be used in ui should this action be used? So for the audit of such actions are used then when the user is happy with the reshuffle a seed step with the reshuffling needs to be written - the problem means that it needs to be recorded in the correct place which might not be in the audit steps after the original recipe ... important only for Audit"

## DECIDED (ledger)
- D-0341: Reshuffle is offered only in Audit mode; the Exploration plot is the recipe's plot.
- D-0052: a seed fixed in the recipe HOLDS; the app warns, does not overwrite.
- D-0056: the seed is 0 by default and written in the recipe; every seed that is used is written in the recipe or the audit recipe; HOME draws no seed per session.
- D-0332: in an audit recipe each tier has the author's `steps` (never touched) and a second list `audit_steps`; a plot's tier 3 follows the same form. D-0329: the reason is `audit_comment`. D-0322: an audit step is only a filter or a drop (for now; the list is in one place). D-0040: the copy minus its audit additions equals the original. D-0331: a hand-edited audit recipe is tampering.
- D-0092: the registering decorators keep the field that says exact, modified or own (the "keys already decided" she remembers); no ledger line decides a field for "random" or "special treatment".
## Asked, not decided
- A special seed field linked to the steps that use jitter, changed only in audit and Blueprint, the used seed recorded for the step (old ledger A01).

## Facts today (READ; file:line in the scout's report, kept by the coordinator)
- Where a seed lives in a recipe: on a LAYER of the plot (`layers[i].params.random_state`, a whole number, accepted only on a random layer), or once for the whole recipe (`plot_defaults.random_state`). The layers are NOT in a tier; tier 3 of a plot holds data steps only. There is no registered action for a seed.
- Which seed is used: an audit pin, else the layer's own number, else the recipe's default, else 0.
- The Reshuffle button today: shown when the plot has a random layer AND no seed is written anywhere for it (every random layer uses the default). A click draws a new number and stores a PIN for that plot in the session (not an audit step: no reason, no entry in the audit list). The pin is applied to EVERY random layer of the plot. It is saved in the session file.
- The export today: the exported plot uses the pin; the pin is listed in the steps file as an entry "random_seed" with a generated reason; and the reproducibility recipe gets the number written INTO each random layer's `random_state` (so the copy of the recipe differs from the original inside the author's layers).
- Which components are random: a list in code (`libs/utils/src/utils/random_layers.py`: geom_jitter, position_jitter, position_jitterdodge, geom_sina, stat_sina, and a bootstrap summary), proven by a test that draws every component twice. The registration of a component does NOT say "random" in a way a program can read (some carry a tag "jitter" and a `random_state` parameter; geom_jitter's own parameter list does not even list it).
- Actions on tables with a seed: `polars_sample` (seed required, a list in code) and `polars_rank` with the random method (its registration already carries a readable rule: "when method is random, require seed").
- Registration fields that exist: actions: label, category, context, tags, polars (exact or wrapper), wraps, params, description, yaml_example, rules, not_exposed. Plot components: label, category, context, tags, plotnine (exact, modified, own), params, overlay, not_exposed, engine, allow_extra_params.
- Records that disagree with the code (to correct with this): the rule file says `random_state: null` gives a new arrangement at every draw; the code refuses it (a seed is a number). The task SEED-HOLDS-1 is marked open; the code has it built.

## Candidate ways to record an audited seed
- **W1. Into the layer** (as the export does today): the audit recipe's layer gets `random_state: N`. The author's layers are changed.
- **W2. A place of its own on the plot, beside the author's layers** (the same idea as `audit_steps` beside `steps`): for example `audit_seed: {id: audit_..., seed: N, audit_comment: "..."}` on the plot entry; the author's `layers` never touched; the drawing uses it as the audit pin (the precedence already exists).
- **W3. As an item of the plot's tier 3 `audit_steps`** (a new pseudo-action "seed"): one list for everything the audit adds to a plot.
- **W4. Only in the audit record / steps file**, not in the recipe.
## Candidate ways to know "this plot can be reshuffled"
- **K1. As today:** the list in code, proven by the draw-twice test.
- **K2. A field on the registration** of a plot component (and of an action), for example `random: true` with the name of its seed parameter, checked against the draw-twice test; the UI and the check read the field.
- **K3. Both:** the field is the declared truth, the test proves the field.

## To judge
1. Which place keeps "the author's recipe untouched", lets "copy minus audit additions = original" be checked, survives the export and a rerun on another machine, and gives the same picture from the recorded seed?
2. One seed for the plot (as the pin today) or one per random layer?
3. A reshuffle TRIED is not an audit step; "when the user is happy" it becomes one, with a reason: what is the flow and what is stored before that?
4. When is Reshuffle possible "based on the recipe": a random layer with no seed written by the author; what if the author wrote a seed (D-0052: it holds)?
5. The registration field: what it would say, who reads it (HOME, the check, Blueprint), where the truth lives given that `libs/utils` cannot import the plot library.
6. Whether the allowed list of audit steps (filters and drops, D-0322) must widen, and what the check must refuse.
