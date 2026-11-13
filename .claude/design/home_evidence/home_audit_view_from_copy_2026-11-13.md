# How audit mode shows data and plots from a copy of the recipe (investigation, 2026-11-13)

**Status:** reasoned from the code read today (counts verified) and from the forked-recipe test of 2026-11-12; **Source of truth DECIDED by Eve 2026-11-13, with the invariant that original steps cannot be modified in the copy** (the copy minus its marked steps equals the original; tested as a property). Eve's point: the audit steps are registered in a **copy of the recipe**; the rest is a consequence, so in audit the data and the plots that are shown come from that copy.

## 1. The model
- **Exploration** reads the original recipe and the original stored tables. Nothing changes.
- **Audit mode** reads the **audit recipe** (the copy) and a **second set of stored tables** (a second orchestrator on the copy, in its own cache folder). The plots are drawn by the same visualisation factory from the copy's plot specs (copied unchanged) and the T3 data of the copy.
- **Compare** shows the original Result (original recipe) beside the audited one (copy).
- **Source of truth (proposal):** the audit steps live **in the copy**, each marked as an audit step (an origin marker with its id, reason, initials and date; its name is set with the step compiler and the recipe format, `recipe_format_spec.md` 6.6, OPEN). The copy is then one self-contained, re-runnable artifact: undo, remove and revert edit the copy; the export is the copy; a session restores the copy. Beside it, an **append-only event log** keeps the history (created, removed, reverted, acknowledged warnings); a test checks that replaying the log gives the copy. The hash parts `a` are computed from the marked steps' operations only (never reason, initials, date).
- **Where the copy lives:** a real file in the session folder (`_sessions/<session key>/audit/<recipe id>.yaml`), the resolved single-file recipe (all `!include` merged, as `build_mode2_recipe` does today), with a header that says which original it was made from (the original's file-set hash) and the recipe format version. The engine reads files, so it runs unchanged.

## 2. What was checked in the code (verified)
- HOME reads the recipe through **one** reactive value, `active_cfg` (`app/src/server.py`), used about 35 times: 18 in `home_theater.py`, 7 in `server.py`, 5 in `export_handlers.py`, 5 in `audit_stack.py`. The data is read through `orchestrator.` about 12 times (6 in `home_theater.py`, 6 in `export_handlers.py`).
- So the change is **one new pair of reactive values**: a *view recipe* and a *view orchestrator*, which are the original ones in Exploration and the copy's in audit mode, and a migration of those call sites to them. The plot drawing call sites (`viz_factory.render`, 4) already receive the recipe config, so they work with the copy's.
- A second orchestrator on a generated recipe works with the unmodified engine (the forked-recipe test, 2026-11-12: 126 rows and 41 samples for the changed table, the other table untouched).

## 3. What has to be designed (decisions and edge cases)
| Case | Proposal |
|---|---|
| Apply, undo, remove, revert | the copy is rewritten from its marked steps; the keys decide which nodes are recomputed; the copy file is deterministic (same steps, same bytes, same hash) |
| The original recipe or the data changes while audit is open | the copy's origin hash no longer matches: a notice; the export is refused (the key check); the user chooses "re-base": the marked steps are written again into the new original, and each step gets a status (applied, not concerned, broken) |
| An older or newer app opens a copy or a bundle | the header carries the recipe format version; an unknown key or action is a failure (fail instead of warn), with the replacement named; the import blocks with the reason |
| Two sessions on one recipe | each session has its own copy and its own audit cache; the original tables are shared and read-only |
| Many steps on a big recipe | the copy is small (steps only); recomputation is per node by key; the cost is the audit nodes, not the whole recipe |
| What is shown in the badge and the popup | "audit view of <recipe id>: N steps, based on original <hash>" so the user always knows which recipe the data comes from |

## 4. Risks
The migration of about 35 call sites to the view recipe is mechanical but easy to get partly wrong (a panel that still reads the original in audit mode would show a plot that is not the audited one): the test is a property, "in audit mode no handler reads the original recipe", checked by a test that scans for direct uses of `active_cfg` outside the view calculation. The marker on audit steps must be accepted by the recipe checker only in an audit copy.
