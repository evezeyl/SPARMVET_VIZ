# Independent goals review (Sonnet), whole picture against her goals

Date 2026-11-22. Branch `study/goals-review-sonnet`, from `dev` `31034158`. Read-only study: nothing is built from it.
Order: ledger `D-0528`, `D-0529`, `D-0530`, `D-0531`, `D-0532`.

## Summary for her (two screens)

I wrote my own path to your goals first, without the Opus overview (commit `a36bd0e5`). Then I compared, then I tried to break every KEEP of the match list. I ran the demo myself: one entity removed at one place, then every table and plot rebuilt (about 6 seconds). Same demo, same entity as the Opus runs, so the numbers are comparable.

**What we agree on (so you can trust it).** The scope stays yours. The effect of a choice cannot be read from the recipe; it has to be measured by a run before you confirm. Removing an entity "at the start" can leave it in 7 of 17 plots, 3 of them with source, year and country erased: I got the same numbers as Opus. The audit that is built today (a filter on the plot's finished table) must be replaced by the audit recipe plus a rerun. I measured why: for the plot `qa_population_zscore`, a filter on the finished table leaves all 41 other samples with a z-score that still includes the removed sample; a rerun without it changes all 41 (largest change 0.064). Remove step, the reason gate, the fingerprint, the audit copy and the run are sound and are used by my runs.

### 1. Where I disagree with the Opus agent: you decide

1. **Column drops in the audit (its question 29).** Opus recommends: no drops in the audit; the recipe author removes a column. I recommend: keep the drop, but only in the table a plot reads, recorded with a reason. Why: you said the user may not be the author. A user who must publish a table without one column will otherwise edit the exported file by hand. That is outside every record. Opus's argument "the check of key columns is no longer needed" is an argument by less code, which is not an argument by your rule. This is reasoning, not a run.
2. **The Reshuffle (its question 17).** Opus recommends: remove it. I say: both are defensible, and I do not rank them. Opus is right that the seed has no home once the join fork of the export is removed (`bake_plot_seeds` writes into the recipe copy). But the seed is already written in `effective_run.yaml`, so a home exists. Your words of D-0341 are on the other side; Opus shows them.
3. **Your case "keep the poor-quality sample in the quality results" (D-0499).** The Opus text (4.4) says: with "remove from all the data" and two tables unticked, the sample stays in exactly the 3 quality plots with its metadata. I ran the option as decided and built: it stays in none, and all 17 plots change, because the source tables are still ticked. To keep it in the quality plots you must also untick `FastP`, `Quast`, `Bracken` and the metadata. The Opus run used a 19-place variant that you did not decide (D-0416 says every table that holds the key). Please do not rely on that sentence.
4. **Ten questions answered "by my reading unless you object" (its 10-12, 16, 18-22, 24, 25).** I would not let silence count as a yes. A default is not a decision (rule G). Ask you for one explicit yes to the block.
5. **The bundle (not seen by Opus).** The export writes `T1_data.tsv` and `T2_data.tsv` from the ORIGINAL tables; only `T3_data_<plot>.tsv` is audited. Someone who takes the T2 file publishes the sample you removed. The audited part of the bundle must hold audited tables, or say loudly which file is which.

**A correction of mine.** In part A I recommended turning the "every join in tier 1" rule into an advice. I withdraw it: the rule (ST05) is wider than your decision (it covers every join, not only the metadata), but it makes the end of tier 1 of a joined table one clear place, and Opus is right that your question 27 is the place to decide the breadth.

### 2. The KEEP items that survive my attempt to break them

- Merge the branch `task/home-filter-follows-table` (its 5 test files: 88 passed). Does not depend on any open question.
- `remove from all the data` writing only at the places left ticked (`apply(..., ticked=)`, 125 tests pass), without the sentences about unticked tables. Keep it a library step: the measured map must follow, or you never learn where the sample stays.
- The audit recipe, the one list `audit_steps`, "Remove step", the reason gate, the fingerprint, the log, the two export parts, the dialog of places with their reach, the opening build, Exploration as built, `table_compare` (it already gives "41 rows changed, 1 removed"), `audit_run`, `audit_copy`, the refusal of a result id written twice, the good-practice page for the gotchas, the naming rule and the limits.

Not sure, as in the match list, plus three more: D-0501 "no per-table warnings" (the measured line about other samples reopens it in part, so it is not a plain KEEP); D-0203 against D-0501 (they pull); the `audit/` folder in a deployment with no writable place (never decided).

### 3. What neither of us verified

- The dialog does not exist: nobody has used it. Every "what you would see" is described.
- One recipe (the demo), one entity (`10668076`), a few places chosen by hand. Not a filter on a value other than the key; not the join kinds anti, right, full, cross (the demo has none); not a large recipe (speed).
- BLUEPRINT, the documentation pages and the Gallery were not read by me. The Opus claim about a summary table made from a join (a new group with empty country and year) I did not reproduce.
- The full suites were not run. For the two branches I ran only the test files of the change.

---

---

# PART A. Blind: how her goals would be obtained

Part A was written before I opened any file of the Opus overview, of its match list or of its reviews. The commit of part A (hash at the top of part B) is the proof.

Labels used: **verified** = I read it at `file:line` or I ran it. **reasoned** = my argument. **ledger** = a ledger line, her words are in its evidence field. **collection** = taken from a scout collection in `tmpAI/coordinator/whole_picture/` and re-checked where I say so.

What I ran (all read-only on the repository; scratch under this worktree's `tmpAI/exp/`, run with the main tree's `.venv`, on the demo recipe `1_test_data_ST22_dummy`, dev `31034158`):
- **E1** (`tmpAI/exp/e1.py`, result `tmpAI/exp/e1_result.txt`): one entity (the key `10668076`; the app is data agnostic, the demo calls it a sample) is removed with ONE audit step (`modif_filter`, `not_in`, `na: keep`) written by `audit_copy.add_step` at ONE place, then `run_audit` rebuilds every table and plot table of the audit copy. For each of the 28 tables I counted the rows that still hold the entity, before and after. Four places: `T1:metadata_schema`, `T1:FastP`, `T1:FastP_with_metadata`, `T1:ST22_Anchor`. This is one entity and four places chosen by hand. It proves what happens for those cases. It does not prove a rule.
- **E2** (`tmpAI/exp/e2.py`): the same entity is removed (a) after the plot's table is finished (what HOME's audit does today: a filter on the T3 table) and (b) at tier 1 of the table (the recipe is rerun). The plot `qa_population_zscore` shows an N50 z-score over all samples. I compared the z-score of each other sample in (a) and (b).

---

## A1. Her goals, in her words

All quotes are from the evidence field of the ledger line named (her exact words, her spelling). Anything in a bracket of the ledger line is the review session's reading and is not used as a goal here.

| # | Goal (my reading, mine) | Her words | Ledger |
|---|---|---|---|
| G1 | The user can make an audit that is clear, scientifically correct, reproducible and transparent. I read four separate properties. | "allow the user to make audits in an clear, scientifically correct , reproducible and transparent way" | D-0528 |
| G2 | The app is a tool for good data science. | "provide a tool the user can use to do good data science" | D-0528 |
| G3 | The visualisations (plots and tables) can be used for publication and trusted. | "help provide visualisations it can use for publication (incl. Tables an plot) it can trust" | D-0528 |
| G4 | The audit exists for small corrections: removing observations. | "audit is done to allow making small correction to results where some "observations" must be removed" | D-0528 |
| G5 | The audit is presented clearly, with the information the user needs to choose well. Recipe structure and how the audit steps are made are part of it. | "This includes recipe structure and how we perform the audit steps and how it is presented clearly with the necessary information so the user can make informed and good choices" | D-0528 |
| G6 | The app provides the tool, reproducibility, transparency, reliability; it does not choose for the user. | "Our role is to provide the tool, the reproducibility, transparency, reliability - however we cannot take choices for the user because it depends on the user context" | D-0528 |
| G6a | The scope of an audit step is the user's choice. The app cannot decide it. The reviewer must understand the lineage, the user the effects of the choices. | "the context is so depend for the user that is much choose the scope adapted to its case. We cannot choose for him..the app cannot decide the scope. The reviewer should understand the lineage and the user the effects of its choices" | D-0531 |
| G7 | Method: find how to get there, then adapt the code, even if that means reviewing decisions or changing strategy. | "I want to know how to get there, and then our current code needs to be adapted, which implies reviewing decisions or changing strategy that hoder to get there" | D-0528 |
| G8 | Where she misses something, I argue why and how. | "So if i miss something i want a good argumentation of why and how .." | D-0532 |

The six places of `D-0529` are covered in A3 (the path) and A4. Her words there are only "Ok i agee"; the six places are the review session's list.

Companion rules that she gave and that bind the answer: the app is data agnostic (`D-0512`: "remember that we are data agnostic, so sample id is the example"); cost, effort and delay are not arguments (`D-0268`, `D-0521` asks for the big line first); "reopens a decision" is information only (`D-0532` and the brief).

### Tensions between goals (each with both quotes)

**T1. Informed choice against "no warnings about natural consequences".**
- G5: "the necessary information so the user can make informed and good choices" (D-0528).
- `D-0501`: "we are complicating the work by putting warnings that should not be there, because they are natural consequences of the recipe"; "she would just show the differences where applied and no per-table warnings about downstream effects".
- Why it is a real tension (verified by E2, see A3 step 5): one "natural consequence" is not harmless. When an entity is removed before a step that computes across entities (a z-score, a mean, a rank), the values of ALL OTHER entities change. A row count "rows removed here: 1" does not show it. The user cannot choose well without seeing it. `D-0501` itself gave the way out: show "the differences where applied". A measured comparison of the original and the audited result is exactly that, with no per-table lecture. So the tension can be resolved without a warning list (see A6, question 2).

**T2. The user chooses the scope against a default of ticks.**
- G6a: "We cannot choose for him..the app cannot decide the scope" (D-0531).
- `D-0508`: "we tick low (early) near the original table - so by default it is propagated in the lineage". `D-0521` wants fewer decisions: "reduce the micromanagement decisions".
- Any default tick is the app suggesting a scope. It is acceptable only if it is named as a starting point and if the screen shows what each tick reaches, so that leaving it ticked is the user's act (A6, question 1).

**T3. "Correct science" against "small corrections that remove observations".**
- G1 (scientifically correct, reproducible) and G4 (remove observations).
- Removing an observation changes every statistic computed across observations. E2: all 41 other samples change z-score (largest change 0.064 on a z-score near 1.8). This is not a fault of the app. It is the science. What the app must do is to show it and to record it (A3 steps 5 and 8).

**T4. A tool that fits every recipe against a rule that shapes the recipe.**
- G2/G6: robust for every recipe; `D-0512`: data agnostic.
- `D-0510`: "the join with any metadata must be done at T1", enforced by the recipe check "for now". The rule imposes a structure on the author so that the audit is simpler. Whether it is needed is tested in A5.

**T5. The audit is "to remove observations" against everything the audit may do today.**
- G4 against `D-0322` (a step is a filter, a column drop or a removal by key), `D-0341` (Reshuffle in Audit mode), the "Plot Style" overrides (not mounted).
- A column drop or a re-drawn jitter does not remove an observation. They are other acts with other risks. See A6, questions 3 and 4.

---

## A2. Is each goal reached? (on the demo, today)

"Today" means `dev` `31034158`. "Decided, not built" means a ledger decision exists and the code for the user does not. The user sees nothing of a library that no screen calls.

| Goal | Reached today? | What the user sees today (verified) | Reached by what is decided and not built | The one thing missing |
|---|---|---|---|---|
| G1 clear | Partly | Header strip `Mode: Exploration / Audit`, `Table to view: Source / T1 / T2 / T3` (`app/handlers/home_theater.py` strip, mode set at `app/src/server.py:145`, view at `:146`); the line "Audit steps apply to the plot's table (T3) for now." (`home_theater.py:1482`); "To create an audit step, view T3." (`filter_and_audit_handlers.py:727`). | A dialog that offers every place of the lineage (D-0316, D-0346, D-0347, D-0355). | The user cannot say where the step goes. Nothing shows the user the lineage. |
| G1 scientifically correct | **No, for any result that is computed across observations** | The audit filters the finished plot table (T3). `audited_frame` is the one applier (`app/modules/t3_audit_engine.py:799`). E2: the numbers of all other entities are NOT what a rerun without the observation gives. | The audit copy plus rerun (`utils.audit_copy`, `app/modules/audit_run.py`): built and tested, called by no screen (grep: `run_audit(` appears only in `audit_run.py`; `remove_from_all`, `table_compare` have no caller in `app/` or `libs/*/src` outside themselves). | Wire the audit to the rerun. |
| G1 reproducible | Partly | Plots, T1, T2, `effective_run.yaml` (always: hashes, seeds, engine, git commit), `t3_steps.yaml` for the audit steps. The audit steps are applied in memory on export (`export_handlers.py:1299, 1463`). Only if the box "Also include a reproducibility/reimport bundle" is ticked does the bundle hold a recipe with the steps baked in (`export_handlers.py:677`, `:1564`). Import never checks the audit steps: the leg is always `not_checked` (`app/modules/bundle_importer.py:186-194`). | The export holds the audit recipe, the original as baseline, the audit record with a hash, the audit log (D-0324, D-0333, D-0478, D-0492). | An audit recipe that is the thing exported and imported, and a check on import that it reproduces. |
| G1 transparent | Partly | Every audit step has a reason and the Apply button is locked without one (`audit_stack.py:51`, `:189`). The reason and the steps are in `t3_steps.yaml` and the report. There is no log of who/when/what was shown at the choice, no "Remove step" control (grep of `app/` for "Remove step", `audit_log`, `audit_record`: no hit). The trash icon deletes a step and all copies. | Audit log, audit record, audit folder in the session (D-0315, D-0319, D-0333, D-0423, D-0478). | The record that says what the user chose and what the app showed. |
| G2 good data science | Partly | Exploration vs Audit separation, nothing from exploration is exported (D-0327), seeds fixed (D-0056), opening proof that every plot draws (`app/modules/opening_build.py`). | Same as above. | Informing about effects on other entities (E2). |
| G3 plots and tables to trust | Partly | `materialize_tier3` is the one reader for plot, T3 table and export (`home_theater.py:487-518`, `export_handlers`). **But** the bundle also writes `<table>/T1_data.tsv` and `T2_data.tsv` from the ORIGINAL stored tables, never audited (`export_handlers.py:1409, 1431`); only `T3_data_<plot>.tsv` is audited (`:1467`). A user who takes the T2 file of a table gets the observation that the audit removed. The report says what each file is (`:1914`). | The audit recipe is the truth and the bundle says which file is which (D-0324). | Tables of the bundle that follow the audit, or a clear mark. |
| G4 remove observations | Partly | Filters and column drops become steps; Send to Audit only while T3 is viewed (`filter_and_audit_handlers.py:157-160`). "Remove from all the data" exists as a library (`libs/utils/src/utils/remove_from_all.py:221 describe`, `:370 apply`), tested on the demo (`app/tests/test_remove_from_all_demo.py`), not on any screen. | D-0415, D-0416, D-0498, D-0499. | A removal that reaches the tables the user wants, and shows where the entity stays. |
| G5 clear information | **No** | The propagation modal says "This plot only / All plots / All plots except" and, per plot, whether the column exists (`filter_and_audit_handlers.py:~1056-1100`). It does not show tables, tiers, how many rows go, which plots change. | Lineage dialog and picker (D-0347, D-0496, D-0508). | The measured effect per place (see A3 step 4). |
| G6 not choosing for the user | Mostly, in what is built | The only scope is "this plot" unless the user picks. The app writes nothing the user did not send. | A default tick (D-0508) is decided; it must be shown as a default (D-0531). | Name the default as a default; show its reach. |
| G6a scope is the user's | In the built path the user chooses only among plots, never among tables or tiers | Same | D-0355 "That is the choice of the user". | The dialog. |

Summary: the decisions are mostly right and mostly built **as libraries**. The one missing piece is the wiring: no screen uses the audit copy, the walk, the rerun, the comparison. The screen the user sees still runs the older T3-only audit. That older path is not only incomplete. It gives a different number than a true removal (E2), so it must be replaced, not kept beside the new one.

---

## A3. The path: what a user does on the demo to obtain the goals

I describe the path that reaches the goals, step by step. For each step: what the app shows, what the user chooses, what the app does. Marks: **[built]**, **[decided, not built]**, **[mine]** (my proposal, not decided).

Case on the demo: the user (not the recipe author) sees in the plot `qa_population_zscore` or `year_distribution` that one entity (a sample with poor quality) must go. This is the use case of `D-0415` ("a sample so bad that it will be resequenced") and of `D-0499` ("he wants to show the poor quality sample for the quality results but remove the bad sample from all other results").

**Step 0. Opening the recipe.** [built] The app builds and stores every tier-1 and tier-2 table and draws every plot once; an error of the recipe is reported through the load gate (`app/modules/opening_build.py`, called at `home_theater.py:2513` by the collection; I did not re-check the line). Goal served: G3 (a plot that cannot be drawn is refused). The user sees a progress line.

**Step 1. Exploration: find the observation.** [built] The user views Source, T1, T2 or T3 and builds filters; they change only the table viewed; nothing is saved or exported (D-0327; `filter_and_audit_handlers.py:776-788`). Goal: G2. Nothing to change.

**Step 2. Choose to make an audit step.** [built, T3 only] The user switches to Audit mode. Today the "Send to Audit" button works only while T3 is viewed (`:157-160`). **[decided, not built]** the user starts the step from wherever he found the entity (Source, T1, T2, T3) and the step goes to the places he chooses (D-0507, D-0316, D-0346).

**Step 3. The dialog: what the app shows about the lineage.** [decided, not built; the library exists] The walk (back, forward, back again: D-0347) lists the places where the column exists and, for each place, its reach: the tables and plots that read it. Each place is a line with a tick. The walk is `libs/utils/src/utils/lineage_walk.py:549 walk`, used today only by the drop check and the tests.
 [mine] The screen is the outline of the data story (she asked for "the story", `D-0508`): the original data tables at the top, then each table, its tiers, the plots at the bottom; the places a step can be written at are marked; a place where the app cannot follow the column is shown grey with the plain reason (as decided, D-0454, D-0460).

**Step 4. The effect of each choice, measured.** [mine, uses decided parts: D-0501 "show the differences where applied", D-0450 "do not get wrong results because we did not select the correct scope", `D-0508` "the check is where you apply it"]
 Reading a recipe cannot say what happens in a table where no step is written. The scout evidence on the untick branch shows it twice (`EVIDENCE_untick_branch_reviews.md`: two versions of "stays / removed upstream" gave false statements on the demo). I confirm the principle with E1, which is a RUN of the audit copy:

| Step written at (only there) | Tables that no longer hold the entity | Tables that still hold it | Plots changed |
|---|---|---|---|
| `T1:metadata_schema` | metadata_schema, ST22_Anchor (T1, T2), MLST_with_metadata (T2 only), QA_AMR_per_sample, QA_year_types, QA_fanout_exhibit, QA_aggregated_no_key, QA_population_zscore | 20 of the 27 tables that hold the key: the 10 source tables; Summary_phenotype_length_fragmentation, AR1_MLST_Serotype_Virulence, QA_ST_with_NA, QA_L50_integer; and 6 result tables built by a left join (FastP, Quast, Bracken, ResFinder, MLST `_with_metadata`, QC_Reads_Anchor). I read 4 of those 6 (FastP, Quast, MLST `_with_metadata`, QC_Reads_Anchor): source, year and country are **EMPTY** for the entity | 13 of 17 "changed": 10 lose the entity, 3 (`miaou`, `assembly_quality_dotplot`, `qc_reads_horizontal_barplot`) still show it with empty source, year and country; 4 show it unchanged (`phenotype_genome_length_fragmentation`, `amr_heatmap`, `qa_sequence_type_missing`, `qa_l50_integer`) |
| `T1:FastP` | FastP, FastP_with_metadata, QC_Reads_Anchor | all others | 1 of 17 |
| `T1:FastP_with_metadata` | FastP_with_metadata | all others | 0 of 17 (no plot reads it) |
| `T1:ST22_Anchor` | ST22_Anchor (T1, T2) | all others | 2 of 17 |

 Reading of the table (verified by E1, 28 tables, one entity; the empty metadata verified by reading the audit run's `FastP_with_metadata`, `Quast_with_metadata`, `QC_Reads_Anchor`, `MLST_with_metadata` for that entity: before `source Broiler, year 2024, country Norway`, after all three empty): the metadata table is the **right** side of the left joins of most result tables, so removing the entity from the metadata does NOT remove it from those tables. The left side keeps its row and the metadata columns become empty. This is worse than "not removed": the entity is still counted and now sits in a "no country, no year" group. The user who removes the entity "at the start" sees "13 plots changed" and believes it is gone, when 3 plots still show it with its metadata erased and 4 show it unchanged. He cannot know which without a run. This is the case of `D-0508`: "the user will have to learn that it is not the sample that stays but where the change is applied". The app can show this without choosing for the user: after the user ticks places, one **measured map**, for the tables that hold the entity key, "rows with the entity: before, after", and the list of plots whose table changed, each from a real run of the audit copy (`audit_run.run_audit`; the demo took about 6 seconds for a base build and three runs on this machine, `time`). Where the key is rewritten the map says "cannot count here" instead of guessing. A map of the same kind for a filter on a value shows "rows removed here" per table.

**Step 5. Effect on other entities: one measured line.** [mine] E2 proves that removing an entity before a step that computes across entities changes all others (all 41 differ, up to 0.064 on a z-score; a filter on the finished table leaves them unchanged and wrong for a removal). The app can compare original and audited result tables (the decided `table_compare`, D-0485, D-0488, D-0489: counts, a whole-row difference, a paired view with a verified key) and tell, per result the user cares about: "values of entities you did not remove changed in N tables and M plots". It does not say which place is right. It only shows the effect. This is compatible with `D-0501`: no per-table warnings that explain natural consequences, only the measured difference.

**Step 6. The user chooses, gives a reason, confirms.** [decided, not built] The user ticks and unticks places (D-0316, D-0499: "he is responsible of its choice"). The default is a starting point named as a default (D-0531 reading; A6 question 1). The reason is required (the gate exists today: `audit_stack.py:51`, `:189`). The app writes one audit step at each ticked place, in the list `audit_steps` of its tier, with an id and the comment (D-0332: `libs/utils/src/utils/audit_copy.py:212 add_step`, built as a library). The original steps are never touched.

**Step 7. See the result and compare.** [decided, not built; the plot compare exists as a baseline] The user views each table at each tier (original or audited), the audited plot and the original side by side. Today the Compare switch shows the plot as drawn from the table the plot reads with no audit step (`home_theater.py` `_make_cmp_baseline_handler`, by the collection). The comparison of tables is `table_compare.compare` (`libs/utils/src/utils/table_compare.py:355`), no caller outside the library.

**Step 8. Remove a step.** [decided, not built] One control "Remove step": the user picks any step (D-0314); the run is redone. Today only a trash icon exists; it deletes a node and all its copies (`audit_stack.py:628`). The library has `remove_step` (`audit_copy.py:245`).

**Step 9. Export the results she can trust, and reproduce them.** [decided, not built] The bundle holds the audit recipe (the original plus the audit steps), the original recipe as baseline with a plain "which is which", the data stored once, the audit record with the hash, the audit log (who, when, why, places chosen, warnings shown), the tables as audited, the plots as audited, the hashes and seeds (`effective_run.yaml`, built). On import the app recomputes and compares the audit leg (today it never checks it: `bundle_importer.py:186-194`). Today the bundle holds the original T1/T2 files and an in-memory audit, a plot-private fork of the join only in the optional mode 2 (`libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197`).

**The six places of D-0529**

1. **Trust in the whole result.** What is seen is what is exported: built for the plot and its T3 table (one reader, `materialize_tier3`). Not built for the T1/T2 files (Step 9). The same recipe and data give the same picture: seeds fixed (D-0056), keys, engine fingerprint recorded. A current picture: only the Gallery has the key of the picture (D-0400).
2. **Two kinds of person.** The author declares the entity key, writes the joins, follows the recipe-making rules (`D-0498`, `D-0510` to `D-0512`); the user makes the audit with no knowledge of the recipe's internals. The dialog must therefore tell the story in the user's words (tables, not steps) and must not ask the user to understand join kinds. The advice texts for the author exist as "Suggestion:" lines of the recipe check (collection, `recipe_check.py`). Not checked by me beyond the collection.
3. **BLUEPRINT.** Not my main subject. Ledger `D-0495`: no silent overwrite, comments are kept. As said in that line, Save today writes without keeping comments. I did not read BLUEPRINT code. See A7.
4. **Documentation and help.** The gotchas (a key recomputed, a key under another name with no join, a key rewritten by a step; `D-0508`) must be on the good-practice page; the audit folder must be explained (D-0423). I did not find or read that page (A7).
5. **Where it runs.** The audit is written in the session folder, in the user's own place (D-0422, D-0423); export is a browser download that "works identically" (`ui_implementation_contract.md` section 7.2). Not decided: what a deployment with no writable user place does (D-0422, choice 5). My proposal: A6 question 6.
6. **How we know a goal is reached.** An acceptance check on the demo (mine, A6 end): (a) remove entity E at a place; the map shows E gone in the ticked places and where it stays; (b) rerun gives the same tables and the same hash twice; (c) export, import, reproduce: the audit leg is `match`; (d) the T2 file of each table in the bundle has no E in the ticked cone; (e) the other entities' values compared: the line says whether they changed; (f) two plots reading the same table agree.

---

## A4. What must be modified

### (i) Her plans and decisions

| Item | Verdict | Reason (goal) |
|---|---|---|
| D-0316/D-0346/D-0347 the dialog of places by lineage, ticks | **Keep** | G1, G5, G6a: it is the way for the user to choose scope. |
| D-0508 default ticks low, near the original data | **Keep as a named starting point; change the screen around it** | G6a: a default is a choice made for the user unless the screen shows what it reaches; E1 shows a default that looks complete (the earliest table) leaves 4 plots unchanged in 13 of 17 that change. Argued in A6 question 1. |
| D-0501 no per-table warnings; "rows removed here" | **Keep the per-table silence; add one measured line on other entities** | G5, G3: E2. |
| D-0499 the user may untick | **Keep** | G6a. |
| D-0498 listed, unticked, tickable (table with same key name, no declared key) | **Keep** | G6a, G5. |
| D-0415/D-0416 "remove from all the data": off by default, list shown first, only for the entity key | **Keep** | G4, G6. One thing to add: show the measured map (A3 step 4). |
| D-0509 no T0 | **Keep** | The removal at the table that joins the raw table with the metadata is enough; E1 shows the real problem is the right side of left joins, which T0 would not solve either. |
| D-0510 join with metadata must be at T1, enforced "for now" | **Questionable: advice instead of refusal** | G2, G6, data agnostic: the audit's reach comes from the walk, not from where the join sits (E1: the demo has the join at T1 everywhere and still the removal at the metadata table reaches only part). It restricts the author. A6 question 5. |
| D-0322 audit step = filter, column drop, removal by key | **Change: keep filter and removal by key; offer column drop only at the table a plot reads** | G4 is about observations. A6 question 3. |
| D-0341 Reshuffle only in Audit mode | **Keep, record the seed in the audit record, no reason required** | Cosmetic; recorded in `effective_run.yaml` today (seeds). A6 question 4. |
| D-0324/D-0333/D-0478/D-0492 export holds the audit recipe, original as baseline, record, log, data once | **Keep** | G1 reproducible/transparent. |
| D-0314 one control "Remove step" | **Keep** | G1 transparent. |
| D-0332 `audit_steps` second list in each tier | **Keep** | G1, simple to see what was changed. |
| D-0355 "the user decides the scope by the places ticked" | **Keep** | G6a. |
| D-0506 exploration filter belongs to the table, not the plot | **Keep** | clear, small. |
| D-0496 derived tables (form 3) | **Not sure: must wait for her; the audit design does not depend on it** | The walk reads the graph, whatever the format. |
| D-0507 order: one whole-picture design before more audit/lineage/format | **Keep** | G7. |

### (ii) The code, item by item (verified at `file:line`)

| Part | Verdict | Evidence |
|---|---|---|
| HOME modes and view choice (`app/src/server.py:145-146`, strip in `home_theater.py`) | **OK** (adjust the "for now" line and the T3-only rule when the dialog exists) | `home_theater.py:1482`, `filter_and_audit_handlers.py:157-160` |
| Exploration filters, their key, their clearing | **OK** | `filter_and_audit_handlers.py:776-788` |
| Propagation modal "this plot / all plots / all except" | **Replace** by the lineage dialog | `filter_and_audit_handlers.py` ~970-1195 (collection; I confirmed `:1097-1101`) |
| `audited_frame` as the applier of the audit steps on the finished table (`t3_audit_engine.py:799`) | **Replace** by the run of the audit copy | E2: not equal to a removal before the computing step |
| Node type model `AuditStep` and `t3_audit_steps_by_plot`, flat list and per-plot list stored together (`session_manager.py` per the collection `:488-545`) | **Replace** by the audit copy stored in the session's `audit/` folder; bump the session format number (the number exists: `SESSION_FORMAT_VERSION`) | D-0319, D-0423 |
| Right panel list (`audit_stack.py`) | **Adjust**: list the steps of the audit copy per place, with one "Remove step" | D-0314 |
| `key_drop` gate (`libs/utils/src/utils/key_drop.py`) | **Keep** as the rule of a drop; its HOME call at the T3 place cannot refuse (comment in `filter_and_audit_handlers.py` near `:895`, collection), so with drops limited to the last table it stays trivially right | A6 question 3 |
| `lineage_walk.py`, `lineage_records.py`, `lineage_sentences.py`, `recipe_graph.py`, `step_effects.py`, `declared_plans.py`, `plan_book.py`, `plan_composer.py` | **OK**: wire them to the dialog. Keep the closed list of readings (`step_effects.READINGS`) and "not yet followed" joins (anti, right, full, cross) as grey lines | collection §3, `step_effects.py:57-73` as read by the collection |
| `audit_copy.py` | **OK**: wire (add_step, remove_step, integrity_errors) | `audit_copy.py:212, :245, :352` |
| `audit_run.py` | **OK**: wire; it is the engine of the measured map and of the plot effect | `audit_run.py:310` |
| `remove_from_all.py` | **OK as the option; adjust**: the `may_stay` list is "values may differ" sentences read from the recipe; replace its role of telling where the entity stays by the measured map | `EVIDENCE_untick_branch_reviews.md`, E1 |
| `task/remove-from-all-ticked` (the untick branch) | **Hold, do not merge as it is**; its writing at ticked places (`apply(..., ticked=...)`) is sound; its statements for unticked tables are the part that two reviews found false; use the measured map instead | `EVIDENCE_untick_branch_reviews.md` |
| `table_compare.py` | **OK**: wire it to Compare | `table_compare.py:355` |
| Export: `T1_data.tsv`/`T2_data.tsv` from the original stored tables (`export_handlers.py:1409, :1431`) | **Adjust**: follow the audit, or name the files "original" | A2 G3 |
| Export mode 2 (the fork of the join, `t3_translator.py:197`) | **Remove** when the audit recipe is exported (it is the "second copy" the rule text names) | D-0324 |
| `effective_run.yaml` | **OK** | `export_handlers.py:1649-1690` (collection) |
| Bundle import leg `t3_steps` always `not_checked` (`bundle_importer.py:186-194`) | **Replace** by a recompute and compare of the audit recipe | G1 reproducible |
| `report_template.qmd` (dead), names `decision_hash` | **Remove / retire** (the code writes the report itself) | collection §2.10, rule text |
| Opening build (`opening_build.py`) | **OK** | G3 |
| Reshuffle and aesthetic override outside audit steps (`home_theater.py:881`, `audit_stack.py`) | **OK, record in the audit record** | A6 question 4 |
| BLUEPRINT save, comments | Not reviewed (D-0495) | A7 |

### (iii) What is ok as it is

Exploration/Audit separation; opening proof; one table reader; recorded seeds and hashes; the reason gate; fixed order of audit steps; the lineage library as a library (typed, tested, with plain "cannot yet follow" sentences); `audit_copy` integrity check (the copy minus audit steps equals the original); `audit_run` (rebuilds only what changed; rollback on error).

---

## A5. Decisions or strategies that work against the goals (information; argued)

**5.1 The audit that is built is a filter on the finished table, and nothing says so (G1 correct, G3, G5).**
Why it matters: E2. A user who removes a poor-quality sample with "All plots" gets plots in which the sample is gone and every other sample still has the z-score, mean, rank or share that was computed WITH the sample. The published figure says "audited" and the numbers are those of the unaudited data. How I know: I ran both and compared (41 of 41 differ). What the user sees today: the plot without the dot; no warning. Alternatives: (a) keep it and say so on the screen ("the audit removes rows from the plot's table only; results computed before the table are not recomputed"): honest but defeats G4. (b) replace it by the run of the audit copy (decided in D-0332, D-0316). This is a built-in contradiction between decisions that are DECIDED (the audit copy) and the code that is running (the T3 filter); `D-0507` already says "old things that exist are taken again because they are not build".

**5.2 "Tick low near the original table" as the default (D-0508) can read as "everything is removed" while it is not.**
E1: a step at `T1:metadata_schema`, the table with the information about the entities, leaves the entity in 20 of 27 tables and, in 7 of the 17 plots, still present (3 of them with source, year and country erased), because the metadata is the right side of the left joins of most result tables. A user who ticks "the original data" only for the metadata table and sees "13 plots affected" believes the entity is gone from the work. The decision itself is sound for entity removal (the earliest place of each branch is each original table, that is "remove from all the data"). The risk is the screen. If the screen shows the measured map (A3 step 4), the default is harmless and respects D-0531.

**5.3 The refusal of statements about unticked tables is right; it must not become silence.**
`D-0508`: "the check is more where you apply it". The scouts show reading join kinds gives false statements (`EVIDENCE_untick_branch_reviews.md`). The honest way is to say nothing read from the recipe and to show what a run measured. E1 is that run. If the dialog said nothing, the user would not learn where the entity stays (the very case of `D-0499`). So the right reading of D-0508 is "no statements read from the recipe", not "no information about unticked tables".

**5.4 `D-0510` (join with the metadata at T1, refused by the check).**
The reason in her words is "that would simplify removing of samples by key". E1 shows the removal by key is simplified by the lineage walk plus the measured map, not by where the join is written: on the demo, where every join with the metadata is already at T1, the removal at one place still reaches only part of the tables. The rule has costs: it forbids a recipe that the author needs (a metadata join in a later table of a derived table form, still open in D-0496), and it makes the checker decide the author's structure ("the app cannot choose for the user" applies to the author as well). It is "for now" and can be re-verified. My view: keep the advice, drop the refusal, unless a case is found where the walk cannot follow the join (an anti, right, full or cross join, which are "not yet followed"). Her decision.

**5.5 The `D-0322` list includes the column drop with the whole drop-gate machinery.**
G4 is about observations. A drop at an earlier place can remove a column that joins or plots need; the gate (`key_drop.py`) and the red lines (D-0460) exist to prevent that. This is a large part of the lineage code for an act that does not serve G4. Argued in A6 question 3.

**5.6 The bundle holds unaudited T1/T2 files next to the audit (G3).**
See A2. The README says what each file is. A reader who publishes `T2_data.tsv` publishes the removed observation. This does not follow from a decision; it is a built shape (the T3 file is the only audited table).

**5.7 The reason gate covers filters and drops but not the seed.** Minor. A6 question 4.

**5.8 Several `DECIDED, not built` labels are now wrong in the rule files** (the opening build is built; the aesthetic overrides are applied; `developer_raw_yaml` is gone) (collection §5.2). They make agents "take old things again" (D-0507). Verify before use. I only spot-checked: `opening_build.py` exists and is called (grep).

---

## A6. The questions that are really hers

Only questions that change what is built. Each: the situation, what the app does today, the options with what the user SEES, a "neither" option, then "Recommendation (mine)".

### Q1. What is ticked when the audit dialog opens?
**Situation.** `D-0316`: all places ticked. `D-0508`: tick low, near the original data. `D-0531`: the app cannot decide the scope.
**Today.** No dialog. The user picks "this plot only / all plots / all except".
**Options.**
- **A. Nothing ticked.** The user sees the outline and ticks. Slow but fully his act.
- **B. The earliest place of each branch ticked (the original-data tables that hold the column), named "starting point".** The user sees ticked lines and, beside them, the measured map of what that choice reaches and what stays.
- **C. Every place ticked (D-0316).**
- **Neither:** a first screen that asks "where do you want the change: only in this plot's table, in the tables before it, or in the original data tables?" (the user picks a level; the app ticks the places of that level; no default level).
**Recommendation (mine).** B or "neither". B respects D-0508 and shortens the work. It is acceptable under D-0531 only with two things on the same screen: the word "starting point" and the measured map. Without the map I recommend A. Reason: E1.

### Q2. How does the app tell the user that other entities' values changed?
**Situation.** `D-0501`: no per-table warnings about downstream effects. E2: removing an entity before a computing step changes all others.
**Today.** Nothing is shown (and the T3 filter does not change them at all, see 5.1).
**Options.**
- **A. Nothing** (D-0501 as read). The user sees a plot with changed values and no word.
- **B. One measured line per audit (and per result), from the comparison of original and audited result tables:** "values of other entities changed in 2 tables and 3 plots; rows removed: 1 (metadata_schema), 3 (...)". No advice on which place is right.
- **C. A per-table list of warnings.**
- **Neither:** the line is shown only when "Compare" is open.
**Recommendation (mine).** B. It is the "difference where applied" of D-0501, measured, with no warning list. Reason: A leaves a published number with an invisible cause; C is what D-0501 rejected.

### Q3. Does the audit keep the column drop at every place?
**Situation.** `D-0322`: filter, column drop, removal by key. The drop needs the key-drop gate and red lines (D-0460) at earlier tables.
**Today.** HOME drops only at the T3 table of a plot (`filter_and_audit_handlers.py` `_col_drop_to_audit`), where nothing is built after it, so the gate cannot refuse.
**Options.**
- **A. Drop at every place the walk offers (as decided in D-0358 and D-0460).** User sees "drop column" lines at tables and tiers, some red.
- **B. Drop only at the table a plot reads (what is built).** User sees the drop only in the plot's table; no red lines for drops.
- **C. No drop in the audit; the user hides a column in the table view only (nothing recorded).**
- **Neither:** the drop is a different thing, not in the audit but a setting of the published table, recorded in the bundle.
**Recommendation (mine).** B. G4 is about removing observations. A drop is a choice of what columns a published table has; it needs recording (so B, not C) but it has no goal reason to travel up the lineage, and A is the largest source of lines the user cannot tick. Her words of D-0450 ("do not get wrong results because we did not select the correct scope") are met in B because the drop cannot hurt a later step.

### Q4. Reshuffle (the jitter seed) and the "Plot Style" overrides: audit steps with a reason, or recorded only?
**Today.** Reshuffle writes a seed into `t3_plot_overrides` with no reason and no Apply (`home_theater.py:881`); the seed is exported (report, `t3_steps.yaml`, `effective_run.yaml`). The Plot Style panel is not mounted.
**Options.** A. an audit step with a reason; B. recorded in the audit record without a reason; C. not allowed in Audit mode.
**Recommendation (mine).** B. The seed does not change a number; it changes where points are drawn. It is recorded (so nothing is silent) and reproducible. A reason adds a gate with no scientific content. Her decision (D-0341 asks the same).

### Q5. The metadata join at T1: refusal or advice (`D-0510`)?
**Options.** A. keep the refusal "for now"; B. an advice only; C. nothing.
**Recommendation (mine).** B. Reason: A5 5.4. Her words "A I think for now - worse case we reverify after" allow the change.

### Q6. A deployment with no writable place for the user.
**Situation.** `D-0422`: the audit is saved in the session in the user's own place. Choice 5 (a deployment with no writable place) is not decided.
**Options.** A. the audit works in memory; the export is the only record; the screen says "this session cannot be saved; export before you leave". B. Audit mode is not offered. C. a temporary folder with a warning.
**Recommendation (mine).** A. The export is a browser download that works everywhere, and it is the thing that must reproduce.

### Q7. Where the entity stays: how is it shown after the step?
**Situation.** The map of A3 step 4 is a run of the audit copy. It costs a run per candidate (6 seconds on the demo). It needs the key column to keep its value.
**Options.** A. computed only after the user confirms ("recount after the build" is open in D-0508); B. computed before confirm for the ticked places, as a preview; C. both.
**Recommendation (mine).** C. A preview before confirm is what D-0450 asks ("a wrong scope must be seen before confirm"). The recount after is the proof that goes to the audit record.

### Acceptance check she can do on the demo (mine)
1. Remove the entity of plot `qa_population_zscore` at the place you choose. The map says where it is gone and where it stays; the plots that changed are named.
2. Open `qa_population_zscore`: the line says whether other entities' values changed. They did.
3. Remove the step with the one control; the original numbers return.
4. Export; open the bundle on another day; reproduce; the audit leg is "match".
5. Open `T2_data.tsv` of a table in the ticked cone: no entity.

---

## A7. What I did not check

- BLUEPRINT code and its spec (`D-0495`, seven-point check): not read.
- The documentation and help pages (good-practice page, user guide, `docs/`): I found no gotchas page by name; not read.
- The Gallery code and pictures (`D-0400`): not read.
- `home_theater.py` between lines I cite: I took the plot compare, the right panel and the opening call from the scout collection. I re-checked only lines I cite as verified.
- E1 and E2 use ONE entity (`10668076`) and the places listed. E1 does not test aggregated tables other than those shown, filters on a value other than the key, joins of the kinds "anti, right, full, cross" (none in the demo), or a key that is rewritten.
- The speed of `run_audit` on a large recipe: only the demo (about 6 seconds for a base build and three runs).
- Test status: no test suite was run.
- The recipe format part (`recipe_spec.yaml`, names pass): not studied beyond the collection.
- Whether the sessions of other users or the Compare pane share one run: not checked.
- `table_compare` semantic details (layers, tolerance) were not read beyond its header in the collection.

---

# PART B. Comparison with the Opus overview

**Part A was committed before part B was written: commit `a36bd0e5` ("docs(design): independent goals review, blind part A").** I opened the Opus files only after that commit. I have not changed part A. Where part A was wrong or incomplete, I say so below.

Opus files read (branch `study/whole-picture-goals`, commit `122334a3`): `WHOLE_PICTURE.md` part 0 and part 8 (questions 28, 29, 1, 2, 27, 4, 17, and the table at the start of part 8), `GOALS_REVIEW.md` (all), `DIFFERENCES.md` section C1 (to check its runs). I read no other file of that folder in this step.

What I ran in part B (read-only, same method as E1; `tmpAI/exp/e1.py`):
- **E3**: places `T1:MLST` and `T1:metadata_schema` (Opus's reading (a) of the default for a removal started from `mlst_bar`).
- **E4**: (i) the 13 tables that join the metadata (Opus's reading (b)); (ii) "remove from all the data" as built (every table holding the key at tier 1) with `QC_Reads_Anchor` and `Quast_with_metadata` unticked.
- A check of 36 `file:line` references of `GOALS_REVIEW.md` against the code, and a scan of ~120 quotes of hers (a quote followed by a D-number within 60 characters) against the evidence field of that ledger line (script `tmpAI/exp/quotes.py`).
- `table_compare.compare` on the E2 tables (`tmpAI/exp/out2`).
- The tests of the two branches (in their worktrees, with the main `.venv`).

## B1. Where we AGREE

1. The goals: the same G1 to G6 in substance. Both list the same companion goals (nothing silent, data agnostic, two kinds of person).
2. The scope is the user's (D-0531). Both reject the app choosing places. Both keep the dialog of places with ticks.
3. The central finding: **the effect at a place does not tell the effect at the results.** Both found it with runs. My E3 reproduces their numbers exactly: with `T1:MLST` + `T1:metadata_schema`, 13 plots change and the entity stays in 7: 4 unchanged, 3 with source, year and country emptied (`miaou`, `assembly_quality_dotplot`, `qc_reads_horizontal_barplot`). My E4 (i) reproduces their (b): the 13 tables that join the metadata, 13 plots change, nothing emptied, the entity stays in the 4 plots that never meet the metadata.
4. A reading of the recipe cannot say what happens in a table where no step is written; only a run can. Both say so; both hold the untick branch's sentences as false.
5. The measured effect before Confirm (their Q28 (a), my Q7 C and A3 step 4). Their (a) is my proposal.
6. What to keep, change, replace, remove in the built code: the same list in substance: replace the T3-only node store and `audited_frame`, replace the propagation modal, replace the trash icon by "Remove step", remove the join fork of mode 2, wire `walk`, `audit_copy`, `audit_run`, `table_compare`, keep the opening build, the reason gate, the key check at export.
7. The audit at T3 only is wrong for a computation over all entities. They reasoned it ("a removed entity still counts in a mean computed earlier"). I measured it (E2).
8. Both hold that `task/remove-from-all-ticked` must not be merged as it is and that `apply(..., ticked=)` is the part to take.
9. Both put the BLUEPRINT and documentation items after HOME; both point out that old texts and rule labels are stale.

## B2. Where we DIFFER

For each: the two positions, who is right, the evidence. "Right" means on the evidence I have.

### B2.1 The claim in `GOALS_REVIEW.md` 4.4 about her case of D-0499
- **Opus** (4.4, last bullet): with "remove from all the data" and the places of the 3 quality plots unticked (`QC_Reads_Anchor`, `Quast_with_metadata`), "the entity stays in exactly those 3 plots, with its metadata, and 14 plots change".
- **Me** (E4 ii): with "remove from all the data" **as built and decided** (a step at tier 1 of every table that holds the key, 27 tables) and those two places unticked, the entity is in **none** of the plots and **all 17** change, because the source tables `FastP`, `Quast`, `Bracken`, `metadata_schema` are still ticked and their left joins no longer have the row. `QC_Reads_Anchor` and `Quast_with_metadata` hold 0 rows for the entity.
- **Why the two differ:** `DIFFERENCES.md` C1 shows their run used a different list: under their reading (B), "remove from all" is **19** places (the 13 joins and the first table of 6 branches), and the 8 original tables "still hold it at tier 1". That is not the option of `D-0416` point 1 ("It reaches every table that holds the key column, also a table no plot reads": "1. yes") and not the library (`remove_from_all.describe` reaches 27). So the sentence in 4.4 is true only for a variant that nobody decided.
- **Right:** me, for the option as decided and built. For her case under the decided option she must also untick the upstream sources (and then, in their own (A) run, the entity stays in 9 plots). A reader of 4.4 would believe that two unticks give her case. They do not. This matters: it is the one case she gave in her words (`D-0499`).
- Label: verified by run (E4 ii). One entity, one list of places.

### B2.2 Column drops (their question 29)
- **Opus:** (a) no: the audit removes observations only; a column that must not appear is removed by the recipe author. Reasons given: G4; the check of key columns is no longer needed.
- **Me** (A6 question 3): keep the drop, but only at the table a plot reads (what is built), recorded with a reason.
- **Argument (why and how, D-0532):** `D-0500`: "the user might not be the author". A user who may not touch the recipe and who must publish a table without a column (a name, an internal id) has two ways under (a): ask the author, or open the exported TSV and delete the column by hand. The second is outside every record: not reproducible, not transparent (G1), and it is the exact kind of silent change the app exists to prevent. Under (b) the drop is a recorded step with a reason. A drop at the plot's own table cannot break a later join, so the large machinery of the drop gate (`key_drop.py`, red lines of D-0460) is not needed for it. Opus's "For (a)" includes that the check "is no longer needed": that is an argument from less code, which is not an argument by her rule.
- **Right:** I think the merit is on my side, but this is a real choice and the evidence is reasoning, not a run. Opus did show her words against its own recommendation (it lists `D-0322` under "Reopens").
- Label: reasoned.

### B2.3 The Reshuffle (their question 17)
- **Opus:** (c) remove it from HOME. Two reasons: a new arrangement removes no observation (G4); a reader cannot tell it was picked among several (G3). A technical fact: `bake_plot_seeds` writes the seed into the plot's layers of the exported recipe copy, which the decided audit recipe forbids (D-0332, D-0040).
- **Me:** record the seed in the audit record without a reason (A6 question 4).
- **What I checked:** the technical fact is correct: `app/modules/plot_seeds.py:156` `bake_plot_seeds` writes into `layers`; it is called at `app/handlers/export_handlers.py:1567`, inside `if wants_mode2` (`:1559`). I missed it in part A. But the seed also has another carrier today: `effective_run.yaml` holds `seeds_per_plot` and `seeds_per_layer` (`export_handlers.py:1675-1677`). So "an audited reshuffle cannot be re-run" is a consequence of removing the fork, not a hard blocker: the seed can live in the audit record or the run file and be read at the re-run.
- **Right:** neither is proven. Opus is right that a home for the seed must be decided before the fork is removed; I do not agree that this forces option (c). Her words (`D-0341`: "A - but then we need to be able to add it as a step at the correct place in audit"; "not critical for now") are on the other side; Opus shows them. I would put it to her as the choice it is and not rank it.
- Label: read at the lines named; the rest reasoned.

### B2.4 The default ticks (their question 1)
- **Opus:** recommends (b): the end of tier 1 of each table that joins the metadata (13 lines on the demo). I verified its numbers (E4 i).
- **Me** (A6 Q1): B (a named starting point) with the measured map, or "neither".
- **Where we really differ:** a little. (b) is a rule of the structure of the recipe ("tables that join the metadata"; on a branch that never meets the metadata, "the first table its results read", a second rule). (a) is a rule of the structure of the lineage. Both are defaults of the app. E3 and E4 (i) show that on the demo (b) is the safer start (nothing emptied) and that under (b) 4 plots still show the entity: so under either default only the measured map tells the user the truth. I accept (b) as the recommendation if the screen names it as a default and shows the map, as Opus says.
- **One thing to add:** under (b) the audit recipe holds the same step 13 times; Opus shows this as "Against". Under D-0531, the user may think that "13 places" is the app's decision. The screen text must say "starting point".
- **Right:** no real conflict. Label: verified by run for the numbers.

### B2.5 The rule that every join is tier 1 (ST05, D-0510, their question 27)
- **Opus:** the recipe check already refuses every join outside tier 1 (ST05); the ledger fact put to her in D-0510 ("the check has no such rule") was wrong. Question 27 stays open, no recommendation.
- **Me (part A):** I treated D-0510 as "enforced for now" and, in A5.4 and A6 Q5, argued the refusal should be an advice, because the audit's reach comes from the walk, not from where the join sits.
- **What I checked:** Opus is right. `libs/utils/src/utils/recipe_check.py:714-715` gives `ST05` for any action of `TIER1_ONLY` (`libs/utils/src/utils/action_names.py:66`: `JOIN`, `JOIN_ASOF`, `JOIN_WHERE`) in tier 2 or tier 3. It covers every table, not only the metadata.
- **Correction of my part A:** I **withdraw my recommendation to make the rule an advice (A6 Q5 and A4)**. I wrote it without knowing the rule's breadth. With every join in tier 1, "the end of tier 1 of a joined table" is one unambiguous place that has the metadata and every join of the table: this is what E4 (i) relied on, and it is a real argument for the rule (it keeps the places of the lineage few and clear). The rule still goes further than her words: she decided it for the metadata join (D-0510), and wrote "other joins could be used after" and "the other data tables can be used in later joins" (D-0523). That is their question 27. I agree it needs no recommendation now.
- Label: verified at `recipe_check.py:714`.

### B2.6 Things Opus did not state that I found
- **The bundle holds unaudited tables.** `export_handlers.py:1409` writes `<table>/T1_data.tsv` and `:1431` `T2_data.tsv` from the stored ORIGINAL tables; only `T3_data_<plot>.tsv` is audited (`:1467`). The README line says what each is (`:1914`), but a reader who takes the T2 file publishes the observation the user removed. `GOALS_REVIEW.md` G3 point 2 says "yes" for what the screen shows is what the export holds; it considers plots and the T3 file, not these files. Their path (step 10) speaks of "the audited results" and does not say the tables of the audited part follow the audit. This is a condition for G3 ("tables it can trust").
- **A measured number for the computation over all entities** (E2: 41 of 41 other samples differ; max 0.064 on a z-score near 1.8) where Opus has an argument. It does not change a recommendation; it makes the evidence harder.
- **`table_compare.compare` already gives the line they propose.** On the E2 tables with the key `sample_id`: `paired.n_paired=41, n_rows_changed=41`, one row removed (`sample_id 10668076`). So "the values of other observations change here" can be read from the library that exists; no new method is needed (their 4.4 says it uses layers 1 and 3).

### B2.7 Their pre-answers to ten questions
- **Opus:** "my reading of your goals answers questions 10 to 12, 16, 18 to 22, 24 and 25 (you may object)" (part 0.5, table of part 8). In the match list and the build order a build may then follow.
- **Me:** this turns silence into consent. `decision_compliance.md` rule G: "a default is never a decision". The text says "you may object" and "my reading", so nothing is claimed as decided, but the structure asks her to object to ten things to keep them from being built, in a document where she is already asked for five questions first. I would list them as a short block "I propose to build these ten as written unless you say no, and nothing is built until you say yes".
- **Right:** a matter of form. I label it a risk, not an error.

### B2.8 Question 28: "withdrawn" and still an option
- Part 8 says: the first version proposed the app choose the places from the results; "Your words of D-0531 rule it out... It is not an option any more." The same question lists as option (b): "Results first: the app proposes places that you see and change". It is a softer form of the withdrawn thing: the app picks the ticked places; the user may change them.
- Does every option leave the scope to the user? (a) yes. (b) yes **if** it is named a proposal and the user can change every place; it is the same status as a default tick in (a) and (b) of question 1. (c) yes. (d) yes. So the options do not break D-0531. But the text that says "not an option any more" contradicts the presence of (b); a reader will not know which is true. The "Reopens" list of (b) is complete by my reading (D-0508, D-0194, D-0316, D-0415 A, D-0022, D-0501/D-0318 as in (a)). The list of (a) is complete: D-0501 second part, D-0508 second part, D-0318 extended.
- Is any option argued by cost, delay or by her own words? (a) no. (b) "two lists to keep in agreement" is a design argument. (c) "the dialog you decided, with nothing added" argues by her own decision: it is listed as "For", and "Reopens: nothing". An option that is argued "for" because it does not reopen is a use of the "reopens" label as an argument. It is stated, not hidden, and the recommendation is (a). Small.
- Question 29 (a) "For: ... the check of key columns and its rules are no longer needed": an argument by less code (B2.2). Question 17 (c) "For": the figure a reader sees is the one the recipe fixes: a merit argument.

### B2.9 The use of their runs
- All their numbers on the demo are three runs, one entity each, places listed by hand. They say so in 0.3, 0.6, Q1 and part 9. I reproduced the numbers for E3 and E4 (i).
- **Is anything stated as proven beyond that?** Yes, two things:
  1. The sentence of 4.4 about D-0499 (B2.1): not what the decided option gives.
  2. Q1 (a), "Also run, on a small part of the demo with a summary table made from a join": it states that the removed entity appears in the summary as a new group with an empty country and year, "10 rows instead of 9, the total still 42, although nobody ticked it". The limits are given ("two joins, the summary table was emulated, because the app does not have it yet"). I did not reproduce it: **not verified by me**. It is the reason for recommending (b) over (a) in the case of derived tables; the recommendation stands on the demo numbers even without it.
- "Four plots never meet MLST or the metadata": true for `amr_heatmap` (reads `ResFinder`), `phenotype_genome_length_fragmentation`, `qa_l50_integer`, `qa_sequence_type_missing` (E3). Right.

### B2.10 Quotes of hers
Of ~120 quotes followed by a D-number, ~105 are in the evidence field of the line cited. The others I read one by one: they are names of buttons or labels used inside quotation marks (`table changed`, `picture changed`, `this result only`, `remove from all the data`, `Web Demo (web-demo)`), a quote that Opus itself marks as the review session's report (D-0496: "we can exclude form 4 and I guess 5", in the decision field), a text of the decision field (D-0344), and `"We do not do half fixes."` which Opus marks: "in the goal text that you approved with '1. ok.' (D-0125); who wrote that text is not stated". I found **no quote that is made to say more than her words**, and none taken from a bracket and presented as hers. Quotes were not checked when no D-number follows within 60 characters.

### B2.11 Claims about the code
Of 36 `file:line` references, the ones I opened are all correct in substance. Line numbers are within 3 to 5 lines of the code, except `t3_audit_engine.py:771-791` for `audited_frame`, which is at `:799` now (28 lines). Claims I checked beyond the lines named: ST05 (B2.5); `bake_plot_seeds` (B2.3); the warning "T3 ghost save failed ... will not survive a page refresh" (`audit_stack.py:1049-1058`) is real; session restore with an edited recipe is a warning and not a refusal (`session_handlers.py:594-602`); the 13 tables that join the metadata (counted in the recipe); the table of 17 plots to targets (the entity stays in 7); the mode-2 fork (`t3_translator.py:197`, `export_handlers.py:1559-1569`); the live parts of the lineage library. None wrong.

### B2.12 Is part 0 readable by her alone?
Mostly. For: short paragraphs, a table "today you see / as decided you would see / still missing", a drawn dialog, a route of nine steps with what she can do after each, "words used here". Against: about 3000 words; 26 bare codes `G1` to `G6`, `E1` to `E7` in tables she must keep in mind; 15 ledger numbers in the sentences (the earlier reader check asked for none in the sentences; they are mostly after quotes, as a source mark); the questions she must answer are named by number ("question 28", "question 1") and live in part 8, 400 lines further; in part 8 question 28 carries 20 D-numbers in 25 lines. A reader who is not a developer will understand the path and the sketch; she will find the questions harder than the path. The words "tier", "propagation", "reach" are defined before use.

### B2.13 What Opus did not run
Their `GOALS_REVIEW.md` section 9 says: "Runs: none by me." So the second pass relied on the first pass's runs and the reviews. It states this clearly. My E1 to E4 add runs on the same demo; they agree with theirs on all numbers I could check.

# PART C. The match list, row by row (red team)

I read `MATCH_LIST.md` after part B. For each row I tried to find a reason the verdict is wrong: that it depends on an open question of hers, that it has the app decide the scope, that it breaks a goal, that the code is not what the row says. **SURVIVES** = the verdict stands after the attempt. **DOES NOT SURVIVE** = it should be different (I say what). **NOT SURE** = I cannot decide it from the evidence or it depends on a question of hers that the row does not name.

What I ran or read for part C:
- Branch `task/home-filter-follows-table` (`7981a569`): its diff read; its 5 test files run in its worktree: **88 passed** (134 s). I did not mutation-test it and did not read all the code.
- Branch `task/remove-from-all-ticked` (`95b6285e`): the diff of `remove_from_all.py` read in part; `libs/utils/tests/test_remove_from_all.py`, `test_remove_from_all_unticked.py` and `app/tests/test_remove_from_all_demo.py` run there: **125 passed, 1 skipped**. `apply(..., ticked=...)` takes `ticked` as a required keyword (checked in the signature).
- `table_compare.compare` and `audit_run`/`audit_copy`: run through E1 to E4 and the E2 comparison (all worked on the demo).
- The check for the duplicate result id: loaded the demo, added a second entry with an existing plot id in another group, ran `check_recipe`: **no new code appears** (the loaded raw already gives T08 for a root `plots` key, because the loader flattens it; so the probe is weak: it shows no code for the duplicate, not that a raw recipe passes). The task text `RESULT-ID-TWICE-NOT-REFUSED` (tasks.md:963) says the same and cites `recipe_tiers.py:152-160`.

## C1. Section 0 of the match list: "KEEP builds that can start or be merged now"

| # | Row | Opus | Mine | Evidence and reason |
|---|---|---|---|---|
| 0.1 | Slice 0, the records agree | KEEP | SURVIVES | No code. The records have more drift than listed (rule files say "DECIDED, not built" for the opening build, which is built: `run_opening` is called at `app/handlers/opening_handlers.py:124`; and the D-0363 conflict). Correcting them cannot break a goal. |
| 0.2 | Merge `task/home-filter-follows-table` | KEEP | SURVIVES | 88 tests pass in its worktree. The key is the table viewed (`viewed_table`), not the plot; two plots on one table share it; a plot with its own tier 3 steps is told apart. It follows `D-0506` ("the filter is associated to the table and not the plot"). It does not depend on an open question. Not mutation-tested by me. The row says KEEP means the decisions match, "not that the code is right": I add that its tests pass. |
| 0.3 | Refusal of a result id written twice | KEEP | SURVIVES (weakly verified) | My probe found no code for a duplicate id (above). Serves E1 (no silent error). Independent of every open question. Under form 3 (Q2) the rule changes its words, not its need. |
| 0.4 | Remove from all: write at the ticked places; no sentence about unticked tables; remove the "may stay" sentences | KEEP | SURVIVES as a library step; with one condition | `apply(..., ticked=)` is verified (125 tests). Why not say anything about unticked tables: E1 shows a recipe cannot say it. **The condition:** this must stay a library step. If it is the end of the matter, the user never learns where the entity stays (A5.3). The measured map (A3 step 4) must follow. The row says "no screen yet". |
| 0.5 | The good-practice page | KEEP | SURVIVES in part | The gotchas, the naming rule, the limits (D-0461, D-0498, D-0508, D-0486) are decided and independent. **The audit-folder paragraph (D-0423) describes a folder that is not built and whose place in a deployment with no writable user place is not decided (D-0422, choice 5).** It should wait for the build. |

## C2. Section 1: the decisions that lead to a build

| Row | Opus | Mine | Evidence and reason |
|---|---|---|---|
| Audit recipe: copy, second list, id, reason, `audit_of` (D-0102 ...) | KEEP | SURVIVES | `audit_copy.add_step`, `integrity_errors` run in E1 to E4. Note: "Depends on: —" is not complete: the form (author's parts untouched, D-0332, D-0040) is in tension with `bake_plot_seeds` (B2.3), so Q17 decides where a seed lives. The decision stands; one build detail depends on Q17. |
| Fingerprint, `audit/` folder in the user's place, a hand edit refused | KEEP | NOT SURE (in part) | Fingerprint and refusal: SURVIVES. The folder "in the user's own place" is not decided for a deployment with no writable place (D-0422 choice 5, my Q6). The row says "—". |
| Audit log always exported, with what was shown | KEEP | SURVIVES | Existence yes (D-0478). What it holds depends on what the dialog shows (Q28): the row says so. |
| Export: two ticks, original and audited part, data once, original recipe | KEEP | SURVIVES, with a missing item | The tables of the audited part must follow the audit: `T1_data.tsv`/`T2_data.tsv` are unaudited today (B2.6). Not a reason to change the decision; it is a requirement of it. |
| Original and corrected plot both in the export (D-0147) | KEEP | SURVIVES | G3. |
| "Remove step" (D-0314) | KEEP | SURVIVES | `audit_copy.remove_step` exists (`audit_copy.py:245`); no such control in the app (grep). |
| Sessions of another recipe or older form refused (D-0312, D-0317, D-0362) | KEEP | SURVIVES | Q26 is named. |
| The user chooses the places; nothing written that is not ticked; one automatic placement (D-0093, D-0355, D-0053, D-0022, D-0531) | KEEP | SURVIVES | It is her rule of D-0531 and D-0355. |
| The dialog: one line per distinct table with reach; tables no result reads are lines | KEEP | SURVIVES | The walk is PROVISIONAL in its grouping (P1 of `lineage_walk.py`), not a decision of the owner; the list that the walk offers is the app's menu of places. The normal dialog offers lineage and join-linked places; tables with the same key and no join are info only (`Walk.outside`), tickable only in "remove from all" (D-0498). That is her D-0415 A/B split. |
| "Tick low" and the propagation | NOT SURE | NOT SURE | Agree. |
| No per-table warnings about downstream effects (D-0501 first part) | KEEP | **NOT SURE** | `D-0501`: "if there is then an aggregation it is normal that the count differs" and "no per-table warnings". Their own recommended dialog (Q28 a) and mine (Q2 B) add a per-result line "the values of other observations change here". Their Q28 (a) says "Reopens: D-0501 in part". A KEEP that "every option of the open questions keeps" (their own definition) is contradicted by their own question. The two readings can be reconciled (a measured difference at the result, no per-table lecture; `D-0501` itself said "show the differences where applied") but that is a choice to confirm with her, not a KEEP. |
| Count of rows at the plot removed; check where applied (D-0501 second, D-0508) | NOT SURE | NOT SURE | Agree. |
| "Table changed" and "picture changed" per plot (D-0318) | KEEP | SURVIVES | Needs the run of the audit copy for "picture changed": built (`audit_run.PlotRun.affected`). |
| Remove from all: off, explicit, list first, data-agnostic words, may untick (D-0415 B, D-0416, D-0499, D-0500, D-0498) | KEEP | SURVIVES | Verified in the demo test: 27 of 28 tables reached; the entity is in none after (the test and E4 ii). Note that Opus's `DIFFERENCES.md` uses a 19-place variant of "remove from all" that D-0416 point 1 does not say (B2.1). |
| Two lists of keys (D-0313) | KEEP | SURVIVES | Not built (HOME uses join keys only: `session_manager.py:125-135`); independent. |
| Warning when a value does not match one to one between ticked places (D-0203) | KEEP | NOT SURE | A per-place downstream warning of the kind D-0501 rejects; the row says "between ticked places only" (C14 of their study). The two decisions pull; no later decision says which wins. |
| The walk: places from the plan, rename followed, red lines YET | KEEP | SURVIVES | The library runs on the demo through `remove_from_all` and the drop check. The row notes `walk()` is called by tests only. Its grouping P1 is a builder's PROVISIONAL choice. |
| Audit steps: filters, removals by key, column drops (D-0322) | NOT SURE | NOT SURE | Agree. My view: keep the drop only at the table a plot reads (B2.2). |
| Key column drop refused by place; declared key follows; uncertain drop refused | NOT SURE | NOT SURE | Agree: needed only if drops travel up the lineage. |
| Reshuffle written as a step (D-0341) | NOT SURE | NOT SURE | Agree (B2.3). |
| No plot-style change for now (D-0120, D-0145) | KEEP | SURVIVES | Unmounted code (`audit_stack.py`, `home_theater.py:2340` comment) goes with removal. |
| A table can be a result (D-0485...) | KEEP | SURVIVES | The form is Q2. |
| Recipe form with derived tables (D-0516...) | NOT SURE | NOT SURE | Agree. |
| Every join with the metadata in tier 1; the three kinds of table (D-0510, D-0523, D-0513) | KEEP, "Built (ST05)" | NOT SURE for the breadth, SURVIVES for the metadata | ST05 refuses any join in tier 2 or 3 of any table (B2.5), wider than the decision (the metadata join). Her words "other joins could be used after" make the breadth question 27. The match list notes Q27 as "later". It should say the build is wider than D-0510. The demo needs neither. |
| Opening build, Exploration, "Table to view", filters cleared when the table changes (D-0326 ...) | KEEP | SURVIVES | Code read and used in E1 to E4 (the opening stores the tables `run_audit` reuses). One edge: after `home-filter-follows-table` is merged, "cleared when the table changes" holds and "when the plot changes" does not; the row's words should be updated. |
| A table no plot reads can be viewed and exported (D-0457) | KEEP | SURVIVES | Export writes `T1_data.tsv` for them (`export_handlers.py:1501`). |
| The report by groups | NOT SURE | NOT SURE | Agree. |
| The names pass | KEEP | SURVIVES | Timing after Q2: stated. |
| BLUEPRINT is an IDE ... never replace by mistake | KEEP | SURVIVES | Decision stands. I did not read the code. |
| The lineage picker | NOT SURE | NOT SURE | Agree. |
| Upload of a recipe refused under an existing name... | KEEP | SURVIVES | Not examined beyond the row. |
| First pass: the app chooses the places from the results | DROP | SURVIVES | Correct. But note Q28 (b) is a softer form (B2.8). |

## C3. Section 2: the builds

| Build | Opus | Mine | Evidence and reason |
|---|---|---|---|
| Filters panel (D-0503, D-0504) | KEEP | SURVIVES | Its tests are in the 88 that pass (the between test is among them). |
| Two sentences of the data preview (D-0488) | KEEP | SURVIVES | Not re-run. |
| Opening build | KEEP | SURVIVES | Used in E1 to E4. |
| Export writes every table no plot reads | KEEP | SURVIVES | `export_handlers.py:1501`. |
| Lineage library | KEEP | SURVIVES | As above. |
| Drop gate | NOT SURE | NOT SURE | Agree. |
| `table_compare.py` | KEEP | SURVIVES | Run: `compare(original, audited, [("sample_id",)])` returns `n_rows_changed=41`, one row removed: the measured line exists. |
| `audit_copy.py` | KEEP | SURVIVES | Run in E1 to E4 (`start_audit`, `add_step`). |
| `audit_run.py`, `compose_candidate_plan_book` | KEEP | SURVIVES | `run_audit` was run many times in E1 to E4; a base build plus three audit runs took about 6 s on the demo (the first measurement, with `time`). `compose_candidate_plan_book` not run by me. |
| `remove_from_all.py` library | CHANGE | SURVIVES (CHANGE) | The change is as in C1 row 0.4. |
| Branch `home-filter-follows-table` | KEEP | SURVIVES | C1 row 0.2. |
| Branch `remove-from-all-ticked` | CHANGE | SURVIVES (CHANGE) | 125 tests pass; its `_flow` / `unticked_places` sentences are the part two reviews found false. I read the `_flow` code: it decides by the `how` of each join and by the first ingredient only; an inner join on a column that is not the key, and a later row-dropping step, break it (as the evidence file shows on the demo `ST22_Anchor`). |

## C4. The planned slices and the tasks

| Item | Opus | Mine | Reason |
|---|---|---|---|
| Slice 0, 1, 11 | KEEP / done | SURVIVES | As above. |
| Slice 2 (recipe upload code) | NOT SURE | NOT SURE | Not examined. |
| Slice 3 (one form, HOME's plot and table from the run) | NOT SURE | NOT SURE | Agree, but I add the reason in the evidence: E2. Keeping the T3 filter beside the run would leave two audits that give different numbers. It is needed under every option. The row's dependencies on Q26, Q29, Q17 are right for details only. I would say KEEP for the decision to replace, NOT SURE for the details. |
| Slice 4 (the dialog), 5 (export of an audit), 6, 7, 8, 9 | NOT SURE | NOT SURE | Agree. Slice 5 must include the audited T1/T2 files (B2.6). |
| Slice 10 | mixed | SURVIVES in part | As C1 row 0.5. |
| `AUDIT-VIEW-1`, `AUDIT-REPLACE-1`, `AUDIT-RECIPE-RULE` | KEEP | SURVIVES | E2 is the evidence for the first. |
| `AUDIT-HISTORY-LOG-1` | CHANGE | SURVIVES | D-0478. |
| `AUDIT-DIALOG-PREVIEWS`, `AUDIT-WARN`, `AUDIT-ERROR-Q`, `AUDIT-ADVICE` | NOT SURE | NOT SURE | Agree. |
| `AUDIT-USABILITY-1` | KEEP | SURVIVES | G5. |
| `AUDIT-PANEL-UNTESTED` | CHANGE | SURVIVES | |
| `AUDIT-MESSAGES-PLAIN-1` | KEEP | SURVIVES | Not examined. |
| `EXPORT-MODES`, `EXPORT-RECIPE-REFUSE-1`, `SESSIONS-MANY-DATASETS`, `DATA-IMPORT-OVERWRITE` | KEEP / NOT SURE | SURVIVES / NOT SURE | Not examined. |
| `BP-COMMENTS-1` | KEEP | SURVIVES | D-0495. Not examined in code. |
| `ENGINE-T3-READER` | NOT SURE | NOT SURE | Q2. |
| `RESULT-ID-TWICE-NOT-REFUSED` | KEEP | SURVIVES | C1 row 0.3. |
| `DEMO-USERS-1`, `DEMO-BRANCH-PLAN-1` | KEEP | SURVIVES | Not examined. |

## C5. What the match list should have judged and did not

1. **The unaudited T1/T2 files of the export** (`export_handlers.py:1409, 1431`): a build that serves G3 badly; no row.
2. **The join breadth of ST05** against D-0510 (C2).
3. **The import leg for the audit steps** is always `not_checked` (`bundle_importer.py:186-194`). No row. It is part of G1 reproducible (a bundle that cannot check the audit it carries).
4. **The deployment with no writable user place** (D-0422 choice 5): a decision not taken that three KEEP rows depend on.
5. **The built propagation modal** and its `Apply to: This plot only / All plots / All plots except` (`filter_and_audit_handlers.py:1097-1101`): judged in `GOALS_REVIEW.md` ("replace") but not a row.
6. **D-0203 against D-0501**: two decisions that pull; the list has one KEEP and one NOT SURE and no note that they conflict.
7. **Screen texts that say "samples" and "for now"** (`home_theater.py:1482`, `filter_and_audit_handlers.py:674-676, 997, 1002-1007`): against D-0512 (data agnostic); in the review text, not in the list.
8. **`export_include_reproducibility` and the mode-2 fork** as a build to remove: in the review, not a row (only `EXPORT-MODES`).

---
