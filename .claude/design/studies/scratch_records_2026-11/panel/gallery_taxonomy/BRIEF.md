# Gallery: review of the taxonomy itself (coordinator, 2026-11-21; the owner's order with her decision D-0404, channel M434)

## The owner's words
"I think that the taxonomy fields and choice should also be reviewed by our agents - maybe they would come with better taxonomic classification ?"
Earlier the same day, on the chart type: the `geom_` names are good for people with plotnine or ggplot2 experience and must not be taken away; the classification must also let a statistician or a person with little experience of those libraries find what they look for (line chart, QQ plot, dumbbell, violin, box plot).

This is a STUDY. Build nothing, change no recipe and no spec. The viewpoints propose; she decides. It comes BEFORE the spec text for the chart type words, the counting rules and the meanings, so that they are written once.

## Her standing rules
- An option is judged on merit: correct, sound, useful to the user. "It reopens a decision" is INFORMATION in its own column, never a reason to reject an option or to rank it lower.
- Verify, never guess: label each statement RUN, READ (file:line) or REASONED.
- The tool informs; the user chooses. Plain short sentences. "Suggestion:" before a remedy.

## What the taxonomy is for
A user of the Gallery (34 plot examples today; more later, written by recipe authors) ticks values in a filter panel to find an example to copy for their own data. Three kinds of user: a scientist new to data science; a statistician who thinks in chart names and questions; a person who knows plotnine or ggplot2 and thinks in `geom_` names.

## What exists today (READ these)
- The six axes and their allowed values: `libs/utils/src/utils/recipe_spec.yaml`, gallery section (about lines 187-215): family, pattern (data pattern), difficulty, show (what it shows), sample_size, and the derived geom. The cheatsheet with the meanings: `assets/gallery_data/TAXONOMY_CHEATSHEET.md` (read by no code today). How the filter works: `app/modules/gallery_listing.py`, `app/modules/gallery_viewer.py`.
- The 34 examples: `assets/gallery_data/<example>/data_analysis_recipe.yaml` (the `taxonomy` mapping in the plot entry).
- What the verification of the 34 examples found about the tags: the TAG TABLES at the end of `tmpAI/panel/gallery_verify/data_scientist_1.md` and `data_scientist_2.md`; the tag remarks of `tmpAI/panel/gallery_verify/statistician.md`; the user's view in `tmpAI/panel/gallery_verify/user_new_to_data_science.md`.
- The draft of the new axis "Chart type" and its review: `tmpAI/panel/gallery_study/Q2_CHART_TYPE_DRAFT.md` (sections 1, 3, 4 and 9: the user found "family" and "chart type" together confusing, and 13 of 25 words unknown to it).
- The study that found overlaps: `tmpAI/panel/gallery_study/TABLE_FOR_THE_OWNER.md` and the files beside it.

## Decisions taken so far (information; read each ledger line in `.claude/knowledge/decision_ledger.md` before you rely on it)
D-0397 (names and headings), D-0398 (the geom filter lists all layers; a new typed axis "Chart type" with several values), D-0399 (the spec holds the words and their meanings; the cheatsheet and the docs are generated), D-0402 and D-0403 (three tags are checked against the recipe and data: pattern, sample size, difficulty; a mismatch is an advice), D-0404 (the meaning of a filter term is shown on hover or click, and in the documentation). If your best proposal changes one of them, propose it anyway and name the decision in the column "Reconsiders a decision?".

## The question
Are the axes and their values the right ones? Propose the classification you would give the Gallery, judged on merit, for the three kinds of user. Cover at least:
1. Each axis today: what question of the user it answers; whether its values are distinct, complete and checkable; examples that fit no value or several.
2. The overlaps: family against what-it-shows; family against chart type; pattern against the mapped columns (could it be derived instead of typed, and what would be lost?); difficulty (what does it measure: number of layers, the statistics needed, the data preparation needed?); sample size (per group or whole table; a requirement of the plot or a property of the example's data?).
3. Missing axes or values: for example the question the user asks ("compare groups", "show how values are spread", "follow over time", "relate two measurements", "show parts of a whole"); panels (facets) as a derived property; what the data must look like (one row per observation, or already summarised); whether a plot shows every observation or a summary.
4. Which axes should be typed by the author and which derived from the recipe, and for a typed axis how it can be checked.
5. The filter with more than one value per example: what the user must be told.
6. A concrete proposal: the list of axes, each with its values and a one-line plain meaning, and the value(s) of each of the 34 examples under your proposal for the axes you change (a table). Say what it costs (the 34 recipes, the spec, the checker, the filter code, the cheatsheet) and what it gives.

## What to return
Start with a 6-line summary. Then the table she asked for: | axis | today | problem (with evidence) | proposed change | what it gives | what it costs or risks | reconsiders a decision? (number, information only) |. Then your proposal in full (point 6). End with "To decide first (ranked)" and "Not verified". If you have a shell, save your text as `tmpAI/panel/gallery_taxonomy/<your name>.md` with a redirect and return the path plus the summary and the table; if you cannot write, return the full text.
