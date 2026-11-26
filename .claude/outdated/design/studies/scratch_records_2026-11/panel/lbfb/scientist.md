# LBFB: scientist and data scientist viewpoint (2026-11-20)

Evidence labels: RAN (a script under `tmpAI/panel/lbfb/scientist/`, Polars 1.40.1), READ (file or ledger line read), reasoned. Nothing in the repository was changed. Scripts: `mini.py`, `q34.py`, `awk.py`, `real.py`, `reach.py` (the last one uses `build_graph` of the real demo recipe). All row numbers below come from an independent plain-Polars replay written in the script, never from the walk (the walk does not exist yet).

Decided lines used (all READ in the ledger): D-0347 (three moves), D-0346 (lines), D-0325 (plan gives names and types), D-0351 (the walk may read a short fixed list of step arguments, each checked against the plan, a disagreement is grey), D-0352, D-0353, D-0337, D-0194, D-0316, D-0318, D-0195, D-0332, D-0322, D-0297, D-0344, D-0326, D-0343.

The test every section applies: a step written at a ticked place must remove exactly the rows (or the column) the user means, at every table and plot the line claims to reach, and nowhere else; a line must never say "same column" for another quantity; and the consequence in rows and plots is on screen before she confirms.

---------------------------------------------------------------------
## A. What LBFB is expected to do: two walk-throughs
---------------------------------------------------------------------

### A.1 My small recipe (MR)

Sources: A(sample_id, mic Float64, country) 5 rows S1..S5 (S5 has mic missing; countries NO, SE, NO, SE, NO). B(sample_id, country, year) 5 rows S1,S2,S3,S4,S6 (years 2022, 2023, 2023, 2024, 2024; countries NO, SE, NO, SE, DK).
- Table A: T1 `[rename country -> origin]`, T2 `[rename origin -> country]` (a rename and a rename back across two tiers).
- Table B: no steps.
- Join J = A, B: T1 `[join left on sample_id, right_ingredient B]`; T2 `[filter year >= 2023, na: remove]`.
- Plots: PA reads A (T3 = T2:A, no own steps); PJ reads J (T3 = T2:J); PK reads J with its own T3 `[select sample_id, mic]`.

Graph (READ `recipe_graph.py` docstring lines 1-20): `DS:A -> T1:A -> T2:A -> T3:PA`; `DS:B -> T1:B`; a join reads the T1 of its ingredients, so `T1:A -> T1:J` and `T1:B -> T1:J`; `T1:J -> T2:J -> T3:PJ, T3:PK`. B has no T2 steps and no plot reads B directly, so T2:B is T1:B. Distinct stored tables: A1, A2, B1, J1, J2 (5), plots PA, PJ, PK.

Baseline rows (RAN `mini.py`): A1 5, A2 5, B1 5, J1 5 (S5: country and year missing after the left join), J2 3 (S2, S3, S4), PA 5, PJ 3, PK 3. J1 columns: sample_id, mic, origin, country, year. The rename made the clash vanish: B's `country` keeps its name in J1 because A's is called `origin` there (RAN: without the rename the plan gives `country`, `country_right`).

#### Walk 1: start `sample_id` at PJ's table (the commonest case: one bad sample, S3)

Start: column `sample_id`, node T3:PJ (= T2:J end, because PJ has no own steps, D-0343).

Move 1, BACK. What it knows and from where:
- the map's edges: T3:PJ <- T2:J <- T1:J <- {T1:A, T1:B}; T1:A <- DS:A; T1:B <- DS:B (`lineage_back`);
- the steps of each node (`recipe_tiers.step_list`, audit steps included): T2:J has a filter that names `year` only, so `sample_id` passes unchanged; T1:J has a join with `on: [sample_id]`: sample_id of J is the join key of both ingredients (`join_keys.key_columns`, D-0351), so the walk goes back into BOTH A and B; T1:A has a rename whose mapping does not name sample_id: unchanged;
- the plan (D-0325): `sample_id` exists in every plan it passes (String): each prediction checked.
Result of move 1: the column exists, as `sample_id`, at T1:A, T1:B, T1:J, T2:J (and T2:A by the continuation below). Source names (`original_name` of input_fields) are a note on the first place, not a line (DESIGN L028).

Move 2, FORWARD. Only the map: `lineage_forward(T1:A)` = T2:A, T3:PA, T1:J, T2:J, T3:PJ, T3:PK; `lineage_forward(T1:B)` = T1:J, T2:J, T3:PJ, T3:PK. The reach does not ask whether the column survives (D-0346: a step on a shared table reaches everything below it). Collapse: a node with no steps is the table before it.

Move 3, BACK AGAIN. For every reached place, along its own path, read the name and type there from the plan and the step that decides it (rename mapping, join keys and suffix, select, drop): here nothing differs, so no name note and no type note on any line. PK: its select keeps `sample_id`: present.

Lines returned (8), each with reach (tables, plots):
1. T1:A tick (4, 3): A1, A2, J1, J2; PA, PJ, PK.
2. T2:A tick (1, 1): A2; PA. (J is NOT reached: it reads A's T1.)
3. T1:B tick (3, 2): B1, J1, J2; PJ, PK.
4. T1:J tick (2, 2).
5. T2:J tick (1, 2): the place she is looking at ("you are here").
6. only PA tick (0, 1).
7. only PJ tick (0, 1).
8. T3:PK (PK has own steps: this IS its only-this-plot line) tick (0, 1).
Gone places: none for sample_id. Counts found: 8 ticked, 0 grey, 0 gone.

Rows (RAN `mini.py`, filter `sample_id != "S3"`, independent replay), after ticking all eight: A1 4, A2 4, B1 4, J1 4, J2 2, PA 4, PJ 2, PK 2. Ticking one line only:

| line ticked | A1 | A2 | B1 | J1 | J2 | PA | PJ | PK |
|---|---|---|---|---|---|---|---|---|
| none (baseline) | 5 | 5 | 5 | 5 | 3 | 5 | 3 | 3 |
| T1:A | 4 | 4 | 5 | 4 | 2 | 4 | 2 | 2 |
| T2:A | 5 | 4 | 5 | 5 | 3 | 4 | 3 | 3 |
| T1:B | 5 | 5 | 4 | 5 | 2 | 5 | 2 | 2 |
| T1:J | 5 | 5 | 5 | 4 | 2 | 5 | 2 | 2 |
| T2:J | 5 | 5 | 5 | 5 | 2 | 5 | 2 | 2 |
| only PK | 5 | 5 | 5 | 5 | 3 | 5 | 3 | 2 |

Two facts a scientist must see before confirming, both RAN: (1) T2:A reaches PA but NOT J (the join reads T1): ticking only T2:A leaves S3 in J1, J2, PJ, PK. (2) T1:B alone leaves S3 in J1 (the left join is based on A): the row stays with `country` and `year` missing (RAN: `S3, mic 4.0, origin NO, country null, year null`), and then J2 loses it only because the recipe's T2 filter drops missing years (J2 3 to 2). So "S3 removed from B" is "S3 emptied in J1, removed from J2": the line must say "removed" or "emptied" per table, not just a number.

#### Walk 2: start `country` at PA (the rename-back and the clash)

Move 1, BACK: T3:PA = T2:A. T2:A has `rename {origin: country}`: `country` here is `origin` at T1:A (mapping, step argument; the plan agrees: T1:A has `origin` and no `country`, T2:A has `country` and no `origin`). T1:A has `rename {country: origin}`: `origin` is `country` of DS:A (mapping; plan of DS:A has `country`). Stop at the source.
Move 2, FORWARD: from T1:A as in walk 1.
Move 3, BACK AGAIN: at T2:A the name is `country` (the start); at T1:A `origin` (note "called origin here"); at T1:J: the join (D-0351: keys, suffix) keeps A's non-key columns under the name they have at T1:A, so A's country is `origin` in J1 and B's `country` is a different column (RAN: both are in the plan of J1: origin, country); T2:J the filter does not name it: `origin`; PJ: `origin` present; PK: the select keeps only sample_id and mic: GONE (a note, not a line).
Lines: T2:A (country), T1:A (origin), T1:J (origin), T2:J (origin), only PA (country), only PJ (origin); T3:PK is not a line (column gone) but is IN the reach of T1:A, T1:J, T2:J. NOT a line: T1:B (its `country` is another column).
Rows (RAN, `country != "NO"`, A's country is NO for S1, S3, S5): ticking all of T1:A, T2:A, T1:J, T2:J, PA, PJ: A1 2, A2 2, B1 5, J1 2, J2 2, PA 2, PJ 2, PK 2. Writing the J line with B's `country` instead removes a different set (RAN: J1 2 rows kept, but B1, A1, PA stay 5).

#### What the walk must not have done (the point of walks 1 and 2)
- Followed names through the plans: walk 2 from `country` at PA would find J1's `country` (B's column) and offer T1:B, and miss `origin` at T1:A and T1:J. (D-0351 exists for this.)
- Read T2:A as an input of J (walk 1 line 2).

### A.2 The demo recipe, `MLST with metadata` (READ the yaml; RAN `real.py`, `reach.py`)

Structure (READ `1_test_data_ST22_dummy.yaml:110-119, 196-203` and the three wrangling files): MLST: T1 `[polars_select [sample_id, scheme, sequence_type]; polars_with_columns sequence_type = replace_strict({'unknown': 'Non Determined'}); polars_fill_null sequence_type 'Non Determined']`. metadata_schema: T1 `steps: []` (no steps). MLST_with_metadata = MLST, metadata_schema: T1 `[polars_join metadata_schema on sample_id, how left]`; T2 `[polars_with_columns era = when(year<2024) Early else Recent; modif_filter year between [2023, 2025], na: remove]`. Plots mlst_bar and year_distribution both read it (RAN: `plots_reading`). Data (RAN): 42 samples in both files, same ids, metadata years 2022 x9, 2023 x8, 2024 x25.

#### Walk 3: `sample_id` at mlst_bar, remove one sample
Move 1 BACK: T3:mlst_bar = T2:MLST_with_metadata (no own steps); the T2 steps (a with_columns that creates `era`, a filter on year) do not name sample_id; T1:MLST_with_metadata: the join `on: [sample_id]`: back into MLST and metadata_schema; MLST's select keeps sample_id. DS names: `sample_id` in both.
Move 2 FORWARD (RAN `reach.py`): from T1:MLST the forward nodes are T2:MLST, T1/T2 of MLST_with_metadata, ST22_Anchor, AR1_MLST_Serotype_Virulence, and the plots virulence_bar, mlst_bar, year_distribution, virulence_variants (4 plots). From T1:metadata_schema: 40 forward nodes, 27 table nodes, 13 plots. From T1:MLST_with_metadata: 1 table node, 2 plots.
Move 3 BACK AGAIN: unchanged name and type at all places.
Lines (those that hold sample_id and are distinct tables): T1:MLST (reach: MLST_with_metadata T1 and T2, ST22_Anchor and AR1 tables, 4 plots), T1:metadata_schema (13 plots), T1:MLST_with_metadata, T2:MLST_with_metadata (2 plots), only mlst_bar, only year_distribution, and the other joins that read MLST or metadata and keep sample_id (decided by their plans; I did not enumerate them).
Rows (RAN `real.py`, independent re-implementation of the tier steps; `between` taken as inclusive: base J2 = 33 = 42 - 9, which matches):
- a 2023-2025 sample (32557144), all four places of this chain ticked: MLST 42 to 41, metadata 42 to 41, J1 42 to 41, J2 33 to 32, mlst_bar and year_distribution 33 to 32.
- a 2022 sample (50677095): MLST 41, metadata 41, J1 41, J2 33 unchanged, both plots 33 unchanged. The T2 filter already excluded it. The honest reading: "table changed" for MLST, metadata, J1, and every other table below metadata; "picture changed: no" for these two plots. Ticking only the T2 or plot line removes 0 rows (every place after the filter): a ticked line that does nothing must read "0 rows here".
- a reach of 13 plots from metadata_schema means a removal ticked at that line changes 13 plots while she looks at 2.

#### Walk 4: `sequence_type` at mlst_bar (a column rewritten twice in tier 1 of its source)
BACK: T2 steps do not name it; the T1 join takes it from the MLST ingredient (metadata has no such column: no clash); T1:MLST: the select keeps it; the `with_columns` names it as a key of `named_exprs` (READ DESIGN F-D: the output names of the common actions are in the step's own arguments): "recomputed by step 2"; `polars_fill_null columns [sequence_type]` names it: "filled by step 3". Source name: `Sequence Type` (`original_name`), with `null_values: ["-"]`.
Lines: T1:MLST (here sequence_type, notes: recoded by step 2, filled by step 3), T1:MLST_with_metadata, T2:MLST_with_metadata, only mlst_bar, only year_distribution (+ the other joins that carry it). Not a line: DS:MLST.
What is true in the data (RAN): raw `Sequence Type` has 0 values `unknown` (so the recode never fires on this file) and 2 missing (the `-`); after step 3 those 2 rows hold the text `Non Determined`. Typing `Non Determined` matches 2 rows at every line; typing `-` or `unknown` matches 0 rows at every line, because the source view shows missing, not `-`. The plan is blind to all of this (RAN `awk.py` D1: plan identical before and after the recode and fill; `st != '57'` keeps 3 rows before and 4 after the fill). LBFB can say "recomputed by step 2 and filled by step 3 before this place"; the row count says the rest.

---------------------------------------------------------------------
## B. What it should do in the hard places (the four questions)
---------------------------------------------------------------------

What the walk must track, per column and per place (one record, built by the three moves; it is the structure of a `Line` plus the sets already in DESIGN section 1):
- `name_here` and `type_here` (engine type string), from the plan at the END of the place;
- `how` in {unchanged, renamed, recomputed, cast, created, dropped} for the step that last touched it before this place, with the step number and action, and `source_column` = the name and place where the identity started (DS name, `original_name`);
- the PATH: the ordered list of (node, step number, action, what it did) from the source to the place (this is what a user reads as "renamed from `origin` by step 1 of T1:A"); for a column present through two paths (a join key), both paths;
- `identity_basis` in {same step-free pass, mapping read and checked, join key equated, grey: cannot follow (action)}: WHY the walk believes it is one column. A line without a basis is not tickable.
- reach as SETS of nodes, split into `reach_tables_with_plot`, `reach_tables_no_plot`, `reach_plots`, and `gone_places` with the step that removed the column.
- the plan was composed per step (U2 of DESIGN), so that drop-then-create in two steps is seen.

### B.1 A rename across two tiers (a to b in tier 1, b back to a in tier 2)

Recommendation that keeps the science right: ONE column, followed by identity, offered at each tier's table under the name it has there (the reading in D-0352's own bracket). Within one tier (a to b to a inside the same list) it is the same column and the intermediate name `b` is not a place at all (no stored table holds it; only per-step plans see it).

Why (RAN `mini.py`): the data are the same values; and joins read T1, so the T1 table is a different place with a different name that a join's column carries. Worked example (MR, walk 2, `country != NO` for A's country):
- one column, three-plus lines ticked: A1 5 to 2, A2 5 to 2, J1 5 to 2, J2 3 to 2, PA 5 to 2, PJ 3 to 2, PK 3 to 2, B1 5 (untouched, B's country is another column).
- the alternative, two columns (the line at T2:A and only PA, but no T1:A, no join): only A2 and PA change (5 to 2). A1 stays 5, J1 5, J2 3, PJ 3, PK 3: A's tier-1 table and everything built from it still hold the NO samples. A figure she exports from PJ still contains them. RAN, row `at A2`.
- a third wrong behaviour, follow the NAME: the line at T1:J named `country` is B's column (J1 5 to 2, A1 and PA stay 5).
Cost of "one column": the line's name differs per place, so the dialog must write the name there (`origin`) and the step it writes uses that name; this is a note, not a choice.
What must be tracked: `how = renamed` with the path, and the check against both plans (the rename's mapping is predicted, T1:A plan has `origin` and no `country`).
Remaining doubt, flagged: the plan CANNOT confirm a swap by rename when the types are equal (RAN: `{a:Int64,b:Int64}` becomes `{b,a}`; the names set is equal), so the check D-0351 describes passes without discriminating. A swap is uncommon but is exactly where a wrong line is confident. Mitigation: a swap (a mapping whose keys and values overlap) is detected from the mapping itself and is shown grey ("names exchanged at step n: cannot be followed by name") unless the marker oracle covers it (E).

### B.2 What the reach counts

Recommendation: both, said apart. "N tables that a plot reads, M further stored tables that no plot reads, K plots", with the rows per table for both groups.
Evidence: the architect verified (READ DESIGN F-B) that adding a step at any place changes the cache keys of the place and all of `lineage_forward`, including joins no plot reads; D-0326 builds every table at opening, so those tables exist, change, and are stored. Demo, from `T1:metadata_schema` (13 plots RAN; 20 tables with unread joins, 16 without READ from DESIGN F-A/Q5).
Worked example (MR plus one extra join JU = A join B that no plot reads, RAN `q34.py`): ticking T1:A with S3: JU 5 to 4 (same as J1). "4 tables, 3 plots" would hide JU. Counting JU only inside the 5 tables would be fine, counting it nowhere is a silent change: the stored table is later read by whoever adds a plot to it, or by a join that is later added, and its content depends on an audit step she never saw listed.
Alternative "only tables a plot reads": shorter, matches what she can see in the plots; but the number she confirms is smaller than the number the stored data change. Alternative "everything in one number": it reads like 20 plots-worth of change; she cannot tell what is visible.
Define "a table a plot reads" once: a distinct stored table with at least one plot below it. A join no plot reads is not a LINE (D-0346, decided) but is in the reach count and in the rows list.
What must be tracked: the sets `reach_tables_with_plot`, `reach_tables_no_plot`, `reach_plots`; never a stored integer.

### B.3 A place in the reach where the column is gone

Recommendation: a note under the line that reaches it, listing each such place with its row change and the step that removed the column; never absent; not a grey line.
Why: such a place IS changed by rows (RAN `q34.py`, `year != 2023` at B1: B1 5 to 3, J1 5, J2 3 to 1, PK 3 to 1; PK's table is `sample_id, mic`, one row S4). Without the note the user sees PK lose two rows and no column to explain it. A grey line says "a place where you could write a step but cannot", which is wrong: nothing can be written there, and a count of lines then mixes ticks and non-ticks.
Alternatives and how each fails: (i) absent: the user cannot tell why PK differs. (ii) grey line: acceptable only if grey lines are never counted as lines in the summary; it also tempts the user to "untick" something that cannot be unticked. (iii) a note alone without the row change: tells the column is gone, hides that rows change.
Distinguish two different absences: (a) KNOWN gone (the plan has no such column and a step is named: select, drop, unpivot, join merged the key): note. (b) UNKNOWN (plan failure, an action outside the closed list): GREY line with the reason, because we cannot say whether the column is there, and we must not let the user tick it. Mixing (a) and (b) in one rendering makes a refused build look like a dropped column.
Turned into rows (unpivot): the column `tet` no longer exists; a filter `tet == 1` has no one-step equivalent at the long table (antibiotic == 'tet' and resistant == 1). Note "became values of `antibiotic`"; no line.
What must be tracked: `gone_places` as (place, step, action, reason code), per start column.

### B.4 The drop of a key column

Recommendation: the dialog opens, key places grey with the reason; the user sees which places are refused and why. But the grey rule must be BROADER than "is a key here": it is "a join key, or named by a later step, or drawn by a plot, anywhere in the reach". RAN `q34.py`: dropping `sample_id` at A1 makes the plan of T1:J fail (`ColumnNotFoundError`); dropping `mic` at A1 (not a key) makes the plan of PK's select fail; dropping B's `country` is fine; dropping `sample_id` at PK only gives `[mic]` and is legitimate.
Why not one plain refusal before the dialog: it is wrong when the column is a key in one place and plain in others (PK above), and it hides that "remove from the plot only" is allowed. Why not only key places grey: a non-key column named by a later step fails just as hard (the build breaks, D-0176).
The robust method (reasoned, uses what the engine already gives): for a drop, the state of each candidate line comes from the PLAN of the candidate audit copy: compose the plans downstream of the place with the drop appended; a PlanFailure downstream = grey with the engine's plain sentence plus the join-key sentence of D-0297 where it is a key. This does not read the recipe's expressions at all.
Worked numbers (MR): drop `sample_id`: lines T1:A, T1:B, T1:J, T2:J grey (join key here or below: T1:J fails), T2:A ticked (no join reads T2:A; PA only; sample_id is not a key there), only PA and only PJ ticked, T3:PK (own select names it): grey "a step of this plot names it". 
What must be tracked: `key_use` (join keys of the reach) and the candidate plans.

---------------------------------------------------------------------
## C. How it should be built, in steps
---------------------------------------------------------------------

Step 0 (no walk; prerequisite). The PlanBook builder (per-step plans, a PlanFailure with its sentence) as a function the walk receives finished. Test: plan equals the real run on every table of both shipped recipes (the measured 108 of 108 becomes a standing test) and equals an independent replay on the fixtures. Needs no open question. User sees nothing.

Step 1 (the smallest useful, trustworthy step): the commonest case, remove a bad sample everywhere. Start column: a column that is a join key or entity key (`key_families`), kind `filter`. Lines come from: map edges, collapse by steps, only-this-plot lines, join keys, plan existence. A place is TICKABLE only when the identity is proved by a "no mention" rule: the column name appears unchanged in the plan before and after every step on the path, and no step on the path names it (rename mapping, `named_exprs` keys, cast columns, fill columns, group_by, drop/select lists). Everything else on the path is GREY with the reason ("step n (action) names this column or changes the columns: not followed yet"). Plus: the counts of rows per table and the plot flags from the audit run, plus the POST-CONDITION CHECK after the audit copy is built (see E): the removed id is absent from every table that holds the key family, every other row of those tables is unchanged. Tests (DESIGN cases): L001, L002, L003, L005 (needs a decision on reach, or both sets), L006, L007, L008, L009, L010, L011, L012, L013, L014, L020, L021, L048, L052, L053, L075, L076, L077, L078 and the mutants M4, M5, M7, M8, M9, M12, M18, M19. What it leaves grey: any place whose path has a rename, a cast, a recompute of the column, an action outside the closed list. What the user sees if the dialog stopped here: a correct, ticked list of tables and plots for "remove this sample", greys with a reason elsewhere, rows per table, before confirming. Needs none of the open questions if the Walk keeps the table sets apart (B.2) and the ordering is the graph's. This is the first step a scientist can already trust; D-0194's "most frequent use case".

What must be true before the less common cases are offered at all (better a grey line than a wrong one): (1) Step 0's equality; (2) the post-condition check passes on both shipped recipes and every fixture; (3) every grey has a reason code from a closed list and the number of greys per recipe is a recorded figure (E); (4) mutants M1, M2, M3, M15 die; (5) a step the walk does not know is grey by construction (default deny).

Step 2: renames, join clashes, key under another name (L015-L019, L021, L023, L028, and L018 after B.1 is confirmed). Needs D-0351 (decided) and the swap detection of B.1. Leaves grey: swaps, renames of a key column that a join keeps for only one side, steps outside the list. User sees: `origin` written on the line where the name differs, a note naming the step.

Step 3: types (L036, L037, L039, L041, L035 after Q10): the value written in the type of the place (D-0202), the note (D-0337). Needs the Q10 answer only for family-versus-exact. Leaves grey: a typed value that cannot be written there (Q12). User sees: the type per line and the value as it will be written.

Step 4: values changed in place, with the note (D-0353): L030, L031, L042-L047. Needs only decided lines. The note names the step; the count is the engine's. Leaves nothing grey, which is why it depends on the count being on screen (see D).

Step 5: gone places and drops (L024, L025, L027, L029, L032, L033): B.3 and B.4. Needs the Q6 and Q8 answers (or both renderings behind one switch).

Step 6: shape-changing and cross-row actions (pivot, unpivot, explode, unnest, group_by, unique, with_row_index, head, sample): default grey, one action at a time moved to understood only with its own fixture and a mutant. In the shipped recipes (READ, counting `action:` across `config/data_analysis_recipes/pipelines`): polars_join 27, with_columns 17, select 13, cast 9, modif_filter 9, rename 6, group_by 5, unique 4, str_strip_chars 4, sort 4, drop 4, unpivot 3, explode 3, unnest 2, str_splitn 2, fill_null 2, with_row_index 1, drop_nulls 1, mutate 1. Steps 1 to 3 cover the first six; the others are grey whenever they touch the start column's path.

---------------------------------------------------------------------
## D. What we will miss
---------------------------------------------------------------------

The plan sees names and types only (RAN `awk.py`: D1, D2, D3 all show the plan identical before and after). For each meaning change, what LBFB can say from a step's own arguments and what only the rows say:

| change | what the plan shows | what LBFB can say | what it cannot say |
|---|---|---|---|
| recode (`replace_strict`) | nothing | "recomputed by step n" if the step names the column | which values moved: RAN D1: `unknown` matches 2 rows before the recode and 0 after |
| fill of missing values | nothing | "filled by step n" (the `columns` argument) | that missing rows became a text; RAN: `!= '57'` keeps 3 rows before, 4 after |
| unit change | nothing (Float64 both) | "recomputed" | that 500 now means 0.5: RAN D2: `t > 1` keeps 3 rows before, 2 after, the same typed number is another quantity |
| aggregation under its own name | nothing | the group keys survive; `val` after `group_by.agg(mean)` is "computed here" | that it is a mean: RAN D3: `v > 2`: 2 rows before aggregation, 1 group after; the means differ (NO 2.0 vs 3.0) |
| deduplication (`unique`) | nothing | "rows are chosen by step n" | which tied row survived: RAN D4: keep first gives lab X, removing X before `unique` keeps lab Y, removing X after removes S1 entirely |
| a join that multiplies rows | the same names | `how`, keys | that rows at J are not samples: RAN D5: J has 4 rows for 2 samples, mean of x in A 1.5, in J 1.25 |
| a filter earlier in the same tier | nothing | the line's tier has a row filter before the place | that the removed sample is already gone: RAN real.py, a 2022 sample changes MLST, metadata, J1, not the two plots |
| a cross-row computation earlier in the tier | nothing | the tier has steps before this place that can compute across rows | RAN D6: z-score kept rows -0.735, -0.49, -0.245 with S4 removed afterwards, -1.0, 0.0, 1.0 if removed before |
| left join (base on the other table) | nothing | the join side | RAN: removing S3 from B leaves the row in J1, emptied |

Things not in DESIGN.md or only partly:
1. NaN is not missing. RAN D7: `v != 1.0` keeps NaN (`[nan, 2.0]`) and drops the null; `fill_null(0.0)` leaves NaN; a computed `0/0` is NaN. A `na: remove` that tests null misses NaN, and a filter written for "missing" never matches it. Not tracked anywhere in LBFB.
2. IDs. RAN D8: ` S1`, `s1`, `S1 ` are different values from `S1`; D12: a join on `S1` and `s1` matches 0 rows. Shipped sources strip at ingestion (`strip: true`), but four recipe steps strip in place (`polars_str_strip_chars`): at a place before the strip the typed id matches 0 rows, at one after it matches. LBFB should report, after the audit run, near-matching ids (case or space differences) still present in any table of the key family. That informs; it does not choose.
3. Key families are by column NAME for the whole recipe (READ `recipe_graph.py` docstring, "provisional choices"). A column called `id` that means two things in two joins is one family: a confident wrong line. Needs to be a per-pair relation (the join that equates them) or a visible assumption.
4. A rename that makes a clash vanish or create one (MR: the rename of A's country removed the `country_right`): the same lines depend on step order in the recipe, so a recipe edit moves the identity.
5. `labels` (display names) per table can differ from the column name; the line must show the name used by the step, and the label the user clicked.
6. Rows versus samples: a table with several rows per sample (RAN D5, 4 rows for 2 samples) makes "rows affected" a poor measure of "samples removed". For a key column, give distinct keys before and after per table (Q21).
7. A step after `head`/`sample`/`unique`: an audit removal after it does not bring other rows in (Q24).
8. Stale PlanBook: a changed data file (headers) with the same recipe keeps the same recipe key; U9 binds the book to the keys, but the file's own content is part of the plan (a pivot's columns come from rows, RAN D15: removing `tet` rows removes the column `tet` downstream). The walk reads no rows; a step upstream can change the column set downstream (L081).
9. An `era` created from `year` (demo T2 step 1): the identity of `era` starts at T2; a user who wants to remove the "Early" samples gets lines at T2 and only-this-plot lines, not T1. LBFB can say "created at step 1 of T2:MLST_with_metadata; its expression mentions `year`" by reading `pl.col('year')` in the expression string, a mention list, information only. The equivalent T1 filter (year < 2024) is the user's choice; it is not offered silently.
10. Audit steps land at the END of the tier (D-0146): a removal ticked only at T2:MLST_with_metadata is after the T2 filter; ticked at T1 it is before `era`. Fine for sample removal; for a value condition on a column that a later step recomputes, the dialog's value and the stored step can mean different things per line (D-0202).
11. A line at a place where the typed value matches 0 rows must read "0 rows here" and not "removes nothing" without a reason: the user may have mistyped (`unknown` vs `Non Determined`).
12. The audit copy for a PLOT with an own T3 is a plot table; a plot that was built with sampled or randomised rendering is outside LBFB.

Where LBFB gives a confident wrong answer: (a) name-based identity through a key family when two columns share a name; (b) a swap with equal types; (c) an in-place recompute whose step does not name the column (e.g. `with_columns` of another column through an expression that mutates it indirectly: not possible in Polars by name; but a `polars_unnest` or `explode` can rewrite columns without naming them: these are in the "outside the list" greys); (d) a cast between two types that the engine reports with the same name (Int32 to Int64): no value change, but D-0337 notes it.
What cannot be known, and must be said: whether the typed value means the same at each place; whether rows are samples; that statistics before the place include the removed rows; what happens to NaN; that a sample's rows in a long table are many.

---------------------------------------------------------------------
## E. Tests of the behaviour once built
---------------------------------------------------------------------

All checks take an expectation computed WITHOUT the walk: an independent replay (O1 of DESIGN), the real engine on altered files, or Polars called by the test.

E1. The counterfactual deletion check (the strongest, on the commonest case). For a shipped recipe and a sample id: (a) build the recipe on a scratch copy of the source files from which every row of that id has been deleted (all files whose key family holds it); (b) build the audit copy with every line of the walk ticked and the filter on that id; compare, table by table and plot by plot (frames, sorted, names and types). Expected: equal, EXCEPT in tables whose tier has a cross-row step before the place (z-score, rank, `with_row_index`, `head`, `sample`, `unique` with ties, aggregates): there the test lists the difference and the list must equal the places where the walk's note "computed across rows before this place" appears. Run on 3 ids per recipe (a 2022 id and a 2024 id of the demo, a missing key). Needs only a small data set (42 samples).
E2. Every column of every table of every shipped recipe as a start: the walk returns a Walk or a plain refusal, never an exception; time recorded; the number of lines equals the independent count (collapse classes by the cache keys, F-B), and the ticked lines plus the grey lines plus the gone places equal the places in the reach.
E3. Marker oracle on text columns (O2): mark the column values in a scratch copy of the files, run the real engine, compare the tables that hold the marked values with the walk's lines (tickable lines must be a subset of the holders, and every holder in the reach must be a tickable line or a stated grey). It catches rename, a clash and a swap (L019) that plans cannot. Numeric columns: O3 only for reach.
E4. Metamorphic checks on a shipped recipe copy: (i) rename a column nothing mentions at one table: the line set is the same, only `name_here` changes; (ii) add a plot on a table: exactly one new only-this-plot line and the reach of every line above it grows by one plot; (iii) add a no-op `with_columns` that does not name the column: nothing changes; (iv) reorder the recipe's plots: the lines are the same set (the order is by graph order); (v) add an audit step at a line, rebuild, and the next walk's lines for the same start are the same lines (collapse changes only where a tier becomes non-empty).
E5. Reach equals effect: for each line of each shipped recipe, add the step through `audit_copy.add_step`, rebuild keys: the set of nodes whose key changes equals `{place} U lineage_forward(place)` (already verified once, F-B, for 58 and 8 places: make it permanent).
E6. Rows per line: for each tick set (none, each alone, all, each adjacent pair) the engine's count equals the replay's count (the MR table above is the model: 8 tables x 7 states).
E7. The grey ledger: for each shipped recipe record the number of (start column, place) pairs that are tickable, grey by reason code, and gone. Fail if it changes without a note. A walk that greys most of a recipe is not working; a walk that greys nothing in a recipe containing `unnest`, `explode`, `group_by` is wrong.
E8. Mutants (M1-M24) as must-fail cases; add (a) a walk that follows the T2 of a source into joins (RAN fact: A2 does not reach J), (b) a walk that counts unread joins only in the reach (B.2), (c) a walk that treats a swap as no change.
E9. Determinism with several PYTHONHASHSEED values; no file, no row, no change of the input (L075-L078).
E10. A plan check on the check: for each step kind in the closed list, the prediction equals the plan on every step of the shipped recipes (L086); for the swap, the prediction cannot be confirmed by the plan, so the test fails if the walk does not mark it grey.

What would count as "LBFB works": (1) E1 holds on the shipped recipes except at the listed cross-row places; (2) E2 returns without failure and with equal counts; (3) E5 and E6 equal; (4) no tickable line whose written step fails to build, and no grey line whose step would have built (E3 and the audit run on every candidate); (5) every mutant dies; (6) the grey ledger is recorded and every grey has a reason; (7) nothing in a table outside the ticked lines' reach differs from baseline (P6).

---------------------------------------------------------------------
## Decided lines put in doubt by LBFB (reported, not reopened)
---------------------------------------------------------------------
- D-0353 with D-0194 and D-0337: a recomputed or aggregated column is "the same column, offered and ticked". For a key removal this is harmless. For a VALUE condition (country, val, a threshold) a ticked line at an aggregated or unit-changed place applies the number to another quantity by default (RAN D2, D3). It stays safe only if the note names the quantity ("mean per group after step n") and the rows per line are shown; both are in the decision, but the note must be first-class text, not a footnote.
- D-0346 (a join no plot reads is not offered) with D-0326 (everything is built): the table exists and changes; D-0346 is consistent only if the reach says so (B.2).
- D-0325/D-0351: "the plan stays the authority" cannot confirm a rename-swap with equal types (RAN); not wrong, but the check that "each reading is checked against the plan" is vacuous there.
- The provisional builder choice in `recipe_graph` (not a ledger line): families by column name for the whole recipe underlie the join-key identity of D-0351 (READ docstring); the decision relies on a provisional builder's choice.
