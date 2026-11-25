# Review of WHOLE_PICTURE.md: are the decisions quoted truly (2026-11-22)

VERDICT: FIX FIRST (text only; none changes the picture). 431 citations, 117 distinct ledger numbers in the main document; 145 in the tables file: all exist, all DECIDED, all taken by EVE; no wrong number. The wording of about 90 lines was read in the ledger. No replaced line is presented as in force (D-0316/D-0508, D-0346/D-0451, D-0146/D-0332, D-0315/D-0478, D-0324/D-0389 are handled correctly).

## A. Citations that are not true as written
| Place | The document says | The ledger says | To do |
|---|---|---|---|
| Section 5 intro "Not asked, because you closed them" (D-0511, D-0513) | she closed the two metadata points; "a table's kind is declared by its block" | D-0511: her words are only "well it seems trivial the metadata is what carries the sample information - derived tables should already have the metadata joined ..."; "both points closed" is the review session's bracket ("she was not asked to confirm it"); D-0513: the mapping block to kind is a bracket reading | say "closed by the review session's reading of D-0511"; do not present the closing wording as hers |
| Q1 option (b): "it applies D-0509 and D-0510"; recommendation "keeps the original tables unchanged, as D-0509 says" | (b) is what D-0509 and D-0510 mean | D-0509 her words: "keeping the raw data unchanged"; the line says "NOT decided: which place is the earliest in that sense"; D-0501: "the earliest place of each branch - which is the original data basically"; D-0508: "near the original table" | (b) is a legitimate option; remove "applies" and "as D-0509 says"; "(b) reopens nothing" is arguable: it departs from the literal words of D-0501 and D-0508: say so |
| Section 1 "the picker you asked for, any table of the recipe" (D-0496) | a picker for any table | her words: "pick every original data and see all lineages that goes from there"; D-0496: "NOT decided: whether a lineage picker is built in HOME and in what form; where it lives; what a node shows"; D-0508: "I like the idea of outline at the base" | say that whether it is built at all is not decided; slice 8 must not build it without that |
| Section 1 Words: "An entity is what one row of the metadata describes" | a settled definition | no ledger line says it (D-0224: "metadata is one row per sample id") | mark as the document's wording |
| Section 1 Three kinds: `VirulenceFinder` "as you decided" (D-0513) | decided | her words: "I think VirulenceFinder should be moved under data_schemas"; who and when is not decided (D-0373) | soften to her words |
| Flag 9 and 4.10: "D-0192 removed the recipe from the Publication part" | as stated | D-0192: "removed from mode 1", and "when in audit it is added anyway (via the audit_recipe)"; the line never says mode 1 = Publication | add the audit_recipe clause and "mode 1" |
| Quotes not exact | step 4 of section 1: "if no recipe steps for T3 then T3=T2" | D-0343: "not recipe steps for T3 then T3=T2" | quote exactly or do not use quotation marks |
| | 4.4: "removed from all other results" | D-0499: "remove the bad sample from all other results" | |
| | 4.9: "more a practical trick" | D-0224: "its more a practical tric than a real one" | |
| | 4.11: "See original and modified plot in the export" | D-0147: "In the export we need to be able to see original and modified plot." | |
| | tables file, export-scope row: "all plots of the recipe are exported" | D-0292: "all plots included in the export" | |

## B. Decisions in force that the document misses
1. D-0440, D-0441 (the browser upload is OFF unless the deployment declares a place: "Yes off unless deployment place required it."; a write test at start; a recipe whose name breaks the convention is refused and renamed), D-0393 (2), D-0394 ("overwrite control ... only in its own directory"), D-0437 ("a warning when trying to write on a file name that exists"). They change flag 7 and slice 2: the document cites only D-0390.
2. D-0463 (the lineage colours: "I like green"; NOT decided: which colour means what, the mark for an interruption, where colours appear): affects slices 4 and 8, the propagation drawing, the red lines of D-0460. Not mentioned, not asked.
3. D-0448 (a declared entity key may be dropped in the audit unless a later join reads it) and D-0445 (a column renamed and renamed back is one column): they govern the dialog's places and the drop gate: into the decisions of slice 4.
4. D-0203 (her "yes warn that is good": the dialog warns when a value does not correspond one-to-one between ticked places) beside D-0501 (no per-table warnings about downstream effects): an unexamined meeting point (probably compatible: it is about ticked places): add to section 4.
5. D-0497 (the README, the report and the picture metadata show the app features `ui_label` with its file name): missing from slice 5.
6. D-0433, D-0434 (Data Import replace: no copy, no archive, no recorded old file): the rule text still describes keeping the replaced file: into the list of out-of-date rule texts.
7. D-0455, D-0458 (the engine per tier; stage 0 done): section 1 does not say tiers may run on different engines. Minor.

## C. The pairs
- D-0361 (11-20: "8 - No we had decided to clear them- Only the steps applied in the audit are kept": filters cleared on a mode switch) against D-0505, D-0506 (11-22: "NOT decided: what a change of mode does to the filters", which is review-session text): a real records error; D-0361 is a decision and nothing replaces it. The document is right.
- D-0389 (11-20, later: "1. yes must." the export always contains the original recipe; it names no part) against D-0192 (11-16): real; D-0192 is not formally replaced; correctly left to question 7; say that D-0389 is the later line.
- D-0486 "not merged" and D-0358 "NOT BUILT": stale ledger states (the semi join and the drop rule by place are merged), not conflicts. Correct in the document.

## D. Section 5, question by question
| Q | Verdict |
|---|---|
| 1 earliest place | open (D-0509: "NOT decided: which place is the earliest"); wording: see A |
| 2 later places | open; option (b) removes the ticking of later places, which D-0093, D-0316 and D-0355 give her: say "reopens D-0093, D-0316, D-0355", not only "reaches D-0355" |
| 3 the number | open (D-0508 lists it as not decided) |
| 4 recount after the build | open, BUT D-0508 holds her stated preference: "one option could be to automatically check tables after BUT there is actually no added steps after - Id rather the check is more where you apply it": options (b) and (c) go against it: say so at those options |
| 5 what the log keeps | open (D-0478); add the other not-decided points of D-0478: a step cancelled before confirming; the log's file name and form |
| 6 picker tables / start of Send to Audit | open; add D-0496 "NOT decided: whether a picker is built" |
| 7 the Publication part | open; options (a) and (c) contradict D-0389's "must ... always": say so, and that D-0389 is the later line |
| 8 where the picker opens | NOT clean: the recommended option (the right panel in Exploration) REOPENS D-0383 ("yes (but it will be empty at least for now)"), D-0375 (hidden in Exploration) and D-0385 (closes when leaving Audit); "Reopens: nothing" is wrong |
| 9 a table as a result | open; D-0496 records, as the review session reports it, that she excluded forms 4 and 5 ("we can exclude form 4 and I guess 5"): the document offers forms 4 and 5 without saying so: state it |
| 10 defaults | open |
| 11 words for the stages | open |
| 12 Reshuffle | PARTLY DECIDED, and the document reopens D-0341 unsaid. D-0341, her words: "A - but then we need to be able to add it as a step at the correct place in audit ... when the user is happy with the reshuffle a seed step with the reshuffling needs to be written". Option (a) (a step with a reason) matches her; the RECOMMENDED option (b) (a setting without a reason) goes against it; option (c) (remove the button) reopens "offered only in Audit mode". Only the HOW is not decided |
| 13 dates | open |
| 14 tiers of a table no plot reads | open (D-0457); her D-0451 words "T1+T2 and T1+T2+T3" lean against option (a); quoted |
| 15 advice on mixed kinds | open (D-0511) |

Missing questions (listed as NOT decided in lines of 20 to 22 November; they block slice 4): D-0508: the rule that also ticks a place where the key is created; the marks of the audit log; a step started on purpose at a later table (partly in Q2). D-0451, D-0457: whether the line of a table no plot reads starts ticked, what it says, which step is written there ("ticked like the others" is only a reading). D-0499: whether the dialog warns when a table that computes across entities stays ticked or unticked. D-0463: which colour means what. D-0478: the cancelled-step log and the log's file form.

## E. Section 1 sentences with neither a number nor "not decided"
Audit step 2: "She finds the sample in the story of `mlst_bar` (D-0508)": the story view does not exist; the sentence rests on a wish plus the unbuilt picker: say so in the sentence. (The paragraph "What of this is built today" and the demo facts are facts, acceptable.)

## F. Her corrections of today
- Data agnostic: respected in general statements; one candidate screen text says "rows with this sample: before, after" (heading of 4.8): write "this value" or "this entity".
- T0: never an option; it appears in 3.7, as a quote in 4.1 and in one line of "Examined and dropped": trim to the conflicts list.
- D-0510, D-0513 respected. D-0511: see A.
- Cost: none, except two borderline "For" points of Q1 option (a): "the fewest steps" and "already run twice on the demo": remove.

## Not checked by this review
The code and the runs. About 40 rows of the tables file. The cited lines D-0020, D-0094, D-0312, D-0317, D-0320, D-0321, D-0337, D-0351 to D-0354, D-0356, D-0368, D-0372 were not read.
