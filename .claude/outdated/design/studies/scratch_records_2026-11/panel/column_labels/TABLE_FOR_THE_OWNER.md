# Display labels of columns: what exists, what would have to translate, options (a study; nothing built)

For the owner. Written by the coordinator, 2026-11-20, from a read of the code on dev by a scout (READ only) and the label trace of 2026-11-18 (`tmpAI/panel/label_trace/`, run in a browser then). She decides. The question of labels in the keys of the stored tables (Q-A1) follows from this.

Her words: "the label I think is the label shown in the table (ui) ... unsure for plots I think we had said we should use labs ... (also for the filters and column selection - we might need a little translation here between what is shown to the user and the filters by using the labels) --- use case: in the data there is 'AMRFinder / predicted phenotype from Database X' and we want the display label to be easier 'Predicted Phenotype'".

## Her use case today: half of it already works
A recipe can already write this for a column of a source table:
```yaml
predicted_phenotype:                                   # the name used everywhere in the recipe
  original_name: "AMRFinder / predicted phenotype from Database X"   # the header in the data file (exact match)
  type: String
  label: "Predicted Phenotype"                          # the display label
```
- `original_name` WORKS: the import reads the long header and renames the column to the short name; every step, filter, plot and export then uses `predicted_phenotype`. No rename step is needed.
- `label` EXISTS but is shown in ONE place only: the field card of Blueprint. HOME, the filters, the plots, the audit and the export never read it.
So today the user of HOME sees `predicted_phenotype` everywhere, never "Predicted Phenotype".

## Where the user sees what today (READ; preview headers from the browser trace)
| Place | Shows |
|---|---|
| HOME data table, column headers | the name (`predicted_phenotype`) |
| HOME column selector | the name |
| Filter form, column box | the name and its type |
| Audit drop list; audit step shown in the panel | the name |
| Plot axes and legends | the name, unless the plot's `labs` layer types a text by hand |
| Group tabs and plot tabs | the label (`ui_label`) |
| Blueprint field card | the label AND the name |
| Export: data files, audit steps file, recipe | the name |
| Export report headings | the plot's title |

## The labels a recipe has today, and who reads them
| Label | Read by |
|---|---|
| The recipe's own `label` (under `info`) | HOME's banner. |
| A group's and a plot's `ui_label` | the tabs, the lists of plots, the report. |
| A table's `label`, a join's `label` | **nobody** (only the check that it is there). The screens show the table's id. |
| A join's `labels` (a list "column: display text") | **nobody.** |
| A column's `label` (in `input_fields`) | Blueprint's field card only. |
| A plot's `labs` (title, x, y, legend) | the figure. |

## Records that do not agree (to settle with this decision)
- 2026-11-16 (D-0171): "The label fields determine what is seen in the plot (for example mlst is seen as MLST)."
- 2026-11-18 (D-0253): the text of a figure (axis, legend, title) is written ONLY in the `labs` layer.
- The format page (DEC22) says axis and legend titles default to the column's label and that this is built; the code does not do it.
Her sentence of today ("for plots I think we had said we should use labs") matches D-0253.

## Options
| | Option | What she sees | For | Against |
|---|---|---|---|---|
| A | **As today** | Names everywhere in HOME; the label only in Blueprint. | Nothing to build. What is shown is exactly what is filtered and exported. | Her use case is not met: the short name is readable (`predicted_phenotype`) but it is not the display text she wants. |
| B | **The column's label is shown in HOME wherever a column is offered or headed**: the table headers, the column selector, the filter form, the audit dialog. The real name stays the value used: filters, audit steps, the audit recipe and the export keep `predicted_phenotype`. Plots: unchanged (text only from `labs`). | "Predicted Phenotype" in the table and the lists; the name on hover or in brackets. | Her use case, with the "little translation" she describes, and the app already has the pattern (the filter's value list shows a text and stores the real value; the plot lists show a label and store the id). Results cannot change: a label is display only. | A plot's axis still says `predicted_phenotype` unless its `labs` types the text, so table and figure can show different words for one column. Columns MADE by a step (a rename, a new column, a count) have no label: they show their name. |
| C | **B, and a plot's axis and legend take the column's label when its `labs` says nothing** | The same words in the table and on the figure, without typing them twice. | One place to write the display text. | It changes her decision D-0253 (figure text only in `labs`) and it changes the pictures of existing recipes wherever a label differs from the name (the picture proof would show it; each difference is then intended, but it is a change of results on screen). |
| D | **B, and the recipe can also label columns made by steps** (the join's `labels` list, which exists and is read by nobody, becomes the place: "column: display text" for the columns of a table or join) | Derived columns get display text too. | Completes B. | One more place to keep in step; needs the rule "which wins" when a column has a label from its source table and from the list. |

## Points that hold for B, C and D
- **Two columns with the same label** in one table (nothing checks it today): the lists would show two identical lines. Ways: the check refuses equal labels in one table; or the list always shows "Label (name)". My view: show "Predicted Phenotype (predicted_phenotype)" in lists where one must choose, the label alone in table headers, and let the check warn (not refuse) on equal labels.
- **The export keeps the real names** in every data file and in the audit steps (so a rerun works and the recipe stays the one truth). The report can carry a small table "name, label" so a reader can match them.
- **The audit dialog** shows the label with the name, because the step is written with the name.
- **The keys of the stored tables (Q-A1):** if a label is display text, it must NOT rebuild a table. Today changing the label of a table, a join or a column rebuilds that table and everything built from it (the rows come out identical; tried on 2026-11-18: 7 tables rebuilt). So with any of A to D the answer to Q-A1 is: take the labels and descriptions out of the keys. One place in the code.
- **Table and join labels read by nobody:** either they get shown (in the Source list of the new data choice, in the audit dialog's list of places: "Summary" instead of the id) or they are noise. With the new Source list and the coming audit dialog they have a natural use.

## Recommendation of the coordinator
**B now, with the table and join labels shown where a table is offered (the Source list, the audit dialog's places); Q-A1 = labels out of the keys. C only if she wants the figure to follow without typing, knowing it changes D-0253. D later, when a real recipe needs it.**

## Points that are hers
1. A, B, C or D.
2. In lists: "Label (name)", or the label alone with the name on hover.
3. Equal labels in one table: warn, or refuse.
4. Q-A1: labels and descriptions out of the keys of the stored tables (follows from "a label is display text").
5. Which of the three records on plot text stands (my reading of her words today: D-0253, `labs` only; then D-0171 and the format page's sentence are corrected).
6. Still pending from 2026-11-18: which `label` keys are renamed `ui_label` (she said then that table and join labels are "ui_label" because they are shown in the ui, and that the column label is fine).
