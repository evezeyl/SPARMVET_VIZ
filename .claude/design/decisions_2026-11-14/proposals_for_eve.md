# Proposals for Eve (prepared by the coordinator with the viewpoint agents; nothing here is decided)

Evidence classes: RUN (proved by running code), READ (read in a file), INFERRED (reasoning, not checked).
Viewpoints: S = scientist and data scientist, A = architect (also effort and risk), U = user who is not a developer.

---

## Batch 1 (2026-11-14): the HOME view and the export disagree

Findings (root cause, by running): `tmpAI/panel/export_value/findings.md`, `tmpAI/panel/step_order/findings.md`. Brief: `tmpAI/panel/brief_view_vs_export.md`.

### Flags first
1. **Silent, in the app today (RUN):** with a filter and a drop on the same column in one audit, the PLOT ignores the filter without a message. Shipped plot `QA_population_zscore`, filter `n50 >= 324189`, then drop `n50`: table 21 rows, plot 42 rows. The results bundle then holds a TSV of 21 rows and a plot of 42 rows.
2. **Silent, in the app today (RUN, N9):** a plot filter `in` / `not_in` on a number column compares as text: `in [90.0]` shows no rows in the plot, the table keeps them.
3. **Option C of proposal 1 decides FILTER-UNIFY-1** (open, yours) and touches the rule "no hidden choice" (DEC33).
4. **Several fixes touch files frozen by the build brief S4** (`t3_translator.py`, `export_handlers.py`): each needs your yes.
5. The design already says "a filter on a dropped column is not possible" (`home_audit_steps.md:326`): decided, not built.

### Proposal 1 (N10, N9, N11): a filter value stored as text

**What.** The multi-select box stores text for a number column shown as discrete (Year), for Date and for Boolean. HOME converts the value with the real column type. The export writes the text; the engine step `modif_filter` compares the value as written; the re-run stops with `cannot compare string with numeric type`. A recipe maker who writes `value: "90"` by hand gets the same error. Nothing warns at export time. No silent difference was found in the export.

| Option | S | A | U | Evidence |
|---|---|---|---|---|
| A. Do nothing | Con: a broken bundle with no warning | Con: exports fail at re-run, the checker is silent | Con: the user learns it from a colleague, in jargon | RUN |
| B. The translator writes the value with the step's stored type | Pro: new exports typed. Con: old exports and hand-written recipes stay broken; steps without a stored type cannot be fixed | Small, 1 frozen file. Con: the stored type comes from the T2 sample and can differ at the step's stage; P5 would throw it away | Fixes new exports only, invisibly | READ |
| C. `modif_filter` converts the value to the column type at run time; plain error when it cannot | Pro: one place repairs old and new. Con: changes the engine for every recipe; decides FILTER-UNIFY-1; a conversion the recipe does not show | Small to medium (`modified.py`, `filter_values.py`, tests). The recipe declares the column type (DEC27), so not a hidden choice. Survives P5. Date and Boolean wait for FILTER-DTYPES-1 | Pro: the colleague's re-run works | READ |
| D. The panel stores a typed value at recording | Helps new rows only | Medium; a second place that converts. Not recommended | Invisible; old sessions unchanged | READ |
| E. A check at export (and in the recipe checker) refuses a value that does not fit the column type | Pro: nothing hidden, fits DEC33. Con: the checker does not get declared types today | Medium to large | Pro: the only option where the user sees the problem while they can still act | RUN (checker has no types) |

Recommended by the viewpoints: S = E first, plus the N9 fix now; C only after your decision. A = C, then E later; N9 with FILTER-DTYPES-1. U = C plus E; N9 now. All three: `between` (N11) stays refused with a clear sentence.

**Coordinator's recommendation.** The real question is yours and is FILTER-UNIFY-1: **does the engine convert a filter value to the column's type, or refuse it?**
- I recommend **convert (C)**, with a plain error that names the step, the column and the value when it cannot be converted. Reasons: one place; it repairs exports already written and hand-written recipes; the conversion follows a type that the recipe declares, so the result stays determined by what is recorded. Checked by running (`tmpAI/panel/verify/results.md`, a matrix of column types, value forms and operators): with the conversion as it exists today (`coerce_filter_value`, number columns only), no case that RUNS today gives different rows; only cases that stop with an error today start to run. A value of 90.5 on an integer column is compared as a number today and after (never cut). NOT covered: a conversion for Date, Boolean or text columns would be new code and needs its own check. The matrix becomes a test before any merge.
- **Fix N9 now** (two of three viewpoints): it is silent, small, and 4 strict xfail tests are ready. Consequence: plots with a numeric `in` filter change, towards agreeing with the table.
- **E later**, as a task: a check at export that the written recipe can run. It needs the checker to know the declared types.
- **Not B, not D:** they do not repair what exists.
- If you prefer **refuse**: then E becomes the first build (medium to large) and exports already written stay broken.
- Not covered: Date and Boolean values (a Boolean filter gives no rows in HOME itself); they belong to FILTER-DTYPES-1, which waits for your NaN rule (NA-RULE-63). Not checked: UInt, Decimal, Datetime, Categorical columns.

Sessions and exports saved before: stored steps are not rewritten in any option. Only C makes old exports run.

Proposed message (U), for E: "Filter on 'Year' = 2019: this value is saved as text but the column is a number, so the recipe would stop when re-run. Remove the step and add it again with the number box, or fix the recipe."

### Proposal 2 (N13): a drop and a filter on the same column

**What.** Three orders exist. The table and the exported TSV run all filters, then all drops. The plot (in HOME and in the results bundle) runs all drops, then the filters, and skips a filter whose column is gone. The reproducibility recipe runs the recorded order, top to bottom. It is not a Polars problem. The filter panel still offers a dropped column, and nothing checks when a step is recorded.

| Recorded order | Table and TSV | Plot | Reproducibility re-run |
|---|---|---|---|
| filter n50, then drop n50 | 21 rows | 42 rows (filter ignored) | 21 rows |
| drop n50, then filter n50 | 21 rows | 42 rows (filter ignored) | error: column not in the table |
| drop n50, then exclude a row by n50 | 41 rows | 42 rows | error |

| Option | S | A | U | Evidence |
|---|---|---|---|---|
| A. Do nothing | A figure that does not match its own table cannot be defended | Not acceptable | Silent. No | RUN |
| B. Refuse at recording: the filter panel offers only columns still present; a drop of a column used by a recorded filter is refused or needs a choice | Pro: prevents it; the design promised it. Con: old sessions untouched; needs a UI choice | Small to medium (`filter_and_audit_handlers.py`); already decided, not built | Pro: the user is told at the moment they choose | READ |
| C. Every view runs the recorded order; a step whose column is missing is an error shown | Pro: one truth, matches rule 3 of the contract and P5. Con: views of old sessions change (tell the user) | Large: three paths rewritten; overlaps P5 (not confirmed), may be thrown away | The honest option; old sessions change visibly | READ / RUN |
| D. The translator reorders | Reject: contradicts the recorded order and hides it | Reject (ADR-097, frozen file) | Hides the order. No | READ |
| E. A check at export refuses and names the step | Catches the failing re-run, not the plot mismatch | Small to medium (export handler or checker) | Too late, but a useful safety net | READ |

Recommended by the viewpoints: S = B + C, E as a safety net. A = B + E now, C left to P5. U = B + C (+ E). All three: the silent skip in the plot must go now, independent of the order.

**Coordinator's recommendation.**
1. **Now: B** (build what the design already says).
2. **Now: the plot agrees with the table, and nothing is skipped silently.** Caution, checked by running (`tmpAI/panel/verify/results.md`): removing the skip alone would turn the valid order "filter, then drop" into an error on the plot, because the plot path removes the column before VizFactory applies the filters (`home_theater.py` about 528-533), so the column is absent when the filter runs. So the plot path must apply the audited filters before the drops, as the table does, and show an error only for a step that cannot run.
3. **Now or next: E**, so that an old session with "drop, then filter" gets a plain message at export and not a failing recipe. `export_handlers.py` is frozen: your yes is needed.
4. **C (one recorded order for every view) with P5**, after you confirm or change the stage-2 spec. With B and point 2 in place, every stack a user can record gives the same rows in the table, the plot, the TSV and the re-run.
5. **Not D.**
Also needed: a test for a plot with a drop and a filter on one column (none exists).

Sessions saved before: steps stay as recorded. With 1 to 3, an old "drop, then filter" stack shows 21 rows in table and plot and gets a message at export.

Proposed messages (U). B: "Column 'n50' was dropped in step 2, so it cannot be filtered. Remove step 2 first, or filter a different column." Old session: "Step 3 filters 'n50', which step 2 dropped. This step is not applied. Remove one of the two steps."

**Not checked in the findings:** real clicks in the panel, pending steps, `developer_raw_yaml` steps, the importer's verification, other recipes.

### What you decide (batch 1)
- D1. Convert or refuse a filter value that does not have the column's type (FILTER-UNIFY-1). Recommended: convert in the engine, plain error otherwise.
- D2. Fix the plot `in` / `not_in` comparison now (N9). Recommended: yes.
- D3. Build the recording guard B. Recommended: yes.
- D4. Make the plot follow the table and remove the silent skip now, before P5. Recommended: yes, after a builder confirms the scope.
- D5. A check at export that the reproducibility recipe can run (touches frozen `export_handlers.py`). Recommended: yes.
- D6. The wording of the messages above.

---

## Batch 2 (2026-11-14): joins and gallery

Brief with the options and what is already decided: `tmpAI/panel/brief_joins_gallery.md`. Viewpoints: S and A on all seven points; U on the gallery points and J-c.

### Flags first
1. **Silent row multiplication with a float join key (RUN, S; and RUN through the real ingestion with the type declared in `input_fields`, now a test in `libs/transformer/tests/test_join_key_types.py`: "001", "1", "1.0" are accepted without a message and a join gives 9 rows for 3 samples):** read as Float64, the identifiers "001", "1" and "1.0" all become 1.0, and "S1" becomes missing. A join on such a key returned 4 rows from 2. The shipped `complex_template` declares `sample_id` as Float64 on both sides, and users copy templates. The decided rule "a join keeps the declared types" keeps the type, not the identity of the sample.
2. **A step is dropped silently (READ, A):** the "redundant init" skip (`data_assembler.py:221-223`) covers every step whose right table is the first table, so a real self-join with different left and right keys is also dropped, without a message.
3. **Hidden from the user (READ):** with a read-only gallery folder a failing example is still listed and opens; the reason an example is left out is never shown.
4. **N15 is already decided:** `tasks.md:200` (Q3-GALLERY-SUBMISSION-1, Eve 2026-11-14) says `submit_example` stays. `tasks.md:134` asks again: that line should be closed, not answered again. Deleting the function would reconsider your decision.
5. **Side finding, not verified by running (READ, A):** `complex_template.yaml` names `assets/test_data/genomics_data.tsv` and `metadata.tsv`, which do not exist, so the template cannot run as it is.

### The points

| Point | S | A (with effort) | U | Evidence |
|---|---|---|---|---|
| J-a. Join key rule in three places (N1): A keep three copies with parity tests / B one rule in `libs/utils` | B: one rule, no drift; con: refactor cost | A: the three read different inputs (Polars schemas, type names, declared YAML with "unknown"); about 15 common lines; B is medium (4 files, 3 test files) with risk in the checker's "silent when unknown" logic | not asked | READ |
| J-b. Checker refuses a join key not declared in `input_fields` (N5): A confirm / B advice only / C remove | A: an undeclared key has no known type | A: equals the build's refusal; the checker stays silent when it cannot know. Effort none | not asked | READ |
| J-c. Self-join of the base table skipped silently: A keep / B fail with a message / C warn | B: no hidden step; con: an old recipe may start to fail | B, small (`data_assembler.py`, one test); search the shipped recipes first | B; C is a warning users click through | READ |
| J-d. Template declares `sample_id` as Float64: A leave / B change to a text type / C checker advises against a float join key | B and C: identifiers stay text, leading zeros survive | B, small (2 YAML files), only together with restoring the template's test data; C not needed (wider scope) | not asked | RUN (S), READ (A) |
| G-a. Read-only gallery folder shows a failing example (N3): A keep / B leave failing examples out in memory / C stop the gallery | B: a failing example is never shown as working | B, small (`gallery_viewer.py`, one test); con: the viewer reads two inputs | B, with the list of G-b; C is too much for one bad example | READ |
| G-b. Where the user reads why an example is left out (N4; "reason shown" is decided, not built): A a list under the gallery filters, as HOME does / B alert log only / C console only | A: the reason is visible, as decided | A, medium (`gallery_viewer.py`, a pure function for the list, a test) | A, same wording and layout as HOME's rejected recipes | READ |
| G-c. `submit_example` has no caller (N15) | keep, documented as unused | keep (your decision of 2026-11-14); correct its stale `@deps` line | no visible effect, no view | READ |

**Coordinator's recommendation.**
- **J-a: keep the three copies (A)**, and correct the docstring that says "written twice". The viewpoints split. I follow the architect: the three callers read different things, and the parity tests run against the real build and can fail. Note: your own rule from #62 (shared code in `libs/utils`) points to B; if you prefer B it is a medium task, no result changes.
- **J-b: confirm.** Both viewpoints agree.
- **J-c: fail with a plain message (B)**, after a search of the shipped recipes for a step that relies on the skip. All three agree. Proposed message (U): "Assembly step 1 joins 'X' with itself, so it does nothing. Remove this step from the data analysis recipe." Open detail for you: a real self-join with different keys is dropped today; decide whether such a join is allowed or also refused.
- **J-d: change the template to a text type (B) and add an advice in the checker for a float join key (C as advice, not refusal).** The run check shows a silent wrong result, and advice informs without choosing for the recipe maker. A builder first verifies the side finding (missing data files).
- **G-a: leave failing examples out in memory (B).** All three agree.
- **G-b: a list under the gallery filters (A)**, with HOME's wording. All three agree. Proposed message (U): "N example(s) not shown, failed the check: <name>, <first reason>. Contact: <contact>." For the read-only case: "2 examples are not shown because they failed the check. The gallery folder is read-only, so the list was not rewritten."
- **G-c: nothing to decide.** Close `tasks.md:134`; the `@deps` line is a small correction.

Recipes and sessions saved before: J-c makes a recipe with a self-join first step stop with a message (a search tells how many shipped ones). J-d changes one template only. G-a and G-b change what the gallery lists, never an example file.

### What you decide (batch 2)
- D7. J-a: three copies with parity tests, or one rule in `libs/utils`. Recommended: three copies.
- D8. J-b: confirm the refusal J10. Recommended: yes.
- D9. J-c: fail on a first step that joins the base table with itself; and is a real self-join (different keys) allowed? Recommended: fail; the second part is open.
- D10. J-d: template key to a text type, plus a checker advice against a float join key. Recommended: both.
- D11. G-a: leave failing examples out in memory when the folder is read-only. Recommended: yes.
- D12. G-b: the list under the gallery filters, wording as HOME. Recommended: yes.

---

## Small points (2026-11-14): the coordinator's recommendation only, no panel

These are small technical or record choices; a panel would cost more than the choice. Evidence is what the session's reviewers reported (handoff of 2026-11-14, final section).

| Point | What | Options | Recommended | Why, and the cost |
|---|---|---|---|---|
| D13 (N2) | The Blueprint join preview catches every exception and shows "Preview failed: ..." (`blueprint_handlers.py`, about line 2060). In this session it hid a missing import: the preview failed for every join and no test saw it. | A leave / B catch only the expected errors (a bad key, a type problem, a load problem), let a programming error through | B | A hidden programming error looks to the user like their own mistake. Small, one handler and a test. Blueprint can wait, so no hurry. |
| D14 (N6) | `audit_old_words.py --check` fails on four words (`persona`, `manifest`, `profile`, `project`) and one UML tag. | A fix the text / B adapt the exclusions / C per word | C: first a scout lists every hit; then fix the text where the word is the retired configuration vocabulary, and exclude where the word is current (for example the checker's `profile`, the project root) | An audit that always fails is not read any more. Not checked: how many hits per word. `recipe` waits for RECIPE-WORD-1. |
| D15 (N14) | Tests not written: where the audit writes a step (P5), the key of T3 and the per-collection key (P4), property tests with `hypothesis` (a new dependency). | A wait / B allow `hypothesis` now | A | They test a mechanism that is not confirmed (stage-2 spec v0.1). Decide the dependency when P4 and P5 are confirmed. |
| D16 (N16) | The UML package diagram PKG-TIERS has 6 violations: five missing arrows, one stale arrow (transformer to ingestion). Not new. | A leave / B correct the six arrows | B | The model then says what the code does. Needs StarUML open and your yes for a UML edit; small. |
| D17 (N17) | `rules_verification_testing.md` section 8: add `--durations=10` to the browser command; "about 4 minutes" is now 8 minutes. | A leave / B edit | B | A rule file: your double confirmation. Two lines. |
| D18 (N8) | When the Blueprint package (W14) starts. `tasks.md` line 82 says not now; the night handoff listed it next. | now / after HOME and Gallery | After HOME and Gallery (your priority of 2026-11-14) | The two records should then say the same. BP-VALIDATE-1 (a small, decided check on upload) is being built now at your request. |
| D19 (N11) | `between` has no translation to a recipe step: the export refuses such a step. | A keep refusing / B add the translation | A for now, with a plain sentence; B together with FILTER-DTYPES-1 | All three viewpoints of batch 1 agree. |

---

## NA rule, after the decision of 2026-11-14 (channel M65): what is built now, and five questions

Gap between the decision and the code, proved by running: `tmpAI/panel/na_rule/gap.md`.
- **The engine, the HOME table and the plot already follow the decided rule** (RUN: all nine operators, on a float and a text column with an empty cell and NaN, give the same rows in the three places; an empty cell is removed, NaN is a number).
- **The real gap is "keep":** the HOME filter row has no `na` field, no tick, no count; "keep" exists only in the engine step `modif_filter`.
- **Flag:** the export translator (frozen) always writes `na: remove` (`t3_translator.py:127`). A "keep" chosen in a HOME dialog would be exported as "remove": a silent change of a result. So the dialog tick and the translator change must ship together.
- **Being built now** (no frozen file, no open question): the tests of the decided rule in the three places (three old strict xfails encoded the withdrawn rule and are replaced), a pure function for the two counts and the sentences, the help text of `modif_filter` with the Polars equivalents, the user documentation paragraph.

| # | Question for Eve | Options | Coordinator's recommendation |
|---|---|---|---|
| Q-NA1 | Edit the frozen files for this: `t3_translator.py:127` (write the chosen `na`), `export_handlers.py:220` and `:373-380`, the audit card if it shows `na` | yes / no | Yes: without it the tick cannot ship (silent change). |
| Q-NA2 | "NA (missing)" as a selectable VALUE in a filter (`home_preview_filters.md:72`, decided 2026-11-12): kept next to the new tick, or replaced by it | keep both / the tick replaces it | The tick replaces it: two ways to say the same thing can contradict each other in one step. It reconsiders a decision of 2026-11-12: yours. |
| Q-NA3 | A HOME filter row, a saved session or an old audit step that has no `na` | treat as `remove` (what it did when it was made) / refuse and ask the user | Treat as `remove`, stated in the step when it is shown and exported: it is what those steps did (RUN), so no result changes. |
| Q-NA4 | Does the tick also apply to exploration filters (never exported), or only to audit steps | both / audit only | Both: one dialog, one behaviour; the exploration view must show what the audited step would do. |
| Q-NA5 | Is "keep" offered for `>`, `<` and between (Polars has no switch there; we add `or is missing`) | offer for every operator / only for `==`, `!=`, in, not-in | Your decision point 3 says "all filter options are offered": offer for every operator, the sentence says what happens. Confirm. |
| Q-NA6 | On which table is the count taken, and the text "NA" | the table the filter runs on (the plot's data) / the whole joined table | The table the filter runs on. The text "NA" left as text is a value, not missing: the count sentence must not call it missing (a test is being written). |

---

## Records check (2026-11-14, late): what batch 3a looked like after reading the records and the commits since 2026-11-04

Full result with file:line and commit for each: `tmpAI/panel/records/corrections.md` (READ and git history; the code was not run against the corrected records). 14 stale records are being corrected by a scribe; rule files and ADR text are not touched.

**Settled from the records (no question left for you):**
- C3, C4, C6: of HOME-DESIGN-REVIEW-1 only one point is open (SC4, question R1 below). SC1 was withdrawn; AR4, AR1, AR2 are closed; SC2 and SC5 are decided.
- C7: the hash model was decided on 2026-11-12 (the later lines 51-52 of the hash file win over line 47).
- C8, C9: "option C+" was named only in a commit message (155b930a). DEC23 (2026-11-13) supersedes it: both `final_contract` and the schema `output_fields` are removed, done 2026-11-14.
- C2: the "default keep" lines are replaced by your NA rule of today.
- N15 and the N10 wording are corrected in the records.

**Four questions that the records cannot settle (one at a time):**
| # | Question | The two records |
|---|---|---|
| R1 (SC4) | When you remove samples by an attribute (a country), does the selector find all samples that carry it across the tables (28), or those at the node you look at (21 at `MLST_with_metadata`, which has a year filter)? | `home_design_review_2026-11-12.md:11` and `home_audit_steps.md:119-123` give both numbers and decide neither |
| R2 (IMPORT-PATH-1) | You decided "as production" on 2026-11-14. Which mechanism carries it: a data folder per import (`<user_data>/_imports/<recipe id>/data/` plus a record the orchestrator reads, the recommendation) or another? Also: the name of the imported recipe, and whether the lookup by dataset id accepts `.parquet`. | `tasks.md` (decided: as production) and the findings note of the import task |
| R3 (formulas) | FORMULA-SAFETY-1 and ADR-099 point 14 (allow-list of Polars operations, 2026-11-12) say the same thing, and the list is built (fe856c26). One decision, so both tasks close (same as D22)? | `tasks.md:86`, ADR-099 point 14 |
| R4 (seed) | In HOME, does a seed that the recipe maker fixed (`random_state: 123`) hold, or may the seed drawn per session replace it? | `rules_viz_factory.md` section 8 and ADR-090 say the layer's seed wins; `home_theater.py:408-432` and `plot_config_resolver.py:577-582` overwrite it (READ, not run) |

**For your double confirmation (not applied):**
- No ADR holds the two parity mandates. ADR-035 is "Gallery Taxonomy" and ADR-036 is "UI Integrity", yet `rules_data_engine.md:76`, `rules_viz_factory.md:13` and eight documentation pages cite them for parity with Polars and plotnine. The parity text exists only in the rule files (commit 342f7980, 2026-04-17). Proposal: a new ADR for parity (or for its replacement, see V9 of the visualisation plan), then the citations are corrected.
- `rules_viz_factory.md` section 8: add the per-session seed of ADR-097, after R4.
- ADR-099 points 12 and 15 are stale.
- The rule files that still describe `final_contract` (the D24 list).

---

## Found while building (2026-11-14, evening): small points, the coordinator's recommendation only

| Point | What (evidence) | Options | Recommended |
|---|---|---|---|
| D24 | **Rule files still describe the old recipe format** (READ by the docs builder, RECIPE-DOCS-1; rule files need your double confirmation, none was edited): `rules_data_analysis_recipe_structure.md` lines 4, 26, 42-44, 60, 63, 66, 70, 94, 202-214, 333, 335 (`output_fields`, the old `categorical` type, `action: join/mutate/cast/sort`, the unquoted `on` fallback, `final_contract`); `rules_agent_role_bioscientist.md` lines 22, 71, 89, 105, 119-136, 194-208, 227, 249, 308, 327, 354, 383, 396-399, 411 (old action names, `final_contract`, the action list of section 8); `rules_data_engine.md` 70, 74; `rules_test_lab.md` 135, 143; `rules_code_quality.md` 63, 65; `ui_implementation_contract.md` 85, 97, 684, 686, 689. Also ADR-099 point 16(g) says unknown keys are warnings; the checker now refuses them. | A leave / B a builder prepares the diff of each rule file for you to read, you confirm, then it is merged | B, one file at a time, the two large ones first: agents read these rules at every start and still learn the old format from them |
| D25 | **An orphan fragment with three removed actions** (RUN by the reviewer): `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml` uses `derive_categories`, `drop_duplicates`, `summarize`. No shipped recipe includes it; the checker test covers only top-level recipe files, so fragment files that nothing includes are never checked. | A delete the file / B migrate it to format 1 / C leave | A, plus a test that fails when a file under a recipe's folder is included by nothing (so the next orphan is seen). If the fragment holds analysis you want to keep, B. |
| D26 | **Two helper scripts still speak the old format** in their own headers (READ): `normalize_data_analysis_recipe_fields.py`, `debug_apply_data_analysis_recipe_standards.py` (documented in `docs/appendix/running_helper_scripts.qmd` 28-32, 141). | A remove them and their documentation / B bring them to format 1 | Not checked whether anything still calls them: a scout first; remove if nothing does |
| D27 | **The Blueprint agent tool `get_field_contract` still returns `output_fields`** (`libs/blueprint_arch/src/blueprint_arch/agent_tools.py:202`, READ), a key the format no longer has. | A leave until the Blueprint package / B correct now | A: Blueprint waits (your priority); record it in the Blueprint package |
| D28 | **Two documentation statements not settled** (READ): `docs/foundations/data_contracts_adr.qmd` step 2b ("Identity Fallback", "Strict Assembly") is not verified against the assembler; `docs/workflows/wrangling.qmd` line 8 still says row order may differ between runs. | a reviewer verifies both against the code and a builder corrects | yes, no decision needed: I dispatch it |

---

## Batch 3a (2026-11-14): what blocks the HOME rebuild: records that contradict each other

A scout read the records (READ, file:line below; nothing run). **Main finding: several points listed as "waiting for Eve" are written elsewhere as already confirmed or closed.** Before any panel, each needs one answer from you: which record is current. These are confirmations, not new choices.

| Point | Record that says it is settled | Record that says it waits | Question for you |
|---|---|---|---|
| C1. NA rule of #63 (a missing value is a value; `!=` and "none of" keep it; `==`, "one of" and comparisons remove it; always counted; message "N rows have no value in this column: they are kept / removed") | `home_audit_steps.md:591`: "Confirmed 2026-11-12 (Eve, P6)" | `tasks.md:38`: "confirm with Eve, then unblock" | Is the rule confirmed as written at `home_audit_steps.md:587-591`? If yes, NA-RULE-63, then FILTER-DTYPES-1 and stage-2 P1 can be built. |
| C2. Default for missing values when rows are removed | `tasks.md:83` (O25): default keep, a recipe maker's choice; `home_audit_steps.md:523`: "safe default: keep", needs your default | `tasks.md:82` and `tasks.md:91`: no default | Default "keep", or no default (the user or recipe maker must choose)? A panel is asked (batch 3b). |
| C3. Design review items AR4, AR2, AR1 | `home_audit_steps.md:492-493`: closed | the review file line 16 (AR4 "Open"); `tasks.md:74` still lists all three | Closed? Then they leave HOME-DESIGN-REVIEW-1. |
| C4. Design review item SC1 (check that the filter acts on the plotted variable) | the review file line 14: "Withdrawn by Eve, 2026-11-12" | `tasks.md:74` still lists it | Withdrawn? |
| C5. SC4 (remove by attribute) | principle decided, `home_audit_steps.md:494` | one point open: which samples the selector finds (28 or 21) | The open point only. |
| C6. SC2 (caption count for plots without a key), SC5 (`exclusions.tsv` in the export) | none | open in the review file | Really open: to discuss. |
| C7. Hash model (KEYS-NODE-1) | `home_hash_model_2026-11-12.md:51-52`: a decided list; point (2) "no separate coarse phase unless the graph is late" | the same file line 47 keeps a coarse phase 1; line 50 says "the one still open" and lists none | Confirm the model; say whether the coarse phase stays. |
| C8. "Option C+" (RECIPE-GRAPH-UTILS-1) | none | `tasks.md:48`: "option C+, Eve decides" | **The options A, B, C and C+ are not written in any file under `.claude/`** (search by the scout). What is option C+? It was probably said in a chat only. Without it nobody can build `utils.recipe_graph`, and stage-2 P3, P4 and everything after wait for it. |
| C9. `final_contract` | `recipe_format_spec.md:292` and `tasks.md:82`: removed (use `polars_select`) | `tasks.md:48` keeps it as the last operation of T1 | Removed? Then `tasks.md:48` is corrected. |
| C10. Stage-2 spec v0.1 (`home_stage2_mechanism_spec.md`) | none | seven open points in its section 6 (lines 71-78); P1 includes the NA rule | Your reading. Order: P0, then P1 (after P0), P2 (recipe format), P3 (after P2), P4 (after P3), P5 (after P1, P3, P4), then P6 to P12. |
| C11. ADR-099 | `architecture_decisions.md:4958`: "ACCEPTED in principle (2026-11-11). Not built." Items marked [confirm] in `home_audit_steps.md` section 16 need your OK | | Those [confirm] items. |
| C12. FORMULA-SAFETY-1 | options A to D and a recommendation exist: `home_evidence/actions_and_polars_2026-11-13.md:89-94` | `tasks.md:86`: "Decision: Eve" | Keep formulas with a safe workaround, or block them now. A panel is asked (batch 3b). |

**Coordinator's recommendation.** Answer C1, C3, C4, C9 first: they are one-word confirmations, and C1 alone unlocks three builds (NA-RULE-63, FILTER-DTYPES-1, the start of P1). Then C8, because the whole graph work waits for a definition nobody can find. C7 and C10 need your reading time; I can have the viewpoints review the stage-2 spec (design-review personas) if you want that before you read it.

---

## Batch 3b (2026-11-14): the default for missing values (C2) and formulas (C12)

Brief: `tmpAI/panel/brief_na_default_formulas.md`. Viewpoints: S and A on both; U on missing values.

### Flags first
1. **An empty cell and NaN are not the same in the engine (RUN, S):** on the values 1, empty, NaN, 3: every comparison drops the row with the empty cell; NaN counts as larger than every number, so `> 1` KEEPS the NaN row and `< 1` drops it. The design file says "NaN follows the same rule" (`home_audit_steps.md:590`); the code says the `na` choice does not touch NaN (`transformer/actions/modified.py:51`). Today this is invisible to the user.
2. **A default of "keep" would change today's results** for `!=` and "not in" (READ, S).
3. **Formulas: the question is partly out of date (READ, A).** The allow-list (option A) is already built on this branch and on `dev`: `libs/utils/src/utils/formula_check.py` (commit `fe856c26`), used by the checker (`recipe_check.py:448`) and at run time. **`main` still runs the old unrestricted evaluation until `dev` is merged.** The task FORMULA-SAFETY-1 is still open in `tasks.md`, and the evidence file's line numbers are stale.

### Proposal 3 (C2): missing values when a filter removes rows

| Option | S | A (with effort) | U | Evidence |
|---|---|---|---|---|
| A. Default keep | Con: a default hides a choice that depends on the data; contradicts your reason that the software cannot know what missing means | Con: a silent choice for `==` and `>`; contradicts "no default" (2026-11-13, later than O25) | Extra samples with no measurement look like data; hidden unless the count is read | READ |
| B. Default remove | Con: silent loss of samples that failed and should be rerun | Polars' own result, but silently drops `!=` rows | Samples vanish, n shrinks, hidden | READ / INFERRED |
| C. No default: the choice is required | Pro: matches your reason and the ruling of 2026-11-13. Con: one click per step | **Already built in the engine:** `modif_filter` requires `na`, no default (`modified.py:36,84`). The recipe never depends on a hidden rule | Con: a question the user may not understand, clicked through (warning fatigue) | READ |
| D. The rule by operator (`!=` and "none of" keep; `==`, "one of", comparisons remove) | A default in disguise as an engine rule; fine as a visible preselection | Sensible as a preselection in the HOME dialog only | Pro: matches intuition ("not Norway means everything else"); honest with the count | RUN (Polars does this for empty cells) |

Recommended by the viewpoints: all three converge. **The engine keeps "no default" (C, built). The HOME filter dialog preselects by operator (D), as a visible tick the user can flip, with the count. The step written to the audit and to the recipe always states the choice explicitly.** A recipe step written by a recipe maker has no preselection: the choice is required. NaN is reported as its own count, not folded into "missing".

**Coordinator's recommendation:** as the three viewpoints. Consequences: the audit and the exported recipe hold the same explicit text, so the result never depends on a hidden rule; `tasks.md` lines 82, 83, 91 and the design file lines 523 and 590 get one wording; line 590 ("NaN follows the same rule") is corrected or the code is changed, your choice (S and A both prefer a separate count, with `polars_fill_nan` / `polars_drop_nans` as the explicit steps). Effort: small (records, the dialog, the translator: a frozen file).

Proposed wording (U). Choice: "Some rows have no value in this column. Keep them or remove them? (Preselected for 'is not': kept. For 'is' and 'greater than': removed.)" Count: "12 of 240 rows have no value in 'identity': removed. 3 further rows have a failed calculation: removed. Tick here to keep them." For the user, "empty" means no value was recorded, and "not a number" means a calculation failed.

### Proposal 4 (C12): formulas in recipes (FORMULA-SAFETY-1)

State (READ, A): the three places that evaluate a formula now pass through a check. Two (`polars_calls.py:205`, `id_reconciliation/core.py:254`) call `evaluate_formula`: the formula is checked as a syntax tree, then run with no builtins. The plot function (`viz_factory/geoms/core.py:1330`) allows only a one-argument function over numbers with numpy maths. A recipe from an untrusted source cannot import, read or write files, or call arbitrary functions. It can still use up processor time or memory (written in the module's docstring). Not proven: that every Polars method which takes a function is on the denial list (the list is read from signatures).
The viewpoints disagreed on one fact (S: the plot function "has no restriction at all"; A: it is restricted). Settled by running (`tmpAI/panel/verify/results.md`): it IS restricted today. `lambda x: x**2` is evaluated; an import, an attribute walk through `__class__` and a call to `open` are each refused with a message. Not audited: the allow-list itself for other ways around it.

| Option | S | A |
|---|---|---|
| A. Allow-list | Keeps every formula the analyses need; needs attack tests | Built; one rule in one place |
| B. Single steps instead of formulas | Transparent; some expressions have no step | Afterwards, step by step |
| C. Consent only | No defence | No |
| D. Block now | Breaks the 6 formulas of the 4 shipped recipes; `when/then` and `over` are lost | Not needed now |

**Coordinator's recommendation:** confirm option A as built and close FORMULA-SAFETY-1, with three small follow-ups that need no further decision once you confirm: (1) a reviewer runs a mutation check on the 11 formula tests; (2) the stale line numbers in the evidence file are corrected; (3) a test lists the Polars methods that accept a function and proves each is refused. Yours to decide: whether to add a time or size limit (processor and memory use remain possible).

### What you decide (batch 3b)
- D20. Missing values: engine requires the choice (built), HOME preselects by operator with a visible tick and a count. Recommended: yes.
- D21. NaN: its own count and explicit steps, or made to follow the rule for missing values. Recommended: its own count.
- D22. Formulas: confirm the allow-list as built, close FORMULA-SAFETY-1. Recommended: yes.
- D23. A time or size limit for formulas. No recommendation yet (no evidence of need).
