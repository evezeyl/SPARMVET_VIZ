# Architect round 2 (panel widths), verified on shiny 1.6.0 with playwright, prototype proto2.py, persist.js, m2.py, m3.py, m4.py

## (a) Server-driven open/close (verified, m2.py)
ui.update_sidebar("audit_sidebar", show=bool) works on the nested right sidebar (ui.sidebar(open="closed") at build, then show=True on mode change).
1366 px, left 340: right closed -> centre 1026; right open 340 -> centre 686. Toggling Exploration/Audit repeated: stable. Settled after about 1 s (animation).
Server can read the open state: input.audit_sidebar() is True/False (the user's own toggle click is reported too).
Content inside a closed sidebar is not rendered until first opened (output suspended when hidden): rcontent rendered once per session, at first open.
The bslib toggle stays on the page: the user can open the right panel by hand in Exploration (not prevented by update_sidebar).

## (b) How bslib holds the width (verified)
- Build: ui.sidebar(width=) is written as inline style on the .bslib-sidebar-layout container: --_sidebar-width: 340px (private variable, underscore).
- Drag: bslib JS writes the same inline --_sidebar-width: 460px on the container. Public variable --bslib-sidebar-width is overridden by the inline private one (tested: setting it did nothing).
- bslib dispatches a DOM event "bslib.sidebar.resize" on the sidebar (detail.phase = start|move|end|keyboard, detail.width px). No Shiny input is sent by bslib for the width.
- Drag limits are in the JS: min 150 px, max window.innerWidth - 50, no knowledge of the other sidebar or of a minimum centre: dragging the right panel to -1000 px gave right 978, centre 48 px at 1366. Keys Home/End give 150 / 978.
- A 30-line local script (www/, ADR-071 allows local JS) listened to the event, saved {px, vw, share} in localStorage and sent it to the server with Shiny.setInputValue; at DOMContentLoaded it set --_sidebar-width inline. Reload restored left 240 / right 460 (also when the right panel was closed at build and opened later). Saved as a share: reload at 1920 gave right 647 (0.337 x 1920). Window resize without reload does not rescale (px stays).
- Second browser profile: nothing restored (localStorage per profile).
- Dependence on a private bslib variable and event: a bslib upgrade can break it silently; a test that drags and reloads is the only guard.

## (c) The handle today (verified, real theme.css loaded)
12 px wide, full height, cursor ew-resize, tabindex 0, role separator, title "Drag to resize sidebar", keyboard arrows. Visible part: a 2 x 30 px bar at opacity 0.1 (dark, #1d1f21), growing to 3 x 40 at hover, 4 x 50 blue on press. Hit area extended by an invisible ::before (14 px). Hidden when the sidebar is collapsed and on mobile width. No double-click reset. Nothing in theme.css touches it. Findability: poor (a faint 2 px bar on a #c0c0c0 panel).

## Floors (m4.py, plain select/card inside the real theme, 1100 px, both open)
| left/right | centre px | centre % | overflow |
| 340/340 | 420 | 38 | none |
| 220/200 | 680 | 62 | none, inputs follow the panel (189 wide at 190) |
| 190/170 | 740 | 67 | none in the test content |
| 150/150 | 800 | 73 | none in the test content (150 = bslib's own minimum) |
Not run on the real app (load, and the real left panel has the filter rows, accordions, nav pills). 2/3 at 1100 needs floors near 190/170 (about 17 % each).
