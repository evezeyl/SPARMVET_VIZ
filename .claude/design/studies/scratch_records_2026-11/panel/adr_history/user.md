# ADR history and "what stands now": the READER's viewpoint (panel-user, 2026-11-20; saved by the coordinator from its report)

It read FACTS.md, three ADRs (086, 098, 099: `.claude/knowledge/architecture_decisions.md` lines 4174-4218 and 5029-5118) and the head of the ledger. It did not check any banner against the app.

## Flagged first: an old rule can be read as current
1. ADR-086 (lines 4176-4182): three banners stacked, the newest on top, the third telling the reader to ignore the second; the body still says "Status: ACCEPTED" and "IMPLEMENTED 2026-11-05" and "Defaults: Data to show = Result": the old rule, with nothing on the sentence itself marking it dead.
2. ADR-098 (line 5031 against 5033): one line says the entry is superseded and the replacement is built; the next says "Built on dev ... It describes what the app does today"; the body says "Status: ACCEPTED"; point 4 is struck through AND marked "[No longer holds]".
3. ADR-099 (line 5057 against 5061): the banner says "BUILT in part" and names the audit file, the dialog and the opening build with decision numbers, then ends "NOT BUILT: the audit recipe file and its record, the new dialog and its walk, the opening build"; line 5061 still says "Not built." The reader cannot tell which is true. [Coordinator: the opening build was merged on 2026-11-20 at 16:35: this banner is now out of date; a scribe corrects it.]
4. ADR-098 lists its points 7, 8, 9, then 6. ADR-099's reading guide says "What holds now" inside an entry that is partly history.
5. The ledger was the only place it could rely on, but the ledger does not say which lines are built.

## One question: "in HOME, what does a filter change today?"
Read: ADR-086 (three banners, 44 lines), ADR-098 (three banners, the body), ADR-099 (a banner, a status line, a reading guide, the points); the ledger lines named in the banners were not on the page. Misleading: line 5042 "In plots they apply only on My view" and line 4203 "Plot to show ... controls the plots only": both read as current; only a banner above says otherwise. About 15 minutes of careful reading, and still not sure at the end.

## The options, from the reader's side
- O1 one file per ADR, an index of those in effect, superseded ones archived: opens the index, sees titles. A title "in effect" hides that only one POINT of the ADR is in effect: whole-file moves cannot show a partial replacement. Cost: about 1,400 references by number and the UML audit.
- O2 two files, "in effect" and "history": the same long prose without its history; would not be trusted; a partly replaced ADR must be cut in two; the link between a rule and why it changed is lost.
- O3 the log kept as the archive plus a "what stands now" page per topic, each sentence citing its sources: opens the topic page ("HOME header and filters"), sees short sentences with sources. Closest to the reader's question. Risk: the page drifts from the code if nobody updates it.
- O4 the ledger as the record, ADRs only for architecture: one line per decision (373 lines, ten fields): too fine to read as a whole; it records decisions, not what is built nor where; the reasons that ADRs carry are lost.

## What a "what stands now" entry must contain
The rule in one or two plain sentences; a status ("in effect, built" or "decided, not built"); since when; where it lives (file:line or the screen name); a LINK, not text, to what it replaced; the ledger and ADR numbers behind it. NOT: the reasoning, struck-out text, "was previously" prose, counts of work done. A rule that is partly built is split into two entries.

## Partly replaced; decided, not built
- Partly replaced: the ADR stays as it is in the archive; "what stands now" has one entry per POINT, each "in effect since [date]" or "replaced by [link]".
- Decided, not built: a separate section, never in the same list as built rules, each with the line "Today the app does [X instead]".

## Words
Understood without explanation: "in effect", "replaced", "decided, not built". Not understood: "accepted" (by whom? built?), "proposed", "enforced", "implemented" (they mix deciding and building). Smallest set: In effect (decided and built); Decided, not built; Replaced (with a link); Open (not decided). The page head says "Last checked against the code: [date]".

## Recommendation
O3, with the entries drawn from the ledger numbers (O4 as the source). The ADR log stays untouched, so no reference breaks. The first page must: say when it was last checked against the code and list what is in effect per topic in one line each; show "in effect" and "decided, not built" apart; link every entry to its sources.
