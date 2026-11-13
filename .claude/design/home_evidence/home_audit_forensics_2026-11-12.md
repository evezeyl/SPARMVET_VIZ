# HOME audit: forensics of the current design, and options for what is still undecided

**Written for:** Eve, to decide with. **Written:** 2026-11-11 late evening; **rebuilt 2026-11-12 (second pass)** after you asked me to check every consequence against what is decided. **Status:** analysis and recommendations; nothing here is decided.
The only change to code or recipes since the first version is the new QA canary. **Companions:** `home_audit_architect_review_2026-11-12.md` (the app seen by a software architect) and `home_gating_and_test_configs_2026-11-12.md` (the decision paper on how filters are gated by configuration, and on test configurations; written after your answers of 2026-11-12).
**Method:** `.claude/workflows/design_review_personas.md`. Evidence classes: **verified** (run, or read at `file:line` or in a diagram), **reasoned** (follows from verified facts, not run), **assumed** (not checked, said so). Scripts and logs are in
`tmpAI/recipe_review/` and `tmpAI/architect/` (not committed). Points of view: **S** scientist who publishes, **DS** data scientist, **Dev** developer, **QA** checker, **Ops** operator, **N** novice user.
**Status words used on every item:** **DECIDED** (you decided it; the source is named), **CONFIRM** (proposed in the design review, marked `[confirm]`, waiting for you), **OPEN** (a question of the reading guide), **MINE** (a proposal that comes from these forensics and is not in the design).

## 0. Status map, and what I got wrong the first time

### 0.1 What the design says today (read from `home_preview_filters.md`, `home_audit_steps.md`, ADR-098, ADR-099, the reading guide, the diagrams, issues #56 and #60)

**A caution on the word DECIDED.** ADR-099 is "ACCEPTED in principle" (2026-11-11, items marked `[confirm]` need your OK before code), while issue #60, #56 and the reading guide still say "designed, not decided" for the design as a whole. I mark DECIDED only what
`home_audit_steps.md` section 16 lists as decided by you, or what ADR-099 states as a decision; everything else is CONFIRM or OPEN. The documents differ in wording here; if I read one of them wrongly, tell me and I change the label.

| Item | Status | Source |
|---|---|---|
| **Exploration** (Raw or Result) is for looking: a preview filter or column choice changes the **table only**, per view and dataset, is cleared on a view or recipe change, is never saved or exported, and **never changes a plot** | DECIDED | `home_preview_filters.md` 1-5; ADR-099 point 1 |
| **The target screen:** the strip is "Exploration: one toggle **Data: Raw (T1) \| Result (T2)**. **No "Plot to show"**, no grey explanations"; "Not in this mode: **My view, Compare, Plot to show**, Send to Audit, any change to a plot or to the data" | DECIDED | `home_preview_filters.md` 2; diagram `UI-HOME-EXPLORATION` (picture read); `HOME-VIEW-MATRIX` |
| **Audit mode** replaces My view and Compare: a mode switch "Exploration \| Audit mode" at the left of the group-tabs row, **only with the sandbox flag**; Compare is an on/off toggle inside it; there is no "Plot to show" there either | DECIDED | ADR-099 point 2; `home_audit_steps.md` 3 |
| **Without the sandbox flag only Exploration exists.** "Keeping My view as a scratchpad without the sandbox flag" is listed under **alternatives not chosen** ("plots would change without a reason or a record"). `comparison_mode_enabled` becomes a child of the sandbox flag; the validator gets two rules; `pipeline-exploration-simple` (comparison on, sandbox off) "must change" | DECIDED (the validator rules: confirmed by you in the review) | ADR-099 point 2 and "alternatives"; `home_audit_steps.md` 3, 13, 14, 16 |
| **Sequencing:** nothing is removed before audit mode exists: My view, Compare and "Plot to show" stay as built until then | DECIDED | reading guide 5; #56 scope note; #60 "not to be built before"; brief S3 |
| No draft; three-step dialog; reason; Apply and Cancel; Undo last, Revert to step N, Remove all; initials; broken steps block the export; drop policy; project overview and coverage check; atomic Apply; the software informs, warns, lets the user decide; **the NA rule "never silent"** (NA a visible, selectable value; "remove" keeps NA unless selected; comparisons drop NA unless ticked; counts always shown) | DECIDED | `home_audit_steps.md` 16, 19 |
| Reach selector in the dialog, nothing preselected; stage follows from the kind; numbers 0-3; **early insertion at the sources inside each reached collection**; **a separate audit cache with chained keys, a canonical hash, N = 5 as a setting, recompute when missing** | DECIDED | `home_audit_steps.md` 5, 7, 16 |
| **Keys:** declared `is_primary_key` plus the join steps; **inference as fallback** when none is declared; read from the loaded dictionaries; never from column names | DECIDED ("later in the review"); the reading guide still lists it as question 5, so the two files disagree | `home_audit_steps.md` 7.4, 16; reading guide 3 |
| Event log accepted **in principle** | DECIDED in principle; the form (event-sourced, D2) is CONFIRM | reading guide 3; `home_audit_steps.md` 11, 16, 20 |
| `developer_raw_yaml`: "stays as it is ... listed as 'recipe fragment', deletable, **never authored in audit mode**"; `aesthetic_override` out of scope | DECIDED as the design text; "legacy step types kept" is CONFIRM (question 13) | `home_audit_steps.md` 4, 16 |
| Question 1 stage = the table the user looks at; 3 reason categories; 4 optional caption; 6 three reach options with a checklist; 7 audit table selector; 8 trial computation; 9 event-sourced log; 10 lineage map; 11 first checks and thresholds; 12 D1-D14 (with `hypothesis`); 13 legacy types and `t3` names kept | CONFIRM / OPEN | reading guide 3; `home_audit_steps.md` 16, 20 |
| A **smaller first audit version** ("the cut") | on the path: the reading guide (6) says "possible once you decide ... tell me if you want that cut written as a plan"; `outdated/home_audit_first_cut.md` is that plan, a PROPOSAL | reading guide 6 |
| **Your answers of 2026-11-12:** filters that are not active are **hidden**; the gating follows the configuration and must be gated cleverly; preview filters and filters that change and go to audit stay different things; correct configuration files for automatic tests are needed; the demo is not a design concern (demos may use other configurations) | DECIDED (as I read them; section 1 of the gating paper asks you to confirm the reading, Q1-Q2) | `home_gating_and_test_configs_2026-11-12.md` |

### 0.2 What I got wrong in the first version (corrected below)

1. **The strip (F8, 3.7).** I wrote it as a per-feature case ("one choice only, so the strip is not shown") and said "My view in the Data toggle stays unchanged". The design removes "Plot to show" **everywhere** and My view leaves the Data toggle too; the strip becomes "Data: Raw | Result" in every feature. I also asked for a decision that ADR-099 had already taken.
2. **Keys (3.6) and the NA rule (3.4)** were shown as open options; the design already decides inference as fallback and "never silent". What is open is smaller (see 3.4, 3.6).
3. **The cheaper engine (E)** was shown as "the way". It **reconsiders a decided mechanism** (the audit cache with its own keys and canonical hash). I also measured the export's mode (a plot-level fork) while the design runs levels 0-2 in the fork and keeps level 3 at render time (F15). I listed a clean-up rule as missing; the design has it (N = 5).
4. **"Until the audit build ships nothing changes"** is the decided sequencing, but it **contradicts your rule for the two features without the sandbox flag** (F8). That is the real catch, and it is the open question 3 of the build brief, never answered.
5. **My proposal to put a pure view policy first in WP4** was built on today's view model (Raw, Result, My view, Compare) that the target replaces; WP4 is deliberately interim. **Withdrawn** (architect review 3.2).

### 0.3 Where my proposals reconsider something decided or on the path

| # | My proposal | What it reconsiders | Where |
|---|---|---|---|
| R1 | E: audit stages computed by running a forked recipe | the decided mechanism of 7.1-7.3 and 14 (overlay in `orchestrator.py`, new key function). The decided **properties** can be kept (table in 3.2b); one changes (the T1 stage is not shared with the original) | 3.2, 3.2b |
| R2 | Reach in two options for the first full build | the CONFIRM item "three options with a checklist" (and the decided level 2 reach "all plots that use the same table") | 3.3 |
| R3 | Event log as additive fields on the step record | the CONFIRM item D2 (event-sourced) | 3.5 |
| R4 | Keep the `developer_raw_yaml` step type but **display-only**: the translator refuses it (the design's block B1, "a step the forked recipe cannot represent"). Verified: no code creates this step, it can only arrive in a saved or imported session file | CONFIRM question 13 ("legacy step types kept") and the design text of 4 ("stays as it is") | architect review N2 |
| R5 | Features without the sandbox flag get the target strip before audit mode exists | the decided sequencing ("nothing removed before audit mode") and the freeze of the strip in brief S3 | 3.7 |
| R6 | "Decision 9 is overstated": an additive record does not need a new session format | the stated impact of question 9 | F5, 3.5 |

## 1. Forensic findings (new facts that bear on the decisions)

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| F1 | **The central flaw of #60 cannot be shown on any shipped recipe.** In all 7 recipes every plot-target collection still has a `sample_id` column in its T2 (11 targets in ST22, 1-2 in the others). The flaw ("a sample removed from all plots stays in plots whose data has no such column") needs a plot built on an aggregate without the key | verified: `tmpAI/recipe_review/forensics_data.py` | the reach tests (and check I2, "N plots contain the column, M do not"; edge case "plot on an aggregate" in `home_audit_steps.md` 15) had no real fixture. **The canary exists since 2026-11-12:** `QA_aggregated_no_key` (T1 has `sample_id`, the T2 the plot reads has not; 9 country/year groups, 42 samples; mutation-checked, picture looked at) |
| F2 | The orchestrator loads a recipe **by id from a file** and prepares **all** ingredient schemas on every collection build; there is no hook for an overlay on one collection | verified: `orchestrator.py:110-165` | the DECIDED early insertion (`home_audit_steps.md` 7.5) needs edits in `orchestrator.py` and `cache_keys.py` (listed in section 14 of that file), both frozen in the brief. The design also plans "no unused-ingredient builds" (14), which is the same cost |
| F3 | An audit state **can be a forked recipe file run by a second `DataOrchestrator` in an audit folder, with the existing keys.** Proof of concept (plot-level fork, the export's mode): 87 rows, equal to the direct Polars filter of the original T2 (126 rows); keys differ automatically; ADR-089: `tier2_key = hash(tier1_key, the join's tier2 steps)` | verified: `tmpAI/recipe_review/poc_forked.py`; `cache_keys.py:75-110`; `t3_translator.py:191-281` | this is R1 (a proposal that reconsiders a DECIDED mechanism). Untested: the two modes HOME needs (shared late, early at the sources) |
| F4 | The translator already handles all 8 operators and builds the forked recipe in memory (`build_mode2_recipe`) | verified: `t3_translator.py:70,86-142,191-281` | the "step compiler" (D3, CONFIRM) mostly exists. The design **already plans** to extend it with two modes for the export (`home_audit_steps.md` 7.6; ADR-099 point 8), so those two modes are needed anyway |
| F5 | Format versioning partly exists: ghost files carry `schema_version: 2`; `AuditStep` is a `TypedDict(total=False)`, so added fields are safe; `LegacySessionError` fires only on pre-rename keys | verified: `session_manager.py:47-57,379,433,141` | R6: an additive record does not by itself change the session format; replacing the list by an event store (D2) does |
| F6 | **2 of 7 shipped recipes declare no `is_primary_key`** (`2_test_data_ST22_dummy`, `figshare_integration`); both join on `sample_id`. ST22 declares it on 11 of 12 schemas, Abromics 3 of 4, `3_test_no_joins` and `demo_abromics` all | verified: `forensics_data.py` and a join scan | supports the DECIDED inference fallback: "declared keys only" would switch sample exclusion off for 2 of 7 recipes |
| F7 | **Blast radius of replacing My view, Compare and per-plot steps** (code refs in `app/` and `libs/*/src`, then test refs): `t3_audit_steps_by_plot` 35 in 9 files (13 in tests), `tier_toggle` 43 in 9 (12), `aesthetic_override` 42 in 8 (34), `comparison_mode` 11 in 3 (23), `plot_view` 12 in 2 (10), `exclusion_row` 17 in 7 (9); `home_theater.py` has 2255 lines | verified: grep counts | agrees with the impact list in `home_audit_steps.md` 14; the cut avoids most of it |
| F8 | **The interim contradicts your rule for two features.** Your rule (DECIDED): without the sandbox flag no plot ever changes. Today `pipeline-exploration-simple` and `web-demo` (`interactivity_enabled: true`, `t3_sandbox_enabled: false`) offer "Plot to show: My view" and "Data to show: My view", and an applied preview filter **changes that plot with no reason and no record** (`home_theater.py:478-490`, ADR-085/098). The decided sequencing keeps it until audit mode exists, and the question of the interim (brief section 5, question 3) was never answered. `pipeline-exploration-simple` also has `comparison_mode_enabled: true` (a dead flag the validator rules will refuse) | verified by reading the code and the flag files, **and by running** scratch configurations with the same flags (`test-preview`: "Data to show" offers T1, T2, T3 and "Plot to show" offers T2, T3 although the audit is off; the shipped files themselves were not launched); `config/app_features/pipeline-exploration-simple.yaml` 7-25, `web-demo.yaml` 8-21; ADR-099 "alternatives not chosen" | for any demo on these two features the plots can be changed unrecorded. See 3.7 for options |
| F9 | **Wording drift survived the consistency pass:** `home_audit_steps.md` still says "Audit workspace" (1x), "workspace" (2x), "rebuilt" (1x); the diagram `HOME-VIEW-MATRIX` is titled "What Exploration and the Audit workspace show and do" in the model; the word "never" is in 16 places of 8 HOME diagrams (EXPLORATION 3, VIEW-MATRIX 2, AUDIT-FLOW 3, AUDIT-EFFECT 3, AUDIT-CACHE 2, AUDIT-LINEAGE 1, AUDIT-COMPONENTS 1, UI-HOME-EXPLORATION 1) | verified: term scan of the design files and of `docs/UML/app.mdj` | breaks your UML rule; to fix in track D. Statements about built behaviour ("never exported" for preview filters) are true today; those about the target are not |
| F10 | The data check and `test_render_every_plot` passed with wrong figures (recipe review); the two generated recipe audits pass and cannot see a many-to-many join or an ignored plot key | verified: recipe review, #66, #68, #71 | the safety net is the canaries plus pictures looked at, not green tests alone |
| F11 | **Property tests bring randomness.** D9 (CONFIRM) proposes `hypothesis`; random generation without a fixed seed adds the kind of intermittent failure we are chasing in the browser gate (#72) | reasoned: Hypothesis is seeded per run unless `derandomize=True` or a fixed seed is set | if adopted: derandomized or fixed seed in CI, the seed printed on failure |
| F12 | Build time is not a constraint at this scale: the slowest plot-target collection builds in 0.3 s (Abromics), 203,146 rows in 0.2 s (figshare) | verified: `forensics_data.py` | exact trial computations (D4, question 8) are affordable here; production size **assumed unknown** |
| F13 | Browser gate flakiness: timing races in the tests under load, **not** caused by the 2026-11-11 changes (the old code fails as often under the same load) | verified: controlled experiment, section 5 | the UI parts of the build are verified with a gate that gives false alarms; hardening proposed in #72 |
| F14 | **"Raw has no plot (NA)" is ambiguous.** The decided texts say, in three places, that Raw has no plot: `home_preview_filters.md` 3 ("Raw has no plot (NA)"), the box of `UI-HOME-EXPLORATION` ("Raw has no plot (NA)"), and the PLOT row of `HOME-VIEW-MATRIX` ("NA: no plot on T1"). Today the plot stays on screen when "Data to show" is Raw (ADR-086: plots never show T1, they show T2) | verified: the three texts (pictures read); ADR-086 | the target Data toggle controls the plot area too: when the user picks Raw, does the plot area go empty, or does the Result plot stay? Not decided in words; it changes the screen of every feature |
| F15 | **Level 3 keeps two implementations in the decided design.** Level 3 steps "run on the plot frame at render time" (not stored); the forked recipe carries levels 0-2, and for the export the translator still forks per plot and appends the level 3 steps as recipe actions (`home_audit_steps.md` 7.6; brief S6 lists the four consumers of the filter engine) | verified by reading | the #62 problem (figure and bundle disagree) can come back for level 3; the safeguard is WP1's equivalence test, not the design |

| F16 | **WITHDRAWN 2026-11-12 (Eve, P1): audit mode requires export, Compare and sessions, so Rule 6 is right and nothing contradicts; I had misread "Off: the audited plot uses the full width" (the toggle, not the flag). The facts below stay as a record.** ~~The validator contradicts a decided text.~~ `AppFeaturesValidator` Rule 6 makes the audit flag without comparison, sessions and export a **fatal** error; the decided design allows audit mode without Compare (`home_audit_steps.md` 3). Of the 32 combinations of the five gating flags: 11 clean, 7 warn only, 14 fatal; with interactivity on, one combination with the audit on is legal. The two rules the design decided (comparison needs the audit; the audit needs its `audit_stack` slot) are not built | verified: ran the real validator on all 32 combinations and the CLI on a file for "audit without Compare" (fatal, Rule 6) | decides which configurations can exist and be tested; options R-a, R-b, R-c in the gating paper, section 5 |

## 2. What holds (checked again, no change needed)

Original data is never touched; "informs, warns, lets the user decide; blocks only the technical"; early insertion on **every ingredient that has the
key** (7.5) is the right rule and also covers joins that could bring a sample back from the right side (shipped recipes use only `left` 24x, `inner` 5x and one `join_filter`; the action's options also include outer, semi, anti and cross);
key mapping by declared keys plus join steps, never by column names (`VirulenceFinder.metadata_sample_material` shows why); the audit stays out of the original anchors; filtering before an aggregation is a recipe change, not an audit step (`home_audit_steps.md` 5).

## 3. Decisions: status, options, consequences by point of view, recommendation

Order: the structural choices first (they decide the size of the build), then the numbered questions of the reading guide, then the new ones. "Reversibility" says how hard it is to change your mind later.

### 3.1 The size of the first audit build: cut or full (status: on the path, reading guide 6; the cut is MINE as a plan)

| Option | S | DS | Dev | QA | Ops / N |
|---|---|---|---|---|---|
| **(1) Cut first** (`outdated/home_audit_first_cut.md`), then the full design | safer figures sooner (NA, entities, warnings, reasons, export review); "remove everywhere" stays manual | the statistics risk (C1) is warned, not removed | small pure modules reused later; avoids the frozen files | each piece has an oracle and canaries | no new cache; users see little new. **My view, Compare and "Plot to show" stay** (reading guide 5): see 3.7 for the two features without the sandbox flag |
| **(2) Full design straight** | the structural problem of #60 solved | entity removal at the sources recomputes statistics correctly | large (F7), screen last, needs the overlay or E (3.2) | most paths to test | new cache and dialogs to learn |
| **(3) Engine fixes and Exploration only, audit unchanged until after the demo** | the old audit stays, with its known limits | #62, #61, #63-info fixed; the rest warned in the help | smallest | least to retest | the demo shows the old audit |

**Recommendation: (1).** It fixes what is verified wrong now and adds the safeguards with the best value per effort; every piece is a pure module the full design reuses (compatible with brief S5). **Reversible:** yes (each piece alone).
**What would change it:** if the demo must show "remove a sample everywhere", (2) with the narrow reach of 3.3 and engine E; if there is no time before the demo, (3).

### 3.2 How audit data is computed (status: the mechanism is DECIDED (7.1-7.3); E is MINE and reconsiders it, R1)

The decided design computes audit stages by an **overlay inside the orchestrator** and stores them in a **separate audit cache with new chained keys and a canonical hash**; separately it generates a **forked recipe** for the export (7.6, ADR-099 point 8). E uses the forked recipe for the stages that the overlay would compute (levels 0-2).

| Option | S | DS | Dev | QA | Ops |
|---|---|---|---|---|---|
| **A. As decided** (overlay, audit cache, new key function, canonical hash) | same result | same | new cache and keys, edits in `orchestrator.py` and `cache_keys.py`, a compiler keeps the hash and the executed list the same | new tests for keys and cache (listed in 14) | finer reuse (a level 2 step reuses the original T1) |
| **E. Forked recipe** (MINE): build the forked recipe from the steps, write it into `audit/<session_key>/`, run a **second `DataOrchestrator`**; ADR-089 keys | the exported recipe is what produced the figure (for levels 0-2) | figure = bundle by construction for levels 0-2 | much less new code; the two frozen files stay frozen; the two translator modes are needed for the export anyway | the key and the executed steps are one object; `test_cache_keys` already covers the keys | **coarser**: an added join changes the tier-1 material, so the audit rebuilds tier 1 (0.3 s here; production size unknown) |

**Recommendation: E after a spike, but your decision, because it replaces a decided mechanism.** The decided *properties* can all be kept (table in 3.2b). **Reversibility:** high (the interface is "recipe in, frames out").

### 3.2b The cheaper engine (E) explained: what it gives, what it costs (measured 2026-11-12)

**What E is.** Today a recipe is a file; the orchestrator turns it into stored tables (T1, then T2) and every plot reads T2. E treats an audit state the same way: a copy of the recipe plus the steps, written as a file in an audit folder and built and stored by a second `DataOrchestrator`.
"Cheaper" means less new code, because the machinery exists and is tested. **What was measured:** the proof of concept and the numbers below use the **plot-level fork**, which is the mode the export already has. The two modes HOME needs (shared late = level 2, early at the sources = levels 0-1) are **new code and not measured**; the early mode rebuilds tier 1 of every collection it reaches.

**Measured** (`tmpAI/architect/engine_cost.py`; one plot-level filter per recipe; second orchestrator in a temporary folder; load average 2.9):

| Recipe and plot | T2 rows, original -> audit | Equal to a direct Polars filter of the original T2 | Original cold / warm | Fork cold / warm | Fork's stored stages | Recipe file |
|---|---|---|---|---|---|---|
| ST22 `qc_reads_horizontal_barplot`, `sample_id != <one id>` | 42 -> 41 | yes | 0.09 / 0.25 s | 0.08 / 0.01 s | 2 files, 0.06 MB | 15 KB entry file -> 42 KB (one resolved file) |
| Abromics `abromics_st_by_country` | 342 -> 335 | yes | 0.05 / 0.00 s | 0.04 / 0.00 s | 2 files, 0.01 MB | 3 KB -> 10 KB |
| figshare `plot_A_phenotype_bar`, `host_animal_species != 'Bos taurus'` | 203,146 -> 151,569 | yes | 0.16 / 0.07 s | 0.14 / 0.05 s | 2 files, 0.28 MB | 3 KB -> 8 KB |

In all three the tier-1 key of the fork differs from the original (verified), so an audit never reuses or overwrites a stored stage of the original. Timings are noisy at this size: read them as "all below 0.3 s", not as a ranking. The builds read the shipped test data; **production size is not known.**

**The decided properties, kept or changed by E:**

| Decided property (source) | With E |
|---|---|
| Own folder `audit/<session_key>/`, never in `anchors/` (7.1, 7.3) | kept |
| Chained keys; the key is stored in the file and compared on read (7.2; ADR-089 already stores it in the Parquet metadata) | kept; the keys are ADR-089's `tier1_key` and `tier2_key` of the forked recipe, not a new function |
| A canonical hash of the operations that will run; the same code produces the hashed list and the run (7.2) | kept in spirit: the resolved forked recipe is both what is hashed and what is run. To check in the spike: reason, initials and date stay out of the hash (they are not part of the translated actions: reasoned) |
| A level 2 step changes only the T2 key and reuses the T1 stage (7.2) | **changes:** a join added to the recipe changes the tier-1 material (`tier1_material` strips only plot sections and tier-2 steps), so the audit rebuilds its tier 1 and shares nothing with the original's stored stages |
| N = 5 states, oldest removed, never the one in use, recompute when missing, removed when the recipe or data change (7.3) | kept; to implement by removing audit directories (this is the clean-up rule; the design has it) |
| Trial computation stored under the would-be key; Apply adopts it (6.5, CONFIRM) | possible: build the would-be fork in the audit folder and adopt it on Apply |
| Level 3 runs on the plot frame at render time, not stored (7.6) | **unchanged by E**, so level 3 keeps two implementations (F15) |
| `orchestrator.py` and `cache_keys.py` change (14) | **avoided:** the orchestrator is used as it is, on another recipe |
| Early insertion at the sources inside each reached collection (7.5) | to build as a translator mode; untested |

| | Pros of E | Cons of E |
|---|---|---|
| Correctness | for levels 0-2 the figure, the table and the export are one computation; an engine bug is fixed once | an engine bug is inherited by the audit (true for any design), so #61, #62 and #63 come first; level 3 is not covered (F15) |
| Size of the change | much less new code; the recipe cache is keyed by absolute path, so a second orchestrator does not collide with the first (`cache_keys.py:179-205`, verified); the translator modes are needed for the export anyway (F4) | the two HOME modes are new and untested; only the plot-level mode was run |
| Cache and disk | invalidation by construction; own folder; 2 files per state, 0.01 to 0.28 MB here | coarser rebuild (above); each state is a resolved recipe copy; the N = 5 removal must be written (the design has the rule) |
| Checking and export | the bundle can carry the audit recipe, runnable with the debug scripts (`debug_assembler.py`); the oracle is a direct Polars filter (what the proof of concept used) | `id` must equal the file name (ADR-092): ids must be generated and unique; the session key and the export key check must name the audit state |
| Security | filters translate to named actions, no code | the audit state is a recipe and recipes are code (architect review AR1); the kinds in audit must be limited (N2) |

**What E does not solve:** the scattered view logic (AR2), the size of the handlers (AR3), the NA rule (3.4), many-to-many joins (#68), level 3 (F15).
**The spike before deciding** (one session, no UI): (1) the early key-exclusion mode and the shared late mode as translator modes, run on all 7 shipped recipes with the oracle "same rows as filtering every ingredient that has the key"; (2) measure the rebuild on the largest recipe;
(3) the session key and the export key check with an audit state; (4) the N = 5 removal; (5) the trust check (N3).

### 3.3 Reach and stage (status: DECIDED = selector in the dialog, nothing preselected, stage from the kind, early at the sources for key exclusion; CONFIRM = three options with a checklist (question 6); OPEN = stage = the table the user looks at (question 1))

| Option | S | DS | Dev | QA | N |
|---|---|---|---|---|---|
| **A. As designed:** kind x three reaches (selected plots with a checklist; all plots that use the same table; every plot in the project) x levels 0-3 | most expressive; "same table" is the hardest sentence (open wording, section 17) | level 2 (a value filter after an aggregation) is the statistically weakest | two new fork modes, coverage check, overview | most paths | three choices and a checklist |
| **B. Two reaches** (MINE, R2): "this plot" (level 3) and "the whole project by sample ID" (level 0); value filters and drops only at plot level | covers the real job (bad sample out everywhere) with one clear choice | entities removed at the sources; no filter on an aggregate | one new mode (early, key only) plus what exists | about half the paths | two plain choices |
| **C. Plot level only** (the cut) | "everywhere" stays many per-plot steps | the statistics risk is warned, not removed | none | minimal | a hidden limit, stated in the help |

**Recommendation: B for the first full audit, C as the stepping stone**, **A when you want it** (B is a subset of A, so nothing is thrown away). B reconsiders a CONFIRM item (R2). The verified motivating flaw is key exclusion; level 2 value filters are the weakest statistically and the "same table" reach is the hardest to explain and test.
**Reversibility:** high. **What would change it:** a real lab need for table-level filters (usually a recipe change, tier 1). **Needs:** the canary of F1 (built).

### 3.4 NA rule (status: DECIDED in principle, `home_audit_steps.md` 19 "never silent"; OPEN: the default of the implementation and where the rule lives)

The rule as written (decided): NA is a visible, selectable value; "remove" filters keep NA unless selected; "keep" filters drop it unless selected; comparisons drop NA unless "keep rows with NA" is ticked; the dialog always says how many.
What is not settled: how it reaches the 8 registered actions without changing existing recipes (issue #63, brief WP3b: BLOCKED). Two ways:

| Option | S | DS | Dev | QA | Ops |
|---|---|---|---|---|---|
| **A. An optional `na` parameter on the 8 actions**, default = today's behaviour, passed explicitly by the audit, VizFactory and the translator (the plan in the comment on #63) | "remove Norway" keeps unknown-country rows | standard for comparisons | closest to the data; 8 places to change and test; Blueprint schemas retested | matrix operators x null/NaN (the table of #63), canary `QA_ST_with_NA` | existing recipes unchanged |
| **B. The rule only in the step compiler**, which emits expressions that handle NA (MINE) | same | same | one place; needs an expression-based filter action, which the allow-list of N3 can judge | the same matrix on one module | the registered actions stay frozen |
| **C. Keep today's semantics, information only** (WP3a) | surprising rows vanish but are counted | same as today | none | counts tested | none |

**Recommendation: C now (WP3a, no decision needed), then A or B with the compiler.** The default for "remove" and for comparisons is already written in 19; only you can confirm it for #63. **Reversibility:** medium (the stored step carries the rule).

### 3.5 Event log (status: DECIDED in principle; the form, event-sourced D2, is CONFIRM; the option below that I add reconsiders it, R3)

Options: **A** event-sourced store, steps derived (D2); **B** step list plus a separate log (the earlier draft; the developer review rejected it: "can disagree"); **C** (MINE) additive fields on the step record (`created_at`, `removed_at`, `reason_category`, `acknowledged_warnings`), the log is the derived list, nothing is hard-deleted; **D** nothing (today: hard delete).
S - A and C both let the report list removed steps, D cannot. DS - attrition and overrides reportable with A or C. Dev - C is small (F5: the record is a `TypedDict(total=False)`, added fields are safe); A needs a new `schema_version` and a migration (D13); B has two stores. QA - A: replay properties (D9); C: "a removed step stays listed".
**Recommendation: C for the cut, A when the full design needs replay.** The step record of `home_audit_steps.md` 11 (id, kind, reach, level, targets, params, reason, initials, created_at; status computed) fits both. **Reversible.**

### 3.6 Keys (status: DECIDED, `home_audit_steps.md` 7.4 and 16; the reading guide still lists it as question 5: tidy one of the two)

Decided: declared `is_primary_key` plus the join steps, **inference as fallback**, read from the loaded dictionaries, no-key fallback to a row filter on a column the user picks. F6 supports it (declared keys only would switch sample exclusion off for 2 of 7 shipped recipes). Nothing to decide; to add (MINE, small): a recipe-validator **advice** "no key declared" and the docs line "declare `is_primary_key` on the ID column" (already in 7.8).

### 3.7 Without the sandbox flag, and the strip (status: the target is DECIDED; the interim is an OPEN question of the brief; R5 is MINE)

**Decided.** Plots change only through an audit step. Without the sandbox flag only Exploration exists. The strip is "Data: Raw | Result" in **every** feature; "Plot to show", My view and Compare are not in Exploration at all (they are replaced by audit mode, which exists only with the flag). Nothing here needs a new decision.

**What each screen is** (verified: the code of today, the decided texts and pictures):

| | Strip | Plot | Preview filters |
|---|---|---|---|
| **Today** (built, ADR-085/086/098), every feature with `interactivity_enabled` | "Data to show: Raw / Result / My view" and "Plot to show: Result / My view / Compare (if the flag)" (`home_theater.py:940-1008`) | follows "Plot to show"; the My view plot **is changed** by preview filters (`:478-490`) | table on every view; plot only on My view |
| **Target, features without the sandbox flag** (simple, web-demo) | "Data: Raw \| Result" only | always the recipe's Result plot (Raw: see F14) | table only |
| **Target, features with the flag, Exploration** | "Data: Raw \| Result" + the mode switch | the Result plot | table only |
| **Target, features with the flag, audit mode** | the mode switch; Compare on/off; **no "Plot to show"** | the audit plot (audit T3) | not applied (kept for when the user returns) |
| **Interim** (decided sequencing: the strip stays as built until audit mode exists; the WP4 package changes only the lists, not the strip) | as today | as today | as today, now per dataset |

**The catch (F8).** In the interim the two features without the sandbox flag keep a plot that changes with no reason and no record, against your rule. Question 3 of the brief ("Interim My view ... acceptable until audit mode replaces it?") was never answered. Options:

| Option | S | DS | Dev | QA | Ops / N |
|---|---|---|---|---|---|
| **(a) As planned:** nothing removed before audit mode; a help caveat | a viewer of these features can still change a plot unrecorded | a screenshot of a filtered plot has no record | no change | none | the demo caveat must be said aloud |
| **(b) An early slice for features without the sandbox flag only (MINE, R5):** hide My view, Compare and "Plot to show" when `t3_sandbox_enabled` is off, so the strip is "Data: Raw \| Result"; set `comparison_mode_enabled: false` in `pipeline-exploration-simple`; the features with the flag stay as built | your rule holds in every feature that has no audit | no plot can change unrecorded | small change in the header-strip code (frozen by S3, so it needs your explicit OK); it is **exactly the final screen of those features**, so the audit build does not undo it; the validator rules (decided) can come with it; `test_flag_matrix_doc.py` compares the doc matrix (row 128 of `rules_app_features_flags.md`) with the files, so the doc changes in the same commit | the masking tests and `test_every_app_features_starts.py` run for both features; F14 (Raw) must be settled first | users of these features get the final, simpler screen; their help line: "In this configuration filters change the tables; plots always show the Result." |
| **(c) The target strip for all features now** | not possible: in features with the flag, My view is where audited steps are made until audit mode exists | | | | rejected |

**Recommendation: (b) if the demo or any shared use runs on `pipeline-exploration-simple` or `web-demo`; otherwise (a).** It removes the one place where a feature with no audit lets a plot change, it is not work the audit design would undo (brief goal), and it is reversible. **Needs from you:** the yes (S3 freezes the strip), the answer to F14, and a note on the brief and on #56. Your answer "not active, hidden" fits (b), but you did not choose between (a) and (b), so I did not: this is question Q7 of `home_gating_and_test_configs_2026-11-12.md`, which also explains how (b) is gated and tested (a capability resolver and the `test-preview` configuration make it cheap and checkable).

### 3.8 The remaining numbered questions of the reading guide (status for each: CONFIRM / OPEN)

| # | Question | Options | Recommendation and why |
|---|---|---|---|
| 3 | Reason categories | free text / fixed list + text / configurable | fixed list (technical failure, contamination, duplicate, out of scope, outlier by value, other) + text, "outlier by value" flagged (the proposal of 19); configurable later (D7). A list makes the report groupable and costs one field |
| 4 | Figure caption "n = X" | off / optional / always | optional, off by default (as proposed), only for entity counts; always would stamp n of the wrong thing |
| 7 | Audit table selector (T1/T2/T3) | now / with the full audit / never | with the full audit (needs audit T1); not in the cut |
| 8 | Exact trial computation vs estimate | exact / estimate / exact with estimate fallback | exact with the "estimate only" fallback of 6.5 (F12: cheap here, unknown in production) |
| 10 | Lineage map | own HOME renderer / Blueprint's map / text chain | text chain (as drawn in the dialog) now, own plain renderer later (`home_audit_steps.md` 3: the cross-panel rule forbids HOME to mount Blueprint's panel) |
| 11 | First guard-rail list and thresholds | the list of 19 / fewer / more | the cut takes I1, I2, C1, C3, W4; thresholds (20 %, 3 entities) as settings; test the wording with 2-3 scientists first (warning fatigue, 20) |
| 12 | D1-D14 | each separately | now: D5 (pre-export review), D8 (honest wording), D10 ("N audit steps"), D13 (versions, partly there); with E: D3 becomes the generalised translator; later: D1 recipe graph (start as the key-mapping module), D4, D7, D11; D9 `hypothesis` only with a fixed seed (F11); D12 when data is large |
| 13 | Legacy names and legacy step types kept | keep / rename; keep types / retire | keep names plus a glossary line (a rename touches F7's references and saved sessions); for `developer_raw_yaml` see architect review N2 (R4) |

### 3.9 The recipe questions (from `recipe_review_st22_2026-11-11.md`; independent of the audit design)

R1 anchor: **(a)** virulence + MLST + metadata, no ResFinder (recommended: the plots read virulence, AMR has its own collection and heatmap; the canary shows the correct per-sample AMR count). R2 four samples without usable phenotype: **(a)** not plotted with a note "n = 38 of 42" ("0" would say "no resistance").
R3: keep the 2023-2025 filter and put the years in the MLST title. R4: decide `virulence_variants` facets with R1.

## 4. The recommended path in one table

| Step | What | Needs from you | Unlocks |
|---|---|---|---|
| 0 | Builders: WP1-WP9 as briefed (WP4 stays interim). The canary of F1 is done | nothing | the base |
| 1 | Answer the questions of the gating paper (Q1-Q8: hidden-not-greyed, gating mechanism, the companion rule, test configurations, the interim a or b, two small defects), and F14 (Raw and the plot) | about 9 answers, in that one file | a screen and a configuration model that follow your rule, and configurations the tests can use |
| 2 | Decide 3.1 (cut first), 3.4 (C now), 3.5 (C for the cut), 3.2 (E, as a spike, because it reconsiders a decided mechanism), and the architect review's N2-N6 | about 8 answers | pieces 1-7 of the cut |
| 3 | Spike: the two translator modes, the N = 5 removal, the trust check (list in 3.2b) | 3.2 yes | decision 3.3 with evidence |
| 4 | Decide 3.3 (B) and the rest of 3.8 | after the spike | the full audit plan |
| 5 | Fix F9 (wording, UML, "never") and the two files that disagree on keys (3.6) | your rule on built-behaviour "never" | consistent diagrams |

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

Production data size and the real cost of the early mode (the measured costs in 3.2b are the plot-level mode: all below 0.3 s on the shipped data); whether the early key-exclusion mode and the shared late mode work on every shipped recipe (neither was run);
that the two features without the sandbox flag behave as read in the code (they were **not launched**); who uses them and for which demo (3.7 depends on it);
usability of the warning texts (needs 2-3 scientists); the `hypothesis` seeding behaviour (taken from its documented defaults, not run); whether the reason, initials and date stay out of an E hash (reasoned, to check in the spike).
