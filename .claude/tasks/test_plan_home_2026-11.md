# SPARMVET_VIZ — HOME Test Plan (Phase 1 of the split)

**Owner:** @evezeyl (tester) · @dasharch (fixer)
**Split from:** [`test_plan_2026-06.md`](test_plan_2026-06.md) on 2026-11-08 — Eve: "last time it went
in all directions," testing should follow what you actually do when you launch the app, not jump
between spaces. HOME is what you land on, so HOME is tested alone, start to finish, before
anything else.
**Scope:** HOME only — every item below is observed from inside HOME. Nothing from TEST_LAB,
BLUEPRINT, GALLERY, cross-space handoffs, or the 8-config-file gating sweep is in this file; those
are **Phase 2**, picked up in `test_plan_2026-06.md` once this file is done.
**Config file for this round:** `developer.yaml` — full functionality, one launch, no switching.
Config-file *limitations* (what's absent in `pipeline-static` etc.) are deliberately Phase 2: you
can't tell whether something is missing-by-design or actually broken until you've seen it working
at full capability first.
**Protocol:** same as the master file — status markers, how to write a finding, the round-trip.
See [`test_plan_2026-06.md` §0](test_plan_2026-06.md#0-how-this-document-works-read-first--this-is-the-efficiency-engine)
for the full legend; the one-line version: flip `[ ]` to `[x]`/`[!]`/`[~]`/`[?]`/`[b]` as you go,
add a `> EVE:` note on anything not a plain pass.

**This round is live-guided**, not async: say "go" and work through the items in order; report
pass/fail/note in chat as you hit each one and I'll keep the file in sync, rather than you
hand-editing markdown while also looking at the browser. Use whichever is easier in the moment.

---

## Round log (heartbeat — I maintain this)

**Round 2 pre-pass, 2026-11-10:** Eve's own first manual click-through (not yet logged item by
item here) surfaced three real gaps across Home/Blueprint/Export that code reading alone had not
caught — filed as issues #53/#54/#55, all fixed same session (see `tasks.md` "Manual-testing
findings, 2026-11-10" for the full writeup). HOM-59 added (reproducibility bundle import had no
test item at all until now). BLU-32/BLU-33/LAB-29 added to `test_plan_2026-06.md` for the Phase 2
(Blueprint/Test Lab) retest, since this file is HOME-only. Also fixed, found while answering
Eve's question about the Validate button in Blueprint: it never called the real engine load path
(`validate_data_analysis_recipe`), so it could PASS a recipe that would be rejected at real load
time (`id:` != file name, flat wrangling list) — see BLU-33. Headless suite (1589) and the full
Playwright gate re-run clean after all four fixes.


**Round 1, 2026-11-08:** PRE-01/02/03/05, HOM-07 passed. HOM-08 is `[~]` (tier resets to Result
on Home→Gallery→Home; plot sub-tab itself is restored correctly). Fixed live: Alerts moved to the
left sidebar (same reachability fix as Processing Issues, F-26), 28 stale test sessions cleared.
Built live, not originally part of this round: ADR-096 — the app now ships and links to the full
Quarto book (`? Help` / `📖 Full Documentation` / `GitHub`, all three in the left Navigation stack,
HOM-56). Found and logged, not fixed yet: HOM-53 (session list doesn't refresh after delete),
HOM-54 (want bulk session delete), HOM-55 (`? Help` modal content stale across all 4 workspaces —
`gallery.md` actively describes a removed feature), `CONFIG-PIPELINE-RENAME-1` in `tasks.md` (the
`pipeline-*` app features names collide with `CTX-1`'s "Analysis pipeline," same shape as the
Processing Issues rename — scoped to Phase 2, not fixed mid-HOME-testing). A reported "duplicate
Shiny ID" error during this round was a stale-server artifact (`--reload` doesn't watch YAML),
not a real regression — confirmed via the fresh-process `test_every_app_features_starts.py` suite
passing clean both before and after.

**Hanging-fruit fix pass, 2026-11-08:** HOM-53 and HOM-54 fixed and mutation-tested (see their
entries above). Two subagents were spawned to parallelize this pass alongside documentation work;
both turned out to be working from stale git worktrees (one 356 commits behind `origin/dev`, one
~6 months stale) — stopped before merging anything from them; HOM-53/HOM-54 were implemented
directly against the real repo instead. One subagent's otherwise-good `app/src/help/*.md` rewrite
(committed as `1964c9c`) needed one correction for the same reason (a stale "Clone to Sandbox"
reference to a feature ADR-093 already removed).

**Diagram re-draw, 2026-11-08:** the 4 remaining HOME/BLUEPRINT diagrams redrawn in plain
language via the StarUML bridge — SEQ-OPEN and SEQ-AUDIT (lifelines/messages renamed off
code/function names, type suffixes suppressed, current "Raw/Result/My view" vocabulary per
ADR-085/086), UI-BLUEPRINT (stray flowchart shape and an "Undo" box describing a button that
doesn't actually exist on screen both removed; all 19 panel labels reworded to plain language,
no more L1–L4 layer tags), UC-BLUEPRINT (added the missing "Branch the lineage at a node" use
case, ADR-082 §Q3 — UI-BLUEPRINT already showed the Branch designer panel but the use-case
diagram didn't have it). All 29 diagrams re-exported to `docs/UML/diagrams/`; the 3 Quarto pages
that embed these 4 re-rendered clean (`quarto render --no-execute`, images resolve, no
warnings — also fixed a pre-existing unrelated orphan `:::` in `data_lifecycle_theater.qmd` hit
during the render check); `audit_uml_model.py` passes with 0 violations.

## 0. Launch

```bash
cd /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/developer.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
```
Open <http://127.0.0.1:8000>. Chrome, dev console open, network cache disabled (per your usual setup).
`--reload` restarts the server on code edits during a fix round.

- [x] PRE-01 — App boots clean. Eve, 2026-11-08: many `[ConfigManager] Auto-unnesting redundant key...` lines but no traceback — confirmed expected/benign (documented behaviour in `config_loader.py`, not an error). Original console-error finding closed. **Follow-up fixed, 2026-11-08** ([#37](https://github.com/evezeyl/SPARMVET_VIZ/issues/37)): edited first-party/vendored scripts weren't picked up on reload (browser cache, URL never changed) — fixed with mtime-based cache-busting on every script/link tag served from `app/src/www/`.
- [x] PRE-02 — Browser loads at :8000 with no red error banner on first paint. Eve, 2026-11-08: ok.
- [x] PRE-03 — Default data analysis recipe **ST22 Dummy Dataset** (`1_test_data_ST22_dummy`) loads with its tabs. Eve, 2026-11-08: yes.
- [x] PRE-05 — Switch data analysis recipe → tabs change, plots reload, no traceback. Eve, 2026-11-08: seems ok.

---

## 1. Tabs, plots, preview (core)

- [x] HOM-01 — Group tabs = data analysis recipe `analysis_groups` (Quality Control · Curiosity · Results · Cat 🐱). No hardcoded tabs.
  > EVE: ok - tested by changing data analysis recipe and observing changes in analyses groups
- [x] HOM-02 — Each tab's plots render as static images; multi-plot groups expose plot **sub-tabs**.
  > EVE: ok
- [x] HOM-03 — **Data Preview** accordion below the plot shows ~100 rows of the active plot's dataset; updates on sub-tab switch.
  > EVE: ok
- [x] HOM-50 — The AMR heatmap (Results, `amr_heatmap`) draws, coloured by `predicted_phenotype`. Eve 2026-11-05. [#13](https://github.com/evezeyl/SPARMVET_VIZ/issues/13). *(Automated: all plots of the test data analysis recipes render, `app/tests/test_render_every_plot.py`.)*
- [x] HOM-04 — (superseded, 2026-11-05) The old header strip (dataset label + tier radios) no longer exists: it is now the two-row strip of HOM-45 (ADR-086). The follow-ups it raised are HOM-40 to HOM-43, all done. → [20260810_testing_part1.md#hom-04-follow-ups](20260810_testing_part1.md#hom-04-follow-ups-tier-toggle--audit-scope-2026-08-10).
- [x] HOM-37 — "All rows" toggle in Data Preview blanks the table entirely, no error shown. → [20260810_testing_part1.md#hom-37](20260810_testing_part1.md#hom-37--all-rows-toggle-blanks-the-data-preview-table-bug) — needs a terminal traceback to root-cause, see note. [#1](https://github.com/evezeyl/SPARMVET_VIZ/issues/1)
> EVE: this was an error - all rows are showing correctly when toogle activated (can be delay if many rows). BUT the message is not clear - we need to know if it shows only a portion of the data or all the data. Would be nice to indicate data dimension of the full dataset that is shown (and when preview only - not all rows to know that is max first 100)
  > Merged into HOM-39 — same underlying ask (row-count clarity).
- [x] HOM-38 — The word "Plot" in the plot panel header is blanked (redundant). Retested by Eve 2026-11-05 (open and collapse, single and Compare). [#16](https://github.com/evezeyl/SPARMVET_VIZ/issues/16) → [20260810_testing_part1.md#hom-38](20260810_testing_part1.md#hom-38--redundant-plot-accordion-title-above-each-plot)
- [x] HOM-39 — Data Preview doesn't make the 100-row cap clear to the user; the total row count of the underlying table isn't shown anywhere, and (per HOM-37) it should also be clear whether "All rows" is showing a portion or everything. → [20260810_testing_part1.md#hom-39](20260810_testing_part1.md#hom-39--data-preview-100-row-cap-not-communicated) [#1](https://github.com/evezeyl/SPARMVET_VIZ/issues/1)
- [x] HOM-41 — **FIXED**: committed T3 audit filters/column-drops no longer leak into T1/T2. → [20260810_testing_part1.md#hom-41](20260810_testing_part1.md#hom-41--t3-audit-nodes-leak-into-t1t2-reference-views-confirmed-bug)
- [x] HOM-40 — A "Viewing: Raw / Result / My view" badge shows above each plot and in the Data Preview header, with "T2=T1" and "T3=T2" notes (the badge is not in the plot image, so not exported). Retested by Eve 2026-11-05. [#17](https://github.com/evezeyl/SPARMVET_VIZ/issues/17) → [20260810_testing_part1.md#hom-40](20260810_testing_part1.md#hom-40--no-explicit-viewing-tier-x-indicator)
- [x] HOM-42 — **DECIDED**: covered by the "Compare" choice of **Plot to show** (T2 on the left, My view on the right), ADR-086, [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3). A one-line My view summary under the plot may follow later. — RETEST ↻
- [x] HOM-43 — **FIXED**: Apply (exploration, every tier) and Send to Audit (T3-only, permanent) are now two distinct buttons instead of one that changed meaning by tier. → [20260810_testing_part1.md#hom-43](20260810_testing_part1.md#hom-43--t3-mode-has-no-exploration-only-filter-path) — RETEST ↻

## 2. Header strip — Data to show / Plot to show

- [x] HOM-05 — **Data to show** Raw → Result on `year_distribution` (AMR and Virulence group): the data preview shows all years on Raw and only 2023–2025 on Result. The plot does not change when you switch Raw/Result (plots never show T1, ADR-086). [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [x] HOM-06 — My view (advanced+): Apply always explores; **"Send to Audit" appears when either "Plot to show" or "Data to show" is on My view** (and `t3_sandbox_enabled`); right sidebar Pipeline Audit shows Tier 2 (inherited) + Tier 3 (my adjustments) once something is committed. See HOM-43, ADR-085/086. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [x] HOM-07 — Changing **Data to show** (T1→My view→T1) keeps the active plot sub-tab. Eve, 2026-11-08: ok.
- [~] HOM-08 — Home→Gallery→Home **restores** the previously active group tab + sub-tab + tier. Eve, 2026-11-08: the plot sub-tab is restored correctly, but the tier/header-strip choice resets to "Result" instead of staying on whatever it was before leaving. Eve: annoying, not critical. **FIXED, 2026-11-08**: `dynamic_tabs` rebuilt the header strip with a hardcoded `selected="T2"` on every re-render (any trigger, not just a tier flip — a workspace switch rebuilds it too), discarding the real selection. Fixed with an isolated read of the current input value, same pattern as the existing active-tab restoration. New test `TestTierPersistence::test_tier_survives_a_workspace_switch`, mutation-tested (reverted the fix, confirmed the test fails; restored, confirmed it passes). — RETEST ↻
- [x] HOM-44 — On `year_distribution` (data analysis recipe "1_test_data_ST22_dummy", AMR and Virulence group), the Year axis renders discrete on T2 but continuous on T3/My view — same data, should look the same. [#36](https://github.com/evezeyl/SPARMVET_VIZ/issues/36). **FIXED, 2026-11-09**: not a filter/dtype issue — `scale_x_continuous(breaks_integer: true)` delegated to `MaxNLocator(integer=True)`, which only *prefers* integer ticks: on a narrow span (after the filter narrows the year range) it falls back to fractional ticks (`2023.6, 2023.7, ...`) because no "nice" step fits. `_integer_breaks()` (`libs/viz_factory/src/viz_factory/scales/core.py`) now lists every whole integer directly for small spans, delegating to the locator only for genuinely wide ranges. New `test_integer_breaks.py` (5 cases) + verified live against the actual plot spec with a `year >= 2024` filter (tick label `'2024'`, was fractional before). — RETEST ↻
- [x] HOM-45 **NEW** — Header strip (ADR-086): two labelled rows "Plot to show" (Result / My view / Compare) and "Data to show" (Raw / Result / My view), defaults both Result. Plot choice affects only plots, data choice only the data preview/table. Compare absent when `comparison_mode_enabled` is false. Strip absent when `interactivity_enabled` is false. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻

## 3. Filters (T1/T2)

- [~] HOM-09 — String column: operators are `= equals` / `≠ not equal` / `∈ any of` / `∉ none of` (no `between`), each with words. Add row → staged; Apply → preview + plot update **on Raw, Result and My view** (badge "N preview filter(s) on, not saved" on Raw/Result); Reset clears. Eve's first pass 2026-11-11: filter did nothing on Result → model changed, ADR-087, [#56](https://github.com/evezeyl/SPARMVET_VIZ/issues/56), labels/text size [#57](https://github.com/evezeyl/SPARMVET_VIZ/issues/57). Fixed on dev. Retest 2026-11-11: filters, Compare, badge, labels OK; trash icon now also unapplies (no second Apply); column selector is table-only by design, discussion open. ↻
- [ ] HOM-10 — Numeric column: operators include `↔ between` → two lo/hi inputs; inclusivity radios read `≤ inclusive` / `< exclusive` (single symbol).
- [ ] HOM-11 — Int column shows integer default (`2022` not `2022.0`), step = 1.
- [ ] HOM-12 — Multiple staged rows AND together; removing one updates the count and result.
- [ ] HOM-13 `[?]` — **(carried, old §5b)** Filter selectize choices are **not** refreshed after Apply (excluded values still show in the picker). Decision: refresh choices from filtered data (cleaner) vs keep all so you can add filters back without Reset. Your call.

## 4. T3 audit — the reproducibility core

- [ ] HOM-14 — Build a filter on a non-key column → `➜ Audit (1)` → **propagation modal** ("choose scope", no PK warning). Pick "This plot only" → pending yellow node with required reason input.
- [ ] HOM-15 — Apply is **blocked** until the reason is non-empty; once filled, Apply commits; notification confirms; plot + preview reflect it; **other sub-tabs unaffected** (per-plot scoping).
- [ ] HOM-16 — Filter on a **primary-key** column → modal shows ⚠️ PK warning; node renders with the PK-warning banner; operator is preserved verbatim (no silent flip to exclusion).
- [ ] HOM-17 — "All plots" scope → node copied to every plot's stack (same id); "All plots except…" → multiselect excludes chosen plots.
- [ ] HOM-18 — Drop a non-key column via the Data-Preview column selector → `➜ Audit drops (1)` → drop_column node; reason required; applies; column gone for this plot only.
- [ ] HOM-19 — Attempt to drop a **join-key** column → blocked with a red "cannot drop join key" notification; no node added.
- [ ] HOM-20 — Delete a committed node (🗑) → removed across all plots it was propagated to; data reverts.
- [ ] HOM-21 `[~]` — **(carried, old §10)** Primary-key concept is unfamiliar to non-CS users. Add a short, plain-language hover/tooltip when filtering/removing a PK ("this is the column that links your tables; removing rows here changes what appears everywhere"). Confirm whether any such hint exists today; if not, mark `[~]` for me to add. Longer doc-page welcome too.

## 5. Palette / plot-config cascade / Apply UX

- [ ] HOM-22 **NEW** — If a data analysis recipe declares `plot_defaults.palette` or a per-plot `palette:`, plots render in that palette. Switching data analysis recipes changes palette accordingly.
- [b] HOM-23 `[b]` **(blocked since 2026-11-05: the Plot Style panel is not shown in HOME, issue [#15](https://github.com/evezeyl/SPARMVET_VIZ/issues/15); no authoring path)** **NEW** — `aesthetic_override` (T3 plot colour/fill/alpha/shape), **if an authoring path exists**, actually changes the rendered plot (not just recorded). If there's no UI to author it yet, mark `[b]` (VIZFAC-T3-OVERRIDE-1 may still be pending).
- [b] HOM-47 — **Plot Style panel: decided 2026-11-05.** The panel (right sidebar of HOME, added 2026-05-11, commit fa5a78d) is the authoring UI of the T3 `aesthetic_override` (ADR-082). Using it broke the plot, and letting users change in HOME what the data analysis recipe defines is too much for now. **Decision (Eve):** the panel is **not shown in HOME**; its code is kept, unused, with a pointer comment at the mount point (`home_theater.py`); BLUEPRINT and ADR-082 are unchanged. It stays an **eventual enhancement** ([#15](https://github.com/evezeyl/SPARMVET_VIZ/issues/15), task UX-PLOTSTYLE-1 deferred), when we will also find why it broke the plot. Plot style that belongs to the data analysis recipe is a separate, later BLUEPRINT matter. Related: HOM-23 (blocked: no authoring path). Check: no "Plot Style" in the right sidebar (verified in a browser on 2026-11-05).
- [ ] HOM-24 **NEW** — Apply-button UX improvements (UX-APPLY-IMPROVE-1, Phase 34): confirm the apply/pending states read clearly (disabled reason, pending badge). Note anything confusing.
- [ ] HOM-25 — Integer axis breaks: `year_distribution` x-axis shows whole years (`2018`…`2025`), no `.0`; survives T1↔T2 toggling; no `MaxNLocator` traceback.

## 6. Session management

- [ ] HOM-26 — Open Session Management; commit ≥2 T3 nodes across plots; save a named session.
- [ ] HOM-27 — Restart app → session ghost auto-restores (or via "Restore"); committed T3 nodes reappear in their per-plot panels.
- [ ] HOM-28 — Export Active Session (.zip) downloads the full session dir.
- [ ] HOM-29 `[~]` — **(carried, old §14)** Show "Last auto-save: <timestamp>" in the Session Management panel so the user knows the ghost-save fired. Confirm if present; if not, `[~]`.
- [ ] HOM-30 `[?]` — **(carried, old §14)** During the auto-save window, "Export Active Session" should either be disabled or trigger a save first (avoid exporting a stale/partial session). Decide the behaviour.
- [~] HOM-53 **NEW (Eve, 2026-11-08, live-found while testing)** — Deleting a session in the Session Management panel doesn't update the list; the deleted session stays visible until the page is reloaded. (We'd previously decided a page refresh could help for other things too — see if this is the same underlying "list doesn't re-render" cause or a separate one.) **FIXED, 2026-11-08**: `session_management_ui` had no reactive dependency on anything that changes after a delete — `list_all_sessions()` was a plain filesystem scan read once per unrelated re-render, so the panel never refreshed on its own. Added a `_session_list_version` counter: subscribed to (R1-safe `.get()`) at the top of the render, bumped by the delete handler. New tests `TestSessionListRefresh::test_delete_one_session_refreshes_without_reload` + `test_delete_all_sessions_requires_confirm_then_clears_list` (`test_shiny_smoke.py`), plus unit tests for `delete_all_sessions()` in `test_session_manager.py`. Mutation-tested (reverted the subscribe-read, confirmed both Playwright tests fail; restored, confirmed they pass; same for `delete_all_sessions()` itself). — RETEST ↻
- [~] HOM-54 **NEW (Eve, 2026-11-08)** — Add a "Delete all sessions" option to Session Management, for faster test cleanup (28 old test sessions had accumulated in `tmp/UI_TEST/user/_sessions/`, cleared by hand 2026-11-08). **FIXED, 2026-11-08**: `SessionManager.delete_all_sessions()` added (reuses `delete_session()` per key rather than `rmtree`-ing the root, so one malformed/legacy entry can't abort the sweep); wired to a "🗑 Delete All Sessions" button in the panel with the same confirm-modal gate as single-session delete (`session_delete_all_btn` → modal → `session_delete_all_confirm`). — RETEST ↻
- [~] HOM-55 **NEW (Eve, 2026-11-08, live-found)** — The `? Help` modal works, but its content (`app/src/help/home.md`) is stale: still describes the pre-ADR-086 tier toggle (T1 Raw / T2 Reference / T3 Wrangling / T3 Plot buttons), which no longer exists — the real UI is the "Plot to show"/"Data to show" strip (HOM-45). **Found to be worse than just HOME's file while checking the other three**: `blueprint.md`/`test_lab.md` use old "pipeline" vocabulary, `test_lab.md` lists only 4 of the 8 real Test Lab tools (missing Reformatter, ID Reconciliation, Scaffolding, Anonymiser), and `gallery.md` actively describes **"Send to Blueprint"** — a feature removed this session (ADR-093). All 4 files need rewriting to match current reality; not done yet, logged.
- [ ] HOM-56 **NEW (2026-11-08, never live-tested)** — Three new buttons under Navigation, left sidebar, in every config file: "? Help", "📖 Full Documentation" (opens the Quarto book root in a new tab — only shown once `quarto render docs/` has been run for this deployment), "GitHub" (opens your fork, bootstrap-icons GitHub glyph). Confirm all three render, the Documentation link actually opens a working page, and (if you relaunch without having rendered the book) the Documentation link correctly disappears rather than 404ing.
- [~] HOM-57 **NEW (Eve, 2026-11-08, from `issue-drafts/switching-data-analysis-recipe-leaves-first-plot-blank.md`)** — Switching data analysis recipe left the first plot blank until its tab was clicked; the Pipeline Audit panel also kept the previous recipe's plot name until clicked. **Reproduced and FIXED, 2026-11-08**: root cause confirmed with a scripted browser (not just visual impression) — switched recipe, took zero actions, polled for 5s: plot stayed blank and the audit panel stayed on the old recipe's plot name the entire time (not a rendering-latency issue, genuinely stuck). Root cause: `home_theater.py`'s `plots_card` passed `selected=_saved_subtab` (the OLD recipe's active plot id) unconditionally to the inner `navset_card_tab`, with no check that the id exists among the NEW recipe's `plot_ids` — unlike the outer group-level navset three lines below it, which already guards the equivalent case (`_saved_group` is `None` when no match). Fixed by adding the same guard: `selected=_saved_subtab if _saved_subtab in {f"subtab_{p}" for p in plot_ids} else None`. New regression test `TestRecipeSwitchPlotRender` (`test_shiny_smoke.py`), mutation-tested (reverted the guard, confirmed the test fails — twice, once per test-writing attempt after an unrelated test-ordering bug in the first version was caught and fixed; restored, confirmed passes, including in the full suite and repeated for flakiness). Confirmed no regression on the Home↔Blueprint↔Test Lab↔Gallery back-and-forth round-trip Eve was specifically worried about (different code path — workspace switches keep matching ids, so the guard's `else None` branch never fires there). Full suite: 40 passed, 3 skipped. — RETEST ↻
- [~] HOM-58 **NEW (Eve, 2026-11-08, GitHub #24)** — A data analysis recipe with data schemas and plots but no `joins:` block (plots target a data schema directly) failed HOME with "Data Assembly Failed: No assembly or data_schema 'Untitled_Collection' found". **Reproduced and FIXED, 2026-11-08** — per Eve's direction ("If there is no join in the recipe then well there is just no join. The plots can just be made by data that are not joined with anything else."): `active_collection_id()` (`app/src/server.py`) now falls back to the first plot's bare `target_dataset` when `joins:` is empty, instead of the placeholder `"Untitled_Collection"` — `materialize_tier1`'s existing "Path A" already handled a bare data schema correctly, it just never used to be reached. New dedicated test recipe `config/data_analysis_recipes/pipelines/3_test_no_joins.yaml` (reuses the real MLST data schema/TSV from `1_test_data_ST22_dummy`, no joins at all) confirmed at the engine level (`materialize_tier1` directly, 42 rows) and live in the browser (plot renders, audit panel shows "Collection: MLST", no red banner). New regression test `TestNoJoinsRecipe`, mutation-tested — the first attempt's loose assertion (any `.shiny-plot-output img` exists) passed against the broken code too (caught a stale image left over from the previous recipe); tightened to check recipe-specific content, re-confirmed the mutation then correctly fails it. Full suite: 26 passed, 3 skipped; headless: 1464 passed; every-app-features: 9 passed. — RETEST ↻

## 7. Export bundle

- [ ] HOM-31 — Export panel: set a bundle label, pick format (PNG/SVG/PDF), pick scope (global / group / plot), click Export → `.zip` downloads.
- [ ] HOM-32 — Bundle contains `plots/`, `data/` (T1+T2; T3 when advanced+T3 active), `data_analysis_recipes/`, `report.qmd` (with a **T3 Audit Trail** section when T3 nodes exist), `README.txt`. Filters present → `FILTERS.txt` included ("no trace, no export").
- [ ] HOM-33 — `report.qmd` front-matter records data analysis recipe id + sha; methods text reads in plain English from active T3 nodes; PK-touching nodes carry the ⚠️ marker.
- [ ] HOM-46 `[?]` **NEW (note from Eve, 2026-11-05)** — Export after an audit: the exported data analysis recipe must state **the data actually used**, not the default data. Check with a deployment that has `prefer_discovery: true` (data delivered into `raw_data`) and after a Data Import. Suspected gap: the bundle's `data_analysis_recipes/` holds a verbatim copy of the data analysis recipe, which still shows the default `source.path`, while the README/report list the data really used (`data_source_paths`). Decide how the bundle states which data was used. [ADR-088 point 5](../knowledge/architecture_decisions.md)
- [~] HOM-59 **NEW (issue #48/#54, reproducibility bundle import, never live-tested)** — Left sidebar accordion, panel now titled **"Export / Import"** (was "Export"); expand it. The **"⬇ Import a bundle"** block is now at the *top* of the panel, above the "⬆ Export" fields. Check "Also include a reproducibility/reimport bundle" (inside the Export section below) → Export Bundle → re-import that same .zip via the "Reproducibility bundle (.zip)" file control in the Import block at the top. Expect a 4-leg report (`recipe`/`data`/`engine`/`t3_steps`, each match/mismatch/not_checked with a one-line reason) and a notification naming the new recipe id; reload (F5) and confirm it appears in the Data analysis recipe selector. Separately: export **without** checking the box, then try to import that bundle — expect a clear red refusal (not a silent no-op) naming the missing box. **Eve, 2026-11-10, live-found, twice**: first the refusal read as "the feature does nothing" (fixed: hint at the checkbox, visible file-control label, red alert box instead of small grey text) — then, retesting, still couldn't find the control at all, because it was buried below ~10 export-form fields and an `<hr>`. **Fixed again, same day**: Import moved to its own bold-headed block at the top of the panel, panel renamed "Export" → "Export / Import". Full Playwright gate re-run clean (64 passed/3 skipped) after this second fix. **Open, needs your call**: does "comparison to what was before" mean something beyond this 4-leg hash table (e.g. a diff view against the currently-open recipe)? — RETEST ↻

## 8. Data Import + Processing Issues

- [x] HOM-34 — **Files: [`assets/test_uploads/`](../../assets/test_uploads/README.md) (`FastP_valid_changed.tsv`); restore afterwards with `git restore assets/test_data/`.** Data Import accordion: upload a TSV matching a schema → assignment table appears with the right dataset id pre-selected → Apply → plots reload, no traceback.
- [x] HOM-35 — **Files: `assets/test_uploads/FastP_error_*.tsv` (4 files, expected result for each in its README).** Upload a file with wrong columns → per-file validation error (missing/mistyped columns); no data written, cache not busted.
- [x] HOM-36 — **Files: `FastP_valid_changed.tsv` + `Bracken_valid_changed.tsv`.** Multi-file (Ctrl/⌘-select two) → independent dataset dropdowns; both apply.
- [x] HOM-48 — **Files: `FastP_gap_text_in_numeric_column.tsv`.** Text in a numeric column is rejected at import with the column and the value named ("column 'total_reads' (numeric): 'abc'"); nothing is written; valid files still import. Eve 2026-11-05. [#11](https://github.com/evezeyl/SPARMVET_VIZ/issues/11)
- [x] HOM-49 — The message for a rejected import file is readable (banner, normal text size, hint on its own line). Eve 2026-11-05. [#14](https://github.com/evezeyl/SPARMVET_VIZ/issues/14)
- [x] HOM-51 — Rename a column header of a test data file (then `git restore assets/test_data/`) and open Home: it says "Data Assembly Failed" with the dataset and the reason, not a silently wrong plot. Eve 2026-11-05. [#18](https://github.com/evezeyl/SPARMVET_VIZ/issues/18)
- [ ] HOM-52 **NEW (2026-11-08, never live-tested)** — A new **"Processing Issues"** panel now sits at the bottom of the left sidebar, in **every** config file including `pipeline-static` (it has no gate flag — this was a real bug: the panel existed since an earlier phase but was never actually mounted anywhere until now, see finding F-26 in `uml_findings.md`). It's empty when nothing has failed this session. Repeat HOM-51 (rename a column, open Home) and confirm: (a) the panel shows a red-bordered entry with component, timestamp, and problem text; (b) a "Fix (<who>): …" line appears below it with plain guidance, not just the problem restated; (c) the panel stays empty if you haven't triggered a failure yet, and empty again after `git restore`-ing the test data and relaunching.

## 9. Regression & legacy guards (observed from HOME)

- [ ] REG-01 — STATE-1: no plot flicker on T3 toggle / panel switch.
- [ ] REG-02 — STATE-2 / AUDIT-4: comparison T2/T3 toggle stays on the correct plot after a sub-tab switch.
- [ ] REG-03 — UX-1 / BUG-PERF-1: plot rendering is reasonably fast; terminal shows `materialize_tier1` only on cache miss, not repeatedly. *(Also covered by automated tests since 2026-11-05: `app/tests/test_cache_chain.py`, `test_cache_keys.py`. The browser check is still yours.)*
- [ ] REG-04 `[~]` — **(carried, old §17 UX-2)** "Visible columns" multiselect in Data Preview is narrower than its panel. Confirm; `[~]` if still present.
- [x] REG-05 — **Plot to show** → Compare (advanced+): two panes, left labelled "T2 — Result (Reference)", right "My view"; on `year_distribution` both show only the T2 years (2023–2024) until a filter is applied. Back to Result → single plot. No stale compare state after leaving My view. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [ ] REG-06 — Notification log (`🔔 Alerts (N)`) in right sidebar: actions append newest-first with timestamps + colour; max 20 kept; persists across nav within a session.
- [ ] REG-07 — Sidebar collapse: hide left sidebar → content fills width → re-show works after several cycles. *(carried: old §12 sidebar — left untested at Phase 26.)*
- [ ] REG-08 — **Critical (carried)**: hide **both** sidebars (advanced+) → both toggles remain clickable → each sidebar can be re-expanded independently.
- [ ] REG-09 — Legacy-removal smoke: the default data analysis recipes load and render without `ConfigurationError`/`TransformationError` (Phase 34 removed flat `plots:`, `string`/`character` type aliases, flat `wrangling:` lists — none of the shipped data analysis recipes should trip these). *(Also covered by automated tests since 2026-11-05: `app/tests/test_render_every_plot.py` renders all 15 plots of 3 data analysis recipes, `test_data_analysis_recipe_validator.py`, `test_data_analysis_recipe_data_check.py`. The browser check is still yours.)*
- [~] REG-10 — Duplicate Shiny IDs (`notification_log_accordion`/`notification_log_panel_ui`) at launch. → [20260810_testing_part1.md#reg-10](20260810_testing_part1.md#reg-10--duplicate-shiny-ids-notification_log_accordion--notification_log_panel_ui) — root-caused + fixed, RETEST ↻

## 10. Aesthetic / CSS homogenisation backlog (observed from HOME)

> Authoritative palette/scale: `rules_css_style_spec.md` — I'll fix against that, not invent values.

- [ ] CSS-01 `[~]` — **(carried, old §6/§10)** Trash/bin button in **filter** staged rows must match the trash/bin in the **audit** panel (same `btn-link` red style). Re-confirm they're identical on the current build.
- [ ] CSS-05 — Free-find: while testing, note any colour/spacing/font that looks off-palette (Bootstrap blue `#0d6efd`, success green, etc.) with the panel name — I'll reconcile against the style spec.
- [x] CSS-06 — "All rows" switch not aligned with "Data Preview" label in the Data Preview accordion header. → [20260810_testing_part1.md#css-06](20260810_testing_part1.md#css-06--all-rows-switch-not-aligned-with-data-preview-label) [#2](https://github.com/evezeyl/SPARMVET_VIZ/issues/2).
- [x] CSS-07 — **Covered** by the "Compare" choice (sub-label "Result vs My view") in the **Plot to show** row, ADR-086, [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3). Check that the strip reads well: two aligned rows, labels not truncated. — RETEST ↻

---

## Appendix A — Known HOME gaps (don't fail these)

- T3 `aesthetic_override` render path (VIZFAC-T3-OVERRIDE-1) — see HOM-23/HOM-47.
- Plot-panel collapse (THEATER-1).

## Appendix B — When something fails (reminder)

1. Note the **item ID** + what you saw vs expected.
2. Flip the box to `[!]`/`[~]`/`[?]` and add one `> EVE:` line. Screenshot path / terminal snippet welcome.
3. Don't fix inline. Ping me (or just tell me in chat, since this round is live); I grep §0.5 of the master file's protocol, fix, stamp `RETEST ↻`.

## Phase 2 — after HOME is fully done

Everything else moves to `test_plan_2026-06.md`: §2 Configuration-file gating (the 8 config files and
their limitations), §3 TEST_LAB, §4 BLUEPRINT, §6 GALLERY, §7 Cross-space workflow, §10 Re-check
with a real data analysis recipe. That file's §0.4 suggested order has been updated to start there
once this one is closed out.
