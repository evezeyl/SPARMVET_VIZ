# Opus signs v2: my answer to AGREED_AND_OPEN_v2

I read v2 in full. Code: my worktree, at `dev` `febc506f` (merged).

## 1. G1 to G30

I sign G1 to G24 and G26 to G30.
- My four wordings (G1, G7, G11, G17) went in as I meant them.
- My X1 went in as G27; only its last sentence changes, with the B1 result (section 5).
- I re-checked the numbers I could: the lines of `opus_runs.out` that G26 cites (2346-2348 and 4270-4272), G15's run R2 (lines 2349 and 4273), and G6's grep.

**G25: I sign it only with this replacement.** Its sentence "the place list (the walk), the audit copy and 'Remove from all the data' are library code only" is not exact. No `app/` module imports `lineage_walk` or `LineageIndex` directly. But `utils.key_drop` does (`key_drop.py:51`), and HOME calls `key_drop` live. Replacement:

> **G25 What is on screen today, and what is only in the library.** Today a step is written at the finished table of one plot ("this plot only / all plots / all plots except": `ui_implementation_contract.md` 12g.4).
>
> From these libraries the app calls three things today:
> - The rule of a key drop (`utils.key_drop.DropGate`), which builds the walk's lineage index for a drop (`key_drop.py:51`). HOME calls it when a column drop is sent to the audit (`filter_and_audit_handlers.py:938`) and when a session is restored (`session_manager.py:150`, called at `session_handlers.py:673`). It uses the engine's plan book that HOME composes (`home_theater.py:379-383`).
> - The engine's guard on every build, which refuses audit steps in a recipe that is not an audit copy (`orchestrator.py:80-95`).
> - The audit parts of the cache keys (`cache_keys.py:69`).
>
> Library only (no code of `app/` calls these outside tests):
> - the list of places for a filter (`lineage_walk.walk`);
> - `start_audit`, `add_step` and `remove_step` (called only by `plan_composer.compose_candidate_plan_book`, which no screen calls);
> - `remove_from_all`, `table_compare` and `run_audit`.
>
> "Remove from all the data" as built (`remove_from_all.py:292-307`) accepts any subset of the 27 places the demo offers, with no check for nested places; `ticked=None` writes every reached place.

Evidence: grep of `app/`, outside tests. Imports of `key_drop`: `filter_and_audit_handlers.py:37`, `session_manager.py:46`. Imports of `audit_copy`: `cache_keys.py:69`, `build_failure.py:28`, `plan_composer.py:48`. No import of `lineage_walk`, `remove_from_all` or `table_compare`.

## 2. The half page and Q1 to Q8

Every sentence of the half page is true as written; I need no change there. I checked every quote of hers against the ledger's evidence field. All are exact, except Q5's quote on zero (it is not a fit there; R3 below), and Q4's quote of D-0550, which is not her words (R4).

Four replacements, plus one addition:
- **R1. Q1, "What exists only in the library (not on screen)."**
  - Replace "The list of places that hold the column: you can tick any of them, nested or not. "Remove from all the data" writes one step per place (27 on the demo)."
  - With: "The library lists every place that holds the column, nested or not, and nothing in it stops a nested choice; no screen shows that list. "Remove from all the data" (library only) writes one step per place it is given; on the demo it offers 27."
  - Why: no screen lets her tick anything today.
- **R2. Q6, "What you see on screen today."**
  - Replace "The audit has one control, "Remove step": you pick a step and remove it (D-0314)."
  - With: "Each step has a bin that removes it together with its copies on the other plots (`audit_stack.py:531-533`). Decided, not built in that form: one control, "Remove step", which removes the step you pick (D-0314)."
  - Why: that is what the screen does today.
- **R3. Q5, "Against (b)."**
  - Delete "and "the 0 is the signal that its not the correct place to choose where to remove" (D-0501)".
  - Why: it speaks of the place where a step is written, not of a note on a derived place, and she revised it later: "I do not understand why zero means the wrong place" (D-0508).
- **R4. Q4, "What the two agents think."**
  - Replace "(D-0550: "to be asked once")".
  - With: "(D-0550, in its "NOT decided" part, which is not her words: "a reading of the review session, to be asked once when the plan is checked")".
  - Why: in quotation marks it reads as her words.
- **R5. Q3, option (c)**, add what she would see: "You would see one more key in each recipe that names the default place of each original (12 originals on the demo), and the recipe check refusing a named place that is not in that original's tree."

Otherwise:
- Each question is fair to both readings and has "neither".
- No cost or delay argument appears.
- My lean is stated truly ("Opus does not lean" in Q1).

## 3. B1 to B3

- **B1 (the nested pair): RUN.** Script `opus_b1_run.py`, output `opus_b1_run.out` (this folder). It builds a small temporary recipe from the tests' staged world:
  - source A (sample_id, group, value: 10, 20, 30, 40), source B, and the join J = A + B;
  - J's tier 1 computes `value_mean`, the mean of `value` over ALL rows, after the join. This step lies between the upper place `T1:A` and the lower place `T1:J`.
  - Three audit copies remove the entity s1: upper only, lower only, and the nested pair.
  - Result (section 5): the nested pair equals the upper place alone and differs from the lower place alone. G27's general claim is now a fact.
- **B2 (the exported tier 1 files): not run.** It needs three exports and a comparison of files. It still holds by construction: under (c), no step is written at the metadata or at the originals.
- **B3 (the smallest number of steps for her case under R1): settled by reading.**
  - The places of her case, with nothing nested (run R2), and the trees each lies in, from my map: `FastP_with_metadata` {FastP}; `Bracken_with_metadata` {Bracken}; `ResFinder_with_metadata` {ResFinder}; `MLST_with_metadata` {MLST}; `ST22_Anchor` {FastP, ResFinder, MLST, VirulenceFinder}; `AR1` {MLST, VirulenceFinder}; `QA_AMR_per_sample` {ResFinder}; `QA_fanout_exhibit` {ResFinder, VirulenceFinder}; `QA_population_zscore` {Quast}; `T2:ResFinder` {ResFinder}; `T1:QA_L50_integer` {Quast}. Each of the first nine also lies in the metadata's tree, as do `QA_year_types` and `QA_aggregated_no_key`. The four Summary-family tables lie only in their own tree.
  - APEC has no key, so its tree does not count (G5).
  - If the metadata's tree does not count, the minimum is exactly **5** steps. The 5 ResFinder places must go in 5 different steps, and the other places fit among them. Example:
    - step 1: `ResFinder_with_metadata`, `MLST_with_metadata`, `FastP_with_metadata`, `QA_population_zscore`;
    - step 2: `ST22_Anchor`;
    - step 3: `QA_AMR_per_sample`, `AR1`, `T1:QA_L50_integer`;
    - step 4: `QA_fanout_exhibit`;
    - step 5: `T2:ResFinder`.
    - `Bracken_with_metadata`, the two metadata-only tables and the four Summary-family tables go in any step.
  - If the metadata's tree counts, the minimum is exactly **11**. The 11 metadata places must go in 11 different steps; `T2:ResFinder`, `T1:QA_L50_integer` and the Summary-family tables fit among them.
  - So in Q1, "These are lower bounds by reading" becomes: "These are the smallest numbers: 5 steps, or 11 if the metadata's own tree counts (worked out by hand from the trees each place lies in)."

## 4. Closing line

I sign AGREED_AND_OPEN_v2.md with these 8 replacements:
- G25;
- R1 to R5 (Q1, Q6, Q5, Q4, Q3);
- in Q1, the exact minimum of B3 (5 or 11);
- in G27, the B1 result (section 5).

## 5. B1 result (run)

The first attempt waited 20 minutes with the load above 10 and did not run. The second attempt started at load 9.84. Output: `opus_b1_run.out`.

| Audit copy, removing the entity s1 | J's table | `value_mean` |
|---|---|---|
| upper place only (`T1:A`, before the mean) | s2, s3, s4 | 30 (the mean without s1) |
| lower place only (`T1:J`, after the mean) | s2, s3, s4 | 25 (the mean with s1's value) |
| the nested pair (both) | s2, s3, s4 | 30 |

- Nested pair = upper only: True.
- Nested pair = lower only: False.

**Replacement for G27's last sentence** ("The general case is reasoned, not run."):

> Run on a small temporary recipe (B1, `opus_b1_run.out`). A mean over all rows is computed between the two places. The nested pair gives the same table as the upper place alone (mean 30, without the entity). The lower place alone gives a different table (mean 25, with the entity's value). So in a nested pair the upper place decides and the lower place adds nothing. Choosing the upper or the lower place is a different result whenever a computation across entities lies between them.

The demo's own case is the z-score of `QA_population_zscore`: its tier 2 lies after every T1 place. B1 is now a fact. B2 is still by construction (not run). B3 is settled by hand (section 3).
