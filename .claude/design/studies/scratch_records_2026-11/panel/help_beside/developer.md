# Developer viewpoint: help that stays open beside the screen (2026-11-21)

Labels: RUN (I ran it), READ (file:line), REASONED (not run). Nothing in the repository was changed.

## Summary (6 lines)
1. Recommended: option 6 built as two parts. Part A: a small "i" mark that opens a click-open small window (Shiny `ui.popover`) with the short meaning and a "Read more" link. Part B: a non-blocking side drawer (option 2) for the long text of the user space. Option 5 (documentation in a second tab) stays as the "full documentation" link that exists today.
2. New fact, RUN: the installed Shiny 1.6.0 HAS `ui.popover` (signature with trigger, title, placement, options). FACTS.md said it is missing; that is wrong. The popover stays open on click and can hold a link, which a tooltip cannot (RUN_FACTS section 3).
3. The tooltip cannot carry "Read more": it closes when the pointer leaves, so a link inside cannot be clicked (RUN_FACTS 3). So the mark must be a popover, not a tooltip.
4. The drawer (option 2) is a real Bootstrap piece, but nothing in the app uses it yet (grep: no `offcanvas` in `app/`, READ). Whether it leaves the page usable with backdrop off is NOT RUN. This is the first thing to prove.
5. Option 3 (help inside the right panel) is the weakest for a long text: 170 px at 1100 (about 16 characters per line, RUN_FACTS 5) and in HOME it collides with the audit panel (D-0375, D-0385).
6. Option 4 (floating window) is the largest and riskiest build; option 1 does not give what she asked (blocks, dims, locks scroll: RUN_FACTS 1).

## Table
| Option | What the user gets | What it costs or risks | Works at 1100 px | Touch | One source of text | Reconsiders a decision? |
|---|---|---|---|---|---|---|
| 1. Keep modal | Today: a 500 px window, page dimmed, blurred, not clickable, scroll locked | Nothing to build; does not answer her question | Covers 55 % of main (RUN_FACTS 1) | Works | help/*.md only | no |
| 2. Side drawer (Offcanvas) | A panel slides in at the right; page stays usable if backdrop and scroll are set to allow it (to prove) | Small: one JS call, one container, one CSS rule, tests. Risk: it lies OVER the right panel, so in HOME Audit mode it hides the audit panel unless it is a push-aside layout (to design) | Only if narrow (about 340 px) or it pushes the main panel; a 500 px drawer would cover 500 of 740 px main | Tap to open and close; a drag-to-resize needs new script | Yes: same markdown rendered by the server | no |
| 3. Panel type in right panel | Help in the right panel, wider by drag | Small to medium: a `help` entry in `PANEL_REGISTRY` and the sidebar YAML files (READ `sidebar_registry.py:20-60`). Risk: 170 px is unreadable for long text; in HOME it shares the panel with the audit | Poor: about 16 characters per line, about 9 screens (RUN_FACTS 5, estimate) | Works (it is plain content) | Yes | D-0375, D-0383, D-0385 in HOME (the panel is for the audit; it closes on leaving Audit mode); the other spaces: no |
| 4. Floating window | A window the user moves and resizes | Large: new JS (drag, resize, keep in view, pointer events, keyboard, focus, stacking, per-space state). No library in the page (RUN_FACTS 2). Highest risk of regression with the panel drag script `panel_widths.js` (179 lines, READ) | Yes, the user places it; it still covers part of the app | Dragging by finger fights with scrolling; needs care | Yes | no |
| 5. Second tab or window | Documentation beside the app, own screen space, no loss of main panel | Small: a link with `target` name and an anchor. Needs `docs/_site` built (gitignored, READ `docs/.gitignore`; the book icon is hidden when absent, `home_theater.py:77`). Needs one doc page and anchor per user space and term (missing) | Window width is the user's work; two windows on a 1920 screen leave the app at about 960 px, below the tested range (REASONED) | Phone or tablet: no side by side, only a switch of tab | Yes if the docs are generated from the same source (D-0399) | no |
| 6. Mark (popover) + long help elsewhere | Short meaning where the user looks; "Read more" opens the long text | Medium: one helper that makes the mark, one registry of term to text, the generator of D-0399 | Works; the popover is small | A tap opens a popover (REASONED for popover; RUN only for a tooltip stand-in) | Yes, if terms come from the generated source | no; it follows D-0404 and D-0399 |

## What exists, what stays
- Stays: the "?" button, `app/src/help/*.md` (four files, 145 lines; READ), the book icon, the browser test setup (`app/tests/test_panel_widths_browser.py`, many viewport widths, drag tests; READ).
- Exists, RUN: Bootstrap 5.3.1 with Offcanvas, Popover, Modal defined; `ui.popover` and `ui.tooltip` in Shiny 1.6.0.
- Missing: any use of Offcanvas or Popover in the app (READ, grep); a term-to-text registry; the generator of D-0399 (decided, not built); one documentation page per user space with anchors.
- Texts: the help files are static markdown read at each click (`home_theater.py:1890-1901`). Rendering the same markdown in a drawer is a change of container only.
- "Where is the user": the user space is already known (`input.sidebar_nav`, READ `home_theater.py:1887`). The mark knows its own term because the helper that draws the mark takes the term key. The drawer needs a "scroll to the section of the term" rule: markdown headings with fixed ids.

## What the HOME audit panel does (REASONED from D-0375, D-0383, D-0385)
- Drawer: if it overlays the right edge it hides the audit panel exactly when the user verifies. It must either push the main panel, or open on the LEFT, or sit over the main panel only. This is a design question, not a coding detail.
- Right-panel option: the audit panel and help compete; one of them must be tabbed, which changes the HOME right panel.
- Marks and second tab: no effect on the audit panel.

## Build order (CLAUDE.md section 2 tags are my reading of the table; check against it)
Nothing here may start before the "To decide first" items 1 and 2 are answered.
1. Prototype in a scratch copy: Offcanvas with backdrop off and scroll allowed, in the four user spaces, at 1100 and 1920, with a mouse click AND a touch tap on the page behind; plus `ui.popover` with a link inside on touch. This is a test, no repository change. Model: Sonnet, medium effort.
2. Write the browser tests first (adapted to the decided design): page behind stays clickable with the help open; help does not close on a click in the app; Escape closes it; it stays open when the user space changes (and shows the new space or says it does not); a 1100 px check that main panel stays at least half (D-0375/0384); touch tap test with `has_touch`; no horizontal overflow. Sonnet, medium.
3. Part A first (risky logic, small, independent files): registry of terms, `help_mark()` helper, popover content. Waits for D-0399's generated source for the Gallery terms; until then it can run on a hand-written key list only if she decides that, otherwise it must wait (no half fix: a second source of text would drift). Sonnet, medium.
4. Part B: the drawer container, the JS, the CSS, the registration in `ui.py`, the "?" button switched from the modal to the drawer. The modal code is then REMOVED in the same change (rule: no two ways to do one thing; ADR-099 point 16). Sonnet, medium. Parallel with step 3 only if they touch different files (drawer: `ui.py`, a new JS file; marks: a new module, the Gallery panel).
5. Documentation: anchors and a page per user space, generated from the same source. Haiku or Sonnet, low. Parallel with 3 and 4.
6. Review against the decisions, then a manual check by her. Opus for the reviewer.
Smallest step that leaves a working app: step 4 alone with the modal removed and the drawer holding the same four markdown files. The app works; the marks follow later.

## Pitfalls (all REASONED unless marked)
- A `backdrop:false` modal still blocks the page (RUN_FACTS 2). Do not "fix" the modal: use a different piece.
- Escape did not close the injected non-modal window (RUN_FACTS 2, cause unknown): keyboard behaviour of the new piece must be tested, not assumed.
- Offcanvas may set focus into itself and may lock body scroll by default: both are options to set and test.
- A popover is dismissed by a click outside if set to focus mode, but on iOS a click on a non-button does not give focus; use a `<button>` as the mark.
- Many marks fill the screen (her fear, D-0404): one mark per heading of the filter panel, not per value.
- A popover is inserted into the body; in the sidebars with overflow hidden or in the drag-handle zone it can be clipped or covered by the handles (see `test_the_grab_area_of_the_handles...`, READ). Test it in each space.
- Text size: the popover text must stay short; the long text belongs in the drawer or the documentation.
- Shiny re-renders (`output_ui`) destroy popover instances; the init must be done by delegation or on each render.

## Recommendation
Option 6, with the drawer (option 2) as the home of the long text, and the documentation link (option 5) kept for the full book. Reasons on merit:
- It is the only combination that answers both her wishes: a short meaning without a visible line, and a long help that stays open while she uses the screen.
- It uses pieces that exist and are RUN-verified as present (popover, offcanvas), so no new window manager (option 4) is needed.
- One source: the same generated text feeds the popover, the drawer and the documentation.
Condition: the prototype (step 1) must show that the page behind stays clickable and that the drawer does not hide the audit panel. If it does not, option 4 (floating window) becomes the next best, and its cost is then information only.

## Reconsiders a decision?
1: no. 2: no (if it does not take the HOME right panel). 3: yes, D-0375, D-0383, D-0385 in HOME. 4: no. 5: no. 6: no (it applies D-0404 and D-0399).

## To decide first (ranked)
1. Should the long help be allowed to cover the main panel, or must it push it aside (the main panel keeps at least half, D-0384)? This chooses between drawer designs.
2. In HOME Audit mode, may the help hide the audit panel, or must both be visible?
3. Should the short meaning be a popover with "Read more", or a hover tooltip without a link (the tooltip cannot hold a link, RUN)? A novice who does not hover needs the click.
4. Where does "Read more" open: the drawer at the term, or the documentation tab?
5. Does the help follow the user when the user space changes, or stay on the space where it was opened (today the modal stayed, with the old title, RUN_FACTS 1)?
6. May Part A wait for the D-0399 generator, or may a hand-written list be used meanwhile? (Her rule: one source.)

## Not verified
- That Offcanvas with backdrop off leaves the page clickable and does not trap focus or lock scroll (not run).
- That `ui.popover` opens on a touch tap, holds a link, and is not clipped in the side panels (not run; only a tooltip stand-in was run).
- The real width of the HOME right panel in Audit mode.
- The help modal in BLUEPRINT and Test Lab; a real touch device.
- The size of the generated Gallery term text and its fit in a popover.
- That my tags for model and effort match the CLAUDE.md section 2 table (not re-read).
