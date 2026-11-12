# The hash model: what exists, what each hash answers, what the redesign needs (2026-11-12)

**Status: inventory VERIFIED (code read and run); the model in section 4 is MINE, awaiting Eve (CONFIRM).** Eve asked: a hash per node (T1, T2, T3) to see changes (audit), a hash of the whole recipe for recomputation in every deployment mode; verify how the series of hashes (a chain of content-addressed keys) works for stored data, sessions and exports, and whether a UML must change.

## 1. What exists today (verified: `cache_keys.py`, `session_manager.py`, `orchestrator.py`, `export_handlers.py`, `bundle_importer.py`, `docs/foundations/reproducibility_hash_schema.qmd`, ADR-089, ADR-097)
| Hash | Covers | Computed by | Used for | Stored or exported |
|---|---|---|---|---|
| `data_analysis_recipe_sha256` | the recipe **file set** (entry file and every include, each sha256, sorted by relative path, hashed again) | `cache_keys.data_analysis_recipe_fileset_hash` | identity of the recipe: session key, export key check, import leg "recipe"; checkable with `sha256sum` | export README, report, effective_run, image metadata |
| `data_batch_hash` | content of all source data files (`dataset_id:sha256`, sorted) | `SessionManager.compute_data_batch_hash` (reads every file once per session) | identity of the data: session key, input of the T1 key, import leg "data" | same |
| `engine_fingerprint` | engine cache version + Polars + transformer versions (export adds git commit, image ref, `uv.lock` hash) | `cache_keys.engine_fingerprint` | input of the T1 key; import leg "engine" | effective_run |
| `material_hash` | the resolved recipe without the downstream-only parts (`info`, `analysis_groups`, `plot_defaults`, `plots`, the joins' tier2) | `cache_keys.tier1_material` | input of the T1 key only | not exported |
| `tier1_key` | `hash(engine, material_hash, data_batch_hash)`: **one key for the whole recipe** (verified: three collections, three different tables, the same stored key) | `cache_keys.tier1_key` | is a stored T1 still valid; read check in `materialize_tier1` | parquet metadata `sparmvet_tier1_key`; export `stage_keys`, image metadata |
| `tier2_key` | `hash(tier1_key, that join's tier2 steps)`, per join; none when tier2 is empty | `cache_keys.tier2_key` | is a stored T2 still valid | parquet metadata `sparmvet_tier2_key`; export |
| `session_key` | `recipe_sha256[:12]:data_batch_hash[:12]` | `SessionManager.compute_session_key` | names the session folder (identity of the working state) | folder name, session files |
| `t3_audit_steps_sha256` | canonical hash of the per-plot audit steps (and style overrides) | `export_handlers` | import leg "steps" (a snapshot at export) | effective_run |
| `decision_hash` (older) | the step list of an explicit `sink_parquet` step, with a different serializer | `utils.hashing.generate_config_hash`, `data_assembler` | short-circuit of the older assembler path | parquet metadata `sparmvet_decision_hash` |
| plot input key | `hash(tier2_key, plot spec, plot_defaults, palette)`, "not stored" | **not found in the code** | documented in ADR-089 only | none |
**Facts about the hashing itself (verified):** SHA-256, 64 hex characters, lists keep their order, dictionary keys are sorted, the stored key is checked on every read; stale files are recomputed.

## 2. The questions the hashes must answer (the roles differ)
| Question | Hash family | Who asks it |
|---|---|---|
| Is this stored node still valid, can I reuse it? | **node keys** (chain) | the orchestrator, in every deployment mode, at every read |
| Is this the same recipe, the same data, the same engine as before or as in that bundle? | **identity hashes** (file set, data batch, engine; later the audit recipe and the steps) | sessions, the export key check, the import verification, a reader with `sha256sum` |
| Did this audit step list produce this result? | **steps hash** (operations) and **audit recipe hash** | export and import |
| Is the content of this node different from the original (the plot is affected; the attrition snapshot is true)? | **content hash** of the frame (new) | the dialog, the export, the import |
Eve's reading ("node hashes see changes, whole-recipe hashes decide recomputation in every mode") is close; the exact split today is different: **recomputation is decided by node keys only**, and the whole-recipe identity hashes never decide it. What blurs this today is that the T1 key embeds the whole recipe, so a change anywhere rebuilds every T1 (safe, coarse).

## 3. Gaps against the redesign
1. T1 key is recipe-wide (verified): it cannot say which table changed, and equal keys do not identify the data across collections.
2. There is no key for T3 (user steps are applied "on top, never stored"), and none for audit nodes.
3. No content hash: "affected" and the attrition snapshot cannot be verified.
4. The steps leg is per-plot audit nodes of the old model; the audit needs the ordered step list and the audit recipe.
5. Two mechanisms (`decision_hash` and the keys); the plot input key is documented and not built.
6. The documents (`reproducibility_hash_schema.qmd`, ADR-089, the diagrams) describe the three-hash, T1/T2 model.

## 4. Proposed model, designed from the needs and not from the code (MINE; drawn in UML `DM-KEYS` and its details)
**Where the time goes.** Only reading files costs time: the data files (once per session) and the recipe files (small). Everything else hashes a few short strings. So the model must not multiply hashes of files, and it should not hash a hash again when a concatenation is enough.
**Leaves (read from disk, once, kept in a table in memory):** `d(file)` for every source data file, `r(file)` for every recipe file. **Engine** `E`: a short text (cache version, Polars, transformer), no disk.
**Whole-recipe hashes (identity; checkable outside the app):** `D` = hash of the sorted `dataset_id:d(file)`; `R` = hash of the sorted `path:r(file)` (checkable with `sha256sum`); `session_key = R[:12]:D[:12]`. They answer "is this the same project state?" (session, export key check, notice to reload); **they never decide what to rebuild**.
**Parts (cheap, no disk):** `dC` = hash of the data files of collection C; `rC` = hash of the canonical resolved definition of C (ingredients and tier-1 steps); `s2`, `s3` = recipe steps at T2 and T3; `a1`, `a2`, `a3` = **audit operations** at T1, T2, T3 (operations only: no reasons, dates, initials).
**The series key (Eve's idea, adopted):** the key of a node is a **series of labelled parts joined in execution order, not hashed again**:
`T1 = E . rC . dC . [a1]`, `T2 = key(T1) . [s2] . [a2]`, `T3 = key(T2) . [s3] . [a3]`, where `[x]` is omitted when empty, so an empty T3 is T2 and an empty T2 is T1 (same key, nothing stored twice). Properties: a node's key is a **prefix** of its descendants' keys (ancestry is readable); the **first differing part** of two keys is where two runs diverge (the original and the audit run share their parts up to the first audit part: audit T1 = original T1 + `a1`); each part is a **leg** of the import verification (engine, data, recipe, audit steps); a series costs no extra hash. Parts are 128 bits (32 hex characters). The key is stored in the file and compared on read.
**On demand or at export only:** `c` = content hash of a frame in a fixed column and row order (the plot is really affected; the attrition snapshot verifies; exported data); `A` = hash of the ordered audit operations with their node (the steps leg); `Rec` = hash of the steps **with** reasons, initials, dates and the event log (tamper evidence); `AR` = sha256 of the generated audit recipe file.
**Which hash decides what:** rebuild: the series keys (every deployment mode). Same project state: `R`, `D`, `E`. Where did the audit change things: first differing part, then `c`. What an import verifies: each part and `A`, `Rec`, `AR`, per leg match, mismatch or not checked, never blocking.
**Two phases for the parts:** phase 1 (safe, now): `rC` = hash of the whole-recipe material and the collection id, `dC` = `D`; phase 2 (precise, rebuilds less): `rC` and `dC` from the recipe graph in `libs/utils`. The key format does not change between phases.
**Invariants (property tests, written first):** same inputs give the same key; any upstream change changes a part; two nodes with different data never share a key; an empty list adds no part; a different order gives a different key; equal keys on two runs give equal content; a stored file with a different key is recomputed and the stale file removed.

## 5. Decisions (Eve, 2026-11-12) and the one still open
**Decided:** (1) the series of labelled parts, 128 bits each; (2) the target is **precise parts from the recipe graph**; the graph is built first (it is needed anyway), so there is no separate coarse phase unless the graph is late; a collection whose inputs cannot be listed safely keeps a coarse part (fail-safe), and a property test is the gate: changing any input of a collection changes its key; (4) the record hash `Rec` with reasons; (5) retire the older `decision_hash` (after checking that nothing else calls it) and drop the plot input key from ADR-089.
**(3) decided (Eve, 2026-11-12):** the data hash stays the **full content, once per session** (reopening reuses the stored tables, verified; the hashing took 150 ms for the 4.6 MB of test data); **no stat cache** now, because the data changes little; later, maybe a **pre-hash automation** that hashes new data when it arrives. A file that is imported or replaced changes its hash: the nodes of the collections that use it are rebuilt, the others are kept; the session key changes, so audit steps of the old data stay with the old session (restoring them warns).

## 6. UML and documents (done 2026-11-12 for the UML, with Eve's general OK to change what must change)
**New diagrams** (folder "Data and configuration"): `DM-KEYS` (the general picture: what each hash is made from, what it answers, the cost), with details `DM-KEYS-CHAIN` (the series of node keys, original and audit, illustrative example), `DM-KEYS-USE` (when each hash is computed, checked and recorded, by situation) and `DM-KEYS-EXPORT` (what the export records and what the import verifies). **Changed:** `HOME-AUDIT-CACHE` (the series key, audit T1 = original T1 plus the step, T3 cached by key), `EXP-MODES` (the legs and the content of effective_run.yaml), `STM-STAGE` (a stored stage is not stored when the step list is empty), `SEQ-EXPORT` (the message about the legs). `audit_uml_model.py`: no discrepancy. PNG files in `docs/UML/diagrams/`.
**Documents amended with a "to be amended" note 2026-11-12:** `docs/foundations/reproducibility_hash_schema.qmd`, ADR-089, `docs/UML/cross_cutting_concepts.md`. **Still to do:** the plot-level diagrams of the audit redesign (UML-HOME-REDRAW-1).
