# HOME audit: forensics of the current design, and options for what is still undecided

**Written for:** Eve, to decide with. **Written:** 2026-11-11 late evening (for the review of 2026-11-12); **updated 2026-11-12:** F1 canary built, F8 and 3.7 corrected (your rule decides it), section 3.2b (the cheaper engine, measured). **Status:** analysis and
recommendations; nothing here is decided. The only change to code or recipes since the first version is the new QA canary. **Companion:** `home_audit_architect_review_2026-11-12.md` (the app seen by a software architect).
**Method:** `.claude/workflows/design_review_personas.md`. Every finding carries an evidence class: **verified** (run, or read at
`file:line`), **reasoned** (follows from verified facts, not yet run), **assumed** (not checked, said so). Scripts and logs are in
`tmpAI/recipe_review/` (not committed). Points of view used for the consequences: **S** scientist who publishes, **DS** data scientist,
**Dev** developer, **QA** checker, **Ops** operator/maintainer, **N** novice user.

## 1. Forensic findings (new facts that bear on the decisions)

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| F1 | **The central flaw of #60 cannot be shown on any shipped recipe.** In all 7 recipes, every plot-target collection still has a `sample_id` column in its T2 (11 targets in ST22, 1-2 in the others). The flaw ("a sample removed from all plots stays in plots whose data has no such column") needs a plot built on an aggregate without the key | verified: `tmpAI/recipe_review/forensics_data.py` | the reach tests of the full design (and check I2, "N plots contain the column, M do not") have no real fixture. **The canary now exists (2026-11-12):** `QA_aggregated_no_key` (T1 has `sample_id`, the T2 that the plot reads has not; 9 country/year groups, 42 samples; test `test_aggregated_plot_data_has_no_sample_key`, mutation-checked, picture looked at) |
| F2 | The orchestrator loads a recipe **by id from a file** and prepares **all** ingredient schemas on every collection build; there is no hook for an overlay on one collection | verified: `orchestrator.py:110-165` | the design's "early insertion inside the build of each reached collection" (`home_audit_steps.md` 7.5) needs edits in `orchestrator.py` and `cache_keys.py`, both frozen in the build brief |
| F3 | **An audit state can be a forked recipe file, run by a second `DataOrchestrator` in an audit folder, with the existing cache keys.** Proof of concept: a plot-level filter forked with `build_mode2_recipe`, written as `audit_poc.yaml`, built by a second orchestrator: 87 rows, equal to the direct Polars filter on the original T2 (126 rows); the keys differ automatically. ADR-089 already gives "invalidation by construction": `tier2_key = hash(tier1_key, the join's tier2 steps)`, and tier-2 steps are stripped from the tier-1 material, so a late step changes only that join's T2 key and an early step changes the tier-1 key | verified: `tmpAI/recipe_review/poc_forked.py`; `cache_keys.py:75-110`; `t3_translator.py:191-281` | the separate audit cache, the new key scheme and the "canonical hash" of the design (7.1-7.3, D3) largely duplicate machinery that exists and is tested (alternative E, section 3.2). Untested: the early key-exclusion fork mode (new code) |
| F4 | The translator already handles all 8 operators and builds the forked recipe **in memory** (`build_mode2_recipe`, a deep copy, plots stripped, forks named `<join>__t3_<plot>`) | verified: `t3_translator.py:70,86-142,191-281` | the "step compiler" (D3) mostly exists; two modes are to be added (shared late, early at the sources) |
| F5 | Format versioning partly exists: ghost files carry `schema_version: 2`; `AuditStep` is a `TypedDict(total=False)`, so **added fields are safe**; `LegacySessionError` fires only on pre-rename keys | verified: `session_manager.py:47-57,379,433,141` | decision 9 ("the session format changes: confirm") is overstated for an additive record; only replacing the list by an event store needs a new version and a migration |
| F6 | **2 of 7 shipped recipes declare no `is_primary_key`** (`2_test_data_ST22_dummy`, `figshare_integration`); both join on `sample_id`, so inference from the joins finds the key. ST22 declares it on 11 of 12 schemas, Abromics 3 of 4, `3_test_no_joins` and `demo_abromics` all | verified: `forensics_data.py` and a join scan | "declared keys only" would switch sample exclusion off for 2 of 7 recipes; the proposed "declared + join inference" works for all 7 |
| F7 | **Blast radius of replacing My view, Compare and per-plot steps** (code refs in `app/` and `libs/*/src`, then test refs): `t3_audit_steps_by_plot` 35 in 9 files (13 in tests), `tier_toggle` 43 in 9 (12), `aesthetic_override` 42 in 8 (34), `comparison_mode` 11 in 3 (23), `plot_view` 12 in 2 (10), `exclusion_row` 17 in 7 (9); `home_theater.py` has 2255 lines | verified: grep counts | the full design is a large, cross-cutting change; the cut avoids most of it |
| F8 | **A consequence of your rule (corrected 2026-11-12).** Under the new design plots change only through an audit step. `pipeline-exploration-simple` and `web-demo` have `interactivity_enabled: true` and `t3_sandbox_enabled: false`, so their users filter tables to look at the data and the plots always show the Result. That is what your rule asks: **it is not a loss.** My first version called it a loss that needs your yes; that was wrong, your rule already decides it. What changes is the code of today: `plot_view` offers "My view" (and Compare) to them and exploration filters change that plot (`home_theater.py:481`, ADR-085/098). Items to implement, in 3.7 | verified: `config/app_features/pipeline-exploration-simple.yaml` lines 7-25, `web-demo.yaml` lines 8-21, `home_theater.py:478-490, 976-1006`, `home_audit_steps.md:55-60` | the two features need no "Plot to show" strip (one choice only), `comparison_mode_enabled: false` in `pipeline-exploration-simple` (Compare would show the same plot twice) and one help line |
| F9 | **Wording drift survived the consistency pass:** `home_audit_steps.md` still says "Audit workspace" (1x), "workspace" (2x) and "rebuilt" (1x); the diagram `HOME-VIEW-MATRIX` is titled "What Exploration and the Audit workspace show and do"; the word "never" is still in 16 places of 8 HOME diagrams (EXPLORATION 3, VIEW-MATRIX 2, AUDIT-FLOW 3, AUDIT-EFFECT 3, AUDIT-CACHE 2, AUDIT-LINEAGE 1, AUDIT-COMPONENTS 1, UI-HOME-EXPLORATION 1) | verified: term scan of the design files and of `docs/UML/app.mdj` | breaks your UML rule; to fix on 2026-11-12 in track D (statements about built behaviour, such as "never exported" for preview filters, are true today; those about the target are not) |
| F10 | The data check and `test_render_every_plot` passed with wrong figures (recipe review); the two generated recipe audits pass and cannot see a many-to-many join or an ignored plot key | verified: recipe review, #66, #68, #71 | the safety net must be the canaries plus pictures looked at, not green tests alone |
| F11 | **Property tests bring randomness.** D9 proposes `hypothesis`; random generation without a fixed seed would add the kind of intermittent failure we are chasing in the browser gate (#72) | reasoned: Hypothesis is seeded per run unless `derandomize=True` or a fixed seed is set | if adopted: derandomized or fixed seed in CI, the seed printed on failure |
| F12 | Build time is not a constraint at this scale: the slowest plot-target collection builds in 0.3 s (Abromics), 203,146 rows in 0.2 s (figshare) | verified: `forensics_data.py` | exact "trial computations" (D4) are affordable here; production data size is **assumed unknown** |
| F13 | Browser gate flakiness: timing races in the tests under load, **not** caused by the 2026-11-11 changes (the old code fails as often under the same load) | verified: controlled experiment, section 5 | the UI-heavy parts of the build are verified with a gate that gives false alarms; hardening proposed in #72 |

## 2. What holds (checked again, no change needed)

Original data is never touched; the rule "informs, warns, lets the user decide; blocks only the technical"; early insertion on **every ingredient that has the
key** (7.5) is the right rule and also covers joins that could bring a sample back from the right side (shipped recipes use only `left` 24x, `inner` 5x and one `join_filter`; the action's options also include outer, semi, anti and cross);
key mapping by declared keys plus join steps, never by column names (`VirulenceFinder.metadata_sample_material` shows why); the audit stays out of the original anchors.

## 3. Decisions: options, consequences by point of view, recommendation

Order: the big structural choices first (they decide the size of the build), then the numbered decisions of the reading guide, then the new ones.
"Reversibility" says how hard it is to change your mind later.

### 3.1 The size of the first audit build: cut or full (meta-decision)

| Option | S | DS | Dev | QA | Ops / N |
|---|---|---|---|---|---|
| **(1) Cut first** (`home_audit_first_cut.md`), then the full design | gets safer figures sooner (NA, entities, warnings, reasons, export review); "remove everywhere" still manual | statistics risk (C1) is warned, not removed | small, pure modules reused later; avoids the 3 frozen files | each piece has an oracle and canaries | no new cache; users see little new |
| **(2) Full design straight** | the structural problem of #60 solved | entity removal at the sources recomputes statistics correctly | large (F7), screen last, needs orchestrator/keys work (F2) unless E (3.2) | most paths to test, no real fixture for the flaw (F1) | new cache and dialogs to learn |
| **(3) Engine fixes and Exploration only, audit unchanged until after the demo** | the old audit stays as is, with its known limits | #62, #61, #63-info fixed; the rest warned in the help | smallest | least to retest | nothing new; the demo shows the old audit |

**Recommendation: (1).** It fixes what is verified wrong now (#61, #62, #63 information) and adds the safeguards with the best value per effort, every piece is reusable by the full design
(so no work is undone), and it needs no decision from group 2. **Reversible:** yes (each piece alone). **What would change it:** if the demo must show "remove a sample everywhere", choose (2) with the narrow
reach of 3.3-B and engine E (3.2); if there is no time before the demo, (3).

### 3.2 How audit data is computed (not in the reading guide; replaces part of decision 8 and D1-D3)

| Option | S | DS | Dev | QA | Ops |
|---|---|---|---|---|---|
| **A. Bespoke** (design 7.1-7.3): separate audit cache, new chained keys, canonical hash, orchestrator and `cache_keys` extended | same result | same | new cache, new keys, edits in two frozen files, hash and executed list kept in step by a compiler | new tests for keys and cache | finer reuse (per stage) |
| **E. Forked recipe**: generalise `build_mode2_recipe` into an audit recipe builder, write it into `audit/<session>/`, run a **second `DataOrchestrator`** on it; ADR-089 keys for free (F3) | the exported recipe **is** the audit: anyone re-runs it | figure = bundle by construction (today they disagree for #62) | far less new code; orchestrator and keys stay frozen; old states deleted by directory (N = 5) | the key and the executed steps are the same object; existing `test_cache_keys` covers the keys | **coarser**: `tier1_key` is recipe-wide, so an early step rebuilds every collection's T1 (0.3 s here; production size unknown) |

**Recommendation: E, after a spike** that proves the one untested mode (early key exclusion on every ingredient with the key). Reasons: it reuses tested machinery, keeps the frozen files frozen,
and makes "what you see = what the export re-runs" true by construction. Finer keys can be added later behind the same interface if production data makes the rebuild slow. **Reversibility:** high
(the interface is "recipe in, frames out"). **Risks to check in the spike:** `id` must equal the file name (ADR-092); the session key and the export key check must name the audit state explicitly;
a forked recipe is a full resolved copy (size, N = 5 states).

### 3.2b The cheaper engine (E) explained: what it gives, what it costs (added 2026-11-12, measured)

**What E is.** Today a recipe is a file: the orchestrator turns it into stored tables (T1, then T2) and every plot reads T2. E treats an audit state the same way. Take the recipe, add the audit steps to a copy
(`build_mode2_recipe`, which export Mode 2 already uses for the bundle), write the copy as a file in an audit folder, and let a second `DataOrchestrator` build and store it. The audit adds no new way of computing data:
it is "the recipe plus your steps", run by the same code and cached by the same keys (ADR-089). "Cheaper" means: less new code, because the machinery already exists and is tested.

**Measured** (`tmpAI/architect/engine_cost.py`; one plot-level filter per recipe; second orchestrator in a temporary folder; load average 2.9):

| Recipe and plot | T2 rows, original -> audit | Equal to a direct Polars filter of the original T2 | Original cold / warm | Fork cold / warm | Fork's stored stages | Recipe file |
|---|---|---|---|---|---|---|
| ST22 `qc_reads_horizontal_barplot`, `sample_id != <one id>` | 42 -> 41 | yes | 0.09 / 0.25 s | 0.08 / 0.01 s | 2 files, 0.06 MB | 15 KB entry file -> 42 KB (one resolved file) |
| Abromics `abromics_st_by_country` | 342 -> 335 | yes | 0.05 / 0.00 s | 0.04 / 0.00 s | 2 files, 0.01 MB | 3 KB -> 10 KB |
| figshare `plot_A_phenotype_bar`, `host_animal_species != 'Bos taurus'` | 203,146 -> 151,569 | yes | 0.16 / 0.07 s | 0.14 / 0.05 s | 2 files, 0.28 MB | 3 KB -> 8 KB |

In all three the tier-1 key of the fork differs from the original (verified), so an audit never reuses or overwrites a stored stage of the original. Timings are noisy at this size (the original "warm" 0.25 s is slower than its cold run):
read them as "all below 0.3 s", not as a ranking. The builds read the shipped test data; **production size is not known.**

| | Pros of E | Cons of E |
|---|---|---|
| Correctness | the audited figure, the table and the export are one computation: "what you see is what the export re-runs" holds by construction (today the figure and the bundle disagree for #62); an engine bug is fixed once | an engine bug is inherited by the audit (true for any design), so #61, #62 and #63 come first |
| Size of the change | much less new code than a bespoke cache; the translator already handles all 8 operators (F4); `cache_keys.py` and `orchestrator.py` stay frozen; the recipe cache is keyed by absolute path, so a second orchestrator does not collide with the first (`cache_keys.py:179-205`, verified) | one mode is new and untested: early key exclusion on every ingredient that has the key (F2, F3); only the late, plot-level mode was run |
| Cache | invalidation by construction (a changed step changes the key); the audit has its own folder, so it does not meet the shared `anchors/` folder (see architect review AR4); old states are removed by deleting a directory | **coarser:** a join added to the recipe changes the tier-1 material (`cache_keys.py:tier1_material` strips only plot sections and tier-2 steps), so the audit rebuilds tier 1 of its collection and shares nothing with the original's stored stages. Fine at 0.3 s and 203,146 rows; **unknown at production size** |
| Disk | small here (2 files per state, 0.01 to 0.28 MB) | each state is a resolved recipe copy plus stored stages; 5 states per session and many sessions need a clean-up rule, and none exists for stored stages today (AR4) |
| Checking and export | the bundle can carry the audit recipe, runnable by anyone with the debug scripts (`debug_assembler.py`); the oracle is a direct Polars filter of the original T2 (what the proof of concept used: independent and strong) | `id` must equal the file name (ADR-092), so ids must be generated and unique; the session key and the export key check must name the audit state explicitly |
| Security | filters translate to named actions, no code | the audit state is **a recipe**, and recipes are code (architect review AR1): a `developer_raw_yaml` step is run through `eval`; E makes that path a normal one, so the audit kinds and the trust of imported steps must be decided first (N2, N3) |
| Reversibility | the interface is "recipe in, frames out": a finer cache can replace the backend later | the screen is built against that interface; changing it later costs the screen |

**What E does not solve:** the scattered view policy (AR2), the size of the handlers (AR3), the NA rule (3.4), many-to-many joins (#68).
**The spike before deciding** (one session, no UI): (1) early key exclusion as a fork mode, run on all 7 shipped recipes with the oracle "same rows as filtering every ingredient that has the key"; (2) measure the rebuild on the largest recipe;
(3) confirm that the session key and the export key check work with an audit state; (4) try the clean-up rule (N6); (5) try the trust check (N3).

### 3.3 Reach and stage (guide decisions 1 and 6; the structure of audit mode)

| Option | S | DS | Dev | QA | N |
|---|---|---|---|---|---|
| **A. Full:** kind x 3 reaches with a checklist x levels 0-3 | most expressive; "same table" is the hardest sentence (open wording question, section 17) | level 2 (value filter after an aggregation) is the statistically weakest | two new fork modes, coverage check, overview | most paths | three choices and a checklist |
| **B. Two reaches:** "this plot" (level 3) and "whole project by sample ID" (level 0); value filters and drops only at plot level | covers the real job (bad sample out everywhere) with one clear choice | entities removed at the sources, statistics recomputed; no filter-on-aggregate | one new mode (early, key only) plus what exists | about half the paths | two plain choices |
| **C. Plot level only** (the cut) | "everywhere" stays many per-plot steps | statistics risk warned, not removed | none | minimal | hidden limit, stated in the help |

**Recommendation: B for the first full audit, C as the stepping stone.** The verified motivating flaw is key exclusion; level 2 value filters are the weakest statistically, and the "same table" reach is the
hardest to explain and to test. A can be added later as extra options on the same machinery. **Reversibility:** high. **What would change it:** a real lab need for table-level filters (that is
usually a recipe change, tier-1, not an audit step). **Needs:** the canary of F1 so that B has something to be tested against.

### 3.4 NA rule (guide decision 2)

| Option | S | DS | Dev | QA | Ops |
|---|---|---|---|---|---|
| **A. Selectable "NA (missing)"**: "remove" filters keep NA unless selected, "keep" filters drop it unless selected, comparisons drop NA unless "keep NA" is ticked; always say how many | "remove Norway" keeps unknown-country rows | standard for comparisons; `!=` behaves as people expect | an optional `na` parameter on the 8 actions, default **= today's behaviour**, passed explicitly by the audit, VizFactory and the translator | matrix operators x null/NaN (the table of #63) and canary `QA_ST_with_NA` | existing recipes unchanged |
| **B. SQL/Polars semantics + information only** (WP3a) | surprising rows vanish but are counted | same as today | none | counts tested | none |
| **C. Always keep NA unless selected** | simplest sentence | `x < 50` keeps missing values: inflates | like A | like A | changes today's results |
| **D. Ask every time** | most explicit | no hidden default | like A | like A | friction, fatigue |

**Recommendation: A, with B first** (B is WP3a and needs no decision). Default of the registered actions stays today's behaviour so no existing recipe changes; the audit always passes the rule explicitly and stores it in the step.
**Reversibility:** medium (the stored step carries the rule). **Depends on:** decision 12 (compiler) only for the final form.

### 3.5 Event log (guide decision 9)

Options: **A** event-sourced store (steps derived); **B** step list plus a separate log; **C** additive fields on the step record (`created_at`, `removed_at`, `reason_category`, `acknowledged_warnings`), the log is the derived list; **D** nothing (today: hard delete).
Consequences: S - C and A both let the report list removed steps, D cannot; DS - attrition and overrides are reportable with A or C; Dev - C is trivial (F5), A needs a new version and a migration, B has two stores that can disagree (rejected in the developer review); QA - C: property "a removed step stays listed"; Ops - C keeps sessions readable.
**Recommendation: C for the cut, A only if the full design needs replay.** Reversible. (This also removes the "session format changes: confirm" worry of the cut, piece 6.)

### 3.6 Keys (guide decision 5)

Options: **A** declared `is_primary_key` + join steps + inference (the design); **B** declared only; **C** join steps only. Evidence F6: B switches sample exclusion off for 2 of 7 shipped recipes; C misses a recipe with no joins that declares its key.
**Recommendation: A**, plus a recipe-validator warning "no key declared" (advice, not a block) and the docs line "declare `is_primary_key` on the ID column". **Reversibility:** high.

### 3.7 Without the sandbox flag (was decision N1; closed by your rule on 2026-11-12)

Your rule: plots change only through an audit step, and the sandbox flag is what turns audit on. A feature without it (`pipeline-exploration-simple`, `web-demo`) therefore never changes a plot: users filter tables to look at the data and the plots show the Result.
**No decision is needed.** In the first version of this file I asked for your yes and called it a loss; that was a mistake (I read "no changed plot" as a loss, it is the intended behaviour).
What it means for the build (the left column is verified in the code of today):

| Item | Today (built, ADR-085/098) | After the audit build |
|---|---|---|
| "Plot to show" strip | offers Result, My view and, if `comparison_mode_enabled`, Compare (`home_theater.py:976-1006`) | one choice only (Result), so the strip is not shown |
| Exploration filters and the plot | change the plot in My view (`home_theater.py:481`) | change the table only |
| `comparison_mode_enabled` in `pipeline-exploration-simple` | `true` with the sandbox off: Compare puts Result next to a filtered My view | must be `false` (Compare would show the same plot twice); the flag validator should refuse the combination (the flag is a child of the sandbox flag) |
| "Data to show: My view" | table with exploration filters | unchanged; the badge already tells that the plot is not filtered (`view_badge.py:66`, text to update with the audit build) |
| Help text | says My view is a scratchpad | one line: "In this configuration filters change the tables; plots always show the Result." |

Until the audit build ships nothing changes (ADR-098 stays as built). **Reversible.** The flag rule joins decision N4 of the architect review.

### 3.8 The remaining numbered decisions (short)

| # | Decision | Options | Recommendation and why |
|---|---|---|---|
| 3 | Reason categories | free text / fixed list + text / configurable | fixed list (technical failure, contamination, duplicate, out of scope, outlier by value, other) + text, "outlier by value" flagged; configurable later (D7). A list makes the report groupable and costs one field |
| 4 | Figure caption "n = X" | off / optional / always | optional, off by default, only for entity counts; always would stamp n of the wrong thing (rows vs samples) |
| 7 | Audit table selector (T1/T2/T3) | now / with the full audit / never | with the full audit (needs audit T1); not in the cut |
| 8 | Exact trial computation vs estimate | exact / estimate / exact with estimate fallback | exact with an "estimate only" fallback for large data (F12: cheap here, unknown in production) |
| 10 | Lineage map | own HOME renderer / Blueprint's map / text chain | text chain (as drawn in the dialog) now, own plain renderer in the full audit; Blueprint's map is forbidden by the cross-panel rule |
| 11 | First guard-rail list and thresholds | the list of `home_audit_steps.md` section 19 / fewer / more | the cut takes I1, I2, C1, C3, W4 only; thresholds (20 %, 3 entities) as settings; test the wording with 2-3 scientists before it is final (warning fatigue, section 20) |
| 12 | D1-D14 | each separately | now: D5 (pre-export review), D8 (honest wording), D10 (visible "N audit steps"), D13 (versions, already partly there); with E: D3 becomes the generalised translator; later: D1 recipe graph (start as the key-mapping module), D4 dialog, D7 policy, D11 quick path; D9 `hypothesis` only with a fixed seed (F11) or seeded parametrised tests; D12 background computation when data is large |
| 13 | Legacy names (`t3_*`, node types) | keep / rename | keep plus a glossary line; a rename touches F7's references and saved sessions |

### 3.9 The recipe questions (from `recipe_review_st22_2026-11-11.md`)

R1 anchor: **(a)** virulence + MLST + metadata, no ResFinder (recommended: the plots read virulence, AMR has its own collection and heatmap; the QA canary shows the correct per-sample AMR count if you want AMR in a figure).
R2 four samples without usable phenotype: **(a)** not plotted with a note "n = 38 of 42" (recommended; "0" would say "no resistance"). R3: keep the 2023-2025 filter and put the years in the MLST title. R4: decide `virulence_variants` facets with R1.

## 4. The recommended path in one table

| Step | What | Needs from you | Unlocks |
|---|---|---|---|
| 0 | Builders: WP1-WP9 as in the brief. The canary of F1 is **done** (`QA_aggregated_no_key`). **Proposed by the architect review (needs your yes):** the pure view policy comes first inside #56 (AR2) | your yes for the proposal | tests for the reach decisions; one rule for table, plot and export |
| 1 | Decide 3.1 (cut first), 3.2 (E, after a spike), 3.4 (NA: A with B first), 3.5 (C), 3.6 (A); 3.7 is closed by your rule. **New, from the architect review:** N2 (`developer_raw_yaml` in the audit), N3 (trust levels for recipe sources), N4 (flags in one table), N5 (architecture rules as tests), N6 (stored stages) | 5 + 5 answers | pieces 1-7 of the cut |
| 2 | Spike: early key exclusion as a fork mode + second orchestrator, with the clean-up rule and the trust check (one session, no UI; list in 3.2b) | 3.2 yes | the decision 3.3 with evidence |
| 3 | Decide 3.3 (B) and the rest of 3.8 | after the spike | the full audit plan |
| 4 | Fix F9 (wording, UML, "never") | your rule on built-behaviour "never" | consistent diagrams |

The architect review (`home_audit_architect_review_2026-11-12.md`) adds ten findings about the app itself (AR1-AR10); the first is that recipe text runs as Python code.

## 5. Browser gate flakiness (finding F13)

Question asked: can the failures of the later browser runs come from a random seed, and where do they come from?

**Randomness (verified).** pytest 9.0.3 with only the Playwright plugins: no random-order, no xdist, no `hypothesis` installed; test order is the file order. The app's randomness is the jitter
reshuffle seed (`secrets.randbits(31)`, `home_theater.py:432,723`, only for plots with unpinned jitter) and `uuid4` step ids (`session_manager.py:83`). None is on the failing paths. So: not a random seed, not random order.

**Controlled experiment (verified; smoke file, a diagnostic plugin that records load and, on failure, the server log and the page text; "load" = 8 busy CPU processes):**

| Code | Load | Runs | Failed |
|---|---|---|---|
| with the changes of 2026-11-11 | none | 2 | 0 |
| with the changes | yes | 3 | 1 (`test_session_label_saves_on_blur`, load average 11.8) |
| before the changes (`d48c3bb`) | none | 1 | 0 |
| before the changes | yes | 3 | 1 (`TestStartup::test_data_analysis_recipe_load`, 63 s, load average 10.6) |

The old code fails as often as the new code, and only under load: **the failures do not come from the recipe, canary, facet or data-check changes.** Together with the three earlier failures (info-panel twice, preview-row removal once, label once)
the failures are always in different tests.

**What the captures show (verified):**
- `test_session_label_saves_on_blur` reads the label from the disk **right after** `_wait_shiny(page)` (`test_shiny_smoke.py:740-742`). `_wait_shiny` only waits for the "busy" class to be absent and can return before the server has processed the blur event, so a slow server loses the race. This is a race in the test.
- The start-up failure (60 s wait for the "Quality Control" tab): the page text at failure shows the **default recipe (Abromics) instead of the selected one**, and the server log has no error: the selection was lost. A separate test of the suspected cause (select the recipe immediately after `goto`, as the tests do) lost the selection in 1 of 54 trials against 0 of 54 when waiting for "connected and idle" first: **suggestive, not proof**.
- `test_removing_an_applied_row...` (grid of 41 instead of 42 rows): not reproduced here. Reasoned: the same class (a read right after an action).
- Not reproduced either: the four flaky tests alone, in a loop under load: 0 failures of 10. The failures need the context of the whole file (many earlier tests and sessions on one server).

**Conclusion.** Timing races in the browser tests (waits that return before the effect started, reads right after an action), made likely by a loaded machine (this machine runs several Claude sessions and apps at load average 3 to 4, 16 with the test load). Not a defect in the application as far as these captures show, and not caused by the changes. **Proposed hardening, not done** (issue #72): wait for connected and idle before selecting the recipe and check the selection took effect; poll the disk in the label test; read the grid until two reads agree before taking `before`; print the server log in the failure output (the plugin in `tmpAI/recipe_review/diag/diag_plugin.py` is a model); `--durations` in the standard command. Until then: a red gate is a question, rerun the failing test alone.

## 6. Not verified (said plainly)

Production data size and the real cost of rebuilding all collections per early step (the measured late-mode costs are in 3.2b: all below 0.3 s on the shipped data); whether the early key-exclusion fork mode works on every shipped recipe (only the late plot-level mode was run);
usability of the warning texts (needs 2-3 scientists); the `hypothesis` seeding behaviour was taken from its documented defaults, not run here.
