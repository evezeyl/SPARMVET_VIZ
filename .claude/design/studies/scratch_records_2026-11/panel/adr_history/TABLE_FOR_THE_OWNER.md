# How to keep ADR history apart from the ADRs in effect: one table for the owner (coordinator, 2026-11-20)

Her words: "The problem is that ADR are not clean if they keep a lot of history - I would like a good solution where history could be separate to current ADRs that are in effect ... who want to know what stands now in a clear maner - and come to me with proposals with pros and cons". And: "for decisions without ADR we will need to maybe have some - and we might want to check logic of what has been added".
Sources: `FACTS.md` (scout, read), `architect.md` (architect and developer; it ran prototypes: a lossless split into 106 files and a generated index), `user.md` (a reader who is not the author). Nothing is built or changed. The panel recommends; she decides.

## Flagged first
1. **Moving whole superseded ADRs to an archive would clean very little.** Only 11 of the 106 ADRs are superseded as a whole: 7 % of the text. The history is inside the ADRs: 32 ADRs have single points that were replaced, 19 mention "not built". So "history apart" has to work at the level of a POINT, not of a file.
2. **A reader cannot answer a simple question today.** For "in HOME, what does a filter change?" the reader needed three ADRs and about 15 minutes and was still not sure. Old rules read as current; only a banner above them says otherwise. Three ADRs (086, 098, 099) carry status notes that contradict each other.
3. **The log can no longer be read in one go by an agent**: it is 487 KB, above the reading limit, so the instruction "read it at the start of every session" cannot be followed as written. About 125,000 tokens; the ledger about 80,000.
4. **The ledger does not show what was replaced.** Only 20 of 373 lines carry a "replaces" relation; some replaced lines are not marked (the first line of the ledger is replaced in practice by two later ones); 8 lines marked DECIDED hold a part that says "not decided".
5. **Rewriting the body of an ADR goes beyond what she agreed today** (status notes only): cleaning ADR text needs her agreement.
6. Two tools would not notice a move: one check passes silently when the log file is missing; the UML check judges an ADR by a text pattern. Both must be repaired before anything moves.

## The options
| Option | What a reader opens and sees | Pro | Con | Evidence | Viewpoints |
|---|---|---|---|---|---|
| O1. One file per ADR; an index page of those in effect; superseded ones in an archive folder | The index: a list of titles | The index is small (about 12 KB); a clean split was run without loss | A title "in effect" hides that only one point of that ADR still holds; cleans 7 % as stated | architect: prototype run | Reader: misleading for partly replaced ADRs. Architect: needs the point-level rule to be worth it |
| O2. Two files: "in effect" and "history" | The same long ADR text, shorter | Simple to say | Text moves between two files; a partly replaced ADR is cut in two; the link between a rule and why it changed is lost | - | Both: not recommended |
| O3. The log kept as the archive; a new page "what stands now" per topic, each sentence with its sources | The topic page ("HOME header and filters"): short sentences, each with status, date, place in the code or on screen, and links | Closest to the reader's question; fast; no reference breaks | The sentences cannot be generated: a person or an agent writes them, so the page can drift from the code; the log itself stays unclean | reader: its recommendation | Reader: recommended. Architect: fine as a bridge, not as the end state |
| O4. The ledger is the only record of decisions; ADRs only for architecture, pointing to ledger lines | 373 lines, one per decision | One record of what she decided | Too fine to read as a whole; holds no reasons or consequences; does not say what is built or where | - | Both: not as the "what stands" view |
| O5 (architect). One file per ADR, kept in place; each file starts with a small fixed head (status; built or not, with the task; what it replaces and what amends it; the ledger lines behind it); the history of each point moves to a tail section of the SAME file; a generated index; checks that fail when the state is stale | The index (generated from the heads): what is in effect, what is decided and not built, what is replaced; then one clean ADR | History is apart but not lost; partly replaced points are handled; the index cannot drift (it is generated); can be done in five steps, each leaving a working state | The largest piece of work; cleaning the bodies needs her agreement per ADR; 188 files cite the log's path, 38 anchors and 17 line-number citations must keep working | architect: counts and prototype run | Architect: recommended, in steps |

## Where the viewpoints agree
- Whole-file moves alone do not solve it; the unit is the point.
- Four status words are enough and understood without explanation: **in effect** (decided and built); **decided, not built**; **replaced** (with a link); **open**. "Accepted", "enforced", "implemented" mix deciding and building.
- "Decided, not built" is shown apart from what is in effect, each with "today the app does X instead".
- The ledger holds WHAT she decided; an ADR holds how it is built and why. Neither replaces the other. (The architect's reading: to be confirmed by her.)

## Where they differ
- Reader: the "what stands now" page first, per topic, in plain sentences. Architect: that page is a sixth place that can drift; the lasting fix is the head on each ADR and a generated index.
- They fit together as steps: the page as the bridge now, the heads and the generated index after.

## The coordinator's recommendation
Step 0 now (no ADR text changes): a generated index of the 106 ADRs with their status, and the repair of the two tools. Step 1: one "what stands now" page for HOME (the topic where a reader is lost today), written from the ledger and checked against the code, as the model for the others. Then O5 in steps, each with her agreement before any ADR body is cleaned.

## The decisions without an ADR
- 239 of 275 ledger lines on architecture-like topics name no ADR.
- Proposed rule of thumb for "this deserves an ADR": it sets a boundary between parts; a format or a security rule; something that must always hold; a choice between real alternatives; something hard to reverse. Everything else stays in the ledger and in the design pages.
- A first grouping gives 18 candidate ADRs (titles and ledger numbers in `architect.md`), about 10 of them amendments of existing ADRs.

## What she would decide (when she asks; nothing here blocks a build)
1. How far the cleaning goes: status heads and a generated index only, or also moving the history of each point to a tail of its ADR?
2. Where superseded ADRs live: kept in place and marked, or in an archive folder?
3. When the ledger and an ADR disagree, the ledger wins?
4. The rule of thumb for what deserves an ADR: accept or change?
5. Who may clean the text of an ADR, and does she read each one?
6. The missing ADRs: write them first, or record today's state as a baseline and write them as topics come up?
7. Should the new checks fail the tests, or only warn at first?

## Not verified
The token counts (estimated from file size); the 14 ADRs still marked "proposed" against the code; how much shorter an ADR becomes after cleaning (a trial on two ADRs would tell).
