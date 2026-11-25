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

