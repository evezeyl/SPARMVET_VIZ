# A table as a result: the revised table, with your "text plot" idea (panel round 2, 2026-11-22)

Your orders (channel blocks M537, M538). It replaces the first table (`TABLE_FOR_THE_OWNER.md`) for question 2 and keeps its answer for question 1. Facts: `FACTS_2.md` (round 2) and `FACTS.md` (round 1). The four answers as given: `VIEWPOINTS_2.md`. Each option was judged on merit; what it reopens is in its own column and was not used as an argument.

## 1. Your confirmation question: TRUE
"The table shown is the result of the tier X applied": yes, proven in the code.
- The table at a tier is the result of every step up to and including that tier. T1 = the source read plus the tier 1 steps. T2 = T1 plus the tier 2 steps. T3 = T2 plus the entry's own tier 3 steps.
- A tier with no steps is the same table as the tier below. Nothing extra is stored. The badge says so ("T3=T2", "T3=T2=T1").
- So "the highest tier that has steps" and "T3" are the same table: the table after every step the recipe wrote.
- Four things are laid on top in the data preview only, never in the stored table: the audit steps in Audit mode; the exploration filters; the first 100 rows unless "All rows" is on; the column selector.
- "All rows" exists as you remember (`app/handlers/home_theater.py:1253`): off by default; it is applied after filters and audit steps. No text says "showing N of M" today. The first table's flag about 100 rows was only partly right: the switch exists; what is missing is the sentence.

**Your correction about tier 3: the code agrees with you.** Tier 2 and tier 3 steps are run by the same runner. Nothing in the data makes a tier 3 different. What ties a tier 3 to a plot is only where the app looks it up: in the list of plot entries, by the entry's id.

## 2. Flags first
1. **Your idea works best in one precise form.** If a result table is an entry found exactly like a plot entry (same list, same ids), then the building, the stored file, the key, the audit steps and the lineage place work with the code that exists. If it is anything else (a mark on a table, a second list), it needs a second lookup and a second key.
2. **"Nothing new to build" is true for the data, not for the showing.** Still to build, under every option: the grid in the plot area; "Original" against "Audited" for a table (it exists only for two plots); the table in the report (the report holds figures only); and every place that draws each entry must skip a table entry.
3. **Recognising a table entry by a missing drawing part is a silent trap.** An author who forgot `mapping` or `layers` of a plot would get a table and no error. Today the check refuses that (PS03). All four reject this variant.
4. **A table entry could be missing from the export.** Today a plot's own data file is written only when the plot has tier 3 or audit steps (`app/handlers/export_handlers.py:1438`). A table entry with neither must still be exported, always.
5. **100 rows must not pass for the result.** The screen must say "Showing 100 of N rows", in the result table and in the preview.
6. **A summary can differ silently between runs or readers** (scientist, by a run): a NaN in a group gives NaN for the mean while an empty value is skipped; the middle value of [2, 4] is returned as 4; the order of groups is not fixed without a sort; the number of rows per group is not shown unless the recipe adds it; no rounding is applied anywhere. To be said in the documentation for authors, and to consider as advice of the recipe check.
7. **The word "plot" would be shown for a table** in the audit dialog and the lineage notes (`lineage_walk.py:544, 592`) until the wording is changed.
8. **The same table twice on one screen**: the result table above and the data preview below (T3). The preview must say so, or change what it shows under a table sub-tab.

## 3. The options for a table as a result
| Option | Scientist | Architect | Developer | User | Reopens (information only) |
|---|---|---|---|---|---|
| **2A** nothing new: seen in the data preview and the export | con: 100 rows; the preview follows the plot | con: no named result | con: gives no result table | con: a table that belongs to no plot is not found | nothing |
| **2B** a second list `tables` beside `plots` (round 1's choice) | workable | **withdrawn by the architect**: round 1 counted 19 places; in fact about 15 more handlers read the list of plots directly, and almost all of them want EVERY entry (keys, storing, audit, lineage, export). A second list would be a second path, and a missed place fails silently | less reuse than it looks: a second reader, a second key, a second id check | second choice: easiest to see in the file, but a second list to learn | D-0109; D-0063, D-0237 (tier 3 "at the plot entry") |
| **2E-1** text plot, recognised by the ABSENCE of `mapping` and `layers` | reject: a forgotten drawing part silently becomes a table | reject: PS03 loses its job | reject: a silent change | reject: "the worst one" | PS03 |
| **2E-2** text plot, said by ONE EXPLICIT KEY on the entry (for example `show: table`; the name is open) | **preferred**: screen, export and report can be one object, all read from the stored T3 | **preferred**: one list, one way to ask "is this entry drawn?"; a missed drawing place fails loudly, not silently | **preferred**: "the only variant that is complete and has no guess in it" | **preferred**: one sentence in the documentation; a forgotten drawing part is still an error | PS03 (lifted only for the explicit key); D-0109; the definition of tier 3 (D-0063, D-0237, D-0343) |
| **2E-3** text plot, said by an engine name | con: hides the choice in an engine name | reject: an engine here is a library with components; a grid is not an engine; callers would still branch | reject: puts "table or picture" into the engine list | reject: jargon | D-0238, D-0239 |
| **2F** a mark on a table or join; HOME shows its highest tier with steps | con: the user cannot tell which stage is shown | reject: second lookup; ids could collide; no short name, no group | no id and no entry for a tier 3 | "the worst for the reader": a mark in one part of the file makes a table appear somewhere else | D-0237, D-0250 |
| **2D** a picture of a table | not reconsidered: the data stays data (your rule) | | | | |

## 4. Question 1 again (tiers of a table no plot reads)
All four keep the answer of round 1: tier 2 is allowed on every table and join and is really built; a tier 3 belongs to an entry that shows something, and that entry may now be a table. The two checks that refuse tier 2 today would read "no entry reads this table". Open between the viewpoints: whether that stays a refusal (developer: "or go, say which") or becomes a notice (architect).

## 5. My recommendation (the coordinator's; yours to accept, change or refuse)
**Your "text plot", in the form 2E-2:** the entry stays the only kind of thing a group holds; one explicit key on an entry says "show my table"; everything else about it is an ordinary entry (short name, the table it reads, optional own last steps). All four viewpoints chose it, and the architect withdrew the second list of round 1 after counting the code again.
It gives what you asked for: the table at the highest tier with steps is shown as the result; the data machinery is reused; a tier 3 can be the final table of a result with no plot.
What it does NOT avoid, said plainly: the showing must be built (flag 2), in one pass with tests first, so that a table entry cannot be on screen and missing from the export.

## 6. What stays yours to decide if you choose it (nothing chosen)
1. The key and its words: `show: table` is only an example. And the two refusals that keep it honest: a table entry that also has a drawing part is refused; an unknown value is refused.
2. The list is named `plots` and would hold tables. Keep the name (architect: keep it, and say in the documentation "plots holds the results the user looks at: a plot or a table"), or rename it.
3. The definition of tier 3. The architect's proposal, one sentence: "Tier 3 is the last data stage of one result: the steps that only the entry that shows the table reads, a plot drawing it or a table entry showing it as a grid." Your words are what counts.
4. Your earlier line (D-0109): "A table on itself can produce results that are interesting for the user but need to have plots". Does it stand, changed? A group could then hold only tables.
5. A tier 2 that no entry reads: refused as today (in the new words), or allowed with a notice.
6. What the data preview shows under a table sub-tab (the same table again, with a sentence; or the earlier stages only).
7. For a summary: is the number of rows per group required, advised, or left to the author? Rounding?
8. The Gallery: plots only as today, or table entries too.
9. The words on screen. Suggestions of the user viewpoint, not final: badge "Result: table (T3, after all recipe steps)"; "Showing 100 of 4,213 rows. Switch on All rows to see the whole result."; under it "This is the same table as the result above. Use T1, T2 or Source to see earlier stages."

## 7. A build order if you choose it (developer; each slice complete, no shim)
1. Tests first: one test per place that draws, with a table entry; screen, export and report hold the same table row for row (all rows, not 100); the key of a table entry equals the key of a plot with the same steps; a table entry with a drawing part is refused.
2. The format, the check, and ONE function that answers "is this entry drawn or shown as a table?", used at every place.
3. The places that draw every entry skip a table entry: the opening, the export pictures, the Gallery previews, BLUEPRINT's live plot. The export and the report get the table (side by side).
4. The words of the audit dialog and the lineage notes.
5. HOME: the table in the plot area, "All rows" and its sentence, "Original" against "Audited" for a table. Last.

## 8. The work in progress
- The lineage library part (a table no plot reads is a line): kept under every option; merge first, then extend.
- The export of every table (built, waiting for its review): kept. Under your idea an entry still names the table it reads, so its list of "tables no plot reads" stays right; one comment in it ("a tier 3 is a plot") must be rewritten.
- The questions held by the review session (ticked or not, the words of the line, the reach sentence, the two routes) still wait for your answer here.

## 9. Not verified
No screen was run for this round. The count of places that read the list of plots differs between the architect (about 15 handlers beyond the 19) and the developer (66 reads in 27 files): both counts were made by search, and they count different things; a scout settles the exact list before slice 2. The first round's open point stands: whether the opening already builds tier 2 of every table.
