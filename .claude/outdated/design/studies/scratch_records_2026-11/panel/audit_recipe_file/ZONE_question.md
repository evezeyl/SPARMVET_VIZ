# How the audit recipe file tells original steps from audit steps: the question for the panel (coordinator, 2026-11-20)

## Her words (2026-11-20; NOT decided; a study, no build)
"I need more information - and if necessary need to ask the architect and data scientist --- We need a way to keep track of the added audit step - so its easy for the app to keep track of what is original and cant be modified in the audit recipe vs what can - could a solution be adding a field could be in the audit_comment with start and stop? so the audit step adding possibilities would be added after each T1, T2, T3 (unsure yet how to do with the plot recipe but as this will be built later we can adjust later for that) then you have audit_start, audit_stop and that allows the app to know what is the original vs the modified steps? Have the coordinator investigate possible solutions - but I think it could work".

## Decided, do not reopen (ledger; full list in `FACTS.md` beside this page)
D-0102, D-0040: the audit recipe is a copy of the original with the audit steps; copy minus audit steps = original, else block. D-0146: audit steps are added at the END of each T1, T2 or T3 list. D-0320: the copy keeps the author's comments. D-0321: `audit_<8 hex>_<k>`, k = order of creation. D-0322: an audit step is only a filter, a drop or a removal by key. D-0328: a key under `info:` names the original. D-0329: the reason is the step key `audit_comment`. D-0314: one undo control, "Remove step". D-0324: the audit recipe is the recipe of an audit export.

## Today (slice A, in memory only; READ)
- A tier is written `tier1: {steps: [ ... ]}` (also `tier2`, and `tier3` at a plot). An audit step is an ordinary item of that same list, at its end, told apart ONLY by its `id` of the audit form. `libs/utils/src/utils/audit_copy.py`: `is_marked` (68-70), `add_step` (188-211), `strip_marked`, `integrity_errors` (297-318: the original holds no marked step; no id twice; a marked step is at the END of its list; the copy without marked steps equals the original).
- Weak points known: (1) a hand edit that removes or changes the `id` of an audit step turns it into an "original" step; the equality check then reports a difference, but only when the original is at hand; (2) a hand edit of an ORIGINAL step is found only by the same comparison with the original; (3) when the file is written by editing text, a step list that sits in an included file shared by two tables receives the step for both tables, and the equality check does not notice (it strips every marked step); (4) a list written on one line (`steps: []`, `steps: [{...}]`) needs its own text handling; (5) the PyYAML loader drops `#` lines, so a marker written as a `#` comment is invisible to the app.
- The checker refuses any unknown key on a step and in a tier body; a new key is a format change. `id` on a step is legal only in the audit profile.
- The keys of the stored tables take the audit steps as their own parts (a1, a2, a3), today by picking the marked steps out of the list.

## Candidate forms
- **F1. As today:** audit steps in the same list, marked by their id.
- **F2. Her zone, as two marker items in the list:** `- audit_start` ... audit steps ... `- audit_stop` (items that are not steps; or a key on the first and last audit step, e.g. inside `audit_comment`).
- **F3. Her zone, as `#` comment lines** around the audit steps (`# audit_start` / `# audit_stop`).
- **F4. Her zone, as structure: a second list beside the original one**, in the same tier: `tier1: {steps: [original, untouched], audit_steps: [audit only]}`. The "start" and "stop" are the brackets of that list. The engine runs `steps` then `audit_steps` (the decided order: at the end).
- **F5. The audit steps in their own file** beside an untouched copy of the original's files (the original files byte for byte, plus one file listing the audit steps by place).
- Others the panel finds.

## What each must be judged on
1. Can the app tell, from the file ALONE (no original at hand, e.g. a bundle on another machine), which steps are original and which are audit? After a hand edit?
2. What can a hand edit do silently (a step moved across the marker, a lost marker, two zones, an id removed, an original step changed) and what can the checker refuse?
3. Writing with the author's comments kept: by text edit of copied files (what must be inserted where, for an inline list, a missing tier, an included file shared by two tables) and with a comment-keeping library.
4. "Copy minus audit steps = original": how it is computed and how strong it is.
5. Removing one step (the one undo control); the order of creation.
6. The keys of the stored tables (a1, a2, a3) and the engine: what changes.
7. The recipe format: which new keys, where, and what the checker's audit profile must accept and refuse; ordinary recipes must be untouched.
8. A plot's tier 3 (built later): does the form carry over?
9. What a person reads when opening the file.
