# LBFB: review of the logic (thinking agent, 2026-11-20)

What this is: an independent check of the logic of the walk "back, forth, back" (LBFB) and of `BUILD_PLAN.md`. I built nothing and changed no file of the repository. Scratch scripts: `tmpAI/panel/lbfb/logic/` (`scope.py`, `ids.py`, `shapes.py`, `facts.py`), run from the worktree `.claude/worktrees/slice-c-audit-form` with `PYTHONPATH=libs/utils/src:libs/transformer/src:libs/ingestion/src:libs/viz_factory/src:.`, Polars of the project's `.venv`.

Labels: READ (I read it at file:line), RAN (a script of mine gave it), REASONED (my reasoning, not run). Tags for decisions: DECIDED (a ledger line taken by the owner), READING (the coordinator's or an agent's reading of a decided line, to confirm), OPEN (no decision).

Parts 2 and 7 are written for the owner.

## 0. In short

- The walk is well defined for a column that no join key equates and no unread step touches. It is NOT well defined, as the decided lines are written, in three places: (1) how far it goes for a join key (a sample id); (2) which step arguments it may read; (3) a few recipe shapes (an empty tier 2 of a table read by plots and joins, a self-join, joins other than left and inner, sources read by nothing).
- The architect's top flag is true (RAN). It is worse than written: with the walk read as one pass, the set of places for the same sample depends on which plot the user clicked. Two test cases of the test design (L014 "same set from any start" and L052 "remove a sample from all tables") cannot pass on the demo recipe with the scope the build plan takes as provisional.
- The build plan reads more step arguments than D-0351 lists. Without that extra reading, 48 of the 73 non-source nodes of the demo recipe sit at or below a step the walk may not read (RAN `outside_list.py`), so most lines would be grey. With it, the plan goes beyond what the owner decided. This is a question for her that nobody asked.
- The answers to the four questions are consistent with the decided lines and with each other, with two corrections (part 3).
- The build can start now with the steps that need no answer (part 7), provided four fields are added to the data records now so that no later answer forces a rewrite (part 5).

## 1. Is the walk well defined?

### 1.1 The walk as a procedure

Inputs (REASONED, from D-0325, D-0347, D-0351 and the plan's part 3.1):
1. The recipe graph of the recipe in memory (`recipe_graph.build_graph`), which is the audit copy when an audit is open. A node's steps are the author's steps then the audit steps (`recipe_tiers.step_list`; READ `recipe_graph.py:489, 498-499`).
2. The engine's plan after every step of every node, and of every source: `(node, k) -> names and types`, or a failure with the engine's sentence. Per step, not per tier end (otherwise "dropped, then created again" looks like "kept": DESIGN F-C, U2).
3. The start: a node and the name of the column at the END of that node.
4. The kind: filter or drop.

The objects. An OCCURRENCE is a pair (node, step number k, column name). Two occurrences are LINKED when one of these holds:
- (L1) the next step keeps the name: the name is in the plan before and after step k+1, and step k+1 is not a rename that moves it;
- (L2) a rename maps the name to another (simultaneous mapping; RAN: Polars swaps `{a: b, b: a}` at once, and the engine calls `LazyFrame.rename(mapping)` once, READ `polars_calls.py:263`);
- (L3) the end of a node is the start of the next node on a graph edge (T1 to T2, T2 to T3, T1 of an ingredient to the step of the join that reads it);
- (L4) a join step takes a column of the right table into the join: the same name, or the name with the suffix when it clashes;
- (L5) a join step equates its key pairs (`join_keys.key_columns`, READ `join_keys.py:140-151`): the left key and the right key are one.

The IDENTITY of the start column is the set of occurrences linked to it. A PLACE is a distinct stored table (D-0346): a node with steps, or the first node of a chain of nodes without steps; T1 of a table is always a place (a source file holds no step list, D-0332); a "only this plot" place `T3:p` exists for every plot.

The three moves (D-0347):
1. Back: from the start, follow the links toward the sources. Result: the source occurrences.
2. Forward: the reach of each place is `lineage_forward` of that place in the graph, whether or not the column survives (D-0346: "a step on a shared table reaches everything below it").
3. Back again: for each reached node, follow its own path from the sources, read the name and the type at the end of the node, and the steps that rename, cast or drop it, so that each line says what is true there.

A LINE is a place where an occurrence of the identity exists at the end of the place. A GONE place is a reached place where no occurrence exists at its end.

### 1.2 What "the same column" means at each kind of step

| Kind of step | Same column? | Status | Source |
|---|---|---|---|
| Unchanged (a step that does not touch it) | yes | DECIDED in practice (D-0347 lists only rename, cast, drop as differences) | D-0347 |
| Renamed, inside one tier | yes | DECIDED | D-0352: "If within the same tier then it will be the same column" |
| Renamed, then renamed back in another tier | one column, named per tier | READING (the ledger line itself says her words do not cover it) | D-0352 bracket |
| Cast to another type | yes, ticked, type written | DECIDED | D-0337 |
| Recomputed under its own name (a recode, a mean per group) | yes, with a note | DECIDED | D-0353 |
| Replaced under its own name by another column's values (`x = pl.col('y')`) | D-0353 read literally says yes ("recomputed under its own name"); a scientist would say no | OPEN (not asked) | D-0353 |
| Aggregated (group_by, the name kept) | yes, with a note | DECIDED (D-0353 example "a mean per group that keeps the name") | D-0353. Note: DESIGN U1 still says identity ENDS at an aggregation of a non-key column; U1 is out of date |
| Dropped | gone below the drop | DECIDED (D-0347 "a drop of the column") | D-0347 |
| Not kept by a select | gone | DECIDED by D-0351 (it may read "the columns of a select") | D-0351 |
| Dropped then created again with the same name | a new column (the plan per step shows the gap) | READING (DESIGN U1) | none |
| Created from other columns (`era` from `year`) | a new column | READING | none |
| Through a join as a key, same name | one column on both sides | DECIDED that the walk may read the keys | D-0351 ("the keys ... of a join") |
| Through a join as a key, other names (`left_on: sample_id`, `right_on: isolate`) | one column; the right key is gone after a left or inner join | READING; the plan confirms the right key is gone (DESIGN F-C) | D-0351 |
| Through a join as a value, no clash | the same column | REASONED | D-0351 |
| Through a join as a value, with a clash | the right one carries the suffix | DECIDED that the suffix may be read | D-0351 |
| Self-join (a table joined with itself) | the column exists TWICE at the join (`val` and `val_right`, RAN) | OPEN; nobody asked | none |
| Full join on the key | both keys kept: two occurrences | OPEN (DESIGN question 9) | none |
| Unpivot (columns become values) | gone | READING | none |
| Pivot (values become columns) | gone; new columns depend on the rows | READING | none |
| Explode of a list | same name, other type, other rows | REASONED: D-0337 (type differs) and D-0353 apply | none |

### 1.3 Where two decided lines, read exactly, give different answers

1. **D-0351 and D-0353 (new finding).** D-0351 lets the walk read "a short fixed list of what a step itself writes (the mapping of a rename, the keys and the suffix of a join, the columns of a drop or a select)". D-0353 asks that a column recomputed under its own name gets a line that "says plainly what happened there". The plan cannot see a recompute (RAN `facts.py` (6): a `with_columns` that multiplies a column by 1000 leaves the plan identical; the scientist RAN the same for a recode and a fill). So D-0353's sentence can only be written by reading the output names of `polars_with_columns` (`named_exprs`), of `polars_group_by`, and the `columns` of a cast, a fill or a strip: none of these is in D-0351's list. The build plan's `step_effects.py` reads them (BUILD_PLAN 3.3 first row) and presents this as MINE; it does not say that it goes beyond D-0351. DESIGN U8 had proposed the wider list; the owner's decision D-0351 names four items only. Read strictly, D-0351 makes every path through such a step grey: RAN `outside_list.py` on the demo, 48 of the 73 non-source nodes (tables at a tier and plots) are at or below a step outside the four readings and the row-only steps (the actions: cast, explode, fill_null, group_by, str_splitn, str_strip_chars, unnest, unpivot, with_columns) (for `sample_id` at `mlst_bar`: `T1:MLST` has a `with_columns` and a fill, `T2:MLST_with_metadata` has a `with_columns`). Read widely, the walk does what D-0325 excluded ("rules per action in the recipe map"). The owner must say which (question O2 of part 7).
2. **D-0347 and D-0022 for a key column.** Part 2.
3. **D-0346 and the reach of a collapsed place.** D-0346: "An empty tier is not a separate place" and "Each line shows its reach". For a source table read directly by plots AND by joins, with no tier 2 steps, the two tiers hold the same data but do NOT have the same reach: a step at T1 reaches the joins, a step at T2 does not (joins read T1, READ `recipe_graph.py:14-16`). Collapsing them removes a scope ("the plots that read this table, not the joins"), which the user can then only get by ticking one "only this plot" line per plot. No shipped recipe has this shape (RAN `shapes.py`: `ResFinder` is read by a plot and by joins, but its tier 2 has steps). The plan's provisional (collapse) is safe: the reach shown is true. It is DESIGN question 4.
4. **D-0326 and the "applied nowhere" rule.** D-0326 builds "every tier 1 and tier 2 table" at opening; `audit_copy._target` refuses a tier 2 that no plot reads because "its tier 2 is applied nowhere" (READ `audit_copy.py:175-177`). Question 2 of the four counts "4 more stored tables that no plot reads". Whether those joins are built and stored at all depends on the opening build of D-0326, which is decided and NOT built (READ `tasks.md:834`). Today they change only in the sense that their key changes. Not a contradiction to stop the work (rule H), but the sentence "4 more stored tables" is true only after D-0326 is built and only if it builds the joins no plot reads. Suggestion: the reach sentence says "tables built from this place", not "stored tables", until then.

### 1.4 Where the procedure is under-determined (no decided line and none of the four questions covers it)

- A self-join: the identity has two occurrences at one place (`val`, `val_right`). Which does the step filter? (RAN `facts.py` (3).)
- Joins other than left and inner. A removal at the right table of an anti join ADDS the row back to the join's result; at a semi or inner join it removes it; at a left join it empties the copied columns; at a full join it keeps a row with the other side empty. Shipped recipes use only `left` (28) and `inner` (4) (RAN grep), but the engine accepts the others (READ `join_keys.py:36`).
- Sources that nothing reads (on the demo, `Quality_metrics` and `Detailed_summary`, RAN `facts.py` (1)): a line or not? D-0346 speaks only of joins no plot reads.
- One file read as two tables (`Summary` and `Summary_quality` read the same file, RAN `ids.py`). For the walk they are two tables and their non-key columns are two columns. A filter on a column of one does not touch the other, although it is the same column of the same file.
- A column replaced by another column's values under the same name (table of 1.2).
- The value written at a place where a key has another type (whole number against text): D-0202 says typed per place; what a value that cannot be typed does is DESIGN question 12.

## 2. The architect's top flag (for the owner)

### 2.1 What I checked

RAN `scope.py` on the demo recipe (17 plots, 12 source tables, 16 joins). 11 source tables declare `sample_id` as their key (`is_entity_key`); every join of the demo that names `sample_id` joins on it with the same name on both sides.

Start: `sample_id` at the plot `mlst_bar`, the request "remove sample S7, everything ticked".

| Reading of the walk | Source tables reached | Plots changed |
|---|---|---|
| (a) one pass: back to this plot's sources, forward from them (the architect's reading) | 2 | 13 of 17 |
| (a') one pass, where move 3 also adds the tables met on the way back from every reached join | 8 | 15 |
| (b) follow the joins that equate the key until nothing new comes (the closure) | 8 | 15 |
| (c) every source table that declares the key | 11 | 17 |

From `amr_heatmap` the same sample gives (a) 1 source and 5 plots, (a') 6 sources and 14 plots, (b) 8 and 15. From `qa_l50_integer`: (a) 1 and 5, (b) 8 and 15. The four source tables that no join links to the metadata (`Summary`, `Summary_quality`, `Quality_metrics`, `Detailed_summary`) hold exactly the same 42 sample ids as the metadata (RAN `ids.py`): S7 is really there.

So the architect is right, and two facts are worse than written:
1. **Under (a), the result depends on where she clicks.** The same sample, removed with everything ticked, leaves a different audit recipe when she starts from `mlst_bar` (13 plots changed) than from `amr_heatmap` (5 plots). "The same data and recipe give the same result" is kept (the dialog shows what it does), but the same intent gives two different results, and nothing tells her why.
2. **The test design and the build plan disagree with themselves.** DESIGN case L014 asks that every start of one column gives the same lines; case L052 asks that after "remove from all tables" S3 is absent from every table and plot table of the demo. BUILD_PLAN step 1 lists both as tests and takes (a) as its provisional scope. On the demo, (a) fails L014 (2 sources against 1) and L052 (S7 stays in the Summary plots); (b) passes L014 and fails L052; only (c) passes L052. One of the three must change before step 1 is tested.

### 2.2 Is it a conflict with D-0022?

D-0022 (DECIDED): "one mechanism for every removal = a filter on a field, the lineage shows where the field exists, ... only automatic placement 'remove from all tables'". Its source text (READ `home_audit_steps.md` section 5a, points 3 and 7) says: "'Everywhere' simply means every node where the field exists" and "for 'remove from all tables' every table that has the ID is ticked". So D-0022 already describes a separate placement whose scope is the whole recipe, every table that has the id, and that covers the gap. But D-0022 finds the tables by the NAME of the field ("renames are not tracked", point 8), while D-0347, D-0351 and D-0352 find them by the identity of the column. The two agree for an unrenamed key in a recipe where every table is linked; they disagree in two cases:
- tables that hold the same id and that no join links (the Summary tables): D-0022 includes them, D-0347 read as one pass does not;
- a column of the same name that is another column (`country` of table B against `country` of table A renamed to `origin`; the scientist RAN it): D-0022 by name would write at the wrong column, D-0347 does not.

Neither line replaces the other in the ledger (D-0347 says "applies D-0195; refines D-0325, D-0337 and D-0346"). So it is not a contradiction between records that must stop the work (rule H): it is two decided rules that meet and do not say how. The owner must say how.

### 2.3 Is each scope well defined?

- (a) Well defined only once move 3 is made precise: does "back again from each of those along its own path" ADD the tables it meets (a') or only describe the lines already found (a)? D-0347's words do not say. (a') is not stable either: one more round adds more (RAN: from `amr_heatmap` 6 sources after one round, 8 after the fixpoint, 3 rounds).
- (b) Well defined: it is the set of occurrences linked to the start (part 1.1), the natural meaning of "the same column" once a join key counts as one column on both sides. It gives the same answer from every start (L014 holds by construction). It does not reach tables that no join links.
- (c) Not well defined in general. It rests on the column NAME declared as key: two tables could each declare a key called `id` that means a sample in one and a gene in the other; a recipe with numbered ids (`1`, `2`, ...) in two unrelated tables would remove id 7 from both, and the line would show "1 row removed", which looks right. It also misses a key declared under another name (`isolate`) that no join equates. And `is_entity_key` decides scope, while the decided design says "the key is information, not mechanism" (`home_audit_steps.md` 5a point 3). Today `key_families()` is by name for the whole recipe and is a builder's provisional choice (READ `recipe_graph.py:47-48`). On the demo, (c) is right: same name, same ids (RAN).

### 2.4 What the owner must choose (plain words)

What she sees first: she clicks "remove this sample" on one plot. The dialog lists places, all ticked.

- **Option 1: only what this plot's data comes from, and what is built from it** (reading a). Pro: the narrowest; nothing she did not look at. Con: on the demo, starting from "MLST bar" leaves the sample in 4 plots, starting from "AMR heatmap" in 12; the list depends on where she clicked.
- **Option 2: every table linked to this one by a join on the sample id** (reading b). Pro: the same list from any plot; follows the data. Con: on the demo it still leaves the sample in 2 plots (the Summary tables are not joined to the rest).
- **Option 3: option 2, plus a separate group "same sample id, no join links these tables", also ticked** (reading c shown apart). Pro: on the demo the sample is gone everywhere, as "remove from all tables" promises (D-0022); she sees which tables are linked only by the id's name and can untick them. Con: in a recipe where two tables use the same key name for different things, the second group removes the wrong rows unless she unticks it; she must read the group.
- **Option 4: option 2, with the group of option 3 shown but not ticked.** Pro: nothing is removed on a guess. Con: the commonest case (a bad sample) leaves the sample in unlinked tables unless she ticks them.

Recommendation: option 3 when the request is "remove this sample" (that is what D-0022's text says, and D-0194 says the commonest case is a bad sample), option 2 for every other filter. In both, the dialog says how many rows each table loses, so a table that holds the id under another meaning shows a number she can question. Suggestion: whatever she picks, the walk returns all three groups as data, so a later change of mind changes only what is ticked, not the walk.

## 3. The four questions: consistency, and a counter-example each

### Question 1 (a rename across two tiers): recommendation "one column, named per tier"
Consistent with D-0352 (DECIDED for one tier), D-0337 and D-0353 (both keep identity through a change), and with question 3 (a gone place stays a different fact). I could not build a counter-example where it gives a wrong line. Tried: (i) a rename that removes a clash (the scientist's MR recipe: the walk follows A's column as `origin` through the join and B's `country` stays another column: correct); (ii) a swap `{a: b, b: a}` with equal types (RAN: Polars renames at once, so the mapping is followed exactly; the plan cannot confirm it but cannot contradict it either); (iii) a rename in tier 2 of a table no plot reads (applied nowhere, so not a place: consistent). One correction to the plan: the swap does not need to be grey for safety. Polars' simultaneous rename is a fact we can pin with one test (RAN `facts.py` (2), and READ the engine calls `rename` once). Grey is still the safe provisional; the plan's condition for lifting it is right.

### Question 2 (what the reach counts): recommendation "both, said apart"
Consistent with D-0346 ("a join that no plot reads is not offered": that is about lines) and with F-B (reach = the nodes whose key changes). Two corrections:
- For a DROP, a gone place below the drop is in the reach (its key changes) but its content does not change (the column was already not there). So for a drop "reaches" and "changes" differ, and the reach sentence must not say "changes" (D-0318 already separates "table changed" from "picture changed").
- "4 more stored tables": see part 1.3 point 4 (true only once D-0326 is built and builds unread joins).

### Question 3 (a place where the column is gone): recommendation "a note, with the row change"
Consistent with D-0195 (no silent failure) and with question 2. Two corrections:
- With a plan after every step, the step that removed the column is ALWAYS known when the plan answered (the first step after which the name is absent). So "known gone" against "unknown" collapses to: gone (the plan answered) against grey (the plan failed, or the prediction and the plan disagree). The plan's extra category "a step the list does not know removed it" is not needed for gone; it is needed only for identity.
- For a drop the note says "the table does not change here", not a row change (point above).
Counter-example tried: a gone place where a column of the same NAME but another identity exists (A's `country` gone, B's `country` arrives by a join). The note must say "the `country` here is another column"; otherwise the user reads "gone" next to a table that visibly has `country`. Not a break of the recommendation, a sentence it needs.

### Question 4 (the drop of a key column): recommendation "the refusal as built, for now"
Consistent with D-0297 and safe. Two facts the owner should see:
- The rule as built is by NAME for the whole recipe and also refuses declared entity keys (`is_entity_key`), not only join keys (READ `join_keys.py:328-339`). D-0297's line speaks of "a column that is a join key". I did not find the ledger line that adds declared keys; it may exist elsewhere. Suggestion: a scout checks it.
- Counter-example to the by-name rule (REASONED, not run): a key renamed in tier 2 only (`sample_id` to `id`) on a path no join reads: dropping `id` is accepted (its name is not a key name), while dropping `sample_id` at a plot-only place is refused. And an unrelated column that happens to be named like a key anywhere (`id` of a gene table) cannot be dropped. Neither is a silent wrong result: the first breaks nothing (no join reads it), the second refuses a harmless action visibly. So the by-name rule is safe as a provisional, as the plan says.
The data scientist's slip noted by the architect is real (READ `scientist.md:142` against his own line 139): an audit step at `T3:PK` runs after PK's own select (D-0332: "the engine runs steps, then audit_steps"; the architect cites D-0146, whose position rule D-0332 replaced for the file), so dropping `sample_id` there leaves `[mic]` and is legitimate under a place-aware rule.

## 4. What the mechanism can and cannot prove

### 4.1 What the plan says and does not say (RAN `facts.py`)
- A filter never changes the plan (4); a value of the wrong type passes the plan and fails only when rows are read (4b). One exception the plan misses: below a pivot, the columns come from the rows, so a filter upstream can remove a column downstream and break a later step (DESIGN F-C, L081). No shipped recipe has a pivot.
- An in-place recompute with the same type is invisible (6).
- A swap of two columns of equal type is invisible; the engine's semantics are known.
- An aggregation keeps the name and the type; a column not in the aggregation disappears at that step (5), and the plan per step says at which step.

### 4.2 Is "grey when not provable" enough?
No. It guarantees that no single line is ticked on a guess about identity, but not:
1. **That the SET is complete.** A walk that stops early returns only true lines. The plan's check "the nodes of the reach equal lines plus gone plus grey" (L087) is computed from the walk's own reach, so it cannot see a scope that is too small (part 2). Completeness needs an outside count.
2. **That a "same column" is the same quantity.** D-0353 accepts that (with a note).
3. **That a ticked step runs.** For a filter the plan cannot tell (wrong-typed value, pivot below). Only the real run when the step is applied can (D-0325 already says it happens then).

### 4.3 The smallest set of invariants, each with the test that proves it

| # | Invariant | Test |
|---|---|---|
| I1 | Every line names a place `add_step` accepts, and the name it shows exists in the plan at the end of that place | Property over every column of every table of every fixture and shipped recipe (E2) |
| I2 | The set of lines is the same from every start of one identity (only "you are here" and the notes move) | L014 on fixtures AND on the demo (it fails today under reading (a), part 2) |
| I3 | Nothing is lost: reach nodes = lines + gone + grey; counts are lengths of these sets, never stored | L087 |
| I4 | "Remove sample v, everything ticked": after the real run, v is in no table and no plot table of the chosen scope; every table outside the scope that still holds v is listed by the walk, with the reason | E1 (counterfactual deletion) on the demo with 3 ids; the list of tables still holding v computed from the data files, not from the walk |
| I5 | Nothing outside the union of the ticked lines' reach changes | E5 (keys) plus a content comparison of every other table (P6) |
| I6 | Every ticked line's step, written there, builds | For a drop: the plan of each candidate copy; for a filter: the real run of the audit copy with all lines ticked, on every shipped recipe and fixture with a typed value per place |
| I7 | Every reading of a step argument agrees with the plan after that step; a disagreement greys and fails the test | L086 on every step of every shipped recipe |
| I8 | Same input, same output, same order, in two processes and several hash seeds; inputs unchanged; no file, row or clock | L076, L077 |
| I9 | The walk on the audit copy differs from the walk on the original only where audit steps are, and each difference names the audit step | L066, L067 plus a property: walk(copy) and walk(original) compared line by line |

## 5. The build steps

1. **Order.** Sound for 0a, 0c, 0b, then steps 2 to 5. Two corrections:
   - Step 1 lists L014 and L052 while taking scope (a): they cannot pass on the demo (part 2). Suggestion: step 1 computes the identity closure (b) and the unlinked same-key tables (c) as data, and tests L014 on (b); L052 waits for the owner's scope answer.
   - Step 1's proof "no step on the path names it" needs the per-step plans and needs to know which columns a `with_columns` writes. The first exists only with 0b or the oracle literals; the second is the extra reading of part 1.3 point 1. With the four readings of D-0351 only, the identity can still be proved (a name present before and after a step is the same column by D-0353, a drop then a creation shows as a gap in the per-step plans), but the line cannot say "recomputed here". So step 1 can stand on D-0351's four readings if it writes no recompute note; step 3 (the notes) waits for the owner's answer on the list.
2. **Records that a later step would force to rewrite. Fix them now (in step 0a):**
   - `Line.here` must be a tuple of occurrences (name, type, trail), not one: a self-join and a full join give two occurrences of one identity at one place (RAN `facts.py` (3)).
   - Each line carries its scope group: linked through this plot's lineage, linked by a join on the key, or "same key name, no join links them". The owner's scope answer then only decides which groups are shown and ticked.
   - `Gone` carries the kind of step it was computed for: for a filter the rows change, for a drop the table does not.
   - Each line carries the kind of each join on its path (left, inner, semi, anti, right, full) and its side (base or right table): what a removal does there depends on it.
   - The PlanBook interface: keyed (node, k) with k counting author steps then audit steps; the plan of a join's tier 1 before its join step (the base table after its own pre-join steps: 3 shipped joins have steps before their join step, RAN `shapes.py`); a failure entry for every node below a failure.
3. **Is step 0b needed before step 1?** Not for writing step 1 and its tests on fixtures: the walk takes the plans as an argument, and the oracle makes them. Yes before step 1 is called done: the checks on the shipped recipes (E2, L086) need a plan book of the real engine, and the only other source is `tmpAI/panel/column_tracking/measure/m.py`, a copy of the orchestrator's logic (a second code path, which the principles forbid as a permanent solution). So: 0a, then step 1 on fixtures; 0b after the branch merge; then step 1's real-recipe checks.
4. **Provisional behaviours.**
   - Safe (grey or narrower, and said): collapse of an empty tier 2 (the reach shown is true); full join grey; unknown action grey; the swap grey; the key drop refused by name; the type note with both engine strings; graph order with "you are here".
   - Not safe even provisionally: scope (a) for "remove this sample" with everything ticked, unless the dialog shows, in the same view, the tables that still hold the id (the `outside` list) and the plan tests the sentence. Without that list in the dialog it is a silent partial removal. The plan lists `outside` as data; it must be on the screen before any dialog uses step 1.
   - Not safe: writing a recompute note from the action name alone ("step 2, with_columns, may change it") on every column: it puts a false note on columns the step does not touch (the demo's `era` step would mark `sample_id`). Either read the output names (owner's answer) or write no recompute note.

## 6. What everyone missed

Edge cases and things to track that are in none of the three viewpoints nor in DESIGN.md, or only in part:
1. The answer depends on the start plot under reading (a) (part 2). Nobody said it; it is a reproducibility of intent problem.
2. L014 and L052 contradict the provisional scope; L052 contradicts itself ("every table that holds the key (by identity)" and "absent from every table" differ on the demo).
3. The build plan's reading list goes beyond D-0351 (part 1.3 point 1).
4. Several occurrences of one identity at one place (self-join, full join). The record and the step written there are undefined.
5. Anti, semi, right and full joins: a removal at the right table can add rows downstream (anti). Not shipped; must be grey until decided.
6. One file read as two tables (`Summary`, `Summary_quality`). The walk splits the file's columns into two identities.
7. Source tables that nothing reads (`Quality_metrics`, `Detailed_summary`): line or not.
8. Lines labelled "source file" by the user viewpoint are written after the source's own tier 1 steps (D-0332). On the demo, `MLST`'s tier 1 recodes and fills `sequence_type` before the place, so "remove `-`" matches 0 rows there (the scientist RAN it). The word "file" must not be used for a T1 place.
9. A column replaced by another column's values under its own name: D-0353 makes it the same column; a filter typed for the old meaning is applied to the new one. Only the note and the row count protect her.
10. DESIGN U1 (identity ends at an aggregation) is out of date since D-0353; DESIGN U8 (wider reading list) was not what D-0351 decided.
11. The architect's key-family wording: his `closure.py` counts the sources that HAVE a field `sample_id`, not those that declare it a key (READ `closure.py`); on the demo the two counts are equal (11 and 11, RAN), so his figures stand.
12. `key_drop_problem` also refuses declared entity keys, beyond D-0297's words (part 3, question 4).
13. "Stored tables" in the reach sentence depends on the opening build of D-0326, not built (part 1.3 point 4).
14. Questions nobody asked: what happens to the lines when the start column is itself created inside the start node (`era`): DESIGN says identity starts there, so the only lines are that node and below; the user wanting "remove the Early samples everywhere" must translate to `year < 2024` herself (the scientist mentions it, D 9). Suggestion: the line says "created here from `year` at step 1" and nothing more (no translation offered: the software informs, it does not choose).

Errors found in the viewpoints:
- Scientist, `scientist.md:142`: `T3:PK` grey for a drop of `sample_id` is a slip (part 3, question 4). The architect is right; the governing line is D-0332, not D-0146.
- Architect, flag 1: the figures are right; the conclusion "the walk as written" hides that "as written" has two readings (a) and (a') (part 2.3).
- Architect, step 1: lists L014 and L052 as tests with scope (a): they fail on the demo.
- Architect, 3.3 and 4.2 step 0c: the extended reading list is presented as MINE without saying that it goes beyond D-0351 and close to what D-0325 excluded.
- Architect, part 3 (question 2): "4 stored tables" assumes the opening build.

## 7. Verdict and questions for the owner

### 7.1 Can the build start now?
Yes, with these steps, which need no answer from the owner:
- **Step 0a** (types, fixtures, the oracle, the wrong walkers), with the record fixes of part 5 point 2.
- **Step 0c restricted to the four readings D-0351 decided** (rename mapping, join keys and suffix, drop columns, select columns), plus the actions that only remove or reorder rows (`join_keys.ROW_STEPS`), and the agreement test on every shipped step. The other readings wait for question O2.
- **Step 0b** (the plan built by the same code as the build) after the merge of the branch `task/slice-c-audit-form`.
- **Step 1 on fixtures**: the identity closure (b), the unlinked same-key group (c) as data, gone places, grey reasons, reach sets, no recompute note. Its tests L014 on (b); L052 waits for question O1.

Not before an answer: L052 and the default ticks of "remove this sample" (O1); the recompute and fill notes and any line below a `with_columns` other than by presence (O2); the drop rule by place (O6).

### 7.2 Questions for the owner, in the order they block

**O1. When you remove a sample from one plot, which tables get a line, all ticked?** (Blocks step 1's main test.) You click "remove this sample" on the plot "MLST bar".
- (1) Only the tables this plot's data comes from, and what is built from them. Pro: narrowest. Con: the sample stays in 4 plots; from another plot the list is different.
- (2) Every table joined to these on the sample id. Pro: the same list from any plot. Con: on the demo the sample stays in the 2 Summary plots.
- (3) As (2), plus a separate group "same sample id, no join links these tables", ticked. Pro: the sample is gone everywhere, as "remove from all tables" says. Con: where two tables use the same key name for different things, that group removes the wrong rows unless you untick it.
- (4) As (3), the group shown but not ticked. Pro: nothing removed on a name alone. Con: the bad sample stays in the unlinked tables unless you tick them.
- Recommendation: (3) for "remove this sample", (2) for other filters.

**O2. May the walk read what a step writes beyond the four you listed?** (Blocks the notes of step 3; without it most of the demo's lines are grey or carry no note.) You decided the walk may read the mapping of a rename, the keys and suffix of a join, and the columns of a drop or a select. To write "recomputed here" (your decision on a recompute) it must also read the names a computed-columns step writes, the group and result names of a grouping, and the columns a cast, a fill or a strip names.
- Yes: the line says "values recoded by step 2" where it is true. Pro: the note you asked for. Con: more of the recipe is read; still checked against the plan where the plan can tell.
- No: the line says nothing about recomputes; or every place below such a step is grey. Pro: the walk reads only what you listed. Con: on the demo, 48 of 73 tables and plots sit at or below such a step.
- Recommendation: yes, limited to the names a step writes, never its expressions.

**O3. A column renamed in tier 1 and renamed back in tier 2: one column named per table?** (Blocks the rename-back case of step 2; no shipped recipe does it.) Pro: no partial removal. Con: none found. Recommendation: one column. This only confirms the coordinator's reading of your decision.

**O4. A place where the column is gone: a note under the line, with "N rows removed" for a filter and "table unchanged" for a drop?** (Wording; can wait.) Recommendation: yes.

**O5. The reach: "16 tables you can open and 13 plots; 4 more tables that no plot reads are also built from it"?** (Wording; can wait.) Recommendation: yes, and the word "stored" only once the opening build exists.

**O6. Dropping a key column: refused by its name everywhere (as today), or only where a join reads it?** (Blocks the drop rule of step 4.) By name: one plain refusal; it also blocks dropping it from one plot's table. By place: allows that; each place is checked by the engine. Recommendation: by name for now. Please also say whether "the declared key of a table" is meant to be refused like a join key: the code refuses both, your decision names join keys.

**O7. Tables that no plot and no join reads (on the demo `Quality_metrics`, `Detailed_summary`): a line?** (Blocks O1's option 3 on the demo.) Recommendation: listed in the group of option 3, not ticked, because no plot shows them.

**O8. A self-join, and joins that are not left or inner (anti, semi, right, full).** (Not shipped; can wait.) Recommendation: grey with the reason until a recipe needs them.

## What I could not verify
- That the build plan's figures on cost and on the 108 places are right (I did not rerun them).
- The behaviour of the real audit run on unread joins (whether `run_audit` builds them).
- Whether a ledger line beyond D-0297 decided that declared entity keys cannot be dropped.
- Anything about a pivot, a tier 3 with steps, or anti or semi joins on real data: no shipped recipe has them.
- The counter-example of question 4 (renamed key accepted by the by-name rule) was reasoned, not run.
