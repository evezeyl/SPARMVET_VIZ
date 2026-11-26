# Help that stays open beside the screen: one table for the owner (2026-11-21; your order with decision D-0404)

## 0. How to read this
- Your question: "can the help be open as popup so the user can both see the ui and help at the same time ? not having to open and close all the time".
- Done: a scout read the code (`FACTS.md`); a reviewer ran the app in a browser at 1100 x 800 and 1920 x 1080 (`RUN_FACTS.md`, with screenshots); three viewpoints compared the options (`user.md`, `architect.md`, `developer.md`), and two of them ran small trials in the browser. All files are in `tmpAI/panel/help_beside/`.
- Nothing is built. Nothing is decided. RUN = measured in a browser; READ = read in the code; REASONED = a conclusion.
- Your rule is applied: each option is judged on its merit; "reconsiders a decision?" is its own column, as information only.

## 0b. Corrections and additions after a second browser run (2026-11-21 afternoon; details in `RUN_FACTS_2.md`)
The second run measured the points of section 8. It corrects two statements below and adds numbers. All RUN, at 1100 x 800 and 1920 x 1080; touch is an emulation, not a real device.

| Point | What section 2, 3 or 8 says | What the second run measured |
|---|---|---|
| The small window on a click (section 2) | "stays open until the user clicks elsewhere" | WRONG as tried: it stays open, but it does NOT close on a click elsewhere or on Esc; it closes only on a second click on the mark. Closing on a click elsewhere would have to be built and was not tried. |
| The drawer and the keyboard | not run | Esc closes it only while the keyboard focus is still on the button that opened it. After the user tabs into the app, Esc does nothing. The focus is not moved into the drawer. This would have to be built for keyboard and screen-reader users. |
| The drawer and a click or tap in the app | not run | A click in the app leaves it open. A tap opens it, a tap in the app keeps it open, a tap on the cross closes it. |
| HOME, Audit mode, drawer at the right edge | not measured | It covers the whole audit panel. At 1100 px it also covers 34% of the main panel and 31% of the plot; at 1920 px 10% and 7%. |
| HOME, Audit mode, drawer to the left of the audit panel | "about 320 px" left (an estimate) | The audit panel stays free. At 1100 px it covers 57% of the main panel and 58% of the plot (268 px of plot left); at 1920 px 32% and 31% (834 px left). |
| A real hover text of the app (HOME, an audit step) | measured on a stand-in | It opens on hover and on keyboard focus, is 200 px wide, closes when the pointer moves onto it, and did NOT open on a tap. |
| The small window inside the Gallery's left panel | not run | It is not cut by the panel, moves with it when it scrolls, and its link can be clicked by mouse and tap. At 1100 px it lies 103 px over the main panel. |
| The help window in BLUEPRINT and Test Lab | not run | The same as HOME: 500 px wide, blocks the page. Text height about 2370 px (BLUEPRINT) and 1240 px (Test Lab). BLUEPRINT's window is titled "Wrangle Studio — Help" while the navigation says "Blueprint Architect". |
| Why the window is 500 px wide | not known | READ: the code asks for size "lg" (`app/handlers/home_theater.py:1907`); the toolkit only knows "s", "m", "l", "xl", so the size is ignored. A one-word defect, not fixed. |
| The documentation including a help file | reasoned | READ: the documentation already includes files by path; the four help files have no links and start at a second-level heading, so it should work. Not rendered, not proven. |

Still not verified: a real touch device, a screen reader, the drawer's place in BLUEPRINT and Test Lab, a small window that closes on a click elsewhere, the rendering of the documentation.

## 1. The help today (all four user spaces: HOME, BLUEPRINT, Gallery, Test Lab)
- The "?" button opens one window over the app. RUN: it dims and blurs the page; a click on the app behind it does not reach the app, it closes the help; scrolling behind it is locked; it is 500 px wide and cannot be moved or resized; at a 1100 px window it covers 55% of the main panel.
- Its text is one long file per user space. RUN: HOME's is about 3370 px high.
- The book icon opens the documentation in a new browser tab, served by the app itself (works without the internet). RUN: it answers.
- So today a user cannot read the help and use the screen at the same time.

## 2. The answer in short
**Yes, it is possible, with pieces the app already loads.** All three viewpoints, working separately, recommend the same combination:

1. **A small "i" mark** next to a term. A click (or a tap) opens a small window with the short meaning and a "Read more" link. It stays open until the user clicks elsewhere.
2. **A side drawer** at the right edge for the long help. It does not dim or block the app, and it stays open while the user works. The "?" button and "Read more" both open it.
3. **The documentation link stays** as the full text.

This is your decision on the Gallery filter terms (D-0404: a small visible mark, hover or click, also in the documentation), extended to the long help.

What was RUN for it:
- The click-open small window exists in the app's toolkit. It opens on a click and on a tap, stays open when the pointer leaves, and a link inside it can be clicked. It is about 250 px wide.
- A text shown on hover cannot do this: it closes when the pointer leaves it, so a link inside cannot be clicked, and a novice does not know to hover. It is 200 px wide.
- A side drawer with its dimming switched off is 420 px wide, leaves the app usable, and stays open when the user changes user space.

## 3. The hard limit you must know
**At a 1100 px window nothing can sit beside the app without covering part of it.**
- RUN: the drawer covers the right panel and 250 of the 740 px of the main panel at 1100 px. At 1920 px it covers the right panel and 132 px of the main panel.
- In HOME's Audit mode the right panel holds the audit. A drawer at the right edge covers it. Placed to the left of the audit panel, it covers the plot instead, and at 1100 px the main panel would fall to about 320 px.

## 4. The options compared
| Option | What the user gets | What it costs or risks | At a 1100 px window | Touch screen | One source of text | Reconsiders a decision? (information only) |
|---|---|---|---|---|---|---|
| 1. Keep the window over the app | the same as today | does not answer your question; a click on the app closes the help by accident | covers 55% of the main panel and blocks the rest | works | yes | no |
| 2. A side drawer that does not block | the long help beside the app; the app stays usable; it stays open | it lies over the right panel and part of the main panel; in HOME it hides the audit panel unless placed otherwise; small new work | covers 250 of 740 px of the main panel | a tap works for the mark; the drawer itself was not tried on touch | yes: the same help files | no |
| 3. The help inside the right panel of the frame | always in the same place; nothing is covered | 170 px wide at 1100 px, about 16 characters per line (an estimate); an 800-word text is about nine screens; in HOME it shares the panel with the audit | poor | works | yes | D-0383 and D-0385 in HOME (the right panel of HOME and when it opens) |
| 4. A floating window the user moves and resizes | the user puts it where it does not disturb | everything is new script; dragging with a finger is hard; it can hide what the user reads about; the largest work and the most to test | the best placement, but a small window | difficult | yes | no |
| 5. The help or the documentation in a second browser window | full-size text; ideal with two screens | the app does not know where the user is, so the text does not follow; on one 1100 px screen the two windows leave the app about 550 px; on a tablet there is no side by side | only with two screens | poor | yes, if the documentation is built from the same files | no; a link straight to a section would touch one point of the documentation decision (ADR-096) |
| 6. A mark with a short meaning, the long text elsewhere (in 2, 3 or 5) | a short answer where the word is; the long text only on request | two places of text to keep in agreement; the marks must stay few | yes | yes, with a click or tap | yes, from the generated source you decided (D-0399) | no: it follows D-0404 and D-0399 |

**Recommended by all three viewpoints: option 6 with option 2, and option 5 kept as the documentation link.** Their reasons: it is the only combination that lets a novice get a short answer with one click, keeps long text off the screen until asked, and leaves the app usable while the help is open. Options 3, 4 and 5 each fail at a 1100 px window or on a touch screen.

## 5. What the user would see (proposals of the user viewpoint, not decided)
- The mark's name for screen readers: "What does this mean?"
- A small window, for example: "Difficulty: how much work the example needs. Simple means one shape and no data preparation. Read more"
- The first sentence of the drawer: "This help stays open while you work. Close it with the cross, or press Esc."
- Each long help starts with "What you see on this screen" in five lines or fewer, then sections one can jump to.
- Where the marks sit: only on terms that have a meaning: the Gallery filter groups, the table choices (Source, T1, T2, T3), Exploration against Audit mode. Not on every button.
- In the Gallery's left panel the mark goes inside the opened group, on its first line: the group headings already fill the width, and a mark inside a heading would be a button inside a button.
- The mark is a circled "i", kept apart from the "?" of the long help.

## 6. The choices for you, ranked
| # | The question | The options | What the viewpoints say |
|---|---|---|---|
| 1 | In HOME's Audit mode, what may the help cover? | (a) the audit panel; (b) the plot, with the drawer to the left of the audit panel; (c) the user chooses by dragging it narrower | The architect: tell you both costs. (b) leaves about 320 px for the main panel at 1100 px. The user viewpoint wants to see the audit steps while reading, and proposes one sentence when the help covers it: "Help is covering the audit panel. Make it narrower, or close it." |
| 2 | May the long help lie over part of the screen at 1100 px? | yes, as an overlay; or it pushes the main panel aside | Side by side without covering is not possible at that size (section 3). Pushing aside makes the main panel smaller than the half you decided it keeps (D-0384: information). |
| 3 | The mark: a click, or hover? | a click (and tap), with hover as an extra; or hover only | All three: a click. Hover alone fails for a novice and on a touch screen, and cannot hold "Read more". |
| 4 | Where does "Read more" open? | the drawer, at that term; or the documentation tab | The user and the developer: the drawer. The architect: the drawer, with the documentation holding the same text. |
| 5 | Does the help follow when the user changes user space? | it follows; or it keeps the text of where it was opened | RUN: a drawer stays open across user spaces, so its text must follow. Today's window keeps the old title. |
| 6 | Which text is the master? | the help files of the app, with the documentation including them; or the documentation | The architect: the app's files, because the help must work when the documentation is not built. |
| 7 | May the marks start from a hand-written list? | start now with a hand-written list; or wait for the generated source (D-0399) | The developer asks; the generated source is not built yet. |
| 8 | Does the drawer remember that it was open? | it starts closed at each load; or it remembers in the browser, as the panel widths do | The architect: closed at each load. |
| 9 | How long may a help text be? | a limit, or sections with a short start | The user: a short start and sections; nine screens is where a reader stops. |

## 7. If you say yes: the order the developer proposes (not started)
1. A trial on a scratch copy: the drawer and the mark, with mouse and touch, in the four user spaces at both window sizes. This proves the points still open.
2. The browser tests first: the page behind stays usable; the help does not close on a click in the app; Esc closes it; a tap test; a test at 1100 px.
3. The drawer with today's four help texts, and the blocking window removed in the same change. This alone already gives you what you asked.
4. The marks, from the generated source of the Gallery terms.
5. The same text in the documentation.

## 8. Not verified
- The drawer: Esc, keyboard focus, and touch were not run. Only the mark was tapped.
- A real tooltip of the app: none was visible in the run; the hover behaviour was measured on a stand-in placed in the page.
- A click-open small window inside the scrolling left panel or inside an opened group.
- The overlap in HOME's Audit mode in real numbers (the reviewer's click on the Audit control failed).
- The help window of BLUEPRINT and Test Lab; a real touch device.
- Why today's window is 500 px wide when the code asks for the large size.
- That the documentation can include a help file as it is (reasoned).
