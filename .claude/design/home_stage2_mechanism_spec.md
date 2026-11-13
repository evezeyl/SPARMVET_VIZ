# HOME audit: the mechanism and the build plan (stage 2, draft v0.1, 2026-11-13)

**Written for:** Eve, to read and confirm; after that it is the base of the tests-first work and of the build.
**Status:** DRAFT. Nothing is built from it. It applies the decisions of `spaces/HOME.md`, `home_audit_steps.md` (5a points 3-22, 9, 11, 19), ADR-099 and the hash model to the code as read on 2026-11-12/13.
**Tags:** **[DECIDED]** you decided it; **[MINE]** my choice while writing, to confirm; **[CODE]** fixed by what the code does today (verified); **[RECIPE]** owned by the recipe session (`recipe_format_spec.md`, tasks RECIPE-SPEC-1, RECIPE-TESTS-1).
**Words:** generic (entity, key, attribute, node); examples from the ST22 test recipe are marked.

## 0. Boundaries: who owns what
| Owner | What | Interface with this document |
|---|---|---|
| Recipe session | the recipe format, `check_recipe`, the failure catalogue, the engine keys, the entity declaration, the T3 container, descriptions | this document **uses** them: the T3 container name, the origin marker of an audit step (spec 6.6, OPEN), the recipe format version, `check_recipe` for the audit copy |
| This document | the recipe graph, node keys, the step compiler, the audit copy, the audit view, step-by-step counts, the guard-rail registry, the event log, export and import legs, the build order | |
| BLUEPRINT | builds recipes and plot specs; its navigator is rebuilt on the graph | the graph carries the file of each node (provenance); no change of Blueprint's screens |
| Filters | NA rule (#63), integer threshold (#62), every content type (`FILTER-DTYPES-1`) | the compiler emits only the actions that these tasks make correct |

## 1. Components (pure modules first; thin handlers on top) [MINE, W4]
| Module (place) | Role | Main functions | Depends on |
|---|---|---|---|
| `utils.recipe_graph` (`libs/utils`, Tier 1) | one model of the recipe: nodes, edges, steps in order, columns per node, plots, key families | `build_graph(raw, includes, schema_provider)`; `lineage_back(node)`; `lineage_forward(node)`; `nodes_with_column(name)`; `shared_columns(a, b)`; `plots_reading(node)`; `same_t1_definition(a, b)` | `utils.config_loader`; no other library |
| `utils.node_keys` (`libs/utils`) | series keys | `canonical_steps(steps)`; `part(label, obj)`; `series_key(parts)`; `is_prefix(a, b)`; `first_difference(a, b)` | stdlib, hashing |
| `utils.recipe_check` [RECIPE] | the one rule set | `check_recipe(raw, profile)` returns problems with a severity; `profile` is `run` (HOME rejects) or `build` (BLUEPRINT reports) | graph (columns per node) |
| `app/modules/audit_compiler.py` | one user step becomes recipe actions in the right lists | `compile_step(step, graph) -> [Insertion]`; `insert(original_raw, insertions) -> copy_raw` (deterministic) | graph, node_keys |
| `app/modules/audit_copy.py` | the audit copy as a file | `write_copy`, `read_copy`, `marked_steps(copy)`, `strip_marked(copy)`, `integrity_errors(copy, original)` | recipe_check |
| `app/modules/audit_counts.py` | step-by-step counts | `flow(graph, frames, steps, entity)`: rows, entities, missing values removed, before and after each step | graph; frames injected |
| `app/modules/audit_guard_rails.py` | the checks of `home_audit_steps.md` 19 | one entry per check: id, trigger, level, message, test | graph, counts |
| `app/modules/audit_events.py` | append-only event log | `append(event)`, `replay(log) -> steps` | none |
| `app/modules/node_view.py` | content of the node popup (pure) | `render_node(graph, node, steps, counts) -> html` | graph, counts |
| `app/modules/audit_view.py` | which recipe and orchestrator a panel reads | `view_recipe(mode)`, `view_orchestrator(mode)` and the reactive wiring | orchestrator |
| `app/modules/orchestrator.py`, `cache_keys.py` | stored nodes with keys | keys per collection with precise parts, T3, a second instance on the copy (own cache folder) | node_keys |
Handlers (`home_theater.py` and others) only wire these; they hold no rule.

## 2. Data structures
- **Node id** [MINE]: `DS:<dataset>`, `T1:<collection>`, `T2:<collection>`, `T3:<plot>`; a node's `columns` come from the stored schema (parquet metadata) or a dry run on the column names, never from computing the data [CODE: Polars `collect_schema`].
- **User step** [DECIDED, 5a-1..3]: `{id, kind: filter|drop, field, op, value | values, nodes: [node id], reason, initials, created_at}`. The value is converted to each node's column type (`FILTER-DTYPES-1`).
- **Audit copy** [DECIDED, 5a-22]: the resolved single-file recipe (all `!include` merged, `plots` mirror removed, as `build_mode2_recipe` does today) in the session folder `_sessions/<session key>/audit/<recipe id>.yaml`; header: the original's file-set hash and the recipe format version; each audit step carries the origin marker [RECIPE: name and shape to set]; **invariant: the copy minus its marked steps equals the original; any difference blocks**.
- **Insertion**: the end of a table's tier-1 list (T1), tier-2 list (T2) or the plot's T3 list; the action is a named, parameterised action, never formula text from user values [DECIDED, 5a-14].
- **Series key** [DECIDED]: labelled parts in execution order, `E . rC . dC . [a1] . [s2] . [a2] . [s3] . [a3]`, 128 bits per part, an empty part omitted; the parts `a` come from the operations of the marked steps only. T1 per collection with precise parts from the graph; a collection whose inputs cannot be listed safely keeps a coarse part (fail-safe).
- **Event** [MINE]: `{ts, initials, type: created|removed|reverted|ack_warning, step id, payload}`; replaying the log gives the copy's marked steps (a test).

## 3. Algorithms
1. **Candidate nodes for a field** [DECIDED]: `graph.nodes_with_column(field)` along the open plot's lineage and, for the whole recipe, every node; ticks default to all; suggestions from `shared_columns` (the join key families); the key is information (counts, the warning on a join key), not mechanism.
2. **Compile**: for each ticked node, one insertion; the filter value converted to the node's type; drop uses the same logic (`home_audit_steps.md` 9).
3. **Trial = Apply** [DECIDED, D2]: the dialog compiles the candidate into a temporary copy, runs the affected nodes through the audit orchestrator, shows counts before and after and a preview of the open plot, and discards it; Apply persists the same copy, so the nodes are reused by key and nothing is computed twice.
4. **Step-by-step counts** [DECIDED]: start at the population table (`entity.population`, else the distinct keys of the first node that has the key); each step is applied to the result of the steps before it, with a probe (rows, entities by key, missing values in the filtered column among the removed rows); derived, never stored; the report snapshot is recomputed by the import.
5. **Checks after Apply** [DECIDED, 5a-12]: the same condition is evaluated again on every node that has the field and the result is shown.
6. **Re-base** [MINE]: if the original or the data changes while audit is open, the copy's origin hash no longer matches; the export is refused; "re-base" writes the marked steps into the new original at the same nodes and gives each step a status (applied, not concerned, broken).
7. **View** [DECIDED]: Exploration reads the original recipe and orchestrator; audit mode reads the copy and the second orchestrator; Compare reads both. `active_cfg` (about 35 uses) and `orchestrator.` (about 12) are replaced by the view pair; a test checks that in audit mode no handler reads the original [CODE counts, 2026-11-13].

## 4. Export and import legs [DECIDED, hash model]
Recorded in `effective_run.yaml`: engine, data (with per-file hashes), recipe (file set), audit recipe, steps (operations), record (with reasons), the series key of every exported node (original and audit), the format versions, the file hashes and the content hashes of the exported frames. Import: an invalid recipe or an unknown format version blocks with the reason; each leg is match, mismatch or not checked; a bundle that differs from its own recorded hashes needs an acknowledgment (to confirm at build). The import writes a new recipe and session only.

## 5. Build plan: small revertible packages, tests first (`TEST-ADAPT-1`)
Each package: tests that fail for the right reason on today's code first; one commit per package; the headless baseline stays green; no package leaves a half fix.
| # | Package | Delivers value alone? | Tests (examples) | Depends on |
|---|---|---|---|---|
| P0 | inventory and adaptation of the tests that encode superseded behaviour (`TEST-ADAPT-1`); the order tests (`TEST-ORDER-1`); the shape tests (`TEST-SHAPES-1`) | yes: a truthful test suite | the canaries (`QA_population_zscore`, `QA_aggregated_no_key`, `QA_ST_with_NA`, `QA_year_types`) | none |
| P1 | filters correct: NA rule (#63), integers (#62), every content type (`FILTER-DTYPES-1`), one implementation for preview, audit and VizFactory | yes | per type and operator, including missing values; engine = VizFactory = compiler output | P0 |
| P2 | recipe format and `check_recipe`, fail instead of warn, a dataset's tier-2 applied, the engine keys; **containers in the form of ADR-041 (a dictionary for keyed definitions, a list for ordered ones, flat fragments), refused with a message that shows the corrected text, in the app and in the tests** (recipe spec 4c; added 2026-11-13 at Eve's request) [RECIPE] | yes | one test per failure; every shipped recipe passes or is corrected | the recipe session |
| P3 | `utils.recipe_graph` with columns per node; Blueprint's navigator rebuilt on it (`RECIPE-GRAPH-UTILS-1`); the graph builder relies on the container forms (ADR-041) and reports a wrong form with the checker's message, never guesses; it also feeds check J08 (a column name in both ingredients of a join that is not a join key is renamed `_right` silently) | yes: `extract_primary_keys` fixed (#61), lineage for Blueprint | graph on every recipe shape; navigator tests are the regression oracle | P2 |
| P4 | node keys (`KEYS-NODE-1`): `utils.node_keys`, T1 per collection, T3, retire `decision_hash` | yes: less rebuilding, exact identity | the invariants of the hash model | P3 |
| P5 | **walking skeleton**: one filter at T1 of one table through the whole path, headless: compile, copy, integrity, second orchestrator, keys, counts, export legs, import | the proof of the design | concordance: the exported copy run from the raw data equals the displayed audit data; copy minus marked steps equals the original | P1, P3, P4 |
| P6 | counts, guard-rail registry, event log | | counts on the canaries; replay equals the copy | P5 |
| P7 | audit view wiring (view recipe and orchestrator), Compare | | no handler reads the original in audit mode | P5 |
| P8 | Exploration changes (selector Source/T1/T2/T3, filters per node, clear on change, notices); can start after P1 and P3 | yes | `home_preview_filters.md` tests | P1, P3 |
| P9 | audit screen: dialog with ticks, right panel, node popup (own window), project overview | | browser tests, think-aloud on the ST22 recipe | P6, P7 |
| P10 | export and import with the legs, the exclusion table, the attrition table, the caption; sessions and re-base | | bundle round trip | P5, P6 |
| P11 | removal of the old model (`AUDIT-REPLACE-1`, `AUDIT-RAWYAML-REMOVE-1`) | | the old tests removed with their code | P9 |
| P12 | UML redraw, docs, glossary, help; configuration stage (`CONFIG-REVIEW-1`) and gating tests | | `audit_uml_model.py`, the configuration tests | all |
**First milestone (M1)** is P5: before the screen is touched, the whole path works headless on the real recipes. P1, P2, P3 and P8 can start before M1; P0 comes first.

## 6. Risks and points that need an answer
1. The origin marker name, the format version and the T3 container name are set by the recipe session; the compiler and the copy wait for them (P5).
2. About 35 call sites move to the view pair (P7): the test that no handler reads the original is the safety.
3. A value converted per node can fail on a node (a number as text): a warning with the node named; `QA_year_types` is the fixture.
4. A step with a very long list of values: the record and the key are fine; the dialog shows a summary.
5. Precise per-collection keys must never miss an input: the property test (changing any input changes the key) is the gate; otherwise the coarse part stays.
6. P2 and P3 are on the critical path of M1; if the recipe session is late, P1 and P8 deliver value meanwhile.
7. **If the recipe's steps are dictionaries (Eve 2026-11-13, the recipe session investigates).** This spec assumes ordered lists in three places (insertion at the end, the hash of the steps, the copy-minus-marked-steps invariant). Three facts, verified on 2026-11-13, that a dictionary form must handle: (a) a duplicate key in YAML silently keeps the **last** one, so a duplicated step name drops the first step without any message: the loader must refuse duplicate keys; (b) `canonical_hash` sorts dictionary keys, so two orders of a dictionary of steps give the **same** key: the steps must be converted to an ordered list (file order) before hashing and before the engine runs them, in one place (the loader or the graph), never at the call sites; (c) `yaml.dump` sorts keys by default and several writers do not pass `sort_keys=False` (`exporter.py` twice, `blueprint_handlers.py`, `wrangle_studio.py`, to check call by call): a writer that sorts would reorder the steps silently; a test must scan the writers, or the order must come from an explicit field instead of the mapping order. A dictionary also helps: the step name is a stable id (for the origin marker, the integrity check by key, the removal), and a comment can sit on a step. Decision for the recipe session; this spec then adapts: the insertion adds a key at the end, the marker can be the key's prefix, the invariant compares by key. **My recommendation (2026-11-13): ordered steps stay lists; things that have a name stay dictionaries (data schemas, joins, plots, groups, fields); a step that needs a stable id carries an optional `id` field inside its list item.** That removes (a) to (c) for steps and keeps the ids and comments; where the order of a dictionary matters (tab order, column order of `input_fields`), the recipe session decides whether the order is part of the key.
