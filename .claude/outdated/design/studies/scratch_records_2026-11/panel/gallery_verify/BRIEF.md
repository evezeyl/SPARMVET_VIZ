# Gallery: critical verification of all 34 examples (coordinator, 2026-11-21; the owner's decision D-0401)

## The owner's words (channel M432, 2026-11-21)
"A - ensure that both data scientist and user (new to data science ) and maybe a statistician agent are involced in both passes. A note : we are on development phase so that its wrong now will only aftect my demo - so if having one pass after what is ongoing is better we can do so - but all recipes need to be verified critically so everything is correct".

Read as: every one of the 34 Gallery examples is verified critically, so that everything is correct: the mapping, the layers, the column types, the data, what the plot teaches, the text. Three viewpoints take part: the data scientist, the statistician, and a user new to data science. Each verification says what was READ and what was RUN. This pass changes NOTHING: no recipe, no data file, no text, no picture. It produces the evidence and the proposals; she decides; a picture changes only after she has seen it.

## Her standing rules
- Verify, never guess. Label every statement: RUN (you executed it), READ (file:line), SEEN (you looked at the picture), REASONED.
- An option is judged on merit. "It reopens a decision" is information on its own line, never an argument.
- Science is transparent and reproducible; the tool informs, the user chooses; no half fixes.
- Plain short sentences. Name the Gallery and the example in every finding. "Suggestion:" before a remedy.

## What exists
`assets/gallery_data/<example>/` holds `data_analysis_recipe.yaml` (a recipe of format 1 with one plot; `taxonomy` tags on the plot entry), `example_data.tsv`, `example_meta.md` (the guidance page the user reads), `preview_plot.png` (the picture shown). The Gallery shows the picture, a data sample, the recipe text and the guidance page. Rules: `.claude/rules/rules_gallery_standards.md`. Allowed tag words: `libs/utils/src/utils/recipe_spec.yaml` lines about 187-215.
Earlier findings, to CHECK and not to trust: `tmpAI/panel/gallery_study/Q1_NAMES_AND_HEADINGS_DRAFT.md` (section 2, flags F1 to F9; section 1 "Note on the example itself") and `tmpAI/panel/gallery_study/Q2_CHART_TYPE_DRAFT.md`. Decisions already taken by the owner on names, headings, chart types and the picture key: ledger D-0397 to D-0400 (`.claude/knowledge/decision_ledger.md`); they are not your subject, except where an example's content makes a decided name wrong.

## Scratch and running
You may run read-only checks with `./.venv/bin/python` (never the system Python) from the repository root, with scratch files ONLY under `tmpAI/panel/gallery_verify/<your name>_scratch/`. To draw an example the way the Gallery does, use the app's own path: `app.modules.gallery_examples.render_example` (read `assets/scripts/gallery_previews.py` for how it is called; it has a mode that draws into another folder and compares: never let it write into `assets/gallery_data/`). Machine rule: read `/proc/loadavg` first; do not start a run while the 1-minute load is above 10. No test suites.

## What to return
If you have a shell, save your full text as `tmpAI/panel/gallery_verify/<your name>.md` (a redirect) and return the path plus your summary table; if the write is refused or you have no shell, return the full text. End with "Not verified".
