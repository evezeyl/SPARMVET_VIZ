# Test Lab step 4: Scientist and data scientist viewpoint

Written 2026-11-21. Planning only. I recommend, I decide nothing. Labels: **ran** (my small runs, scripts in `tmpAI/panel/lab_step4/sci_probe.py`, `sci_probe2.py`, `sci_probe3.py`), **read** (file:line), **reasoned**, **assumed**. Test suite not run.

## Summary (6 lines)

1. Recommend a combination: **A as the base, plus one part of B kept optional and later** (a check of a file against a chosen recipe's declared fields, report only), with D's recipe-making moved out of the Test Lab (BLUEPRINT or scripts). C's repairs are needed under every approach.
2. Reason: what a scientist can defend in a methods section is a transformation that is deterministic, written down (settings, seed, tool version, input and output fingerprint) and reversible or at least declared irreversible. Approach A is the only one whose every tool can be made that. B and D add recipe reading and authoring, where the Test Lab would choose for the user.
3. Synthetic data can test that a recipe runs and that it refuses or flags what was planted. It cannot test that the science is right. The Test Lab must say so on the screen and in the record.
4. Ran: the Test Lab anonymiser "hash" pattern merges two different samples into one id with no message (3 collisions in 200,000 ids; one pair merges two rows). The reconciliation tool matches `ISO-1` to `ISO-10` and `Sample_A12` to `Sample_A21` at certainty 0.9. Both are silent wrong results.
5. The Test Lab synthetic generator writes a different file on every run, and when a seed is given it changes the global numpy and random state of the whole app process (ran).
6. Largest decision first: what a file written by the Test Lab must carry (a record next to every output). It is independent of which approach is chosen.

---

## 1. What I walked: one realistic job, start to export

Job: a scientist has an Excel workbook from a pipeline (one sheet per tool, ids typed `007`, `ISO-12`, some with a trailing space), a metadata file from a lab with ids in lower case and a comma decimal, and wants to share an anonymised version, check a recipe on synthetic data, then analyse in HOME and export.

| Step | Test Lab tool | What a reviewer asks | What I could not know today |
|---|---|---|---|
| 1 | File reformatting | Which sheets, how many rows and columns before and after, which delimiter, were numbers kept as text? | No count is shown, no record is written, the delimiter is by file ending, "no sheet ticked" means all sheets (read-1 `H:979`). An Excel sheet keeps Excel's types, so `007` may arrive as `7` (not run: V5). |
| 2 | ID reconciliation | Which pairs did you accept, on what evidence, what threshold, what happened to the ones you did not accept? | Fuzzy matches are not written as steps and the screen does not say so; the written reason is not enforced; the output file holds no file names, no date, no counts. |
| 3 | Anonymisation | Is the output anonymous, where is the key, can the sharing partner re-identify? | Key and table in one ZIP; hash is unsalted (below); the same sample gets different new ids in two runs. |
| 4 | Synthetic data | Can I make the same file again, what did you plant, what does that prove? | No seed, no settings, no list of planted errors. |
| 5 | HOME and export | Does what I tested equal what I ran? | The Test Lab files and the recipe are unlinked: the record of what was done to the data before HOME is nowhere in the export. |

The export of HOME is the audit end of the chain. Everything that happened before HOME (steps 1 to 4) is outside the audit unless the Test Lab writes a record that the user can attach. That is the core scientific point: a Test Lab transformation that leaves no record is a silent change before the audited part starts.

---

## 2. The awkward cases I ran (all in the main venv, nothing in the repository edited)

| # | Case | Result | Class |
|---|---|---|---|
| R1 | Anonymiser, pattern "hash", two ids `S8597` and `S18230` (sha256 prefix of 8 hex = 32 bits) | Both get `A_9D4AE85D`. The anonymised table has two rows with the same id; the mapping has two originals for one new id. No error, no message. 3 collisions in 200,000 ids (birthday: expected near 65,000 ids for one collision; two ids in a 10,000-row study collide with probability about 1 in 86). | ran |
| R2 | Anonymiser hash, dictionary reversal | An id of a known shape (`ISO-2023-0417`) is recovered by hashing 10,000 candidates: one hit. A hash of an id is not anonymous; it is a pseudonym that anyone who can guess the id format can reverse without the key. | ran |
| R3 | Anonymiser sequential, row order | The same three ids in another order get other new ids (`A` is `ANON_0001` or `ANON_0003`). Anonymising two files one after the other gives different ids for the same sample (the several-file function exists in the library only). | ran |
| R4 | Anonymiser, `S1`, `S1 ` (trailing space), `s1` | Three different anonymised ids for what the lab may consider one sample. No cleaning, no warning. It is consistent (no false merge) but invents samples. | ran |
| R5 | Reconciliation with the default cutoff 70 | `ISO-1` to `ISO-10` (0.9091), `ISO-101` to `ISO-1010` (0.9333), `ISO 7` to `ISO-7B` (0.9091), `Sample_A12` to `Sample_A21` (0.9). Different samples matched with high certainty. `S1` to `s1 ` was not matched at all (no strip). | ran |
| R6 | Reconciliation, a missing id (None) in the list | The tool crashes in the pattern step (`id_patterns.py:39`, `None.lower()`). Zero rows: handled. | ran |
| R7 | Synthetic generator, seed | Same seed gives the same table; no seed gives a different table each time; `generate(seed=...)` changes the global `numpy` state of the process (`AQ:84-86`, ran: state changed). | ran |
| R8 | Synthetic generator: the screen | calls `generate` with no seed (`H:639`, read-1) so the user cannot reproduce. | read |

Meaning for the methods section: a pseudonym by hash of an unsalted id with 8 hex characters is neither safe against guessing (R2) nor safe against collisions (R1). A fuzzy match at 0.9 is a hypothesis, not a join key (R5).

---

## 3. Approach by approach

Notation: **exists** (verified in the review file or my runs), **extend**, **missing**. Sources: `04_what_test_lab_must_be.md` (`04`), `05_three_ideas.md` (`05`), `02`.

### A. A small, safe toolbox for every user

What the user sees and leaves with, per journey:

| Journey | Sees | Leaves with |
|---|---|---|
| J1 Reformat | The file name, the delimiter found and a choice, the sheets, rows and columns before and after, the columns whose type is a risk (looks like a number, leading zeros, comma decimal) | A TSV plus a small record (see section 5) |
| J2 Synthetic | The columns, the seed (shown, editable, default written), the error kinds, a plain warning of what the file can prove | A TSV plus a settings record that regenerates the identical file, plus a list of every planted error (row, column, kind) |
| J3 Ids | Pairs by evidence class: exact, normalised (case, whitespace), pattern, fuzzy; nothing fuzzy goes on without the user | A mapping file with file names, counts, threshold, the user's reason; fuzzy accepted pairs written one by one |
| J4 Anonymise | Which column, which pattern, the consequence of each (see section 6); the ZIP split into "to share" and "keep" | Two separate downloads; record without the key |
| J5 Recipe | Not here (moves to BLUEPRINT or scripts) | - |

What exists: the library functions `generate(seed)`, `save_config`, `load_config`, the anonymiser config record, the reconciliation engine (`AQ:77-129`, `AN:118-139`, read-1). Extend: record for every tool, seed on screen, cleaning, counts. Missing: input fingerprint, tool version in the record, shared id set across several synthetic tables (the demo script does it: `assets/scripts/generate_demo_data.py:16-18`).

Pros:
- Each tool is a transformation with declared inputs, settings and outputs. That is what reproducibility needs. (reasoned)
- The Test Lab no longer reads or writes recipes: no conflict with D-0102, the choice of 2026-11-08, or D-0082 (key declared).
- Safe for scientists, so "for the user" in her words is met. (reasoned)

Cons and pitfalls:
- The "correct format" stays a TSV only. A user can still produce a TSV that HOME refuses. HOME's Data Import already checks against the recipe, so the user learns at HOME (read: `DI:273-315`), which is late but not silent.
- Showing the Test Lab to scientists means each tool must be safe for a non-developer first (unsalted hash, collisions, crashes).

Silent changes and hidden steps: R1, R3, R4, R5, R6, the "no sheet ticked means all sheets", Excel types. All are fixable inside A.

Asks of BLUEPRINT and HOME: nothing but files. The record is a file attached to the output.

Larger decisions needed first: who sees the Test Lab; the record format; the anonymisation policy (section 6).

Can wait: several-file anonymisation on screen; named scenarios.

### B. A file-preparation companion to a chosen recipe

What the user sees: pick a recipe; the Test Lab says which columns the recipe declares, which are in the file, which types differ, which missing words are used; makes synthetic data from the declared fields with planted errors; reconciles ids on the recipe's declared key.

Pros:
- It is the most useful for a user: "will HOME accept this file" before HOME. (reasoned)
- Synthetic data from declared fields is the strongest valid test of a recipe: the test data have the recipe's own types and key, so the test is not a test of the generator's guess. (reasoned)
- The key comes from the recipe (D-0082), not from a column name: it repairs the known defect of the synthesizer and scaffold (F5, `04`).

Cons and pitfalls:
- It reverses the choice of 2026-11-08 (flagged). The Test Lab would read recipes of the deployment: a new coupling with the recipe checker and the recipe places (open study, D-0394).
- A check of a file against a recipe can be mistaken for a pass of the science. It checks shape (names, types), not the content. The screen must say that.
- "Reshape files to match the recipe" is a choice made for the user: renaming columns, converting decimals, trimming ids. Under D-0015 this must be a proposal the user confirms, every change counted. Without that it is a silent change. This is the main risk of B.
- Synthetic data from a declared schema can pass a recipe that fails on real data (see section 4).

Asks of BLUEPRINT and HOME: the recipe has to be available to the Test Lab by file (upload) since user spaces are independent. B in its strongest form conflicts with that unless the recipe is uploaded as a file. Reasoned.

Larger decisions: reverse the 2026-11-08 choice or not; the report-only line (check and report, never rewrite).

Can wait: all of it. It also needs the recipe places study first.

### C. Keep today's tools, fix defects, make hand-offs work

Pros: it is a list of repairs that are needed anyway (see section 7). Smallest change.

Cons:
- Still developer-only: her words say "the user". Not solved.
- It repairs the scaffold into a recipe writer with a first plot: the Test Lab then chooses a plot for the user (a result-shaping choice). Under D-0015 the plot is a draft the user did not ask for (`05` To decide 4, option b con). Not wrong, but it must be labelled.
- Leaves "three recipe writers" (`SC`, `BS`, `recipe_factory`): one way per job is not met.
- Does not on its own give a record for each file (it only "fixes defects").

Silent changes: it fixes the known ones (R1 to R6 are fixes inside C as well). It does not add the record, so the reproducibility gap (F6) remains unless the record is an item of C.

### D. The Test Lab as the recipe starter

Pros: a new user starts a recipe with known fields per tool; format detection helps.

Cons and pitfalls (the scientific ones):
- Format detection by column names is a guess. A file that looks like ResFinder output but is a re-exported or edited file is declared as ResFinder: the recipe then claims a meaning the file does not have. It must be shown as "looks like", with the columns that matched and those that did not, and never silent. (reasoned)
- A tool-specific recipe encodes a version of the tool's output columns. Tools change their output between versions; the recipe must carry the tool version and the check must refuse a mismatch. Otherwise a recipe produced for ResFinder 2.1 is applied to 2.4 output and the figure changes meaning silently. (reasoned, `05` section 3 does not mention versions)
- A pilot recipe cut out of a large one (idea 1, reading 1a) reconstructs a lineage. Cut-out recipes can differ in tier steps from the parent and so give a different row set for the same plot. The cut-out must be checked against the parent on the same data (same rows, same plot values) or the user told. Share-or-copy of fragment files: a shared fragment is a hidden coupling (a change for one recipe changes the result of the other, `05` 2.3).
- Combining recipes (idea 3): the joins, keys and name clashes; the joint designer lives in BLUEPRINT.
- It makes recipe authoring a second place beside BLUEPRINT, against D-0102 and D-0306.

Asks of BLUEPRINT and HOME: BLUEPRINT edits and owns the result.

Larger decisions: where recipe making lives (`05` To decide 2).

Can wait: ideas 1 and 3; idea 2 only as documented templates.

---

## 4. Is synthetic data a valid test of a recipe?

What planted errors prove:
- The recipe or its checker runs on a file of the declared shape (it does not crash).
- The recipe's declared handling of a planted error (missing value word, duplicate id, wrong type, malformed value) does what the recipe says: refuses, flags, or fills as declared.
- Regression: the same synthetic file with the same seed after a change gives the same output (only if the seed and settings are recorded).

What they do not prove:
- That a figure is correct on real data. Real data have correlations, batch effects, structured missingness and ids from several systems that a generator without a model does not have. (reasoned)
- That the recipe handles the real mess. A planted error is the one the author expected. The errors the author did not expect are, by definition, not planted.
- That the shown statistics are right: synthetic values from a column profile have no biology.
- That HOME's Data Import will not refuse the stress file first: today's stress file with type errors may be refused before the recipe runs (`04` J2, reading, V3 not run). Then the test never reaches the recipe.

Pitfalls for validity:
- A generator that infers types from 100 rows and `value_A/B/C` text (read-1 `02` D) writes a test table that has a different distribution of values than the real one: a recipe filter on a real label (for example `ST == "ST22"`) returns zero rows on synthetic data: a "pass" that tests nothing. Zero rows must be reported by the tool (the user must see that the test result is empty).
- Tests with one table at a time cannot test joins: ids must be shared across tables (D-0205 "the same set of ids are used across all the datasets of the recipes", her words, read in `04` J2).
- The sample id must be a string (D-0225): today the synthesizer writes ids by name guess (`AQ:20-28`).
- Reproducibility: seed recorded; generator version recorded; the file equals the regenerated file (checksum). Today: neither seed nor settings (ran R7, R8), and a seed changes the process-wide numpy state (ran) which would change other random draws in the app, a silent coupling. A local generator (`np.random.default_rng(seed)`) would not. (reasoned fix)

What the screen must say at the moment of the choice (plain words): "This file tests that your recipe runs and handles the errors listed. It does not test that the result is right for your real data."

---

## 5. What every file the Test Lab writes must carry (the larger decision)

A small record file written next to every output (text, plain key: value, one per output; the same shape for all tools):

| Field | Why a reviewer asks |
|---|---|
| tool, tool version, app version, date and time | what produced it |
| the input file name as the user gave it (not the upload number) and a content hash of the input | "which file was this" (today the upload number likely replaces the name, `04` J4, reasoned, V6) |
| every setting, including defaults actually used (delimiter, sheets, pattern, prefix, threshold, error rates, rows) | same data and settings give the same file |
| the seed, if anything random | D-0004, D-0056 reading |
| counts before and after (rows, columns, ids, matches by kind, merged, dropped) | a reviewer asks "how many" |
| what was changed that the user did not ask for (renamed key column, ids stripped, sheets defaulted) | no silent change (D-0050) |
| a content hash of the output | detect a later edit |
| for synthetic data: list of planted errors (row, column, kind) | to say what the test covers |
| for reconciliation: each pair, kind, certainty, user decision, user reason | the audit of a match |

Note: the key of an anonymisation never goes in this record (section 6). I verified none of this exists today except the anonymiser's settings record (read `AN:118-139`).

---

## 6. Anonymisation (my own weight)

| Question | Answer | Class |
|---|---|---|
| Is a hash of an id anonymous? | No. For ids of a known shape it is reversible by guessing (R2). It is a pseudonym. Also 8 hex characters collide (R1). | ran |
| Where does the key live? | Today in the same ZIP as the anonymised table (read-1 `H:716-718`). ADR-097 point 8 says anonymise before data reach the app, key kept outside. A ZIP with both is one file to lose. | read-1 |
| The way back | Function exists, writes the old step name `join`, not called (read-1 `AN:228-246`). So the claim "reversible" in the docs is not currently true from the screen. | read-1 |
| Does anonymising change a result? | Yes if the id is a key of a join and only one file is anonymised, or two files with sequential ids (R3), or the id is renamed `anon_<column>` (read-1 `AN:119`): the recipe's declared key no longer exists. | ran, read-1 |
| Do personal columns suffice? | The tool strips ticked columns. Quasi-identifiers (dates, places, rare values) are not detected. "Anonymised" is a claim the tool cannot make. It can say "ids replaced and these columns removed". | reasoned |

What a user can defend: "ids replaced by random labels, mapping kept separately, columns X removed". They cannot defend "anonymised" for hashes. Random labels with a stored mapping are the defensible form. A salted hash with the salt kept like a key is also a pseudonym.

What I would tell the user at the choice: sequential is order dependent (same data in another order gives other ids), hash is guessable and may collide, custom depends on your format string and can give the same id to all rows if the string has no placeholder (reasoned: `_make_custom_id` returns `fmt.format(i)`; a format with no `{}` returns a constant. Not run). The tool must refuse a mapping where two originals get one new id (R1) and say so.

The key in the same ZIP: tell the user in plain words that this download contains the key and must not be shared with the table.

---

## 7. Id reconciliation on messy ids (my own weight)

- False matches (R5): `token_set_ratio` with subset tokens gives high scores to ids that differ by one character in a number. In a bacterial isolate list, `ISO-1` and `ISO-10` are different isolates. A cutoff of 70 (default, `core.py:28`) is far too low to be offered as a default; the score is not a probability.
- The cleaning step acts on the whole column and breaks ids that matched (ran in step 1, case C); a clean step must be tested on the ids that already matched before it is offered (a "no loss" check: all exact matches before still match after). This is the property the strict xfail tests record.
- Order matters: exact, then pattern (best single pattern for all unmatched), then fuzzy. The best pattern is applied to every unmatched id even if it is right for a third of them (read `core.py:56-66`): the pattern is a global choice that may be wrong for some ids. Show how many ids each pattern matches and how many would be changed.
- Many-to-one: two ids of one file match one target (`detect_many_to_many` exists, `core.py:209`; whether the screen shows it is not verified).
- Whitespace and case: `S1` does not match `s1 ` (R5): normalisation is not offered as a step with a count.
- Missing ids: a crash (R6), against D-0050.
- Fuzzy matches are not written as steps and the screen does not say so (read-1): the user believes they are in the file.
- Every accepted pair needs a person's decision and reason for anything below exact. The design asks for it (`TEST_LAB.md:151-162`, document), not built.

Rule for a user: exact and normalised matches can go as a rule; anything fuzzy is a list of pairs a person confirms, each written to the record.

---

## 8. Type inference from a sample (my own weight)

- A sample of 100 rows (read-1) cannot see the rare values: a numeric column with `NA` on row 400 is typed numeric; a column that is all digits in the first 100 rows but has `ISO-12` later is typed number.
- Ids that look like numbers become `Int64` in the scaffold (ran, step 1 cases A, B): against D-0225. Leading zeros are lost (`007` becomes `7`) and cannot be recovered. This is also true for Excel number cells (reasoned; V5 not run).
- Dates: no date type in the generator; dates written as text are fine if the recipe says so.
- Decimal comma: `3,5` read as text in a comma-delimited file with comma separator, or split into two columns in a comma-delimited file (reasoned). The reformatter reads all columns as text for delimited files (read-1), which is safe; a type must be a user choice later.
- A principle that avoids all of these: the Test Lab proposes a type with the evidence (how many rows read, how many matched, the first exceptions) and the user confirms; an id column is text by default and can never be proposed as a number.

---

## 9. Where the three recipe ideas belong (from my viewpoint)

| Idea | Scientific risk | Where I would put it |
|---|---|---|
| 2 Tool-specific | Tool version drift; a recipe claiming a meaning a file does not have. | A documented template or script now; not a Test Lab screen. Needs a decision on versions (to decide). |
| 1 Pilot extraction | A cut-out that gives other rows than the parent; share-or-copy of fragments. | BLUEPRINT (it owns lineage and branch). Not Test Lab. Check "cut-out equals parent on the same data" before it is offered. |
| 3 Combine | Joins, keys, names; the entity key. | BLUEPRINT only. The Test Lab at most reports what recipes share (report only). |

I give no ranking of wanted/not wanted: that is hers.

---

## 10. What would change a result silently or hide a step: flagged first

1. Anonymiser (hash): two samples receive one id (R1). Ran.
2. ID reconciliation: near-identical different ids matched at 0.9 (R5); a column-wide cleaning step that breaks matched ids; fuzzy matches left out without a message. Ran and read-1.
3. Synthetic generator: a seed that sets global state (R7); no seed shown or recorded (R8); a stress file that is refused before the recipe is tested (reading).
4. Reformatter: Excel types kept (`007`), "no sheet" means all, no counts. Read-1, not run.
5. Anonymiser: renamed key column, key and table in one ZIP, unsalted hash.
6. Approach B's "reshape to fit" and approach D's "format detection" would add new silent changes unless every change is a proposal with a count that the user confirms.
7. Approach C's scaffold with a first plot or an inner join: the Test Lab chooses a plot and drops rows with no partner.

---

## 11. Recommendation

**Combination: A as the base, with B's check-only part later, D moved out.**

Why, from my viewpoint:
- A is the only approach where every tool is a transformation I can describe in one methods sentence with its record, and where nothing reads or authors a recipe. That keeps D-0102, D-0082, D-0050, D-0015 and ADR-097 point 8 intact.
- The record (section 5) is what turns "a set of utilities" into "utilities a user can defend". It is cheap and applies to every approach.
- B's strongest value, "will HOME accept this file", can be offered as a report only (names, types, missing words compared with a chosen recipe's declared fields, with counts), never as a rewrite. That is informing, not choosing. It still reverses the 2026-11-08 choice and depends on the recipe places study, so it comes after A and only if the owner accepts the reversal.
- C's repairs are contained in A (they are the same list), except the scaffold writing a first plot, which I would not make the Test Lab do (recipe making).
- D mixes recipe authoring and file preparation: two jobs of different risk in one place, and BLUEPRINT is the place for edits (D-0102).

What I would not support: any rewrite of a user file without a count and a confirmation; any "anonymised" label without the key outside and the quasi-identifier warning; fuzzy matches treated as a rule.

---

## To decide first (ranked)

1. What every Test Lab output must carry (the record, section 5), and whether a "make it again" upload exists. It decides reproducibility for all approaches.
2. Whether the Test Lab reads a recipe at all (reverses 2026-11-08): none, report-only, or reshape with confirmation.
3. The anonymisation policy: which patterns exist (remove the unsalted 8-hex hash or replace by a random label), where the key goes (ADR-097 point 8), whether the tool refuses a mapping that merges two ids (R1).
4. The reconciliation policy: which match kinds may become a rule (exact, normalised) and which need each pair confirmed (fuzzy); the cutoff default.
5. Who sees the Test Lab (all tools, safe tools only, scripts).
6. Where recipe making lives (BLUEPRINT, scripts) and the three ideas.
7. A seed policy for synthetic data (a local generator, the seed shown and written) and what the screen says that planted errors prove.

## Not verified

- Nothing seen in a browser. All statements about the screen are from code (read-1 from step 1).
- Real Excel conversion (`007` as number), decimal comma, HOME Data Import's behaviour on stress files and on `anon_` columns (V2 to V5).
- A custom pattern without a placeholder giving one id for all rows (reasoned from `_make_custom_id`, not run).
- Whether the screen shows many-to-one matches.
- Collision probability numbers are from a birthday approximation and one 200,000-id run; the 1 in 86 for 10,000 ids is computed, not simulated.
- I did not read `ADR-084`, `ADR-097` or the ledger lines directly; I used the quotations in `04` and the brief. I did not run the test suite.
