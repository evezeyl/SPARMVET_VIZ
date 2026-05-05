# Audit Remediation Tasks — Verified Plan
**Date:** 2026-05-03
**Source audit:** `.antigravity/logs/audit_final_exhaustive_2026-05-03.md`
**Reviewer:** @dasharch (claude-opus-4-7)
**Status:** Each audit point reviewed against current repo state. Verdict + actionable task per point.

## Verdict legend

| Mark | Meaning |
|---|---|
| ✅ CONFIRMED | Audit claim is accurate and actionable. |
| 🟨 PARTIAL | Claim has merit but framing is wrong or scope needs narrowing. |
| ❌ INCORRECT | Audit claim is factually wrong; no fix needed. |
| 🟦 KNOWN-DEFERRED | Already tracked in `tasks.md`; audit just resurfaced it. |
| 🟥 DISCUSS | Genuinely ambiguous — needs user decision before fix. |

## Model & effort flag legend

| Tag | Meaning |
|---|---|
| `[sonnet-low]` | Mechanical, single-file edit. Sonnet, low thinking. |
| `[sonnet-med]` | Multi-file find/replace or simple refactor. Sonnet, medium thinking. |
| `[sonnet-high]` | Cross-cutting refactor, traceable but careful. Sonnet, high thinking. |
| `[opus-med]` | Architectural call required (interpret rule, propose ADR amendment). Opus, medium thinking. |
| `[discuss-first]` | Do not assign — user must decide scope/intent before any agent acts. |

---

# Section 1 — Unreported incomplete tasks

## ✅ 1A. Ingestion sanitization TODOs absent from `tasks.md`
- **Verified:** [libs/ingestion/src/ingestion/placeholder/um_sanitization.py:62-66](libs/ingestion/src/ingestion/placeholder/um_sanitization.py#L62-L66) contains 4 unimplemented TODOs (data type transformation, mandatory column reporting, whitespace/Windows char cleaning, Orchestrator failure reporting). `grep "sanitization" .antigravity/tasks/tasks.md` returns 0 matches.
- **Task — `[sonnet-low]`:** Add a "Technical Debt" entry to [.antigravity/tasks/tasks.md](.antigravity/tasks/tasks.md) under the existing `### Technical Debt` block:
  ```
  - [ ] **INGEST-SANITIZE-1**: Implement TODOs in libs/ingestion/src/ingestion/placeholder/um_sanitization.py:62-66
        — (a) data type transformations, (b) missing mandatory column reporting,
        (c) whitespace/Windows char cleaning, (d) raise SPARMVET_Error subclass
        on failure (consumed by Orchestrator in app/modules/orchestrator.py:83).
  ```
  Do **not** implement the logic itself in this task — only register it.

## ✅ 1B. Lineage 2 (Plasmid) does not join AMR data
- **Verified:** [config/manifests/pipelines/2_test_data_ST22_dummy/assembly/Plasmid_Profile_Joint.yaml](config/manifests/pipelines/2_test_data_ST22_dummy/assembly/Plasmid_Profile_Joint.yaml) joins only `metadata_schema`. Header comment says `consumes: ... dataset:plasmid_data, dataset:metadata_schema` — no `amr_data`. tasks.md line 76 says "Assemble with metadata and AMR results".
- **User decision (2026-05-03):** Agent drafts the AMR join → user reviews.
- **Task — `[sonnet-high]`:** Draft an updated `Plasmid_Profile_Joint.yaml` that:
  1. Adds `amr_data` (from `2_test_data_ST22_dummy/input_fields/amr_data.yaml`) as an ingredient.
  2. Joins `amr_data` after the existing `metadata_schema` join, on `sample_id`. Use `how: left` (plasmids are the anchor; not every sample necessarily has AMR hits — left preserves all plasmid rows).
  3. Decide: include `predicted_phenotype` (and possibly `predicted_phenotype_clean` if already materialized in Lineage 1) in the projected columns.
  4. Update the `@deps` header to add `dataset:amr_data` to `consumes`.
  5. Materialize via `debug_assembler.py` and write the Tier 1 audit artifact to `tmpAI/2026-05-03/plasmid_lineage2/`.
  6. Stop and write a "for review" note in [.antigravity/logs/handoff_active.md](.antigravity/logs/handoff_active.md) — do **not** copy to `tmp/` or close the task. User approves before promotion.

## 🟦 1C. VizFactory gaps (Spatial / Network)
- **Verified:** Already explicit deferred items in tasks.md: `GALLERY-MAP` ("blocked — geom_map/spatial layer requires GeoDataFrame support"), `GALLERY-FLOW` ("blocked — plotnine has no native support"). Audit is restating known status, not finding hidden debt.
- **Task — `[sonnet-low]`:** None. Optionally cross-link these tasks to ADR registry by adding a one-line note to `architecture_decisions.md` saying "Spatial/Network types deferred — see GALLERY-MAP / GALLERY-FLOW in tasks.md". Skip if user not interested.

---

# Section 2 — Inconsistencies, errors, engine bugs

## ✅ 2A. Boolean Manifest Trap (unquoted `on:`)
- **Verified all 5 files** (greps below show exact line):
  - [config/manifests/templates/complex_demo/master_recipe.yaml:4](config/manifests/templates/complex_demo/master_recipe.yaml#L4) → `on: "sample_id"` (unquoted key)
  - [config/manifests/templates/simple_project_template.yaml:43](config/manifests/templates/simple_project_template.yaml#L43)
  - [config/manifests/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:33](config/manifests/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml#L33)
  - [config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml:3](config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml#L3)
  - [config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml:12](config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml#L12)
- **Reference rule:** `libs/transformer/README.md:69` ("The Boolean Shield: always use quotes `\"on\":`").
- **Task — `[sonnet-low]`:** In each file, replace `^(\s*)on:` with `\1'on':` (preserving leading whitespace) — only on lines where `on:` is a YAML key, NOT inside string values. The 5 files above are the verified targets; do not run a global regex. Run `python -c "import yaml; yaml.safe_load(open('FILE'))"` after each edit and confirm the parsed dict has key `'on'` not `True`.
- **Sanity check (one-liner):** After the fix, run `grep -rnE "^\s+on:" config/manifests/` — expect empty output.

## ❌ 2B. "Missing `SPARMVET_Error`" — claim is WRONG, real gap is different
- **Verified:** `SPARMVET_Error` **DOES exist** at [libs/utils/src/utils/errors.py:7](libs/utils/src/utils/errors.py#L7). `IngestionError`, `TransformationError`, `VisualizationError`, `ManifestError` are all **subclasses** of it (lines 17, 24, 31, 38). Audit's claim "class does not exist" is factually incorrect.
- **Real gap:** ADR-034 (in [rules_verification_testing.md:75-79](.agents/rules/rules_verification_testing.md#L75-L79)) requires every significant component to ship a "Malformed Manifest" failure test that intentionally triggers a `SPARMVET_Error` subclass. `grep -rn "SPARMVET_Error\|malformed_manifest" libs/*/tests/` returns 0 matches.
- **Task — `[sonnet-high]`:** Audit each `libs/*/tests/` for an automated failure test that:
  1. Loads a deliberately broken manifest fixture, AND
  2. Asserts a `SPARMVET_Error` subclass is raised with a populated `.tip` attribute.
  Produce a checklist by component (ingestion, transformer, viz_factory). Do **not** write the tests yet — first land the audit + write a follow-up task per missing component. Update the audit doc to correct the false "class does not exist" claim.

## 🟨 2C. Cross-library imports (ADR-011 / "Clear Lines" policy) — superseded by Section 9 utils architecture review
- **Verified:**
  - [libs/transformer/src/transformer/pipeline.py:11-12](libs/transformer/src/transformer/pipeline.py#L11-L12) → `from utils.config_loader import ConfigManager` and `from ingestion.ingestor import DataIngestor`. **The `ingestion.ingestor` import is unambiguously a violation**.
  - `data_wrangler.py:11`, `metadata_validator.py:4`, `data_assembler.py:11` → import from `utils.errors` / `utils.hashing`.
- **Task A (always-correct) — `[sonnet-high]`:** Refactor [libs/transformer/src/transformer/pipeline.py](libs/transformer/src/transformer/pipeline.py) to remove the `ingestion.ingestor` import. Move orchestration that needs both libs up to `app/` (likely `app/modules/orchestrator.py`). Re-run `python -m transformer.pipeline ...` smoke test.
- **Task B — see Section 9** (utils architecture review). Outcome of that review decides whether the `utils.errors`/`utils.hashing` imports are legal or need migration.

## 🟦 2D. T3 LazyFrame threading
- **Verified:** Tracked in tasks.md ("T3 lf threading: When new T3 node types … are added, thread them through `_apply_t3_to_lf`. Design in `.antigravity/tasks/design_sge_lineage_t3.md`"). Design doc exists.
- **Task — `[sonnet-low]`:** None now. Re-evaluate when a new T3 node type is actually added.

---

# Section 3 — Path hacking & CLI protocol

## ✅ 3A. `sys.path` violations (ADR-016)
- **Verified all 6 files**:
  - [libs/viz_gallery/tests/debug_gallery_ui_logic.py:12](libs/viz_gallery/tests/debug_gallery_ui_logic.py#L12) — `sys.path.append`
  - [libs/utils/tests/debug_blueprint_mapper.py:8](libs/utils/tests/debug_blueprint_mapper.py#L8)
  - [app/tests/debug_pipeline_connector.py:25](app/tests/debug_pipeline_connector.py#L25) — `sys.path.insert`
  - [app/tests/debug_home_theater.py:36](app/tests/debug_home_theater.py#L36)
  - [app/tests/debug_session_flow.py:28](app/tests/debug_session_flow.py#L28)
  - [libs/viz_gallery/assets/generate_previews.py:26-27](libs/viz_gallery/assets/generate_previews.py#L26-L27) — two inserts
- **Task — `[sonnet-med]`:** For each file, delete the `sys.path.*` lines plus any `import sys` / Path-juggling that becomes dead. The libraries are installed editable (`pip install -e`) so direct `from <pkg> import …` should already work. Run each script after editing to confirm imports still resolve. If a script fails, the right answer is to install the missing package editable, not to re-add `sys.path` hacks.

## 🟨 3B. Argparse / hardcoded paths
- **Verified:** Only [assets/scripts/generate_demo_data.py:30-31](assets/scripts/generate_demo_data.py#L30-L31) shows the hardcoded `Path("assets/test_data/...")` pattern with no `argparse`. The other 4 files in the audit list (`materialize_manifest_plots.py`, `figshare_plot_integration.py`, `libs/transformer/tests/debug_decorator_suite.py`, `libs/utils/tests/debug_blueprint_mapper.py`) **did not** show `argparse` imports OR obvious hardcoded paths in the targeted grep — the audit's claim is over-broad.
- **Task A — `[sonnet-med]`:** Rewrite [assets/scripts/generate_demo_data.py](assets/scripts/generate_demo_data.py) to use `argparse` with `--ground-truth-dir` and `--out-dir`, defaulting to current values. Print resolved paths at start. Confirm `python assets/scripts/generate_demo_data.py --help` works.
- **Task B — `[sonnet-low]`:** For the other 4 files, run `head -50` on each and decide individually:
  - If it reads CLI args via `sys.argv` directly or has hardcoded paths → add argparse.
  - If it's a function-only library used by another runner → leave alone, remove from audit list.
  Update the audit doc (correct entry) when done.

## ✅ 3C. `debug_viz_factory_audit.py` misplaced
- **Verified:** Lives at [assets/scripts/debug_viz_factory_audit.py](assets/scripts/debug_viz_factory_audit.py); [libs/viz_factory/tests/](libs/viz_factory/tests/) exists and contains other `debug_*.py` runners. Per ADR-032, library-internal debug runners belong in their `libs/<x>/tests/`.
- **Task — `[sonnet-low]`:** `git mv assets/scripts/debug_viz_factory_audit.py libs/viz_factory/tests/debug_viz_factory_audit.py`. Then grep for any references (`grep -rn "debug_viz_factory_audit"`) and update import paths / docs / runbooks. Re-run the script from its new location.

## ✅ 3D. Debug runners do not auto-route output to dated `tmp/`
- **Verified:** [libs/transformer/tests/debug_wrangler.py](libs/transformer/tests/debug_wrangler.py) and [debug_assembler.py](libs/transformer/tests/debug_assembler.py) — no `datetime.now()` / `date.today()` / `tmp/2` / `tmpAI` patterns found. tasks.md already lists this as `Unified Materialization` under Technical Debt.
- **Task — `[sonnet-med]`:** Add a helper in `libs/transformer/tests/_paths.py` (new file) that returns `Path("tmpAI") / date.today().isoformat() / lineage_id` and ensures the dir exists. Wire `debug_wrangler.py` and `debug_assembler.py` to use it for all output writes. Per `workspace_standard.md §4`, write to `tmpAI/` (agent scratch); only promote to `tmp/` on `@verify`.

---

# Section 4 — UI architecture violations & UX deficits

## ✅ 4A. Two-Category Law violations (`shiny` imports in `app/modules/`)
- **Verified all 4 files** import `shiny`:
  - [app/modules/wrangle_studio.py:11](app/modules/wrangle_studio.py#L11) — `from shiny import ui, reactive, render`
  - [app/modules/help_registry.py:9](app/modules/help_registry.py#L9) — `from shiny import module, ui, render`
  - [app/modules/gallery_viewer.py:7](app/modules/gallery_viewer.py#L7)
  - [app/modules/dev_studio.py:9](app/modules/dev_studio.py#L9)
- **Task — `[sonnet-high]`:** This is a real refactor — `shiny.module` decorators are pervasive. For each file, choose:
  1. **Move to `app/handlers/`** if the file defines `@module.ui` / `@module.server` blocks (most likely route).
  2. **Split** if the file mixes pure-Python introspection with shiny: keep introspection in `app/modules/`, move shiny in `app/handlers/`.
  Update all imports across the app after the move. Run `app/tests/test_shiny_smoke.py` and the persona masking test (`app/tests/test_ui_persona_masking.py`) after each move. **Do not bundle all 4 in one PR** — one file per commit so the diff stays reviewable.

## 🟦 4B. Theater & Export functionality
- **Verified:** `THEATER-1`, `EXPORT-TUBEMAP`, `EXPORT-2` all already exist in tasks.md (lines 119, 145, 148, 160). Audit is just resurfacing existing deferred work.
- **Task — `[sonnet-low]`:** None. Optionally tag these in the audit doc as "duplicates of existing tasks.md entries" so the next reviewer doesn't re-flag them.

## 🟦 4C. Notification resilience (`UX-NOTIF-2`, `UX-NOTIF-3`)
- **Verified:** Both items already exist in tasks.md (lines 159, 180) with implementation hints. Audit is resurfacing.
- **Task — `[sonnet-low]`:** None. Same note as 4B.

---

# Section 5 — `@deps` blocks

## ✅ 5. Missing `@deps` annotations
- **Verified:**
  - `app/src/main.py`, `app/src/bootloader.py`, `app/src/server.py`, `app/src/ui.py` → 0 `@deps` blocks each.
  - `app/handlers/notification_utils.py` → 0.
  - `libs/connector/src/connector/`: 4 of 11 files missing (`adapter_A/B/C/D.py`, `adapter_metadata.py`, `galaxy_connector.py`, `__init__.py`).
  - `libs/generator_utils/src/generator_utils/`: ALL 5 files missing.
  - `libs/viz_gallery/src/viz_gallery/`: at least `gallery_manager.py` missing (sample of one).
- **Task — `[sonnet-high]`:** Workflow:
  1. Read [.agents/rules/workspace_standard.md §5](.agents/rules/workspace_standard.md) and the existing `@deps` blocks in `libs/connector/src/connector/base.py`, `filesystem.py`, `irida.py`, `galaxy.py` to learn the format.
  2. For each missing file, infer `provides` (top-level class/function names), `consumes` (imports from project modules), `consumed_by` (run `grep -l "from <pkg>.<file>"` across repo), `doc` (rule reference if applicable).
  3. Insert the `@deps` block as a top-of-file comment.
  4. Run `python assets/scripts/build_dep_graph.py` and confirm no errors.
  5. Iterate file-by-file in commits of ~10 files, not one giant commit.
- **Subtask split (parallelizable):**
  - `[sonnet-med]` — `app/src/*.py` and `app/handlers/notification_utils.py` (5 files)
  - `[sonnet-med]` — `libs/connector/` missing files (~6 files)
  - `[sonnet-med]` — `libs/generator_utils/` (5 files)
  - `[sonnet-med]` — `libs/viz_gallery/` (full audit + injection)

---

# Section 6 — Documentation & Violet Law

## ✅ 6A. Violet Law violations in READMEs
- **Verified:** All 5 README files use plain backtick form (e.g. `` `VizFactory` ``, `` `BaseConnector` ``, `` `DataAssembler` ``). Per ADR-029 / `rules_documentation_aesthetics.md`, human-facing docs must use `` `VizFactory (viz_factory.py)` `` form.
- **Task — `[sonnet-med]`:** For each README, identify class/component references and rewrite to Violet form. **Do NOT use a blind regex** — backticks are also legitimately used for code keywords (`true`, `path`, env vars). Approach:
  1. Read each README line-by-line.
  2. Identify only references to **named project components** (classes, modules, library nicknames).
  3. Rewrite those to `` `Name (relative/path/file.py)` ``.
  4. Skip primitives, env vars, YAML keys, generic terms.
  Files: [libs/viz_factory/README.md](libs/viz_factory/README.md), [libs/connector/README.md](libs/connector/README.md), [libs/transformer/README.md](libs/transformer/README.md), [libs/generator_utils/README.md](libs/generator_utils/README.md), [libs/utils/README.md](libs/utils/README.md).

## ✅ 6B. `phenotype` vs `predicted_phenotype` — clarified as a manifest column-naming standard
- **Origin:** ADR "Precision Renaming Standard" in [.antigravity/knowledge/architecture_decisions.md:869](.antigravity/knowledge/architecture_decisions.md#L869): "Favor `predicted_phenotype` (ResFinder) or `observed_phenotype` (Lab) over generic `phenotype`. Use underscores to avoid collision in joined datasets."
- **Not** a rename script artifact — it is a **manifest column-naming convention** applied to YAML target field keys. The `original_name:` value preserves the actual column header in the source file (which often will remain `phenotype` because that's what the upstream tool emits).
- **Verified occurrences of unqualified `phenotype` as a target key:**
  - [config/manifests/pipelines/1_test_data_ST22_dummy/output_fields/ResFinder_output_fields.yaml:5](config/manifests/pipelines/1_test_data_ST22_dummy/output_fields/ResFinder_output_fields.yaml#L5) — `phenotype:` as the target key. ResFinder always emits *predicted* phenotypes, so rename target → `predicted_phenotype` (`original_name:` stays whatever the source column is — likely `Phenotype` or `phenotype`).
  - [config/manifests/pipelines/figshare_integration.yaml:84,104](config/manifests/pipelines/figshare_integration.yaml#L84) — `phenotype:` as target key in `fg_phenotypes` `input_fields` and `output_fields`. Figshare (Galaxy AMR) data is also predicted (ResFinder/AMRFinder output), so rename the **target key** to `predicted_phenotype`. Keep `original_name: phenotype` (that's still the actual column in the TSV).
- **Task — `[sonnet-med]`:** Mechanical rename of YAML keys only:
  1. In `ResFinder_output_fields.yaml`, change the top-level key `phenotype:` to `predicted_phenotype:`. If a `target_name:` field is missing, leave the key change to do the work; otherwise add `target_name: predicted_phenotype` and keep `original_name: phenotype`.
  2. In `figshare_integration.yaml` `fg_phenotypes` block (lines 84-87 and 104-107), rename the target keys `phenotype:` → `predicted_phenotype:` while keeping `original_name: phenotype`.
  3. Search the rest of `config/manifests/` for any plot/recipe references that consume `phenotype` (vs `predicted_phenotype`) and update them. Run `grep -rnE "(\$|\")phenotype(\"|\$| )" config/manifests/` to find consumers.
  4. Run `debug_assembler.py` and `debug_wrangler.py` against ST22 + figshare to confirm pipelines still materialize.
- **Out of scope:** `cge_phenotype` is already namespaced — leave alone unless user explicitly wants `cge_predicted_phenotype` (already used in `Detailed_summary_input_fields.yaml:18`, so the mixed state should be unified — flag if encountered, do not block on it).

## ✅ 6C. Taxonomy doc drift
- **Verified:**
  - [assets/gallery_data/TAXONOMY_CHEATSHEET.md](assets/gallery_data/TAXONOMY_CHEATSHEET.md) exists (the source of truth).
  - [docs/appendix/viz_factory_components.qmd](docs/appendix/viz_factory_components.qmd) (287 lines) — no mention of `geom`, `show`, `sample_size`, "6-axis", "taxonomy".
  - [docs/user_guide/viz_gallery.qmd](docs/user_guide/viz_gallery.qmd) — same, only references "Wrangle Studio" (Phase 24/25 drift).
- **Task — `[sonnet-high]`:** Add a "Visualization taxonomy (6-axis)" section to both `.qmd` files explaining the icon → axis map (⚙️ geom · 🎯 show · 📏 sample_size + the 3 prior axes). Pull canonical descriptions and allowed values from `TAXONOMY_CHEATSHEET.md`. Render with `quarto render docs/` and confirm no broken links.
- **Sub-task — `[sonnet-low]`:** Audit `assets/gallery_data/*/recipe_manifest.yaml` (34 files) — verify each has the 3 new fields populated. Output: a CSV `tmpAI/2026-05-03/taxonomy_audit.csv` with `recipe_name, geom, show, sample_size, missing_fields`.

---

# Section 7 — User documentation drift (Phase 24/25)

## ✅ 7A. Outdated UI nomenclature
- **Verified:**
  - **"System Tools"** appears in [docs/user_guide/system_transparency.qmd:101](docs/user_guide/system_transparency.qmd#L101), [docs/workflows/ui_persona.qmd:75,135,190](docs/workflows/ui_persona.qmd#L75), and [docs/appendix/FAQ.qmd:83](docs/appendix/FAQ.qmd#L83) (the audit's "FAQ.qmd" path was wrong — it lives at `docs/appendix/FAQ.qmd`).
  - **"Dev Studio"** appears in [docs/appendix/dev_studio_rationale.qmd:1,5,19](docs/appendix/dev_studio_rationale.qmd) and [docs/index.qmd:54](docs/index.qmd#L54).
  - **"Analysis Theater"** appears in [docs/appendix/Terminology.qmd:23](docs/appendix/Terminology.qmd#L23) defined as active mode (eliminated by ADR-043).
  - **"Wrangle Studio"** also appears (separately from "Dev Studio") in `system_transparency.qmd:9,37,45` and `glossary_and_feedback.qmd:16-17` — see 7B below.
- **Task — `[sonnet-med]`:** Per-file controlled replacements (NOT a global sed):
  - "System Tools" → "Global Project Export" where it refers to the export panel; check each occurrence in context. In `ui_persona.qmd:75,190`, may need more nuanced wording — read full sentence.
  - "Dev Studio" → "Test Lab". File `dev_studio_rationale.qmd` should be renamed to `test_lab_rationale.qmd`; update `docs/_quarto.yml` and any cross-link.
  - "Analysis Theater" in `Terminology.qmd:23` — remove or replace with "Home" (sole results mode per ADR-043). Verify ADR-043 in `architecture_decisions.md` first to use the exact wording.

## ✅ 7B. T3 sandbox contradiction
- **Verified:** [docs/user_guide/glossary_and_feedback.qmd:16-17](docs/user_guide/glossary_and_feedback.qmd#L16-L17) defines T3 as "the sandbox stage (The Wrangle Studio)" — directly contradicts `rules_ui_dashboard.md` ("T3 scope is permanently locked to row filters … NOT a wrangling sandbox").
- **Task — `[sonnet-med]`:** Rewrite the T3 glossary entry. Keep it short:
  > "Tier 3: An in-session audit/aesthetic layer applied on top of T2 results. Scoped strictly to row filters and aesthetic overrides (color, shape, fill). Does not modify the manifest. Persona-gated; not all users see it."
  Also update line 17's reference to "Wrangle Studio". Check the rest of the file for residual "Wrangle Studio" / "Dev Studio" mentions and fix them in the same pass.

---

# Section 8 — Audit doc itself

## ✅ Update the audit document
- **Task — `[sonnet-low]`:** After the above tasks ship, append a "## Corrections (2026-05-03 review)" section to [.antigravity/logs/audit_final_exhaustive_2026-05-03.md](.antigravity/logs/audit_final_exhaustive_2026-05-03.md):
  - 2B: SPARMVET_Error class **does** exist; the real gap is missing automated failure tests per ADR-034 §7.
  - 3B: Argparse claim was over-broad — only `generate_demo_data.py` confirmed; other 4 files need individual review.
  - 4B / 4C / 1C: Items already tracked in tasks.md, not "unreported".
  - 7A: `docs/FAQ.qmd` does not exist.

---

# Section 9 — `libs/utils/` architecture review (agent draft for discussion)

**User asked:** "Why is `gallery_manager.py` in utils, would its place not be better in viz_gallery? And the blueprint mapper — should it be somewhere else? `utils` was for things we did not really know where to place."

## What's currently in `libs/utils/src/utils/`

| File | Lines | Real role | Currently consumed by |
|---|---|---|---|
| `errors.py` | ~40 | `SPARMVET_Error` hierarchy (cross-cutting error type taxonomy) | `transformer/*.py`, `ingestion/*.py`, `app/handlers/*` |
| `config_loader.py` | (read) | Loads SPARMVET YAML manifests with `!include` resolution | `transformer/pipeline.py`, `app/` orchestrator |
| `hashing.py` | (read) | `generate_config_hash`, `get_parquet_metadata_hash` — pipeline cache invalidation | `transformer/data_assembler.py`, `app/` cache logic |
| `blueprint_mapper.py` | (read) | `BlueprintMapper` — generates Cytoscape elements for the **Blueprint Architect UI** | **Only `app/handlers/blueprint_handlers.py`** + colour-mirror constants in `app/src/ui.py` and `assets/scripts/build_dep_graph.py` |
| `gallery_manager.py` | 83 | **DUPLICATE** of `libs/viz_gallery/src/viz_gallery/gallery_manager.py` (which is 173 lines, has more features incl. geom/show/sample_size, json, hashlib) | utils version → `app/handlers/gallery_handlers.py`; viz_gallery version → `viz_gallery/assets/refresh_gallery.py` and its own debug suite |
| `placeholder/discovery.py` | stub | Empty argparse hook | nothing |
| `placeholder/schema.py` | stub | Empty argparse hook | nothing |

## Major finding (was not in the audit)

🚨 **`gallery_manager.py` is duplicated** with two divergent implementations. The **app handler imports the older 83-line utils version** while a richer 173-line `viz_gallery.gallery_manager` exists with newer features (taxonomy fields, JSON+hashlib persistence) but is only consumed by a refresh script and tests. Net effect: the app is running stale logic.

## Traditional usage of a `utils` / `commons` package — pros and cons

### Pattern A: "Junk drawer utils" (current state)
- **Pro:** Quick to add helpers when you don't know where they belong yet. Single `pip install -e libs/utils` covers everyone.
- **Con (severe in monorepos):** Becomes the universal dependency. Every package depends on utils → utils changes trigger ripple effects across libs that should be independent. Hidden coupling: `transformer` "doesn't depend on viz_factory" on paper, but if both pull from utils, a utils change can break both at once.
- **Con (current evidence):** Domain logic accumulates (`blueprint_mapper` is a UI feature that ended up in utils because there was no UI lib); duplicates appear when domain owners later realise they want their own version (`gallery_manager`).

### Pattern B: Strict "shared/commons" foundation library (industry standard for monorepos)
- **Rule:** `utils` may **only** contain dependency-free, domain-agnostic helpers. Allowed: error type taxonomy, hashing, datetime helpers, IO primitives. Forbidden: anything that knows what a "manifest", a "tier", a "blueprint", or a "gallery" is.
- **Pro:** Libraries can evolve independently as long as they don't touch `utils`. `utils` itself rarely changes (so the coupling is cheap).
- **Pro:** Clear test for "should this go in utils?" — if the helper would make sense in a totally unrelated project, yes; if it knows about SPARMVET concepts, no.
- **Con:** Requires discipline to maintain.

### Pattern C: No utils — co-locate
- **Pro:** Strictest "Clear Lines" interpretation — true zero shared code between libs.
- **Con:** Practical headache. `SPARMVET_Error` has to be duplicated three times, and now if you raise an `IngestionError`, the `except SPARMVET_Error` in `app/` doesn't catch it because they're different classes.
- **Verdict:** Not viable for SPARMVET.

## Recommended target state for SPARMVET

Adopt **Pattern B** with explicit relocations:

| Current | Recommendation | Reason |
|---|---|---|
| `utils/errors.py` | **Stay** in utils. Whitelist explicitly in ADR-011. | Genuinely cross-cutting, domain-agnostic. Keep here, document. |
| `utils/hashing.py` | **Stay** in utils. Whitelist. | Pure functions over bytes/strings/files. No SPARMVET concepts. |
| `utils/config_loader.py` | **Move to `libs/transformer/`** — or to a new `libs/manifest_engine/` if a separate package is wanted later. | `ConfigManager` knows about SPARMVET manifest structure (`!include`, ingredient lists) — that's domain. Currently used mainly by transformer + app; moving to transformer is the smallest change. App imports `transformer.config_loader` instead of `utils.config_loader`. |
| `utils/blueprint_mapper.py` | **Move to `app/modules/blueprint_mapper.py`** (it's pure-Python introspection; no shiny imports → fits Two-Category Law) — OR to a new `libs/blueprint/` library if it's expected to grow. | Used **only** by `app/handlers/blueprint_handlers.py`. It's UI feature logic, not utils. The colour-mirror comment in `ui.py` and `build_dep_graph.py` is an existing maintenance smell — flag separately. |
| `utils/gallery_manager.py` | **Delete the utils version**, migrate `app/handlers/gallery_handlers.py` to import from `viz_gallery.gallery_manager`, and add any missing methods to the viz_gallery version if the app needs features that only exist in the utils stub. | Resolves the duplicate. viz_gallery owns the gallery domain. |
| `utils/placeholder/discovery.py`, `schema.py` | **Delete** if the stubs were never wired up; otherwise port to wherever the placeholder logic actually lives. | Currently dead code (empty argparse hooks). |

After this, the only code in `utils/` is `errors.py` + `hashing.py`. Then amend [.agents/rules/rules_runtime_environment.md §4](.agents/rules/rules_runtime_environment.md#L45) "Clear Lines Library Policy" to say:

> **Single foundational exception:** `libs/utils/` is the sole library that may be imported by other libraries. It is restricted to dependency-free, domain-agnostic primitives (error taxonomy, hashing, IO helpers). Any code in `utils/` that names a SPARMVET concept (manifest, tier, blueprint, gallery, persona, …) is by definition misplaced and MUST be relocated.

## Trade-off summary (the "evolve independently" goal)

- With this change, `transformer`, `ingestion`, `viz_factory`, `viz_gallery`, `connector`, `generator_utils` each truly evolve independently for **domain logic**. The only thing they share is the error type system + hashing — both are stable, low-velocity contracts.
- `app/` is the only place that knows about all libs, and that's correct (it's the orchestrator/UI).
- Cost of the migration:
  - `config_loader` move: medium (touches every importer of `utils.config_loader`).
  - `blueprint_mapper` move: small (one importer in `app/handlers/blueprint_handlers.py`).
  - `gallery_manager` dedup: medium (need to diff and merge features into viz_gallery version, then migrate app handler).
  - placeholder cleanup: trivial.
- **Risk:** Low — all moves are mechanical and backed by a working test suite. Suggest one commit per move.

## What this means for the audit's "Clear Lines violation" claim

- Once Pattern B is adopted: `utils.errors` and `utils.hashing` imports become explicitly legal. The audit's flag on `data_wrangler.py`, `metadata_validator.py`, `data_assembler.py` resolves to "rule needs amending, code is fine".
- The `pipeline.py → ingestion.ingestor` import is still a violation regardless of Pattern A/B/C. Fix unconditionally.
- The `transformer.config_loader` location migration removes another false-friend dependency.

## Tasks (after user approves Pattern B)

1. `[sonnet-med]` — Move `utils/blueprint_mapper.py` → `app/modules/blueprint_mapper.py`. Update [app/handlers/blueprint_handlers.py:39](app/handlers/blueprint_handlers.py#L39) import. Update `@deps` blocks. Re-run `app/tests/test_shiny_smoke.py`.
2. `[sonnet-high]` — Resolve `gallery_manager` duplicate: diff the two implementations, merge missing features into `libs/viz_gallery/src/viz_gallery/gallery_manager.py`, repoint `app/handlers/gallery_handlers.py` to import from `viz_gallery.gallery_manager`, delete `libs/utils/src/utils/gallery_manager.py`.
3. `[sonnet-med]` — Move `utils/config_loader.py` → `libs/transformer/src/transformer/config_loader.py`. Update all importers (`transformer/pipeline.py`, app modules, tests). Re-run `debug_assembler.py`.
4. `[sonnet-low]` — Delete `utils/placeholder/discovery.py` and `utils/placeholder/schema.py` if confirmed unused (`grep -r placeholder.discovery; grep -r placeholder.schema` returns 0 matches in `src/`).
5. `[sonnet-low]` — Amend [.agents/rules/rules_runtime_environment.md §4](.agents/rules/rules_runtime_environment.md) to add the "single foundational exception" wording. Add a new ADR entry recording the decision.
6. `[sonnet-low]` — Delete `libs/utils/tests/debug_gallery_submission.py` once gallery_manager dedup is done (or move test logic to `libs/viz_gallery/tests/`).

---

# Section 10 — Recommended execution order (chosen by agent)

Splitting into **Wave 1 (no further user decisions needed — agent can run now)** and **Wave 2 (need user discussion before running)**.

## Wave 1 — Safe, mechanical, can start immediately

| # | Task | Section | Tag | Rationale |
|---|---|---|---|---|
| 1 | Append "Corrections" section to the original audit doc | §8 | `[sonnet-low]` | Keeps the audit honest. No code touched. |
| 2 | Quote unquoted `on:` in 5 manifests | §2A | `[sonnet-low]` | Verified targets, mechanical, low-risk. Rerun manifest load after. |
| 3 | Strip `sys.path.*` from 6 files | §3A | `[sonnet-med]` | All libs already editable-installed. Run each script after edit. |
| 4 | `git mv assets/scripts/debug_viz_factory_audit.py → libs/viz_factory/tests/` | §3C | `[sonnet-low]` | One-line move + ref update. |
| 5 | Doc terminology drift in `.qmd` (System Tools / Dev Studio / Analysis Theater / Wrangle Studio / T3 sandbox) | §7A + §7B | `[sonnet-med]` | Per-file controlled edits. No code-paths affected. |
| 6 | Add `FAQ.qmd:83` to the System Tools rename in §7A pass | §7A | `[sonnet-low]` | Folded into task above. |
| 7 | Violet Law in 5 READMEs | §6A | `[sonnet-med]` | Per-file rewrite. |
| 8 | Add 6-axis taxonomy section to `viz_factory_components.qmd` and `viz_gallery.qmd` | §6C | `[sonnet-high]` | Reads `TAXONOMY_CHEATSHEET.md` as source. |
| 9 | Audit `assets/gallery_data/*/recipe_manifest.yaml` for missing geom/show/sample_size → CSV | §6C sub | `[sonnet-low]` | Read-only audit. |
| 10 | `phenotype` → `predicted_phenotype` rename in 2 manifests + downstream consumers | §6B | `[sonnet-med]` | Now clarified — manifest convention. Mechanical. |
| 11 | Refactor `transformer/pipeline.py` to drop `ingestion.ingestor` import (the unambiguous violation) | §2C Task A | `[sonnet-high]` | Independent of utils decision. |
| 12 | Inject missing `@deps` blocks (4 batches) | §5 | `[sonnet-med]` × 4 | Independent batches; can parallelize. |
| 13 | Argparse fix for `generate_demo_data.py` | §3B Task A | `[sonnet-med]` | Single confirmed violator. |
| 14 | Audit other 4 §3B files individually | §3B Task B | `[sonnet-low]` | Read-only triage; updates audit doc. |
| 15 | Debug runner output routing helper + wire-up | §3D | `[sonnet-med]` | Self-contained. |
| 16 | Failure-test gap audit (per-component report) | §2B | `[sonnet-high]` | Read-only research; produces follow-up tasks. |
| 17 | Register `INGEST-SANITIZE-1` in `tasks.md` | §1A | `[sonnet-low]` | One line in tasks.md. |

## Wave 2 — Need user decision before running

| # | Task | Section | Why it waits |
|---|---|---|---|
| W2-A | `utils/` relocations (blueprint_mapper, gallery_manager dedup, config_loader move, placeholder cleanup, ADR amendment) | §9 | User must approve Pattern B and the specific relocation map. |
| W2-B | Plasmid Lineage 2 AMR-join draft | §1B | Agent will draft to `tmpAI/`; user reviews. |
| W2-C | `app/modules/` shiny refactor (4 files, 1 per PR) | §4A | Each move touches reactive plumbing — agent should propose a per-file plan first. |

## Things I'm NOT doing without confirmation

- Anything that pushes to remote, changes git config, or runs destructive commands.
- Anything that touches `tmp/` (only `@verify` does that).
- Modifying user-owned `[@user]` items.

---

# 🟦 Decision register (for follow-up — non-blocking for tired user)

1. **Plasmid Lineage 2:** ✅ Decided — agent drafts, user reviews. Wave 2.
2. **`utils` library:** Pattern B recommended. Awaiting confirmation. Wave 2.
3. **`phenotype` rename:** ✅ Clarified — manifest column-naming standard. Wave 1 task.
4. **Audit cross-referencing tasks.md:** Open. Suggest we add a one-line "check tasks.md before listing" step to the audit protocol (`audit_2026-05-03.md` and similar). Non-urgent.
5. **Execution order:** Decided by agent (above).

---

# 🚨 Surprises found during this review (not in original audit)

1. **`gallery_manager.py` duplicate** — utils version (83 lines, used by app) vs viz_gallery version (173 lines, has newer features). App is running stale logic. See §9.
2. **`SPARMVET_Error` claim was factually wrong** — class exists; gap is missing failure tests per ADR-034 §7. See §2B.
3. **`utils/placeholder/*.py`** — empty argparse-only stubs, never wired up. Likely deletable. See §9.
4. **`docs/FAQ.qmd` does not exist** — file is at `docs/appendix/FAQ.qmd` (and uses "System Tools"). See §7A.
5. **`predicted_phenotype` is a column-naming convention**, not a temporary rename script. Originated from ADR Precision Renaming Standard. See §6B.
