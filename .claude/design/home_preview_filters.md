# HOME: preview filters and column choices (Exploration panel)

**Status:** DRAFT 2026-11-11, written with Eve. Companion: `home_audit_steps.md`. Nothing here is code
until Eve has read both files and the diagrams. Marks: **[built]** = in the app today, **[decided]** = Eve
decided, not built yet, **[open]** = still to decide.

## 1. The rule, in one sentence

**A preview filter or column choice only helps you look at the data you are looking at right now. It is never
saved, never exported, and never changes a plot. To change what a plot shows, use the Audit workspace
(`home_audit_steps.md`).**

## 2. Where it lives

- The existing header strip is renamed **Exploration**; its two choices are simply **Data** (Raw (T1)| Result (T2)) and
  **Plot** (the recipe's Result plot), without "to show". [decided]  @eve: as such will allow to remove the grey comments under the selectors and win space. -> done in this file: the grey explanations under the selectors go. **[to confirm]** With My view and Compare gone, the Plot choice has only one value (the Result plot); it can be removed, leaving one toggle **Data: Raw (T1) | Result (T2)**. @eve : good point - agreed
- **My view and Compare leave this strip** and move to the new Audit workspace. The two are **exclusive**:
  when the Audit workspace is open, Exploration is minimised; when Exploration is active, the Audit workspace is
  minimised (space). [decided] @eve: audit workspace minimized when Exploration is active. -> done
- The Filters panel in the left sidebar is renamed **Exploration Filters** (it is only used in Exploration). Its
  header names what it acts on, for example "Exploration Filters: Raw table of MLST_with_metadata". [decided]
  @eve: we can rename Filters to "Exploration Filters" if its only used in Exploration : this clarifies. -> done

## 3. What a preview does

| Item | Behaviour |
|---|---|
| Row filter | Hides rows in the **data table** of the stage you are on (Raw = T1, Result = T2). [built for the table] |
| Column selector | Hides columns in the **data table** only. [built] |
| Plot | **Not changed** by anything in Exploration. Raw has no plot ("NA"). [decided; today Apply also filters the My view plot, which moves to the Audit workspace as an audit step] |
| Data files | Never written. The filter runs on a lazy copy at render time. [built] |
| Export | Never exported. [built] |
| Audit | Nothing is sent to audit from Exploration. [decided; today Send to Audit starts from the same list] | @eve: yes any way in this mode send to audit does not exist. 

## 4. Life of a preview filter

1. **Add**: a row (column, operator, value) goes to the *staged* list.
2. **Apply**: staged rows become the *applied* list, shown in the table. [built]
3. **Trash** on a row removes it from staged and applied at once. [built, #56 retest]
4. **Reset** clears both. [built]
5. **Change of Data view (Raw <-> Result): all preview filters and column choices are cleared**, with a short
   message ("3 preview filters cleared, you changed view"). [decided]
6. **Change of recipe**: cleared. [open: confirm]
7. Not saved in sessions, not in the export. [built]

Why clear on a view change: a filter built on Raw (wide) can be wrong on Result (long, renamed columns, other
data types: Year is 2022.0 in T1 and "2022" in T2). Keeping it would silently match nothing or the wrong rows. @eve: ok and I agree and understand: this is why the filters needs to be cleared on view change. This resoning must be documented (its a logic reason to do so - so it needs to be stated shortly as comment in the code AND in the documentation)

**Documented reason (to repeat as a short `WHY` comment in the clearing code, in the help text and in the ADR):**
a preview filter is built against the columns, names and data types of ONE stage. T1 (Raw) and T2 (Result)
differ (wide vs long, renamed columns, Year read as 2022.0 vs text "2022"), so a filter carried across a view
change can match nothing, match the wrong rows, or silently skip. Clearing it on a view change keeps every
preview filter valid for the data it is applied to. -> to do in code, with the change itself @eve: this should also shortly be explained in the help for the user. 

## 5. Scope

- A preview list belongs to **one view and one dataset** (the dataset the plot targets; plots sharing it share
  the list). [decided; today it is ONE global list for the whole analysis: to change] @eve: ok - @eve: short explanation in help for user
- **[open]** switching to a plot of another dataset inside the same view: keep each dataset's own list
  (recommended) or clear. @eve: ok
- The columns offered are those of the current stage, so a preview filter is always valid where it is applied.
  The safety skip ("a stage without the column skips the filter") stays but should never fire. [built]

## 6. Operators (one vocabulary everywhere) [built, #57]

Categories: `= equals`, `≠ not equal`, `∈ any of`, `∉ none of`. Numbers: `= equals`, `≠ not equal`,
`> greater than`, `≥ greater or equal`, `< less than`, `≤ less or equal`, `↔ between`. One selected value reads
"column = value"; several read "any of". Source: `OP_WORDS` in `app/modules/t3_audit_engine.py`.

## 7. Feedback to the user

- Badge on the table: "Viewing: Raw / Result" plus "N preview filter(s) on, not saved". [built]
- Plot badge on Result: "preview filters change the table only". [built; to reword with the new panel]
- Row count line of the table ("Viewing rows a through b of N") is the user's check that a filter worked.

## 8. Edge cases (each needs a test, see section 10)

zero rows left; all rows kept; all columns hidden; same row added twice; remove the first, the last, all rows;
remove one of several applied rows (the table must refresh at once); staged but not applied; Reset with
staged-only rows; filter on a column absent from the stage; value type differences (int vs float vs text);
between inclusive/exclusive; recipe switch with filters on; Home -> Gallery -> Home; very wide table.

## 9. What changes from the app today

1. One global list -> one list per (view, dataset).
2. Preview no longer changes any plot; plot preview becomes "draft step" in the Audit workspace.
3. My view and Compare move out of the strip.
4. Clear on view change, with a message and a `WHY` code comment (reason in section 4); panel header names the target view.
5. Strip renamed Exploration, shorter labels, minimised when the Audit workspace is open.

## 10. Tests (browser, data oracle, screenshots)

Each test compares the table (row count line and values) with the same filter applied directly with Polars on
the same stage, and saves a screenshot per step to `tmpAI/`. One test per edge case of section 8, plus: the plot
image on Result is byte-identical before and after Apply; nothing is written under the anchors folder; the
export contains no preview filter; clear on view change; mutation check of each rule (break it once, see it fail).
