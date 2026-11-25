# The export report built by group: the heading levels (coordinator's proposal, 2026-11-22)

> **UPDATE, later on 2026-11-22: you answered (channel block M558; ledger line to follow).** Your words: "Cant we have the technical section separated from the plots eg # technical # results ## groups ### plots ### table result info ?" and "### table shows the link or best, the name/id of the file - yes # Results before # Technical". So the structure is the one below; the options A, B, C further down are kept only as the record of what was put to you.
>
> ```
> (title)  Results Report - <recipe id>
> # Results
>    ## <group ui_label>
>       ### <plot ui_label>            the picture
>       ### <table result ui_label>    the name (id) of its file, and a link where the format allows it
>    ## <next group ui_label>
>       ...
> # Technical
>    ## Overview
>    ## Dataset -> Plot Mapping
>    ## Provenance
>    ## About the data in this report
>    ## Methods                        (only with audit steps)
>    ## Data files
>    ## T3 Audit Trail                 (only with audit steps)
>    ## Processing Issues During Session   (only when there are any)
>    ## Data Lineage
>    ## Random scatter seeds           (only when the box is ticked)
> ```
> What this changes besides the headings: every section number shifts (the sections are numbered); the contents list is three levels deep, so it shows the two parts, the groups and the technical sections, and every plot and table result.
>
> **Proposals you asked for (mine; yours to decide):**
> 1. **An intro line under `# Results`?** Suggestion: one line, "The results of the recipe <name>, by group. How they were produced is in the part Technical." Reason: a reader who opens the report meets the results with no word before them otherwise. Or none.
> 2. **A group with no result, or whose results all failed.** Suggestion: the group keeps its heading; a failed result keeps its heading and says why it was not drawn (as today); a group with nothing in it says "This group has no result." Reason: a heading that silently disappears hides that something was expected there.
> 3. **The five places that show a plot's id** (the mapping table, the hash table, "Used by", the link to a plot's own data file, the seeds section). Suggestion: "label (id)" in the three places a person reads (the mapping table, "Used by", the seeds section), and the id alone where it is a file name or a key (the hash table, the link). Reason: the label is what you saw in HOME; the id is what the files are named by, so showing both keeps the link between a heading and its file.
> 4. **The audit trail section** (one heading per audited plot today): the same grouping as the results, or flat. Suggestion: flat, with "label (id)": it is a technical list, and the group adds nothing there.

Your decision (ledger D-0484): "yes report build by group you can eg. use the group ui_label as Header ## and the plot ui_label as header ###". You gave the levels as an example; this is the proposal you asked for. Facts by a scout survey of `app/handlers/export_handlers.py` (read, not run).

## The report today (headings as a reader sees them)
```
(title)  Results Report - <recipe id>
## Overview
## Dataset -> Plot Mapping
## Provenance
## About the data in this report
## Methods                      (only with audit steps)
## Plots
   ### <one heading per plot>   (17 for the demo recipe, flat, no group)
## Data files
   ### <one heading per table>
## T3 Audit Trail               (only with audit steps)
   ### <one heading per audited plot>
## Processing Issues During Session   (only when there are any)
## Data Lineage
   ### Lineage Step Summary
## Random scatter seeds         (only when the box is ticked)
```
The sections are numbered. The contents list goes three levels deep in the web page (set), and by default in the PDF and Word forms. No heading deeper than `###` exists today. The report never names a group today.

## Two things the survey found that matter here
1. **The report and HOME show different names for the same plot today.** HOME's tab shows the plot's `ui_label` ("QC Reads Horizontal Barplot"); the report's heading shows its `ui_title` ("Reads Quality & Taxonomy Proportion"). This is so for all 17 plots of the demo recipe. Your decision (D-0409, D-0484) removes it: both show the `ui_label`; the longer text stays as the figure title inside the picture.
2. **A plot is named in nine places of the report, and five of them show the plot's id, not its label**: the mapping table, the hash table, "Used by" under each data file, the link to a plot's own data file, the seeds section. Your words (D-0409): the export "follows the same format that the user has seen". Not decided by you for these five: label, id, or both.

## Option A: your example, literally (my recommendation)
```
## Overview
## Dataset -> Plot Mapping
## Provenance
## About the data in this report
## Methods
## <group ui_label>            for example  ## Quality Control
   ### <plot ui_label>
   ### <plot ui_label>
## <next group ui_label>
   ### <plot ui_label>
...
## Data files
## T3 Audit Trail
...
```
- The flat "## Plots" heading goes; each group is a section of its own.
- Pro: exactly your words; every plot stays in the contents list (three levels); a group reads as "a category of results", at the same weight as the other parts.
- Con: the groups sit between the technical sections with nothing that says "the results start here"; a recipe with many groups makes a long top level (the demo: five groups, so sections 6 to 10).

## Option B: the groups under one "Plots" section
```
## Plots
   ### <group ui_label>
       #### <plot ui_label>
```
- Pro: one visible place for all results; the rest of the report is untouched.
- Con: a fourth level, new in this report; a plot is no longer in the contents list unless the depth is raised to four (then the list is long); numbers like 6.2.3.

## Option C: option A, with the results moved up
The same as A, and the group sections come right after "Overview", before the technical sections (mapping, provenance, about the data, methods).
- Pro: a reader meets the results first.
- Con: it also changes the order of the report, which you did not ask for.

**Recommendation: A.** It is what you said, it needs no new heading level, and every plot stays in the contents list. C is worth your look if you find the results buried.

## For you to decide (nothing chosen)
1. A, B or C.
2. The five places that show a plot's id (see above): the label, the id, or both ("Label (id)")? The id is what the data file names use (`T3_data_<id>.tsv`), so showing both keeps the link between a heading and a file.
3. The same for a table: "Data files" shows the table's key today, not its `ui_label`.
4. A group with no plots, or whose plots all failed: heading shown with a line that says so, or left out? (Today a failed plot keeps its heading and says why it was not drawn.)
5. The audit trail section has one heading per audited plot: grouped the same way, or flat as today?

## The QA group label (your "Can reduce QA ui_label")
The long sentence is ALREADY in that group's `description` (the format allows `description` and `comment` on a group). So only the label needs shortening; no text is lost.
- Today: `ui_label: "QA canaries (not for publication): each plot isolates one failure mode; the expected numbers are in its title"`
- Proposed: `ui_label: "QA canaries (not for publication)"`
- Even shorter, if you prefer: `"QA canaries"`.
Beside it, a fact: in the four other groups of the demo recipe the `description` is the same text as the `ui_label` (it was the old fallback). Agents do not change the demo recipe; say the word and it goes in with the names pass.
