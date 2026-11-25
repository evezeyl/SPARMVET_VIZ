# 05 review of test logic (second scientist). Written early; appended as I go.

Status: skeleton. Scratch scripts in scratch/r5_*.py. Labels: [run] = executed on the demo recipe through the real classes; [read] = read at file:line; [reasoned].

## Facts read (before running)
- [read] Completion is made at READ of each source (`orchestrator._read_source` -> `id_completion.complete_table`, union of ids of the metadata and every data schema "as read", no recipe step, id_completion.py docstring lines 1-30). The audit steps are tier steps, so they run AFTER the completion; the union is not recomputed from an audited table. `DS:` nodes are never a place (recipe_graph.py places()). So no allowed place lies before the completion: an audit step cannot make the completion add an entity back or not; see the run in section 3.
- [read] Places: T1 of every table, T2 of tables a plot reads, T3 of every plot. `chosen_places_problem`: no chosen place below another; the T1 places of several original tables may be chosen together.

All runs below: [run] on `1_test_data_ST22_dummy`, 42 entities, 28 tables, 73 nodes, 17 plots; E = 32557144, X = 40503315 (a completion line in ResFinder: `ResFinder_not_in_original_data` = True, status "Not Found"). Scripts: scratch/r5_lib.py (base + audit copy as file 02), r5_a..r5_h.py. Counts of figures come from the REAL `run_audit` (`plot_table`, `affected_plots`), cross-checked with a node-by-node build; both agree.

## 1. File 02's cases: place, step, inferred intent, scope check

Inferred intent for file 02 (it states none): "remove this sample / apply this filter, and read the effect on everything the place reaches" (reach = removal). It tested "reached = removed". That is the very equivalence the design does not promise (D-0549/G8, and the left-join design).

| case | place used (table, tier, where in the path) | step | intent assumed (inferred) | expectation tested | right scope under the rule of places |
|---|---|---|---|---|---|
| 1a | T3:amr_heatmap (the plot, after everything) | remove E, na keep | "remove E from the results" | gone everywhere reached | T3 reaches 1 figure by construction: the expectation was never possible; it is the right scope only for "hide E from this one figure" (and then 1 figure is the correct answer) |
| 1b | T1:ResFinder (original, AFTER completion, BEFORE every join) | same | same | gone from the 5 plots below | right for "remove E's ResFinder results"; wrong for "remove E". Correct result: 3 lose E, 2 (virulence_*) keep E by design |
| 1c | T1:metadata_schema (original, the table that is the RIGHT side of the 11 left joins) | same | same | gone from the 10 plots below | wrong scope for "remove E": E is the right table, so the left join keeps E with NULL source/year/country. The metadata is the scope for "forget E's description", not "remove E". The 7 plots that keep E are the designed result |
| 2 | T1/T2:ResFinder, T3:amr_heatmap | identity >= 98, na remove/keep | "keep high-identity hits" | N the same in every figure | T1:ResFinder is the only original that holds `identity`: right place for "filter the AMR results"; N differs per figure (19 AMR, 42 virulence, left join keeps the entity) by design. T2/T3 are the right scopes for "export table only"/"figure only" |
| 3 | T1:ResFinder, T2, T3, T1:ResFinder_with_metadata, T1:ST22_Anchor | remove rows with marker True | "drop the 4 completed samples" | N the same | marker belongs to one table: the scope for "ResFinder was not run: leave these out of the AMR counts" is T1:ResFinder; for "leave these 4 samples out of everything" the marker is the wrong tool: ids at all data originals. Refusal at ST22_Anchor (marker dropped) is correct |
| 4 | T1/T2/T3 | column drops | "remove a column" | accepted/refused | the lowest place where no later step reads it; independent of the lineage question |
| 5 | T1:Quast, T1:QA_population_zscore, T3:qa_population_zscore | remove E before/after the z-score | "population without E" vs "E hidden" | statistic same | both right for two different intents; T1:Quast is the matching scope for "without E in the population" |
| 6 | T1:metadata_schema | remove E | same as 1c | E gone | wrong scope; E left two plots only through the author's own `year between ... na remove` |
| 7 | T1 of a result table (Quality_metrics, ResFinder_with_metadata, AR1...) | remove E | "remove E from this exported table" | plots affected | T1 of that table is right for that intent (one table, none else); `affected_plots` empty is correct |

So: cases 1a, 1c, 6 are tests of the wrong scope for the inferred intent. Their findings are true as facts, but the headline "reached is recomputed, not removed" describes a scope mistake of the test, not a defect of the lineage. Cases 2, 3, 5, 7 used a scope that matches a legitimate intent; their results are the designed ones.

## 2. Re-runs with the scope that matches the intent [run]

### (a) Intent "remove E from every result"
Scope = the T1 of the 12 original tables that carry `sample_id` and feed results, chosen together (valid under `chosen_places_problem`: none lies below another): Summary, Summary_quality, Quality_metrics, Detailed_summary, FastP, Quast, Bracken, ResFinder, MLST, VirulenceFinder, QA_year_types, QA_aggregated_no_key. APEC_STEC_virulence_genes is a look-up with no `sample_id` (a step on it fails: "column 'sample_id' is not in the table"); it is left out. 44 places are derived.
- Metadata NOT needed: no join starts from it (it is always the right table of a left join). Result with 12 data tables: 17 of 17 figures affected, 0 of 17 show E (16 held E before; `qa_aggregated_no_key` has no id column: E's row was inside its aggregate, the figure changes and E cannot be "seen"). Of 71 non-original nodes (tables T1/T2 and plots), 0 hold E. Only T1:metadata_schema and its T2 still hold E (1 row, an original, not a result).
- Adding the metadata (13 places) -> 0 of 73 nodes hold E; 71 of 73 nodes differ (the 2 unchanged: the look-up).
- Row effects: figures 42 -> 41 rows (one row per entity), assembly/miaou/phenotype 126 -> 123, amr 74 -> 72, virulence_bar/variants 617 -> 599, mlst/year 33 -> 32.
- Minimal set is smaller than 12 for appearances only [run, drop-one test]: without Quality_metrics, Detailed_summary, Bracken, VirulenceFinder or QA_aggregated_no_key no FIGURE shows E (Bracken still leaves E in Bracken_with_metadata, a result table); each of the other 7 is needed for at least one figure (Summary: phenotype_genome_length_fragmentation; Summary_quality: qa_sequence_type_missing; FastP: qc_reads; Quast: 4 figures; ResFinder: 3; MLST: mlst_bar, year_distribution; QA_year_types: 2). Needing all 12 is a fact of results the user can export (tables nobody plots, Bracken_with_metadata).
- Remaining appearances: none. The look-up and the metadata are not result carriers. A table "built from the metadata alone" does not exist in this recipe (QA_year_types is a data schema with its own sample_id).

COMPLETION "add back" [run + read]: NO. The completion is made when each source is read (`orchestrator._read_source`, before any recipe step), from the ids "as read"; an audit step is a tier step after it and `DS:` nodes are never a place. Removing E at T1 of all 12 data originals while E stays in the metadata: E is not re-added (0 rows in every data T1; the metadata T1 keeps its 1 real row; no marker line for E anywhere). At T1 (after the completion) a removal also removes the added lines: X, a completion line in ResFinder, is removed from all 14 figures that held it and from every result table (0 left) with the same scope. A scope that omits ResFinder leaves X's completion line there: amr_heatmap, qa_amr_genes_per_sample, qa_fanout_rows_per_sample, QA_fanout_exhibit keep X (13 affected, 3 figures show X).
NOT tested: a removal made BEFORE the read (impossible as the rule stands: no place before the completion; the recipe-level way would be to remove E from the file).

### (b) Intent "remove E's ResFinder results only": T1:ResFinder
Of the 5 figures below, 3 lose E (amr_heatmap 74 -> 72, qa_amr_genes_per_sample and qa_fanout_rows_per_sample 42 -> 41); virulence_bar and virulence_variants keep E, 18 -> 9 rows: ST22_Anchor starts from FastP and left-joins ResFinder, so E stays with `gene`, `status`, `phenotype` NULL (9 rows, status NULL). This is the expected result and is the intended meaning of "remove ResFinder's lines for E": the other tools still describe E. Two things the user must know [run]: (1) the ST22 rows of E now carry status NULL, whereas a sample with a completion line shows status "Not Found" (X: 9 rows "Not Found"): "ResFinder removed" and "ResFinder ran, nothing found" look different in the data, correct but a reader of virulence_bar must tell them apart; (2) the 11 other figures (qc_reads, assembly..., mlst_bar...) still hold E: they do not read ResFinder, they are outside the scope, not "not removed". 5 affected, 13 figures show E, 16 held it before (matches file 02: 3 of 5 lose it).

### (c) Intent "remove it from one figure only": T3:amr_heatmap
1 affected, 15 of 16 figures still hold E (it left only the heatmap: 74 -> 72). By design.

### Partial scopes of a data original [run]
- T1:FastP alone: E leaves qc_reads, virulence_bar, virulence_variants (3 affected); amr_heatmap and 12 others keep it. FastP is the start of ST22_Anchor and of the left joins `FastP_with_metadata`/`QC_Reads_Anchor`.
- T1:VirulenceFinder alone: 3 affected (virulence_bar, virulence_variants, qa_fanout); E leaves the virulence figures although ST22 starts from FastP: the join with the look-up is an INNER join, which drops E's rows (gene NULL).
- Metadata only: 9 affected, 14 figures still show E, among them all three of amr_heatmap, virulence_bar, virulence_variants (E stays with NULL country/year).
- T1 of FastP, ResFinder, MLST, VirulenceFinder together: 8 affected, 8 figures still show E (those fed by Quast, Summary, Summary_quality, QA_year_types, ...): outside the scope.
- The existing option "remove from all the data" (`libs/utils/src/utils/remove_from_all.py`, D-0415/D-0416), run with `describe(raw, "sample_id")` and no plan book [run]: offers 17 places, of which `T1:QA_ST_with_NA` lies below `T1:Summary_quality`: `chosen_places_problem` refuses that list; and it does not reach Summary, Detailed_summary, MLST, VirulenceFinder, ST22_Anchor, QA_fanout_exhibit (listed as not reached, "unsure" without a plan book). So the two ways of implementing intent (a) are not the same set and the older one breaks the new rule of places. Not run with the plan book.
(Correction of wording in (a): with the 12 data originals, 71 of 73 nodes hold no E; the 2 that do are T1 and T2 of metadata_schema. With the metadata added, 73 of 73 hold none.)

## 3. Is "reached is not removed" a defect, a wrong scope, or both?

- Wrong scope (the test's, not the app's): 1a, 1b (as "remove E"), 1c, 6. With the scope that matches the intent, the effect is the intended one in every case run (a: 17 of 17, 0 show E; b: the exact figures by the left-join design; c: 1 figure).
- Not a defect of the engine: nothing changed silently; "below" is not "gone" (D-0549/G8) and the left join is the designed way to keep an entity with NULL description.
- Still a display problem (a "both" in a narrow sense): the word "reach" read alone makes the user think of removal. The user picks the right scope only if the lineage says what each parent is to its children (left side, right side, inner partner) and which parents are the starts of left joins. That is information about the recipe, not a choice for the user.

Cases where the RIGHT scope still does not give the intended effect (real findings):
1. Intent "remove E's ResFinder results, E stays everywhere else" gives, in virulence_bar/variants, E with status NULL; the recipe's own description says "a sample with no AMR hit counts as one hit", i.e. the same sample read as "no AMR" in the recipe's wording. No allowed scope can express "ResFinder was not run for E" in a figure that left-joins ResFinder, other than the completion's marker (dropped by ST22's select). [run for the NULL; recipe text read]
2. Intent "remove E from every result" via original tables is not expressible by one choice if the recipe has an original table with no entity id (the look-up): the user must leave it out; the app must say so (a step there fails). Also the existing "remove from all" option reaches fewer tables (6 "not reached") and violates the new rule on its own list. [run]
3. Intent "remove E from the metadata AND keep him described as removed in all figures" cannot be done from the metadata: only from the data originals (metadata is the right side). A user who removes E in the metadata "because it is the top" cannot get the removal. Expressible only by the data-original scope: allowed, not a conflict.
4. Intent "remove the lines the completion added, everywhere": the marker is per table (`<table>_not_in_original_data`) and is dropped by the joins' selects (39 of 73 nodes keep one): no allowed scope writes "remove completed lines" in joined tables; it IS expressible as ids at the data originals. [file 02, verified; not rerun]
5. Rule limit: the same entity cannot be chosen at an original and at a table below it (one place per path). So "remove E from ResFinder (T1) AND, separately, correct ST22_Anchor T2" is refused by the rule, correct; but "originals chosen together + one joined table beside them" is allowed only when not on a path; the rule is consistent for (a) as tested.
No case run where the rule forbids a combination that the intent needs. Not run: intents that need two places on one path (e.g. remove E from ResFinder and also filter a column in ResFinder_with_metadata).

## 4. Forth-back-forth lineage: what it must show [run: graph + `plots_below`]

Method: from the result, BACK to its original parents (T1 of schemas); from each parent, FORTH to all plots and tables below; then the plots and tables NOT below any of them; then which parents together serve an intent.

Needed beyond sets: for each parent, its role in each child (start of the left join / right side / inner partner / look-up with no entity id) so the user sees WHICH parent decides the entity set. The graph lists parents but not left/right; this had to be read in the recipe (ST22: FastP left metadata left ResFinder left MLST left VirulenceFinder inner APEC_STEC). [read]

### Start 1: plot amr_heatmap (reads T2:ResFinder)
- Back: ResFinder only.
- Forth from ResFinder: 5 plots (amr_heatmap, virulence_bar, virulence_variants, qa_amr_genes_per_sample, qa_fanout_rows_per_sample); 4 tables (ResFinder_with_metadata, ST22_Anchor, QA_AMR_per_sample, QA_fanout_exhibit).
- Outside: 12 plots, 10 derived tables (mlst_bar, qc_reads, ... all the other 12).
- Intent -> scope: "remove E from this heatmap and what the same data feeds" = {T1:ResFinder} (3 figures lose E, 2 keep it, by the joins); "heatmap only" = {T3:amr_heatmap}; "remove E from everything" = not this parent alone.

### Start 2: plot virulence_bar (reads T2:ST22_Anchor)
- Back (6): FastP, metadata_schema, ResFinder, MLST, VirulenceFinder, APEC_STEC_virulence_genes (look-up, no sample_id).
- Forth: FastP 3 plots; ResFinder 5; MLST 4; VirulenceFinder 3; APEC 2; metadata 10. Union 11 plots, 11 tables.
- Outside the union: 6 plots (phenotype_genome_length_fragmentation, qa_sequence_type_missing, qa_year_label, qa_l50_integer, qa_facet_by_mapping, qa_aggregated_no_key) and 3 tables.
- Intent -> scope: "E out of virulence_bar" = T1:FastP (start of the left joins) or T1:VirulenceFinder (inner join with the look-up drops him): two valid scopes with different reach (3 plots each; FastP also qc_reads, VirulenceFinder also qa_fanout) [run]. "E out of virulence_bar and every figure these parents feed" = the 4 data parents chosen together + the look-up left out (8 affected; 8 figures still show E: outside). Metadata is not needed to remove E (right side), needed only to forget his description.

### Start 3: AR1_MLST_Serotype_Virulence (result table, no plot reads it)
- Back (4): MLST, metadata_schema, VirulenceFinder, APEC_STEC_virulence_genes.
- Forth from MLST: 4 plots (virulence_bar, mlst_bar, year_distribution, virulence_variants) + AR1, MLST_with_metadata, ST22_Anchor; from VirulenceFinder 3 plots; APEC 2; metadata 10. Union 10 plots, 11 tables. Outside: 7 plots (amr_heatmap, ...) and 3 tables.
- The table itself: its own T1 is the one-table scope (only that table; no plot changes; `affected_plots` empty). Choosing its parents also changes the 10 plots.
- Which parents "together": MLST + VirulenceFinder are the data parents; the metadata is a description; the look-up has no entity.

What the display must show beyond the sets (no choice made for the user): the join role of each parent per child; whether a parent holds the entity id (look-up: no); the original parents grouped with the plots they feed; what is outside (plots not fed by the chosen parents, so that "E still in the other 8 figures" is not a surprise).

## 5. File 02 findings after this review

Stand unchanged (independent of the scope):
- An id typed with a leading space or another case removes nothing, no message (0 plots affected). Not rerun; the check is a count at the place. [file 02, run]
- A threshold that removes every row (`gt 1000` -> 0 rows, no error) [file 02, run]; the `na` choice changes the number of entities (19 or 23) and `na: remove` drops null for every operator including `ne`/`not_in` [file 02, run].
- NaN larger than every number; type refusals as sentences.
- The graph's column knowledge unknown at 50/87 nodes and wrong on the marker, against the engine's plan: stands (not rerun).
- Statistic before or after (case 5), N differing per figure (case 2), refusals of column drops (case 4), result-table case (7).

Reworded:
- Headline "the figures a place reaches are recomputed, not the figures the entity leaves": reword to "the figures a place reaches are recomputed; where the entity leaves depends on the join: a place that is the right side of a left join (the metadata) never removes the entity; a place that is the start of the joins (the data originals) does. With every data original chosen together E leaves 17 of 17 figures (16 that held it) and every result table." Not a weakness of the lineage.
- "reach 10 = 9 change but E leaves 2": the metadata scope is the wrong one for removal; for "forget the description" 9 changed is the designed effect.
- Case 6 side effect: a lesson on `na: remove` filters below, not on the lineage.

Withdrawn:
- Any wording that treats "E stays in 7 figures after metadata removal" or "virulence_bar keeps E after ResFinder removal" as a risk of the lineage; they are the designed left-join results and the user chose a scope for a different intent.
- "At the metadata ... a user who wants 'remove this sample' picks the metadata because it is the highest place": only a hypothesis about users; not tested with a user, and the lineage view (section 4) is what addresses it. [reasoned]

Count at the chosen place before confirming: still worth proposing, for ONE purpose only: to catch typing and threshold mistakes the lineage cannot (id not found at the place: 0 rows; filter removes none or all; null rows decided by `na`). It must not claim anything about the figures below: it does not say where E leaves; that is the lineage's job. Cost 0.06 to 0.17 s on the demo [file 02, run]. Also useful: "N entities in the original parent(s) chosen" to make section 5 case 1 visible (E has 1 row in some, 24 in another). Not run again here.

What I did not test: more than one entity at once; real-size data; the plan-book version of "remove from all"; the dialog; an intent needing two places on one path.
