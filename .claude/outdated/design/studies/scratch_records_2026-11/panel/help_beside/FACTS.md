# Help that stays open beside the screen: facts of today (scout, 2026-11-21, `dev`; filed by the coordinator from its report; READ, nothing run; the facts that need a run are in `RUN_FACTS.md`)

The owner's question (ledger D-0404, her words): "a question can the help be open as popup so the user can both see the ui and help at the same time ? not having to open and close all the time (would be practical if user can have help stay open while it verifies and try to understand)". Also hers: "I am afraid that too much explanation in the ui will be too much information - and Id rather the user be able to use the help".

Short file names: `home_theater` = `app/handlers/home_theater.py`; `frame_widths` = `app/modules/frame_widths.py`; `sidebar_registry` = `app/modules/sidebar_registry.py`.

## What the user sees today (all four user spaces: HOME, BLUEPRINT, Gallery, Test Lab)
- In the left panel: a small "?" button (title "Quick help for this workspace"), a book icon and a GitHub icon (`home_theater:1849-1874`).
- "?" opens ONE centred window over the app (a modal), titled "<user space> — Help", large size, closed by a click outside or the Close button (`home_theater:1887-1909`).
- The text is one file per user space, read from disk at each click: `app/src/help/home.md`, `blueprint.md`, `gallery.md`, `test_lab.md` (`home_theater:1890-1901`). An unknown user space gets the HOME text; a missing file gives "No help available".
- The book icon opens the documentation (`/docs/index.html`) in a new browser tab. It is shown only when the documentation has been built (`docs/_site`) (`home_theater:77, 1857-1864`). The documentation is served by the app itself, so it works without the internet (reasoned).
- The Gallery help does not come from the taxonomy source: that source is decided (D-0399), not built.

## Other help-like things
- Tooltips (a small text when pointing at a control) exist: on the filter rows of HOME (`home_theater:2429, 2447`), in the audit panel (`app/handlers/audit_stack.py:381, 403, 706, 739`), in BLUEPRINT (`app/modules/wrangle_studio.py:483, 979, 1031, 1093`). The tool for them exists in the installed Shiny (`ui.tooltip`). Whether they open on a click or a touch: needs a run.
- A popover (a small window opened by a click, which stays open) IS in the installed Shiny as a ready tool (`ui.popover`, Shiny 1.6.0). CORRECTED 2026-11-21: the scout's search did not find it; the developer viewpoint found it by running. The app does not use it anywhere yet.
- BLUEPRINT has an "action help" card in its right panel (`sidebar_registry:75-78`; `home_theater:2165-2173`; listed in `config/ui/sidebars/blueprint_standard_right.yaml:4`).
- `app/modules/help_registry.py` (a "Help & Configuration Registry" page) is called by nothing.
- The notification log and the pattern "a short notice; a click opens the detail" (ADR-060, `.claude/knowledge/architecture_decisions.md:1864, 3569`).

## The frame the help must live in
- Three panels: left, main, right (`app/src/ui.py:364-389`). Widths (`frame_widths:25-42`, PROVISIONAL): left 17% of the window (190 to 340 px), right 15% (170 to 340 px), the main panel never under half after a drag.
- At a 1100 px window: left 190, right 170, main about 740 px. At 1920 px: left 326, right 288, main about 1306 px (computed from those values).
- HOME: the right panel is closed in Exploration and holds the audit in Audit mode (D-0375, D-0383, D-0385).
- Gallery: the right panel shows a static card "Gallery Explorer" with two short sentences (`home_theater:2236-2246`; `config/ui/sidebars/gallery_focus_right.yaml:3`).
- Test Lab: the right panel shows a list of tool descriptions (`home_theater:2248-2257`; `config/ui/sidebars/testlab_standard_right.yaml:3`).
- BLUEPRINT: the right panel shows the action help card and the agent chat.
- The content of a side panel is a list of "panel types" set in configuration files (`sidebar_registry`; one file per side and user space in `config/ui/sidebars/`). A help panel would be one more type and one more line in those files.

## What the libraries offer (READ; several need a run)
- A side drawer that slides over the edge without blocking the page ("offcanvas" of Bootstrap): its style file is in the installed Shiny; its script was not found by a text search in Shiny's files. Needs a run to know.
- A window that can be dragged and resized: no helper found (jQuery UI absent). It would need new script, kept inside the app (ADR-071: no outside links).
- A second browser tab or window: exists (the documentation link).

## Decisions and rules that bear on it (read each line in `.claude/knowledge/decision_ledger.md`)
D-0404 (this question; and the meaning of a Gallery filter term on hover or click of a small mark); D-0399 (one generated source for the Gallery terms, also for the documentation and later the help); D-0375, D-0381 to D-0386 (the frame and its widths; the right panel of HOME); D-0149 ("be aware of not over warning - warn only when problem"); D-0094, D-0100, D-0059 (texts that go into the documentation and the help); D-0010 (the documentation book ships with the app); ADR-060 (notifications); ADR-071 (no outside links; assets kept in the app). Asked, not decided (ledger, "Asked, not decided", M155 point 13): a small help button in the audit dialog.
One record out of date: the ledger line of D-0375 says the side panels are "fixed at 340 px"; the code now follows the window.

## The options that follow from the facts (the scout's neutral list; not chosen)
| Option | What the user sees | What exists / what is missing | The right panel of HOME | Reconsiders a decision? |
|---|---|---|---|---|
| 1. Keep the modal | a window over the app; the page behind is covered | exists | unchanged | no; but it does not give what she asked |
| 2. A side drawer over the right edge that does not block the page | the help slides in at the right; the app stays usable | script to confirm by a run, or new script kept in the app | it would lie over it or take its place | no, if separate from the HOME right panel |
| 3. The help as a panel type in the right panel of the frame | the help sits in the right panel; the user drags it wider | the mechanism exists; a help panel type and a line per user space are missing | in HOME the right panel is the audit panel in Audit mode: the help would share it | D-0375, D-0385 in HOME; none in the other user spaces |
| 4. A floating window the user moves and resizes | a small window over the app, placed by the user | all of it is missing; new script kept in the app | unchanged | no |
| 5. The documentation or a help page in a second browser tab or window | the user puts the second window beside the app | exists for the documentation; a page per subject and a link to it are missing | unchanged | no |
| 6. A short meaning on a small mark, the long text in a second window | marks in the panel; long text off screen | tooltips exist; the generated source is not built; a link per term is missing | unchanged | no; follows D-0404 and D-0399 |

## Not verified (by reading)
Whether the modal blocks clicks and scrolling behind it; whether it can be moved; whether tooltips open on click or touch; the Bootstrap version and scripts loaded in the page; the docs link in this checkout; the real widths of the right panels on screen. These are checked by a run: `RUN_FACTS.md`.
