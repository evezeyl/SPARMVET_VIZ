Written by Opus for D-0590
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md` as it stands on disk (with the D-0589 text). Each anchor occurs exactly once (fixed-string search). Her words are copied from the channel block M650.

## BLOCK 1. INSERT AFTER the line that begins `   Lean (Sonnet, as a lean): the union: only then are the sets identical in every table`
`   > **ANSWERED by D-0590:** the union ("All should unique ids should be equivalent betwen original data, and metadata"); this is the review session's and the agents' reading of "equivalent", one line to confirm with her.`

## BLOCK 2. INSERT AFTER the line that begins `- **(g) No metadata attached: no completion,**`
`  > **CHANGED by D-0590:** with no metadata attached, the original tables complete each other ("Case 1 no metadata -> completions and reverification of test 3"). The sentence above is kept as history.`

## BLOCK 3. REPLACE `## THE CAUSE, AND WHAT WAS FOUND` BY the lines up to END BLOCK 3:
### Added 2026-11-23 (ledger D-0590): a third check of the id sets, in all cases; the completion with no metadata

**Her words, exact.** "If no metadata added - and I think that actually should be a 3d step done in all the cases (after having filed ids for tests 1 and 2) that the unique ids of each original data are compared to each other (and to the unique ids of metadata when existing) . Case 1 no metadata -> completions and reverification of test 3. Case 2. metadata existed - All should unique ids should be equivalent betwen original data, and metadata (if not I think we have a bug)." [HER WORDS D-0590]

**What her words say (she writes "I think").**
- A third step "in all the cases", after the ids are filled for her tests 1 and 2: the unique ids of each original table are compared with each other, and with the metadata's when there is one.
- No metadata: "completions and reverification of test 3".
- With a metadata: all unique ids "should be equivalent betwen original data, and metadata (if not I think we have a bug)".
- Readings, not her words:
  - the three checks are named by their content (the ids of a result file not in the metadata; the ids of the metadata not in a result file; the id sets compared);
  - a failed third check is a red warning and a line in the log, never a stop (D-0581).

**Points for her, by reading and reasoning.**
- **(a) Which tables take part when there is no metadata:** those that declare an entity id. A reference table with none stays out: the APEC list (`1_test_data_ST22_dummy.yaml:134`) declares none [RECIPE FILE `input_fields/APEC_STEC_virulence_genes_input_fields.yaml`].
  - Two tables whose ids name DIFFERENT kinds of entity would complete each other wrongly: each would gain the other's ids, marked.
  - How the recipe says that its tables describe one population: the optional `entity.population` names one table [CODE READ `libs/utils/src/utils/recipe_spec.yaml:29-30`], or every table that declares the entity id counts. Hers.
- **(b) What a line added from ANOTHER result table means:** the required meaning per table (D-0574, D-0586) covers "not in original data". With no metadata there is no "not in metadata" marker: there is nothing to add it to.
- **(c) "Unique ids"** are read after the declared strip and null words of the read [CODE READ `libs/ingestion/src/ingestion/declared.py:115-120`]: an id repeated within one table counts once; an empty id is no id.
- **(d) The order, once per data batch:** the metadata's own ids (a warning); the two completions; the third check.
- **(e) A failed third check:**
  - a line in the log, words PROVISIONAL: "check of the id sets failed: N ids differ between <tables>", and the red warning where there is a panel; with no panel only the person who reads the log sees it (D-0585);
  - it checks the app's own work ("I think we have a bug"), so when it is built it becomes a test: the expectation is written now and run when the code exists (D-0580).
- **(f)** The "equal id sets" line of the data check (D-0586 sub-section) is the report BEFORE the completion; the third check is the proof AFTER it.
- **(g)** With (A) the third check compares the completed tables as read, before any audit step, so an audit removal never makes it fail. With (B) a removal at one place can make it fail.
- **On the demo (case 2):** after the completion ResFinder holds 38 + 4 = 42 ids, every other table and the metadata 42, so the third check passes [ESTABLISHED: OVERLAP section 1; REASONED].

**What remains hers, one at a time.**
1. **(A) or (B):** the completion reads the files as read, or follows the places. With (A) the third check never fails after an audit step. Lean (Opus, as a lean): (A). [Sonnet lean] Neither: say what you meant.
2. **The population when there is no metadata:** every table that declares an entity id, or the table named by `entity.population`. Lean (Opus, as a lean): the named population when the recipe gives one; with none named, every table that declares the entity id, and the warning says that they are treated as one population. [Sonnet lean] Neither: say what you meant.
3. **Item 2: a line of the metadata with no usable id.** It can be given to no table, and the third check ignores it (it has no id). The options (a), (b), (c) of item 2 stand. Neither: say what you meant.
4. **The rest, by title:** the marker's form and name; the block's form and tables; before or after the recipe's tier-1 steps; the log's directory; where the red warning shows; a dummy id; how "data first" is enforced; a recipe with no metadata block and her view of D-0588; the count per target; the threshold; the two QA tables.

---

## THE CAUSE, AND WHAT WAS FOUND
END BLOCK 3
