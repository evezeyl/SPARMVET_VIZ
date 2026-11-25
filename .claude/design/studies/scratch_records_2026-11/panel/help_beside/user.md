# Help beside the screen: the viewpoint of the new user (panel-user, 2026-11-21; filed by the coordinator from its report)

Labels: READ = file and line; RUN = measured in `RUN_FACTS.md`; SEEN = it looked at the screenshot; REASONED = its own conclusion.

## Summary
1. Today the user cannot read and act at the same time: the window dims and blurs the app, a click outside closes it, and its text is very long (RUN).
2. The idea in one sentence: a small "i" mark gives a short meaning when I click it, and the long help opens beside the app and stays open until I close it.
3. Recommended: option 6 (a mark with a short meaning) with option 2 (the side drawer) as the place for the long text. Not the right panel (option 3): 170 px at a 1100 px window is about 16 characters per line (RUN).
4. Hover alone fails for this user: it does not know it should hover, a touch screen has no hover, and the hover text vanishes when the pointer leaves it, so a link inside cannot be clicked (RUN, on a stand-in). The mark must open on click or tap.
5. The long text must start with a short "What you see here" part and be split into sections. Nine screens of scrolling (an estimate) is where this user stops reading.
6. One hidden risk: a drawer on the right edge may cover the audit panel of HOME, where the user needs to see the steps while reading (REASONED).

## Table
| Option | What the user gets | Cost or risk | Works at 1100 px | Touch | One source of text | Reconsiders a decision? |
|---|---|---|---|---|---|---|
| 1. Keep the blocking window | the same as today | I lose the screen I try to understand; a click outside closes it by accident | covers 55% of the main panel (RUN) | works | yes | no |
| 2. A side drawer that does not block | the text beside the app; I can click the app | may cover the right panel and the audit (REASONED) | only if narrow (about 350 px); the main panel shrinks | yes (the ready piece exists, RUN) | yes | no |
| 3. Help inside the right panel | always in the same place | 170 px is too narrow to read; in HOME it shares the audit panel | no | yes | yes | D-0375, D-0385 in HOME |
| 4. A floating window I move and resize | most freedom | I must learn to drag it; it can hide what I read about; new script | poor | hard to drag with a finger | yes | no |
| 5. A second tab or window | the full documentation on a second screen | I must place two windows myself; on one small screen I switch tabs, the same problem as today | poor | poor | yes | no |
| 6. A mark with a short meaning, the long text elsewhere | a short answer at the spot, the long text only if I ask | the marks must stay few | yes | yes, if it opens on tap | yes (D-0399) | no (it follows D-0404) |

## Recommendation: option 6 with option 2
- Each user space keeps its "?" button; it opens the drawer instead of the window.
- The "i" mark opens a small text on click or tap. It stays open until I click elsewhere.
- That small text ends with "Read more", which opens the drawer at that term.

Words the screen must carry (its wording, not decided):
- The mark's label for screen readers: "What does this mean?"
- A small text, for example: "Difficulty: how much work the example needs. Simple means one shape and no data preparation. Read more"
- The first sentence of the drawer: "This help stays open while you work. Close it with the cross, or press Esc."
- Each drawer starts with "What you see on this screen" in five lines or fewer, then sections one can jump to.
- When the drawer covers something, say so, for example in HOME's Audit mode: "Help is covering the audit panel. Make it narrower, or close it." The one warning it would keep (D-0149).

Where the mark sits:
- Only on terms that have a meaning: the six Gallery filter groups, the table choices (Source, T1, T2, T3), Exploration against Audit mode. Not on every button.
- In the Gallery's left panel the group headings already fill the width (SEEN: `right_Gallery_1100.png`): no room beside "Family (Purpose)". The mark goes inside the opened group, on its first line (REASONED).
- The same circled style as the existing "?" button.

## To decide first (ranked)
1. Does the drawer cover the right panel (and the audit in HOME), or push the main panel aside?
2. Does the mark open on click only, with hover as an extra?
3. How long may a help text be before it is cut into sections?

## Not verified
A real drawer (none was built or run); a real phone; the help texts of Test Lab and BLUEPRINT; a real tooltip of the app (only a stand-in was tested); whether Esc and keyboard focus work in the drawer; the ledger lines were not read in full.
