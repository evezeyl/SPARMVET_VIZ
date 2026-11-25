# A table as a result: the check and the two proposals you asked for (coordinator, 2026-11-22)

After your answers on `TABLE_FOR_THE_OWNER_3.md` (channel block M551). Three parts: (1) the check of your point that the screen already says what is laid on the preview; (2) options for the key system; (3) what "the result is the default at opening" does exactly. The proposals are mine; you decide.

## 1. Does the screen already say what is laid on the preview? Partly.
You said: "I think this is seen because its indicated either on the left panel and in the right panel when in audit mode." Checked in the code for each of the four (a scout survey, read at file:line, no screen run):

| What is laid on the table | Said on screen today? | Where, and the words |
|---|---|---|
| Exploration filters | **Yes, beside the table.** | The badge in the header of the data preview: "2 preview filter(s) on, not saved; they change this table only, never a plot". Visible without opening anything. The left Filters panel also says "2 active", but that panel is CLOSED by default. |
| The column chooser (columns hidden from the view) | **No.** | The chooser sits in the data preview with its label "Table columns (view only — no effect on plot):". Nothing says that some columns are hidden, nor how many. |
| The 100-row limit | **Half.** | The title says "Data Preview (max. first 100 rows)". The number of rows of the whole table is shown nowhere, so one cannot tell whether 100 rows is all of it or a small part. |
| Audit steps (Audit mode) | **Yes.** | The badge: "Viewing: T3 (audited)", "the table the audited plot is drawn from: T3 plus 2 audited step(s)". The right panel lists the steps; it opens by itself in Audit mode. Only steps applied with a reason are in the table; pending steps are not, and the right panel shows them as pending. |

So for a table that IS the result, two things are missing: **"N columns hidden"** and **"Showing 100 of N rows"**. Both are small, and useful for every preview, not only for a result.

Two more facts from the same check:
- "Table to view" is one value for the whole of HOME. Only the user's click changes it today: not a change of plot, of mode or of recipe, and not a restored session.
- The data preview is open by default and no code opens or closes it by itself.

## 2. The key system: options in the words a recipe maker reads
Your words: "show is weak we need a good key system that make it clear for the recipe maker - which means also that we would have a definition of what is the result : a table or a plot."
What you already decided and the options keep: an entry is a result that is a plot or a table; the result is the last stage of the entry (no key chooses a tier); a table entry has no drawing part.

**Option K1: the list is `results`; each entry says `result: plot` or `result: table`.**
```yaml
analysis_groups:
  quality:
    ui_label: "Quality control"
    results:
      reads_summary:
        ui_label: "Reads summary"
        result: table            # the result of this entry is its table, at its last stage
        target_dataset: FastP_summary
        tier3:
          steps: [...]           # optional: the entry's own last steps
      reads_barplot:
        ui_label: "Reads"
        result: plot             # the result of this entry is the drawing
        target_dataset: FastP
        mapping: {...}
        layers: [...]
```
- Pro: the key reads as the definition you ask for: "the result of this entry is a table". One key; a third kind later is one more value.
- Con: the word "result" appears twice (the list, the key).

**Option K2: the list is `results`; each entry says `kind: plot` or `kind: table`** (the user viewpoint's words).
- Pro: short. Con: "kind" does not say kind of what; weaker as a definition.

**Option K3: two lists in a group, `plots:` and `tables:`; the place of the entry says what it is; no key.**
```yaml
    plots:
      reads_barplot: {...}
    tables:
      reads_summary: {...}
```
- Pro: nothing to forget; an existing recipe does not change at all; the most readable file.
- Con: the order of plots and tables in the tabs can no longer be mixed freely (all plots, then all tables, unless a rule is added); a third kind is a third list; the architect withdrew this form in round 2 because two lists invite two code paths (it can be done with one reader that joins both lists, ids unique across both; that discipline must then be kept by a test).

**Option K4: keep the list `plots`; each entry may say `result: table`.**
- Pro: the smallest change. Con: a list named "plots" that holds tables, which you and the user viewpoint found hard to explain.

**Beside the option, one choice: is the key required in every entry, or is a plot meant when it is absent?**
- Required (my recommendation under K1): every entry states what its result is. This is your "make the decision clear for the person designing the recipe"; a forgotten key is refused by the recipe check with a plain line. The migration writes `result: plot` into every existing entry, once.
- Absent means plot: fewer lines; but an author who forgets the key on a table entry gets "mapping and layers are required", a message about drawing for an entry that draws nothing.

**My recommendation: K1, with the key required.** It is the only option where the recipe itself carries your definition in plain words, and where the list name matches what it holds.

What each reopens (information only): K1, K2 and K4 add a key to the entry; K1 and K2 rename the list in every recipe and Gallery bundle (done by the names migration script that exists); none needs a new format number under your decisions (the format is amended before its first release, D-0236, D-0469).

## 3. "The result should be the default at opening, but the user must still be able to navigate"
Your words. Two things the sentence leaves open:

**(i) When does the preview go to the result?**
- **R1 (my recommendation): each time a table entry is selected**, the preview shows its result (the last stage), with the badge "Result". The user then moves freely to T2, T1 or Source; the badge reads "an earlier stage, not the result".
  - Pro: one rule, easy to say in the documentation: "a table result always opens on the result". Never a table result silently shown at an earlier stage.
  - Con: a user who compares T1 of two table results clicks T1 again after each change of sub-tab.
- **R2: only the first time an entry is opened**; after that the app remembers the stage chosen for that entry.
  - Pro: no repeated click. Con: a memory per entry that the user cannot see; coming back to an entry days later (a restored session does not hold it) behaves differently from the first visit.

**(ii) What happens to the choice when the user moves on to a PLOT entry?**
- **P1 (my recommendation): the stage chosen before the table result comes back.** The table result's jump to the result is temporary and belongs to that sub-tab only. A user who was inspecting T1 across plots keeps T1 across plots.
- **P2: the choice stays on the last stage** (T3) after a table result was visited. Simpler in the code; but the app changes a choice the user made, for good.

Under R1 with P1, "Table to view" behaves as today for every plot, and a table result adds one predictable step: it opens on the result.

In Audit mode nothing differs: the result is the audited last stage, the badge says "Result (audited)", and T2 and T1 show the originals, as today.

## 4. For you to decide (nothing chosen)
1. The key system: K1, K2, K3 or K4; and with a key: required in every entry, or a plot when absent.
2. The default: R1 or R2; and P1 or P2.
3. The two missing sentences near the table, for every preview: "N columns hidden" and "Showing 100 of N rows". Add both?
4. Still with the review session, one at a time: the audit comparison for a table (one line always; your diff where a row key exists), the export file of the result (named from the id; one file or two), the format-number sentence in the format file.
