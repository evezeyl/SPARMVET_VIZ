# BUILT: the audit and the lineage in HOME (branch `dev`, read on 2026-11-22)

Task: describe what the code does today, without judging and without proposing, for the whole-picture design (owner's order, ledger D-0507). Brief: `tmpAI/coordinator/whole_picture/COLLECT_BUILT.md`.
No tracked file was changed. Nothing was run (no tests, no scripts). `tmp.md` and `tmpAI/agent_channel.md` were not read.

Evidence labels used below: **read** = the function body or the line was read at that place. **grep** = found by a search of the callers (no body read). **rule text** = copied from a rule file as given in the context of this session (not re-opened with the Read tool).
Line numbers are the ones seen on 2026-11-22; the files may move.

## 0. Header: files read and their size

Size = number of non-empty lines (grep count), not the total line count.

| File | Non-empty lines | Read |
|---|---|---|
| app/src/server.py | 251 | grep, lines 140-150, 215-245 |
| app/handlers/home_theater.py | 2367 | 153-230, 290-520, 660-760, 877-945, 1039-1110, 1160-1230, 1385-1480, 1669-1720, 2505-2530 (plus grep of the whole file) |
| app/modules/t3_audit_engine.py | 734 | 60-125, 620-630, 730-900 (plus grep) |
| app/handlers/filter_and_audit_handlers.py | 1142 | 150-260, 643-705, 776-860, 861-925, 960-1260 (plus grep) |
| app/handlers/audit_stack.py | 943 | 54-60 region, 187-310, 441-700, 692-750, 762-830 (plus grep) |
| app/modules/session_manager.py | 903 | 55-135, 186-192, 827-836 (plus grep) |
| app/handlers/export_handlers.py | 2170 | 60-70, 670-700, 1550-1630 (plus grep) |
| app/modules/audit_run.py | 289 | 1-40 (plus grep of its callers) |
| app/modules/view_badge.py | 96 | grep |
| app/modules/orchestrator.py | 715 | 20-40, 298-330, 431-460, 690-760 (plus grep) |
| app/modules/opening_build.py | 251 | 10-45 (plus grep) |
| app/modules/cache_keys.py | 412 | header 1-100, grep |
| app/modules/plan_composer.py | 316 | 1-50 (plus grep) |
| app/src/bootloader.py | (not counted) | grep only (gate functions 431-582, 556-582) |
| libs/utils/src/utils/audit_copy.py | 331 | 1-45, 194-283 (plus grep) |
| libs/utils/src/utils/recipe_graph.py | 641 | 1-64 (plus grep) |
| libs/utils/src/utils/lineage_walk.py | 810 | 1-88 (whole module text read; bodies only grep) |
| libs/utils/src/utils/lineage_records.py | (counted in its family) | 1-30 |
| libs/utils/src/utils/lineage_sentences.py | (small) | 1-24 |
| libs/utils/src/utils/step_effects.py | 227 | 1-40, 55-85 |
| libs/utils/src/utils/key_drop.py | 173 | 1-46 (plus grep) |
| libs/utils/src/utils/remove_from_all.py | 346 | 1-60 (plus grep) |
| libs/utils/src/utils/plan_book.py | (small) | 1-24 |
| libs/utils/src/utils/table_compare.py | (large) | 1-30 (plus grep) |
| libs/utils/src/utils/declared_plans.py | (not read) | grep only |
| libs/utils/src/utils/join_keys.py | (not read) | grep only |
| libs/blueprint_arch/src/blueprint_arch/t3_translator.py | 251 | 1-100, 197-290 |
| Rule files | - | the contents given in this session's context: ui_implementation_contract.md (sections 1, 2, 4, 5, 8, 12, 13), rules_data_engine.md (section 1), rules_ui_dashboard.md (sections 1, 3, 4). Not re-opened with Read. |
| Ledger | - | `.claude/knowledge/decision_ledger.md`: grep for D-0336, D-0363 only |

Plus workflow files: `agent_principles.md`, `decision_compliance.md` (read).

Not read in full (see section 6): most bodies of `lineage_walk.py`, `remove_from_all.py`, `key_drop.py`, `declared_plans.py`, `plan_book.py`, `join_keys.py`, `table_compare.py`, `cache_keys.py` (keys body), `bootloader.py` gate bodies, `session_manager.py` ghost write bodies, `export_handlers.py` bundle bodies.

---

## 1. Exploration and Audit mode, the table viewed, exploration filters and their key

**1.1 The three HOME choices as state.** `app/src/server.py:145-147`: `home_mode = reactive.Value("exploration")`, `data_view = reactive.Value("T3")`, `source_table = reactive.Value(None)`. The comment at `server.py:143` says: "PROVISIONAL P-B1: the data choice starts on T3". They are passed to the handlers at `server.py:220-222` and `242`.
- Reachable: yes (the radio inputs `home_mode`, `data_view`, `source_table` feed them, `home_theater.py` strip).
- Status in code: comment "PROVISIONAL P-B1". Ledger in code: D-0016, D-0310; P-B7 (name of the input) at `home_theater.py:197`.

**1.2 Audit mode test.** `app/handlers/home_theater.py:384-390`: `_audit_available()` = `t3_sandbox_enabled` AND `interactivity_enabled`; `_in_audit()` = `_audit_available()` AND `home_mode == "audit"`. Docstring: "Without the audit flag the app is always in Exploration." Reachable: yes (every plot, table, filter handler). The filter handlers receive it as `in_audit` (`home_theater.py:2581`). Ledger: review F4 (named in `filter_and_audit_handlers.py:150`).

**1.3 The header strip (texts).** `home_theater.py:1160-1230`, function `dynamic_tabs`. Shown only when `interactivity_enabled` (`:1217`); the mode switch only when `_audit_available()` (`:1219`).
- Data choices, with tooltips (read, `:1170-1192`): "Source" (sub "as read from the file"; tooltip "Source: one source table as read from its file with its declared types, before any step of the recipe. A second list names the source tables that feed this plot."); "T1" (sub "after tier 1"); "T2" (sub "after tier 2"; tooltip "If the recipe has none, T2 = T1."); "T3" (sub "the table the plot shows"; tooltip "T3: the table the plot is drawn from: T2 plus the plot's own tier-3 steps of the recipe. If it has none, T3 = T2.").
- Mode choices (read, `:1193-1205`): "Exploration" (sub "look at the data; nothing is saved"; tooltip "Exploration: one plot, the Result. Filters change the table you view, never the plot. Nothing here is saved or exported."); "Audit" (sub "create audit steps"; tooltip "Audit: filters and column drops become audit steps with a reason. They change the plot, are saved with the session and are exported. Compare shows the original and the audited plot.").
- Code comment at `:1169`: "PROVISIONAL (slice B, the coordinator's wording; the owner reads it)".
- The strip reads the mode and the choice isolated (`:1211-1213`).

**1.4 Source table list.** `home_theater.py:1439-1461` `source_table_ui`: shown only when `data_view == "SRC"`; lists the source tables that feed the open plot (`_source_tables_of`); text "Source table:"; "No source table feeds this plot." when the list is empty (read). Reachable: yes. Ledger: D-0310.

**1.5 Compare switch and the line about audit steps.** `home_theater.py:1463-1480` `audit_strip_ui`: only in Audit mode. The Compare switch (label "the original and the audited plot side by side") is shown when `comparison_mode_enabled` (read). Then the line (read, `:1478-1479`): `# PROVISIONAL P-B3 text (slice B): until the audit dialog of slice C, a step is written at the plot's table only` and the shown text **"Audit steps apply to the plot's table (T3) for now."** Reachable: yes. This is a text that states a limit (see section 5).

**1.6 Recipe and plot helpers.** `home_theater.py:394-435` (read): `_open_recipe_id` (raises "No data analysis recipe is open, so no source table can be read." when none); `_source_tables_of(p_id)` (graph, `utils.recipe_graph.source_tables_of_plot`, memo `_graph_memo`); `_effective_source_table` (the picked table when it feeds the plot, else the first one; a different plot can drop the pick); `_open_plot_id`; `_view_source_table` (None unless the data choice is SRC). Reachable: yes.

**1.7 The view key.** `home_theater.py:437-445` `_current_view_key()`: calls `view_key(recipe_id, "audit" or "exploration", data_view, source table only when SRC, active subtab)`. Returned as `current_view_key` to the filter handlers (`home_theater.py:2584`). Reachable: yes.
- `app/modules/t3_audit_engine.py:69-73` `view_key(recipe_id, mode, data_view, source_table, subtab)` (read): the key is the tuple; the source table is kept only for SRC. Its docstring: "An exploration filter is built on this table: when any of them changes, the filters are cleared." Ledger: D-0311, D-0178.
- So a change of the **plot** (subtab) is part of the key: it clears the exploration filters (see 1.10). The code comment says this is PROVISIONAL (`filter_and_audit_handlers.py:175`, "P-B2, PROVISIONAL: it changes the table viewed").

**1.8 The key of a filter row.** `filter_and_audit_handlers.py:769`: a new staged row is built with `staged_filter_row(..., view=current_view_key())` (read). `t3_audit_engine.py:620-623` writes `row["view"] = view` (grep). Reachable: yes.

**1.9 Which applied filters the data preview uses.** `home_theater.py:447-449` `_applied_for_view()` = `rows_built_on(applied_filters, _current_view_key())`. `t3_audit_engine.py:627-630` `rows_built_on` (read): a row is used only when its `view` equals the key; a row with no key is not used. Used by the data preview (`home_theater.py:1690`) and the badge (`:1656`). Reachable: yes. Ledger: review F3 (`home_theater.py:448`).

**1.10 When the exploration filters are cleared.** Two mechanisms:
- (a) Effect `_clear_filters_on_view_change` (`filter_and_audit_handlers.py:181-200`, read): on every change of `current_view_key()` (idempotent: a real change only; the first key is not a change) it empties `_pending_filters` and `applied_filters`, bumps `_form_reset` when rows existed, and shows the notice (warning, 10 s). Reachable: yes (effect). Comment at `:177-178`: idempotent guard, "the selector input is re-created when the user returns to HOME ...".
- (b) Explicit clears: `_clear_exploration_filters()` (`:160-170`, read) is called by Send to Audit (`:849`), by the Reset button (`:855`), by `_clear_filters_on_t3_apply` (`:1233`) and, according to its own comment (`:163`), by the recipe change. Reachable: yes.
- Causes named (the view key order): `t3_audit_engine.py:76-81` `_VIEW_CAUSES` = (1) mode switch, (2) data viewed, (3) source table, (4) "you opened another plot (its table can differ)". Recipe change is handled first by `filters_cleared_notice` (`view_change_notice`, `:91-94`).
- Notice texts (read, `t3_audit_engine.py:55-66, 84-102`): recipe: "The filters of the previous recipe were removed because the recipe changed (a filter is built on one recipe's columns). Audited steps are kept." View: "The filters were removed because {why}. A filter is built on the table you view, so it is not kept when that table changes. Audited steps are kept." with the why text "Audit mode builds audit steps; exploration filters do not exist there" or "a filter belongs to the table it was built on". Docstring: "PROVISIONAL words (the owner reads them)".
- Clearing on a mode switch: via the key (cause 1). `home_theater.py` comment at `:1401-1403` is about the panel, not the filters.
- Ledger: D-0311 (cleared with a notice), D-0178. PROVISIONAL: plot change (P-B2), mode switch (see rule text in section 5).

**1.11 Apply in Exploration only.** `filter_and_audit_handlers.py:776-788` `_filter_apply()` (read): returns at once in Audit mode; otherwise `applied_filters = list(_pending_filters)`. Reachable: yes (button `filter_apply`, shown only when not in Audit, `:661-668`). Its docstring: "a transient view filter, never written to the audit log ... no plot ever does (home_theater.py)". Button title (read, `:666-667`): "Applies these filters to the table you view (Source, T1, T2 or T3) for exploration. They change that table only, never a plot. Not written to the audit log, and not exported."

**1.12 The Send to Audit button and its gate.** `filter_and_audit_handlers.py:152-155` `_can_write_audit_step()` = `_in_audit()` AND `data_view == "T3"` (read). The comment (`:153-154`) says it is PROVISIONAL (P-B3): "the existing dialog writes at the plot's table only". Button shown when `can_send` (`:669-678`); title (read, `:674-676`): "Writes these filters to the permanent audit log (with a reason) — included in every export, applies only to T3, and cannot be silently discarded once committed."
- The button label is "➜ Send to Audit (n)". There is no Apply in Audit mode (`:661`, comment P-B4 "no Apply" in `:649`).

**1.13 Reminders under the buttons (texts).** `filter_and_audit_handlers.py:693-699` (read):
- Audit, T3 not viewed: "To create an audit step, view T3."
- Audit, T3 viewed: "Audit: a step you send changes the plot and is exported."
- Exploration: "Exploration: filters change this table only, never a plot. Nothing here is exported."
Comment: "PROVISIONAL words (the coordinator's; the owner reads them)".

**1.14 The filter rows: operators by type (reached from the dialog).** `t3_audit_engine.py:299-353` `ops_for_column` (read in part): line `:318` "PROVISIONAL (FILTER-PICKERS-1 ..., point 1): true/false offers equal and not equal only"; `:321` "point 2: the operators of a date: the list, every comparison and between." (so dates DO get comparisons, as PROVISIONAL); `:324` time of day and duration offer comparisons and between. Reachable: yes (dialog). See section 5, rule text §8 says the opposite for date.

**1.15 The data preview (the table viewed).** `home_theater.py:1669-1712` `home_data_preview` (read):
- Table: `_resolve_active_lf(spec)` with the data choice (`:1679`).
- Exploration: `_apply_filter_rows(lf, _applied_for_view())` (`:1690`).
- Audit and T3: `audited_frame(lf, _active_plot_t3_nodes(), p_id)` (`:1685-1687`).
- Audit and T1, T2 or Source: no audited step and no exploration filter is applied: the table is shown as it is (`:1685-1687`, comment: "T3 is the audited table").
- 100 rows unless "preview_all_rows" (`:1692-1693`). Column visibility is applied as a preview only (`:1696-1700`).
- Errors: an `AuditStepError` is reported to Alerts ("T3Audit") and shown in the table (`:1704-1712`).

**1.16 The plot in each mode.** `home_theater.py:660-760` `_make_group_plot_handler` (read in part):
- The plot's table is `_resolve_active_lf(spec, tier="T3")` in every mode and every data choice (`:681`).
- In Audit mode the audited steps of this plot are applied with `audited_frame` (`:700-702`, `_active_plot_t3_nodes(this_subtab)`).
- Exploration filters are not applied to a plot (comments `:667-671`: "in Exploration there is ONE plot, the Result ... preview filters (Apply) change the data TABLE of the view shown and never a plot").
- Aesthetic overrides from `t3_plot_overrides` for the audited plot only (`:714-720`, "D-0341: only the audited plot of Audit mode carries it") and passed to `viz_factory.render(..., aesthetic_override=...)` (`:734`).
- Error in the plot: the text "Data error: {e}" in red (`:690-696`).

**1.17 The table of a plot: the function that reads it.** `home_theater.py:485-518` `_resolve_active_lf(spec, tier)` (read): "SRC" to `_read_source_lf`; "T2" and "T3" with a target dataset to `orchestrator.materialize_tier2` (`:515`) or `materialize_tier3` (`:510`); otherwise `_resolve_t1_lf`. Docstring (read, `:488-496`): T3 "the table the plot reads ... the table the plot shows". Reachable: yes.
- `_resolve_t1_lf` (`:327-348`, read): `orchestrator.materialize_tier1(...)` with the anchor `user_data/anchors/<target>.parquet` (`:336-337`); `tier1_anchor()` when the spec is None.
- `_read_source_lf` (`:463-483`, read): one source table through `orchestrator.read_source`, kept in `_source_memo` (8 entries, key = recipe, table, data batch hash, recipe sha). Reachable: yes.

**1.18 Badges.** `app/modules/view_badge.py` (grep, lines 15-117): labels "Viewing: <source label>" with "(audited)" when audited (`:82`); "Plot: Result" and "Plot: Audited" (`:110-117`); the text "no audited step for this plot yet: identical to the Result" (`:111`); `PLOT_STEPS_NOTE` "T3 = T2 plus this plot's own steps of the recipe" (`:36`); `PLOT_STEPS_NOTE_NO_TIER2` (`:37`). Source words are PROVISIONAL: `view_badge.py:20`, `:35`, `:38`. Reachable: yes (`home_theater.py:947-957`, `:1642-1656`).

**1.19 Compare pane.** `home_theater.py:755-790` `_make_cmp_baseline_handler` (grep and partial read): the original (left) pane is the table the plot reads with no exploration filter and no audit node (comment `:779`). Reachable: yes when the switch is on.

**1.20 Right panel follows the mode.** `home_theater.py:1401-1425` (comment and effect `_drive_right_panel`): closed in Exploration, open in Audit (D-0375, D-0385) through `frame_widths.right_panel_open`. Reachable: yes.

**1.21 Restored session opens Audit mode.** `home_theater.py:1421-1437` `_open_audit_mode_after_restore`, comment `:1421`: "P-B5 (PROVISIONAL, the coordinator's choice): a restored session that holds audit steps opens Audit mode". Reachable: yes (effect).

**1.22 Right panel texts in Exploration.** `home_theater.py:2348-2350` (grep): in Exploration the right panel is empty when opened by hand (comment D-0383); `parts = _build_right_sidebar("home") if _in_audit() else []`. Reachable: yes.

---

## 2. Where an audit step is written, how it is stored and applied

**2.1 The audit node: the one written in the running app.** `app/modules/session_manager.py:56-106` `AuditStep` (TypedDict) and `make_audit_step` (read): keys `node_type`, `id` (hex; propagated copies share it), `created_at`, `plot_scope`, `params`, `reason`, `active` (default True, `:100`), `primary_key_warning` (only when True), `gallery_source` (optional). Filter steps always get `na` through `with_na` (`:91-92`, comment "NA-RULE-63: a filter step is never written without `na`"). Line `:64` says `active` is a "legacy soft-delete flag — Phase 22-I switched to hard delete". Reachable: yes.

**2.2 Node types the app writes.** Grep: the running app creates only `filter_row` (`filter_and_audit_handlers.py:835-841`, read: `node_type = "filter_row"`, comment AUDIT-1 "Keep the row as filter_row") and `drop_column` (`:909-913`, read). `exclusion_row` is never created in `app/` (grep). `aesthetic_override` (alpha / colour etc.) is created only by the aesthetic panel, which is not mounted (see 2.13). `random_seed` is not a node: the Reshuffle writes a seed into the overrides (see 2.14).
- The dialog title still says "Add N filter/exclusion(s) — choose scope" (`filter_and_audit_handlers.py:997`, read). Text states a type the app does not write.

**2.3 Send to Audit (filter rows to nodes).** `filter_and_audit_handlers.py:792-849` `_filter_send_to_audit` (read): needs `_can_write_audit_step()`; builds one node per staged row with `audit_params_from_row(frow)` (`:821-842`); `primary_key_warning` = column in `home_state["primary_keys"]` (`:818`, `:826`); stores the nodes in `_propagation_scratch` and opens the propagation modal (`:845-846`); then clears the exploration filters (`:849`). Reason is "" (`:840`). Reachable: yes (button).

**2.4 Drop of columns (the data-preview column selector).** `filter_and_audit_handlers.py:861-922` `_col_drop_to_audit` (read): the columns deselected in `preview_col_selector` on the T3 table are the drop candidates; if none, a notice "No deselected columns to drop. Uncheck columns above first." (`:889-892`). Then the key check (2.5), then `drop_column` nodes (`:908-915`), then the modal. Afterwards the selector is reset to the kept columns (`:919-922`). Reachable: yes (button `col_drop_audit_btn_ui`, `home_theater.py:1790-1812`, shown only in Audit on T3: `:1800`).

**2.5 Key check at a drop in HOME.** `filter_and_audit_handlers.py:895-904` (read): `problem = key_drop.DropGate(recipe_raw(), recipe_plans()).problem(f"T3:{p_id}", to_drop)`; a problem is shown as "⛔ ..." and nothing is written. Comment at `:895-897` (read): "A column a join step later reads as a key is refused BY PLACE ... this drop is written in the plot's own steps, the place T3:<plot>, after every join and with nothing built from it, so the rule finds nothing to refuse there today; it is asked all the same". Module docstring (`:864-866`): "A column that a join step later reads as a key → BLOCKED with the sentence of the rule". So: **in HOME the refusal branch is asked but, per this code comment, cannot fire for a drop at T3.** `PlanComposerBug` leads to a silent return (`:900-901`, the notice was shown by `recipe_plans`).

**2.6 Modal for propagation (text).** `filter_and_audit_handlers.py:970-1116` `_open_propagation_modal` (read). Header: "Drop {n} column(s) — choose scope" or "Add {n} filter/exclusion(s) — choose scope" (`:991-997`). Warning when any node has `primary_key_warning` (`:1002-1007`): "One or more nodes target a join key. Removing rows here changes which samples appear in joined plots." Presence preview (`:1010-1050`): "Propagation preview: N apply • N skip (col missing)"; per plot "⚠ <plot> — column not in plot data; will be SKIPPED" (`:1015-1018`); "? <plot> — could not resolve dataset; verify manually" (`:1019-1022`); footer "A skipped plot is NOT filtered — it shows the unfiltered data." (`:1044-1047`) and "Apply filters one at a time and verify each plot before stacking." Radio "Apply to:" with "This plot only" (default), "All plots", "All plots except…" (`:1056-1066`). Button "Add to audit pipeline" (`:1107-1110`). The modal reads the column presence per plot (`_column_presence_per_plot`, `:926-968`, reached; "unknown" when no schema).

**2.7 Confirm of the propagation.** `filter_and_audit_handlers.py:1118-1195` `_handle_propagation_confirm` (read): target plots from the choice (`this` = active plot; `all`; `except` = all minus the picks) (`:1141-1148`); for each node and each target plot: `_plot_has_column(plot, col)` (`:1172`); if absent the plot is skipped and the column recorded (`:1173`); else a copy `make_audit_step(..., plot_scope=plot_id, reason="", primary_key_warning=..., node_id=shared_id)` (`:1175-1181`) appended to `_pending_t3_nodes` (`:1184`). Notice: "N audit entry(ies) added across M plot(s)." and "Skipped (column not in plot data): ..." (`:1188-1194`). The notice for "No target plots selected. Audit pipeline unchanged." (`:1151`).
- `_plot_has_column` (`:1197-1212`, read): errors return True ("fail-safe to True so we don't silently drop nodes").
- The docstring of `_open_propagation_modal` (`:973-983`) says the pending nodes are appended to `home_state._pending_t3_nodes`. That is what happens.
- The pending copy does **not** carry `plot_scopes_intent`. The comment at `home_theater.py:287` says "The modal reads from this and writes plot_scopes_intent on confirm", and `orchestrator_helpers.py:53` says "(carry plot_scopes_intent)". grep finds no write of `plot_scopes_intent` in the app. Stale comments, and the rule text §12g.7 (the token "__all_at_apply__") is not in the code (grep).

**2.8 Apply (btn_apply): commit.** `app/handlers/audit_stack.py:187-306` `handle_apply` (read):
- Reads the reason text of each node from the live input `t3_reason_<suffix>` (`:212-225`); if the input is not on the page, the kept text is used (`kept_reasons`, `:224-225`).
- Copies the reason to all copies of one id (`:227-238`, comment "Linked-id reason fan-out").
- Gatekeeper: `gatekeeper_blocked(committed + pending)` (`:241`). If blocked: a `PipelineError` (printed), a notice "Nothing was applied: N step(s) have no reason (...)" with the remedy "write a reason for each step, then press Apply" (`:249-267`), the typed reasons are kept in `home_state` (`:269-273`), and nothing is committed.
- If not blocked: each pending node is appended to `t3_audit_steps_by_plot[plot_scope]` (`:276-281`); `_pending_t3_nodes` emptied; `t3_apply_count` + 1 (`:283-288`); the T3 ghost is written when `session_manager` and `_ghost_save_enabled` (`:291-296`); notice "audit steps applied — N node(s) across M plot stack(s)." (`:302-306`).
- Reachable: yes (`btn_apply` in the right panel, Audit mode only, `audit_stack.py:692-700`, comment D-0377).

**2.9 Gatekeeper rule (which node types block).** `audit_stack.py:51` `_REASON_REQUIRED = {"filter_row", "exclusion_row", "drop_column"}`; `session_manager.py:188-192` `node_blocks_apply` (read): blocks when `active` (default True) AND type in `{filter_row, exclusion_row, drop_column}` AND reason empty. `gatekeeper_blocked` (`session_manager.py:834-836`, read) returns the ids. `aesthetic_override` never blocks. `developer_raw_yaml` is not in either set (see 5.2).

**2.10 The button label when blocked.** `audit_stack.py:692-748` `audit_stack_tools_ui` and `btn_apply_ui` (read in part): Apply is drawn as "Apply ⛔" when `gatekeeper_blocked(all_nodes)` is not empty (`:704-708`, `:736-741`), else "Apply". Shown in Audit mode only (`:693-695`).

**2.11 Right panel list (the audit trail).** `audit_stack.py:441-564` `audit_nodes_tier3` (read): shows the active plot's committed nodes plus its pending nodes, newest first (`:470-472`); with no node: "No T3 adjustments for <plot> yet." (`:452`); header "My Adjustments (Tier 3) — <plot>" (`:460`). Per node: icon and label from `_NODE_META` (`:44-51`; the entry for `aesthetic_override` is "Plot Style"), "PENDING" badge (`:491-494`), "Applied to N plots" badge when the id is in more than one plot (`:496-499`, text), primary key banner "⚠ Primary key — Primary ID/Key alignment" (`:501-504`, read: only this title text; the longer explanation of the rule §12g.6 is not in the code), delete button with title "Delete this audit node (linked: removes from all plots)" (`:530-534`), reason input "Reason (required)…" shown for filter/exclusion/drop when the step is active (`:506-522`).
- Orphaned nodes from a legacy ghost: "N orphaned node(s) from a legacy ghost. Delete or re-target manually." (`:555-562`).

**2.12 Deactivation (the Power icon) is not built.** `audit_stack.py:479` reads `node.get("active", True)` and `:489` gives `opacity:0.45; text-decoration:line-through` when it is False. Grep for any write of `active` to False in `app/handlers`, `app/modules`, `app/src`: none. So the strike-through branch is never reached. Rule §1 and §12c say the same ("not implemented", F-07, task STM-NODE). `session_manager.py:64` keeps the field "legacy soft-delete flag".

**2.13 Delete (linked).** `audit_stack.py:627-682` `_handle_delete` (read): clicks on `t3_delete_<suffix>` remove every copy with that id from every plot stack and from the pending list (`:662-671`); notice "N audit decision(s) deleted (M copy/copies across plots)." (`:678-682`). Docstring: "ADR-049 §12g.10". This is the only removal path in the running app. There is no "Remove step" control and no revert control (grep for "Remove step", "Revert", "btn_revert" in `app/`: none).

**2.14 Aesthetic panel: defined, not mounted.** `audit_stack.py:762-830` `aesthetic_style_panel_ui` and `_handle_aesthetic_apply` (read in part); the alpha is written straight to `t3_plot_overrides` (`:829-837`); other aesthetics open a propagation modal "simplified — no column-presence check for aesthetics" (`:851`); the modal confirm `_handle_aesthetic_propagation_confirm` (`:901-948`). The panel is **not mounted**: `home_theater.py:2230-2234` (comment: "The 'Plot Style' panel (aesthetic_style_panel_ui, defined in audit_stack.py) is NOT ... after fixing HOM-47"). The handlers are registered (`audit_stack.py:21`, `:751`) but no screen reaches them.

**2.15 Reshuffle writes a seed into the overrides (no audit node, no reason).** `home_theater.py:877-899` `_handle_reshuffle` (read): in Audit mode, a click sets `t3_plot_overrides[<plot>]["random_state"] = secrets.randbits(31)` in `home_state` (`:893-899`). No audit node, no reason, no apply. Its comment (`:714-715`) says the pin is in `_t3_overrides`. The seed line (`_plot_seed_ui`, `:901-917`) shows the seed and offers "removing the pin" (`:919-943`, `_handle_unpin`: writes `t3_plot_overrides`). Ledger: D-0341 (offered only in Audit mode; "how a reshuffle is written down as an audit step ... is not decided"). Export: the overrides go into the report and `t3_steps.yaml` (`export_handlers.py:1076-1089`, `:1539`).

**2.16 Aesthetic overrides are applied in the plot.** `home_theater.py:714-734` (read): the audited plot takes `t3_plot_overrides[this_subtab]` (only in Audit mode) and passes it to `viz_factory.render(..., aesthetic_override=...)`. Export: `export_handlers.py:1301-1303` (comment "VIZFAC-T3-EXPORT-1: pass L5 aesthetic_override"). So overrides are applied, although rule §12g.9 says they "were never applied to the rendered plot until VIZFAC-T3-OVERRIDE-1 ships" (see 5.3).

**2.17 Store: the session state and the ghost.** `session_manager.py:488-545` (`write_t3_ghost`, read in part): writes `t3_<timestamp>.json` with `t3_audit_steps` (a flat list, "legacy flat view, kept for bw compat", `:509-522`), `t3_audit_steps_by_plot` (normalised), `t3_plot_overrides`, `schema_version` = `SESSION_FORMAT_VERSION` (`:519-521`). Two representations are stored at once (the flat list is derived from the per-plot one, `:509`).
- Reading (`:552-590`): a ghost with only a flat list is put in the "__legacy__" bucket (`:572-576`, read); the orphan text is in `audit_stack.py:558`.
- `write_t3_ghost` is called from `audit_stack.py:291-296` (`_write_t3_ghost`, `:1019`), only after a successful Apply.

**2.18 Format number and refusals.** `session_manager.py:214-241`: `SESSION_FORMAT_VERSION = 3` (`:217`). `session_format_problem` (`:220-232`, read): a file with no number, a lower number or a higher one is refused as a whole; the text is marked "PROVISIONAL wording (D-0312 gives the sense, a text the owner reads)" (`:223`). `session_recipe_refusal` (`:235-253`): a session of another recipe is refused (D-0317); marked PROVISIONAL (`:239`). `session_handlers.py` uses them (grep, `:673-678`).

**2.19 Primary keys (for the warning only).** `session_manager.py:125-135` `extract_primary_keys` (read): returns `join_keys.recipe_join_keys` (the key columns of the joins of tier 1 and tier 2). Used for `home_state["primary_keys"]` and the warning on filter rows (`filter_and_audit_handlers.py:818-826`). Docstring: "This includes both true PKs ...". The rule §12g.2 says there are two lists, the "entity key" and the "columns used to join" (DECIDED, not built, D-0313, D-0082); the code has only the join keys (`session_manager.py:134-135`, grep for `is_entity_key` in HOME: none).

**2.20 Restore: drops that a join needs are not restored.** `session_manager.py:138-164` `split_key_drops` (read): asks `key_drop.DropGate(recipe_raw, plans)` for each stored `drop_column` (by place, D-0358, D-0297). A refused drop is returned. `key_drop_notice` (`:166-185`): one notice per refused decision; the text is marked "PROVISIONAL wording (D-0297 asks for plain words ...)" (`:169`). Called from `session_handlers.py:673-678` (read). Reachable: yes.

**2.21 Session restore of the audit nodes.** `session_handlers.py:656`, `:682` (grep): `t3_plot_overrides` and the nodes are restored from the latest ghost; `normalise_audit_steps` (`session_manager.py:109-122`, read) gives `na` = "remove" to old filter steps.

**2.22 Export pre-check.** `export_handlers.py:1102-1130` (read in part): `_audited_nodes(p_id)` and `_base_frame(p_id, spec)`; `audit_failures(...)` (`:1129`) runs `audited_frame` on every plot with steps before any file is written (`t3_audit_engine.py:886-898`, read: "The check the export makes before it writes anything"). Reachable: yes.

**2.23 Export of audited data.** `export_handlers.py:1296-1303` (plot) and `:1463` (T3 data): `audited_frame(lf, _audited_nodes(p_id), p_id)` applied to the plot's base table; `T3_data_<plot>.tsv` written for plots with audited steps. Exploration filters are not an argument (the docstring of `audited_frame`, `t3_audit_engine.py:778-779`: "they are not audited and are never exported").
- `plot_content_rules(audited_rows, audited_drops)`, named as "the pure rule" in the rule text (§7.2 rule 4), does **not exist** in the code (grep for `def plot_content_rules` in `app/` and `libs/`: none).
- Export of `drop` is `lf.drop` in `audited_frame` (`:786-788`).

**2.24 The order rule.** `t3_audit_engine.py:734-768` `audit_steps_in_order` (read): "DECIDED 2026-11-15 (Eve, S2-1): the recorded order" (`:737`). Skips `aesthetic_override` and `random_seed` (`:752-753`); inactive nodes are skipped (`:758-759`, but none is inactive, see 2.12); a defective node raises `AuditStepError` (`:755-757`). Numbering counts only active data steps (`:760`).

**2.25 The applier.** `t3_audit_engine.py:771-791` `audited_frame` (read): for each step in order: a column that is not in the table raises `AuditStepError` naming the plot (`:784-785`); drop: `lf.drop` (`:786-788`); filter: `_apply_filter_rows(lf, [row])` (`:790`). Docstring: "The ONE function for HOME's T3 table in Audit mode, HOME's audited plot (also in Compare), the results bundle ..., the check before an export and the column list of the filter dialog: they cannot differ." Reachable: yes (see 1.15, 1.16, 2.22, 2.23).

**2.26 The dialog frame.** `t3_audit_engine.py:794-798` `dialog_frame` (read): in Audit mode on T3 the dialog acts on the audited table; else on the table shown. "DECIDED 2026-11-15 (Eve, S2-1 (a)); D-0178." Used in `filter_and_audit_handlers.py:583-600` (`_active_frame`, read in part).

**2.27 The audit copy of a recipe (library): what it does and who calls it.** `libs/utils/src/utils/audit_copy.py` (read header 1-45 and 194-283):
- Module text: a copy of the recipe that only ADDS audit steps, each in a second list `audit_steps` of its tier (`:5-10`, D-0102, D-0143, D-0332). An audit step is the operation plus `id: audit_<8 hex>_<k>` and `audit_comment` (D-0329, D-0321). "The audit may take its own steps out again, any of them (D-0314: one undo control, 'Remove step'); an original step can never be removed." (`:8-9`).
- `add_step` (`:212-232`, read): allowed actions only (`AUDIT_ACTIONS`, `:197-198`); a drop of a key column is refused by `key_drop` at this place (`:204-209`, `:199-201`); a reason that is not empty is required (`:225-226`); id = `audit_<audit_id>_<created+1>`, the counter never goes down (`:228-231`).
- `remove_step` (`:245-264`, read): takes out any audit step by id; a tier created by the add is removed again (`:261-262`).
- `integrity_errors` (`:352`) checks "the copy minus its audit steps equals the original" (ADR-105 point 6, D-0040).
- Callers in the running app: `integrity_errors` and `audit_operation` are called by `app/modules/cache_keys.py:69` (imports; used for the keys and the check, `:402`), and `orchestrator.refuse_audit_steps_outside_an_audit` (`orchestrator.py:80-100`, docstring, "The engine's own refusal (D-0332)"). `add_step`, `start_audit`, `remove_step`, `with_audit_steps`: **no caller in `app/handlers`, `app/modules`, `app/src`** except `plan_composer.compose_candidate_plan_book` (`plan_composer.py:359-369`), which itself has no caller outside the tests (grep). So in the running app no audit copy is created and no audit step is written into one. Section 3 has the test status.
- Module PROVISIONAL list (`:26-40`): "where the copy is written to a file, the date and initials of a step, the log of added and removed steps, the key under `info` that names the original" are PROVISIONAL / not decided and not built. The place form is "PROVISIONAL, the builder's form" (`:30`); "where `created` and `audit_id` are kept when the audit is written to a file ... is the audit record's job (D-0333; not built here)" (`:22-23`).

**2.28 The engine accepts `audit_steps` in recipes (the rule says "not read from a file yet").** `libs/transformer/src/transformer/data_wrangler.py:17` imports `AUDIT_STEPS` from `utils.recipe_tiers` (grep), and `recipe_tiers` is the one reading of the tier lists (docstring of `audit_copy.py:13`). `orchestrator.py:80-100` refuses `audit_steps` in a recipe that is not an audit copy. So the engine reads the key in a file. The rule §12a says "DECIDED, not built: the keys are not read from a file yet; D-0354". This is a difference to check (section 5).

**2.29 Export: the reproducibility fork (a second way).** `export_handlers.py:1554-1628` (read): when the checkbox `export_include_reproducibility` is ticked, `blueprint_arch.t3_translator.build_mode2_recipe(cfg.raw_config, _t3_by_plot)` (`:1561-1564`) writes `data_analysis_recipes_reproducibility/<recipe>.yaml`. The T3 steps of each plot are translated (`translate_t3_node`, `t3_translator.py:92-160`) and appended to a plot-private copy of the join's tier 2 (`build_mode2_recipe`, `t3_translator.py:197-290`, read): the copy is named `<join>__t3_<plot>`, the plot's `target_dataset` is repointed, a `comment` says which join it copies, which plots it serves and the ids of the audit steps (`:287-288`). Also the data files are copied (`export_handlers.py:1575-1588`). The root key `plots` is removed (`t3_translator.py:239`).
- Operators translated: `eq ne gt ge lt le in not_in between` to `modif_filter` (`t3_translator.py:73-76`); drop to `polars_drop`. `aesthetic_override` and other node types raise `UntranslatableNode` and the plot is "skipped" (`t3_translator.py:92-99`, `:263-267`).
- Notice when a plot cannot be baked: "N plot(s)' T3 steps could not be fully baked into the reproducibility recipe ... they are still in the Publication content, just not engine-replayable yet." (`export_handlers.py:1615-1620`, read).
- Toggle text (read, `export_handlers.py:675-692`): "Also include a reproducibility/reimport bundle" with the help "The verification record (effective_run.yaml ...) is always included. Checking this also adds the full recipe (your audited steps baked in as real wrangling actions) and the actual data files ... a bundle exported without this box checked cannot be imported, only verified against its effective_run.yaml."
- Code comment `export_handlers.py:1573-1574`: "Sensitive-data handling is #46, not built here." The notice (`:1604-1612`) tells the user the bundle includes the raw data files.
- Rule §12a/§7.2 "DECIDED, not built": the export of an audit should hold the audit recipe and replace "today's export copy that writes the audit steps into a copy of a join's tier 2" (rule §7.2, rule 4). The code is the fork described here.

**2.30 Audit run (the copy run without a screen).** `app/modules/audit_run.py` (read header 1-40): `run_audit` (`:310`) builds the copy's tables into a separate folder and says which plots are affected. Its header says: "Serves the audit that the next slices put on the screen. Nothing a user sees is wired to it yet." (`:4`), and "Consumed by: app/tests/test_audit_run.py. If deleted: nothing runs a copy yet" (`:30`). grep: `run_audit` and `AuditRun` have no caller in `app/handlers`, `app/modules` (other than the file), `app/src`; the only consumer is the test. **Test-only (dead for the running app).** `audit_run` does import `compose_plan_book`, `integrity_errors`, `with_audit_steps`, `build_graph` (`:51-56`) for that purpose.

**2.31 Remove from all the data (the library) and the audit copy.** `libs/utils/src/utils/remove_from_all.py:237` and `:395` (grep): `remove_from_all.apply` writes `audit_copy.add_step` at each reached table. Its header (read, `:56`): "Consumed by: libs/utils/tests/test_remove_from_all.py, app/tests/test_remove_from_all_demo.py (HOME's Create audit step dialog will call it; that screen is not built)." **Test-only.**

**2.32 The audit node model and the copy model are two representations.** See section 4 (two ways).

---

## 3. The lineage library: each module and whether the running app calls it

Call graph by grep (the only way it was checked here: the import lines and the names in `app/handlers`, `app/modules`, `app/src`, `libs/*/src`). "Live" = imported by a module the running app uses (`app/handlers/*` registered in `home_theater.define_server`, or `app/modules/*` they import). "Test-only" = imported only by `tests/` folders or `app/tests`.

### 3.1 `libs/utils/src/utils/recipe_graph.py` — LIVE
- `build_graph(raw)` (`:75` import). Callers: `home_theater.py:68,413` (source tables of a plot), `cache_keys.py:73`, `data_analysis_recipe_validator.py:49` (the load gate), `plan_composer.py:51`, `audit_run.py:56`, `key_drop.py:53`, `declared_plans.py:29`. Live.
- `source_tables_of_plot` (`home_theater.py:414`). Live (Source view).
- `key_candidates_for` / `key_candidate_sources` (`:503-548`): grep finds no caller in `app/` or in `libs/*/src` other than the module; `test_key_candidates.py` calls it. **Test-only.** Its docstring: "the ordered column tuples to hand to `table_compare.compare`" (`table_compare` is test-only, see 3.11).
- Header text (read, `recipe_graph.py:55-61`): "Consumed by: libs/utils/tests/test_recipe_graph.py ... nothing runs yet; the rebuild of those callers needs it." The module is in fact live (above). **Stale header.** `:66` lists `libs/utils/src/utils/lineage_walk.py (declared_entity_keys, key_family_of, lineage_forward, plot_columns)`; the names are not checked here.
- PROVISIONAL / choices (read, `:45-53`): a join that names a join is drawn (chain of tier-1 nodes); signature `build_graph(raw, *, columns_provider=None)` differs from the mechanism page; the build raises `RecipeGraphError` on a broken recipe; only row steps, `polars_select` and `polars_drop` are understood, every other step makes columns unknown; the key-family rule: `by` columns of an as-of join link families, and families are by column name for the whole recipe.

### 3.2 `libs/utils/src/utils/step_effects.py` — LIVE (through the graph and the walk)
- `READINGS` (`:57-65`, read) — the closed list of D-0351, exactly:
  - `rename`: `mapping`
  - `join`: `right_ingredient`, `on`, `left_on`, `right_on`, `how`, `suffix`
  - `drop`: `columns`
  - `select`: `exprs`
  - `with_columns`: `named_exprs`
  - `cast`: `columns`
  - `group_by`: `by`, `named_aggs`
- `FOLLOWED_JOINS = ("left", "inner", "semi")` (`:68`); `NO_COPY_JOINS = ("semi",)` (`:70`); `NOT_YET_FOLLOWED_JOINS = ("anti", "right", "full", "cross")` (`:73`). A self-join is not followed YET (module text `:33`).
- Module text: "The kinds anti, right, full and cross are not followed YET (D-0452 ...)"; semi join followed (D-0486); the capital YET is decided (D-0454, lineage_sentences).
- Callers: `recipe_graph.py:489-532` (`effect_of`, live), `declared_plans.py:27` (`fx`, see 3.8), `lineage_walk.py:88`, `lineage_sentences.py:24` (`NOT_YET_FOLLOWED_JOINS`).
- Header "Consumed by: libs/utils/src/utils/lineage_walk.py, libs/utils/tests/test_step_effects.py" (`:38`) is **stale**: `recipe_graph` and `declared_plans` use it too.
- Module text says "PROVISIONAL, see `lineage_walk`" for the rule that a step outside the list is `unread`.

### 3.3 `libs/utils/src/utils/lineage_walk.py` — LIVE only through `LineageIndex.drop_facts`; `walk()` is TEST-ONLY
- The module text (read, `:1-79`) is the list of places of the owner's decisions. Copied as they are:
  - **P1 (O1)**: which groups of places are offered. The user chooses the levels (source, T1, T2, T3; D-0355) and ticks. Groups: lineage, join_linked. No group for "the same key, no join links it"; tables with the same key and not linked are information only (`Walk.outside`). PROVISIONAL.
  - **P1b**: a line at SOURCE is grey with `no_step_list` (D-0332); not decided how a step acts there.
  - **P2**: a step outside the readings: a column across it is ticked only when the plan alone proves the name and type unchanged, else grey (`step_not_read`).
  - **P3**: a name that changes on the path is followed (rename, key with another name, suffix of a clash) (D-0352, D-0357). A column written under its own name is the same column with a note (D-0353, D-0337): cast (`another_type_here`), compute (`recomputed_here`), group-by aggregate (`aggregated_here`), group key (`one_row_per_group_after_this_step`). PROVISIONAL: a recompute or aggregate under the same name is ticked also when the values come from another column (D-0356), with `knows_source_of_values` False.
  - **P4 (D-0451)**: a place no plot reads that the walk reaches is a line (`Line.no_plot_reads`). NOT decided (D-0451): whether such a line is ticked when the dialog opens (PROVISIONAL reading), the words, the two routes to one place.
  - **P4b**: a rename in one tier and back later is one column named as in each table (owner 2026-11-20).
  - **P5 (O4)**: a place of the reach where the column no longer exists is a `Gone` note, not grey (not confirmed).
  - **P6 (Q4)**: a table whose tier 2 is empty is one place with its tier 1 (D-0346 as written).
  - **P7 (O8)**: a column that exists twice at a place is grey (`several_columns`). A table joined with a table it already holds is no longer followed (see P12).
  - **P8 (O3)**: an empty tier 2 or a tier 2 of a table no plot reads is not a place; a tier 3 is always a line (D-0346). NOT decided whether this should change (D-0451).
  - **P9**: a line is ticked when ANY path from the chosen place is certain; grey only when every path is uncertain.
  - **P10**: the group of a place is the smallest group that reaches it.
  - **P11**: `Gone.removed_by` is the first removing step in data-flow order.
  - **P12 JOINS (D-0452, D-0454, D-0460, D-0486)**: a semi join is followed like inner and left (D-0486). Kinds anti, right, full, any kind outside `FOLLOWED_JOINS`, and a self-join are NOT YET followed: every link across them is uncertain (`join_not_yet_followed`), so the line is grey and cannot be ticked. NOT decided: whether only the places after the join should be red (owner's question); how a red line is shown; the words beyond YET (PROVISIONAL). The key columns of such a join are linked by an uncertain link (`_join_key_links`), so the second table is a red line seen from either side (review of 2026-11-22).
  - **P13**: a source line next to a tier 1 without steps is the same table: grey `no_step_list`, with `duplicates`.
  - **P14**: a walk that selects no place says so (`Walk.nothing`); `Walk.held_at_levels`.
  - **Drop (kind "drop", D-0358, D-0297)**: a drop is refused by place when a join later reads the column as a key, followed by the links of the walk (`DropFacts`, `drop_facts`: one function, also the gate of `audit_copy`, the integrity check and the checker, through `utils.key_drop`); a refused line is grey with `refusal`. A column that a later step or a plot uses without being a key is NOT refused: the line carries `Line.consequences`.
  - **P15 (D-0448, "Her answer: B")**: a declared entity key that no later join uses is not refused for being declared; the line says so (`declared_entity_key` note).
  - **P16 (D-0460)**: a column the walk cannot follow to the end is grey on a drop line and the gate REFUSES the drop; it replaces D-0449 (which allowed it with a warning). How a red line is shown is not decided.
  - **P17**: without a candidate plan the consequences hold only what the steps the walk reads and the plot mapping say (`consequences_checked` False).
- Callers (grep): `key_drop.py:72,87,111,120-128` (`LineageIndex(...)`, `drop_facts`, `DropGate`) — **live** (from `filter_and_audit_handlers.py:899`, `session_manager.py:150`, `audit_copy._key_drop`, `recipe_check.py:575`). `LineageIndex.walk` and the module function `walk` (`:549`, `:883-890`): **no caller in the running app** (only `tests/`; `remove_from_all.py` builds `LineageIndex` but is test-only). `LineageIndex.certainty_from`, `uncertain_ends`: used by `remove_from_all` (test-only).
- The module docstring says "libs/utils/tests/test_lineage_walk.py (the dialog of HOME calls the walk later)" (`:70`): the dialog does not call the walk.
- Stale in the header: the walk is not called by the dialog (see above); the text is the design's intent, not the code's status.

### 3.4 `libs/utils/src/utils/lineage_records.py` — LIVE through `key_drop` and `lineage_sentences`
- Plain data: `Walk`, `Line`, `Gone`, `Outside`, `Occurrence`, `Hop`, `StepRef`, `SourceColumn`, `Reach`, `Reason`, `Note`, `Start`, `KeyNeed`, `Consequence`, `DropFacts`, `Certainty` (`:16` provides list). Levels: `SOURCE, T1, T2, T3` (`:30`); the user chooses them (D-0355). Reason and note codes are data.
- Callers: `key_drop.py:48` (live), `lineage_sentences.py:25` (live), `lineage_walk.py:89`, `remove_from_all.py:75` (test-only), tests.

### 3.5 `libs/utils/src/utils/lineage_sentences.py` — LIVE through `key_drop`
- `join_not_yet_followed_sentence(reason)` returns the full sentence with the capital "YET" (decided D-0454; a test asserts it). The rest is PROVISIONAL: the list of kinds, the clause for an anti join, "Check them before you confirm" (module text, `:4-5`).
- Live text example (read, `lineage_sentences.py:53`): "The app cannot YET follow this column through this kind of join (...). Here it is ..."
- Callers: `key_drop.py:50,159` (live, the drop refusal), `remove_from_all.py:76` (test-only).

### 3.6 `libs/utils/src/utils/key_drop.py` — LIVE (the gate of a drop)
- Module text (read, `:1-40`): "The drop of a key column is refused BY PLACE, in one rule (LBFB step 4; D-0358 modulates D-0297)." A drop at place p (`T1:<table>`, `T2:<table>`, `T3:<plot>`) is refused when a later join reads the column as a key (followed by the walk's links). Where no later join reads it (a plot's own steps), the drop is allowed. A drop the walk cannot follow to the end (`DropFacts.uncertain`) is NOT written: red, cannot be ticked, and refused with ONE plain sentence (D-0460: "B of needed we try to.fimd a.solutiom later"; replaces D-0449; D-0450 "do not get wrong results because we did not select the correct scope").
- The sentence: which column, at which place, the step where the app loses it and why, what the walk can still read downstream, "The app cannot YET follow it", and "Suggestion:" with what can be done in fact (`DropGate.ways_out`, only the own table of a plot "where nothing is built after it", D-0450). The WHOLE sentence is PROVISIONAL (builder's wording, D-0297).
- A declared entity key is refused only where a later join reads it (D-0448).
- Callers, live: `filter_and_audit_handlers.py:899` (HOME's T3 drop), `session_manager.py:150` (restore), `audit_copy.py:208,390` (`add_step`, `integrity_errors`; `integrity_errors` is reached from cache keys and the orchestrator guard), `recipe_check.py:575` (the checker). Tests: `test_key_drop.py`, `test_uncertain_drop_engine.py`.
- Module text says the engine behaviour with such a drop is proved in `app/tests/test_uncertain_drop_engine.py` ("the table meant, a plain error, or a different table").
- Consumed by (header): `audit_copy.py`, `recipe_check.py`, `session_manager.py`, `filter_and_audit_handlers.py`, `test_key_drop.py` (matches the grep).

### 3.7 `libs/utils/src/utils/declared_plans.py` — LIVE as the fallback of `key_drop`
- `declared_plan_book(graph)` (`:34`, grep): a plan made from the NAMES the recipe declares, without the engine. Used by `key_drop.py:72` when no engine plan is given (`plans is None`). Module text (`:3-5`): "A caller that may not ask the engine (`audit_copy.add_step`, the integrity check, the checker ...)". Callers: `key_drop.py:72`, `remove_from_all.py:237` (test-only path), tests. So: when `plan_book_for_the_gate` gives no plan (a recipe that does not load, `plan_composer.py:67-80`, read in its docstring), the drop gate runs on names only.
- Declared plans do not know types (docstring of `key_drop` `:14-16`: "then a place behind a step the walk does not read ... cannot be followed").

### 3.8 `libs/utils/src/utils/plan_book.py` — LIVE (types only)
- Types `Plan`, `PlanFailure`, `PlanBook`, `PlanBookIncomplete` (`:21`). The book holds one plan per (node, k); a failure is a value (`PlanFailure`). A missing entry raises `PlanBookIncomplete` (`:13-15`). Callers: `plan_composer.py:49` (live), `audit_run`, `declared_plans`, `key_drop`, `step_effects` (tests).

### 3.9 `app/modules/plan_composer.py` — LIVE (the engine's plan of each place)
- `compose_plan_book(orchestrator, recipe_id, loaded, graph)` (`:342`): called by `home_theater.py:377` in `_recipe_plans` (memo `_plans_memo`, `home_theater.py:370-381`).
- `plan_book_for_the_gate(compose, tell)` (`:67-80`, read in part): a recipe that does not load or does not draw as a graph, or a file that cannot be read, gives no book; the rule then reads the names only. A `PlanComposerBug` is shown as `BUG_NOTICE` ("The check of the column could not be run because of an error of the app, not of your recipe. Nothing was changed.", `:63`) and raised again.
- `compose` (`:323`) and `compose_candidate_plan_book` (`:359-369`, read in part: it adds one trial step with `audit_copy.add_step`): **no caller besides the tests**.
- Module text (read, `:2-30`): the plan of every place "composed by the build's own code and never built or stored (LBFB step 0b, D-0325)". "A FAILURE IS A VALUE (D-0176, D-0342)". Two PROVISIONAL choices: (1) a failure below a failing place keeps the engine's sentence and where it first failed; (2) a join with no step and more than one ingredient has no plan (the build says "No step list and no ingredients").
- The planner reads the data files the way the build does (`DataOrchestrator._read_source`, module text `:26`), so opening a plan reads source files (as the module text says, "only a pivot, a sample or a describe read rows while the plan is made").
- Header "Consumed by" lists `app/modules/audit_run.py` (test-only consumer) and `filter_and_audit_handlers.py` (import of `PlanComposerBug` only).

### 3.10 `libs/utils/src/utils/remove_from_all.py` — TEST-ONLY (HOME's dialog does not call it)
- Header (read, `:2-8`): "The option 'remove from all the data' of the HOME audit ... (task AUDIT-REMOVE-FROM-ALL-DATA, step 1; D-0415 part B, D-0416, D-0313)." Decided points (D-0416, read `:6-8`): it reaches every table that holds the key column, also a table no plot reads (1); it is OFF by default, an explicit act (2); the list of tables reached is known BEFORE anything is applied (3); its warning is data agnostic (4); offered ONLY for a removal by the entity key, never another column (D-0415, D-0313).
- Points (read, `:10-27`): (1) offered only for the entity key (declared `is_entity_key`, D-0313, D-0082, or a column a join equates with one, the "key family"); not offered otherwise with a reason. (2) which tables are reached: every table that holds the key at the end of its tier 1, judged from the engine's plan and the lineage links; a table that the app cannot follow is NOT reached and is listed as `unsure`; a table with the same NAME that nothing links to the key is listed as `SAME_NAME_NOT_LINKED` (D-0355). (3) where the step is written: at tier 1 of each reached table, `T1:<table>` (D-0415 B), with the table, the tier, the name and type there, the plots that read it. (4) `apply` writes `modif_filter` with `op: not_in` on the key, `na: keep` (the rule of "none of", `utils.na_choice.default_na`), in the list `audit_steps`; all or nothing. (5) `may_stay`: the one list of every table where the values may stay after the removal (not written; or written but the key passes a step that rewrites values or a step the app cannot read); `apply` returns `Applied.not_written` and `Applied.may_differ`.
- NOT decided, not done here (read, `:41-44`): whether the option reaches a source FILE that no recipe table reads (D-0416, "asked only if the build meets it"); whether the user can untick one table of the list (D-0416); where the unsure and same-name tables show and in what words.
- PROVISIONAL (read, `:46-51`): P1 the words of `WARNING` ("or something alike", D-0416 point 4) and of the not-offered sentences; P2 the entity key is the key family, and a column is judged by NAME when no place is given; P3 `na: keep` and the operator `not_in` (also for one value); P4 a table reached only by an uncertain link is unsure, not reached; P5 `apply` recomputes the option from the original of the audit copy and refuses a stale one; P6 without the engine plan the plan is the one the recipe declares (names only, types empty).
- Callers: only `libs/utils/tests/test_remove_from_all.py` and `app/tests/test_remove_from_all_demo.py` (grep). Dead for the running app.

### 3.11 `libs/utils/src/utils/table_compare.py` — TEST-ONLY
- Header (read, `:2-30`): the comparison of an ORIGINAL and an AUDITED result of the same entry (D-0485, D-0488, D-0489): counts (layer 1), whole-row diff without a key (layer 2), paired view with a verified key (layer 3). "How values are compared: EXACTLY", a tolerance is not decided (`:23`). `max_cells` guard; default "no limit". The module never searches for a key (`:20-21`).
- `compare(...)` (`:355`) has no caller in `app/` or in `libs/*/src` (grep). Tests only: `libs/utils/tests/test_table_compare.py`. The compare of the Compare pane in HOME is the plot baseline, not this module.

### 3.12 `libs/utils/src/utils/join_keys.py` — LIVE (the engine and HOME)
- `join_key_problem` (the one rule, JOIN-KEY-ONE-1): used by `libs/transformer/src/transformer/data_assembler.py:85` (the engine, live) and `libs/blueprint_arch/src/blueprint_arch/join_designer.py:50` (BLUEPRINT, live in the blueprint handler).
- `self_join` / `self_join_text` (`data_assembler.py:131,150`): live.
- `recipe_join_keys` and `key_columns`: used by `session_manager.py:135` (`extract_primary_keys`, live) and by `lineage_walk.py` (`:88`, `JOIN_ACTIONS`, `key_columns`).
- Consumed by (header, `join_keys.py:28`): `data_assembler.py`, `join_designer.py`, `recipe_check.py`, `step_effects.py` (matches the grep).

### 3.13 `libs/utils/src/utils/recipe_tiers.py` — LIVE (the one reading of the tier lists)
- Used by the orchestrator (`orchestrator.py:19`), `cache_keys.py:75`, `opening_build.py:39`, `data_analysis_recipe_validator.py:51`, `plan_composer.py`, `audit_copy.py:58`, `data_wrangler.py:17` (`AUDIT_STEPS`), `blueprint_handlers.py:79`, `export_handlers.py:30` (`plot_targets`, `schema_bodies`). Live.

### 3.14 `libs/utils/src/utils/engine_boundary.py`, `action_names.py`
- Marks and names; not behaviour. `engine_boundary.py:152,172,175` lists `table_compare.py`, `step_effects.py`, `remove_from_all.py` as places of the engine (marks only).

### 3.15 Other lineage-related pieces in the running app (named because they are part of the same area)
- `app/handlers/filter_and_audit_handlers.py:861-925` `_col_drop_to_audit`: the only HOME caller of the drop gate (see 2.4, 2.5).
- `app/handlers/session_handlers.py:673` `split_key_drops` (restore).
- `app/modules/t3_audit_engine.py:9-20` header lists `view_key`, `rows_built_on` etc. (read).
- `app/modules/cache_keys.py:402-422` (`integrity_errors` and the key of an audit copy, grep).

---

## 4. Two ways of doing one thing (found)

1. **Audit representation: three.** (a) The running HOME writes an audit node (`AuditStep` dict in `home_state["t3_audit_steps_by_plot"]`, `session_manager.make_audit_step`) and applies it with `audited_frame` (sections 2.1-2.25). (b) The library `utils.audit_copy` writes an audit step into a copy of the recipe (`audit_steps` list with ids `audit_<hex>_<k>`); nothing in the running app creates such a copy (section 2.27). (c) The export writes the audit into a fork of a join's tier 2 (`build_mode2_recipe`, section 2.29). The rule text (`ui_implementation_contract.md` §7.2 rule 4 and "DECIDED, not built") says the export should hold the audit recipe and replace (c). Both (a) and (b) carry the same operation and reason, in different shapes.

2. **Two stored forms of the same T3 steps in the ghost.** `write_t3_ghost` writes the flat list `t3_audit_steps` and the per-plot dict `t3_audit_steps_by_plot`, the flat one "kept for bw compat" (`session_manager.py:509-523`). Restore reads the per-plot one and puts a flat-only ghost in "__legacy__" (`:572-576`).

3. **Removal of an audit step.** The running app removes by id from every stack (`audit_stack.py:627-682`, the trash icon). The library has `remove_step` for ONE step of an audit copy (`audit_copy.py:245-264`), described as "the one undo control ... 'Remove step'" (D-0314). The text "Remove step" is not in the app (grep). So the decided control and the built one differ (built: per node, linked, no choice of the one step; the library: any one step).

4. **A reason on every step.** The app keeps the reason in each node (`reason`) and copies it to all copies of an id (`audit_stack.py:227-238`). The library keeps `audit_comment` in the step (`audit_copy.py:229`). Two keys for one fact (`reason` in the running app, `audit_comment` in the library).

5. **Plot-changing choices written in two places.** Audit nodes (filter, drop) go to `t3_audit_steps_by_plot` (with a reason, via Apply). The Reshuffle seed and the aesthetic alpha go to `t3_plot_overrides` (no reason, no Apply: `home_theater.py:893-899`, `audit_stack.py:829-837`). Both are exported (report and `t3_steps.yaml`). The rule says the Reshuffle's way is "not decided" (D-0341).

6. **Two ways to clear the exploration filters.** The clearing effect on the view key (`filter_and_audit_handlers.py:181-200`) and the explicit calls of `_clear_exploration_filters` (`:160-170`, from Send to Audit, Reset, T3 apply). Both empty the same two lists; the notice comes only from the effect.

7. **Two ways to read a T1 table.** `_resolve_t1_lf` (`home_theater.py:327-348`) calls `materialize_tier1` for the plot's target; `tier1_anchor()` (`:333`) is the shared calc used when there is no spec. The opening (`opening_build.run_opening`, `:262`) builds the same tables again at opening; both read the same stored key.

8. **Two ways to build a stored table: at opening and on first need.** The opening builds and stores every table (`opening_build.py:262-271`, from `home_theater.py:2513`); a plot's table that is not stored is built again when the plot asks (`_resolve_active_lf` → `materialize_tier2/3`). The rule text (§1 `rules_data_engine.md`) says "Today the tables are built when a plot first needs them" (stale for the opening, see 5.4).

9. **Two sources of the plan.** The engine's plan (`plan_composer.compose_plan_book`, `plan_book`) and the names the recipe declares (`declared_plans.declared_plan_book`). The drop gate uses the second when the first is not available (`key_drop.py:72`, `plan_book_for_the_gate` returns None).

10. **Two source-table caches.** `_source_memo` in HOME (`home_theater.py:461-483`, 8 entries, not stored) and `read_source` (`orchestrator.py:298`, reads the file again each call). The memo key includes the data batch hash and the recipe sha.

11. **Two notices for the same clearing.** The recipe-change notice (`filters_cleared_notice`, `t3_audit_engine.py:55-66`) and the view notice (`view_change_notice`, `:84-102`). Both are shown by the same effect.

12. **Exclusion as a type and as a filter.** `exclusion_row` is listed in `_REASON_REQUIRED` (`audit_stack.py:51`), in `node_blocks_apply` (`session_manager.py:191`), in `KNOWN_AUDIT_STEP_TYPES` (`renamed_keys.py:184`) and in the dialog title (`filter_and_audit_handlers.py:997`), but the app never writes it (section 2.2). The engine (`audit_steps_in_order`, `t3_audit_engine.py:763`) treats it as a filter. The `remove by key` of the rule is the filter with `not_in` (`remove_from_all.py:23-24`, `audit_copy` module text).

13. **Key drop check: two rules, one name.** HOME asks the drop gate for a T3 place (`filter_and_audit_handlers.py:899`), where the gate cannot refuse (section 2.5). The same gate with a T1 place would refuse; HOME never offers a T1 drop.

---

## 5. Texts on screen that state a limit, and rule texts that describe this area (with the code's status)

### 5.1 Texts on screen (read; the wording as in the code)
| Where | Text | Limit it states |
|---|---|---|
| `home_theater.py:1479` | "Audit steps apply to the plot's table (T3) for now." | "for now": steps only at T3 (rule §2: DECIDED, not built, T1/T2 steps). |
| `filter_and_audit_handlers.py:694` | "To create an audit step, view T3." | Steps only from T3. |
| `filter_and_audit_handlers.py:674-676` (title) | "...applies only to T3, and cannot be silently discarded once committed." | "T3 only". The trash button removes a committed step (`audit_stack.py:530-534`), so "cannot be discarded" is not what the screen does. |
| `filter_and_audit_handlers.py:666-667` (title) | "...Not written to the audit log, and not exported." | Exploration never exported. |
| `filter_and_audit_handlers.py:696` | "Audit: a step you send changes the plot and is exported." | Exported. |
| `filter_and_audit_handlers.py:698` | "Exploration: filters change this table only, never a plot. Nothing here is exported." | Exploration filters never a plot. |
| `filter_and_audit_handlers.py:997` | "Add N filter/exclusion(s) — choose scope" | Names "exclusion" which the app never writes. |
| `filter_and_audit_handlers.py:1004-1007` | "One or more nodes target a join key. Removing rows here changes which samples appear in joined plots." | Join-key warning. |
| `filter_and_audit_handlers.py:1015-1018` | "⚠ <plot> — column not in plot data; will be SKIPPED" | A plot is skipped for a propagated step. |
| `filter_and_audit_handlers.py:1046-1047` | "A skipped plot is NOT filtered — it shows the unfiltered data." | Skipped plots show unfiltered data. |
| `filter_and_audit_handlers.py:1188-1194` | "N audit entry(ies) added across M plot(s). Skipped (column not in plot data): ..." | Same. |
| `filter_and_audit_handlers.py:1151` | "No target plots selected. Audit pipeline unchanged." | - |
| `filter_and_audit_handlers.py:889-892` | "No deselected columns to drop. Uncheck columns above first." | Drop = deselect. |
| `filter_and_audit_handlers.py:903` | "⛔ <DropGate problem>" (the refusal sentence) | "The app cannot YET follow ..." (if so). |
| `t3_audit_engine.py:100-101` (notice) | "The filters were removed because ... A filter is built on the table you view, so it is not kept when that table changes. Audited steps are kept." | Filters not kept across view change. Docstring: PROVISIONAL words. |
| `t3_audit_engine.py:64-66` (notice) | "The filters of the previous recipe were removed because the recipe changed ..." | - |
| `t3_audit_engine.py:97-99` (why texts) | "Audit mode builds audit steps; exploration filters do not exist there" / "a filter belongs to the table it was built on" | - |
| `home_theater.py:1174-1205` (tooltips) | "T3: ... If it has none, T3 = T2." / "Exploration: ... never the plot ..." / "Audit: ... They change the plot, are saved with the session and are exported." | Mode meaning (PROVISIONAL slice B wording, `:1169`). |
| `view_badge.py:111` | "no audited step for this plot yet: identical to the Result" | - |
| `audit_stack.py:452` | "No T3 adjustments for <plot> yet." | - |
| `audit_stack.py:502` | "⚠ Primary key — Primary ID/Key alignment" | Only the title; the explanation of §12g.6 is not in the code. |
| `audit_stack.py:533` (title) | "Delete this audit node (linked: removes from all plots)" | Linked delete. |
| `audit_stack.py:558-561` | "N orphaned node(s) from a legacy ghost. Delete or re-target manually." | Re-target is not a control in the code (grep: no re-target). |
| `audit_stack.py:266` | "Nothing was applied: N step(s) have no reason (...)" | - |
| `audit_stack.py:688` (code comment, not on screen) | "T3 nodes are authored in the left panel (filter rows) or via Gallery clone." | Stale: the Gallery clone was removed (ADR-093, rule §12e). |
| `export_handlers.py:675-692` | Mode 2 toggle: "...a bundle exported without this box checked cannot be imported, only verified against its effective_run.yaml." | Import needs this box. |
| `export_handlers.py:1615-1620` | "N plot(s)' T3 steps could not be fully baked into the reproducibility recipe ... still in the Publication content, just not engine-replayable yet." | "yet", and the plot is skipped from the replay. |
| `export_handlers.py:1605-1612` | "...This reproducibility bundle includes your actual raw data files, not just hashes..." | Raw data copied (sensitive, code comment `:1573-1574`: "#46, not built here"). |
| `opening_build.py:110, 114-115` (texts) | progress "Opening 'x': tables N of M, plots K of L"; large-data warning | PROVISIONAL (D-0334; D-0336), `:110-115`. |
| `plan_composer.py:63` | "...could not be run because of an error of the app, not of your recipe. Nothing was changed." | - |
| `lineage_sentences.py:53` | "The app cannot YET follow this column through this kind of join (...)" | "YET" is decided (D-0454); the rest PROVISIONAL. |
| `session_manager.py:166-185` (`key_drop_notice`) | the restore notice for refused drops | PROVISIONAL wording (`:169`). |
| `session_manager.py:223` (`session_format_problem`) | "...was saved by an older version of the app and cannot be opened. Delete it and start a new session." (the sentence, from `bundle_importer` test text) | PROVISIONAL wording. |
| `home_theater.py:1964` (Test Lab, not this area) | "instructions coming soon." | Out of scope; noted only. |

### 5.2 Rule texts: "DECIDED, not built", "PROVISIONAL", and what the code does (rule text vs code)

**`.claude/rules/ui_implementation_contract.md`**
- §1 "Disable (Strikethrough)" (Power icon): "Not implemented (2026-11-07, finding F-07)". Code: no control; no write of `active` = False (section 2.12). Built status: not built.
- §1 "Trash (Permanent)" for a Violet node: a modal "CRITICAL: Removing a blueprint step may break the intended visualization. Are you sure?" Code: the text is not in `app/` (grep). Not built.
- §1 "Removing an audit step (D-0314): ONE undo control, 'Remove step' ... no revert control". Code: per-node linked trash; no "Remove step" text; `remove_step` is test-only (section 2.13). Built differently.
- §1 "Position awareness: nodes above or below Violet nodes = pre- or post-transform" and the "Direct pass-through" rule: not checked here.
- §2 "DECIDED, not built: an audit step written at T1 or T2 of a table, chosen in the audit dialog by tick lines (D-0022, D-0316, D-0318, D-0337, D-0346, D-0347). Today ... 'Audit steps apply to the plot's table (T3) for now.'" Code: not built; the line is shown (`home_theater.py:1479`).
- §2 "PROVISIONAL P-B1" data choice starts on T3; "mode default is not decided: PROVISIONAL" (`server.py:143`). Built as stated.
- §2 "Clearing on a plot-tab change, on a mode switch and on a recipe change is as built and PROVISIONAL (filter_and_audit_handlers.py:168-174)". The line numbers are stale: the effect is at `:181-200` (`:172-179` is its comment). The behaviour matches the rule.
- §2 "Each panel title carries a badge ... 'Viewing: T2', 'Plot: Result', 'Plot: Audited'" — built (`view_badge.py`).
- §2 "Pipeline Audit (Right) ... In HOME the panel is closed in Exploration ... opens in Audit mode" — built (`frame_widths` via `home_theater.py:1401-1425`).
- §2 "Value box redraw ... PROVISIONAL" — built, `t3_audit_engine.py:356-411` (read in part, `:411` comment PROVISIONAL FILTER-PICKERS-1 point 8).
- §4 table row "Filters panel Apply ... NONE (Transient)" — built (`filter_and_audit_handlers.py:776-788`).
- §4 "Ref Table Drop in Tier 1 or Tier 2 Table: visual-only drop" — not checked here.
- §4 "This replaces the tier_toggle gate of ADR-085" — built (the strip uses `data_view`, `home_mode`).
- §5 "The strip is absent only when interactivity_enabled: false" — built (`home_theater.py:1217`).
- §8 "Operators by column type ... Comparisons on text, date and true/false columns are not decided and not offered." — the code offers EVERY comparison and `between` on a date (PROVISIONAL FILTER-PICKERS-1 point 2, `t3_audit_engine.py:321`), and only equal / not equal on true/false (`:318`). Rule and code differ on dates (section 1.14).
- §8 "Value type rule ... a date is kept as year-month-day text" — built per the docstring (`filter_and_audit_handlers.py` and `t3_audit_engine.py` read partly; not verified line by line).
- §8 "For the owner, not decided: the typed value at a change of kind ... a change of plot tab, which resets the box" — built as described (PROVISIONAL, the builder's choice, `t3_audit_engine.py:484` for the start values).
- §12a "DECIDED, not built (D-0322, D-0329, D-0332): the check of an audit recipe refuses any audit step that is not a filter, a column drop or a removal by key ... On dev today the audit copy, in memory only (`libs/utils/src/utils/audit_copy.py`, slice A) ... the `audit_steps` / `audit_comment` form is on a branch, not merged." Code: the form IS on dev (`audit_copy.py`, `recipe_tiers`, `data_wrangler.py:17`, `orchestrator.py:80-100`); the rule's "on a branch" is not true of this branch (section 2.28). Check.
- §12a "DECIDED, not built: the keys are not read from a file yet; D-0354." Code reads `audit_steps` in the engine (section 2.28). Check.
- §12a table row `developer_raw_yaml` (node type) and the gatekeeper line "btn_apply is locked if any filter_row, exclusion_row, drop_column, or developer_raw_yaml node has an empty reason field." Code: the type is refused as a removed key (`renamed_keys.py:186`: "it held a raw fragment of a recipe, and no screen created it any more"); not in the gate. The rule text is stale.
- §12a "Plot Style panel not mounted (2026-11-05, fork issue #15)". Built as not mounted (section 2.14).
- §12a "column_visibility toggle ... there is no ..." — consistent with the code (no such toggle; drop is `lf.drop`).
- §12c "Design intent (not yet built, F-07): ... deactivated `active: false`" — not built (section 2.12). The export warning for deactivated nodes (blocking dialog) is not in the code (grep "deactivated" not checked; treat as not built).
- §12d Ghost slots: the T1/T2 ghost (`assembly.json`, written once) and the T3 ghost (on every Apply) — written (`session_manager.py:335-360`, `audit_stack.py:291-296`). "Prepped Chef" restore: not checked here.
- §12g.2 "DECIDED, not built as described (D-0313, D-0082): both lists exist ... the entity key (is_entity_key) ... and columns used to join." Code: only the join-key list (section 2.19).
- §12g.3 table: "Drop column | join key that a later join still uses | BLOCKED by place (built 2026-11-20, merge 8772f368, key_drop.py)." The gate is built (section 3.6). In HOME the drop is asked at a T3 place where nothing is built after it, so the block does not occur for HOME drops (section 2.5). Built, with a HOME path that cannot reach the block.
- §12g.3 "A declared entity key that no later join uses is not refused for being declared (decided 2026-11-21, D-0448 ...; the mark PROVISIONAL in the code is to be removed when that code is next touched)." Code: the decision is in the module text (`key_drop.py:27-28`, `lineage_walk.py:63-64`); the PROVISIONAL mark is not checked here (grep-able).
- §12g.4 "DECIDED, not built: the Create audit step dialog that replaces this one (D-0316, D-0318, D-0325, D-0337, D-0346, D-0347, D-0451): every place the step can reach is ticked when the dialog opens ... lines per distinct table ... a walk of the lineage ..." Code: not built; the walk is test-only (section 3.3); the built dialog is the three-scope propagation modal (section 2.6). The rule also says "whether it is ticked when the dialog opens is not decided (D-0451)".
- §12g.4 "The three scope options above are what is built today." Built (`filter_and_audit_handlers.py:1056-1066`).
- §12g.5 `primary_key_warning`, `plot_scope` — built (`session_manager.py:102-103`, `filter_and_audit_handlers.py:1175-1181`).
- §12g.6 "A primary-key-warning node renders with a yellow banner above the params summary ... 'This filter targets a join key ...'" — the banner exists (`audit_stack.py:501-504`) but the explanation sentence is not in the code (section 2.11). Partly built.
- §12g.7 "pending nodes carry plot_scopes_intent ... '__all_at_apply__' ... expand on btn_apply". Not built: the code expands at the confirm (`filter_and_audit_handlers.py:1166-1184`); no intent field (section 2.7). The comment at `home_theater.py:287` still says the field exists.
- §12g.8 "Backward-compat: a flat ghost ... '__legacy__' ... show a notification on restore: 'Loaded a legacy T3 ghost — N nodes are orphaned ...'" Code: the bucket is built (`session_manager.py:572-576`) and the orphan list exists (`audit_stack.py:555-562`). The notification text is not found in the code (grep). Partly built.
- §12g.8 "Orphaned nodes after data analysis recipe restructure ... flagged at restore time and listed under 'Orphaned' ..." Partly: the orphan text (`audit_stack.py:558`) exists; the flagging at restore is not checked here.
- §12g.9 "Render-side behaviour (designed 2026-05-10): aesthetic_override nodes ... were never applied to the rendered plot until VIZFAC-T3-OVERRIDE-1 ships." Code: applied in the audited plot (`home_theater.py:714-734`) and in the export (`export_handlers.py:1301-1303`). The rule text is stale. Note: the aesthetic panel is not mounted, so the only producer is the Reshuffle pin (section 2.15) and the session restore.
- §12g.10 "Undo and re-include: the user undoes by deleting the audit node; ... deleting a node from one plot deletes it from every plot." Built (section 2.13).
- §12g.11 "the export report marks primary-key nodes with '⚠️ [Primary key affected]'" — not found in the code (grep: "Primary key affected" not in `app/`). Not built.
- §13 "home_state" fields — built (`orchestrator_helpers.py:53-58`, `home_theater.py:1421`).

**`.claude/rules/rules_data_engine.md`** section 1
- "Tier 1 — Persistence: `pl.sink_parquet("tmp/session_anchor.parquet")`." Code: stored at `user_data/anchors/<collection>.parquet` (`home_theater.py:336-337`, `orchestrator.py` tier 1). Rule text stale (no "DECIDED" marker).
- "Tier 2 ... Implemented 2026-11-06 (fork issue #10)." Built (`home_theater.py:515`).
- "Tier 3 — Execution (built) ... Today it is not stored." The code stores a T3 table of a plot that has tier-3 steps next to the T2 of its target (`orchestrator.py:725`, `:742-749`, `tier3_path_for` `:37-40`); a recipe handed in (an audit copy) is not stored (`:734-736`). The rule's "not stored" is stale for HOME.
- "The opening of a recipe (DECIDED, not built): at the opening the app builds and stores by key every tier 1 and tier 2 table and the tier 3 table of every plot ..., draws every plot once ...; an error of the original recipe found while building is reported through the load gate with a plain reason; a later open with equal keys rebuilds nothing (D-0326, D-0335, D-0343)." Code: BUILT and wired (`opening_build.py:1-45`, `opening_handlers.py:124`, `home_theater.py:2513`, `bootloader.py:556-582` for the rejection). The label "DECIDED, not built" is stale.
- "Today the tables are built when a plot first needs them." Partly true: the on-demand path exists beside the opening (section 4.8).
- "With a lot of data ... the number of rows that triggers the warning is not decided (D-0336)." Code: `opening_build.py:41-43` "The value is decided: 1,000,000 rows per plot (D-0363, ...)". The ledger line D-0363 (grep, `decision_ledger.md:397`): "The number of rows per plot that triggers the large-data warning is 1,000,000; the provisional value stays. [Review session's wording, not her words.]". So the rule says "not decided", the code says "decided", the ledger line is the review session's wording. **Contradiction to check.** The status field of D-0363 was cut off in the grep; not read.
- "A test shows that a recipe with a plot that cannot be drawn is refused at opening (D-0327)." Built (`opening_build.py:146-160` `draw_plot_proof`; test name not checked here).

**`.claude/rules/rules_ui_dashboard.md`** sections 1, 3, 4
- §1 "T3 = Publication Finisher ... Tier 3 scope is permanently locked to row filters, row exclusions, column visibility, aesthetic overrides, and BLUEPRINT's own YAML escape hatch (`developer_raw_yaml` ...)". Code: `developer_raw_yaml` removed (`renamed_keys.py:186`); "column visibility" is a preview only (`home_theater.py:1696-1700`), the drop is permanent. Stale wording in the list.
- §1 "audit steps IS the Audit Trace ... aesthetic_override nodes are stored separately as t3_plot_overrides" — built.
- §1 "Two Ghost Save Slots ... T3 Ghost on every btn_apply" — built (`audit_stack.py:291-296`).
- §1 "State feedback ... dimming overlay with a 'recalculating' message" — not checked here (grep for "Recalculat" in `app/handlers` not run for this area; the rule `ui_implementation_contract.md` §7 says there is no such overlay for the data import).
- §3 "The Gatekeeper: btn_apply is locked unless all T3 audit nodes have non-empty reason" — built (`audit_stack.py:704-748`, `session_manager.py:188-192`).
- §3 "Calculation Scope: clicking btn_apply executes the 3-stage Polars pipeline and updates only the Active Leaf panes ... Until btn_apply is pressed, the Active Plot remains in a 'Pending' state (blurred or ... 'Recalculate' badge)." Code: no blur or "Recalculate" text found in this area (grep 'Recalculat' in `app/handlers`: only the data import notice, not checked here). Not built as described, treat as not verified.
- §3 "Visualization: until btn_apply is pressed the Active Plot remains in a Pending state" — same as above; not checked.
- §4 "Mode and data choice (D-0016, D-0019, D-0310, D-0327; built 2026-11-20, slice B)" — built (section 1).
- §4 "The Pipeline Builder Scope ... (D-0322; DECIDED, not built as a check on dev)" — the check of the audit recipe is in the library (`audit_copy.py:197-198` `AUDIT_ACTIONS` refusal; `key_drop` by place) and is reached only through the tests and the integrity check; the HOME path does not run it. Partly built.
- §4 "There is no build_polars_pipeline function in the code; in the exported recipe an audit step is written as the registered action modif_filter or polars_drop (libs/blueprint_arch/src/blueprint_arch/t3_translator.py)." Built (`t3_translator.py:73-76`, `:92-160`); the function name is absent (grep not run; consistent with the file read).

---

## 6. Not read / could not tell

- Bodies not read in full: `lineage_walk.py` (only the module text and the call sites), `remove_from_all.py` (module text and the call sites), `key_drop.py` (module text and the functions named), `declared_plans.py`, `plan_book.py` (module text), `join_keys.py` (call sites only), `table_compare.py` (module text and `compare` signature), `lineage_records.py` (module text, not the record classes), `plan_composer.py` (`compose` body not read), `recipe_graph.py` (module text and call sites).
- `app/modules/cache_keys.py` key functions: only the header (1-100) and the grep of the key parts. `_coarse_parts` (`:242`) is a fail-safe that was seen by name only.
- `app/src/bootloader.py` load gate: the function bodies at 431-582 were not read; the names and the docstrings were seen by grep.
- `app/modules/session_manager.py` ghost write (`write_t3_ghost`, `:488-545`) read only in part; the T1/T2 ghost writer (`:335-360`) by its docstring; restore bodies (`:552-720`) not read.
- `app/handlers/export_handlers.py` bundle bodies: the lines 1102-1130, 1296-1303, 1463, 1550-1630 were read; the rest only by grep.
- `app/handlers/home_theater.py` `_make_cmp_baseline_handler` (`:755-816`), `_plot_seed_ui` (`:901-917`), `_handle_unpin` (`:919-943`): seen by grep and partly read; the texts inside were not all read.
- `t3_audit_engine.py` `value_box_kind`, `ops_for_column` bodies (`:299-411`): only the comments with PROVISIONAL marks and the docstrings were read.
- `sweep_orphan_tier3` (`opening_build.py:193-200`) is called at `:252` (read); its behaviour not read.
- Whether the Compare pane (`home_theater.py:755`) and the T1/T2 table of the Compare use `table_compare`: no (grep: no import).
- The restore text "Loaded a legacy T3 ghost ..." and the marker "[Primary key affected]" in the export: grep only, not found in `app/`.
- The "Recalculating" overlay (rules §3 of `rules_ui_dashboard.md`): not checked in the code for this area.
- Tests: none run. Test names in the entries are only those named by the files (grep). The test status of `app/tests/test_audit_run.py`, `libs/utils/tests/test_remove_from_all.py` etc. is "test-only" from the grep of imports; that they pass was not checked.
- The ledger status (DECIDED, PROVISIONAL, RELAYED) of the numbers cited was not checked except D-0336 and D-0363 (grep of their lines; the status field of D-0363 was cut off in the grep output). The ledger numbers quoted in the code were taken as the code writes them.
- Blueprint's use of the lineage and of `join_designer` (BLUEPRINT is not this area): only the imports were noticed.
- Gallery and Test Lab: out of area.

---

## 7. Summary of what matters most (for the design agent)

1. **Three audit representations** exist: the HOME audit node (live), the library audit copy (no running caller; section 2.27), and the export fork of a join's tier 2 (live when the box is ticked; section 2.29). The rule text (§7.2, "DECIDED, not built") wants the export to hold the audit recipe.
2. **"for now" limit on screen**: "Audit steps apply to the plot's table (T3) for now." (`home_theater.py:1479`). Every T1 and T2 audit step is "DECIDED, not built" in the rule text.
3. **The lineage walk and the rest of the lineage library are test-only** except `key_drop` (drop gate) and its helpers (`lineage_records`, `lineage_sentences`, `lineage_walk.LineageIndex.drop_facts`, `declared_plans`, `plan_book`, `plan_composer`, `recipe_graph`, `step_effects`, `join_keys`). `remove_from_all`, `table_compare`, `walk()`, `audit_run.run_audit` and `audit_copy.add_step/remove_step/start_audit` have no caller in the running app.
4. **Rule texts that say "DECIDED, not built" for things that are built**: the opening of a recipe (`rules_data_engine.md` §1; built in `opening_build.py` and `opening_handlers.py`, wired at `home_theater.py:2513`), and the aesthetic overrides "never applied" (`ui_implementation_contract.md` §12g.9; applied at `home_theater.py:714-734`). Rule texts that describe removed things as current: `developer_raw_yaml` (`ui_implementation_contract.md` §12a and `rules_ui_dashboard.md` §1; removed, `renamed_keys.py:186`).
5. **The HOME drop check cannot refuse**: `filter_and_audit_handlers.py:895-899` asks the gate at place `T3:<plot>`, where a comment says it finds nothing to refuse; the rule §12g.3 says a join-key drop is "BLOCKED" in HOME.
6. **Reshuffle and alpha write plot changes without a reason or an audit node** (`home_theater.py:893-899`, `audit_stack.py:829-837`); both reach the export through `t3_plot_overrides`.
7. **Date filters**: the rule (§8) says comparisons on dates are not offered; the code offers them (PROVISIONAL, `t3_audit_engine.py:321`).
8. **Stale header texts in code**: `recipe_graph.py:55-61` ("nothing runs yet"), `step_effects.py:38` (consumers), `audit_stack.py:688` ("Gallery clone"), `home_theater.py:287` and `orchestrator_helpers.py:53` (`plot_scopes_intent`, which is never written), `filter_and_audit_handlers.py:997` ("exclusion").
9. **Ledger**: D-0363 (1,000,000 rows) is cited in the code as "decided"; the rule says the number is "not decided" (D-0336); the ledger line says "Review session's wording, not her words".
