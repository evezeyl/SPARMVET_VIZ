---
trigger: always_on
deps:
  provides: [rule:canonical_steps_syntax, rule:directory_taxonomy, rule:analysis_groups_structure, rule:final_contract]
  documents: [libs/transformer/src/transformer/data_assembler.py, app/handlers/home_theater.py, libs/utils/src/utils/recipe_spec.yaml, libs/utils/src/utils/recipe_check.py]
  consumed_by: [.claude/rules/rules_agent_role_bioscientist.md, docs/appendix/data_analysis_recipe_structure.yaml, .claude/knowledge/dependency_index.md]
---

# Data analysis recipe Structural Standard (rules_data_analysis_recipe_structure.md)

**Authority:** Defines the structural organization and explicit layout requirements for all data and plotting data analysis recipes.

## 1. Basename Mirroring Mandate (Keyword & Complexity Trigger)

To maintain modularity and prevent YAML bloat, **high-complexity data analysis recipes** (e.g., Master Pipelines) MUST separate their logical components into individual YAML snippet files via the `!include` constructor.

- **The Rule**: A main data analysis recipe file (e.g., `main.yaml`) MUST organize its `!include` components within a directory matching its exact basename (e.g., a `main/` directory located at same level as `main.yaml`).
- **Complexity Trigger**: For small or "Single-Task" data analysis recipes, inline logic is permitted to avoid overhead. However, any data analysis recipe exceeding ~150 lines or involving more than 3 data sources MUST transition to the Mirrored Directory standard.

## 2. Directory Taxonomy (Keyword-Driven Organization)

When decomposition is triggered, components must be strictly categorized into subdirectories based on their logical keywords. Specifically:

- `input_fields/`: Defines raw incoming schemas.
- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources, one file per tier; a tier file holds `steps` (and an optional `data_engine`) and is included as `tier1: !include <file>` (D-0250).
- `join/`: Defines the join steps (the `steps` of a tier, included as `tier1: !include <file>`) for joining multiple ingredients into a collection. One file per join block (e.g., `AMR_Profile_Joint.yaml`). Top-level data analysis recipe key: `joins:`.
- `plots/`: Contains the plot entries of `analysis_groups` that are written in their own file. Each file contains the whole plot entry (there is no `spec:` key; D-0237, D-0252).

There is no `output_fields/` folder: `output_fields` and `final_contract` are removed (D-0034; section 5).

## 3. Structural Authority Reference

The file `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` serves as the official structural standard.

- Any adaptations made to the `1_test_data_ST22_dummy.yaml` template logic or subdirectory groupings MUST be immediately reflected back into this rulebook to remain the authoritative requirement for the entire system.

## 4. Documentation & Appendix Mandate

- **User Documentation Sync**: Any changes made to the structure of data analysis recipes MUST be immediately reflected in the appropriate library READMEs and user-facing `.qmd` documentation files.
- **Standalone Appendix Registry**: The YAML data analysis recipe structure must be physically maintained as a standalone reference file located at `docs/appendix/data_analysis_recipe_structure.yaml`. If any changes are implemented regarding how data analysis recipes are used, grouped, or structured, this appendix file must be updated to serve as the external user-facing source of truth.

## 5. The published columns (the last `polars_select`)
- **The Protocol**: `final_contract` and the schema's `output_fields` are removed (D-0034, DEC23; built: the checker refuses both with the replacement named). The published columns of a collection are the last step of its tier 1, a plain `polars_select` (or `polars_drop`), so every column change is a visible step and the column order is the order of the list. Display names of computed columns go in a `labels: {column: text}` mapping on the collection.
- **The Effect**: A column that the last `polars_select` does not name is not in the table.
- **Developer Rule**: Always check the last `polars_select` of the tier if a newly created column is missing from the output TSV/Parquet.

## 6. Biological Typing & Discrete Plotting
- **The Protocol**: To ensure Plotnine correctly renders discrete scales (e.g., for Year, Sequence Type), columns MUST be cast to appropriate types in the assembly steps.
- **The Rule**: Numeric values used as categories (integer years) MUST be cast to `int` or `string` in the Tier 2 assembly to prevent continuous-scale stretching in visualizations.

---

## 7. Canonical steps syntax (STRICT — No Shorthand)

**ALL** wrangling and assembly steps MUST use the canonical `action:` key format, with the registered action names (`polars_<name>`, `modif_<name>`, `step_<name>`; D-0036). Shorthand formats (using the action name as the YAML key, e.g., `- join: {...}`, `- mutate: [...]`, `- sort: [...]`) are refused by the checker (ST01), and an old action name without its prefix is refused with the new name (ST02).

### ✅ Canonical (ONLY valid format)

```yaml
tier1:
  steps:
    - action: polars_with_columns
      named_exprs:
        predicted_phenotype_clean: pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()
    - action: polars_join
      right_ingredient: metadata_schema
      'on': [sample_id]
      how: inner
      maintain_order: left_right
    - action: polars_cast
      columns: [Year]
      dtype: String
    - action: polars_sort
      by: [Year, Source, Country]
      maintain_order: true
```

### ❌ Forbidden shorthand (silently broken)

```yaml
# ALL OF THESE ARE FORBIDDEN:
- mutate:
    - col: "expr"        # WRONG — engine never sees 'action' key
- join:
    dataset_id: foo      # WRONG — must be 'right_ingredient', not 'dataset_id'
    on: sample_id        # WRONG — 'on' is YAML boolean True, must be quoted 'on'
- sort:
    - Year               # WRONG — shorthand, no 'action' key
```

### Key-specific rules

| Step list concept | Canonical key | FORBIDDEN alias |
|---|---|---|
| Join right-side dataset | `right_ingredient` | `dataset_id` |
| Join column (symmetric) | `'on'` (quoted!) | `on` (unquoted — YAML parses as boolean `True`) |
| Add or compute a column | `action: polars_with_columns`, `named_exprs: {column: expression}` | the old `action: mutate` (refused with the new name) |
| Cast a column type | `action: polars_cast`, `columns`, `dtype` | `action: polars_with_columns` with `pl.col().cast()` inline |

### YAML Boolean Trap

The key `on` is a **YAML reserved word** that is silently parsed as boolean `True`. **Always quote it**: `'on': sample_id`.

**Engine resilience (defensive fallback — not a license to omit quotes):**
`DataAssembler` (`data_assembler.py:249-252`) recovers from unquoted `on:` via key-chain fallback:

```python
join_key = (step.get("on") or          # correct (quoted 'on' → string key)
            step.get("left_on") or
            step.get("on_column") or
            step.get(True))             # fallback: unquoted 'on' → boolean True key
```

`ConfigManager` uses `yaml.SafeLoader` with **no custom resolver** for the boolean trap — prevention is not handled at load time. The fallback in the assembler catches the most common failure mode, but:
- `parse_join_step` in `join_designer.py` (Blueprint save path) applies the same guard: `step.get("on", step.get(True))`.
- The **serialization path** (writing a dict back to YAML via `yaml.dump`) will emit `'on': value` correctly only if the key is already the string `"on"` — `yaml.dump` does NOT automatically quote YAML reserved words when the key comes from a Python string. Safe as long as `build_join_step` is used (it emits the string key `"on"`).
- **Risk for the join Save path** (`_serialise_component_for_save`, not yet implemented): the serializer MUST explicitly quote the `on` key in the output YAML (e.g., via a custom representer or manual string quoting). Failure to do so will produce a data analysis recipe that reloads with `True` as the key; the assembler fallback will recover, but the data analysis recipe will be non-human-readable and flagged as malformed.

**Rule:** Always quote in data analysis recipe YAML (`'on': sample_id`). The fallback is a safety net, not the intended path.

---

## 8. `analysis_groups` Structure (Data analysis recipe-Driven Home Theater)

> **REMOVED (LEGACY-FLAT-PLOTS-1, Phase 34, 2026-05-22):** Root-level `plots:` is now a `ConfigurationError`.
> ConfigManager raises a fatal error if a data analysis recipe contains `plots:` at the root. Declare all plots inside `analysis_groups:` exclusively.
> Migration: move all plot specs from root `plots:` into an `analysis_groups:` block.
> **Tombstone expires:** Phase 36 (delete this block after two phases)

The `analysis_groups` top-level key defines the groups and plots rendered in the Home Theater (Phase 21-B). **This is the ONLY authoring format for plots.**

```yaml
analysis_groups:
  <group_id>:                         # Snake_case, no spaces
    ui_label: "Human-readable group name"
    plots:
      <plot_id>:                      # Snake_case; unique across ALL data analysis recipes
        ui_label: "Human-readable plot name"
        # the plot content is written here (target_dataset, mapping, layers, ...), or the WHOLE entry is in a file:
      <other_plot_id>: !include <basename>/<subdir>/<other_plot_id>.yaml
```

**Rules:**
- `plot_id` must be snake_case (ASCII identifier — letters, digits, underscore) and **globally unique across all data analysis recipes** (the app registers `@render.plot` by ID at startup).
- The same `plot_id` written in two groups of ONE recipe is refused by the recipe check, code P07 (built 2026-11-22; wording PROVISIONAL): one plain line names the id and both groups. Across recipes the id is checked by X5 (`check_recipe_set`).
- `group_id` (the dict key) is auto-sanitised to a Shiny-safe internal ID via `_safe_id()`. **Spaces, emoji, and punctuation are allowed** — they're stripped from the internal ID but preserved verbatim in the visible label. (Updates ADR-036: previously hardcoded sanitisation; now general regex sanitisation.)
- Each plot entry written as `!include` points to a file in `plots/` subdirectory.
- The included plot file holds the whole plot entry (`ui_label`, `target_dataset`, `mapping`, `layers`, ...) and no wrapper key; there is no `spec:` key (D-0237, D-0252; built: `spec` is refused, P01).

### Visible labels (icons & emoji are encouraged)

The visible name of a group or a plot comes from ONE key, `ui_label` (D-0253, D-0409; required on a group and on a plot entry; the recipe check refuses a group or a plot without it). There is no fallback: the app invents no name (no `description`, no id in title case). The same `ui_label` is the tab in HOME, the list entry in the dialogs and the heading in the export report (a group is a `##` heading, a plot a `###`). The recipe's own name is `info.ui_label` (optional, with an advice when it is missing: the file name is shown then; D-0410, D-0470); the HOME banner shows it and reads nothing else of `info`.

All of them preserve any unicode, including emoji and CJK. Data Analysis Recipe authors can use any icons in `ui_label:` to make the UI friendly. Example:

```yaml
analysis_groups:
  Cat 🐱:                              # Internal id auto-sanitised to "cat"
    ui_label: "🐱 Cat"                 # ← Tab shows "🐱 Cat"
    description: The boss's favourites
    plots:
      miaou: !include cat/miaou.yaml   # plot_id stays snake_case (unique-id contract); the file holds the whole entry, e.g. ui_label: "Miaou 🐱" (Tab shows "Miaou 🐱")
```

Reserve `description:` for longer prose; use `ui_label:` for short emoji-rich tab text. The report uses the same `ui_label` as the tab (D-0409; `ui_title` is removed). The figure text (axis names, legend names, figure title) is written only in the `labs` layer (D-0253).

### Plot spec file structure (`plots/<plot_id>.yaml`)

> **DEPRECATED (ADR-083, 2026-05-20):** `factory_id` shorthand (e.g. `factory_id: bar_logic`) is removed.
> Use explicit `geom_*` layers in `layers:` and all aesthetics under `mapping:` (see canonical format below).
> Engine raises `PipelineError` when `factory_id` is present. Migration: `assets/scripts/migrate_plot_specs.py --apply`.
> **Removal task:** BP-PLOT-LEGACY-REMOVE-1

Plot specs use a grammar-of-graphics format (ADR-083): explicit `geom_*` layers in `layers:`, all aesthetics in a `mapping:` block.

```yaml
ui_label: "Plot name"            # Required — the short name of the tab
target_dataset: <join_id>        # Must match a joins key
mapping:
  x: <column>                    # Aesthetic mapping — column must exist in target_dataset
  fill: <column>                 # Optional
  facet_by: <column>             # Optional — triggers facet_wrap(~<column>)
theme: theme_light               # Optional — must be a registered theme component
layers:
  - name: geom_bar               # Primary geom — always first. See registered components.
    params: {}
  - name: position_dodge         # For side-by-side bars
    params: {}
  - name: labs
    params:
      title: "Plot Title"
      fill: "Legend Label"
      x: "X Axis Label"
```

Common primary geoms: `geom_bar`, `geom_col` (needs `y`), `geom_point`, `geom_tile`, `geom_boxplot`, `geom_violin`. See `libs/viz_factory/src/viz_factory/geoms/` for the full registered list.

**`position`, `labels`, and `color`/`fill` scales as flat keys are NOT supported.** They must appear as named layers. See registered components in `libs/viz_factory/src/viz_factory/`.

---

## 9. Authorized Data Types for `input_fields`

`type` is required on every field and is a Polars dtype that a text file can hold, written with its Polars name (`String`, `Categorical`, `Int64`, `Float64`, `Boolean`, ...); the declared dtype is given to the reader, which fails strictly and names the value (D-0035, D-0057; built, check FD02). `String` and `Categorical` are both valid types (D-0057). The old names `categorical`, `utf8`, `string`, `character`, `numeric`, `integer`, `int`, `i64`, `float` are refused with the replacement named; `categorical` always meant `String` ("this was String").

**Primary key rule:** the sample id is a string or a categorical, never a number: a number gives join and type problems (it loses leading zeros, and type-parity mismatches in `polars_join` steps). The checker refuses a number type on a field marked `is_entity_id` (code E03; D-0225).

---

## 10. `plot_defaults` Block (ADR-081, BP-COLOR-3, VIZFAC-PLOT-CASCADE-1)

The optional `plot_defaults:` top-level key in a data analysis recipe sets defaults applied to every plot in that data analysis recipe. Individual plot specs may override any key. `plot_defaults` participates as **L2** in the five-tier resolution cascade (L5 T3 override > L4 plot entry > L3 optimisation > L2 plot_defaults > L1 built-ins). Full cascade spec: [.claude/design/plot_config_cascade.md §7a](../design/plot_config_cascade.md).

### 10a. Allowed keys (authoritative — extend by ADR amendment only)

```yaml
plot_defaults:
  # Visual style
  palette:             nvi_official       # deployment palette name or matplotlib name (see §10b)
  theme:               theme_light        # registered theme component name (e.g. theme_bw)
  layers:              []                 # layers added to every plot (a theme layer sets font, legend position, panel spacing)
  random_state:        0                  # the one seed of the random layers of the recipe
```

**Removed keys (D-0220, D-0242, 2026-11-17):** `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` did nothing and are not keys of `plot_defaults`. Font, legend position and panel spacing are set through a theme layer in `layers:`; the automatic axis-text adjustment has no switch of its own: an `element_text` layer for an axis overrides it.

**Unknown keys fail:** a key not in the list above is refused by the checker (PD01), as every unknown key of the format is (D-0033, DEC02; built, `recipe_check.py`). Each of the four removed keys is refused with a tombstone text (PD02).

### 10b. `palette` key

- Value must be either a deployment palette name (defined in `config/palettes.yaml`) or a matplotlib palette name (`Blues`, `viridis`, `Set1`, etc.).
- VizFactory resolves the palette at render time via the cascade resolver.
- Resolution order: **plot-level `palette:` > `plot_defaults.palette` > none**.
- Scale injection is skipped when the plot mapping has no `fill` / `color` aesthetic, or when the data analysis recipe already declares a `scale_fill_*` / `scale_color_*` layer.

### 10c. `theme` key

- Value must be a registered theme component name. Examples: `theme_bw`, `theme_light`, `theme_minimal`, `theme_dashboard`.
- Per-plot `theme:` in the plot entry overrides this default (L4 wins over L2).
- With no theme in the data analysis recipe, a plot is drawn with plotnine's own default (`theme_gray`): the app injects no theme (D-0258; built, `plot_config_resolver.py:55`).

### Built-in palettes (always available, no `config/palettes.yaml` required)

| Name | Colors |
|---|---|
| `sparmvet_brand` | `#345beb`, `#10a395`, `#ffc107`, `#d62828`, `#6c757d`, `#6a4c93` |

Deployment palettes are defined in `config/palettes.yaml` and loaded by `bootloader.get_palettes()` at startup. See that file's header for the format. Agents MUST NOT assume a deployment palette name exists unless `config/palettes.yaml` has been inspected.

---

## 11. Data analysis recipe Load Errors (ADR-087, extended by ADR-094)

> **Implementation status (2026-11-08):** HOME's automatic load gate (below) is implemented
> and is how ADR-087's promise is actually kept today. `ConfigManager` itself is unchanged —
> it still calls `exit_if_errors` (`sys.exit`) on a broken data analysis recipe. What changed
> is that HOME never hands it one: every recipe is checked once at `Bootloader` startup, and a
> recipe that fails never reaches `ConfigManager` through HOME's normal path. BLUEPRINT's own
> recipe-load path is intentionally untouched — BLUEPRINT is meant to show you the error, not
> hide it (see §11a).

### 11a. HOME's automatic load gate (ADR-094) — different rule for HOME than for BLUEPRINT

HOME and BLUEPRINT need opposite failure behaviour, not the same one: HOME runs an
already-built recipe for a user who may not be able to fix it; BLUEPRINT is where errors are
the expected, normal state while building one.

- **HOME — automatic, blocking, no button to press.** `Bootloader` (module-level singleton,
  created once per app process) runs `validate_data_analysis_recipe()` (structure) and
  `validate_data_analysis_recipe_data()` (data vs. declared contract) against every discovered
  recipe once at startup. A recipe that fails either check is excluded from
  `bootloader.available_data_analysis_recipes` — it can never be selected, never becomes the
  default — and recorded in `bootloader.rejected_data_analysis_recipes` with its problems and a
  resolved contact. HOME's "Data analysis recipe Choice" panel shows rejected recipes beneath
  the selector. The app never crashes because of a bad recipe; a bad recipe is simply not an
  option, with a visible reason.
- **BLUEPRINT — manual, advisory, unchanged.** The "Validate" action (`btn_bp_validate`,
  BP-VALIDATE-1 / VALIDATE-UI-1) runs the same two checks on demand. Nothing is excluded or
  blocked — BLUEPRINT's job is to help you see and fix the problem, not hide the recipe from you.
- **Contact resolution, two tiers, no fabrication.** `resolve_contact()`
  (`data_analysis_recipe_validator.py`): the rejected recipe's own `info.contact` first, else
  the deployment's `branding.contact` (`config/deployment/.../*.yaml`), else nothing shown.
  `info.contact` is a recommended (not required) field in a recipe's `info:` block — the only
  way a HOME user can reach a real contact when BLUEPRINT is not part of that deployment
  (`blueprint_enabled: false`, e.g. `pipeline-static`, `pipeline-exploration-simple`).
  `read_data_analysis_recipe_header(path)` reads `info.contact` via a bare `yaml.safe_load` —
  no `ConfigManager`, no engine — so it survives a recipe broken badly enough to fail every
  other check.
- **The operator-named default gets the same gate, not a bypass.** If
  `default_data_analysis_recipe` names a recipe that exists but fails the gate: selector
  visible → HOME falls through to the first recipe that passes, never silently opens the broken
  one; selector hidden (no escape hatch for the user) → still fatal at startup, same as a
  genuine "not found" typo, but the message names the real cause and the contact instead of
  suggesting a spelling fix.
- **Scope boundary — closed (issue #38, 2026-11-09):** `get_default_data_analysis_recipe()`
  itself still raises when literally every recipe fails the gate (unchanged exception type,
  improved message) — but nothing in the startup path calls it unguarded any more.
  `Bootloader.get_default_data_analysis_recipe_or_none()` and `bootloader.has_usable_data_analysis_recipe`
  are the non-raising siblings; `active_cfg()` (`app/src/server.py`) returns an empty stand-in
  instead of raising when there is no usable recipe, and `dynamic_tabs()`'s Home branch renders
  a short "No data analysis recipes yet" message (pointing at Blueprint/Test Lab, whichever
  this deployment enables) instead of reaching the assembly `try`. See ADR-094 point 6's
  closure note for the full list of what changed.
- **Pre-release deployment testing is a separate, earlier line of defense**, not replaced by
  this gate — the gate is the second line, for drift after release.

### 11b. The underlying checks

- A problem in a data analysis recipe's own shape (missing `analysis_groups:`, missing
  `!include` file, bad step list shape) raises `DeploymentFailure` inside
  `validate_data_analysis_recipe()` (caught internally — `ConfigManager`'s own `sys.exit` on
  this path is intercepted and turned into a reported problem, never propagates).
- Command-line scripts and audits catch load problems directly, print the block and exit
  non-zero themselves — unchanged.
- To check a data analysis recipe without loading it into the app, use
  `validate_data_analysis_recipe()` (`app/modules/data_analysis_recipe_validator.py`).
- `validate_data_analysis_recipe_data(path, raw_data_dir)` (same module) also reads the data
  files and reports a dataset that cannot be loaded (missing file, missing input column, a value
  that does not fit its type) and a wrangling step that cannot run on the declared types (issue #18).
  `output_fields` no longer exists (D-0034; section 5).
  `app/tests/test_data_analysis_recipe_data_check.py` runs it on every shipped data analysis
  recipe; `app/tests/test_data_analysis_recipe_load_gate.py` runs the full gate.
- **Where a recipe fails (DECIDED, not built; D-0338, D-0342):** one function turns the place of a problem (the table or join, the tier, the step) into the file and the line where it is written, also inside an included file, and every error that names a place uses it: the recipe check, the load gate, the build at opening, the writing of the audit file. Not decided (D-0342): the form of the sentence, whether the path of keys stays in the message, the guard when a file changed between the check and the message, and how a problem met only when the data is read names its place. The line shown when the check itself fails is kept as built, provisional (D-0338).
- A dataset that the requested collection needs and that cannot be loaded makes
  `materialize_tier1` raise `IngestionError` naming the dataset and the reason. Before issue #18
  it was dropped and the join steps that used it were skipped with a console line.

---

## 12. The `id:` key equals the file name (ADR-092)

The file name without `.yaml` is the data analysis recipe id (selector, cache keys, sessions, export). The top-level `id:` key of the file marks the root of a data analysis recipe and is shown in the Pipeline Audit panel, so it MUST equal the file name. `validate_data_analysis_recipe()` reports a difference; `app/tests/test_data_analysis_recipe_validator.py` checks every shipped data analysis recipe and template. There is no top-level `type:` key (removed, issue evezeyl/SPARMVET_VIZ#29); describe the data analysis recipe under `info:`.
