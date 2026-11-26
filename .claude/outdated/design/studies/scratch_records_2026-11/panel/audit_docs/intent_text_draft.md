# Draft text: "the node you tick expresses the intent" (INTENT-TEXT-DRAFT-1)

Status: DRAFT for Eve to read. Not decided text. Nothing here is built.
Basis: D-0200 (the sentence goes into the user docs and the user help, with better examples), D-0201 (the app cannot know the intent; it makes the user aware; it does not choose).
Numbers are from her run on the real recipe (`tmpAI/panel/audit_model/scenarios_report.md`, S1, S9, S10). The app would compute them for any recipe.

Words used in the drafts: "node" and "T1, T2, T3" appear in the technical version; "place", "first table", "table of the result", "the plot's data" in the plain version. Section C gives both. She chooses.

---

## A. The help text in the dialog (ten seconds)

### A1. One sentence

Technical: The node you tick is the intent: tick every node to remove the samples from the whole lineage, tick only T3 to hide them from one plot.

Plain: The place you tick is what you mean: tick every place to remove the samples everywhere, tick only the plot's data to hide them from that plot.

### A2. Three sentences

Technical: The node you tick expresses the intent. Tick every node of the lineage to remove the samples everywhere; tick only the T3 node of one plot to hide them from that plot and keep them in the data. The app cannot know which you mean; it shows you what each choice changes.

Plain: The place you tick is what you mean. Tick every place to remove the samples everywhere; tick only the plot's data to hide them from that plot and keep them in your tables. The app cannot know which you mean; it shows you what each choice changes.

### A3. A short box (six lines)

Technical:

```
What you tick is what you mean.
  Every node ticked   : the samples leave the whole lineage.
  Only T3 of one plot : the samples stay in the data; that plot does not show them.
Select as early as possible in the lineage: at T1 you see all samples, at T2 the recipe may already have removed some.
The app cannot know your intent. Check the step shown before Apply.
```

Plain:

```
What you tick is what you mean.
  Every place ticked        : the samples leave all your tables and plots.
  Only the plot's data      : the samples stay in your tables; that plot does not show them.
Select as early as possible: in the first table you see all samples; later tables may have lost some already.
The app cannot know what you intend. Check the step shown before Apply.
```

---

## B. The docs section (user guide, one screen)

### B (technical version)

#### What "the node you tick" means

When you add an audit step, the dialog lists the nodes where the step can be applied: the tables of the lineage (T1, T2) and the plot's data (T3). All candidate nodes start ticked; you untick the ones you do not want. **The node you tick expresses the intent.** The app cannot know beforehand what you mean. It can only make you aware of the cases that can surprise you. The choice stays yours.

#### Example 1: remove bad samples from the whole lineage

Sample quality is poor in 28 samples from Norway. You want them gone from every table and every plot.

- Tick every node. Select the samples as early as possible in the lineage.
- Why early: at T1 you see 28 Norway samples. At T2 you see 21, because a step of the recipe (years 2023 to 2025) has already removed the 7 Norway samples of 2022. If you select at T2, you select 21 samples. The 7 others stay in the other tables and in 14 of the 17 plots.
- Before you press Apply, read the step the dialog shows: the rows and the samples before and after.

#### Example 2: hide a value from one plot

The year 2023 has 8 samples of 42. The bar is too small to mean anything, and it makes the other years harder to compare.

- Tick only the T3 node of that plot.
- The plot then draws 34 of the 42 samples. The plot should say what it left out, for example "Year 2023 not shown: 8 samples".
- The 8 samples stay in your tables and in the other plots. Nothing else changes.

#### Things that can surprise you

- **The count depends on where you look.** 28 at T1, 21 at T2. Look at: the node where you select.
- **A table without the column cannot be ticked for that property.** You cannot tick "country = Norway" in a file that has no country column. Look at: which nodes the dialog offers.
- **The recipe can change a value between two nodes.** If the recipe turns "Norway" into "Norge" at T2, what you select at T2 does not match at T1. A computed value (for example a z-score) also differs between nodes. Look at: the value at each node.
- **Two values can become one.** Two values at T1 may be one value at T2. Look at: the warning, if the dialog shows one.
- **Another table can keep the samples.** A table that reads the metadata as a lookup may keep the samples with an empty value. Look at: the tables after Apply.
- **Hiding is not removing.** A value hidden in one plot is still in the data and in the other plots. Look at: the other plots.

### B (plain version)

#### What "the place you tick" means

When you add an audit step, the dialog lists the places where the step can be applied: your tables, from the first table to the table of the result, and the plot's data. All places start ticked; you untick the ones you do not want. **The place you tick is what you mean.** The app cannot know beforehand what you intend. It can only make you aware of the cases that can surprise you. The choice stays yours.

#### Example 1: remove bad samples everywhere

Sample quality is poor in 28 samples from Norway. You want them gone from every table and every plot.

- Tick every place. Select the samples as early as possible.
- Why early: in the first table you see 28 Norway samples. In the table of the result you see 21, because a step of the recipe (years 2023 to 2025) has already removed the 7 Norway samples of 2022. If you select there, you select 21 samples. The 7 others stay in the other tables and in 14 of the 17 plots.
- Before you press Apply, read the step the dialog shows: the rows and the samples before and after.

#### Example 2: hide a value from one plot

The year 2023 has 8 samples of 42. The bar is too small to mean anything, and it makes the other years harder to compare.

- Tick only the plot's data.
- The plot then draws 34 of the 42 samples. The plot should say what it left out, for example "Year 2023 not shown: 8 samples".
- The 8 samples stay in your tables and in the other plots. Nothing else changes.

#### Things that can surprise you

- **The count depends on where you look.** 28 in the first table, 21 in the table of the result. Look at: the place where you select.
- **A table without the column cannot be ticked for that property.** You cannot tick "country = Norway" in a file that has no country column. Look at: which places the dialog offers.
- **The recipe can change a value between two places.** If the recipe turns "Norway" into "Norge", what you select later does not match earlier. A computed value (for example a z-score) also differs. Look at: the value at each place.
- **Two values can become one.** Two values in the first table may be one value later. Look at: the warning, if the dialog shows one.
- **Another table can keep the samples.** A table that reads the metadata as a lookup may keep the samples with an empty value. Look at: the tables after Apply.
- **Hiding is not removing.** A value hidden in one plot is still in your data and in the other plots. Look at: the other plots.

---

## C. Short glossary: the words on the screen (she chooses)

| Idea | Technical word | Plain word | Note |
|---|---|---|---|
| Where a step can be applied | node | place | "Node" is the word of the design. "Place" needs no explanation. |
| The raw joined table | T1 | the first table | "Raw (T1)" is already in "Data to show". |
| The table of the result | T2 | the table of the result | "Result (T2)" is already in the header. |
| The data a plot reads after the audit | T3 | the plot's data | |
| The chain from the first table to the plot | lineage | the chain of tables | "lineage" is used in the app today. |
| The recipe you opened | original_recipe | the original recipe | Names decided (O5: screen words open). |
| The copy that holds your steps | audit_recipe | the audit recipe | Same. |
| The choice you make by ticking | intent | what you mean | |

Her choice needed: place or node; T1/T2/T3 or words; one word for "lineage". The two versions in B are written so that you can take either, or mix them.

---

## Left out because it is not decided

- Whether a removal is written as a condition (for example country != Norway) or as a list of sample ids. The texts say "the samples leave", not how it is written.
- Whether a later place is shown as "covered" by an earlier one. The word and the idea are not used.
- A choice of intent at the top of the dialog (for example two buttons "remove samples" and "hide from this plot"). The texts describe ticking only.
- The exact wording of the caption on a plot. "Year 2023 not shown: 8 samples" is marked "for example"; her example was "year xx not shown so few samples removed from the plot" (D-0199).
- That the dialog shows a count per node, or the warning for two values that become one. D-0203 decides the warning; the screen is not built, so B says "if the dialog shows one".
- That the dialog lists the tables where the step has no effect, or that it shows how many plots keep the samples. The "14 of the 17 plots" is a fact of the run, told as a story, not as a promise of a display.
- The rule "only the earliest ticked node writes the step" (her idea, not decided).
- What happens with "na" (rows with an empty value) for a property step ticked at several places: no decision exists (D-0165); the "another table can keep the samples" line states the fact only.
- Reading the sentence "what each choice changes" in A2 as a promise of a preview: the only decided display is the step before Apply, with rows and samples before and after (first page point 7 of the intent document, confirmed by her).

## Whose sentences

Her own words:
- "the node you tick expresses the intent" (D-0200: she confirms the review session's sentence with "Exactly"; the sentence is the review session's wording).
- "we cannot know before the intend of the user" / "make the user aware of the possible got you problems" / "we cannot make the choice for the user" (D-0201), used as: the app cannot know the intent; it makes the user aware; the choice stays yours.
- "you need to do that as early as possible in the lineage" (D-0197), used as: select as early as possible.
- Her example of hiding a value: "year xx not shown so few samples removed from the plot" (D-0199), used as the caption example.
- Her figures and the idea of 28 at T1 against 21 at T2 "due to the other events in between" (D-0197).
- Her choice of default "all candidate nodes ticked" (D-0194).
- "you cannot tick country = Norway at a table without the column" (D-0196).
- "it warns when a value does not correspond one-to-one" (D-0203).

My sentences (not hers): all the headings, the two examples written as stories, the A1 to A3 texts, the glossary table, the "Look at:" lines, the "Things that can surprise you" list (the cases come from the run and from D-0198, D-0196, D-0203; the wording is mine), the numbers 34 of 42, 8 samples, 7 samples of 2022 and 14 of 17 plots (from the scenario run, not from her).
