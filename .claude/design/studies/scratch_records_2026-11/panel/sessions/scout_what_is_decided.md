# SESSIONS-SCOUT-1: one recipe, many datasets, sessions (read-only, facts only)

Labels: **[read]** = read at file:line in this run; **[grep]** = found by search, the line was checked; **[reasoned]** = my inference from the cited lines. Nothing was built, changed or decided. Ledger numbers are the status in `.claude/knowledge/decision_ledger.md` on 2026-11-16.

## Summary table

| # | Question (M175) | DECIDED (ledger, taken by EVE) | Open / state |
|---|---|---|---|
| 1 | How the user chooses the dataset | D-0030, D-0045, D-0184, D-0185, D-0186 (D-0184 replaces part of D-0009) | No ledger line for "select data to replace the default data". Its only record is the intent doc quote (Tcd L1497), CONFIRM. M175 says "already decided": not found. Code has no per-session dataset choice. |
| 2 | What identifies a session | D-0025 (ADR-101), D-0003 (ADR-089) | Built: key = recipe hash + data hash; list grouped by recipe. Session-key rule is in ui contract 12d (CONFIRM, no line). |
| 3 | Session label and comment | none | Built as a free label (no ledger line). Her comment request is in "Asked, not decided" (ledger:262, "as was in place"). Label is not exported. |
| 4 | Several sessions side by side | none directly | Not found in code (one active state, switch and restore only). Asked, not decided (ledger:262). |
| 5 | Data change and audit steps | D-0088 (re-base; her words are about recipes), D-0005, D-0186, D-0025 | Re-base not built (no code hit). Records disagree on what happens to old steps (section 5 below). |
| 6 | Data check per dataset | D-0002, D-0009 (on start), D-0079, D-0184 (not built), D-0185 | Built: a load and a run of each dataset, with the engine's message. Not built: check on selection. Data differences that keep the columns pass (reasoned). |
| 7 | What the export records about data | D-0013, D-0186, D-0187 to D-0193 (D-0191 = "the dataset the user has actually worked with") | Built: hashes and the recipe's own source paths. No dataset choice exists, so D-0191 cannot be met yet. Session label not in export. |

---

## 1. How the user chooses the dataset

(a) **DECIDED**
- D-0030 (2026-11-12): "Import is its own function, on only by configuration, for an authorised person" [ledger:59].
- D-0045 (2026-11-14): "Imported data stored by dataset id in its own folder, 'as production'; the recipe's path is not touched; mechanism open (Eve)" [ledger:74].
- D-0184 (2026-11-16, replaces in part D-0009): "I think the recipe should fail when its selected and not all recipes checked at boot loader" [ledger:213].
- D-0185 (2026-11-16): "in a production environment the recipe will be used on different datasets - that are the datasets that will be most likely to change not the recipes" [ledger:214].
- D-0186 (2026-11-16): "Well changing data is not necessary a failure but changing a recipe is" [ledger:215].

(b) **CONFIRM / RELAYED / no line**
- Intent doc:89 quotes her Tcd L1497 (2026-11-15 22:07): "the user will be able to select data to use - to replace the default data used in the recipe ... the purpose being to analyse data produced regularly (pipelines) using the same recipe." No ledger line carries this text (ledger searched for "default data", "data selector", "dataset"). CONFIRM.
- HOME.md:124-125 says the source dropdown is "decided 2026-11-13 (Eve)". The text is about which node to look at (Source, T1, T2, T3) and the datasets that feed a table. No ledger line dated 2026-11-13 holds it. CONFIRM, no line.
- M175 says "the data selector already decided: replacing the default data of the recipe". No ledger line holds those words. Disagreement with the ledger (see section 6).
- Asked, not decided (ledger:262) lists "how the user chooses the dataset" as open.
- ADR-088 point 5 (architecture_decisions.md:4282, ADR-088 heading at :4252): "`source.path` is the **default data** (a development and test shortcut)". The ADR does not say a user may pick another dataset.

(c) **BUILT TODAY** [read]
- A deployment fixes the recipe: `data_analysis_recipe_selector.visible: false` and `testing_mode: false` in `config/app_features/pipeline-exploration-simple.yaml:38-42`.
- `testing_mode` defaults to true: `app/src/bootloader.py:812-814`.
- With testing_mode false, the Data Import panel is read-only: "Data paths are set by the deployment configuration (read-only)." `app/handlers/data_import_handlers.py:132-140`. With testing_mode true it shows "Current default data paths (override below for testing)" and upload slots: `data_import_handlers.py:174-181`.
- A recipe names its source file in each dataset schema as `source.path`: `app/modules/orchestrator.py:85` and the doc at `:72-80` ("development default"). In production the code drops `source` and discovers the file by schema id under `raw_data`: `orchestrator.py:131-133`. Deployment `locations.raw_data` is in `config/deployment/` (example `config/deployment/local/local.yaml:13-15`).
- The HOME session takes the source files of the active recipe only: `app/handlers/home_theater.py:1217-1224` calls `orchestrator.get_source_files(data_analysis_recipe_id)`. `get_source_files` is at `app/modules/orchestrator.py:411-422`.
- The data check runs at HOME load for every recipe: `app/src/bootloader.py:387-400` (`_gate_one`), called in the candidate loop at `:416-427`.

(d) **OPEN**: no code or record that lets the user choose a dataset for a recipe in a session. Searched: `app/` for "data selector", "default data", "source selector"; `.claude/design/` and `.claude/knowledge/` for "dataset selector", "choose data", "data to show". Only the cites above.

## 2. What identifies a session today

(a) **DECIDED**
- D-0025 (2026-11-12): "Key = series of labelled parts ... data hash = full content once per session; retire `decision_hash`" [ledger:54]. Its evidence cites the hash model file section 5 and ADR-101.
- D-0003 (2026-11-05): "Chained keys T1 to T2 ... no anchor reuse by file name" [ledger:32], ADR-089.
- ADR-101 decision (architecture_decisions.md:5236-5238, heading :5229): "`session_key = R[:12]:D[:12]`. They never decide what to rebuild." Eve decided 2026-11-12 per the ADR heading and the ledger.

(b) **CONFIRM**
- ui_implementation_contract.md:169: "`session_key` = `data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]`, see §12d"; :170 "Multiple sessions are allowed per user"; :171 "Sessions carry an optional user-supplied `label`... editable from the session panel". No date, no author. Rule file, CONFIRM.
- Intent doc:51: "**Session**: the saved unfinished work of one recipe on one data set; its name is the recipe hash and the data hash." Cites ADR:5238. CONFIRM.
- HOME.md:119 (session_key) and HOME.md:131 (the switch needs the sandbox flag, audit mode needs sessions and export switched on).

(c) **BUILT TODAY**
- Key computed as `f"{sha[:12]}:{dbh[:12]}"`: `app/modules/session_manager.py:219-221`. Data hash = SHA-256 of all source files: `session_manager.py:198-212`. Recipe hash = `load_data_analysis_recipe(...).data_analysis_recipe_sha256`: `session_manager.py:185-191`.
- The session list is grouped by recipe hash prefix: `app/handlers/session_handlers.py:110-114`. Each card shows "Batch: {data_batch_hash[:8]}": `session_handlers.py:126, 136`. So one list per recipe, each card with its data batch, as M175 asks.
- Session folder: `{location_4}/_sessions/{session_key}/` (`session_manager.py:170` doc; ui contract 12d :523).

(d) **OPEN**: nothing found for a session that holds two datasets of one recipe at once, or a second session of the same recipe and data. Reasoned: the key is per (recipe, data) pair, so a second dataset gives a second session by construction.

## 3. The session label and any note

(a) **DECIDED**: no ledger line for a session label or note. Searched "label" and "session" in the ledger; the label appears only in "Asked, not decided" (ledger:262, her words "that is why the user needs to be able to write comments in what the session is about (as was in place)", Tcd L2542).

(b) **CONFIRM**: ui_implementation_contract.md:171 (optional label, e.g. "AMR_run_Jan2025"); :182 (Restore, Delete). Design-level, no date.

(c) **BUILT TODAY**
- Stored in `assembly.json` as `label`: `app/modules/session_manager.py:258-272` (`write_assembly_ghost`, the label comment "REPRO-SESSION-LABELS-1 (#50)" at `:249-257`). Read: `get_session_label` `:570-582`; written: `set_session_label` `:584-591`.
- Edited in the panel as a text box, saved on blur: `app/handlers/session_handlers.py:144-149` (text box), `:286-299` (save when changed). Placeholder "Describe this session…" at `:146`.
- Shown in the card: `session_handlers.py:129` (`label = s.get("label", "")`), input at `:144-146`.
- Export: **not used**. `get_session_label` is called only at `session_handlers.py:298`; `export_handlers.py` has no session label (grep). The report helper `app/modules/qmd_text.py:3` says a session may supply text to `report.qmd`, but no caller passes one (grep).
- Commit `c8c62dc5`: not checked (no git tool in this run). The code comment names REPRO-SESSION-LABELS-1 (#50) at `session_manager.py:249`.

(d) **OPEN**: a longer note, when the label can be edited, export of the label to README or the audit recipe header. Not found in the ledger or the design files. The audit recipe `#` comment (D-0148) exists for the reason of each step, not for the session.

## 4. Several sessions side by side

(a) **DECIDED**: none specific. Related: D-0102 (original recipe never edited; the audit recipe is a copy with the audit steps) [ledger:131]; D-0040 (audit copy is the source of truth) [ledger:69]; D-0093 (user ticks the nodes; counts before and after) [ledger:122].

(b) **CONFIRM**: ui contract 7.1:170 "users can switch between sessions"; 7.1:176 restore "matching on `session_key`". HOME.md:134: "`audit_recipe` is a real file in the session folder. When it is first written is OPEN (O2)". Intent doc:178 "In audit it holds the `audit_recipe` (the copy) and its log; restoring recomputes."

(c) **BUILT TODAY**
- One restore at a time: `session_handlers.py:334-372` reads one ghost and notifies on a recipe or data mismatch (`:349-370`). The active HOME state is one dict (`home_theater.py:1229-1256`), so one active recipe hash and data hash at a time (reasoned from that code).
- Restore warnings, text as built: "Session was saved against a different data analysis recipe version. Audit step may not match current columns." (`session_handlers.py:353-358`); "Session was saved against a different data batch. Row filters and exclusions may match different or no rows." (`:365-370`). Both are warnings, the restore continues.
- No code found that keeps the audit steps of two sessions open together, or compares two sessions. Searched the files read; a full search for "compare sessions" was not run.

(d) **OPEN**: several sessions open or compared side by side (Asked, not decided, ledger:262, from M175). Intent doc:238 on the readable summary is separate.

## 5. What a data change does to an existing session's audit steps

(a) **DECIDED**
- D-0088 (2026-11-15): "The audit export is refused until the user re-bases; re-base marks each step applied, not concerned or broken; a broken step blocks the export" [ledger:117]. Her words: "S2-3: a - however unlikely recipes are changed during work" (#1012). Her words name **recipes**.
- D-0005 (2026-11-06): "export refuses when files changed since the view" [ledger:34].
- D-0186 (2026-11-16): "changing data is not necessarily a failure, but changing a recipe is" [ledger:215].
- D-0025 (2026-11-12) "data hash = full content once per session" [ledger:54].

(b) **CONFIRM / conflicting**
- Hash model file section 5 (`.claude/design/home_evidence/home_hash_model_2026-11-12.md:52`, "decided (Eve, 2026-11-12)"): "A file that is imported or replaced changes its hash ... the session key changes, so audit steps of the old data stay with the old session (restoring them warns)." No ledger line carries the "old session" sentence. Intent doc:179 and :260 mark it CONFIRM (O9).
- Intent doc:182 (point 10): "the audit steps are written again into the new original; each is marked applied, not concerned or broken". Her words cover only the export refusal and the statuses (D-0088). The "written again" part is not in her words (intent doc:4-9 says point 12 is not confirmed, ledger D-0151 RELAYED).
- Stage-2 spec: S2-3 (`home_stage2_mechanism_spec.md:79`) says "the recipe or the data changes"; its section 3 point 6 (:133) is tagged **[MINE, S2-3]**. tasks.md:397 says "DECIDED 2026-11-15 (M102)".

(c) **BUILT TODAY**
- Re-base: **not found** in `app/` (search for "re-base", "rebase" over the repo, excluding `tmpAI/`, hits only tasks.md, ledger, design, docs). Queued in tasks.md:397.
- Data change while a view is open: `app/modules/data_change_notice.py:25-28` ("the export is refused until the page is reloaded"). The export refuses on changed keys: `app/handlers/export_handlers.py:209-225` (`changed_since_view`: recipe, data, processing rules).
- Data change in HOME: `home_theater.py:1236-1244` warns, does not block.
- Audit steps and data: `.claude/design/home_audit_steps.md:245-247`: "When the recipe or the data change (the original keys change) the audit entries that depended on them are removed at that moment." This disagrees with the hash model and with D-0088 (see section 6).

(d) **OPEN**: what the user is told about the counts before and after a data change; the re-base mechanism (who writes the steps, at which node); whether re-base covers data changes or recipe changes only (D-0088 words name recipes; S2-3 and intent point 10 say both).

## 6. The data check per dataset

(a) **DECIDED**
- D-0002 (2026-11-05): "Recipe ... errors raise; the app reports and skips, never exits" [ledger:31].
- D-0009 (2026-11-08): "HOME checks every recipe at start (structure + data); a failing one is not selectable, shows reason + contact" [ledger:38]. Part replaced by D-0184.
- D-0079 (2026-11-15): "A recipe with an error is not accepted in HOME (a message ...)" [ledger:108].
- D-0184 (2026-11-16): "A recipe is checked when it is selected, not all recipes at start" [ledger:213].
- D-0185 (2026-11-16): "Measure the time of start at first load" [ledger:214].

(b) **CONFIRM / RELAYED**
- D-0185 relay: the split (structure keyed by recipe file set hash, data keyed by recipe and data hash, failure message naming recipe or data and the file) is the review session's design, RELAYED, not her words (ledger:214 bracket).
- D-0184 relay: the design (selector lists, check on selection, message with WHAT failed and the contact) is the review session's (ledger:213 bracket).

(c) **BUILT TODAY**
- `validate_data_analysis_recipe_data(path, raw_data_dir, ...)`: `app/modules/data_analysis_recipe_validator.py:352-400`. For each dataset schema it runs `prepare_ingredient` and reports "dataset cannot be loaded: {exc}" with the engine's tip (`:386-390`). It then runs `frame.head(1).collect()` and reports "wrangling cannot run on this dataset: {exc}" for a SchemaError or ColumnNotFoundError (`:395-399`). Each problem carries the file name and the location `section.ds_id` (`:343`, `:389`).
- The check is called at HOME load for every recipe: `app/src/bootloader.py:393-400`, and in Blueprint Validate: `app/handlers/blueprint_handlers.py:3013`.
- The check does not compare the data to a stored hash or contract: a dataset that is different but loads with the declared columns gives no problem (reasoned from the code; no comparison found in the function).
- Tests: `app/tests/test_data_analysis_recipe_data_check.py` (e.g. lines 98, 107, 115, 154) cover missing or wrong-type columns.

(d) **OPEN**: the message wording for a dataset that does not match (M175 wants "an error naming the file and the column"; the built message is the engine's text plus its tip). Check on selection is **not built** (tasks.md:466 CHECK-ON-SELECT, "impact report running"). Startup check still in place: `bootloader.py:416-427`.

## 7. What the export records about the data used

(a) **DECIDED**
- D-0013 (2026-11-09): "`effective_run.yaml` always" [ledger:42].
- D-0186 (2026-11-16) [ledger:215].
- D-0187 (2026-11-16): "if the user has used audit both mode 1 and mode 2 must use audit recipe and data, hashed" [ledger:216].
- D-0188: "If the user only explored ... mode 1 and mode 2 export the original recipe and the data that was used" [ledger:217].
- D-0190: "The app has to distinguish when the user has worked in audit mode and added steps or if its only exploration" [ledger:219].
- D-0191 (2026-11-16): "The export is always of the dataset the user has actually worked with: if the user uses the same recipe with several datasets ... we need to ensure he can export the result of the dataset he has choosen" [ledger:220].
- D-0192 (2026-11-16): recipe in mode 2, removed from mode 1 [ledger:221]. D-0193 (2026-11-16): one source, two purposes [ledger:222].

(b) **CONFIRM / RELAYED**
- Ledger bracket on D-0191 (added by the review session, not her words): "its files and hashes in effective_run.yaml; its data copied in Reproducibility" (ledger:220).
- D-0187 bracket: the reading "identified by hash in Publication, included in full in Reproducibility" is the review session's (ledger:216).
- Intent doc:188-189 and 191 (export, CONFIRM where not her words).

(c) **BUILT TODAY**
- `effective_run.yaml` written unconditionally: `app/handlers/export_handlers.py:1365-1409`. It holds `data_analysis_recipe_sha256` (:1385), `data_batch_hash` (:1386), `t3_audit_steps_sha256` (:1387), and `data_source_paths` (:1395).
- `data_source_paths` = `orchestrator.get_source_files(data_analysis_recipe_id)`: `export_handlers.py:121-128`. These are the active recipe's own source files only (no dataset choice exists; see section 1).
- README: data source block `export_handlers.py:1866-1869`; data folders `export_handlers.py:808` (T1 TSV per dataset referenced by active plots).
- Session label: not in the export (section 3).
- The audit steps with who and when are in the export per the intent doc:188 (AS:346) [CONFIRM]; code not checked here.

(d) **OPEN**: which dataset was used when the user picks one (D-0191 cannot be met yet: no selection exists); the session comment in the export header (not found); whether the raw data copy is in mode 2 (not checked in this run).

---

## Records that disagree (flag)

1. **Re-base scope.** D-0088 words name recipes ("recipes are changed during work") [ledger:117]; S2-3 (`home_stage2_mechanism_spec.md:79`) and intent doc:182 say "recipe or data"; M175 asks for "a CHANGED recipe only"; D-0186 says data change is not a failure [ledger:215]. Three readings, not resolved.
2. **Old audit steps after a data change.** Hash model §5(3) (`home_hash_model_2026-11-12.md:52`): steps stay with the old session. `home_audit_steps.md:245-247`: steps that depended on the changed keys are removed at that moment. D-0088 and intent doc:182: steps are written again into the new original. Three records, three behaviours.
3. **"Already decided" data selector.** M175 says the selector is decided (ledger ref). No ledger line holds it; intent doc:89 quotes her words (Tcd L1497) with no line; HOME.md:125 says "decided 2026-11-13 (Eve)" for a different selector (node and source).
4. **Check at start vs on selection.** D-0009 (check every recipe at start, ledger:38) is replaced in part by D-0184 (check on select, ledger:213). Code still checks all recipes at load (`bootloader.py:416-427`). D-0184 is recorded DECIDED but not built (tasks.md:466). Not a record-vs-record clash, but a built-vs-decided gap.
5. **Intent point 12 vs ledger.** Intent doc:6 and ledger D-0151 (RELAYED): point 12 (export refused until re-base) is listed as confirmed by the review session but her turn does not mention it. The rule itself stays D-0088.
6. **Session ghost write.** ui contract 12d:520 says the T1/T2 ghost is written "Once on first assembly; re-written when data analysis recipe or source data changes". `home_theater.py:1258-1271` writes it in the sync effect when both hashes are present (reasoned: the write is unconditional in that branch, not compared to the stored file).
7. **Stale line reference.** tasks.md:228 cites `get_source_files` at `app/modules/orchestrator.py:236-275`; the function is at `:411-422` now.
8. **D-0045 wording.** Ledger line says "mechanism open (Eve)" with status DECIDED (ledger:74); tasks.md IMPORT-PATH-1 says "Eve DECIDED 2026-11-14: option A". Consistent in outcome; the open mechanism is still open (tasks.md:228 references it).

## Decisions a proposal could reconsider (name the decision)

- D-0088 (re-base; export refused until re-base; her words name recipes).
- D-0005 (export refuses when files changed since the view).
- D-0186 and D-0185 (changing data is not a failure; start-time check and its measure).
- D-0184 and D-0009 (check on selection; HOME checks every recipe at start; a failing recipe is not selectable).
- D-0025, ADR-101, D-0003, ADR-089 (session key = recipe hash : data hash; no anchor reuse by file name). Any per-dataset session list or a second key reconsiders them.
- D-0102, D-0040 (original never edited; audit copy is source of truth) for side-by-side sessions and for re-base.
- D-0191, D-0187 to D-0192 (export is the dataset worked with; mode contents). A dataset choice changes what they cover.
- D-0030 (import is its own function, only by configuration, authorised person). A user-chosen dataset at HOME touches it.
- D-0013 (effective_run always; two modes).
- D-0093 and D-0053 (the user chooses nodes; the app does not decide the scope).

## Not found / not checked

- No ledger line for: a dataset selector; a session label or note; side-by-side sessions; re-base (as code).
- Commit `c8c62dc5` not checked (no git access in this run).
- Not searched: a full "compare sessions" search; the Blueprint side of recipe choice; the README text of mode 2 beyond the lines above.
- Lines in `home_redesign_intent_and_consequences.md` and `spaces/HOME.md` were both read; cites above name the file by its own line numbers.

Sources read: `.claude/workflows/agent_principles.md`, `.claude/workflows/decision_compliance.md`, `tmpAI/agent_channel.md` (M175 at :1524), `.claude/knowledge/decision_ledger.md` (lines 30 to 262), `.claude/knowledge/architecture_decisions.md` (ADR-088 at :4252, ADR-089 at :4294, ADR-101 at :5229), `.claude/design/home_redesign_intent_and_consequences.md`, `.claude/design/spaces/HOME.md`, `.claude/design/home_audit_steps.md`, `.claude/design/home_stage2_mechanism_spec.md`, `.claude/design/home_evidence/home_hash_model_2026-11-12.md`, `.claude/rules/ui_implementation_contract.md` (7.1, 7.2, 12d), `.claude/tasks/tasks.md` (:397, :466, :228), `app/modules/session_manager.py`, `app/handlers/session_handlers.py`, `app/handlers/home_theater.py`, `app/handlers/data_import_handlers.py`, `app/handlers/export_handlers.py`, `app/modules/data_analysis_recipe_validator.py`, `app/modules/orchestrator.py`, `app/modules/data_change_notice.py`, `app/src/bootloader.py`, `config/app_features/pipeline-exploration-simple.yaml`.
