# Panel brief: help that stays open beside the screen (coordinator, 2026-11-21; the owner's order with decision D-0404)

You recommend; the owner decides. A study: build nothing, change nothing. Read-only in the repository; scratch only under `tmpAI/panel/help_beside/<viewpoint>_scratch/`. Never read `tmp.md`. No word limit: as long as needed to be clear, no padding. Plain short sentences; tables for comparisons.

## The owner's words
"Id go for C (hoover) - how novices can hoover --- it can also be written in the documentation ? I am afraid that too much explanation in the ui will be too much information - and Id rather the user be able to use the help --- a question can the help be open as popup so the user can both see the ui and help at the same time ? not having to open and close all the time (would be practical if user can have help stay open while it verifies and try to understand)."

## Her standing rules
- An option is judged on merit: correct, sound, useful to the user. "It reconsiders a decision" is INFORMATION on its own line, never a reason to reject an option or to rank it lower.
- Verify, never guess: label each statement RUN, READ (file:line) or REASONED.
- The tool informs; the user chooses. No half fixes. "Be aware of not over warning" (D-0149). No outside links: every asset is kept inside the app (ADR-071).

## Read first
1. `tmpAI/panel/help_beside/FACTS.md` (what the code does today; the scout's neutral list of six options).
2. `tmpAI/panel/help_beside/RUN_FACTS.md` (measured in a browser at 1100 x 800 and 1920 x 1080). The main results: the help window today is 500 px wide, dims and blurs the page, blocks every click behind it (a click outside closes it) and locks scrolling; its text is long (HOME about 3370 px high); the page loads Bootstrap 5.3.1 with its ready pieces for a side drawer (Offcanvas), a click-open small window (Popover) and a modal; no ready piece for dragging or resizing a window exists; a small text on pointing (tooltip) opens on hover and keyboard focus, closes when the pointer leaves it (a link inside cannot be clicked), opens on a tap on a touch screen and is 200 px wide; the documentation link works from the app's own server; the right panel is 170 px wide at a 1100 px window and 288 px at 1920 px in the Gallery, BLUEPRINT and Test Lab; in HOME it is closed in Exploration and holds the audit in Audit mode.
3. The decisions named in FACTS.md (read each ledger line in `.claude/knowledge/decision_ledger.md` before you rely on it): D-0404, D-0399, D-0375, D-0381 to D-0386, D-0149, D-0010.
A small read-only check is allowed where your proposal depends on a fact (give file:line).

## The question
How should help be given so that a user can read it WHILE looking at and using the screen, in all four user spaces (HOME, BLUEPRINT, Gallery, Test Lab), at a 1100 px window and at 1920 px, without filling the screen with text? Two kinds of help are in play and must fit together: (1) the short meaning of one term or control (her decision D-0404 for the Gallery filter terms: a small visible mark, hover or click, also in the documentation; it must work on a touch screen and for a novice who does not know to hover); (2) the longer help of a user space (today one long text per user space in a blocking window).

Compare these options (you may add one or combine):
1. Keep the blocking window.
2. A side drawer over the right edge that does not block the page (Bootstrap's ready piece).
3. The help as a panel in the right panel of the frame (in HOME that panel is the audit panel in Audit mode).
4. A floating window the user moves and resizes (new script).
5. The help or the documentation in a second browser window or tab that the user places beside the app.
6. A short meaning on a small mark, and the long text elsewhere (2, 3 or 5).

For each option say, from your viewpoint: what the user sees and does in each user space at 1100 px and at 1920 px; what it does to the space of the main panel; what exists and what is missing; what happens to the audit panel of HOME; touch screens and keyboard; whether the text can come from one source shared with the documentation (D-0399) and how the help knows WHERE the user is (which user space, which panel, which term); how it is tested; pitfalls. Then: how the short meaning (mark, hover, click) and the long help connect (does the small window offer "read more", and where does that open); what the mark looks like and where it sits so that a novice finds it without the screen filling with marks.
Recommend ONE option or combination and say why, on merit. Add one line per option: "Reconsiders a decision?" (the number, or no).

## Each viewpoint's own weight
- User who is not a developer (and new to data science): do I find the help; can I read and act at the same time; does it cover what I am looking at; too much or too little text; what the mark and the words should be; what frightens or annoys (a window that closes when I click the app; a text of nine screens).
- Architect: where help texts live and how they are kept in one source (the help files, the documentation, the generated meanings of D-0399); the frame and the panel registry (`app/modules/sidebar_registry.py`, `config/ui/sidebars/`); state (open or closed, per user space, per browser); independence of the user spaces; ADR-071; what each option amends.
- Developer: effort and risk as facts for ordering (her rule: build time is no argument against an option, delay is fine); what of today's code stays; the browser tests each option needs (a touch test; a 1100 px test); the smallest first step that leaves a working app; what must not be built before a decision.

## What to return
Start with a 6-line summary. Then a table | option | what the user gets | what it costs or risks | works at 1100 px | touch | one source of text | reconsiders a decision? |. Then your recommendation. End with "To decide first (ranked)" and "Not verified". If you have a shell, save your text as `tmpAI/panel/help_beside/<viewpoint>.md` with a redirect and return the path plus the summary and the table; if you cannot write, return the full text.
