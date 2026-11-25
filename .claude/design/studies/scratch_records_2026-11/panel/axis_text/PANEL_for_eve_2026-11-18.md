# Question 13: the axis text the app adjusts by itself. Panel result for Eve

Coordinator, 2026-11-18. The panel recommends. Eve decides. Nothing is built.
Facts and pictures: `FACTS.md`, `INDEX.md` and the 21 contact sheets in `sheets/` of this folder.

## Flagged first

- **A result changes silently today.** A recipe author who writes an axis text size through `theme_custom`, a named theme or `plot_defaults` loses it with no message (measured: 14 becomes 8, turned 45 degrees). Only an `element_text` layer wins.
- **Nothing is recorded today.** The same recipe gets another axis text on other data, or after a filter in My view, and no file of the export says so.
- **Two options would reconsider a decision.** "No automatic adjustment" and "the automatic step wins" (also "the author's size is a maximum") go against D-0242, which says an author overrides per axis with an `element_text`.
- **Fixing the two defects of today's rule changes some shipped pictures** (the flipped plots and the plots with a number axis). This must not be mixed into the big recipe change, whose pictures must stay identical.

## Her question "does the automatic adjustment cover only the visuals?"

Yes. It changes only the size, the turn and the alignment of the two axis texts. Proven on all 17 plots of `1_test_data_ST22_dummy`: data, scales, labels and facets are identical with it on or off. Nothing else in the app adjusts a figure from the data.

## What no option can do

About 60 labels fit on a figure 8 inches wide. With 100 or 500 sample ids on one axis, the labels overlap under EVERY option (5 or 6 of the 17 plots). Text size is not the tool for that case. The remedy is in the recipe (fewer labels, a summary plot) or in a filter.

## The table

| Option | Viewpoint | For | Against | Evidence |
|---|---|---|---|---|
| T: as today | architect | smallest change; the pictures stay | silent loss of a theme size; no record; two defects | facts F2, F3, F1 |
| N: no automatic adjustment | scientist, user | the figure is exactly what the recipe says | labels collide already at 100 on a plot that the turn saves today; reverses D-0242 | sheet `mlst_bar`; 6 plots overlap against 5 |
| O1: the author always wins | scientist, user (both rank it first); architect (a narrow form) | the author gets what was written; no silent loss; keeps D-0242 and extends it to themes | the size still differs between data sets where the author wrote nothing, so it needs the record | facts F2; sheets `virulence_bar`, `qc_reads` |
| O2: the automatic step wins, with a message | none | clearest picture at 10 samples | worse than the author's own choice at 100 and 500 on two plots; overrides the author; against D-0242; its message text does not exist yet | facts F4; sheet `virulence_bar` |
| O3: the author's size is a maximum | none first | never larger than written | looks like today in the pictures; hard to explain; the turn rests on an estimate; HOME and the export could differ because the fit depends on the figure width | facts F4; architect |
| O4: the author writes "auto" with a minimum and a maximum | architect second, scientist "later, as an add-on" | the author states the range | four settings to write correctly; a recipe-format change; at 100 and 500 it falls to the minimum and is still unreadable; same width problem as O3 | variant sheet; architect |
| O5: write down what was adjusted | all three: required with any option | answers "can we capture the adjustments?"; needed for a methods section | none named; needs the record to be produced in one place | facts F3; architect: the plot library already keeps the applied steps in one object nobody reads |
| New, from the panel: warn instead of shrink | scientist, user | past about 60 labels the app says "N labels do not fit on this axis; filter or summarise in the recipe"; informs, does not choose | a threshold to choose | facts F4 |

## What all three agree on

1. The record (O5), whatever else is chosen: per plot and per axis, what the recipe wrote, what the rule proposed, what was applied, and why with the numbers. Shown in HOME under the plot, written in the export. One place produces it.
2. A size written in a theme must not be lost silently.
3. The two defects of today's rule are fixed first: on a flipped plot the rule reads the wrong axis; on a number axis it counts data values instead of ticks.
4. "The automatic step wins" (O2) is the worst choice.

## Where they differ

The scientist and the user want "the author always wins" in full. The architect wants the same for `theme_custom` now, and leaves a named theme's base size as an open point, because copying plotnine's own size rule into the app would make two sources of truth.

## My recommendation (coordinator)

Keep the automatic adjustment where the recipe says nothing about the axis text, because her purpose needs it ("our plots will always look horrible when we have a new dataset"). And:
- the author's written size wins, also through `theme_custom` (a named theme's base size: ask the architect's open point as a separate small question);
- every adjustment is recorded and shown (O5);
- past about 60 labels the app warns in plain words instead of pretending the text can be read;
- the two defects are fixed in their own announced change, with the affected pictures listed, AFTER the big recipe change is merged;
- "auto with a minimum and a maximum" is not built now.

Order and effort (architect): big recipe change merged first; then the two defects [sonnet/medium]; the record [sonnet/medium]; the `theme_custom` rule [sonnet/medium]; the warning [sonnet/low].

## What she decides

1. Which option: my recommendation above, or another line of the table.
2. Does a named theme's base size also win over the automatic step? Default: yes in principle; how to build it without copying plotnine's rule is checked first.
3. The threshold of the "labels do not fit" warning: about 60 labels on an 8 inch figure. Default: computed from the figure width, not a fixed number.
4. Question 14 was waiting for this one.

## Limits of the evidence

- 100 and 500 samples are copies of the 42 shipped samples under new ids (no generator exists for this recipe), so only the sample count grows, not the other categories.
- HOME's real figure width was assumed.
- Overlap was measured with one renderer. The pictures were read by the panel on a few sheets each, not all 21.
- No export bundle was built; "not recorded" comes from reading the code that writes the export.
