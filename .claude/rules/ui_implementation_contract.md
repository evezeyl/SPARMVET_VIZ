**Status:** FINALIZED / ARCHITECTURAL LOCK — Phase 25 complete. Last update: 2026-05-04 (export redesign: scope toggle replaces separate Single Graph Export + Audit Report button; T3 audit trail auto-included in report.qmd; assembly→join rename).

# UI Implementation contract

## 1. The Tier 3 "Branching & Blueprint" Logic

Tier 3 is a sandbox branch of Tier 1. It pre-populates by copying the Tier 2 "Blueprint" recipe.

- **Node Inheritance**: Copied T2 nodes are **Violet** (#f3e5f5). New user nodes are **Yellow** (#fffde7).
- **Position Awareness**:
  - Nodes dragged **ABOVE** Violet nodes = Pre-transform (Wide Data/T1 filters).
  - Nodes dragged **BELOW** Violet nodes = Post-transform (Long Data/T2 filters).
- **The Deletion & Deactivation Protocol**:
  - **Disable (Strikethrough)**: A "Power" icon allows the user to toggle a node off. The node remains in the UI with a strikethrough effect but is ignored by the Polars engine.
  - **Trash (Permanent)**: A trash icon allows for removal. If the node is **Violet**, a modal triggers: _"CRITICAL: Removing a blueprint step may break the intended visualization. Are you sure?"_

- **The Revert Protocol**: The **btn_revert** performs a **Full Wipe**. It clears all user nodes and restores the Tier 3 stack to the exact state of the Tier 2 blueprint.
- **Direct Pass-Through**: If the T2 manifest contains zero transformation steps (T2=T1), the T3 recipe starts **Empty**.

## 2. Shell Architecture (The 3-Zone Navigator) — Updated ADR-043/ADR-044 (2026-04-23)

The UI implements a high-density **3-column nested shell** to maximize screen real estate. The right column (Pipeline Audit) is **persona-gated** and suppressed entirely for lower personas (see ADR-044):

- **Left Sidebar**: Accordion of named panels: Manifest Choice, Data Import, Filters, Export (gated — scope toggle), Session Management (gated). Panels are context-reactive — filter widgets are scoped to the active plot sub-tab's `plot_spec` aesthetics. Uses a Dark Grey (#c0c0c0) background.
- **Home Theater (Center)**: The primary workspace. Structure (post-ADR-043):
  - Top-level tabs are **exclusively** driven by manifest `analysis_groups` — no hardcoded tabs (Inspector removed).
  - Each group tab contains `navset_underline` sub-tabs (one per declared plot), wrapped in a **collapsible accordion panel**.
  - A **separate collapsible accordion panel** below shows the data preview (T1/T2 table or T3 sandbox table).
  - A **Tier Toggle** radio-button strip (T1 / T2 / T3-Wrangle / T3-Plot, persona-gated) controls which tier is displayed.
  - Uses a Neutral Grey (#d1d1d1) background.
- **Pipeline Audit (Right)**: Audit trail for T2 blueprint and T3 sandbox transitions. **Visible only for ≥ `pipeline-exploration-advanced`**. When hidden, the theater column expands to fill the full layout width — the layout element itself is excluded, not merely hidden via CSS. Uses a Dark Grey (#c0c0c0) background.

**Manifest-Driven Tab Rule**: Home tabs and sub-tabs MUST derive exclusively from `analysis_groups` in the active manifest. No hardcoded tab names or fallback tabs are permitted (ADR-003/ADR-004 compliance).

**Tier Toggle Strip** (replaces `ref_tier_switch` + `view_toggle`):

| Button | Plot Pane | Data Pane | Persona Gate |
|---|---|---|---|
| **T1 Raw** | T2 Reference Plot (read-only) | T1 Anchor table (read-only) | All |
| **T2 Reference** | T2 Reference Plot (read-only) | T2 Branch table (read-only) | All |
| **T3 Wrangling** | T3 Active Plot (Apply-gated) | T3 post-wrangling table (sandbox) | ≥ `pipeline-exploration-advanced` |
| **T3 Plot** | T3 Active Plot (Apply-gated) | T3 post-plot data slice | ≥ `pipeline-exploration-advanced` |

**Comparison Mode** (Option A — Separate Toggle, Persona-Gated, ≥ `pipeline-exploration-advanced`):

- When **ON**: theater splits into a 2-column layout — left = T1/T2 reference (per Tier Toggle), right = T3 Active.
- When **OFF**: single-pane view driven by the Tier Toggle alone.
- Replaces the previous `is_comparison` + `is_triple` flag system.

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
  1. No changes detected/made OR comments are missing (`recipe_pending == False`).
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
| **Drag Node**                | Reorder Polars operation sequence. | Update `recipe_pending` |
| **Ref Table Filter** in Tier 1 or Tier 2 Table         | Visual-only filter for inspection. | **NONE** (Transient)    |
| **Ref Table Drop**  in Tier 1 or Tier 2 Table              | Visual-only drop for inspection. | **NONE** (Transient) |                             |                                    |                         |

## 5. The Theater Layout Model (Updated ADR-043, 2026-04-23)

The theater layout is controlled by two independent controls: the **Tier Toggle** and **Comparison Mode**.

**Single-Pane Mode** (Comparison Mode OFF — all personas):

| Tier Toggle State | Plot Area | Data Area |
|---|---|---|
| T1 Raw | T2 Reference Plot (read-only) | T1 Anchor table (read-only, collapsible) |
| T2 Reference | T2 Reference Plot (read-only) | T2 Branch table (read-only, collapsible) |
| T3 Wrangling* | T3 Active Plot (Apply-gated) | T3 wrangling table (sandbox, collapsible) |
| T3 Plot* | T3 Active Plot (Apply-gated) | T3 plot slice table (sandbox, collapsible) |

*T3 states hidden for personas < `pipeline-exploration-advanced`.

**Comparison Mode** (ON — ≥ `pipeline-exploration-advanced`):

```
┌──────────────────────┬──────────────────────┐
│  T2 Reference Plot   │  T3 Active Plot       │  ← Plot accordion (collapsible)
├──────────────────────┼──────────────────────┤
│  T1/T2 Data (R/O)   │  T3 Sandbox Data      │  ← Data accordion (collapsible)
└──────────────────────┴──────────────────────┘
```

- Left column tier (T1 or T2) is driven by the Tier Toggle.
- Both plot and data rows are independently collapsible via accordion panels.
- The previous `theater_grid` toggle, `btn_max_plot`, `btn_max_table`, and `btn_reset_theater` controls are **removed** (superseded by this model).

## 6. Component Interaction Matrix

|**Zone**|**ID**|**Reactive Behavior**|
|---|---|---|
|**Table Ref**|`table_ref`|**Visual Only**: Filtering here updates the table view but creates NO audit nodes and does NOT trigger the Apply button.|
|**Table Active**|`table_active`|**Recipe Driver**: "Brush" events or column de-selections automatically generate a new **Yellow Node** in the Audit Stack.|
|**Audit Stack**|`audit_stack`|**Order Matters**: Drag-and-drop reordering of nodes marks `recipe_pending = True`.|

## 7. Session Management vs. Global Export

To ensure a clean separation between "Working State" and "Final Provenance," the UI distinguishes between these two actions:

### 7.1 Session Management (Left Sidebar — Session Management Panel)

**Panel:** `Session Management` accordion panel in the left sidebar. Gate: `session_management_enabled`. Absent for `pipeline-static` and `pipeline-exploration-simple`.

**Function:** Persists and restores the full working state so a user can resume interrupted work, or maintain separate sessions for different pipeline runs (e.g., AMR pipeline run 2025-01 vs run 2025-06).

**What is saved per session:**
- Active `t3_recipe` (all Yellow nodes and their comment fields)
- `applied_filters` (committed filter rows)
- Active sub-tab and tier toggle state
- Reference to the active manifest and data source (so the session knows which pipeline run it belongs to)
- If metadata was replaced (see §9): reference to the uploaded metadata filename

**Session model:**
- Each session is a named `.json` file stored in a subdirectory of Location 4 (`user_sessions/sessions/<session_id>.json`).
- Multiple sessions are allowed per user — users can switch between sessions (different pipeline runs, different dates).
- Sessions are **named at save time** — the UI prompts for a session label (e.g., "AMR_run_Jan2025").

**Ghost save:**
- Automatic background save on every `btn_apply` press and on every filter commit.
- Stored as `user_sessions/sessions/_autosave.json` — single slot, always overwritten.
- Restored automatically if the app detects an autosave newer than the last explicit session save.

**Save location:** `user_sessions` (Location 4) from the active deployment profile. This path is deployment-specific — on Galaxy it maps to a Galaxy-accessible path; on a local machine it is a local directory. Users only have write access to Location 4 — they cannot choose an arbitrary path.

**UI controls (Session Management accordion panel):**
- **Export Active Session (.zip)** — panel header button; downloads the full `_sessions/{session_key}/` directory as a `.zip` for archiving or sharing.
- Per-session card actions: **Restore** (load T1/T2 assembly + T3 ghost picker) and **Delete** (removes session directory; confirmation required). Per-session Export was removed in Phase 25-G — use the header-level Export Active Session instead.

---

### 7.2 Export Results Bundle (Export Panel — Left Sidebar, ADR-047, updated 2026-05-04)

**Panel:** `Export` accordion panel (renamed from "Global Project Export" in export redesign 2026-05-04). Gate: `export_enabled`.

**Implementation:** `@render.download export_bundle_download` in `app/handlers/export_handlers.py`.

**UI Controls:**
- `export_bundle_label` (text, sanitized — label is "Bundle label / name", not "Your name"). Sanitized: `re.sub(r"[^A-Za-z0-9_-]", "_", raw)[:40]`.
- `plot_format` selector: **PNG** / **SVG** / **PDF**.
- **3-way scope toggle** `export_scope`: `global` (all plots in project) / `group` (all plots in active group tab) / `plot` (active plot sub-tab only). "Active group" and "Active plot" options are shown with reduced opacity when no plot tab is active.
- Filter warning shown when `applied_filters` non-empty.
- Download button: `📦 Export Bundle`.

**Scope detection at download time:** reads `safe_input(input, "export_scope", "global")` and `active_home_subtab.get()` to filter which plots are included. Scope label recorded in `t3_steps.yaml` and `README.txt`.

**Filename:** `YYYYMMDD_HHMMSS_<label>_results.zip`.

**Bundle contents:**

| Path | Contents |
|------|---------|
| `plots/` | PNG/SVG/PDF per plot in scope |
| `data/<ds>_T1.tsv` | T1 (Assembled) — always |
| `data/<ds>_T2.tsv` | T2 (Analysis-ready) — always |
| `data/<ds>_T3.tsv` | T3 (User-adjusted) — advanced+ persona only when `tier_toggle=="T3"` |
| `recipes/<proj>/` | All YAML wrangling/join/plot files for the active project |
| `FILTERS.txt` | Filter trace when `applied_filters` non-empty ("No Trace No Export" — ADR-021 extension) |
| `recipes/t3_steps.yaml` | T3 committed nodes (active only) — auto-included when T3 has committed nodes and `t3_sandbox_enabled` |
| `report.qmd` | Quarto source: front-matter, filter table, figure includes, data section, **T3 Audit Trail** section (per-plot table of Step/Action/Details/Justification when T3 has active nodes) |
| `README.txt` | Bundle manifest: timestamp, project, persona, scope, tiers, metadata source filename, counts |

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

**No separate Export Audit Report button.** The audit trail is auto-included in `report.qmd` inside the bundle. The `audit_report_enabled` persona flag is retained in the validator for backwards compat but is unused by the UI.

**Single Graph Export accordion removed.** Superseded by the "Active plot" scope option in the 3-way toggle (see §7.3).

**Metadata provenance in bundle:** If a custom metadata file was uploaded (§9), its original filename is recorded in `README.txt` and in the `report.qmd` front-matter.

**Export location:** Browser download. Works identically in Galaxy, IRIDA, and local deployments.

**Deferred:**
- Per-plot checkbox selection (all in-scope plots always exported).
- Server-side write to Location 4.

---

### 7.3 Export Active Graph ⚠️ Superseded

**Status:** The `Single Graph Export` accordion panel was **removed** in the 2026-05-04 export redesign.

The "Active plot" scope option in the 3-way scope toggle (§7.2) replaces this panel. Selecting `[Active plot]` in the scope toggle and clicking `📦 Export Bundle` produces a single-plot bundle containing only the active plot's data, recipe, and audit trail. The `export_enabled` flag now gates the full Export panel (both the bundle and the scope toggle) rather than a separate accordion.

## 8. Filter Recipe Builder (Phase 21-F — Left Sidebar, 2026-04-23)

Row filters live in the left sidebar (Home mode only). They affect both plots and the data preview.

**State model:**
- `_pending_filters`: staging area (`reactive.Value[list]`) — rows added by user, not yet applied.
- `applied_filters`: committed (`reactive.Value[list]`) — consumed by all `@render.plot` handlers and `home_data_preview`.

**Each row:** `{column: str, op: "eq"|"ne"|"gt"|"ge"|"lt"|"le"|"in"|"not_in", value: str|list[str], dtype: str}`.

**Ops for discrete columns (or `scale_x_discrete` declared):** `in`, `not_in`, `eq`, `ne`.
**Ops for numeric columns:** `eq`, `ne`, `gt`, `ge`, `lt`, `le`.

**Type coercion rule:** Values are always stored as strings (selectize returns strings). `_apply_filter_rows` casts column to Utf8 for set ops (`in`/`not_in`); coerces scalar value to column dtype for numeric comparisons. Auto-promotes `eq`→`in` / `ne`→`not_in` when value is a list.

**VizFactory predicate pushdown:** `applied_filters` are injected into `plot_config["filters"]` (without `dtype`) before `viz_factory.render()`. VizFactory supports: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`.
  
## 9. Metadata Ingestion (Data Import Panel — Left Sidebar)

**Purpose:** Allow a user to upload an updated metadata file that replaces the metadata source for the active pipeline run. This is a **full replacement** — the uploaded file becomes the new source of truth for that metadata source. It triggers a T1 rebuild.

**When used:** Users correct errors in metadata (e.g., wrong collection date, corrected resistance phenotype, updated sample annotations) and need the plots to reflect the correction without re-running the upstream pipeline.

**Panel:** `Data Import` accordion panel in the left sidebar. When `import_helper_enabled: true`, metadata upload is nested above the multi-file ingestion control. When `import_helper_enabled: false` and `metadata_ingestion_enabled: true`, it appears as a standalone control in the Data Import panel.

**Persona gate:** Gate: `metadata_ingestion_enabled`. Available from `pipeline-exploration-advanced` and above. Hidden for `pipeline-static` and `pipeline-exploration-simple`.

**Flow:**
1. User uploads a TSV/CSV metadata file via file input in the Data Import panel.
2. `MetadataValidator` gates the upload: validates that required columns (defined in `input_fields` contract for the metadata schema) are present. Uses fuzzy matching to suggest corrections if columns are missing.
3. If validation passes: the uploaded file is written to Location 1 (`raw_data`) as the new metadata source, **replacing** the previous file. The original filename is recorded (for provenance).
4. T1 rebuild is triggered automatically — the DataOrchestrator re-runs ingestion and assembly. A "Recalculating..." overlay is shown.
5. On completion: T2 and all plots update. A notification confirms: "Metadata updated from `<filename>`. T1 rebuilt."

**Provenance obligation:** The original uploaded filename (not just its path) is stored in a sidecar file (e.g., `metadata_provenance.yaml` in Location 1) so that exports and session files can reference it. This filename is included in `README.txt` and `report.qmd` of any subsequent export bundle.

**What is NOT replaced:** Raw instrument data (sequencing results, VCF files, etc.) — only the metadata source. The manifest's `input_fields` contract determines which file is considered "metadata" for validation purposes.

**Status:** Deferred to Phase 22+. UI stub (greyed file input + label) present in Data Import panel when persona allows. Validation and rebuild flow designed here; implementation pending.

---

## 10. Data Ingestion & Excel Converter (Data Import Panel — Left Sidebar)

**Purpose:** Allow a user to provide raw data files when the app is deployed independently of an automated pipeline (e.g., pipeline deposited results in an Excel file that the user now uploads manually).

**Panel:** `Data Import` accordion panel in the left sidebar. Multi-file ingestion section is nested inside when `import_helper_enabled: true`.

**Persona gate:** `import_helper_enabled: true` in persona template. Available to ≥ `project-independent` and `developer`. Hidden for lower personas. Also deactivatable at the deployment level (profile sets `data_ingestion_enabled: false`) for deployments where data is always pushed automatically by a pipeline — the Data Import ingestion section is suppressed entirely (metadata upload remains available, see §9).

**Supported ingestion types:**
- **Raw data** — TSV/CSV instrument output
- **Metadata** — sample annotation files (goes through MetadataValidator gate, same as §9)
- **Extra data** — supplementary tables (e.g., reference databases, additional annotation layers)

**Manifest association:** When uploading, the user must associate the file with a manifest schema (dropdown of known schemas from `locations.manifests`). This tells the DataOrchestrator which `input_fields` contract to validate against and which pipeline slot the file fills.

**Multi-file upload:** A `+` button allows queuing multiple files (e.g., one per schema). Each queued file shows its assigned schema and validation status before the user commits the ingestion.

**Excel → TSV Converter (within Data Ingestion):**
- Available as a sub-step when an `.xlsx` file is uploaded.
- App reads sheet names from the workbook (via `ExcelHandler` — `libs/ingestion/src/ingestion/excel_handler.py`).
- User assigns each sheet to a role: **raw data**, **metadata**, or **extra data**, and selects the target schema from the manifest dropdown.
- Converter writes TSVs to Location 1 (`raw_data`) in the user-accessible directory.
- After conversion, the resulting TSVs are queued for ingestion as normal.
- **Why here and not Test Lab:** Scientists receive Excel files from collaborators and pipelines — this is a practical data preparation step, not a developer concern. Test Lab (developer persona only) is for synthetic data generation (AquaSynthesizer).

**Status:** Deferred to Phase 22+. Design finalized here. `ExcelHandler` backend already exists.

---

## 11. Left Sidebar — Accordion Panel Structure (Phase 25-E)

The left sidebar content is **not static** — it changes based on which top-level panel (mode) is active. The same sidebar slot renders different content per panel.

| Active Panel | Left Sidebar Content |
|---|---|
| **Home** | `#nav_accordion` — panels: Manifest Choice, Data Import, Filters, Export (gated, scope toggle), Session Management (gated) |
| **Blueprint Architect** | Manifest/component navigation (dataset pipeline selector, TubeMap node selector) |
| **Gallery** | Focus Mode (ADR-038) — operation controls hidden; search/filter for gallery only |
| **Test Lab** | TBD — deferred until Test Lab is finalized. Left sidebar content for this panel is an open design question. |

**Home accordion panels (Phase 25-E):**

| Panel | Content | Gate |
|---|---|---|
| **Manifest Choice** | Manifest selector (`manifest_selector.visible` must be `true` in persona template) | `manifest_selector.visible` |
| **Data Import** | Metadata upload (§9, always if `metadata_ingestion_enabled`) + multi-file ingestion + Excel converter (§10, when `import_helper_enabled`) | `metadata_ingestion_enabled` or `import_helper_enabled` |
| **Filters** | Filter Recipe Builder row widgets (§8) | always (Home only) |
| **Export** | Export Bundle with 3-way scope toggle (§7.2). T3 Audit Trail auto-included in report.qmd (§12f). | `export_enabled` |
| **Session Management** | Session list + Restore/Delete + Export Active Session header button (§7.1) | `session_management_enabled` |

**Implementation rule:** The `sidebar_nav_ui` render function reads the active top-level nav item and renders the appropriate sidebar content. Switching panels clears and replaces the entire left sidebar DOM subtree (not CSS-hide — physical replacement, following the Shell Stability Law in §3a of `project_conventions.md`).

**Filter Recipe Builder scope:** Filters are a Home-mode-only feature. They are never rendered in Blueprint Architect, Gallery, or Test Lab left sidebars. The filter `_pending_filters` and `applied_filters` reactive state is preserved across panel switches but the filter UI widgets are only mounted when Home is active.

**Blueprint Architect left sidebar:** May eventually include filter-like controls (e.g., field search, schema filtering within the TubeMap) — decision deferred until Architect mode is finalized. Not the same as the Home row-filter system.

---

## 12. Tier 3 Audit Trace — Publication Finisher

### 12a. Scope Lock

T3 is a **Publication Finisher**, not a wrangling sandbox. Its scope is permanently locked to four node types:

| Node Type | What it does | Reason required? |
|---|---|---|
| `filter_row` | Row-level inclusion filter `{column, op, value}` | **Mandatory** |
| `exclusion_row` | Explicit row exclusion (named sample / value) | **Mandatory** |
| `drop_column` | Permanently drop a column from the exported data (not just hidden in preview) | **Mandatory** |
| `aesthetic_override` | Plot colour / fill / alpha / shape changes (per plot sub-tab) | Optional — included in report |
| `developer_raw_yaml` | Escape hatch: arbitrary manifest fragment (≥ `pipeline-exploration-advanced` / `developer` persona only) | **Mandatory** |

**Gatekeeper rule:** `btn_apply` is **locked** if any `filter_row`, `exclusion_row`, `drop_column`, or `developer_raw_yaml` node has an empty `reason` field. `aesthetic_override` nodes never block apply.

**`drop_column` is permanent within the session:** it physically removes the column from the working frame — it does not merely hide it in the UI. This is the unambiguous truth the export reflects. There is no "column_visibility" toggle that hides without dropping; any column removal in T3 must be justified and is permanent until the node is deactivated.

T3 never exposes an action-picker UI. Wrangling (rename, cast, derive, split, etc.) is always done in Tier 1/2 manifests — never in T3.

### 12b. RecipeNode Schema

Each node in the T3 recipe is a YAML mapping:

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

### 12c. T3 Recipe IS the Audit Trace

There is **no separate FILTERS.txt** for T3. The T3 YAML recipe is the complete audit trail.

- Every Yellow node has `id`, `created_at`, `plot_scope`, `params`, and `reason`.
- The recipe is append-only during a session (deletions mark nodes `active: false` rather than removing them from the file, so the sequence of decisions is preserved).
- **Export warning for deactivated nodes:** If any node has `active: false` at export time, the UI shows a blocking warning dialog: *"You have [N] deactivated filter(s) / exclusion(s) / column drop(s). Export reflects only active nodes. Deactivated nodes will NOT appear in the exported data or Methods section. Confirm you want to discard them from this export?"* The user must explicitly confirm. The export is the unambiguous truth — deactivated nodes are absent from the exported data and from the Methods section. They are listed in an appendix ("Decisions Considered and Discarded") for transparency only.

`aesthetic_override` nodes are stored **separately** from the wrangling recipe as `t3_plot_overrides` (a dict keyed by plot sub-tab ID) in the session state object (§13). They are included in the export report but do not block `btn_apply`.

### 12d. Ghost Save — Two Slots

#### Session Identity

A **session** is the combination of one manifest + one data batch. The same manifest run against different data batches (e.g., batch A vs. batch B of ST22 samples) produces different sessions. Two discriminators are combined:

- **`manifest_sha256`**: SHA256 of the pipeline manifest YAML. Changes if the manifest is edited (wrangling steps, field definitions, join recipe).
- **`data_batch_hash`**: A single SHA256 derived by hashing all per-source-file SHA256s together in deterministic (sorted) order. Changes when any input file is replaced, even if the manifest is unchanged.

```
session_key = manifest_sha256[:12] + ":" + data_batch_hash[:12]
# e.g. "a3f9c81b04e2:c4d29e1a3f80"
```

Using content hashes (not IDs or names) means the key is invariant to manifest renames, path changes, or file moves — only content changes produce a new key. The `session_key` namespaces both ghost file directories and Parquet output paths so sessions for different manifests or different data batches never collide.

---

#### Ghost Slots

| Slot | File | Written when | Content |
|---|---|---|---|
| **T1/T2 Ghost** | `_sessions/{session_key}/assembly.json` | Once on first assembly; re-written when manifest or source data changes | Manifest ID + SHA256, source files + per-file SHA256, `data_batch_hash`, assembled Parquet paths, assembly timestamp |
| **T3 Ghost** | `_sessions/{session_key}/t3_{timestamp}.json` | On every `btn_apply`; on every panel switch away from Home | Full T3 recipe YAML + `t3_plot_overrides` + tier toggle + `session_key` + `saved_at` |

Both slots live under `{Location_4}/_sessions/{session_key}/`. All ghost files for a session are co-located, making it easy to archive, share, or delete a full session as a unit.

---

#### T1/T2 Ghost Content

```json
{
  "session_key": "my_pipeline_v2:c4d29e1a3f80",
  "manifest_id": "my_pipeline_v2",
  "manifest_sha256": "a3f9...",
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

1. Scan `_sessions/` for all `assembly.json` files. Compute the current `data_batch_hash` from the active manifest's source files.
2. Find the matching session by `session_key` (manifest_id + data_batch_hash).
3. **Match found AND Parquet files exist on disk** → short-circuit: load existing Parquet, skip re-assembly. Normal fast path.
4. **Match found BUT Parquet files missing** (e.g., tmp/ cleared, server restart) → re-assemble silently from source files listed in the ghost. Rewrite Parquet paths after completion. No user action required.
5. **No match** (new batch or new manifest) → full assembly, write new session ghost.
6. **Source files missing from disk** (user moved data) → blocking UI error: *"Source data for '[dataset_id]' cannot be found at [path]. Please re-upload or update the manifest."* Assembly blocked until resolved.

T1/T2 state is always self-healing: lost Parquet is recovered automatically from the ghost as long as source data is accessible.

---

#### T3 Ghost Content

```json
{
  "session_key": "my_pipeline_v2:c4d29e1a3f80",
  "manifest_id": "my_pipeline_v2",
  "manifest_sha256": "a3f9...",
  "data_batch_hash": "c4d29e1a3f80...",
  "saved_at": "2026-04-24T14:30:12",
  "label": "",
  "tier_toggle": "T3",
  "t3_recipe": [],
  "t3_plot_overrides": {}
}
```

`label` is an optional user-supplied name (e.g., "batch-A final filters"). Empty by default; editable from the session panel.

**Manifest SHA256 mismatch on restore:** If the saved `manifest_sha256` differs from the current manifest, the UI warns: *"This session was saved against a different manifest version. Recipe nodes referencing renamed or removed columns may fail. Proceed with caution."* The user can still restore but is not blocked.

**Data batch mismatch on restore:** If `data_batch_hash` differs (user loaded a different data batch), the UI warns: *"This session was saved against a different data batch. Row filters and exclusions may match different or no rows."* Again, non-blocking — user confirms.

---

#### Session Management Panel

Accessible from the **Session Management** accordion panel in the left sidebar (gate: `session_management_enabled`; ≥ `pipeline-exploration-advanced`).

**Session list view:** All sessions in `_sessions/` displayed as cards, grouped by `manifest_id`, sorted by most-recent T3 ghost `saved_at` within each group. Each card shows:
- `manifest_id` + short `data_batch_hash` (first 8 chars)
- User `label` (editable inline)
- Last saved timestamp
- Number of T3 ghosts (saves) in that session

**Per-session actions:**
- **Restore** — loads T1/T2 assembly state + opens a T3 ghost picker (list of all `t3_{timestamp}.json` files for that session, sorted newest-first). User selects which T3 snapshot to resume, or "Start fresh T3" to keep T1/T2 but clear T3.
- **Export session** — downloads the full `_sessions/{session_key}/` directory as a `.zip` for archiving or sharing. Includes both assembly ghost and all T3 ghosts.
- **Import session** — accepts a `.zip` exported by another user or machine. Validates `session_key`, checks source file availability, registers in the local `_sessions/` store.
- **Delete session** — removes the session directory and all its ghosts. Confirmation required.

T3 ghost is never written on intermediate filter edits — only on apply or panel leave. Restoring a T3 ghost triggers the T1/T2 restore logic first (steps 1–6 above) to ensure the Parquet base is valid before applying T3 nodes.

### 12e. Gallery → T3 Transplant Rules

**Persona gate:** Gallery transplant into the T3 sandbox is available to **`pipeline-exploration-advanced` and `developer` personas only**. Lower personas (static, simple) can browse the gallery but the "Send to T3" button is hidden.

- Gallery transplant always targets the **last-active plot sub-tab** in Home.
- A transplanted gallery node is inserted as a Yellow `developer_raw_yaml` node with `reason: ""` (empty, blocking apply).
- The `reason` field is pre-focused in the UI immediately after transplant so the user fills it before doing anything else.
- The transplanted node carries a `gallery_source` metadata field: `{gallery_id, gallery_yaml_hash}` for provenance.
- Gallery transplant is **deferred** — no changes are applied until `btn_apply` is pressed. If the user navigates away from Home before applying, the pending transplant is preserved in `_pending_t3_nodes` (see §13).

### 12f. Export Report Spec

**Location:** Auto-included as `## T3 Audit Trail` section in `report.qmd` inside every Export Bundle (2026-05-04 redesign). No separate "Export Audit Report" button. The `audit_report_enabled` persona flag is retained in the validator for backwards compat but is no longer used by the UI.

**Format:** `report.qmd` is a Quarto source file included in the bundle ZIP. Users render it locally with `quarto render report.qmd`. The T3 Audit Trail section is part of this file.

**Front-matter block:**
```yaml
title: "SPARMVET Audit Report"
date: "2026-04-24"
manifest_id: "my_pipeline_v2"
manifest_sha256: "a3f9..."   # SHA256 of the pipeline manifest YAML at time of export
t3_recipe_sha256: "b7c1..."  # SHA256 of the serialized T3 recipe
```

**Report sections:**

1. **Study Context** — manifest `id`, `name`, deployment profile name, export timestamp.
2. **Data Summary** — dataset IDs, source paths, row counts post-assembly.
3. **Methods** — auto-generated plain English from **active** T3 nodes only:
   - `filter_row`: *"Rows were filtered to include only [column] [op] [value]. Reason: [reason]."*
   - `exclusion_row`: *"The following [column] values were explicitly excluded: [value]. Reason: [reason]."*
   - `drop_column`: *"Column '[column]' was permanently removed from the exported dataset. Reason: [reason]."*
   - `aesthetic_override`: *"Plot aesthetics were adjusted for [plot_scope]: [params summary]."*
   - `developer_raw_yaml`: *"A custom manifest fragment was applied to [plot_scope]. Reason: [reason]."*
4. **Figures** — embedded PNG outputs for each active plot sub-tab.
5. **Appendix: Decisions Considered and Discarded** — lists any `active: false` nodes by type, params, and reason. Present only if deactivated nodes exist. Framed as transparency, not Methods.
6. **Raw T3 Recipe** — full YAML (active nodes only) appended as a fenced code block for reproducibility.

**Render engine:** Quarto only. The format selector drives `quarto render --to html|pdf|docx`. No Pandoc subprocess needed — Quarto handles all format targets internally.

---

### 12g. Per-Plot Audit Scoping & Join-Key Propagation (Phase 22-J, 2026-04-25)

**Why this exists**

A T3 audit decision (filter, exclusion, drop) is rarely "global" in a meaningful sense — it usually applies to *one plot's analytical context*. Two examples motivate per-plot scoping:

- A row filter `value > 90` makes sense on a long-format AMR similarity plot but is meaningless (or wrong) on a metadata QC plot.
- A primary-key exclusion (e.g. drop sample `S2` for poor quality) typically *should* propagate everywhere — but Case A in §12g.4 below shows when the user wants to keep that sample visible on a QC plot to **justify** the exclusion in the report.

The design replaces the old single-list `t3_recipe` model with a per-plot stack plus an explicit propagation choice at promotion time.

#### 12g.1. Storage shape

The single `t3_recipe: list[RecipeNode]` is replaced by:

```python
"t3_recipe_by_plot": {
    "subtab_qc_box": [node_a, node_b],
    "subtab_amr_heatmap": [node_a, node_c],   # node_a propagated here, same id
    ...
}
```

Propagated nodes appear in multiple plot stacks but **share the same `id`**. Linked-deletion: deleting a node by id from one plot's panel removes it from every plot's stack.

#### 12g.2. Primary-key set

The "primary keys" set is the union of every join key declared in any assembly recipe:

```yaml
join_manifests:
  bigtable:
    recipe:
      - action: join
        on: sample_id           # → {sample_id} added
      - action: join
        left_on: sample_id
        right_on: sample_id     # → already in set
      - action: join
        on: [sample_id, gene_id]  # → {sample_id, gene_id} added
```

Both true primary keys (`sample_id`) and secondary/accessory keys used in long-format joins (`gene_id` in Resfinder-style tables) qualify. The set is computed once per session and recomputed on manifest reassembly.

#### 12g.3. Authoring rules — column targeting

| User action | Targeted column | Result |
|---|---|---|
| Drop column | non-key | `drop_column` RecipeNode, per-plot propagation dialog |
| Drop column | **any join key** | **BLOCKED** — notification: *"Column [c] is a join key — cannot be dropped. Use a row filter or row exclusion instead."* |
| Filter row (value condition) | non-key column | `filter_row` RecipeNode |
| Filter row | join key, any operator | `filter_row` RecipeNode with `primary_key_warning=True`. **No silent conversion.** The user's operator is preserved verbatim. The PK warning banner appears in the modal and the audit panel. |
| Filter row | non-key column whose effect happens to remove all rows for some sample | Stays as `filter_row`. The audit reports "value condition not met" — semantically different from "sample excluded". |

**Rationale (amended 2026-04-30, AUDIT-1)**: the original spec silently converted `eq`/`in` on a PK column to `ne`/`not_in` (filter_row → exclusion_row), aiming to bias the audit-report wording toward "removed". Live testing (Phase 22-J) showed this broke user mental model — `sample_id == S2` is a *select*, not a *remove*, and the silent flip surprised users. New rule: **the operator is the truth**, the `primary_key_warning` banner is the safety rail. Users who want exclusion semantics author `ne` or `not_in` directly. The warning still flows into the exported report ("⚠️ \[Primary key affected\]") so methods sections remain explicit about PK-touching decisions.

#### 12g.4. Propagation dialog

Shown at promotion time when:
- a `drop_column` node targets a non-key column (per-plot decision worth confirming), OR
- an `exclusion_row` / primary-key-derived node is created (always propagation-eligible), OR
- an `aesthetic_override` for `color` or `shape` is created (homogeneity often desired across plots).

`alpha` aesthetic and `filter_row` on non-key columns are per-plot only — no dialog.

Three scope options:

1. **This plot only** — node added to active plot's stack only.
2. **All plots** — node copied into every plot's stack with the same `id`. New plots added later do NOT inherit (S2a — explicit re-propagation required).
3. **All plots except…** — multiselect picker showing every other plot subtab. Node copied into selected plots only. Captures "Case A" (exclude S2 from analysis but keep visible on the QC contamination plot).

**S3b — column-presence check at propagation**: when copying to other plots, skip plots whose data schema lacks the targeted column. Show a notification listing skipped plots. The audit accurately reflects which plots actually had the column to act on.

#### 12g.5. RecipeNode schema additions

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

Shows only the active plot's stack (`t3_recipe_by_plot[active_plot_subtab]`) plus pending nodes targeting this plot. Switching plots swaps the visible stack.

A propagated node appears in every stack it was applied to — the user sees it on each plot's panel. Above the node card, a small badge: *"Applied to N plots"* (N counts unique plot_scopes for this `id`). Clicking the badge could (future) show the list.

A primary-key-warning node renders with a yellow banner above the params summary:

```
⚠️ Primary key — Primary ID/Key alignment
```

The banner explains "this filter targets a join key — removing rows here changes which samples appear in joined plots."

#### 12g.7. Pending nodes (uncommitted)

`_pending_t3_nodes` stays a flat list. At promotion time the user picks the scope; the pending node carries `plot_scopes_intent: list[str]` (the chosen target plot subtab ids, or the special token `"__all_at_apply__"` to expand to every plot at commit). On `btn_apply`:
1. Resolve `plot_scopes_intent` → concrete list of plot subtab ids.
2. For each, instantiate a RecipeNode copy sharing the same `id`, with that plot's `plot_scope`.
3. Append each copy to `t3_recipe_by_plot[plot_scope]`.
4. Drop the pending node.

This keeps the pending area readable (one entry per user decision, not N entries).

#### 12g.8. Ghost save & restore

T3 ghost format stores `t3_recipe_by_plot: {plot_scope: [nodes]}` directly. Backward-compat: if an old ghost contains a flat `t3_recipe: [...]`, treat all nodes as targeting `__legacy__` (orphaned bucket); show a notification on restore: "*Loaded a legacy T3 ghost — N nodes are orphaned and will not apply until you re-target them. Open the Audit panel to review.*"

**Orphaned nodes after manifest restructure**: if a saved ghost has `plot_scope: "subtab_qc_box_v1"` but the current manifest only has `subtab_qc_box_v2`, those nodes are flagged at restore time and listed under an "Orphaned" section in each affected plot's audit panel. The user manually re-targets or deletes them.

#### 12g.9. Aesthetic propagation

`aesthetic_override` nodes:

| Aesthetic | Propagation dialog | Default |
|---|---|---|
| `color` | yes (dialog with three options) | "This plot only" |
| `shape` | yes | "This plot only" |
| `fill`  | yes | "This plot only" |
| `alpha` | no — per-plot only | n/a |

No primary-key warning ever applies to aesthetic nodes.

#### 12g.10. Undo & re-include

There is no "re-include" node type. The user undoes by deleting the audit node; the data reappears because the recipe no longer removes it. With linked-id propagation, deleting a node from one plot deletes it from every plot. To "un-propagate from one plot only" the user must delete and re-author with a smaller scope.

#### 12g.11. Export report — primary-key warning persistence

`generate_methods_text` renders nodes with `primary_key_warning: true` with a leading marker:

> ⚠️ **[Primary key affected]** Excluded sample `S2` from all plots (reason: poor sequencing quality, lab notebook 2026-04-12).

The Methods section makes the user-claimed responsibility explicit. The marker is purely textual in HTML/PDF/DOCX output — the export consumer (peer reviewer, journal editor) sees that primary-key adjustments were made and how they were justified.

The Appendix ("Decisions Considered and Discarded") similarly marks deleted-but-recorded nodes (if the user deletes an audit node before export, it's gone — so this only triggers on the legacy `active: false` path).

---

## 13. Home Module State Object

The Home module state object is a `reactive.Value` dict that **survives all panel switches** (Home → Gallery → Blueprint → Home). It is serialized to the T3 Ghost on apply and on panel leave.

```python
home_state = reactive.Value({
    # Navigation
    "active_group_tab": None,          # str: active analysis_group tab id
    "active_plot_subtab": None,        # str: active plot sub-tab id within the group
    "tier_toggle": "T2",               # "T1" | "T2" | "T3"

    # Accordion collapse states (True = expanded)
    "accordion_plots_expanded": True,
    "accordion_data_expanded": True,

    # Filter state (left sidebar)
    "_pending_filters": [],            # list of {column, op, value} — staged, not yet applied
    "applied_filters": [],             # list of {column, op, value} — committed on btn_apply

    # T3 recipe (wrangling nodes — filter, exclusion, drop_column, developer_raw_yaml)
    # Phase 22-J: per-plot stacks. Replaces the flat t3_recipe list. See §12g.
    "t3_recipe_by_plot": {},           # {plot_subtab_id: list[RecipeNode]} — committed state
    "_pending_t3_nodes": [],           # pending nodes; each carries plot_scopes_intent (§12g.7)
    "primary_keys": [],                # list of column names — union of all assembly join keys (§12g.2)

    # T3 session provenance (links state to ghost file and manifest)
    "t3_ghost_file": None,             # str: path to the ghost file this session was restored from (None if new)
    "t3_ghost_saved_at": None,         # ISO str: timestamp of last ghost write

    # T3 plot aesthetic overrides (separate from wrangling recipe)
    "t3_plot_overrides": {},           # {plot_subtab_id: {fill, colour, alpha, shape}}

    # Assembly provenance
    "manifest_sha256": None,           # str: SHA256 of the active manifest at assembly time
    "assembly_timestamp": None,        # ISO str: when the last assembly completed
})
```

**Panel independence rule:** Every top-level panel (Home, Gallery, Blueprint Architect, Test Lab) maintains its own independent state object. Switching panels never resets another panel's state. Gallery sub-tab position, Blueprint selected node, and Home tier toggle are all independently preserved.

**State persistence:** On every `btn_apply`, `home_state` is serialized to `_autosave_t3.json` (T3 Ghost slot). On panel switch away from Home, only `t3_recipe`, `_pending_t3_nodes`, `t3_plot_overrides`, `tier_toggle`, and the two accordion states are written (not filter state, which is already committed).

**Reactive dependency graph:**

```
active_group_tab ──► active_plot_subtab ──► tier_toggle
                                          │
                        applied_filters ──►│──► plot render
                        t3_recipe       ──►│
                        t3_plot_overrides ►│
```

Tab changes clear `_pending_filters` and `_pending_t3_nodes` but never touch `applied_filters` or `t3_recipe` (committed state is never cleared by navigation).

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

**Lesson source:** Phase 22-H bug fix `_sync_session_provenance` (data_batch_hash + manifest_sha256 sync). First implementation placed the writes inside `dynamic_tabs` render; produced the three client-state errors above on every tab switch. Fix: extract to standalone `@reactive.Effect` with idempotent guard.

**Rule R4 — Don't read an input inside the render that mounts it.**  If a `@render.ui` builds an `input_*` widget AND reads that same widget's value to compute part of the rendered output, every interaction with the widget invalidates the render. The widget is destroyed and re-mounted on every keystroke/click, wiping the user's transient state (cursor position, partial selection, scroll, focus).

**Symptom:** A widget appears to "snap back" — the user clicks, sees a brief effect, then the change reverts.

**Fix:** Split into two outputs. The widget-mounting output should depend only on schema-level inputs (column lists, dataset, tier mode). The display output that *reads* the widget value goes in a separate, smaller output (e.g. a count label, a button with a count, a summary line). Re-rendering the small display on each interaction is cheap and correct; re-rendering the widget itself is the bug.

**Lesson source:** Phase 22-I (column-drop audit). `home_col_selector_ui` mounted `input_selectize("preview_col_selector")` AND read it to compute the audit-button count. Deselecting a column → re-render → selectize rebuilt with `selected=cols` (all) → user's deselection wiped. Fix: extract `col_drop_audit_btn_ui` as a separate output.

---

# CSS & Styling Rules (ADR-055, 2026-05-02)

- **CSS lives in `config/ui/theme.css`** — not inline in Python code. This is the authoritative base stylesheet, loaded at startup by `app/src/ui.py` via `bootloader.get_theme_css_path()` and injected via `ui.tags.style()`.
- **New UI styling MUST go in `config/ui/theme.css`** (or a persona-specific override CSS file). Do not add `style=` attributes on individual components unless the value is truly one-off and cannot be expressed as a reusable CSS rule.
- **Per-persona/deployment branding**: Each persona template declares `theme_css: "config/ui/theme.css"`. A deployment overrides this key to point at a custom CSS file — no Python changes needed. `bootloader.get_theme_css_path()` resolves the active path.

---

# UI Configuration Dependencies

## Deployment Profile (ADR-048)

Defined in deployment profile YAML. Resolution chain:
1. `SPARMVET_PROFILE` env var → path to profile
2. `~/.sparmvet/profile.yaml`
3. `/etc/sparmvet/profile.yaml`
4. `config/deployment/local/local_profile.yaml` (dev fallback)

Profile declares `default_manifest`, `default_persona`, `project_root`, and the five `locations` keys.
See `config/deployment/local/local_profile.yaml` for the dev template.

**Path resolution (2026-05-02, ADR-048 §11):** `bootloader.get_location(key)` returns paths from `connector.resolve_paths()` output (`self._resolved_locations`), not from the raw profile dict. UI code must always call `bootloader.get_location(key)` — never read `locations` from the profile YAML directly.

## Persona

Defined in persona templates: `config/ui/templates/<persona_id>_template.yaml`. Persona IDs use hyphens, never underscores (e.g. `pipeline-exploration-advanced`, not `pipeline_exploration_advanced`).

Feature visibility flags: `interactivity_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `export_enabled`, `audit_report_enabled`, `import_helper_enabled`, `metadata_ingestion_enabled`, `data_ingestion_enabled`, `developer_mode_enabled`, `gallery_enabled`.

See `rules_persona_feature_flags.md` for the authoritative flag matrix and dependency cascade rules.

## User Preferences [Implementation Deferred]

Saving location: Location 4 (`user_sessions`) from deployment profile, filename `user-preferences.yaml`.
Overrides persona template settings where permitted (priority rule).
Not implemented yet.
