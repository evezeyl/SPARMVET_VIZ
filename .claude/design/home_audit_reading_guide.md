# HOME filters and audit: reading guide (start here)

**Written for:** Eve, to re-read the whole redesign with a fresh mind. 2026-11-11.
**Companions (the real content):** `home_preview_filters.md`, `home_audit_steps.md`, ADR-098 (what is built), ADR-099 (the
target), issues #56, #60, #61, #62, #63, #64.

## 0. How we work on the HOME redesign (Eve, 2026-11-12)

1. **Design first.** Settle how HOME should work, so that it is both **science-sound** and **software-design-sound** (the criteria below). One problem at a time.
2. **Review and agree.** For each problem: the statement, the options with pros and cons seen from both sides, your decision, and then it is written into the design files (`spaces/HOME.md`, `home_preview_filters.md`, `home_audit_steps.md`, ADR-099). Nothing is built, gated or tested before its design is agreed.
3. **Then plan.** The mechanism (engine, keys, code structure), then a build plan in small revertible steps. Existing plans are ON HOLD until then.
4. **Then build, gate and test**, from the agreed design.

**Criteria every design decision is judged against**

| Science-sound | Software-design-sound |
|---|---|
| S1 the original data is never changed | W1 one source of truth for each rule |
| S2 nothing changes a plot, the data or an export without a recorded, reasoned, removable step | W2 looking (preview) and changing (audit) are two separate things |
| S3 the numbers are right: missing values, thresholds, samples counted as well as rows | W3 behaviour is specified per kind of configuration, so it can be tested |
| S4 the same data, recipe and steps give the same figure and export | W4 pure logic is kept apart from the screen |
| S5 the software informs and warns, the user decides; only the technical blocks | W5 a feature that is off is absent, not greyed (ADR-071) |
| S6 what you see is what is exported | W6 changes come in small, tested, revertible steps; no mechanism the design does not need |
| | W7 **data-agnostic** (Eve, 2026-11-12): the software is used for datasets other than bioinformatics; no field-specific word in the code or in fixed texts; domain words (the name of the entity, the examples) come from the recipe or the help. **Design documents too (Eve, 2026-11-12):** they lead with generic words (entity, attribute, population table) and put the field example in a marked example; `home_audit_steps.md` section 4 is done, the other sections still use field words and are swept section by section |

**The problems, in the order we settle them** (details of P1-P4 in `home_design_first_roadmap_2026-11-12.md` section 3-4; the analysis behind each in `home_evidence/`)

| # | Problem | Status |
|---|---|---|
| P1 | Which kinds of configuration exist, and what depends on what | **DECIDED 2026-11-12 (Eve):** audit mode needs export, Compare and sessions (compare the effect, save unfinished work, export what is finished and verifiable); Compare needs audit |
| **P2** | **The Exploration screen.** Plot: **DECIDED 2026-11-12 (Eve)**: one plot, the Result, immutable, always shown (the Data toggle only changes the table). Notices: **DECIDED 2026-11-12** (three texts, in `home_preview_filters.md` 7 and `home_audit_steps.md` 3) | decided |
| P3 | Preview lists while audit mode is on | **DECIDED 2026-11-12 (Eve):** hidden, kept; the Filters panel and column control follow the mode; one candidate step previewed in the dialog, then Apply with a reason (`home_audit_steps.md` 3). Columns: same logic as filters (candidate drop, previewed in the dialog, then Apply) | decided |
| **P4** | **Export and session.** P4a (no audit): **DECIDED 2026-11-12** (same export without audit parts; preview never saved or exported; session = recipe and data reference). **P4b DECIDED 2026-11-12**: original and audited side by side for affected plots, labelled; audit tables only where a step changed; one tick "include recipe and raw data" (off, warning) | decided |
| P5 | Audit: where in the data processing a step goes | **DECIDED 2026-11-12, revised the same day** (Eve): a step is an operation on data written at T1, T2 or T3, chosen by the user with the lineage shown; ticks state exactly what is written (safe mode); the only automatic placement is "remove from all tables"; the first version (tick boxes, earliest safe point) was replaced after testing (`home_audit_steps.md` 5a, ADR-099 point 12) | decided |
| P6 | The NA rule and its defaults (question 2, #63) | **DECIDED 2026-11-12** (Eve): never silent; missing is a visible, selectable value in preview and audit; defaults as in `home_audit_steps.md` 19; the user and the recipe maker decide what missing means |
| P7 | Audit: reason, caption, tables shown, first checks | **DECIDED 2026-11-12**: reason = free text with a hashtag convention; caption in the report text, on by default, entity word from the recipe; tables shown = stage x version, T3 defined by the recipe, Result = the plot's own table, the recipe is as is (the audit only adds); first set of checks (`home_audit_steps.md` 3 and 19) | decided |
| P8 | The transition for features without audit | **WITHDRAWN 2026-11-12 (Eve)**: a configuration file only switches functionalities on or off; it does not change what we build. The design is the same in every configuration (Exploration = preview, one immutable Result plot; no "My view" or "Plot to show" anywhere). The configuration files are adapted at the end (stage 5): `pipeline-exploration-simple` gets `comparison_mode_enabled: false`; the web page configuration (`web-demo`, to be renamed `static-web`; the word "demo" is confusing) is to decide: fully static or Exploration only | withdrawn |
| P9 | Who may bring recipe text into the app | **DECIDED 2026-11-12** (Eve): Import is gated by the configuration and for an authorised person only; warn and validate with the existing recipe validation plus a formula rule (`home_audit_steps.md` 11, ADR-099 point 14) | decided |
| P10, P10b, P11 | Findings of the independent review, the small items, the UML review, the nodes and keys, the hash model, the attrition proposal | **DECIDED or done** (see section 2); what remains is in section 2, O1-O8 |
| later | Mechanism (stage 2): the audit engine, trial computation, event log, lineage map, D1-D14, architect findings N2-N6, legacy names (questions 8-10, 12, 13); then the build plan; then gating and test configurations | after P1-P9 |

## 0b. All the HOME working documents and their role (checked 2026-11-12)

| File | Role | Status |
|---|---|---|
| `spaces/HOME.md` | the canonical HOME design (CLAUDE.md 3.6: read before implementing) | **REWRITTEN 2026-11-12** from the agreed design, each statement marked built or target; one place to read the whole of HOME |
| `home_preview_filters.md` | Exploration design | agreed 2026-11-11 |
| `home_audit_steps.md` | audit mode design, v4, with the three reviews | decided in part; `[confirm]` items open |
| ADR-098 / ADR-099 (`architecture_decisions.md`) | what is built / the target | ADR-099 accepted in principle, not built |
| this guide | the order of work, the criteria, the problem queue and the 13 questions | entry point |
| `home_design_first_roadmap_2026-11-12.md` | the behaviour table by kind of configuration and the questions of P1-P4 | working document for stage 1 |
| `home_evidence/home_hash_model_2026-11-12.md`, `home_attrition_report_2026-11-12.md`, `home_design_review_2026-11-12.md`, `home_uml_review_2026-11-12.md`, `home_where_to_remove_data_science_2026-11-12.md` | the hash model, the attrition and caption, the independent review, the UML review, the data-science analysis behind the placement of steps | evidence and decisions; the first two are decided |
| `recipe_review_st22_2026-11-11.md` (section 3b) | the test recipe defects and the AMR data scientist proposals R1-R4 (agreed) | applied by `RECIPE-ST22-FIX-1` |
| `home_stage2_mechanism_spec.md` | stage 2: the components, the data structures, the algorithms, the export legs, the build plan P0-P12 with the first milestone (the walking skeleton), the risks; draft for your reading | **new 2026-11-13** |
| `home_observations_and_future.md` | am I blocked (no), where my text is interpretation, my observations and risks, the future (other engines, non-tabular data, maps, interactivity) and the small engine registry | read when you want the honest state |
| `home_audit_review_agenda_2026-11-12.md` | the script of the review session | current |
| `home_evidence/` (forensics, architect review, gating paper) | analysis: what is decided, options with pros and cons, verified findings | evidence to consult per problem, not designs; the gating paper is paused |
| `home_audit_first_cut.md` | a smaller first audit version | PARKED (plan stage) |
| `../tasks/home_exploration_build_brief.md`, `../tasks/next_session_start.md` | instructions for the builders | **ON HOLD** until the design is agreed |
| `../tasks/test_plan_home_2026-11.md` | HOME test plan | valid for HOME as built; rewritten after the redesign |
| `../workflows/design_review_personas.md` | the review method | current |
| `../outdated/` | outdated plans, test notes and research, kept for history (index in its README) | OUTDATED |
| `docs/UML/diagrams/HOME-*`, `UI-HOME-*` | pictures | see section 4 |

**Not listed in CLAUDE.md:** none of the HOME design files above except `spaces/HOME.md` (stale). A session that follows CLAUDE.md alone would not find the design.

## 0c. The configurations as Eve wants them (2026-11-12; targets only, adapted at the end after the design is coded)

A configuration file only switches functionalities on or off for the user; it never changes what we build. The deployment configurations are easy to redo once the build exists, so the design comes first.

| Configuration | What it is | Target |
|---|---|---|
| `pipeline-static` | what runs at the end of a pipeline: no user interaction, no exploration; picks the data and runs the recipe automatically (one day perhaps producing an HTML page) | unchanged |
| `pipeline-exploration-simple` | Exploration (preview) only, no audit | **rename `pipeline-simple-exploration`**; audit off; Compare is only part of audit, so off here |
| `pipeline-exploration-advanced` | Exploration and Audit mode (with Compare, sessions, export), **no Test Lab, Blueprint or Gallery** | unchanged in content |
| `developer` | everything | unchanged |
| `demo-vetinst` | the web page configuration with some CSS adjustments, to show the flexibility | **rename `web-demo-vetinst`** |
| `web-demo` | the web page configuration (static or Exploration only: still to decide) | **rename (word "demo") when decided**; base of `web-demo-vetinst` |
| `standalone`, `qa`, any other | for testing; Claude's to remove or replace | replace by purpose-made test configurations when needed |

Compare is part of Audit mode and is on whenever audit is on (P1). Names use hyphens (validator rule). Task `CONFIG-REVIEW-1` in `tasks.md`.

## 1. The idea, as decided today (2026-11-12; replaces the ten lines of 2026-11-11)

1. **Exploration** (Raw | Result) is for looking: a preview filter changes the table only, is never saved or exported, is cleared when the view changes, and never changes a plot. The one plot is the Result, immutable.
2. **Audit mode** is the only way to change data, a plot or an export. Every change is a **step with one recorded reason** (free text, a hashtag convention), recorded, removable. The original data is never changed.
3. **Every plot has a T3, every table a T2**; T1, T2, T3 are defined the same way (an ordered list of steps; empty means equal to the previous node). A step is a **filter on a field or a drop of a column**, written at the places the user ticks (T1 or T2 of a table, or T3 of a plot); the lineage shows every node where the field exists; the key is information (counts, suggestions, the join-break warning), not mechanism; there is no automatic placement. The dialog shows the lineage backwards to the roots and forwards to every descendant; each place is a tick line that states exactly what is written (safe mode).
4. The audit is **the original recipe plus steps written into its own lists** (the audit recipe, exportable and re-runnable); audit steps are filters, drops and removals by key; a recipe maker may use any action in T3 and is responsible for good practice.
5. The software **informs, warns and lets the user decide**: three levels (info, warning, block, technical only). Missing values are a value: "not x" keeps them, "only x" and comparisons remove them, always counted and reported.
6. **Attrition per step**, derived and never stored: it starts at the source population (every unit of the population table), lists the recipe's own row-removing steps, then the audit steps, each with before and after; the figure caption is composed from it, in the entity's own word (declared in the recipe).
7. **Keys**: a series of labelled parts (`E . rC . dC . [a1] . [s2] . [a2] . [s3] . [a3]`), per collection, empty parts left out; whole-recipe hashes identify the project state and never decide what to rebuild (`home_evidence/home_hash_model_2026-11-12.md`, diagrams `DM-KEYS*`).
8. **Export** is one bundle: audited plots, the original Result plot for each really affected plot, original and audit data, the steps with reasons, the exclusion list, the attrition table, the verification legs; one tick adds the recipe and raw data. **Import** is gated by the configuration and validated.
9. **Every table has T1, T2 and T3, with or without a join** (empty = the previous node, a dataset plotted directly is a collection). **Everything written in a recipe is executed or the recipe is rejected with the reason**: HOME rejects at the load gate, BLUEPRINT reports and never blocks building (empty placeholders accepted).
10. Audit is for **publication-ready** figures (data that is really bad or makes no sense in a plot, with a reason); not for exploring, not for mass cleaning.
11. Build order: design, review, mechanism and build plan, code (tests adapted first), configuration and gating last.

## 2. Decision register (counted 2026-11-12)

**Decided: 47 items, counted by this grouping (A 8, B 15, C 4, D 8, E 4, plus O1-O5, O7, O8 and the principle of O6 confirmed by Eve on 2026-11-12; another grouping gives another number).** (A) Behaviour: P1-P7, P9 (P8 withdrawn). (B) Audit model: the T1/T2/T3 model and the nodes in the recipe file; where a step is written; ticks as safe mode; "remove from all tables"; remove by attribute (select with the filter, remove by key); one reason per action; three levels; attrition from the source population; caption; exclusion list; first set of checks; affected plot by content; the exact checks after Apply; the NA meaning. (C) Recipe format: `label` and `description` everywhere and the advice that explains why; the `entity:` declaration; limits of the first version (one key family); **the container forms of ADR-041 enforced everywhere (a dictionary for keyed definitions, a list for ordered ones, flat fragments), with a message that shows the corrected text, in the app and in the tests** (recipe spec 4c; Eve 2026-11-13; added after the count). (D) Architecture: the recipe graph in `libs/utils`, Blueprint's navigator rebuilt on it; the hash model (series, precise parts, full-content data hash once per session, record hash, retire `decision_hash`, drop the plot input key). (E) Rules of work: correct wrong recipes (no shims), complete steps, tests adapted first, data-agnostic. Where written: sections 5a, 4, 11, 19 of `home_audit_steps.md`, ADR-099 points 10-16, the hash model document.

**Still to decide (the real remainder):**
| # | Decision | My recommendation | Needed for |
|---|---|---|---|
| O1 | Loader and validator roles | **DECIDED** (Eve, 2026-11-12) | - |
| O2 | The read-only popup per node, kept open while the user looks | **DECIDED**; the mechanism (pinned panel) is for stage 2 | - |
| O3 | The audit step kind `developer_raw_yaml` | **DECIDED: remove** (task `AUDIT-RAWYAML-REMOVE-1`) | - |
| O4 | Permission to change `libs/transformer` | **DECIDED** (tests first) | - |
| O5 | Rule texts | **DECIDED and edited** (Tier 1 dependencies in `rules_runtime_environment.md`; the T3 sentence in `ui_implementation_contract.md`) | - |
| O6 | The node popup and the project overview: **DECIDED a popup in its own window**, built as a pure content function so a panel can replace the window later. **The right panel is kept for the audit steps** (Eve, 2026-11-13); its content is in `spaces/HOME.md` Open Questions, to confirm | partly decided | UI-HOME-AUDIT |
| O7 | The **step compiler** (defined in the vocabulary of `home_audit_steps.md`: it turns a user's step into recipe actions in the right list of the audit recipe; the generalised `t3_translator`), the event log, the pre-export review gate, D1-D14 (trimmed) | **accepted** (Eve); the specification is written in stage 2 | the build plan |
| O9 | Rename the recipe field `is_primary_key` to `is_entity_key` (a primary key is unique, an entity key repeats in long tables); warn first, refuse later | yes, at the recipe-format stage | clarity |
| O10 | The engine declaration: **DECIDED** (`data_engine`, `plot_engine`, required, unknown = failure; overrides later, 5a point 21) | - | recipe format |
| O11 | From Eve's review of `spaces/HOME.md` (2026-11-13): **DECIDED** the data selector T1 \| T2 \| T3 (the end of "Raw"), the import classes (an invalid recipe or a bundle of another app version blocks; environment legs inform; a bundle that differs from its recorded hashes needs an acknowledgment, to confirm at export build), the right panel (kept, node shown per step, slightly wider, adjustable width). **Also decided (2026-11-13):** the copy of the recipe is the source of truth of the audit steps, and its original steps cannot be modified (5a point 22). **Also decided (2026-11-13):** the double selector for the source data (Source | T1 | T2 | T3 with a dataset dropdown) and the lineage popup as the navigator of every node. **Nothing is left to decide for the HOME design except the details of the right panel, with the screen.** Requirement added: filters on every content type (`FILTER-DTYPES-1`) | - | the screen redraw |
| O8 | Configuration stage | **DECIDED** to leave it to the end (`CONFIG-REVIEW-1`) | - |
So **nothing is waiting for you now except the review of the text; the right panel is decided at the screen redraw (O6), and the compiler is specified in stage 2 (O7).**

## 3. The path to the first code (what stands between us and building)
1. **Your answers** to O1-O5 (a few minutes).
2. **Your review of the design text.** Reading list, in this order (each was changed or added during 2026-11-12; nothing is waiting for a decision while you read, mark what you disagree with):
   1. `spaces/HOME.md` (new: the whole of HOME in one place, built or target);
   2. `home_preview_filters.md` sections 2, 3, 6, 7 (Exploration);
   3. `home_audit_steps.md`: section 2 (vocabulary, step compiler), 4 (the two kinds of step), 5a points 3-20 (the mechanism, nodes, keys, shapes, fail instead of warn, the Blueprint boundary), 9 (drop), 10, 11 (reason, export, import), 16, 19 (levels, missing values, attrition and caption);
   4. `home_evidence/home_hash_model_2026-11-12.md` with the diagrams `DM-KEYS`, `DM-KEYS-CHAIN`, `DM-KEYS-USE`, `DM-KEYS-EXPORT` (`docs/UML/diagrams/`);
   5. `home_evidence/home_attrition_report_2026-11-12.md`;
   6. ADR-099 points 10-16 in `architecture_decisions.md`;
   7. `home_evidence/home_uml_review_2026-11-12.md` (which diagrams are outdated) and `recipe_review_st22_2026-11-11.md` section 3b (the recipe proposals);
   8. the planned terms in `docs/user_guide/glossary_and_feedback.qmd`.
3. **Documents I rewrite from the agreed text**: `spaces/HOME.md` (done 2026-11-12) and the UML redraw of the diagrams marked in `home_evidence/home_uml_review_2026-11-12.md` (task `UML-HOME-REDRAW-1`).
4. **Stage 2, the mechanism and the build plan** (draft written 2026-11-13: `home_stage2_mechanism_spec.md`): the recipe graph specification (`RECIPE-GRAPH-UTILS-1`), how steps are written into the audit recipe, the keys per node (`KEYS-NODE-1`), the loader and validator (`UNKNOWN-KEYS-1`, `ENTITY-DECL-1`), the engine path for T3; a build plan in small revertible packages, tests adapted first (`TEST-ADAPT-1`, `TEST-ORDER-1`).
5. **First code, in this order** (each package: tests that fail for the right reason first): the missing-value rule `NA-RULE-63`; unknown keys; the recipe graph in `libs/utils`; keys per node; then the audit pieces; the recipe fixes `RECIPE-ST22-FIX-1` run in parallel because they only need descriptions and explicit missing-value steps.

## 4. Diagrams (`docs/UML/diagrams/`, model `docs/UML/app.mdj`)
| Diagram | Status |
|---|---|
| `DM-KEYS` (general), `DM-KEYS-CHAIN`, `DM-KEYS-USE`, `DM-KEYS-EXPORT` | **new 2026-11-12, current target** |
| `HOME-AUDIT-CACHE`, `EXP-MODES`, `STM-STAGE`, `SEQ-EXPORT` | updated 2026-11-12 for the keys |
| `HOME-EXPLORATION`, `HOME-VIEW-MATRIX`, `UI-HOME-EXPLORATION`, `UI-HOME-AUDIT`, `HOME-AUDIT-GUARDRAILS`, `HOME-AUDIT-COMPONENTS`, `UC-HOME` | partly outdated (details in `home_evidence/home_uml_review_2026-11-12.md`); redrawn after your review |
| `HOME-AUDIT-LINEAGE`, `HOME-AUDIT-FLOW`, `HOME-AUDIT-EFFECT` | **contradicted** (they show the replaced level model); redrawn |
| `UI-HOME` (as built), `SEQ-AUDIT`, `COM-REACTIVE`, `C4-COMP-HOME`, `SEQ-OPEN`, `SEQ-LAUNCH` | as built; replaced or updated when built |
The audit script `audit_uml_model.py` checks tags against the repository only (0 discrepancies on 2026-11-12); that diagrams agree with each other is a review.

## 5. What is replaced when audit mode is built (unchanged; task `AUDIT-REPLACE-1`)
My view, Compare and "Plot to show" in the header strip; the propagation dialog; per-plot audit steps (`t3_audit_steps_by_plot`, old sessions map to T3 steps); the pending badge, filter inventory and Apply gate of the right panel (O6); `extract_primary_keys` (fixed with the graph, #61); the integer-threshold and missing-value behaviour of the filters (#62 and #63, `NA-RULE-63`). Nothing is removed before audit mode exists.

## 6. The earlier "13 questions" (2026-11-11), kept for history only
They are answered or replaced: stage and reach (replaced by the T1/T2/T3 model), NA rule (decided), reason categories (replaced by free text), caption (decided, on by default), keys from `is_primary_key` (decided, with the recipe graph), reach selector (replaced by ticks), audit table selector (tables shown by stage and version), trial computation (one candidate step previewed in the dialog), event log, lineage map, guard-rail checks (first set decided, three levels), D1-D14 (O7), legacy step types (O3).
