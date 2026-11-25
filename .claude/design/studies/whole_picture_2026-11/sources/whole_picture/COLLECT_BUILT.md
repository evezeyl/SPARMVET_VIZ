# Collecting what is BUILT, for the whole-picture design (owner's order of 2026-11-22, ledger D-0507)

The owner ordered ONE whole-picture design of how the app should work, before more is built. Her reason: "right now the old things that exist are taken again because they are not build and this mixes with the decisions of what should happen." Your part: describe what the code on branch `dev` DOES today in the area given in your task, WITHOUT judging and without proposing, so that a design agent can compare it with the decisions.

Repository `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ` (branch `dev`). Change NO tracked file. Run nothing. Never read `tmp.md`; do not read `tmpAI/agent_channel.md`. Read the code itself (function bodies, not only names); a module docstring that lists "DECIDED / PROVISIONAL / NOT decided" points is valuable: copy those lists with their numbers.

## What to write for each behaviour (one entry per behaviour, grouped by the sub-areas of your task)
`what the app does, in one or two plain sentences, as a user or a caller would meet it | file:line (the function) | is it reachable in the running app (called from a handler: which), only from tests, or dead | what the code itself says about its status (a comment or docstring: DECIDED D-NNNN, PROVISIONAL, "for now", "not built", TODO; quote it) | the ledger numbers the code cites there`
Rules: "read" = you read it at that place; never write a behaviour you did not read. If the code has two ways of doing one thing (an old path and a new one), write BOTH and say which is called from where. Name every text shown to the user that states a limit ("for now", "not yet", "T3 only"). Name every place where a rule file (`.claude/rules/*.md`) describes this area as "DECIDED, not built" (file and section), so that the gap is on the list.

## Output
Write ONE file (the path is given in your task): a header (the files you read, with line counts), the entries by sub-area, then "Two ways of doing one thing found", then "Texts on screen that state a limit", then "Not read / could not tell". Your final message: the path, the number of entries, and the five most important "two ways" or "for now" findings in one line each. Plain short sentences. Be complete rather than short.
