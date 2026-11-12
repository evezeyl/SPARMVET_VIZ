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
| | W7 **data-agnostic** (Eve, 2026-11-12): the software is used for datasets other than bioinformatics; no field-specific word in the code or in fixed texts; domain words (the name of the entity, the examples) come from the recipe or the help |

**The problems, in the order we settle them** (details of P1-P4 in `home_design_first_roadmap_2026-11-12.md` section 3-4; the analysis behind each in `home_evidence/`)

| # | Problem | Status |
|---|---|---|
| P1 | Which kinds of configuration exist, and what depends on what | **DECIDED 2026-11-12 (Eve):** audit mode needs export, Compare and sessions (compare the effect, save unfinished work, export what is finished and verifiable); Compare needs audit |
| **P2** | **The Exploration screen.** Plot: **DECIDED 2026-11-12 (Eve)**: one plot, the Result, immutable, always shown (the Data toggle only changes the table). Notices: **DECIDED 2026-11-12** (three texts, in `home_preview_filters.md` 7 and `home_audit_steps.md` 3) | decided |
| P3 | Preview lists while audit mode is on | **DECIDED 2026-11-12 (Eve):** hidden, kept; the Filters panel and column control follow the mode; one candidate step previewed in the dialog, then Apply with a reason (`home_audit_steps.md` 3). Columns: same logic as filters (candidate drop, previewed in the dialog, then Apply) | decided |
| **P4** | **Export and session.** P4a (no audit): **DECIDED 2026-11-12** (same export without audit parts; preview never saved or exported; session = recipe and data reference). **P4b DECIDED 2026-11-12**: original and audited side by side for affected plots, labelled; audit tables only where a step changed; one tick "include recipe and raw data" (off, warning) | decided |
| P5 | Audit: where in the data processing a step goes | **DECIDED 2026-11-12** (Eve): written into `home_audit_steps.md` section 5a and ADR-099 point 12 (operation on data, tick boxes, earliest point that reaches no unticked plot, all-at-once key removal, no pinning, no hiding, four layers of information, uniform `label` and `description`) | decided |
| P6 | The NA rule and its defaults (question 2, #63) | **DECIDED 2026-11-12** (Eve): never silent; missing is a visible, selectable value in preview and audit; defaults as in `home_audit_steps.md` 19; the user and the recipe maker decide what missing means |
| P7 | Audit: reason, caption, tables shown, first checks | **DECIDED 2026-11-12**: reason = free text with a hashtag convention; caption in the report text, on by default, entity word from the recipe; tables shown = stage x version, T3 defined by the recipe, Result = the plot's own table, the recipe is as is (the audit only adds); first set of checks (`home_audit_steps.md` 3 and 19) | decided |
| P8 | The transition for features without audit | **WITHDRAWN 2026-11-12 (Eve)**: a configuration file only switches functionalities on or off; it does not change what we build. The design is the same in every configuration (Exploration = preview, one immutable Result plot; no "My view" or "Plot to show" anywhere). The configuration files are adapted at the end (stage 5): `pipeline-exploration-simple` gets `comparison_mode_enabled: false`; the web page configuration (`web-demo`, to be renamed `static-web`; the word "demo" is confusing) is to decide: fully static or Exploration only | withdrawn |
| **P9** | **Who may bring recipe text into the app (recipe text is code)** | **NOW** |
| later | Mechanism (stage 2): the audit engine, trial computation, event log, lineage map, D1-D14, architect findings N2-N6, legacy names (questions 8-10, 12, 13); then the build plan; then gating and test configurations | after P1-P9 |

## 0b. All the HOME working documents and their role (checked 2026-11-12)

| File | Role | Status |
|---|---|---|
| `spaces/HOME.md` | the canonical HOME design (CLAUDE.md 3.6: read before implementing) | **STALE** (2026-05-05): "audit always on, no opt-out", the old "T3 cascade rule" with retired flag names; no Exploration, no audit mode. To rewrite from the agreed design |
| `home_preview_filters.md` | Exploration design | agreed 2026-11-11 |
| `home_audit_steps.md` | audit mode design, v4, with the three reviews | decided in part; `[confirm]` items open |
| ADR-098 / ADR-099 (`architecture_decisions.md`) | what is built / the target | ADR-099 accepted in principle, not built |
| this guide | the order of work, the criteria, the problem queue and the 13 questions | entry point |
| `home_design_first_roadmap_2026-11-12.md` | the behaviour table by kind of configuration and the questions of P1-P4 | working document for stage 1 |
| `home_audit_review_agenda_2026-11-12.md` | the script of the review session | current |
| `home_evidence/` (forensics, architect review, gating paper) | analysis: what is decided, options with pros and cons, verified findings | evidence to consult per problem, not designs; the gating paper is paused |
| `home_audit_first_cut.md` | a smaller first audit version | PARKED (plan stage) |
| `../tasks/home_exploration_build_brief.md`, `../tasks/next_session_start.md` | instructions for the builders | **ON HOLD** until the design is agreed |
| `../tasks/test_plan_home_2026-11.md` | HOME test plan | valid for HOME as built; rewritten after the redesign |
| `../workflows/design_review_personas.md` | the review method | current |
| `../outdated/` | outdated plans, test notes and research, kept for history (index in its README) | OUTDATED |
| `docs/UML/diagrams/HOME-*`, `UI-HOME-*` | pictures | see section 4 |

**Not listed in CLAUDE.md:** none of the HOME design files above except `spaces/HOME.md` (stale). A session that follows CLAUDE.md alone would not find the design.

## 1. The idea in ten lines

1. **Exploration** (Raw or Result) is for looking. A preview filter changes the table only, is never saved or exported,
   is cleared when you change view. It never changes a plot.
2. **Audit mode** is the only way to change a plot, the data or the export. It needs a reason, it is recorded, it can be
   removed. The original data (original T1 and T2) is never changed.
3. A step has a **kind** (remove samples by ID | keep or remove rows by a value | remove a column), a **reach** (which plots)
   and a **stage** (where in the pipeline). The user picks the reach; the stage follows.
4. Audit data is **recomputed**, never copied, in a **separate cache**; a step is a list of existing recipe actions
   (the "compiler"), so the hash, the execution, the export and the lineage highlight all come from one place.
5. The **software informs, warns and lets the user decide**. Four levels: info, warning, confirm with a written reason,
   block (technical only). Everything shown, acknowledged or overridden is stored and exported.
6. The user sees **what a step touches before applying**: the chain original T1 > audit T1 > audit T2 > audit T3, the
   plots and tables affected, rows and entities before/after, a before/after preview of the plot, a read-only lineage map.
7. **No draft**: a three-step dialog (what, check, why), then Apply; removing a step is the undo. Before an **export** there
   is a review of every exclusion and warning.
8. Missing values are never silent ("NA" is a visible value). Rows are not samples: in a long table one sample has many rows, so a filter that removes 10 rows may remove 10 samples or only 1 (and a sample can vanish from a plot although only some of its rows were removed). The software therefore shows both numbers, rows and samples ("entities"), before and after a step.
9. The audit is for **publication-ready** figures. It can remove data that is really bad (for example poor-quality samples, from some or all analyses) or that makes no sense to show in a plot (for example a category with too few observations to compare), each with a reason, recorded as "data not shown". It is **not** for exploring data, and it is **not** meant to clean messy data (no mass homogenisation of non-standardised fields: that is a recipe change).
10. Build the risky logic first, **without a UI**, with property tests; the screen comes last.

## 2. Read in this order

| Step | File | What you get |
|---|---|---|
| 1 | this guide | the map |
| 2 | `home_preview_filters.md` | Exploration (short; agreed) |
| 3 | `home_audit_steps.md` sections 1-5 | rule, words, audit mode, kinds, reach and stage |
| 4 | `home_audit_steps.md` sections 18-20 | the scientist, data-scientist and developer reviews; guard rails; the changes D1-D14 |
| 5 | the diagrams in section 4 below | pictures; open them in StarUML for the full version |
| 6 | `home_audit_steps.md` sections 6-17 | the details, when you want them |

## 3. What to decide (my recommendation; what changes if you say no)

| # | Question | My recommendation | If no |
|---|---|---|---|
| 1 | **Stage and reach.** Stage = the table the user is looking at (T1, T2 or plot); reach depends on the stage; the numbers 0-3 become (stage, reach) | yes: values come from the table you look at, and a table step cannot be limited to some of its plots | keep levels 0-3 and "never early" for value filters; redraw nothing |
| 2 | **NA rule.** Missing values are a selectable value; "remove" filters keep NA unless selected; comparisons drop NA unless ticked; counts always shown | yes (never silent) | choose the opposite default; the rule stays visible either way |
| 3 | **Reason categories** (technical failure, contamination, duplicate, out of scope, outlier by value, other) + free text, "outlier by value" flagged in the report | yes | free text only |
| 4 | **Optional figure caption** "n = X after exclusions", off by default | yes (optional) | drop it |
| 5 | **Keys**: from `is_primary_key` (optional) + join steps, inferred if missing; read from the loaded dicts | yes | keys from join steps only |
| 6 | **Reach selector**: three options with a checklist of plots, in the dialog | yes | other wording |
| 7 | **Audit table selector** (audit T1 / T2 / T3 of the plot, read-only) | yes: lets you see where a sample was removed | drop it |
| 8 | **Trial computation** for the numbers and the before/after plot, reused by Apply | yes | estimates only (less exact) |
| 9 | **Event-sourced log** (only events are stored; the step list is derived) | yes | step list + separate log (can disagree) |
| 10 | **Lineage map** (read-only, own renderer in HOME; data from `blueprint_arch`) | yes | drop; the chain drawing remains |
| 11 | **Guard-rail checks** first list and thresholds (20 % attrition, groups under 3 entities) | yes, then test with users | change the list |
| 12 | **D1-D14** of section 20, incl. the dev dependency `hypothesis` and a policy block in the configuration | yes | smaller version, see section 6 |
| 13 | Keep legacy step types (`developer_raw_yaml`, `aesthetic_override`) and the `t3` names for now | yes | rename later as its own task |

Already decided by you: exploration vs audit split; audit mode replaces My view and Compare (Compare on/off); mode switch at
the left of the group-tabs row; reach selector in the dialog, nothing preselected; Apply and Cancel; initials; Revert to step N;
separate audit cache with chained keys; N = 5 as a setting; delete = recompute without it; atomic Apply; event log in
principle; recipe documentation; the software's role (inform, warn, let the user decide); comparison as a child of the
sandbox flag and the validator rules; "remove samples on a plot" is a plot-level row filter; filter values come from the data.

## 4. Diagrams (`docs/UML/diagrams/`, model `docs/UML/app.mdj`, package HOME)

| Diagram | Shows | Status |
|---|---|---|
| `HOME-EXPLORATION` | preview filters: staged, applied, clear on view change, why | **current target** |
| `HOME-VIEW-MATRIX` | Raw, Result and audit mode against table, plot, filters, columns, lists, Compare, export | **current target** |
| `UI-HOME-EXPLORATION` | the screen with audit mode off | **current target** |
| `UI-HOME-AUDIT` | the screen with audit mode on (three-step dialog) | **current target** |
| `HOME-AUDIT-FLOW` | what, check, why, apply, statuses, pre-export review, lineage map | **current target** |
| `HOME-AUDIT-GUARDRAILS` | the four levels and the check ids | **current target** |
| `HOME-AUDIT-CACHE` | original cache, audit cache, chained keys, limit, tests | **current target** |
| `HOME-AUDIT-COMPONENTS` | planned pure components and layers | **current target** (new, from the developer review) |
| `HOME-AUDIT-LINEAGE` | levels 0-3 on real ST22 collections | **pending decision 1** (red box says so) |
| `HOME-AUDIT-EFFECT` | what each level changes | **pending decision 1** (red box says so) |
| `UI-HOME The screen as built today` | the screen before the redesign | **as built; replaced when audit mode is built** |
| `SEQ-AUDIT` | exploration and audit as built today (picture embedded in `docs/appendix/data_lifecycle_theater.qmd`) | **as built; replaced when audit mode is built** |
| `COM-REACTIVE`, `C4-COMP-HOME` | reactive wiring and components as built (tier_toggle, applied_filters, audit_pending) | **as built; updated when built** |
| `UC-HOME` | use cases: four old ones are named "(replaced by audit mode, ADR-099)"; four planned ones added | **mixed, marked** |
| `STM-STAGE`, `SEQ-OPEN`, `SEQ-EXPORT` | stored stages, open a plot, export as built | **valid; gain audit companions when built** |

The audit script `audit_uml_model.py` checks tags against the repository only. It does **not** check that diagrams agree with
each other. That check is a review (`.claude/workflows/design_review_personas.md`, persona 1) and was done on 2026-11-11.

## 5. What is replaced when audit mode is built (and what is not)

Nothing is removed before then. Tracked as a task (`AUDIT-REPLACE-1` in `tasks.md`) so nothing becomes orphaned.

| Today | Replaced by | Not before |
|---|---|---|
| My view, Compare and "Plot to show" in the header strip | Exploration toggle (Data: Raw / Result) and audit mode (Compare on/off) | audit mode exists |
| Propagation dialog "this plot / all / all except" | the three-step dialog with reach and stage | audit mode exists |
| Per-plot audit steps (`t3_audit_steps_by_plot`) | steps with kind, reach, stage; old sessions map to plot-level steps | the new step record exists |
| Pending badge, filter inventory, Apply gate in the right panel | to review (open question 5 of the audit file) | audit mode exists |
| `extract_primary_keys` (returns an empty list on tiered joins) | key mapping (#61), **fix now** | not blocked |
| Integer threshold and NA behaviour of the filters | explicit rules (#62, #63), **fix now** | #63 needs decision 2 |

## 6. What can start now, and what cannot

**Can start now (needs no audit decision):** the engine fixes #62 and #61, and the information part of #63 ("N rows have no value...", behaviour unchanged); the preview changes of
`home_preview_filters.md` that do not touch the header strip (lists per dataset, clear on view and recipe change, panel
header, reset-to-all-columns, one operator vocabulary); the filter test suite with a data oracle and screenshots; the
related help text. Brief for the next session, with a safety protocol (baseline, one revertible commit per package, frozen files, compatibility with the audit): `.claude/tasks/home_exploration_build_brief.md`.
**Blocked until you decide:** the NA rule itself (#63 step 2): the audit engine and the registered recipe actions that the reproducibility export re-runs must change together, backward compatible. **Found while re-verifying:** today the figure and the reproducibility bundle give different rows for an integer threshold such as `>= 90.5` (#62), so WP1 also repairs that.

**Waits for your decision:** everything of audit mode (new panel, dialog, step model, cache, export review). Since the design
is large and the demo needs scientifically good software, a **smaller first audit version** is possible once you decide:
keep today's per-plot steps and add the safeguards that matter most (key fix, NA rule, integer fix, entity counts, the
population-statistics warning, the incomplete-exclusion check, reason category, event log, the pre-export review), and build
the cache, the lineage-level steps and the lineage map afterwards. Tell me if you want that cut written as a plan.
