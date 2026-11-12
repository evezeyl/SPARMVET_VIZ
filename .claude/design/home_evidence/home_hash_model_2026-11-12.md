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

## 4. Proposed model (MINE)
**Three families, one rule each.**
- **A. Identity hashes** (what it was made from; external, verifiable, exported): recipe file set, data batch, engine fingerprint; added for audit: the **audit recipe** (file bytes) and the **steps hash** (the ordered operations with their node; reasons and dates are not in it, as decided for the cache). Never used to decide recomputation.
- **B. Node keys** (is the stored node valid): the same definition for T1, T2 and T3: `key = hash(previous key, ordered steps)`; an empty list keeps the previous key (T3 = T2 = T1, nothing stored twice); the key is stored in the file and checked on read; the T1 root key = `hash(engine, what that collection depends on, data hash of its sources)`. Phase 1 (safe): `hash(recipe material key, collection id)`. Phase 2 (precise, rebuilds less): from the recipe graph in `libs/utils` (datasets, ingredients, tier-1 steps of that collection). Exported per node (original and audit), so the key check of ADR-089 covers the audit nodes.
- **C. Content hash** (what it produced): hash of a node's frame in a fixed column and row order (row order is deterministic, ADR-090), computed on demand, never part of the chain. Used for "affected" (key equality is only the fast path for "identical"), for verifying the attrition snapshot at import, and for the exported data files.
- **Session key**: unchanged in meaning (recipe + data); the audit steps belong to the session record, not to its name.
**Invariants (property tests, written first):** same inputs give the same key; any upstream change changes it; two nodes with different data never share a key; an empty list keeps the key; a different order gives a different key; equal keys on two runs give equal content; a stored file whose key differs is recomputed and the stale file removed.
**Use by situation, identical in all deployment modes:** start: compute A (the data hash once per session), read the stored node keys, recompute only the nodes whose key differs and their descendants; session restore: compare A with the session's A (warn); export: refuse when the view's A or B differ from now (exists), record A, B per node and C per exported frame; import: report each leg (data, engine, recipe, audit recipe, steps) as match, mismatch or not checked, never block, and recompute the attrition snapshot to verify it.

## 5. Open points for Eve (my recommendation first)
1. T1 key: **phase 1 now** (collection id added), phase 2 later. 
2. Retire the older `decision_hash` mechanism: no shipped or gallery recipe uses `sink_parquet`; the orchestrator already uses its own metadata keys. To verify that nothing else calls it before removal (one authoritative way, `rules_legacy_management.md`).
3. Drop the "plot input key" from ADR-089 (never built; plots are not stored) or build it: recommendation drop.
4. Tamper evidence for the reasons: add an `audit_record_sha256` (steps with reasons, dates, initials) to the export, separate from the operations hash that feeds the keys? Recommendation: yes, one more line in effective_run, decided at the export build.
5. Session key truncation (12 hex characters each): harmless for a few sessions; full length costs nothing. Low priority.

## 6. UML and documents to change (nothing edited; each UML edit needs Eve's OK)
`STM-STAGE` (a stored stage): the node can be T1, T2 or T3, and "not stored (equal to the previous key)" is the general case, not "Tier 2 only". `HOME-AUDIT-CACHE`: the key rule (empty list keeps the key), T3 cached by key like the others (storage is an implementation detail), audit T1 as original T1 plus steps (reasoned), content hash. `EXP-MODES` and `SEQ-EXPORT`: the legs (audit recipe, steps hash, record hash) and the per-node keys. **Missing: a diagram of the hash model itself** (families A, B, C, inputs, who uses them): proposed `DM-KEYS` in "Data and configuration". Documents: `docs/foundations/reproducibility_hash_schema.qmd` and ADR-089 (amended by ADR-099 point 16), `docs/UML/cross_cutting_concepts.md` (Provenance).
