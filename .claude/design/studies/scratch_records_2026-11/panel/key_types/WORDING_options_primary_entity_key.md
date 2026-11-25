# Wording options: "primary key", "entity key", "join key", and `sample_id` as the example

Date: 2026-11-18. Status: options for Eve. Nothing was rewritten and nothing is decided. Request: M271 task 5 (Eve: "docs we need to rework to make data agnostic with sample_id as example - for primary key a bit unsure"). Items 6a and 6d of the earlier wording questions stay HELD.
Labels: VERIFIED (file:line, or the count script `tmpAI/panel/key_types/count_words.py`, which I ran), REASONED (my inference).
Terms: a **key** is a column that matches rows of two tables. A **recipe** is the YAML file that says how data becomes plots. The **checker** is `libs/utils/src/utils/recipe_check.py`.
Counting method: all text files of `app`, `docs`, `libs`, `config`, `assets`, `.claude/rules`, `CLAUDE.md`, without `docs/_site` (generated), `build`, `.venv`, tests and worktrees. A count is a number of matches, not of lines.

## 0. The short answer

1. The app uses **three different things under two words.** (a) The column the recipe author declares as "the one that identifies a row" (`is_entity_key`). (b) The columns that the join steps use to match tables. (c) For the audit, "primary key" means (b), not (a). The docs say "primary key" for (c) and for (a). That is the confusion. (VERIFIED, section 2.)
2. The word "primary key" is mostly spoken to the **user in the app and the user guide** (audit screens, `audit_pipeline.qmd`). The word "entity key" lives in the **recipe and checker** (the recipe author and the developer). "Join key" lives in the **developer code and the join messages**.
3. `sample_id` is used as THE key in a few places that decide behaviour (the Test Lab default, a name list that marks the key, the checker message E03) and as an example in most of the docs (section 1).
4. Four options are given (section 3). My recommendation (section 4): **keep `is_entity_key` in the recipe, say "key column" to the user, say "join column" where a join is meant, and drop "primary key" from the user texts**. It costs no recipe change and no migration.

## 1. Where each word is used today

Counts from the script (VERIFIED, run). Reader: **U** = user of the app, **R** = recipe author, **D** = developer, **A** = agent (rule files).

| Word | Where | Count | Reader | Two examples |
|---|---|---|---|---|
| "primary key" (also "primary-key", `primary_key`) | docs (user guide, appendix) | 29 in 8 files | U, R | `docs/user_guide/audit_pipeline.qmd:121` "A **primary key** is a column that links your tables together. In a typical SPARMVET project the primary key is `sample_id`"; `docs/appendix/test_lab_rationale.qmd:35` |
| | app code (screens, notices, comments) | 32 in 6 files | U (some), D | `app/handlers/audit_stack.py:447` the banner "Primary key - Primary ID/Key alignment"; `app/src/help/test_lab.md:9` "primary-key candidate hints" |
| | libs, scripts, READMEs | 21 + 12 + 6 | D, R | `libs/ingestion/src/ingestion/excel_handler.py:16`; `assets/scripts/create_data_analysis_recipe.py:17` (option `--primary_key_data`) |
| | agent rules | 21 in 2 files | A | `.claude/rules/ui_implementation_contract.md:275, 657`; `.claude/rules/rules_data_analysis_recipe_structure.md:214` ("Primary key rule") |
| | old key left in a shipped file | 1 | R | `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml:5` still writes `is_primary_key: true` (VERIFIED; the checker refuses that old key; whether this file is used by a recipe: I found no `!include` of it, REASONED orphan) |
| "entity key" (also `entity_key`, `is_entity_key`) | recipes and templates | 25 in 21 files | R | `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:5`; `templates/e_coli.yaml` |
| | checker | 11 in 1 file | R | `recipe_check.py:262` message E02 "has no field with is_entity_key: true"; `:364-379` rule E03 |
| | docs | 8 in 4 files | R | `docs/appendix/Standards_yaml.qmd:48`; `docs/foundations/data_contracts_adr.qmd:139` |
| | libs code, scripts | 23 + 4 | D | `libs/utils/src/utils/recipe_factory.py:79`; `assets/scripts/create_data_analysis_recipe.py:122` |
| | app | 1 | U (Blueprint field card) | `app/modules/wrangle_studio.py:1327` (shows a key marker) |
| | agent rules | 1 | A | `rules_data_analysis_recipe_structure.md:214` |
| `is_entity_key` only | all of the above | 55 total | R, D | (a subset of the "entity key" line) |
| "join key" | docs | 28 in 14 files | U, R | `docs/appendix/Terminology.qmd:12` (the "Record ID" paragraph); `docs/appendix/data_analysis_recipe_structure.yaml:23` |
| | app code | 26 in 7 files | U (notices), D | `app/handlers/filter_and_audit_handlers.py:744` "Cannot drop join key column(s)"; `test_lab_handlers.py:339` the box "Join key column" |
| | checker and join rules | 25 + 6 | R, D | `recipe_check.py:43-52`; `libs/utils/src/utils/join_keys.py` |
| | libs code | 53 in 7 files | D | `libs/transformer/src/transformer/data_assembler.py` (19); `libs/blueprint_arch/src/blueprint_arch/join_designer.py` (17) |
| | agent rules | 19 in 5 files | A | `rules_agent_role_bioscientist.md` (8); `ui_implementation_contract.md` (8) |
| "sample id"/`sample_id` (all uses, example or not) | recipes and configs | 176 in 64 files | R | the shipped recipes' columns (it is the data, not a wording choice) |
| | docs | 89 in 21 files | U, R | `docs/appendix/Standards_yaml.qmd` (15), `docs/foundations/data_contracts_adr.qmd` (12) |
| | agent rules | 21 in 4 files | A | `rules_test_lab.md:14`; `rules_data_analysis_recipe_structure.md:214` |
| | app code | 6 in 2 files | U, D | `test_lab_handlers.py:340, 422, 424`; `session_manager.py:124` |
| | libs code | 16 in 5 files | D | `scaffolder.py:156`, `bootstrapper.py:122`; `aqua_synthesizer.py:20-21` |

### 1.1 Where `sample_id` is treated as THE key, not as an example (VERIFIED, read)

These are the places where the word is not an example but a rule or a default. I read each one; I did not read all 89 doc matches.

| File:line | What it does | Reader |
|---|---|---|
| `app/handlers/test_lab_handlers.py:340, 422, 424` | The box "Join key column" starts as `sample_id` and falls back to it silently | U |
| `libs/test_lab/src/test_lab/scaffolder.py:156`, `bootstrapper.py:122` | A column named `id`, `sample_id` or `isolate_id` is marked `is_entity_key: true`; no other column is | R (the recipe it writes) |
| `libs/test_lab/src/test_lab/aqua_synthesizer.py:20-28` | A column is a key when its name ends in `_id`, `_pk`, ... or is `id`, `key`, `sample`, ... | U (synthetic data) |
| `libs/utils/src/utils/recipe_check.py:364, 375` | E03 says "The sample id ... is declared Int64, a number. A number as an id loses leading zeros" | R |
| `.claude/rules/rules_data_analysis_recipe_structure.md:214` | "Primary key rule: the sample id is a string or a categorical, never a number" | A |
| `docs/user_guide/audit_pipeline.qmd:121` | "In a typical SPARMVET project the primary key is `sample_id`" | U |
| `app/src/help/test_lab.md:9` | "primary-key candidate hints" | U |

The rule text has an existing counterweight: `docs/appendix/Terminology.qmd:12` says the "Record ID" is "not necessarily `sample_id`, and not necessarily unique within one dataset" (VERIFIED). So the docs already carry a data-agnostic definition, in the glossary, under a **fourth** word: "Record ID".

## 2. What each word means in the code today

1. **`is_entity_key: true`** (the recipe field flag; `libs/utils/src/utils/recipe_spec.yaml`, `recipe_check.py`). The author marks the column that identifies one row of that table (for a table of samples: the sample column). What reads it (VERIFIED by grep of `app`, `libs`):
   - E02: if the recipe has an `entity:` block, the table named as its `population` must have such a column (`recipe_check.py:259-262`).
   - E03: a marked column must not be a number type (`:364-379`; D-0067, D-0225).
   - FD05: the value must be true or false (`:425-426`).
   - Blueprint's field card shows a key marker (`wrangle_studio.py:1327`).
   - The engine and the audit do **not** read it. The docs say so: "`is_entity_key: true` is informational ... Join keys are always written in the `joins` step list" (`data_contracts_adr.qmd:139`; `Standards_yaml.qmd:48`).
   - A Date or true/false key is **not** refused today (the dates report, section 2, VERIFIED by run).
2. **A join key** (the `on`, `left_on`, `right_on` of a join step). The columns the author wrote to match two tables. Checked for equal types (`utils/join_keys.py`, one rule for build, Blueprint and checker; D-0044). Not necessarily unique; a long table repeats it (D-0223: `sample_id` repeated for each gene found).
3. **What the audit protects, called "primary key"** (`app/modules/session_manager.py:119-146`, `extract_primary_keys`): every column used as `on`, `left_on` or `right_on` in any join step, name only, no type. It is shown to the user as "Primary key" (`audit_stack.py:447`) and, in the drop notice, as "join key" (`filter_and_audit_handlers.py:744`). So on one screen, one thing has two names. It does not read `is_entity_key` (VERIFIED by reading the function: only the three step names; the dates report also notes that it ignores `by` of an as-of join).
4. **"Primary key" in the database sense** (a column that is unique and not empty). The app does **not** check uniqueness or non-emptiness of any key, in a recipe or at load. (VERIFIED by reading the checker rules named above: none tests uniqueness; the `Candidate PK` hint in the Test Lab says "100% unique" from the first 100 rows only, `scaffolder.py:166-172`.) So the word promises a guarantee the app does not give.
5. **"Record ID"** (`Terminology.qmd:12`): the glossary word for "whichever column (or combination) the join actually matches on". It is the join key of point 2 under another name.

Plain summary for Eve: the recipe flag says "this column names the thing in each row". The join step says "match on these columns". The audit protects the second list and calls it "primary key". The two lists often overlap (both contain `sample_id`) but are not the same, and the app never checks that they agree. The dates report (section 5.1) proposes one function that reads both.

## 3. Wording options

All options keep the recipe working. Each is described: one sentence as the user reads it in the app and one in the docs; the cost; the risk of confusion with database words; whether it stays true when the key is a date or a pair of columns. Cost counts come from section 1 (VERIFIED counts; "to change" is my estimate of what would be touched, REASONED).

### Option A: one plain word, "key column", everywhere; qualifiers say which kind

- Rules: "key column" for the declared one ("the key column of this table"); "join column" for the columns of a join step; "primary key" and "entity key" are dropped from every text a person reads. The recipe flag stays `is_entity_key`.
- In the app (audit card): "Key column: this decision changes which samples reach the joined plots." Drop notice: "The column `sample_id` is used to join your tables, so it cannot be dropped. Use a row filter instead."
- In the docs: "A **key column** identifies one row of a table, for example a sample (`sample_id`) or a day (`date`). A **join column** is a column that two tables are matched on."
- Cost: the user-facing texts only: `audit_pipeline.qmd` (18), the audit banner (`audit_stack.py:447`), Test Lab texts and help (`test_lab_handlers.py:339`, `help/test_lab.md:9`), E03 and E02 messages (`recipe_check.py:262, 375`), the Standards and data contract pages (about 12 matches). Recipe: no change, no migration. Developer code keeps `primary_keys`/`extract_primary_keys` names or renames them in a later cleanup (not needed).
- Confusion with databases: low. "Key column" is neutral. No uniqueness is promised.
- Date key: stays true ("the key column is `date`"). Pair of columns: "the key columns are `sample_id` and `gene_id`" works; the singular "column" needs a "(or columns)" note once.

### Option B: "entity key" for the declared one, "join key" for the join, drop "primary key"

- Rules: `is_entity_key` stays and its words are used in the text: "entity key" = the column that identifies the thing a row is about; "join key" = the matching columns. "Primary key" is removed from user texts.
- In the app: "Entity key: ..." in the field card; audit banner: "Join key: this decision changes which samples reach the joined plots." Drop notice stays "join key".
- In the docs: "An **entity key** identifies one row (for example a sample). A **join key** is a column two tables are matched on. They are often the same column, but not always."
- Cost: the same texts as option A, with different words; "entity" appears more in user texts (today it is nearly absent there: 1 match in app code, 8 in docs). Recipe: no change.
- Confusion with databases: low for "join key". "Entity" is a data-modelling word and unfamiliar to a bioscientist; Eve is unsure of it. In a recipe the `entity:` block (`noun`, `plural`, `population`) already uses the word for "what a row is about", so it is consistent inside the recipe (VERIFIED, `recipe_spec.yaml:16-18`).
- Date key: stays true ("the entity key is the collection date" reads strangely: a date identifies a row, but is not an "entity"). Pair: fine.

### Option C: keep "primary key" for the user, define it once and say what it is not

- Rules: keep the word in the audit screens and the user guide; keep "entity key" in recipes. Add one definition to the glossary: "primary key (in the audit) = a column used to join tables; it is not checked to be unique."
- In the app: unchanged ("Primary key - Primary ID/Key alignment" becomes "Primary key (a column your tables are joined on)").
- In the docs: a definition box in `audit_pipeline.qmd` and `Terminology.qmd`.
- Cost: lowest (2 or 3 files). Recipe: none.
- Confusion with databases: **highest.** In SQL a primary key is unique and not empty, and a long table (`sample_id` repeated per gene, D-0223) has no primary key in that sense. Data scientists will read the word as a promise the app does not keep (section 2, point 4). Eve is unsure of the word, and the two-name situation on one screen stays.
- Date key: "the primary key is the date" is odd; pair: "composite primary key" is a database term the users do not need.

### Option D: rename the recipe flag too (`is_entity_key` becomes `is_key` or `key: true`), with option A's words

- Rules: as option A in the texts, and the recipe key becomes simpler and data agnostic.
- Cost: **a recipe-format change and a migration.** 55 matches in 21 recipe/template files, the checker (8), the factory, the migration tools, the Test Lab writers, the schema `recipe_spec.yaml`, the docs (7), tests (not counted), plus the format change that is being built now (ENGINE_KEYS: tier keys, `ui_label`). It would have to join that migration or follow it (D-0034 decided the name `is_entity_key` on 2026-11-13).
- Confusion with databases: low. Date key and pair: fine. A bare `key:` could be mixed up with the YAML word "key" (REASONED).
- Not recommended now: the gain over option A is only the recipe word, which only recipe authors read; the cost is a second migration of every recipe. If Eve wants it, do it inside the format change that is already running, not after.

## 4. Recommendation (mine, not a decision)

**Option A, with the recipe flag unchanged.** Reasons:
1. The user texts are where the confusion is (section 2, point 3: "Primary key" and "join key" on one screen for one thing). Option A removes both database-flavoured words from what a bioscientist reads, and needs no recipe change.
2. It is data agnostic by construction: "key column" is true for a sample, a day, a pair, a plate. `sample_id` stays as an example, written "for example `sample_id`", never as the rule.
3. It keeps `is_entity_key` (D-0034, 55 matches), so it does not touch the migration that is running (ENGINE_KEYS).
4. It tells the truth about uniqueness: the app does not check it, and "key column" does not promise it. If Eve later wants the check (a rule that a declared key column has no repeats where the table is one-row-per-entity), that is a separate decision.

Two things that go with it, because they are not wording (each "needs a decision"):
- The default `sample_id` and the name lists in the Test Lab (section 1.1) are behaviour, not wording; they are in the Test Lab review (`.claude/design/exploration/2026-11-18_test_lab_review.md`, items 4 and 5).
- The audit's "primary key" list and the recipe's `is_entity_key` should be one source (the dates report, section 5.1, K2). If K2 is chosen, the words in option A are exactly right: "key column" for both.

## 5. What a wording pass would touch (for an estimate, not started)

Files with the most matches, user-facing first (VERIFIED counts): `docs/user_guide/audit_pipeline.qmd` (18 "primary key"), `docs/appendix/Standards_yaml.qmd` (15 "sample id", 2 entity), `docs/foundations/data_contracts_adr.qmd` (12 "sample id", 4 entity), `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd` (10 "sample id"), `app/handlers/filter_and_audit_handlers.py` (15 "primary key", mostly code and comments), `app/handlers/audit_stack.py:447`, `app/handlers/test_lab_handlers.py` (8 "join key"), `app/src/help/test_lab.md`, `recipe_check.py` E02/E03 messages, the rule files `ui_implementation_contract.md` (20) and `rules_data_analysis_recipe_structure.md:214`. Code comments and variable names (`primary_keys`, `primary_key_warning`, 7 + 15 matches) do not need to change for option A. Estimate: about 25 files, [sonnet/medium], after the ENGINE_KEYS merge to avoid conflicts (REASONED).

## 6. What I could not verify

- I did not read all 89 docs matches of "sample id", so the list in 1.1 is the places that decide behaviour, plus the user guide; other doc pages may treat it as THE key.
- Whether the old `is_primary_key` file (`PlasmidFinder_wrangling.yaml`) is used by any recipe: no `!include` found by grep in `config`, not run through the checker.
- How the audit banner and notice look on screen (strings read from code only, the app was not started).
- Whether any recipe in `docs/_site` or outside the folders counted uses the words (generated pages excluded on purpose).
