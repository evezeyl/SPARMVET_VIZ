# FILTER-PICKERS-1: seven choices that are the agent's, not yours (waiting for Eve)

What you decided (2026-11-15, ledger N06, M84 point 9): a date picker; a two-choice control for true/false; no greater/less on text; the control follows the type; every type usable. Everything below is the agent's choice, marked "PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve)" in the code, in `tasks.md` and in `filter_pickers.proposal.md`. Each point: what the user sees, options, the default built.

## 1. True/false: which operators
User sees: two choices (true, false) and the operators "=" and "not equal".
Options: (a) equal and not equal only; (b) also "one of" / "none of" (they mean the same on two values; one extra use: "remove the rows with no value" with both values ticked); (c) a third choice "no value" in the control.
Default built: (a).

## 2. Operators for dates, times and durations
User sees, Date and Date and time: "one of", "none of" (a list of the values present), =, not equal, >, >=, <, <=, between. Time of day and duration: =, not equal, >, >=, <, <=, between, no list.
Options: (a) as built; (b) dates and date and times without the list (pickers only); (c) time and duration also with a list of the values present.
Default built: (a).

## 3. A time of day
User sees: three number boxes: hour, minute, second (the second takes decimals, up to nine digits).
Options: (a) three number boxes (Shiny for Python has no time input); (b) one native time input through a small custom input binding (a JavaScript file in the app); (c) one text box "hh:mm:ss" with a check.
Default built: (a).

## 4. A duration
User sees: a number box and a unit list: ns, us, ms, s, min, h, d, w (for example 90 min).
Options: (a) a number and 8 units; (b) fewer units (s, min, h, d); (c) one text box "1h30m".
Default built: (a). The boxes start with the largest unit that holds the value exactly (5400 s shows as 90 min).

## 5. A date and time
User sees: a date picker and the three boxes of a time under it; the dialog says the time is read in the time zone of the column.
Options: (a) as built; (b) one text box "yyyy-mm-dd hh:mm:ss"; (c) a date picker and a time box with a time zone choice (not needed today: the column has one zone).
Default built: (a). A time that does not exist (summer time) or exists twice (winter time) in the zone is refused with a message; for the repeated hour the dialog cannot choose between the two and says so (the list "one of" holds each time with its offset).

## 6. The starting values of the boxes
User sees: for a comparison the box starts at the smallest value of the column; for between the two boxes start at the smallest and the largest value (exact, no digit cut).
Options: (a) as built; (b) empty boxes (the user must fill them; a missing value is refused); (c) today / zero.
Default built: (a). With (b) nothing is ever filled in for the user.

## 7. A value finer than the column
User sees: a message: the value is finer than the unit of the column (for example 1.5 microseconds on a microsecond column); the row is not added; "Suggestion: write at most the digits of the unit".
Options: (a) refuse (built); (b) round to the unit and say so; (c) cut silently (not recommended: changes a result silently).
Default built: (a).

## 8. The date box: what is typed, what is picked
User sees: a box with a calendar. The date staged is exactly a whole date typed as year-month-day (2023-02-28; 2023-2-8 is accepted and shown in full in the staged line) or a day picked in the calendar. Anything else (2023-0, abc, 20220305, 03/05/2022, 2023-02-30) is refused with "The text ... is not a date written as year-month-day, so no filter is added. Suggestion: write the date as year-month-day, for example 2023-02-28, or pick it in the calendar"; the box keeps the text so it can be corrected. (Cause: the calendar widget repairs free text: today for a partial text, 2023-03-02 for 2023-02-30; and Enter in an empty box chose today.)
Keyboard-only user: can type the date and Tab; the arrow keys and Enter of the calendar are off (they were what chose a day for the user), so the calendar itself needs a mouse.
Options: (a) as built (calendar for the mouse, strict typed text); (b) a plain text box with the strict rule, the calendar only as a helper button (no widget repairs at all; arrow keys can be added back); (c) refuse also 2023-2-8 (only 2023-02-08 accepted).
Default built: (a).

## Also provisional (smaller)
- The on-demand value list starts above 1000 values; below, the whole list stays in the page (L10, own commit). Option: on demand at every size (one path; the browser tests would wait for the list).
- A date picker's Enter key does not choose a day (the widget filled in today for an empty box; closed 2026-11-16: an emptied date box now means "no date chosen").
