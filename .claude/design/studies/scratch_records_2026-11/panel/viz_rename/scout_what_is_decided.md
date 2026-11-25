---- FULL FILE TEXT ----
Summary (five lines):
1. The rename of the plot components is DECIDED in principle: D-0091 (plotnine_ / modif_ / step_ prefixes, old names refused, migration script) and D-0092 (field exact/modified/own kept, prefix-equals-field test). Nothing is renamed; the registry has no prefix in code.
2. Decided with no open point attached in any record I read: D-0092 (field plus test) and the prefix of the 123 exact components (plus the 31 modified ones outside the 15 of Q6). The rename itself is gated by D-0091's own evidence ("the impact list comes to her first") and tasks.md:387 ("starts only after Eve has seen the impact list"); Q1 (fingerprint of converted recipes) is open for every recipe.
3. Open for her: impact document Q1 to Q10 (section 8); FOR_EVE B8 Pt11 (CONFIRM), Pt12 to Pt15 (OPEN); B9 Pt16 (stat_summary, OPEN); Q6 (15 objects that plotnine cannot add to a plot) and Q7 (guide_label) are open too.
4. Built today: a decorator with a `plotnine` field in ui_schema (registry.py:44-84); a read-only rename-table script; an audit test that runs plotnine; 37 config recipes and 34 gallery recipes name a component (block form, my count).
5. Records that disagree or are unclear: D-0091 "no old names accepted" vs impact plan step 1 "old names still working" (impact line 397); tasks.md:386 says V1-B-AUDIT OPEN while tasks.md:442 says the audit is DONE; FOR_EVE B8 cites tasks.md:447 for "fixed and tested", but that line is TWO-RECIPE-NAMES-1 (the words are at tasks.md:452). Nothing in the impact document says she must read it; the only "read first" sentence is in FOR_EVE B8 (tasks.md:93 of that file), written by an agent. Records say "seen", not "read".

Labels: verified = read at file:line in this run; reasoned = my inference from those reads; "impact doc says" = a figure I did not re-run.

## 1. Ledger lines (`.claude/knowledge/decision_ledger.md`)

Columns: number, date, area, taken by, status, relation, decision (word for word), evidence (first 200 characters; short ones whole).

- **D-0051** (line 80; date field 2026-11-15, evidence says decided 2026-11-14), plots, EVE, DECIDED. Relation: "replaced in part by D-0091". Decision: "V1-10 as recommended: registry field exact/modified/own, no rename; exact = proved equal; parameters read from plotnine; one strict rule set; full check at HOME; silent paths become errors; one error form; factory refuses an engine it lacks; honest parity list, both spellings; 194 old test recipes dropped (Eve)". Evidence: `same turn: "V1-10 ok" (ADR-106 "DECIDED 2026-11-14"). The part "no rename" is replaced by N36 (11-15). | L49`.
- **D-0091** (line 120; date 2026-11-15), plots, EVE, DECIDED. Relation: "replaces in part D-0051". Decision: "Plotnine names follow the Polars procedure: a true plotnine equivalent is `plotnine_<name>`; a documented change is `modif_<name>` with the exact one registered next to it; a composite is `step_<name>`; the 22 names with no plotnine equivalent are looked up and renamed; no old names accepted, a migration script converts the shipped recipes and an old name is refused with "did you mean"; the registry audit comes first". Evidence (cut at 200): `"Same as we had done with polars: ... add plotnine_<action> on all true plotnine equivalent" (#1065, 17:34 UTC); "that is the price of transparency and reproducibility we have opted for ... we only accept new names - same procedure" (#1081,` ... evidence continues: "Reconsiders L49 (V1, "no rename"): this later line wins. The rename is not built: the impact list comes to her first (M129). | N36".
- **D-0092** (line 121; 2026-11-15), plots, EVE, DECIDED. Relation: "-". Decision: "The registering decorators keep the field that says exact, modified or own, under the new names, with a test that the prefix and the field agree". Evidence (whole): `"do not forget to add the fields in the decorators that register if pure or modified" (#1108, 17:42 UTC). | N37`.
- **D-0120** (line 149; 2026-11-16), HOME audit, EVE, DECIDED. Relation: "consistent with D-0102, D-0063; the record names no line it replaces". Not a rename line: the decision is "The audit does not change the steps of the plot: it changes the data before the plot, and the plot must read the data after T3 is applied. One day minor changes of the plot (for example a colour) may be implemented, not now. The plot recipe cannot be changed in the audit ...". Evidence (cut): `Y7 : the audit does not change the steps of the plot - it changes the data before the plot - but yes the plot must read the data after T3 is applied." (#1774)...`.
- **D-0036** (line 65; 2026-11-13), engine/steps, EVE, DECIDED. Relation "-". Decision: "DEC31-42: prefixes polars_/modif_/step_; a `polars_` action is exactly Polars; ... (Eve)". This is the ACTION prefix, not the plot components. Evidence: `SP 2.1 column "Eve" = 2026-11-13. DEC41 "other Polars methods deferred" was replaced by Eve on 2026-11-14 (ADR-100 note, M77 point 4: start now). DEC15/DEC39: report point 4.`
- **D-0037** (line 66; 2026-11-13), engine/steps, EVE, DECIDED (action prefix only): "`step_` is only `step_top_n_other` (Eve, relayed; later than DEC36)".
- **D-0058** (line 87; 2026-11-15), engine/steps, EVE, DECIDED (action): "`polars_join_where` becomes `modif_join_where`; the docs and the help say what it changes against Polars". Evidence: `"Those needs to be re-rewriten in the recipe I think that was the decision no ?" (#604); M81 "Confirmed by her". BUILT (min_items.py; ROW-ORDER-1, merge be08b169).`
- **D-0006** (line 35; 2026-11-07): names of app features, not components. Not used.
- Asked, not decided (ledger lines 246, 250): line 246 (A08) "M97: plan the visualisation refactor as a night queue; V1-V10 stand (restated, not new)." Line 250 (A12) "M106: N28 `stat_summary` and other components that take a function: NOT decided; investigation with a concrete example." `stat_summary` appears only there (verified by search).
- `guide_label` and `facet` (searched, case-insensitive): no ledger line found.
- The word "viz" also matched lines 159 to 192; I read them; none names a plot component.

**Question 1 answer (reasoned from the lines above).** D-0051 and D-0091 conflict on "no rename" (D-0051) against the rename (D-0091). They do not conflict on the field, which D-0092 keeps. A later line names the earlier one as replaced: D-0091's relation column says "replaces in part D-0051", and D-0091's evidence says "Reconsiders L49 (V1, "no rename"): this later line wins." D-0051's own relation column says "replaced in part by D-0091". D-0051's decision text still says "no rename" (the ledger rule is that nobody rewrites a line; decision_compliance.md section 5). D-0120 does not contradict either; it names no replaced line and is about the plot recipe in the audit.

## 2. Impact document (`.claude/design/viz_rename_impact_2026-11-15.md`, 631 lines)

- **Status** (line 3, verified): "Status: AUDIT AND PREPARATION ONLY. Nothing is renamed. The rename follows Eve's decision of 2026-11-15 (ADR-106 note V1-B, channel M106-M108) and waits for her answers in section 8." Title line 1 says "corrected 2026-11-16".
- **Must happen, counts** (line 630, verified): "191 components: 123 exact -> `plotnine_`, 46 modified -> `modif_`, 22 own -> `step_`". Line 34: registered 191 = 169 with a plotnine name, 22 without. Lines 35-36: exact 123 / modified 46 / own 22. Section 9 (lines 436-630) is the old-to-new table, generated (impact doc says; not re-run).
- **Plan** (section 7, lines 393-407, verified): step 0 picture baseline; 1 one function for the shape of a name "with the old names still working"; 2 rename in the registry, prefix equals field; 3 add the exact neighbours (31); 4 migration script (dry run by default, `--apply`); 5 Blueprint pickers; 6 docs; 7 controls. "Each step a commit with tests; one builder and one reviewer at a time."
- **OPEN, waits for her** (section 8, lines 411-429, verbatim fragments):
  - Q1 (reproducibility): "A results bundle exported before the rename holds old names and the old recipe fingerprint. Options: (a) refuse it with the migration command ... (default); (b) ... (c) ... Default (a)."
  - Q2 (prefix rule): "(a) as stated, so prefix and registry field agree one to one (default); (b) the one-call conveniences (`facet_rows`, `guide_nrow` ...) become `modif_<their name>`".
  - Q3 (35 gaps): "(a) all that need no extra package and are a layer or a scale: 30 (default); (b) only the 21 scale variants; (c) none, keep the list and the test."
  - Q4 (two spellings): "(a) register both as separate components, each equal to plotnine (15 more; default ...); (b) one spelling only ...; (c) a silent conversion ... (not proposed: silent)."
  - Q5 (names inside values): "Default: they stay plotnine's names ... The `theme:` key of a plot spec and of `plot_defaults` changes."
  - Q6 (15 objects): "They become `modif_<name>` with no exact neighbour (it cannot exist). ... Default: `modif_` only; the description says why."
  - Q7 (`guide_label`): "Options: remove it now (default); rebuild; keep it renamed."
  - Q8 (facet setters and conveniences): "(a) keep all 21 working own components as `step_` (default ...); (b) remove the 9 ...; (c) fold the four facet setters ..."
  - Q9 (function parameters, N28): "(a) leave them out and document the `fun_data` names (default); (b) named summaries ...; (c) both." Also: "a text given to `labels` is read by plotnine as letters ... add a check? Default yes."
  - Q10 (rule files): "The prefix rule goes into `rules_viz_factory.md` (sections 1, 2, 7). Only after your yes."
  - Also section 1 point 5 (line 26-27): "This is the one point that touches reproducibility; it needs your decision (question Q1)." Rule files: section 6.1 line 244-245 "edited only after your yes".
- **What it says would break** (verified, counts from the impact doc, not re-run):
  - Table 6.1 (lines 182-199): viz library code 13 files, 465 MUST CHANGE; viz library tests 221 files, 1098 MUST CHANGE; records 29 files, 33; other tests 64 files, 294; docs and READMEs 14 files, 60; gallery recipes and index 70 files, 87; scripts 4 files, 71; plot spec files 25 files, 65; rule files 8 files, 0 must change (43 read); other code 7 files, 18; pipeline recipes 6 files, 12; Blueprint 1 file, 8; templates 4 files, 8; retest 4 files, 5. TOTAL 535 files, 5185 occurrences: 2224 MUST CHANGE, 1638 STAYS, 1323 READ.
  - Line 241: shipped recipes use 39 of the 191 components in 171 places (27 exact, 11 modified, 1 own); 152 are used only by tests and the form.
  - Section 6.3 (lines 263-285): 64 lines in 20 files; 23 lines in 6 production files that test a name by its start (example line 270: "`plotnine_geom_point` does not start with `geom_`: two geoms with the same name would count as one ..."). Blueprint: `_THEME_CHOICES` in `app/handlers/blueprint_handlers.py` (8 occurrences, line 242).
  - Gallery: line 401 says "37 gallery examples"; table 6.1 says 70 files. Not reconciled (see section 4 below).
- **Build order it proposes**: section 7 steps 0 to 7, above.
- **Must she read it first?** The impact document has no such sentence (I searched for "read", "must", "before the build", "wait"). Its own status line (line 3) says the rename "waits for her answers in section 8". The sentences that say she must see or read it come from elsewhere: (a) tasks.md:387 "starts only after Eve has seen the impact list." (records author not stated; "seen", not "read"); (b) D-0091 evidence "The rename is not built: the impact list comes to her first (M129)." (ledger, her decision line; "comes to her first"); (c) FOR_EVE_still_open_2026-11-16.md line 93 (B8): "starts only after you have seen the impact document, `tasks.md:387`. Read `.claude/design/viz_rename_impact_2026-11-15.md` sections 1 and 2 first." The writer of that file is an agent (its line 3: "written for the review session (M176) by an agent"). That is the only "read ... first" sentence.

## 3. FOR_EVE_still_open_2026-11-16.md (`tmpAI/panel/round7/`)

- **B8** (line 93): "The rename of all plot components (Pt11 to Pt15). Waits: the whole rename (535 files, 5185 places; starts only after you have seen the impact document, `tasks.md:387`). Read `.claude/design/viz_rename_impact_2026-11-15.md` sections 1 and 2 first." Line 95: "Pt11 (CONFIRM, listed in (d)), Y10 and Y26 (CONFIRM) belong to the same block." Line 96: "Records: D-0091 ... No record speaks of Pt12 to Pt15. Default: none supported."
- **Pt11** (line 345, tag CONFIRM*): "Names plotnine does not have (22): prefix step_ or modif_" (record: D-0036 and D-0091; "the 22 are not all composites").
- **Pt12** (line 346, OPEN*): "Names written as values (geom: geom_area) get the prefix or stay plotnine's"; no record ("No record speaks of values").
- **Pt13** (line 347, OPEN*): "The 15 plotnine objects that cannot be added to a plot (element_*, position_* ...)"; "No record".
- **Pt14** (line 348, OPEN*): "guide_label fails on every use: remove, rebuild, or keep renamed". Its record note: "Records disagree: tasks.md:312 'your choice: rebuild or remove' and :447 'fixed and tested'". Verified: tasks.md:312 holds "(c) `guide_label` cannot work (Eve's choice: rebuild or remove)"; tasks.md:447 is TWO-RECIPE-NAMES-1; "fixed and tested" is at tasks.md:452 (VIZ-DEFECTS-1). The cited line number is wrong.
- **Pt15** (line 349, OPEN*): "The facet and guide conveniences (21 own components): keep, remove 9, or fold 4"; "no record decides".
- **B9** (lines 98-100): "A mean with an error bar per group (Pt16). Waits: the `stat_summary` work (`tasks.md:388`)." Pt16 (line 350, OPEN*): "How a recipe maker gets a mean with an error bar (stat_summary takes functions)". Its record: ledger A12 "NOT decided". tasks.md:388 is N28 (verified).
- The FOR_EVE file's own tag legend (line 7): "OPEN: no record answers, or two records disagree."

## 4. Tasks (`.claude/tasks/tasks.md`) on the viz rename

- **VIZ-STANDARD-1** (lines 61-65, `[opus/high]`): V1, V3, V5, V6, V7, V8 merged; "Next: V4, V2, V10, V9." Not the rename, but it is the same library. "Eve 2026-11-14: V1 to V10 accepted as recommended."
- **VIZ-NIGHT-QUEUE** (line 365, DECIDED 2026-11-15, M97): "V1 to V10 stand as recommended. Queue ... V4; then V2 + V10-B; then V9-B; the export lines for `plot_engine`; the plot's two silent filter paths. Kept out (need Eve's yes): the rule-file edit of V9; the ADR-036 reference; V1-C; `guide_label`; the theme order; `stat_summary` `fun_y`." The rename is not on this queue.
- **V1-B, plot names like the Polars names** (line 385, `[sonnet/high]`): DECIDED 2026-11-15 (M107, M108). "State: open; the registry audit comes first."
- **V1-B-AUDIT, registry audit** (line 386): "OPEN, first step of V1-B". Conflict: line 442 (section 6, "Done, 2026-11-16") says "AUDIT-PLOT-COMPONENTS-1, audit of the plot components and impact of the rename — DONE in `3d69e14f`". The tasks file does not use the ID VIZ-REGISTRY-AUDIT-1 (the impact document's header uses it); I found no such ID in tasks.md.
- **V1-B-RENAME, the rename** (line 387, `[sonnet/high]`): "DECIDED in principle 2026-11-15 (M107); starts only after Eve has seen the impact list. One planned change, one builder and one reviewer at a time, may run at night ... State: not started."
- **N28, `stat_summary`** (line 388, `[sonnet/medium]`): "OPEN (M106). Not decided ... Not on the night queue until she answers."
- **VIZ-FOLLOWUPS-1** (line 312, done merge fcae8d0c): items (c) `guide_label` "(Eve's choice: rebuild or remove)" and (b) five facet components fail on their own example. Items (c) to (f) "were not named as done by the merge, check before closing."
- **VIZ-DEFECTS-1** (line 452, `[sonnet/medium]`, open): theme_seaborn and theme_matplotlib fail with base_size; guide_label fails on every use; a text where a list is meant is read letter by letter. "Fix: each one fixed and tested, with the error named."
- The rename does not appear as a separate item for the rule file (rules_viz_factory.md); only Q10 in the impact document.

## 5. What is built today

- **Registration and names** (verified): `libs/viz_factory/src/viz_factory/registry.py:44` `def register_plot_component(name: str, ui_schema: ...)`. The name is the string given to the decorator; no prefix is added. The registry field is the key `plotnine` in `ui_schema`: documented at `registry.py:53-56` ("`exact` ... `modified` ... `own`"); enforced by `_read_exact_parameters` at `registry.py:76-84` (an `exact` schema may not write `params`; they are read from plotnine). Field values in code, e.g. `libs/viz_factory/src/viz_factory/themes/core.py:49` `"plotnine": "modified"`, `:65`, `:81` and more.
- The strings `plotnine_`, `modif_`, `step_` do not occur as code prefixes. `plotnine_` occurs only in comments: `registry.py:56` (points to the test file) and `plot_config_resolver.py:171`.
- **Name-shape code** (verified): `libs/viz_factory/src/viz_factory/plot_config_resolver.py:130` `if name.startswith("geom_") or name.startswith("stat_"):` (the impact document lists 23 such production lines; section 6.3). Not re-verified line by line.
- **Test that the field agrees with the code** (verified by its docstring, lines 1-11): `libs/viz_factory/tests/test_component_plotnine_field.py` re-derives the `plotnine` value from each component's code. The registry docstring (`registry.py:56`) names it. D-0092 asks for a prefix test; I did not find one that checks the prefix (no prefix exists yet).
- **`assets/scripts/viz_rename_table.py`** (verified, lines 1-60): changes nothing (line 8). Subcommands: `table`, `count`, `sample`, `sites`, `report` (lines 10-20). `PREFIX = {"exact": "plotnine_", "modified": "modif_", "own": "step_"}` at line 51. `EXCLUDED` (line 56) leaves out itself and the impact document. It reads `COMPONENT_SCHEMAS` (line 49).
- **`libs/viz_factory/tests/test_registry_audit_vs_plotnine.py`** (verified docstring lines 1-14; I did not read the test bodies): four questions answered by running plotnine: A, every public plotnine object is registered, named, or a known gap; B, every registered name plotnine does not have is one of the 22 own names; C, every `exact` component gives the same plot as the direct call; D, what a `modified` component is to plotnine. Lines 13-14: "The lists below are the audit result of 2026-11-15, plotnine 0.15.4. They are meant to change: the rename task ... rewrites them in the same commit."
- **Counts of shipped recipes and gallery examples naming a component** (my grep, verified; block form only, `name:` at the start of a line; flow form not counted):
  - `config/`: 37 files, 66 lines (grep "Found 66 total occurrences across 37 files").
  - `assets/gallery_data/`: 34 `data_analysis_recipe.yaml` files (glob); only 1 of them has a block-form component name line (`heatmap_correlation`). So the gallery's uses are in another form, not counted here.
  - The impact document's figures for the gallery (70 files, 87 lines at line 190; 37 examples at line 401) do not match these; not reconciled.

## 6. Answers from the records only

(a) **Covered by a DECIDED line of hers, no open point attached:**
- The field kept and the prefix-equals-field test: D-0092. No open point in the impact document's section 8 or in FOR_EVE B8/Pt11-Pt16 (verified by reading both).
- The prefix `plotnine_` for the exact components (123) and `modif_` for the modified components that are not among the 15 of Q6 (31): D-0091, with no open point in section 8 or FOR_EVE (reasoned: Q3 and Q4 concern gaps and spellings, not these names; Q5 concerns values).
- The registry audit ("comes first" in D-0091): done per tasks.md:442.
- Caveat (verified in the text): D-0091's own evidence and tasks.md:387 gate the rename on her seeing the impact list, and the impact document's Q1 (fingerprint) applies to every converted recipe. So "could be built now" is not what the records allow.

(b) **Waits for an answer:**
- Q1: the fingerprint of recipes and exported bundles (default a: refuse with the migration command). Every converted recipe.
- Q2: the 22 own names (Pt11, CONFIRM) and the one-call conveniences (step_ or modif_).
- Q3: which gaps to register (default 30) and whether `geom_map` and the labellers stay listed.
- Q4: the two spellings (default: register both, 15 more).
- Q5/Pt12: names inside values (`geom: geom_area`) stay plotnine's (default) or get the prefix.
- Q6/Pt13: the 15 objects (default `modif_` only, no exact twin).
- Q7/Pt14: `guide_label` (default remove; records disagree).
- Q8/Pt15: 21 conveniences (default keep all as `step_`).
- Q9/Pt16 and B9: `stat_summary` and `fun_y`, `fun_ymin`, `fun_ymax` (default leave out).
- Q10: the rule file `rules_viz_factory.md` (only after her yes).
- All rule-file and ADR text: only after her yes (impact doc section 6.1; tasks.md:387; D-0091 evidence).

(c) **Record that says the rename waits for her to READ the impact document:**
- Only FOR_EVE_still_open_2026-11-16.md line 93 (B8): "Read `.claude/design/viz_rename_impact_2026-11-15.md` sections 1 and 2 first." Written by an agent for the review session (line 3 of that file).
- The nearest record sentences say "seen", not "read": tasks.md:387 "starts only after Eve has seen the impact list."; D-0091 evidence "the impact list comes to her first (M129)."
- The impact document itself contains no read requirement.

## 7. Contradictions between records (reported, not resolved; decision_compliance.md rule H)

1. D-0091 "no old names accepted" vs impact document plan step 1 (line 397) "with the old names still working: tests green, pictures identical". A transitional step against a decided rule; not stated to be temporary in D-0091.
2. tasks.md:386 "OPEN" vs tasks.md:442 "DONE" for the registry audit.
3. FOR_EVE B8 and Pt14 cite tasks.md:447 for "fixed and tested"; the words are at tasks.md:452; line 447 is TWO-RECIPE-NAMES-1.
4. D-0091 says a documented change is `modif_` "with the exact one registered next to it"; the impact document (section 2.2 and Q6) says the 15 `modif_` objects cannot have an exact neighbour. Not a clash for the 31 others; Q6 is open for the 15.
5. D-0051 still reads "no rename" in its decision text (replaced in part by D-0091, by the ledger's own relation column).

Items I did not check: D-0067 (cited by FOR_EVE Pt16, not opened); the test bodies of test_registry_audit_vs_plotnine.py and test_component_plotnine_field.py; the claim "191 components" (impact document says so; not re-run); the table of section 9 (not re-run).
