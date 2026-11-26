# The ADR log and its history: facts for the panel (scout survey of dev, READ only, 2026-11-20; digest by the coordinator)

## Her words (2026-11-20)
"The problem is that ADR are not clean if they keep a lot of history - I would like a good solution where history could be separate to current ADRs that are in effect - have the coordinator check how it would be possible via its different agents - including architect and developper (and maybe user) : who want to know what stands now in a clear maner - and come to me with proposals with pros and cons". And: "for decisions without ADR we will need to maybe have some - and we might want to check logic of what has been added".

## Size and shape
- `.claude/knowledge/architecture_decisions.md`: 5,370 lines, 480 KB, 106 ADR headings (ADR-001 to ADR-106; no 017, no plain 029; ADR-072 reserved; ADR-040 sits after ADR-041). No fixed template (Status 106 lines, Context 97, Decision 96, Consequences 33). Longest: ADR-076 (322 lines), ADR-048 (216), ADR-097 (213).
- Status values in use: IMPLEMENTED 35, ACCEPTED 21, DECIDED 18, PROPOSED 14, ENFORCED 12, and single ones (FULLY IMPLEMENTED, MVP-1 IMPLEMENTED, PARTIALLY IMPLEMENTED, DEPRECATED, SUPERSEDED, RESERVED).
- No index and no summary of what is in effect. The head of the file says "Last Updated: 2026-04-23".

## How history is marked today
- 32 banners dated 2026-11-14 ("Partly stale", "Note", "Correction", a reading guide); 7 "To be amended by ADR-099 (not yet built)"; 6 whole-entry SUPERSEDED banners and one status line; about 8 "HISTORICAL in part" or point-level markers; 4 entries amended in place; 215 lines carry a date of October or November 2026.
- The rule file on legacy (`rules_legacy_management.md`) defines only four states (Active, Deprecated, Historical, Tombstone; "Unmarked = Active") and says historical context belongs in ADR entries; the log uses more kinds of markers than the rule defines.
- Not built or not verified: ADR-099 "ACCEPTED in principle, not built"; ADR-100, 101, 103, 105, 106 "NOT BUILT" in whole or in part; ADR-069, 073, 074, 075 "DECIDED, implementation pending"; 14 entries still "PROPOSED" (ADR-009, 012, 019, 020, 021, 025, 027, 028, 029b, 029c, 030, 038, 039, 046), status not checked against the code.
- One banner is itself out of date (ADR-052 says a validator rule is not built; it is).

## Who reads it and what points to it
- `CLAUDE.md` section 3.1: read at the start of every session ("never violate an ADR without authoring a superseding one"). Not every dispatched agent loads `CLAUDE.md`.
- About 1,400 references `ADR-n` outside the log: `.claude/design/` 750 in 89 files; `app/` 445 in 106 files; `docs/` 310 in 42 files (93 in the UML model); `libs/` 279 in 102 files; `.claude/rules/` 168 in 16 files; `.claude/workflows/` 52; `assets/scripts/` 27.
- Tools: `assets/scripts/audit_uml_model.py` resolves an `adr` tag of the UML model by the heading `## ADR-n` in THIS file and fails a tag whose ADR carries a HISTORICAL, REMOVED or SUPERSEDED marker; `scripts/audit_docs_sync.py` checks duplicate headings and passes silently if the file is missing; `check_doc_links.py` skips the log; no test opens it; no hook reads it.
- So: references are by NUMBER; moving an ADR to another file breaks the UML audit unless it is taught where to look; nothing else parses the file.

## Where one decision is written today (two traced examples)
- "Comparison requires the audit" (ledger D-0018): the ledger; ADR-099 point 11, ADR-105 point 8, a stale banner in ADR-052; three design pages; the code and its tests; two doc pages; the tasks file. About 15 places in 12 files. The rule file on flags does NOT state it.
- "Figure text only in the `labs` layer" (ledger D-0253): the ledger; NO ADR; the format spec; the machine spec; three knowledge files; about 12 code files and 12 test files. About 40 places in 30 files.

## The other records of decisions
- The ledger `.claude/knowledge/decision_ledger.md`: 354 decisions, one line each, ten fields, relation words (replaces, replaced in part by, refines, refined by, consistent with); nobody rewrites an existing line; a part "Asked, not decided".
- Of the ledger's lines on architecture topics (engine, recipe, audit, session, flags, export, format) about 133 of 157 name no ADR. Examples: D-0029, D-0058, D-0059, D-0060, D-0062, D-0067, D-0080, D-0086.
- The format spec keeps its own decision table (DEC01 ...); the design pages carry "Decided ..." notes; `changelog.md` records renames.
- Archives that exist, with their convention: `.claude/design/outdated/` (a README table: file, why outdated, replaced by; each file with an OUTDATED banner), `.claude/knowledge/archive/`, `.claude/tasks/archives/` (`tasks_archive_*.md`), `.claude/tasks/outdated/`, `.claude/plans/outdated/`.

## What a reader must reconcile today for ONE topic (the HOME header strip and what filters do)
ADR-085 (older, marked), ADR-086 (older, marked as a target), ADR-098 (partly current, "to be amended"), ADR-099 (the target, still "not built" although parts are built), the ledger lines of 2026-11-16 and 2026-11-20 (current; not referenced from the log), the rule file `ui_implementation_contract.md` (the old strip, UNMARKED), the design page `spaces/HOME.md` (the best summary, lacks the decision of 2026-11-20). Nine sources; two of them disagree on what plots use; the newest decisions are in none of the ADRs.
