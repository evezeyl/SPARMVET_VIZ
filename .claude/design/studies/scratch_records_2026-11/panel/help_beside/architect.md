# Architect viewpoint: help that stays open beside the screen (2026-11-21)

Labels: RUN = measured by me (scratch: tmpAI/panel/help_beside/architect_scratch/run.py, out.json, screenshots oc_*.png; the app was started on port 8767 and stopped); RUN_FACTS = the scout's measures; READ = file:line; REASONED = deduced. "Reconsiders" lines are information only.

## Summary (6 lines)
1. Recommended: option 6 with the long text in option 2. A small "i" mark opens a click popover with the short meaning and a "Read more" link; "Read more" and the "?" button open one side drawer that does not block the page, and its text follows the user space.
2. New facts (RUN): Shiny 1.6.0 DOES have `ui.popover` (the scout found none); it opens on click and on tap, stays open when the pointer leaves, and a link inside it is clickable (253 px wide). The tooltip could not do this (RUN_FACTS).
3. New fact (RUN): an Offcanvas drawer with backdrop false is 420 px wide, leaves no backdrop, leaves the nav usable, and STAYS open when the user space changes. So its content must be a reactive output of the current user space, not a one-shot like today's modal (which kept "Home - Help" over the Gallery, RUN_FACTS 14).
4. Hard limit: at 1100 px nothing sits "beside" without covering: main is 740 px; a 420 px drawer covers 250 px of it plus the right panel (screenshot oc_1100_mouse_explore.png). At 1920 px it covers the right panel (288) and 132 px of main.
5. In HOME Audit mode the drawer covers the audit panel at the right edge: the owner's wish (help open while she verifies) is then not met unless the drawer is offset to the left of the right panel. This is the first thing she must choose.
6. One source: the four help files stay the source of the long text; the generated meanings (D-0399) are the source of the marks; the documentation includes both; one headless test ties every mark to an existing section.

## Table
| option | what the user gets | what it costs or risks | works at 1100 px | touch | one source of text | reconsiders a decision? |
|---|---|---|---|---|---|---|
| 1. Keep the modal | text over a dimmed, blurred, blocked page; closes on an outside click | does not answer her question; making it non-modal needs extra CSS and still locks body scroll (RUN_FACTS 22-23): a shim | yes, but blocks | works | yes (today's files) | no |
| 2. Drawer, no block | text at the right edge; page usable; stays open across user spaces (RUN) | covers right panel and part of main; hides the HOME audit panel unless offset; new content output, 1 anchor script | covers 250 of 740 px of main | works (tap; not run on the drawer) | yes, same files as the modal | no (amends the wording "modal" in ADR-096 context and the task HELP-INLINE-1) |
| 3. Help in the right panel | pushes nothing, resizable by the existing drag | panel is 170 px at 1100 (about 16 characters a line, RUN_FACTS estimate), max about 360 by drag; shares the space with audit (HOME), form and chat (BLUEPRINT); a help panel type is not a gated feature | poor | works | yes | D-0383 (panel empty in Exploration), D-0385 (closes on leaving Audit) in HOME |
| 4. Floating window | user places it where it hurts least | all new script: drag, resize, keep in view, focus, touch drag; no test base | best placement | fiddly | yes | no |
| 5. Second window or tab | full-size text, second monitor possible, no overlap | the app does not know where the user is; needs the book built (gate `docs/_site`, `home_theater:77`) or a new app-served page; on one 1100 px screen the OS split gives the app about 550 px | only on two screens | tabs on tablets | yes if the book includes the files | ADR-096 point 1 (no deep-linked pages) if it deep-links |
| 6. Mark + long text elsewhere (with 2) | short meaning where the word is; long text on demand | two surfaces to keep consistent; marks inside accordion headers are nested buttons | yes | click works (RUN) | yes, if generated | no |

## Fit with ADRs and rules
- ADR-071 (no outside assets): Bootstrap 5.3.1 Offcanvas, Popover and Modal are defined in the page (RUN_FACTS 2) and come from the Shiny package, not from a CDN. DECIDED rule holds for options 2 and 6. Option 4 adds a script in `app/src/www/` (not vendor): kept in the app, ADR-071 holds.
- Clear Lines: help is a frame feature (like the "?" and book buttons, `home_theater:1849-1874`), not a panel. Option 3 forces it into `PANEL_REGISTRY` (`sidebar_registry.py`), whose entries are gated feature flags: a mismatch (REASONED). MINE.
- Two stores that can disagree: today `app/src/help/*.md` and `docs/user_guide/*.qmd` are separate hand-written texts (READ: no include of `src/help` in `docs/`). Existing includes of files outside `docs/` exist (`docs/appendix/FAQ.qmd:94`), so a Quarto include of the help files is the same pattern (REASONED, not run). D-0399 covers only the Gallery terms; the long text has no decided source. CONFIRM.
- ADR-096 point 2: the quick help must work when the book is not built. So the app copy is the master and the book includes it, not the reverse. DECIDED.
- Dead code: `app/modules/help_registry.py` is called by nothing (READ). If the help surface is rebuilt, remove it with a tombstone (no shims). MINE.
- ADR-090 / ADR-099: help state (open, closed) is not a result and must stay out of the session record and the export. MINE; guard by a test.

## What exists and what is missing (option 2 + 6)
- Exists: help files per user space; `ui.popover` and Offcanvas; the user space is read from `sidebar_nav` (`home_theater:1890`); `frame_widths.py` is the one place for panel numbers (D-0386).
- Missing: heading ids (`ui.markdown` makes none, RUN); a pure module that lists the sections of each help file and the topic keys; the drawer container in `ui.py`; one small script that opens the drawer and scrolls to a section; the generator of D-0399 (not built); the help drawer width as a named value in `frame_widths.py`.
- Open/close is client-only (a button with `data-bs-toggle`); the server renders only the text of the current user space. No server state, no race with the anchor: the whole text of the space is rendered and the script scrolls to the id.

## How the help knows where
- User space: from `sidebar_nav` (READ). Panel and term: each mark carries a topic key `<space>/<section id>`. Mark and section are tied by the headless test, so a renamed heading fails a test and not a user.

## Short meaning and long help
- Mark: a circled "i" (the app already uses `bi-question-circle` for "?"; keep them apart: "?" = help for this screen, "i" = the meaning of this word). One mark per group heading or non-obvious control, never per value; the popover of a group lists its values (generated). Not on self-explanatory controls (D-0149).
- Click is the one way (D-0404 allows hover or click). Hover would add a second way and fails for touch and for a novice who does not know to hover.
- Pitfall: Gallery group titles are accordion buttons (left panel 190 px at 1100, `Family (Purpose)` already fills it, screenshot). A mark inside the title is a button inside a button (REASONED). Put the mark in the first line of the opened group body, or beside the accordion, then test it.
- Popover ends with "Read more": opens the drawer at that section. It does not open a new tab.

## Tests
- Headless: generated meanings equal the spec (D-0399); every topic key resolves; section ids unique per file; each of the four user spaces has a file; the docs include path exists; help state not in the session record.
- Browser at 1100 and 1920: popover click and tap; link inside; drawer leaves nav usable; text changes with the user space while open; Escape; no overlap fault with the audit panel; a mark in an accordion title does not toggle it.
- Not caught by tests or audit: overlap that hides something the user needs; hand-written help that no longer matches behaviour (`test_home_help_text.py` guards only HOME and only a few words); a deployment where the book was not built (docs copy absent).

## Recommendation
Option 6 with the long text in option 2. On merit: it is the only option that keeps the page usable, follows the user space, needs no new window script, uses what is already in the page, and gives one text for app and documentation. Option 3 fails at 1100 px and in Audit. Option 4 is a later upgrade of the same drawer, not a second way. Option 5 stays as the existing book link.

## To decide first (ranked)
1. In HOME Audit mode: may the drawer cover the audit panel, or must it sit to the left of the right panel (then it covers the plot: at 1100 px main would fall to about 320 px, the width she called horrible in D-0375)? Tell her both costs.
2. May the help drawer be an overlay that covers part of the screen at 1100 px? It cannot be side by side at that size.
3. Which text is the master of the long help: the app files (recommended by ADR-096 point 2) with the book including them.
4. Mark: click only, circled "i", where it sits inside the Gallery accordion.
5. Does the drawer start closed on each load (recommended) or remember its state in the browser like D-0382?

## Not verified
- Offcanvas Escape and focus behaviour; keyboard open of the popover; touch on the drawer (only the popover was tapped).
- Audit-mode overlap in numbers (my click on the Audit control failed; the right panel width in Audit is still unmeasured).
- A Quarto include of a help markdown file (reasoned from the YAML includes only).
- Whether a click popover works inside an accordion body and inside a left panel that scrolls.
- ADR-096 text that names "modal" is in its Context; I read it, I did not search every task file that cites HELP-INLINE-1.
