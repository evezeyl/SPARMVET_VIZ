# HOME: Exploration (preview filters and column choices)

**Status:** 2026-11-11, agreed with Eve (history of the comments: git commit 5b59a4a), checked again in the full
consistency review. Companion: `home_audit_steps.md`. Decision record: ADR-099. Nothing here is code yet. Marks: **[built]** = in the app today, **[to build]** = decided,
not built.

## 1. The rule, in one sentence

**Exploration only helps you look at the data you are looking at right now. A preview filter or column choice is
never saved, never exported and never changes a plot. To change what a plot shows, use audit mode
(`home_audit_steps.md`).**

## 2. Where it lives [to build]

- The header strip becomes **Exploration**: one toggle **Data: Raw (T1) | Result (T2)**. The old "Plot to show"
  choice goes (the plot is always the recipe's Result plot) and so do the grey explanations under the
  selectors: more space.
- **My view and Compare leave the strip** and live in audit mode.
- Exploration and audit mode are **exclusive**: opening one minimises the other. The **mode switch**
  (Exploration | Audit mode) sits at the left of the group-tabs row and is shown only with the sandbox flag.
- The left panel keeps the name **Filters**. Its header names what it acts on, for example "Filters: Raw table of
  MLST_with_metadata". There is no Send to Audit here. **Under the hood** the same filter form serves two
  tools: in Exploration its button is "Add to preview" (a lazy filter on the shown table, this file); in the Audit
  audit mode the same form creates an audit step (`home_audit_steps.md`, a recomputation through the lineage). Only the
  form widgets are shared. A short note in the code and in the docs states that the two behave differently.

## 3. What a preview does

| Item | Behaviour |
|---|---|
| Row filter | Hides rows in the **data table** of the stage you are on (Raw = T1, Result = T2). [built for the table] |
| Column selector | Hides columns in the **data table** only. [built] |
| Plot | **Not changed.** The Result plot is the recipe's plot; Raw has no plot (NA). [to build; today Apply also filters the My view plot] |
| Data files | Never written; the filter runs on a lazy copy at render time. [built] |
| Export | Never exported. [built] |

## 4. Life of a preview filter

1. **Add**: a row (column, operator, value) goes to the *staged* list. [built]
2. **Apply**: staged rows become the *applied* list, shown in the table. [built]
3. **Trash** on a row removes it from staged and applied at once. [built]
4. **Reset** clears both. [built]
5. **A change of Data view (Raw <-> Result) clears all preview filters and column choices**, with a message
   ("3 preview filters cleared, you changed view"). [to build]
6. **A change of recipe** clears them. [to build]
7. Never saved in sessions, never exported. [built]
8. Switching between Exploration and audit mode is **not** a view change: the lists are kept, and not applied while
   audit mode is on. [to build]

**Why clear on a view change (state this reason in the code as a short `WHY` comment, in the help text and in
the ADR):** a preview filter is built against the columns, names and data types of ONE stage. T1 (Raw) and T2
(Result) differ (wide vs long, renamed columns, Year read as 2022.0 vs text "2022"). A filter carried across a
view change can match nothing, match the wrong rows or be skipped silently. Clearing keeps every preview filter
valid for the data it is applied to.

## 5. Scope

- A preview list belongs to **one view and one dataset** (the dataset of the plot; plots sharing it share the
  list). Each dataset keeps its own list while you stay in the same view. [to build; today ONE global list]
- The columns offered are those of the current stage, so a preview filter is always valid where it is applied.
  The safety skip ("a stage without the column skips the filter") stays but should never fire. [built]

## 6. Operators (one vocabulary everywhere) [built]

Categories: `= equals`, `≠ not equal`, `∈ any of`, `∉ none of`. Numbers: `= equals`, `≠ not equal`,
`> greater than`, `≥ greater or equal`, `< less than`, `≤ less or equal`, `↔ between`. One selected value reads
"column = value"; several read "any of". Source: `OP_WORDS` in `app/modules/t3_audit_engine.py`.

## 7. Feedback to the user

- Badge on the table: "Viewing: Raw / Result" plus "N preview filter(s) on, not saved". [built]
- The row count line ("Viewing rows a through b of N") is the user's check that a filter worked. [built]

## 8. Help text for the user (to write with the change)

Two short explanations must be in the "?" help, the user guide and the FAQ:
1. **Why filters clear when you switch Raw/Result:** the two views have different columns and data types, so a
   filter made on one could give wrong results on the other.
2. **What a filter applies to:** the data you are looking at (this view, this dataset); plots that share the
   dataset share the filter; other datasets have their own. Filters are for looking, not for changing results:
   use audit mode for that.

## 9. Edge cases (each needs a test)

zero rows left; all rows kept; all columns hidden; same row added twice; remove the first, the last, all rows;
remove one of several applied rows (the table must refresh at once); staged but not applied; Reset with
staged-only rows; filter on a column absent from the stage; value type differences (int vs float vs text);
between inclusive/exclusive; recipe switch with filters on; Home -> Gallery -> Home; plot tab on another
dataset (own list); very wide table; view change with filters on (cleared, message shown).

## 10. What changes from the app today

1. One global list -> one list per (view, dataset).
2. Preview no longer changes any plot.
3. My view and Compare move out of the strip into audit mode; the "Plot to show" choice goes; a mode switch is added.
4. Clear on view and recipe change, with a message and a `WHY` code comment.
5. Strip renamed Exploration; the Filters panel keeps its name and its header names the target view.

## 11. Tests (browser, data oracle, screenshots)

Each test compares the table (row count line and values) with the same filter applied directly with Polars on
the same stage, and saves a screenshot per step to `tmpAI/`. One test per edge case of section 9, plus: the plot
image on Result is byte-identical before and after Apply; nothing is written under the anchors folder; the
export contains no preview filter; mutation check of each rule (break it once, see it fail).
