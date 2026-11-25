# Review of fix 83a2e246 (task/session-import)
Verdict: MERGE AFTER A NAMED FIX (one HIGH residual: two stored folders with one look on screen).
See the handback text for the full evidence; summary here.
- HIGH: session_handlers.py:371-427 loops over every listed session; two stored folders whose keys give one id part
  (e.g. 'a:b' and 'a_b', ran: both list, both give 'a_b') read the SAME input id, and _is_new_click (line 75) is keyed by
  session key, so one Delete click deletes BOTH sessions (Restore runs both, last wins). The refusal exists only in
  import_session_zip (session_manager.py:618-624). Not covered for folders already in the store or put there by hand/earlier import.
- Fix: make the panel refuse to draw/act on a colliding group (plain message naming the folders, no Restore/Delete for them), or
  make the id unique from the listing (e.g. index/hash of the key, looked up from the list), plus a test with two such folders.
- Everything else passed (see handback).
