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

