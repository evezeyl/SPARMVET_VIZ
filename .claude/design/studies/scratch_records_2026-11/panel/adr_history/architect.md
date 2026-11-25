# ADR history: architect and developer viewpoint (2026-11-20)

Recommendation only; Eve decides. Labels: READ (opened the file), RAN (ran a command or script), INFERRED (reasoned), EXTERNAL (from memory, not re-checked online). Scratch work: `tmpAI/panel/adr_history/architect/` (a lossless split dry run, a prototype index, ledger extracts). Nothing else was changed.

## 0. Flags first (information loss, broken references, hidden decisions)

1. **A split by whole ADR cleans little.** RAN: the 11 ADRs that are wholly superseded or historical hold about 34 KB of 499 KB (7%); all banners together are 17 KB (3%). The history is point-level: 32 ADRs carry a "partly stale / in part" marker (the 29 sections with a "Partly stale" banner hold about 166 KB), 19 mention "not built". Options O1 and O2 as stated move 7%; the rest stays mixed unless the bodies are edited too.
2. **The whole log cannot be read at session start today.** RAN: the Read tool refuses the file (487 KB, limit 256 KB). `CLAUDE.md` 3.1 "read at the start of every session" is not doable in one read. 499,120 bytes is about 125k tokens (INFERRED, 4 bytes per token). The ledger is 321,235 bytes, about 80k tokens (373 lines, about 860 bytes each).
3. **The UML audit reads history by accident.** READ `audit_uml_model.py:129-143`: an `adr` tag fails when the ADR section contains `**HISTORICAL`, `**REMOVED` or `**SUPERSEDED` anywhere. RAN: 11 sections match (ADR-013, 014, 021, 042, 049, 050, 063, 085, 086, 088, 098). ADR-099 passes only because its point-level markers are written `[HISTORICAL in part` (square bracket). So the check depends on how a banner is typed, not on what stands. It would also not catch a tag that points at a historical POINT of a live ADR.
4. **A move can pass silently.** READ `audit_docs_sync.py`: it passes without error when the log is missing (READ `audit_docs_sync.py:222-224`: `if not log.exists(): return []`). After a split, that check would report zero problems while checking nothing. It must be changed to fail when the folder or file is missing.
5. **References that a split must keep alive.** RAN: 188 tracked files name the path `architecture_decisions.md` (134 outside `.claude/logs`); 68 code files carry `# doc: .claude/knowledge/architecture_decisions.md...` links; 38 references use an anchor `architecture_decisions.md#adr-099` (an anchor would stop resolving after a split; `check_doc_links.py` skips this file and, INFERRED, does not test anchors, so nothing would catch it); 17 references cite a line number of the log (already drifting). By number: RAN, 3,524 mentions `ADR-n` in 452 tracked files outside the log and `.claude/logs` (FACTS says about 1,400; it counted fewer directories; either way a number-based scheme must keep every number resolving).
6. **Git history of the text is cut by a split.** `git log --follow` and blame do not follow a 106-way split. The big file stays in history; the index must name the last commit that held it (INFERRED).
7. **The ledger "status" never shows a replacement.** RAN: all 366 lines taken by Eve stay `DECIDED` forever; replacement lives only in the relation field: 4 lines fully replaced, 16 in part, 156 lines with relation `-`. Chains exist: D-0293 (tick removed) is replaced in part by D-0295 (tick stays), which is replaced in part by D-0298 (two ticks). A reader who stops at D-0293 gets the wrong answer. D-0001 ("Data to show" and "Plot to show") is replaced in practice by D-0179 and D-0350 but is not marked replaced (RAN). 8 DECIDED lines also carry a sentence "NOT DECIDED (asked)", an open part hidden inside a decided line.
8. **D-0350 allows updating ADR text only for sentences her decisions made out of date.** A wholesale rewrite of ADR bodies is more than that: it needs her agreement per ADR (D-0104 style). READ D-0104, D-0350.

## 1. What each record is for (and which wins)

| Record | For | Written by | Changes | Cannot do |
|---|---|---|---|---|
| Ledger (`decision_ledger.md`) | WHAT Eve decided, when, in her words | scribe, same day | never rewritten; a new line names what it replaces | say what stands without following relation chains; carry context, alternatives, consequences, mechanism |
| ADR | HOW the architecture is, why, what follows; the reference that code and tests cite by number | builder / architect | today: edited in place with banners | be read in full (flag 2); show built or not built reliably |
| Design page / spec / rule file | detail and narrative | various | edited | agree with the others (HOME: nine sources) |

- DECIDED (D-0105): "the existing ledger is used and updated (no second ledger)". So no option may create another decision list.
- Can one be derived from the other? Not the ledger from the ADRs (her words and the date are not in them). Not the ADRs from the ledger (consequences and mechanism are not in it). A **list** (index) of ADRs and a **list** of which ledger lines each ADR covers can be derived or checked.
- Source of truth when they disagree: INFERRED from `agent_principles.md` ("if this file and a source disagree, the source wins") and decision compliance: the ledger for what she decided, the ADR for how it is built. A disagreement means the ADR is wrong and is amended; it is never "resolved" by reading the ADR. CONFIRM with Eve (question Q3).
- The hook `coordinator_guard.py` accepts only ledger numbers (READ `decision_ledger.py` header). In practice briefs already cite the ledger; ADRs are read for context.

## 2. Options

Shared building blocks (used below):
- **Front matter per ADR**: `status` (in-effect | partly-superseded | superseded | proposed | reserved), `built` (yes | partly | no | n/a) with a task id when not yes, `supersedes`, `superseded_by`, `amends`, `amended_by`, `ledger` (the D-numbers it records), `topic`.
- **Partial supersession**: the superseded point stays in the same ADR file under a closing heading "History of this ADR", with one line left in place ("Point 3: replaced by ADR-099 point 11, 2026-11-14, D-0xxx; old text in History"). The number still resolves; the top of the file holds only what stands. A check: no `HISTORICAL`, `Partly stale` or `SUPERSEDED` wording above the History heading.
- Convention (EXTERNAL): Nygard's ADR note and `adr-tools` keep superseded records, mark them "Superseded by ADR-n" and never reuse numbers; `adr-tools` can generate a table of contents and has link kinds such as "Amends / Amended by" (whole record, not a point); MADR keeps files in one folder with a status field. Nobody deletes a superseded record. None of them has a standard for a point-level supersession.

### O1. One file per ADR in a folder, an index of ADRs in effect, superseded ones in an archive folder
- Pros: reading cost falls (RAN prototype: an index of title and status for all 106 ADRs is 11.9 KB, about 3k tokens; one ADR is at most 26 KB, median 2.6 KB); a place for front matter and checks; a number is a filename, so duplicates are impossible; follows the convention.
- Cons: alone it moves 7% (flag 1); an archive folder changes the path of a superseded ADR (every `doc:` link and number lookup must try two folders: avoidable by keeping superseded files in the same folder and letting the index separate them: O1a; a physical archive folder is O1b); partial supersession needs the building blocks above.
- Couples/breaks: UML audit (`adr_errors`), `audit_docs_sync`, 68 `doc:` links, 38 anchors, `INDEX.md`, `CLAUDE.md` 3.1. Touches ADR-099 (HOME and audit), `rules_legacy_management.md` (its section 3 says history lives in the ADR entry: that sentence changes), no ledger decision.
- Effort: medium. Risk: low for the move (lossless: RAN, 106 files, re-joined byte for byte identical), medium for the content work.

### O2. One log split into "in effect" and "history", each number in exactly one
- Pros: smallest tool change (two files, same heading form); fast.
- Cons: two files still too large to read (in effect would remain about 90% of the bytes); partly superseded ADRs have no clear home (flag 1); every change of state moves a text block between files (a diff that shows a deletion in one and an addition in the other; a reviewer cannot see what changed); no index; the UML audit and the duplicate check must read both and agree on which is authoritative.
- Breaks: anchors in both files, line citations. Effort low, risk medium, value low. I do not recommend it.

### O3. Keep the log, add a generated "what stands now" page; the log becomes the archive
- Pros: no migration, nothing breaks; fastest to the reader; can start tomorrow.
- Cons: the sentence per topic cannot be generated (an agent or a person writes it): it is a sixth place that says what stands (HOME already has nine; `spaces/HOME.md` is the best summary and lacks the 2026-11-20 decision: it drifted); the log stays unclean, so an agent that opens ADR-099 or ADR-097 still meets contradicting text; "the log becomes the archive" leaves tool and reference rules unchanged and unclear (which one does a number mean?).
- Staleness check I would add: every sentence cites D- and ADR numbers; a check fails when a cited D-number is replaced (relation field) or when a DECIDED ledger line of that area, newer than the page, is cited nowhere on it.
- Effort low-medium to start, risk of drift high over time. Fits the goal only as a bridge.

### O4. The ledger is the only record; ADRs only for architecture, each pointing to ledger lines
- Pros: one record of what she decided (consistent with D-0105); ADRs shrink to context, decision, consequences.
- Cons: the ledger is bigger than the log (80k tokens) and is NOT a "what stands" view (flag 7: status never changes; only 20 of 373 lines carry a replace relation); to make it one, the relation field would have to be complete and a new field "stands / replaced" would have to be written by a scribe: the file's rule is "nobody rewrites a line" (a new line names what it replaces: possible, but then a replaced line is still listed); ADRs lose the reasons that today are only there. It does not replace the need to clean ADRs. 41 of 373 ledger lines name an ADR (RAN): the link would have to be built backwards for the rest.
- Reconsiders: D-0105 is not reconsidered; the ADR role in `CLAUDE.md` 3.1 and 168 rule references are. Effort high, risk high, value unclear. Not recommended as an option by itself; one part of it is kept in O5 (the `ledger:` pointer).

### O5. (mine) O1a plus point-level history tail, front matter, generated index, a coverage check against the ledger
In steps (section 4). Same files and numbers; superseded ADRs stay in place with status; the index (generated) shows in-effect, partly superseded, proposed, superseded; per ADR `built` and open tasks; per ADR the ledger lines it records; a list of ledger lines on architecture that no ADR records.
- Pros: meets her sentence (current ADRs read clean; history in the same file under History, or the index separates it); reading cost: the index at session start (about 3k tokens now, about 6k when each ADR has one summary line) and open one ADR by number; one source for state (the front matter); every part checkable; same numbers.
- Cons: the content work per ADR (edit 32 partly-superseded ADRs, check 14 PROPOSED against code) is judgment and needs her per-ADR agreement beyond D-0350; front-matter fields are one more thing a scribe updates; the index needs a summary line per ADR (106 sentences to write once).
- Couples/breaks: as O1, plus a new script and new rule text. Reconsiders: the "history lives in the ADR entry" sentence of `rules_legacy_management.md` (kept, in a tail), the unmarked-equals-active rule (ADRs get an explicit status), `CLAUDE.md` 3.1 (read the index, not the log). No Eve decision.
- Effort: medium-high, spread over steps. Risk: low per step.

### Comparison

| | Reader: what stands | Agent at session start | Numbers resolve | Tools to change | Partly superseded | Decided, not built | Stays true by |
|---|---|---|---|---|---|---|---|
| O1 | index | index 3k tokens | yes if same folder | UML audit, docs_sync | needs tail rule | needs field | index check |
| O2 | two files | still 100k+ | yes, two lookups | both audits | unclear | status text | none new |
| O3 | page | page + log | yes | none | log unchanged | page sentence | citation check |
| O4 | ledger lines | 80k tokens | numbers become ledger | hook, guard, rules | n/a | n/a | relation chains |
| O5 | index + clean ADR | index 3k to 6k | yes | UML audit, docs_sync, new check | History tail | `built` + task | checks below |

## 3. How the state stays true (checks I propose; a failing check is the signal)

Who updates: the builder or scribe in the same merge that changes behaviour (`decision_compliance.md` section on checkpoint 4 already lists "UML and ADR sync").
1. `status` and `built` are required and from a closed list; an ADR with `built: no` or `partly` names a task id that exists and is open in `tasks.md`; a task closed while the ADR says `no` fails (it catches the ADR-099 "Not built" versus "BUILT in part" contradiction, RAN: both texts are in the log today; and the stale ADR-052 banner).
2. Every `superseded_by` and `amended_by` target exists and points back; no wording of history above the History heading.
3. Every `ledger:` number exists, is DECIDED and not fully replaced by a line newer than the ADR's `reviewed:` date; if it is replaced, the check says which ADR to amend (limit, stated honestly: it only sees replacements that a scribe wrote in the relation field; D-0001 shows that is not always done).
4. Coverage: every DECIDED ledger line in an architecture area is in some ADR's `ledger:` list or in an exemption list `adr_exempt.md` (D-number and reason); today's uncovered lines go in a baseline file so the check fails only on new lines or on a baseline line that became covered. (The baseline is what makes her second sentence checkable.)
5. UML audit reads `status` front matter instead of the text regex; a tag to an ADR whose status is `superseded` fails; a tag to a point named in History fails.
6. `audit_docs_sync`: the ADR folder missing is an error, not silence.
What these would NOT catch: a decision that the ledger never received; an ADR sentence that is wrong but unmarked; a replacement the scribe did not write; a ledger "area" typed differently (about 60 free-text areas, RAN), so "architecture area" needs a mapping file or a field.

## 4. Migration in steps (each step leaves a working state)

- **S0 (no break, no edit of the log)**: a script generates `adr_index.md` from the current log (title, status line, markers: prototype RAN, 11.9 KB). Add to the index header "state of reading". Cost: one script, one check. Reference rewrite: none.
- **S1 (decisions, no code)**: Eve fixes the status words, the `built` field and the History rule; `rules_legacy_management.md` gets the ADR-level states (today it has four states and the log uses more; READ). Needs her yes.
- **S2 (mechanical, one commit)**: split into 106 files (dry run RAN: lossless; two odd numbers ADR-029b and ADR-029c; ADR-040 after 041; ADR-072 reserved), front matter filled from the current status line, `architecture_decisions.md` kept as the generated index (so 188 path citations and 68 `doc:` links stay valid), 38 anchors rewritten to `adr/ADR-nnn.md` by one `sed`, `audit_uml_model.py` `adr_errors` and `audit_docs_sync.py` changed in the same commit (no shim, no two-place lookup), 5 docs updated. Files: 106 new plus about 10 changed. No ADR number changes. Test: the dry-run round trip; the two audits run before and after with the same results.
- **S3 (content, per ADR, with her yes)**: move point-level history to the tail, starting with the most read: ADR-099, 097, 098, 085, 086, 105, 100, then the 32 with markers; verify the 14 PROPOSED ones against the code.
- **S4**: coverage baseline and the checks of section 3.
Order can be stopped after S0 or S2 with a working repository.

## 5. Which decisions deserve an ADR (a rule of thumb for Eve to accept or change)

An ADR if the decision does at least one of: (a) draws a boundary or a contract between modules, libraries or layers; (b) fixes an on-disk or exported format, a key, or a security rule; (c) sets an invariant that code and tests must keep (reproducibility, no silent change, parity); (d) was chosen between real alternatives whose reasons must be kept; (e) is hard or expensive to reverse.
No ADR (stays in the ledger and, where it belongs, the spec, a rule file or the design page): wording of a message or button, where a control sits, one key name inside an already decided format (format spec), a provisional value (1,000,000 rows), a clean-up or fix of data files, process and way of working, demo dates and tags, test tooling, "keep as built". These are still found by number in the ledger.
Measure RAN: of 275 ledger lines in architecture-like areas (I excluded process, agents, records, docs, rule files, demo, test data, themes), 36 name an ADR, so 239 do not (FACTS counts 133 of 157 with a narrower area list; same picture).

### First grouping of missing ones (titles only; not checked against each ADR; several are amendments of an existing ADR, not new numbers)
1. Recipe format 1 amended before release: engines declared per plot and per tier, open engine list, cache keys: D-0219, D-0236 to D-0240, D-0247 to D-0250 (amends ADR-100, 089, 101).
2. Registry names and Polars/plotnine exactness (polars_, modif_, step_, plotnine_ prefixes, 30 objects, name pairs, the wide split): D-0058 to D-0060, D-0091, D-0092, D-0210 to D-0214, D-0218, D-0254, D-0264, D-0265 (check against ADR-100 DEC31-42 and ADR-106).
3. Formula safety: allowed and refused expressions, one check, one place for crashes: D-0064, D-0229 to D-0232, D-0257, D-0259 to D-0261, D-0267, D-0273, D-0275.
4. What a recipe may pass; silent defaults refused; seeds required: D-0052, D-0056, D-0276 to D-0280, D-0282.
5. Join rules and key types, self-join, join of joins: D-0065, D-0066, D-0078, D-0183, D-0344 (amends ADR-102).
6. Sample id, data kinds, lookup tables: D-0067, D-0222 to D-0225.
7. Figure text in `labs`, label field, plot entry in its own file, gallery bundle shape: D-0251 to D-0253, D-0360, D-0171, D-0077, D-0062.
8. Opening of a recipe: tables stored by key, plots drawn once, progress line, large data, screen cleared: D-0184, D-0185, D-0326, D-0334 to D-0336, D-0343, D-0363, D-0372.
9. HOME views: Exploration and Audit mode, data choice, filters cleared, Reshuffle, start state: D-0019, D-0021, D-0061, D-0175 to D-0180, D-0196, D-0310, D-0311, D-0327, D-0341, D-0361, D-0365 (amends ADR-098, 099, 105; replaces parts of ADR-085, 086).
10. The audit recipe: a copy, its file form, `audit_of`, `audit_comment`, folder, hash and tampering, format 1: D-0040, D-0102, D-0143, D-0145, D-0319 to D-0321, D-0328, D-0329, D-0331 to D-0333, D-0339, D-0340, D-0354.
11. Audit steps and the lineage walk: step kinds, scope by ticks, the places, renames, key drop by place, one undo: D-0022, D-0027, D-0028, D-0083, D-0093, D-0096, D-0194 to D-0203, D-0302, D-0313 to D-0316, D-0322, D-0325, D-0337, D-0346, D-0347, D-0351 to D-0353, D-0355 to D-0359, D-0371.
12. Audit signals: warn, never block; nothing vanishes silently: D-0015, D-0095, D-0149, D-0168, D-0201, D-0203 (maybe an amendment of ADR-104).
13. HOME export: one panel, fields kept in memory per session, two modes, bundle texts, audit export: D-0187 to D-0193, D-0288 to D-0301, D-0324, D-0330, D-0345 (amends ADR-097, with the chain D-0293, D-0295, D-0298).
14. Sessions: what is refused on restore, size limit: D-0186, D-0281, D-0283, D-0312, D-0317, D-0362.
15. Where a recipe fails and when it is checked: D-0079, D-0176, D-0184, D-0338, D-0342 (amends ADR-094).
16. Import and imported data: D-0030, D-0045, D-0207, D-0209.
17. Blueprint order and tier 3 authoring: D-0063, D-0305 to D-0309, D-0348 (amends ADR-082, 083).
18. One interpreter for the app and its child processes: D-0263 (small; a rule file may be enough).
About 18 candidates, about 10 of them amendments. First check each against ADR-094, 097 to 106 so as not to write one twice. Logic check of what was added (her second request): reading one candidate group at a time, list contradictions (like D-0293 against D-0298, or D-0001 against D-0179), open parts hidden in decided lines (8), and decisions that say "ADR text not changed without her yes" (D-0293, D-0298 and others): these are exactly the ADR sentences that now need updating under D-0350.

## 6. Recommendation

O5, in steps; O3 only as a bridge if she wants a readable page before S2 (a generated one, not a written one). Reason: it is the only option that changes what an agent reads (index plus one file), keeps every number and path alive, gives each fact one home (state in front matter, history in a tail of the same file, her words in the ledger), and has checks that fail when the state is stale. O2 gains too little; O4 duplicates the problem in a bigger file.

**Smallest useful first step**: S0. One generated index of the 106 ADRs (title, status, partly-superseded, not built), plus the fix of `audit_docs_sync` so a missing log is an error. No ADR text changes, nothing breaks, and she can see on one page which ADRs are in effect, which are partly historical, and which are decided but not built.

## 7. Questions for Eve (short)

1. How far should the cleaning go?
   - (a) Only the index; the ADRs stay as written. Pro: no risk. Con: the history stays in the bodies.
   - (b) Index plus a History tail per ADR (the superseded points moved, not deleted). Pro: current text reads clean, nothing lost. Con: a judgment per ADR; she must agree.
   - (c) Also shorten the long ADRs (076, 099, 091, 079). Pro: less to read. Con: more editing and more risk.
2. Where do superseded ADRs live?
   - (a) Same folder, marked in the index. Pro: every number and link keeps working. Con: the folder holds both.
   - (b) An archive folder. Pro: physical separation. Con: every tool and link must look in two places.
3. When an ADR and a ledger line disagree, is the ledger right? Pro of yes: it is her words and it is already the rule for briefs. Con: an ADR can then be wrong for a while until amended.
4. Which decisions get an ADR? Accept, change or add to the rule of thumb in section 5.
5. May agents edit ADR text for the sentences her decisions made out of date (D-0350), or does she want to see each ADR before it is changed?
6. For ledger lines with no ADR: baseline (list the old ones, fail only on new ones) or write the missing ADRs first? Baseline: fast, shows the size. Writing first: complete, slow.
7. Do the generated index and the checks go into the standard controls so a stale ADR fails a merge, or only warn? Fail: it stays true. Warn: less friction.

## 8. What I could not verify

- Token numbers are bytes divided by 4 (not a tokenizer).
- The 14 PROPOSED statuses against the code; which "Partly stale" banners are still true (only ADR-099 and ADR-052 examples checked).
- Whether `check_doc_links.py` checks anchors (INFERRED not; I did not run it); how many of the 1,400 or 3,524 references use a point, not just a number.
- `adr-tools` and MADR behaviour is from memory (EXTERNAL), not re-checked online.
- The grouping in section 5 was made from the first 110 characters of each ledger line plus the lines I read in full; the full text may move some numbers between groups.
- How much the "in effect" text would shrink after S3: not measurable without doing the edit. A trial on ADR-099 and ADR-097 would give the figure.
- The ledger area strings are free text (about 60 distinct values), so "architecture area" in check 4 needs a defined list.
