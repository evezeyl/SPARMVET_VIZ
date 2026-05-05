# SPARMVET-VIZ Changelog
Append a new `## [date]` section for each release / breaking-change session.
Breaking changes are marked ⚠️. Renames that affect the manifest data contract are marked 🔑.

---

## [2026-05-04] — Export redesign + manifest modularisation

### Export pipeline (EXPORT-REDESIGN-1, EXPORT-REDESIGN-2)
- **Removed** separate "Export Audit Report" button and its handler (`export_audit_report_ui`, `export_audit_report_download`, `_audit_report_filename`). The `audit_report_enabled` persona flag is now unused by the UI (kept in validator for backwards compat).
- **Removed** "Single Graph Export" accordion panel from the sidebar. Functionality superseded by the scope toggle.
- **Added** 3-way scope toggle `[Global project | Active group | Active plot]` to the Export panel, gated on persona having both `export_enabled`.
- **Added** `recipes/t3_steps.yaml` to the export bundle when T3 has committed active nodes.
- **Added** "T3 Audit Trail" section to `report.qmd` — per-plot table of committed T3 steps + user justifications; deactivated nodes excluded.
- Accordion label renamed from "Global Project Export" → "Export".
- Spec: `.claude/design/export_specification.md`

### Manifest modularisation
- `1_test_data_ST22_dummy.yaml` rewritten from 1334 → ~290 lines using `!include` fragments under `config/manifests/pipelines/1_test_data_ST22_dummy/`.
- `figshare_integration.yaml` rewritten using `!include` (224 → 69 lines).
- Templates updated to current schema conventions: `simple_project_template.yaml` (canonical inline showcase), `e_coli.yaml`, `audit.yaml`.
- Fragment conventions + threshold (inline ≤80 lines / ≤2 schemas / ≤3 plots) documented in `.claude/knowledge/manifest_data_contract_rules.md` §6.

---

## [2026-05-04] — assembly_manifests → join_manifests rename

⚠️ 🔑 **Breaking change to manifest data contract** — all manifest YAML files must be migrated simultaneously.

### What changes
| Old | New | Where |
|-----|-----|-------|
| YAML key `assembly_manifests:` | `join_manifests:` | All manifest `.yaml` files (~10 config files) |
| Python dict key `"assembly_manifests"` | `"join_manifests"` | ~21 Python files in app/ + libs/ |
| Role string `"assembly"` | `"join"` | blueprint_handlers, manifest_navigator, wrangle_studio |
| TubeMap node label `"…\nAssembly"` | `"…\nJoin"` | `libs/utils/src/utils/blueprint_mapper.py` lines ~167, ~189 |
| UI labels `"◆ Assembly"`, `"Assembly Output (Input)"` | `"◆ Join"`, `"Join Output (Input)"` | `app/modules/wrangle_studio.py` |

### Motivation
"Assembly" has a specific meaning in bioinformatics (genome/contig assembly). The concept here is purely a dataset join operation. Rename avoids confusion, especially in the Cytoscape TubeMap which the team reads.

### Exception — do NOT rename
- `session_manager.py` ~line 213: `{"assembly": ..., "contracted": ...}` — this is a Parquet file path label, unrelated to the manifest role.

### Variable name rule
Never use bare `join` as a Python variable (shadows `str.join()`, confusing next to Polars). Use `join_defs`, `join_block`, `join_step`, `is_join_step` etc.

### Execution plan
See task `ASSEMBLY-RENAME` in `.claude/tasks/tasks.md` for the 5-pass VSCode checklist.
