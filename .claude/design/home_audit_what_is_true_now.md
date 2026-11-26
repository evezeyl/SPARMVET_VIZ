# WHAT IS TRUE NOW: HOME, the audit and the lineage (state of 2026-11-26, evening)

**Describes `dev` at commit `043a0c5c` (the merge that holds the one reader), plus the decisions of 2026-11-26 recorded in the ledger lines D-0638 to D-0667 and later (branch `task/records-2026-11-26`). Copied into git from the coordinator's page `tmpAI/status/WHAT_IS_TRUE_NOW_HOME_AUDIT.md` (not in git) on 2026-11-26; this copy is the one a new session reads. Paths below that start with `tmpAI/` are working pages in the main tree, not in git: they may be missing in a clone.**

One page. A new session reads this first and trusts it over any older text on the same subject. Written by the coordinator. Every "decided today" item comes from the review session's relays of 2026-11-26 of what the owner said: some as channel blocks (M693 to M704), and the direct messages to the coordinator (the rule for what is shown; the review of a step before applying it; no plot tabs in Audit mode; the two removals and the one rename; the review before the demo) are now recorded in the channel blocks M705 (the review before the demo) and M706 (the other seven items), each marking what is hers and what is to be confirmed. The ledger lines are D-0638 to D-0668 in `.claude/knowledge/decision_ledger.md`. "Built" means merged on `dev` (not pushed). When this page and an older record disagree, the older record is the one to correct.

## The model, in six sentences
1. An audit step is applied in **data**, never "in a plot". A plot's own drawing steps are not changed.
2. **Where** it is applied is a **place**: a table after its tier 1 (T1), after its tier 2 (T2), or the **Result data (T3)** of a plot: the last data table, the data that arrives at that plot.
3. The **scope** of a step is the place or places the user chooses in the panel **"Path of the data"** (the lineage). Nothing else says where a step goes.
4. What is built from a place follows by the recipe and is **shown as information** ("what the step reaches"); it is not chosen and not ticked.
5. At most **one place on a path**; the metadata is **not** a place; a step in several plots separately means choosing the Result data (T3) of each.
6. What the user **verifies** is the table at the place. Exploration never changes a plot and is never exported; the export holds the Result plus the applied audit steps.

## Words (use these; the others are retired)
| Say | Do not say |
|---|---|
| Result data (T3) | plot data, the plot's table |
| the table the plot reads (T1, T2 or T3) | the plot's table |
| place; the places chosen; what the step reaches | scope by plot: "This plot only", "All plots", "All plots except" |
| applied step / audit step; trial (a step being tried) | "My view" (gone since 2026-11-20) |
| original / audited / trial (the three states of a table or figure) | |

## Built (on `dev`)
- Audit steps at any tier: every step is a node with its place; HOME builds an audit copy of the recipe from the applied steps and reads its tables; the export writes the audited tables, the audit recipe and the per-place list of steps.
- The lineage as data and the panel "Path of the data" in Audit mode: a list and a map, one place per independent graph, pan and zoom, resizable, graph numbers, level headings (a column of the map is a level, not a tier), plain names ("<name>: Table, T1").
- The right panel lists the audit steps under "My Adjustments", each with "Written at <name>: Table, T1" or the plot's Result data.
- Plain wording of a filter step ("rows with no <column> record are removed / kept").
- The recipe checks for the metadata (declared only with a data table; joined from the data table with a left join in tier 1; a listed but unjoined metadata refused).
- One test walks every recipe folder and every Gallery example against the recipe check; its exception lists are empty; the two retest recipes that are refused on purpose are declared in `config/data_analysis_recipes/retest/EXPECTED_REFUSALS.yml` and the test asserts the refusal (it fails if one stops failing).
- The opening of a recipe: HOME builds and stores every table and draws every plot once, with a progress line in plain words, and warns (refusing nothing) when a plot receives more than 1,000,000 rows (`app/modules/opening_build.py`, `app/handlers/opening_handlers.py`; D-0326, D-0334, D-0363).
- The one reader of what is on screen, as pure code, merged but NOT yet wired into HOME: `app/modules/audit_place_view.py` (`viewed`, `table_for`, `view_identity`, `condition_fits`; the three states original, audited, trial; the no-plot cases). Slice 3a wires it in.
- The UML model: names of at most 45 characters and no line break (checked by the audit script); one diagram of the keys and hashes, DM-KEYS-HOME-AUDIT; tags not drawn on diagrams.

## Still built the OLD way (old thinking, to be removed; do not copy it into new work)
- The pop-up after "Send to Audit" that asks "This plot only / All plots / All plots except / At a table this plot is built from". The place chosen in the lineage replaces it.
- Four entries that create a step (the Filters panel button, the lineage button, the column-drop button, a small form for a table no plot reads). One entry will remain.
- "Send to Audit" offered only while T3 is viewed; the condition always built on the table of the open plot.
- In Audit mode, "Table to view: Source, T1, T2, T3" and the plot tabs.
- Stored names that speak of plots as scope (`plot_scope`, `t3_audit_steps_by_plot`); a second, unreachable pop-up for colour and shape overrides.
- The two-step way: a step is staged as a card without a reason, then "Apply".
Details with file and line: `tmpAI/panel/review_queue/OLD_THINKING_IN_CODE.md`.

## Decided today, not built (the target)
- **The header (her DIRECTION; D-0652 is to be confirmed as a whole):** a toggle "Exploration | Audit" in a row beside the recipe title; "Table to view" in Exploration only; Compare near the plot. The exact form "a switch above the plot area" and its words are the builder's, PROVISIONAL. (In build: slice 1.)
- **Showing:** choosing in the lineage only stages; a button shows (working label "Show selection"). A table place shows its table and a note in the plot area; a plot place shows the plot and its Result data. With nothing chosen, the item shown on entering Audit is the plot that was open. A condition being built is cleared, with a notice that stays, only when another table is shown.
- **In Audit mode there are no plot tabs:** one item at a time, with its Compare.
- **Try before applying:** the effect of a step is computed before it is applied, labelled as a trial; applying reuses that result. Marks ("place verified") reset when the condition or the places change.
- **One entry: a step bar next to the preview title** (she chose C, D-0663: condition, place, reach, Try, reason, "Add to audit pipeline"); it also carries the column drop. Build order: the flow first with the Filters panel button, the bar last; both old buttons removed at the end.
- **One reader** for what HOME shows: built (see "Built"), to be wired in by slice 3a.
- **The coordinator's design rule, not her words:** a trial is never saved and never exported; it follows from D-0302 (only applied steps are saved) and from D-0327 (exploration is never exported).
- Data with no plot stays reachable (a table no plot reads; no plot open).
- **At "Add to audit pipeline" the step is written at ALL the places chosen, including those not marked verified (D-0669):** the summary shows "N of M places verified" and the audit log records which were not; the mark is advisory, and making it required can be added later. (Source: the review session's direct message to the coordinator, 2026-11-26; a channel block has been requested.)
- **Removal and one rename, ON HOLD until she has read the behaviour page (D-0665, decided 2026-11-26, after M703):** the colour and shape pop-up (Plot Style, with its three plot choices) and its rule text (contract section 12g.9) are removed with the pop-up of "Send to Audit"; the stored names `plot_scope` and `t3_audit_steps_by_plot` are renamed ONCE, with a new session format number, together with that removal; only the per-place list is kept in `t3_steps.yaml` (the per-plot list goes). Not decided: the new names. Task: AUDIT-OLD-SCOPE-REMOVE-1.

## Open (the owner has not decided; do not build on a guess)
1. The word for the mark ("verified", "checked", "accepted").
2. What Compare shows beside a trial (the state before this step, or the original).
3. Whether the mark is kept in the audit log beyond what is decided above (the recommendation is yes).
4. Whether the separate "Apply" with staged cards goes (then steps are tried and applied one at a time). The tension: the step bar (D-0663) carries the reason and "Add to audit pipeline", which implies one act; she has not said that the separate Apply goes.
5. [moved to "Decided today, not built": the removal of the colour and shape pop-up, the one rename of the stored names, the per-place list only; D-0665. Still open: the new names.]
6. A recipe of tables only (refused before HOME today; kept refused until she answers).
7. Her new idea, being checked for feasibility: in Exploration, a switch "Recipe: Original | With my audit steps".
8. Older open points, unchanged: the audit log's content; uploaded data; plot ids across dated copies; the Gallery list (`tmpAI/status/QUESTIONS_HOME_2026-11-26.md`, `QUESTIONS_GALLERY_2026-11-26.md`).
**On hold until she has read the behaviour page:** the confirm-and-apply flow, the marks, the removal of the pop-up and of Apply.

## Where things are
- The behaviour page and its mock: `tmpAI/panel/review_queue/BEHAVIOUR.md`, `mock_flow.html`. (The study page beside it, `DESIGN_FOR_THE_OWNER.md`, is superseded in its flow and questions; its part on the reuse at apply holds.)
- The header and Audit-mode design: `tmpAI/panel/header_strip_audit/DESIGN_FOR_THE_OWNER.md` (the dated updates at its top win), `mock_strip.html`.
- The plan: `tmpAI/status/DEMO_BUILD_PLAN_2026-11-26.md`.
- Branches in work: `task/strip-toggle-compare` (fix round, the walk test, slice 1), `task/records-2026-11-26` (records and ledger lines), `task/outdated-wave1` (a records wave of the coordinator, not part of this page).
- Held and left alone: BLUEPRINT; Test Lab; the Gallery beyond what is necessary.
