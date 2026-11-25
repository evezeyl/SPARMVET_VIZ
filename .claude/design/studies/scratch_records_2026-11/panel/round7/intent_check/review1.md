# Strict check 1 of home_redesign_intent_and_consequences.md (commit e9fc1e15), 2026-11-16
Reviewer: checker. Read: the channel blocks M124-M126, M131, M146-M149, M118, M102; Eve's own turns of T92, Tcd, Tad, T28 (extracted to text, searched by turn line); AS 510-666; reading guide (all); contract 7.2; recipe_format_spec DEC rows (DEC15-18, 39, note 2026-11-15) and plot entry section; code lines E1-E7, E12. Not read: the UML pictures, HM, archive tag, other 2 sessions' turns beyond grep.
VERDICT: CORRECT FIRST (no WRONG answer; 6 INCOMPLETE; 6 of 28 sampled READ labels fail; 5 decided points missed).

## 1. The 12 test answers (doc line numbers = lines of the committed file)
| # | Judgement | Her words / source | Gap: hers or the document's |
|---|---|---|---|
| 1 | RIGHT | Tcd L1383 "audit steps are added to the recipe (created as copy ... steps of the original cannot be edited)"; Tcd L1790 "added in the audit recipe that is a full copy" | none |
| 2 | RIGHT | Tcd L1774 "does not change the steps of the plot - it changes the data before the plot - ... plot must read the data after T3"; Tcd L1790; T28 L38 "there is no audit of the plot (not yet ...)" | none |
| 3 | INCOMPLETE | Tcd L670(e) / recipe spec note 2026-11-15 "T3 is the data that goes to the plot BUT not the plot recipe"; DEC17 + AS:162 (Eve 11-12) "the T3 list sits at the plot entry BESIDE the spec, not inside it" | DOCUMENT's. The doc says both "not the plot recipe" and "steps.tier3 at the plot entry" but never says the entry's list is a data list beside `spec`, not part of it. Also missed: recipe spec R1 (spec-level `filters` stay allowed until the engine reads tier3, then migrate; S2 A4 "confirmation") = a real open point not in section (d) |
| 4 | RIGHT | Tcd L1790; M147 "nothing is left out"; Tcd L986 errors captured | none |
| 5 | INCOMPLETE | M131 (her two modes: results in HOME "the recipe produced this with the data used", user may select the data; and "the changes in the audit"); the paragraph she CONFIRMED (Tcd L1497 "original and audit recipe correct"; S2:19 line 7 "The export is the audit recipe"); Tcd L1368 "the audit recipe becomes the recipe you can export"; ADR-097 (11-09, Eve: mode 1 never holds the recipe); AS:346 P4b (11-12, one tick off by default) | BOTH. Real open of hers (O1). But the document hides that her later words contradict the old records: the doc calls "holds neither file" Reading 1 and E12 says the docs page "stays", while the later word (11-15) says mode 1 holds the recipe with the data used. L200 vs L201 is that conflict, shown but not reconciled |
| 6 | RIGHT | T92 L115, L7849; Tad L8704 | none |
| 7 | RIGHT | Tcd L1383; M125 line 5; Tcd L670(e) | none |
| 8 | INCOMPLETE | Her only words: T92 L11773 (11-13) "In audit ? the unto is the remove step button" and Tcd L1383 (remove an added step). "Undo last / Revert to step N / Remove all" are AS:53,78,327 (agent design), HO:124 | DOCUMENT's: three controls given as decided; no word of hers found for Revert and Remove all; her word on Undo says undo = the remove-step button (maybe no separate Undo) |
| 9 | INCOMPLETE | T92 L10291 (field -> lineage -> user ticks; key = warning only); T92 L8831/L9111 (11-12, Norway: country comes from metadata; remove samples there; others unmatched); AS:119 (helper list of key values) | HERS, real open (O4: 21 or 28). The doc omits her Norway words L8831/L9111 |
| 10 | RIGHT | Tcd L1013 "S2-3: a ... can we block recipes from edit if they are in use ... a warning"; M102 | real open of hers (O6), plus M102 notes the build already notices a changed recipe |
| 11 | INCOMPLETE | T92 L9231 "T3 ... empty = T2 ... backward all have T2 of T2=T1"; Tcd L986 "in order written in the recipe - and performed in audit"; AS:135 steps go at the END of the tier list of the chosen node; ADR:5239 key chain T1 -> T2 -> T3 | DOCUMENT's: the order T1 steps, T2 steps, T3 steps, each tier's audit steps after the recipe's own in that tier, is implied in (b)5-6 and C2, never stated as one rule. She said it |
| 12 | INCOMPLETE | M118/channel line 774: "N7-2 DECIDED: final audit steps carry who and when; `audit_history_log` is a separate optional part, written by default, never mixed in" (Eve yes, 11-15); Tcd L1264 "M7-2 (who eg. initials) - ok" | DOCUMENT's: it says "may keep" (first page 8, L25) and O8 "not confirmed by her words". Decided. |
Count: RIGHT 6 (1,2,4,6,7,10), WRONG 0, INCOMPLETE 6 (3,5,8,9,11,12), NOT SAID BY HER 0 as a whole answer (a piece of 8 is). Of the six "in part" (3,5,9,10,11,12): real open of hers = 9, 10, and the core of 5; document's gap = 3, 11, 12 and the confirmed line in 5.

## 2. 28 READ statements sampled (first page 1-14 all; (a) 8; (b) 5; (c)/(d)/(e) 3)
FAIL (6): 
1. First page 3 "Audit mode is the only way to change data, a plot or the export [T92 L7815; Tcd L1165]". Neither source says it; it is reading guide section 1 point 2 (agent text of 11-12). Her L7815 says the audit "is NOT for exploration; not aimed to clean messy data". It can be read as "the audit changes a plot", against Tcd L1774.
2. First page 8 / (b)8 "a separate history log may keep them": N7-2 DECIDED written by default (M118). Weaker than the record.
3. C4 / (b)8 "Undo last, Revert to step N, Remove all ... DECIDED [AS:327-328; HO:124; QC:25]": agent's sentences; her word T92 L11773 reads "undo is the remove step button".
4. (b)2 "(later a 'Source' choice too) [PF:19; HO:125]": HO:125 is "decided 2026-11-13 (Eve)": selector Source | T1 | T2 | T3 with a dataset dropdown. "Later" misleads. (minor)
5. O8 "not confirmed by her words": see 2 (N7-2).
6. O1 "Also open: does the user choose the data used": she said it (Tcd L1497: "the user will be able to select data to use - to replace the default data used in the recipe ... data produced regularly (pipelines)"). It is an intent, not a question. Also (b)11 uses T92 L8097 for "original plot beside the affected plot": that turn says "this is unclear for me ... seems ok otherwise"; the decision is AS:346 (P4b) only (weak, not counted).
PASS: first page 1,2,4,5,6,7,9,10,11,12,13,14; (a) T92 L3370, Tad L8704, T92 L1563, Tcd L1203/L1368, T92 L10656/L10694, Tcd L1165, Tcd L1759, all dates and times checked; S2-3 "a" (ledger line 92 confirms); ADR 5123, 5125, 5334-5338, 5343 say what is cited.

## 3. Decided points in the unread sources that the document lacks or contradicts
- The three levels info / warning / block; only technical problems block; warning needs "I understand"; guard-rail registry (AS:19 section, Eve 11-12 P7 "a good start"). Missing.
- Reason = free text, required, hashtag convention, no fixed categories (ADR:5125). Only "needs a reason" on the page.
- Attrition per step (rows and entities, derived never stored), figure caption "n = X after exclusions" in the report text, on by default (Eve 11-12 P7 "Ok proposal"); `exclusions.tsv` (11-12). Missing.
- Pre-export review gate (D5), accepted (guide O7). Missing.
- Data-agnostic rule (Eve 11-12, guide W7): no field word in code or fixed texts. The doc's example uses sample ids and Norway-type words with no such remark on page 1.
- Drop of a join key is refused in audit; join-key safeguards turned on (guide O12, 11-13; DEC26; contract 12g.3); key = information. Missing.
- Recipe spec R1 / spec-level `filters` vs `steps.tier3` (open, DEC17). Missing from (d).
- Source | T1 | T2 | T3 selector decided (HO:125); contradicts "later".
- Contract 7.2: bundle table lists `data_analysis_recipes/<proj>/` always and rule 4 "from any view": stale against ADR-097/098; absent from (e).
- N7-2 (above). S2-2 (Tcd L998: she cannot see how a text value reaches a number column, wants the data scientist to check): not decided, absent from (d).

## 4. First page
Change: line 3 (see 2.1: say "In HOME, audit mode is the only way to change what the audited plots, the tables and the export show; it adds steps that change the DATA before the plot and never the plot recipe"); line 8 ("may" -> written by default, separate, N7-2); line 11 (add: she confirmed "the export is the audit recipe" and said mode 1 = results with the recipe and the data used, user may select the data; records say recipe only when ticked: open); line 6 (define T1, T2, T3, lineage, tick in one line each: T1 table after the recipe's first steps, T2 after its second list, T3 the plot's own data after its list; empty = the node before). Add a line: section (b) ids are illustrations; add data-agnostic; the two names "original recipe"/"audit recipe" (screen words open). Line 5 add her limit "colour changes one day, not now" (Tcd L1790). Lines 1,2,4,5,7,9,10,12,13,14,15 true.

## 5. E1-E15, five opened
E1 (home_theater.py:433-469) true. E2 (t3_translator.py:30-40,213) true (fork, repoint). E3 (export_handlers.py:1303-1311) true but nuance: the plot's steps stay in the publication part; only the engine-replayable recipe omits them (doc says "skipped"). E4 (recipe_check.py:46-47, ~900 "TIER3_READ_BY_ENGINE = False", P05) true. E5 no Undo/Revert/Remove all in audit_stack.py: true. E7 line is 187 not 186 (trivial). E12 lines true. Not checked: E6, E8-E11, E13-E15 beyond line existence of E8, E11.

## What these checks cannot see
Turn extraction used `origin.kind == human`; pasted briefs in Tcd may hide a few of her turns. T92 sessions I did not read in full (158 turns): I read the cited ones and searched "revert|remove all|history log|norway". Tad and the other transcripts only searched.
