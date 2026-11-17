Exploration report. Nothing in it is decided unless a ledger number is given. Status: Nothing is decided and nothing is built (as written in the report). Written: 2026-11-16. Source: tmpAI/panel/audit_rules/PROPOSALS_for_eve.md. Copied here on 2026-11-17.

Paths inside the body that point to tmpAI/ working files are local (not in git) and stay as written.

---

# The rules of the audit: proposals for Eve

Written 2026-11-16 by the coordinator from three viewpoints (data scientist, architect, user). These are proposals. Nothing is decided and nothing is built.

The viewpoints worked from two runs of your mental model on recipe `1_test_data_ST22_dummy` with the real engine:
`tmpAI/panel/audit_model/scenarios_report.md` and `tmpAI/panel/audit_model/scenarios_report_round2.md`.

None of the recommendations reopens a decision of yours (ledger D-0194 to D-0203).

## Read this first: what would change a result silently

1. **A removal written as a condition does not remove the samples everywhere.** "country is not Norway", written at the metadata, leaves the 28 Norway samples in 7 tables and 3 plots. Those tables are built with a left join: the join keeps every sample of the other side and leaves the country empty. Ticking every place does not repair it when rows with no value are kept.
2. **A check that looks by property sees nothing.** After Apply it finds "0 Norway" while 28 samples are still drawn with an empty country.
3. **A removed sample comes back as "0 genes".** 21 samples removed at the ResFinder table stay in the table of genes per sample, 20 of them with a count of 0. A removed sample then looks like a sample with no resistance gene.
4. **A step at an earlier place can miss a later place.** When the recipe changes the values in between (a recoded value, a rounding step, a value computed from the other rows), the earlier step does not do at the later place what the user selected there. In a test copy, a tick at T1 with the value seen at T2 removed 0 of 42 rows, with no message.
5. **A typed value of the wrong kind selects nothing, silently, today.** A decimal typed for a whole-number column selects 0 rows. This is today's code; your decision D-0202 is not built yet.

One tension with a line you decided today. "The node you tick expresses the intent" (D-0200) is read as: all places of a chain ticked = the samples are removed. The run shows this is true only when the step is written as a list of sample ids. So the dialog has to say which form it writes. No decision covers that (question 1 below).

## The questions, with the options

### 1. A removal of samples: written as a condition, or as the list of sample ids?

| Option | Who recommends it | For | Against |
|---|---|---|---|
| A. The user chooses between the two forms, with the consequence shown; neither is chosen by the app. One action in the recipe either way. | Scientist, user | The user knows what will happen. It respects "the app does not choose for the user" (D-0201). | One more choice in the dialog. |
| B. Both, placed by the app: the condition at the places that have the column, the sample ids at the places that do not. | Architect | Removes everywhere. The recipe stays readable where it can. | The app decides the placement; a list of ids does not carry over to new data. |
| C. Always the list of sample ids. | (alternative) | Always removes everywhere. | The recipe becomes hard to read. The list is frozen: on next week's data the ids match nothing or miss new samples of Norway. Measured size: 28 ids are half a kilobyte; 5000 ids at 27 places would be almost 2 megabytes. |
| D. Always the condition. | Nobody | Readable; works on new data. | 16 places keep the samples; the result is not what the user meant. |

All three agree on two points, whatever you choose:
- Before Apply, the dialog says per place how many samples stay, and whether they stay with an empty value.
- After Apply, the check counts by sample id, never by the property.

Recommendation (the coordinator's, not a decision): A. It is the only option where the app neither hides the consequence nor chooses.

### 2. Your idea: only the earliest ticked place of a chain writes the step

The runs: a step at T1 gives exactly the same rows as ticking T1, T2 and the plots of the same table (52 of 52 cases), as long as the recipe does not change the column in between. It does not hold after a recode, a rounding step, a value computed from other rows, a column that exists only later, across a left join, or on another chain.

| Option | Who | For | Against |
|---|---|---|---|
| A. Write every ticked step. Show nothing as "covered" for now. | Architect, scientist | Always correct. A second step in the same chain changes nothing (identical tables). | Duplicate steps in the audit_recipe. |
| B. Show a later place as "same rows removed by the step at T1" and do not write it, but ONLY where the app can prove it from the recipe (the steps in between do not touch the column and work row by row). Everything else stays ticked and is written, with the reason ("the values change at T2"). | User (wording), architect (as the only safe form of your idea) | Shorter audit_recipe; the user sees why. | A wrong "covered" would be silent. 12 of the 79 steps of recipe 1 cannot be read from the recipe (a new column built by a formula); they would always count as "not covered". More to build and to test. A step that is not written cannot be checked again when the recipe changes. |

Recommendation: A now. B can be added later, with a test on every shipped recipe that "covered" always means identical tables.

### 3. The two intents: remove samples from the data, or hide a value in one plot

All three: the same action in the recipe; the place says the scope (T1 = the data; T2 = this table and its plots; T3 = this plot only). What differs is what the user is shown.

| Option | Who | For | Against |
|---|---|---|---|
| A. A visible choice at the top of the dialog: "Whole chain: removes the samples" or "Only this plot: hides the value". It sets the ticks; the user can still change them. | User | The two intents are named in the user's words. Nobody removes 8 samples from 41 places by accident. | It sits beside your decision that everything is ticked when the dialog opens (D-0194): the dialog would open on "whole chain", which is the same thing. |
| B. Everything ticked, and a hint: "untick the places where you do not want it". | (alternative) | Nothing new. | The user viewpoint: too easy to miss. |

All three also say: the plot and the audit points file print the scope in words. "Removed from the data: 28 samples." "Not shown in this plot: 8 samples of 2023 (34 of 42 shown); still in the table." A warning with the count when a small group is hidden, never a block.

Recommendation: A.

### 4. A removed sample that stays with a count of 0

All three: tell the user, at that table: "20 samples show 0 genes because they were removed in the ResFinder table; they were not measured as 0." The scientist adds: the correct result is that these samples are absent, not 0. Whether the app should also remove them there is the same question as question 1 (a removal by sample id at that table does it).

### 5. The lineage of a column (your question: "it is still the same lineage, no?")

The runs: nothing follows a column through a rename or a computed column today. In recipe 1 one piece of information has three names (`VF_gene`, `Selected_Virulence_Genes`, `selected_virulence_genes`), and one name covers two different columns (`phenotype`, `value`). Your example "numbers at T1, text at T2" is two columns in recipe 1: `year` stays a number; `year_label` is a new text column built from it.

| Option | Who | For | Against |
|---|---|---|---|
| A. The app reads the columns and their types at every place from the engine itself (exact; 56 places in under 2 seconds). It follows a rename only where the recipe states it ("renamed from VF_gene"). Everywhere else it says: "a column named X exists here; the app cannot tell whether it holds the same information." | All three | Honest. No second copy of the engine's logic. No silent miss for stated renames. | A column built by a formula is not followed; the user is told so. |
| B. As today: search by name only. | Nobody | Nothing to build. | Misses the three-names case silently; offers two different columns as one. Against "the whole lineage is really searched" (D-0195). |

Flag: an older design note (2026-11-12) says "renames are not tracked, the user chooses the new name". It has no ledger number. Option A changes it. You should confirm.

### 6. Typed values and the warning "two values become one" (D-0202, D-0203)

Your two questions were answered by running: 2002.0 and 2002.5 are the same at T2 only, after a visible rounding step (the engine refuses a cast that would drop the decimals). No tracing of rows is needed: each place evaluates the condition on its own data.

Architect's recommendation: one function converts the typed value to the type of each place, checks that nothing is lost, and refuses with a plain message otherwise; the dialog shows "rows matched here" per place, so a zero is visible. For the warning: compare the two places by a key when the table has one (exact), else compare the distinct values, else say "cannot be checked" and never "ok".

One point to confirm: a decimal typed for a whole-number column is refused for "equal", "not equal" and lists, but kept for comparisons such as "at least 8.5" (which works today and is meaningful).

### 7. Rows with no value

No decision exists. Today one tick ("keep the rows with no value") applies to the whole step. The scientist: when the same step is written at several places, the choice must be visible per place and recorded in each step; one value for all places is a silent choice, and it is what makes "everything ticked" fail in the run.

## The order the architect proposes for the audit of the new design

1. The one function for typed values, and the two readers corrected.
2. The engine reads the steps of a plot (T3). It does not today.
3. The lineage with the columns of every place.
4. The audit_recipe file (a copy with the steps added).
5. The counts, the check after Apply by sample id, the warning.
6. The dialog last.

## What you are asked

1. A removal of samples: the user chooses between the condition and the sample ids, with the consequence shown (question 1, option A)?
2. Write every ticked step for now, and leave "covered by T1" for later (question 2, option A)?
3. A visible choice of intent at the top of the dialog (question 3, option A)?
4. The lineage of a column: follow stated renames, and say honestly where identity is not known (question 5, option A)? This changes the older note "renames are not tracked".
5. A decimal typed for a whole-number column: refused for "equal" and lists, kept for comparisons?
6. Rows with no value: one choice per place, recorded in each step?

Not checked by the viewpoints: other recipes than recipe 1; a recipe with a pivot; the dialog itself, which does not exist yet.
