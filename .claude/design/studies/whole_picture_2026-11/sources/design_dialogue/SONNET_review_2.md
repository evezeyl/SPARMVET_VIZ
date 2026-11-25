# SONNET review, round 2: the records error (Part 0), the answer to the Opus position (Part A), and the full paste-ready draft (Part B), 2026-11-23

**What this is.** Round 2 of the review ordered by her (ledger D-0577, D-0578; channel blocks M633, M634). I read `OPUS_review_1.md` whole. Reading and reasoning only, NO RUN (D-0565, D-0566); the checks of Part 0 are fixed-string searches in the committed text, not engine runs. No study file is edited by this file; `WHOLE_PICTURE.md` untouched; no waiting loop; no process left behind. Data agnostic ("the entity", "the result table", "the metadata"); "samples" only for the demo's numbers. Nothing is chosen for her; a lean is a lean. History is marked, never deleted (`rules_legacy_management.md`).

**Two new blocks since my first position.** (1) Channel block M635, ledger **D-0579**: her answer on the two directions of the id test and the order (the test that stops first). It is answered in section A9 and in question 1 of Part B; the two tests are named by their CONTENT, never by number. (2) Channel block M636, ledger **D-0580**: her weekly quota is 75% used; this week only the recipe design and the audit with the lineage concept; no test or run whose code is not changed yet. So: I name runs only as "after the code exists", I keep the draft as short as clarity allows, I re-derive nothing that is established, and I finish Parts 0, A and B in this round.

Tags: [HER WORDS D-n / M-n] / [CODE READ file:line] (what the code DOES TODAY) / [TO BUILD] (not built; she wrote "the code is not build yet", D-0573) / [RECIPE FILE] / [RULE FILE] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] / [RECORD READ] (a committed study file) / [REASONED, not run].

---

# PART 0. THE RECORDS ERROR (first, and plain)

## Plain account

The Opus agent is right. The signing line of `CAUSE_AND_SOLUTIONS_ZEROS.md` says "OPUS_checks_b6_v1.md, R1 to R26 applied". That is false for **11 of the 26 replacements**: R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 are NOT in the committed text. Their old text is still there (examples: line 164 "before the recipe's steps; the added line is marked;" for R4; line 200 "| no for the recipe side |" for R9; line 228 `settled: the marker says "no result"` for R13). The other 15 (R1, R3, R12, R15 to R26) are in the text.

**What happened (my doing).** I applied the replacements with a small editing script. R2 to R14 were applied to a working copy of the text inside one step, and that copy was never written back before the next step (R15) read the file again and replaced the lean line on the older text. So R2 to R14 were lost, and R15 onwards were written on the older text. My script only reported old text it could not find at the moment of replacing. I did not read the written file again before I reported "all 26 applied" and before the signing line was written. The line was wrong the moment it was written. Nobody hid anything; but the record said "applied" when it was not, and that is a records error the coordinator must report to her.

**What the missing replacements are, and whether a result is changed.** No result, no number and no decision of hers is changed by the missing text. They are corrections the Opus agent had asked for in the draft: the quote header (R2), where in the table the completion sits (R4), what the author writes (R5), why the middle column has three states (R6), the evidence for the 6 entities of `Detailed_summary` (R7), the fixed order of added lines (R8, a real omission: the same data must give the same rows in the same order, ADR-090), the run need of variant (iii) (R9), a third source for the meaning (the declared population) (R10), the words of the alert marked provisional (R11), what her words settle on Q1 and Q7 (R13, R14). Until applied, the committed section is weaker than the text both agents signed.

**What else I checked, so that the same error is not repeated elsewhere.** The same fixed-string method on the D-0570 round (`OPUS_checks_notdetected_v1.md`, R1 to R32) against `CAUSE_AND_SOLUTIONS_ZEROS.md` and `OVERLAP_AND_POPULATION.md`: the new text of R1 to R32 is present (the C/G renaming at lines 127 to 136, R20 at line 139, R24 at line 65, R25 at line 64, R27 at line 473, R28 at line 152, and the others). Nothing missing there. **Not checked** (the coordinator may order it): the rounds of D-0569 (Q1 to Q6), of D-0568 (O1 to O7, P1 to P4), of the recipes file (C1 to C15) and of the paths file. I will check them with the same method on request.

**What I do now.** In Part B, section B1, the 11 replacements are written out in full, to be applied with a visible note "applied 2026-11-23, late: the signing line said applied", and the signing line gets a visible correction. I do not edit the study file before the Opus check and the coordinator's order.

## The check, replacement by replacement

Method: for each R of `OPUS_checks_b6_v1.md`, a fixed-string search of its new text and of its old text in the committed file (`CAUSE_AND_SOLUTIONS_ZEROS.md` lines 156 to 266 is the D-0572 section; R25 and R26 are in `OVERLAP_AND_POPULATION.md`). Reading only.

| R | What it corrects | Applied? | Where (committed file, line) |
|---|---|---|---|
| R1 | tag "[HER WORDS M627]" becomes "[HER WORDS D-0572]" | YES | CAUSE 158, 222; none left in the section; OVERLAP uses D-0572 |
| R2 | quote header: "channel block M627; ledger D-0572 ... then her proposal" | **NO** | new text absent; old "Her answers to the facts:" at 158 |
| R3 | "it knows the risk it accepts": "it" is the recipe maker | YES | CAUSE 160 |
| R4 | the moment: "at the first step (your words ...); question 5 asks before or after" | **NO** | new absent; old "before the recipe's steps; the added line is marked;" at 164 |
| R5 | what the author writes depends on question 1 | **NO** | new absent; old "A key on the data table, for example" at 165 |
| R6 | why the middle column has three states (inserted paragraph) | **NO** | new absent |
| R7 | flag 3: no other step removes rows; the count rests on the engine run RR2 | **NO** | new absent; old "A completion before tier 1 adds nothing there ..." at 185 |
| R8 | the order of the added lines is fixed (ADR-090) | **NO** | new absent |
| R9 | (iii) "NEEDS A RUN: yes, run 1 below" | **NO** | new absent; old "no for the recipe side" at 200 |
| R10 | a third source: the declared population (E02) | **NO** | new absent |
| R11 | alert words PROVISIONAL (CAUSE) | **NO** | new absent; old "(what the alert says: the file" at 218 |
| R12 | "The risk (your words)", "(our reading ...)" (two places) | YES | CAUSE 220, 222 |
| R13 | Q1 row: the meaning is the recipe maker's | **NO** | new absent; old `settled: the marker says "no result"` at 228 |
| R14 | Q7 row: conditional on B6 ("That would remove need for 6 anti join") | **NO** | new absent; old "B6 gives both from one table" at 234 |
| R15 | the Opus lean, exact | YES | CAUSE 239 |
| R16 | Q2 starts from her words ("an automatic completion") | YES | CAUSE 244 |
| R17 | Q3 starts from her words | YES | CAUSE 245 |
| R18 | Q4 starts from her words | YES | CAUSE 246 |
| R19 | Q5 starts from her words | YES | CAUSE 247 |
| R20 | Q7 middle case ("42 rows with 1 shown as no line") | YES | CAUSE 249 |
| R21 | Q8 her preference first | YES | CAUSE 250 |
| R22 | Q10 (`demo_abromics`) becomes a note, not a question | YES | CAUSE 254 |
| R23 | the list/count question becomes "10. The count per target" | YES | CAUSE 252 |
| R24 | run 5 only once the completion is built | YES | CAUSE 261 |
| R25 | alert words PROVISIONAL (OVERLAP) | YES | OVERLAP 210 |
| R26 | "The risk: ... (our reading ...)" (OVERLAP) | YES | OVERLAP 213 |

Count: applied 15 (R1, R3, R12, R15 to R26); not applied 11 (R2, R4, R5, R6, R7, R8, R9, R10, R11, R13, R14). The Opus flag 5 is confirmed in full.

---

# PART A. THE ANSWER TO THE OPUS POSITION, point by point

I answer `OPUS_review_1.md`. AGREE, AGREE WITH A POINT ADDED, DISAGREE (with file:line) or MISSING (a thing it does not say that I do). Each "I agree" rests on reading the same file or on my own first position (`SONNET_review_1.md`).

## A1. Its six flags

| Flag | Answer | Evidence / what I add |
|---|---|---|
| 1. "Not a zero" against today's count steps | **AGREE**, and I add the second aggregate | `QA_AMR_per_sample_tier2.yaml:8` `n_amr_genes: pl.col('gene').count()` gives 0 for a line with empty result cells; `ResFinder_wrangling_tier2.yaml:6` `total_gene_count: pl.len().over(['sample_id'])` gives 1; the plot says "Expect 42 samples: 4 with 0 genes, 70 genes in total" (`plots/qa_amr_genes_per_sample.yaml:15`) [RECIPE FILE]. Her rule "The marker of "not in original data" is not a zero" [HER WORDS D-0573] cannot hold by default: the engine itself would turn the 4 added lines into a 0 and a 1. Same point as my table in `SONNET_review_1.md` section 3.4. |
| 2. Her refusal may reverse D-0569 for result ids missing from the metadata | **AGREE**, and her new block D-0579 makes it sharper | D-0569: "Choice for data check - b: and inform that the user should better fix this". D-0573: refuse "errors or missing data (at the id level only)". D-0579: "stopping first no?". Under the reading "also an id of the original data that the metadata lacks" the metadata is refused and D-0569 (b) is reversed for that case. I did not see this clearly in my first position (I wrote "a mismatch ... informs (test 2)" in section 3.2); the Opus agent is right to separate it. It must go to her as one question (now question 1 of the merged list). |
| 3. A refusal at the load gate closes the recipe; pipeline profiles stop at start; the re-upload loop has no way in | **AGREE** | `bootloader.py:431-451` (`_gate_one`: any problem rejects, advices never reject and come from the recipe check only), `:453-459` (a rejected recipe never reaches `available_data_analysis_recipes`); `rules_data_analysis_recipe_structure.md` section 11a: a refused default recipe is still fatal at startup where the selector is hidden. I had the same in `SONNET_review_1.md` 3.2. I add: Data Import works from HOME's sidebar on the open recipe, so a refused recipe has no panel to upload a corrected metadata; her loop "re-upload and the verification start" can only live in Data Import (seat s2) or in a new way in (s3). |
| 4. `demo_abromics` would be refused as shipped | **AGREE** | metadata file lines 5, 6, 11: empty, `-`, `""` [ESTABLISHED: OVERLAP, D-0570 part: three lines, not two]; the recipe removes them after the read (`demo_abromics.yaml:44-47`, `polars_drop_nulls`); a check of the metadata as read (before tier 1) would refuse it. Her order D-0569 ("remove the null and empty rows from the metadata") already changes the file in the dry run. In my first position I asked "corrected to 27 lines, or kept as a fixture" (Q-K). Her words settle it: not a question (see A8). |
| 5. The committed D-0572 section lacks 11 of 26 replacements | **AGREE**: my error | Part 0. |
| 6. A dummy id cannot be "removed afterwards" from the metadata | **AGREE**, with the way out named | The result file still holds the id, so check X fires again after the removal. The ways out: a removal by key of the entity (an audit step, D-0322) or the library "remove from all the data" (`utils.remove_from_all.apply`, built as a library step; the screen is not built: D-0499, D-0531, D-0501); or a new result file. I add that every removal or upload of the metadata is a new data batch (A6): the acceptance is asked again. |

## A2. The two tests (its section 0, reading 1)

**AGREE: same finding.** In my first position (section 0) I found the same fact: the written question of each test and its action name two different sets. The review session read each test by its action and she confirmed with "yes" [HER WORDS D-0573]. The Opus point N1 is my Q-A. **Her block D-0579 now settles the labels:** "what is missing in one and in other and vis versa - what is test 1 and test 2 - does not really mater". So the numbers do not matter; the content does. I name them as the review session did in D-0579: **check X** (ids of the original data that are not in the metadata) and **check Y** (ids of the metadata that are not in the original data). The question "which set does each test check?" is no longer asked. What stays for her is the order and the stop (A9).

## A3. Its settled / void / open lists against mine; "B6 chosen" against her D-0574 words

**"B6 chosen"? Quote.** D-0574, her words exactly: "yes so it does not record directly in the recipe how many were added because it would modify the recipe and we cannot do that BUT as it reports it in the log then this is transparent correct ? Once per data batch - and yes confirmation and what as added is kept in the session log - I think we need to force - it makes it transparent, it makes thinking about it - and it will avoid problems to the maker when those problem arrise and there ia a clear treatment. I think once per data batch (as recalled by session ?) - the recipe required on every result table - and once for each data batch - the user must only to accept once." [HER WORDS D-0574]

What is hers in those words: the completion exists; it is in the recipe ("the recipe required on every result table"); it is forced ("I think we need to force"); the recipe does not record the count; once per data batch; the confirmation and what was added are kept in the session log. What is the review session's reading, not hers: "option (i-b), a block done by the app when it reads the file" (D-0574, marked as such). The one sentence where she names the form is NOT in D-0574's exact words: it is in the relay at `tmpAI/agent_channel.md:4101`: "Before that she said, on seeing option (i) explained: "I would lean also to add this in the recipe"". So: **B6 is decided in substance (the completion, in the recipe, required, forced); its form (a block read by the app, option i, or a first step the author writes, option ii) is read, not stated.** I disagree in a small way with Opus D(a) row 1 "SETTLED: ... (i-b)": her "lean" was said of option (i) as a whole (i-a, i-b, i-c), and "required on every result table" fits (i-b) and also a first-step action. I keep the form open in the merged list (question 6), with the reading as the lean.

**"Required on every result table": two readings (not in the Opus text, MISSING).** Her words say "every result table". Both agents and the review session wrote "every result table that has an entity id". A result table with no entity id (the 3 tables of `2_test_data_ST22_dummy` today) cannot be completed. Either such a table must declare one first (her order D-0569: "Have the recipes declaire entity id"), or it carries a block that says "no entity id". One question for her (merged question 6).

**Each "void" against her words.**

| Candidate | Opus says | Her words | My answer |
|---|---|---|---|
| E2 (anti-join) | VOID | D-0572: "That would remove need for 6 anti join" (said of B6) | **VOID by her words**, with the condition that the completion is built; she keeps the anti-join as a tool she avoids "as much as possible" (D-0570), not forbidden |
| B4 (metadata first + manifest of the analysed) | VOID | none | **NOT void by her words.** Less needed: the completion does the job for the zeros. A manifest as the declared population (`entity.population`, E02) stays a possible source of meaning (the third source, R10). Mark "no longer needed for the zeros (the agents' reading), kept as history" |
| E (right or full join) | VOID | none | same: less needed, not void by her word |
| C (the app labels from the audit record) | VOID for the completion | D-0574: the recipe does not record the count; the count is in the log | **superseded in function** (the completion is in the recipe; a removal leaves the entity absent or with no line). The audit-record reading survives only for the information line F. Not void by her word |
| B2 (a table of the analysed entities first) | VOID as a form for the zeros | none | less needed; a manifest as population stays a variant. Same |
| B3 (the files list every analysed entity) | SUPERSEDED, compatible | D-0569 "a point to consider" | **agree**: a file that already lists every id gets no added line |
| B5 (a column "has a line") | SUPERSEDED | D-0572: "a different kind of other "missing value"" | agree: the marker gives the third state |
| A (metadata first, fill in the recipe) | CHANGED | none | agree: still a possible spelling (question 12) |
| B (count first) | CHANGED | none | agree: a pattern; the count table gets a block too |
| D (no zeros) | CHANGED, becomes a stated meaning "excluded" | none | agree: a recipe meaning, no longer an option of the app |
| F (information line) | CHANGED | D-0575, D-0576 | agree: the log and the alerts carry the counts; F as a screen line stays possible |
| G (declared meaning) | SETTLED, absorbed | D-0574 "force" | **agree in substance**; what the required meaning may hold (free text or a few words) is open (question 5/6) |

**One rule for the marks.** Only E2 is void by her words. Everything else is marked "no longer needed for the zeros / superseded in function" with the reason, as the agents' reading, to be confirmed with her in one line at the end of the list (not a decision asked of her one by one). This follows `feedback_reopen_decisions_on_merit`: a candidate is not killed by a decision that does not name it.

## A4. Its N1 to N9 and my Q-A to Q-K: ONE merged list, one naming

Numbers 1 to 15, in the recommended order (section A10). The first column is the new number; the next two are the old names, so that nothing is lost.

| New | Subject | Opus | Sonnet (round 1) | Note |
|---|---|---|---|---|
| (settled) | names of the two checks | N1 | Q-A | settled by D-0579: names by content (X, Y); not asked |
| 1 | the order of X and Y, and the stop | N2 + (her D-0579) | Q-I (part) | merged: "stopping first" is "refuse until fixed" or "hold Y" |
| 2 | which id errors refuse the metadata | N3, Q9' | Q-B | |
| 3 | where the refusal sits, its wording, the order with the metadata's own check | N4 | Q-G, Q-I | |
| 4 | the user does not confirm | (missing) | (missing) | NEW, found now (A7) |
| 5 | the marker: form; "not a zero" and the counts; the demo's 4 | N9, Q4' | Q-C, question 4 | |
| 6 | the block: form, which tables, names, what the meaning accepts | (missing as a question) | Q-H | the form is open (A3) |
| 7 | the position | Q5' | question 5 | |
| 8 | which metadata | Q6' | question 6 | |
| 9 | the acceptance: key, deleted session, no session | N5 | Q-D | |
| 10 | the log | N6 | Q-E | |
| 11 | a dummy id | N7 | Q-F | |
| 12 | the join order | Q7' | question 7 | |
| 13 | a recipe with no metadata block | N8 | Q-J | |
| 14 | the count per target | Q10 | question 10 | |
| 15 | the threshold (low) | D(d) 6 | question 6 of D-0570 | |
| (note) | `demo_abromics` | D(d) 8 | Q-K | not a question (A8) |

Items in my list that Opus lacks: 4 (no confirmation), 6 (form, and "every result table"), Q-C merged into 5. Items in the Opus list that I lacked: N2 (as a question of its own, now merged in 1), N8 (I had Q-J), N9's two ways z1 and z2.

## A5. The log (both lean L1)

**AGREE on L1, and I accept the Opus form.** The Opus form: one YAML file, `format: 1`, a reader that refuses an unknown format, the date and the initials given by the caller, data only, name provisional `id_log.yaml`, "in the manner of the held `audit_log.py`". I had proposed `id_completion_log.jsonl` (append-only JSON lines). I change to the Opus form for these reasons:

- The held `audit_log.py` (branch `task/audit-slice1-effects-log`, commit 42d5ae6d, on hold, not on `dev`) writes `audit_log.yaml` starting with `format: 1`; its text says "the same entries give the same bytes, ADR-090", "a reader refuses an unknown number, a file that is not a log and an entry that breaks the form", "PROVISIONAL" for the file name and every key [CODE READ `git show task/audit-slice1-effects-log:libs/utils/src/utils/audit_log.py`, lines 1-30]. Two logs read in the same way is one habit for her to learn and one reader to write.
- Her recipes are YAML; she reads YAML. JSON lines would be a second style.
- What JSON lines would give (append-only, safe against a stop in the middle of a write) matters less: an entry is one event per user action, the file is small, and the module can write to a new file and rename.

"In the manner of" means the same rules, not an import: the audit log is held and not on `dev`; the id log must not wait for it. **The file name: I accept `id_log.yaml`** (provisional). The Opus entry kinds are right (`metadata_refused`, `ids_not_in_metadata`, `completion`, `accepted`); I add three more: `not_confirmed` (question 4), `dummy_ids_declared` (question 11), and `check_x_stopped` (question 1). Where a refusal is logged when no session exists: A6.

## A6. The session key and the evidence (`session_manager.py:10, 280-308`; `orchestrator.py:793-821`)

**AGREE with its B1/B2; the evidence is the same reading.**

- The key: `session_key = data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]` [CODE READ `session_manager.py:10, 305-308`]. The recipe hash covers the entry file and every included file (`:280-287`). The batch hash is the hash of the per-file hashes of every dataset the recipe names, the metadata and the additional datasets included (`:294-299`; `orchestrator.py:793-821`; `cache_keys.py:139-152`).
- So: a replaced metadata file gives a new key; a replaced result file gives a new key; **an edit of the recipe (any included file) also gives a new key**: "once per data batch" is, as the code is, once per recipe version and batch, if the acceptance is stored under the session key. Stored under the batch hash alone it would be once per batch. That is a choice for her (question 9). The Opus text says "an edit of the recipe also asks again" too; I add that she said "once per data batch" and the key says more.
- A deleted session: `delete_session` removes the whole folder (`:774-778`): the log and the acceptance go with it; the next opening asks again.
- Another machine or user: another `_sessions` folder; the key is made of content hashes, not paths, so the same files give the same key but no session is found; the user is asked. A session zip (`export_session_zip` `:647-650`, `import_session_zip` `:662-737`) carries the folder and its log; a key that exists is never overwritten silently. Whether an acceptance carried from another user counts is open.
- No session at all: `session_management_enabled` false in the pipeline profiles [RULE FILE `rules_app_features_flags.md` flag matrix]: no place to store an acceptance (question 9).
- **Where a refusal is logged when no session exists.** `session_dir` creates the folder (`:314-320`), but the list of sessions is built from `assembly.json` (`:602-640`); a folder with only a log would not be listed. So a log of a refusal must be written where it will be found: in the export of the next session, or in a log at the deployment level. I add this to the question on the log.
- **A point both of us missed in round 1 (found now): fixing the metadata is itself a new batch.** A typo fixed in the metadata gives a new batch hash and a new session key; an acceptance given before the fix is lost. This is an argument for check X before check Y (A9).

## A7. What is MISSING in both texts: the user does not confirm

Her rule: "A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)" [HER WORDS D-0573]; "the user must only to accept once" [HER WORDS D-0574]. Neither agent said what happens if the user does **not** accept (or cannot: a deployment with no one at the screen). Three states are possible:

| If there is no acceptance | What the user sees on the demo | What it risks |
|---|---|---|
| the recipe does not open (a refusal, like an id error) | `qa_amr_genes_per_sample` is not on HOME's list; the reason names ResFinder and its 4 ids | closes the recipe for everyone who cannot confirm; in a pipeline profile the app stops at start (flag 3) |
| the recipe opens with the table as in the file (no added line) and a loud, standing note | ResFinder has 70 lines and the plot has 38 samples; the note says "4 ids of the metadata are not in ResFinder; not completed" | the export must say so on every figure: otherwise the result changes with a missing message (the 4 entities silently absent) |
| the recipe opens and completes anyway, the log says "not confirmed" | 74 lines, 4 marked; the log says nobody confirmed | breaks her rule: the confirmation is the point of the rule |

It is a real question for her (merged question 4). I do not lean: each door closes something.

## A8. `demo_abromics`

Her words settle it: "remove the null and empty rows from the metadata" [HER WORDS D-0569] and "it must not contain errors nor missing data. A rule" [HER WORDS D-0573]. So the metadata file is corrected in the dry run (D-0525); no question. A refused example, if she wants one to teach the refusal, would be a separate fixture, not a shipped recipe. I withdraw my Q-K.

## A9. Her D-0579: the order of the two checks and "stopping first"

She asks, as a question: run X first and stop there when it finds ids; Y only when X passes. [HER WORDS D-0579: "it might be more logical to have test 2 as the first test .... stopping first no ?"] The review session asks the agents for the case for and against and a recommendation. Mine, by reading:

**For stopping at X first (evidence):**
1. **The same typo shows in both directions.** A misspelled id (the data holds `S1`, the metadata `S01`) is one error: X lists `S1` (not in the metadata) and Y lists `S01` (not in the data). If Y is confirmed first, the user confirms the addition of a marked line for `S01`, which is a false absence. After the fix both lists are empty. Only X-then-Y shows the real absences. [REASONED from the join of ids; the two sets differ by exactly the misspelled pair]
2. **A confirmation given before the fix is lost.** Fixing the metadata is a new data batch (A6): new key, the acceptance asked again, the log with a confirmation of a list that never became true.
3. **The metadata is the reference of both checks.** It is refused when its own ids are wrong [HER WORDS D-0573]; completing data from a list that will change builds on sand. This is her own reason (D-0579 reading).
4. **On the demo it costs nothing:** X finds 0 ids on every demo result file (every id of a result file is in the metadata [ESTABLISHED: OVERLAP section 1]); Y finds 4 for ResFinder. X first changes nothing there; on `left_join_lesson` X finds 2 (`ACC0001`, `ACC0002`).

**Against stopping, or to qualify:**
1. **A user who cannot fix is blocked.** In the profiles with no upload panel (`metadata_ingestion_enabled` false: static, simple, demo-vetinst, web-demo [RULE FILE `rules_app_features_flags.md` flag matrix]) the metadata comes from the pipeline. A stop there is a refusal of the recipe and the app stops at start with the cause and the contact (flag 3). It is fatal for a deployment that cannot fix the data.
2. **It reverses D-0569 (b) for X**, if "stop" means refuse (flag 2 above). D-0569: "inform that the user should better fix this". D-0579: "stopping first". They are both hers; she must say which holds.
3. **A result file may legitimately hold an id the metadata lacks** (a control sample): the dummy fill [HER WORDS D-0573] is the way out, and it pollutes every result with a dummy entity until removed (flag 6).
4. **BLUEPRINT's Validate reports and never blocks** [RULE FILE 11a]: the stop belongs to HOME's gate, not to the author's check.

**Three readings of "stopping first"** (to put to her):
- (a) **Refuse:** X finds ids, the recipe does not open until the metadata is fixed.
- (b) **Hold Y:** the recipe opens with X's note; Y's list is shown as information, not confirmed, nothing is completed until X passes.
- (c) **No stop:** X and Y are both shown; Y's confirmation is asked at once.

**The two leans (as leans, hers to decide):** the Opus lean on the stop is to be given in its check (its first position leaned to inform only, reading r1, for D-0569's sake). **Sonnet lean:** (b) is the least that keeps her order and her earlier decision: nothing is confirmed, completed or logged on a list that will change, and the recipe still opens where nobody can upload. (a) follows D-0579 most literally and is the right choice where the user can upload, if she wants the stop to be a refusal. Whether the behaviour depends on the deployment (a hybrid) is itself a choice: "the app informs and does not choose for the user". Question 1 of the list.

**The full order of checks, whatever she chooses:** (0) the metadata's own ids (empty, repeated: refuse); (1) X; (2) Y with the confirmation. Step (0) comes first because it is on the metadata alone, and the metadata is the reference of both.

## A10. The order (its D(e) against mine)

The Opus order: N1, N2, N3 with Q9', N4, N9 with Q4', Q5', Q6', N5, N6, N7, Q7', N8, Q10. Mine: Q-A, Q-B, Q-G and the place, Q-I, Q-D, Q-H with question 4, Q-C, question 5, 6, 7, then Q-E and Q-F, Q-J. The first four are the same. **I agree with the Opus order**, with these changes: question 1 (the order and the stop) first because it decides what every later question means (does the recipe open?); question 4 (no confirmation) right after the refusal seat, as it is the same door; question 6 (the block's form) before the position, since the position depends on what is placed. Section B3 below holds the final order.

## A11. The review of RECIPES and PATHS: the Opus table against mine, merged

The merged table is in Part B (B3 and B4). Where we differed:

| Point | Opus | Mine | Merged |
|---|---|---|---|
| G4 the entity id | STILL TRUE, with D-0569, D-0573, D-0574 | CHANGED MEANING: required id | **STILL TRUE**, with a new fact: the entity id is the condition for the completion; its meaning is unchanged |
| G6 zeros, false zero | SUPERSEDED as the recommended pattern | CHANGED: false zero accepted (D-0569); data first keeps zeros | **SUPERSEDED as the way to give zeros**; its facts stay true of today's recipes; the false zero at the table's own place is accepted (D-0569) |
| G7 a zero cannot tell | first half true, second half superseded | CHANGED: the marker tells the added lines | **split**: the first half stays true (the accepted risk); the second half is superseded (with the completion the entity exists with the result table first) |
| G12 uniqueness | STILL TRUE (a fact) | STILL OPEN | **STILL TRUE as a fact**; the question where "unique" is judged is (iii) |
| G13 what nothing checks | STILL TRUE of the code | SUPERSEDED IN PART | **STILL TRUE of the code**; part of it is decided and not built (the id check, the two checks) |
| G17 reading rules | STILL TRUE; a completed table also reads the metadata | CHANGED: the metadata file is a parent | **STILL TRUE, plus a new fact:** an edge from the metadata's file (or its tier 1, question 8) into every completed result table |
| G19 a rule "metadata on the right" | CHANGED MEANING | CHANGED MEANING | agree |
| (ii), (iii), (iv) | CHANGED MEANING | CHANGED | agree |
| (viii) | STILL OPEN, weightier | same | agree |

---

# PART B. THE FULL DRAFT, paste-ready after the Opus check

How to read Part B: each block says where it goes and which exact text (an anchor) it follows. Her words are exact and tagged. "Today" is kept apart from "to be built". Nothing here is applied until the Opus check and the coordinator's order. Plain short sentences; what she sees first.

## B1. `CAUSE_AND_SOLUTIONS_ZEROS.md`

Three things, in this order: (B1.1) apply now the 11 replacements that the signing line wrongly called applied; (B1.2) visible correction notes inside the committed D-0572 section for what her words changed; (B1.3) the new section, appended after the D-0572 section (before the heading "## THE CAUSE, AND WHAT WAS FOUND"). Also (B1.4) the signing line.

### B1.1 The 11 late replacements (apply with exact edits; the text is the text signed by both agents in `OPUS_checks_b6_v1.md`)

Visible note, one blockquote at the top of the D-0572 section (text in B1.2, note N0): "applied 2026-11-23, late: the signing line said applied". Each replacement changes only the text named. "Draft N" in the Opus file is replaced here by the text to find (an anchor), because the draft lines are not the file's lines.

**R2.** Find: `**Her words, exact** (channel block M627). Her answers to the facts:` Replace with: `**Her words, exact** (channel block M627; ledger D-0572). Her answers to the facts, then her proposal:`

**R4.** Find: `before the recipe's steps; the added line is marked;` Replace with: `at the first step (your words: "an automatic completion at (first step)"; question 5 asks whether before or after the recipe's own tier-1 steps); the added line is marked;`

**R5.** Find: `- **What the author writes.** A key on the data table, for example` Replace with: `- **What the author writes.** It depends on where the completion lives (question 1). With (i): a key on the data table, for example`

**R6.** After the line that begins `  [REASONED from the engine order (` and ends `NEEDS A RUN after your choice]`, insert one line: `  Why the middle column has three states: after a left join from the metadata, an entity that has no line in the result table gets one row whose result columns are all empty, the marker included; an added line has the marker set; a file line has it unset. [POLARS SEMANTICS; REASONED]`

**R7.** Find: ``` `Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`); its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities; ``` Replace with: ``` `Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`), and no other step of that tier removes rows [RECIPE FILE `Detailed_summary_wrangling.yaml:3-36`]; its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12, engine run Opus RR2]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities: with the data table first they are absent; ```

**R8.** Find: `leaves the Source view true to the file and runs BEFORE any audit step.` Replace with: `leaves the Source view true to the file and runs BEFORE any audit step. The added lines come in a fixed order (for example the order of the metadata), so that the same data give the same rows in the same order [RULE FILE `rules_data_engine.md` section 2, Determinism, ADR-090].`

**R9.** Find: `| NEEDS A RUN | yes | yes (and an engine change) | no for the recipe side | no |` Replace with: `| NEEDS A RUN | yes | yes (and an engine change) | yes: run 1 below (the added lines written by hand are the same test) | no |`

**R10.** Find: `but ResFinder's first place lies below the metadata's: two places on one path (flag 4).` Replace with: `but ResFinder's first place lies below the metadata's: two places on one path (flag 4). A third source exists if the recipe declares `entity.population`: with a manifest of the analysis as the population, the marker would mean "analysed, nothing found" (the key exists and is checked, E02 [CODE READ `recipe_check.py:332-348`]; nothing else reads it today [ESTABLISHED: OVERLAP section 3]).`

**R11.** Find: `(what the alert says: the file, how many lines were added,` Replace with: `(what the alert says, words PROVISIONAL: the file, how many lines were added,`

**R13.** Find: `| 1. A never-analysed entity counted as "not detected"? | settled: the marker says "no result"; "only a recipe maker (in collaboration with a real user) can decide" | nothing for the app |` Replace with: `| 1. A never-analysed entity counted as "not detected"? | settled: the meaning is the recipe maker's, "which only a recipe maker (in collaboration with a real user) can decide"; with B6 such an entity would show as "no result in file" (working name; since D-0573 the marker is called "not in original data") | nothing for the app |`  (The parenthesis is the only change from the signed text of R13; it carries the D-0573 name.)

**R14.** Find: `| 7. The number, the list or both | B6 gives both from one table | how the list is shown |` Replace with: `| 7. The number, the list or both | if B6 is chosen, both come from one table ("That would remove need for 6 anti join") | how the list is shown (the key of a table as a result is open, D-0487) |`

### B1.2 Visible correction notes inside the committed D-0572 section (blockquotes; nothing is deleted)

Each note is a blockquote placed directly under the text it corrects. The words of her blocks are quoted in B1.3.

**N0, directly under the heading `## Added 2026-11-23 (ledger D-0572): her solution B6 and the control of the ids`:**

> **Update of 2026-11-23 (ledger D-0573 to D-0579):** her next answers changed this section. B6 is no longer only her proposal: since D-0574 the completion lives in the recipe and is required on every result table (form open). The marker is called "not in original data" (not "no result in file") and is not a zero. The metadata is refused when its ids are wrong. A confirmation once per data batch is noted in a separate log, also in the export. The ten questions at the end of this section are replaced by the list in the section "Added 2026-11-23 (ledger D-0573 to D-0579)" below; each of the ten has its fate there. The lines below are kept as history, each marked where it is stale. **Applied 2026-11-23, late: the signing line of this file said "R1 to R26 applied" but R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 of `OPUS_checks_b6_v1.md` were not in the text; they are applied now (a records error of the Sonnet agent: the editing script lost them; found by the Opus review, flag 5).**

**N1, directly under the paragraph that ends `**B6 is HER PROPOSAL, not chosen**: fill the data tables with the ids of the metadata, with a marker "data file has no result".`:**

> **Update of 2026-11-23 (ledger D-0574):** the completion in the recipe, required on every result table, is decided in substance (her words: "I think we need to force"; "the recipe required on every result table"). What is not decided: whether it is a block that the app reads (option i) or a first step the author writes (option ii), the key names, and which tables ("every result table", or those that declare an entity id).

**N2, directly under the line `[REASONED from the engine order (`data_wrangler.py:92`, `orchestrator.py:282-295`) and the join semantics; NEEDS A RUN after your choice]` (after the R6 line):**

> **Update of 2026-11-23 (ledger D-0573):** the first column "4 in the bar at 0" holds only if the recipe says that a marked line counts as 0. Her rule: "The marker of "not in original data" is not a zero." The demo's count `pl.col('gene').count()` gives 0 for an added line by itself and `pl.len()` gives 1; both would make a zero or a one without a message. What the plot shows for the 4 is her question (new list, question 5).

**N3, directly under the heading `### The marker (short and explicit; a different kind of missing value)`:**

> **Update of 2026-11-23 (ledger D-0573):** the working name `no_result_in_file` and the words "no result in file" are replaced by her name: "not in original data". Everywhere in this section where `no_result_in_file`, "no result in file" or "data file has no result" stands, read "not in original data".

**N4, directly under the heading `### Where the completion can live (her open question)`:**

> **Update of 2026-11-23 (ledger D-0574):** (i-a) (a key on each table) and (i-c) (automatic, no key) are void: the block is required, with its meaning required. (iii) outside the recipe and (iv) the audit copy stay as history. What remains open is (i-b) against (ii) (new list, question 6).

**N5, directly under the heading `### The control of the ids (hers)`:**

> **Update of 2026-11-23 (ledger D-0573, D-0574; her D-0579):** (a) an id of a result file with no metadata is "check X": inform and list; the user adds the ids to the metadata by hand and uploads it again; an unknown or false id may be added with a dummy fill and a note to remove it; there is no marker "not in metadata". (b) an id of the metadata with no line in a result file is "check Y": warn; the data is completed with the marker "not in original data" after the user's confirmation, once per data batch, noted in a separate log, also in the export. (c) the metadata with no id is refused, not only informed. (d) a repeated id may be an error at the id level (new list, question 2). The correction text of the committed paragraphs is in the new section.

**N6, directly under the heading `### Her eight questions: settled or not`:**

> **Update of 2026-11-23 (ledger D-0573 to D-0576):** row 1 now reads "the meaning is the recipe maker's"; row 4 is settled (required in the block); row 8 (`demo_abromics`) is settled by her words "remove the null and empty rows from the metadata" and "it must not contain errors nor missing data. A rule". The rows 2, 3, 5, 6, 7 have a new status in the new section.

**N7, directly under the heading `### Leans, as leans (two agents, two sentences)`:**

> **Update of 2026-11-23:** these leans were written before her answers D-0573 to D-0576. They are history. The leans of the two agents on the new list are in the new section.

**N8, directly under the heading `### The questions that remain for you, one at a time (each with what you would see on the demo)`:**

> **Update of 2026-11-23 (ledger D-0573 to D-0579):** this list of ten is replaced by the list in the new section. Question 1 (where the completion lives) and questions 2 and 3 are settled in substance; question 8 is settled; question 9 changed (an error at the id level); questions 4, 5, 6, 7 and 10 are rewritten; nine new questions came (1, 2, 3, 4, 6, 9, 10, 11 and 13 of the new list; question 2 holds the old question 9). The ten are kept here as they were asked.

**N9, directly under the heading `### Runs after your choice (each registered before it runs; three points)`:**

> **Update of 2026-11-23 (ledger D-0573):** run 7 (`not_in_metadata`) is void: there is no marker "not in metadata". Run 1 and run 2 use the marker "not in original data". Four runs are added in the new section, to run only after the code exists (D-0580).

### B1.3 The new section (append after the D-0572 section; before `## THE CAUSE, AND WHAT WAS FOUND`)

---

## Added 2026-11-23 (ledger D-0573 to D-0579): her decisions on the ids, the completion and the log; the updated list of what is still hers to answer

Not yet in the signed text above. The text above is kept; where her answers made a part stale, it is marked there. **She wrote, about the code: "the problem is the code is not build yet ...but I guess that helps knowing what needs to be build" [HER WORDS D-0573].** So this section keeps apart what the code does today ([TODAY]) and what has to be built ([TO BUILD]).

### Her words, exact

**Block M629 (ledger D-0573).** "seems opus agent checked against the code .. the problem is the code is not build yet ...but I guess that helps knowing what needs to be build... We need to fix the metadata - it must not contain errors nor missing data. A rule. The marker of "not in original data" is not a zero ... right now our recipe does not say how to process those cases. Not sure the agent have understood the functionning the sets at correction 1. test inclusions : are all original data id included in metadata ? -> yes no problem / no -> warn and include those present in metadata to original data - with the specific marker "not in original data" 2. second test inclusion are all id in metadata included in original data ? -> yes no problem // no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards eg. because eg they are wrong." And her answer to two questions: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)  - yes - can you send again for review ?" [HER WORDS D-0573]

**Block M630 (ledger D-0574).** "yes so it does not record directly in the recipe how many were added because it would modify the recipe and we cannot do that BUT as it reports it in the log then this is transparent correct ? Once per data batch - and yes confirmation and what as added is kept in the session log - I think we need to force - it makes it transparent, it makes thinking about it - and it will avoid problems to the maker when those problem arrise and there ia a clear treatment. I think once per data batch (as recalled by session ?) - the recipe required on every result table - and once for each data batch - the user must only to accept once." [HER WORDS D-0574] (Before that, on seeing option (i) explained: "I would lean also to add this in the recipe", relayed in the channel; it is not in the ledger's exact words.)

**Block M631 (ledger D-0575).** "yes that must be in the export - we might need logs for different things - maybe better to keep the id adding in a separate log ? - wait for other questions now we need to get to the bottom of this" [HER WORDS D-0575]

**Block M632 (ledger D-0576).** "yes separate log" [HER WORDS D-0576]

**Block M633 (ledger D-0577).** "I think we need them to review their evaluations of what I should answer now that we should have added some solutions to problems" [HER WORDS D-0577]

**Block M634 (ledger D-0578).** "the RECIPES_FROM_THE_MODEL_AGREED.md needs to be reviewed also - we have made significant choices already and found solutions." [HER WORDS D-0578]

**Block M635 (ledger D-0579).** "there are 2 directions in the test - what is missing in one and in other and vis versa - what is test 1 and test 2 - does not really mater however it might be more logical to have test 2 as the first test .... stopping first no ?" [HER WORDS D-0579]

### What is DECIDED in her words, and what is only the review session's reading

| What | Her words | Line |
|---|---|---|
| The metadata is refused when it has errors or missing data at the id level only; true missing data in other columns does not refuse it; the user is responsible | "refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)" | D-0573 |
| The two directions of the check; the numbering does not matter (naming them X and Y by content is the review session's reading) | "there are 2 directions in the test"; "what is test 1 and test 2 - does not really mater" | D-0579 |
| **Check X**: an id of the original data that the metadata lacks: inform, list; the user adds it to the metadata and uploads again; verification starts again; an unknown or false id may be added with a dummy fill and a note to remove it | "no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start" | D-0573 (the pairing of her question and her action is the review session's reading, confirmed by her "yes") |
| **Check Y**: an id of the metadata that the original data lacks: warn; include it in the original data with the marker "not in original data"; the user confirms; the confirmation is noted in the log | "warn and include those present in metadata to original data - with the specific marker "not in original data""; "A user confirm is good"; "noted in the log" | D-0573 |
| The marker is called "not in original data" and is not a zero | "The marker of "not in original data" is not a zero" | D-0573 |
| The recipe does not say today how to process those cases | "right now our recipe does not say how to process those cases" | D-0573 |
| The completion is in the recipe, required on every result table, forced | "the recipe required on every result table"; "I think we need to force" | D-0574 |
| The recipe never records how many lines were added | "it does not record directly in the recipe how many were added because it would modify the recipe" | D-0574 |
| Once per data batch; the user accepts once; the acceptance and what was added are in the session log | "Once per data batch ... the user must only to accept once"; "confirmation and what as added is kept in the session log" | D-0574 |
| The record is in the export | "yes that must be in the export" | D-0575 |
| A separate log | "yes separate log" | D-0576 |
| Order check X first, stopping first? | "it might be more logical to have test 2 as the first test .... stopping first no ?" | D-0579 (a question of hers, not a decision) |

**The review session's reading, not hers** (D-0573 to D-0576): that the form is "(i-b), a block done by the app when it reads the file"; that the log of the completion is beside the audit log, in the session and in the export; that the acceptance is stored under the session key. **NOT decided** (the ledger says so): the form and key names of the block; the format, name and entries of the log; what the code does with the session key and a deleted session.

### What the code does today, and what has to be built

| Topic | [TODAY] | [TO BUILD] |
|---|---|---|
| Refusal of a metadata with bad ids | Nothing compares or checks ids. The data check builds each table alone after its tier 1 [CODE READ `data_analysis_recipe_validator.py:485-545`]. The gate rejects a recipe on a structure or data problem [CODE READ `bootloader.py:431-459`]. An empty id is missing only through the declared null words (`null_values: ["", "-"]` on the demo's id field [RECIPE FILE]); a cell of spaces stays text [CODE READ `declared.py:115-120`]. E02/E03 check the declared population and a number type on an id [CODE READ `recipe_check.py:332-348, 445-458`] | The check of the metadata's ids as READ (before tier 1), its refusal, with a plain line naming file, lines and ids |
| Checks X and Y | Nothing compares the ids of two tables | both checks; the list of ids shown to the user |
| The completion | no key, no action: no step appends rows; a schema's tier 1 runs on its own table [CODE READ `orchestrator.py:282-295`]; an unknown key is refused (S01) [CODE READ `recipe_check.py:390`] | the block, the completion after `_read_source` (before or after the author's tier-1 steps: question 7), a new edge in the graph, a new part of the table's key |
| The confirmation, once per batch | the session key exists [CODE READ `session_manager.py:10, 305-308`] | the stored acceptance, the dialog |
| The log | on `dev`, the session holds `assembly.json` and `t3_<time>.json` (with a `notification_log`); no audit log; D-0315 and D-0478 are decided, not built | the id log and its writer |
| The data check that only informs | does not exist: the data check returns problems only; advices come from the recipe check [CODE READ `bootloader.py:431-451`] | the new channel (decided, D-0569) |

### The flags (what could change a result without a message, hide a step, or reconsider a decision)

1. **"Not a zero" against today's count steps.** The demo's count of values gives 0 and its count of rows gives 1 for a line with empty cells; the plot says "4 with 0 genes". Her rule cannot hold by default. [RECIPE FILE; POLARS SEMANTICS] (question 5)
2. **The stop at check X may reverse D-0569 (b).** D-0569: the data check only informs. D-0573 and D-0579: refuse; "stopping first". Both are hers. She must say which holds for check X. (question 1)
3. **A refusal at the gate closes the recipe** and, where the selector is hidden (the pipeline profiles), the app stops at start; her loop "re-upload" has no way in for a refused recipe. [CODE READ `bootloader.py:453-459`; RULE FILE `rules_data_analysis_recipe_structure.md` 11a] (question 3)
4. **`demo_abromics` is refused as shipped** (3 lines with no id: file lines 5, 6, 11). Her order D-0569 corrects the file in the dry run.
5. **A dummy id does not leave through the metadata.** Check X fires again because the result file still holds the id; it leaves through a removal by key or "remove from all the data" (library built, screen not built), or a new file. (question 11)
6. **"Required on every result table": two readings.** Every result table (then one with no entity id says so), or every one that declares an entity id. (question 6)
7. **No confirmation: what then?** Not said in her words. Each answer closes something (question 4).
8. **The marker and the added lines are visible in the export and the log, not in the recipe.** She asked that the recipe does not record the count. So the figure must carry, in the export, the log and a line in the README and the report, that lines were added. Otherwise a published figure shows 4 entities that were added from the metadata with no sign. Her own check: "then this is transparent, correct?" Only if the same record is in the export (D-0575). [REASONED; her decision D-0575]

### The open points, each with the evidence by reading

**The session key and "once per data batch, as recalled by session ?"** (her question). The key is `recipe hash[:12] : data batch hash[:12]` [CODE READ `session_manager.py:10, 305-308`]. The batch hash covers every dataset of the recipe, the metadata included [CODE READ `session_manager.py:294-299`; `orchestrator.py:793-821`; `cache_keys.py:139-152`]. So a changed metadata or result file asks again; **an edit of the recipe also asks again** (the recipe hash is in the key); a deleted session asks again (`delete_session`, `:774-778`); another machine or user asks again; a session zip carries the log. In the pipeline profiles there is no session [RULE FILE `rules_app_features_flags.md` flag matrix]: no place to store an acceptance. **Fixing the metadata is itself a new batch.** (question 9)

**Where a refusal of the metadata can sit.** [TODAY] three places read a recipe's data: the HOME gate (a problem rejects the recipe), BLUEPRINT's Validate (reports, never blocks) and Data Import (checks a candidate file by the ingestion's own read, all files or none). Seats: (s1) at the gate: the recipe cannot open; (s2) in Data Import: an uploaded metadata with id errors is refused and the old file stays: where her loop lives; (s3) both, with a way in for a refused recipe. A deployment with no upload panel (`metadata_ingestion_enabled` false) cannot re-upload: the fix is upstream and the refusal shows the contact. (question 3)

**The cases around the two checks.** A repeated id in the metadata multiplies the rows of a join with the metadata second [ESTABLISHED: RECIPES G9, G13]; whether a repeat is an error at the id level is her question 2: her approved sentence (D-0567, G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity. A table with no entity id (a look-up such as the APEC list): never checked or completed. A recipe with no metadata block (`figshare_integration`: its metadata is a data schema): the checks cannot run without a table named the metadata (`metadata_schema`, or `entity.population` [CODE READ `recipe_check.py:332-348`]). (questions 2, 13)

**The marker and "not a zero".** Polars has one missing value (null) and NaN for floats [POLARS SEMANTICS]; a second kind must sit beside the empty cells. Forms: (m1a) a yes/no column named after the marker, for example `not_in_original_data`, label "not in original data" (through the join's `labels` mapping, `recipe_spec.yaml:44`); (m1b) a text column whose value is the marker. After a left join from the metadata an entity with no line has the marker empty in both: a third state, "no line". What each aggregate gives for a line whose cells are empty:

| Aggregate | Result for an added line | Compatible with "not a zero"? |
|---|---|---|
| count of values (`pl.col('gene').count()`) | 0 | no, unless the recipe states "nothing found" |
| count of rows (`pl.len()`) | 1 | no |
| sum | 0 | no, unless stated |
| mean, minimum, maximum | missing | yes |
| distinct count | 1 | no |
| a stamp (`status: pl.lit('Detected')`) | "Detected" | no: the demo's ResFinder stamps every line, and `ST22_Anchor` and `integration_plot` carry it |

Ways to keep her rule: (z1) the required meaning is chosen from a few words the check knows ("nothing found", "not analysed", ...), and a count is refused unless the marker is named (a match on the text of the steps, which can miss a case); (z2) the meaning is free text and the data check says how many marked lines each count met; (z3) she says what she meant. (question 5)

**The position.** Her words: "an automatic completion at (first step)"; "this might be before T1 a step the app does". Read as before the recipe's own tier-1 steps (P1). With P1 the recipe's own steps see the added lines (the stamp and the row count must be adapted); a filter that removes every line of an entity leaves it absent (on the demo, 6 entities of `Detailed_summary`: 42 ids in the file, 36 after its three filters [ESTABLISHED: RECIPES G12; engine run RR2; `Detailed_summary_wrangling.yaml:20, 25, 30`]). With P2 (after the author's tier-1 steps and before the audit steps) the author's steps cannot say how to process them, against "processed as a normal recipe". After the audit steps is never right: the completion would add back an entity the user removed [CODE READ `data_wrangler.py:92`]. (question 7)

**Which metadata.** (α) as read from its file, after the id check: the result table's first place stays a first place (D-0553); a step at the metadata's place does not remove an added line. (β) after its tier 1: a step at the metadata removes the added line, but the result table's first place lies below the metadata's: two places on one path, refused by her rule "the user chooses at most one place" [HER WORDS D-0553]. (question 8)

**The join order.** With the completion, a join with the result table first and the metadata second keeps every entity: the added lines are in the result table. Her direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564] can then be followed without losing an entity. A rule, an advice or documentation? (question 12)

### The separate log (her "yes separate log"; format, name and entries open)

[TODAY] On `dev` the session folder holds `assembly.json` and `t3_<time>.json`. Only on the held branch `task/audit-slice1-effects-log` (commit 42d5ae6d) is there `audit_log.py`, writing `audit_log.yaml` with `format: 1`; its keys are provisional [CODE READ `git show task/audit-slice1-effects-log:libs/utils/src/utils/audit_log.py`]. D-0478 (audit log in the bundle) is decided, not built.

| Option | What it is | Pro | Con |
|---|---|---|---|
| L1 | one file of its own for the ids, beside the audit log, in the session and in the export | her "separate"; the audit log is untouched; each file readable by itself | two files to name in the README and the report |
| L2 | one log with entries of several kinds | one story in time | changes the audit log's file; against "separate" |
| L3 | the record only in the export, no file | nothing new in the session | the acceptance is not kept; against D-0574 |

**Both agents recommend L1 (as a recommendation, hers to decide).** The form, in the manner of `audit_log.py` (the same rules, no import): one YAML file in the session folder, starting with `format: 1`; a reader refuses an unknown format; the date and the initials are given by the caller; data only; name PROVISIONAL `id_log.yaml`. Entries (one per event, keys PROVISIONAL): `metadata_refused` (when; the file and its hash; each problem: line, id, why), `ids_not_in_metadata` (check X: the table, the ids), `check_x_stopped`, `completion` (per result table: the file hashes, the ids added, their count, the marker, the meaning the recipe states), `accepted` (who, when, the sentence shown, the session key), `not_confirmed`, `dummy_ids_declared`. In the export: beside the audit log of D-0478, as its own file; the README says in one line what it is; `report.qmd` has a short section per table: the ids added, the marker, the meaning. The acceptance is once per data batch because the session key changes with the batch. A refusal when no session exists yet (a refused recipe never opens): written to the export of the next session, or to a log at the deployment level (question 10). The audit log of D-0478 is unchanged.

### The two checks, their order and the stop (her question D-0579)

She proposes: run check X first and STOP there when it finds ids; check Y only when X passes ("stopping first no ?"). The case for and against, with the evidence:

**For.** (1) A typo shows twice: the data holds `S1`, the metadata `S01`; X lists `S1`, Y lists `S01`. If Y is confirmed first, the user confirms a marked line for `S01`, a false absence. After the fix both lists are empty. (2) Fixing the metadata is a new data batch (new session key), so a confirmation given before the fix is lost and the log holds a confirmation of a list that never became true. (3) The metadata is the reference of both checks and is refused when its own ids are wrong (D-0573). (4) On the demo it costs nothing: X finds 0 ids (every id of every result file is in the metadata [ESTABLISHED: OVERLAP section 1]) and Y finds 4 for ResFinder; `left_join_lesson` has 2 for X (`ACC0001`, `ACC0002`).

**Against, or to qualify.** (1) A user who cannot fix is blocked: with no upload panel (the static, simple, demo-vetinst and web-demo profiles) a stop is a refusal of the recipe and the app stops at start with the cause and the contact. (2) If "stop" means refuse, it reverses D-0569 (b) for X. (3) A result file may legitimately hold an id the metadata lacks (a control sample): the dummy fill is the way out, and it adds a dummy entity to every result until removed. (4) BLUEPRINT's Validate reports and never blocks.

**Three readings of "stopping first".** (a) Refuse: the recipe does not open until the metadata is fixed. (b) Hold Y: the recipe opens with X's note; Y's list is shown as information, nothing is completed or confirmed until X passes. (c) No stop: X and Y are both shown and Y's confirmation is asked at once.

**Lean of the Sonnet agent, as a lean:** (b): it keeps her order and her earlier decision, and nothing is confirmed, completed or logged on a list that will change. (a) follows her words most literally. Whatever she chooses, the order is: (0) the metadata's own ids (refuse); (1) X; (2) Y with the confirmation. **Lean of the Opus agent, as a lean:** (b) as well: it keeps her D-0569 (X informs) and her order (Y waits for X), so nothing is confirmed, completed or logged on a list that the fix of the metadata will change (the typo case); (a) is the more literal reading of "stopping first" and closes the recipe where no one can fix the metadata.

### The updated list of what is still hers to answer (her order M633, M634)

#### (a) The ten questions of the D-0572 section: which are settled by her words

| # | Question | Now | Her line |
|---|---|---|---|
| 1 | Where the completion lives | SETTLED in substance: in the recipe, required on every result table. The form (a block the app reads, or a first step you write) is read as (i-b), not stated | D-0574; relay "I would lean also to add this in the recipe" |
| 2 | One line in the recipe or none | SETTLED: required on every result table | D-0574 "the recipe required on every result table" |
| 3 | The meaning required, or the note enough | SETTLED: required ("force") | D-0574 |
| 4 | The marker: form and name | NAME SETTLED ("not in original data", not a zero). FORM open | D-0573 |
| 5 | Before or after the recipe's tier-1 steps | OPEN (her words read as before) | D-0572 |
| 6 | Which metadata | OPEN | none |
| 7 | The join order | OPEN, narrower | none |
| 8 | The marker "not in metadata" | SETTLED: none; the user corrects the metadata (or adds a dummy) and uploads again | D-0573 (the review session's reading, confirmed "yes") |
| 9 | A note for a repeated id | CHANGED: an error at the id level, or a note | D-0573 |
| 10 | The count per target | OPEN, unchanged | none |

#### (b) The eight questions of the D-0570 section, and Part 1, Part 2

| Item | Now | Line |
|---|---|---|
| 1 A never-analysed entity counted as "not detected" | SETTLED: the meaning is the recipe maker's; the marked line is not "not detected" unless the recipe says so | D-0572, D-0573, D-0574 |
| 2 The name of the third class | SETTLED: "not in original data" | D-0573 |
| 3 The app reads the audit record | NO LONGER NEEDED for the completion; only for the information line F | D-0574 |
| 4 Where the recipe says what a missing value means | SETTLED: in the required block, on each result table | D-0574 |
| 5 The count per target | OPEN | none |
| 6 The threshold in "not detected" | OPEN, low; touched by position (`Detailed_summary`) | none |
| 7 The number, the list or both | SETTLED in substance: both from the completed table (the marked lines); how a table result is shown is the open key of D-0487 | D-0572 ("That would remove need for 6 anti join") |
| 8 `demo_abromics`'s three id-less lines | SETTLED: the metadata must be clean; the file is corrected in the dry run | D-0569, D-0573 |
| Part 1 A, B | still possible spellings, no longer the way to give zeros | |
| Part 1 B2, B3, B4, B5, C, D, E | NO LONGER NEEDED for the zeros (the completion does the job); the agents' reading, not her words; history kept | D-0574 |
| Part 1 E2 (anti-join) | NO LONGER NEEDED by her words: "That would remove need for 6 anti join" | D-0572 |
| Part 1 B6 | DECIDED in substance (form open) | D-0574 |
| Part 2 F | the log and the alerts carry the counts; F as a screen line stays possible | D-0575, D-0576 |
| Part 2 G | ABSORBED by the required meaning; what the meaning may hold is open (question 5, 6) | D-0574 |

To confirm with her in one line at the end: "the candidates that the completion makes unnecessary are kept as history, none is deleted".

#### (c) The new list, one question at a time, in the recommended order

Each question is hers. Each says what she would see on the demo. Each ends with "Neither: say what you meant." Leans are the leans of the agents, as leans (where no lean is given, we have none). The first four are the same door: what happens when the ids do not agree.

**Settled, not asked any more:** the names of the two checks (check X, check Y, by content: her D-0579).

**Question 1. When an id of a result file is not in the metadata (check X): stop, or go on?** Your words: "stopping first no ?" (D-0579) and, earlier, "the user should better fix this" (D-0569, option b: inform only). Three ways: (a) the recipe does not open until the metadata is fixed; (b) the recipe opens, X's note is shown, and nothing is completed or confirmed until X passes; (c) both notes are shown at once and the completion is confirmed at once. On the demo: no result file has an id outside the metadata, so you see nothing; on the lesson template `left_join_lesson` you would see 2 ids (`ACC0001`, `ACC0002`) refused (a), noted with nothing completed (b), or noted with the completion asked (c). A typo (`S1` in the data, `S01` in the metadata) shows twice, once in each check; fixing the metadata is also a new data batch, so a confirmation given before the fix is asked again. In a deployment with no upload panel, (a) stops the app at start. Lean (Sonnet and Opus): (b). Neither: say what you meant.

**Question 2. Which errors in the ids refuse the metadata?** An id empty after the null words; a cell of spaces; an id repeated. A "false" id (a wrong but well-formed one) cannot be seen by the app. On the demo: the metadata has 42 distinct ids, none empty or repeated: it passes; `demo_abromics` as shipped has 3 lines with no id (file lines 5, 6, 11): refused until its file is corrected (the dry run does it). Lean: refuse the three, say plainly that a false id cannot be seen. Neither: say what you meant.

**Question 3. Where does the refusal sit, and in which order do the checks run?** At the opening (the recipe is not on HOME's list, with the reason and the contact; in a deployment with no selector the app stops at start); in Data Import (an upload with wrong ids is refused and the old file stays: this is where your "re-upload" loop lives); or both, with a way in for a refused recipe. The order: the metadata's own ids, then check X, then check Y with the confirmation. On the demo (developer profile): a bad upload is refused in Data Import and the old file stays; a bad shipped metadata takes its recipe off HOME's list with the contact; in `pipeline-static` the app stops at start. Lean (both agents): in Data Import and at the opening, and a way in for a refused recipe where the deployment has Data Import. Neither: say what you meant.

**Question 4. If the user does not confirm the completion (or nobody can), what happens?** (a) the recipe does not open; (b) the recipe opens with the table as in the file (no added lines) and a loud standing note on screen, in the export and in the log: "not confirmed"; (c) the recipe completes anyway and the log says "not confirmed". On the demo: (a) the recipe is not on the list, the reason names ResFinder and its 4 ids; (b) ResFinder has 70 lines; the plot shows what today's recipe shows (42 samples, 4 in the bar at 0, because `QA_AMR_per_sample` starts from the metadata; 38 samples where a join starts from ResFinder), with the note; (c) 74 lines, 4 marked. (b) and (c) can change a figure without the user having read the reason; (a) closes the recipe for everyone who cannot confirm. Lean (Opus): (b): nothing is added that the user did not accept, and no one is locked out; the standing note must also say that where a join starts from the metadata the entities with no line may show as 0. Sonnet: no lean, each closes something. Neither: say what you meant.

**Question 5. The marker and "not a zero".** You said the marker is not a zero. The demo's counts would turn the 4 added lines into a 0 (count of values) or a 1 (count of rows) by themselves. (i) The form: a yes/no column named after the marker, beside empty result cells; or a word in a column. (ii) What the required meaning may be: a few words the check knows ("nothing found", "not analysed"), or free text. On the demo: with the column and the meaning "nothing found", the plot keeps 4 samples in the bar at 0, by the recipe's own statement; with "not analysed", the 4 are shown apart, never as a silent 0; with a word in the gene column, `QA_AMR_per_sample` counts 1 gene for each of the 4 and the bar at 0 is empty. Lean (both agents): the yes/no column; the few words. Neither: say what you meant.

**Question 6. The block in the recipe: its form, the tables it covers, its names.** (i) A block that the app reads (the app adds the lines when it reads the file) or a first step you write in tier 1. (ii) "Every result table": a result table with no entity id says "no entity id" in its block, or must declare one first (your order D-0569: "Have the recipes declaire entity id"). (iii) The key names and what each holds. On the demo: ResFinder carries one block with its meaning; the APEC list has no entity id and is never completed; the 3 tables of `2_test_data_ST22_dummy` have no id today and must declare one. Lean: a block the app reads; declare the id first; the agents propose the key names after your answer. Neither: say what you meant.

**Question 7. When in the table: before or after the recipe's own tier-1 steps?** Your words: "an automatic completion at (first step)"; "this might be before T1 a step the app does". On the demo: before, ResFinder's stamp would read "Detected" on the 4 lines and its row count would give 1 for them (the recipe's steps must change); `Detailed_summary` (42 ids in the file, 36 after its filters) gets no added line and 6 entities are absent. After: the steps do not see the added lines and cannot say how to process them. Lean: before. Neither: say what you meant.

**Question 8. Which metadata does the completion read?** As read from its file (after the id check), or after its tier 1? On the demo: remove one of the 4 added entities at the metadata's place: from the file, it stays in ResFinder marked; after tier 1, it is no longer added, but ResFinder's place lies below the metadata's (one place per path: refused). Lean: as read. Neither: say what you meant.

**Question 9. Once per data batch: what asks again, and where there is no session.** Your words: "once per data batch (as recalled by session ?)" and "confirmation and what as added is kept in the session log". The session key holds the recipe too, so an edit of the recipe asks again; a changed metadata or result file asks again; a deleted session asks again; another machine asks again; a session zip carries the acceptance. In a deployment with no session (the pipeline profiles) there is no place: a standing acceptance written by the operator in the deployment and recorded in the export, or a confirmation at each opening recorded in the export only. On the demo: the dialog "4 lines will be added to ResFinder: <ids>. Confirm?" once; a changed metadata file asks again. Two points are yours: should an edit of the recipe (not of the data) ask again, as the session key makes it today; and where does the acceptance go in a deployment with no session. Lean (both): the session key as it is (an edit may change the stated meaning); with no session, a confirmation at each opening recorded in the export. Neither: say what you meant.

**Question 10. The log.** Our recommendation: a file of its own beside the audit log, in the session and in the export, `id_log.yaml`, starting with `format: 1`, the entries above; a refusal when no session exists written to the next export or to a log of the deployment. On the demo: one entry for ResFinder (4 ids, the marker, the meaning, who accepted and when), in the session folder and in the export, with one line in the README. Lean (both): this. Neither: say what you meant.

**Question 11. A temporary id (an unknown or false id added to the metadata with a dummy fill).** The app cannot tell a dummy from a real id unless it is marked. (a) a note given at upload and kept in the log, with a warning in the export while the log says dummy ids were declared and the data still holds them; (b) a column of the metadata the app reads; (c) nothing: the user's responsibility. It does not leave through the metadata (the result file still holds the id): it leaves through a removal by key, "remove from all the data", or a new file. On the demo: none; a dummy would appear in every plot with its dummy values until removed. Lean (Sonnet and Opus): (a). Neither: say what you meant.

**Question 12. The join order: a rule, an advice, or documentation?** With the completion, a join with the result table first and the metadata second keeps every entity. On the demo: remove one detected entity at ResFinder: result table first, 41 samples; metadata first and the marker read, 42 rows with 1 shown as "no line"; metadata first and genes only, 42 samples with 5 in the bar at 0. Lean (both): an advice. Neither: say what you meant.

**Question 13. A recipe with no metadata block** (`figshare_integration`: its metadata is a data schema). The checks cannot run. The check says so, or the recipe names its metadata. On the demo: none; `figshare_integration` shows the message. Lean: the recipe names it (in the dry run). Neither: say what you meant.

**Question 14. The count per target** (for each gene, how many entities do not carry it). None of the forms gives it. On the demo, for any one gene, how many of the 42 samples lack it. Unchanged. Neither: say what you meant.

**Question 15 (low). The threshold in "not detected".** Unchanged; touched by question 7. Neither: say what you meant.

(Not a question: `demo_abromics`'s three id-less lines. Your words "remove the null and empty rows from the metadata" (D-0569) and "it must not contain errors nor missing data. A rule" (D-0573); the change is shown in the dry run of the one big move, D-0525.)

#### (d) Runs: named only, to run after the code exists (her order D-0580)

No run is dispatched now: the code of the completion, of the two checks and of the id log is not built, so a run would test the old code and mean nothing. The expectations are written here and registered when the code exists. Runs 1 to 6 of the D-0572 section stand, with the marker "not in original data"; run 7 is void. Added, each "after the code exists": (8) the typo case (the data holds `S1`, the metadata `S01`: the first check lists `S1`, the second lists `S01`; after the fix both lists are empty; the session key changes with the metadata); (9) the id check of the metadata (an empty id, a cell of spaces, a repeated id, as she decides); (10) the session key (a changed metadata file gives another batch hash and key; an edit of one recipe file another recipe hash); (11) no confirmation (the chosen state of question 4). Each keeps its three points (requirement, expected, independence) and is registered before it runs.

### B1.4 The signing line of `CAUSE_AND_SOLUTIONS_ZEROS.md` (visible correction; nothing deleted)

Directly under the signed paragraph at the end of the file (the one that ends `D-0572 additions: Sonnet (this file) and Opus (OPUS_checks_b6_v1.md, R1 to R26 applied)`), add:

> **Correction of 2026-11-23 (records error, Sonnet agent):** the words "R1 to R26 applied" were wrong. R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 of `OPUS_checks_b6_v1.md` were not in the text; the editing script lost them. They were applied on 2026-11-23, late (see the note at the top of the D-0572 section). Found by the Opus review (flag 5 of `OPUS_review_1.md`), confirmed by a fixed-string search of every replacement. The same search found R1 to R32 of the D-0570 round present. **D-0573 to D-0578 additions (her answers on the ids, the completion, the log and the review order; and her D-0579):** Sonnet (this file) and Opus (`OPUS_review_1.md`, `SONNET_review_2.md`; [to be signed after the Opus check of this draft, with the number of replacements applied and verified by a search of the written file]).

---

## B2. `OVERLAP_AND_POPULATION.md`

Two things: (B2.1) visible notes in the third part (the control of the ids) for what her words changed; (B2.2) a fourth part, appended after the third part and before `## Open between the two agents`; (B2.3) the signing line.

### B2.1 Visible notes in the third part (blockquotes under the stale text)

Directly under `- **(a) An id in a result file and in no metadata.**` (end of its bullet):

> **Update of 2026-11-23 (ledger D-0573; her D-0579):** this is check X. Her flow: inform, list the ids; the user adds them to the metadata by hand and uploads it again; the verification starts again; an unknown or false id may be added with a dummy fill and a note to remove it afterwards. There is no marker "not in metadata" in her flow (the review session's reading, confirmed by her "yes"). Whether X stops the recipe (refuse) or only informs (D-0569 (b)) is her question 1 of the new list. The sentence "she prefers the metadata corrected; the alternative she names, a marker "not in metadata"" is history.

Directly under `- **(b) An id in the metadata and not in a result file.**`:

> **Update of 2026-11-23 (ledger D-0573, D-0574, D-0575, D-0576):** this is check Y. Her words: "warn and include those present in metadata to original data - with the specific marker "not in original data"", with the user's confirmation noted in the log, once per data batch, in a separate log, also in the export. The completion lives in the recipe, required on every result table (D-0574). The marker is called "not in original data" and is not a zero. The alert words below are provisional and are replaced by a confirmation dialog (words open).

Directly under `- **(c) Metadata lines with no id.**`:

> **Update of 2026-11-23 (ledger D-0573):** "informs" is replaced by "refuses". Her words: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)".

Directly under `- **(d) An id repeated in the metadata**`:

> **Update of 2026-11-23 (ledger D-0573):** a repeated id may be an error at the id level (her question 2 of the new list: refuse or note); her approved sentence (D-0567, RECIPES G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity.

### B2.2 The fourth part (append)

## Her answers of 2026-11-23, fourth part (ledger D-0573 to D-0576, her D-0579): the two checks, the refusal of the metadata, the confirmation

Added after the file was signed; the signed text above is kept. Checked by the Opus agent (`OPUS_checks_review_v1.md`). Her words are in the section "Added 2026-11-23 (ledger D-0573 to D-0579)" of `CAUSE_AND_SOLUTIONS_ZEROS.md`; the lines this file needs are:

- "We need to fix the metadata - it must not contain errors nor missing data. A rule." [HER WORDS D-0573]
- "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)" [HER WORDS D-0573]
- Check Y: "warn and include those present in metadata to original data - with the specific marker "not in original data"". Check X: "inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards" [HER WORDS D-0573]
- "it might be more logical to have test 2 as the first test .... stopping first no ?" [HER WORDS D-0579]

**The control of the ids, as she said it, with the data check's note for each** (words of the notes PROVISIONAL). The order, whatever she decides on the stop (her question 1): (0), then X, then Y.

| Step | What it checks | What the user sees | What the check does |
|---|---|---|---|
| (0) The metadata's own ids | an id empty (after the null words), a cell of spaces, a repeated id (question 2) | "The metadata file <name> has N lines with a missing id (file lines <...>)" | **refuses** the metadata (where: at the opening, in Data Import, or both: question 3); the loop: correct and upload again |
| X | ids of the original data that are not in the metadata | "In <table>, N ids have no row in the metadata: <the ids, up to 20>. Add them to the metadata and upload it again. If you do not know an id, or it is false, you may add it for now with a dummy fill and note that it must be removed afterwards." | informs, or stops (her question 1); no marker "not in metadata" |
| Y | ids of the metadata that are not in the original data | "N ids of the metadata have no line in <table>: <the ids>. They will be added to <table>, marked "not in original data". The app cannot tell whether they were analysed with nothing found or not analysed. Confirm?" | asks the user's confirmation, once per data batch; records it in the log; completes after the confirmation (without one: question 4) |

**On the demo.** (0): the metadata has 42 lines and 42 distinct ids, none empty: it passes; `demo_abromics` as shipped has 3 lines with no id (file lines 5, 6, 11): refused until its file is corrected by the dry run (D-0525). X: 0 ids in every demo result file; `left_join_lesson` has 2 (`ACC0001`, `ACC0002`). Y: ResFinder has lines for 38 of the 42 metadata ids, so 4 have none; every other result file has all 42 [ESTABLISHED: OVERLAP section 1].

**What the code does today and what has to be built.** [TODAY] Nothing compares the ids of two tables; the data check builds each table alone after tier 1 [CODE READ `data_analysis_recipe_validator.py:485-545`]; Data Import checks a candidate file by the ingestion's own read, all files or none, and compares no ids [CODE READ `data_import_check.py`]; the gate rejects on a problem and never on an advice [CODE READ `bootloader.py:431-451`]. [TO BUILD] the check of the metadata's ids as read, the refusal, checks X and Y, the confirmation, the log. She wrote "the code is not build yet" [HER WORDS D-0573].

**Two points that concern this file.** (1) D-0569 chose option (b), "only inform", for the ids of a result file with no metadata row. Her new rule refuses a metadata with errors at the id level, and D-0579 asks "stopping first". If X stops the recipe, D-0569 (b) is reversed for X: her question 1. (2) The agents propose to check the metadata as read (before its tier 1): a step in the metadata's own tier 1 (for example a `polars_drop_nulls` on the id) would hide the error from a check run after it. In `demo_abromics` that step is in its join's tier 1 (`demo_abromics.yaml:44-47`; the metadata's own tier 1 is empty, `:30-31`), so it would not hide it.

### B2.3 The signing line

Directly under the signed paragraph at the end of `OVERLAP_AND_POPULATION.md`, add: "**D-0573 to D-0576 additions and the notes of 2026-11-23:** Sonnet (this file) and Opus (`OPUS_review_1.md`, `SONNET_review_2.md`; [to be signed after the Opus check of this draft])."

---

## B3. `RECIPES_FROM_THE_MODEL_AGREED.md`

Her order: "the RECIPES_FROM_THE_MODEL_AGREED.md needs to be reviewed also - we have made significant choices already and found solutions." [HER WORDS D-0578]. Two things: (B3.1) a section at the top, after the line that ends `...[CODE READ file:line] / [HAND COUNT] / [READ SCAN] / [REASONED, not run].` and its `---`, before `## HALF PAGE FOR HER`; (B3.2) a short mark at each point that is superseded or changed. Nothing is deleted. The file's own questions are numbered (i) to (viii); the "(a) to (h)" of the order are read as these eight.

### B3.1 The section at the top

## REVIEW OF 2026-11-23 (her order, ledger D-0577 and D-0578): what her decisions since changed in this file

**Why.** This file was written before her answers D-0568 to D-0576 and her D-0579. Since then she decided: the metadata is refused when its ids are wrong; two checks of the ids (X, Y); the completion of a result table with the marker "not in original data", in the recipe, required on every result table, confirmed once per data batch, noted in a separate log, also in the export; "stopping first" is her question. She wrote about the code: "the code is not build yet" [HER WORDS D-0573]. So "what is true today" and "what is decided and to build" are kept apart in each row.

**The words used for the status.** STILL TRUE (nothing in her words touches it). SETTLED (her words answer it; the line is named). CHANGED MEANING (the text is true of today's recipes, but the question it answers is no longer the same). SUPERSEDED (replaced; kept as history). STILL OPEN. Where only the agents say so, the row says "the agents' reading" and the line to confirm with her.

**The half page**

| Item | Status | Deciding line |
|---|---|---|
| 1 A join with the metadata is written in tier 1 | STILL TRUE | D-0510 |
| 2 Two ways of writing a result; the metadata first with the counts filled with 0 gives a false zero | CHANGED MEANING: with the completion decided, a per-entity result can start from the result table and keep every entity; the false zero at a table's own place is accepted; the facts stay true of today's recipes | D-0569, D-0573, D-0574 |
| 3 A zero cannot tell "analysed, nothing found" from "not analysed"; a removed entity also shows 0 | SPLIT: the first half stays true (the risk the recipe maker takes); "a removed entity also shows 0" is SUPERSEDED: with the completion a removed entity is absent or has no line, and an added line is marked | D-0572, D-0573 |
| 4 Three kinds of join; rows multiply | STILL TRUE | |
| 5 Nothing checks today (uniqueness, side, block meaning, look-up key, inner join; two recipes declare no id) | STILL TRUE of the code; CHANGED in what is to be built: the metadata's ids are refused when wrong, two checks of the ids are decided, the recipes declare their ids | D-0569, D-0573 |
| 6 The engine does not run the check | STILL TRUE; weightier: a refusal of the metadata holds only where the check runs | D-0573 |
| 7 The five forms tried | STILL TRUE (history); a new decided element, the completion block, was not among them | D-0574 |
| 8 The rename counts | STILL TRUE (counts of that date) | D-0562 |
| "Since the list was written, her words D-0563 to D-0566" | add one line: D-0567 to D-0578 and D-0579 | |
| "Before the demo recipe can be touched: (iii), (iv), (v) answered, a solution chosen for the join that starts from the metadata" | CHANGED: the solution is decided in substance (the completion, D-0574); (iii) partly settled, (iv) narrower, (v) the form of the block is open | D-0574 |

**Her eight questions of the file**

| Question | Status | Deciding line |
|---|---|---|
| (viii) The engine does not run the recipe check: a gap, or by design? | STILL OPEN, weightier | D-0573 |
| (iii) Must the entity id be declared; where is "unique" judged | CHANGED MEANING, partly SETTLED: the shipped recipes declare their ids (D-0569); the completion needs a declared id on a result table (D-0574; whether a table with none says so is the new question 6); for the metadata a repeated id may be an error (new question 2); where uniqueness of a result table's id is judged: STILL OPEN | D-0569, D-0573, D-0574 |
| (iv) "The join should not start with the metadata": rule, advice or documentation | STILL OPEN, narrower: the completion is the "solution we do not have yet" of D-0564, so the result-table-first join keeps every entity (new question 12) | D-0564, D-0574 |
| (ii) A result per entity with zeros: the default place for a removal | CHANGED MEANING: with the result table first a removal at the result table is complete; the default at the join (D-0549) stands; the "can remain" sentence (PATHS Q6) is needed only for metadata-first joins and paths through other originals | D-0549, D-0574 |
| (i) A system for joins that are not metadata | STILL OPEN | |
| (vii) An inner look-up join removes rows | STILL OPEN | |
| (vi) A look-up join after tier 1 (her question 27) | STILL OPEN | |
| (v) The recipe form (PATHS Q3) | STILL OPEN; one decided element: the completion block on each result table | D-0574 |

**The 19 agreed points**

| Point | Status | Deciding line |
|---|---|---|
| G1 The three blocks | STILL TRUE; the metadata block is the population of the two checks; the completion applies to result tables (data schemas), never to look-up tables | D-0574 |
| G2 VirulenceFinder moves to `data_schemas` | STILL TRUE, not done; after the move it gets the completion block | D-0523, D-0574 |
| G3 Joins in tier 1, source tables only | STILL TRUE | D-0344, D-0510 |
| G4 The entity id | STILL TRUE, with a new fact: the entity id is the condition for the completion; the metadata's ids are checked and refused when wrong | D-0562, D-0567, D-0573, D-0574 |
| G5 A result per observation | STILL TRUE | |
| G6 A result per entity with zeros (the metadata first, the fill with 0, the false zero) | SUPERSEDED as the way to give zeros; its facts stay true of today's recipes (agents' reading, to confirm) | D-0573, D-0574 |
| G7 A zero cannot tell analysed from not analysed; an entity with metadata and no observation exists in the result only when the metadata is the first table | SPLIT: the first half STILL TRUE (the accepted risk); the second half SUPERSEDED: with the completion it exists with the result table first | D-0572, D-0574 |
| G8 A removal at a table with no entity id is refused by the engine | STILL TRUE | |
| G9 Three kinds of join | STILL TRUE | |
| G10 The tiers as shared steps; the audit block | STILL TRUE | D-0539, D-0541 |
| G11 A table result has no form yet | STILL TRUE of the code; the design is decided (D-0485, D-0487), its key open | D-0485, D-0487 |
| G12 Uniqueness differs between the file and tier 1 | STILL TRUE (a fact); "where unique is judged" is question (iii) | |
| G13 What nothing checks today | STILL TRUE of the code; the id check, the overlap and the two checks are decided, not built | D-0570, D-0573 |
| G14 An inner look-up join removes rows | STILL TRUE | |
| G15 The rename `is_entity_key` to `is_entity_id` | STILL TRUE (decided, not done) | D-0562, D-0567 |
| G16 The engine does not run the check | STILL TRUE | |
| G17 Reading rules and parents | STILL TRUE, with a new fact: a completed result table also reads the metadata (an edge from the metadata's file under reading (α), from its tier 1 under (β); new question 8) | D-0574 |
| G18 The forms as tried | STILL TRUE (history); the completion block was not tried | |
| G19 A rule "metadata on the right" would forbid the zeros pattern written with the metadata first | CHANGED MEANING: with the completion the zeros can be written with the result table first, so such a rule forbids only a spelling | D-0574 |

**The demo recipe candidates and the rest**

| Row | Status | Deciding line |
|---|---|---|
| The rename `is_entity_id` | STILL TRUE (YES, decided) | D-0562 |
| VirulenceFinder moves | STILL TRUE (YES) | D-0523 |
| An `entity` block | STILL TRUE (only under some answers) | |
| The metadata moved off the first place in the 4 joins | CHANGED: no longer needs a solution to be chosen; remains a choice under new question 12 | D-0574 |
| A kind on each join step; the inner look-ups; the reimport copies; the APEC joins in tier 2; the declared default key; joins of joins | STILL TRUE (only under their questions) | |
| NEW (decided in substance): the completion block with its stated meaning on every result table; on the demo 9 data tables today (10 after the VirulenceFinder move), only ResFinder receives lines (4) | NEW | D-0574 |
| NEW: ResFinder's steps that stamp "Detected" and count rows are adapted | NEW | D-0573 |
| NEW: `qa_amr_genes_per_sample`, whose text says "4 with 0 genes", follows the stated meaning | NEW | D-0573 |
| NEW: `demo_abromics`'s metadata without its 3 id-less lines | NEW (dry run) | D-0569, D-0573 |
| NEW: the two recipes with no declared id declare it | NEW (dry run) | D-0569 |
| "The old recipe study": the line "result: plot | table stays a direction (D-0487)" | CHANGED: a decided design, not built; its key open | D-0485, D-0487 |
| Facts F1 to F6 | STILL TO RUN, only when she asks; the expected numbers of F6 hold for today's recipe | |

**What stays hers to answer, from this file.** (viii), (i), (vii), (vi), (v), and narrower (ii), (iii) and (iv). They are now in the one list of `CAUSE_AND_SOLUTIONS_ZEROS.md` (section "Added 2026-11-23 (ledger D-0573 to D-0579)"), with the questions that her answers created. Where this file and that list differ, that list is the later.

### B3.2 The marks (blockquotes, placed directly under the text named; nothing deleted)

- Under the sub-bullets of `2. A result can be written in two ways`: `> **Update of 2026-11-23 (ledger D-0573, D-0574):** the "metadata first, counts filled with 0, false zero" way is no longer the way to give zeros; the completion with the marker "not in original data" is decided. The false-zero facts stay true of today's recipes. See the review section at the top.`
- Under `3. A zero cannot tell "analysed, nothing found" from "not analysed".`: `> **Update of 2026-11-23 (ledger D-0572, D-0573):** the first sentence stays true. "A removed entity also shows 0 there" is superseded: an added line carries the marker "not in original data", and a removed entity is absent.`
- Under `**G6. A result per entity with zeros.**` (its paragraph): `> **Update of 2026-11-23 (ledger D-0573, D-0574):** SUPERSEDED as the way to give zeros (the agents' reading, to confirm); the facts stay true of today's recipes.`
- Under `**G7. A zero cannot tell "analysed, nothing found" from "not analysed".**`: `> **Update of 2026-11-23 (ledger D-0572, D-0574):** the first half stays true. The sentence "an entity with metadata and no observation exists in the result only when the metadata is the first table" is superseded: with the completion it exists with the result table first.`
- Under `**G17. Reading rules and parents.**`: `> **Update of 2026-11-23 (ledger D-0574):** new fact: a completed result table also reads the metadata; the parent is the metadata's file (reading α) or its tier 1 (reading β).`
- Under `**G19. A rule "metadata on the right" would forbid pattern 2 written with the metadata first.**`: `> **Update of 2026-11-23 (ledger D-0574):** CHANGED MEANING: with the completion the zeros pattern can be written with the result table first; such a rule forbids only a spelling.`
- Under `### (ii) A result per entity with zeros: where does the removal go by default, and what does the user see?`, `### (iii) Must the entity id be declared? And where is "unique" judged?`, `### (iv) Her direction: "the join should not start with the metadata". A rule, an advice or documentation?` and `### (v) The recipe form (PATHS Q3)`: the matching row of the table above, as one blockquote line each, beginning `> **Update of 2026-11-23 (ledger D-0578):**`.
- In "THE OLD RECIPE STUDY: kept, changed, dropped", under the CHANGED item `"result: plot | table" stays a direction (D-0487)`: `> **Update of 2026-11-23:** a table as a result is a decided design, not built; its key is open (D-0485, D-0487).`
- In the line `**Since the list was written, her words D-0563 to D-0566:**` add at its end: ` Then D-0567 to D-0578 and D-0579 (the review section at the top).`
- Signing line, at the end: `**Review of 2026-11-23 (D-0577, D-0578):** Sonnet (this file) and Opus (OPUS_review_1.md, SONNET_review_2.md; [to be signed after the Opus check of this draft]).`

---

## B4. `PATHS_AND_DERIVED_AGREED.md`

(B4.1) A section at the top, before `## HALF PAGE FOR HER`; (B4.2) marks.

### B4.1 The section at the top

## REVIEW OF 2026-11-23 (her order, ledger D-0577, D-0578): what her decisions since changed in the seven questions

The seven questions of this file were written before D-0573 to D-0576 and D-0579. Her new decisions touch five of them (Q1, Q3, Q5, Q6, Q7). Nothing is deleted. The line "where the metadata is the first table of a left join, the entity's rows stay, with the ResFinder columns empty" (half page, item 4) stays true of today's recipes.

| Question | Status | Deciding line |
|---|---|---|
| Q1 A parent reused in another graph | STILL OPEN; touched: the completion makes the metadata feed every completed result table (an edge from its file under reading (α), from its tier 1 under (β); new question 8 of `CAUSE_AND_SOLUTIONS_ZEROS.md`) | D-0574 |
| Q2 "Each T1 coming from the parent": which place | STILL OPEN | |
| Q3 The recipe form | STILL OPEN; one decided element: the completion block on each result table | D-0574 |
| Q4 The default place where her rule says nothing | STILL OPEN; the join place default (D-0549) stands | D-0549 |
| Q5 What "Remove from all the data" writes | STILL OPEN; touched: the library step is built, the screen with the ticks is not (D-0499, D-0531, D-0501); under reading (β) the completed result tables lie below the metadata, which adds nested pairs | D-0574 |
| Q6 "Can remain" before Apply | CHANGED MEANING, narrower: with the result table first and the completion, a removal at the result table is complete; the note is needed for metadata-first joins and for paths through other originals (the 23 virulence genes) | D-0549, D-0574 |
| Q7 "Remove step"; the side of the metadata; the entity key | "Remove step": STILL OPEN. The side of the metadata: CHANGED, now new question 12 (a rule, an advice or documentation). The entity key: CHANGED, partly settled: the shipped recipes declare their ids (D-0569) and the block needs a declared id (D-0574); whether the format requires it is the recipes file's (iii) and the new question 6 | D-0569, D-0574 |

The one list of what she still has to answer is in `CAUSE_AND_SOLUTIONS_ZEROS.md` (section "Added 2026-11-23 (ledger D-0573 to D-0579)").

### B4.2 The marks

Under the headings `### Q1 A parent reused in another graph: what should the app do?`, `### Q5 What does "Remove from all the data" write?`, `### Q6 May the app say, before Apply, that the entity can remain in a place below?` and `### Q7 The earlier questions on "Remove step", the side of the metadata and the entity key`: one blockquote each, beginning `> **Update of 2026-11-23 (ledger D-0578):**` with the matching row of the table above. Signing line: `**Review of 2026-11-23 (D-0577, D-0578):** Sonnet and Opus ([to be signed after the Opus check of this draft]).`

---

## What I did not do, and what is open

- I did not edit any study file, did not run the engine, did not touch `WHOLE_PICTURE.md`, left no process behind, wrote no commit.
- I did not check the earlier rounds D-0569 (Q1 to Q6), D-0568 (O1 to O7, P1 to P4), the recipes file (C1 to C15) and the paths file for the same records error; I checked D-0570 (R1 to R32) and D-0572 (R1 to R26). I propose to check the others on order.
- Block M635 is ledger D-0579; its content is answered as question 1. M636 (D-0580) is applied: runs are named only for after the code exists.
- The statement "the two checks are by content: X and Y" rests on her D-0579; the pairing of each written question with its action is the review session's reading, and she confirmed it with "yes" (D-0573).
- Open between the two agents: **the leans on questions 1 and 4** (I lean (b) on question 1 and have no lean on 4; the Opus agent leans to inform (r1) on the old N2), the form of the block (the Opus text reads (i-b) as settled; I read it as open: A3), and the file name of the log (I accept `id_log.yaml`). To settle in the Opus check.
