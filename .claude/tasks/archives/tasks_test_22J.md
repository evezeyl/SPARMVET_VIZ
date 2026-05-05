# Phase 22-J Live-UI Test Checklist

> **DEPRECATED 2026-05-02** — Superseded by [tasks_test_ui_current.md](tasks_test_ui_current.md).
> This file covered Phase 22-J per-plot audit scoping at `94bb917`. The app has since
> been through Phase 23-A/B, Phase 24 (home_theater decomposition), and Phase 25
> (left sidebar restructure + persona flag gating). The scenarios below are stale.
> Kept for historical reference only.

**Owner:** @evezeyl
---> See my comments if necessary EVE_WORK_daily/2024-04-30/UI_user_test.md
and comments bellow in -> [ here ]

**Branch / commit baseline:** `dev` @ `94bb917`
**Implementation phase:** 22-J — Per-Plot Audit Scoping & Join-Key Propagation (ADR-049, §12g)
**Purpose:** Walk every behavioural promise made in the design conversation against the running app. Each section is a discrete scenario; check the boxes as you go. If anything fails, note the symptom — that's the bug list for the next pass.

---

## 0. Pre-flight

Before starting, make sure you're running the latest code:

- [x] `git status` shows clean working tree (or only your scratch files).
- [x] `git log --oneline -3` shows `94bb917 feat(22-J): per-plot T3 audit scoping & join-key propagation` at top.
- [x] App starts: `./.venv/bin/python app/src/main.py` — UI loads without console errors. --->  [Warning: Extensibility clash. Action 'sort' is already registered and will be overwritten.- Sent to agent so ok]
- [x] Persona is one of the advanced ones (`pipeline-exploration-advanced`, `project-independent`, or `developer`). Otherwise the right sidebar is hidden.
- [x] Open at least two plots in different sub-tabs so you can test propagation. A QC plot + an analysis plot is the cleanest combination. [Filtering isolates is good -> is propagated to other plot when Not primary key - Filtering of primary key should be allowed with a warning, but NOT the removal of the primary key Column - Thus cannot verify propagation to the entiere set of data T3/plots ]

---

## 1. Per-plot stack visibility — basic

The right-sidebar audit panel must show only the active plot's stack.

- [x] Switch to **T3 ("My adjustments")** mode.
- [x] Right sidebar shows `My Adjustments — <plot_id>` header (with the *currently active* plot's id).
- [x] If no audit nodes yet: shows "No T3 adjustments for <plot> yet."
- [x] Build a filter row on Plot A (no key column). Click `➜ Audit (1)` → modal opens.
- [x] Pick **"This plot only"** in the modal → click `Add to audit pipeline`.
- [x] Right sidebar now shows the new pending node, with a yellow reason input.
- [x] Switch to Plot B (different sub-tab) → right sidebar header changes to Plot B's id, and the pending node from Plot A is **gone** (it was scoped to A only).
- [x] Switch back to Plot A → the pending node reappears.

**If any of the above fails:** the per-plot scope key isn't being plumbed through correctly. Check `home_state.active_plot_subtab` in the handler (`_track_active_home_subtab` in `home_theater.py`).


## 2. Filter authoring on a non-key column (Case C from user guide)

This is the simplest path: filter by value, no PK touched.

- [x] In T3 mode, build a filter on a **non-key column** — e.g. on a similarity / value column, `value > 90`. ---> [See my notes : Render error : cannot compare string with numeric type f64 (so we have a problem of types casting / transformation that is either not done correctly in manifest or that should be tackled byt the code ) - But works with string column]
- [x] Click `+ Add` to stage the row, then click `➜ Audit (1)`.(tested with other filters worked)
- [x] Modal opens. The header reads "Add 1 filter/exclusion(s) — choose scope". The summary line shows your column name.
- [ ] **NO** ⚠️ Primary-key warning banner inside the modal (since the column isn't a join key).See comments
- x] Pick **"This plot only"** → click confirm.
- [x] Pending node appears in right sidebar. The node is a `filter_row` (icon: 🔍 Row Filter, NOT 🚫 Exclusion). -> see comments
- [x] Type a reason in the yellow box.
- [x] Bottom **Apply** button transitions from "Apply ⛔" to clickable "Apply".
- [x] Click Apply. Notification: "✅ T3 recipe applied — N node(s) across 1 plot stack(s)."
- [x] The plot data (and the data preview below) reflects the filter.
- [x] Switch to a different plot → that plot is **unaffected** (per-plot scoping holds).

---> [This is good - But we will need to developp a test manifest for the whole UI and a procedure associated to the testing of the UI - So we know what to expect with the data - minimal dataset]
---

## 3. Filter authoring on a primary-key column → silent conversion (Case B from user guide)

Targeting `sample_id` (or any join key) should silently convert to `exclusion_row` and warn.

- [x] In T3 mode, build a filter where **column = sample_id** and value = some sample (e.g. `eq` `S2`). [Filtering with primary key column should be allowed, but with a warning that it is a join key, BUT it should not be allowed to drop the primary key column - Warnings should stay]]
- [x] Click `+ Add` then `➜ Audit (1)`.
- [x] Modal opens — this time the modal header includes a yellow ⚠️ banner: *"One or more nodes target a join key…"* 
- [x] Pick **"All plots"**.
- [x] After confirm: pending nodes appear in the right sidebar. The node icon is **🚫 Exclusion** (NOT 🔍 Row Filter — silent conversion).
- [x] Pending node shows the ⚠️ Primary key — Primary ID/Key alignment banner.
- [ ] Pending node shows an "Applied to N plots" badge (N = total number of plots).
- [x] Switch to another plot → the same pending node appears in that plot's panel too (with the same id; same ⚠️ banner).
- [x] Type a reason on the node in *one* plot's panel.
- [x] Switch to another plot — the reason is NOT yet visible in the input (the inputs are independent per render), BUT the bottom Apply button on this plot is now **enabled** (because the reason fan-out happens at gatekeeper time).
- [x]Click Apply. Both copies commit; notification confirms count.
- [x] In every plot, sample S2 should be gone from the data preview and from the plot.

**If the icon is 🔍 instead of 🚫:** silent conversion didn't happen — `_filter_apply` isn't seeing `column ∈ home_state.primary_keys`. Check that `_sync_session_provenance` populated `primary_keys` (open browser console / check assembly logs on app start).

---

## 4. Case A — exclude S2 everywhere except the QC justification plot

This is the killer case: keep the bad sample visible on the QC plot for the report.

- [x] Identify your "QC plot" (the one you'd cite as evidence S2 was bad).
- [x] Switch to T3 mode. From any plot, build a filter `sample_id eq S3` (use a different sample so you don't conflict with section 3).
- [x] Click `+ Add` then `➜ Audit (1)`.
- [x] In the modal, pick **"All plots except…"**.
- [x] In the multiselect, pick the QC plot.
- [x] Click confirm. Notification reports number of pending nodes added.
- [x] Pending nodes appear in every plot's panel **except** the QC plot.
- [x] Switch to the QC plot → no pending node for S3 appears there.
- [x] Type a reason on any one pending node.
- [x] Click Apply.
- [x] In the QC plot, sample S3 is **still visible** in the data and the rendered plot.
- [x] In every other plot, S3 is gone.

---

## 5. Drop column on a join key → BLOCKED

- [x]In T3 mode, in the data preview column selector, **deselect** `sample_id` (or any other join key).
- [x] Click `➜ Audit drops (N)`.
- [x] Notification: red error — *"Cannot drop join key column(s): sample_---id. Use a row filter or row exclusion instead."*
- [x] No audit node was added.
- [x] Re-select sample_id; the count badge resets.

---

## 6. Drop column on a non-key column

- [x] Pick a column that is **not** a join key — e.g. `notes`, or any genuinely auxiliary column.
- [x] Deselect it; the `➜ Audit drops (1)` button activates.
- [x] Click → propagation modal opens. Header: "Drop 1 column(s) — choose scope".
- [x] No PK warning banner inside the modal.
- [x] Pick "This plot only" → confirm.
- [x] Pending `drop_column` node (icon: ✂️) appears in the right sidebar.
- [x] Type a reason → click Apply.
- [x] The dropped column disappears from the data preview AND from the column selector's choices (committed drops are excluded from the `cols` list — you can't re-drop).
- [x] Switch to another plot → that plot still has the column.

---

## 7. Schema-skip propagation (D9)

If a propagated node targets a column that some plots don't have, those plots are skipped.

- [x] Pick a column that exists in some plots but not all (e.g. a metadata-only column that appears in `plot_metadata_summary` but not in a long-format AMR plot).
- [x] Author a filter on that column → propagate "All plots".
- [x] After confirm, the notification should say something like *"Skipped (column not in plot data): plot_amr_heatmap: <col>"* — listing which plots were skipped.
- [x] Verify by switching to a skipped plot — no pending node for it.
- [x] Verify by switching to a plot that *did* receive the node — the pending node appears.z

---

## 8. Linked-id deletion

A propagated node lives in N plots' panels but is one decision. Deleting any copy deletes all. -> [I think this is the right choice, however - a message saying that it will be deleted in all plots might need to be added]

- [x     ] Use the Case A or Case B node from above (the one propagated to multiple plots).
- [x] Make sure it's committed (clicked Apply).
- [x] Switch to plot X → click the 🗑 next to the audit node.
- [x] Notification: *"🗑 1 audit decision(s) deleted (N copy/copies across plots)."*
- [x] Switch to plot Y → the node is gone there too.
- [x] Switch to plot Z → also gone.
- [x] The data is no longer filtered (sample S2 / S3 reappears) on every plot.

---

## 9. Reason input stability (regression test for §14 R4)

Typing in a reason input must not destroy the input mid-character.

- [x] Author any T3 audit node so a yellow reason input is visible.
- [ ] Type a long reason slowly, pausing between characters. Cursor should stay where you left it. No focus loss.
- [ ] The Apply button label flips between "Apply ⛔" and "Apply" as you type / clear the box.

**If the input keeps clearing or losing focus:** R4 is broken somewhere — likely a render that mounts the input is also reading it.

---

## 10. Column selector stability (also §14 R4)

- [ ] In T3 mode, deselect a non-key column.
- [ ] The deselection persists; the column does NOT snap back.
- [ ] The `➜ Audit drops (N)` button updates its count live.
- [ ] Selecting the column again restores it; count goes to 0; button greys out.

---

## 11. Tier toggle interaction

- [ ] In T3 with audit nodes committed, switch to **T2** mode.
- [ ] Left-panel "Apply" button label is now blue **"Apply (N)"** (NOT orange "➜ Audit") — T2 commits transient `applied_filters`, not audit nodes.
- [ ] Right-sidebar audit panel still shows your committed T3 nodes (read-only behavior at this tier — you should not see propagation modals trigger from T2).
- [ ] Switch back to T3 — Apply button is orange "➜ Audit (N)" again.

---

## 12. Ghost save & restore

- [ ] After committing several T3 nodes (across multiple plots), close the app.
- [ ] Re-open the app on the same project / same data.
- [ ] Restore the most-recent session ghost via the left-sidebar System Tools panel (Session Management).
- [ ] All your audit nodes reappear in their per-plot panels.
- [ ] Propagated nodes still show their "Applied to N plots" badge.
- [ ] PK warning banner persists.

---

## 13. Legacy ghost backward-compat (D10)

Only relevant if you have ghost files saved before commit `94bb917`.

- [ ] If you have a pre-22-J `t3_*.json` in `tmp/UI_TEST/user/_sessions/` or your real session folder: try to restore it.
- [ ] Notification appears: *"✅ Session restored… (N orphaned legacy node(s) — see audit panel)"*.
- [ ] Right sidebar shows an "Orphaned" section listing the legacy nodes.
- [ ] You can 🗑 delete them; no other action is allowed on them (they have no plot to apply to).

If you don't have any legacy ghosts: skip this section. It's mainly for the design's documentation completeness.

---

## 14. Export Methods generation

The exported audit report is the proof artifact. Verify the PK marker shows up.

- [ ] After committing a Case A/B node (PK-affected), trigger **Export Audit Report** from the left sidebar System Tools.
- [ ] Open the exported HTML.
- [ ] In the Methods section, the PK-affected line begins with **⚠️ [Primary key affected]**.
- [ ] If the node was propagated to multiple plots, the line lists every target plot in one entry (NOT N separate entries — they're deduplicated by id).
- [ ] If you authored case A: the QC plot is NOT in that list (since it was excluded from propagation).

---

## 15. Edge cases worth a quick poke

- [ ] Click "Cancel" in the propagation modal → no node added, no pending state left behind.
- [ ] Click `➜ Audit (N)` with N=0 (no staged rows) → notification asks you to add rows first.
- [ ] Author 2 filters on the same column with different values → both become separate nodes, propagate independently.
- [ ] Aesthetic adjustments (color/shape/fill) — currently no UI authoring path exists (deferred 22-J-10), so nothing to test here.

---

## What to do if something breaks

If a checkbox above fails:

1. Note the section number and what specifically went wrong (what did you see vs. what was expected).
2. If the app is in a wedged state, take a screenshot of the right sidebar and the browser console.
3. Don't try to "fix" it — flag it back, and we'll triage in order.

The deferred / known issues:
- **22-J-10 aesthetic propagation UI** — not implemented. No tests in §15 for that.
- **Filter operator/value edge cases** flagged in 22-I — those existed before this phase; some may surface again here. Note any but don't conflate them with 22-J failures unless they're new symptoms.

When all critical sections (1–9, 11, 12, 14) pass: the phase is verified. Sections 7, 13, 15 are nice-to-have.

---

**Reference docs:**
- `.claude/rules/ui_implementation_contract.md` §12g — full technical spec
- `docs/user_guide/audit_pipeline.qmd` — user-facing walkthrough with the three use cases
- `.claude/knowledge/architecture_decisions.md` ADR-049 — design rationale
- `.claude/tasks/tasks.md` Phase 22-J — sub-task breakdown + decision matrix
