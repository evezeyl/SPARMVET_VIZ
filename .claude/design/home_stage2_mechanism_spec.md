# HOME audit: the mechanism and the build plan (stage 2)

> **HISTORICAL, see `.claude/design/home_audit_what_is_true_now.md` (2026-11-26).** This is a dated record. Where it speaks of plots as the scope of a step ("This plot only / All plots / All plots except", per-plot stacks, a propagation dialog), of "My view", of "the plot's table" or "plot data", or of an audit that is written only at T3, the page "what is true now" and the ledger lines D-0662 to D-0667 win; nothing below is edited.

**Status:** draft v0.2, 2026-11-15 15:05, for Eve's confirmation; nothing is built from the unconfirmed points. PROVISIONAL under Eve's rule of 2026-11-15 (this version changes no result and hides nothing). v0.1 was written on 2026-11-13 and never confirmed.
**Written for:** Eve, to read and confirm (part A alone is enough); then part B is the base of the tests-first work and of the build.
**Applies:** `spaces/HOME.md`, `home_audit_steps.md` (5a points 3-22, 9, 11, 19), ADR-099 (as read in its reading guide), ADR-100 to ADR-106, the hash model, to the code as read on 2026-11-15 (`feat/recipe-format-1` at `c5570336`).
**Tags:** **[DECIDED]** Eve decided it (source named); **[MINE]** my choice while writing, to confirm (part A, questions S2-1 to S2-5); **[CODE]** fixed by what the code does today (verified, file:line); **[RECIPE]** owned by the recipe format (`recipe_format_spec.md`).
**Words:** generic (entity, key, attribute, node); "table" for what the engine calls a collection; examples from the ST22 test recipe are marked. The old word "project" for the whole data analysis recipe is retired (ADR-091).

---

## Original recipe and audit recipe (confirmed by Eve, 2026-11-15)

1. HOME opens the original recipe. It is the reference. HOME never changes it.
2. Only Blueprint can edit a recipe.
3. When you audit, HOME works on a copy of the original recipe. This copy is the audit recipe.
4. The steps of the original recipe are in the copy. You cannot edit them or remove them.
5. In the audit you can only add steps: remove rows, or remove a column. Each step has a reason.
6. A step you added can be removed again. It leaves the audit recipe. The original recipe is not touched.
7. The export is the audit recipe: the original steps plus the audit steps that are still in it.
8. The original plot stays beside the audited plot, so you can see what the audit changed.

---

# Part A. For Eve (read this part alone)

## A1. What this is
1. This is the plan for **how** the HOME audit is built: 13 small packages, P0 to P12, in order.
2. Version 0.1 was never confirmed. Your decisions since then changed it.
3. Nothing here is new science. Only the questions in A4 need you.
4. Words: "tier 1" = tables as built from the raw files; "tier 2" = the table made for the plots; "tier 3" = the changes of one plot. The "audit copy" = a copy of the data analysis recipe holding your marked audit steps. The original never changes.

## A2. What is already built (checked 2026-11-15 by git and by reading the code)
| Package | What it delivers | State | Evidence (commit) |
|---|---|---|---|
| P0 | tests that tell the truth | partly | `19a45571`, `416a5056`, `18e5cda6` |
| P1 | filters that are correct | partly | `4b41b719`, `4674b604`, `46425c89`, `efcce204`. Left: the plot drops a column before it filters |
| P2 | recipe format and its checker | partly | `5a7ab37b`, `c827d335`, `eafc570c`. Left: the engine does not yet read a plot's tier-3 list |
| P3 | one model of the recipe (which table feeds which) | not built | issue #61 open |
| P4 | one stored-data key per table | not built | today one key for all tier-1 tables (`cache_keys.py:90-91`) |
| P5 | first thin version of the whole path, run without the screen | not built | |
| P6 | counts, checks, event log | not built | |
| P7 | view of the audit | not built | |
| P8 | changes of Exploration | not built | |
| P9 | audit screen | not built | |
| P10 | export and import | not built | |
| P11 | removal of the old audit | not built | |
| P12 | diagrams, documents | not built | |

**Count:** 0 built, 3 partly, 10 not built. Next: P3 and the tier-3 reader.

## A3. What your decisions changed in the plan
- **Missing values:** every filter step says `na: keep` or `na: remove` (ADR-103). The audit writes it in each step.
- **A filter value keeps the type of its column.** A wrong type is an error shown at that place, not converted silently (ADR-104 point 7). v0.1 said "converted".
- **A step that cannot run is an error, never skipped.** The plot follows the table (ADR-104 point 1).
- **Steps stay lists.** An audit step carries a label `id: audit_<8 characters>_<k>`, only in the audit copy (DEC18); the number `k` counts the order in which the steps were created in that audit (D-0321, 2026-11-20). **Decided 2026-11-20, not built (D-0329, D-0332):** in the audit recipe each tier keeps the author's `steps` and holds the audit steps in a second list `audit_steps`, each with its id and its reason in `audit_comment`; on `dev` (slice A) the marked steps sit at the end of `steps` with the reason in `comment`.
- **A table's published columns are its last tier-1 select step** (DEC23); a tier-1 audit step is written after it.
- **A table plotted directly has its own tier 2** (DEC16, built `eafc570c`). Every table has a tier 2 to write into.
- **Blueprint may write a plot's tier 3** (note at ADR-100). Audit steps go after them.

## A4. Your questions, in one list (answer by number)
A number from the agent channel is answered there once, not asked again.

**Decided, no question**
- The test library `hypothesis`: decided after you confirm this document (D15, 2026-11-15). Until then, plain tests with fixed cases.

**Confirmation, one line**
- The engine reads a plot's tier-3 list; a `filters` key in a plot specification is then refused. The recipe spec already says it (R1, DEC17). No shipped recipe uses that key, so no picture changes.

**Already numbered on the channel (answer there)**
- **N7 point 1:** keys are declared, never guessed. ADR-099 point 6 (`architecture_decisions.md:5105`) says yes; the old side is `home_audit_steps.md:257` and `tasks.md:74` ("inferred when absent").
- **N7 point 2:** the event log of the audit goes into the export (ADR-101 point 5, line 5242; ADR-105 point 6, line 5336). Plan: yes.
- **N7 point 4:** which samples a selection finds (28 across the tables or 21 at one table), and the caption count for plots without a key. Plan: each ticked table is filtered by your condition.
- **N13:** the name of the overview dialog. Plan: "recipe overview".
- **L18:** `column` or `columns` as the parameter name. Plan: `column`.

**New, to answer here** (default = what is built if you say yes)
- **S2-1.** DECIDED by Eve 2026-11-15 (built by PLOT-TABLE-ORDER-1; ADR-105 note of that date): steps run in the order they were recorded, in the table, the plot, the bundle and the exported recipe; a step whose column does not exist, or was removed by an earlier step, is an error that names the plot, the step, the column and the fix, never a skip; the filter dialog does not offer a column that an earlier step dropped. (This replaces the earlier default "filters are written before drops".) *For you:* the table, the plot and the re-run give the same rows, or the same plain error.
- **S2-2.** A value that cannot be typed at one ticked place (for example text for a number column): that line shows the error and cannot be ticked; the other places can be written. *For you:* nothing is converted silently; you see where a step cannot go.
- **S2-3.** The recipe or the data changes while an audit is open: the export is refused until you "re-base". Re-base writes your steps again into the new recipe and marks each: applied, not concerned, or broken. A broken step blocks the export. *For you:* nothing is exported from a mix of old and new.
- **S2-4.** Build order: the left-overs of P1, then P3 and P4, then P5; the screen last. *For you:* you can try the first audit in the app only after P5 and P7.
- **S2-5.** The first end-to-end proof (P5) also runs on the deliberately dirty copy of the ST22 data (missing values, repeated keys, a sample in one table only). *For you:* the proof is not limited to clean data.

**For information, not asked:** the technical layout of part B sections 1 and 2 (modules, place names, files). Nothing you see changes.

## A5. What waits for your confirmation
- The key tests (`tasks.md:34`), `hypothesis`, P4 and P5 start after you confirm this document.
- Where the overview dialog opens: settled with pictures at the screen step (P9).
- What happens when a bundle differs from its recorded hashes: confirmed when the export is built (P10).

---

# Part B. The mechanism (for the build)

## 0. Boundaries: who owns what
| Owner | What | Interface with this document |
|---|---|---|
| Recipe format | the format, `check_recipe`, the failure catalogue, the entity declaration, the T3 container, descriptions | this document **uses** them: the T3 container name, the origin marker of an audit step ~~(spec 6.6, OPEN)~~ (corrected 2026-11-15: section 6 of this document has no item 6.6; the marker was set by DEC18 on 2026-11-13), the recipe format version, `check_recipe` for the audit copy. **Now [DECIDED]:** T3 container `steps: {tier3: [...]}` on the plot entry (DEC17); marker `id: audit_<8 hex>_<k>`, only in profile `audit` (DEC18, `recipe_format_spec.md` 7.5; checked by ST08, `recipe_check.py:422-425`); `spec_version: 1` (DEC04); `check_recipe(raw, profile="audit")` for the copy (DEC03, DEC18; `recipe_check.py:50`) |
| This document | the recipe graph, node keys, the step compiler, the audit copy, the audit view, step-by-step counts, the guard-rail registry, the event log, export and import legs, the build order | |
| BLUEPRINT | builds recipes and plot specs; its navigator is rebuilt on the graph | the graph carries the file of each node (provenance); no change of Blueprint's screens. **Added 2026-11-15:** Blueprint may also write a plot's tier 3 (note at ADR-100); the audit copy keeps those steps and adds its own after them |
| Filters | NA rule (#63), integer threshold (#62), every content type (`FILTER-DTYPES-1`) | the compiler emits only the actions that these tasks make correct. **Now:** `na` required (ADR-103), integers (`46425c89`), typed values and every operator (ADR-104 points 4 and 7, `efcce204`); one condition `utils.filter_values.filter_condition` [CODE] |
| Plot library | the plot standard (ADR-106) | the audit view shows a plot error in the plot's place, as HOME does (`c442af4c`) |

## 1. Components (pure modules first; thin handlers on top) [MINE, W4; for information, A4]
| Module (place) | Role | Main functions | Depends on |
|---|---|---|---|
| `utils.recipe_graph` (`libs/utils`, Tier 1) [DECIDED: place, ADR-099 point 16(d)] | one model of the data analysis recipe: nodes, edges, steps in order, columns per node, plots, key families | `build_graph(raw, includes, schema_provider)`; `lineage_back(node)`; `lineage_forward(node)`; `nodes_with_column(name)`; `shared_columns(a, b)`; `plots_reading(node)`; `same_t1_definition(a, b)` | `utils.config_loader`; `utils.recipe_tiers` (the one reading of tier lists, `fe2a812e`); the one join-key rule (D7, JOIN-KEY-ONE-1); no other library |
| `utils.node_keys` (`libs/utils`) | series keys | `canonical_steps(steps)`; `part(label, obj)`; `series_key(parts)`; `is_prefix(a, b)`; `first_difference(a, b)` | stdlib, hashing |
| `utils.recipe_check` [RECIPE] | the one rule set | `check_recipe(raw, profile)` returns problems with a severity; ~~`profile` is `run` (HOME rejects) or `build` (BLUEPRINT reports)~~ (superseded 2026-11-13 by DEC18: four profiles). **Now [CODE]:** profiles `run`, `build`, `gallery`, `audit` (`recipe_check.py:50`), built `5a7ab37b` | graph (columns per node), later |
| `audit_compiler` (planned, not built; place `app/modules`) | one user step becomes recipe actions in the right lists | `compile_step(step, graph) -> [Insertion]`; `insert(original_raw, insertions) -> copy_raw` (deterministic) | graph, node_keys; replaces `t3_translator` for the audit (one source of truth, D7) |
| `audit_copy` (built in memory in `libs/utils/src/utils/audit_copy.py`, slice A; as a file not built, D-0319, D-0340) | the audit copy as a file | `write_copy`, `read_copy`, `marked_steps(copy)`, `strip_marked(copy)`, `integrity_errors(copy, original)` | recipe_check |
| `audit_counts` (planned, not built; place `app/modules`) | step-by-step counts | `flow(graph, frames, steps, entity)`: rows, entities, missing values removed, before and after each step | graph; frames injected; `utils.missing_values` (`4b41b719`) |
| `audit_guard_rails` (planned, not built; place `app/modules`) | the checks of `home_audit_steps.md` 19 | one entry per check: id, trigger, level, message, test | graph, counts |
| `audit_events` (planned, not built; place `app/modules`) | append-only event log | `append(event)`, `replay(log) -> steps` | none |
| `node_view` (planned, not built; place `app/modules`) | content of the node popup (pure) [DECIDED: pure content function, 5a point 7, O6] | `render_node(graph, node, steps, counts) -> html` | graph, counts |
| `audit_view` (planned, not built; place `app/modules`) | which recipe and orchestrator a panel reads | `view_recipe(mode)`, `view_orchestrator(mode)` and the reactive wiring | orchestrator |
| `app/modules/orchestrator.py`, `cache_keys.py` | stored nodes with keys | keys per table with precise parts, T3, a second instance on the copy (own cache folder); the engine reader of `steps.tier3` (recipe spec 7.7 leaves its name and place to P5) | node_keys |
Handlers (`home_theater.py` and others) only wire these; they hold no rule.

## 2. Data structures
- **Node id** [MINE, for information, A4]: `DS:<dataset>`, `T1:<table>`, `T2:<table>`, `T3:<plot>`; a node's `columns` come from the stored schema (parquet metadata) or a dry run on the column names, never from computing the data [CODE: Polars `collect_schema`]. A T1 node's columns are those of its last tier-1 `polars_select` (DEC23).
- **User step** [DECIDED, 5a-1..3]: `{id, kind: filter|drop, field, op, value | values, nodes: [node id], reason, initials, created_at}`. ~~The value is converted to each node's column type (`FILTER-DTYPES-1`).~~ (superseded 2026-11-14 by ADR-104 point 7: the value is stored in the column's type, never converted silently; a wrong type is a plain error.) **Now [DECIDED]:** a filter step also carries `na: keep|remove` (ADR-103 points 2 and 8) and, for `between`, `closed` (ADR-104 point 4); the value is typed per node from the schema of the table at that node (ADR-104 point 7); a node where it cannot be typed is shown with the error and cannot be ticked [MINE, S2-2].
- **Audit copy** [DECIDED, 5a-22]: the resolved single-file recipe (all `!include` merged, `plots` mirror removed, as `build_mode2_recipe` does today, `t3_translator.py:212` [CODE]) in the session folder `_sessions/<session key>/audit/<recipe id>.yaml` (path [MINE, for information, A4]; the audit folder inside the session's folder, in the user's directory of the deployment, is DECIDED 2026-11-20, D-0319, D-0340; the exact file name is not decided; not built); header: the original's file-set hash and the recipe format version (`spec_version`, DEC04); ~~each audit step carries the origin marker [RECIPE: name and shape to set]~~ (superseded 2026-11-13 by DEC18). **Now [DECIDED, DEC18]:** each audit step carries `id: audit_<8 hex>_<k>`; the copy passes `check_recipe` in profile `audit`; **invariant: the copy minus its marked steps equals the original; any difference blocks** (5a-22; AUDIT-VIEW-1, 2026-11-13).
- **Insertion**: the end of a table's tier-1 list (T1), tier-2 list (T2) or the plot's T3 list; the action is a named, parameterised action, never formula text from user values [DECIDED, 5a-14]. **Now [DECIDED]:** a filter is `modif_filter` (`column`, `op`, `value`, `na`; DEC39), a drop is `polars_drop` (DEC37). T1: after the table's last step, so after its `polars_select` (DEC23). T2: a join's `steps.tier2`, or the `wrangling.tier2` of a table plotted directly (DEC16, built `eafc570c`). T3: the plot entry's `steps.tier3`, after the steps the maker wrote there (DEC17; note at ADR-100, 2026-11-15). At one place the steps run in the recorded order, a step that cannot run is an error [DECIDED 2026-11-15, S2-1; was: filters before drops, MINE].
- **Series key** [DECIDED, ADR-101]: labelled parts in execution order, `E . rC . dC . [a1] . [s2] . [a2] . [s3] . [a3]`, 128 bits per part, an empty part omitted; the parts `a` come from the operations of the marked steps only (the `id` and `comment` of a step are not hashed, recipe spec 7.5). T1 per table with precise parts from the graph; a table whose inputs cannot be listed safely keeps a coarse part (fail-safe). **Today [CODE]:** one T1 key for the whole recipe (`cache_keys.py:90-91`): P4 changes it.
- **Event** [MINE, for information, A4]: `{ts, initials, type: created|removed|reverted|ack_warning, step id, payload}`; replaying the log gives the copy's marked steps (a test). Exported (ADR-101 point 5, line 5242; ADR-105 point 6, line 5336; N7 point 2).

## 3. Algorithms
1. **Candidate nodes for a field** [DECIDED, ADR-105 point 2]: `graph.nodes_with_column(field)` along the open plot's lineage and, for the whole recipe, every node; ticks default to all; suggestions from `shared_columns` (the join key families, from the one join-key rule, D7); the key is information (counts, the warning on a join key), not mechanism (ADR-105 point 3).
2. **Compile**: for each ticked node, one insertion; ~~the filter value converted to the node's type~~ (superseded 2026-11-14 by ADR-104 point 7: typed from the node's schema, a wrong type is an error); drop uses the same logic (`home_audit_steps.md` 9). A filter on a column that an earlier audit step dropped at that place is refused at recording (PLOT-TABLE-ORDER-1, Eve 2026-11-14).
3. **Trial = Apply** ~~[DECIDED, D2]~~ (corrected 2026-11-15: the tag "D2" of v0.1 points to no traceable record; the rule is ADR-105 point 4, one candidate step previewed in a dialog, Apply with a reason adopts it, Cancel changes nothing) [DECIDED, ADR-105 point 4]: the dialog compiles the candidate into a temporary copy, runs the affected nodes through the audit orchestrator, shows counts before and after and a preview of the open plot, and discards it; Apply persists the same copy, so the nodes are reused by key and nothing is computed twice (the reuse is [MINE, for information, A4]).
4. **Step-by-step counts** [DECIDED, SC2 2026-11-12; 5a points 17, 18]: start at the population table (`entity.population`, else the distinct keys of the first node that has the key); each step is applied to the result of the steps before it, with a probe (rows, entities by key, missing values in the filtered column among the removed rows, counted on the table the filter acts on, ADR-103 point 10); derived, never stored; the report snapshot is recomputed by the import. The join counts of JOIN-COUNTS-1 (PROVISIONAL, channel L32) are read here when they exist.
5. **Checks after Apply** [DECIDED, 5a-12]: the same condition is evaluated again on every node that has the field and the result is shown.
6. **Re-base** [MINE, S2-3]: if the original or the data changes while audit is open, the copy's origin hash no longer matches; the export is refused; "re-base" writes the marked steps into the new original at the same nodes and gives each step a status (applied, not concerned, broken).
7. **View** [DECIDED, 5a-22]: Exploration reads the original recipe and orchestrator; audit mode reads the copy and the second orchestrator; Compare reads both. `active_cfg` (about 35 uses) and `orchestrator.` (about 12) are replaced by the view pair; a test checks that in audit mode no handler reads the original [CODE counts, 2026-11-13]. **Recount 2026-11-15 [CODE]:** 34 lines with `active_cfg` and 14 with `orchestrator.` in the HOME handlers (Blueprint left out). A plot that cannot be drawn shows its error in its place (ADR-106 V7, `c442af4c`).

## 4. Export and import legs [DECIDED, hash model ADR-101; ADR-097]
Recorded in `effective_run.yaml`: engine, data (with per-file hashes), recipe (file set), audit recipe, steps (operations), record (with reasons; and the event log, ADR-101 point 5, `architecture_decisions.md:5242`; ADR-105 point 6, line 5336; N7 point 2), the series key of every exported node (original and audit), the format versions, the file hashes and the content hashes of the exported frames. **Added from later decisions:** `na` and `closed` of every filter step (ADR-103, ADR-104 point 4; exported since `4674b604`); the seed of every random layer, the recipe's or 0 (ADR-104 point 3, SEED-HOLDS-1 being built); the plot engine and its version (ADR-106 V8). Import: an invalid recipe or an unknown format version blocks with the reason; each leg is match, mismatch or not checked; a bundle that differs from its own recorded hashes needs an acknowledgment (to confirm at build, A5). The import writes a new recipe and session only.

## 5. Build plan: small revertible packages, tests first (`TEST-ADAPT-1`)
Each package: tests that fail for the right reason on today's code first; one commit per package; the headless baseline stays green; no package leaves a half fix. State and evidence: A2.
| # | Package | Delivers value alone? | Tests (examples) | Depends on | State 2026-11-15 | What is left |
|---|---|---|---|---|---|---|
| P0 | inventory and adaptation of the tests that encode superseded behaviour (`TEST-ADAPT-1`); the order tests (`TEST-ORDER-1`); the shape tests (`TEST-SHAPES-1`) | yes: a truthful test suite | the canaries (`QA_population_zscore`, `QA_aggregated_no_key`, `QA_ST_with_NA`, `QA_year_types`) | none | PARTLY | TEST-SHAPES-1 (with P3); a decision per strict xfail (TEST-ADAPT-1); the N14 tests after confirmation |
| P1 | filters correct: NA rule (#63), integers (#62), every content type (`FILTER-DTYPES-1`), one implementation for preview, audit and VizFactory ~~(NA rule as "missing is a value")~~ (superseded 2026-11-14 by ADR-103: `na: keep|remove`, the engine follows Polars) | yes | per type and operator, including missing values; engine = VizFactory = compiler output | P0 | PARTLY | PLOT-TABLE-ORDER-1 (the plot follows the table; recording guard; check at export); FILTER-PICKERS-1 (Date, Boolean, Time, Duration); FILTER-UNIFY-1 (the code around the shared condition, three places) |
| P2 | recipe format and `check_recipe`, fail instead of warn, a dataset's tier-2 applied, the engine keys; **containers in the form of ADR-041 (a dictionary for keyed definitions, a list for ordered ones, flat fragments), refused with a message that shows the corrected text, in the app and in the tests** (recipe spec 4c; added 2026-11-13 at Eve's request) [RECIPE] | yes | one test per failure; every shipped recipe passes or is corrected | the recipe session | PARTLY | the loader's repair of an unquoted `on` (ADR-100 point 3); the open format points (`column`/`columns`, L18; the `Categorical` list, CATEGORICAL-LIST-1); the tier-3 reader moves to P5 (recipe spec 7.7) |
| P3 | `utils.recipe_graph` with columns per node; Blueprint's navigator rebuilt on it (`RECIPE-GRAPH-UTILS-1`); the graph builder relies on the container forms (ADR-041) and reports a wrong form with the checker's message, never guesses; it also feeds check J08 (a column name in both ingredients of a join that is not a join key is renamed `_right` silently) | yes: `extract_primary_keys` fixed (#61), lineage for Blueprint | graph on every recipe shape; navigator tests are the regression oracle | P2 (the parts it needs are built); JOIN-KEY-ONE-1 (D7) | NOT BUILT | all; J08 is today checked from the declared fields only (`recipe_check.py:722-731`) |
| P4 | node keys (`KEYS-NODE-1`): `utils.node_keys`, T1 per table, T3, retire `decision_hash` | yes: less rebuilding, exact identity | the invariants of the hash model (property tests; tool per the R1 confirmation in A40) | P3; confirmation (A5) | NOT BUILT | all |
| P5 | **walking skeleton**: one filter at T1 of one table through the whole path, headless: compile, copy, integrity, second orchestrator, keys, counts, export legs, import; **added 2026-11-15:** the engine reader of `steps.tier3` (the R1 confirmation in A4) | the proof of the design | concordance: the exported copy run from the raw data equals the displayed audit data; copy minus marked steps equals the original; also on the dirty ST22 copy (S2-5) | P1, P3, P4; the R1 confirmation in A4 | NOT BUILT | all |
| P6 | counts, guard-rail registry, event log | | counts on the canaries; replay equals the copy | P5 | NOT BUILT | all |
| P7 | audit view wiring (view recipe and orchestrator), Compare | | no handler reads the original in audit mode | P5 | NOT BUILT | all |
| P8 | Exploration changes (selector Source/T1/T2/T3, filters per node, clear on change, notices); can start after P1 and P3 | yes | `home_preview_filters.md` tests | P1, P3 | NOT BUILT | HOME-EXPLORE-4 to -6; exploration no longer changes the plot (ADR-105 point 1) |
| P9 | audit screen: dialog with ticks, right panel, node popup (own window), ~~project overview~~ the overview dialog (name to be confirmed: N13) (word corrected 2026-11-15, ADR-091) | | browser tests, think-aloud on the ST22 recipe | P6, P7 | NOT BUILT | all; where the overview opens and the right panel details (A5) |
| P10 | export and import with the legs, the exclusion table, the attrition table, the caption; sessions and re-base | | bundle round trip | P5, P6; SEED-HOLDS-1 | NOT BUILT | all |
| P11 | removal of the old model (`AUDIT-REPLACE-1`, `AUDIT-RAWYAML-REMOVE-1`) | | the old tests removed with their code | P9 | NOT BUILT | all |
| P12 | UML redraw, docs, glossary, help; configuration stage (`CONFIG-REVIEW-1`) and gating tests | | `audit_uml_model.py`, the configuration tests | all | NOT BUILT | all |

~~**First milestone (M1)** is P5: before the screen is touched, the whole path works headless on the real recipes. P1, P2, P3 and P8 can start before M1; P0 comes first.~~ (superseded 2026-11-15: P0, P1 and P2 are partly built; the order below starts from today's code.)
**First milestone (M1) is still P5** [MINE, S2-4]. **Order from today:**
1. P1 leftovers: PLOT-TABLE-ORDER-1 (decided 2026-11-14), then FILTER-PICKERS-1 (screen only, in parallel).
2. P3, the graph, with TEST-SHAPES-1 written first; it uses the one join-key rule (JOIN-KEY-ONE-1, D7), so that comes just before or with it.
3. P4, the keys, after your confirmation of this document (the N14 tests and D15 wait for it).
4. P5, the walking skeleton, with the tier-3 reader (the R1 confirmation in A4) and the concordance on the dirty data (S2-5).
5. P6 and P7 in parallel; P8 can run beside P4 to P7 once P3 is in.
6. P9, then P10 (needs SEED-HOLDS-1 merged), then P11, then P12.

## 6. Risks and points that need an answer
1. Set (Eve 2026-11-13): marker `id: audit_<8 hex>_<k>` (DEC18), `spec_version: 1` (DEC04), T3 container `steps: {tier3: [...]}` on the plot entry (DEC17; written `tier3: {steps: [...]}` since the amendment of 2026-11-17, D-0250). **Built in the checker** (`libs/utils/src/utils/recipe_check.py`: the audit marker is `_AUDIT_ID` at `:61`; the ST08 check is at `:654-656`; verified on this branch). The example in `recipe_format_spec.md` 7.5 shows `id: audit_7f3a`, which ST08 would refuse: the example needs the full form (for the recipe session).
2. About 35 call sites move to the view pair (P7): the test that no handler reads the original is the safety. (Recount 2026-11-15: 34 and 14 lines, section 3 point 7.)
3. ~~A value converted per node can fail on a node (a number as text): a warning with the node named; `QA_year_types` is the fixture.~~ (superseded 2026-11-14 by ADR-104 point 7: no conversion; a value of another type is a plain error.) **Now:** a value that cannot be typed at a ticked node is shown as an error on that line (S2-2); `QA_year_types` stays the fixture.
4. A step with a very long list of values: the record and the key are fine; the dialog shows a summary.
5. Precise per-table keys must never miss an input: the property test (changing any input changes the key) is the gate; otherwise the coarse part stays.
6. ~~P2 and P3 are on the critical path of M1; if the recipe session is late, P1 and P8 deliver value meanwhile.~~ (superseded 2026-11-15: P2 is mostly built.) **Now:** P3 and the tier-3 reader are on the critical path of M1; P1 leftovers and P8 deliver value meanwhile.
7. **Decided (DEC18, `recipe_format_spec.md:385`): steps stay lists.** (The rest of this point is HISTORICAL, superseded 2026-11-13 by DEC18; kept for the reasons it records. The safeguards for the keyed containers `analysis_groups` and `plots` are in RECIPE-ORDER-IDS-1: repeated keys refused, built in `utils/strict_yaml.py`; writers keep the key order.) The facts below apply only to the keyed containers `analysis_groups` and `plots`. This spec assumes ordered lists in three places (insertion at the end, the hash of the steps, the copy-minus-marked-steps invariant). Three facts, verified on 2026-11-13, that a dictionary form must handle: (a) a duplicate key in YAML silently keeps the **last** one, so a duplicated step name drops the first step without any message: the loader must refuse duplicate keys; (b) `canonical_hash` sorts dictionary keys, so two orders of a dictionary of steps give the **same** key: the steps must be converted to an ordered list (file order) before hashing and before the engine runs them, in one place (the loader or the graph), never at the call sites; (c) `yaml.dump` sorts keys by default and several writers do not pass `sort_keys=False` (`exporter.py` twice, `blueprint_handlers.py`, `wrangle_studio.py`, to check call by call): a writer that sorts would reorder the steps silently; a test must scan the writers, or the order must come from an explicit field instead of the mapping order. A dictionary also helps: the step name is a stable id (for the origin marker, the integrity check by key, the removal), and a comment can sit on a step. Decision for the recipe session; this spec then adapts: the insertion adds a key at the end, the marker can be the key's prefix, the invariant compares by key. **My recommendation (2026-11-13): ordered steps stay lists; things that have a name stay dictionaries (data schemas, joins, plots, groups, fields); a step that needs a stable id carries an optional `id` field inside its list item.** That removes (a) to (c) for steps and keeps the ids and comments; where the order of a dictionary matters (tab order, column order of `input_fields`), the recipe session decides whether the order is part of the key.
8. **New 2026-11-15:** HOME's load gate runs once at start (GATE-GAP-1, a defect being fixed). The audit copy must not rely on it: its integrity is checked each time it is read (load, Apply, export, import; 5a-22).
9. **New 2026-11-15:** three places still wrap the shared filter condition (FILTER-UNIFY-1). The audit view must run the copy through the engine, not a fourth filter path, or the table, the plot and the re-run can drift again (the lesson of PLOT-TABLE-ORDER-1).
10. **New 2026-11-15:** a T1 audit step comes after the table's `polars_select` (DEC23), and a step is written only at T1, T2 or T3 (5a point 4). So a field that a table does not publish at T1 cannot be filtered at that table. [MINE, for information, A4] The dialog says so and names the tables that publish the field; nothing is inserted before the maker's `polars_select`.
