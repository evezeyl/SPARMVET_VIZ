# Panel widths, round 2 (coordinator, 2026-11-20). Read BRIEF.md first, then this.

## Round 1 result (shown to the owner)
Option B: side panel widths follow the window (left clamp 220 to 340 px, right clamp 200 to 340 px, in vw), main panel about 62 to 67 % at 1100 to 1920 px. bslib already draws a drag handle and a close toggle on each sidebar; a dragged width is lost on reload. Prototype: tmpAI/panel/panel_widths/proto.py, measure.py.

## The owner's answer (her words, 2026-11-20)
"ok - So I think we need a combination I think - so ok to hide the right side panel in home when the audit mode is inactive - but it will need to appear when the audit mode is activated. The question is can we have a ca  2/3 at any with but that the user can adjust via drag ? can this be saved eg in a session ? because the way the user will have to work will depend on the screen capabilities - eg. at home I have a wide screen but not at work so I need eg. to be able to adjust the width depending on how its practical to do - have all agents necessary explore what is possible in this line . So its near the B if I understand well  - and the drag must be findeable by the user ..."

## DECIDED by her now
- HOME: the right side panel is hidden when Audit mode is inactive and appears when Audit mode is activated.
- Direction: near option B (main panel about 2/3 at any width), and the user can adjust by drag; the drag must be findable.
OPEN (to explore, she decides after): where and how a dragged width is kept ("eg in a session"); how the drag is made findable; what the other user spaces do with the right panel.

## Facts to respect
- The frame is one code block for the four user spaces; today the right sidebar is present or absent for ALL spaces from HOME's config (app/src/ui.py:378), decided at page build, not reactive. The mode (Exploration / Audit) is a reactive value `home_mode` in app/src/server.py; the mode switch exists only with `t3_sandbox_enabled`.
- In HOME the right panel today also holds content shown outside Audit mode? CHECK what `right_sidebar_content_ui` shows in Exploration (home_theater.py about :2307) and what BLUEPRINT, GALLERY, TEST_LAB put in the right panel (placeholders for two of them).
- A HOME session (`{user_data}/_sessions/{session_key}/`) belongs to one recipe plus one data batch and exists only with `session_management_enabled`; it is written on Apply in the audit (D-0302). It can be opened on another machine (export/import zip). Her reason for saving is the SCREEN she sits at ("at home I have a wide screen but not at work").
- User preferences file (`user-preferences.yaml` in user_data): designed, NOT implemented (ui_implementation_contract.md, last section).
- ADR-071: no CDN; local JS only under app/src/www. ADR-062: do not reposition bslib's toggle. ADR-045 and the reactive write rules R1 to R4 of ui_implementation_contract.md section 14.
- Browser local storage is per browser and per machine; nothing in the app uses it today (CHECK by grep for localStorage).

## What each viewpoint answers (one round; at most 300 words plus a table)
1. Showing the right panel only in Audit mode in HOME: how (bslib sidebar open/close driven from the server, e.g. `ui.update_sidebar`; or build/remove), what the main panel gets in Exploration at 1100/1366/1600/1920, what happens with pending audit steps when the user goes back to Exploration, what the other three user spaces do.
2. About 2/3 for the main panel at any width WITH both panels open: the numbers (round 1 found 62 % at 1100 with floors 220/200); can the floors go lower, what breaks.
3. Keeping the dragged width: options at least (a) the browser's local storage, per machine and per browser; (b) the HOME session file; (c) a user preferences file in user_data; (d) not kept, a reset button only. For each: does it answer her reason (the screen she sits at differs between home and work), which app features have it, what a second machine or a second user of the same deployment sees, privacy, effort, tests. Should the stored value be px or a share of the window? Is a "reset widths" control needed?
4. Making the drag findable: what bslib draws today (measure or read), and options (a visible grip, a wider hit area, a cursor, a tooltip, a line in the help page, a double click to reset), within rules_css_style_spec.md.
5. Pitfalls and what must be tested. Recommend one combination. You recommend; she decides.
Scratch only under tmpAI/panel/panel_widths/. Do not edit the repository. Never read tmp.md.
