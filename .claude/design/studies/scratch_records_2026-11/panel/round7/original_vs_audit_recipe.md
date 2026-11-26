# Original recipe and audit recipe: what the records, diagrams, docs and code say (2026-11-15)

For Eve. A reading task: nothing was fixed. Main tree at `5be9f103` (branch `feat/recipe-format-1`), `dev` at `060cee41`.
Method: every row has a `file:line` or a diagram name and was READ; rows marked RUN were run (scratch scripts in `tmpAI/panel/architect/`).
The seven diagrams exist in the current `docs/UML/app.mdj` (last change 2026-11-12 19:20, commit `86e42fe4`). The archive tag `archive/home-filters-uml-2026-11-11` (2026-11-11 15:42) does NOT hold them: it is from before they were redrawn (RUN: `git show <tag>:docs/UML/app.mdj`).

Eve's five lines (channel M125, 2026-11-15; task TWO-RECIPES, `.claude/tasks/tasks.md:410`):
1. The original recipe is never edited during auditing.
2. The audit recipe is a copy. Its original steps cannot be edited or removed.
3. The audit only adds steps. A step added in the audit can be removed; that removes it from the audit recipe only.
4. The export is the audit recipe (original steps plus audit steps still present).
5. Full recipe edit exists only in Blueprint.

## The main finding in one paragraph

The idea "the audit is the original recipe plus steps, in a copy that cannot change the original steps" is written clearly in the records of 2026-11-12 and 2026-11-13 (`home_audit_steps.md:83, 132, 164`; ADR-105 points 5 and 6). But the seven diagrams were drawn on 2026-11-11 and 2026-11-12, before the copy was decided (2026-11-13). They draw original and audit DATA (original T1, audit T1, audit T2, audit T3). The words "original recipe" and "audit recipe" appear 0 times in the seven (RUN, text of each diagram). The only recipe word in them is "forked recipe", on the export. So the diagrams cannot show Eve the two recipes. Also, the review of 2026-11-12 (`home_evidence/home_uml_review_2026-11-12.md:9-11`) called three of them CONTRADICTED and suggested a banner; no banner was added and the redraw (UML-HOME-REDRAW-1, `tasks.md:137`) is not done (RUN: no "superseded" text in the diagrams).

Dates, to know which text wins (Eve: the revised rule has precedence):
- Old model (violet nodes, T3 sandbox): 2026-04 (contract section 1, ADR-029a, ADR-044).
- Export fork: ADR-097, 2026-11-09. Audit design v4 and the seven diagrams: 2026-11-11.
- Placement by tick lines, review of the diagrams: 2026-11-12. The copy and its invariant (point 22): 2026-11-13.
- ADR-105 confirmed: 2026-11-14. The five lines: 2026-11-15.

---

## A. Every place, by line

Verdicts: AGREE, DISAGREE, AMBIGUOUS. The number is the row id used in the counts.

### Line 1. The original recipe is never edited

| id | Verdict | Place | Quoted words | Why (one sentence) |
|---|---|---|---|---|
| 1a | AGREE | `.claude/design/home_audit_steps.md:132` (2026-11-12) | "the user's recipe files are never edited. Running the original recipe gives the original tables, running the audit recipe gives the audited ones." | Says line 1, and uses both names. |
| 1b | AGREE | `.claude/design/spaces/HOME.md:47, :92` (2026-11-12/13) | ":47 the original recipe, its steps and the data are never changed"; ":92 Original data and recipe never change (S1)" | Same rule, same names. |
| 1c | AGREE | `.claude/knowledge/architecture_decisions.md:5335, :5339` (ADR-105 points 2 and 6, 2026-11-14) | "Audit is the original recipe plus audit steps" | Latest ADR; agrees. |
| 1d | AGREE | `architecture_decisions.md:5117-5118` (ADR-099 point 8, 2026-11-11) | "the user's recipe files are never edited" | Older, same rule. |
| 1e | AGREE | `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:221`; RUN | "The ORIGINAL recipe's raw_config. Never mutated" | The export code works on a deep copy; the run shows the original dictionary equal before and after. |
| 1f | AMBIGUOUS | `home_audit_steps.md:11-13` (v4, 2026-11-11); `docs/user_guide/glossary_and_feedback.qmd:28` | "it never edits the original data (original T1 and T2)"; "The original data is never changed." | Names the DATA, not the recipe; the file also uses the phrase "the original" 34 times, often with no noun (RUN: count). |
| 1g | AMBIGUOUS | The seven diagrams (HOME-AUDIT-LINEAGE, -FLOW, -EFFECT, -CACHE, HOME-VIEW-MATRIX, HOME-EXPLORATION, UI-HOME-AUDIT) | "ORIGINAL T1 / T2 ... unchanged" (EFFECT); "originals are never written" (CACHE); "original Result plot (reference)" (UI-HOME-AUDIT) | They say the original DATA and original plot are unchanged; none draws the original recipe or a copy of it. |
| 1h | AMBIGUOUS | `.claude/design/home_stage2_mechanism_spec.md:17` (A1.4, 2026-11-15) | "The 'audit copy' = a copy of the data analysis recipe holding your marked audit steps. The original never changes." | The part Eve reads says "audit copy", not "audit recipe", and "the original" is not named. |
| 1i | AMBIGUOUS | `home_stage2_mechanism_spec.md:66, :120` (S2-3, re-base); `home_evidence/home_audit_view_from_copy_2026-11-13.md:21` | "The recipe or the data changes while an audit is open: ... re-base" | Says what happens if the original is changed (in Blueprint) during an audit; line 1 is about HOME, so this needs Eve (question Q3). |

### Line 2. The audit recipe is a copy; its original steps cannot be edited or removed

| id | Verdict | Place | Quoted words | Why |
|---|---|---|---|---|
| 2a | AGREE | `home_audit_steps.md:164` (point 22, 2026-11-13) | "the user cannot modify the steps that come from the original: the copy minus its marked audit steps must be identical to the original ... any difference outside the marked steps is an error that blocks" | The exact rule of line 2. |
| 2b | AGREE | `home_audit_steps.md:83` item (3) (2026-11-12) | "The recipe is as is: the audit can only add steps; it never removes or overrides a step of the recipe" | Same. |
| 2c | AGREE | `spaces/HOME.md:47, :49, :126` (2026-11-13) | ":49 It does not mean that recipe steps can be removed: they cannot."; ":126 original steps are read-only in the copy" | Same. |
| 2d | AGREE | `architecture_decisions.md:5338-5339` (ADR-105 points 5 and 6) | "an audit never removes or overrides a recipe step"; "the copy minus its marked audit steps must equal the original, otherwise it blocks" | Same, in the ADR. |
| 2e | AGREE | `home_stage2_mechanism_spec.md:109` (part B section 2); `recipe_format_spec.md:205`; `home_evidence/home_audit_view_from_copy_2026-11-13.md:3` | "invariant: the copy minus its marked steps equals the original; any difference blocks" | Spec and checker profile `audit` carry the rule; it is in part B, not in part A. |
| 2f | AGREE | `docs/user_guide/system_transparency.qmd:136`; `.claude/knowledge/app_features_traceability_matrix.md:85` | "Violet nodes — the T2 blueprint steps (inherited from the data analysis recipe, read-only reference)" | Old model, but it says read-only. |
| 2g | DISAGREE | `.claude/rules/ui_implementation_contract.md:13-15` (text of 2026-04; edited 2026-11-07; no "superseded" mark); also `:71` | ":14 A 'Power' icon allows the user to toggle a node off"; ":15 A trash icon allows for removal. If the node is Violet, a modal triggers: 'CRITICAL: Removing a blueprint step may break the intended visualization.'"; ":71 (and modified Violet node)" | These controls let the user disable, remove or modify an original (violet) step: the opposite of line 2. Older text, revised later by point 22 and ADR-105. The contract itself says at `:14` the icon is not built (F-07). |
| 2h | AMBIGUOUS | `ui_implementation_contract.md:10-12, :17` (2026-04) | "Nodes dragged ABOVE Violet nodes = Pre-transform"; "btn_revert performs a Full Wipe ... restores the Tier 3 stack to the exact state of the Tier 2 blueprint" | Old model: user steps sit above or below the original steps; the wipe removes user steps only, so it does not break line 2, but it is a different mechanism from "append to the copy". |
| 2i | AMBIGUOUS | `home_audit_steps.md:318, :329` (section 10, 2026-11-11, before point 22) | "Removing any step is simply 'recompute without it'"; "edit a step (= replace it)"; "Remove all steps (back to the originals)" | "any step" and "edit a step" do not say "audit step only"; "the originals" means data. |
| 2j | AMBIGUOUS | Diagrams HOME-AUDIT-FLOW and UI-HOME-AUDIT | FLOW: "Delete a step, Undo last, Revert to step N or Remove all: recompute WITHOUT it". UI-HOME-AUDIT: "Undo last \| Revert to step N \| Remove all steps"; "Today the panel also has Inherited (Tier 2) nodes, the filter inventory and a pending badge: to review what stays" | "a step" is not tied to audit steps; the Inherited nodes were dropped on 2026-11-13 (`HOME.md:124`) but the diagram still carries the question. |
| 2k | AMBIGUOUS | `docs/appendix/data_lifecycle_theater.qmd:60-69` (2026-11-08); `docs/workflows/ui_app_features.qmd:155`; `docs/workflows/dashboard_app.qmd:44, :100` (2026-11-08) | ":67 Steps ABOVE the 'Inherited' block"; ":60 Reset Sync ... revert your Tier 3 workspace back to the Tier 2 baseline"; ":155 btn_revert (full wipe back to T2 blueprint)" | Old model, no "outdated" mark; silent on editing original steps, but they teach the old picture. |
| 2l | AMBIGUOUS | `home_stage2_mechanism_spec.md:17` and part A as a whole | "The original never changes." | Part A, the part Eve reads, does not say that the original steps in the copy cannot be edited or removed; only part B (`:84, :109`) does. |

### Line 3. The audit only adds; an added step can be removed, from the audit recipe only

| id | Verdict | Place | Quoted words | Why |
|---|---|---|---|---|
| 3a | AGREE | `spaces/HOME.md:47, :49` (2026-11-13) | "the audit never removes a recipe step; it only adds"; "removing an audit step updates the numbers" (`:49`) | Same rule. |
| 3b | AGREE | `home_audit_steps.md:146` (point 15) and `architecture_decisions.md:5336` (ADR-105 point 3) | "In audit only filters, drops and removals by key are possible" | Only additions of two kinds. |
| 3c | AGREE | `home_evidence/home_audit_view_from_copy_2026-11-13.md:9, :20` | "undo, remove and revert edit the copy; the export is the copy"; "the copy is rewritten from its marked steps" | A removal changes the copy, not the original. |
| 3d | AGREE | `home_audit_steps.md:336-338` (event log) | "so removing a step to hide it is visible" | The removed step leaves the audit recipe but stays in the log (see Q8). |
| 3e | AGREE | `docs/user_guide/audit_pipeline.qmd:38` | "To remove an audit decision, click the trash ... deleting a node is the only 'undo'" | Old model, but it only lets the user remove his own step. |
| 3f | AMBIGUOUS | `architecture_decisions.md:5091` (ADR-099 point 3, 2026-11-11) | "Removing a step is the undo (recompute without it; later steps are kept and re-checked)" | "a step" is not tied to audit steps. |
| 3g | AMBIGUOUS | `home_stage2_mechanism_spec.md:97, :112` | "`strip_marked(copy)`"; "replaying the log gives the copy's marked steps" | The spec supports "only marked steps can go" but never says it in words; M125 asks that it does. |
| 3h | AMBIGUOUS | `home_audit_steps.md:329` | "edit a step (= replace it)" | Replace = remove and add; not said which steps. |

(2g also breaks line 3: a trash on an original step. Counted once, in line 2.)

### Line 4. The export is the audit recipe

| id | Verdict | Place | Quoted words | Why |
|---|---|---|---|---|
| 4a | AGREE | `home_audit_steps.md:35`; `architecture_decisions.md:5115-5116, :5242`; `home_stage2_mechanism_spec.md:124`; diagram DM-KEYS-EXPORT | ":35 the audit recipe in the export"; "AR audit recipe hash: the generated recipe, runnable on its own with the bundle's data" | The export holds the audit recipe (and its hash). |
| 4b | DISAGREE | `home_audit_steps.md:346` (P4b, 2026-11-12); `spaces/HOME.md:57`; `docs/user_guide/understanding_your_export.qmd:12`; the screen text `app/handlers/export_handlers.py:582-590` | ":346 One tick box 'include recipe and raw data', off by default ... it adds only the recipe (in audit mode the forked recipe)"; ":12 This standard bundle never contains your data analysis recipe or your raw data files" | By default the export has the steps and the hash, not the audit recipe file. The decision is older than line 4. |
| 4c | DISAGREE | `understanding_your_export.qmd:118`; `app/handlers/export_handlers.py:1297-1304`; diagram HOME-AUDIT-GUARDRAILS (B1) | ":118 Not every audited step can always be rewritten as a real recipe action ... the affected plot is named"; screen: "T3 steps could not be fully baked into the reproducibility recipe"; B1 (block): "a step the forked recipe cannot represent" | Built and docs: the export goes on and skips such a plot, so the export is not the full audit recipe. The diagram says this case BLOCKS; M124 line 3 says refuse. Three records, three behaviours. |
| 4d | AMBIGUOUS | HOME-AUDIT-FLOW ("Export ... forked recipe"), HOME-VIEW-MATRIX ("EXPORT ... forked recipe"), EXP-MODES ("frozen recipe, T3 baked in as real steps"), DM-KEYS-EXPORT ("audit recipe") | the four different names | Same thing, four names inside the diagrams; `home_audit_steps.md:132` equates "the forked recipe" with the audit recipe, nothing else does. |
| 4e | AMBIGUOUS | `app/modules/bundle_importer.py:165-167` (message shown after an import) | "the bundle's recipe copy has your audited T3 steps baked in ... never hashes the same as the original recipe by design" | Uses "original recipe" for the reference (good) and "recipe copy" for the audit recipe (another name). |

### Line 5. Full recipe edit only in Blueprint

| id | Verdict | Place | Quoted words | Why |
|---|---|---|---|---|
| 5a | AGREE | `spaces/HOME.md:83, :91` | "HOME does not build recipes and does not edit original recipes or plot specifications"; "structural changes go to BLUEPRINT" | Same rule. |
| 5b | AGREE | `home_audit_steps.md:99, :162` (point 20) | "no 'edit this step' button ... the text points to Blueprint for recipe changes" | Same rule. |
| 5c | AGREE | `ui_implementation_contract.md:466` (reworded 2026-11-12) | "In audit mode T3 never exposes an action-picker UI: the user can only add filters, drops and removals by key." | The audit offers two kinds of step only. |
| 5d | AGREE | `app/modules/wrangle_studio.py:1905-1914` | "YAML escape hatch ... Editable textarea + Save when data_analysis_recipe_edit_enabled" | The only recipe editor in the code is Blueprint's. |
| 5e | DISAGREE | `.claude/rules/rules_ui_dashboard.md:13` and `ui_implementation_contract.md:458, :484` | "BLUEPRINT's own YAML escape hatch (developer_raw_yaml ...)"; "Escape hatch: arbitrary data analysis recipe fragment" | These rule files still list a step type that is a piece of recipe text typed in the audit. Removal decided 2026-11-12 (`home_audit_steps.md:125`, task AUDIT-RAWYAML-REMOVE-1, in work). The code still has it: `session_manager.py:155`, `audit_stack.py:47,109`, `export_handlers.py:377`, `t3_translator.py:157`. |
| 5f | AMBIGUOUS | `HOME.md` and `home_stage2_mechanism_spec.md:66` | (silent) | Nothing says what the user sees if the original is edited in Blueprint while an audit is open (Q3). |

### Already marked as old in the records (not counted)

- `architecture_decisions.md:380, :382` (ADR-029a, status SUPERSEDED at `:348`): "Removing an inherited Tier 2 step triggers a ui.modal warning".
- `architecture_decisions.md:842` (ADR-044): "The T3 recipe ALWAYS initializes as a silent copy of the T2 blueprint"; the entry has the "Partly stale" banner at `:810`.
- `ui_implementation_contract.md:93`: marked superseded in part (ADR-098) but not for section 1.
- ADR-099 title words "four levels" (`:5045`) and the three diagrams LINEAGE, FLOW, EFFECT (levels 0-3, reach selector): contradicted by `home_uml_review_2026-11-12.md:9-11`; no banner in the diagrams.

### Counts

| Line | AGREE | DISAGREE | AMBIGUOUS |
|---|---|---|---|
| 1 | 5 (1a-1e) | 0 | 4 (1f-1i) |
| 2 | 6 (2a-2f) | 1 (2g) | 5 (2h-2l) |
| 3 | 5 (3a-3e) | 0 (2g counted once) | 3 (3f-3h) |
| 4 | 1 (4a) | 2 (4b, 4c) | 2 (4d, 4e) |
| 5 | 4 (5a-5d) | 1 (5e) | 1 (5f) |
| **Total** | **21** | **4** | **15** |

---

## B. The names used today

Counts are lines (files). Records = `.claude/design`, `.claude/knowledge`, `.claude/tasks`. Rules = `.claude/rules`. Scratch, worktrees, archives, tests and `tmpAI` left out (RUN: `tmpAI/panel/architect/count_names.py`).

### For the audit recipe: nine names

| Name | Records | Rules | Diagrams (elements) | Docs | Screen and code |
|---|---|---|---|---|---|
| "audit recipe" | 37 (13 files) | 0 | 6 (all in DM-KEYS-EXPORT / DM-KEYS-CHAIN; 0 in the seven) | 3 (`glossary_and_feedback.qmd:36`, `UML/cross_cutting_concepts.md:59`, `foundations/reproducibility_hash_schema.qmd`) | 0 |
| "forked recipe" | 38 (11 files) | 0 | 4 (FLOW, VIEW-MATRIX, GUARDRAILS B1, COMPONENTS) | 0 | 1 (`t3_translator.py` text) |
| "audit copy" | 17 (6 files; the stage-2 spec uses it 8 times) | 0 | 0 | 0 | 2 (`t3_translator.py:35-37`) |
| "copy of the recipe" | 14 | 0 | 0 | 0 | 1 |
| "recipe copy" | 8 | 0 | 0 | 1 (`reproducible_plots.qmd:61`) | 4 (message to the user `bundle_importer.py:165,227`; export README `export_handlers.py:1894`) |
| "frozen recipe (copy)" | 4 | 0 | 1 (EXP-MODES) | 0 | 1 (export README text) |
| "reproducibility recipe" | 4 | 0 | 0 | 0 | 3 (screen notice `export_handlers.py:1301`, importer messages) |
| "exported recipe" | 16 | 0 | 1 (TESTS box) | 0 | 0 |
| "view recipe" / "audit view" | 15 | 0 | 0 | 0 | 0 |

### For the original recipe: five names

| Name | Records | Rules | Diagrams | Docs | Screen and code |
|---|---|---|---|---|---|
| "original recipe" | 17 (10 files) | 0 | **0** | 0 | 3 (importer message `bundle_importer.py:167`; comments) |
| "the recipe" / "the original" (no noun) | hundreds (`home_audit_steps.md` alone: "the original" 34 times) | | "recipe" leg in DM-KEYS | many | |
| "recipe file set" (leg R, `rC`) | ADR-101, hash docs | | DM-KEYS, DM-KEYS-CHAIN | `understanding_your_export.qmd:41-47` | `effective_run.yaml` key `data_analysis_recipe_sha256` |
| "T2 blueprint", violet / inherited nodes | 7 (knowledge 6, design 1) | 7 (contract, dashboard rules, CSS spec) | 2 (note in UI-HOME-AUDIT) | 5 (4 files) | 3 comments in `audit_stack.py`; **on the screen**: the label "Inherited (Tier 2)" (`home_theater.py:1875`) and entries "[Tier 2] action: label" (`audit_stack.py:330`) |
| "Result", "Result (T2)", "reference plot" (for the original's data and plot) | | | UI-HOME-AUDIT "Original Result plot (reference)" | `help/home.md` | on screen "Result" |

### What the user sees on screen today

- "Audit recipe" appears nowhere on screen. "Original recipe" appears once, in the message after an import (`bundle_importer.py:167`). The rest of `app/` has them only in code comments (READ: grep of `app/`).
- The screen says: "Pipeline Audit", "Inherited (Tier 2)", "Result", "My view", "Compare", "Also include a reproducibility/reimport bundle", "the full recipe (your audited steps baked in as real wrangling actions)" (`export_handlers.py:582-590`), "the reproducibility recipe" (`:1301`).
- So the audit recipe has nine names in records, diagrams, docs and code; the screen adds its own words ("My view", "reproducibility recipe"). The original recipe has five.

---

## C. Does the BUILT code follow the five lines today?

Short answer: **no audit action edits, disables or removes an original step, and the original recipe file is never written in HOME.** But the audit recipe of the records (a copy that HOME reads) is **not built**; today only the export makes a recipe, per plot, and it is optional.

- **Violet nodes: no trash, no power icon (READ).** `audit_stack.py:313-333` draws the original tier-2 steps as plain text, "[Tier 2] action: label"; no button. The panel header is `home_theater.py:1875-1878`. The delete handler `audit_stack.py:565-619` removes only ids found in `t3_audit_steps_by_plot` and `_pending_t3_nodes`, that is audit steps. There is no `btn_revert` anywhere in `app/` (RUN: grep). Nothing sets `active` to False (RUN: grep; same finding as contract `:14`). So the contract section 1 (2g) describes controls that do not exist.
- **The original recipe file is not written in HOME (READ).** HOME writes only session ghost files as JSON (`session_manager.py:279, :422, :589`). The only recipe editor is Blueprint's (`wrangle_studio.py:1905-1914`).
- **What the export writes (READ + RUN).**
  - Default: plots, T1/T2/T3 data, `t3_steps.yaml`, `effective_run.yaml`, report. No recipe (`export_handlers.py:1220-1250, :1313-1364`).
  - Only when "Also include a reproducibility/reimport bundle" is ticked (`:1258-1266`): `data_analysis_recipes_reproducibility/<id>.yaml`, built by `build_mode2_recipe`.
  - RUN (`tmpAI/panel/architect/run_fork2.py`): a recipe with one join and one plot, one audit filter. The input dictionary is unchanged after the call. The original tier-1 and tier-2 steps are unchanged in the output. The output differs from the original in two places: a new join `J__t3_p1` was ADDED, and the plot's `target_dataset` was CHANGED from `J` to `J__t3_p1`.
  - So: original steps kept, audit steps added at the end of a copied join: good for lines 2 and 3. But "the copy minus its marked steps equals the original" (point 22) is not true: a new join and a repointed plot exist. This is the old per-plot mechanism; `t3_translator.py:35-37` says the audit copy is to replace it.
- **Where HOME and the export disagree (known).** A step of type `developer_raw_yaml` is applied by the export and ignored by HOME's table and plot (task `AUDIT-RAWYAML-REMOVE-1`, `tasks.md:408`: 42 rows in the export, 22 in HOME). No screen creates it; the code still knows it in four places (see 5e). Removal is in work.
- **Skipped steps (line 4).** A plot whose steps cannot be rewritten is skipped and named in `effective_run.yaml` (`export_handlers.py:1297-1311`), not refused.
- **HOME does not read an audit recipe.** HOME applies audit steps with its own filter code on the data (the "T3 ghost"). Stage-2 packages P3 to P7 (graph, keys, copy, view) are all "not built" (`home_stage2_mechanism_spec.md:26-30`; `HOME.md:4`). So lines 2 and 4 hold only as design, plus the optional export copy above.

Verdict: the built code does not break lines 1, 2, 3 or 5. For line 4 it does not follow the rule: the audit recipe is not in the default export, and a plot can be skipped.

---

## D. Proposed paragraph for the top of the stage-2 spec and the docs (for Eve to read)

**Original recipe and audit recipe**

1. HOME opens the original recipe. It is the reference. HOME never changes it.
2. Only Blueprint can edit a recipe.
3. When you audit, HOME works on a copy of the original recipe. This copy is the audit recipe.
4. The steps of the original recipe are in the copy. You cannot edit them or remove them.
5. In the audit you can only add steps: remove rows, or remove a column. Each step has a reason.
6. A step you added can be removed again. It leaves the audit recipe. The original recipe is not touched.
7. The export is the audit recipe: the original steps plus the audit steps that are still in it.
8. The original plot stays beside the audited plot, so you can see what the audit changed.

(Line 7 depends on Q1. "Audit copy" in the spec would become "audit recipe".)

---

## E. Questions only Eve can answer

**Q1. Is the audit recipe always in the export?**
Today (decided 2026-11-12, P4b) the recipe is behind one tick, off by default, together with the raw data. Your line 4 says the export is the audit recipe.
Options: (a) the audit recipe is always in the export; the tick keeps only the raw data (the recipe holds no data); (b) keep as decided: one tick for recipe and raw data.
Default: (a).

**Q2. When is the audit recipe created?**
Options: (a) at the first audit step; before that, HOME reads the original; (b) when audit mode is switched on; (c) at the start of the session.
Default: (a). The records say an empty audit uses the original as it is (HOME-AUDIT-CACHE).

**Q3. The original recipe is edited in Blueprint while an audit is open. What happens?**
Options: (a) "re-base" as in the spec (S2-3): the audit steps are written again into the new original, each marked applied, not concerned or broken; the export is refused until then; (b) the audit is closed with a message and the steps are kept in the log; (c) Blueprint refuses to save a recipe that has an open audit.
Default: (a).

**Q4. Do "Undo last", "Revert to step N" and "Remove all" touch audit steps only?**
So that "Remove all" gives back exactly the original recipe. Default: yes; the screen word becomes "Remove all audit steps".

**Q5. One pair of names.**
Options: (a) "original recipe" and "audit recipe" in records, diagrams, docs and screen; the nine other names are retired (code names may stay inside the code); (b) keep "audit copy" in the spec only.
Default: (a). Also: what is the screen word for the original's plot and data ("Result" today) and for the audited one ("My view" today, "Audited plot" in the target diagram)? Default: "Result (original recipe)" and "Audited (audit recipe)".

**Q6. The old rule texts.** `ui_implementation_contract.md` section 1 (violet nodes, power icon, trash with a modal, Revert) and section 12 and `rules_ui_dashboard.md` section 1 (`developer_raw_yaml`) contradict your lines 2 and 5. Four docs pages teach the old picture (`data_lifecycle_theater.qmd`, `dashboard_app.qmd`, `ui_app_features.qmd:155`, `system_transparency.qmd:136`).
Options: (a) a "superseded by the two-recipes rule" banner now, rewrite when the audit is built; (b) rewrite now.
Default: (a). No rule file is changed without your yes (M128 list).

**Q7. The seven diagrams.**
Options: (a) the interim banner suggested on 2026-11-12 on LINEAGE, FLOW and EFFECT, plus one new small diagram "TWO-RECIPES" (original recipe, audit recipe = original plus marked steps, export); (b) full redraw first (UML-HOME-REDRAW-1).
Default: (a). Each UML edit needs your OK.

**Q8. A removed audit step: does it still show in the export?**
Line 3 says it leaves the audit recipe. The decided event log keeps "created, removed" (`home_audit_steps.md:336-338`), so the export would list it as removed.
Options: (a) keep the log in the export; (b) the log is kept only in the session.
Default: (a) (it is the point of the log: nobody can hide a removal).

**Q9. A step the export cannot write as a recipe step.**
Today: the plot is skipped and named. The diagram says block. M124 says refuse.
Options: (a) refuse the export with a message; (b) keep: skip and name.
Default: (a).

**Q10. Until the audit copy is built, may today's optional export recipe be called "audit recipe"?**
It keeps the original steps but adds a new join and repoints the plot (RUN, section C).
Options: (a) call it "audit recipe (per-plot form, until the audit copy is built)"; (b) leave its old name until it is replaced.
Default: (a).
