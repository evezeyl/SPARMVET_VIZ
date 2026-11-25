# Fix 2: two stored sessions never share a button
Commit e27d6228 on task/session-import (worktree session-import). git status --short: clean.

Done
- session_manager.py: new pure `session_input_id_parts(listed_keys)` (key -> id part) and `session_id_collisions(listed_keys)`. Unique safe form stays as before; a shared safe form gets `_` + first 8 hex of sha256 of the exact key. @deps updated.
- session_handlers.py: render and the effect `_handle_session_actions` both build the ids from that mapping of the same listing (restore, delete, label). Lookup is by mapping, never by reversing text.
- Import refusal kept. New: the `session_key` inside every `t3_*.json` must equal the folder, else whole zip refused before any writing, naming the file.

What the user sees with a colliding pair (PROVISIONAL wording)
- Above the cards (red small text): "Some stored session folders have names that differ only in a character the screen cannot tell apart: 'aa:bb' and 'aa_bb'. Each of their cards shows the exact folder name; a button acts only on the folder named on its own card."
- On each card of the pair: "Folder: <exact folder name>". Cards without a collision show nothing extra.
- t3 refusal text: same form as the assembly one: "The zip was refused and nothing was written: the session folder is named '...' but the session_key inside <file> is '...'. The two must be the same."

Tests
- New app/tests/test_session_id_collisions.py: 10 tests (mapping: unique, two, three, kept copy, order; real effect delete of one leaves the other; real effect restore restores only the clicked one; panel with pair: two ids + notice, panel without pair: no notice; crafted t3 zip refused, nothing written).
- Browser: new second test in app/tests/test_shiny_session_keep_both.py (two look-alike folders, click Delete on one, other folder remains on disk and its group is still listed).
- Headless run: copy_panel, import_safety, session_manager, clicks_once, errors_visible, id_collisions = 117 passed. Browser (qa): keep_both 2 passed (twice in a row at the end), session_restore 1 passed.
- Fail-once: mapping returning plain safe form always: 5 of 10 new headless tests failed (two colliding, three colliding, delete, restore, panel); browser test failed at the id assertion. Restored from a backup copy (no git checkout/stash).

Not checked / notes
- The t3 refusal test (d) was not broken once by mutation (it asserts a message and an untouched store; the check is new code, no earlier test could pass it).
- Browser test 1 (existing, keep both) failed intermittently twice during my runs (a notice was not seen in 20 s; a failed run left stray folders in tmp/UI_TEST that I removed). It passed on re-runs. Cause not found; I did not check it on the previous commit.
- After a delete the panel is redrawn with groups closed and the other card was not in the DOM at once, so the browser test checks the group heading and the folder on disk, not the other card's button.
- Folder name inside the key (ghost `session_key`) differing from the folder name was not examined; delete uses the listed key as the folder name as before.
- Hash collision of 8 hex between two keys of one group is not handled (about 1 in 4 billion).
