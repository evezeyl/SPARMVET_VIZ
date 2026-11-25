# Panel round 2: a table as a result, with the owner's "text plot" idea (2026-11-22)

PRIORITY: the owner waits for this to answer a question that blocks a build. One round. You only recommend; she decides.

Read first, in full: `FACTS_2.md` (this folder: what a tier shows, what ties a tier 3 to a plot, what exists today), then `FACTS.md` (what is decided) and `TABLE_FOR_THE_OWNER.md` (round 1). Verify at file:line what you rely on. Never read `tmp.md`.

## Her rules for this panel
- Judge each option ON MERIT. That an option reopens a decision, a check or a definition is information only: one line "Reopens:", never an argument against.
- Build time is not an argument. But "nothing new built" is a value SHE named ("That would avoid build something new"): judge honestly how much each option really reuses, and where "nothing new" would be an illusion.
- The data stays data: a table shown as a grid, never a picture.
- The "All rows" switch must stay (100 rows by default, the whole table on demand).
- Avoid, if it can be avoided, a new place that assumes "an entry is a plot" or a second parallel path.
- NEW from her: a tier 3 is a data table. That it is "the last stage before a plot" is our definition, not a limit. A tier 3 may be the final table of a RESULT in table shape, with no plot. Judge the options WITH that.

## Her idea, in her words
"when a table is the result it is shown in the highest tier that contains instruction ... So we could actually have a "text plot" : the table Tier X shows the results requested by the recipe. That would avoid build something new."
Confirmed by the code (FACTS_2 section 1): the table at a tier is the result of every step up to that tier; a tier with no steps is the same table as the one below; so "the highest tier with steps" and "T3" are the same table.

## The options for question 2 (a table as a result)
- **2A** nothing new: such a table is seen in the data preview (under a plot) and in the export.
- **2B** (round 1's choice) a new kind of entry in a group, in a sibling key `tables` beside `plots`: own short name, the table it reads, own tier 3, shown as a grid in the plot area in its own sub-tab.
- **2E "text plot" (her idea, as an entry)**: the PLOT ENTRY stays the only kind of entry. An entry that asks for a table instead of a drawing shows its table (its T3 = the highest tier with steps) as a grid in the plot area, with "All rows". It lives in `plots`, has an id in the same id space, `ui_label`, `target_dataset`, optional `tier3`. Because it is found by the same lookup as a plot entry, its table is built, keyed, stored, traced (`T3:<id>`) and audited by the code that exists (FACTS_2 section 3). What differs is only the SHOWING. How the entry says "show me as a table" has variants:
  - **2E-1**: by the absence of `mapping` and `layers` (the check PS03 is relaxed for that case).
  - **2E-2**: by an explicit key on the entry (for example `show: table`; the name is open).
  - **2E-3**: by the engine key, `plot_engine: <a table engine>` (the review session's idea, not hers; D-0238/D-0239: the list of engine names is open).
- **2F** a mark on a table or join of the recipe (for example `result: true`), no entry: HOME shows the marked table at its highest tier with steps. Then: where does a tier 3 of that table live (on the table itself, a new `tier3` key of a table or join), what is its id for the audit steps, the lineage and the stored file, what carries its short name, in which group and sub-tab does it appear?
- **2D** a picture of a table: rejected by all four in round 1; say only if the new facts change that.
You may add a variant if a better one exists; name it.

For EACH of 2E (say which variant) and 2F, answer concretely: what is reused unchanged; what must still be built (from FACTS_2 section 4: the check PS03; each caller of the draw that expects a plotnine object: HOME plot output, Compare, the opening build "draws every plot once", the export picture, the report, Gallery previews, BLUEPRINT's live plot; a two-pane Original against Audited for tables; the report includes no table today); what the user sees; what the audit and the export do; what could change or go missing silently.

## Question 1 again, in the light of round 2
Round 1 chose 1B (tier 2 allowed on every table and really built; a tier 3 only on an entry that shows something). With her correction, say whether you keep 1B, and whether under your choice for question 2 the checks S07 and J14 go, or become "no entry reads this table".

## Your answer: AT MOST 250 words
Preferred option for question 2 (with the variant) and the reason; the strongest con of your own choice; one line per other option (pro, con); question 1 in one or two lines; "Reopens:" (decisions, checks, definitions; information only); "Flags:" anything that changes a result silently, hides a step, or differs between screen and export; evidence as file:line. No preamble.
