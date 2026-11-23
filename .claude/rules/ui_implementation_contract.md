**Status:** FINALIZED / ARCHITECTURAL LOCK — Phase 25 complete. Last update: 2026-05-09 (ADR-073: sidebar slot registry — §11 replaced; REVIEW decisions closed). Updated 2026-11-20 to Eve's decisions (ledger D-0350): the HOME mode and data choice, filters, sessions and the audit (§1, §2, §4, §5, §7, §8, §12, §13); what is decided but not built is marked "DECIDED, not built".

# UI Implementation contract

## 1. The Tier 3 "Branching & Blueprint" Logic

Tier 3 is the plot's own stage: T1 feeds T2 feeds T3 feeds the plot (D-0179). T3 is T2 plus the plot's own tier 3 steps of the recipe; with no such steps T3 equals T2 (D-0343). An audit adds steps to a copy of the recipe and never changes the recipe's own steps (D-0021, D-0102).

- **Node Inheritance**: Copied T2 nodes are **Violet** (#f3e5f5). New user nodes are **Yellow** (#fffde7).
- **Position Awareness**:
  - Nodes dragged **ABOVE** Violet nodes = Pre-transform (Wide Data/T1 filters).
  - Nodes dragged **BELOW** Violet nodes = Post-transform (Long Data/T2 filters).
- **The Deletion & Deactivation Protocol**:
  - **Disable (Strikethrough)**: A "Power" icon allows the user to toggle a node off. The node remains in the UI with a strikethrough effect but is ignored by the Polars engine. **Not implemented (2026-11-07, finding F-07):** `audit_stack.py` reads `node.get("active", True)` to render the strikethrough style, but nothing in the running app ever sets `active` to `False` — there is no Power-icon control wired up. Tracked as task STM-NODE.
  - **Trash (Permanent)**: A trash icon allows for removal. If the node is **Violet**, a modal triggers: _"CRITICAL: Removing a blueprint step may break the intended visualization. Are you sure?"_ **As built:** deletion is real list removal (`audit_stack.py:585`, `[n for n in nodes if n.get("id") not in ids_to_delete]`), not a soft `active: false` mark — see §12c below, which this contradicted until F-07.

- **Removing an audit step** (D-0314): the audit offers ONE undo control, "Remove step": the user picks any step in the list and removes it; there is no "remove last" and no "remove all" (no Full Wipe, no `btn_revert`). **As built:** each committed step has a trash button (`audit_stack.py`, `t3_delete_<id>`) that removes that step and its linked copies; no revert control exists in `app/`.
- **Direct Pass-Through**: If the T2 data analysis recipe contains zero transformation steps (T2=T1), the audit steps starts **Empty**.

## 2. Shell Architecture (The 3-Zone Navigator) — Updated ADR-043/ADR-044 (2026-04-23)

The UI implements a high-density **3-column nested shell** to maximize screen real estate. The right column (Pipeline Audit) is **flag-gated** and suppressed entirely for lower app features files (see ADR-044):

- **Left Sidebar**: Accordion of named panels: Data analysis recipe Choice, Data Import, Filters, Export (gated — scope toggle), Session Management (gated). Panels are context-reactive — filter widgets are scoped to the active plot sub-tab's `plot_spec` aesthetics. Uses a Dark Grey (#c0c0c0) background.
- **Home Theater (Center)**: The primary workspace. Structure (post-ADR-043):
  - Top-level tabs are **exclusively** driven by data analysis recipe `analysis_groups` — no hardcoded tabs (Inspector removed).
  - Each group tab contains `navset_underline` sub-tabs (one per declared plot), wrapped in a **collapsible accordion panel**.
  - A **separate collapsible accordion panel** below shows the data preview (the table chosen in "Table to view").
  - A header strip with the mode switch **Mode: Exploration | Audit** and the data choice **Table to view: Source | T1 | T2 | T3** (D-0016, D-0310). The data choice controls the data preview; the plot follows the mode (D-0019, D-0327). Details below.
  - Uses a Neutral Grey (#d1d1d1) background.
- **Pipeline Audit (Right)**: Audit trail for T2 blueprint and T3 sandbox transitions. **Visible only for ≥ `pipeline-exploration-advanced`**. When hidden, the theater column expands to fill the full layout width — the layout element itself is excluded, not merely hidden via CSS. Uses a Dark Grey (#c0c0c0) background. In HOME the panel is closed in Exploration (it is empty if the user opens it by hand, D-0383) and opens in Audit mode, closing again when the user leaves it (D-0375, D-0385); in the other user spaces it is open (D-0381). As built; the widths and the drag are in `rules_css_style_spec.md` section 12 (values PROVISIONAL, D-0386).

**Data analysis recipe-Driven Tab Rule**: Home tabs and sub-tabs MUST derive exclusively from `analysis_groups` in the active data analysis recipe. No hardcoded tab names or fallback tabs are permitted (ADR-003/ADR-004 compliance).

**Header strip: the mode and the data choice (D-0016, D-0019, D-0310, D-0311, D-0327; built 2026-11-20, slice B).**

The two choices "Data to show" and "Plot to show" of ADR-086, the view "My view" and Compare as a third plot value are gone (D-0179, D-0180). There is no "My view" any more.

> **Implementation status:** built (`app/handlers/home_theater.py`, the strip in `dynamic_tabs`; `home_mode` and `data_view` in `app/src/server.py`). The strip exists only with `interactivity_enabled`. Without it there is no strip: the plots show the Result and the table shows T3 (as built; the choice of T3 there is the builder's, not a decision).

| Table to view | Data pane | Gate |
|---|---|---|
| **Source** | A source table as read from the file; the list "Source table" (shown only while Source is chosen) picks which one | `interactivity_enabled` |
| **T1** | The plot's table after tier 1 | `interactivity_enabled` |
| **T2** | After tier 2 (T2 equals T1 when there are no tier 2 steps) | `interactivity_enabled` |
| **T3** | The table the plot is drawn from: T2 plus the plot's own tier 3 steps (T3 equals T2 when there are none; D-0310, D-0343) | `interactivity_enabled` |

| Mode | What the user sees | Gate |
|---|---|---|
| **Exploration** | One plot, the Result: the recipe's plot, drawn from T3; an exploration filter never changes it (D-0019, D-0180, D-0327). The data table shows the chosen table; filters are built on it and change only it (D-0178, D-0310). No "Send to Audit", no column drop. Nothing here is saved or exported. | `interactivity_enabled` |
| **Audit** | The audited plot. A **Compare** switch shows "Original" and "Audited" side by side. Under T3 the table is the audited table; Source, T1 and T2 show the originals. "Send to Audit" and the column drop are offered only while T3 is viewed; no preview Apply. | `t3_sandbox_enabled` (Compare: `comparison_mode_enabled`) |

Defaults, as built (`app/src/server.py:140-141`): the mode starts on Exploration, the data choice on T3 (PROVISIONAL P-B1, `server.py:138-139`). D-0310 offers the four data choices and says what a T3 plot is drawn from; it does not state the default: the data choice default is PROVISIONAL, and the mode default is not decided: PROVISIONAL. Without `t3_sandbox_enabled` the mode switch is absent and the app is always in Exploration. A restored session that holds audit steps opens in Audit mode. The Reshuffle button of a plot with a random layer is offered only in Audit mode (D-0341).
When the viewed table changes, the exploration filters are removed, with a notice; they are not kept, not checked and not carried (DECIDED: D-0311; D-0178 says the same for the view). The filter belongs to the table, not to the plot (DECIDED, D-0505, D-0506; built): the key of the view (`view_key`) holds the table the open plot reads (`viewed_table`: the target table, plus the plot itself only on T3 and only when the recipe writes tier-3 steps for it), so a change to a plot that reads the SAME table keeps the staged rows, the typed value and the applied filters, and says nothing; a change to a plot that reads another table clears them with the notice ("you opened a plot that reads another table", wording PROVISIONAL). T1 and T2 of a table that has no tier-2 steps are the same table, yet the filters are cleared when the data choice changes between them, because the data choice is in the key (D-0311: "when the viewed tier changes"); PROVISIONAL: the builder's choice, not a decision of the owner; the alternative is that a change between T1 and T2 of a table without tier-2 steps keeps the filters, by a literal reading of D-0506. A switch between Exploration and Audit mode clears them (DECIDED, D-0361). A change of recipe clears them (as built, ADR-099 point 1; not restated in the owner's words of this slice); `home_preview_filters.md` point 8 says the opposite for a mode switch and is superseded by D-0361.
Each panel title carries a badge stating what it shows ("Viewing: T2", "Plot: Result", "Plot: Audited"), with "identical to" lines (e.g. "T2 identical to T1" when the dataset has no tier-2 steps; `app/modules/view_badge.py`). The badge is never part of an exported plot image.

**DECIDED, not built:** an audit step written at T1 or T2 of a table, chosen in the audit dialog by tick lines (only distinct tables are lines, each with its reach) found by a walk of the lineage (D-0022, D-0316, D-0318, D-0337, D-0346, D-0347). Today an audit step is written at T3 of the plot, and the strip says so ("Audit steps apply to the plot's table (T3) for now.").

**The two facts of every data preview (D-0488; built; the WORDS are PROVISIONAL).** The note line next to the preview title (the badge, `app/modules/view_badge.py`, output `home_data_preview_badge`, an output of its own that never mounts the column chooser, section 14 R4) always says how many rows the table has and, when the column chooser hides columns, how many. Rows: "N rows", or "Showing 100 of N rows" when "All rows" is off and the table has more than 100 rows; N is counted (lazily) on the same lazy table the grid is cut from, after the audit steps (Audit mode, T3) or the exploration filters, so a filter lowers it. Columns: "N column(s) hidden; add them back in the column chooser"; in Audit mode on T3 "N column(s) not shown, not dropped; ..." (an unselected column is only a candidate for an audit drop); a column already dropped by an applied audit step is not counted; an empty choice hides nothing (the grid then shows every column). A table that cannot be built gives no sentence (its error is in the table's place). The limit 100 is `PREVIEW_ROW_LIMIT`, used by the cut, the title and the sentence. The grid's own summary line is off: it counted the 100 rows it was handed ("Viewing rows 1 through 9 of 100") and read as the table's total. Without `interactivity_enabled` the preview says the row count only. The hidden-columns sentence is shown only when the chooser was built for the table now shown: the chooser carries the key of its table (a hidden input, `preview_col_selector_key`, one function `_chooser_key` in `home_theater.py` gives it and the badge's own key; the key names the open recipe and the data it was built on, the plot, the data choice, the source table and the audited drops, so a switch of recipe or a data refresh also changes it) and the badge compares the two; right after a switch of table, plot tab or recipe, while the chooser is still the previous table's, only the row sentence is shown (D-0050). The "All rows" switch sits in the header of the data panel and a click on it does not fold the panel (`app/src/www/preview_switch.js`; PROVISIONAL: the builder's fix; the alternative, the switch outside the header, is the owner's choice).

**Collapsibility Rules**:

- Plot accordion panel: default **expanded**. User-collapsible. Collapse state MUST persist across sub-tab navigation.
- Data accordion panel: default **expanded**. User-collapsible. Collapse state MUST persist across sub-tab navigation.
- Column picker (T3 sandbox): MUST span `width: 100%`, `flex: 1 1 100%`. MUST NOT wrap to multiple rows.

## 3. The Mandatory Audit Gatekeeper (The Gate)

Reactivity in the Active Leaf (Right side) is strictly gated by documentation to ensure scientific reproducibility

- **Logic**: Every user action (Filter, Column Drop, Node Addition in Tier 3) generates a node that **MUST** have a comment.
- **Comment Mandate**: Every Yellow node (and modified Violet node) MUST have a non-empty string in its `comment_field`.
- **Execution Rule**: The **btn_apply** state is disabled if:
 	- **Disabled (Grey)**:
  1. No changes detected/made OR comments are missing (`audit_pending == False`).
  2. Any node in the stack (excluding disabled ones / and ones inherited by tier 2) has an empty comment field.  
  - **Active (Orange/Green)**: Changes detected AND all nodes have comments.
- **Calculation Scope**: Clicking **btn_apply** executes the 3-stage Polars pipeline and updates only the **Active Leaf** (Right) panes.
- **Visualization**: Until **btn_apply** is pressed, the **Active Plot** remains in a "Pending" state (e.g., blurred or overlayed with an orange "Recalculate" badge).

## 4. Interaction & Event Mapping

| **UI Event**                 | **Resulting Action**               | **Audit Entry**         |
| ---------------------------- | ---------------------------------- | ----------------------- |
| **Brush on Active T3 Plot**     | Filter rows in T3 data.            | Automatic Yellow Node   |
| **Col Drop in Active T3 Table** | `df.drop_columns()` in T3.         | Automatic Yellow Node   |
| **(Advanced Filter) in active T3 Table**        | Filter cols in T3 data. | Automatic Yellow Node   |
| **Drag Node**                | Reorder Polars operation sequence. | Update `audit_pending` |
| **Filters panel "Apply"** (Exploration) — commits to `applied_filters` | Changes only the data table viewed (Source, T1, T2 or T3), never a plot (D-0327). Never written to Parquet, never saved, never exported. Removed when the viewed table changes (D-0311). | **NONE** (Transient) |
| **Filters panel "Send to Audit"** — Audit mode, T3 viewed, `t3_sandbox_enabled` | Promotes staged rows via the propagation modal. | Automatic Yellow Node (reason-gated) |
| **Ref Table Drop**  in Tier 1 or Tier 2 Table              | Visual-only drop for inspection. | **NONE** (Transient) |

**Exploration filters and audit steps (D-0016, D-0178, D-0311, D-0327; built 2026-11-20, slice B).** An exploration filter (`applied_filters`) is built on the table viewed and carries the key of that view; it changes only that table and is never applied to a plot, to a stored table or to the export (D-0327). A filter built on another view is not applied (`t3_audit_engine.rows_built_on`, `home_theater._applied_for_view`). Audit-committed nodes (`_t3_filter_rows()`/`_t3_drop_columns()`) are applied only in Audit mode, on top of the T3 table; Source, T1 and T2 always show the originals (D-0021). Any new render function that reads either list MUST apply the same gates. This replaces the `tier_toggle` gate of ADR-085 and the rule of ADR-098 that exploration filters change the plots on My view (D-0179, D-0327).

## 5. The Theater Layout Model (Updated ADR-043, 2026-04-23; ADR-085, 2026-08-10)

The theater layout is controlled by the mode (Exploration or Audit, which decides the plot) and the data choice "Table to view" (which decides the data preview) (D-0016, D-0310; built 2026-11-20, slice B). There is no "My view" any more (D-0179); see §2 for the strip.

**Plot area** (driven by the mode):

| Mode | Plot Area |
|---|---|
| Exploration | The Result: the recipe's plot, drawn from T3; never changed by an exploration filter (D-0019, D-0327) |
| Audit | The audited plot: T3 plus the audit steps applied with a reason; with Compare on, two panes, see below |

**Data area** (driven by "Table to view"; collapsible):

| Table to view | Data Area |
|---|---|
| Source | A source table as read from the file |
| T1 | The table after tier 1 |
| T2 | The table after tier 2 |
| T3 | The table the plot is drawn from (in Audit mode, the audited table) |

*The strip is absent only when `interactivity_enabled: false`. The mode switch, and so Audit mode and "Send to Audit", additionally require `t3_sandbox_enabled` — see §4.

**Comparison Mode** (Audit mode with the Compare switch on; gate `comparison_mode_enabled`, which requires `t3_sandbox_enabled`, D-0018):

```
┌──────────────────────┬──────────────────────┐
│  Original            │  Audited              │  ← Plot accordion (collapsible)
└──────────────────────┴──────────────────────┘
```

- The left pane is the original plot (the Result); it does not follow "Table to view".
- The data preview below stays a single table that follows "Table to view".
- Plot and data accordions are independently collapsible.
- The previous `theater_grid` toggle, `btn_max_plot`, `btn_max_table`, and `btn_reset_theater` controls are **removed** (superseded by this model).

## 6. Component Interaction Matrix

|**Zone**|**ID**|**Reactive Behavior**|
|---|---|---|
|**Table Ref**|`table_ref`|**Visual Only**: Filtering here updates the table view but creates NO audit nodes and does NOT trigger the Apply button.|
|**Table Active**|`table_active`|**Audit trail Driver**: "Brush" events or column de-selections automatically generate a new **Yellow Node** in the Audit Stack.|
|**Audit Stack**|`audit_stack`|**Order Matters**: Drag-and-drop reordering of nodes marks `audit_pending = True`.|

## 7. Session Management vs. Global Export

To ensure a clean separation between "Working State" and "Final Provenance," the UI distinguishes between these two actions:

### 7.1 Session Management (Left Sidebar — Session Management Panel)

**Panel:** `Session Management` accordion panel in the left sidebar. Gate: `session_management_enabled`. Absent for `pipeline-static` and `pipeline-exploration-simple`.

**Function:** Persists and restores the full working state so a user can resume interrupted work, or maintain separate sessions for different pipeline runs (e.g., AMR pipeline run 2025-01 vs run 2025-06).

**What is saved per session:**
- Active `t3_audit_steps` (all Yellow nodes and their comment fields)
- Reference to the active data analysis recipe and data source (so the session knows which pipeline run it belongs to)
- If metadata was replaced (see §9): reference to the uploaded metadata filename

Not saved: exploration filters (`applied_filters`; they are never saved or exported, D-0005, D-0327), the mode, the data choice and the open tab (as built: the T3 ghost holds no `tier_toggle` and no view choice, `app/modules/session_manager.py` `write_t3_ghost`). Every session file carries a format number; a file saved by an older version (it holds "My view") is refused with a plain line and is not converted (D-0312; built, `SESSION_FORMAT_VERSION`).

**DECIDED, not built:** the log of added and removed audit steps (date, initials, reason) is always written in the session (D-0315); it is always exported with the audit recipe, with the warnings shown at each choice (D-0478); the audit recipe and its audit record live in an audit folder inside the session's folder, in the user's own directory of the deployment (D-0319, D-0340, D-0333).

**Session model:**
- Each session lives under `{location_4}/_sessions/{session_key}/` (`session_key` = `data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]`, see §12d).
- Multiple sessions are allowed per user — users can switch between sessions (different pipeline runs, different dates).
- Sessions carry an optional user-supplied `label` (e.g., "AMR_run_Jan2025"), editable from the session panel.

**Ghost save (see §12d for the authoritative two-slot spec):**
- T1/T2 Ghost (`assembly.json`) — written once per assembly, rewritten when data analysis recipe or source data changes.
- T3 Ghost (`t3_{timestamp}.json`) — written on every `btn_apply` press: only audited steps applied with a reason are saved; pending steps are not; there is no save on a panel switch (D-0302). Each save is a new timestamped file, not an overwrite — the session panel lets the user pick which T3 snapshot to restore.
- Restored automatically via the T1/T2 "Prepped Chef" check at startup, matching on `session_key`.

**Save location:** `user_data` (Location 4) from the active deployment. This path is deployment-specific — on Galaxy it maps to a Galaxy-accessible path; on a local machine it is a local directory. Users only have write access to Location 4 — they cannot choose an arbitrary path.

**UI controls (Session Management accordion panel):**
- **Export Active Session (.zip)** — panel header button; downloads the full `_sessions/{session_key}/` directory as a `.zip` for archiving or sharing.
- Per-session card actions: **Restore** (load T1/T2 assembly + T3 ghost picker) and **Delete** (removes session directory; confirmation required). Per-session Export was removed in Phase 25-G — use the header-level Export Active Session instead.

---

### 7.2 Export Results Bundle (Export Panel — Left Sidebar, ADR-047, updated 2026-05-04)

**Panel:** `Export` accordion panel (renamed from "Global Export" in export redesign 2026-05-04). Gate: `export_enabled`.

**Implementation:** `@render.download export_bundle_download` in `app/handlers/export_handlers.py`.

**UI Controls:**
- `export_bundle_label` (text, sanitized — label is "Bundle label / name", not "Your name"). Sanitized: `re.sub(r"[^A-Za-z0-9_-]", "_", raw)[:40]`.
- `plot_format` selector: **PNG** / **SVG** / **PDF**.
- **3-way scope toggle** `export_scope`: `global` (all plots of the data analysis recipe) / `group` (all plots in active group tab) / `plot` (active plot sub-tab only). "Active group" and "Active plot" options are shown with reduced opacity when no plot tab is active.
- Filter warning shown when `applied_filters` non-empty.
- Download button: `📦 Export Bundle`.

**Export rules (2026-11-06, issue #10, EXPORT-KEYCHECK-1, EXPORT-T3-1) — science must be correct. The export holds the Result plus what the user validated with an audit step; exploration is never exported.**

1. **Key check.** The export compares the keys the open view was built on (`_data_analysis_recipe_keys`) with the keys computed now. If the data analysis recipe file set or the data changed, nothing is exported: an error notification explains it and the download holds only `EXPORT_NOT_CREATED.txt` (what changed, what it means, reload with F5, check, export again, both sets of keys). Never export silently from different files than the user looked at.
2. **Data source.** T1, T2 and the plots are read through `DataOrchestrator.materialize_tier1/2/3` with the session keys (key-checked). Plots are rendered from the table the plot reads (`materialize_tier3`: the stored T2 plus the plot's own tier 3 steps; T3 equals T2 when there are none), the same base as HOME (D-0310, D-0343). Reusing an anchor by file name is forbidden (ADR-089 point 7).
3. **Build rule T3 > T2 > T1.** The audited data of a plot is the table the plot reads (`materialize_tier3`) plus the plot's audited filter rows and column drops, built by `export_handlers.audited_frame`, the same steps and order as the HOME data preview in Audit mode.
4. **The export is the Result plus the audited steps; exploration is never exported** (issue #25, Eve 2026-11-06; D-0005, D-0327). Audited T3 steps (`filter_row`, `exclusion_row`, `drop_column`, `aesthetic_override`, committed with a reason, for example to remove poor quality data) are the user's decision for the publication: they are ALWAYS applied to the exported plot of that plot and to its `T3_data_<plot>.tsv`, whatever the screen shows, and recorded (T3 trail in the report, `data_analysis_recipes/t3_steps.yaml`). Exploration filters (`applied_filters`: what the user tries in Exploration on Source, T1, T2 or T3 to understand the data, not sent to audit) are a sandbox and are NEVER exported; there is no checkbox to include them and no `FILTERS.txt`. A reminder tells the user so: under the Filters buttons in Exploration ("Exploration: filters change this table only, never a plot. Nothing here is exported.") and in the Export panel. The pure rule is `export_handlers.plot_content_rules(audited_rows, audited_drops)`: exploration is not even an argument.

**DECIDED, not built (D-0324, D-0333, D-0315, D-0345, D-0478):** when audit steps have been added, the export holds the audit recipe as the recipe that produced the figures; it replaces today's export copy that writes the audit steps into a copy of a join's tier 2. The original recipe may be added as the baseline, saying plainly which file is which. An audit record (with the hash of the audit recipe) is always written beside the audit recipe in every bundle of an audit; the hash is also in the run file of the bundle; the README says in one sentence which file is the audit recipe and which the baseline; the audit log (who, when, the reason, the scope chosen, the warnings shown at the choice, steps added and removed) is ALWAYS in the bundle beside the audit recipe; there is no tick (owner, 2026-11-22, ledger `D-0478`, which revises her earlier rule; what exactly the log holds of a warning is not decided). The old name `decision_hash` is retired with the bundle texts when the export of an audit is built.
5. **Traceability.** README, `report.qmd` and PNG/SVG metadata record `data_analysis_recipe_sha256` (file set), `data_batch_hash`, and per dataset `tier1_key` and `tier2_key` (empty when T2 equals T1).
6. **Tests.** `app/tests/test_export_provenance.py`, `test_export_view_consistency.py` (headless) and `test_export_download.py` (real download, qa app features), `test_export_unread_tables.py` (tables no plot reads).
7. **Tables that no plot reads (D-0457; built, the reading is PROVISIONAL).** The export writes the Tier 1 data file (`<table>/T1_data.tsv`) of every table of the recipe that no plot reads, also those no plot reads at all (her words, D-0457: "Must be and yes must be viewabøenin the data preview"; earlier the same evening: "maybe export should export all the tables if there are included in a recipe even if no plot"). Only Tier 1 exists for such a table: the recipe check refuses tier-2 steps on a table or join no plot reads (S07, J14), and a tier 3 is a plot. The file is read like every other table, through `DataOrchestrator.materialize_tier1` with the keys of the export, so the key check (rule 1) and the refusal while building apply to it, and its Tier 1 key is recorded in README.txt and report.qmd like the others; README.txt and report.qmd say in one line that these tables are read by no plot (wording PROVISIONAL). A table that cannot be loaded gives `<table>/T1_data_ERROR.txt` and an error notification, as a plotted table does. An audit step never changes these files (HOME writes audit steps only at a plot's table); exploration is never exported (D-0327). PROVISIONAL, not decided (D-0457 reading to be confirmed): which tables count as "a table of the recipe": built as every source table and every join that no plot targets directly (`export_handlers.tables_no_plot_reads`), so a source that only a join reads also gets its file. NOT decided and not built: how the user reaches such a table in HOME's data preview (the preview follows the plot today), and the viewing of its tiers.

**Scope detection at download time:** reads `safe_input(input, "export_scope", "global")` and `active_home_subtab.get()` to filter which plots are included. Scope label recorded in `t3_steps.yaml` and `README.txt`.

**Filename:** `YYYYMMDD_HHMMSS_<label>_results.zip`.

**Bundle contents:**

| Path | Contents |
|------|---------|
| `plots/` | PNG/SVG/PDF per plot in scope |
| `data/<ds>_T1.tsv` | T1 (Assembled) — always. As built the file is `<ds>/T1_data.tsv` (one folder per table, next to its plots). It is also written for every table that no plot reads (D-0457; see rule 7 below) |
| `data/<ds>_T2.tsv` | T2 (Analysis-ready) — only when the join has tier2 steps; read from the stored Tier 2 parquet (issue #10) |
| `<ds>/T3_data_<plot>.tsv` | Audited data of a plot (T3): stored T2 (T1 without tier2 steps) plus that plot's AUDITED filters and drops. Written for every plot with audited steps, never for others; no checkbox (EXPORT-T3-1, issue #25, 2026-11-06) |
| `data_analysis_recipes/<proj>/` | All YAML wrangling/join/plot files for the active data analysis recipe |
| ~~`FILTERS.txt`~~ | Removed 2026-11-06: exploration filters are never exported, so there is no filter trace to write; the audit trail is `data_analysis_recipes/t3_steps.yaml` and the T3 Audit Trail of `report.qmd` |
| `data_analysis_recipes/t3_steps.yaml` | T3 committed nodes (active only) — auto-included when T3 has committed nodes and `t3_sandbox_enabled` |
| `report.qmd` | Quarto source: front-matter, filter table, figure includes, data section, **T3 Audit Trail** section (per-plot table of Step/Action/Details/Justification when T3 has active nodes) |
| `README.txt` | Bundle data analysis recipe: timestamp, data analysis recipe, app features, scope, tiers, metadata source filename, counts |

**T3 Audit Trail in report.qmd:** Auto-generated `## T3 Audit Trail` section with one table per plot (Step / Action / Details / Justification). Deactivated nodes excluded. Only present when `t3_sandbox_enabled` and committed active nodes exist.

**`t3_steps.yaml` format:**
```yaml
generated: "2026-05-04T12:00:00"
export_scope: "global"          # or group_id or plot_id
t3_steps:
  <plot_id>:
    - action: <node_type>       # filter_row | exclusion_row | drop_column | aesthetic_override
      # ...params...
      reason: "..."
      committed_at: "..."
```

**No separate Export Audit Report button.** The audit trail is auto-included in `report.qmd` inside the bundle. The `audit_report_enabled` app features flag has been **REMOVED (LEGACY-AUDIT-FLAG-1, Phase 34, 2026-05-22)** — deleted from all templates, `AppFeaturesValidator`, and `Bootloader`. Tombstone expires Phase 36.

**Single Graph Export accordion removed.** Superseded by the "Active plot" scope option in the 3-way toggle (see §7.3).

**Metadata provenance in bundle:** If a custom metadata file was uploaded (§9), its original filename is recorded in `README.txt` and in the `report.qmd` front-matter.

**Export location:** Browser download. Works identically in Galaxy, IRIDA, and local deployments.

**Deferred:**
- Per-plot checkbox selection (all in-scope plots always exported).
- Server-side write to Location 4.

---

### 7.3 Export Active Graph ⚠️ Superseded

**Status:** The `Single Graph Export` accordion panel was **removed** in the 2026-05-04 export redesign.

The "Active plot" scope option in the 3-way scope toggle (§7.2) replaces this panel. Selecting `[Active plot]` in the scope toggle and clicking `📦 Export Bundle` produces a single-plot bundle containing only the active plot's data, audit trail, and audit trail. The `export_enabled` flag now gates the full Export panel (both the bundle and the scope toggle) rather than a separate accordion.

## 8. Filter builder (Phase 21-F — Left Sidebar, 2026-04-23; ADR-085, 2026-08-10)

Row filters live in the left sidebar (Home mode only). In Exploration they are built on the table viewed (Source, T1, T2 or T3) and change only that data table, never a plot (D-0178, D-0310, D-0327); in Audit mode they become audit steps (§4/§5 above; built 2026-11-20, slice B).

**State model:**
- `_pending_filters`: staging area (`reactive.Value[list]`) — rows added by user, not yet applied.
- `applied_filters`: committed (`reactive.Value[list]`) — exploration only, never audited, never saved, never exported. Each row carries the key of the view it was built on; consumed only by `home_data_preview` (and its badge) for that view (`_applied_for_view`). Both lists are emptied, with a notice, when the viewed table changes (D-0311; `_clear_filters_on_view_change`).

**Two distinct actions on the staged rows (do not merge back into one button):**
- **`filter_apply`** — Exploration only: commits `_pending_filters` → `applied_filters`.
- **`filter_send_to_audit`** — rendered only in Audit mode while T3 is viewed (`t3_sandbox_enabled`).
  Promotes the staged rows into the audit steps via the propagation modal (primary-key stamping, this-plot /
  all-plots / all-except scope choice). In Audit mode on Source, T1 or T2 the panel says "To create an audit step, view T3."

**Each row:** `{column: str, op: "eq"|"ne"|"gt"|"ge"|"lt"|"le"|"in"|"not_in"|"between", value: the real value in the type of the column (number, True/False, text; a date as year-month-day text), or a list of them (for between: [low, high]), dtype: str, na: "keep"|"remove", closed: "both"|"left"|"right"|"none" (between only)}`. `na` is the tick of the dialog (keep the rows with no value in the column; preselected `keep` for `!=` and none-of, `remove` otherwise, NA-RULE-63); a row or audit step without it is read as `remove`, and an audit step is never written without it. `closed` says which ends of a `between` are included (`both`, the default, `left` = the lower end only, `right` = the upper end only, `none`); "Send to Audit" carries `na` and `closed` exactly as chosen, and the export writes them into the `modif_filter` step.

**Operators by column type (ADR-104 points 4 and 7, `app/modules/t3_audit_engine.py` `ops_for_column`, `value_widget_for`):** a number column offers `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `between` with number boxes; when the plot uses it as a discrete axis it also offers `in`, `not_in` (first) and `eq`, `ne` with a list, while the comparisons keep the number boxes ("> 1998 and < 2003" on a Year). Every other column (text, true/false, date, category) offers `in`, `not_in`, `eq`, `ne` with a list. Comparisons on text, date and true/false columns are not decided and not offered. The type shown next to the column and used everywhere comes from the schema of the table (`collect_schema()`), the list of values from the whole column, not from a sample of rows.

**Value box redraw (as built, 2026-11-22; `dev` after merge `51be0a46`).** The value box of a filter row is drawn again only when the column, the viewed table, the columns or types of the form (a plot's discrete axis counts for a number column only), or the kind of box changes. The kind is the result of `value_box_kind` (`app/modules/t3_audit_engine.py`), which reads the operator's family through `value_widget_for`: `list`, `number`, `range` (two number boxes, `between`), `bool`, `date`, `datetime`, `time`, `duration`; a date, datetime, time or duration with `between` gives `date_range`, `datetime_range`, `time_range` or `duration_range`; `text` when the column has no type; no kind (None) when the column has no filter. A change of operator within the same kind leaves the box and what was typed in it; a value typed right after the operator is chosen stays, and "+ Add row" adds that value. At a change of kind the new box starts at its default and the typed value is not carried over (DECIDED, D-0503). The two ends of `between` start empty and "+ Add" refuses the row until BOTH ends hold a value the user gave: nothing is added, and a plain line near the boxes says so ("Give both values for 'between': the lower and the upper. Nothing was added.", wording PROVISIONAL); it goes when the user changes the column, the operator or an end (as built; D-0504, D-0050). The rule is on the operator, so it holds for a number, a date, a date and time, a time of day and a duration column alike; the range of a number column is shown beside the boxes as information, never as a value in them. A lower end above the upper is put in order without a word (as built; not decided). A change of plot tab onto a plot that reads the SAME table leaves the box and the typed value (DECIDED, D-0505, D-0506; built: the form is mounted again only when its columns or types change, and a plot's discrete axis counts only for a number column, `dialog_schema_signature`); onto another table the filters and the form are cleared. The kind is held in a `reactive.Value`, written by an Effect with an equality guard (`app/handlers/filter_and_audit_handlers.py`).

**Value type rule (ADR-104 point 7):** the panel keeps a map from the text shown in a list to the real value and stores the real value (`dialog_value`): a number for a number column (also on a discrete axis), True/False for a true/false column, text for text; a date is kept as year-month-day text because a session file holds no date object, and is typed at export from the dtype. `utils.filter_values.filter_condition` builds the condition for the HOME table and the plot (an old value held as text is read from the dtype; a value that cannot be read gives a plain error) and, strict, for the recipe action `modif_filter` (a value of another type gives a plain error, nothing is converted). The export types an old step's value from the `dtype` it carries. `eq`/`ne` with a list mean `in`/`not_in`.

**VizFactory predicate pushdown:** HOME does not inject `applied_filters` into `plot_config["filters"]`: an exploration filter never reaches a plot (D-0327; built, no such injection in `app/handlers/`). The audited filters and drops of Audit mode are applied to the T3 frame before it is drawn. VizFactory itself still accepts a `filters` key: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`.
  
## 9. Metadata Ingestion (Data Import Panel — Left Sidebar)

**Purpose:** Allow a user to upload an updated metadata file that replaces the metadata source for the active pipeline run. This is a **full replacement** — the uploaded file becomes the new source of truth for that metadata source. It triggers a T1 rebuild.

**When used:** Users correct errors in metadata (e.g., wrong collection date, corrected resistance phenotype, updated sample annotations) and need the plots to reflect the correction without re-running the upstream pipeline.

**Panel:** `Data Import` accordion panel in the left sidebar. When `import_helper_enabled: true`, metadata upload is nested above the multi-file ingestion control. When `import_helper_enabled: false` and `metadata_ingestion_enabled: true`, it appears as a standalone control in the Data Import panel.

**App features gate:** Gate: `metadata_ingestion_enabled`. Available from `pipeline-exploration-advanced` and above. Hidden for `pipeline-static` and `pipeline-exploration-simple`.

**Flow:**
1. User uploads one or more files via the file input in the Data Import panel and assigns each to a dataset.
2. **The check (as built; D-0034, DEC24, DEC25).** On Apply, every file is checked BEFORE anything is written, by the ingestion's own read of the candidate file for that dataset of that recipe (`ingestion.ingestor.ingest_file`, called by `app/modules/data_import_check.py`; the handler only wires it): the declared columns are found by their exact `original_name` (the slug when none is given), then `strip`, `null_values` and the declared Polars types are applied, and the WHOLE file is read once, so that a row with more fields than the header, a quote that is never closed, a byte that is not UTF-8 or a value that does not fit its type is refused here and not at the next build. A file is accepted when its name has the format of the stored file (step 3: by name, so a tab-separated file named `.txt` is refused though its content could be read) and the ingestion reads all of it; there is no second definition of the content rule (the slug-based `MetadataValidator` is removed). The refusal is the ingestion's own reason (which headers are expected, which value does not fit its type); for headers the way out is written for the person who uploads (correct the headers of the file), and a file that cannot be read at all says so in plain words (empty, a row too long, a quote never closed, not UTF-8). An undeclared extra column is accepted, as the ingestion does (it is not imported). Wording of the new messages: PROVISIONAL.
3. **The format of the stored file.** The file must have the format of the file the orchestrator reads for that dataset: `.tsv` for a tab-separated dataset, `.parquet` for a Parquet one. A comma-separated or Excel file is refused with a plain line that says why and what to do (convert it to a tab-separated file first). Converting a file for the user is NOT decided and is not built.
4. **All files or none.** If any file of the Apply is refused, none is written and each file shows its own reason; two files assigned to one dataset, or to two tables that read the same data file, are both refused. When the file replaced is also the data file of other tables of the recipe (the demo recipe: `Summary` and `Summary_quality`), every one of those tables must read it too, or the file is refused with the table named. When all pass, each file is copied next to its place and put in place together.
5. **The place is the orchestrator's** (`DataOrchestrator.file_place`, built on `locate_dataset_file`): the file the orchestrator reads for the dataset; else the recipe's `source.path` (`data_lookup: data_analysis_recipe_paths`). **PROVISIONAL (the coordinator's choice, not a decision of the owner; task DATA-IMPORT-OVERWRITE waits for her):** a deployment that finds its data files by table name (`data_lookup: by_dataset_id`) is refused, with a plain line (the data is delivered by the pipeline and cannot be replaced from here), because the panel would overwrite the real file with no copy of it; options for the owner: keep the refusal, or allow the overwrite and keep the old file and the name of the uploaded one. **PROVISIONAL (an agent's choice, not Eve's):** a recipe imported from a bundle reads only the folder of its import ("the data of an import is only what its bundle carried"), so Data Import refuses to replace its data, with a plain line; options for the owner: keep the refusal, replace the file in the import's folder (it would no longer be what the bundle's hashes verified), or store uploads in a place of their own that the orchestrator reads, with a record.
6. The success notice names each file, every table that reads it and the place written; it is shown only when what the app reads has changed.
7. After the write (as built; there is no "Recalculating..." overlay): the panel drops what the app kept for every table that reads a replaced file (its stored anchor and its cached table) and raises `data_refresh_trigger`, so that HOME reads the new file; the stored tables are keyed on the content of the data files they read (ADR-089), so they are rebuilt from the new file when next needed. This is also done for the files already replaced when a later file cannot be written.
8. A notification confirms: "N file(s) imported — plots are refreshing now. `<file>` -> `<tables>` (`<place>`)". When a file cannot be written the notice is a warning that says what is already replaced and what is not (a file that is replaced is not put back).

**Provenance obligation (NOT built; waits for the owner, task DATA-IMPORT-OVERWRITE, together with the overwrite of the recipe's data file with no copy of the old one):** The original uploaded filename (not just its path) is stored in a sidecar file (e.g., `metadata_provenance.yaml` in Location 1) so that exports and session files can reference it. This filename is included in `README.txt` and `report.qmd` of any subsequent export bundle.

**What is NOT replaced:** Raw instrument data (sequencing results, VCF files, etc.) — only the metadata source. The data analysis recipe's `input_fields` contract determines which file is considered "metadata" for validation purposes.

**Status:** the check (a full read of the file), the format refusal, the all-or-nothing Apply, the shared files and the place are built (steps 2 to 8 above). Not built: the record of the original file name and the keeping of the replaced file (task DATA-IMPORT-OVERWRITE), the conversion of a comma-separated or Excel file.

---

## 10. Data Ingestion & Excel Converter (Data Import Panel — Left Sidebar)

**Purpose:** Allow a user to provide raw data files when the app is deployed independently of an automated pipeline (e.g., pipeline deposited results in an Excel file that the user now uploads manually).

**Panel:** `Data Import` accordion panel in the left sidebar. Multi-file ingestion section is nested inside when `import_helper_enabled: true`.

**App features gate:** `import_helper_enabled: true` in app features file. Available to ≥ `standalone` and `developer`. Hidden for lower app features files. Also deactivatable at the deployment level (the deployment's `app_features_override` sets `data_ingestion_enabled: false`) for deployments where data is always pushed automatically by a pipeline — the Data Import ingestion section is suppressed entirely (metadata upload remains available, see §9).

**Supported ingestion types:**
- **Raw data** — TSV/CSV instrument output
- **Metadata** — sample annotation files (goes through the same check as §9: the ingestion's own read of the file)
- **Extra data** — supplementary tables (e.g., reference databases, additional annotation layers)

**Data analysis recipe association:** When uploading, the user must associate the file with a data analysis recipe schema (dropdown of known schemas from `locations.data_analysis_recipes`). This tells the DataOrchestrator which `input_fields` contract to validate against and which pipeline slot the file fills.

**Multi-file upload:** A `+` button allows queuing multiple files (e.g., one per schema). Each queued file shows its assigned schema and validation status before the user commits the ingestion.

**Excel → TSV Converter (within Data Ingestion):**
- Available as a sub-step when an `.xlsx` file is uploaded.
- App reads sheet names from the workbook (via `ExcelHandler` — `libs/ingestion/src/ingestion/excel_handler.py`).
- User assigns each sheet to a role: **raw data**, **metadata**, or **extra data**, and selects the target schema from the data analysis recipe dropdown.
- Converter writes TSVs to Location 1 (`raw_data`) in the user-accessible directory.
- After conversion, the resulting TSVs are queued for ingestion as normal.
- **Why here and not Test Lab:** Scientists receive Excel files from collaborators and pipelines — this is a practical data preparation step, not a developer concern. Test Lab (developer app features only) is for synthetic data generation (AquaSynthesizer).

**Status:** Deferred to Phase 22+. Design finalized here. `ExcelHandler` backend already exists.

---

## 11. Sidebar Configuration — Slot Registry (ADR-073, 2026-05-09)

**This section supersedes the Phase 25-E hardcoded accordion spec.** Sidebar layout is now declarative and configurable per app features file and per workspace.

### 11a. Core rule — two-layer resolution

| Layer | Controls | Source |
|---|---|---|
| **Slot list** | Which panels appear and in what order | App features file `workspaces.<ws>.<side>_sidebar.panels` |
| **Feature flag** | Whether panel functionality is active | `bootloader.is_enabled(flag)` — unchanged |

A panel in the slot list with a disabled gate flag is silently skipped. Flags and cascade rules (ADR-052, AppFeaturesValidator) operate independently of the slot list.

### 11b. Per-workspace independence

Left and right sidebar configs are declared per workspace in the app features file:

```yaml
workspaces:
  home:
    left_sidebar:
      visible: true
      panels:
        - type: data_analysis_recipe_info
        - type: data_analysis_recipe_choice
        - type: filters
        - type: data_import
        - type: export
        - type: session_management
    right_sidebar:
      visible: true
      panels:
        - type: audit_stack
  blueprint:
    left_sidebar: !include sidebars/blueprint_standard_left.yaml
    right_sidebar: !include sidebars/blueprint_standard_right.yaml
  gallery:
    left_sidebar: !include sidebars/gallery_focus_left.yaml
    right_sidebar:
      visible: false
      panels: []
  test_lab:
    left_sidebar:
      visible: true
      panels:
        - type: data_analysis_recipe_info
    right_sidebar:
      visible: false
      panels: []
```

Shared sidebar configs live in `config/ui/sidebars/` and are referenced via `!include`. Multiple app features files sharing the same layout reference the same file. See `docs/workflows/ui_app_features.qmd` for the full panel type reference table.

### 11c. Visibility and structural exclusion

- `visible: false` — excludes the sidebar container from the DOM (not CSS-hidden).
- `visible: true` with no active panels — renders an empty sidebar container (acceptable for `data_analysis_recipe_info`-only configs).
- Auto-hide: if `visible` is unset and all panels are skipped after flag-gating, sidebar is treated as hidden.
- **Right sidebar structural exclusion** (previously an app features name string comparison in `ui.py` — ADR-053 violation, task 25-O) is now driven by `bootloader.get_sidebar_config("home", "right").visible`. No app features name checks.

### 11d. Built-in panel types (current)

| Type | Gate flag | Workspace | Description |
|---|---|---|---|
| `data_analysis_recipe_info` | — | any | Data analysis recipe title, description, dataset summary |
| `test_lab_info` | — | test_lab | Test Lab's own Info panel — static placeholder text, never the open data analysis recipe's `info:` block (issue #33, 2026-11-08: Test Lab tools don't operate on an open recipe, so showing recipe content there is actively wrong, not just unused). Content TBD once Test Lab's own panels are finished. |
| `deployment_info` | — | any | Branding: logo, contact, institution (params in template) |
| `data_analysis_recipe_choice` | `data_analysis_recipe_selector.visible` | home | Data analysis recipe selector dropdown |
| `filters` | `interactivity_enabled` | home | Row filter builder (§8) |
| `data_import` | `metadata_ingestion_enabled` | home | Metadata upload + optional multi-file (§9/§10) |
| `export` | `export_enabled` | home | Export bundle with 3-way scope toggle (§7.2) |
| `session_management` | `session_management_enabled` | home | Session save/restore/import (§7.1) |
| `audit_stack` | `t3_sandbox_enabled` | home right | T3 audit trail panel + apply tools (one `ui.TagList` block — card and tools button sit as direct siblings, not nested in an extra wrapper) |
| `gallery_main` | `gallery_enabled` | gallery left | **Freestanding** — Gallery's taxonomy/search accordion (`gallery_viewer.build_sidebar_ui()`), one cohesive bespoke unit |
| `gallery_right_info` | `gallery_enabled` | gallery right | Static "Gallery Explorer" card |
| `blueprint_main` | `blueprint_enabled` | blueprint left | **Freestanding** — Blueprint's recipe-editor accordion (`WrangleStudio.build_sidebar_ui()`), one cohesive bespoke unit |
| `blueprint_surgeon` | `blueprint_enabled` | blueprint right | Action form for the focused TubeMap node |
| `blueprint_action_help` | `blueprint_enabled` | blueprint right | Inline help for the active action |
| `blueprint_plot_defaults` | `blueprint_enabled` | blueprint right | `plot_defaults:` editor (VIZFAC-BLUEPRINT-FORM-1) |
| `blueprint_branch_node` | `data_analysis_recipe_edit_enabled` | blueprint right | Branch-node editor (BP-BRANCH-NODE-1) |
| `blueprint_agent_chat` | `blueprint_agent_enabled` | blueprint right | AI agent chat panel (ADR-076) |
| `test_lab_right_info` | `test_lab_enabled` | test_lab right | Static tool-description accordion (ID Reconciliation, Data Analysis Recipe Scaffolding, Synthetic Data, Anonymisation, File Reformatting). Reachable since issue #55 (2026-11-10) — `testlab_standard_right.yaml` flipped to `visible: true`, `panels: [{type: test_lab_right_info}]`. |
| `notification_log` | — | any left | Alert log accordion (ADR-060). **Moved from right to left for every workspace (Home, Gallery, Blueprint, Test Lab), 2026-11-08, issue #33**: the right sidebar is structurally absent for some app features (Home: `pipeline-static`/`pipeline-exploration-simple`) or for an entire workspace (Test Lab: `testlab_standard_right.yaml` is `visible: false`), which made alerts unreachable there. Home, Gallery, and Blueprint keep their right sidebars — reserved for future modules, not removed (Eve: "I am pretty sure we will need the space in further developments"). |

**Superseded (2026-11-08, issue #42):** the note that used to appear here said Gallery and Blueprint's sidebars bypass the slot registry by deliberate, permanent design. That stood for a few hours the same day — Eve then asked the harder question ("why do we have two different mechanisms that differ") and, after walking through the tradeoffs (one source of truth per sidebar; `SidebarValidator` becomes meaningful everywhere instead of validating files nobody reads; `home_theater.py` sheds ~200 lines of workspace-specific UI construction it was never supposed to own), decided to unify rather than document the split as acceptable. **Every workspace, both sides, now goes through the registry.** What's preserved from the original design, and still genuinely true: Gallery's and Blueprint's sidebar *content* stays exactly as bespoke as it always was — unification only changed *how it's reached* (`_build_left_sidebar`/`_build_right_sidebar`, same mechanism Home and Test Lab already used), not what it looks like or how it's built internally. See `gallery_main`/`blueprint_main` above (the "freestanding panel" concept, §11e) for how a cohesive, non-decomposable unit fits into a registry built around independent interchangeable panels.

### 11e. Implementation notes

- Panel registry: `app/modules/sidebar_registry.py` — `PANEL_REGISTRY` dict, headless-safe (Two-Category Law).
- Bootloader: `get_sidebar_config(workspace, side)` reads `workspaces.<ws>.<side>_sidebar`.
- `home_theater.py`: `_build_left_sidebar(workspace_key, open_panels)` and `_build_right_sidebar(workspace_key)` are the two generic dispatchers, shared by all four workspaces. Each workspace's `sidebar_tools_ui()` / `right_sidebar_content_ui()` branch is now a one-line call into the matching dispatcher — no hardcoded UI construction remains in either function.
- **Freestanding panels (left side only, issue #42):** a panel type whose renderer returns a complete, already-formed UI block (its own accordion, its own DOM id) rather than a single `ui.accordion_panel()` to merge into the shared `nav_accordion`. Needed because some workspaces' sidebar content is one cohesive bespoke unit, not a list of independent generic panels — forcing it into individually-swappable pieces would be fake decomposition, not real consistency. `_left_freestanding_renderers` in `sidebar_tools_ui()` holds these (`gallery_main`, `blueprint_main`); `_build_left_sidebar` renders the shared accordion only when `panels` is non-empty, then appends any freestanding blocks after it. The right side doesn't need this distinction — there's no shared outer accordion to merge into there, every right-side panel is already just "one block appended to a flat list," generic or bespoke alike.
- **The app's own redraw of the HOME left sidebar keeps what the user has open and closed (D-0502; built).** The render follows the open user space (`_active_space`, written by an effect only when it changes), not the raw `sidebar_nav` input, so the page's first send of that input no longer draws the sidebar a second time; if the sidebar is drawn again within the same user space, `app/modules/sidebar_open_panels.py` (`open_panels_after_redraw`) keeps the panels the user opened and closed (read isolated from `input.nav_accordion`), and the fixed list opens only the first draw, a new panel, and the draw after a change of user space.
- Each workspace keeps its own outer wrapper class and empty-state fallback on the right side (Home/Blueprint: `sidebar-content p-0 d-flex flex-column h-100`; Gallery/Test Lab: `sidebar-content p-0`) — `_build_right_sidebar` returns a plain list, the per-workspace caller wraps it, so this real difference is preserved rather than unified away.
- `ui.py`: reads `bootloader.get_sidebar_config("home", "right").visible` for right sidebar structural exclusion.
- Validation: `SidebarValidator` runs at startup alongside `AppFeaturesValidator`; CLI gate: `scripts/validate_app_features_config.py --all --strict`.

**Implementation tasks:** SIDEBAR-CONFIGS-1, SIDEBAR-REGISTRY-1, SIDEBAR-VALIDATE-1, **SIDEBAR-UNIFY-1** (issue #42, see `tasks.md`).

---

## 12. Tier 3 Audit Trace — Publication Finisher

### 12a. Scope Lock

**Note (D-0016, D-0179):** this section describes the **audit** (Audit mode) — the AuditStep types
below only ever exist once `t3_sandbox_enabled` is on and something has been explicitly Sent to Audit. The
plain exploration layer (`applied_filters`, transient, no reason, no AuditStep) exists independently in
Exploration, also without `t3_sandbox_enabled` — see §5, §8. There is no "My view" any more.

**DECIDED, not built (D-0322, D-0329, D-0332):** the check of an audit recipe refuses any audit step that is not a filter, a column drop or a removal by key, with a plain line; the list of allowed steps is kept in one place. The reason of an audit step is a separate step key, `audit_comment`; in an audit recipe each tier keeps the author's `steps` untouched and has a second list `audit_steps`, run after `steps`. On `dev` today the audit copy, in memory only (`libs/utils/src/utils/audit_copy.py`, slice A), adds a marked step (`id: audit_<8 hex>_<k>`) at the end of a tier list with its reason in `comment`, and HOME writes audit steps at T3 of a plot; the `audit_steps` / `audit_comment` form is on a branch, not merged. An audit recipe is a recipe of format 1: the format number stays 1; `audit_steps`, `audit_comment` and `info.audit_of` are legal only in an audit recipe and refused in every other recipe (DECIDED, not built: the keys are not read from a file yet; D-0354).

T3 is a **Publication Finisher**, not a wrangling sandbox. Its scope is permanently locked to five node types (four of which gate `btn_apply` on a mandatory reason — `aesthetic_override` is the exception, see the Gatekeeper rule below):

| Node Type | What it does | Reason required? |
|---|---|---|
| `filter_row` | Row-level inclusion filter `{column, op, value}` | **Mandatory** |
| `exclusion_row` | Explicit row exclusion (named sample / value) | **Mandatory** |
| `drop_column` | Permanently drop a column from the exported data (not just hidden in preview) | **Mandatory** |
| `aesthetic_override` | Plot colour / fill / alpha / shape changes (per plot sub-tab) | Optional — included in report |
| `developer_raw_yaml` | Escape hatch: arbitrary data analysis recipe fragment (≥ `pipeline-exploration-advanced` / `developer` app features only) | **Mandatory** |

> **Plot Style panel not mounted (2026-11-05, fork issue #15).** The UI that authors `aesthetic_override` nodes (the "Plot Style" panel) is not shown in HOME for now: letting users change in HOME what the data analysis recipe defines is too much at this stage, and using it broke the plot (test plan HOM-47). The node type stays in this schema and the panel's code is kept, unused, in `audit_stack.py`. This does not change the T3 scope of ADR-082.

**Gatekeeper rule:** `btn_apply` is **locked** if any `filter_row`, `exclusion_row`, `drop_column`, or `developer_raw_yaml` node has an empty `reason` field. `aesthetic_override` nodes never block apply.

**`drop_column` is permanent within the session:** it physically removes the column from the working frame — it does not merely hide it in the UI. This is the unambiguous truth the export reflects. There is no "column_visibility" toggle that hides without dropping; any column removal in T3 must be justified and is permanent until the node is deactivated.

In audit mode T3 never exposes an action-picker UI: the user can only add filters, drops and removals by key. A data analysis recipe may declare any registered action in its own T3 list; the engine runs it like any step and the recipe maker is responsible for good practice (reshaping early is better). Reworded 2026-11-12 (Eve, ADR-099 point 16); before, this sentence said that wrangling is never done in T3.

### 12b. AuditStep Schema

Each node in the audit steps is a YAML mapping:

```yaml
- node_type: filter_row          # filter_row | exclusion_row | drop_column | aesthetic_override | developer_raw_yaml
  id: "t3_node_001"              # auto-generated UUID on creation
  created_at: "2026-04-24T14:30" # ISO timestamp
  plot_scope: "__all__"          # "__all__" or a specific plot sub-tab id
  params:
    column: "species"
    op: "in"
    value: ["cat", "dog"]
  reason: "Exclude aquatic species — outside study scope."
```

For `aesthetic_override` nodes, `params` carries `{fill, colour, alpha, shape}` dicts keyed by plot sub-tab ID. For `developer_raw_yaml`, `params` carries `{yaml_fragment: "..."}`.

`reason` is a free-text string. The UI renders it as a required text-input next to each Yellow node; the field border turns red if empty and `btn_apply` is locked.

### 12c. audit steps IS the Audit Trace

There is **no separate FILTERS.txt** for T3. The T3 YAML audit trail is the complete audit trail.

- Every Yellow node has `id`, `created_at`, `plot_scope`, `params`, and `reason`.
- **Design intent (not yet built, F-07):** the audit trail was designed to be append-only, with deletions marking nodes `active: false` rather than removing them, so the sequence of decisions is preserved. **As built,** there is no control that ever sets `active: false` — deletion is real removal from the list (`audit_stack.py:585`). The `active: false` / "deactivated node" path below describes the intended future behaviour once the Power-icon toggle (§1) is implemented; today it never triggers. Tracked as task STM-NODE.
- **Export warning for deactivated nodes (not yet reachable, see above):** If any node has `active: false` at export time, the UI shows a blocking warning dialog: *"You have [N] deactivated filter(s) / exclusion(s) / column drop(s). Export reflects only active nodes. Deactivated nodes will NOT appear in the exported data or Methods section. Confirm you want to discard them from this export?"* The user must explicitly confirm. The export is the unambiguous truth — deactivated nodes are absent from the exported data and from the Methods section. They are listed in an appendix ("Decisions Considered and Discarded") for transparency only.

`aesthetic_override` nodes are stored **separately** from the wrangling steps as `t3_plot_overrides` (a dict keyed by plot sub-tab ID) in the session state object (§13). They are included in the export report but do not block `btn_apply`.

### 12d. Ghost Save — Two Slots

#### Session Identity

A **session** is the combination of one data analysis recipe + one data batch. The same data analysis recipe run against different data batches (e.g., batch A vs. batch B of ST22 samples) produces different sessions. Two discriminators are combined:

- **`data_analysis_recipe_sha256`**: SHA256 of the pipeline data analysis recipe YAML. Changes if the data analysis recipe is edited (wrangling steps, field definitions, join steps).
- **`data_batch_hash`**: A single SHA256 derived by hashing all per-source-file SHA256s together in deterministic (sorted) order. Changes when any input file is replaced, even if the data analysis recipe is unchanged.

```
session_key = data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]
# e.g. "a3f9c81b04e2:c4d29e1a3f80"
```

Using content hashes (not IDs or names) means the key is invariant to data analysis recipe renames, path changes, or file moves — only content changes produce a new key. The `session_key` namespaces both ghost file directories and Parquet output paths so sessions for different data analysis recipes or different data batches never collide.

---

#### Ghost Slots

| Slot | File | Written when | Content |
|---|---|---|---|
| **T1/T2 Ghost** | `_sessions/{session_key}/assembly.json` | Once on first assembly; re-written when data analysis recipe or source data changes | Data analysis recipe ID + SHA256, source files + per-file SHA256, `data_batch_hash`, assembled Parquet paths, assembly timestamp |
| **T3 Ghost** | `_sessions/{session_key}/t3_{timestamp}.json` | On every `btn_apply` (no save on a panel switch, D-0302) | Full audit steps YAML + `t3_plot_overrides` + `session_key` + `saved_at` + `schema_version` (no tier toggle) |

Both slots live under `{Location_4}/_sessions/{session_key}/`. All ghost files for a session are co-located, making it easy to archive, share, or delete a full session as a unit.

---

#### T1/T2 Ghost Content

```json
{
  "session_key": "my_pipeline_v2:c4d29e1a3f80",
  "data_analysis_recipe_id": "my_pipeline_v2",
  "data_analysis_recipe_sha256": "a3f9...",
  "data_batch_hash": "c4d29e1a3f80...",
  "assembled_at": "2026-04-24T14:00:00",
  "source_files": {
    "fastq_metadata": {"path": "assets/test_data/.../metadata.tsv", "sha256": "c4d2..."},
    "amr_results":    {"path": "assets/test_data/.../amr.tsv",      "sha256": "9e1a..."}
  },
  "parquet_paths": {
    "assembly":   "tmp/EVE_assembly_my_pipeline_v2_c4d29e1a.parquet",
    "contracted": "tmp/EVE_contracted_my_pipeline_v2_c4d29e1a.parquet"
  }
}
```

#### T1/T2 Restore Logic (the "Prepped Chef" check at startup)

1. Scan `_sessions/` for all `assembly.json` files. Compute the current `data_batch_hash` from the active data analysis recipe's source files.
2. Find the matching session by `session_key` (data_analysis_recipe_id + data_batch_hash).
3. **Match found AND Parquet files exist on disk** → short-circuit: load existing Parquet, skip re-assembly. Normal fast path.
4. **Match found BUT Parquet files missing** (e.g., tmp/ cleared, server restart) → re-assemble silently from source files listed in the ghost. Rewrite Parquet paths after completion. No user action required.
5. **No match** (new batch or new data analysis recipe) → full assembly, write new session ghost.
6. **Source files missing from disk** (user moved data) → blocking UI error: *"Source data for '[dataset_id]' cannot be found at [path]. Please re-upload or update the data analysis recipe."* Assembly blocked until resolved.

T1/T2 state is always self-healing: lost Parquet is recovered automatically from the ghost as long as source data is accessible.

---

#### T3 Ghost Content

```json
{
  "session_key": "my_pipeline_v2:c4d29e1a3f80",
  "data_analysis_recipe_id": "my_pipeline_v2",
  "data_analysis_recipe_sha256": "a3f9...",
  "data_batch_hash": "c4d29e1a3f80...",
  "saved_at": "2026-04-24T14:30:12",
  "label": "",
  "schema_version": 3,
  "t3_audit_steps": [],
  "t3_audit_steps_by_plot": {},
  "t3_plot_overrides": {},
  "notification_log": [],
  "t3_audit_steps_sha256": "..."
}
```

`label` is an optional user-supplied name (e.g., "batch-A final filters"). Empty by default; editable from the session panel.

There is no `tier_toggle` any more (built: `session_manager.write_t3_ghost`). `schema_version` is the format number of every session file (`SESSION_FORMAT_VERSION`, 3 today): a file with no number, a lower or a higher one is refused as a whole with a plain line ("... was saved by an older version of the app and cannot be opened. Delete it and start a new session."), nothing is converted; a refused session can be deleted from the panel (D-0312; built). All old session files are removed: session files only, never recipes or data; the list is stated first and what was removed is reported (D-0312).

**Session of another recipe:** Restore of a session saved against another recipe is refused with a plain line (it belongs to another recipe; open that recipe first); nothing is applied (D-0317; built, `session_manager.session_recipe_refusal`, compared by recipe id).

**Data analysis recipe SHA256 mismatch on restore:** If the recipe id is the same but the saved `data_analysis_recipe_sha256` differs from the current data analysis recipe, the UI warns (as built: *"Session was saved against a different data analysis recipe version. Audit step may not match current columns."*). The user can still restore but is not blocked. D-0317 keeps the continue-warning "only for the same recipe with a different data batch"; whether an edited recipe with the same id counts as "a different recipe" is not stated there (open reading, reported).

**Data batch mismatch on restore:** If `data_batch_hash` differs (user loaded a different data batch), the UI warns: *"This session was saved against a different data batch. Row filters and exclusions may match different or no rows."* Again, non-blocking — user confirms.

---

#### Session Management Panel

Accessible from the **Session Management** accordion panel in the left sidebar (gate: `session_management_enabled`; ≥ `pipeline-exploration-advanced`).

**Session list view:** All sessions in `_sessions/` displayed as cards, grouped by `data_analysis_recipe_id`, sorted by most-recent T3 ghost `saved_at` within each group. Each card shows:
- `data_analysis_recipe_id` + short `data_batch_hash` (first 8 chars)
- User `label` (editable inline)
- Last saved timestamp
- Number of T3 ghosts (saves) in that session

**Per-session actions:**
- **Restore** — loads T1/T2 assembly state + opens a T3 ghost picker (list of all `t3_{timestamp}.json` files for that session, sorted newest-first). User selects which T3 snapshot to resume, or "Start fresh T3" to keep T1/T2 but clear T3.
- **Export session** — downloads the full `_sessions/{session_key}/` directory as a `.zip` for archiving or sharing. Includes both assembly ghost and all T3 ghosts.
- **Import session** — accepts a `.zip` exported by another user or machine. Validates `session_key`, checks source file availability, registers in the local `_sessions/` store.
- **Delete session** — removes the session directory and all its ghosts. Confirmation required.

T3 ghost is never written on intermediate filter edits — only on apply (D-0302). Restoring a T3 ghost triggers the T1/T2 restore logic first (steps 1–6 above) to ensure the Parquet base is valid before applying T3 nodes.

### 12e. Gallery → T3 Transplant Rules

> **REMOVED (ADR-093, 2026-11-08):** the Gallery clone-to-T3 feature this section described
> (`handle_gallery_clone`, the "Clone to Sandbox" button) is deleted. T3 is audited modifications a
> HOME user makes to their own running analysis — never a place to import recipe content from
> anywhere, Gallery included (ADR-082 §4 extended). GALLERY is now unconditionally the static
> reference browser `rules_ui_dashboard.md §5` describes, with no interactive handoff into any other
> space. See ADR-093 for the full reasoning. This section's content below is kept only so a reader
> who finds an old reference to `gallery_source`/`developer_raw_yaml`-from-Gallery understands what it
> meant; it is not current.
>
> - Gallery transplant always targeted the **last-active plot sub-tab** in Home.
> - A transplanted gallery node was inserted as a Yellow `developer_raw_yaml` node with `reason: ""` (empty, blocking apply).
> - The transplanted node carried a `gallery_source` metadata field: `{gallery_id, gallery_yaml_hash}` for provenance.

### 12f. Export Report Spec

**Location:** Auto-included as `## T3 Audit Trail` section in `report.qmd` inside every Export Bundle (2026-05-04 redesign). No separate "Export Audit Report" button. The `audit_report_enabled` app features flag has been **REMOVED (LEGACY-AUDIT-FLAG-1, Phase 34, 2026-05-22)** — deleted from all templates, `AppFeaturesValidator`, and `Bootloader`. Tombstone expires Phase 36.

**Format:** `report.qmd` is a Quarto source file included in the bundle ZIP. Users render it locally with `quarto render report.qmd`. The T3 Audit Trail section is part of this file.

**Front-matter block:**
```yaml
title: "SPARMVET Audit Report"
date: "2026-04-24"
data_analysis_recipe_id: "my_pipeline_v2"
data_analysis_recipe_sha256: "a3f9..."   # SHA256 of the pipeline data analysis recipe YAML at time of export
t3_audit_steps_sha256: "b7c1..."  # SHA256 of the serialized audit steps
```

**Report sections:**

1. **Study Context** — data analysis recipe `id`, `name`, deployment name, export timestamp.
2. **Data Summary** — dataset IDs, source paths, row counts post-assembly.
3. **Methods** — auto-generated plain English from **active** T3 nodes only:
   - `filter_row`: *"Rows were filtered to include only [column] [op] [value]. Reason: [reason]."*
   - `exclusion_row`: *"The following [column] values were explicitly excluded: [value]. Reason: [reason]."*
   - `drop_column`: *"Column '[column]' was permanently removed from the exported dataset. Reason: [reason]."*
   - `aesthetic_override`: *"Plot aesthetics were adjusted for [plot_scope]: [params summary]."*
   - `developer_raw_yaml`: *"A custom data analysis recipe fragment was applied to [plot_scope]. Reason: [reason]."*
4. **Figures** — embedded PNG outputs for each active plot sub-tab.
5. **Appendix: Decisions Considered and Discarded** — lists any `active: false` nodes by type, params, and reason. Present only if deactivated nodes exist. Framed as transparency, not Methods.
6. **Raw audit steps** — full YAML (active nodes only) appended as a fenced code block for reproducibility.

**Render engine:** Quarto only. The format selector drives `quarto render --to html|pdf|docx`. No Pandoc subprocess needed — Quarto handles all format targets internally.

---

### 12g. Per-Plot Audit Scoping & Join-Key Propagation (Phase 22-J, 2026-04-25)

**Why this exists**

A T3 audit decision (filter, exclusion, drop) is rarely "global" in a meaningful sense — it usually applies to *one plot's analytical context*. Two examples motivate per-plot scoping:

- A row filter `value > 90` makes sense on a long-format AMR similarity plot but is meaningless (or wrong) on a metadata QC plot.
- A primary-key exclusion (e.g. drop sample `S2` for poor quality) typically *should* propagate everywhere — but Case A in §12g.4 below shows when the user wants to keep that sample visible on a QC plot to **justify** the exclusion in the report.

The design replaces the old single-list `t3_audit_steps` model with a per-plot stack plus an explicit propagation choice at promotion time.

#### 12g.1. Storage shape

The single `t3_audit_steps: list[AuditStep]` is replaced by:

```python
"t3_audit_steps_by_plot": {
    "subtab_qc_box": [node_a, node_b],
    "subtab_amr_heatmap": [node_a, node_c],   # node_a propagated here, same id
    ...
}
```

Propagated nodes appear in multiple plot stacks but **share the same `id`**. Linked-deletion: deleting a node by id from one plot's panel removes it from every plot's stack.

#### 12g.2. Primary-key set

The "primary keys" set is the union of every join key declared in any assembly steps:

```yaml
joins:
  bigtable:
    tier1:
      steps:
        - action: polars_join
          'on': [sample_id]           # → {sample_id} added
        - action: polars_join
          left_on: sample_id
          right_on: sample_id         # → already in set
        - action: polars_join
          'on': [sample_id, gene_id]  # → {sample_id, gene_id} added
```

Both true primary keys (`sample_id`) and secondary/accessory keys used in long-format joins (`gene_id` in Resfinder-style tables) qualify. The set is computed once per session and recomputed on data analysis recipe reassembly.

**DECIDED, not built as described here (D-0313, D-0082):** both lists exist and are named differently: "the entity key" (declared in the recipe with `is_entity_id`; it drives the key warning and "remove from all tables") and "columns used to join" (the set above, shown as information). As built, the set above is what `primary_key_warning` uses (`session_manager.extract_primary_keys`).

**"Remove from all the data": DECIDED, built as a library step; no screen (D-0499, D-0531, D-0501).** `utils.remove_from_all.apply(..., ticked=...)` writes the removal at tier 1 only of the places the user left ticked; without a list it writes at every reached place (PROVISIONAL, the default is not decided). The library says nothing about a table where no step is written (no "may stay" sentence). The screen with the ticks is not built: the measured case of the owner (keep the entity in the quality results only) needs six places unticked, and the user cannot yet see that before confirming (`app/tests/test_remove_from_all_demo.py`).

#### 12g.3. Authoring rules — column targeting

| User action | Targeted column | Result |
|---|---|---|
| Drop column | non-key | `drop_column` AuditStep, per-plot propagation dialog |
| Drop column | **join key that a later join still uses** | **BLOCKED by place** (built 2026-11-20, merge `8772f368`, `libs/utils/src/utils/key_drop.py`): the refusal names the join that needs the column and says to use a row filter or row exclusion instead. Where no later join uses the column (for example a drop in a plot's own steps) the drop is allowed. A recipe's own steps are never refused (D-0358, D-0371). A declared entity key that no later join uses is not refused for being declared (decided 2026-11-21, ledger `D-0448`; the mark PROVISIONAL in the code is to be removed when that code is next touched). |
| Filter row (value condition) | non-key column | `filter_row` AuditStep |
| Filter row | join key, any operator | `filter_row` AuditStep with `primary_key_warning=True`. **No silent conversion.** The user's operator is preserved verbatim. The PK warning banner appears in the modal and the audit panel. |
| Filter row | non-key column whose effect happens to remove all rows for some sample | Stays as `filter_row`. The audit reports "value condition not met" — semantically different from "sample excluded". |

**Rationale (amended 2026-04-30, AUDIT-1)**: the original spec silently converted `eq`/`in` on a PK column to `ne`/`not_in` (filter_row → exclusion_row), aiming to bias the audit-report wording toward "removed". Live testing (Phase 22-J) showed this broke user mental model — `sample_id == S2` is a *select*, not a *remove*, and the silent flip surprised users. New rule: **the operator is the truth**, the `primary_key_warning` banner is the safety rail. Users who want exclusion semantics author `ne` or `not_in` directly. The warning still flows into the exported report ("⚠️ \[Primary key affected\]") so methods sections remain explicit about PK-touching decisions.

#### 12g.4. Propagation dialog

Shown at promotion time when:
- a `drop_column` node targets a non-key column (per-plot decision worth confirming; a drop of a key that a later join uses is refused by place, see 12g.3, and gets no dialog), OR
- an `exclusion_row` / primary-key-derived node is created (always propagation-eligible), OR
- an `aesthetic_override` for `color` or `shape` is created (homogeneity often desired across plots).

`alpha` aesthetic and `filter_row` on non-key columns are per-plot only — no dialog.

Three scope options:

1. **This plot only** — node added to active plot's stack only.
2. **All plots** — node copied into every plot's stack with the same `id`. New plots added later do NOT inherit (S2a — explicit re-propagation required).
3. **All plots except…** — multiselect picker showing every other plot subtab. Node copied into selected plots only. Captures "Case A" (exclude S2 from analysis but keep visible on the QC contamination plot).

**S3b — column-presence check at propagation**: when copying to other plots, skip plots whose data schema lacks the targeted column. Show a notification listing skipped plots. The audit accurately reflects which plots actually had the column to act on.

**DECIDED, not built: the Create audit step dialog that replaces this one (D-0316, D-0318, D-0325, D-0337, D-0346, D-0347, D-0451).** Every place the step can reach is ticked when the dialog opens; the user unticks what she does not want; the dialog shows the rows and plots affected before she confirms. Only distinct tables are lines (an empty tier is not a separate place: the line is the lowest level of the lineage that really has steps), each with its reach (how many tables and plots depend on it), plus a line for one plot only; a table that no plot reads but that the walk reaches is a line too (decided 2026-11-21, ledger `D-0451`); whether it is ticked when the dialog opens is not decided (the review session's reading "ticked like the others" is to be confirmed by the owner, D-0451; it replaces the earlier 'a join that no plot reads is not offered'). The places are found by asking the engine for the plan of every place (names and types) and by a walk of the lineage back, forward and back again; a place where the column has another type starts ticked and its line says what the type is there. The walk may read, beside the engine's plan, a short fixed list of what a step itself writes (the mapping of a rename, the keys and the suffix of a join, the columns of a drop or a select); each reading is checked against the plan; when they disagree the column is shown grey with the reason, never guessed, and a test on every shipped recipe fails; the plan stays the authority for what exists and its type (D-0351). A column is judged at the tier it is on: when both renames are within the same tier it is the same column (D-0352). [not decided: a rename across two tiers] A column recomputed under its own name (for example a mean per group that keeps the name, values recoded in place) is the same column, with a note: its place is offered and ticked and its line says plainly what happened there (for example one row per group after this step); the rows affected are shown per line before she confirms (D-0353). Each affected plot reads "table changed" and, separately, "picture changed". The three scope options above are what is built today.

#### 12g.5. AuditStep schema additions

Two new optional fields on every node:

```yaml
- node_type: exclusion_row
  id: "8a3f9c1d…"
  plot_scope: "subtab_amr_heatmap"     # which plot's stack this copy lives in
  primary_key_warning: true             # set when targeted column is in primary-key set
  params:
    column: sample_id
    op: not_in
    value: ["S2"]
  reason: "S2 had instrument error per lab notebook entry 2026-04-12."
```

- `primary_key_warning: bool` — set to `true` (default `false`) when authoring touched a join key. Persists in the ghost. Renders as a banner on the audit card and as a marker in the export report.
- `plot_scope: str` — the plot subtab this *copy* lives in. Replaces the previous "global / per-plot" string. Each propagated copy records its own plot_scope, but copies share `id`.

#### 12g.6. Right-sidebar audit panel

Shows only the active plot's stack (`t3_audit_steps_by_plot[active_plot_subtab]`) plus pending nodes targeting this plot. Switching plots swaps the visible stack.

A propagated node appears in every stack it was applied to — the user sees it on each plot's panel. Above the node card, a small badge: *"Applied to N plots"* (N counts unique plot_scopes for this `id`). Clicking the badge could (future) show the list.

A primary-key-warning node renders with a yellow banner above the params summary:

```
⚠️ Primary key — Primary ID/Key alignment
```

The banner explains "this filter targets a join key — removing rows here changes which samples appear in joined plots."

#### 12g.7. Pending nodes (uncommitted)

`_pending_t3_nodes` stays a flat list. At promotion time the user picks the scope; the pending node carries `plot_scopes_intent: list[str]` (the chosen target plot subtab ids, or the special token `"__all_at_apply__"` to expand to every plot at commit). On `btn_apply`:
1. Resolve `plot_scopes_intent` → concrete list of plot subtab ids.
2. For each, instantiate an AuditStep copy sharing the same `id`, with that plot's `plot_scope`.
3. Append each copy to `t3_audit_steps_by_plot[plot_scope]`.
4. Drop the pending node.

This keeps the pending area readable (one entry per user decision, not N entries).

#### 12g.8. Ghost save & restore

T3 ghost format stores `t3_audit_steps_by_plot: {plot_scope: [nodes]}` directly. Backward-compat: if an old ghost contains a flat `t3_audit_steps: [...]`, treat all nodes as targeting `__legacy__` (orphaned bucket); show a notification on restore: "*Loaded a legacy T3 ghost — N nodes are orphaned and will not apply until you re-target them. Open the Audit panel to review.*"

**Orphaned nodes after data analysis recipe restructure**: if a saved ghost has `plot_scope: "subtab_qc_box_v1"` but the current data analysis recipe only has `subtab_qc_box_v2`, those nodes are flagged at restore time and listed under an "Orphaned" section in each affected plot's audit panel. The user manually re-targets or deletes them.

#### 12g.9. Aesthetic propagation

`aesthetic_override` nodes:

| Aesthetic | Propagation dialog | Default |
|---|---|---|
| `color` | yes (dialog with three options) | "This plot only" |
| `shape` | yes | "This plot only" |
| `fill`  | yes | "This plot only" |
| `alpha` | no — per-plot only | n/a |

No primary-key warning ever applies to aesthetic nodes.

**Render-side behaviour (designed 2026-05-10):** `aesthetic_override` nodes are recorded and exported today, but **were never applied to the rendered plot** until VIZFAC-T3-OVERRIDE-1 ships. They participate as **L5 (the highest tier)** in the plot configuration cascade defined at [.claude/design/plot_config_cascade.md](../design/plot_config_cascade.md) §6, which fixes the schema as: `fill_color` ⊕ `fill_palette` (mutex with notification warning), `color`, `alpha`, `shape`, `size`, `theme`. `plot_scope` MUST be a single plot_id; cross-plot propagation is achieved by creating one node per plot via the dialog above (the propagation modal duplicates the node with linked id). The cascade rendering path is single-pass — overrides apply at the existing `VizFactory.render()` call site once VIZFAC-RESOLVER-1 + VIZFAC-RENDER-WIRE-1 + VIZFAC-T3-OVERRIDE-1 ship.

#### 12g.10. Undo & re-include

There is no "re-include" node type. The user undoes by deleting the audit node; the data reappears because the audit trail no longer removes it. With linked-id propagation, deleting a node from one plot deletes it from every plot. To "un-propagate from one plot only" the user must delete and re-author with a smaller scope.

#### 12g.11. Export report — primary-key warning persistence

`generate_methods_text` renders nodes with `primary_key_warning: true` with a leading marker:

> ⚠️ **[Primary key affected]** Excluded sample `S2` from all plots (reason: poor sequencing quality, lab notebook 2026-04-12).

The Methods section makes the user-claimed responsibility explicit. The marker is purely textual in HTML/PDF/DOCX output — the export consumer (peer reviewer, journal editor) sees that primary-key adjustments were made and how they were justified.

The Appendix ("Decisions Considered and Discarded") similarly marks deleted-but-recorded nodes (if the user deletes an audit node before export, it's gone — so this only triggers on the legacy `active: false` path).

---

## 13. Home Module State Object

The Home module state object is a `reactive.Value` dict that **survives all panel switches** (Home → Gallery → Blueprint → Home). Its audit steps and plot overrides are serialized to the T3 Ghost on apply (D-0302).

```python
home_state = reactive.Value({
    # Navigation
    "active_group_tab": None,          # str: active analysis_group tab id
    "active_plot_subtab": None,        # str: active plot sub-tab id within the group
    # (no tier_toggle: the mode and the data choice are the reactive values home_mode, data_view and source_table of server.py)

    # Accordion collapse states (True = expanded)
    "accordion_plots_expanded": True,
    "accordion_data_expanded": True,

    # Filter state (left sidebar)
    "_pending_filters": [],            # list of {column, op, value} — staged, not yet applied
    "applied_filters": [],             # list of {column, op, value, ...} — exploration rows applied on filter_apply, for the view they were built on

    # audit steps (wrangling nodes — filter, exclusion, drop_column, developer_raw_yaml)
    # Phase 22-J: per-plot stacks. Replaces the flat t3_audit_steps list. See §12g.
    "t3_audit_steps_by_plot": {},           # {plot_subtab_id: list[AuditStep]} — committed state
    "_pending_t3_nodes": [],           # pending nodes; each carries plot_scopes_intent (§12g.7)
    "primary_keys": [],                # list of column names — union of all assembly join keys (§12g.2)

    # T3 session provenance (links state to ghost file and data analysis recipe)
    "t3_ghost_file": None,             # str: path to the ghost file this session was restored from (None if new)
    "t3_ghost_saved_at": None,         # ISO str: timestamp of last ghost write

    # T3 plot aesthetic overrides (separate from wrangling steps)
    "t3_plot_overrides": {},           # {plot_subtab_id: {fill, colour, alpha, shape}}

    # Assembly provenance
    "data_analysis_recipe_sha256": None,           # str: SHA256 of the active data analysis recipe at assembly time
    "assembly_timestamp": None,        # ISO str: when the last assembly completed
})
```

**Panel independence rule:** Every top-level panel (Home, Gallery, Blueprint Architect, Test Lab) maintains its own independent state object. Switching panels never resets another panel's state. Gallery sub-tab position, Blueprint selected node, and the Home mode and data choice are all independently preserved.

**State persistence:** On every `btn_apply` a T3 Ghost `t3_{timestamp}.json` is written (§12d). It holds the audit steps, `t3_plot_overrides` and the notification log; no mode, data choice or filter state (exploration filters are never saved, D-0327).

**Reactive dependency graph:**

```
active_group_tab ──► active_plot_subtab ──► T3 table of the plot
                                          │
                        home_mode ───────►│──► plot render (Exploration: the Result; Audit: + audit steps)
                        t3_audit_steps ──►│
                        t3_plot_overrides►│
data_view, source_table, applied_filters ──► data preview only
```

A change of the viewed table clears `_pending_filters` and `applied_filters` with a notice (DECIDED: D-0311). A change to a plot that reads the same table clears nothing (DECIDED, D-0505, D-0506; built: the key holds the table, not the plot); a change to a plot that reads another table clears with the notice; a mode switch clears them (DECIDED, D-0361); a recipe change clears them (as built, ADR-099 point 1). `t3_audit_steps` are never cleared by navigation.

---

## 14. Reactive Write Discipline (Phase 22-H, 2026-04-25)

Companion rule to ADR-045 (Two-Category Law). The Two-Category Law allows handler files to contain only `@render.*` and `@reactive.*` decorators; this section adds **what may execute inside each**.

**Rule R1 — Renders are read-only.**  A `@render.*` function MUST NOT call `reactive.Value.set(...)` on any reactive value, directly or transitively. Renders read state and return UI; they never write state.

**Why:** Writing to a reactive value during a render invalidates downstream readers immediately, while the render is still running. Shiny's client/server state machine then sees illegal transitions and emits messages such as:

> Shiny server sent a message that the output 'X' is recalculating, but the output is in an unexpected state of: 'idle'.
> Shiny server has sent a progress message for 'X', but the output is in an unexpected state of: 'running'.
> Shiny server sent a message that the output 'X' has been recalculated, but the output is in an unexpected state of: 'invalidated'.

These errors are not actionable from the client side — they are always a symptom of a `set()` call inside a render.

**Rule R2 — State writes belong in `@reactive.Effect`.**  Any computation that updates a `reactive.Value` (provenance hashes, sync between input and shim values, applying transplant nodes) must live in a dedicated `@reactive.Effect`, separate from the render that reads the result.

**Rule R3 — Effects must be idempotent.**  When an `@reactive.Effect` writes to a `reactive.Value` it also reads (directly or transitively), it must guard the write with an equality check:

```python
@reactive.Effect
def _sync_X():
    new_val = compute()
    cur = state.get()
    if cur.get("X") != new_val:        # idempotent guard — prevents reactive loop
        state.set({**cur, "X": new_val})
```

Without the guard, the effect re-fires every tick and produces an infinite reactive loop.

**Lesson source:** Phase 22-H bug fix `_sync_session_provenance` (data_batch_hash + data_analysis_recipe_sha256 sync). First implementation placed the writes inside `dynamic_tabs` render; produced the three client-state errors above on every tab switch. Fix: extract to standalone `@reactive.Effect` with idempotent guard.

**Rule R4 — Don't read an input inside the render that mounts it.**  If a `@render.ui` builds an `input_*` widget AND reads that same widget's value to compute part of the rendered output, every interaction with the widget invalidates the render. The widget is destroyed and re-mounted on every keystroke/click, wiping the user's transient state (cursor position, partial selection, scroll, focus).

**Symptom:** A widget appears to "snap back" — the user clicks, sees a brief effect, then the change reverts.

**Fix:** Split into two outputs. The widget-mounting output should depend only on schema-level inputs (column lists, dataset, tier mode). The display output that *reads* the widget value goes in a separate, smaller output (e.g. a count label, a button with a count, a summary line). Re-rendering the small display on each interaction is cheap and correct; re-rendering the widget itself is the bug.

**Lesson source:** Phase 22-I (column-drop audit). `home_col_selector_ui` mounted `input_selectize("preview_col_selector")` AND read it to compute the audit-button count. Deselecting a column → re-render → selectize rebuilt with `selected=cols` (all) → user's deselection wiped. Fix: extract `col_drop_audit_btn_ui` as a separate output.

---

# CSS & Styling Rules (ADR-055, 2026-05-02)

- **CSS lives in `config/ui/theme.css`** — not inline in Python code. This is the authoritative base stylesheet, loaded at startup by `app/src/ui.py` via `bootloader.get_theme_css_path()` and injected via `ui.tags.style()`.
- **New UI styling MUST go in `config/ui/theme.css`** (or an app features specific override CSS file). Do not add `style=` attributes on individual components unless the value is truly one-off and cannot be expressed as a reusable CSS rule.
- **Branding belongs to the deployment** (ADR-091): the `branding:` block of the deployment file declares `theme_css: "config/ui/theme.css"`. A deployment overrides this key to point at a custom CSS file — no Python changes needed. `bootloader.get_theme_css_path()` resolves the active path.

---

# UI Configuration Dependencies

## Deployment (ADR-048)

Defined in deployment file. Resolution chain:
1. `SPARMVET_DEPLOYMENT` env var → path to deployment
2. `~/.sparmvet/deployment.yaml`
3. `/etc/sparmvet/deployment.yaml`
4. `config/deployment/local/local.yaml` (dev fallback)

Deployment declares `default_data_analysis_recipe`, `default_app_features`, `project_root`, and the five `locations` keys.
See `config/deployment/local/local.yaml` for the dev template.

**Path resolution (2026-05-02, ADR-048 §11):** `bootloader.get_location(key)` returns paths from `connector.resolve_paths()` output (`self._resolved_locations`), not from the raw deployment dict. UI code must always call `bootloader.get_location(key)` — never read `locations` from the deployment file directly.

## App features

Defined in app features files: `config/app_features/<app_features_id>.yaml`. App features IDs use hyphens, never underscores (e.g. `pipeline-exploration-advanced`, not `pipeline_exploration_advanced`).

Feature visibility flags: `interactivity_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `export_enabled`, `import_helper_enabled`, `metadata_ingestion_enabled`, `data_ingestion_enabled`, `blueprint_enabled`, `test_lab_enabled`, `gallery_enabled`.

See `rules_app_features_flags.md` for the authoritative flag matrix and dependency cascade rules.

## User Preferences [Implementation Deferred]

Saving location: Location 4 (`user_data`) from deployment, filename `user-preferences.yaml`.
Overrides app features file settings where permitted (priority rule).
Not implemented yet.
