# HOME filter scoping: concept, diagrams and test plan (DRAFT, thinking stage)

> 2026-11-11, later: this file is the working log. The two clean descriptions are
> `home_preview_filters.md` (Exploration) and `home_audit_steps.md` (Audit workspace); issue
> evezeyl/SPARMVET_VIZ#60. Where they differ from this file, they win.

**Status:** DRAFT 2026-11-11. No behaviour is changed by this file. Written with Eve to settle the
concept before any further code change. Related: issues evezeyl/SPARMVET_VIZ#56, #57; ADR-087.

## 1. Words (to be fixed in the UI, the help, the UML)

Two different things are called "tier" today. They must be named apart.

| Word | Means | Where |
|---|---|---|
| **Data stage** T1 / T2 | Raw / Result: stored data of a dataset (Parquet cache). Never modified by the user. | data lineage |
| **View mode** Raw / Result / My view | What the header strip shows. "My view" = the workspace where the user is allowed to change what the plot shows. | UI |
| **Exploration** | Temporary preview (Apply). Never stored, never exported. | UI |
| **Audited step** | Send to Audit with a reason. Permanent, per plot, exported. | T3 |

Eve's rule (2026-11-11), CONFIRMED and implemented: *Raw and Result are for looking at the data. They do
not modify the plots. To change a plot, work in My view.*

## 2. What the code does today (read from code, not changed)

| Item | Today |
|---|---|
| `applied_filters` | ONE global list. Used by every plot, every tab, and the data preview, in every view mode. No plot, dataset or stage scope. |
| Column list in the filter form | Columns of the active plot's dataset only. |
| Filter on a column the dataset lacks | Skipped for that dataset (issue #56). |
| Audited steps | Per plot (`t3_audit_steps_by_plot`), with propagation choice (this plot / all / all except). Only on My view. |
| Compare left pane | Result with no exploration filter and no audited step. |
| Export | Result + audited steps. Exploration never. |

Open defect to cover first in the tests: after removing one of two applied filters the view was not
refreshed (Eve, 2026-11-11), although the badge count dropped when tested headless. Needs a data-level test.

Stale text to correct when the concept is settled: the docstring of `_filter_apply`
(`filter_and_audit_handlers.py`) still says exploration filters apply on "My view" only.

Correction 2026-11-11 (Eve): once a preview filter is sent to audit it becomes an audited step and the
staged/applied preview rows are cleared when the audit is applied (`_clear_filters_on_t3_apply`). So My view
plot = stored data + audited steps; preview filters appear in it only while the user is still trying them.
Export = stored data + audited steps, or stored data alone when there are none.

To test (Eve): trash icon with several applied filters, removing only one; the data table must refresh at once.
To detail later: audited steps per plot (this plot / all / all except); a separate UML (HOME-AUDIT-SCOPE) can be
linked from the "Audited steps" boxes once the exact behaviour is known (tag `detail` = diagram name).

Rule proposed by Eve, 2026-11-11 (matches the code, to be confirmed): **an audited step always applies on T3.**
T3 = the derived frame of ONE plot: its dataset's T2 plus that plot's audited steps. T1 and T2 never change.
Consequences: the column check at promotion must run on the T3 base (T2), not on the data view (issue #58);
"this plot only" changes only that plot's T3, so another plot on the same dataset keeps its own T3 by design
(use "all plots" to keep them alike); the same T3 function should serve the table, the plot and the export.

Column drops (checked 2026-11-11, issue #59): on Raw/Result the column selector changes the table only (plots
unaffected). On My view a drop can be sent to audit (reason, scope options like filters, join-key columns blocked).
Dropping a column the plot maps makes that plot fail (`VisualizationError`); nothing warns at promotion and "all
plots" can break several. Eve: allowed in T3 with a warning. Drops are offered only when Data to show = My view
(filters: either choice).

## 3. Data lineage cases (what can differ between stages)

A plot reads ONE dataset (`target_dataset`, a join id or a data schema). Several plots can share it.
Real examples in `1_test_data_ST22_dummy`:

| Case | Lineage | Example in the recipe |
|---|---|---|
| L1 | T1 = T2 = T3 (no tier-2 steps, nothing audited) | `FastP` / `ResFinder` (a data schema used directly), `Quast_with_metadata` |
| L2 | T1 = T2, T3 differs (audited steps exist) | any L1 dataset after a Send to Audit |
| L3 | T1, T2, T3 all differ | `MLST_with_metadata` (tier2 steps; Result keeps only 2023-2025), after an audit step |
| L4 | Two plots share one dataset | `MLST_counts_bar` + `year_distribution`; `miaou` + `assembly_quality_dotplot`; `integration_plot` + `VirulenceFinder_counts_bar` (`ST22_Anchor`) |
| L5 | Plots on different datasets with different columns | `QC_Reads_Anchor` (wide QC columns) vs `MLST_with_metadata` |
| L6 | Join built from several ingredients | `QC_Reads_Anchor` (FastP + Quast + Bracken + metadata), `ST22_Anchor` (6 ingredients, tier2) |
| L7 | Dataset that is an assembly with its own output contract | `Summary_phenotype_length_fragmentation` |

For each case the diagram must answer: which stored object exists (T1 file, T2 file, none because
T2 = T1), where an exploration filter is applied (on a lazy copy, after the stored stage), where an
audited step is applied (on a forked copy at render/export), and what is exported.

## 4. Diagrams to build (StarUML, native API; names follow the code)

HOME package, status tag `implemented` / `planned`, ADR tag ADR-087.

1. **HOME-FILTER-STATE (as is)**: state diagram. Staged rows, applied rows; events Add, Apply, trash,
   Reset, plot-tab change, view-mode change; Send to Audit leaves the diagram into the audit stack.
2. **HOME-FILTER-SCOPING (concept)**: one diagram per case L1, L2, L3 side by side (three swimlanes):
   stored data (T1 / T2 files) -> exploration filter (lazy, global today) -> audited steps (per plot) -> plot / table.
   Colour: stored = grey, exploration = blue dashed, audited = amber, exported = teal. "My view" is drawn
   as a lane label, never as a data stage.
3. **HOME-LINEAGE-ST22 (reality check)**: object diagram of `1_test_data_ST22_dummy`: datasets, joins,
   which have tier-2 steps, which plots target which dataset (cases L4-L7).
4. **HOME-FILTER-SEQUENCE**: sequence for "filter on Result, switch plot to another dataset, Compare".

Review rule: one diagram answers one question; the scope question (global / plot / dataset) is drawn
once as "today" and once as the options, then Eve decides.

## 5. Edge cases (catalogue)

Filters: none; one; two (remove first / remove second / remove all); staged but not applied; remove
while staged only; Reset; same row added twice; value empty; zero rows left; all rows kept; column
present in T2 not in T1 (wide vs long); column absent on another plot's dataset; column renamed by tier-2;
dtype: string, int (`2022`), float, between inclusive/exclusive; filter value no longer in data
after a recipe switch; recipe switch with filters applied; session restore with filters.
Views: Raw / Result / My view / Compare; switch view with filters on; switch plot tab; Home -> Gallery -> Home.
Audit: preview filter + audited step on the same column; audited step on one plot, filter global;
propagation "all except"; deleting an audited step; export with both kinds.
Column selector: remove column used by the plot (temporary break, restore with "all columns"); remove all columns; reset.

## 6. Decisions needed from Eve (not yet taken)

1. ~~Do exploration filters change the plot in Raw/Result?~~ DECIDED 2026-11-11: no. Apply on Raw/Result
   changes the **table only**; plots change only in My view; Compare left = Result as is, right = My view.
2. ~~Scope of an exploration filter~~ DECIDED 2026-11-11: per dataset (plots sharing a dataset share it). Earlier options: global (today) / per plot / per dataset (plots that share a dataset) / per dataset and stage.
   Eve's thinking aloud: a preview filter is for verification, so per dataset may be simpler; the real question is
   the scope inside My view and for audited steps. Decide after the diagrams.
   Argument for per dataset (Claude, 2026-11-11): the filter form already offers only the columns of the active
   plot's dataset, so a filter is already built on one dataset; a global list lets it also hit other datasets that
   happen to share a column name (sample_id, Year, Country). Per dataset follows the stored data (T1/T2 per dataset)
   and plots sharing a dataset share the filter. Needs Eve's confirmation before code.
3. DECIDED: column selector (preview) is table only on every view; a drop is a T3 step sent to audit, same logic as filters, with a warning for plots that use the column (#59).
4. TO CONFIRM: My view without audit capability (ADR-085 scratchpad vs Eve: only when audit is on). TO CONFIRM: what Apply of an audit clears from the preview lists.

## 7. Test suite plan (browser + screenshots; science must not be wrong)

Location `app/tests/test_filters_behaviour.py` (Playwright, `qa` app features, recipe
`1_test_data_ST22_dummy`), plus headless checks on the filter functions.

- A **data-level oracle**: read the same data with Polars in the test, apply the same filter, compare
  the row count and values to what the table shows ("Viewing rows a through b of N" gives N) and to the
  plot's source frame. Screenshots are evidence, not the assertion.
- A **screenshot** after every step of each scenario, saved to `tmpAI/filters_<scenario>/NN_step.png`
  (agent scratch); the final state of each scenario is copied to `tmp/` for Eve's review.
- Each scenario of section 5 is one test; lineage cases L1-L6 are parametrised over the real datasets.
- Mutation checks: for every rule (preview only, no write, scope, remove refreshes, column absent skipped,
  Compare left pane unfiltered, export excludes exploration) break the code once and see the test fail.
- No test may leave state behind (shared page): each test resets filters through the same path a user uses.
