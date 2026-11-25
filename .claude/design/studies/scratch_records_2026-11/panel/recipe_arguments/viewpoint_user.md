NOVICE / TEACHER VIEW. Read: the three shipped plots, q6_the_15_objects.md (sections 1, 3, 5, 6, 7) and docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:295-335. I did not run any code. I did not read the other docs that mention layers, so I cannot say what they tell an author about positions, themes or guides. The user guide shows only geom_bar, labs and a one-line `theme:` (lines 296-335). It never explains `element_text` or `position_dodge`. Today a novice learns these only by copying the shipped plots (VirulenceFinder_counts_bar.yaml:15-21).

THE THREE EXAMPLES, PER WAY

A. Layers in a list (today)
```
- name: geom_bar
  params: {width: 0.8}
- name: position_dodge
  params: {width: 0.5}
- name: element_text
  params: {target: axis_text_x, angle: 90, size: 6}
```
- Error bars: `- name: stat_summary, params: {fun_data: mean_se}`. I could not check whether it is allowed.
- It looks like a plain list, but order matters and I am not told. q6 section 6 (D1-D5):
  - Dodge goes to the last layer. After a point layer, it fails with "Width not defined".
  - A second element_text on the same axis silently drops the first.
  - A second guide or element_blank silently drops the first.
  - element_text is applied last, whatever its place.
- ggplot2 and plotnine examples cannot be copied, because they have no `- name: position_dodge` line, and `target` is an invention of this app.
- I would make a mistake by writing dodge before the bar, or by putting two text styles on one axis. The message I want: "position_dodge was placed on layer 'geom_point' (the last layer), not on 'geom_bar'. Put it directly after the layer you want, or write position inside the layer."
- HOME users cannot see any of this. A rotation that vanishes is invisible.

B. Typed value in place
```
- name: geom_bar
  params: {width: 0.8, position: {name: position_dodge, params: {width: 0.5}}}
theme:
  axis_text_x: {name: element_text, params: {angle: 90, size: 6}}
```
- Error bars: `stat_summary` with `fun_data: {name: mean_se}`.
- The picture is simple: the dodge belongs to this bar, and the text style belongs to this axis. Nothing depends on order.
- I cannot copy from plotnine's documentation, but the translation is mechanical. `position_dodge(width=0.5)` becomes `{name: position_dodge, params: {width: 0.5}}`.
- It is verbose, with nested braces. My likely mistakes are a typo in `name` and a missing `params`. The message I want: "position: 'position_dodg' is not a known position. Choose one of: dodge, dodge2, stack, fill, identity, jitter, jitterdodge, nudge."
- The form can show a pick list of allowed names, then one field per parameter once a name is chosen. This is the clearest form to build.

C. A section per owner, plain keys
```
position on the layer: {dodge: {width: 0.5}}
theme:
  axis_text_x: {angle: 90, size: 6}
```
- This is the shortest to write. But "the app knows which object each key needs" means I cannot tell that `axis_text_x` is an element_text. Then I cannot find it in the plotnine documentation.
- I would hit a wall at `axis_ticks_x`, which needs `element_line`, not text. Unless the app says so, I will pass `angle` to a line and fail.
- A typo is the likely mistake. The message I want: "theme key 'axis_txt_x' not known. Did you mean 'axis_text_x'? This key takes: angle, size, hjust, vjust, color."
- The form shows the key as a section with the fields that fit it.

D. A short text like the library call
```
position: "position_dodge(width=0.5)"
axis_text_x: "element_text(angle=90, size=6)"
```
- This is the easiest to copy from the plotnine and ggplot2 documentation, and it is a single line. That is the strongest point for a scientist. It feels like code, and I would wonder whether it runs.
- Mistakes are quotes, commas and `=` versus `:`. The message I want: "position: could not read 'position_dodge(width 0.5)'. Expected name(parameter=value, ...). Allowed names: ... Not run as code."
- Parameters inside a string cannot get a field in the form. The form would have to parse the string back, which is worse than B.
- Table formulas: `pl.col('a') / pl.col('b')` is readable to me because it matches the polars documentation. But I cannot tell which functions are allowed until I fail. A form with nested boxes for a formula would be worse. Three nested boxes for a division is slower than one line. A good middle: write the text, and show the allowed functions and the parsed result beside it.

E. A named ready-made choice
```
summary: mean_se
x_labels: rotated
```
- This is the simplest for HOME and for a novice. A pick list gives the full set of choices.
- It hides the numbers. Does "rotated" mean 45 or 90? Where is size 6? I cannot reproduce a published figure from a name.
- It does not cover what the shipped list lacks. I would be stuck, with no way out. It is good as a convenience on top, not as the only way.
- The message I want: "x_labels: 'rotate' not in the list. Available: rotated (90 degrees, size 8), ..." The list must show what each name sets.

RECOMMENDATION
Choose B as the one way to write each object. E is allowed only if each name expands visibly into B. Reasons:
- It keeps the original plotnine name, so the documentation can be copied and adapted.
- It places each setting where it acts, so layer order cannot change the result.
- It maps one-to-one onto form fields.
- It is plain data, with no code.

Two ways side by side would confuse me most. I would not know which one "wins" when both appear, or whether the two differ.

WHAT HOME SEES FOR A DISALLOWED OBJECT
The plot is not drawn, and the page does not show a blank figure. It says: "This recipe uses 'element_txt' in theme.axis_text_x. This app does not know it. The plot was not drawn. Recipe: <name>, line <n>." The current fallbacks must go: `theme_custom` silently drops an unknown name (D7), and `guides` turns a typo into a legend (D6).

THREE THINGS THE DOCUMENTATION MUST SHOW
1. A table: where each object goes. Layer `position`, theme key, guide, summary. For each, the list of allowed names with their parameters and a plotnine documentation link.
2. The three examples above (rotation, dodge, error bars) written out, side by side with the plotnine call they equal.
3. What the app refuses and what the message looks like. State "never run as code", and that a name outside the list stops the plot and is never silently skipped.
