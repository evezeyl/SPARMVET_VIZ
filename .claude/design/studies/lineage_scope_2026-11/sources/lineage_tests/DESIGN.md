# Lineage walk: the merged test design (architect, data scientist and user viewpoints)

Written 2026-11-20 by the architect viewpoint, merging `scientist_cases.md` (sci C01-C62, harness H1-H5, OQ1-17), `user_cases.md` (user A1-A16, checks chk C1-C17, pitfalls P1-P13, Q1-12) and the architect's own cases. Nothing in the repository was changed. Evidence labels: **verified** (run or read at file:line, scratch scripts in `tmpAI/panel/lineage_tests/architect/`), **reasoned**, **assumed**. Decisions are quoted by ledger number; tags DECIDED / CONFIRM / OPEN / MINE.

Verified facts this page stands on (scripts: `count.py`, `shared.py`, `structure.py`, `reach.py`, `keys_vs_reach.py`, `e1.py`, `e2.py`):
- F-A. The recipe with 17 plots (the "demo", `1_test_data_ST22_dummy.yaml`) has 85 graph nodes (12 DS, 28 T1, 28 T2, 17 T3), 73 non-source nodes (58 of them can take an audit step: the T2 of a table no plot reads cannot, `add_step` refuses it), 35 DISTINCT tables once empty tiers are collapsed, 29 of them with at least one plot below, 6 with none (unread joins and unused sources); an upper bound of 46 lines for a column present everywhere (29 table lines plus 17 "only this plot"). `figshare_integration.yaml`: 14 nodes, 4 distinct tables, 7 lines at most. `demo_abromics.yaml` is a SMALL recipe (9 nodes, 1 join, 1 plot): it is not the demo of the 108 places. The measurement's 108 places are step-level places of the 17-plot recipe (`TABLE_FOR_THE_OWNER.md`, Bverify: plan equals the real run at 108 of 108).
- F-B. On both real recipes, for EVERY writable place (58 on the demo, 8 on figshare), adding one audit step through `audit_copy.add_step` changes exactly the keys of {the place} plus `lineage_forward(place)` (non-DS nodes) and no other key: 0 differences (`keys_vs_reach.py`). This includes joins no plot reads (their key changes too).
- F-C. Polars plan facts (`e1.py`, `e2.py`): a rename swap `{a:b, b:a}` shows as two type changes when the types differ and as NO change when they are equal; `with_columns` replacing a column in place with the same type shows no change; a join with `left_on/right_on` drops the right key (left and inner) and keeps it for a full join; a clash gives `val_right` or the given suffix; an existing column named like the suffix result makes the plan itself fail (`DuplicateError`); `group_by.agg(pl.col("val").mean())` KEEPS the name `val` and the type; `pivot` columns come from the values (removing `tet` upstream removes the column `tet` downstream).
- F-D. `polars_with_columns` names every output column as a key of `named_exprs` (`libs/transformer/.../polars_calls.py:71`, `min_items.py:42`), `polars_rename` has a `mapping`, `polars_select` takes plain names: the OUTPUT names of the common actions are in the step's own arguments, no expression has to be parsed for them.
- F-E. The graph joins read `T1` of their ingredients, never `T2` (`recipe_graph.py:14-16`): a step at `T2:S` of a source read directly by a plot does not reach the joins that read `S`; `T1:S` reaches both. On the demo, `ResFinder` is such a table (T2 has 2 steps, 1 plot reads it directly, 4 joins read it).
- F-F. Main (`libs/utils/src/utils/audit_copy.py`) writes audit steps as marked steps at the end of `steps`; the unmerged branch (`.claude/worktrees/slice-c-audit-form`) writes them in `audit_steps` (D-0332). Both are read through `recipe_tiers.step_list`; the walk must read only through it (a mutant that reads author steps only must die).

## 1. The contract of the walk, in plain words

**What it is.** One pure function in `libs/utils` (proposed `utils/lineage_walk.py`; it imports only `recipe_graph`, `recipe_tiers`, `join_keys`, `action_names`: no Polars, no `app`). For the table and column the user is looking at, it says which places can hold a step, what is true of the column at each, and what each reaches. It reads no row, stores nothing, changes nothing and counts no rows (rows affected are the ENGINE's, D-0316).

**Input**, all in memory: (1) the recipe graph of the recipe in memory, which is the audit copy when an audit is open, so audit steps are ordinary steps (`step_list`); (2) the PlanBook, the engine's plan of every place composed once, a mapping `(node, k) -> Plan | PlanFailure` where `k` is the number of steps applied (a source is `(DS:S, 0)`), a Plan being the ordered (name, engine type), a PlanFailure the engine's reason with the step and the place (D-0342); the app layer builds it (`app/modules/plan_book.py`, the composition `measure/m.py` mode `Bsteps` already does without storing: 0.16 s on the demo) and the walk receives it finished, so it cannot ask twice and a test can hand it a literal; (3) the start: the viewed node and the column's name at the end of it; (4) the kind of step, `filter` or `drop` (the lines are the same; a join-key drop is grey, D-0297).

**Output**: a `Walk`: an ordered tuple of `Line`, the places in the reach where the column is gone (where and by which step), and the counts found, grey, gone (D-0195). A `Line` holds `place` (exactly what `add_step` takes), `covers` (the nodes collapsed into it), `kind` (table or plot), the column's `here` name and type at the END of that place, `name_note` and `type_note` as data (renamed from X by step N; type differs, with both engine types), `source_name`, `state` (tick or grey) with the reason as a code and its parameters, and `reach_nodes`, `reach_tables`, `reach_plots` as SETS (a count is the `len` of a set, never stored). The plain sentence is a second pure function, `describe(line)`.

**The three moves (D-0347).** BACK from the start along the identity of the column (section 1b) to every table where it exists; FORWARD from those to every node that depends on them (the reach, from the graph's edges, whether or not the column survives, D-0346); BACK AGAIN from each dependent along its own path, to read its name and type and where a rename, a cast or a drop sits. Two columns are one only through a rename, a cast, or a join key the join equates (`key_families`: never from equal names alone).

**Places and collapse (D-0346, D-0343).** A node with no steps (author or audit) is the same table as the node before it: `T2` empty is `T1`, `T3` empty is `T2`; `T1` is always a place. A line is one collapsed table, written at its first node; a tier with only audit steps is NOT empty. Every plot also has the line "only this plot" `T3:p`; when its `T3` has steps that is the same place, one line.

**Guarantees.** Same input, same output in the same order (graph order, 1c); never set or dict order; input never changed; no file, clock, random or row. One failing place greys only its own lines; every other line equals the line without the failure. A step the rules do not cover is grey with its name, never a guess. The announced reach equals the nodes whose key changes when a step is written at the line (F-B), and the plots later found affected are a subset of the reach.

### 1b. What a pair of plans (before and after ONE step) says, and what it cannot

| What the pair shows | Derivable from the two plans alone? | What the walk does | Test that proves it |
|---|---|---|---|
| name in both, same type | the name survives; NOT whether its values changed (recode, fill, round, strip, `with_columns` in place: F5 of the scientist file) | same column by name; values are the ENGINE's count | L042, L043, L044, L045 |
| name in both, type changed | a type change; NOT whether it is a cast, a recompute, or a swap (F-C) | read the step: `polars_cast` names it, else grey or "recomputed" (Q3) | L036, L019, L026 |
| one name gone, one new | NOT whether it is a rename or a drop plus a new column | read the step (`mapping`), check the prediction against the plan, else grey | L015, L026 |
| several gone or new | the pairing is not derivable | step arguments or grey | L017, L032 |
| a swap by rename | invisible when the types are equal, two casts when they differ | `mapping` decides; plan only checks | L019 |
| a join | which side a name came from, that a right key was merged away, the suffix | join keys, `how`, `suffix` (hybrid rule); a full join keeps the right key | L021, L022, L023 |
| an aggregation that keeps the name | nothing: same name, same type, other quantity (F-C) | `by` keys survive, other outputs are "computed here" | L031 |
| a select that reorders | order only; the order of columns is not a fact (`order_known`) | identity by name; no line ever depends on column order | L078 |
| a pivot | the names come from the values; the plan reads rows | the PlanBook of the audit copy is compared with the original's (ENGINE) | L033, L081 |
| drop then create in TWO steps | derivable only with per-step plans (end-of-tier plans show a survivor) | per-step plans: the column is new after the create | L026 |
| drop and create in ONE step | not derivable | `named_exprs` / `exprs` name the column: "recomputed" or grey | L026 |

The consequence the owner must see (OPEN, Q2 in section 5): D-0325 chose the engine's plan to say WHERE a column exists and excluded "rules per action" for that. D-0347 asks the walk to say what differs along a path (a rename, a cast, a drop). The plan alone cannot say a rename, and at a join it gives a FALSE place (verified: from `J.val` the name-follower offers `B.val`, which is `val_right` in J) and a missing one. The proposal below is a hybrid: the plan decides existence and type; a CLOSED list of the steps' own arguments names the column at the neighbour place; each prediction is checked against the plan, and a disagreement makes that column grey (and fails a test on every shipped recipe) instead of showing a wrong place.

### 1c. The order of lines (one rule)
Graph order of the place (`RecipeGraph.nodes()`: topological, recipe order among free nodes), the start's own line first when the dialog wants "you are here" (user A16, Q11 in section 5). Never alphabetical, never set order. Tested with several `PYTHONHASHSEED` values (L077).

## 2. The merged list of test cases

Legend. Levels: PURE (the walk as a function on a small recipe, the PlanBook a literal made by the oracle; `libs/utils/tests`), ENGINE (the PlanBook and the audit run on tiny data, `app/tests`), BROWSER (the dialog). Waves: section 4. Properties: P1 no place missed, P2 no false place, P3 the reach right, P4 the note true, P5 rows affected right, P6 nothing changes outside the ticked places, P7 able to fail. A "line" is written `place [tick|grey] reach(tables, plots)`; every plot that holds the column also has its "only this plot" line (D-0346), mentioned only where it matters; a reach counts the line's own table and every table or plot below it, also where the column is gone (D-0346); a plot with own steps counts as a plot, not as a table. "Rows" is the expected result of applying the step; it is the ENGINE part of a case and always compared with the oracle O1 (section 3), never with the code under test. "Wrong" is the implementation the case must kill (mutants M1-M24, section 3).

Fixtures are defined in section 3 (FX-CHAIN, FX-TIERS, FX-REN, FX-JOINS, FX-TYPES, FX-VALUES, FX-ROWS, FX-SHAPE, FX-MISSING, FX-AUDIT, FX-FAIL, R-DEMO, R-FIG).

### A. Structure: places, collapse, reach

### L001 equal_chain
- From: sci C01, C02, C05; user chk C5. Fixture FX-CHAIN. Levels PURE, ENGINE. Wave 1. Props P1 P2 P3 P4 P6.
- Recipe: A has one T1 step (filter val>0), B none, J = A left join B on sample_id (one T1 step, no T2), P1 reads J, P2 reads A. Start: `country` in the table of P1 (= J).
- Lines (4): `T1:A` tick reach(2, 2) [A, J; P1, P2], `T1:J` tick (1, 1), `T3:P1` "only P1" tick (0, 1), `T3:P2` "only P2" tick (0, 1). No `T2:*`, no `T3` line other than the two "only", no line for B (it has no `country`, and is not below A). No name note, no type note on any line (nothing differs: a note on an equal line is a false statement).
- Rows: filter `country != "NO"` with the one NO row joined: A -1, J -(joined rows), P1 and P2 table changed. Ticking only `T1:A` gives the same J, P1, P2 as ticking all four (the later lines are redundant, D-0198, see L057). Result equals O1 for the subsets none, each alone, all.
- Wrong: lists `T2:J` and `T3:P1` as lines (M5); reach of `T1:A` = 1 (M8); drops "only P2" because P2 reads a T1 table directly (M4); merges A and J into one line.

### L002 collapse_by_steps
- From: sci C39 (part), user chk C5, A10; arch. Fixture FX-TIERS. Levels PURE. Wave 1. Props P2 P3.
- Recipe: see FX-TIERS. Start: `sample_id` anywhere (it is in every table).
- Lines (13): `T1:S` (5, 5), `T2:S` (1, 1), `T1:E` (4 or 3, 4: Q5), `T1:M` (5 or 4, 4), `T1:J1` (2, 3), `T2:J1` (1, 3), `T1:J2` (1, 1), and the six plot lines `T3:Ps`, `T3:Pe`, `T3:Pa`, `T3:Pb`, `T3:Pc`, `T3:Pd`, each (0, 1). Not lines: `T1:U` (no plot below), `T1:JU` (a join no plot reads, D-0346 / Q-A17), `T2:E`, `T2:M`, `T2:J2` (empty: collapsed), `T2:U`.
- Property: a table with T2 steps gives two lines, one without gives one (`J1` two, `J2` one). Pc has its own T3 steps: `T3:Pc` is ONE line, not the table line plus an "only Pc".
- Wrong: one line per tier whatever the steps (M5); a plot with T3 steps gets two lines; JU or U offered (M4 inverse); the 13 is computed from the YAML by hand in the test, not by the walk (independent count).

### L003 audit_only_tier_is_not_empty
- From: arch (brief: "a tier that holds only audit steps is NOT empty"); D-0332, D-0346. Fixture FX-TIERS + FX-AUDIT. Levels PURE, ENGINE. Wave 1. Props P1 P2 P3 P6.
- Recipe: FX-CHAIN with two audit steps already in the copy: one at `T2:J` (J has no author T2 steps) and one at `T3:P2`. Start: `country` at P1's table.
- Lines: `T1:A` (reach counts `T2:J` as its own table: tables A, J(T1), J(T2)), `T1:J`, `T2:J` tick (1, 1) [now a distinct table: a different content and key], `T3:P1` only, `T3:P2` (the plot has audit steps at T3: the table line and "only P2" are the same place, ONE line).
- Rows: the plan of `T2:J` has the audit step; the key of `T2:J` differs from that of `T1:J` (cache_keys: `collection_tier2_key` returns the `a2` part, F-B). Removing the audit step brings back the collapse: lines return to L001.
- Wrong: the walk reads author steps only (`recipe_tiers.author_steps`) and collapses `T2:J` (M19); two lines for P2; a dirty copy that leaves `tier2: {steps: []}` after `remove_step` makes a phantom line (checks `remove_step` leaves no tier).

### L004 collapse_equals_key_classes
- From: arch (brief: "collapsing never merges two places with different content"). Fixtures R-DEMO, R-FIG, FX-TIERS, FX-AUDIT. Levels ENGINE (keys only, no data read, file hashes faked). Wave 2. Props P2 P3.
- Method: compute the keys of every node with `data_analysis_recipe_keys` (as `keys_vs_reach.py`). Two nodes are the same table by the walk (`Line.covers`) if and only if their keys are equal AND they are on one chain. Both directions are asserted: equal key, same chain implies same line; a different key implies a different line. Expected on R-DEMO: 35 classes (verified F-A); on R-FIG: 4.
- Wrong: collapse by plan equality (same names and types, different rows after a filter) (M6): the test adds an audit filter at `T2:J` and expects 2 classes; collapse by name; collapse across a join.
- Note: key equality is a necessary check, not a sufficient one (a filter that removes nothing moves a key and no row, `audit_run.py`): the test says so and never claims content equality from keys.

### L005 table_no_plot_reads_is_not_a_line
- From: user chk C6; D-0346 (Q-A17); arch. Fixture FX-TIERS (JU, U). Levels PURE, BROWSER (the dialog). Wave 1. Props P1 P2.
- Recipe: JU = E join M, no plot. Start: `sample_id` at Pe's table. Lines: no `T1:JU`, no `T1:U`. Add one plot reading JU: `T1:JU` appears (reach (1, 1) plus its plot line). Removing the plot removes the line again.
- Also: the reach of `T1:E`: the table JU is IN the reach or NOT is Q5 (OPEN). Whatever the owner chooses, the property tested is `reach_tables == tables whose key changes` or `== those among them that a plot reads`, named in the test, and the other side is asserted to differ by exactly the unread joins (verified on R-DEMO: `T1:metadata_schema` reaches 20 tables, 4 read by no plot, 13 plots; `T1:FastP` 5 tables, 1 unread).
- Wrong: the unread join offered as a line (it holds a tier-2 step that no plot runs, `add_step` refuses `T2` of it: a line that cannot be written); the unread join silently counted or silently not counted.

### L006 shared_source_scope
- From: arch (F-E). Fixture FX-TIERS (E and S). Levels PURE. Wave 1. Props P2 P3. BLOCKED by Q4 (section 5) for the empty-T2 variant.
- (a) S has T2 steps, is read directly by Ps and is an ingredient of J1 and J2: `T1:S` reaches J1, J2 and their plots; `T2:S` reaches only `Ps`. A step at `T2:S` must NOT reach J1 (the join reads T1). Expected reach `T2:S` (1, 1).
- (b) E has NO T2 steps (the same situation, the empty tier): `T2:E` collapses into `T1:E` by D-0346, so the user cannot choose "all plots that read E directly, but not the joins that read E": the only way is one "only this plot" step per plot. The walk returns the collapsed line; the case records the lost scope and expects the owner's answer (Q4). Variant tests both rules (collapse: one line `T1:E` (4,4); keep: a second line `T2:E` (1,1)) so the answer is a one-line change.
- Wrong: reach of `T2:S` includes J1 (M9: forward over the wrong edge); the `T2` of a schema read as the input of a join.

### L007 several_plots_one_table
- From: sci C40; user A9, chk C7, C8. Fixture FX-TIERS (J1: Pa, Pb, Pc) and a six-plot fixture variant FX-SIX (the recipes have at most 3 plots on a table: verified, `figshare_triple_join`). Levels PURE, ENGINE. Wave 1. Props P3 P6.
- Lines for a column of J1: `T1:J1`, `T2:J1` (3 plots), "only Pa", "only Pb", "only Pc". With six plots on J: reach (1, 6) and six "only" lines; the names are in the set.
- Rows: ticking only "only Pb": J1 unchanged, Pa and Pc unchanged, Pb changed; flags table changed / picture changed for Pb only. Ticking `T2:J1` alone changes all three.
- Wrong: "only Pb" writes at the table; reach (1, 1); the plot count is the number of lines instead of the set.

### L008 plot_with_own_tier3
- From: sci C39; user A10; D-0347 (required: "a plot with its own tier 3 steps"). Fixture FX-TIERS (Pc). Levels PURE, ENGINE. Wave 1. Props P1 P3 P5.
- Recipe: Pc has T3 steps [filter val>0, rename country->origin, drop lab]. Start: `country` at Pa's table. Lines: `T2:J1` (reach 3 plots: Pa, Pb, Pc), "only Pa", "only Pb", `T3:Pc` ONE line with `here = origin` and a name note "renamed from country by step 2 of the plot's own steps", reach (0, 1). Start at Pc's table with `origin`: the same set, `here` of the others is `country`.
- Rows: audit step on `origin` at `T3:Pc` is written AFTER the plot's own steps (end of list: `audit_steps`); a step at `T2:J1` removes k rows from J1; at `T3:Pc` the count is at most k (its own filter already removed some). Compare O1.
- Wrong: the line for Pc is missed because it is also in the reach of `T2:J1` (M4); the step written at the start of the plot list; two lines for Pc.

### L009 plot_reads_t1_directly
- From: sci C41; D-0346. Fixture FX-CHAIN (P2 reads A). Levels PURE. Wave 1. Props P2 P3.
- Lines for a column of A: `T1:A` (2, 2) and "only P2" (0, 1). If P2 is the ONLY reader of A (no join): `T1:A` (1, 1) and "only P2" (0, 1) are both lines (D-0346 says each plot has its own line); their effect on the plot is the same, on the table A different. The case records that both are listed and that ticking both writes two steps with the same effect on P2. (Q12 of the scientist is answered by D-0346: no exception.)

### L010 table_read_by_two_joins
- From: sci C56. Fixture FX-TIERS (S in J1 and J2). Levels PURE, ENGINE. Wave 1. Props P3 P6.
- `T1:S` reach counts J1 and J2 and their plots once each; a step at `T1:J1` does not touch J2 (rows of J2 equal the baseline).
- Wrong: a table counted twice (M8), J2 touched.

### L011 join_of_join_is_refused
- From: sci C29; D-0344 (a join that takes another named join is NOT built). Fixture FX-JJ (J1 = A join B; J2 = J1 join C). Levels PURE, ENGINE. Wave 1. Props P1 P7.
- Verified: `recipe_graph` DRAWS the chain (`recipe_graph.py:17, 40-42`, "provisional") while the engine refuses (`orchestrator.py:370-375`). So `lineage_forward(T1:A)` includes `T1:J2` although nothing builds it. The walk must not report a reach through a chain the engine does not build, and must not silently walk only the first level: it returns a refusal (`WalkRefused`: "join J2 reads join J1: not built, D-0344") before any line. The ENGINE half: the PlanBook has a `PlanFailure` for J2; the load gate gives the plain refusal.
- Wrong: reach includes J2 (M8); J2 silently dropped.

### L012 reach_independent_of_survival
- From: sci C55, C13; arch (brief). Fixtures FX-CHAIN + aggregation, FX-TIERS. Levels PURE. Wave 1. Props P3.
- A column that is dropped by one table's T1 select: the table is still in the reach of the source line (it receives the removed rows), `Walk.gone` lists it with the step that removed the column ("year is not kept at step 3 of T1:Quast_with_metadata").
- Property over every start in FX-TIERS: `reach_nodes(line) == {place} U lineage_forward(place)` minus DS, whatever the plans say. Test mutates the PlanBook (the column removed everywhere downstream) and asserts the reach sets do not change (M7 dies).
- Wrong: the reach counts only the holders (M7).

### L013 plot_counted_once
- From: arch (brief: "a plot counted once when it reads a table through two paths"); sci C55. Fixtures FX-CHAIN (the key `sample_id` is in A and B), FX-ROWS (a key in three sources, two joins), FX-SELF (a self join, the ingredient listed twice). Levels PURE. Wave 1. Props P3.
- In this graph a plot has ONE parent (`T2:target`), so the double path is made by the walk itself: a column that exists in several tables (a key in A and B) is reached forward from EACH of its occurrences, and J and its plots are reached twice. The reach is the UNION as a set: `reach_plots` and `reach_tables` are frozensets, the count shown is `len` of the same set, and the structure holds no `int` count field (a count kept apart is a second store that can disagree). A self join (`join_keys.self_join`; `recipe_graph._ingredients` keeps one edge) gives one table, not two.
- Wrong: counts kept as integers added per path (M8).

### L014 same_set_from_any_start
- From: user chk C16; arch. Fixtures FX-TIERS, FX-REN. Levels PURE. Wave 1. Props P1 P2 P4. (property)
- For every table that holds a column of one identity (every start place), `{line.place}` and the `reach` of each line are the same set; only the "you are here" marker and the notes (name, type, relative to the start) move. Test loops over all starts of each fixture.
- Wrong: the walk goes back only (starts higher in the lineage give more lines) (M1, M9).

### B. Identity along a path: renames, joins, drops, new columns

### L015 rename_on_one_path
- From: sci C03; user A7, chk C10; D-0347 (required: "a column renamed on one path only"). Fixture FX-REN. Levels PURE, ENGINE. Wave 1. Props P1 P2 P4 P6.
- Recipe: A and B both carry `country`; `T1:A` renames `country` to `origin`, B unchanged; plots Pa reads A, Pb reads B; no join. (a) Start `origin` at Pa: lines `T1:A` (here `origin`, source_name `country`, name note "called `origin` here, `country` in the source file"), "only Pa". No line at B. (b) Start `country` at Pb: `T1:B`, "only Pb"; NOT `T1:A`, although A's source file has a `country` header and the pair of plans of A's source shows the name (the source place is not a line; the plan of `T1:A` has no `country`).
- Rows: the step at `T1:A` is written with `origin`; A loses the matching rows; B, Pb unchanged (P6, compare O1).
- Wrong: matching by name over plans offers B for (a)'s identity or A for (b) (M1); no name note on a line where the name differs from the start's (M11).

### L016 same_name_different_column
- From: sci C07; arch. Fixture FX-REN. Levels PURE. Wave 1. Props P2 P4 P5 P6.
- Recipe: `T1:A` renames `a_year` to `year`, `T1:B` renames `b_year` to `year`; Pa reads A, Pb reads B. Start `year` at Pa: lines `T1:A`, "only Pa". `T1:B` is NOT a line although its plan has a column `year` of the same type: same name and same type are not the same column.
- With the join JAB (A join B on sample_id, B's `year` becomes `year_right`): start `year` in JAB gives `T1:A` and `T1:JAB`; start `year_right` gives `T1:B` and `T1:JAB`. The two choices have different line sets.
- Rows: removing year 2022 at `T1:A` leaves B untouched. The count per line (ENGINE) would show B losing rows if B were offered.
- Wrong: follows the name through every plan (M1).

### L017 rename_on_all_paths_and_join_clash
- From: sci C04, C25; user A8. Fixture FX-REN, FX-JOINS. Levels PURE. Wave 1. Props P1 P2 P4.
- Recipe: A(sample_id, val), B(sample_id, val), J = A left join B on sample_id: J has `val` (A's) and `val_right` (B's). Start `val` at J: lines `T1:A` (here `val`) and `T1:J`; NOT `T1:B`. Start `val_right`: `T1:B` (here `val`: B's own name; note "called `val` here, `val_right` after the join") and `T1:J` (here `val_right`).
- Verified (e1.py E9): the plan alone cannot tell which side `val` or `val_right` came from; B has a `val` too, so a plan-only walk offers B for J's `val` (a FALSE place: a step written on B) and offers nothing for `val_right` (a MISSED place).
- Rows: the step written at `T1:B` for the second choice uses `val`, never `val_right` (the build would fail: D-0176), at `T1:J` it uses `val_right`.
- Wrong: M1, M2 (plan-only identity).

### L018 rename_back
- From: sci C06; OQ1. Fixture FX-REN-BACK (A: `T1` rename country to origin; `T2` rename origin to country; plot P reads A). Levels PURE. Wave 1. BLOCKED by Q1 (section 5, U1 in section 6). Props P1 P4.
- Start `country` at P. By identity (the walk back to the source through both renames): lines `T2:A` (here `country`), `T1:A` (here `origin`, note), "only P". By name-only: `T1:A` is missed. The case asserts the identity reading and states it as the proposal; it is the test of "same name does not prove the same column and a different name does not prove a different one".
- Rows: all three steps remove the same rows.

### L019 swap_by_rename
- From: arch (section 1b). Fixture FX-REN-SWAP (A(a: Int, b: Str, c); T1 rename {a: b, b: a}; plot P reads A) and the equal-types variant A(a: Int, b: Int). Levels PURE. Wave 1. Props P1 P2 P4.
- Start `b` at P (it is the old `a`): `T1:A` is a line with `here = a` and a name note "called `a` here". Verified (e1.py E1, E2): the pair of plans shows two type changes when the types differ, and NOTHING when equal; a plan-only walk says `b` at `T1:A` (a false place: the step would filter the other column).
- Expected line is produced from the step's `mapping`, and the plan is the check (the predicted names equal the plan: a mapping that disagrees with the plan makes the line grey).
- Wrong: M2, M3.

### L020 case_only_difference
- From: user A7 (`selected_virulence_genes` / `Selected_Virulence_Genes`, AR1 vs ST22). Fixture FX-REN (two tables whose column differs only in case). Levels PURE. Wave 1. Props P2 P4.
- Names are compared exactly (Polars is case sensitive). Start `Selected_Virulence_Genes` at the ST22 table: `T1:ST22` only; the AR1 table is not offered (its column is a different name); a join of the two keeps two columns. The line shows the exact spelling.
- Wrong: case-insensitive match (a silent merge).

### L021 key_under_another_name
- From: sci C31; D-0022 ("remove from all tables"). Fixture FX-JOINS (A(sample_id), B(isolate), JK = A left join B left_on sample_id right_on isolate; plots Pk on JK, Pb on B). Levels PURE, ENGINE. Wave 1. Props P1 P2 P4 P6.
- Verified (e1.py E8): after a left or inner join the right key `isolate` is gone from J: only `sample_id` remains. Start `sample_id` at JK: lines `T1:A`, `T1:B` (here `isolate`, note "the join key of B: called `isolate` here", from `join_keys.key_columns`), `T1:JK`, "only Pk", "only Pb". Without the B line S3 would remain in B and in Pb after "remove from all tables": a silent partial removal.
- Variants: B also has its own `sample_id` (a different field): it is NOT offered (P2); the key renamed AFTER the join (`sample_id` to `id` at T2 of JK): start `id`, the walk goes back to `sample_id` at the join key and on to `isolate`.
- Rows: removing S3 at every line: S3 is absent from A, B, JK, Pk, Pb (oracle O1); count per table = the number of S3 rows there.
- Wrong: M16 (join keys not read).

### L022 full_join_keys
- From: arch (F-C: a full join keeps the right key). Fixture FX-JOINS (how: full). Levels PURE. Wave 1. BLOCKED by Q9 (section 5). Props P1 P2.
- J has `sample_id` (A's) and `isolate` (B's) as TWO columns; rows only in B have `sample_id` null. Start `sample_id` at J: `T1:A`, `T1:J`. Is `T1:B` offered (the join equates the keys, but a filter on J's `sample_id` does not remove B-only rows)? Two honest outputs: a line at J for `sample_id` plus a note that rows only in B keep a null there, and B offered with its own name. The walk must not merge the two columns silently.
- Wrong: treats `isolate` as gone (as in a left join), or as the same column as `sample_id` (M16).

### L023 suffix_parameter_and_plan_failure
- From: sci C25 (parametrised suffix); arch (e1.py E11). Fixture FX-JOINS. Levels PURE, ENGINE. Wave 1. Props P2 P7.
- (a) Join with `suffix: "_b"`: J has `val` and `val_b`; the lines follow the suffix given, not `_right`. (b) A right table that already has a column named `val_right` together with a clash on `val`: the engine's plan FAILS (`DuplicateError`, verified). The PlanBook holds a `PlanFailure` for J; the lines for J and below are grey with the engine's reason in plain words (with the step and the place, D-0342); the lines above J (A, B) are unchanged from a run without the failure.
- Wrong: the suffix `_right` hard-coded; a plan failure that empties the list or turns J's lines tickable.

### L024 drop_on_one_path
- From: sci C13, C16; user A5; D-0347 (required: "dropped on one path only"). Fixture FX-TIERS variant (a table whose T1 `select` drops `country` on one of two joins). Levels PURE, ENGINE. Wave 1. Props P1 P2 P3 P5.
- Recipe: source S has `country`; join J1 keeps it, join J2's T1 select drops it; plots P1 on J1, P2 on J2. Start `country` at P1: `T1:S` (reach counts J1, J2, P1, P2), `T1:J1`, "only P1". `T1:J2` is NOT a line (the column is gone at the end of its T1: nowhere to write it); `Walk.gone` has "country is not kept at step n of T1:J2" and P2 is still IN the reach of `T1:S`.
- Rows: ticking `T1:S`: J2 and P2 change although `country` is gone there (they receive the removed rows): flags "table changed" for P2, "picture changed" only when the plot draws rows or `country`. Not counting P2 would hide a change (P3).
- Wrong: follows the name and offers a tickable `T1:J2` that fails at build (M2); drops P2 from the reach (M7).

### L025 plot_dropped_column
- From: sci C13 (OQ4); user Q6. Fixture FX-TIERS (Pc). Levels PURE, BROWSER. Wave 1. BLOCKED by Q6 (section 5). Props P2 P3.
- Pc's own T3 drops `country`. Start at Pa. "Only Pc": the column is absent at the END of Pc's T3, where the audit step would go. The three possible outputs (absent; grey with "dropped by this plot's own steps"; a note under the reach line) are all tested for the same facts: no tickable line, Pc still in the reach of `T2:J1`.

### L026 drop_and_recreate_same_name
- From: sci C14; arch (per-step plans). Fixture FX-REN-NEW (A: T1 step 1 `polars_drop country`, step 2 `polars_with_columns {country: "X"}`; B untouched with the original `country`; plots Pa, Pb). Levels PURE. Wave 1. Props P1 P2 P4.
- (a) Start `country` at Pa: the column is the NEW one; the walk stops at A (the creation step); `T1:A` is a line with a note "created at step 2 of T1:A, not the column of the source file". (b) Start `country` at Pb: lines `T1:B`, "only Pb"; A is NOT offered although its plan has `country` of the same type.
- Verified (section 1b): drop and create in TWO steps is derivable only from per-step plans; end-of-tier plans show a survivor by name. In ONE step (`select` with a computed `country`, or `with_columns` replacing it) nothing in the pair of plans shows it: `named_exprs` names it (F-D) and the line says "recomputed here" (L030).
- Wrong: M1 (name-based) merges the two columns.

### L027 drop_in_the_middle_of_a_tier
- From: sci C15. Fixture FX-CHAIN variant (A's T1: step 1 `select` without `country`). Levels PURE, ENGINE. Wave 1. Props P2 P7.
- The column exists at the source and at the start of T1 but not at the end: no line for `T1:A` (an audit step goes after the recipe's steps, so it would name a column that does not exist; D-0176 would stop the build). A line offered here would fail in the audit run: the ENGINE half runs it and expects the plain message, proving the PURE rule is the right one.

### L028 source_view_and_source_name
- From: user A7 ("ResFinder (source file): here the column is called `predicted_phenotype`"); arch Q7. Fixture FX-REN (T1 renames). Levels PURE, BROWSER. Wave 1. BLOCKED by Q7 (section 5). Props P1 P4.
- `DS:S` is not a place (it has no step list, D-0332, `audit_copy._holders`: only T1, T2, T3). So the source name is `Line.source_name` on the first place of the path and a sentence ("in the source file: `predicted_phenotype`"), never a line. A start from a Source view (HOME's Source view, D-0310) is `DS:S` with the source name; the first line is `T1:S` with `here` = the renamed name.
- Wrong: a tickable "source" line (no place to write it).

### L029 key_drop_is_refused
- From: sci C16; user A5, chk C15; D-0297, D-0322. Fixtures FX-CHAIN, FX-JOINS. Levels PURE, ENGINE. Wave 1. Props P2 P7. Partly BLOCKED by Q8 (section 5).
- Kind `drop`, column `sample_id` (a join key and a declared entity key): every line where it is a key is grey with D-0297's sentence ("Column [c] is a join key, cannot be dropped. Use a row filter or row exclusion instead."); a non-key column of the same table drops fine; a composite key; a key present on one table only; with kind `filter` the same lines are tickable. The rule is `join_keys.key_drop_problem` (ONE rule, asked by `add_step`, the integrity check and the walk); a test fails when the walk and `add_step` disagree on any place of any fixture.
- Wrong: the walk re-implements the rule (M17: grey and tickable disagree with `add_step`).

### L030 recomputed_in_place
- From: arch (F-D); OQ6. Fixture FX-VALUES (T1: `with_columns {virulence_raw: pl.col('virulence_raw').cast(...).str.split(',')}`, as the demo does at `VirulenceFinder_wrangling.yaml:4-6`). Levels PURE. Wave 1. BLOCKED by Q3. Props P1 P4.
- The step's `named_exprs` key is the chosen column: the plan is unchanged by name; the list type may change. The line after the step carries a note "recomputed by step n (polars_with_columns)". Whether the identity continues (same column, transformed) or ends (new column) is Q3; the structured note is the same either way, only `reach and lines` differ. The case runs both rules.
- A `with_columns` that does not name the column leaves it unchanged with no note (a note on every with_columns would be noise: 12 such steps in the demo).
- Wrong: no note (the user believes the earlier and later values are alike); a note on every column of the table.

### L031 aggregation_keeps_the_name
- From: sci C17, C17b; arch (e1.py E14). Fixture FX-VALUES (A(country, year, val); T2 `group_by country, year` then `agg(pl.col('val').mean())` which KEEPS the name `val`). Levels PURE, ENGINE. Wave 1. BLOCKED by Q3. Props P3 P4 P5.
- Start `val` at the plot's table. The pair of plans shows the same name and type (verified); the quantity is a mean. Group keys survive (`country`, `year`: lines before and after the grouping, "after a grouping: removes groups, not rows"); `val` after the step is "computed here" (identity ends at the grouping, Q3). Rows (ENGINE): filter `year != 2022` at T1 removes 3 of 6 rows and changes the means; at T2 it removes 2 of 5 groups and leaves the means unchanged: the plot table differs; counts in rows versus groups.
- Wrong: treats the mean as the same column (M1, M2).

### L032 unpivot_column_becomes_values
- From: sci C37; user pitfall P8. Fixture FX-SHAPE (wide W(sample_id, amp, cip, tet), T1 `unpivot` index sample_id on [amp, cip, tet] to (antibiotic, resistant)). Levels PURE, ENGINE. Wave 1. Props P2 P4 P5.
- Start `antibiotic` at the long table: `T1:W` with note "created at step 1 from the columns amp, cip, tet". Start `resistant`: the same. A column `tet` is NOT offered anywhere (no place has it as a column: "turned into values of antibiotic at step 1"); `sample_id` survives (kept as index): removal of S3 removes 3 rows per sample.
- Wrong: offers `T1:W` for `tet` (M2).

### L033 pivot_values_become_columns
- From: sci C38; user P13; arch. Fixture FX-SHAPE (long L, T1 `pivot` index sample_id, columns antibiotic, values resistant). Levels PURE, ENGINE. Wave 1 (PURE), wave 2 (ENGINE). Props P1 P2 P3 P4.
- Start `amp` at the wide table: the line exists only at the wide table, note "created at step 1 by a pivot from the values of `antibiotic`"; not offered at the long table. Start `antibiotic` at the long table: `T1:L` and, in the reach, the wide table where `antibiotic` is gone ("became the columns amp, cip, tet": a note, no line). The plan of a pivot reads rows (Polars, verified e2.py); the PlanBook builder is the ONE place allowed to read rows, only for pivot, sample, describe (L080).
- See L081 for the effect of a step upstream on the column set downstream.

### L034 unknown_step_is_grey
- From: arch (the closed list of section 1b). Fixture FX-VALUES with a step whose action is outside the list and renames or adds names (for example `polars_unnest`, `polars_explode`), and a step of the list whose prediction the plan contradicts (a rule that disagrees with the engine). Levels PURE. Wave 1. Props P2 P7.
- The names that appear or vanish at the step cannot be followed: the lines through them are grey "cannot follow step n (action): the walk has no rule for what it does to this column", never tickable, never guessed; the lines that do not pass the step are unchanged. A mutant that fills the rule table from the plan (guesses a rename from "one gone, one new") must die.
- Wrong: M15.

### L035 type_family_rule
- From: arch (section 6, U5); D-0337. Fixture FX-TYPES. Levels PURE. Wave 1. BLOCKED by Q10 (section 5). Props P4.
- Whole numbers `Int32` and `Int64`, decimals `Float32` and `Float64`, `String` and `Categorical`, `Date` and `Datetime`. D-0337 says "another type" gets a line note. If the comparison is exact on engine type strings, `Int32` versus `Int64` makes a note that says "whole number here, whole number there": noise and a false statement. The case stores both engine strings in the note and tests the rule the owner picks; until then the test fixes exact comparison and a families table side by side.

### C. Types along a path

### L036 cast_on_one_path
- From: sci C08; user A4, chk C10; D-0337, D-0347 (required: "cast to another type on one path only"), D-0202. Fixture FX-TYPES. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (value, rows). Props P4 P5 P6 P7.
- Recipe: A(sample_id, year: Int64); J = A join B; `T2:J` casts `year` to String; plot Pc reads J, plot Pi reads A. Start `year` at Pi (whole number). Lines: `T1:A` (Int64, no note, reach (3, 2)), `T1:J` (Int64, no note, (2, 1)), `T2:J` tick (1, 1), here `year`, type_note "text here, whole number at the place you chose" (D-0337: ticked, the difference written), "only Pc" (String, same note), "only Pi". 
- Value: the user typed 2022. At `T1:A` the written step holds the integer 2022, at `T2:J` and `T3:Pc` the text `"2022"` (D-0202: written in the type of THAT place, per line); the dialog shows the value per line. The build of the audit copy succeeds (comparing a whole number with text FAILS at run time, verified in the scientist file F2).
- Rows: removing 2022 at A removes 2 rows of 6; the later steps are redundant. Compare O1.
- Wrong: the same typed value written at every line (a hard error at the text place, M20); the line missing for the text place; a note with no type.

### L037 cast_lossy
- From: sci C09; user A4b, chk C12; D-0202, D-0203. Fixture FX-TYPES (L50 Float64 values 2.0, 2.4, 2.5, 3.0; `T2:J` casts to Int64 by rounding down). Levels PURE, ENGINE. Wave 1 (type note), wave 2 (value, rows). Props P4 P5 P7. Partly BLOCKED by Q12 (section 5).
- Lines: `T1:A` (decimal), `T1:J` (decimal), `T2:J` (whole number, note "decimals were cut off by a step of the recipe: the same condition can keep different rows here"). Typing 2.0 removes 1 row at the decimal place and 2 at the whole-number place (2.0 and 2.4 both become 2): D-0203's warning with the count per line. Typing 2.5 cannot be written as a whole number: refused with a plain sentence for that line (D-0202); the number shown for that line is the refusal, never 0.
- Rows: user's `L50 >= 8.5` on the demo: the rows kept at the decimal place and at the whole-number place are both reported (R-DEMO, `QA_L50_integer`: decimal at 5 places, whole at 3).
- Wrong: silent conversion with no count (M10); a refused value written as 0 rows.

### L038 cast_to_category_and_missing
- From: sci C10. Fixture FX-TYPES. Levels PURE, ENGINE. Wave 2. Props P4 P5.
- Text cast to categorical at T2: the lines are `T1:A` and `T2:A` with the type note; a value that exists gives the same count at both; a value absent from the data gives a plain "no row matches here" at both. A text-to-number cast of a non-number makes missing values at the later place and none at the earlier: the two lines show different counts when the missing tick differs (the cast creates missing values the earlier place does not have).

### L039 cast_round_trip
- From: sci C11. Fixture FX-TYPES (T1 int to text, T2 text to int). Levels PURE. Wave 1. Props P1 P4.
- One column through three types: lines `T1:` (text note), `T2:` (the start's type). Wrong: the round trip is read as "a column disappears and a new one appears" and the T1 line is missed.

### L040 cast_to_date
- From: sci C12; OQ3. Fixture FX-TYPES (d: String "2022-03-01" cast to Date at T2). Levels PURE, ENGINE. Wave 2. BLOCKED by Q13. Props P4 P7.
- A value typed at the date place must be a date (refusal otherwise, never a silent range); at the text place it is the text. Whether a date is an allowed audit value at all is Q13.

### L041 float_and_integer_key
- From: sci C61. Fixture FX-TYPES (`year` read as Float64 from one file and Int64 from another, joined). Levels PURE. Wave 1. Props P4.
- Note "decimal here, whole number at your place" and the value written as `2022.0` or `2022` per place (L036's rule); a join on mixed key types is the engine's own matter, the walk reports the two types.

### D. Values changed without a change of the plan (ENGINE: only the rows tell)

All cases here assert the same thing from the other side: the PURE walk says "same column" (the plan is blind, F5 of the scientist file), so the ONLY protection is the count of rows affected per line (D-0316), measured on the audit copy. The tests prove the count, and prove that the walk does not claim more than the plan shows.

### L042 recode_in_place
- From: sci C20; OQ8. Fixture FX-VALUES (S(sample_id, country: Norway x3, Sweden x2, NO x1); T1 keeps; `T2:J` recodes Norway to NO; plot P reads J). Levels ENGINE. Wave 2. BLOCKED by Q20 (partly answered by D-0203). Props P4 P5 P6 P7.
- Start `country` at P (values NO, Sweden), type NO. Lines `T1:S` and `T2:J`, both tick, no type or name note (the plan is blind). Typing `"NO"`: `T1:S` removes 1 row, `T2:J` removes 4 (3 recoded plus the original). The dialog shows 1 and 4 (counts by really evaluating each place's filter on the audit copy). A user who types "Norway" removes 0 rows everywhere and is told "no row matches here".
- Wrong: the same count copied to both lines; no count (P5); the count read from the start place only.

### L043 fill_in_place_and_the_missing_tick
- From: sci C21, C36; D-0042 (every filter step states `na: keep|remove`, no default; HOME may preselect with a visible tick and a count). Fixture FX-VALUES (val Float64 with 2 missing; a fill with 0.0 at T1 of one table and in a downstream T2 of another). Levels ENGINE. Wave 2. Props P5 P7.
- Matrix (tick on/off) x (place before the fill / after the fill) for `val != 0.0`: counts 1 and 3 with the tick "keep missing", 3 and 3 without (Polars drops missing rows in `!=`, verified F1); asserts all four. The tick is a property of the step (D-0042), the counts differ per line.

### L044 round_in_place
- From: sci C22. Fixture FX-VALUES (val 2.34, 2.36, 2.41; `T2` rounds to 1 decimal). Levels ENGINE. Wave 2. Props P5.
- `val != 2.4` removes 2 rows after the round and 0 before: "no row matches here" at the earlier line, not a silent 0.

### L045 string_case
- From: sci C23, C59, C60. Fixture FX-VALUES (sample_id S1, s1; `T2` lowercases). Levels ENGINE. Wave 2. Props P5 P6.
- `"s1"` removes 0 rows before the lowercase and 2 after; the comparison is exact (no silent folding) and the written step holds exactly what was typed (no strip, no lower). A list of values with one absent here ("S9 matches no row here") gives a line note, not an error.

### L046 count_changes_value_not_rows
- From: sci C18. Fixture FX-VALUES (T2 `group_by country` with `n = count()`; plot draws `n`). Levels ENGINE. Wave 2. Props P5 P7.
- A filter at T1 on `val > 1` leaves the T2 row count unchanged and changes `n`: flags "table changed" and "picture changed" come from comparing CONTENT (D-0318), not row counts. Wrong: an implementation that compares counts reports "unchanged".

### L047 statistics_before_removal
- From: sci C19; OQ7. Fixture FX-VALUES (T1 step `z-score of val`; audit filter at the end of T1). Levels ENGINE. Wave 2. BLOCKED by Q23 (words). Props P4 P5.
- Audit steps go at the end of the tier (D-0146, D-0332), so the kept rows keep the z-scores computed WITH the removed rows: the test asserts the baseline z-scores of the kept rows are unchanged, and that the line carries a structured fact "a step before this place computes over the whole column (z-score, mean, rank)". Whether and how it is said is Q23.

### E. Joins and removal by key (ENGINE for the counts; the lines are PURE)

### L048 join_key_one_column
- From: sci C24. Fixture FX-ROWS. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (rows). Props P1 P3 P5 P6.
- A(S1..S5), B(S1..S5 or fewer), J inner on sample_id. Start `sample_id` at J: lines `T1:A`, `T1:B`, `T1:J`, "only P". A filter removing S3 at `T1:J` only: A and B keep S3. At `T1:A` only: J loses S3, B keeps it. A row only in B that the inner join already dropped: the B line says "1 row in B, 0 in the join's result".
- Wrong: only `T1:J` (the key exists at A and B: P1); reach of `T1:A` forgets J.

### L049 left_join_before_after
- From: sci C26, C35, A3 of the user. Fixture FX-ROWS (A: S1..S5; B: S1..S3 with lab X, X, Y; J = A left join B). Levels PURE, ENGINE. Wave 2 (counts). Props P3 P5 P6 P7.
- Start `lab` at J: lines `T1:B` (reach B, J, plots) and `T1:J`. Filter `lab != "X"`: at `T1:B` it removes 2 rows of B and J keeps 5 rows with 2 EMPTIED (S1, S2 lab missing); at `T1:J` it removes 2 rows (tick "keep missing") or 4 (without: S4, S5 have missing lab after the join, F1). Counts for (B only, J only, both, none) x tick: 12 numbers computed by O1 and fixed in the test. The count shows "removed" and "emptied" (rows kept but the value became missing).
- Wrong: both lines announce "2 rows"; reach read as rows lost (user pitfall P1); the missing tick ignored.

### L050 inner_join_multiplies_rows
- From: sci C27. Fixture FX-ROWS (A 3 rows; B S1 x3, S2 x1, S3 x2; inner J = 6 rows). Levels ENGINE. Wave 2. Props P3 P5.
- `sample_id != "S1"`: A line 1 row, B line 3 rows, J line 3 rows; the unit of each number is the rows of that table. Distinct samples are not given unless Q21 says so.

### L051 join_with_missing_keys
- From: sci C28. Fixture FX-ROWS. Levels ENGINE. Wave 2. Props P5.
- A row with no sample id: missing keys do not match; a left join keeps the A row; a filter on the key removes it or not by the tick, at A and at J alike.

### L052 remove_sample_from_all_tables
- From: sci C30; user A1; D-0022 (the one automatic placement, "remove from all tables"). Fixtures FX-ROWS (three sources, two joins), R-DEMO, R-FIG. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (rows), wave 3 (real). Props P1 P3 P6.
- Every table that holds the key (by identity) is a line, all ticked; after the step S3 is absent from every table and plot table (O1: no table contains S3), each table loses its own S3 rows; a source of two joins is not double counted. This is the case the others protect.

### L053 key_not_on_every_table
- From: sci C32. Fixture FX-ROWS (a lookup table D without a sample column; plot reads D). Levels PURE, ENGINE. Wave 1. Props P2 P6.
- D appears in no line and is unchanged (O1); it is not in the "remove from all" summary.

### F. Missing values

### L054 missing_tick_matrix
- From: sci C34; D-0042. Fixture FX-MISSING (v = [1, 2, 3, None, 3] and a text column with an empty string). Levels ENGINE. Wave 2. Props P5 P7.
- For every operator the dialog offers (equal, not equal, less, greater, in list, not in list, is missing, is not missing, contains) the removed count with the tick on and off equals O1's explicit null logic: `!=` 3 with `v = 3` and the tick off (the two 3s and the missing one), 2 with it on. The written step carries `na` explicitly (no default).
- Wrong: tick ignored; the step written without the missing clause while the count says 2.

### L055 empty_text_is_not_missing
- From: sci C53 (OQ16). Fixture R-FIG (`strip: true`, `null_values: []`), FX-MISSING. Levels ENGINE. Wave 2. BLOCKED by Q18. Props P5.
- With `null_values: []` an empty field is the empty text, not missing: the "no value" count is 0 and the dialog does not offer a distinction that no place has (stripped ids `" S1"` and `"S1"` are one value from T1 on).

### G. Plots, flags, the counts, redundancy

### L056 plot_flags_table_versus_picture
- From: sci C42; D-0318. Fixtures FX-CHAIN, R-DEMO. Levels ENGINE. Wave 2. Props P3 P5.
- Plot draws `val` against `year`: a filter on `country` removes rows (table changed, picture changed); a drop of an undrawn `lab` (table changed, picture the same); a filter that matches no row here (neither). NA handling of the picture is Q22's remainder.

### L057 earlier_place_covers_later
- From: sci C40, C43 (part), C02; user A12, chk C14 (part), P6; D-0198 (the three cautions are part of the tests), D-0194 (all ticked at opening). Fixtures FX-CHAIN, FX-REN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q15. Props P5 P6.
- Default all ticked writes the same step at a table and at its dependants. Three cautions as tests: (1) an earlier place covers a later one in the SAME chain only; (2) only when the column is unchanged in between (a rename or cast between: not covered); (3) other chains are not covered. Count per line "removes 0 rows here that the ticked place above does not already remove". Results of "all ticked" and "earliest only" are identical rows (O1).
- Wrong: counts added up (3+3+3 = 9); "covered" shown across a rename.

### L058 rows_affected_definition_and_stability
- From: sci C43 (OQ14); user chk C2; D-0316. Fixture FX-CHAIN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q16. Props P5.
- For each line ticked ALONE the rows that disappear from that table equal the announced count; the number on a line does not change when another line is ticked, or the dialog says which definition it shows ("alone" or "after the lines above"). The reach is never shown as a row count.

### L059 empty_result
- From: sci C57 (OQ17). Fixture FX-CHAIN. Levels ENGINE. Wave 2. BLOCKED by Q19. Props P5 P7.
- A step that removes every row, and one that matches none: "n of n rows" and "no row affected here" shown; the plot of an empty table does not crash the dialog.

### L060 ties_and_order_determinism
- From: sci C58. Fixture FX-ROWS (ties; `unique` or `sort then head` after a join). Levels ENGINE. Wave 2. Props P6.
- Two identical runs give identical tables including row order; the oracle matches including WHICH of the tied rows is kept.

### L061 audit_after_head_sample_unique
- From: sci C47 (OQ15). Fixture FX-ROWS (T1 `head(3)`). Levels ENGINE. Wave 2. BLOCKED by Q24. Props P4 P5.
- The audit step runs after the recipe's steps (D-0146): 6 rows, 3 after the head, 2 after removing S2; the 4th row does not come in. A filter before the head is not offered. The line carries the structured fact "a position step (head, sample, unique) comes before"; wording is Q24.

### L062 the_recipe_already_removes
- From: user A4, P7. Fixture R-DEMO (`MLST_with_metadata`: T2 keeps year 2023 to 2025). Levels ENGINE. Wave 2. Props P5.
- A filter `year > 2022` written at T1 removes 0 more rows at T2: "your step removes 0 more rows here"; and `era` (built from `year` at T2) changes legends when a T1 filter changes years: "picture changed".

### L063 one_plot_only
- From: user A2, chk C8. Fixture FX-TIERS (Pa, Pb on J1). Levels ENGINE, BROWSER. Wave 2. Props P3 P6.
- Untick all but "only Pa": Pb (same table) and J1 stay the same row for row; the summary says so. "Only this plot" appears for every plot and reaches exactly 1.

### L064 same_step_twice
- From: user A13, chk C14; Q17. Fixture FX-CHAIN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q17. Props P5 P6.
- The same step added a second time: refused, warned, or finds nothing ("already in your audit steps (step 2); writing it again removes 0 rows"); the result in rows is the same as once.

### L065 nothing_ticked
- From: user A11, chk C11. Levels BROWSER. Wave 4. Props P6.
- No line ticked: "Nothing is ticked, so this step would change nothing. Tick at least one place." The confirmation is blocked; all lines start ticked (D-0194).

### H. The audit copy as input; undo

### L066 audit_copy_column_dropped_earlier
- From: sci C46; arch (brief: "a column dropped by an earlier audit step no longer exists downstream; a second step offered only where the column still exists"); D-0176. Fixture FX-AUDIT (FX-CHAIN + an audit drop of `lab` at `T1:B`). Levels PURE, ENGINE. Wave 1 (PURE: the copy and its PlanBook), wave 2 (the build). Props P1 P2 P7.
- The walk run on the copy (the PlanBook of the copy: `lab` is gone at B and in J): start `lab` is not offered at J; at no place is a line offered for `lab`. A step on `lab` forced from an older view fails at build with the plain D-0176 message, never silently passes. The reverse (a filter on `lab` first, then the drop at the same table) is allowed and equals O1.
- Wrong: the walk reads the original's PlanBook (M19); the audit step missing from `step_list`.

### L067 two_audit_steps_second_dialog
- From: sci C45; D-0316. Fixture FX-AUDIT. Levels ENGINE, BROWSER. Wave 2. Props P5 P6.
- Step 1 `year != 2022` at `T1:A`; step 2 `year != 2023` at `T2:J`. The second dialog is walked on the copy with step 1: the counts at J exclude rows already removed; the set of lines equals the first dialog's (no new places) except where step 1 changed a collapse (L003).

### L068 remove_step_restores_everything
- From: sci C44; user A14, chk C4; D-0314. Fixture FX-AUDIT. Levels ENGINE, BROWSER. Wave 2. Props P6 P7.
- Add (with a reason), remove through "Remove step", add again: every table and plot equals the state before, row for row (frames compared, not parquet bytes: the metadata carries the key); the original `steps` of every tier are byte-identical (H5); the second addition equals the first except a new id (ids are not reused: `created` counts up); the lines returned by the walk are those before the first add (the tier the add created is gone: `remove_step`'s own rule).
- Wrong: a duplicate step after the second add; the first step stays after removal; an id collision.

### L069 walk_is_idempotent
- From: sci C62 (part). Fixture all small fixtures. Levels PURE. Wave 1. Props P1 P2 P3 P7.
- Walk twice: equal. Add a step and remove it (a no-op round trip), walk again: equal to the first. Walk a recipe restored from a session (`load_data_analysis_recipe` of the file, then the copy again): equal.

### I. Failure: one place cannot answer

### L070 data_file_missing
- From: sci C48; user A15, chk C9, P10; D-0195; arch. Fixture FX-FAIL (A present, B's file renamed away). Levels PURE (injected failure, L072), ENGINE (a real missing file), BROWSER (the text). Wave 2. Props P1 P3 P7.
- Lines: `T1:A` tick and correct; `T1:B` grey "the data file of B is missing" (the engine's reason in plain words); `T1:J` and the plots reading J grey "cannot be built: B missing"; "only P" for a plot reading A stays tick. The reach of `T1:A` still counts J and its plots. "N found, M cannot be answered" is shown (D-0195). The summary says "2 places could not be checked: the step is not written there and they are not in the counts" (user A15, wording in Q28).
- The lines that can be answered are IDENTICAL to a run with B present (compared field by field, apart from the reach of the grey ones being the same set): the test is a diff of two Walks.
- Wrong: the missing file raises and the whole list is empty; a grey place dropped from the list silently (M14).

### L071 step_fails
- From: sci C49; D-0176, D-0342; arch. Fixture FX-FAIL (a T1 step on a column that does not exist; a cast of "abc" to a whole number, a value error that shows only when rows are read). Levels ENGINE. Wave 2. Props P1 P2 P7.
- Planning names the step: the engine's own error names only the column (`"no_such_column" not found`), so the PlanBook builder runs the steps one at a time (the way `materialize_tier3` already does) and gives the table, the tier, the step number and file and line (D-0342). The failing table's lines and those below are grey with that sentence; other tables are normal. A failing table upstream of the START cannot happen (the user views an existing table). A value error that shows only at read is NOT a plan failure: it is found when the step is applied (ENGINE, L068).

### L072 one_place_plan_fails
- From: arch (brief "failure"). Fixtures FX-CHAIN, FX-TIERS with a PlanBook literal. Levels PURE. Wave 1. Props P1 P2 P7.
- A `PlanFailure` injected at every single (node, k) in turn: the Walk equals the walk without the failure except for the lines at and below that place, which are grey with the failure's sentence. Never an exception, never an empty list, never a tickable line whose plan is missing. A node missing from the PlanBook altogether (a bug of the caller) is a hard error `PlanBookIncomplete` naming the node, not a silent grey.
- Wrong: M14 (swallows), M17 (tickable on failure).

### J. Keys, order, purity, scale (the architect's own)

### L073 reach_equals_keys_changed
- From: arch (brief "the keys"). Fixtures R-DEMO, R-FIG, FX-TIERS, FX-AUDIT. Levels ENGINE (keys with faked file hashes, no data read). Wave 2. Props P3 P6.
- For every line of every Walk: add one step at `line.place` through `audit_copy.add_step`, compute the keys of the copy and of the original; `{nodes whose key changed} == line.reach_nodes` and no key outside it changed. Verified once by hand: 58 of 58 writable places on the demo and 8 of 8 on figshare, 0 differences (F-B). The test is the permanent version, with the case where the reach would differ from the keys named: unread joins (their key does change).
- Wrong: a reach that is wider (a table that does not read the place) or narrower (a missing join) than the keys.

### L074 affected_plots_subset_of_reach
- From: arch; D-0318; `audit_run.py` ("a filter that removes nothing moves a key and no row"). Fixture FX-CHAIN, FX-TIERS. Levels ENGINE. Wave 2. Props P3 P6.
- For every line and a step that removes rows: `AuditRun` affected plots are a subset of `line.reach_plots`; for a step that matches no row the affected set is empty while the keys still moved (the test says "keys changed, content not": the reach is structural, the affected set is about content).

### L075 plan_asked_once
- From: arch (brief "scale"). Fixtures R-DEMO, FX-TIERS. Levels PURE (the walk), ENGINE (the builder). Wave 1 (the walk), wave 3 (the builder). Props P7.
- The walk takes the finished PlanBook (a mapping) and has no call to the engine; a counting mapping proves that each (node, k) is read a bounded number of times (once per start of the walk, not once per line per place) and that the number of reads does not grow with the number of lines. The PlanBook builder composes each (node, k) exactly once per recipe state (counted by wrapping `wrangler().run`/`assemble`: N places, N compositions, not N times the number of columns tried). Starting from every column of every table adds no composition.
- Wrong: M13 (asks per line).

### L076 purity_no_rows_no_writes
- From: arch (brief "what the walk must NOT do"); sci C50. Fixture all. Levels PURE, ENGINE. Wave 1. Props P6 P7.
- (a) Deep copies of the graph input, the PlanBook and the recipe dict are equal after the walk (frozen dataclasses where possible). (b) `builtins.open`, `os.stat`, `time.time`, `random`, `polars` are patched to raise inside the walk (and `utils.lineage_walk` imports none of `polars`, `app`; checked by an import test). (c) ENGINE: the source files are replaced by poisoned files after the PlanBook is built (garbage bytes): the walk still answers (it reads no row). (d) Nothing is written under the anchors folder or the audit folder by the walk or by the PlanBook builder; the builder reads rows only for `pivot`, `sample`, `describe` and says so.
- Wrong: M18, M22.

### L077 determinism_across_processes
- From: arch; user chk C3, C13; sci C62. Fixture R-DEMO, FX-TIERS. Levels PURE. Wave 1. Props P7.
- The Walk is serialised (JSON of the data, sets sorted by graph order) and compared across 4 subprocess runs with different `PYTHONHASHSEED`, across a fresh process after a "restart" (recipe reloaded), and (BROWSER, wave 4) across two machines for the same recipe and data. A `frozenset` is never iterated to build a list: the lists are built from the graph order.
- Wrong: M12.

### L078 order_of_lines
- From: arch; user A16, Q11 of the user; section 1c. Fixture FX-TIERS, R-DEMO. Levels PURE, BROWSER. Wave 1. BLOCKED by Q11. Props P7.
- One rule, tested as a function: the start's line first (when the owner wants "you are here"), then graph order; groups in the data-flow order (source tables, joins, plots). The number of lines in the sentence "This step will be written in N places" equals `len(lines)` of ticked ones. Same input, same order (L077). Column order of a table never changes the order of lines (a select that reorders: same output).
- Wrong: alphabetical; grouped only by path.

### L079 scale
- From: arch (brief "scale"). Fixtures R-DEMO (85 nodes, 108 step-level places), R-FIG (and its 30x and 100x copies from `measure/`). Levels PURE, ENGINE. Wave 3. Props P7.
- The walk on a PlanBook of the demo recipe starting from every column of every table (302 columns in 51 tables of the demo at the tier ends, 799 columns over its 108 step-level places, per the measurement) finishes in a bounded time that the test records (the measured PlanBook costs 0.16 s on the demo, 0.03 s on figshare, 0.23 s at 100x, 0.02 to 0.22 s of it the one read of the source files); the walk's own time is a small multiple of the number of nodes. The test records and compares with a generous limit; it does not claim a speed.
- A recipe with a pivot costs the builder a real read up to that step (L080).

### L080 reads_rows_only_where_the_engine_must
- From: sci C50; user P13; FACTS. Fixture FX-SHAPE (a pivot) and R-DEMO (none). Levels ENGINE. Wave 3. Props P7.
- A read counter (or poisoned files after the schema read, see L076) shows that on a recipe with one pivot only the places downstream of the pivot cost a read, and every other place is answered without reading rows (the one source check per file aside: 1 read on figshare, 11 on the demo, measured). The dialog tells the user why a recipe with a pivot waits (user P13).

### L081 downstream_column_set_changes
- From: sci C38 (second half); arch (e2.py). Fixtures FX-SHAPE. Levels ENGINE. Wave 2. Props P3 P4 P7.
- A row filter written upstream of a pivot changes the SET of columns downstream (removing `tet` removes the column `tet`). The PlanBook of the audit copy is compared with the original's for every place: places not in the reach are equal (P6); places in the reach differ only where expected (names: only after a pivot; with `drop` kind: the dropped column); a plot that uses a vanished column is listed as broken before the confirm (Q14 for the words).

### K. Real recipes, width, properties

### L082 demo_sample_id
- From: sci C51; user A1, chk C17; D-0195 ("every node that has the field is offered, every node that lacks it is not; the dialog says how many nodes were found"). Fixture R-DEMO (`1_test_data_ST22_dummy.yaml`, 17 plots; NOT `demo_abromics.yaml`, which has 9 nodes, see section 3). Levels ENGINE. Wave 3. Props P1 P2 P3 P7.
- Expected lines for `sample_id` computed independently of the walk: the structural count by hand from the YAML (an upper bound of 46: 29 table lines and 17 "only this plot", F-A) and the identity from the marker oracle O2 (section 3). The reach of each line is the graph set (`T1:metadata_schema` reaches 20 tables, 4 of them read by no plot, and 13 plots, verified); NOT "the tables that carry the marker" (the scientist's C51 wording defines the reach by the marker, which contradicts C55 and D-0346; the marker defines WHERE the column exists, the graph defines the reach). A golden file stores the oracle's lines by place, reach and name; the test compares place by place and prints the list of places that are not lines (P2). Run once with mutant walkers M1, M4, M7 and see the test fail (user chk C17).

### L083 demo_column_of_one_source
- From: sci C52; user A6 (`serotype`, `VF_protein`: a SHORT list, not padded with tables that lack the column). Fixture R-DEMO. Levels ENGINE. Wave 3. Props P1 P2 P3.
- Lines = the tables downstream of that source that carry the marker (O2) plus the plots; no other source offered. Variation: a column of one source dropped by one plot's T3 or one join's select: reach counts the dependant, the line is absent or grey (Q6).

### L084 figshare_sample_id_and_one_source_column
- From: sci C53, C54; D-0195. Fixture R-FIG (`fg_metadata`, `fg_phenotypes`, `fg_genotypes`, one triple join, 3 plots, 7 lines at most). Levels ENGINE. Wave 3. Props P1 P2 P3 P5 P6.
- Remove one sample: each table, the join and each plot loses exactly the count O1 gets from the TSV with a plain reader (`libs/transformer/tests/data/fg_*.tsv`), no other row; the phenotype table has several rows per sample (rows, not samples: the join line says rows). A host-species column that only the metadata has: the phenotype table is not a line (P2), the join line removes pig rows of J (the tests of those samples).

### L085 property_fuzz
- From: sci C62. Fixture generated: random small recipes (steps drawn from rename, cast, drop, filter, join with and without clash, group_by, unpivot) and a seed. Levels PURE with ENGINE oracle. Wave 3. Props P1 P2 P3 P4 P7.
- The walk's lines equal O1's identity (the oracle replays the recipe eagerly on tiny data and tracks identity by marker values, O2 for text, the differential O3 for numbers); failing seeds are written to a file and become named cases. Run against every mutant in section 3: each must fail on at least one seed.

### L086 prediction_equals_plan_on_shipped_recipes
- From: arch (section 1b, the hybrid check). Fixtures R-DEMO, R-FIG, the stress recipe, `1_Abromics_general_pipeline`. Levels ENGINE. Wave 2. Props P2 P7.
- For EVERY step of EVERY shipped recipe: the names the rule table predicts (from the step's arguments) equal the names of the plan after the step (and the types equal, except for a cast); zero disagreements, and each rule has at least one shipped step or its own fixture step covering it (a rule no test touches is dead text). A disagreement is a failing test, not a wrong line.

### L087 found_count_and_no_silent_failure
- From: sci C48; D-0195. Fixtures R-DEMO, FX-FAIL. Levels PURE, BROWSER. Wave 1 (count), wave 4 (text). Props P1 P7.
- `Walk` has `found` (lines tick), `greyed` (grey), `gone` (places where the column is no longer); `found + greyed == len(lines)`. A silent loss is impossible: the sum of nodes in the reach equals the nodes accounted for as line (covers), gone, or failed (a conservation test on every fixture).

### L088 words_and_vocabulary
- From: user words section, chk C1, P12; D-0337. Levels PURE (the sentence function), BROWSER (the dialog). Wave 4. Props P4.
- `describe(line)` never contains "lineage", "node", "tier", "schema", "upstream", "downstream", "cast"; "key" only as "join key: the column that links the tables"; T1/T2/T3 only with the one-time explanation (user B). Every line names a table or plot that can be opened in the data choice with the same words (BROWSER: open it and see the rows).

### L089 long_list_and_summary
- From: user A16, chk C3, P11. Levels BROWSER. Wave 4.
- "This step will be written in N places. Untick the places you do not want." with N = ticked lines; group headers with counts ("Source tables, 8 of 8 ticked"); untick or tick a whole group (Q27 of the user, open); the demo's first line is the place she looks at.

### L090 show_which
- From: user chk C7; Q25 of the user. Levels BROWSER. Wave 4.
- "Reaches 3 tables and 5 plots" and "show which" list exactly those 3 and 5 names (the sets); the count is `len` of the same sets (L013).

### 2.1 Where every case of the two other files went (nothing is dropped; what is folded says why)

Scientist file. C01 L001; C02 L001 and L057 (its two assertions are one case each); C03 L015 (with C03b); C04 L017; C05 L001 (the "no note on equal lines" assertion, folded: a separate case would repeat C01); C06 L018; C07 L016; C08 L036; C09 L037; C10 L038; C11 L039; C12 L040; C13 L024, L025 and L012; C14 L026; C15 L027; C16 L029 and L081; C17 L031 (C17b is the variant with a rename; the default-name variant is added); C18 L046; C19 L047; C20 L042; C21 L043; C22 L044; C23 L045; C24 L048; C25 L017 and L023; C26 L049; C27 L050; C28 L051; C29 L011; C30 L052; C31 L021; C32 L053; C33 was a pointer to C37, folded in L032; C34 L054; C35 folded in L049 (same fixture, same assertion: the missing-after-join count); C36 folded in L043 (the tick is per step, D-0042); C37 L032; C38 L033 and L081; C39 L008 and L002; C40 L007 and L057; C41 L009; C42 L056; C43 L057 and L058; C44 L068; C45 L067; C46 L066; C47 L061; C48 L070 and L087; C49 L071; C50 L080; C51 L082 with a corrected oracle (see section 3.2 and the report); C52 L083; C53 L084, L055 and L052; C54 L084; C55 L012 and L013; C56 L010; C57 L059; C58 L060; C59 L045; C60 folded in L045 and L054 (the in-list operator row); C61 L041; C62 L085, L069 and L077. Harness H1-H5 section 3.2; OQ1-OQ17 section 5.

User file. A1 L052 and L082; A2 L063; A3 folded in L049 (a filter at the metadata source blanks a column in left-joined tables: the left join case); A4 L036, L037 and L062; A4b L037; A5 L029, L024, L056 and L081; A6 L083; A7 L015, L020 and L028; A8 L017; A9 L007; A10 L008; A11 L065; A12 L057; A13 L064; A14 L068; A15 L070; A16 L078 and L089. Checks chk C1 L088; C2 L058; C3 L077 and L078; C4 L068; C5 L001 and L002; C6 L005; C7 L013 and L090; C8 L007 and L063; C9 L070; C10 L015 and L036; C11 L065; C12 L037; C13 L077 (two machines is its BROWSER-wave part); C14 L057 and L064; C15 L029; C16 L014; C17 L082. Pitfalls P1 L049; P2 L049; P3 L015; P4 L007; P5 L036; P6 L057; P7 L062; P8 L032; P9 L081; P10 L070; P11 L089; P12 L088; P13 L033 and L080. Words section L088. Q1-Q12 section 5.

Architect's own (added, not in the two files): L003, L004, L006, L011, L012 (in part), L013, L014, L019, L022, L023, L026 (per-step plans), L030, L034, L035, L066 (as the brief states it), L069, L072 to L081, L086, L087.

## 3. Shared fixtures, the independent oracle, the mutant walkers

### 3.1 Fixtures (eleven tiny ones and two real recipes)

One definition, two uses: each fixture is a recipe dictionary plus tiny tables in ONE helper module (`libs/utils/tests/lineage_fixtures.py`, no Polars: tables as plain lists), turned into a PlanBook literal by the oracle O1 for PURE tests, and written as CSV into `tmp_path` for ENGINE tests (so the PURE and ENGINE tests cannot describe different recipes). A fixture has named variants (a variant changes one step), so the number of fixtures stays small. "Serves" is computed from the cases above (the `Fixture` field of each case).

- **FX-CHAIN**: A(sample_id, country, year, val), T1 `filter val > 0`; B(sample_id, lab), no steps; J = A left join B on sample_id (one T1 step, no T2); P1 reads J, P2 reads A directly. The smallest recipe with a join, a shared table, a plot on a source and empty T2 and T3. Variants: a `select` without `country` in A's T1 (L027); a join no plot reads. Serves: L001, L009, L012, L013, L027, L029, L056, L057, L058, L059, L064, L066, L072, L074.
- **FX-TIERS** (the structure kitchen, no column detail): sources S (T1 one step, T2 two steps; read directly by plot Ps AND an ingredient of J1 and J2), E (no steps; read by plot Pe AND an ingredient of J1 and JU), M (metadata, no steps), U (read by nobody); J1 = S, E, M (T1 two join steps, T2 one step; plots Pa, Pb, Pc where Pc has two own T3 steps), J2 = S, M (T1 one step, no T2; plot Pd), JU = E, M (no plot). Verified by script (`architect/fx_tiers.py`): 10 distinct tables, 7 table lines and 6 plot lines (13 lines) for a column present everywhere, reaches as in L002. Variants: FX-SIX (one join read by six plots), a `select` that drops `country` at J2 (L024). Serves: L002, L003, L004, L005, L006, L007, L008, L010, L012, L014, L024, L025, L063, L072, L073, L074, L075, L077, L078.
- **FX-REN**: A(sample_id, country, a_year) with T1 renames country to origin and a_year to year; B(sample_id, country, b_year, isolate) with T1 rename b_year to year; Pa reads A, Pb reads B; JAB = A left join B on sample_id with plot Pj. Variants: REN-BACK (T2 renames origin back to country), REN-SWAP (A(a Int, b Str) and A(a Int, b Int), T1 `rename {a: b, b: a}`), REN-NEW (T1 drops `country` then `with_columns {country: "X"}`), a pair of tables whose column differs only in case. Serves: L014, L015, L016, L017, L018, L019, L020, L026, L028, L057.
- **FX-JOINS**: A(sample_id, val, country), B(isolate, val, lab); JK = A join B with left_on sample_id and right_on isolate (how left, inner, full); JV = A join B2(sample_id, val) on sample_id (clash `val`, default suffix, suffix `_b`, a B3 that already has `val_right`: the plan fails); self join J = A join A (SELF); a join that reads a join (JJ, refused). Serves: L011, L013, L017, L021, L022, L023, L029.
- **FX-TYPES**: A(sample_id, year Int64, L50 Float64 [2.0, 2.4, 2.5, 3.0], country String, d String "2022-03-01"); J = A join B; `T2:J` casts year to String, L50 to Int64 (rounds down), country to Categorical, d to Date; Pi reads A, Pc reads J; a round-trip variant (int to text at T1, back at T2); a Float64-versus-Int64 key. Serves: L035, L036, L037, L038, L039, L040, L041.
- **FX-VALUES**: S(sample_id, country [Norway x3, Sweden x2, NO x1], year, val [2.34, 2.36, 2.41, None, None, ...], virulence_raw) with one step per variant: recode Norway to NO at T2, fill with 0.0, round to 1 decimal, lowercase, `with_columns` in place, a z-score, `group_by country, year` with `mean(val)` that KEEPS the name `val`, `group_by country` with `count`. The plan-blind fixture. Serves: L030, L031, L034, L042, L043, L044, L045, L046, L047.
- **FX-ROWS**: A(S1..S5, country); B(S1..S3, lab X, X, Y); B3(S1 x3, S2, S3 x2, mic); C(S1..S5); D(lookup, no sample column); a variant with a missing sample id; a `head(3)` variant; a variant with ties before `unique`. Joins inner and left; two joins for the key removal. Serves: L013, L048, L049, L050, L051, L052, L053, L060, L061.
- **FX-SHAPE**: W(sample_id, amp, cip, tet) with T1 `unpivot` to (antibiotic, resistant); L(sample_id, antibiotic, resistant) with T1 `pivot`. Serves: L032, L033, L080, L081.
- **FX-MISSING**: X(v [1, 2, 3, None, 3], t ["a", "", "b", None, "a"]), one plot. Serves: L054, L055.
- **FX-AUDIT**: FX-CHAIN plus an `AuditCopy` in four states: (a) an audit drop of `lab` at `T1:B`; (b) audit steps at `T2:J` and `T3:P2`; (c) two successive steps; (d) a step added then removed. Serves: L003, L004, L066, L067, L068, L073.
- **FX-FAIL**: FX-CHAIN with (a) B's file missing, (b) a T1 step of A naming a column that does not exist, (c) a cast of "abc" to a whole number, (d) the plan failure of FX-JOINS (3). Serves: L070, L071, L087.
- **R-DEMO**: `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (17 plots, 85 nodes, 108 step-level places; the user file's facts about `MLST_with_metadata`, `Quast_with_metadata`, `QA_L50_integer`, `ST22_Anchor` are read from it). Serves: L004, L052, L056, L062, L073, L075, L077, L078, L079, L080, L082, L083, L086, L087.
- **R-FIG**: `figshare_integration.yaml` (3 sources, 1 triple join, 3 plots; the TSVs `libs/transformer/tests/data/fg_*.tsv`) and the 30x and 100x copies of the measurement. Serves: L004, L052, L055, L073, L079, L084, L086.

What the real recipes do NOT contain (verified, `count.py`, `shared.py`): a plot with its own tier 3 steps, a table read by more than three plots, a pivot, a join of a join, a source with an empty T2 that is read directly and by joins. Those can only be covered by the tiny fixtures; no test on a real recipe can catch them.

### 3.2 The independent oracle

- **O1, the eager replay (the scientist's H1-H3, kept).** A small interpreter written inside the test (about 80 lines, only `polars` eager calls, no import from `transformer`, `app` or `ingestion`) for the actions the fixtures use: filter, rename, drop, select, cast, `with_columns` (a Python function per fixture), join (`on`, `left_on/right_on`, `how`, `suffix`), `group_by.agg`, `unpivot`, `pivot`, `fill_null`, `unique`, `head`, `sort`. It gives (a) the plan of every (node, k) (the names and types the PURE tests use as a PlanBook literal, and the oracle for the PlanBook builder at the ENGINE level), (b) the identity of columns by construction (it knows which output came from which input because the fixture's step functions say so), (c) the expected rows of every table and plot with a filter inserted at any set of places (the scientist's H3). Subsets: none, all, each alone, each adjacent pair (not 2^n: 46 lines on the demo). Compare frames (sorted rows, names, types), never parquet bytes (the file carries the key).
- **O2, the marker oracle (real recipes, text columns).** Copy the source files to a scratch folder; suffix every value of the column under test with a marker (the values of keys that a join equates get one common suffix, so the join still matches); run the recipe eagerly through the REAL engine (`materialize_*`); a table holds the column iff some column of it holds marked values. It finds identity through renames and ignores same-name columns of other origin (the scientist's idea, kept). Limits the architect adds: (1) it cannot mark a numeric or date column (a text marker fails the declared type); (2) a filter or recode on the marked column can remove or rewrite every marker: a table with zero rows or with unmarked values is "undecided", never "absent"; (3) it proves WHERE the column is, not the reach: the reach comes from the graph (the scientist's C51 text defined the reach by the marker; that contradicts D-0346 and C55).
- **O3, the perturbation oracle (numeric columns, floor check only).** Change the values of a numeric source column slightly in a scratch copy and run: a downstream column that changes depends on it. It cannot tell "the same column" from "derived from it" (a recompute and an aggregate both change), so it only proves P1 (no table the perturbation reaches is missed), not P2.
- **The harness (scientist H1-H5, with two changes).** H1 baseline, H2 subsets (limited as above), H3 compare with O1, H4 the mutants below as parametrised must-fail cases kept in the test files, H5 the original `steps` of every tier unchanged and the steps only in `audit_steps` (D-0332). Changes: frames not file bytes; the oracle is also run against the real engine on the shipped recipes (L086, L082) so that O1 itself is checked (two readings of Polars by the same team can share a mistake).

### 3.3 The mutant walkers every test set must kill

Each mutant is a deliberately wrong walker in the test file; the case(s) after the arrow must fail against it. A case that no mutant can fail is not a test.

| # | Mutant | Killed by |
|---|---|---|
| M1 | follows the column by NAME through the plans (no step rules) | L015, L016, L017, L020, L026 |
| M2 | plan-only identity: existence and neighbours from the plans, no rename or join rule | L017, L019, L024, L032 |
| M3 | assumes the name never changes, skips places where it differs | L015, L018, L019, L021 |
| M4 | one line removed (first, last, an "only this plot", the plot with own T3) or one added (a join no plot reads) | L001, L002, L005, L008, L082 |
| M5 | one line per tier whatever the steps (no collapse) | L001, L002, L003 |
| M6 | collapses by equal plans (names and types) instead of by steps | L003, L004 |
| M7 | the reach counts only the places that hold the column | L012, L024, L082 |
| M8 | the reach is a count: off by one, own table forgotten, a table or plot counted twice, a chain the engine does not build included | L001, L010, L011, L013 |
| M9 | forward over the wrong edges (T2 of a source read as a join input; ancestors included) | L006, L014 |
| M10 | no type note, or against the wrong place, or exact versus family inverted | L035, L036, L041 |
| M11 | a name note on an equal line, or from the start only | L001, L008, L015 |
| M12 | lines in set order, dict order or alphabetical | L077, L078 |
| M13 | asks the plan per line per place | L075 |
| M14 | swallows a plan failure (drops the place, or returns an empty list) | L070, L072 |
| M15 | guesses a rename from "one gone, one new", or marks an unknown step tickable | L034 |
| M16 | ignores join keys (a key under another name; a full join) | L021, L022 |
| M17 | grey and tickable confused; the key-drop rule written a second time | L029, L070, L072 |
| M18 | changes the recipe, the graph or the PlanBook | L076 |
| M19 | reads author steps only (ignores audit steps; on main, marked steps) | L003, L066 |
| M20 | ENGINE: the typed value is written unchanged at every line | L036, L037 |
| M21 | ENGINE: the step is written at the start or one tier too early | L047, L061, L068 |
| M22 | reads rows or files inside the walk | L076, L080 |
| M23 | uses plans at the end of each tier only (no per-step plans) | L026 |
| M24 | skips one of the three moves: (a) no back, (b) no forward, (c) no back-again (the notes from the start only) | (a, b) L014, L012; (c) L015, L036 |

### 3.4 What this test set cannot catch (rule 7 of the personas file)

1. A PURE test trusts its PlanBook literal: a literal that disagrees with the real engine hides a wrong walk. Closed by L086 (rule prediction equals plan on every step of the shipped recipes) and by the PlanBook builder compared with O1 and with the real run (the measurement's 108 of 108).
2. Identity of numeric columns on real recipes (O2 cannot mark them; O3 proves reach, not sameness): only the tiny fixtures and the plan names cover them.
3. In-place value changes (recode, fill, round) are invisible to every plan: only the row counts per line (ENGINE) protect the user, and only on the data of the test.
4. Equal keys do not prove equal content (L004, L074); the oracle for content is the frames, not the keys.
5. A step kind or shape that no shipped recipe and no fixture contains (listed in 3.1) is untested: nothing flags it. The rule table (Q2) must list the actions it covers; every other action is grey by construction, which is the protection.
6. BROWSER tests prove the screen, not the walk; a screen test that passes with a wrong walk is possible if the fixture hides it (hence the walk has its own PURE tests first).

## 4. The build order

The coordinator decides the order (D-0345: "the best build order is the coordinator decision - what I want is the final product that works according to my decisions"; a piece is DONE when it is finished and working, built, tested, in use, before anything depends on it; "present or partly built is not enough"). This is the architect's proposal of the order and of what DONE means for each wave; it follows the personas file ("risky logic first, the screen last").

Counts (computed from the case headers of section 2 by `architect/assemble.py`): 90 cases. By level (a case with two parts counts in each): PURE 56, ENGINE 60, BROWSER 16; by first level only: PURE 56, ENGINE 31, BROWSER 3. By the wave of its first part: wave 1 49, wave 2 31, wave 3 6, wave 4 4; in addition the ENGINE part of 22 wave-1 cases is built in wave 2, and the BROWSER part of 12 earlier cases in wave 4.

### Wave 1: the pure walk, the cases that catch a scientifically wrong result
- Cases: L001, L002, L003, L005, L006, L007, L008, L009, L010, L011, L012, L013, L014, L015, L016, L017, L018, L019, L020, L021, L022, L023, L024, L025, L026, L027, L028, L029, L030, L031, L032, L033, L034, L035, L036, L037, L039, L041, L048, L052, L053, L066, L069, L072, L075, L076, L077, L078, L087 (PURE parts; 49 cases).
- Must exist first: (1) the decisions of section 6 (U1 to U8, U10 to U12) and the questions of section 5 that block wave 1 (Q1 to Q11), or the test for that point written for both answers (the cases say so); (2) the fixtures module (`lineage_fixtures.py`) and the oracle O1's plan interpreter; (3) the data types `PlanBook`, `Plan`, `PlanFailure`, `Walk`, `Line` and the closed rule table of what each action does to a column (the owner's answer to Q2 decides whether it exists); (4) the decision on the one store of columns (U7).
- Written first, in this order: the mutant harness (M1-M19, M22-M24 as must-fail parametrised cases) with an empty walk so that every case starts red; then L001-L014 (structure and reach); then L015-L035 (identity); then L066, L069, L072 (copy, idempotence, failure); then L075-L078 (calls, purity, determinism, order).
- DONE means: every wave-1 case passes; every mutant M1-M19, M22-M24 fails at least one case (the run is part of the test file, not a manual act); `utils.lineage_walk` imports nothing outside `utils` (an import test); the walk is not wired to any screen; for every question of section 5.1 that blocks wave 1 and is not yet answered, both answers are tested and one switch decides.

### Wave 2: the engine cases (rows affected, keys, the audit copy)
- Cases: L004, L038, L040, L042, L043, L044, L045, L046, L047, L049, L050, L051, L054, L055, L056, L057, L058, L059, L060, L061, L062, L063, L064, L067, L068, L070, L071, L073, L074, L081, L086; and the ENGINE part of L001, L003, L007, L008, L010, L011, L015, L021, L023, L024, L027, L029, L031, L032, L033, L036, L037, L048, L052, L053, L066, L076.
- Must exist first: wave 1 done; `app/modules/plan_book.py` (per-step composition without storing, the PlanFailure sentence with step and file and line (D-0342, D-0176), the one allowed read of rows for pivot, sample, describe); the count per line from the audit run (`audit_run.run_audit` exists on main, slice A); the value written per line in its type (D-0202).
- DONE means: the PlanBook equals O1 on every fixture and the real run on both shipped recipes (the measurement's 108 of 108 as a permanent test); for every line the keys that change equal the reach (L073, 58 and 8 places today) and the affected plots are a subset (L074); the rows after each subset of ticked lines equal O1 (H3); a failing place gives grey lines and the others are identical (L070-L072); M20 and M21 fail a case; the rule table has zero disagreements with the plan on every step of the shipped recipes (L086). Before the build: measure the cost of "rows affected alone per line" (one audit run per line, up to 46 on the demo; it has not been measured) because Q16 depends on it.

### Wave 3: real recipes and scale
- Cases: L079, L080, L082, L083, L084, L085; and the ENGINE part of L075 (the builder composes each place once).
- Must exist first: waves 1 and 2; the marker oracle O2 and its golden files; a read counter.
- DONE means: L082-L084 equal the golden files place by place (the oracle ran in the same session as the walk: both printed); the mutants M1, M4, M7 fail L082; the fuzz (L085) runs a recorded number of seeds with each mutant dying on at least one; times are recorded (L079). Nothing here may make a wave 1 test depend on the real recipes.

### Wave 4: the browser cases with the dialog
- Cases: L065, L088, L089, L090, and the BROWSER parts of the earlier cases.
- Must exist first: waves 1 to 3; the answers to Q23 to Q28; the dialog (slice C form) reading the Walk and nothing else (no second computation of lines in a handler, D-0031).
- DONE means: each user check C1 to C17 is a browser test that points to the PURE or ENGINE case that proves its rule (a browser test that passes with a wrong walk is possible): C1 L088, C2 L058, C3 L077-L078, C4 L068, C5 L001-L002, C6 L005, C7 L013 and L090, C8 L063, C9 L070, C10 L036 and L015, C11 L065, C12 L037, C13 L077, C14 L064, C15 L029, C16 L014, C17 L082; the demo dialog opens in the time the measurement allows (the PlanBook 0.16 s).

## 5. Questions for the owner (merged from the three viewpoints)

One sentence each, with the wave it blocks and the options when they are obvious. Where a decided rule already answers or partly answers, the number is given in section 5.2 and the question is removed or reduced to the part that is open. Source of each: sci OQ = scientist file, user Q = user file, arch = architect.

### 5.1 Open

Blocks wave 1:
- **Q1** (sci OQ1) When a column is renamed and later renamed back, is the later column the same column as the first (one set of lines through both names; D-0347 says "back to the source" but not this), or a new column? Options: same; new.
- **Q2** (arch; reconsiders D-0325) May the walk read a few of the step's own arguments (rename mapping, join keys and suffix, drop, select, group_by keys) to say which column at the next place is the same one, every prediction checked against the engine's plan and a disagreement shown grey, or must it use the plan alone, which at a join with a name clash offers a false place and a missing one (verified) and cannot follow a rename? Options: hybrid with a closed list; plan only (then "renamed on one path only" of D-0347 becomes "not found under this name").
- **Q3** (sci OQ6; arch) Is a column that a step recomputes under its own name (`with_columns` on itself), or an aggregate that keeps its name (a mean still called `val`), the same column with a note, or a new column whose path starts there ("computed here")? Options: same with a note; new.
- **Q4** (arch) For a source table read directly by plots and by joins whose tier 2 is empty, is it right that "only distinct tables are lines" hides the choice "the plots that read it directly but not the joins" (the user then ticks each plot), or must T2 of such a table stay a line? Options: hidden (D-0346 as written); kept. (No shipped recipe has this shape.)
- **Q5** (arch) Does the reach count the joins that no plot reads (their stored tables DO change: verified) and is "a table" in "N tables and M plots" a distinct stored table? Options: count them (honest, equals the keys that change); count only tables a plot reads. Example: `T1:metadata_schema` reaches 20 tables with them, 16 without, and 13 plots.
- **Q6** (sci OQ4; user Q2) At a place in the reach where the column is gone (dropped by a join's select or by a plot's own steps), is it absent from the list, a grey line with the reason, or a note under the line that reaches it (the user's proposal)?
- **Q7** (user A7; arch) Is the column's name in the source file shown as a note on the first line of its path (a source table has no list of steps, D-0332, so it is not a place), or must the source file be a line of its own?
- **Q8** (user Q6) For a drop of a join key, are the lines where it is a key shown grey with the sentence of D-0297, or not offered at all?
- **Q9** (arch) In a full join on keys with different names (both columns kept; rows on one side only have a null in the other), is the other table's key offered as a line for "remove this sample from all tables"?
- **Q10** (arch) When is a type "another type" for D-0337's note: any difference of the engine's type, or only of the family (whole number, decimal, text, date, category), so that a 32-bit and a 64-bit whole number carry no note?
- **Q11** (user Q7) Is the order of the lines the order of the data flow with the place she is looking at first ("you are here"), or the data flow alone?

Blocks wave 2:
- **Q12** (sci OQ2) When a typed value cannot be written at one place (2.5 into a whole-number column), does that block the whole dialog, only that line, or turn that line grey?
- **Q13** (sci OQ3) May the value of an audit filter be a date, and how is it typed where the column is a date at one place and text at another?
- **Q14** (sci OQ5) When a step makes a later recipe step or a plot that draws the column impossible, is that plot listed as "cannot be drawn" before the confirmation?
- **Q15** (user Q1; sci OQ11) When a ticked place already covers the ticked places below it in its chain, does the dialog mark them as covered and not write them, only tell her, or say nothing?
- **Q16** (sci OQ14; user Q4) Is the row count shown on each line for that line alone (one audit run per line, up to 46 on the demo, not measured), or given the other ticked lines (one run), and may the number change when she ticks another line?
- **Q17** (user Q5) When the same step is added a second time, is it refused, warned, or accepted and shown as removing 0 rows?
- **Q18** (sci OQ16) Where a source has `null_values: []` an empty field is empty text and not missing: is the user told so when the "no value" count is 0?
- **Q19** (sci OQ17) When a step removes every row of a table, does the dialog warn, block, or show the count only?
- **Q20** (sci OQ8) When the same value matches different numbers of rows at two places because a recode sits between them (Norway to NO), is a warning required beyond the count per line (D-0203 covers values that stop corresponding one to one for casts; row-by-row lineage is not planned)?
- **Q21** (sci OQ9) For a long table (several rows per sample), must the dialog also give the number of distinct samples besides the rows?
- **Q22** (sci OQ13) Does "picture changed" count the rows the plot drops for missing values or by its own filter (D-0318 says "the columns or rows the plot itself uses")?

Blocks wave 4:
- **Q23** (sci OQ7) Must a line say that a value computed earlier in the tier (z-score, mean, rank) still includes the removed rows, since audit steps go at the end of the tier (D-0146)?
- **Q24** (sci OQ15) Must the user be told that a removal after the recipe's `head`, `sample` or `unique` does not bring other rows in?
- **Q25** (user Q3) Are the names behind "reaches 3 tables and 5 plots" shown on demand ("show which") or always?
- **Q26** (user Q8) Is a one-time explanation of T1, T2 and T3 in the dialog enough, or do the data-choice labels change to plain words in both screens?
- **Q27** (user Q9) Can a whole group of lines be ticked or unticked in one click?
- **Q28** (user Q12) Must the summary say which places could not be checked and that the step is not written there (D-0195 asks for how many were found)?

### 5.2 Answered by decided rules (removed from the list, or reduced)
- sci OQ12 "is the line 'only this plot' shown when it has the same effect as the table line": answered by D-0346 ("There is also a line for one plot only ... its reach is one plot"): every plot has the line, no exception (L009).
- user Q10 "a plot with tier 3 steps and the 'only this plot' line: one or two": answered by D-0346 (the line is the lowest level of the lineage that really has steps; her "Tick"): ONE line, `T3:p` (L008, L003). CONFIRM: it is the review session's reading that she confirmed.
- user Q11 "a place with another type: only inform or offer a cast": answered by D-0337 ("A": ticked, the type written, no cast offered).
- sci OQ10 "the tick for rows with no value: per filter, default": answered by D-0042 (every filter step states `na: keep|remove`, no default; HOME may preselect with a visible tick and count) and D-0043; the dialog writes one step, so one tick for the audit step: CONFIRM (the same `na` at every line).
- sci OQ11 reduced to Q15: D-0198 (caution 2: "only if the column is unchanged in between") says that after a rename or a cast the later line is NOT covered.
- sci OQ13 reduced to Q22: D-0318 defines the two statements; only the treatment of missing values is open.
- sci OQ2 reduced to Q12: D-0202 says an unwritable value is "refused with a plain message"; only the scope of the refusal is open.
- sci OQ8 reduced to Q20: D-0203 decides the warning for values that do not correspond one to one between places (its note: row-by-row lineage is "not planned"); what is open is the case with no cast.
- user Q1 (offer to untick what adds nothing) is part of Q15. user Q4 (row count per line or per table) is part of Q16 (D-0316 says only that rows and plots affected are shown before she confirms).
- Not a question any more: the tests for D-0198's three cautions (she asked for them, L057); the order of the build (D-0345: the coordinator's).

## 6. What the decided rules leave undefined, and must be defined before wave 1 can be written

These are not questions of taste: a test cannot be written without an answer, and a wrong answer gives a wrong result without an error. Each has a proposal (MINE) so that the test can be written; where the proposal also touches the owner's choice the question number is given. Tags: DECIDED means a ledger number states it, CONFIRM means a ledger number implies it, MINE is the architect's proposal.

- **U1 What "the same column" means (identity).** Not stated anywhere (D-0347 gives only the three events, rename, cast, drop). Proposal MINE: one column continues through (a) a rename (also a rename back, Q1), (b) a cast (D-0337: the line is ticked and the type written, so it is the same column), (c) a change of its values in place by a step that keeps its name (recode, fill, round, strip), (d) a join, where the keys the join equates are one identity (`join_keys.key_columns`; `key_families` already says "never found from equal column names alone") and a clash gives the right side another name. It ENDS (a new column starts) at a drop, at a column created from other columns, at an aggregation of a non-key column (Q3), at an unpivot or pivot (names become values and values become names), and at a copy (`b = a`). Two columns are never one because they share a name and a type. The first sentence of every test of section 2 depends on this.
- **U2 The granularity of "a plan of every place".** D-0325 says the engine's plan of every place; the measurement that backs it (`TABLE_FOR_THE_OWNER.md`) is per step (108 places on the demo). Per-tier-end plans cannot tell "dropped then created again" from "kept" (L026). Proposal MINE (CONFIRM with D-0325): a plan after every step and the plan of each source, keyed `(node, k)`.
- **U3 The unit of the reach.** A reach is a set of nodes; "tables" are the distinct collapsed tables below the place (the line's own table included, a plot with own T3 steps counted as a plot only), "plots" are the plots below. Counts are `len` of the sets, never stored apart (L013). Whether unread joins count is Q5.
- **U4 The start.** The start occurrence is the column at the END of the viewed node (`k = len(steps)`); a Source view starts at `DS:S`, whose first line is `T1:S` (Q7). A view of a plot starts at `T3:p` (equal to `T2` when it has no own steps).
- **U5 Equality of names and types.** Names are compared exactly (case sensitive, as Polars). Types are compared as the engine's type strings; whether a difference of family only is "another type" is Q10. The structured note keeps both strings so that either rule is a one-line change.
- **U6 Where a step lands, so what "exists" means.** An audit step goes at the END of its tier's list (D-0146, D-0332), so a column exists at a place when it is in the plan at the end of that tier (D-0325, D-0175). A column that exists in the middle of a tier only is not at the place (L027); a table whose columns are fixed by a final `select` has only those.
- **U7 One store of columns.** `RecipeGraph.column_info` (declared fields, select, drop; unknown otherwise; `recipe_graph.py:276-289`) and the PlanBook are two stores that can disagree (declared `input_fields` against the real columns of the file). MINE: the walk reads only the PlanBook; `column_info` stays for the checker (J08) or is fed from the PlanBook through its `columns_provider` hook, which no caller uses today; the decision is recorded once (D-0031, one authoritative way).
- **U8 The closed rule table (Q2).** If hybrid: the list of actions the walk understands (rename, drop, select, cast, join with `on`/`left_on/right_on`/`how`/`suffix`, `with_columns`, `group_by`, `unpivot`, and the actions that keep names), what each does to every column name, and that EVERY other action is grey where it changes names. Each rule is covered by a fixture step or a shipped step (L086), or it does not ship. If plan only: the rule table does not exist and L015, L017, L019, L021, L023 change their expected result to grey.
- **U9 The validity of a PlanBook.** A PlanBook is valid for one recipe state and one set of data files (the file headers can change). MINE: it is cached by the recipe keys of the copy (D-0326, `DataAnalysisRecipeKeys`), so a changed recipe or file gives a new book and a stale one is never read (two stores, one key).
- **U10 The kind of step.** `filter` and `drop` give the same lines; the difference is only the grey of a key drop (D-0297, Q8), asked of `join_keys.key_drop_problem`, the one rule.
- **U11 A recipe the engine does not build.** `recipe_graph` draws a join that reads a join (provisional); the engine refuses it (D-0344). MINE: the walk refuses such a recipe with a plain sentence before any line (L011); the refusal lives in one place (the graph or the checker), not in the walk and the dialog both.
- **U12 Reading steps, audit steps.** Only through `recipe_tiers.step_list` (D-0332: "One helper returns the original steps then the audit steps, with a test that fails when a reader does not use it"). The PlanBook builder and the walk both use it; main (marked steps in `steps`) and the unmerged branch (`audit_steps`) behave the same through it (F-F). An audit step is recognised by its id (`audit_<8 hex>_<k>`).
- **U13 The plain sentence of a failure.** The PlanBook builder owns the conversion of the engine's reason into the plain sentence with the table, tier, step and file and line (D-0176, D-0342); the walk carries the sentence as data and never rewrites it.

