# Your design for a table as a result: can it work (panel round 3, 2026-11-22)

Your order (channel blocks M548, M549). Four viewpoints answered once, with the code open: scientist, architect, developer, user. They recommend; you decide. Judged on merit; what a point reopens is in its own column. Their answers as given: `VIEWPOINTS_3.md`. Facts: `FACTS_2.md`, `FACTS.md`.

## The answer in one line
**Yes, your design can work**, all four say so, and it needs less building than round 2's (no new grid, no two-pane view). It works under the conditions in section 1.

## 1. Flags first: what must be true so that nothing is hidden or silently different
1. **The result must always be exported under its own name.** Today a plot's own data file (`T3_data_<id>.tsv`) is written only when the plot has tier 3 or audit steps. A table result with neither would be missing from the bundle. (scientist, developer, architect; `app/handlers/export_handlers.py:1095, 1438`)
2. **"Table to view" is one choice for all sub-tabs, and it is sticky.** A user who chose T1 for the previous plot would land on a table result still seeing T1, with nothing saying it is not the result. (architect, user; `home_theater.py:1388`)
3. **The preview is never the bare result.** It carries the exploration filters, the column chooser, the 100-row limit, and in Audit mode the audit steps. A plot's area always shows the unfiltered Result; with your design no place on screen shows the unfiltered result table unless the screen says which of these are on. (architect, scientist, user)
4. **The Compare switch would silently do nothing** for a table result unless it is given something to do or is not offered. (architect)
5. **A column drop on a result table gets no "this entry uses that column" note today**: the note reads the plot's mapping, and a table has none; a table uses every column. It needs its own note. (architect; `libs/utils/src/utils/recipe_graph.py:379`)
6. **A written part must never be dropped silently:** an entry that says "table" and also has a drawing part (`mapping`, `layers`, a plot engine) is refused, naming both. (architect, developer)
7. **"The result is the last stage" has one trap** (scientist): an author who adds last steps only to round numbers or to make text columns ("mean ± sd") makes the rounded table the result, and the unrounded values a reviewer needs are then only in the earlier stage. To be said in the documentation; the result should be shown with its last steps listed.
8. Still true from round 2: a summary can differ silently (an empty value against NaN, the quantile method, the order of groups without a sort, no number of rows per group unless the recipe adds it); "Showing 100 of N rows" does not exist yet; the report holds figures only; the words "plot" in the audit dialog and the lineage notes.

## 2. What each place does with a table result (question a)
| Place | What it does | Verified at |
|---|---|---|
| The opening of a recipe | builds the table of every entry as today; draws only the entries that are plots | `app/modules/opening_build.py:81-86, 146-152` |
| The export, pictures | skips a table result | `export_handlers.py:1241, 1277` |
| The export, data | writes the result by name, always (flag 1) | `:1095, 1438` |
| The report | names the result under its group and includes the table (new: the report has no table today) | `:367-384, 1866-1874` |
| Gallery previews | a Gallery example stays a plot; the Gallery check refuses a table entry | `app/modules/gallery_examples.py:131` |
| BLUEPRINT's live plot | can work: it skips a table entry (BLUEPRINT is refactored later) | `app/modules/wrangle_studio.py:706-714` |
| One safety net | the one function that draws refuses a table entry by name, so a place that was forgotten fails loudly, never silently | `app/modules/engine_registry.py:94` |
| HOME, the plot area | no plot output for a table entry; your sentence instead | `home_theater.py:960` |
| The recipe check | the keys required and forbidden depend on the kind of entry, read from the format in one table | `recipe_check.py:1149-1218` |
| The audit dialog and the lineage | the word "plot" is taken from the entry's kind | `lineage_walk.py:545, 593` |
| Keys, stored tables, audit steps, lineage place | reused unchanged | `FACTS_2.md` section 3 |

## 3. The data preview under a table result (question b)
- It already follows the selected sub-tab: nothing new is needed to find the entry's table. Only one grid shows the table (your design avoids the same table twice).
- Open for you: when a table sub-tab is selected, does "Table to view" jump to the last stage by itself?
  - (b1) Yes, with a line "Switched to the result (T3)." Pro: the user sees the result at once. Con: the app overrides a choice the user made.
  - (b2) No; the badge says "Viewing: T1, an earlier stage, not the result". Pro: nothing changes by itself. Con: the result is one click away, and a hurried user reads T1.
  - Either way the badge reads "Result" only on the last stage (developer: a test switches to T1 and checks that the line changes).
- Suggested words (user viewpoint; yours to change): in the plot area "This result is a table, not a picture. It is shown below in 'Data preview', at its last stage (T3)."; under the table "View only: 2 filters and 3 hidden columns. The result is unchanged."; "Showing the first 100 of 2,340 rows. Turn on All rows to see all."; when the preview is collapsed "The table is in the collapsed Data preview below. Open it." (the app does not open it for the user).

## 4. The export of the result (question c)
- **The file name comes from the entry's id, not from its `ui_label`** (scientist, developer): the id is stable; a label can be renamed, and holds characters a file name cannot. The label is written in the README and the report beside it: "Result: <label> (<id>)", with the number of rows and whether it is audited.
- Suggested place: `results/<id>.tsv` (scientist). Not decided.
- **One file or two?** Today `T3_data_<id>.tsv` is the AUDITED table when there are audit steps. Options: (c1) the result file replaces `T3_data_<id>.tsv` for a table result (one file; developer); (c2) both (the same table twice, told apart only by the README); (c3) the result file is the audited result and a second named file holds the original result, so that a reviewer can redo the comparison (scientist: "export both tables by name", or say plainly that the baseline recipe plus the audit recipe let a reviewer rebuild the original).

## 5. The audit: what replaces "Original against Audited" for a table (question d)
A run by the scientist: removing one sample moved a group's mean from 23.67 to 30.5; removing every sample of a group makes its row disappear. So for a summary the VALUES change, not only the rows.
| Option | What the user learns | Needs | Could go wrong | Scientist | Developer | User |
|---|---|---|---|---|---|---|
| **d1** your diff: rows removed, groups gone, cells changed with old and new values | the most: the mean that moved, the group that vanished | a row KEY to line the rows up; a summary may have none | lined up by position, the diff is silently wrong; it must refuse a table with no key, never guess | fits a table best; computed from the two tables, never from the step text | medium to large; the only key the recipe declares is the entity key, often gone after an aggregation | the only one that shows the values; as a short list, on request |
| **d2** one line above the table: "audited: 2 steps applied; 3 rows and 1 column fewer" | that it changed, and roughly how much | two counts the audit run already has in hand (it collects both tables) | says nothing of values that changed in place | the honest minimum: rows and columns before and after, cells changed, groups added or removed | small and the safest | easy to read; must also say that values changed |
| **d3** two tables side by side | everything, if the rows are matched | a key again; width | unreadable on a wide table | only with matched rows | large | rejected |
| **d4** only the badge | almost nothing | nothing | hides a mean that moved | hides the size of the change | hides the effect | rejected |
Today, without anything new: "Table to view" on T2 shows the original and on T3 the audited table, in turn. The user viewpoint: enough only if the screen says "T3 differs from T2 by audit".

## 6. The names (question e)
Counted by the architect in the files under git: 251 recipe-like files hold the list `plots` (193 test fixtures of the plot library, 34 Gallery bundles, 16 recipes, 8 others); 34 source files read it (116 lines); "plot entry" is written in 91 source lines; 65 documents.
| Option | Pro | Con | Reopens (information only) |
|---|---|---|---|
| **e1** keep the list `plots`; one key on the entry says "table" | small; nothing existing changes | a list named "plots" holds tables: "wrong and hard to explain" (user); the reading function in the code would be named for plots and return tables | nothing |
| **e2** a general name for the list (for example `results`), each entry says what it is | says what it is; your words "a plot entry actually should be a result_entry"; done once by the migration script that exists | every recipe and Gallery bundle changes once; large in the code (the readers, the check, the documents); the riskiest places are the text paths that write audit steps back into a recipe | D-0236 ("no format 2"): see the note below |
- A half rename (the recipe key renamed, the code's reading function not) is not acceptable (architect, by the legacy rule): the function would say one thing and do another. Names that are stored or exported (`T3:<id>`, `T3_data_<id>.tsv`, the sub-tab ids) may stay, each on a named list.
- The key on the entry: one key with a list of values, so that a third kind later is one more value and not a second key. The words are yours: `show: plot | table` (architect), or `kind: plot | table` (user). When absent it means a plot.
- **A contradiction in the records to settle with it:** the architect reads in the format file that a key change means format number 2; your decisions say the format is amended before its first release and stays 1 (D-0236, D-0469). Your decisions govern; the format file's sentence is then out of date and is corrected in the pass.

## 7. My recommendation (the coordinator's; yours to accept, change or refuse)
1. **Your design, as you described it**, with the conditions of section 1 built in the same pass.
2. **The audit: d2 always, and d1 on request where the table has a key** (the user viewpoint's proposal; the scientist and the developer agree on each half). The line is always there and cannot be wrong; the diff shows the values and says plainly "no key: cannot line the rows up" instead of guessing. d1 can be built after d2 without redoing it.
3. **The names: e2**, done as its own step first, changing no behaviour, and folded into the names migration that is already prepared. Two viewpoints prefer it on merit (architect, user); the developer calls it "large but complete". Its cost is one migration of every recipe, which the names pass does anyway.
4. **The export: the file is named from the id; the label is beside it.** One file or two is yours (section 4).

## 8. What stays yours to decide (nothing chosen)
1. Does "Table to view" jump to the last stage when a table result is selected (b1), or stay with a clear badge (b2)?
2. The audit comparison: d2 only; d2 with d1 where a key exists; or another.
3. The export of the result: one file or two (c1, c2, c3), and its folder.
4. The names: e1 or e2; the list's word; the key's word and values.
5. What Compare does for a table result: not offered, or it opens the diff.
6. The sentences of section 3.
7. From round 2, still open: whether your earlier line "a table on itself ... need to have plots" (D-0109) stands in a changed form; a tier 2 that nothing reads (refused, or allowed with a notice); the number of rows per group and rounding for a summary; the Gallery (plots only, as the architect proposes, or tables too).

## 9. A build order if you choose it (developer; each slice complete, no shim)
1. Tests first: one per place that draws, with a table entry; the preview switched to T1 changes its line; the result file equals the last-stage table, all rows; the stored table's key equals that of a plot with the same steps; an entry with "table" and a drawing part is refused.
2. The format, the check and the one function "what kind of entry is this?".
3. The places that draw skip a table entry; the export and the report get the result (side by side with 4).
4. The audit line (d2): the counts.
5. HOME: the sentence, the preview's line and words. Last.
6. If e2: a separate step after 2 (the migration rule, the old-key refusal, the documents).

## 10. Not verified
No screen was run. The developer's and the architect's counts of places differ because they count different things; a scout settles the exact list before step 2. Whether a table result with exploration filters on is clear enough on a real screen can only be judged by your test.
