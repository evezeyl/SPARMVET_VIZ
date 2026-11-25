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

