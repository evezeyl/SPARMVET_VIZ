# The verification findings, placed in time (VERIF-TWO-PERIODS-1)

Written 2026-11-16 from the eight check files and `SUMMARY_for_eve.md`. Branch `feat/recipe-format-1`, HEAD `7632f963`. Read-only work: no tracked file changed, no test run. The findings are the ones of the check files; I did not judge them again and added none.
All times are local (`git log --date=iso-local`; in November +01:00, April and May +02:00). The time of a commit is its author time.

The groups, as asked:
- B: 2026-11-09 00:00 to 2026-11-14 12:03 (before the first Fable message).
- A-before: 2026-11-14 12:03 to 14:49 (Fable works here, the coordinator session has not started).
- A-after: after 2026-11-14 14:49 (the Fable coordinator session runs).
- Older than the range: the line that causes the finding was written before 2026-11-09.
- Date not found.

## 1. The five counts

- A-after (after the coordinator started, 14:49 on 11-14): 14 findings.
- A-before (Fable works, no coordinator yet, 12:03 to 14:49 on 11-14): 6 findings.
- B (11-09 to 11-14 12:03): 30 findings.
- Older than the range (code from April to 11-06): 14 findings.
- Date not found: 1 finding (a feature that was never built, so no commit introduced it).

Total 65. How I counted:
- Each of the 14 places that swallow an error in the session, import and export paths (E1) counts once, with its own commit. E2 and E3 are the same lines as E1 places 4, 8 and 9, so they count once, under E2 and E3.
- Each of the 15 rule-file commits "with nothing on record" counts once. RC (the contradiction in CLAUDE.md) and one of the 15 come from the same commit `55e578f5`; they count as two findings.
- Five of the 65 are minor test items (T3, T4, T5, T6, T7; see the tables). They are in the counts and marked "minor".
- Not in the counts: seven more rule-file commits where the decision is on record but her yes to the text is not (section 2f); the open doors of the guard hook (they are not changes); things that held.

Commits in each period, for scale only (all commits at HEAD, merges included): B 235, A-before 40, A-after 439. The checks were chosen by area, not by time, so these are not error rates.

Kinds: D = the code does less or other than a decision says; N = a change with no decision found; S = a silent or swallowed error (the user is told nothing); R = a rule, agent or hook file, or a written record; T = a lost test or a test mark. Model = the "Co-Authored-By" line of the commit (S5.5 = Sonnet 5.5, S5 = Sonnet 5, S4.6 = Sonnet 4.6, F5.2 = Fable 5.2, H5.5 = Haiku 5.5, "-" = no line). That line names the session that committed; it does not prove who wrote the code.

## 2. The tables

### 2a. A-after: after 2026-11-14 14:49 (14 findings)

| What the user or the recipe author sees | Code name | Kind | Commit | Date and time | Model | Described in |
|---|---|---|---|---|---|---|
| A table joined to itself with an "anti" join gives 0 rows and no message. Her decision of 11-15 says it must be an error. The code is older than the decision; nothing was built after it. | J1 | D | `b27f89e4` feat(transformer): run a first join step whose right table is the base table, and advise on a self-join (J12); `38fa288e` fix(checker): make advice J12 true for every self-join | 2026-11-14 19:40:31; 19:59:58 | F5.2; F5.2 | check_3_joins.md, Entry 15b |
| A decimal join key gets its advice only when the key is declared decimal, not when a recipe step makes it decimal; keys such as 0.1+0.2 and 0.3 then silently do not match. No decision is broken (a gap). | J4 (no name in the summary) | S | `b27f89e4` (same as J1) | 2026-11-14 19:40:31 | F5.2 | check_3_joins.md, behaviour (b) |
| The Blueprint join preview shows a false sentence ("lists differ in length: 0 and 0") when the key list is empty. | J5 (no name in the summary) | S | `d58ae1e4` refactor(join): one join-key rule in libs/utils for the build, the preview and the checker | 2026-11-15 15:21:27 | S5.5 | check_3_joins.md, behaviour (f) |
| A sample with one phenotype and one missing phenotype counted as multi-resistant; it does not now. No decision of hers was found. No shipped number moves (16 of 38 samples). | M1 (the "multi-resistance formula") | N | `7f4ea21a` fix(recipes): a missing phenotype no longer counts as a phenotype in the multi-resistance flag | 2026-11-16 02:01:51 | S5.5 | check_2_engine.md, Entry 12 (12c); check_5_baseline.md, section E |
| A seed written as `null` is now refused and a new recipe-wide seed key exists. Both were built as "provisional" with no answer of hers; the plot rule file and an ADR still say the opposite. | R5 | N, R | `54e6979f` feat(seed): random_state null and random are refused; `6f9479e0` feat(seed): plot_defaults.random_state is the one seed of the whole recipe | 2026-11-15 13:38:33; 13:41:01 | S5.5; S5.5 | check_8_rest.md, Entry 27; check_6_7_rules_tests.md, A2 point 3 |
| In HOME an error while reading the click of the "remove pinned seed" button is ignored; the click does nothing. Harmless by reading. | SP2 (one of the "four more silent places") | S | `39ed8983` feat(home): the seed in use is shown with the plot; Reshuffle follows the resolver's precedence; a way back from a pin | 2026-11-15 18:54:44 | S5.5 | check_8_rest.md, finding F4 |
| CLAUDE.md says in two lines that the coordinator may do "a one-line fix" and in a third that it never edits a file. The hook enforces "never". | RC (contradiction in the rules) | R | `55e578f5` chore(agents): standing rules of the coordinator, and the guard refuses Bash that writes files (the two older lines come from `547c6a78` 11-14 13:54 and `6e318386` 11-14 14:33) | 2026-11-14 23:48:46 | H5.5 | check_6_7_rules_tests.md, A2 point 2 |
| Rule-file change with nothing on record: the decision-compliance files mark which parts are the builder's text, not hers. | RF (one of the 15) | R | `f1f70353` docs(agents): mark what is not Eve's text in the decision-compliance files | 2026-11-16 08:45:00 | S5.5 | check_6_7_rules_tests.md, A1 table and "For Eve" item 9 |
| Rule-file change with nothing on record: the hook now requires a "NONE-CHECKED" path to be a regular file inside the project (stricter than her D-0125). | RF | R | `ee4f1eac` fix(hooks): a NONE-CHECKED path is a regular file inside the project, leading dots kept | 2026-11-16 08:39:30 | S5.5 | same, A1 and "For Eve" item 9 |
| Rule-file change with nothing on record: dead document paths pointed at files that exist (a fact fix). | RF | R | `fdb7df0f` docs: point the document references at the files that exist today | 2026-11-15 19:49:28 | S5.5 | same, A1 |
| Rule-file change with nothing on record: the coordinator's standing rules and the hook that refuses Bash that writes files. | RF | R | `55e578f5` (same commit as RC) | 2026-11-14 23:48:46 | H5.5 | same, A1 and "For Eve" item 1 |
| A fix of the filter dialog (it reads a guarded copy of the audit steps) has no test that fails if the fix is removed. Minor. | T7 | T | `173faf20` fix(audit): the filter dialog reads the plot's audit steps through a guarded mirror, not home_state | 2026-11-15 21:31:36 | S5.5 | check_6_7_rules_tests.md, B4 |
| One test mark that is meant to hold a known plot defect (guide label) is never applied; it protects nothing. Minor. | T3 (dead mark) | T | `9caab17a` feat(viz_factory): five silent paths fail and every plot error has one form | 2026-11-15 08:34:17 | S5.5 | check_6_7_rules_tests.md, B3 table |
| A known Blueprint defect (the data preview applies a component's steps to HOME's data) is held by an "expected to fail" test with no task. Minor. | T5 | T | `0406d2ef` fix(gate): HOME's selector follows the load gate, the export of an unavailable recipe is refused plainly | 2026-11-15 15:03:44 | S5.5 | check_6_7_rules_tests.md, B3 table |

### 2b. A-before: 2026-11-14 12:03 to 14:49 (6 findings)

| What the user or the recipe author sees | Code name | Kind | Commit | Date and time | Model | Described in |
|---|---|---|---|---|---|---|
| Three tools that write recipes (gallery submission, gallery converter, recipe creator) check what they wrote without the lists of actions and plot components. A partial check passes without a word. | F2 | D | `7f052638` feat(scripts): create_data_analysis_recipe writes a checked recipe in recipe format 1; `1437e3ad` feat(gallery): an example is a standard recipe, the index runs the gallery check | 2026-11-14 13:25:24; 13:31:11 | S5; S5 | check_1_recipe_format.md, Entry 1 (F2) |
| Three plots of the figshare recipe were renamed to lower case. The picture and the table are the same. No decision of hers was found; a saved session that uses the old names was not checked. | B3 | N | `ce373923` feat(recipes): the shipped recipes take the strict form and pass the recipe checker | 2026-11-14 12:15:19 | F5.2 | check_5_baseline.md, section B (rename) |
| In the Test Lab, if the dataset choice of the scaffold form cannot be read, the first uploaded file is taken and nothing is said. | SP3 | S | `dd4d7125` fix(app): the scaffold form writes the ID cleaning steps as recipe steps | 2026-11-14 12:29:45 | F5.2 | check_8_rest.md, finding F4 |
| Rule-file change with nothing on record: the retest steps follow the new action names. | RF | R | `da4e5ae7` test(retest): a select step with a misspelled column replaces the retired output field scenario | 2026-11-14 13:25:14 | S5 | check_6_7_rules_tests.md, A1 |
| Three tests of the ID-cleaning steps are marked "expected to fail": the suggested steps do not give the matches the user accepted. The task that covers it is marked done. Minor. | T4 | T | `87542c4e` fix(id_reconciliation): a lower case match suggests its step, an unknown pattern is refused | 2026-11-14 12:29:35 | F5.2 | check_6_7_rules_tests.md, B3 table |
| A draft made by Blueprint that the app cannot load is held by an "expected to fail" test; its task is done and this item is in no open task. Minor. | T6 | T | `4f3418b0` fix(blueprint): the new recipe form writes format 1 and the raw yaml views keep the key order | 2026-11-14 13:25:24 | S5 | check_6_7_rules_tests.md, B3 table |

### 2c. B: 2026-11-09 00:00 to 2026-11-14 12:03 (30 findings)

| What the user or the recipe author sees | Code name | Kind | Commit | Date and time | Model | Described in |
|---|---|---|---|---|---|---|
| The checker does not read the formulas of `polars_with_columns` and `polars_remove`; a forbidden formula passes the check and is refused only when the table is built. | F1 | D | `5a7ab37b` feat(utils): check_recipe, the strict recipe loader and the format as data (W2) (the action schema without the marker is from `159ffe78`, 11-13 21:25) | 2026-11-13 21:30:12 | S5.5 | check_1_recipe_format.md, Entry 1 (F1) |
| Two joined tables that both hold a column of the same name: the second becomes `<name>_right` and nothing says so. The decided error is never run. | F4 = J2 | D | `5a7ab37b` (the J08 check was written to need a recipe graph that no caller gives) | 2026-11-13 21:30:12 | S5.5 | check_1_recipe_format.md, Entry 4 (DEC19); check_3_joins.md, behaviour (g) |
| An exploration filter on a column that the table shown does not have is skipped without a word; the badge still counts it as on. A test calls this "by design". | H1 | S, D | `b055ba07` feat(home): preview filters on Raw and Result, one operator vocabulary | 2026-11-11 11:33:15 | S5.5 | check_4a_home.md, Entry 19 |
| A "Reshuffle" button draws a new seed on a click, and the pin is stored in the plot-style slot. No decision covers the button. | H2 (no name in the summary) | N | `dc49a7e5` feat(home): reshuffle-and-pin control for an unpinned plot seed (#49) | 2026-11-09 17:14:12 | S5 | check_4a_home.md, Entry 25 |
| In HOME an error while reading the Reshuffle click is ignored. Harmless by reading. | SP1 | S | `dc49a7e5` | 2026-11-09 17:14:12 | S5 | check_8_rest.md, finding F4 |
| If the table schema cannot be read, no filter is reported as not applicable. | SP4 | S | `b055ba07` | 2026-11-11 11:33:15 | S5.5 | check_8_rest.md, finding F4 |
| The check of a recipe against its data lets a step through that fails on the real values (text turned to a whole number); the build fails later. | R3 | S | `af36dc9a` fix(validator): the recipe data check runs the wrangling, not only the plan | 2026-11-11 22:50:20 | S5.5 | check_8_rest.md, finding F3 |
| About 55 old action names are refused with "choose a registered action" and not with the new name. | R2 | D | `d63d3f3d` feat(engine): the switch to recipe format 1 on the branch (a331e6e9 on 11-15 09:05 added one name) | 2026-11-13 22:18:04 | S5.5 | check_8_rest.md, Entry 10 and finding F5 |
| Three actions were removed (`value_counts`, `select_by_pattern`, `sanitize_column_names`) with no decision of hers. | N1 (no name in the summary) | N | `d63d3f3d` | 2026-11-13 22:18:04 | S5.5 | check_8_rest.md, Entry 7 table |
| `derive_categories` was removed "as dead" by an agent's choice, marked provisional (D-0038). | N2 (no name in the summary) | N | `d63d3f3d` | 2026-11-13 22:18:04 | S5.5 | check_8_rest.md, Entry 10 |
| `ST22_Anchor` got a new column `phenotype` (empty in 31 of 617 rows). No decision names it; the task says "Eve to confirm". | B1 | N | `99a14148` feat(recipes): demo recipe on the new standard, the ST22 phenotype rename is a step, dead submission code removed | 2026-11-14 11:11:35 | S5.5 | check_5_baseline.md, section B |
| The demo recipe's joined table went from 30 to 28 rows: 12 of 27 samples fall out (no MLST result), 3 rows with no sample id fall out, and the 28 rows are only 15 samples. Her decision allows the correction but not this size of loss. | B2 | D | `99a14148` | 2026-11-14 11:11:35 | S5.5 | check_5_baseline.md, section B |
| The bioscientist rule file lists 67 "verified action names" to use; none of them is registered. An agent that obeys it writes recipes the engine refuses. | RB (no name in the summary) | R | `d63d3f3d` (the old actions were removed; the list was last edited by `0db0b49e`, 11-09 16:25) | 2026-11-13 22:18:04 | S5.5 | check_6_7_rules_tests.md, A2 point 1 |
| The test of the conversion of the old step `split_column_to_parts` was removed and not replaced. | T1 | T | `6f3ec110` test(libs): the library tests follow the new registry, the old action tests are replaced | 2026-11-13 22:25:07 | S5.5 | check_6_7_rules_tests.md, B1 (42-a) |
| A test file was deleted that checked how column names travel through the tiers and a join; nothing replaces it. | T2 | T | `8f2dfe7d` test(app): the app tests follow format 1; uploads are checked with the declared types | 2026-11-13 22:32:23 | S5.5 | check_6_7_rules_tests.md, B1 (42-b) |
| A comment in the code says a saved session and an export give the same hash of the steps; they differ. And three places of the export rule file are older than her decision of 2026-11-09 and no longer match the code. | E6 | R | `4bf00271` feat(session): T3-steps restore integrity check (the comment); the rule text is older than the decision `b8f59f6d` docs(adr): ADR-097 (2026-11-09 12:19:27) | 2026-11-09 13:10:47 | - | check_4b_export.md, finding F3 and the last table row |
| Session screen: saving a session label fails with no message. | E1 place 3 | S | `c8c62dc5` feat(session): editable per-session labels | 2026-11-09 16:38:55 | S5 | check_4b_export.md, section D table |
| Session file: a damaged `assembly.json` resets the label to empty with no message. | E1 place 6 | S | `c8c62dc5` | 2026-11-09 16:38:55 | S5 | same |
| Import of a bundle: any error while the local recipe is hashed turns into "not checked", with a text that can be wrong. | E1 place 10 | S | `0821ef6f` feat(export): sensitive-data warning + import with hash verification | 2026-11-09 15:33:12 | S5 | same |
| Export: if the reproducibility recipe step fails, the user sees nothing on screen; the error is only written inside the zip. | E1 place 13 | S | `682fdfe2` feat(export): opt-in reproducibility/reimport bundle | 2026-11-09 14:05:06 | - | same |
| Rule-file change with nothing on record: strict import (only declared fields enter); error text of the retest. | RF | R | `9bfdaf4c` feat(ingestion): strict import - only declared input fields enter | 2026-11-13 16:35:51 | S5.5 | check_6_7_rules_tests.md, A1 |
| Rule-file change with nothing on record: "all automatic audits are off until the refactor is finished (Eve)". | RF | R | `16d52140` docs(tests): P0 inventory of tests that encode superseded behaviour; automatic audits paused | 2026-11-13 14:57:50 | S5.5 | same, "For Eve" item 2 |
| Rule-file change with nothing on record: the retest procedure becomes a permanent workflow file. | RF | R | `19285129` chore(claude): triage the backlog; make the retest procedure permanent | 2026-11-13 14:40:10 | S5.5 | same, "For Eve" item 4 |
| Rule-file change with nothing on record: the dates of the audit table (a record). | RF | R | `e3865b59` chore(audits): triage the 2026-11-12 Thursday reports | 2026-11-13 10:23:04 | S5.5 | same, A1 |
| Rule-file change with nothing on record: a new file with the review method with personas. | RF | R | `4ba10ba9` docs(home): reading guide, review personas, UML status, safe build brief and handoff | 2026-11-11 21:34:22 | S5.5 | same, "For Eve" item 3 |
| Rule-file change with nothing on record: preview filters on Raw and Result in the UI contract (replaced the next day by `fa552bf7`). | RF | R | `b055ba07` (same commit as H1) | 2026-11-11 11:33:15 | S5.5 | same, A1 and A2 point 4 |
| Rule-file change with nothing on record: a row of the UI contract says the Test Lab info panel is reachable. | RF | R | `143ae2d4` fix(blueprint,home): close #53/#54/#55 and make Validate check the real recipe rules | 2026-11-09 20:12:44 | S5 | same, "For Eve" item 6 |
| Rule-file change with nothing on record: four filter action names added to the bioscientist list (stale since `d63d3f3d`). | RF | R | `0db0b49e` feat(transformer): register filter_ne/filter_gt/filter_lt/not_in actions (#52) | 2026-11-09 16:25:43 | S5 | same, "For Eve" item 5 |
| Rule-file change with nothing on record: rows for `bundle_importer.py` in the app structure rules. | RF | R | `0821ef6f` (same commit as E1 place 10) | 2026-11-09 15:33:12 | S5 | same, "For Eve" item 7 |
| Rule-file change with nothing on record: "no usable recipe no longer crashes" in the recipe structure rules. | RF | R | `c32e7ea2` fix(home): empty data analysis recipe state no longer crashes startup | 2026-11-09 10:21:29 | - | same, "For Eve" item 7 |

### 2d. Older than the range (14 findings)

For these the line that causes the finding was written before 2026-11-09 ("blame" = `git blame` on the line at HEAD).

| What the user or the recipe author sees | Code name | Kind | Commit | Date and time | Model | Described in |
|---|---|---|---|---|---|---|
| The report says one value is a "SHA256 of wrangling steps"; it is the key of the first stage (`tier1_key`). | F3 | D | `e7ae9209` feat(export): record the cache keys and remove a false Tier 2 on Tier 1 check (the value became the key there; the sentence is older, see section 4) | 2026-11-06 13:26:30 | - | check_1_recipe_format.md, Entry 5 |
| Session screen: a Restore click that fails for any reason other than the old format shows nothing. | E1 place 1 | S | `f540cbfc` refactor(24-B): move session management to app/handlers/session_handlers (a move; may be older) | 2026-04-30 23:07:02 | S4.6 | check_4b_export.md, section D table |
| Session screen: a Delete that fails shows nothing; the card stays. | E1 place 2 | S | `f540cbfc` | 2026-04-30 23:07:02 | S4.6 | same |
| A session left out of the list because its file cannot be read; the user sees no session. | E1 place 5 | S | `c65d536c` feat: implement session manager and T3 recipe gatekeeper | 2026-04-25 08:52:40 | - | same |
| When the recipe sha and data hash cannot be written to the session state, nothing is said, and the next steps follow. | E1 place 7 | S | `5eca5cc2` (2026-04-25 10:16:23) and `bc3d1f9e` (2026-05-02 19:44:07) | 2026-04-25 / 2026-05-02 | - | same |
| Export: if the data source paths cannot be read, the bundle holds no data files and nothing is said. | E1 place 11 | S | `3c74cb48` feat(export): implement provenance embedding in exported images | 2026-05-09 18:20:01 | - | same |
| Export: if the picture metadata (keys) cannot be written into a PNG or SVG, the picture has no keys and nothing is said. | E1 place 12 | S | `3c74cb48` | 2026-05-09 18:20:01 | - | same |
| Export: if Quarto fails, the report is not made and the only trace is a text file inside the zip. | E1 place 14 | S | `037f9b7c` fix(export): plot format explicit, plot_bytes for Quarto render | 2026-05-02 11:00:30 | S4.6 | same |
| A restore skips the newest save when it cannot be read and restores an older one, without naming the damaged one. | E2 (= E1 place 4) | S | `c65d536c` | 2026-04-25 08:52:40 | - | check_4b_export.md, section D table (place 4, scenario S3) |
| When the session holds no keys, "audit steps applied" saves nothing, and a restore gives no warning. | E3 (= E1 places 8 and 9) | S | `c65d536c` (the save, place 8); `f540cbfc` (the recipe-key warning, 04-30); `4bf00271` (the data-batch warning, 11-09 13:10) | 2026-04-25 08:52:40 | - | same (places 8 and 9) |
| The report links data files that do not exist (`T3_data.tsv`; the real files are one per plot). | E4 | D | `10ef3200` feat(export): block an export when the files changed since the view, build T3 on T2 (per-plot file names; the link text is from `5430278a`, 2026-05-02) | 2026-11-06 13:47:54 | - | check_4b_export.md, finding F1 |
| With the audit switch off and steps present, the plot and its data are audited but the export records no steps. No shipped setting reaches this. | E5 | D | `7916691d` design: enhance export functionality (the switch on the report side, 2026-05-04); the plot side read the steps without the switch before `307e6b4e` (reasoned, see section 4) | 2026-05-04 18:21:38 | - | check_4b_export.md, finding F2 |
| Every save in Blueprint drops all the comments of a recipe file (12 comments became 0 in the main test recipe). | R1 | D | `68cd1c9c` feat(BP-GROUPS-1): group/plot sidebar inventory with CRUD functionality (the `yaml.dump` writer); her rule is of 2026-11-13 | 2026-05-21 11:50:33 | - | check_8_rest.md, finding F1 |
| Blueprint's "create plot" writes a plot that the checker refuses (an empty plot with the wrapper key `spec`). | R4 | D | `68cd1c9c` (the stub); her rule is of 2026-11-13 | 2026-05-21 11:50:33 | - | check_8_rest.md, finding F2 |

### 2e. Date not found (1 finding)

| What the user or the recipe author sees | Code name | Kind | Commit | Date and time | Described in |
|---|---|---|---|---|---|
| A join that multiplies rows (4 rows became 7) or drops rows is told to the user nowhere except per key in the Blueprint preview. No decision covers it; the open task HOME-EXPLORE-10 asks for it. | J3 (no name in the summary) | S | None: this was never built. The join engine file is from 2026-04-07 (`4ae002a1`, `a3444b42`); the task line was written in `93129a4b` on 2026-11-11 21:59:48. | not applicable | check_3_joins.md, behaviour (d) |

### 2f. Not counted: seven rule-file commits where the decision is on record and her yes to the text is not

These are class B of the rule-file check. The list of rule-file changes already asks her about each.

| Commit | Date and time | Model | Group |
|---|---|---|---|
| `74abfc48` the orchestrator integrity-suite rule becomes the pytest gate | 2026-11-14 08:52:12 | S5.5 | B |
| `873cf3a4` one session (HOME) reports to Eve | 2026-11-13 18:35:58 | S5.5 | B |
| `58e56842` channel message limit lifted | 2026-11-13 15:34:27 | S5.5 | B |
| `22a0dc14` the na tick in the filter value lists | 2026-11-14 19:40:51 | F5.2 | A-after |
| `f8636ff4` the filter row lists `between`, `closed` | 2026-11-14 23:56:16 | F5.2 | A-after |
| `89043503` typed filter values, operators by column type (ADR-104) | 2026-11-15 01:14:48 | S5.5 | A-after |
| `2b13bbdb` browser-test time worded as "one measurement" | 2026-11-15 14:30:37 | S5.5 | A-after |

### 2g. What did NOT deviate, by period (only the items that name a commit)

28 held items name a commit. The other held items are checks of the state at HEAD (49 shipped recipes pass the checker; 14 actions equal Polars; the export equals what is seen; and so on). I do not attribute those to a period: "not attributed" (about 39 entries by the overview table of the summary; some overlap with the 28).

| Group | Count | Items (commit, date and time) |
|---|---|---|
| B | 7 | `18e5cda6` golden baseline created (11-13 21:08); rule-file commits with her yes on record: `6521f966` (11-13 16:08), `c454bcf6` (11-13 14:34), `6349ba7f` (11-12 17:33), `e0f79a84` (11-11 23:19), `d36a2a05` (11-11 19:52), `fa552bf7` (11-11 13:30) |
| A-before | 6 | `1f2c447e` (11-14 13:22), `547c6a78` (13:54), `6e318386` (14:33) rule-file commits with her yes on record (the guard hook of the last one only tightens); `1547aab9` (14:09) and `db9d5113` (14:08), types changed with no value changed; `d81ce81f` (13:31) gallery pictures resized only |
| A-after | 15 | Rule-file commits with her yes on record: `772881f3` (11-15 13:55), `3a3aa73d` (11-16 08:26), `d64f0cdf` (11-16 08:29). Five fixes whose undoing a test caught: `6a5af970` (11-15 13:32), `26c40302` (11-14 20:00), `a8fe20f2` (11-15 09:04), `d94bc6a4` (11-15 09:37), `fe2a812e` (11-15 13:09). Allowed and exact: `9490490d` (11-15 13:10), `2ac83ddb` (11-15 23:29), `5363c930` (11-15 13:13), `f37ba13d` (11-14 19:38), `2e4b9dc8` (11-15 00:16), `307e6b4e` (11-15 18:59), `551462d3` (11-15 09:41) |

## 3. What this does and does not show

What the evidence shows:
- The count is not higher after the coordinator started. B has 30, A-before 6, A-after 14. A-after has the most commits (439 against 235 in B), so per commit it is lower, but the checks were not drawn evenly by time; do not read these as rates.
- By kind, code and data findings (D, N, S) are B 16, A-before 3, A-after 6, older 14. Rule-file and record findings (R) are B 12, A-before 1, A-after 5. Test findings (T) are B 2, A-before 2, A-after 3.
- The findings that change a result with no decision are three: B1 and B2 (both in `99a14148`, 11-14 11:11, before the first Fable message) and M1 (`7f4ea21a`, 11-16 02:01, after). The B3 rename (`ce373923`, 11-14 12:15) changes names, not values.
- No commit of group B carries a Fable line (0 of 235 commits). Fable lines appear from `ce373923` (12:15 on 11-14): 14 of 34 commits without merges in A-before, 88 of 342 in A-after. Five findings have a Fable line on the commit that introduced them: J1, J4, B3, SP3, T4. None of them changes a result.
- Most silent places are old code. Her rule "no silent error" was spoken on 2026-11-14 at 19:33 local (ledger D-0050, her turn at 18:33 UTC). Of the 20 silent places (E1 14, SP1 to SP4, R3, H1), 19 were written before that time and one (SP2, `39ed8983`) after.
- Most rule-file edits with nothing on record are older than her rule D-0104 (11-15 19:36 UTC = 20:36 local: no rule file changes without her agreement, one traceable list). 13 of the 15 were made before it. Two came after: `ee4f1eac` and `f1f70353`, both on the morning of 11-16, and the files mark them as the builder's text for her to accept or remove. Four of the 15 are fact fixes or records by the check's own words (`fdb7df0f`, `da4e5ae7`, `9bfdaf4c`, `e3865b59`).
- Some findings were written before the decision they now break, so they were not a deviation when written: J1 (code 11-14 19:40, decision D-0078 on 11-15), H1 (code 11-11, rule 11-14), R1 and R4 (code May, rule 11-13), the older swallows. In these the deviation starts at the date of the decision, not of the commit.
- A finding of period B that a later commit could have caught and did not (only the facts):
  - F1 and F4 come from the same commit `5a7ab37b` (11-13 21:30). `recipe_check.py` was changed by 40 later commits and `polars_calls.py` by 8 since `159ffe78`; none closed the two gaps. The checker's own test for formulas uses a made-up parameter (check_1, Entry 1).
  - H1 (`b055ba07`, 11-11): the audit path was corrected by `307e6b4e` (11-15 18:59), the exploration path next to it was not, and a test still says the skip is "by design". `t3_audit_engine.py` was changed by 19 later commits.
  - R3 (`af36dc9a`, 11-11): `data_analysis_recipe_validator.py` was changed by 23 later commits; the swallow is still there.
  - R2 (`d63d3f3d`, 11-13): `a331e6e9` (11-15 09:05) added one old name to the table, and the other ones stayed unnamed.
  - E1 places 3 and 6: `c8c62dc5` (11-09) added swallows in files that already held older ones; two later commits (`8bf8a8fc` 11-15 20:13, `45742491` 11-15 23:21) changed `session_handlers.py` and left the older ones.

What this does not show:
- It does not show that a model, a session or the coordinator is the cause. The trailer names the committing session, and every commit has the same author. I cannot tell who wrote which line.
- It does not show rates. The 45 entries of the check were chosen by area (`could_have_deviated.md`), not by period, and I do not know how well each period was covered. A period with few findings may be less checked.
- It does not show that the A-after period is clean: batches 4a and 4b could not use a browser (the filter dialog, Compare, a real download), and commits of 11-15 and 11-16 that no check entry reaches are unexamined.
- Decisions taken in chat and never written down are not visible (the check files say so too), so "no decision found" can mean "not written".

## 4. How I found each date, and what I could not check

Method:
- For every finding where a check file names a commit, I ran `git show -s --date=iso-local <hash>`. All the named commits exist (they are in the tables with hash, time and subject).
- Where a check file names only a file and line, I ran `git blame --date=iso-local -L<line>` at HEAD (`7632f963`) and, for text that could have moved, `git log -S"<text>" --date=iso-local -- <file>`. Examples: F1 (`polars_calls.py:81`, `recipe_check.py:558-571`), F2 (the three `check_recipe(` calls), H1 (`t3_audit_engine.py:552`), R2, R3, R4, the 14 places of E1.
- Model lines: `git show -s --format="%(trailers:key=Co-Authored-By,valueonly)"`.
- Decision dates: from `.claude/knowledge/decision_ledger.md` (D-0050, D-0078, D-0104 and the others named above). D-0050 and D-0104 are given as UTC in the ledger; I converted them to local time (+1 hour).
- Commit counts per period: `git log --since/--until` at HEAD (714 commits since 11-09 00:00; the check files say 701 because HEAD moved).

What I could not check, or did by reasoning (so weaker):
- E5: the gate on the report side is from `7916691d` (blame). That the plot side read the steps without the switch before `307e6b4e` is reasoned from `git show 307e6b4e^` (the old code used `t3_filter_rows`, which does not read the switch); I did not run the old version. The finding stays "older than the range".
- E4: the link text is from `5430278a` (2026-05-02). The per-plot file names appear in `10ef3200` (2026-11-06) by `git log -S"T3_data_{"`. The check file itself labels the date "reasoned".
- F3: the value became the first-stage key in `e7ae9209` (2026-11-06). I did not find the commit that first wrote the sentence "SHA256 of wrangling steps"; `git log -S` finds only later edits of the line (`9ef3ffd1`, 11-07; `469cd552`, 11-16, a text-safety change).
- E6: the comment is from `4bf00271` (11-09). Whether the two hashes already differed that day, or began to differ later, I did not check. Both parts of E6 are placed in B because the comment and the decision it follows are of 11-09.
- E1 places 1 and 2: blame gives the move `f540cbfc` (2026-04-30); the swallow may be older. Either way it is before the range.
- R2: that the old names were refused without the new name from `d63d3f3d` on is reasoned: at that commit the validator does not fill the table of old names (`git show d63d3f3d:...` has no `old_action_names`).
- J1 and J4: the line was written on 11-14 19:40, but the deviation from decision D-0078 exists only from 11-15. I placed J1 and J4 by the commit, as asked.
- Commit times are author times. A branch merged later keeps the author time of its commits; merge times are not used. I did not check clock errors between worktrees.
- I did not check any check file's own finding again, and I did not read the 45 entries of `could_have_deviated.md` one by one, only its header.

## 5. Contradictions between the check files

- `SUMMARY_for_eve.md` (batch 4b) says "two of them are older than the redesign: April 2026". The table of `check_4b_export.md` shows nine of the 14 places older than 2026-11-09 (April 25 to May 9). Blame agrees with the table.
- `check_1_recipe_format.md` (F2) says the missing lists date "since `5a7ab37b`..`ce373923` (2026-11-13/14)". By blame the three calls were written by `7f052638` and `1437e3ad` on 11-14 at 13:25 and 13:31.
- `check_4b_export.md` dates E1 place 7 "April"; blame gives `5eca5cc2` (April 25) for the outer swallow and `bc3d1f9e` (May 2) for the inner one.
- I found no other contradiction between the check files.
