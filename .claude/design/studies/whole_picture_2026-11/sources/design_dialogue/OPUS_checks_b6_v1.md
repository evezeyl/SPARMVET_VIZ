# Opus check of SONNET_b6_2.md, Part B (the draft for the two study files), case D-0572 (2026-11-23)

**What this is.** The check of Part B against its sources: every fact against the file it cites; her words against the channel block "### M627 from sparmvet-viz-cb" (fixed-string searches); B6 shown as HER PROPOSAL, not chosen; the demo numbers per join direction; the 36 / 42 claim on `Detailed_summary`; the eleven questions; my lean, exact; no cost or effort argument; data agnostic. Reading only, NO RUN. No study file is edited. "draft N" = line N of `SONNET_b6_2.md`.

**Checked and right as drafted** (no replacement):
- Her words: the four quotes of draft 57 and 169 are exact, and so are the short quotes ("only a recipe maker (in collaboration with a real user) can decide", "metadata should be clean - all with an id", "That would remove need for 6 anti join", "the user must add the ID and update metadata"). Each was found as a fixed string in the block. Ledger D-0572 exists and holds them, with "NOT decided: where the completion lives ...; the marker and its name; whether B6 is chosen".
- **The 36 / 42 claim** rests on an engine run, not on a reading: RECIPES G12 ("`Detailed_summary`: 280 rows and 42 distinct in the file, 91 rows and 36 distinct at tier 1 [RECIPE FILE; ENGINE RUN RR2; file read]"); RR2 is my register entry `RUN_REGISTER_opus_recipes.md` (RR2 `demo_join_cardinality`, DONE: "Detailed_summary (91, 36)"). The three filters are at `Detailed_summary_wrangling.yaml:20, 25, 30`, and no other step of that tier removes rows (a split, an unnest, a rename, a cast, a computed column, a drop: lines 3-19 and 35-36), so the 6 entities are removed by the filters. Not counted again (no run).
- The demo numbers of the B6 table (draft 67-72) in all three join directions; the flags 1, 2, 4 and 5 with their files (`ST22_Anchor_wrangling_tier1.yaml:47`, `plots/integration_plot.yaml:9`, `polars_calls.py:54-60`); the engine order (`orchestrator.py:264-267, 282-300`; `data_wrangler.py:92`); the keys (`cache_keys.py:14-20`); S01 (`recipe_check.py:390`); the spaces note (`declared.py:115-120`); (iv) does not fit (D-0322, D-0541); the T0 quote (D-0509).
- No cost or effort argument. Data agnostic, except the demo's own names where the demo is meant.

---

## The replacements (numbered; old text → new text)

**R1. Tags, everywhere in Part B** (the ledger line now exists).
Old: "[HER WORDS M627]" (draft 57, 121, 169, 176).
New: "[HER WORDS D-0572]".

**R2. draft 57** (the quote holds her proposal too).
Old: "**Her words, exact** (channel block M627). Her answers to the facts:"
New: "**Her words, exact** (channel block M627; ledger D-0572). Her answers to the facts, then her proposal:"

**R3. draft 59** ("it" in "it knows the risk it accepts" is not the app: her sentence is "the recipe maker has to consider those cases specifically and the 3. it knows the risk it accepts". My own round-1 position made the same slip.)
Old: "the meaning of a missing value is for the recipe maker with a real user; the app accepts the risk."
New: "the meaning of a missing value is for the recipe maker with a real user; "it knows the risk it accepts" (our reading: "it" is the recipe maker, who "has to consider those cases specifically"; the risk is that the app cannot tell "not analysed" from "analysed, nothing found")."

**R4. draft 63** (her words name the moment; the variant is question 5).
Old: "before the recipe's steps; the added line is marked;"
New: "at the first step (your words: "an automatic completion at (first step)"; question 5 asks whether before or after the recipe's own tier-1 steps); the added line is marked;"

**R5. draft 64** (what the author writes depends on question 1).
Old: "- **What the author writes.** A key on the data table, for example"
New: "- **What the author writes.** It depends on where the completion lives (question 1). With (i): a key on the data table, for example"

**R6. After draft 74** (the line "  [REASONED from the engine order ... NEEDS A RUN after your choice]"), insert:
"  Why the middle column has three states: after a left join from the metadata, an entity that has no line in the result table gets one row whose result columns are all empty, the marker included; an added line has the marker set; a file line has it unset. [POLARS SEMANTICS; REASONED]"

**R7. draft 84** (flag 3: why the 6 are the filters' doing, and what the count rests on).
Old: "`Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`); its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities;"
New: "`Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`), and no other step of that tier removes rows [RECIPE FILE `Detailed_summary_wrangling.yaml:3-36`]; its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12, engine run Opus RR2]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities: with the data table first they are absent;"

**R8. draft 90** (the order of the added lines).
Old: "leaves the Source view true to the file and runs BEFORE any audit step."
New: "leaves the Source view true to the file and runs BEFORE any audit step. The added lines come in a fixed order (for example the order of the metadata), so that the same data give the same rows in the same order [RULE FILE `rules_data_engine.md` section 2, Determinism, ADR-090]."

**R9. draft 99** (the recipe side of (iii) is exactly run 1).
Old: "| NEEDS A RUN | yes | yes (and an engine change) | no for the recipe side | no |"
New: "| NEEDS A RUN | yes | yes (and an engine change) | yes: run 1 below (the added lines written by hand are the same test) | no |"

**R10. draft 101** (a third source, from my position, missing in the draft).
Old: "but ResFinder's first place lies below the metadata's: two places on one path (flag 4)."
New: "but ResFinder's first place lies below the metadata's: two places on one path (flag 4). A third source exists if the recipe declares `entity.population`: with a manifest of the analysis as the population, the marker would mean "analysed, nothing found" (the key exists and is checked, E02 [CODE READ `recipe_check.py:332-348`]; nothing else reads it today [ESTABLISHED: OVERLAP section 3])."

**R11. draft 117** (the alert's words are not decided).
Old: "(what the alert says: the file, how many lines were added,"
New: "(what the alert says, words PROVISIONAL: the file, how many lines were added,"

**R12. draft 119 and 121** (the risk: see R3).
Old (draft 119): "### The risk you accept"
New: "### The risk (your words)"
Old (draft 121): ""it knows the risk it accepts" [HER WORDS M627]: the app cannot tell"
New: ""it knows the risk it accepts" [HER WORDS D-0572] (our reading: "it" is the recipe maker): the app cannot tell"

**R13. draft 127** (Q1: what her words settle does not depend on B6, which is not chosen).
Old: "| 1. A never-analysed entity counted as "not detected"? | settled: the marker says "no result"; "only a recipe maker (in collaboration with a real user) can decide" | nothing for the app |"
New: "| 1. A never-analysed entity counted as "not detected"? | settled: the meaning is the recipe maker's, "which only a recipe maker (in collaboration with a real user) can decide"; with B6 such an entity would show as "no result in file" | nothing for the app |"

**R14. draft 133** (Q7: conditional on B6).
Old: "| 7. The number, the list or both | B6 gives both from one table | how the list is shown |"
New: "| 7. The number, the list or both | if B6 is chosen, both come from one table ("That would remove need for 6 anti join") | how the list is shown (the key of a table as a result is open, D-0487) |"

**R15. draft 138** (my lean, exact; replace the whole line).
Old: "- Lean of the Opus agent, as a lean: (i), a read-time option declared on the data table, automatic for every result table that declares an entity id (variant i-b), placed before the tier-1 steps (P1). The source: (α), the metadata as read from its file. The marker: m1, a yes/no column, with its meaning required by the completion. With B6 the data table first keeps the initial population and the zeros, and a removal at the result table is complete. [as the Opus agent states them]"
New: "- Lean of the Opus agent, as a lean: if you choose B6, (i) a read-time option declared on the data table, automatic for every result table that declares an entity id, with its meaning required (variant i-b), done before the recipe's own tier-1 steps (P1, your words "at (first step)"), reading the metadata as read from its file (α), with the marker m1, a yes/no column beside empty cells; and the data table first. Reason: the recipe then states the completion, so the app does not modify the recipe; a removal written at the end of the result table's tier 1 runs after the completion and is complete; with the data table first the result keeps the initial population and its zeros; α keeps the result table's first place a first place (D-0553). What P1 asks of the recipe maker: a filter in that tier 1 that removes every line of an entity leaves it absent (on the demo, 6 entities of `Detailed_summary`); a rule written as a mark instead of a filter keeps it."

**R16. draft 143** (Q2 is half answered by her words: "an automatic completion").
Old: "2. **Automatic for every result table that has an entity id, or only where the recipe names it?** On the demo both give the same 4 lines on ResFinder; the APEC reference list has no entity id and is never completed. Neither: say what you meant."
New: "2. **You said the completion is automatic ("an automatic completion at (first step)"). Should the recipe still carry one line that states it and its meaning, or nothing at all, the documentation and the alerts saying it?** On the demo both give the same 4 lines on ResFinder; with one line the recipe shows them; with none only the alert and the export's report do. The APEC reference list has no entity id and is never completed. Neither: say what you meant."

**R17. draft 144** (Q3: her words first).
Old: "3. **Must the recipe state what the marked lines mean** (the check refuses the completion without it), or is the data check's note enough?"
New: "3. **You said the recipe says how those lines are processed, "forcing the recipe maker to consider this case". Must the recipe state what the marked lines mean** (the check refuses the completion without it), or is the data check's note enough?"

**R18. draft 145** (Q4: her words first).
Old: "4. **The marker: a yes/no column or a word in the cells, and its name.**"
New: "4. **The marker (you asked for one "short and explicit", "a different kind of other "missing value""): a yes/no column beside empty cells, or a word in the cells, and its name.**"

**R19. draft 146** (Q5: her words first).
Old: "5. **When in the table: before the recipe's own tier-1 steps (they see the added lines) or after them?**"
New: "5. **When in the table? Your words: "this might be before T1 a step the app does". Before the recipe's own tier-1 steps (they see the added lines), or after them?**"

**R20. draft 148** (Q7: the middle case was missing).
Old: "data first, 41 samples; metadata first and genes only, 42 samples with 5 in the bar at 0."
New: "data first, 41 samples; metadata first with the marker read, 42 rows with 1 shown as "no line"; metadata first and genes only, 42 samples with 5 in the bar at 0."

**R21. draft 149** (Q8: her preference first).
Old: "8. **An id in a result file and in no metadata: the note only, or also the marker "not in metadata"?**"
New: "8. **An id in a result file and in no metadata: you prefer the metadata corrected. Should the app also offer the marker "not in metadata" (you said it "could be done"), or the note only?**"

**R22. draft 151** (Q10 is answered by her words; it must not be asked again).
Old: "10. **The three id-less lines of `demo_abromics`: remove them from the file?** On the demo recipe `demo_abromics`: 27 lines, no removal step, no example of a messy id; or keep them as a lesson. Neither: say what you meant."
New (a note after the list, not a question): "(Not a question any more: the three id-less lines of `demo_abromics`. Your words "metadata should be clean - all with an id" and your order "remove the null and empty rows from the metadata" (D-0569); the change is shown in the dry run of the one big move, D-0525.)"

**R23. draft 152** (Q11 held two questions; the list's display is D-0487's open key, R14). Renumber it 10.
Old: "11. **The list of the not-detected and the count per target.** The list is the marked lines, shown as a table result (decided design, not built, D-0485, D-0487); the count per target ("how many entities carry no gene X") is not covered. Neither: say what you meant."
New: "10. **The count per target: for each target (on the demo, each gene), how many entities do not carry it?** None of the forms above gives it: it needs one line per entity and target. On the demo you would see, for any one gene, how many of the 42 samples lack it. Neither: say what you meant."

**R24. draft 159** (run 5 can run only once the completion is built; with (iii) the key moves with the file only).
Old: "5. **The keys.** Requirement:"
New: "5. **The keys (once (i) or (ii) is built; with (iii) the key moves with the file only).** Requirement:"

**R25. draft 173** (the alert's words are not decided).
Old: "said in the documentation and in the alerts: "N lines added"
New: "said in the documentation and in the alerts (words PROVISIONAL): "N lines added"

**R26. draft 176** (the risk: see R3).
Old: "**The risk she accepts:** the app cannot tell "not analysed" from "analysed, nothing found"; the notes say so. [HER WORDS M627: "it knows the risk it accepts"]"
New: "**The risk:** "it knows the risk it accepts" [HER WORDS D-0572] (our reading: "it" is the recipe maker): the app cannot tell "not analysed" from "analysed, nothing found"; the notes say so."

---

## The eleven questions, after R16 to R23

Ten questions remain, each hers, one at a time, with what she would see: 1 where the completion lives; 2 one line in the recipe or none; 3 a required meaning; 4 the marker's form and name; 5 before or after the recipe's tier-1 steps; 6 which metadata; 7 the join order; 8 the marker "not in metadata"; 9 a note for a repeated id; 10 the count per target. Q10 of the draft (`demo_abromics`) is answered by her words and becomes a note for the dry run. None is answered for her; Q2, Q3, Q4, Q5 and Q8 now start from her own words.

## Closing

I sign the draft with these replacements applied.
