# Proposal: `.claude/rules/ui_implementation_contract.md` section 8, the operators and controls by column type

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Built in FILTER-PICKERS-1 (branch `task/filter-pickers`).

**What Eve decided (2026-11-15; ledger line N06; channel block M84 point 9; `tasks.md` line of FILTER-PICKERS-1):** a date picker for a Date column; a two-choice control for a true/false column; greater and less are not offered on text; the control follows the type of the column; every type must be usable (so a time of day and a duration need a control).

**What is PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve):** the seven points in `tmpAI/filter_pickers_points_for_eve.md` of the worktree: (1) true/false offers equal and not equal only; (2) the operators of a date (list, every comparison, between) and of a time or duration (comparisons and between, no list); (3) three number boxes for a time of day; (4) a number with a choice of 8 units for a duration; (5) a date picker plus three boxes for a date and time; (6) the boxes start at the smallest and the largest value of the column; (7) a value finer than the unit of the column is refused. Where the text below describes one of these, it is provisional; the rest of the text follows the decision.

## Change 1 (FACT: the text describes the app as built; the per-type parts marked above are PROVISIONAL)

Line 281 today, paragraph "Operators by column type (ADR-104 points 4 and 7 ...)", from "Every other column (text, true/false, date, category) offers `in`, `not_in`, `eq`, `ne` with a list. Comparisons on text, date and true/false columns are not decided and not offered." to the end of that sentence.

Proposed (replace those two sentences):

`A date and a date and time column offer \`in\`, \`not_in\` (a list of the values present, exact) and every comparison (\`eq\`, \`ne\`, \`gt\`, \`ge\`, \`lt\`, \`le\`, \`between\`) with a date picker (a date and time: a date picker and three boxes for hour, minute and second); \`between\` has two controls and the four ends. A time of day offers the comparisons with three boxes (hour, minute, second, up to nine digits after the second); a duration offers the comparisons with a number and a unit (ns, us, ms, s, min, h, d, w); neither has a list. A true/false column offers \`eq\` and \`ne\` over two choices (true, false): \`in\` and \`not_in\` on one of two choices mean the same, and greater, less and between mean nothing. Text and category columns offer \`in\`, \`not_in\`, \`eq\`, \`ne\` with a list; greater and less on text is not offered (Eve, 2026-11-15, D9). A column of another type (binary, lists) offers nothing and says so. The boxes of a range start at the smallest and the largest value of the column, exact (nothing is cut). A date and time is read in the time zone of the column and a value finer than the column's unit is refused, never cut; the dialog says so under the control. A box left empty (time, duration) is a plain message, not a silent no-op.`

Also in the same paragraph, the sentence "a date is kept as year-month-day text ..." (line 283, "Value type rule") gets: `a time of day is kept as its text (hour:minute:second), a duration as number and unit (for example 90 min), a date and time as year-month-day hour:minute:second; the export types them from the dtype; the recipe step holds them as text in quotes (YAML reads 10:30:00 without quotes as a number).`

Why: FILTER-PICKERS-1. The behaviour is in `app/modules/t3_audit_engine.py` (`ops_for_column`, `value_widget_for`, `dialog_value`) and `libs/utils/src/utils/filter_values.py`.

## Change 2 (FACT, PROVISIONAL (L10))

After the paragraph above add: `PROVISIONAL (L10): a list of more than 1000 different values (\`in\`, \`not_in\`, \`eq\`, \`ne\`) is served on demand while typing (Shiny's server-side selectize); a search shows at most 1000 matches and a note under the box says how many values exist and "type more letters" when more match. Up to 1000 values the whole list is in the page.`

Why: 10000 values took 6.6 s and 30000 values 87 s with the whole list in the page; 100000 values now take 2.0 s (column selected to the list ready).

## Row for `RULE_FILE_CHANGES.md` (next free number at merge time)

| R1xx | ui_implementation_contract.md | 281 and 283 | "Every other column (text, true/false, date, category) offers in, not_in, eq, ne with a list. Comparisons on text, date and true/false columns are not decided and not offered." | per-type controls: date and date and time (list + picker), time and duration (boxes, no list), true/false (eq, ne over two choices), text (list, no greater or less); long lists on demand (PROVISIONAL L10) | FILTER-PICKERS-1, Eve 2026-11-15 (D9, M84 of the agent channel). | proposal file filter_pickers.proposal.md, changes 1 and 2 (fact) | proposed |

## Not settled

1. The hour, minute and second boxes are plain number boxes: Shiny for Python has no time input. A native time input needs a small custom input binding (a JavaScript file); not built, Eve's choice.
2. Whether a long list should be served on demand also under 1000 values (one path instead of two): today the whole list stays in the page up to 1000 values (PROVISIONAL, reversible).
