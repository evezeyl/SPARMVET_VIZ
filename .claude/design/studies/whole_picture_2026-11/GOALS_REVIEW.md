# Your goals, and the path to them (2026-11-22)

A study, not a decision: nothing is built from it before you answer (D-0507, D-0528). The short version is part 0 of `WHOLE_PICTURE.md`. This file holds the detail, for you if you want it, and for the builders.

**How to read it.**
- Your words are between quotation marks, exactly as you typed them, with the ledger number.
- "Reading" marks a reading of your words that is not yours. "Mine" marks my proposal. "Suggestion:" comes before a remedy.
- Evidence: [read] = read in the code at file:line on 22 November; [run] = a run of this study or of its reviews, named; [inventory] = taken from `PARTS_TABLES.md`, `DIFFERENCES.md` or the two collected files of the main tree (`tmpAI/coordinator/whole_picture/BUILT_audit_lineage.md`, `BUILT_format_export_names.md`), not re-read.
- The app is data agnostic: "the entity" and "the entity key". On the demo recipe the entity is a sample and the key is `sample_id`. "Observations" is your word: I read it as the rows of a table, its usual meaning in data science (my reading).

**What this version is.** The coordinator relayed your passage of 22 November (D-0528) and, after it, six more places to cover that you accepted with "Ok i agee" (block M593 of the agent channel: the review session's list, not your words). So this is a design built backwards from your goals, not a check of the earlier design against a list. The earlier study (`WHOLE_PICTURE.md` parts 1 to 9 and the other files of this folder) is an input.

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
| G6 | The app gives the tool, the reproducibility, the transparency and the reliability; it does not choose for the user, because the right choice depends on the user's context. | "Our role is to provide the tool, the reproducibility, transparency, reliability - however we cannot take choices for the user because it depends on the user context" |

### 2.2 From earlier decisions (big goals only)

| # | The goal | Your words |
|---|---|---|
| E1 | Nothing changes a result silently. | "No silent error that is the rule." (D-0050) |
| E2 | No wrong result because the wrong scope was chosen. | "Sorry do not get wrong results because we did not select the correct scope" (D-0450) |
| E3 | One app for every recipe, data agnostic; every recipe works. | "remember we are data agnostic so sample id is the example" (D-0512); "All recipes need to work" (D-0077) |
| E4 | Two kinds of person: the author of a recipe, and the user, who is often someone else. A well-made recipe lets the user choose correctly. BLUEPRINT is the author's tool. | "well the problem is that the user might not be the author" (D-0500); "I think in this case if a recipe is done correctly you can ensure that the user can do correct choices." (D-0498); "blueprint aim is an ide to build recipes" (D-0495) |
| E5 | The story of the data can be followed, from the original files to a result. | "YES the story of is what I want to show - this is why I wanted the lineages" (D-0508) |
| E6 | A well-built app: one source of truth, no half fixes. | "our role is to diliver an app that is well developped architecture wise" (D-0108); "We aim for one source of truth." (D-0065). "We do not do half fixes." is in the goal text you approved with "1. ok." (D-0125); that text is the review session's wording, not yours. |
| E7 | The way there: the whole picture first, then the big line fast; the demo with no special treatment. | "I think we should maybe use a good thinking model to have the abiity to see the whole picture on how it should work - and then build" (D-0507); "I would prefer to have the big line done as fast as possible" (D-0521); "no special treatment of files for the demo" (D-0255); "so agreed I will do the demo in 2 weeks" (D-0370) |

### 2.3 Looked for, and not found in your words (not presented as yours)

- "The user spaces are independent": decided by you (D-0008: ADR-093 "ACCEPTED and IMPLEMENTED (Eve, 2026-11-08)"), with no words of yours in the line. Nothing in this design touches it.
- "Keep it simple" as a general rule: your words simplify specific places ("Maybe we should just simplify - all plots included in the export", D-0292; "we simplify", D-0410). The general rule is in `.claude/rules/dasharch.md`, not attributed to you.
- "What the user sees and does is what the export contains": a rule attributed to you with a date (`rules_verification_testing.md` section 9, "added 2026-11-06, Eve"); whether the sentence is your wording is not stated. Used below as a condition of G3.
- The demo: the audience ("colleagues") is not in your quoted words. The length, 30 minutes to one hour, is in the decision text of D-0255, not in the words quoted there.
- HOME's purpose ("publication-ready results", "a recorded reason for every change", `.claude/design/spaces/HOME.md`): an agent's text of 2026-11-12 (commit `89d0828c`), so a reading.

### 2.4 Goals that pull against each other (yours; not resolved here)

1. **Inform of every pitfall, against no warning the user learns to ignore.** "could we detect those cases and inform about the possible got you" (D-0508) / "that would also avoid the load of warnings that the user would just ignore" (D-0501).
2. **The user chooses the scope, against no wrong result from a wrong scope.** "That is the choice of the user - because the user decide the scope" (D-0355); "yes the user may unthink he is responsible of its choice" (D-0499) / "Sorry do not get wrong results because we did not select the correct scope" (D-0450).
3. **One definition for each table, before its use, against a story that can be navigated.** "Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before" (D-0516) / "I am just wondering of how to make it navigate" (D-0518).
4. **The big line fast, against studying in detail.** "I would prefer to have the big line done as fast as possible" (D-0521) / "study in details in others when necessary - implementation time is not really an important factor as we can delay implementation" (D-0268).
5. **Everything needed to redo the analysis, against not cluttering.** "if you need to redo the analysis then you will need to re-upload the recipe" (D-0389) / "The original recipe can be added for baseline BUT it need to be clear for the user which one is which one ... (and maybe not cluter what the user has access to )" (D-0324).
6. **One app for every recipe, against guarantees that need a well-made recipe.** "All recipes need to work" (D-0077) / "if a recipe is done correctly you can ensure that the user can do correct choices" (D-0498). You named it yourself: "I am afraid there is no perfect solution and that we must adopt a tradeoff here." (D-0500).
7. **The user learns where a change is applied, against the app carrying what is technical.** "the user will have to learn that its not the sample that stays but where the change is applied that is a big difference - so the user will have to learn a bit of datascience" (D-0508) / "Our role is to provide the tool, the reproducibility, transparency, reliability" (D-0528). This pair is my reading of a tension. The path of section 4 keeps both: the app places the step and shows where; the help teaches why the place matters.

---

## 3. Built backwards: what must be true for each goal

For each goal: the conditions that must be true, then whether the design as decided makes them true, and whether the app on `dev` does. "Decided" = the earlier study's design, from your decisions. The marks: **yes**, **partly**, **no**.

**G1. Audits that are clear, correct, reproducible and transparent.**
1. Each correction is written once, in a copy of the recipe, with its reason; the original never changes. Decided: **yes** (D-0102, D-0143, D-0332). Today: **no**: three forms of one step (`DIFFERENCES.md` A11).
2. Before confirming, the user sees what the correction does to each result. Decided: **partly**: rows at each place, and "table changed" and "picture changed" per plot (D-0316, D-0318); the count at the plot was removed (D-0501). Today: **no**.
3. What is shown is measured, not guessed from the recipe. Decided: **partly**. Two reviews proved that a statement about a table where no step is written cannot be read from the recipe: every such statement of the library was false somewhere [run, `EVIDENCE_untick_branch_reviews.md` of the main tree].
4. The step sits where it does what the user intends. Decided: **open** (question 1): with "tick low" read as tier 1 of each original table, the removed entity stays in 3 plots of the demo with its source and country emptied [run, three entities, `DIFFERENCES.md` C1]. Today: **no** (tier 3 of one plot only).
5. Anyone can re-run it and get the same result. Decided: **yes** (two parts, D-0490, D-0492; the record, D-0333). Today: **no** (A17).

**G2. A tool for good data science.**
1. Removing an observation before a step that computes over all observations (a mean, a z-score, a count per group) is a deliberate choice, with its consequence shown. Decided: **no**: "tick low" removes before every such step without asking; question 8 is only a note at one place. Today: **no** (always after everything).
2. The tool does the data-flow reasoning correctly, for every recipe. Decided: **partly** (the walk of the lineage; red lines where it cannot follow YET). Today: library only, called by tests.
3. Each table has one definition. Decided: **open** (form 3, question 2).

**G3. Results for publication, plots and tables, that the user can trust.** (Point 1 of the six places.)
1. A table can be a result. Decided: **yes** (D-0485). Today: **no**.
2. What the screen shows is what the export holds. Today: **yes** for the result and the audited steps of today, and the export refuses when the files changed since the view (X1, X11) [inventory]; **no** for the original pictures beside the audited ones (D-0147, not built).
3. A plot and its table are the same data. Today: **yes**: one reader, `materialize_tier3`, serves HOME's plot, its table, the export and the pictures (`.claude/rules/rules_data_engine.md` section 1).
4. The same recipe and data give the same picture. Today: **yes** (ADR-090; the seed fixed at 0: "Fixed 0 by default fixed and simple", D-0056, built `653e70b1`). One exception: a Reshuffle pin. Today the reproducibility recipe carries it by writing the seed into the plot's layers (`app/modules/plot_seeds.py:156`, called at `app/handlers/export_handlers.py:1567`) [read]. The decided audit recipe cannot hold it there: the author's parts stay untouched and the copy minus its audit steps must equal the original (D-0332, D-0040).
5. A picture is current. Gallery: **yes**, the picture key (D-0400, built). HOME stores no picture: each is drawn from keyed tables (D-0335).
6. A reader sees the original and the corrected result, and how many observations were removed from each. Decided: **partly**: both pictures (D-0147; where: question 16); the count per result was removed (D-0501). Today: **no**.

**G4. The audit is for small corrections by removal of observations.**
1. The audit removes observations: one entity, or the rows that meet a condition. Decided: **yes** (D-0322: filters and removals by key).
2. The audit does nothing else. Decided: **no**: column drops (D-0322) and the Reshuffle (D-0341) are in it. Today: also the code of a plot-style change, which no screen reaches (`app/handlers/audit_stack.py:815-845`) [read].
3. The machinery is no larger than such a correction needs. Decided: **no**: see section 6.

**G5. Each choice shown clearly, with the information needed.**
1. The user decides in terms she knows: which observations, which results, why. Decided: **partly**: she decides in places of the recipe (tier 1 of a table, the end of tier 1 of a join), not in results.
2. Only what changes her choice is shown. Decided: **partly**: no downstream warnings (D-0501), but 13 lines of places on the demo under reading B of question 1.
3. Words for a user who is not a developer. Decided: **open** (question 19).

**G6. The tool, not the choice.**
1. Every choice that depends on the user's context is hers: which observations, which results, before or after a computation over all observations. Decided: **partly**: results are reached through places, and before or after is not asked.
2. Every choice that does not depend on her context is the app's, shown and proven. Decided: **no**: the place, a technical matter, is left to her, with a default.

**E1 and E2. Nothing silent; no wrong result from a wrong scope.**
1. The app says nothing it cannot prove, and measures what it cannot read. Decided: **partly** (the notes "where the app can").
2. The user chooses results, and the app proves the effect on each before she confirms. Decided: **no**.

**E3. Every recipe.** Each rule above works on any recipe because it measures. Decided: **partly**.

**E4. The author and the user.** The author is helped to make a well-made recipe (key declared, one name for one meaning), and BLUEPRINT never damages one. Decided: **yes** (D-0495, D-0498, D-0500). Today: **no**: BLUEPRINT drops parameters on Apply and loses comments on Save (`tmpAI/coordinator/blueprint_verify/REPORT.md` section 2 of the main tree) [inventory].

**E5. The story.** Any table and its stages can be looked at. Decided: **yes** (D-0457, D-0508). Today: **no** (V2, V3 of `PARTS_TABLES.md`).

**E6. Well built.** One representation of an audit step; no old code taken up again. Decided: **yes**. Today: **no** (A11, A12, A21).

**E7. The way there.** Section 4.11.

**What this shows.** The conditions that fail in the decided design meet in one place: the user chooses PLACES in the recipe, and the app infers their effect. The goals ask the opposite: the user chooses what depends on her context (the observations, the results, before or after a computation over all observations), and the app does the technical part and PROVES its effect. Section 4 builds the path from that.

---

## 4. How to succeed: the path

### 4.1 The principle (mine)

- The user describes a correction in her own terms: **what** (one entity, or the rows that meet a condition), **for which results** (the plots and tables she publishes, or keeps to justify the correction) and **why** (the reason).
- **Where** the step goes in the recipe is the app's job, because it does not depend on her context. One exception: a step that computes over all observations (a mean, a z-score, a count per group, a rank). Removing an entity before such a step changes the values of the other entities; removing it after does not. That depends on her context, so the app asks it, and only there.
- The app **proves** what it did: it builds the audit copy and compares each result with the original, before she confirms.

Why this follows from the goals:
- G6: "we cannot take choices for the user because it depends on the user context". The observations, the results and "before or after" are her context; the place in the tiers is not.
- G5: she chooses in terms she knows. Your own case is phrased in results: "he wants to show the poor quality sample for the quality results but remove the bad sample from all other results." (D-0499).
- G1, E1, E2: the effect is measured, not read from the recipe. Reading gave false statements (`DIFFERENCES.md` A4); a place chosen by a rule left the entity in 3 plots with emptied metadata (C1).
- G4: a small correction should not need the user to know the tiers of the recipe.

### 4.2 The path, step by step, on the demo recipe `1_test_data_ST22_dummy`

Before: the author writes the recipe. It declares the entity key and joins the metadata in tier 1 (the recipe check already refuses a join anywhere else, ST05). What the author must do, and how BLUEPRINT helps, is in 4.7 and 4.8.

1. **Open.** The app builds every table and draws every result once; a recipe that cannot be built is refused with a plain reason. [built]
2. **Look (Exploration).** She sees a result (the plot `mlst_bar`) and the table it is made from; the earlier stages of that table ("Table to view"); and any other table of the recipe by its name, also one that no result reads (D-0457). A filter changes only what she looks at; nothing is saved or exported. [built, except "any table by name" and the filters kept per table, D-0506]
3. **Find.** In the table of `mlst_bar` she sees the entity `10668076`; her lab notes say its sequencing failed.
4. **Ask (Audit mode).** From the table where she sees it, she asks to remove the observations: the whole entity, or the rows that meet a condition (for example the year 2023). She writes the reason. [the reason gate is built]
5. **Choose the results.** The dialog lists every result by group and name (plots and tables), and the tables that the export writes although no result reads them. Each line says whether it holds this entity (or rows that meet the condition). The app ticks a default and says why: for an entity, every line that holds it ("my most frequent use case is the sample is bad", D-0194); for a condition on another column, the result where she started (your year case, D-0199). She unticks what must keep the observations, for example the 3 quality results (D-0499). One button ticks "all the data" (D-0415). **Fork, yours: the default (question 4).**
6. **Before or after.** Only if a step on the way to a ticked result computes over all observations, the dialog asks, for that step: "before (the entity no longer counts for the others) or after (it is hidden; the others keep the values computed with it)". No default: it depends on her context. On the demo the study names two such steps: a z-score in tier 2 of `QA_population_zscore` and an aggregate in tier 2 of `QA_aggregated_no_key` [inventory, C1]; whether there are others was not searched. A plot's own count (the bars of a bar chart) is part of the drawing, always after: it is not asked.
7. **See the proof.** The app writes the step into a copy of the recipe (the audit recipe), builds it, and shows for each result: "1 observation removed" or "unchanged". Only where it happens, it adds: "still found here: N observations (the key is written differently here)" or "the values of other observations change here (they are computed over all observations)". One line says where it wrote the step, for example "end of tier 1 of MLST_with_metadata, read by mlst_bar and year_distribution": information, not a choice.
8. **Confirm.** The step is in the audit recipe with its reason (`audit_comment`, D-0329). The audit log records the step, the reason, who and when, the results ticked (by default or by her), her before-or-after answers and the effects she was shown (D-0478). Only the tables that changed are built again (D-0325).
9. **Check.** She sees the audited results; Compare shows the original and the audited one side by side, with the counts (D-0147, D-0489 layer 1). She can take any one step out again ("Remove step", D-0314).
10. **Keep.** Her session keeps the audit recipe, its record (a hash) and the log in `audit/` (D-0319, D-0423). A hand-edited audit recipe, or a session whose original recipe was edited since, is refused at reopening with a plain line (D-0331, D-0362).
11. **Export.** Two ticks, Publication and Reproducibility (D-0298). Publication: the audited results and, for each changed result, the original beside it; the report, results first (D-0491), with one methods line per step (for example "10668076 removed from the results listed, with the number of observations removed from each; reason: sequencing failed, lab notes of 12 April"; wording mine); the audit log. Reproducibility: the data once; `original/` with the original recipe; `final_audited/` with the audit recipe, its record and the log; a README that says which is which (D-0490, D-0492). Exploration is never exported (D-0327).
12. **Re-run.** A reader runs either part and gets the same tables and pictures; the record shows that the audit recipe was not edited by hand.

The forks that are yours, in the order they meet the path: question 28 (this path, results and proof, or the places of the decided design); question 29 (column drops in the audit); question 17 (the Reshuffle); question 4 (the default results); question 2 (the recipe form, for table results); question 26 (old sessions); question 15 (the original recipe in the Publication part). Their full text is in part 8 of `WHOLE_PICTURE.md`.

### 4.3 Who chooses what

| The choice | Whose | Default | Why |
|---|---|---|---|
| Which observations (an entity, or a condition) | the user | none | her context |
| The reason | the user | none; required | a correction without a reason is not transparent (built gate) |
| Which results | the user | a default ticked and said: an entity, every line that holds it; a condition, the result where she started | her context; the default follows your two cases (D-0194, D-0199); question 4 |
| Before or after a step that computes over all observations | the user | none: asked only where such a step lies on the way | it changes the values of other observations: her context |
| Where the step is written | the app | none shown; one line says where | technical; proven by the run |
| Keep the entity in some results (D-0499) | the user | untick | her context |
| "All the data" (D-0415) | the user | off (D-0416: "2. yes off") | an explicit act |
| The table shown when a recipe opens | the app | the result's table (as built) | the table under a figure is the one it is drawn from |
| What the export holds | the user: Publication, Reproducibility | the audit log and the record are always in a bundle of an audit (D-0478, D-0333) | her context; the log is not optional by your decision |

### 4.4 How the app places a step (rules for the builders; mine)

- **An entity:** at the end of tier 1 of each table that joins the metadata on the way to a ticked result, so that the row leaves with its metadata. This is your own reason: "the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" (D-0509); "join with metadata must be done at T1 that would simplify removing of samples by key no" (D-0510). On a way that never meets the metadata: tier 1 of its first table. Then before the steps she answered "before" for, after the others.
- **A place that also leads to a result she did not tick** is replaced by the next place down that leads only to ticked results; at the latest, the result's own stage ("this result only", D-0346).
- **A condition on another column:** at the stage where she built it (the values she saw), when that stage leads only to ticked results; else the next place down that does, where the column still holds the same values (the walk's notes `recomputed_here` and `another_type_here` say where values may change).
- **"All the data":** tier 1 of every table that holds the entity key (`libs/utils/src/utils/remove_from_all.py`; the key is the declared key and a column a join equates with it, D-0500).
- **The proof, always:** the engine builds the audit copy (`app/modules/audit_run.py`, today called by tests only) and compares each result with the original (`libs/utils/src/utils/table_compare.py`, layers 1 and 3, today called by tests only). A result that was not ticked must be byte-equal; a ticked result must have lost exactly the observations asked. When a result that was not ticked would change, the app does not write and says why.
- **Finding a step that computes over all observations, for any recipe (mine):** the app compares a ticked result with the step written early and with the step written at the result's own stage. When the other observations differ, such a step lies between them; the walk's notes (`aggregated_here`, `one_row_per_group_after_this_step`) name it.
- **Evidence on the demo** (reading B of question 1 = the rule above for an entity) [run, three entities, `DIFFERENCES.md` C1]: removed from every result that holds it, the entity is in no plot; with the 3 quality results unticked (D-0499), it stays in exactly those 3, with its metadata, and 14 plots change; no metadata is emptied. The places were listed by hand; the dialog of this path is not built and was not run.

### 4.5 What a scientist needs to defend the result to a reviewer, and no more (mine, from G1, G3, G4)

1. For each correction: which observations, from which results, why, by whom, when.
2. For each result: the original and the corrected version, and how many observations were removed.
3. Proof that nothing else changed: the audit recipe differs from the original only by its audit steps (the record's hash; D-0040, D-0333).
4. A way to re-run both (D-0490, D-0492).
5. Where a removal comes before a step that computes over all observations: that choice, with its reason.

Not needed for the defence: the tiers and places of the recipe, the reach of a place, colours, a propagation drawing, notes per place, the comparison layers 2 and 3 on screen (they serve checking, on request: D-0489).

### 4.6 The recipe structure, seen from the goals

- **The stages** T1, T2, T3: keep (built; D-0179, D-0343).
- **A result is a plot or a table** (G3; D-0485): needed.
- **Derived tables made with `from:`** (form 3, question 2): they serve G2 and G3: one definition per table, so a plot and a table of the same summary show the same numbers by construction. One level for now (option a1 of question 2). The navigation gap of form 3 (D-0518) does not block the audit in this path: the app places a removal before a count, where the key still exists, so the user need not find the derived table's tier 1. It remains for the story (E5).
- **The three blocks** (D-0513) and **the metadata join in tier 1** (D-0510, D-0523; built, ST05): keep. The metadata join in tier 1 gives the app one clean place for removing an entity.
- **Every join in tier 1** (ST05; not a line of yours): keep for now. Question 27 matters only when a recipe needs a look-up join after a count; the demo needs neither option.
- **Is the form as simple as the goals allow?** For small corrections: the author writes nothing for the audit; the audit writes its own steps. For publication results: a result names one table. One complication stays and must be documented: a join reads its tables after their tier 1, `from:` reads its table at its last stage; making joins read tier 2 would change results silently on the demo (the proposal's flag 3, `RECIPE_REDESIGN_REVIEW.md` 5.3).

### 4.7 The two kinds of person (place 2 of M593)

**The author** writes the recipe (in BLUEPRINT or by hand): the structure, the entity key, the metadata join, the derived tables, the results.
- Inform, never choose: the recipe check refuses only what cannot run or would be wrong (ST05, the strict import) and advises the rest. Advices this path needs (mine): declare the entity key where a column is used as a join key ("the key declaration is a good practice (and we need to ensure that blueprint encourages it)", D-0500); one name for one meaning ("do not use same column names for different meanings - declare what is ID key", D-0498); a look-up table with an entity key (question 22).
- Clear information: the check's messages with code, plain sentence and fix (built); the columns that exist at each stage (BLUEPRINT part F, not built); the lineage.
- What the author must never lose: a production-ready recipe, and the comments in it (D-0495).

**The user**, a colleague who may not be the author ("well the problem is that the user might not be the author", D-0500), looks, decides what to remove, for which results, before or after, and why.
- Inform, never choose: the app never chooses the observations, the results or before-or-after; it chooses the place, says where, and proves the effect.
- Clear information: in her terms (results, observations), measured, only what changes her choice.
- The user cannot repair the recipe in HOME (D-0102). When the recipe makes a correct correction impossible (no declared key; a key rewritten), the app says so in plain words and names the recipe's contact. Suggestion: reuse the contact of the load gate (`info.contact`, ADR-094) in the dialog (mine).

### 4.8 BLUEPRINT and the author (place 3 of M593)

- The seven-point check found that BLUEPRINT can damage a recipe silently today: Apply drops a parameter the form does not show; a number becomes text; Save writes with no check and loses the comments; the preview drops a failing step (`tmpAI/coordinator/blueprint_verify/REPORT.md` section 2, items 1 to 4, main tree) [inventory]. A recipe damaged by its author gives wrong results to every user: this hinders G1 and E4 before any audit.
- The coordinator's build plan already moves "a save keeps the comments" and "Save never replaces a recipe by mistake" into its slice 1, after your D-0495 (`BUILD_PLAN.md` of the same folder) [inventory].
- What the goals add (mine): the advice to declare the entity key (BUILD_PLAN item 5; D-0500) and "one name, one meaning" (D-0498); one lineage function shared with HOME's placement (D-0065; `DIFFERENCES.md` A10); BLUEPRINT shows the same rules the audit relies on.
- When: you put BLUEPRINT after HOME and the Gallery ("we do changes to blueprint and lab after - we focus on home and gallery", D-0271). It is not needed for the demo of HOME and the Gallery; its safety slice is needed before anyone writes recipes with it.

### 4.9 Documentation and help, part of the tool (place 4 of M593)

**On screen, short, at the moment of the choice:** where the step is written (one line); the effect on each result; the before-or-after question with its consequence in one line; "still found here" and "the values of other observations change here" only where they occur; in Audit mode, the plain line "do not edit the audit files outside the app" (D-0423).

**On the good-practice page and in the user guide** ("1. Our limits will need to be clearly documented..", D-0461; "A - and it needs to be explained in the documentation and help", D-0423; "I am afraid that too much explanation in the ui will be too much information - and Id rather the user be able to use the help", D-0404):
- why the place of a removal matters, with your sentence "the user will have to learn that its not the sample that stays but where the change is applied that is a big difference" (D-0508): the left join, and the steps that compute over all observations;
- the three gotchas: a key recomputed, a key under another column name with no join, a key rewritten by a step (D-0508), and how the app finds them ("still found here");
- one name for one meaning, declare the ID key (D-0498); import only the columns needed (D-0462);
- the joins the app cannot follow YET (D-0486);
- the two reading rules of form 3 (4.6);
- the audit folder and why it must not be edited by hand (D-0423);
- what Exploration does and does not do (nothing saved, never exported, D-0327).

Today: the page does not exist (`PARTS_TABLES.md` I5); screen texts state old limits (A7) and say "samples" (A8).

### 4.10 Where it runs (place 5 of M593)

- The audit exists only where the app features turn it on (`t3_sandbox_enabled`: the advanced, standalone, developer and qa files), and it requires sessions and export (D-0018; refused at start otherwise) [`rules_app_features_flags.md`]. The static, simple, web-demo and demo-vetinst files have no audit; the static one saves nothing. The export, where it is on, is a browser download and needs no writable place.
- The audit recipe lives in the session folder, in the user's own place (`audit/`; D-0319, D-0340, D-0423). Your words: "as long as it can be saved in session in all deploymenets possibilities and exported in a directory the user can write I think we have our goal done." (D-0422).
- A container with bound paths: the user's place (`user_data` of the deployment) is a bound folder. Writable: sessions are kept. Read-only: as below.
- **No writable place, audit on.** Today the audit is applied in memory and, at Apply, a technical warning says "T3 ghost save failed ... T3 state was applied in-memory but will not survive a page refresh." (`app/handlers/audit_stack.py:1049-1058`) [read]. Your rule asks for "a plain error when the directory cannot be written" (D-0340, the ledger's wording of your answer). Suggestion: when Audit mode opens, the app tests the user's place once; if it cannot write, it says before any work: "This app cannot keep your audit after you close it. Export it before you close." (wording mine). The audit still works, and the export holds the audit recipe, its record and its log, built from the copy in memory: reproducibility holds through the export.

### 4.11 How we will know each goal is reached, and the December demo (place 6 of M593)

**Checks you can do yourself on the demo** (the result on screen or in the export, not that code exists):
- **G1, E2.** In Audit mode on `mlst_bar`, remove `10668076` with a reason, from every result that holds it. Before confirming, the dialog shows "1 observation removed" (or the count) for each such result and "unchanged" for the others. After Apply, the entity is absent from the table of three results you open.
- **Your case D-0499.** Untick the 3 quality results. After Apply, in `qc_reads_horizontal_barplot` the entity is still there WITH its source, year and country; in `mlst_bar` it is gone.
- **G1, reproducible.** Export with both ticks; the README says which part is the original and which the audited; import each part and see the same plots; change one byte of the audit recipe and see the import refuse it.
- **G2.** Remove an entity from a result of `QA_population_zscore`: the dialog asks "before or after"; with "before", it says the z-scores of the other entities change; with "after", it says they do not.
- **G3.** The Publication part holds, for each changed result, the original and the corrected picture; the report's methods line gives the count removed and the reason. After question 2: a table result is exported under its name and equals the table on screen.
- **G4.** The audit offers only removals (if questions 29 and 17 are answered as recommended).
- **G5.** A colleague who did not write the recipe does the first check without help, and says what each line of the dialog means.
- **G6.** The dialog never preselects "before or after"; it ticks a default for the results and says why.
- **E1.** On a small test recipe where a step writes the key in lower case: the dialog shows "still found here".
- **E3.** The same checks on a second shipped recipe.
- **E4.** In BLUEPRINT, open the demo recipe, change nothing, Save: the file is byte-identical, comments kept.
- **E5.** Open `FastP_with_metadata` (no result reads it) in the data preview.
- **E6.** The audit recipe in the session's `audit/` folder and the one in the export are the same file (same hash).

**The December demo.** You agreed on 20 November: "so agreed I will do the demo in 2 weeks" (D-0370); the date follows readiness: "I do not present at the end of the week: we agree on when I can present" (D-0255); no special treatment of files (D-0255). What is in it is your choice. Proposal (mine), from the goals:
- **In:** Exploration (built); the audit on this path: one representation of a step (slice 3), the dialog with results and proof (the new slice 4), Compare with the counts; the export of an audit with its two parts (slice 5) and the report by groups (slice 6); the Gallery as it stands; a short help page with the points of 4.9.
- **After:** a table as a result and the recipe form (question 2; slices 7 and 9); the picker for the story (slice 8); BLUEPRINT's rebuild; the full good-practice page.
- If the new dialog is not ready by the date, the demo shows the audit as built (one result at a time, at its own stage) and says what comes; that choice is yours.

---

## 5. What must be modified

Each item: **keep**, **change** (to what), **drop**, **later**; and the goal that asks for it. Where a change reopens a decision, the line says so as information.

### 5.1 From your plans

**Decisions of the ledger.**

| Decisions | Verdict | What, and why |
|---|---|---|
| D-0102, D-0143, D-0332, D-0329, D-0321, D-0339, D-0040: the audit recipe, a copy; the author's steps untouched; `audit_steps`, `audit_comment`, the id, `audit_of` | keep | the one representation of a correction (G1, E6) |
| D-0333, D-0331, D-0319, D-0340, D-0422, D-0423: the record, the hash, the `audit/` folder in the user's place | keep | trust and re-run (G1, G3) |
| D-0478: the log always exported, with what was shown | keep; it holds the results ticked and how (default or by her), the before-or-after answers, the effects shown | this answers questions 10, 11, 12 and 25 (G1, G6) |
| D-0490, D-0492, D-0389, D-0298, D-0301: the export's two ticks and the two parts | keep | G1, G3 |
| D-0147: original and corrected both visible | keep; both pictures in the Publication part | this answers question 16 (G3) |
| D-0314, D-0362, D-0312, D-0317: Remove step; sessions refused | keep | G1 |
| D-0485, D-0487, D-0489: a table as a result; the comparison in layers | keep; layer 1 (counts) on screen in the dialog and in Compare | G3 |
| D-0491, D-0484: the report by groups | keep; add the count removed per result to the methods line | G3 |
| D-0510, D-0523, D-0513: the metadata joined in tier 1; the three blocks | keep | the clean place for removing an entity (G1) |
| D-0326, D-0327, D-0310, D-0311, D-0361, D-0506: the opening build; Exploration; Table to view; the filters | keep | G5 |
| D-0457: a table no result reads can be viewed and is exported | keep | E5, G3 |
| D-0512, D-0416 point 4: data-agnostic words | keep | E3 |
| D-0495, D-0498, D-0500: the author's side | keep | E4 |
| D-0093, D-0355: the user chooses the node; the user decides the scope | change: the user decides the scope in RESULTS; the app chooses the place and proves it | G5, G6, E2. Reopens D-0093 ("the user need to choose at which point (node) to apply") and D-0355 in part. Question 28. |
| D-0316, D-0346, D-0347, D-0194, D-0359: the dialog of place lines, all ticked; the reach | change: the dialog lists results; the default is by kind (question 4) | G5. Reopens them in part. |
| D-0508, "tick low (early) near the original table" | change: it becomes the app's rule for placing an entity: the end of tier 1 of each metadata join, your D-0509 | G6. The user no longer picks places. |
| D-0508, "Id rather the check is more where you apply it" | change: the effect is measured at each result | G1, E1: the runs showed that "something that by default should not exist" does exist further down (3 plots, C1). Reopens D-0508 in part. |
| D-0501: no per-table warnings downstream; the count at the plot removed | keep the first part; change the second: the measured count per RESULT is shown, as evidence, not as a warning | G3, E1. Reopens D-0501 in part ("The count of rows removed at the plot ... so I think I would removing it"). |
| D-0322: filters and column drops | change: filters and removals by key only | G4: a column is not an observation. Question 29. |
| D-0358, D-0371, D-0448, D-0449, D-0460, as far as they rule a column drop in the audit | drop, if question 29 is (a) | G4 |
| D-0341: the Reshuffle in Audit mode | change: no Reshuffle in HOME; the seed is the recipe's | G3, G4. Question 17. |
| D-0120, D-0145: no plot-style change for now | keep; remove the unmounted code | G4, E6 |
| D-0313: two lists of keys | keep the entity key; the list "columns used to join" is not needed on screen | G5 |
| D-0203: a warning between places when a value does not match one to one | drop under question 28 (a): no places are shown | G5 |
| D-0337, D-0351 to D-0353, D-0356, D-0444, D-0445: the walk's rules for places | keep, as the app's rules for placing a step; their screen lines go | G6 |
| D-0452, D-0454, D-0460, D-0473, D-0486: the joins the app cannot follow YET | keep the limits; on screen only when she answered "before" and the app cannot place the step there ("cannot be written before this join YET") | E1 |
| D-0463: the lineage colours | later, for the picker | E5 |
| D-0451: a table no result reads is a line, ticked | keep, as a line of the results list | E5, G3 |
| D-0415, D-0416: "remove from all the data" | keep, as one button of the results list: everything, before every computation | G4 |
| D-0496, D-0508: the picker, the outline | later: for the story (E5), not on the audit path; "open any table by name" comes first (D-0457) | E5 |
| D-0516, D-0517, D-0525: the recipe form; the one move | keep (question 2) | G2, G3 |
| D-0407 to D-0412, D-0468 to D-0484: the names | keep (one pass with the move) | G5 |

**The questions 1 to 27, and the two new ones.**

| Question | Verdict from the goals |
|---|---|
| 28 (new): the path: results and proof, or the places | yours, first |
| 29 (new): column drops in the audit | yours, with 28 |
| 17: the Reshuffle | yours, reworded: keep it in the audit, or remove it from HOME |
| 4: the default | yours, with 28, reworded in results |
| 2: the recipe form | yours; needed for table results and the one move, not for the audit |
| 26: old sessions | yours, before slice 3 (it depends on sessions only you know) |
| 15: the original recipe in the Publication part | yours, before slice 5 (two of your sentences meet) |
| 1, 3, 5, 6, 7, 8, 9, 23 | dissolve if 28 is (a): no places on screen; the measured effect per result replaces the numbers, notes and colours. If 28 is (b) they stay, and question 1 first needs your reading of D-0451 (which tables are places, `DIFFERENCES.md` A5) |
| 10, 11, 12, 25 | answered by D-0478 and G1: the log holds what was shown, words and facts (10: c); how each result was ticked (11: a, in results); not a cancelled step, "all the steps that are applied" (12: a); one structured file a person can read (25: b) |
| 16 | answered by G3 and D-0147: both pictures in the Publication part (a) |
| 18 | answered by G3 and G5: the result's table, as built (a) |
| 19 | answered by G5: plain words with the stage (c) |
| 20 | answered by G2: dates keep their comparisons, as built (a) |
| 21 | answered by G2 and your "Why Tier 2 refuses ? its still data wrangling" (D-0514): tier 2 allowed (b) |
| 22 | answered by E4 and D-0498: an advice, never a refusal (a) |
| 24 | answered by E6 and D-0507: remove the unreachable upload code (a) |
| 27 | later: no goal needs it now; today's rule stands until a recipe needs a look-up join after a count |
| 13, 14 | later: the picker serves the story (E5), not the audit; "open any table by name" first |

**The slices of `BUILD_ORDER.md`.**

| Slice | Verdict | What changes |
|---|---|---|
| 0, the records agree | keep | also: D-0341's quote and the D-0510 fact (B2 f) |
| 1, the filters follow the table | keep, add | add "open any table by name" in the data preview (D-0457); no answer needed |
| 2, the upload code | change | remove the code; no answer needed (question 24 is answered by the goals) |
| 3, one representation | keep, change | no column drop and no Reshuffle in it (after 29 and 17); HOME's plot and table come from the engine run of the audit copy (its consequence 1); needs question 26 |
| 4, the dialog | replace | the results dialog with the proof of 4.2 and 4.4; needs questions 28 and 4 only; the walk becomes internal |
| 5, the export of an audit | keep, change | both pictures in the Publication part; the count per result in the report; a seed is never written into the author's parts; needs question 15 |
| 6, the report by groups | keep | — |
| 7, the one move | keep | after question 2 and the names |
| 8, the picker | later | after the demo; "by name" moves to slice 1 |
| 9, a table as a result | keep | after question 2; the four places that count only plots as readers |
| 10, the check and the good-practice page | keep, add | the advices of D-0498 and D-0500; the refusal of a result id written twice; the page of 4.9 |
| 11, the preview sentences | done | — |

### 5.2 From the code on `dev`, the built parts one by one

**OK as built** (no change needed for the goals):
- The modes, the header strip, "Table to view", the badges: `app/src/server.py:145-147`, `app/handlers/home_theater.py:1160-1230`, `app/modules/view_badge.py` [inventory]. The words wait for question 19 (answered: plain words with the stage).
- The Filters panel, its pickers and typed values, D-0503 and D-0504 (merged `51be0a46` and `781179e3`) [read: git log].
- The preview sentences (`d2e92547`) [read: git log].
- The opening build: `app/modules/opening_build.py`, `app/handlers/opening_handlers.py` [inventory]: every table built and keyed at opening is the base of the proof.
- Compare for plots: `app/handlers/home_theater.py:755-790` [inventory].
- The right panel that opens with Audit mode (D-0383, D-0385) [inventory].
- The reason gate on Apply; the session saved only on Apply (D-0302) [inventory].
- The session refusals of D-0312 and D-0317 (`app/modules/session_manager.py:214-253`) [inventory].
- The lineage library's live parts: `recipe_graph.py`, `step_effects.py`, `lineage_records.py`, `lineage_sentences.py` (the YET sentence), `plan_book.py`, `app/modules/plan_composer.py` (`compose_plan_book`), `join_keys.py`, `recipe_tiers.py`, `engine_boundary.py`, `action_names.py` [inventory]. Two headers are stale (`recipe_graph.py:55-61`, `step_effects.py:38`): text only.
- The recipe check (ST05 and the other codes) and the load gate (`app/modules/data_analysis_recipe_validator.py`) [inventory].
- The cache keys and `integrity_errors` (`app/modules/cache_keys.py`) [inventory].
- The export's key check (`app/handlers/export_handlers.py:251-319`), all plots exported, the T1 file of every table no plot reads (`:61-80, 1501`), the stage keys and `effective_run.yaml` (`:1649-1690`) [inventory].
- Data Import (`app/modules/data_import_check.py`) [inventory].

**Needs adjusting** (what exactly):
- The key of an exploration filter holds the open plot; it must hold the table viewed: `app/modules/t3_audit_engine.py:69-73`, marked P-B2 (`DIFFERENCES.md` A6; slice 1).
- "Send to Audit" exists only while T3 is viewed: `app/handlers/filter_and_audit_handlers.py:152-155`, marked P-B3. It must start from any table where the observations are seen.
- `libs/utils/src/utils/lineage_walk.py`: OK as a library; it becomes the app's tool for placing a step (the ways to each result, where a column exists, the steps that compute over all observations). Its screen-facing PROVISIONAL choices (P1 groups, P4 and P9 ticks, grey and red lines) are not shown to the user under question 28 (a).
- `app/modules/plan_composer.py`, `compose_candidate_plan_book` (called by tests only): needed for the proof; wire it.
- `app/modules/audit_run.py`, `run_audit` (called by tests only): the engine run of the audit copy; wire it for HOME, the proof and the export.
- `libs/utils/src/utils/audit_copy.py` (the decided form; called by tests only): wire it; teach it table results and derived tables (`audit_copy.py:177`; `recipe_tiers.py:152-161, 182-210, 235-242`); its key-drop part goes if question 29 is (a).
- `libs/utils/src/utils/table_compare.py` (layers 1 to 3; called by tests only): wire layer 1 to the dialog and Compare, layer 3 to the proof (other observations changed), layer 2 on request.
- `libs/utils/src/utils/remove_from_all.py` (called by tests only): keep which tables hold the entity key (D-0500) and the same-name listing (D-0498) as the placement of "all the data"; remove the statements `may_stay`, `may_differ`, `not_written` (false on the demo, TRIAL Q6; against D-0501).
- The held branch `task/remove-from-all-ticked` (`95b6285e`): do not merge as it is: its statements about unticked tables are false [run, the two reviews]. Its `apply(..., ticked=...)`, verified on 127 subsets, can be taken into the placement without `_flow` and `unticked_places`.
- `app/modules/plot_seeds.py:156`, `bake_plot_seeds`: never write a seed into the author's parts of the original or the audit recipe. With no Reshuffle in HOME, a seed is the recipe's or the fixed default, recorded in `effective_run.yaml` (built).
- The recipe check: refuse a result id written twice in one recipe (A23); count derived tables and table results as readers (S07, J14) under form 3; AU04 goes if question 29 is (a).
- The report written in code (`export_handlers.py:1813-2112`): by groups (slice 6); the count removed per result; the original pictures beside the corrected ones.
- `effective_run.yaml`: add the hash of the audit recipe (D-0333); retire the name `decision_hash` (D-0345).
- The bundle import (`app/modules/bundle_importer.py:252-273`): the user's own place, name and date, an existing name refused (D-0435); check the audit recipe's hash (today "not_checked").
- The message when the user's place cannot be written (`app/handlers/audit_stack.py:1049-1058`): plain words, when Audit mode opens, not at Apply (4.10).
- The screen texts that state old limits or say "samples" (`home_theater.py:1479`; `filter_and_audit_handlers.py:674-676, 694, 997, 1002-1007`): they go with the parts they describe.
- BLUEPRINT's Apply and Save (`app/handlers/blueprint_handlers.py:1155-1196, 1255-1346`) [inventory, the seven-point check]: no silent loss; comments kept; no replacement by mistake (D-0495). Its own plan; not on the demo path.

**Must be replaced:**
- HOME's store of audit nodes and their application in memory (`app/modules/session_manager.py:56-106`; `app/modules/t3_audit_engine.py:771-791`, `audited_frame`; `home_state["t3_audit_steps_by_plot"]`): by the audit copy and the engine run (slice 3).
- The propagation modal "This plot only / All plots / All plots except" (`filter_and_audit_handlers.py:1044-1195`): by the results dialog (slice 4).
- The trash per node that removes every copy (`app/handlers/audit_stack.py:530-534, 627-682`): by "Remove step" (D-0314).
- The opening of a session whose original recipe was edited (`app/handlers/session_handlers.py:594-602`): by a refusal (D-0362).
- `t3_steps.yaml` (`export_handlers.py:1510-1546`): by the audit recipe, its record and its log.
- The export's one check box (`export_handlers.py:675-692`): by two ticks and one button (D-0298, D-0301).
- The audit's list of join keys used for the warning (`session_manager.py:125-135`): by the entity key (D-0500).

**Must be removed:**
- The join fork of the reproducibility bundle: `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197-290`, `build_mode2_recipe`, and its call `export_handlers.py:1554-1628`.
- The two older forms in the session file (`session_manager.py:509-523, 572-576`), with question 26.
- The column drop sent to the audit (`filter_and_audit_handlers.py:861-925` and the control "Columns (drop unselected via audit)") and the drop gate's audit uses (`libs/utils/src/utils/key_drop.py`, `recipe_check.py:571-578` AU04, `audit_copy.py:199-208`, the restore at `session_handlers.py:673`), if question 29 is (a). [read: the gate serves only audit steps]
- The Reshuffle button (`app/handlers/home_theater.py:877-899`), if question 17 is as recommended.
- The plot-style code that no screen reaches (`app/handlers/audit_stack.py:815-845`; the panel is not mounted, `home_theater.py:2230-2234`) [read].
- The title "My Adjustments" (`audit_stack.py:460`) and the stale comments of `home_theater.py:287` and `orchestrator_helpers.py:53`.
- The unreachable recipe upload code (`app/handlers/ingestion_handlers.py:38-55`) and its reachability test's statement.
- The report template that no code loads (`app/assets/report_template.qmd`).

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

---

## 6. What hinders the goals: decisions and strategy

Said plainly; each with your words and the goal it hinders. "Reopens" is information, not a reason to keep a path.

1. **The user chooses places in the recipe (a decided strategy).** Your words: "the user need to choose at which point (node) to apply" (D-0093); "That is the choice of the user - because the user decide the scope" (D-0355); "but ok we tick low (early) near the original table - so by default it is propagated in the lineage" (D-0508).
   - It hinders G5 and G6: the place is a technical matter, not the user's context. You saw the cost yourself: "the user will have to learn that its not the sample that stays but where the change is applied that is a big difference - so the user will have to learn a bit of datascience" (D-0508). Your own case is in results (D-0499).
   - It hinders G1 and E2: with one reading of "tick low", the removed entity stays in 3 plots of the demo with its metadata emptied, and the dialog would not say so [run, C1].
   - It creates questions 1, 3, 5 to 9 and 23.
   - Note: "tick low" was decided after the trial of "remove from all the data" (the facts put to you for D-0501 came from it), where ticking the earliest places of all 11 original tables gave the same tables as ticking all 27 places, on all 73 tables compared [run, `tmpAI/panel/default_ticks/TRIAL.md` Q1, main tree]. The study then applied it to the ways of ONE plot, where it does not give the same result. The evidence you saw does not carry over.
2. **The check only where the step is applied.** Your words: "Id rather the check is more where you apply it - knowing it will affect the downward recipe than actually trying to capture the removal of something that by default should not exist" (D-0508); "The count of rows removed at the plot is also a consequence when no change is applied at T3 ... so I think I would removing it" (D-0501).
   - Your reason against downstream warnings holds: they were read from the recipe, they were false, and there were many. A count measured at each result is not such a warning: it is the evidence a reviewer asks for (G3) and the only way to see a correction that did not reach a result (E1).
3. **Column drops in the audit.** Your words: "A : for now yes only filter and drops" (D-0322).
   - A column is not an observation (G4). Keeping drops keeps the drop gate (`key_drop.py`), the checker's AU04, five decisions about drops (D-0358, D-0371, D-0448, D-0449, D-0460) and the control "drop via audit". A column that should not be shown is the author's choice: the last `polars_select` of the recipe (D-0034).
4. **The Reshuffle in the audit.** Your words: "A - but then we need to be able to add it as a step at the correct place in audit" and "this reshuffling is not critical for now but a good thing" (D-0341).
   - A new random arrangement removes no observation (G4). A picture chosen among random arrangements is harder to trust (G3): a reader cannot tell whether it was picked to look better. It needs a new kind of step (question 17), and until then the decided audit recipe cannot carry its seed (section 3, G3 point 4).
5. **Statements read from the recipe instead of measured (a builders' strategy, not yours).** The library's "may stay" lists and the held branch's "stays" / "removed upstream" were false [run, the two reviews]. You warned of this: "right now the old things that exist are taken again because they are not build and this mixes with the decisions of what should happen" (D-0507). Hinders E1.
6. **The order of the questions (the study's strategy, not yours).** Question 1 was put first, although it exists only under the strategy of point 1; questions 10 to 12, 16 and 18 to 25 were put to you although your goals and earlier words answer them.
7. **Your own words of the same day support this list:** "So I think we are complicating a lot of our work putting warnings that should not be there - because they are natural consequences of the recipe" (D-0501). Measured against "small correction ... where some "observations" must be removed" (D-0528), points 1 to 4 are machinery that a small correction by removal does not need.

What does NOT hinder (examined): the audit recipe form (D-0332), the record and the folder, the two-part export, the metadata join in tier 1, form 3, the names pass, "remove from all the data" as an explicit act (D-0416), Exploration as built.

---

## 7. The questions that remain yours

Only those that change what is built, in the order they are needed. Their full text, with what you would see, is in part 8 of `WHOLE_PICTURE.md`.

1. **Question 28 (new): the path.** Does the user choose the results, with the app placing the step and proving its effect (this path), or the places in the recipe (the decided dialog)? It decides whether questions 1, 3, 5 to 9 and 23 exist.
2. **Question 29 (new): column drops in the audit.** Keep, or leave the audit to removals of observations?
3. **Question 17 (reworded): the Reshuffle.** Remove it from HOME, or keep it in the audit with a step of its own?
4. **Question 4 (reworded in results): the default.** For an entity, every result that holds it; for a condition on another column, the result where you started?
5. **Question 2: the recipe form.** Needed for table results and the one move of the demo recipes; not for the audit.
6. **Question 26: sessions saved before the change.** Before slice 3.
7. **Question 15: the original recipe in the Publication part.** Before slice 5.

Later: 27, 13, 14. Answered by the goals (you may still object): 10, 11, 12, 16, 18 to 22, 24, 25. Dissolved if 28 is (a): 1, 3, 5 to 9, 23.

---

## 8. Earlier conclusions of the study that this review changes, and why

1. **The audit dialog.** The study designed a dialog of places in the recipe, with default ticks. Changed: a dialog of results, with the app placing the step and proving its effect. Why: G5 and G6, and the runs of C1.
2. **Question 1 and its recommendation (b).** Changed: no longer a question for you if 28 is (a); reading (b) becomes the app's rule for placing an entity, proven by the run. Why: G6.
3. **"Tick low".** The study applied it to one plot's lineage. Changed: the evidence you saw was the trial of "remove from all the data" (identical results), which does not carry over to one lineage.
4. **No count per result.** The study followed D-0501. Changed: a measured count per result is shown, as evidence. Why: G3 and E1.
5. **Column drops and the Reshuffle.** The study kept them (question 17 was "later"). Changed: proposed out of the audit. Why: G4, G3.
6. **The seed in the export.** Not seen by the study: removing the join fork (slice 5) also removes the only replayable carrier of a Reshuffle seed, and the decided audit recipe cannot hold it in the layers.
7. **The order of the questions.** "Now" was 1, 2, 27. Changed: 28, 29, 17, 4, then 2; 27 moves to later; eleven questions are answered by the goals.
8. **The picker.** The study tied it to the audit's start (question 13). Changed: the audit needs no picker in this path; "open any table by name" comes first; the picker serves the story, later.
9. **Slice 2.** It needed your answer. Changed: remove the code; the goals answer question 24.
10. **The places that count only plots as readers.** Kept, and made part of slice 9 and of the proof.

---

## 9. Evidence, and what I did not check

- **Ledger lines read** (each opened in the ledger, fields printed): D-0004, D-0008, D-0015, D-0018, D-0021, D-0050, D-0056, D-0065, D-0077, D-0093, D-0102, D-0108, D-0117, D-0125, D-0143, D-0147, D-0168, D-0194, D-0195, D-0199, D-0255, D-0268 (her words), D-0271, D-0313, D-0316, D-0324, D-0331, D-0332, D-0340, D-0341, D-0346, D-0355, D-0370, D-0389, D-0400, D-0401, D-0416, D-0422, D-0423, D-0449, D-0450, D-0457, D-0461, D-0478, D-0485, D-0487, D-0490, D-0492, D-0495, D-0496, D-0498 to D-0501, D-0507, D-0508, D-0512, D-0514, D-0516, D-0521, D-0527, D-0528. Other numbers are cited from the study's files, which its reviews checked.
- **Code read by me** on 22 November: `app/handlers/export_handlers.py:1559-1572` and the seed lines found by search; `app/modules/plot_seeds.py:156-181`; `app/handlers/audit_stack.py:815-845, 1040-1060`; `libs/utils/src/utils/recipe_check.py:565-592`; the `key_drop` lines of `libs/utils/src/utils/audit_copy.py`. Every other code claim is [inventory].
- **Runs:** none by me in this pass. The numbers on the demo are the study's runs and its reviews' (`DIFFERENCES.md` C1; `TRIAL.md` of the main tree).
- **Not checked:** the path of section 4 is a design; its dialog does not exist and was not run. The rule for placing an entity was run only as "reading B" with places listed by hand. Whether the demo has other steps that compute over all observations was not searched. No browser was used. I read only block M593 of the agent channel, as the coordinator asked, and not `tmp.md`.
