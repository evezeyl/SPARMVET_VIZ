# RUN_FACTS: can the help stay open beside the screen (run 2026-11-21)

Method: app started on port 8765 with SPARMVET_APP_FEATURES=qa, headless Chromium (Playwright), windows 1100x800 and 1920x1080. App stopped at the end (by its PID). Scripts: tmpAI/panel/help_beside/check_scratch/run.py, run2.py, run3.py, run4.py, run5.py, run6.py. Raw values: out.json, out2.json, out6.json in the same folder.
RUN = measured in this run. NOT VERIFIED = not measured.
Note: the workspace pills in this checkout read Home, Blueprint Architect, Test Lab, Gallery.

## 1. The help modal ("?" button, HOME and GALLERY)
- HOME and GALLERY, both sizes: the page behind is covered by a dark backdrop (opacity 0.5, rgb(70,70,70)) and is also blurred. RUN (screenshots Home_1100_modal.png, Gallery_1920_modal.png).
- HOME and GALLERY, both sizes: a control behind cannot be clicked. The click lands on the full-screen `.modal` layer (element_at_point = "modal fade show"), not on the control; Playwright's click on the nav pill timed out (blocked). A real mouse click on that point CLOSES the modal and does not reach the control. RUN.
- HOME and GALLERY: the page behind cannot be scrolled (body gets `modal-open`, overflow hidden; wheel on the backdrop area moves the modal's own scroll instead: scrollTop 600). RUN.
- Size. The modal is 500 px wide at both window sizes (HOME 1100: x=300; HOME 1920: x=710). Its content is very tall because the text is long: HOME 3368 px, GALLERY 1405 px at 1100 and 1410 px at 1920 (HOME 1920: 3375). It is taller than the window (800 or 1080), so the whole overlay scrolls. RUN.
- How much of the main panel stays visible. The modal is centred over the main panel (main panel 910 px wide at 1100, 1594 px wide at 1920): at 1100 the modal covers 500 of 910 px (55 %), at 1920 it covers 500 of 1594 px (31 %). The rest is visible but dimmed, blurred and not usable. RUN (computed from the measured rects).
- Move or resize: not possible. CSS `resize: none`; no draggable element; jQuery UI is not loaded. RUN.
- Switching user space while it is open: the user cannot do it by mouse (the layer blocks the nav). When a nav click was forced by JavaScript, the space switched (HOME to Gallery) and the modal STAYED open, still titled "Home - Help". RUN (JS click, not a user path).
- What closes it: Escape closes it (RUN, both spaces, both sizes); a click outside the dialog closes it (RUN); the "Close" footer button closes it (RUN).
- Size note: the code asks for size "lg" (`home_theater.py:1904`) but the measured width is 500 px (the default modal width), not lg. RUN (measured value); the reason is NOT VERIFIED.

## 2. JavaScript facts (HOME page, 1100x800)
- window.bootstrap defined: yes (object). Version `bootstrap.Tooltip.VERSION` = 5.3.1. RUN.
- bootstrap.Offcanvas, bootstrap.Popover, bootstrap.Modal: all defined (true). RUN.
- jQuery: defined, version 3.6.0. jQuery.ui: not defined; `$.fn.draggable`: not defined. RUN.
- A Bootstrap modal injected at run time with `{backdrop:false, keyboard:true}` (in the browser only): no backdrop element is made (0) and the body still gets `modal-open` (overflow hidden), BUT the `.modal` layer itself is full-screen and still catches clicks: the click on the nav pill hit the layer (element_at_point = "modal show | zz"), the page behind did NOT react (active pill stayed "Home"). So backdrop:false alone does NOT leave the page usable. RUN.
- Same injected modal with `pointer-events:none` on the `.modal` layer and `pointer-events:auto` on the dialog: the click reached the nav pill (active pill became "Gallery") and the modal stayed open. So the page behind is usable only with that extra CSS. RUN (screenshot inj_pe_none_1100.png).
- Escape on the injected backdrop:false modal did not close it in my script (`inj_escape_closes` false). Cause NOT VERIFIED (focus was perhaps not inside the modal).

## 3. Tooltips
- HOME: no `ui.tooltip` is mounted in this checkout in Exploration or Audit mode with no audit step (0 elements `bslib-tooltip` / `data-bs-toggle=tooltip`). After a filter was added and applied (screenshot home_1920_filtered.png) still 0: `filter_inventory_ui` (the code of `home_theater.py:2429`) is not mounted in the page (the repo tests assert count 0, `app/tests/test_shiny_na_tick.py:71`). The audit panel tooltips need audit steps; I did not create one. So no existing HOME tooltip could be exercised. NOT VERIFIED for a real HOME tooltip.
- BLUEPRINT ARCHITECT: one `ui.tooltip` exists ("Write your intent ...") but its trigger is not visible on load; not exercised. NOT VERIFIED.
- Instead I injected a real `<bslib-tooltip>` (the component `ui.tooltip` produces) into the page in the browser. This is a stand-in, not an app tooltip. Results, desktop mouse: opens on hover (RUN); opens on keyboard focus (RUN); it does NOT stay open when the pointer moves onto the tooltip (list empty after 1 s; so a link inside could not be clicked) (RUN); it closes when the pointer leaves (RUN). Touch (`has_touch`, `tap`): a tap opens it (RUN); a second tap keeps it open (RUN); a tap elsewhere closes it (RUN). Width: 200 px (max-width 200px), 134 px high for a 190-character text. RUN. Screenshots tooltip_hover.png, tooltip_focus.png, tooltip_tap.png.

## 4. The docs link (book icon)
- HOME (and all four spaces: it is in the left panel): the book icon is shown (1 link to /docs/index.html; `docs/_site` exists in this checkout). RUN.
- `GET /docs/index.html` on the app's own server: HTTP 200. RUN (curl).

## 5. The right panel (real width in px, content)
| User space | 1100 px | 1920 px | What it shows today |
|---|---|---|---|
| GALLERY | 170 px (x=930) | 288 px (x=1632) | "Gallery Explorer" card with 3 short lines (right_Gallery_1100.png, right_Gallery_1920.png) |
| BLUEPRINT ARCHITECT | 170 px | 288 px | "Blueprint Surgeon" card, "Action Help", "Plot Defaults" form (palette, theme), further cards below (right_Blueprint_1100.png, right_Blueprint_1920.png) |
| TEST LAB | 170 px | 288 px | five collapsed accordions: ID Reconciliation, Data analysis recipe Scaffolding, Synthetic Data, Anonymisation, File Reformatting (right_TestLab_1100.png, right_TestLab_1920.png) |
RUN for widths and content (all screenshots looked at: Gallery 1100, Blueprint 1100, TestLab 1920; the other three read from the printed text and rect only).
- HOME: the right panel is closed in Exploration (screenshots home_1920_start.png) and opens in Audit mode (home_1920_audit.png was taken; its width was not measured). NOT VERIFIED in numbers.
- Lines of an 800-word help text: ESTIMATE only, not measured. About 5000 characters. At about 8 px per character (16 px font, the panel reports 16 px) and about 40 px of padding: 1100 px window (panel 170) is about 16 characters per line, about 310 lines; 1920 px window (panel 288) is about 31 characters per line, about 160 lines. With a 13 px font (the Gallery card text looks smaller): about 250 and 130 lines. A window of 800 px shows about 35 lines at 1100 px (so about 9 screens of scrolling); 1080 px shows about 48 lines.

## Screenshots (all in tmpAI/panel/help_beside/check_scratch/)
Home_1100_before/modal, Home_1920_before/modal, Gallery_1100_before/modal, Gallery_1920_before/modal, home_1100_modal_scrolled, home_1920_start, home_1920_filter_form, home_1920_filtered, home_1920_audit, inj_modal_1100, inj_pe_none_1100, tooltip_hover, tooltip_focus, tooltip_tap, right_Gallery_1100/1920, right_Blueprint_1100/1920, right_TestLab_1100/1920 (all .png). Looked at: Home_1100_modal, Gallery_1920_modal, right_Gallery_1100, right_Blueprint_1100, right_TestLab_1920, home_1920_filter_form, home_1920_filtered. Not looked at one by one: the others.

## Could not check
- A real in-app tooltip (HOME or the audit panel); only a stand-in injected in the browser.
- BLUEPRINT ARCHITECT and TEST LAB help modal (only HOME and GALLERY were asked and run).
- Whether the help modal could be made non-modal by app code (nothing was built); only the injected test above.
- Right panel width in HOME Audit mode; the real size of an 800-word text (estimate only).
- The cause of "modal 500 px although size lg" and of the Escape result on the injected modal.
- A real phone or touch device; only Chromium headless with touch emulation.
