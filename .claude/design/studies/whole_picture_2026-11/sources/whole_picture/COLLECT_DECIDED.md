# Collecting what is DECIDED, for the whole-picture design (owner's order of 2026-11-22)

The owner ordered ONE whole-picture design of how the app should work, before more is built. Her reason, in her words: "right now the old things that exist are taken again because they are not build and this mixes with the decisions of what should happen." Your part: read a range of the decision ledger and extract, WITHOUT interpreting, every line that touches the scope below, so that a design agent can read your file instead of the ledger.

Repository `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ` (branch `dev`), file `.claude/knowledge/decision_ledger.md`. The lines are very long: read them with Read (offset and limit), not with grep output. Change NO tracked file. Never read `tmp.md`; do not read `tmpAI/agent_channel.md`.

## Scope (keep a line if it touches any of these; drop the rest)
A. STAGES of a table: source / original data, a possible stage on the original data ("T0"), tier 1, tier 2, tier 3, T3 = T2 = T1 rules, derived tables, a join of joins, a result (a plot or a table), what is stored and built at opening, the engines per tier.
B. THE AUDIT: Exploration against Audit mode; where an audit step is written (the places, per tier, per table); the dialog "Create audit step" and its tick lines; the default ticks; the lineage walk (back, forward, back); what the walk reads and cannot follow; joins not yet followed; "remove from all the data"; the entity key and the join keys; the audit recipe (`audit_steps`, `audit_comment`, `info.audit_of`); which steps an audit may hold; removing a step; the reason gate; the comparison (original against audited); the audit log and the audit record; sessions.
C. VIEWING: the table viewed (Source, T1, T2, T3), the data preview and its sentences, exploration filters and when they are cleared, tables no plot reads, the lineage picker / lineage popup / node popup, the badge.
D. EXPORT and REPORT: what the bundle holds, the two parts of the reproducibility bundle, the data stored once, file names of results, the report structure, the audit trail in the report, keys and hashes, every table exported.
E. NAMES and FORMAT: `ui_label` and the names migration, keys of the recipe format that changed or were removed (`final_contract`, `output_fields`, `spec`, `plot_defaults` keys), the format number, action name prefixes, recipe-making rules (one name one meaning, declare the ID key), the recipe check and the load gate where they touch A to D.
Also keep: any line that says an earlier line is replaced, modified or reopened, when either line is in scope.

## What to write for each kept line (one entry per ledger line, in ledger order)
`D-NNNN | date | area letter(s) | status as the ledger says (DECIDED / other) and who took it | THE DECISION in the ledger's own words, shortened only by cutting, never reworded; her quoted words kept in quotation marks | what the line itself lists as NOT decided | what it replaces or modifies / what replaces it (numbers) | built? as the line says (built, not built, provisional), with any file it names`
Keep the brackets that mark "not her words" / "the review session's reading" as such: write them after the decision, prefixed "READING (not her words):". Do not merge two lines. Do not judge. If a line is unclear to you, copy it and write "unclear".

## Output
Write ONE file (the path is given in your task) with: a header (range read, number of lines read, number kept), the entries, then a short list "Lines that replace or contradict another line in scope (as the ledger states it)", then "Could not read / unclear". Your final message: the path, the counts, and at most ten lines naming the replacements you saw. Plain short sentences.
