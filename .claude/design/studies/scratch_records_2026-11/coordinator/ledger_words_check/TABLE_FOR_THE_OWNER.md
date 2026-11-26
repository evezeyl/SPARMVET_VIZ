# Check of today's ledger lines D-0397 to D-0433: what is in your words and what is not (2026-11-21)
Transcript for the next check: /home/evezeyl/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/cd1b0ac7-1df6-422c-a447-bd2cf83b13ea.jsonl (the review session, 2026-11-14 to 2026-11-21; older files for earlier sessions are in the same folder). Row 5 answered 2026-11-21: ledger D-0459. Re-check against that transcript: RECHECK_AGAINST_TRANSCRIPT.md in this folder.

Nothing is changed by this table. No ledger line was edited. It was written by an agent that read the ledger lines and the tables you were shown (files only).

## 0. How to read this

- Your answers reached the ledger through the review session (the relay). Often you wrote a short answer ("A", "P", "R1", "8. B"). The relay added its own text of the option.
- A short letter means exactly what the table under that letter says. Anything more is "added by the relay".
- Section 1 comes first: the statements added by the relay that are in no table option and not in your words. Most consequential first.
- For each statement in section 1 you answer one of three things: **"yes, I meant that"**, **"no, strike it"**, or **"not decided yet"**.
- Sections 2 to 5 are for information: what follows from a table you saw, what is fully yours, what is still open, what I could not check.

Short names used: "names table" = `tmpAI/panel/names_whole_app/TABLE_FOR_THE_OWNER.md`; "deployment table" = `tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`; "Gallery table" = `tmpAI/panel/gallery_study/TABLE_FOR_THE_OWNER.md`; "lineage report" = `tmpAI/panel/lbfb/LOGIC_REVIEW.md`.

A big finding first: for several questions (names Q3 to Q7, Gallery Q2 "option 2", Q7 "C", the audit folder name "A", Data Import "B", deployment choice 6 to 8) the lettered option you answered does **not exist in the files**. The relay showed you its own text on screen. I cannot see that text. For these I write "option text not found" and I treat everything the ledger says beyond your words as added.

---

## 1. FIRST: statements ADDED BY THE RELAY (in no table option and not in your words)

| # | Decision (what it is about) | Her words | The statement that was added | Why it matters (what would be built from it) |
|---|---|---|---|---|
| 1 | D-0411, names question 6: the app features key `ui_title` (a banner text override) | "ok - yes I accept your option A - make sure that the recipe with deployment config with custumization ... work after"; "and doc and recipe specificatio" | The app features key `ui_title {text, subtitle, visible}` is REMOVED; the HOME banner is always the recipe's `info.ui_label`; the old key is refused. The names table (case 4, line 94) shows three viewpoints keeping it as a plain string; only the "User" viewpoint says remove or rename. Option A text not found. | Removes a way to override the banner. A validator refusal and code in HOME would be built. No shipped file sets it (customized_deployments FACTS), so low risk today, but it is a removal she never named. |
| 2 | D-0410 (replaces the key of D-0408), names question 5: the one name key of a recipe | "A - ensure also propagation everywhere - we simplify" | The recipe has ONE name key, `info.ui_label`; there is NO short-name key for a recipe; `info.label`, `info.name`, `info.ui_title` are refused with the new name. Option A text not found. The names table (section 9.2, line 209) offers A "keep `info.label` short", B, C; none says this. | Every recipe file (the shipped ones) would be migrated, the checker changes, BLUEPRINT form changes. This is the core of the recipe format. |
| 3 | D-0411, names question 6: the deployment banner keys | same as row 1 | `branding.banner.title` becomes `ui_label`, `subtitle` becomes `description`; a banner is hidden by an empty `ui_label`; old keys refused. The names table matrix (line 78) says the banner title becomes `ui_title` and `deployment_name` becomes `ui_label`; the ledger line does something else. Option A text not found. | The two customized deployments (demo-vetinst, web-demo) are migrated by script; a proof test is built. A mismatch with the matrix means the key is not what the study proposed. |
| 4 | D-0411 point 4: `deployment_name` | same as row 1 | `deployment_name` is REMOVED; the banner's `ui_label` is the deployment's name. In the names table (case 18, line 108) only the architect offers "delete"; DS and Dev keep it as `ui_label`. | A removal of a key and its reader. |
| 5 | D-0410: "propagation everywhere" | "ensure also propagation everywhere" | The relay's list of what is changed in the same pass includes "ledger and ADR wording" (also UML note, help files, rule files). Her word "propagation everywhere" does not name the ledger. The ledger's own rule says nobody rewrites an existing line. | An agent could be sent to edit ledger lines. Needs your yes or no. |
| 6 | D-0406 (names question 1, option A): the real column name stays reachable wherever a display name is shown; a display text never changes a row | "I think it match your A" (about homogenizing keys and one rule for the recipe spec) | "the real column name stays reachable wherever a display name is shown". This is rule 2 of the data scientist in names table section 7 (line 182), and case 16 (line 106); the table lists it as an open choice (section 9, point 5, line 212) and says the ledger line D-0360 is itself unsettled (section 11, point 3). It is not in the "all four agree" list (lines 49-57). | Decides an open question about how columns are shown in tables, and touches D-0360 (which you said is still your question). |
| 7 | D-0417 point (b): container case, check at start | "...we just need to have paths within the container to allow the binding" | "the app checks at start that each declared place exists and can be used as declared, naming a folder that cannot be written". The deployment table lists the write test at start as choice 11, not answered (line 323; viewpoints differ on shared places). | A start-up check and its error text would be built. Choice 11 is open. D-0418 confirmed only point (a), not (b) or (c). |
| 8 | D-0417 point (c): use cases as a table with a template per use case | same | "The use cases are a table in the specification, kept as the list of options, with a template per use case." (D-0413 says options, not templates.) | Adds content to the specification structure. Moderate. |
| 9 | D-0408: what `info` is | question: "I thought that info was supposed to be used for display of information about the recipe for a user no ? in left panel ? ... Do we need to keep it at all ?"; answer: "A" | "`info` is the free information block shown to the user in HOME's Info panel: every key written is shown; nothing else is required." Option text not found; the review session "changed it after her question" (D-0408's own note). | Defines the contents rule of `info` (every key shown). Checker and Info panel change. |
| 10 | D-0410: longer text of a recipe | "A - ..." | "The longer text of a recipe goes into `info.description`, shown in the Info panel." Not in any table option. | A new place for text; recipes migrated. |
| 11 | D-0408 / D-0410: the check I01 | "A" | "The check I01 ('label required') goes" / "becomes the check for `info.ui_label`". The refusal of old keys is in the names table (line 53); the changed check is not. | A checker rule is rewritten. |
| 12 | D-0429 point 3: no automatic copy | "...if there is a common saved place then it should be the system administrator that should allow for a shared folder" | "the app never copies from a user place to a shared place by itself". The deployment table (choice 7, line 280) has this only as a developer option (one copy function refuses user-to-shared unless chosen on screen); you did not pick it. | A refusal rule in the code (copy function). |
| 13 | D-0429 point 4: static page on Posit Connect | "...a user would log in connect and then can see what the app display (cannot save)" | "the control is absent, not greyed." She said "cannot save"; the choice between absent and greyed is the relay's. | A UI rule: no save control is mounted. |
| 14 | D-0423, audit folder name, option A | "A - and it needs to be explained in the documentation and help" | "A plain text file inside [the audit folder] says not to edit these files outside the app and to export from the app instead." Option text not found (the folder `audit/` itself was your D-0319 "I think audit/ good"). | A file is created in every audit folder. |
| 15 | D-0423 | same | "The same warning is on screen where the audit is shown." | A message on the screen. |
| 16 | D-0398, Chart type axis: several values per example | "I agree with your suggestion - and agree with 2." (option 2 text not found; the Gallery table Q2 has options A to C, line 44) | "several values allowed per example". | Changes how the index and the filter show an axis. |
| 17 | D-0398: where the author writes it | same | "written by the author in the recipe's taxonomy mapping". You said "add the axis to the existing recipes". | A recipe format change. |
| 18 | D-0398: format version | same | "the format version is unchanged". | A decision about the recipe format number. |
| 19 | D-0402, tags | "B - yes - have the agents that verify the recipes verify those tags and compare the tag with the recipe and the data ..." | "The tags stay typed (not derived)." The Gallery table Q6 (line 48) does not say this. | Decides that the author keeps typing these tags. |
| 20 | D-0400, picture is current | "3 - yes good ide - contain the plotnine version so an upgrade triggers redraw. ok we keep png fo now..." | "no pixel comparison (option B dropped); no drawing at runtime (option C not chosen)". Gallery table Q4 (line 46): architect and scientist recommend "A plus B" (B = a test that redraws all 34 and compares). You did not mention B. | The test that redraws and compares is not built. |
| 21 | D-0413: scope of the deployment standard | "And I think we will need to write a deployment standard as we are doing for recipes if its not done so we can track of the options for deployment" | "The app features file gets the same treatment: one document with two parts, or two documents." | Adds a second standard. |
| 22 | D-0413: fields per key | same | "for every key its meaning, purpose, allowed values, default, who sets it, which code reads it, which screen shows it, and the options per deployment use case". | Defines the content of the standard. |
| 23 | D-0431, choice 7 (sensitive data) | "7. Yes but that is a user responsibility if it decided to share not ours so i think our problem is solved." | "choice 7 of the deployment study is closed; no private mark is asked for". The choice also asked what an export may copy and a warning listing each data file (deployment table lines 274-280; code comment "Sensitive-data handling is #46, not built"). | The export warning and task #46 might be dropped by this reading. |
| 24 | D-0425, default test data | "...We need to ensure that the recipe read the test data as a default fallback though ..." | "a test ... shows that the same recipe in a deployment without that place is not silently run on other data: it says in plain words that its default data is not available there." Later settled in part by D-0426 and D-0427. | A named test. |
| 25 | D-0426, no place for the default data | "Well in a deployement without that place then I think the user should select the data then no ? I would select B" | Option B text not found. Added: "the recipe is not refused for that reason, and it never silently runs on other data". | HOME opening behavior. |
| 26 | D-0427 | "Q5 - If that data is absent, the opening should stop with a plain reason. Tell me if you meant something else." | The ledger quotes this as your words. The sentence "Tell me if you meant something else" reads like text written to you. I cannot tell if it is yours or the relay's. | The opening of a recipe stops with a plain reason where the user cannot select data. Please check this one. |
| 27 | D-0424, same recipe name in two places | "yes I agree R1" | R1 text is in the deployment table (line 221) and is the same as the ledger. Added beside it: "when the app saves a recipe it checks the name against every readable place first". In the table this is a "PROPOSAL (architect, developer)" above the options (line 217), not part of R1. | A check at save time. Borderline. |
| 28 | D-0401, content of examples | "A - ensure that both data scientist and user ... are involved in both passes ..." | "A picture changes only after she has seen it." Also: "each verification says what was read or run." Neither in your words. | A review step before any new picture is used. The second is the project's own rule. |
| 29 | D-0411: how deployments are migrated and proved | "make sure that the recipe with deployment config with custumization ... work after" | "the deployment files are migrated by the script, not by hand" and the list of what the test shows (logo, `ui_label`, `description`, stylesheet loaded, contact, banner shows the recipe's `info.ui_label`). Your words: they must work after. | Test content. The script rule follows D-0407 but is not in your words. |
| 30 | D-0397, D-0398, D-0399: order and side points | see the lines | "a clash of two equal names is reported to her"; "the name of the filter says what it is"; "Order: ... the spec text first, then the recipes; same pass as Q1 and Q5"; "no build before her table of Chart type words". | Process and wording rules. Low. |
| 31 | D-0419: what "permanent" means | "no document that is permanent should be left in tmp" | "a document is permanent when a decision rests on it or a task or a ledger line points to it as its source." | Decides which files are moved. Low. |
| 32 | D-0421: studies folder | ".claude/design/studies/ its good because the definitive ones can be moved to .claude/design" | "with a subfolder per study" and "her sentence is the authorization that `rules_runtime_environment.md` section 2 asks for a new folder inside `.claude/`". | A governance claim. Low. |
| 33 | D-0418: where the specification files live | "we need to have this specification in the design - no document that is permanent should be left in tmp ...A yes" | "`.claude/design/`, a deployment specification next to `recipe_format_spec.md`, and its machine-readable keys beside `recipe_spec.yaml` in `libs/utils`." Marked as the relay's reading in the line itself. | File placement. Low. |
| 34 | D-0404, hover or click | "Id go for C (hoover) ..." | "a small visible mark next to the heading". Option C text not found (Gallery table Q7 has one line, line 49). | The shape of the control. Low. |
| 35 | D-0415 / D-0416: named tests | "yes B. 1. yes ... 2. yes off . 3. yes. 4. We need to be data agnostic ..." | "the named case 'resequenced sample'", "not offered for another column" as tests. The behavior is yours; the named tests are the relay's list. | Test list. Low. |
| 36 | D-0408 / D-0411 / D-0412: `info.contact`, `branding.contact`, `branding.theme_css` | answers "A" / "Q7 A" | "stay read by the load gate" / "unchanged". | These keys are kept. Low, probably what you want. |
| 37 | D-0432: Data Import choice 8 (already withdrawn) | "8. B but remember we had also the date rule ... So very unlikely (unless corrections via blueprint)" | The old file kept as a dated copy; a plain confirmation; the uploaded file name recorded. D-0433 withdrew all three. | Listed so you see it was added. Nothing to do. |

How I rated "most consequential": rows 1 to 7 would remove or rename keys or build a check; rows 8 to 13 add rules or content; rows 14 to 26 add behavior or are unclear; rows 27 to 37 are small, process, or already corrected.

**Number of statements in section 1: 37.**

---

## 2. Statements that FOLLOW FROM AN OPTION of a table you were shown

"Her answer" is what she wrote. "Same?" says if the ledger says what the option text says.

| Decision | Her answer | Table and option | The option's own sentence (file and line) | Does the ledger say the same? |
|---|---|---|---|---|
| D-0397 (1), Gallery Q1: the 13 names take the words of the headings | "I think the ui_label should be more like the Heading guidance text ... so I think this is your case B." | Gallery table, Q1 option B (line 43) | "B keep the headings, change the 13 names to the better words" | Yes. Point (2) (rewrite headings as real descriptions) is option C and her words. |
| D-0398 (1), Gallery Q2: the geom filter lists ALL geom and stat layers, derived | "I agree with your suggestion - and agree with 2." | Gallery table, Q2 option B (line 44) | "B derive all geoms and file the example under each (keeps 'derived')" | Yes for "derived, all geoms". The ledger adds "stat layers" (the table line 12 speaks of "geom or stat layer"). "Option 2" itself: text not found. |
| D-0399, Gallery Q3 | "A - But I have a question ..." | Gallery table, Q3 option A (line 45) | "A the recipe spec holds values and meanings, the cheatsheet is generated from it and a test keeps it equal" | Yes. The extraction for documentation and help is her own requirement. |
| D-0400 (1), Gallery Q4: key of recipe, data, plotnine version | "3 - yes good ide - contain the plotnine version ..." | Gallery table, Q4 option A (line 46) | "A a stamp of recipe and data kept with the picture, compared at start, 'picture out of date' shown in the existing notice" | Yes; the plotnine version is yours. See section 1 row 20 for what the ledger drops. |
| D-0401, Gallery Q5: correct three examples first, tags and texts in a second pass | "A - ensure that both data scientist and user ..." | Gallery table, Q5 option A (line 47) | "A correct the three wrong examples now, revise tags and texts in a second pass" | Yes. "All 34 verified" and "both passes" are yours. |
| D-0402, Gallery Q6: three tags are checked | "B - yes - have the agents ... verify those tags and compare the tag with the recipe and the data ..." | Gallery table, Q6 (line 48) (no letters in the table; option B text not found) | "Checkable: the pattern against mapping and column types ..., the sample size against the rows (per group), the number of geoms against the difficulty rule. Author's judgement: family, what it shows, the guidance text" | Yes for the three checkable tags and "family etc. stay the author's". "She confirms the counting rules when proposed" is in the table. Section 1 row 19 for "stay typed". |
| D-0405 (Gallery Q9, option A): `info.label` and `ui_label` may differ | "A : but I need to explain the ui_label is aimed to be short ..." | Gallery table, Q9 (line 51) | "free; an error; an advice" (the coordinator recommends "an advice") | Yes ("free" plus your "control for an author, can be helped from agent"). The ledger writes "an advice at most, not an error". The ledger's later text cites D-0405 for "a too-long name is an advice". D-0405 is about equality of two names, not length. |
| D-0406, names question 1, option A: seven kinds of name | "for info.label this needs to be refactored ... so I think it match your A" | Names table, section 2 (lines 37-57) | "Seven KINDS of name." and "One fallback rule for the whole app ... title, else short name, else the id exactly as written. A description has no fallback ... Never invent text; never use the description as a tab." (lines 37, 50) | Yes for kinds, one fallback function, no invented text, description not a tab. |
| D-0406: one source file, documentation generated | same | Names table, line 54 | "One place writes the kinds, keys and numbers; the documentation is generated from it (the way D-0399 does ...)" | Yes. The file itself is not named in the ledger. |
| D-0406: a blank name is an error, a too-long name is an advice | same | Names table, line 52 | "A name too long is an advice, not an error ... A blank name or one with a line break is an error (DS, Dev)." | The table puts "blank is an error" with two viewpoints (DS, Dev) in the "all four agree" block. The ledger says "all four agreed". |
| D-0407, names question 2: variant P (prefix `ui_` on every display key) | "Q2 - P" | Names table, section 6, variant P (lines 151, 155) | "P: the prefix `ui_` for every display key in every file kind (`ui_label`, `ui_title`...)" and "`description` stays plain in all three" | Yes. "Old keys refused with the new name in one pass per file kind, by a migration script" is in lines 53 and 169. |
| D-0409 (1)(2)(3), names question 4, option B widened: `ui_label` for all, the report uses the name the user saw, fallbacks removed | "so I think we should harmonize and use ui_label for all - including the export ... remove the fall back ..." | Names table, section 4 cases 5, 6, 7, 21 (lines 95, 96, 24, 111) | "give it a reader, or remove it"; "Tab = `ui_label`, else the id"; "the report writes the id in title case ... a name the program invents" | In substance yes. Option B text itself (names question 4) not found. Her sentence says the choice. |
| D-0412, names question 7, option A: key lists for app features and deployment files | "Q7 A" | Names table, case 19 and section 8 (lines 109, 195) | "Arch, Dev: the same key-list check for both file kinds as the recipe has." "A typo is refused with a plain line." | Yes. |
| D-0418: named places with an access word | "A yes (but where is the cache in A ? ...)" | Deployment table, choice 1 option A (lines 186-192) | "A. Named places, each with an access word (sections 2 and 3)" | Yes. |
| D-0422 (1): the audit folder gets no setting of its own | "...as long as it can be saved in session in all deploymenets possibilities and exported in a directory the user can write I think we have our goal done." | Deployment table, choice 2 sentence (line 204) | "The audit folder gets no setting of its own; it stays inside the session folder, in the user's place." | Yes in substance (you did not answer the sentence directly). |
| D-0424: same name, different content | "yes I agree R1" | Deployment table, choice 3 option R1 (line 221) | "R1. Refuse: neither opens, both places named, with a way out ('Rename the one in My recipes, then reload')" and (line 217) "A file order, or a setting 'this place wins', is not offered" | Yes. Section 1 row 27 for the check at save. |
| D-0425 (option A): shipped recipes are not rewritten; the local deployment file declares `assets/test_data/` as a read data place | "...so I would keep A ... our local deployement file ..." | Deployment table, choice 4, first row (line 239) | "Keep the recipes; the development deployments declare `assets/test_data/` as a read data place; a path is accepted if it lies inside a place" | Yes. "The recipe's data path and Data Import reach only inside the named places" is the confinement of line 232 ("All four say no"), which you did not state in those words: you said it is "determined by the configuration of the deployement". |
| D-0429 (1)(2), choice 6: no `users:` word; one copy per person; variables | "i think the saved should only be user associated ... using variables is solution but i do not see what adding several would allow" | Deployment table, choice 6 (lines 262-268) | "Scientist: no such key; a private mark ... means 'private to whoever runs this copy'" | Yes in substance for "no `users:` word". The table's first option (`users: one` or `several`) is not chosen. |
| D-0433 (what stands of D-0432): Data Import never writes into a read-only place | "8 ... this will not happen i think - i think you are making new rules here or i misunderstood you" | Deployment table, access words (line 98) | "`access: read` = the app never writes there." | Yes, as a result of the named places you accepted (D-0418). The text of option B (choice 8) was not found in the table; its rows are not lettered (lines 288-291). |

---

## 3. Lines entirely in your own words (nothing to confirm)

- D-0403: tag mismatch is an advice; you want to see the advice table after the agent review.
- D-0414 (decision field only): the dialog lets you tick all the tables that get the step. (Its points (1) to (3) were the relay's reading and were replaced by D-0415.)
- D-0415 parts A and B: the lineage of where the step was started, all ticked; a separate "remove from all the data" with a warning, only for an ID or a column found in all tables.
- D-0416: the four answers (reaches every table that holds the key column; off by default; list shown before confirming; warning "This removes your selection from any data that holds it"). Row 35 above names only the test list as added.
- D-0419: "no document that is permanent should be left in tmp" (the rule sentence; its definition is row 31).
- D-0421: studies live in `.claude/design/studies/`; definitive ones can be moved to `.claude/design/`.
- D-0422: the audit is saved in the session and exported to a directory the user can write; it is a copy of the original and not written in the consortium place; a structure keeps it apart; the user must know that opening the files outside the app can break the work.
- D-0428: an order for a study (static deployments with several data files; pipeline needing an app-only place); nothing decided. The relay's list of questions is the study's work, not a decision.
- D-0430: choice 6 is enough for now; a warning in the documentation.
- D-0433: the correction itself (the dated copy was not your rule; the date rule of recipe files).
- D-0397 (2)(3)(4): headings as real descriptions by the data scientist and user viewpoints; concordant, not identical; one line in the list.
- D-0401 (1)(3): data scientist, user and statistician in both passes; all 34 recipes verified.
- D-0413: the order for a deployment standard (the additions are rows 21 and 22).

---

## 4. Open points that the ledger still marks "NOT decided" (they are correctly open)

| Line | Still open |
|---|---|
| D-0397 | The wording of names and headings (you read it). No check of "concordant". |
| D-0398 | The list of Chart type words and the value for each of the 34 examples; the filter wording; how the index and filter show several values; the effect on the checker. |
| D-0399 | Which documentation form; whether one generator makes cheatsheet, documentation and help; the test that generated files are current. |
| D-0400 | Which changes need a redraw; whether fonts belong to the deployment or the image. |
| D-0401 | Whether pass 1 is now or merged into the later pass (left to the coordinator, with a reason). |
| D-0402 | The three counting rules and the new pattern values (proposed to you first). |
| D-0404 | How a novice finds the mark and touch screens; two studies ordered (help beside the screen; taxonomy review). |
| D-0405 | One table of the purpose of each name field; whether `ui_label` must be shown in the UI. |
| D-0406 to D-0412 | Screen words; the registries; the format version; old sessions; the migration order; what the Gallery generator writes in `info` (Gallery Q8); the BLUEPRINT info form. D-0409's open point was answered by D-0410; D-0410's by D-0411; D-0411's by D-0412. |
| D-0413, D-0417, D-0418 | The structure table of the deployment standard; where the cache lives among the named places. |
| D-0415, D-0416 | Tables offered for the other filters; whether "remove from all" reaches a source table that no recipe table reads (only if the build meets it); exact warning wording (provisional). |
| D-0420, D-0421 | Subfolder names; what happens to a study after its decision. |
| D-0422 | What a deployment with no writable user place does (deployment table choice 5, not decided). |
| D-0424 | Whether the app offers "rename my copy"; the same rule for data tables. |
| D-0425 to D-0427 | D-0426 and D-0427 answer the open point of D-0425 and D-0426. Open in the line: none, but see section 1 row 26. |
| D-0428 | The whole study (choice 5, "fetched", app-owned place). |
| D-0429, D-0430 | Closed for now (documentation warning). |
| D-0432, D-0433 | Choice 8 is open again: what happens when an upload has the name of an existing data file (confirmation, kept copy, refusal); whether the date rule also covers data file names. |
| Deployment choices not yet asked | 5 (nothing writable), 9 (imports), 10 (order of change), 11 (access words and start test), 12 (PyPI), 13 (when a list is read again), 14 (fonts). |

---

## 5. Not verified

- I cannot see what the relay actually showed you on screen. I only read the files. The options named "A", "B", "option 2", "C", "R1", "Q5" were often written only in the relay's messages. The channel today keeps only the coordinator's outbound blocks; the review session's inbound blocks were deleted after reading. So "option text not found" means: not in the tables I could open.
- I did not compare the "her words" fields with the transcript of the review session (cd1b0ac7). I took them as written in the ledger (ninth field).
- D-0427: I cannot tell if the sentence in the evidence field is yours.
- I did not read the Q1 and Q2 draft files after the decision as sources of options (they were written after your answers).
- For D-0397 to D-0399 I used the Gallery table of 2026-11-20; the relay may have shown newer text.
- The names table section 9.2 options (A keep `info.label` short; B; C) are described there in one line each; the full recipe table `tmpAI/panel/name_fields/TABLE_FOR_THE_OWNER.md` was not opened.

## 6. Added after this table was written (2026-11-21)

Choice 8 of the deployment study (Data Import replacing a file) was decided by you after the correction: ledger D-0434. It was recorded under the new rule: your words as the decision; the review session's option text in a marked bracket; one statement listed as added and not decided (the confirmation does not appear when the name does not exist yet).

Choices 9 and 10 of the deployment study were recorded after this table: ledger D-0435 and D-0436, under the same rule (her words as the decision; the review session's restatement or option text in a marked bracket; what its text says beyond the study table listed as not recorded as decided: for D-0436 'one pass per file kind' and 'the specification and the key lists first').

Later lines of today recorded under the same rule: D-0437 to D-0443. Where your answer was one letter (D-0436 'A', D-0443 'A'), the line quotes the study table's own row beside the review session's option text, and says where the two differ. For D-0443 note: the study table letters its font options a to f; its row a is NOT what was recorded; your 'A' is the review session's own option (the table's rows c and d).
