# The verification of the work since 2026-11-09: summary for Eve (kept current by the coordinator)

Her decisions: D-0126, D-0128, D-0129 (ledger `.claude/knowledge/decision_ledger.md`). Method: no full test run; a list of what could have deviated (`could_have_deviated.md`, 45 entries), then one actual check per entry. Three answers: did not deviate / deviated / could not be checked.

## Batch 1: the recipe format and the checker (file `check_1_recipe_format.md`), done 2026-11-16 about 09:10
Did not deviate: 3 entries. All 49 shipped recipes pass the checker. 11 recipes broken on purpose were each refused with a message that names the rule.
Deviated: 4.
- F1. The checker does not read the formulas of the action that adds columns (`polars_with_columns`), nor of `polars_remove`. A forbidden formula passes the checker. It is refused later, when the table is built, so no code runs. Against the decision that formulas come only from the allowed list (D-0030, D-0064). Fix: small. Nothing shipped breaks (all 21 shipped formulas pass the list).
- F2. Three tools that WRITE recipes (the gallery manager, the gallery converter, the recipe creator) check what they wrote without the lists of actions and plot components. A partial check passes without a word. Against "no silent error" (D-0050). Fix: small to medium.
- F3. The export's report calls one value "SHA256 of wrangling steps". It is the key of the first stage (`tier1_key`). The wording is wrong; the value is right. Fix: three texts, small.
- F4. One decided error of the recipe format (two joined tables that both hold a column of the same name: Polars renames one to `<name>_right` without a word) is never run by the checker: it needs the map of the recipe's tables, and no caller gives it one. Fix now (small): the check says that this rule was not checked. Real fix (large): build the map (an open task).
Could only be checked in part: of the 32 format rules with no test naming them, 21 were confirmed by one run or by reading; 6 were not checked.
Questions for her from this batch (also in the file):
 1. Should the checker refuse a forbidden formula at once (default: yes; it follows her decision), or is the refusal at build enough?
 2. Correct the words "SHA256 of wrangling steps" now (default), or wait for the task that retires the old key name?
 3. The two date fields of the templates (`submission_date`, `collection_date`): `Date`, or dropped because no recipe uses them? (Already point Y11 of the one list.)
 4. Until the map of tables exists: should HOME and Blueprint say "the rule on duplicate column names was not checked" (default), or stay silent?
 5. Should the three recipe-writing tools use the same lists of actions and plot components as the app (default: yes)?

## Batch 2: the engine actions (file `check_2_engine.md`), done 2026-11-16 about 09:15
Did not deviate: 8. Deviated: 0. Could not be checked: 2. Decided but not built yet: 1.
- The missing-value choice of a filter (keep or remove the rows with no value): holds. A filter step without the choice is refused by the action and by the checker. Keep and remove give what the direct Polars calls give, with a missing value and a NaN in the column.
- The test of the order of tied rows: not skipped. The skip named in the list is in another test (the order of pairs of a join on conditions), and that test passed when run. Sort, unique, group and join gave the same table on five runs; tied rows kept the order of the input.
- A `polars_` action gives what Polars gives: 14 actions were compared with the direct call on a table with a missing value, a NaN and ties: equal. About 45 other `polars_` actions were not compared in this check.
- A filter value of another type than its column is refused in plain words. No action returned the table unchanged for 19 steps with a missing parameter or a missing column.
- Decided and NOT built yet: the ResFinder rule (her answers Y2 to Y4: best hit, tie rule, drop NaN). The recipe has none of it yet. The build was paused this morning and waits for the thresholds.
- **Found by the check, and it is the coordinator's doing:** the change of the multi-resistance formula ("a missing phenotype no longer counts by itself", merged this morning as part of the recipe fixes, not pushed) has NO decision in the ledger. No shipped number moves (16 of 38 samples before and after), but a sample with one phenotype and one missing phenotype was multi-resistant before and is not now. I had treated it as decided; no record of her words was found. It stays on the branch, marked as waiting for her (question 5 below).
- Could not be checked without running the app: what happens after an Excel upload. The typing is right, but the original Excel file is then copied to the path of the tab-separated data, and the reader only reads tab-separated files.
- Side result: the recipe check, called without the lists of actions and plot components, answers "ok" for the structure only; a misspelt action name then passes. The app always passes the lists; three writing tools do not (batch 1, F2).
Questions for her from this batch:
 1. A missing column gives the long text of Polars in most actions, and a plain message in the filter and in `top_k`. Which does she want everywhere? Default: the plain message (her wish that errors of Polars are captured).
 2. Should an Excel upload write the checked table as a tab-separated file, instead of copying the Excel file? Default: yes.
 3. An old filter step without the missing-value choice: should the message say "made before the choice existed", or is "no value: removed" enough? Default: say it.
 4. Should the docs say that Polars changes the order of pairs of a join on conditions "on every run", or "can change"? Default: "can change" (what was run).
 5. The multi-resistance formula: keep the change (a missing phenotype is not counted by itself), or put the old formula back until she has decided what counts as a class? Default: she decides; nothing more is built on it.
 6. The ResFinder thresholds (already point 8 of the one list).

## Batch 3: the join rules (file `check_3_joins.md`), done 2026-11-16 about 09:25
For the three entries of the list: did not deviate 2, deviated 1, could not be checked 1. Seven decided join behaviours were also run.
What holds:
- One rule for join keys, used by the three places that judge a join (the engine, the Blueprint preview, the checker). They give the same verdict on good keys, on keys of two types, on a missing key and on an empty list.
- Keys of two different types are refused with a plain message; nothing is converted silently (whole number against text, category against text, decimal against whole number, a date against text). A 32-bit against a 64-bit whole number is refused too, where Polars alone would join them.
- An empty key list, a missing key column, keys of unequal number: refused.
- The order of the rows after a join is the same on five runs.
- After one recent correction, the joined table of the main recipe has 342 rows and the same hash in the golden baseline.
Deviated:
- J1. A table anti-joined with itself on the same key is only an ADVICE of the checker. The engine runs it and returns 0 rows without a message (4 rows in, 0 out). Her decision of 2026-11-15 (D-0078) makes it an ERROR; that part was never built. Fix: an error in the checker and at the build; small.
- J2. Two joined tables that both hold a column of the same name: the second becomes `<name>_right` and nothing says so anywhere (the decided error J08 is never run; found in batch 1 too). Fix: medium (run the rule from the declared fields), or first a line "not checked".
Not told to the user today, and no decision covers it:
- A join that MULTIPLIES rows (4 rows became 7 in the run): the engine, HOME and the checker say nothing; the Blueprint preview says only "2 of 3 keys matched".
- Rows DROPPED by a join are told in the Blueprint preview only, per key; not by the engine, not in HOME.
- A decimal join key gets its advice only when the key is DECLARED decimal, not when a step of the recipe makes it decimal.
Small defect: the Blueprint preview shows a false sentence for an empty key list ("differ in length: 0 and 0").
Could not be checked: the wording of the message for a key that is not unique (it waits for her yes); it names only the first table when both tables repeat a key.
Questions for her from this batch:
 1. Should a join warn when it multiplies rows, and when it drops rows, in HOME and at the check (default: yes, as a warning with the two row counts; never a block)?
 2. The warning with row numbers for a table joined with itself: shown after the run, or from the check of the data (default: after the run)?
 3. Should a decimal key made by a step of the recipe get the same advice as a declared one (default: yes)?
 4. The message for a key that is not unique: is its wording a yes, and should it name both tables (default: name both)?
 5. Confirm: a 32-bit and a 64-bit whole-number key are refused, although Polars alone would join them (default: keep the refusal, with a message that says which type to declare).
 6. Duplicate column names until the map of tables exists: run the rule from the declared fields (default), or show "not checked"?

## Batch 4a: HOME (the screens, the filter dialog, the audit steps, sessions) (file `check_4a_home.md`), done 2026-11-16 about 10:40
Five entries of the list and seven behaviours built since 2026-11-09. Deviated: 1. Did not deviate: 3. Not built yet (not a deviation): 1. The seven behaviours all comply.
What holds:
- The audit steps run in the recorded order through ONE function, for the table, the plot, the data of the bundle, the export check and the dialog. No other path applies audit steps. A filter after a drop of its column gives a plain error; the reverse order runs.
- Nine audit steps of different kinds give the same rows in HOME and through the exported recipe step (lists, "between" with its ends, keep or remove the missing values, a text value on a number column).
- HOME and the export never write to a recipe file; only Blueprint writes.
- HOME draws no seed by itself.
- No build since 2026-11-09 breaks a decided line of this area, except the one below.
Deviated:
- H1. An EXPLORATION filter on a column that the table shown does not have is skipped without a word. In the run the table kept all 3 rows and the badge still counted the filter as on. Against "No silent error" (D-0050). The skip was built on 2026-11-11, three days before that decision; the audit path was corrected since, the exploration path was not. A test even says the skip is "by design". Fix: small, but it needs her choice (question 1).
Not built yet, so not a deviation: the old "My view" model is still in place (the redesign of the audit is work to do; the understanding document lists it).
Not covered by a decision: the "Reshuffle" button draws a new seed on a click (question 2). The seed for the whole recipe was built by an agent as provisional (question 3).
Seen, belongs to another entry (not yet checked): a session restore that fails for another reason than the old format is swallowed without a message.
Could not be checked without a browser: the dialog's controls, the left pane of Compare, the check of changed recipe files.
Questions for her from this batch:
 1. An exploration filter names a column that the table shown does not have: (a) a visible notice, and the table stays as it is (default); (b) the table is replaced by a plain error.
 2. "Reshuffle": keep it as a choice the user makes? And where is the pinned seed stored: today in the slot of the plot's style, although the audit does not change the plot (default: keep the button; store the seed as a data-side audit setting, to design with the audit build).
 3. The seed for the whole recipe (`plot_defaults: random_state`), built as provisional: confirm, or remove? (Already in the one list.)

## Batch 5: every move of the stored results (file `check_5_baseline.md`), done 2026-11-16 about 10:50
The golden baseline holds 76 stored tables and plot tables of 7 shipped recipes. Since 2026-11-09 it was changed by 6 commits. Entries changed IN CONTENT (a changed result): 9. Entries changed in type only: 85 (no value changed: verified on tables built before and after, compared as text and as numbers). Today the check says "identical".
Changed results, one by one:
- B1. The table `ST22_Anchor`, both stages, and 2 plot tables (commit `99a14148`): one NEW COLUMN `phenotype` (the ResFinder predicted phenotype under a new name; empty in 31 of 617 rows). Same 617 rows, no other cell changed. No decision was found for this column; the task note itself says "Eve to confirm". -> question 2.
- B2. The demo recipe's joined table and its plot (same commit): 30 rows became 28; `year` became text; a column `sequence_type` was added. Her decision D-0047 allows the correction of that recipe. It does not say what was dropped: 12 of 27 samples have no MLST result and fall out; 3 rows have no sample id; and the 28 rows are only 15 samples (one sample has 6 rows). This is more than the decision states. -> question 1.
- B3. Three plots of the figshare recipe were renamed to lower case (commit `ce373923`). The content is identical. No decision was found for the rename. -> question 3.
- B4. The ResFinder second stage and the heatmap's table (commit `9490490d`): one new column `total_gene_count` and a new row order, same 70 rows. This is exactly what her decision on directly plotted tables says (D-0034). Allowed, and nothing more changed.
What the golden check CANNOT see:
- a type change that writes the same text (text against number; category against text; date against text);
- the order of the levels of a category;
- anything outside the 7 shipped recipes and the test data.
Pictures: 8 gallery pictures were changed by one commit (`abc6a186`): 7 changed size (800 by 600 to 960 by 600), and `jitter_strip` differs in 2.6 percent of its pixels. No record that she looked at them. -> question 5. The seed-related picture change is allowed by her seed decisions.
The stored findings of the equality tests: finding 1 (the multi-resistance formula) was removed because the shipped formula was changed this morning; no decision was found for that change (see batch 2). Finding 2 is still open.
Questions for her from this batch:
 1. The demo recipe's joined table: keep 28 rows for 15 samples (12 samples without an MLST result fall out), or make it keep every sample (a left join), or one row per sample? Default: she decides; the description now says what the table holds.
 2. The new column `phenotype` of `ST22_Anchor`: is it the right source column ("Predicted Phenotype", what was done), or "CGE Predicted Phenotype"? Or remove the column? Default: keep, with her yes.
 3. The three figshare plot names in lower case: accept (default), or put the old names back? (A saved session that names the old ones was not checked.)
 4. The multi-resistance formula (same as batch 2, question 5).
 5. The 8 changed gallery pictures: keep (default) after she has looked, or put the old ones back?
 6. The ResFinder second stage (new column, new row order): it follows her decision; confirm that she has seen the picture of the heatmap before and after (`tmp/dataset_tier2/`).

## Batches 6 and 7: the rule and agent files; the tests that were weakened (file `check_6_7_rules_tests.md`), done 2026-11-16 about 11:10
Rule files, agent files, hooks, settings, `CLAUDE.md`, workflow files: 34 commits since 2026-11-09.
- Her yes is recorded for 12.
- For 7 the DECISION behind the edit is recorded, but not her yes to the rule text (already in her list of rule-file changes).
- **For 15 nothing is recorded, and they are not in her list of rule-file changes.** The file gives each as a yes / no line with the old text and the new text.
- One of these is wrong today: the rule file of the bioscientist role lists 67 "verified action names" to use. NONE of them is a registered action today (the actions were renamed). The corrected list is already proposed in her list (row R024).
- No commit loosened a hook or a setting. Three commits tightened the hook; today's merge only added.
- Two open doors of the hook, as it is (not changes): it lets a call through when it cannot read its input; and its new rule covers a builder, an Opus builder and a reviewer only: another kind of agent started with a cheap model is not checked.
Two contradictions inside the rules:
- `CLAUDE.md` allows the coordinator "a one-line fix" in two lines, and says "never edits a file" in a third. The hook enforces "never".
- The plot rule file says a seed written as `null` gives a new arrangement at each drawing. The code now refuses `null` (a provisional build, not answered by her).
Tests:
- Two behaviours LOST their test: the conversion of one old step (`split_column_to_parts`), since one commit; and a deleted test file that checked that a column renamed in the first stage is seen by the join steps, and that a column that exists only after a join is seen by the second stage. No replacement was found.
- Everything else that was removed is tested elsewhere, or was removed by a decision.
- 9 groups of tests are marked "expected to fail"; none passes unexpectedly. One mark is dead (it protects nothing). Three sit under a task marked done. Two have no task.
- Five fixes were UNDONE on purpose in a scratch copy to see whether a test notices: all five were caught (one of them by a single test out of 526).
Could not be established without a browser: three fixes whose only test is a browser test.
Questions for her from this batch (Q1 to Q7 in the file; the main ones):
 1. `CLAUDE.md`: may the coordinator make "a one-line fix", or never edit (default: never; correct the two lines that say otherwise, with her yes)?
 2. A seed written as `null`: refused (as built, provisional), or "a new arrangement each time" (as the rule file says)? (Already in the one list, with the seed points.)
 3. The 15 rule-file and agent-file edits with nothing on record: yes or no to each, in the file.
 4. The two behaviours that lost their test: restore the tests (default: yes; small).

## Batch 4b: the export, the import of a bundle, sessions (file `check_4b_export.md`), done 2026-11-16 about 11:20
Did not deviate: 12. Deviated: 6. Not built yet (the redesign, not a deviation): 7. Could not be checked: 2 (a real download in a browser; the SVG and PDF pictures).
What holds (all run on the real export function, without a browser):
- **What is exported equals what is seen**, on one audited case (a plot with a filter, a column removal and a second filter): the rows the plot is drawn from, the data file of the bundle and a re-run of the exported recipe all equal an independent Polars computation (23 rows, 6 columns).
- The export is refused BEFORE anything is written when the data, the recipe or the first-stage key changed, and when a step cannot run.
- Exploration filters are not exported. The keys and hashes are recorded.
Deviated (against "No silent error", D-0050, unless noted):
- E1. The session screen swallows errors: a damaged session file, or a Delete that fails, shows the user nothing. 14 such places were found in the session, import and export paths; each is listed with its line. (Two of them are older than the redesign: April 2026.) Fix: small each, medium together.
- E2. A restore skips a newest save that cannot be read and restores an OLDER one; the message does not mention the damaged one. Fix: small.
- E3. When the session holds no keys for the recipe or the data, "audit steps applied" saves nothing, and a restore gives no warning. Fix: small.
- E4. The report links data files that do not exist (it names one file per dataset; the real files are one per plot). Fix: small.
- E5. Latent: with the audit switch off and steps present, the plot and its data are audited but the export records no steps (no steps file, no audit trail, an empty steps hash). No shipped setting reaches this case. Fix: small.
- E6. A sentence in the code says a saved session and an export give the same hash of the steps; they differ. And three places of the rule file on the export are older than her decision of 2026-11-09 and no longer match the code (a rule file: needs her yes).
Not built yet (her decisions that the export does not yet follow, because the audit redesign is not built): the exported recipe is the older form (a full copy of the original plus one new join per audited plot, the plot pointed to it; the steps carry no reasons in the recipe); the import as its own function switched on by configuration; the initials of who made a step; the re-base after a changed recipe; the warnings listed in the report.
Described, not judged (an open point she already has): with the box "recipe and raw data" on, a plot whose audit steps cannot be written as recipe steps is NOT refused: the plot is named in a file of the bundle and a notice shows for 10 seconds, but the exported recipe draws that plot WITHOUT the filter.
The import of a bundle: a mismatch warns and never blocks (as she decided). But only 2 of the 4 checks are really made (the data and the engine); the check of the steps is never made, and the check of the recipe shows "not checked" with a wrong reason.
Questions for her from this batch:
 1. What the results export holds (the recipe file always, or behind the box): her words of 2026-11-09, 11-12 and 11-15 differ. (Already the first open point of the one list and of the understanding document.)
 2. A plot whose audit steps cannot be written as recipe steps: refuse the export; export as today; or write them anyway once the audit recipe exists. (Already in the one list.)
 3. The import checks 2 of its 4 parts: is that enough for now, or must the recipe and the steps be checked before the import is used? Default: fix it (it is what her decision of 2026-11-09 describes).
 4. A restore of a session made for other keys (another version of the recipe or the data): should it need a click, and should the saved record keep the old keys? Default: yes to both.
 5. An on-screen message when a plot or the report fails during an export (today it is written inside the bundle only)? Default: yes.
 6. Should PDF pictures carry the keys too (PNG and SVG do)? Default: yes.
 7. May the 14 swallowed errors and E2 to E5 be fixed now? They follow "No silent error"; my default is yes, in one build with its review, since they change only what the user is told.

## Batch 8: the plot library, the gallery, Blueprint, and the large commits that name no task (file `check_8_rest.md`), done 2026-11-16 about 11:40
For the 11 entries: did not deviate 5; deviated 3; not built yet 2; one entry is the list of contradictions the understanding document already holds (12 of 17 read: all still true).
What holds:
- The gallery: 34 of 34 examples pass the checker; 34 of 34 stored pictures equal a fresh drawing; the index equals a rebuild by the script (no edit by hand).
- A recipe saved by Blueprint keeps the order of its keys, holds no Python tag and passes the checker. Blueprint writes no audit steps.
- Nothing that was removed is silently gone: every removed action name and every removed recipe key is REFUSED.
Deviated:
- R1. Every save in Blueprint DROPS ALL COMMENTS of the recipe file (lines that start with `#`). In the run: 12 comments became 0 in the main test recipe. Her recipe-format rule says comments are kept by every tool, with a test per writer. Fix: medium; the method is a choice (question 4).
- R2. About 55 old action names are refused with "choose a registered action", WITHOUT naming the new name. The recipe-format rule says an old name gets the name to write. The table of old names holds 1 name; the migration tool knows about 57. Fix: small to medium.
- R3. The check of a recipe against its data swallows one kind of error: a step that converts a text to a whole number passes the check, then the build fails. Against "No silent error". Fix: small.
- R4. Blueprint's "create plot" writes a plot that the checker refuses. Fix: small for one part; the empty draft plot is a question (question 5).
- R5. The seed: the code works, the records contradict it (the plot rule file and one ADR still say a `null` seed is allowed; the format's list of plot defaults lacks the seed). The two seed builds are provisional and are not in the ledger. Fix: three sentences, after her answer.
- Four more silent places added since 2026-11-09: two in HOME (an error while reading a click is ignored), one in the Test Lab (it silently takes the first uploaded file), one in the audit engine.
The 14 largest commits that name no task and no decision: 5 behaviour changes have NO decision of hers: the removal of three actions (`value_counts`, `select_by_pattern`, `sanitize_column_names`); plot names in lower case only (three figshare plots were renamed); the new column `phenotype` of the table `ST22_Anchor`. Two more are marked as an agent's choice (the removal of `derive_categories`; one key).
Not built yet: the per-plot join of the export against the audit copy; one more of the redesign.
Questions for her from this batch:
 1. The seed: may a seed written as `null` be refused (default yes), and is the seed for the whole recipe kept (default keep)? (In the one list.)
 2. Replace the per-plot join of the export by the audit copy when the HOME audit is built (default yes; it is her design).
 3. `derive_categories`: keep it removed, with the replacement named in the message (default), or restore it?
 4. Blueprint keeps the comments of a recipe: by editing the text of the file directly (default), or by adding a library that reads and writes YAML with its comments (`ruamel.yaml`, a new dependency)?
 5. "Create plot" in Blueprint: may an empty draft plot exist in a recipe, or must Blueprint ask for the table and the columns first (default: ask first)?
 6. The check of a recipe against its data reports a step that fails (default yes; it follows "No silent error").
 7. The three removed actions: keep them removed, with the replacement named (default), or restore one?
 8. Plot names in lower case only (default yes)?
 9. The column `phenotype` of `ST22_Anchor`: which source column (same as batch 5, question 2).

---

# OVERVIEW OF THE VERIFICATION (2026-11-16, 11:45): what was checked, what deviated

Range: 701 commits since 2026-11-09. Method: no full test run; 45 things that could have deviated; each checked by reading and small runs. Eight batches.

| Area | Did not deviate | Deviated | Not built yet | Could not be checked |
|---|---|---|---|---|
| 1 Recipe format and checker | 3 (49 shipped recipes pass; 11 broken ones refused) | 4 | 0 | part of 1 |
| 2 Engine actions | 8 | 0 (+ 1 change of the coordinator without a decision) | 1 | 2 |
| 3 Joins | 2 (+ 5 behaviours) | 2 | 0 | 1 |
| 4a HOME, filter, audit steps | 3 (+ 7 behaviours) | 1 | 1 | browser parts |
| 4b Export, import, sessions | 12 | 6 | 7 | 2 |
| 5 Stored results | 1 exact; 85 type-only changes with no value changed | 3 changed results with no or too narrow a decision | 0 | 1 |
| 6 Rule and agent files | no hook or setting loosened | 15 edits with nothing on record; 1 rule wrong today | 0 | 0 |
| 7 Tests | 5 of 5 undone fixes were caught | 2 behaviours lost their test | 0 | 3 (browser only) |
| 8 Plots, gallery, Blueprint, rest | 5 | 5 (+ 4 silent places) | 2 | 0 |

**The three results that matter most for the science.**
1. What is exported equals what is seen (checked on an audited plot against an independent computation), and the audit steps run in one order through one function everywhere.
2. No value changed in the 85 type changes of the golden baseline; but 3 results changed with no decision or more than the decision says (a new column; the demo table's rows; three renamed plots), and the multi-resistance formula was changed this morning without a decision (not pushed).
3. A wrong table could be stored under an old key (found yesterday night, fixed on a branch, in its second review); a recipe text could run code in five places and in the export report (fixed on a branch, in its third review).

**Fixes that follow a decision and need no choice** (they start now, each on its own branch, with a review that checks it against the decisions):
- the checker reads the formulas of two more actions (D-0030, D-0064);
- the three recipe-writing tools check with the lists of actions and plot components (D-0050);
- a table anti-joined with itself on the same key is an error (D-0078);
- the swallowed errors of the session, import, export and check paths are told to the user; the report's wrong links; the restore that skips a damaged save (D-0050);
- an old action name gets the new name in its message (the recipe-format rule);
- the two tests that were lost are restored.

**Everything else waits for her:** the questions of each batch above (56 in all, many already in the one list). The ones that block the most: what the export holds; the three changed results; the multi-resistance formula; the 15 rule-file edits with nothing on record; Blueprint dropping comments.
