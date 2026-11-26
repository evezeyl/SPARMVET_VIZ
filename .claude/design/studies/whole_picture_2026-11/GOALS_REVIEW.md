# Your goals, and the path to them (2026-11-22, second pass)

> **HISTORICAL, see `.claude/design/home_audit_what_is_true_now.md` (2026-11-26).** This is a study of its day. Where it speaks of tick lines of plots or of a dialog that asks the scope by plot, of "My view", of "the plot's table" or "plot data", or of a build order that the owner has since changed (the step bar, the review before the demo, no plot tabs in Audit mode), the page "what is true now" and the ledger lines D-0638 to D-0667 win; nothing below is edited.

Note 2026-11-24: this file still holds quotations of the owner's words from the study rounds. The decisions are written once, in plain words, in the decision ledger; read `WHOLE_PICTURE.md` first.

A study, not a decision: nothing is built from it before you answer (D-0507, D-0528). The short version is part 0 of `WHOLE_PICTURE.md`. This file holds the detail, for you if you want it, and for the builders. The list of which decisions and builds match the goals is `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)` (same folder).

**How to read it.**
- Your words are between quotation marks, exactly as you typed them, with the ledger number.
- "My reading" and "mine" mark what is not yours. "Suggestion:" comes before a remedy.
- Evidence: [read] = read in the code at file:line on 22 November; [run] = a run of this study or of its reviews, named; [inventory] = taken from `PARTS_TABLES.md (removed 2026-11-24 in the cleaning of the studies; see git history)`, `DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` or the two collected files of the main tree (`.claude/design/studies/whole_picture_2026-11/sources/whole_picture/BUILT_audit_lineage.md`, `BUILT_format_export_names.md`), not re-read; [fact check] = the independent check of the first pass (`.claude/design/studies/whole_picture_2026-11/sources/whole_picture/GOALS_CHECK_facts.md`, main tree).
- The app is data agnostic: "the entity" and "the entity key"; on the demo recipe the entity is a sample and the key is `sample_id`. "Observations" is your word: I read it as the rows of a table (my reading).

**What changed in this second pass, and why.** The first pass proposed that you choose the results and that the app choose the places where a step is written. Your words of the same evening rule that out: "I am monitoring and i already think the reviewer might miss the point the context is so depend for the user that is much choose the scope adapted to its case. We cannot choose for him..the app cannot decide the scope. The reviewer should understand the lineage and the user the effects of its choices" (D-0531). In your earlier words the scope IS the places: "That is the choice of the user - because the user decide the scope - the steps are added at the end of one Tier so the steps applies in the Tier where the steps are added" (D-0355). An independent check also found cases that a choice of results cannot write (section 8). So the path now keeps every place yours, and keeps from the first pass only what serves your choice: the effect on each result, measured before you confirm. Where I still think you may be missing something, I argue it, as you asked: "So if i miss something i want a good argumentation of why and how .." (D-0532). The fixes of the two independent checks are mapped in section 10. A third pass answers the independent review you ordered (D-0533), finding by finding, in section 11.

---

## 1. Your passage (D-0528), whole

> "What i want is to make allow the user to make audits in an clear, scientifically correct , reproducible and transparent way, 7 want to provide a tool the user can use to do good data science and help provide visualisations it can use for publication (incl. Tables an plot) it can trust, and audit is done to allow making small correction to results where some "observations" must be removed. I want to know how to get there, and then our current code needs to be adapted, which implies reviewing decisions or changing strategy that hoder to get there. This includes recipe structure and how we perform the audit steps and how it is presented clearly with the necessary information so the user can make informed and good choices. Our role is to provide the tool, the reproducibility, transparency, reliability - however we cannot take choices for the user because it depends on the user context. I want the whole picture to be reviewed again and adapted to my goals. I want to go how to succeed at making the app to reach my objectives and then i need to know what needs to be modified (from our plans already planned and from current code - eg. What build are ok and what needs to be adjusted)"

---

## 2. The goals

### 2.1 From your passage

The review session read six goals in your passage (its reading, block M592). I checked each against your words: each rests on words of the passage, and none goes beyond them.

| # | The goal, in plain words | The words of your passage it rests on |
|---|---|---|
| G1 | The user can make audits that are clear, scientifically correct, reproducible and transparent. | "allow the user to make audits in an clear, scientifically correct , reproducible and transparent way" |
| G2 | The app is a tool for good data science. | "provide a tool the user can use to do good data science" |
| G3 | It helps make results for publication, plots and tables, that the user can trust. | "help provide visualisations it can use for publication (incl. Tables an plot) it can trust" |
| G4 | The audit is for small corrections: removing some observations from results. | "audit is done to allow making small correction to results where some "observations" must be removed" |
| G5 | Each choice is shown clearly, with the information needed to choose well. | "how it is presented clearly with the necessary information so the user can make informed and good choices" |
| G6 | The app gives the tool, the reproducibility, the transparency and the reliability; it does not choose for the user, because the right choice depends on the user's context. | "Our role is to provide the tool, the reproducibility, transparency, reliability - however we cannot take choices for the user because it depends on the user context"; since then: "We cannot choose for him..the app cannot decide the scope" (D-0531) |

### 2.2 From earlier decisions (big goals only)

| # | The goal | Your words |
|---|---|---|
| E1 | Nothing changes a result silently. | "No silent error that is the rule." (D-0050) |
| E2 | No wrong result because the wrong scope was chosen. | "Sorry do not get wrong results because we did not select the correct scope" (D-0450) |
| E3 | One app for every recipe, data agnostic; every recipe works. | "remember we are data agnostic so sample id is the example" (D-0512); "All recipes need to work" (D-0077) |
| E4 | Two kinds of person: the author of a recipe, and the user, who is often someone else. A well-made recipe lets the user choose correctly. BLUEPRINT is the author's tool. | "well the problem is that the user might not be the author" (D-0500); "I think in this case if a recipe is done correctly you can ensure that the user can do correct choices." (D-0498); "blueprint aim is an ide to build recipes" (D-0495) |
| E5 | The story of the data can be followed, from the original files to a result. | "YES the story of is what I want to show - this is why I wanted the lineages" (D-0508) |
| E6 | A well-built app: one source of truth, no half fixes. | "our role is to diliver an app that is well developped architecture wise" (D-0108); "We aim for one source of truth." (D-0065). "We do not do half fixes." is in the goal text that you approved with "1. ok." (D-0125); who wrote that text is not stated in the line. |
| E7 | The way there: the whole picture first, then the big line fast; the demo with no special treatment. | "I think we should maybe use a good thinking model to have the abiity to see the whole picture on how it should work - and then build" (D-0507); "I would prefer to have the big line done as fast as possible" (D-0521); "no special treatment of files for the demo" (D-0255); "so agreed I will do the demo in 2 weeks" (D-0370) |

### 2.3 Looked for, and not found in your words (not presented as yours)

- "The user spaces are independent": decided by you (D-0008: ADR-093 "ACCEPTED and IMPLEMENTED (Eve, 2026-11-08)"), with no words of yours in the line. Nothing in this design touches it.
- "Keep it simple" as a general rule: your words simplify specific places ("Maybe we should just simplify - all plots included in the export", D-0292; "we simplify", D-0410). The general rule is in `.claude/rules/dasharch.md`, not attributed to you.
- "What the user sees and does is what the export contains": a rule attributed to you with a date (`rules_verification_testing.md` section 9, "added 2026-11-06, Eve"); whether the sentence is your wording is not stated. Used below as a condition of G3.
- The demo: the audience ("colleagues") is not in your quoted words. The length, 30 minutes to one hour, is in the decision text of D-0255, not in the words quoted there.
- HOME's purpose ("publication-ready results", "a recorded reason for every change", `.claude/design/spaces/HOME.md`): an agent's text of 2026-11-12 (commit `89d0828c`), so a reading.

### 2.4 Goals that pull against each other (yours; not resolved here)

1. **Inform of every pitfall, against no warning the user learns to ignore.** "could we detect those cases and inform about the possible got you" (D-0508) / "that would also avoid the load of warnings that the user would just ignore" (D-0501).
2. **The user chooses the scope, against no wrong result from a wrong scope.** "That is the choice of the user - because the user decide the scope" (D-0355); "yes the user may unthink he is responsible of its choice" (D-0499) / "Sorry do not get wrong results because we did not select the correct scope" (D-0450). The path of section 4 keeps the first and serves the second by showing the measured effect of a choice before it is confirmed.
3. **One definition for each table, before its use, against a story that can be navigated.** "Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before" (D-0516) / "I am just wondering of how to make it navigate" (D-0518).
4. **The big line fast, against studying in detail.** "I would prefer to have the big line done as fast as possible" (D-0521) / "study in details in others when necessary - implementation time is not really an important factor as we can delay implementation" (D-0268).
5. **Everything needed to redo the analysis, against not cluttering.** "if you need to redo the analysis then you will need to re-upload the recipe" (D-0389) / "The original recipe can be added for baseline BUT it need to be clear for the user which one is which one ... (and maybe not cluter what the user has access to )" (D-0324).
6. **One app for every recipe, against guarantees that need a well-made recipe.** "All recipes need to work" (D-0077) / "if a recipe is done correctly you can ensure that the user can do correct choices" (D-0498). You named it yourself: "I am afraid there is no perfect solution and that we must adopt a tradeoff here." (D-0500).

Not a tension (corrected from the first pass): the user learning where a change is applied. You accept it: "the user will have to learn that its not the sample that stays but where the change is applied that is a big difference - so the user will have to learn a bit of datascience but thanks for the warning so I will pass it to my users." (D-0508). The help and the dialog teach it (4.9).

---

## 3. Built backwards: what must be true for each goal

For each goal: the conditions that must be true, whether the design as decided makes them true, and whether the app on `dev` does. "Decided" = the earlier study's design, from your decisions. Marks: **yes**, **partly**, **no**.

**G1. Audits that are clear, correct, reproducible and transparent.**
1. Each correction is written once, in a copy of the recipe, with its reason; the original never changes. Decided: **yes** (D-0102, D-0143, D-0332). Today: **no**: one step lives in three forms (`DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` A11).
2. Before confirming, the user sees what the correction does to each result. Decided: **partly**: the rows at each place, and "table changed" and "picture changed" per plot (D-0316, D-0318); the count at the plot was removed (D-0501). Today: **no**.
3. What is shown is true. Decided: **partly**. Two reviews wrote sentences about tables where no step is written; each kind was false somewhere [run, `.claude/design/studies/whole_picture_2026-11/sources/whole_picture/EVIDENCE_untick_branch_reviews.md`, main tree]. Only a run of the audit recipe tells the effect at a result.
4. The step sits where the user intends. Decided: **yes**, the user ticks the places (D-0093, D-0355, D-0531). With the default read as "tier 1 of each original table", three runs on the demo, one entity each, with places listed by hand, left the entity in 7 plots: in 4 because their tables never meet MLST or the metadata, and in 3 with its metadata emptied (source and country; in one also the year) [run, `DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` C1]. The default is question 1. Today: **no** (tier 3 of one plot only).
5. Anyone can re-run it and get the same result. Decided: **yes** (two parts, D-0490, D-0492; the record, D-0333). Today: **no** (A17).

**G2. A tool for good data science.**
1. Removing an observation before a step that computes over all observations (a mean, a z-score, a count per group) is possible, and the user sees its consequence. Decided: **partly**: possible by ticking an earlier place; a note at one place is question 8. Today: **no** (always after everything). Measured [run: the independent review's script, rerun by me]: removing an entity after the z-score of `QA_population_zscore` and removing it before give different z-scores for all 41 other entities (largest difference 0.064).
2. Each table has one definition. Decided: **open** (form 3, question 2).

**G3. Results for publication, plots and tables, that the user can trust.** (Place 1 of the six, D-0529.)
1. A table can be a result. Decided: **yes** (D-0485). Today: **no**.
2. What the screen shows is what the export holds. Today: **yes** for the result and the audited steps of today; the export refuses when the files changed since the view (X1, X11) [inventory]. **No** for the original pictures beside the audited ones (D-0147, not built). **No** for the data files: `T1_data.tsv` and `T2_data.tsv` are written from the original tables (`app/handlers/export_handlers.py:1405-1409, 1428-1431`); only `T3_data_<plot>.tsv` is audited (`:1463-1467`); a reader who takes the T2 file publishes an observation that was removed [read; found by the independent review]. The import never checks the audit steps ("not_checked", `app/modules/bundle_importer.py:186-194`) [read].
3. A plot and its table are the same data. Today: **yes**: one reader, `materialize_tier3`, serves HOME's plot, its table, the export and the pictures (`.claude/rules/rules_data_engine.md` section 1) [inventory].
4. The same recipe and data give the same picture. Today: **yes** (ADR-090; the seed fixed at 0: "Fixed 0 by default fixed and simple", D-0056, built `653e70b1`). One exception, the Reshuffle: today the export carries a new seed by writing it into the plot's layers of the recipe copy it exports (`app/modules/plot_seeds.py:156`, called at `app/handlers/export_handlers.py:1567`) [read]. The audit recipe you decided keeps the author's parts untouched (D-0332) and must equal the original once its audit steps are taken out (D-0040), so it cannot hold the seed there. The seed is also recorded in `effective_run.yaml` (`export_handlers.py:1675-1677`), but no code reads it back at a re-run or an import [read: search].
5. A picture is current. Gallery: **yes**, the picture key (D-0400, built). HOME stores no picture; each is drawn from keyed tables (D-0335) [inventory].
6. A reader sees the original and the corrected result, and how many observations were removed from each. Decided: **partly**: both pictures (D-0147; where: question 16); the count per result was removed (D-0501). Today: **no**.

**G4. The audit is for small corrections by removal of observations.**
1. The audit removes observations: one entity, or the rows that meet a condition. Decided: **yes** (D-0322: filters and removals by key).
2. The audit does nothing else. Decided: **no** (my reading): the Reshuffle (D-0341) is in it. Column drops (D-0322) are in it too; my first reading counted them out, and after the independent review I no longer do (section 11 e). Today: also the code of a plot-style change that no screen reaches (`app/handlers/audit_stack.py:815-845`; the panel's comment at `app/handlers/home_theater.py:2340-2344`) [read; fact check].

**G5. Each choice shown clearly, with the information needed.**
1. The lineage is shown as a propagation, so that the user sees what each place reaches: "so maybe lineage should be represented as a propagation eg. original -> T1 -> T2 so the user sees that it affect the next one" (D-0508). Decided: **yes** (D-0508, D-0346). Today: **no**.
2. The effect of the choice on what the user publishes is shown, true, before confirming. Decided: **partly** (G1 point 2).
3. Only what changes the choice is shown: no per-table warnings about downstream effects (D-0501). Decided: **yes**.
4. Words for a user who is not a developer. Decided: **open** (question 19).

**G6. The tool, not the choice.**
1. The scope is the user's at every place. Decided: **yes** (D-0093, D-0355, D-0531).
2. Any default is named as a default, with its reason, and can be changed. Decided: **partly**: "tick low" (D-0508) is a default; which places are "the earliest" is open (question 1).
3. The only automatic placement is "remove from all the data", when asked (D-0022, the ledger's record; D-0416). Decided: **yes**.

**E1 and E2. Nothing silent; no wrong result from a wrong scope.**
1. The app says nothing it cannot prove, and measures what it cannot read. Decided: **partly** (the notes "where the app can").
2. The consequence of the chosen scope is visible before the user confirms. Decided: **partly**: at the place; not at the results.

**E3. Every recipe.** A measured effect works on any recipe; a rule read from the recipe works only where the rule holds. Decided: **partly**.

**E4. The author and the user.** The author is helped to make a well-made recipe (key declared; one column name for one meaning), and BLUEPRINT never damages one. Decided: **yes** (D-0495, D-0498, D-0500). Today: **no**: BLUEPRINT drops parameters on Apply and loses comments on Save (`.claude/design/studies/scratch_records_2026-11/coordinator/blueprint_verify/REPORT.md` section 2, main tree) [inventory].

**E5. The story.** Any table and its stages can be looked at. Decided: **yes** (D-0457, D-0508). Today: **no** (V2, V3 of `PARTS_TABLES.md (removed 2026-11-24 in the cleaning of the studies; see git history)`).

**E6. Well built.** One representation of an audit step; no old code taken up again. Decided: **yes**. Today: **no** (A11, A12, A21).

**What this shows (my reading).** The scope is yours in the decided design, and it stays yours. The conditions that fail meet in one place: the consequence of a choice is read from the recipe, at the place, and not measured at the results. Section 4 keeps your design and adds the measurement.

---

## 4. How to succeed: the path

### 4.1 The principle (mine, after D-0531)

- **The scope is yours:** the places where a step is written. The app does not choose them.
- **The app informs:** it shows the lineage as a propagation, what each place reaches, and the effect of your ticks on each result, measured before you confirm.
- **Defaults are named:** a default tick is a starting point, shown as such, with its reason; you change it.
- **One automatic placement:** "remove from all the data", only when you ask (D-0022, D-0416).

Why the measurement (argued, D-0532): the effect at a place does not tell the effect at the results. A left join keeps the row of its first table, so a removal at the second table leaves the row further down, with emptied columns [run]. A sentence read from the recipe about a table where no step is written was false somewhere for each kind of sentence [run, two reviews]. A user learns the effects of her choices (D-0531) only from effects that are true.

### 4.2 The path, step by step, on the demo recipe `1_test_data_ST22_dummy`

Before: the author writes the recipe. It declares the entity key and joins the metadata in tier 1 (the recipe check already refuses a join anywhere else, ST05). What the author must do, and how BLUEPRINT helps: 4.7 and 4.8.

1. **Open.** The app builds every table and draws every result once; a recipe that cannot be built is refused with a plain reason. [built]
2. **Look (Exploration).** A result (the plot `mlst_bar`), the table it is made from, its earlier stages ("Table to view"), and any other table by its name, also one that no result reads (D-0457). A filter changes only what you look at; nothing is saved or exported. [built, except "any table by name"; the filters kept per table are on a branch in review]
3. **Find.** In the table of `mlst_bar` you see the entity `10668076`; your lab notes say its sequencing failed.
4. **Ask (Audit mode).** From the table where you see it, you ask to remove the observations: the whole entity, or the rows that meet a condition. You write the reason. [the reason gate is built]
5. **See the lineage and tick the places.** The dialog shows the lineage of that table as a propagation, from the original files to the results: one line per place, with its reach (D-0346). The earliest places start ticked: your default, named on screen (D-0508); which places are "the earliest" is question 1. Tables that no result reads are lines too (D-0451). "Remove from all the data" is a separate option, off (D-0416).
6. **See the measured effect.** Under the lines, for each result: "n observations removed" or "unchanged". Only where it happens: "still found here" (for example a row kept by a left join, or a key written differently) or "the values of other observations change here" (a step that computes over all observations lies between the place and the result). Each change of a tick is measured again.
7. **Confirm.** The step is written at the places you ticked, in the audit recipe, with its reason (`audit_comment`, D-0329). The audit log keeps the places, ticked by default or by you, the effects you were shown, who and when (D-0478). Only the tables that changed are built again (D-0325).
8. **Check.** You see the audited results; Compare shows the original and the audited one side by side, with the counts (D-0147, D-0489 layer 1). You can take any one step out again ("Remove step", D-0314).
9. **Keep.** Your session keeps the audit recipe, its record (a fingerprint) and the log in `audit/` (D-0319, D-0423). A hand-edited audit recipe, or a session whose original recipe was edited since, is refused at reopening with a plain line (D-0331, D-0362).
10. **Export.** Two ticks, Publication and Reproducibility (D-0298). Publication: the audited results and, for each changed result, the original beside it; the report, results first (D-0491), with one methods line per step, saying from which results how many observations were removed, and why; the audit log. Reproducibility: the data once; an original part with the original recipe; an audited part with the audit recipe, its record and the log; a README that says which is which (D-0490, D-0492; the folder names are not final). Exploration is never exported (D-0327).
11. **Re-run.** A reader runs either part and gets the same tables and pictures; the record shows that the audit recipe was not edited by hand.

The choices that are yours, in the order they meet the path: question 28 (start from places, from results, or as decided without the measured effect); question 1 (the default ticks); question 29 (column drops); question 17 (the Reshuffle); question 4 (the default for a filter on another column); question 2 (the recipe form, for table results); question 26 (old sessions); question 15 (the original recipe in the Publication part). Their full text is in part 8 of `WHOLE_PICTURE.md`.

### 4.3 Who chooses what

| The choice | Whose | Default | Why |
|---|---|---|---|
| Which observations (an entity, or a condition) | the user | none | her context |
| The reason | the user | none; required | a correction without a reason is not transparent (built gate) |
| The places where the step is written (the scope) | the user | the earliest places, ticked and named as your default (D-0508; question 1) | "the app cannot decide the scope" (D-0531) |
| Before or after a step that computes over all observations | the user, by ticking a place before or after it | as the default ticks; the effect line shows it | it changes the values of other observations |
| Keep the entity in some results (your case: "he wants to show the poor quality sample for the quality results but remove the bad sample from all other results", D-0499) | the user | untick the places that feed those results; the effects show when it is right | her context |
| "Remove from all the data" | the user | off ("2. yes off", D-0416) | an explicit act |
| The table shown when a recipe opens | the app | the result's table (as built; question 18, my reading (a)) | the table under a figure is the one it is drawn from |
| What the export holds | the user: Publication, Reproducibility | the audit log and the record are always in a bundle of an audit (D-0478, D-0333) | her context; the log is not optional by your decision |

### 4.4 The measured effect (rules for the builders; mine)

- **What is measured.** Before Confirm, the engine builds the audit recipe with the ticked places (`app/modules/audit_run.py`, called by tests only today; the same build that "picture changed" of D-0318 already needs), and compares each result with the original (`libs/utils/src/utils/table_compare.py`, layers 1 and 3, called by tests only today).
- **What is shown, per result:** "n observations removed" or "unchanged". Two signals, only where they occur: "still found here: n" when the observations asked for are still in the result (a row kept by a left join; a key written differently); "the values of other observations change here" when rows of other entities differ (a step that computes over all observations lies between the place and the result; layer 3 pairs the rows by a key the result holds).
- **Where a result has no key column** (for example a count per group), the line says "n rows before, m after" and that the entity cannot be seen in it.
- **Nothing is refused and nothing is moved.** The app never changes a tick and never writes at a place you did not tick. A result that changes although you did not mean it to is shown; you decide.
- **The place lines** come from the walk of the lineage (`libs/utils/src/utils/lineage_walk.py`, `walk()`, called by tests only today), with its notes (`recomputed_here`, `aggregated_here`, `another_type_here`) on the line where they apply, and the red lines where the app cannot follow a column YET (D-0460, D-0454).
- **Evidence on the demo** [run, three entities, places listed by hand, `DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` C1]: with the default read as tier 1 of each original table, the measured effect would show the 3 quality plots "still found", with emptied metadata; with the end of tier 1 of each table that joins the metadata ticked, nothing is emptied. Your case of D-0499 with "remove from all the data" as built (27 places) [run, mine, section 11 a]: with `QC_Reads_Anchor` and `Quast_with_metadata` unticked, all 17 plots change and the entity is in none; with `FastP`, `Quast`, `Bracken` and `metadata_schema` also unticked (six places in all), the entity stays in exactly the 3 quality plots, with its metadata, and 14 plots change. The dialog itself is not built and was not run.

### 4.5 What a scientist needs to defend the result to a reviewer (mine, from G1, G3, G4)

1. For each correction: which observations, from which results, why, by whom, when.
2. For each result: the original and the corrected version, and how many observations were removed.
3. Proof that nothing else changed: the audit recipe differs from the original only by its audit steps (the record's fingerprint; D-0040, D-0333).
4. A way to re-run both (D-0490, D-0492).
5. Where a removal comes before a step that computes over all observations: that choice, with its reason.

For the user's choice (not for the defence), the lineage shown as a propagation and the reach of each place are needed (D-0508, D-0346): they are how the user sees what a place reaches. The comparison layers 2 and 3 serve checking, on request (D-0489).

### 4.6 The recipe structure, seen from the goals

- **The stages** T1, T2, T3: keep (built; D-0179, D-0343).
- **A result is a plot or a table** (G3; D-0485): needed.
- **Derived tables made with `from:`** (form 3, question 2): they serve G2 and G3: one definition per table, so a plot and a table of the same summary show the same numbers by construction. One level for now (option a1 of question 2). A derived table adds places to the lineage (its tier 1, and its tier 2 while the key exists there); the dialog shows them like any other place.
- **The three blocks** (D-0513) and **the metadata join in tier 1** (D-0510, D-0523; built, ST05): keep. With the metadata joined in tier 1, the end of tier 1 of a joined table is a place where a removal by the entity key leaves with its metadata.
- **Every join in tier 1** (ST05; not a line of yours): keep for now. Question 27 matters only when a recipe needs a look-up join after a count; the demo needs neither option.
- **Is the form as simple as the goals allow?** For small corrections, the author writes nothing for the audit; the audit writes its own steps. For publication results, a result names one table. One complication stays and must be documented: a join reads its tables after their tier 1, `from:` reads its table at its last stage; making joins read tier 2 would change results silently on the demo (the proposal's flag 3, `RECIPE_REDESIGN_REVIEW.md (removed 2026-11-24 in the cleaning of the studies; see git history)` 5.3).

### 4.7 The two kinds of person (place 2 of D-0529)

**The author** writes the recipe (in BLUEPRINT or by hand): the structure, the entity key, the metadata join, the derived tables, the results.
- Inform, never choose: the recipe check refuses only what cannot run or would be wrong (ST05, the strict import) and advises the rest. Advices this path needs (mine): declare the entity key where a column is used as a join key ("the key declaration is a good practice (and we need to ensure that blueprint encourages it)", D-0500); "do not use same column names for different meanings - declare what is ID key" (D-0498); a look-up table with an entity key (question 22).
- Clear information: the check's messages with code, plain sentence and fix (built); the columns that exist at each stage (BLUEPRINT part F, not built); the lineage.
- What the author must never lose: a production-ready recipe, and the comments in it (D-0495).

**The user**, a colleague who may not be the author ("well the problem is that the user might not be the author", D-0500), looks, decides what to remove, ticks the places, and gives the reason.
- Inform, never choose: the app never chooses the observations or the places; it shows the lineage, the reach and the measured effects.
- Clear information: the effects on the results she publishes, measured; only the signals that change her choice.
- The user cannot repair the recipe in HOME (D-0102). When the recipe makes a correct correction impossible (no declared key; a key rewritten), the measured effect shows it ("still found here"). Suggestion: the dialog then names the recipe's contact, as the load gate does (`info.contact`, ADR-094) (mine).

### 4.8 BLUEPRINT and the author (place 3 of D-0529)

- The seven-point check found that BLUEPRINT can damage a recipe silently today: Apply drops a parameter the form does not show; a number becomes text; Save writes with no check and loses the comments; the preview drops a failing step (`.claude/design/studies/scratch_records_2026-11/coordinator/blueprint_verify/REPORT.md` section 2, items 1 to 4, main tree) [inventory]. A recipe damaged by its author gives wrong results to every user: this goes against G1 and E4 before any audit.
- The coordinator's build plan already moves "a save keeps the comments" and "Save never replaces a recipe by mistake" into its slice 1, after your D-0495 (`BUILD_PLAN.md` of the same folder) [inventory].
- What the goals add (mine): the advice to declare the entity key (BUILD_PLAN item 5; D-0500); the advice from your words of D-0498; one lineage function shared with HOME's dialog (D-0065; `DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` A10).
- When: you put BLUEPRINT after HOME and the Gallery ("we do changes to blueprint and lab after - we focus on home and gallery", D-0271). It is not needed for the demo of HOME and the Gallery; its safety slice is needed before anyone writes recipes with it.

### 4.9 Documentation and help, part of the tool (place 4 of D-0529)

**On screen, short, at the moment of the choice:** the lineage as a propagation; the reach of each place; your default named as a default; the measured effect on each result; "still found here" and "the values of other observations change here" only where they occur; in Audit mode, one plain line saying not to edit the audit files outside the app (the screen text of the option of D-0423, not your words).

**On the good-practice page and in the user guide** ("1. Our limits will need to be clearly documented..", D-0461; "A - and it needs to be explained in the documentation and help", D-0423; "I am afraid that too much explanation in the ui will be too much information - and Id rather the user be able to use the help", D-0404):
- why the place of a removal matters, with your sentence: "the user will have to learn that its not the sample that stays but where the change is applied that is a big difference - so the user will have to learn a bit of datascience but thanks for the warning so I will pass it to my users." (D-0508): the left join, and the steps that compute over all observations;
- the three gotchas: a key recomputed, a key under another column name with no join, a key rewritten by a step (D-0508), and how the measured effect shows them ("still found here");
- your recipe rule: "do not use same column names for different meanings - declare what is ID key" (D-0498); import only the columns needed (D-0462);
- the joins the app cannot follow YET (D-0486);
- the two reading rules of form 3 (4.6);
- the audit folder and why it must not be edited by hand (D-0423);
- what Exploration does and does not do (nothing saved, never exported, D-0327).

Today: the page does not exist (`PARTS_TABLES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` I5); screen texts state old limits (A7) and say "samples" (A8).

### 4.10 Where it runs (place 5 of D-0529)

- The audit exists only where the app features turn it on (`t3_sandbox_enabled`: the advanced, standalone, developer and qa files), and it requires sessions and export (D-0018; refused at start otherwise) [`rules_app_features_flags.md`]. The static, simple, web-demo and demo-vetinst files have no audit; the static one keeps no session (reasoned from the flag table). The export, where it is on, is a browser download and needs no writable place [`ui_implementation_contract.md` 7.2].
- The audit recipe lives in the session folder, in the user's own place (`audit/`; D-0319, D-0340, D-0423). Your words: "as long as it can be saved in session in all deploymenets possibilities and exported in a directory the user can write I think we have our goal done." (D-0422).
- A container with bound paths: the user's place (`user_data` of the deployment) is a bound folder. Writable: sessions are kept. Read-only: as below (reasoned).
- **No writable place, audit on.** Today the audit is applied in memory and, at Apply, a technical warning says "T3 ghost save failed ... T3 state was applied in-memory but will not survive a page refresh." (`app/handlers/audit_stack.py:1049-1058`) [read]. The ledger's reading of your answer of D-0340 (not your words) is "a plain error when the directory cannot be written"; your words were "we need to ensure it can be read write for the directory the user has access which is defined in the config deployment". Suggestion: when Audit mode opens, the app tests the user's place once; if it cannot write, it says before any work: "This app cannot keep your audit after you close it. Export it before you close." (wording mine). The audit still works, and the export holds the audit recipe, its record and its log, built from the copy in memory: reproducibility holds through the export.

### 4.11 How we will know each goal is reached, and the December demo (place 6 of D-0529)

**Checks you can do yourself on the demo** (the result on screen or in the export, not that code exists):
- **G1, E2.** In Audit mode on `mlst_bar`, ask to remove `10668076` with a reason. Before confirming, the dialog shows the lineage with your default ticked, and for each result "n observations removed", "unchanged" or "still found here". After Apply, open three results and see that the effect shown was true.
- **Your case of D-0499.** With "remove from all the data", untick the six places that feed the 3 quality results (on the demo: `QC_Reads_Anchor`, `Quast_with_metadata`, `FastP`, `Quast`, `Bracken`, `metadata_schema`). The effects show those 3 "unchanged" and the 14 others changed [run, mine]. After Apply, in `qc_reads_horizontal_barplot` the entity is still there WITH its source, year and country; in `mlst_bar` it is gone.
- **G1, reproducible.** Export with both ticks; the README says which part is the original and which the audited; import each part and see the same plots; change one byte of the audit recipe and see the import refuse it.
- **G2.** Tick a place before the z-score of `QA_population_zscore`: the effect line says the values of other observations change; tick a place after it: it says they do not.
- **G3.** The Publication part holds, for each changed result, the original and the corrected picture; the report's methods line gives the count removed and the reason. After question 2: a table result is exported under its name and equals the table on screen.
- **G4.** The audit offers removals of observations, column drops if you keep them (question 29), and no Reshuffle if question 17 is (c).
- **G5.** A colleague who did not write the recipe does the first check without help, and says what each line of the dialog means.
- **G6.** No tick is set that you did not set or that is not named as your default; the app never moves a tick.
- **E1.** On a small test recipe where a step writes the key in lower case: the effect line shows "still found here".
- **E3.** The same checks on a second shipped recipe.
- **E4.** In BLUEPRINT, open the demo recipe, change nothing, Save: the file is byte-identical, comments kept.
- **E5.** Open `FastP_with_metadata` (no result reads it) in the data preview.
- **E6.** The audit recipe in the session's `audit/` folder and the one in the export are the same file (same fingerprint).

**The December demo.** You agreed on 20 November: "so agreed I will do the demo in 2 weeks" (D-0370); the date follows readiness: "I do not present at the end of the week: we agree on when I can present" (D-0255); no special treatment of files (D-0255). What is in it is your choice. Proposal (mine), from the goals and the route of part 0.4:
- **In:** steps 1 to 7 of the route: the records agree; filters follow the table; any table opened (after question 13); one form of an audit step; the dialog of places with the measured effect; the export of an audit; the report by groups. The Gallery as it stands. A short help page with the points of 4.9.
- **After:** tables as results and the recipe form (question 2; the one move); the picker for the story; BLUEPRINT's rebuild; the full good-practice page.
- If the dialog is not ready by the date, the demo shows the audit as built (one plot at a time, at its own table) and says what comes; that choice is yours.

---

## 5. What must be modified

Each item: **keep**, **change** (to what), **drop**, **later**, **not sure**; the goal that asks for it; and the question it depends on. This is my reading; you may object to any line. `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)` gives the same verdicts as two tables, decisions and builds.

### 5.1 From your plans

**Decisions of the ledger.**

| Decisions | Verdict | What, and why |
|---|---|---|
| D-0102, D-0143, D-0332, D-0329, D-0321, D-0339, D-0040: the audit recipe, a copy; the author's steps untouched; `audit_steps`, `audit_comment`, the id, `audit_of` | keep | the one representation of a correction (G1, E6) |
| D-0333, D-0331, D-0319, D-0340, D-0422, D-0423: the record, the fingerprint, the `audit/` folder in the user's place | keep the record and the fingerprint; not sure for a deployment where the user's place cannot be written | G1, G3; question 30 |
| D-0478: the log always exported, with what was shown | keep | it holds the places ticked and how (default or by you) and the effects shown (my reading of questions 10, 11, 12, 25) |
| D-0490, D-0492, D-0389, D-0298, D-0301: the export's two ticks and two parts | keep | G1, G3 |
| D-0147: original and corrected both visible | keep; both pictures in the Publication part (my reading of question 16) | G3 |
| D-0314, D-0362, D-0312, D-0317: Remove step; sessions refused | keep | G1 |
| D-0093, D-0355, D-0053, D-0022, D-0531: the user chooses the places; nothing written that is not ticked; one automatic placement | keep | G6 |
| D-0316, D-0346, D-0347, D-0194, D-0359, D-0415 A, D-0451: the dialog of place lines with reach; tables no result reads are lines | keep | G5, G6 |
| D-0508: "tick low", the lineage as a propagation | keep; which places are "the earliest" is question 1 | G5, G6 |
| D-0508, "Id rather the check is more where you apply it" | change in part: the check at the place stays; the effect at each result is added, measured | G1, E1 (argued in section 6); question 28 |
| D-0501: no per-table warnings downstream; the count at the plot removed | not sure, both parts: the measured effect of question 28 (a) and (b) is shown per result, downstream of the step; whether that is a "per table warning" is yours (the independent review) | G3, E1; question 28 |
| D-0318: "table changed" and "picture changed" | keep, extended with counts | G1, G3; question 28 |
| D-0485, D-0487, D-0489: a table as a result; the comparison in layers | keep | G3 |
| D-0491, D-0484: the report by groups | keep; add the count removed per result to the methods line | G3 |
| D-0510, D-0523, D-0513: the metadata joined in tier 1; the three blocks | keep | G1 |
| ST05, as built: every join, not only the metadata join, refused outside tier 1 | not sure: wider than your decision on the metadata join | question 27 |
| D-0326, D-0327, D-0310, D-0311, D-0361, D-0505, D-0506: the opening build; Exploration; Table to view; the filters | keep | G5 |
| D-0457: a table no result reads can be viewed and is exported | keep | E5, G3 |
| D-0512, D-0416: data-agnostic words; "remove from all the data" off and explicit | keep | E3, G6 |
| D-0495, D-0498, D-0500: the author's side | keep | E4 |
| D-0322: filters and column drops | not sure; my recommendation is now to keep drops as decided (section 11 e) | G1; question 29 |
| D-0358, D-0371, D-0448, D-0449, D-0460, as far as they rule a column drop in the audit | not sure | question 29 |
| D-0341: the Reshuffle in Audit mode | not sure: my reading is that a new arrangement is not a correction | G3, G4; question 17 |
| D-0120, D-0145: no plot-style change for now | keep; remove the unmounted code | G4, E6 |
| D-0313: two lists of keys | keep | G5 |
| D-0203: a warning between ticked places when a value does not match one to one | not sure: it pulls against D-0501 (`DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` C14) | G5; question 28 |
| D-0337, D-0351 to D-0353, D-0356, D-0444, D-0445: the walk's rules for places and lines | keep | G5 |
| D-0452, D-0454, D-0460, D-0473, D-0486: the joins the app cannot follow YET; red lines | keep | E1 |
| D-0463: the lineage colours | keep; which colour means what is question 23 | G5 |
| D-0496: the lineage picker | not sure: for the story (E5); how a table that no result reads is reached is question 13 | E5; questions 13, 14 |
| D-0516, D-0517, D-0525: the recipe form; the one move | keep (question 2) | G2, G3 |
| D-0407 to D-0412, D-0468 to D-0484: the names | keep (one pass with the move) | G5 |

**The questions.** See part 8 of `WHOLE_PICTURE.md` (the table at its start). In short: now 28, 1, 29, 17, 4; then 2, 26, 15; after 28 and 1: 3, 5 to 8; 9 is not needed under 28 (a) or (b); my reading of your goals answers 10 to 12, 16, 18 to 22, 24, 25 (you may object); later 23, 27, 13, 14.

**The slices of `BUILD_ORDER.md (removed 2026-11-24 in the cleaning of the studies; see git history)`.**

| Slice | Verdict | What changes |
|---|---|---|
| 0, the records agree | keep | also: the D-0510 fact (B2 f) |
| 1, the filters follow the table | keep, add | built on branch `task/home-filter-follows-table` (in review); add a way to open any table once question 13 is answered (D-0457) |
| 2, the upload code | not sure | question 24 (my reading: remove) |
| 3, one representation | keep, change if you agree | HOME's plot and table come from the engine run of the audit recipe (its consequence 1); without column drops and Reshuffle if questions 29 and 17 say so; needs question 26 |
| 4, the dialog | keep, add | the dialog of places as decided, plus the measured effect per result if question 28 is (a) or (b); needs questions 28 and 1, then 3 to 8 |
| 5, the export of an audit | keep, add | both pictures in the Publication part; the count per result in the report; a seed never written into the author's parts; needs question 15 |
| 6, the report by groups | keep | — |
| 7, the one move | keep | after question 2 and the names |
| 8, the picker | not sure | after question 13 (and 14) |
| 9, a table as a result | keep | after question 2; the four places that count only plots as readers |
| 10, the check and the good-practice page | keep, add | the advices of D-0498 and D-0500; the refusal of a result id written twice; the page of 4.9 |
| 11, the preview sentences | done | — |

### 5.2 From the code on `dev`, the built parts one by one

**OK as built** (no change needed for the goals):
- The modes, the header strip, "Table to view", the badges [inventory].
- The Filters panel, its pickers and typed values, D-0503 and D-0504 (merged `51be0a46` and `781179e3`) [read: git log].
- The preview sentences (`d2e92547`) [read: git log].
- The opening build: `app/modules/opening_build.py`, `app/handlers/opening_handlers.py` [inventory]; it is the base of the measured effect.
- Compare for plots [inventory].
- The right panel that opens with Audit mode (D-0383, D-0385) [inventory].
- The reason gate on Apply; the session saved only on Apply (D-0302) [inventory].
- The session refusals of D-0312 and D-0317 [inventory].
- The live parts of the lineage library: the recipe graph, the step readings, the records and the YET sentence, the plan book and `compose_plan_book` (live at `app/handlers/home_theater.py:379`), the join keys, the tier lists, the engine marks; the drop facts of the walk (`LineageIndex.drop_facts`), live through the drop gate (`app/handlers/filter_and_audit_handlers.py:938`, `app/handlers/session_handlers.py:673`, `libs/utils/src/utils/recipe_check.py:575`); the audit copy's `audit_operation` and `integrity_errors`, live (`app/modules/cache_keys.py:69, 228, 409`; `app/modules/orchestrator.py:84-89`) [fact check]. Two headers are stale (`recipe_graph.py:55-61`, `step_effects.py:38`): text only.
- The recipe check (ST05 and the other codes) and the load gate [inventory].
- The export's key check, all plots exported, the T1 file of every table no plot reads, the stage keys and `effective_run.yaml` [inventory].
- Data Import [inventory].

**Needs adjusting** (what exactly):
- The key of an exploration filter holds the open plot; it must hold the table viewed (`app/modules/t3_audit_engine.py:69-73`) [read]. Built on branch `task/home-filter-follows-table`, in review.
- "Send to Audit" exists only while T3 is viewed (`app/handlers/filter_and_audit_handlers.py:158`) [read]: it must start from any table where the observations are seen.
- Called by tests only today, needed by the dialog [fact check]: the walk that lists the places (`walk()` of `libs/utils/src/utils/lineage_walk.py`); the builder of an audit copy (`AuditCopy`, `add_step` in `libs/utils/src/utils/audit_copy.py`); the run of the audit copy (`app/modules/audit_run.py`); the candidate plan (`compose_candidate_plan_book` of `app/modules/plan_composer.py`); the comparison of two tables (`libs/utils/src/utils/table_compare.py`). They must be connected to HOME. The audit copy must also learn table results and derived tables (`audit_copy.py:177`; `recipe_tiers.py:152-161, 182-210, 235-242`).
- `libs/utils/src/utils/remove_from_all.py` (called by tests only): keep which tables hold the entity key (D-0500) and the listing of a table with the same column name (D-0498); remove the statements `may_stay`, `may_differ`, `not_written` (on the demo all six "may stay" were false alarms, TRIAL Q6).
- The held branch `task/remove-from-all-ticked` (`95b6285e`): not merged as it is, because its sentences about unticked tables were false [run, the two reviews]. Its `apply(..., ticked=...)`, verified on 127 subsets, writes only at the ticked places: it can be taken without `_flow` and `unticked_places`.
- `app/modules/plot_seeds.py:156`, `bake_plot_seeds`: never write a seed into the author's parts of the original or the audit recipe (question 17 decides what replaces it).
- The recipe check: refuse a result id written twice in one recipe (A23); count derived tables and table results as readers (S07, J14) under form 3; AU04 depends on question 29.
- The report written in code (`app/handlers/export_handlers.py:1813-2112`): by groups (slice 6); the count removed per result; the original pictures beside the corrected ones.
- `effective_run.yaml`: add the fingerprint of the audit recipe (D-0333); retire the name `decision_hash` (D-0345).
- The export's `T1_data.tsv` and `T2_data.tsv` (`app/handlers/export_handlers.py:1405-1409, 1428-1431`): once a step can be written at tier 1 or tier 2, the audited part holds the audited tables, or a plain line in their place says they are the originals. The import checks the audit recipe's fingerprint (today "not_checked", `app/modules/bundle_importer.py:186-194`). [read; found by the independent review]
- The bundle import (`app/modules/bundle_importer.py:252-273`): the user's own place, name and date, an existing name refused (D-0435); check the audit recipe's fingerprint.
- The message when the user's place cannot be written (`app/handlers/audit_stack.py:1049-1058`): plain words, when Audit mode opens, not at Apply (4.10).
- The screen texts that state old limits or say "samples" (`app/handlers/home_theater.py:1482`; `app/handlers/filter_and_audit_handlers.py:674-676, 694, 997, 1002-1007`): they go with the parts they describe.
- BLUEPRINT's Apply and Save (`app/handlers/blueprint_handlers.py:1155-1196, 1255-1346`) [inventory, the seven-point check]: no silent loss; comments kept; no replacement by mistake (D-0495). Its own plan; not on the demo path.

**Must be replaced** (under every option of question 28):
- HOME's store of audit nodes and their application in memory (`app/modules/session_manager.py:56-106`; `audited_frame` of `app/modules/t3_audit_engine.py:799`): by the audit recipe and the engine run (slice 3).
- The modal "This plot only / All plots / All plots except" (`app/handlers/filter_and_audit_handlers.py:1097`, "Apply to:"): by the dialog of places (slice 4).
- The bin per step that removes every copy (`app/handlers/audit_stack.py:528-534, 627-682`): by "Remove step" (D-0314).
- The opening of a session whose original recipe was edited (`app/handlers/session_handlers.py:594-602`): by a refusal (D-0362).
- `t3_steps.yaml` (`app/handlers/export_handlers.py:1510-1546`): by the audit recipe, its record and its log.
- The export's one check box (`app/handlers/export_handlers.py:675-692`): by two ticks and one button (D-0298, D-0301).

**Must be removed:**
- The join fork of the reproducibility bundle: `build_mode2_recipe` of `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197-290`, and its call `app/handlers/export_handlers.py:1561-1564`.
- The two older forms in the session file (`app/modules/session_manager.py:509-523, 572-576`), with question 26.
- If you agree: the plot-style code that no screen reaches (`app/handlers/audit_stack.py:815-845`; the panel's comment at `app/handlers/home_theater.py:2340-2344`) [read; fact check]. It was kept unused on purpose on 5 November (`ui_implementation_contract.md` section 12a, fork issue #15); my suggestion to remove it rests on E6 and on your warning about old code taken up again (D-0507).
- The title "My Adjustments" (`app/handlers/audit_stack.py:460`) and the stale comments of `home_theater.py:287` and `orchestrator_helpers.py:53`.
- The report template that no code loads (`app/assets/report_template.qmd`), with the two places that name it: `.claude/rules/rules_app_structure.md:81` and `app/tests/test_writers_emit_format_one.py:364` [fact check].
- If question 29 is (a): the column drop sent to the audit (`app/handlers/filter_and_audit_handlers.py:861-925` and the control "Columns (drop unselected via audit)") and the drop gate's audit uses (`libs/utils/src/utils/key_drop.py`; `recipe_check.py:571-578` AU04; `audit_copy.py:199-208`; the restore at `session_handlers.py:673`) [read: the gate serves only audit steps].
- If question 17 is (c): the Reshuffle button (`app/handlers/home_theater.py:873`).
- If question 24 is (a): the unreachable recipe upload code (`app/handlers/ingestion_handlers.py:38-55`) and its reachability test's statement.

### 5.3 OK as it is: need not be touched

- The three tiers and their engine (`materialize_tier1/2/3`), the fallback T3 = T2 = T1.
- Reproducibility of a picture: the fixed seed 0 (D-0056), the order rules (ADR-090).
- The rule that every join is a tier 1 step (ST05), so the metadata join rule (D-0510, D-0523) needs no work.
- The three blocks of a recipe.
- Exploration as built: one plot, filters on the table viewed, nothing saved, never exported.
- The opening build and the large-data threshold.
- The export's refusal when the files changed; all plots in every export; the tables no plot reads.
- The Gallery and its picture key (D-0400).
- The names pass as planned (one pass with the move of the demo recipes).
- The user spaces and their flags: nothing in this path adds a handoff between them.

All from the inventory of 22 November or read at the lines cited; nothing here was run in this pass.

---

## 6. What the evidence shows, and what I think you may be missing (argued, D-0532)

Each point: the evidence, why it matters, how it would work, the alternatives, and your question. "Reopens" is information.

1. **The effect at a place does not tell the effect at the results.**
   - Evidence: two reviews wrote sentences about tables where no step is written ("stays", "removed upstream"); each kind was false somewhere, on the demo or on small test recipes [run, the two reviews]. Three runs on the demo, one entity each, with the places listed by hand: with the default read as tier 1 of each original table, the entity stayed in 7 plots, 3 of them with emptied metadata [run, C1].
   - Why it matters: you want the user to learn "the effects of its choices" (D-0531). A user learns only from effects that are true, and the rows at a place cannot show a row that a left join keeps further down (G1, G5, E2).
   - How: before Confirm, the engine builds the audit recipe with the ticked places (the build that "picture changed", D-0318, already needs) and compares each result with the original (4.4).
   - Alternatives: (a) the measured effect per result; (b) results first, with places proposed that you change, and the measured effect; (c) as decided: the rows at the place and "table changed / picture changed" per plot; then a count after Apply (question 9) or Compare.
   - Reopens in part: D-0501 (the count at the plot) and D-0508 ("Id rather the check is more where you apply it"). Your question: 28.
2. **The default.** Read as tier 1 of each original table, "the earliest" leaves the entity in 7 plots, 3 of them with emptied metadata; read as the end of tier 1 of each table that joins the metadata, it empties none [run, three entities]. With the measured effect, both are seen before Confirm; without it, the default decides what you get. Your question: 1.
3. **Column drops (revised after the independent review).** My first reading was that a column is not an observation (G4). The review's argument holds: a user who is not the author and must publish a table without a column would otherwise edit the exported file by hand, outside every record (G1). I withdraw my recommendation to take drops out of the audit, and the argument that a check would no longer be needed (an argument by less code). My recommendation is now to keep drops as decided, refused by place where a later join needs the column (D-0358). Your question: 29.
4. **The Reshuffle.** My reading: a new arrangement of random points removes no observation (G4), and a reader cannot tell whether the arrangement shown was picked among several (G3). The seed is recorded in the run file today, but no code reads it back, so a re-run does not draw the same picture; a home for the seed must be decided before the join fork is removed (section 3, G3 point 4) [read]. The independent review does not rank the options. Your question: 17.
5. **Sentences read from the recipe, not measured** (a builders' strategy, not yours). The library's "may stay" lists and the held branch's "stays" / "removed upstream" were false [run]. You warned of old code being taken up again: "right now the old things that exist are taken again because they are not build and this mixes with the decisions of what should happen" (D-0507). Suggestion: show only measured effects.
6. **The export's data files (found by the independent review).** The T1 and T2 files of the export are the original tables; only the T3 file of a plot is audited [read]. A reader who takes the T2 file publishes an observation that was removed. Suggestion: in the audited part, write the audited tables, or a plain line in their place saying they are the originals; and check the audit recipe's fingerprint at import.

Your own words of the same day name the risk of too many warnings: "So I think we are complicating a lot of our work putting warnings that should not be there - because they are natural consequences of the recipe" (D-0501). The measured effect replaces sentences and notes about later tables with one line per result: my reading is that it lowers the number of warnings.

What the evidence does NOT show: that any of your decisions on the scope is wrong. The scope stays yours; the evidence is about what you are shown.

---

## 7. The questions that remain yours

Only those that change what is built, in the order they are needed. Their full text, with what you would see for each answer, is in part 8 of `WHOLE_PICTURE.md`.

1. **Question 28 (rewritten):** start from places (as decided) or from results (the app proposes places you change); with the effect on each result measured, or as decided without it.
2. **Question 1:** which places are "the earliest", ticked by default.
3. **Question 29 (new):** column drops in the audit.
4. **Question 17 (an option added):** the Reshuffle, or none in HOME.
5. **Question 4:** the default for a filter on another column than the entity key.
6. **Question 2:** the recipe form; needed for table results and the one move, not for the audit.
7. **Question 26:** sessions saved before the change; before slice 3.
8. **Question 15:** the original recipe in the Publication part; before slice 5.
9. **Question 13:** how you open a table that no result reads (a picker, or by its name); before step 3 of the route.
10. **Question 30 (new):** a deployment where your place cannot be written: is the audit offered (kept in memory and exported only), or not offered?

After 28 and 1: 3, 5 to 8. Not needed under 28 (a) or (b): 9. My reading of your goals answers 10 to 12, 16, 18 to 22, 24, 25: you may object. Later: 23, 27, 14.

---

## 8. Earlier conclusions that this review changes, and why

**First pass (against version 3 of the study):**
1. A measured effect per result is added to what you see before you confirm. Why: G1, G3, E1, and the runs (section 6, point 1).
2. Column drops and the Reshuffle are proposed out of the audit (questions 29 and 17). Why: G4, G3. (Drops: withdrawn in the third pass, section 11 e.)
3. The seed in the export: removing the join fork (slice 5) also removes today's only replayable carrier of a reshuffled seed; the decided audit recipe cannot hold it in the layers. Not seen by version 3.
4. The order of the questions: version 3's "Now" was 1, 2, 27; 27 moves to later; ten questions get my reading of an answer, which you may refuse.
5. The picker is not needed to start an audit step. A way to open a table that no result reads is needed first; how is question 13 (the first pass called it "no question": corrected).

**Second pass (against the first pass, after D-0531 and the two checks):**
6. **Withdrawn: the app choosing the places from the results you tick.** Why: your words "the app cannot decide the scope" (D-0531), and the independent check found intentions that a choice of results cannot write: before or after the left join with the metadata, with the same results; your case of D-0199, removing the entities at tier 1 against "year xx not shown" at the plot, with the same plot; one intermediate table only; before or after the inner join with the gene list of `ST22_Anchor`; a computation the app fails to detect; and the first pass's rule "the next place down" overrode your ticks [fact check, section G]. These are cases of recipe facts, reasoned, not run.
7. **The place is not "technical"; it is the scope.** Corrected everywhere.
8. **Question 1 is needed again** (the default ticks).
9. **Question 28** now has four options: places with the measured effect; results first with places proposed that you change; as decided; neither. Its "Reopens" lists are complete.
10. **Section 0.5 / 6 no longer calls your decisions "hindrances".** It says what the evidence shows and what is my reading.
11. **"Answered by your goals"** is now "my reading of your goals; you may object", in part 0 and in part 8.
12. **Facts corrected:** 7 plots keep the entity, 3 with emptied metadata (not "3 plots"); the libraries "called only by tests" are named one by one, with the live ones; a line number; the report template's two other places; D-0340 and E6 wording; quote labels (section 10).

---

## 9. Evidence, and what I did not check

- **Ledger lines read** (each opened in the ledger): D-0004, D-0008, D-0015, D-0018, D-0021, D-0022, D-0034, D-0050, D-0053, D-0056, D-0065, D-0077, D-0093, D-0102, D-0108, D-0117, D-0125, D-0143, D-0147, D-0168, D-0194, D-0195, D-0199, D-0255, D-0268 (her words), D-0271, D-0313, D-0316, D-0324, D-0331, D-0332, D-0340, D-0341, D-0346, D-0355, D-0370, D-0389, D-0400, D-0401, D-0415, D-0416, D-0422, D-0423, D-0449, D-0450, D-0451, D-0457, D-0461, D-0478, D-0485, D-0487, D-0490, D-0492, D-0495, D-0496, D-0498 to D-0501, D-0507, D-0508, D-0512, D-0514, D-0516, D-0521, D-0527 to D-0532. D-0022 holds no words of yours (its evidence is a design file "decided 2026-11-12, Eve"); I quote its decision text only as the ledger's record. Other numbers are cited from the study's files, which its reviews checked.
- **Code read by me:** `app/handlers/export_handlers.py:1559-1572` and the seed lines found by search; `app/modules/plot_seeds.py:156-181`; `app/handlers/audit_stack.py:815-845, 1040-1060`; `libs/utils/src/utils/recipe_check.py:565-592`; the `key_drop` lines of `libs/utils/src/utils/audit_copy.py`. The callers named in 5.2 and the line numbers corrected come from the fact check. Every other code claim is [inventory].
- **Runs:** none by me. The numbers on the demo are the study's runs and its reviews' (`DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` C1; `TRIAL.md` and `EVIDENCE_untick_branch_reviews.md` of the main tree).
- **Not checked:** the dialog of section 4 does not exist and was not run; the measured effect was never computed by the app, only by the study's scripts with places listed by hand; whether the demo has other steps that compute over all observations was not searched; no browser was used. I read only block M593 of the agent channel, as the coordinator asked, and not `tmp.md`.

---

## 10. Where each fix of the two independent checks is answered

**The fact check** (`.claude/design/studies/whole_picture_2026-11/sources/whole_picture/GOALS_CHECK_facts.md`):
1. The place is the scope: path and question 28 rewritten (part 0.3, part 8 question 28; sections 4, 6, 8 here); "Reopens" completed (D-0022, D-0053, D-0194, D-0415, D-0451 named, with what each option reopens or not).
2. "Called only by tests": named one by one, live callers listed (5.2).
3. "3 plots": now "7 plots, 3 with emptied metadata; in two of the three only source and country" (section 3, G1 point 4; part 0).
4. Line number: `home_theater.py:2340-2344` (section 3, G4; 5.2).
5. Answers stated as given: "my reading; you may object" in part 0.5 and in the table of part 8; "Must be replaced" now says "under every option of question 28", and removals depend on their question (5.2).
6. D-0508 quoted in full, with "but thanks for the warning so I will pass it to my users" (2.4, 4.9); the propagation and the reach kept as needed for the user's choice (4.5); D-0501's sentences quoted where used.
7. D-0340: "the ledger's reading of your answer (not your words)" (4.10).
8. E6: "approved with "1. ok." (D-0125); who wrote the text is not stated" (2.2).
9. Quote labels: "this result only" and "one name, one meaning" no longer quoted as yours; the D-0423 screen text marked as the option's text (4.7, 4.9).
10. The report template's two other places named (5.2).

**The reader in your place** (`.claude/design/studies/whole_picture_2026-11/sources/whole_picture/GOALS_CHECK_reader.md`):
1. A table "is each goal reached", today and as decided: part 0.2.
2. The route of the work as ordered steps, each with what you can then do on the demo: part 0.4.
3. The code list in what you see, with how each verdict was checked: part 0.5 (ii).
4. No strings of ledger numbers in the sentences of part 0; words explained before use: part 0, "Words used here".
5. No argument from your own words for an option; nothing stated as proven from three runs (marked "three runs, one entity each, places listed by hand"); no reproach: part 0.6 and part 8.
6. Questions 28, 29, 17 and 4 self-contained, with "what you would see" per option and a "neither" option; the contradiction on question 17's recommendation resolved: part 8.
7. The sketch completed: the lineage lines, the default named, the reach, the effect lines including "still found here", the "remove from all the data" option: part 0.3.

---

## 11. Answer to the independent review (third pass)

You ordered an independent review of this work (D-0533: "independent errors - opus agents often overlook important points"). It is `GOALS_REVIEW_sonnet.md (removed 2026-11-24 in the cleaning of the studies; see git history)` in the worktree `SPARMVET_VIZ_wt_goals_sonnet` (commits `a36bd0e5` for its blind part, `563bb774` for its comparison and its check of `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)`). I checked each finding of its parts B and C myself: by a ledger line, by the code at file:line, or by a run. ACCEPTED means I changed the text; NOT ACCEPTED gives my evidence. Where we still disagree, you decide; you see both documents.

**a. Your case of D-0499 (its B2.1). ACCEPTED.**
- My run (`check_a.py`, the app's own run of an audit copy, the demo, entity `10668076`): "remove from all the data" as built reaches 27 places. With `QC_Reads_Anchor` and `Quast_with_metadata` unticked, all 17 plots change and the entity is in none: the sources `FastP`, `Quast`, `Bracken` and the metadata are still ticked, so the row is gone before the joins. With those four also unticked (six places in all), the entity stays in exactly the 3 quality plots, with its source, year and country, and 14 plots change.
- My sentence of 4.4 came from the study's 19-place variant (`DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history)` C1), which is not the option you decided: "1. yes (though unlikely no plot)" to "it reaches every table that holds the key column" (D-0416).
- Changed: 4.4, 4.11, part 0, `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)`. One run, one entity.

**b. The export's T1 and T2 files are the original tables (its B2.6, C5). ACCEPTED.**
- Read: `app/handlers/export_handlers.py:1405-1409` writes `T1_data.tsv` and `:1428-1431` writes `T2_data.tsv` from the tables as built; only `T3_data_<plot>.tsv` passes through `audited_frame` (`:1463-1467`). The import marks the audit steps "not_checked" (`app/modules/bundle_importer.py:186-194`).
- What it means for "results it can trust": today an audit step lives only at a plot's own table, so the T1 and T2 files are the originals by construction. A reader who takes the T2 file publishes the observation you removed; the README names each file, but nothing in the file says it is not audited. Once a step can be written at tier 1 or tier 2, the audited part must hold the audited tables, or a plain line must say that the files are the originals; and the import must check the audit recipe's fingerprint.
- Changed: section 3 (G3 point 2), 5.2, section 6 point 6, part 0, slice 5 in `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)`.

**c. The z-score (its B2.6). ACCEPTED, with my reading of what it shows.**
- My rerun of its script (`e2.py`): removing the entity after the z-score of `QA_population_zscore` (a filter on the finished table: what the audit can do today) and removing it before (tier 1) give different z-scores for all 41 other entities; the largest difference is 0.064, on a z-score near 1.8.
- Both are legitimate choices; which is right depends on your context (D-0531). The run shows that today you cannot choose "before".
- Changed: section 3 (G2), part 0.

**d. The seed in `effective_run.yaml` (its B2.3). ACCEPTED in part.**
- Read: the run file holds the seeds (`export_handlers.py:1675-1677`). Searched: no code reads them back at a re-run or an import (`bundle_importer.py` reads the hashes only). So the seed is recorded, not replayed.
- Accepted: my sentence "cannot be re-run to the same picture" is true of today's code, not a hard limit; a home for the seed can be the audit record or the run file. Question 17 gets that option (the review's proposal), and the technical point is no longer part of my argument for (c).
- NOT ACCEPTED: that nothing separates the options. I keep (c) on merit: a figure picked among random arrangements is harder to trust, and a new arrangement removes no observation. The review does not rank them; you decide.

**e. Column drops (its B2.2). ACCEPTED in part.**
- Accepted: "the check of key columns is no longer needed" was an argument by less code; withdrawn. Accepted: a user who is not the author and must publish a table without a column would otherwise edit the exported file by hand, outside every record. So I withdraw my recommendation (a).
- NOT ACCEPTED: drops only at the result's own table. It limits where a drop may be written, so the app would decide part of the scope ("the app cannot decide the scope", D-0531), and it narrows your rule that a key drop is refused by place only where a later join reads it (D-0358, D-0371).
- My recommendation is now (b), as decided. The review's form is option (c) of question 29.

**f. Question 28 (its B2.8). ACCEPTED.** The text now says what was withdrawn (the app choosing the places for you) and what (b) is (a proposal, every place visible and yours to change, like a default tick). Option (c) no longer argues from your decision; it says what (c) gives: a shorter dialog, the check after Apply.

**g. The ten readings (its B2.7). ACCEPTED.** Part 0.8 lists them in one table, each with what you would see, and says that nothing is built from them until you say yes. Answer in one line: "accept all", or the numbers you object to.

**h. The match list (its C1 to C5). ACCEPTED, every row.**
- D-0501 first part: NOT SURE. Question 28 (a) shows an effect line per result, downstream of the step; whether that is a "per table warning" is yours.
- D-0203: NOT SURE; it pulls against D-0501.
- The audit folder where the user's place cannot be written: NOT SURE; new question 30. D-0422 assumes that saving works in every deployment.
- ST05: split. The metadata join in tier 1: KEEP. Every join in tier 1: NOT SURE (question 27).
- New rows: the export's original T1 and T2 files and the import's check (CHANGE, slice 5); the deployment with no writable place (question 30); the propagation modal (DROP: replaced); the screen texts that say "samples" or "for now" (CHANGE); the join fork of the export (DROP: it writes the steps at a place nobody chose).
- The good-practice page: the paragraph on the audit folder waits until the folder is built and question 30 is answered.
- Slice 3: the decision to replace today's audit at a plot's table by the audit recipe and its run is KEEP (needed under every option; point c shows that two audits would give different numbers); its details stay NOT SURE (questions 26, 29, 17).
- "Remove from all the data" with unticked places stays a library step until the measured effect can show where the entity stays (its C1 row 0.4): agreed.

**i. Part 0 readability (its B2.12). ACCEPTED.** Part 0 names the goals in plain words, without codes; ledger numbers stand only after your quotes; the full text of the questions to answer first is in part 0.8, and part 8 points to it.

**j. Line numbers (its B2.11). ACCEPTED.** Checked again on `dev` (`ac1e1e15`): `audited_frame` is at `t3_audit_engine.py:799`; the modal's "Apply to:" at `filter_and_audit_handlers.py:1097`; "for now" at `home_theater.py:1482`; the Reshuffle button at `home_theater.py:873`; "Send to Audit" only at T3 at `filter_and_audit_handlers.py:158`. Corrected in 5.2. Other line numbers of 5.2 are within a few lines of the code: the files moved since the inventory.

**Other points of its parts B and C.**
- B2.4, the default ticks: agreed; the screen must say "starting point" (added to question 1 in part 0.8).
- B2.5, ST05: the review withdrew its own proposal of part A; agreed.
- B2.9, the summary-table run (a new group with an empty country and year): the review did not reproduce it. It rests on the proposal authors' run, re-run once by the author of the earlier study (`RECIPE_REDESIGN_REVIEW.md (removed 2026-11-24 in the cleaning of the studies; see git history)` section 1), not by me. The recommendation of question 1 stands on the demo numbers alone.
- B2.10 and B2.11: no quote said more than your words; no code claim was wrong in substance. Noted.
- B2.13: I ran the checks of a and c in this pass.
- The opening-build row of `MATCH_LIST.md (removed 2026-11-24 in the cleaning of the studies; see git history)`: after the filter branch is merged, the filters are kept while the table is the same; the row's words follow.

**What I could not verify.** Its test runs of the filter branch (88 passed) and of the held branch (125 passed, 1 skipped); its probe of a result id written twice (weak, as it says); its blind part A as a whole (I answered parts B and C, as asked).
