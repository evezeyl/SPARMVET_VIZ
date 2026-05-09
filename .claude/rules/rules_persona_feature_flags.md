---
trigger: always_on
deps:
  provides: [rule:persona_flags, rule:feature_dependencies]
  documents: [config/ui/templates/, app/src/bootloader.py]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# Persona Feature Flags — Authoritative Reference

This document is the single source of truth for all persona feature flags, their groupings, dependency chains, and the consequences of misconfiguration. It governs `config/ui/templates/*.yaml` and `app/src/bootloader.py`.

---

## Flag Groups and Dependency Chains

Flags are grouped by dependency. Enabling a flag in a group without its parent gate has **no effect** — the feature will not appear. This is enforced by `bootloader._load_persona_config()` at bootload: it resolves effective flags after applying dependency rules, and logs a warning for any flag enabled without its dependency.

### Group A — Viewing (no dependencies)

These flags are always meaningful regardless of any other flag.

| Flag | Default (static) | Effect when true |
|---|---|---|
| `export_enabled` | `true` | Export accordion panel: bundle zip + 3-way scope toggle. Gates the full panel. (`demo-vetinst`/`web-demo`: `false`) |
| `audit_report_enabled` | `false` | Retained in validator for backwards compat — **no longer used by UI** (2026-05-04 redesign). T3 audit trail is auto-included in `report.qmd` inside the bundle. |

No dependencies. Safe to enable in any persona.

---

### Group B — T3 Sandbox

`interactivity_enabled` is the **master gate**. If it is `false`, all flags in this group are silently suppressed regardless of their individual values.

```
interactivity_enabled: true/false   ← MASTER GATE for all below
  │
  ├─ t3_sandbox_enabled             ← T3 wrangling tier + right sidebar audit panel
  ├─ comparison_mode_enabled        ← Comparison Mode toggle in theater
  └─ session_management_enabled     ← Session Save/Import + ghost save
```

**Dependency rule:** `bootloader` ignores `comparison_mode_enabled` and `session_management_enabled` when `interactivity_enabled: false`. Setting them to `true` in a static persona produces no UI effect and logs a warning.

**`export_enabled` is NOT in this group.** Export is independent of interactivity — even a static (read-only) persona can produce an export bundle. It belongs in Group A.

**Structural consequence:** When `interactivity_enabled: false`, the T3 Tier Toggle buttons (T3-Wrangle, T3-Plot) are absent. The T3 recipe still silently pre-fills from T2 to protect plot rendering — but this is internal and invisible to the user.

**Filters accordion absent:** When `interactivity_enabled: false`, the Filters accordion panel is **not created** in the left sidebar — it is absent entirely. Previously it showed a static message; as of 2026-05-02 `home_theater.py` gates the accordion on `bootloader.is_enabled("interactivity_enabled")`.

**Column selector absent:** When `interactivity_enabled: false`, `home_col_selector_ui` returns an empty `ui.div()` immediately — the "Visible columns (preview only)" and "Columns (drop unselected via audit)" controls are not rendered.

**Right sidebar:** Controlled by `workspaces.home.right_sidebar.visible` in the persona template (ADR-073). Set to `false` for `pipeline-static` and `pipeline-exploration-simple`; `true` for all others. Resolved at layout build time via `bootloader.get_sidebar_config("home", "right").visible` — not by persona name comparison (that ADR-053 violation is fixed by SIDEBAR-REGISTRY-1). The `audit_stack` panel within the right sidebar is separately gated by `t3_sandbox_enabled`.

---

### Group C — Data Ingestion

`import_helper_enabled` is the **master gate** for general data ingestion. `metadata_ingestion_enabled` is **semi-independent** (see note).

```
import_helper_enabled: true/false   ← MASTER GATE for data_ingestion
  │
  └─ data_ingestion_enabled         ← Multi-file upload, Excel converter, schema association

metadata_ingestion_enabled: true/false   ← SEMI-INDEPENDENT (see below)
```

**`metadata_ingestion_enabled` semi-independence:**
- When `import_helper_enabled: false` AND `metadata_ingestion_enabled: true`: metadata upload appears as a **standalone control** in the **Data Import** panel (Phase 25-E split).
- When `import_helper_enabled: true` AND `metadata_ingestion_enabled: true`: metadata upload is nested above the multi-file ingestion control inside the Data Import panel.
- When both are `false`: no ingestion controls shown.

**Deployment override:** The deployment profile can set `data_ingestion_enabled: false` to suppress the entire data ingestion section regardless of persona flags. This is for automated-pipeline deployments where data is always pushed by the pipeline. `metadata_ingestion_enabled` is **not** overridden by the deployment profile — correcting metadata is always a legitimate user action.

---

### Group D — Developer Features

`developer_mode_enabled` is the gate for **Test Lab** (renamed from "Dev Studio" in Phase 25-A) and the full registry.

```
developer_mode_enabled: true/false   ← GATE for Test Lab
  │
  └─ Test Lab access (Wrangle Studio, AquaSynthesizer)
  └─ Full @register_action registry in right sidebar

gallery_enabled: true/false          ← INDEPENDENT (can enable without developer mode)
```

`gallery_enabled` can be set independently — a `project-independent` persona has Gallery access without full developer mode (Phase 25-A flipped this to `true` for project-independent). It remains a policy choice rather than a technical constraint, so other personas can enable Gallery without enabling `developer_mode_enabled`.

---

## Full Flag Matrix (Authoritative Values)

Six personas exist (`config/ui/templates/`). `qa` is a CI/headless-test persona with the same gates as `developer` plus `automation.ghost_save: false` for deterministic Playwright runs.

| Flag | static | simple | advanced | independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `interactivity_enabled` | false | true | true | true | true | true |
| `t3_sandbox_enabled` | false | false | true | true | true | true |
| `wrangle_studio_enabled` | false | true | true | true | true | true |
| `comparison_mode_enabled` | false | true | true | true | true | true |
| `session_management_enabled` | false | true | true | true | true | true |
| `export_enabled` | true | true | true | true | true | true |
| `audit_report_enabled` | false | false | true | true | true | true |
| `metadata_ingestion_enabled` | false | false | true | true | true | true |
| `import_helper_enabled` | false | false | false | true | true | true |
| `data_ingestion_enabled` | false | false | false | true | true | true |
| `developer_mode_enabled` | false | false | false | false | true | true |
| `gallery_enabled` | false | false | false | **true** | true | true |
| `blueprint_enabled` | false | false | false | true | true | true |
| `test_lab_enabled` | false | false | false | false | true | true |

**Phase 25 additions** (per ADR-052; not feature flags but persona-template fields):

| Field | static | simple | advanced | independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `manifest_selector.visible` | false | false | true | true | true | true |
| `testing_mode` | false | false | true | true | true | true |

---

## Cascade Enforcement (implemented in Phase 25-L)

`Bootloader._load_persona_config` applies these resolution rules immediately after reading the YAML, before caching the config. `PersonaValidator.validate()` warns about the same violations at startup (Rule 5). All call sites see already-resolved flags via `bootloader.is_enabled(flag)`.

1. If `interactivity_enabled == False`:
   - Force `comparison_mode_enabled = False`
   - Force `session_management_enabled = False`
   - Force `audit_report_enabled = False`
   - Print `[Bootloader] WARNING: <flag>=True ignored — interactivity_enabled=False` for each overridden flag.
   - `export_enabled` is **NOT** forced — export is independent of interactivity (Group A).

2. If `import_helper_enabled == False`:
   - Force `data_ingestion_enabled = False`
   - Print `[Bootloader] WARNING: data_ingestion_enabled=True ignored — import_helper_enabled=False`.

3. If deployment profile sets `data_ingestion_enabled: false` (explicit `False`, not absent):
   - Override persona `data_ingestion_enabled` to `False` unconditionally.
   - Do NOT override `metadata_ingestion_enabled`.

4. Right sidebar suppression: enforced structurally in `server.py` / `ui.py` based on persona level string comparison — not via a flag.

**Note on `audit_report_enabled`:** It is listed in Group A (no inter-flag dependency) because `pipeline-exploration-simple` has `interactivity_enabled=True` but `audit_report_enabled=False`. The cascade above is a safety net — it prevents a misconfigured template from showing the audit export panel in a static-mode persona. No existing template triggers this warning.

**All effective (resolved) flags are accessible via `bootloader.is_enabled(flag_name: str) -> bool`.**

---

## Anti-Pattern: Persona Name String Comparisons (PROHIBITED)

**Rule:** Runtime application code MUST NOT compare `bootloader.persona` against persona name strings to make UI or logic decisions. All such decisions must use `bootloader.is_enabled(flag)`.

**Why:** A persona is an abstract named preset — a convenient bundle of feature flags. What drives behavior is the flag state, not the label. An operator may create a custom template with any combination of flags. Hardcoding persona names makes those custom combinations invisible to the app and creates silent failures.

**Correct pattern:**
```python
# ✓ flag-driven — works for any persona template
if bootloader.is_enabled("t3_sandbox_enabled"):
    tier_choices["T3"] = "My adjustments"

# ✗ name-driven — breaks for any custom persona
if persona in ("pipeline-exploration-advanced", "project-independent", "developer"):
    tier_choices["T3"] = "My adjustments"
```

**Corollary:** If a behavior needs gating but no flag exists, add a flag to all six templates and use that flag. Do not add a persona name check.

**Known violations (tech debt — tracked in task 25-O):**

| File | Location | Current check | Required flag |
|---|---|---|---|
| `app/src/ui.py` | line ~410 | `persona in ("pipeline-static", "pipeline-exploration-simple")` | `t3_sandbox_enabled` (new) |
| `app/handlers/gallery_handlers.py` | line ~35 | `_T3_PERSONAS = {...}` set + two use sites | `t3_sandbox_enabled` (new) |
| `app/handlers/export_handlers.py` | line ~240 | `persona in (advanced, independent, developer, qa)` | `t3_sandbox_enabled` (new) |
| `app/handlers/home_theater.py` | line ~538 | `persona in (advanced, independent, developer)` | `t3_sandbox_enabled` (new) |
| `app/handlers/home_theater.py` | line ~1134 | `persona in hidden_personas` | `t3_sandbox_enabled` (new) |

**`t3_sandbox_enabled` proposed values:**

| Persona | Value |
|---|:---:|
| pipeline-static | false |
| pipeline-exploration-simple | false |
| pipeline-exploration-advanced | true |
| project-independent | true |
| developer | true |
| qa | true |

4. ~~Right sidebar suppression: enforced structurally in `server.py` / `ui.py` based on persona level string comparison — not via a flag.~~ **PROHIBITED — see above. Will be replaced by `t3_sandbox_enabled` in task 25-O.**

---

## Consequences of Misconfiguration

| Misconfiguration | Symptom | Fix |
|---|---|---|
| `comparison_mode_enabled: true` with `interactivity_enabled: false` | Comparison Mode toggle absent (silently suppressed). No error shown to user. | Bootloader resolves and logs warning. Fix the template. |
| `data_ingestion_enabled: true` with `import_helper_enabled: false` | Data ingestion UI absent. No Excel converter. | Bootloader resolves and logs warning. Fix the template. |
| `default_manifest` absent in profile AND persona hides selector | App fails to start with ConfigurationError: "No manifest source available." | Add `default_manifest` to profile, or use a persona that shows the selector. |
| `data_ingestion_enabled: false` in profile with `project-independent` persona | Multi-file ingestion section suppressed inside the Data Import panel. Metadata upload still available (not overridden). | Expected behaviour for auto-pipeline deployments. |
| `SPARMVET_IRIDA_TOKEN` not set with `deployment_type: irida` | IridaConnector raises AuthenticationError at startup. | Ensure IRIDA injects the token at container launch. |

---

## Files Governed by This Rule

| File | Governed aspect |
|---|---|
| `config/ui/templates/*_template.yaml` | Flag values per persona |
| `app/src/bootloader.py` | Flag resolution logic (dependency enforcement, cascade, `is_enabled()`) |
| `app/src/bootloader.py` | Persona loading, deployment profile resolution |
| `app/handlers/home_theater.py` | Must use `bootloader.is_enabled()` — persona name checks are prohibited |
| `app/handlers/gallery_handlers.py` | Must use `bootloader.is_enabled()` — `_T3_PERSONAS` set is a known violation |
| `app/handlers/export_handlers.py` | Must use `bootloader.is_enabled()` — `is_advanced` persona check is a known violation |
| `app/src/ui.py` | Must use `bootloader.is_enabled()` — right sidebar persona check is a known violation |
