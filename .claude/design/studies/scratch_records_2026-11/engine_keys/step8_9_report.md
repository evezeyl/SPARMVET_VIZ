# ENGINE-KEYS steps 8 and 9: the texts say what the app does, and the final checks (worker report, 2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`, start head `c0512941`, end head `43f06c0d`. Everything committed. No process of mine left running. Machine load read before every run (1.3 to 3.4). `dev` not merged, no push.

## 1. The three commits

### COMMIT 1 `docs(spec)`: `e9aeeeec` (37 files)

- `.claude/design/plot_authoring_model.md`
- `.claude/design/plot_config_cascade.md`
- `.claude/design/recipe_format_spec.md`
- `.claude/design/reproducible_export_design.md`
- `.claude/design/spaces/BLUEPRINT.md`
- `.claude/design/spaces/TEST_LAB.md`
- `.claude/knowledge/blueprint_architect_ux_spec.md`
- `.claude/knowledge/changelog.md`
- `.claude/knowledge/data_analysis_recipe_data_contract_rules.md`
- `.claude/knowledge/project_conventions.md`
- `.claude/workflows/audit_routine_registry.md`
- `.claude/workflows/implementation_workflow_transformer.md`
- `README.md`
- `app/README.md`
- `config/data_analysis_recipes/README.md`
- `docs/appendix/Standards_yaml.qmd`
- `docs/appendix/data_analysis_recipe_structure.yaml`
- `docs/appendix/data_flow_analogy.qmd`
- `docs/appendix/viz_factory_components.qmd`
- `docs/appendix/viz_factory_rationale.qmd`
- `docs/foundations/data_contracts_adr.qmd`
- `docs/foundations/reproducibility_hash_schema.qmd`
- `docs/reference/decorator_testing.qmd`
- `docs/reference/wrangling_guide.qmd`
- `docs/troubleshooting/index.qmd`
- `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd`
- `docs/user_guide/understanding_your_export.qmd`
- `docs/user_guide/yaml_101.qmd`
- `docs/workflows/audit_scripts.qmd`
- `docs/workflows/blueprint_architect.qmd`
- `docs/workflows/visualisation_factory.qmd`
- `docs/workflows/wrangling.qmd`
- `libs/blueprint_arch/README.md`
- `libs/transformer/README.md`
- `libs/transformer/tests/README.md`
- `libs/utils/README.md`
- `libs/viz_factory/README.md`

### COMMIT 2 `docs(rules)`: `724c83ce` (6 files)

- `.claude/rules/rules_agent_role_bioscientist.md`
- `.claude/rules/rules_data_analysis_recipe_structure.md`
- `.claude/rules/rules_data_engine.md`
- `.claude/rules/rules_gallery_standards.md`
- `.claude/rules/rules_test_lab.md`
- `.claude/rules/rules_viz_factory.md`

### COMMIT 3 `docs(deps)`: `43f06c0d` (10 files)

- `.claude/knowledge/dependency_index.md`
- `.claude/rules/rules_data_analysis_recipe_structure.md`
- `.claude/rules/rules_data_engine.md`
- `.claude/rules/rules_viz_factory.md`
- `app/modules/orchestrator.py`
- `assets/scripts/migrate_recipe_engine_keys.py`
- `libs/transformer/src/transformer/data_assembler.py`
- `libs/transformer/src/transformer/data_wrangler.py`
- `libs/utils/src/utils/engines.py`
- `libs/viz_factory/src/viz_factory/viz_factory.py`

Commit 1 holds no rule file and no `CLAUDE.md`. Commit 2 holds only the six rule files named in the brief. Commit 3 holds the `@deps` edits of code files (comment lines only), the `deps:` front matter of three rule files (the `documents:` lists), the new `@deps` block of `assets/scripts/migrate_recipe_engine_keys.py` and the regenerated `.claude/knowledge/dependency_index.md` (`build_dep_graph.py --root <worktree>`).

What commit 1 says, in short (the spec, section numbers of `recipe_format_spec.md`): the amendment paragraph at the top and the sentence "Format 1 was amended before its first release, on 2026-11-17, by decision of Eve" (also in 4.1); the example of section 1 rewritten (checked: the example block passes `check_recipe` with 0 errors, only advices); new decisions DEC50 to DEC57 in 2.1 (tier shape, plot entry without `spec:`, `ui_label` and `ui_title`, engines, cache keys, dead keys and theme, export record, "no format 2"); DEC05, DEC06, DEC17 amended; tables of 5 (containers), 7.3, 7.5, 7.6, 7.7 (group and plot entry tables written from `libs/utils/src/utils/recipe_spec.yaml` and the checker), 7.8 (content in the entry, theme paragraph, `plot_defaults` keys and the four removed ones), section 8 (registry field `engine`, entry files), section 9 example, section 11 (T06, EN02, EN03, S06, J07, G01, P01, P04, P05, P06, PS01 retired, PD02 new), section 12 (the amendment table), 14, 17. The `docs/appendix/data_analysis_recipe_structure.yaml` got an `engines` entry and a theme note (it had been edited by hand in step 3).

## 2. THE RULE PASSAGES, OLD AND NEW (commit 2; Eve reads this list before the branch is merged)

Every changed passage of a rule file, in file order of the edits. `old` is the text as it was at `c0512941`; `new` is the text now. Everything else in these files is word for word as before. Rule of choice: the least text that makes the passage true; the sentences are those of D-0249 (cache-key rule with the engine argument; removal of the four dead `plot_defaults` keys; the `spec:` change and the tier mapping; the theme rule; the engine clause of plan 5.3 item 4), plus the examples of the same sections that would show a recipe the checker refuses.


### `.claude/rules/rules_data_analysis_recipe_structure.md`

**1. Section 2 (Directory Taxonomy)**

Old:
```text
- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources.
```
New:
```text
- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources, one file per tier; a tier file holds `steps` (and an optional `data_engine`) and is included as `tier1: !include <file>`.
```

**2. Section 2 (Directory Taxonomy)**

Old:
```text
- `join/`: Defines the join steps (`steps:` key only) for joining multiple ingredients into a collection.
```
New:
```text
- `join/`: Defines the join steps (the `steps` of a tier, included as `tier1: !include <file>`) for joining multiple ingredients into a collection.
```

**3. Section 2 (Directory Taxonomy)**

Old:
```text
- `plots/`: Contains visualization specifications for `analysis_groups`. Each file contains a single `spec:` block.
```
New:
```text
- `plots/`: Contains the plot entries of `analysis_groups` that are written in their own file. Each file contains the whole plot entry (there is no `spec:` key).
```

**4. Section 7 (Canonical steps syntax, the canonical example)**

Old:
```text
```yaml
steps:
  - action: cast
    columns: [Year]
    dtype: String
  - action: mutate
    column: predicted_phenotype_clean
    expression: "pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()"
  - action: join
    right_ingredient: metadata_schema
    'on': sample_id
    how: inner
  - action: sort
    columns: [Year, Source, Country]
```
```
New:
```text
```yaml
tier1:
  steps:
    - action: cast
      columns: [Year]
      dtype: String
    - action: mutate
      column: predicted_phenotype_clean
      expression: "pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()"
    - action: join
      right_ingredient: metadata_schema
      'on': sample_id
      how: inner
    - action: sort
      columns: [Year, Source, Country]
```
```

**5. Section 8 (analysis_groups structure)**

Old:
```text
  <group_id>:                         # Snake_case, no spaces
    label: "Human-readable group name"
    plots:
      <plot_id>:                      # Snake_case; unique across ALL data analysis recipes
        label: "Human-readable plot name"
        spec: !include <basename>/<subdir>/<plot_id>.yaml
```
```
New:
```text
  <group_id>:                         # Snake_case, no spaces
    ui_label: "Human-readable group name"
    plots:
      <plot_id>:                      # Snake_case; unique across ALL data analysis recipes
        ui_label: "Human-readable plot name"
        # the plot content is written here (target_dataset, mapping, layers, ...), or the WHOLE entry is in a file:
      <other_plot_id>: !include <basename>/<subdir>/<other_plot_id>.yaml
```
```

**6. Section 8 (analysis_groups structure, rules)**

Old:
```text
- Each `spec: !include` points to a file in `plots/` subdirectory.
- The included plot file must contain a single `spec:` root key. `ConfigManager` auto-unnests it.
```
New:
```text
- Each plot entry written as `!include` points to a file in `plots/` subdirectory.
- The included plot file holds the whole plot entry (`ui_label`, `target_dataset`, `mapping`, `layers`, ...) and no wrapper key; there is no `spec:` key.
```

**7. Section 8 (Visible labels)**

Old:
```text
1. `label:` field if set (recommended — explicit and concise)
```
New:
```text
1. `ui_label:` field if set (recommended — explicit and concise)
```

**8. Section 8 (Visible labels)**

Old:
```text
Data Analysis Recipe authors can use any icons in `label:` to make the UI friendly.
```
New:
```text
Data Analysis Recipe authors can use any icons in `ui_label:` to make the UI friendly.
```

**9. Section 8 (Visible labels, example)**

Old:
```text
    label: "🐱 Cat"                    # ← Tab shows "🐱 Cat"
    description: The boss's favourites
    plots:
      miaou:                           # plot_id stays snake_case (unique-id contract)
        label: "Miaou 🐱"              # ← Tab shows "Miaou 🐱"
        spec: !include cat/miaou.yaml
```

Reserve `description:` for longer prose; use `label:` for short emoji-rich tab text.
```
New:
```text
    ui_label: "🐱 Cat"                 # ← Tab shows "🐱 Cat"
    description: The boss's favourites
    plots:
      miaou: !include cat/miaou.yaml   # plot_id stays snake_case (unique-id contract); the file holds the whole entry, e.g. ui_label: "Miaou 🐱" (Tab shows "Miaou 🐱")
```

Reserve `description:` for longer prose; use `ui_label:` for short emoji-rich tab text; `ui_title:` (optional) is a longer name that the report uses.
```

**10. Section 8 (Plot spec file structure, example)**

Old:
```text
```yaml
spec:
  target_dataset: <join_id>      # Must match a joins key
  mapping:
    x: <column>                  # Aesthetic mapping — column must exist in target_dataset
    fill: <column>               # Optional
    facet_by: <column>           # Optional — triggers facet_wrap(~<column>)
  theme: theme_light             # Optional — must be a registered theme component
  layers:
    - name: geom_bar             # Primary geom — always first. See registered components.
      params: {}
    - name: position_dodge       # For side-by-side bars
      params: {}
    - name: labs
      params:
        title: "Plot Title"
        fill: "Legend Label"
        x: "X Axis Label"
```
```
New:
```text
```yaml
ui_label: "Plot name"            # Required — the short name of the tab
ui_title: "Plot Title"           # Optional — the longer name the report uses (else ui_label)
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
  - name: labs                   # The text of the figure, its title too, is written only here (there is no `title:` key)
    params:
      title: "Plot Title"
      fill: "Legend Label"
      x: "X Axis Label"
```
```

**11. Section 10 (intro)**

Old:
```text
Individual plot specs may override any key. `plot_defaults` participates as **L2** in the five-tier resolution cascade (L5 T3 override > L4 spec >
```
New:
```text
Individual plot entries may override `palette` and `theme`. `plot_defaults` participates as **L2** in the five-tier resolution cascade (L5 T3 override > L4 plot entry >
```

**12. Section 10a (allowed keys)**

Old:
```text
  theme:               theme_light        # registered theme component name (e.g. theme_bw)
  default_font_family: "Liberation Sans"  # plotnine default font family

  # Layout
  facet_panel_spacing: 0.1    # float 0–1; plotnine default 0.05; increase for dense facets
  legend_position:     "right" # "right" | "top" | "bottom" | "left" | "none"

  # Optimisation toggles (reserved — disabled by default except auto_axis_text)
  optimisation:
    auto_axis_text: true   # auto-rotate axis labels when text is long (default true)
    density_jitter: false  # jitter geom_point on dense scatter (default false)
    panel_spacing:  false  # auto-adjust facet panel spacing (default false)
    legend_ncol:    false  # auto-set legend column count (default false)
```

**Unknown key warning:** keys not in the list above emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`. Non-fatal — experimental keys are allowed — but the warning prevents silent typos.
```
New:
```text
  theme:               theme_light        # registered theme component name (e.g. theme_bw)
  layers:              []                 # layers added to every plot (a theme layer sets font, legend position, panel spacing)
  random_state:        0                  # the one seed of the random layers of the recipe
```

**Removed keys (D-0220, D-0242, 2026-11-17):** `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` did nothing and are not keys of `plot_defaults`. Font, legend position and panel spacing are set through a theme layer in `layers:`; the automatic axis-text adjustment has no switch of its own: an `element_text` layer for an axis overrides it.

**Unknown key:** a key not in the list above is refused by the data analysis recipe checker (PD01); each of the four removed keys is refused with a tombstone text (PD02).
```

**13. Section 10c (theme key)**

Old:
```text
- Per-plot `theme:` in the spec overrides this default (L4 wins over L2).
```
New:
```text
- Per-plot `theme:` in the plot entry overrides this default (L4 wins over L2).
- With no theme in the data analysis recipe, a plot is drawn with plotnine's own default (`theme_gray`): the app injects no theme (D-0258).
```


### `.claude/rules/rules_data_engine.md`

**14. Section 1 (Tier 1, Cache key)**

Old:
```text
(resolved data analysis recipe minus downstream-only parts, plus data hash and engine version; ADR-089). Never reuse an anchor by file name alone.
```
New:
```text
(resolved data analysis recipe minus downstream-only parts, plus data hash, engine version and the effective data engine of every table and join; ADR-089). A key contains the engine of what it stores and nothing else: the engine is an argument of the key function, and the plot engine is in no table key (D-0240). Never reuse an anchor by file name alone.
```

**15. Section 1 (Tier 2, Persistence)**

Old:
```text
keyed by the chained `tier2_key` (ADR-089);
```
New:
```text
keyed by the chained `tier2_key`, which takes the effective data engine of that tier 2 as an argument (ADR-089, D-0240);
```

**16. Section 3 (intro)**

Old:
```text
all `wrangling` blocks in YAML data analysis recipes MUST adopt the tiered nesting structure.
```
New:
```text
the tiers of every table and join in YAML data analysis recipes MUST be written as keys of their own (`tier1`, `tier2`), each a mapping with an optional `data_engine` (first key) and `steps`.
```

**17. Section 3 (Structure Requirement)**

Old:
```text
- **`tier1`**: Required (even if empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. MUST be a Sequential List of actions.
- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". MUST be a Sequential List of actions.
```
New:
```text
- **`tier1`**: Required (even if its `steps` are empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. Its `steps` MUST be a Sequential List of actions.
- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". Its `steps` MUST be a Sequential List of actions.
- **`data_engine`**: Optional, the first key of a tier. The engine that runs the tier; without it the `data_engine` at the top of the data analysis recipe applies. The list of engine names is open: a new name ships with an app release, and an app without its library refuses the value with "no library for this engine in this app" (D-0239).
```

**18. Section 3 (Structure Requirement, example)**

Old:
```text
```yaml
wrangling:
  tier1: [ ...ordered actions... ]
  tier2: [ ...ordered actions... ] # Optional: skipped via Identity Logic if omitted
```
```
New:
```text
```yaml
tier1:
  steps: [ ...ordered actions... ]
tier2:                               # Optional: skipped via Identity Logic if omitted
  steps: [ ...ordered actions... ]
```
```

**19. Section 3 (Flat List Rejection)**

Old:
```text
The engine rejects flat `wrangling:` lists with a `DataAnalysisRecipeError`.
```
New:
```text
The engine rejects a tier written as a flat list, and the old container `wrangling:`, with a `DataAnalysisRecipeError`.
```


### `.claude/rules/rules_viz_factory.md`

**20. Section 6b (Data analysis recipe keys, example)**

Old:
```text
# Per-plot override (inside analysis_groups plot spec):
```
New:
```text
# Per-plot override (in the plot entry of analysis_groups):
```

**21. Section 6b (Data analysis recipe keys)**

Old:
```text
The authoritative schema (palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation toggles) is documented at `rules_data_analysis_recipe_structure.md §10`. Unknown keys emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`.
```
New:
```text
The authoritative schema (palette, theme, layers, random_state) is documented at `rules_data_analysis_recipe_structure.md §10`. `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` were removed (D-0220, D-0242). An unknown key is refused by the data analysis recipe checker (PD01) and a removed key is refused with a tombstone text (PD02).
```

**22. Section 7 (cascade table, L4)**

Old:
```text
| **L4** | Plot `spec:` (`analysis_groups.<grp>.plots.<id>.spec`) | Data analysis recipe author |
```
New:
```text
| **L4** | The plot entry (`analysis_groups.<grp>.plots.<id>`; the entry has no `spec:` key) | Data analysis recipe author |
```

**23. Section 7 (cascade table, L3)**

Old:
```text
| **L3** | Optimisation layer (computed from data + spec) — **visual/aesthetic only** |
```
New:
```text
| **L3** | Optimisation layer (computed from data + the plot entry) — **visual/aesthetic only** |
```

**24. Section 7 (cascade table, L1)**

Old:
```text
| **L1** | VizFactory built-in defaults | Developer |
```
New:
```text
| **L1** | VizFactory built-in defaults (`coord_cartesian`, `facet_null`; no theme: a plot with no theme written is drawn with plotnine's own default, `theme_gray`, D-0258) | Developer |
```

**25. Section 7 (Names in the cascade)**

Old:
```text
the `theme:` key of a plot spec and of `plot_defaults` changes,
```
New:
```text
the `theme:` key of a plot entry and of `plot_defaults` changes,
```

**26. Section 7 (Key constraints, L3)**

Old:
```text
Allowed: axis text rotation/size, panel spacing, density-aware positions.
```
New:
```text
Allowed: axis text rotation/size (built). Panel spacing and density-aware positions are designed, not built, and have no switch (the `optimisation` key was removed).
```

**27. Section 7 (Key constraints, unknown keys)**

Old:
```text
- Unknown keys in `plot_defaults` emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)` per ADR-079. Non-fatal.
```
New:
```text
- Unknown keys in `plot_defaults` are refused by the data analysis recipe checker (PD01; the four removed keys with a tombstone text, PD02).
- **The engine (D-0238, D-0239):** the engine of a component is a field of its registry entry (`python-plotnine` for every component today); the plot library is chosen by the `plot_engine` of the plot entry, else of the data analysis recipe; an engine the app has no library for is refused with "no library for this engine in this app". The plot engine is in no table cache key (D-0240).
```


### `.claude/rules/rules_agent_role_bioscientist.md`

**28. Section 3-A (Wrangling blocks, example)**

Old:
```text
```yaml
wrangling:
  tier1:
    - action: filter_range
      columns: [identity]
      min: 90
    - action: cast
      columns: [Year]
      dtype: String
  tier2: []   # Optional; omit if empty
```
```
New:
```text
```yaml
tier1:
  steps:
    - action: filter_range
      columns: [identity]
      min: 90
    - action: cast
      columns: [Year]
      dtype: String
tier2:
  steps: []   # Optional; omit if empty
```
```

**29. Section 3-B (Assembly steps, example)**

Old:
```text
```yaml
steps:
  - action: mutate
    column: predicted_phenotype_clean
    expression: "pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()"
  - action: join
    right_ingredient: metadata_schema
    'on': sample_id
    how: inner
  # Year arrives from metadata_schema — cast AFTER the join, not before
  - action: cast
    columns: [Year]
    dtype: Int64
  - action: cast
    columns: [Year]
    dtype: String
  - action: mutate
    column: Multiresistant
    expression: "pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl.lit('No'))"
  - action: sort
    columns: [Year, Source, Country]
```
```
New:
```text
```yaml
tier1:                                 # a join's tier is its own key: `steps` is the list (the file is included as `tier1: !include <file>`)
  steps:
    - action: mutate
      column: predicted_phenotype_clean
      expression: "pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()"
    - action: join
      right_ingredient: metadata_schema
      'on': sample_id
      how: inner
    # Year arrives from metadata_schema — cast AFTER the join, not before
    - action: cast
      columns: [Year]
      dtype: Int64
    - action: cast
      columns: [Year]
      dtype: String
    - action: mutate
      column: Multiresistant
      expression: "pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl.lit('No'))"
    - action: sort
      columns: [Year, Source, Country]
```
```

**30. Section 3-C (Plot specs, example)**

Old:
```text
```yaml
spec:
  target_dataset: AMR_Profile_Joint
  mapping:
    x: Year
    fill: Multiresistant
    facet_by: Country
  theme: theme_light
  layers:
    - name: geom_bar
      params: {}
    - name: position_dodge
      params: {}
    - name: labs
      params:
        title: "Multi-Resistance by Country"
        fill: "Multiresistant"
        x: "Year"
```
```
New:
```text
```yaml
ui_label: "Multi-Resistance by Country"   # the short name of the tab (there is no `spec:` key)
target_dataset: AMR_Profile_Joint
mapping:
  x: Year
  fill: Multiresistant
  facet_by: Country
theme: theme_light
layers:
  - name: geom_bar
    params: {}
  - name: position_dodge
    params: {}
  - name: labs                            # the text of the figure is written only here (there is no `title:` key)
    params:
      title: "Multi-Resistance by Country"
      fill: "Multiresistant"
      x: "Year"
```
```

**31. Section 3-D (analysis_groups, example)**

Old:
```text
    label: "AMR Profiling Insight"
    plots:
      multi_resistance_by_country:
        label: "Multi-Resistance by Country"
        spec: !include 2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml
```
```
New:
```text
    ui_label: "AMR Profiling Insight"
    plots:
      multi_resistance_by_country: !include 2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml   # the file holds the whole plot entry
```
```


### `.claude/rules/rules_test_lab.md`

**32. Section 4a (stub table)**

Old:
```text
| `wrangling: tier1: []` / `tier2: []` stubs | Yes | Empty stubs only |
```
New:
```text
| `tier1:` (an `!include` of a file that holds `steps`; a tier is its own key) | Yes | Empty `steps` stub only; no `tier2` (an absent tier 2 means T2 equals T1) |
```


### `.claude/rules/rules_gallery_standards.md`

**33. Section 4 (VizFactory Layer Format, Correct)**

Old:
```text
Correct:
```yaml
plots:
  my_plot:
    mapping:
      x: column_a
      y: column_b
    layers:
      - name: geom_point
```
```
New:
```text
Correct:
```yaml
analysis_groups:
  example:
    ui_label: Example
    plots:
      my_plot:
        ui_label: My plot      # the plot entry holds the content directly: there is no `spec:` key
        mapping:
          x: column_a
          y: column_b
        layers:
          - name: geom_point
```
```

**34. Section 4 (VizFactory Layer Format, Wrong)**

Old:
```text
Wrong (both errors):
```yaml
plots:
  my_plot:
    layers:
      - geom: geom_point        # ← wrong key
        mapping: {x: column_a}  # ← mapping belongs at plot level
```
```
New:
```text
Wrong (both errors):
```yaml
analysis_groups:
  example:
    ui_label: Example
    plots:
      my_plot:
        ui_label: My plot
        layers:
          - geom: geom_point        # ← wrong key
            mapping: {x: column_a}  # ← mapping belongs at plot level
```
```

Notes on this list:
- The entries of section 8 (Visible labels): only the key names `label` to `ui_label` changed. The fallback chain below it (`ui_label`, then `description`, then the key) is NOT true (see section 3 below) and is left as it was.
- The emoji in the cat example (`🐱`) were in the examples before and were moved with them; no emoji was added to a rule file.
- The entry "10 (intro)" of `rules_data_analysis_recipe_structure.md` changes "Individual plot specs may override any key" to "Individual plot entries may override `palette` and `theme`": after the four keys are removed the remaining keys are `palette`, `theme`, `layers`, `random_state`, and a plot entry has no `random_state` key (it is on a layer), so "any key" would still not be true.
- The entry of `rules_viz_factory.md` section 7 (the new bullet "The engine ..."): it is the clause of plan 5.3 item 4 ("the engine of a component is a field of its registry entry"), written only in section 7, as the brief named sections 6b and 7.
- Commit 3 also changed the `documents:` line of the front matter of `rules_data_engine.md`, `rules_viz_factory.md` and `rules_data_analysis_recipe_structure.md` (added: `engine_python_polars.py`, `cache_keys.py`, `engine_registry.py`; `engine_python_plotnine.py`, `plot_config_resolver.py`; `recipe_spec.yaml`, `recipe_check.py`). That is a `@deps` edit, not a rule sentence.

## 3. Passages now UNTRUE that I did NOT change (rules, CLAUDE.md, ADRs)

For the rule files the reason is the same each time: D-0249 does not allow it, or the file is not among those the brief named. Line numbers are of the worktree head.

### 3.1 Rule files (untrue because of THIS change, not changed)

| File:line | What it says | Why untrue now |
|---|---|---|
| `.claude/rules/rules_viz_factory.md:40` | "Parameters must be passed through from the YAML `spec`" (section 2, not 6b or 7) | there is no `spec:` key; the plot entry holds the content. One word, but section 2 is not among the named sections |
| `.claude/rules/rules_runtime_environment.md` section 4 | (nothing) | plan 5.3 item 3 proposes one sentence ("An engine library exposes one entry module named `engine_<engine>`; `app/` registers it; `utils.engines` names it"). The file is not in the brief; the sentence is not written |
| `.claude/rules/rules_toolchain.md` (table, line 22 area) | no row for `assets/scripts/recipe_pictures.py`, `gallery_previews.py`, `golden_baseline.py`, `migrate_recipe_engine_keys.py` | the file says "a new tool is added here, in the same commit that starts to use it" |
| `.claude/rules/rules_app_structure.md:44,46,177` | the directory map of `app/modules/` and the ownership matrix | no `engine_registry.py` (the one place that imports the engine entry files) and no `engine_record.py`; no row for "which engine runs a tier or draws a plot" |
| `.claude/rules/ui_implementation_contract.md` 7.2 (line 212, "Bundle contents") | what the bundle holds | `effective_run.yaml` is not named and its new key `engines` (D-0248) is not described |
| `.claude/rules/ui_implementation_contract.md` 12d and 12g.3 | audit rules for a restored session and for a join key | 12g.3 (a join key cannot be dropped) is true and is now alive (the keys were an empty list on `dev`); what a restore does with a stored drop of a key (the step is left out, the rest restored, the user told; commit a005a6b8) is in no rule text |
| `.claude/rules/rules_legacy_management.md` section 2c and 4 | a tombstone has an expiry and a task in `tasks.md` | the four `plot_defaults` tombstones (PD02) expire "two phases after this change is merged"; no `tasks.md` entry exists yet (the spec and `recipe_spec.yaml` say the task is made with the merge) |

### 3.2 Rule files (untrue, but from EARLIER decisions, not from this change, and not among D-0249)

| File:line | What it says | Why untrue |
|---|---|---|
| `rules_data_analysis_recipe_structure.md:4` (front matter), `:26`, `:42-44` | `rule:final_contract`; the directory `output_fields/`; the `final_contract` whitelist (section 5) | `output_fields` and `final_contract` were removed on 2026-11-13 (DEC23) |
| `rules_data_analysis_recipe_structure.md:151-152` | the visible label falls back to `description`, then the key | a group needs `ui_label` (checker G01) and there is no fallback (spec 7.7: "the fallback goes"); I changed only the key name in item 1 |
| `rules_data_analysis_recipe_structure.md:207-211` | the type words `categorical`, `utf8` | refused since format 1 (types are Polars names, DEC27) |
| `rules_data_analysis_recipe_structure.md` section 7 (lines 59-70) | the canonical example uses `cast`, `mutate`, `join`, `sort` | action names are `polars_`, `modif_`, `step_` since DEC31; the example still shows a recipe the checker refuses for those names (the container I changed is right) |
| `rules_data_engine.md:71-72,76` (section 4) | "`wrangling`: Tiered nesting"; "`output_fields`: The Published Contract"; "If `output_fields` is omitted" | section 4 is not among sections 1 and 3; `wrangling` is not a key and `output_fields` is removed |
| `rules_agent_role_bioscientist.md:102,118-140` (examples) | unprefixed action names `filter_range`, `cast`, `mutate`, `join`, `sort` | DEC31; the container I changed is right, the names are not |
| `rules_agent_role_bioscientist.md:194-208,227,239,249,308,327,354,383,396-399` | the `final_contract` whitelist and its checks | removed (DEC23) |
| `rules_agent_role_bioscientist.md:409-430` (section 8, the action list) | the list of "verified action names", all unprefixed | none of them is accepted since DEC31; the list should be regenerated from the registry (not a D-0249 sentence, so not done) |
| `rules_test_lab.md:135,143` (stub table) | an `output_fields: {}` stub; `final_contract:` not generated | `output_fields` is removed and the bootstrapper writes none (I changed only the `tier1` row) |
| `rules_test_lab.md:145-149` (4b) | "Known bugs ... TL-BOOTSTRAP-FIX-1": writes `"plotting"`, hardcodes `metadata_schema:`, no `joins: {}` | not re-verified; the bootstrapper was rewritten in step 4c; probably fixed |
| `rules_gallery_standards.md:16-25` (section 2) | the six taxonomy fields in the `info:` block | the taxonomy is the `taxonomy` key of the plot entry since DEC47; the 34 bundles are written that way |
| `rules_gallery_standards.md:106-109` | `libs/viz_gallery/assets/generate_previews.py` | that file does not exist; the script is `assets/scripts/gallery_previews.py` (the scout's finding of 2026-11-18) |

### 3.3 `CLAUDE.md` (not edited)

- Line 125: `data_analysis_recipe_data_contract_rules.md | input_fields / output_fields validation rules`. The file is now marked partly HISTORICAL (the `output_fields` rules are superseded since DEC23; its structure, roles and ctx_map sections were rewritten 2026-11-18). The description should say what it holds now.
- No other line of `CLAUDE.md` names a recipe key, a tier container, the cache version or the engines.

### 3.4 ADR passages (`.claude/knowledge/architecture_decisions.md`, for the ADR owner)

| ADR | Lines | What needs a note or a change |
|---|---|---|
| ADR-024 (tiers) | 259, 275, 283-284 | "All `wrangling` blocks ... nested tier keys"; "`_resolve_tier()` ... `ManifestError`": tiers are keys of their own (D-0250); the reader is `DataWrangler.tier_steps` (`_resolve_tier` is gone); line 259 says "`steps: {tier3: [...]}`", the shape before 2026-11-17 |
| ADR-089 (cache keys) | 4308, 4315, 4326-4328, 4342 | the `tier1_key` formula and the table of what each key holds: now with the effective data engine of every table and join, `tier2_key(tier1_key, steps, engine)`, the plot engine in no table key, cache version 5, stored tables of another version removed at app start (`transformer.anchor.remove_tables_of_other_version`), the one notice (PROVISIONAL wording). Line 4308 ("only Tier 1 is written") was already stale |
| ADR-097 (export record) | 4867, 4879, 5006, 5013 | `effective_run.yaml` has a new key `engines` (tables per tier, plots with the theme as applied, library versions; D-0248) |
| ADR-083 (plot spec) | 3948, 3951, 3980, 3986, 3993 | "the plot spec file's `layers:`", `spec:`: the plot entry holds the content (D-0237); `serialise_plot_spec` writes the entry's keys; the title seed of the old root `title` is removed (D-0253) |
| ADR-100 (format 1) | 5191, 5194, 5197, 5201, 5206 | point 9 "the plot entry holds `steps: {tier3: [...]}`": now `tier3:` at the entry; the amendment "format 1 amended before its first release, 2026-11-17, no format 2" (D-0236) has no ADR line; the engines are used (D-0219) and every registry entry has a field `engine` (D-0238) |
| ADR-106 (plots) | 5350-5353, 5368 | cites `plot_engine` as "declared"; it is now chosen by the code and per plot; the built-in `theme_bw` is removed (D-0258) |
| ADR-079 / ADR-081 (named in plan 5.4) | not found by line in my grep | the list of allowed `plot_defaults` keys ("extend by ADR amendment only") lost four keys (D-0242); an unknown key is now refused (PD01), no longer a warning |
| ADR-040 / ADR-082 (Blueprint) | 562, 579-581, 595-602, 611, 638-641, 876, 3805, 3836, 3892 | the roles `output_fields`, `plot_wrangling`; `pre_plot_wrangling` (595); the registry slots `wrangling`, `output_fields`; "BLUEPRINT writes ... `wrangling.tier1`, `wrangling.tier2`, `output_fields`"; the forward-propagation hint (BP-FWD-HINT-1) and the "Add plot wrangling" button are removed; a branch writes a tier 1 file and, for a plot, a copy of the whole entry |
| ADR-013 / 014 / 041 / 045 / 046 / 075 / 076 / 084 | 148-172, 537-543, 930-948, 2848-2850, 2913-2999, 4006-4067 | already marked "partly stale (ADR-SYNC-1)" for `output_fields` / `final_contract`; this change adds the container `wrangling` and the key `spec` in the same lines; the agent instruction text (`config/ui/agents/blueprint_default.md`) and the tool `get_field_contract` were rewritten (2986: "the manifest structure rules" the agent is given) |

## 4. UML model `docs/UML/app.mdj` (not edited; what must change)

Read from the file (names of the diagrams and elements as they are in it):

- **DM-RECIPE "The recipe data model"** (class diagram): class `Data schema`, attribute `wrangling: {tier1, tier2}` becomes two attributes `tier1` and `tier2`, each `{data_engine?, steps}`; its attribute `output_fields: Rich Dict, optional` goes (removed 2026-11-13); class `Join`, attribute `steps: canonical action: syntax only` becomes `tier1` and `tier2` (same form); class `Analysis group`, attribute `label` becomes `ui_label`, add `ui_title`; class `Plot`, attribute `label` becomes `ui_label`, add `ui_title`, `plot_engine`, `tier3`; the attribute `spec: {target_dataset, mapping, theme, layers}` goes and its content keys become attributes of `Plot` (no `spec`); the class `Wrangling step` stays (it is the item of the `steps` list).
- **DM-CONFIG "Configuration"**: class `Data analysis recipe`, attribute `plot_defaults`: the allowed keys are `palette`, `theme`, `layers`, `random_state`; add `data_engine` and `plot_engine` ("default of every tier / of every plot"); the diagram does not show them.
- **DM-KEYS "The hash model"** and its three detail diagrams **DM-KEYS-CHAIN**, **DM-KEYS-USE**, **DM-KEYS-EXPORT**: the box "E engine fingerprint ... made from: the declared data and plot engines with their versions and the cache version; enters the key of every T1" must say: the cache version is 5; the key of a tier holds the effective data engine of THAT tier (an argument of the key function); the plot engine enters no table key; the box "ENGINES (declared in the recipe)" gains "per tier and per plot"; the key series `E . rC . dC . [a1] . [s2] ...` gains the engine argument for the tier 1 and tier 2 parts; DM-KEYS-EXPORT: `effective_run.yaml` gains the entry `engines` (D-0248); DM-KEYS-USE: the sweep at app start (stored tables of another cache version are removed, the one notice).
- **SEQ-OPEN "From data analysis recipe to plot"**: the orchestrator asks `engine_registry.data_entry(recipe, body, tier)` for the entry that runs a tier, and the plot is drawn by `PlotEngines.render` (the plot entry's engine, else the recipe's), not by a direct `VizFactory`; the recipe check receives the two engine tables (`action_engines`, `component_engines`).
- **SEQ-EXPORT "Export"**: the export draws through `PlotEngines`, writes `engines` in `effective_run.yaml` (`app/modules/engine_record.py`, `PlotEngines.record_of`), and the tier-2 key comes from `collection_tier2_key`.
- **Component diagrams** (7 `UMLComponent` in the file): add `engine_python_polars.py` (libs/transformer, exposes `ENTRY`), `engine_python_plotnine.py` (libs/viz_factory, exposes `ENTRY`), `app/modules/engine_registry.py` (imports the two entry files, the only place that does), `app/modules/engine_record.py` and `libs/utils/src/utils/engines.py` (the table of the engines); the component `orchestrator` no longer depends on `DataWrangler` and `DataAssembler` directly; `export_handlers` receives the plot dispatcher. After the edit run `assets/scripts/audit_uml_model.py --project-root .`.

## 5. STEP 9: the final checks

### 5.1 The grep for the four removed keys and for `spec:`

Command (from the worktree root; output saved in `tmpAI/scratch/grep1_out.txt` of the worktree, 47 lines):

```
grep -rnE "default_font_family|facet_panel_spacing|legend_position|optimisation" app libs/*/src assets scripts config docs \
  --include=*.py --include=*.yaml --include=*.yml --include=*.md --include=*.qmd --include=*.json --include=*.css \
  --exclude-dir=_site --exclude-dir=build --exclude-dir=__pycache__ --exclude-dir=node_modules --exclude-dir=vendor
```

Remaining hits and the reason for each:

| Hits | Reason |
|---|---|
| `libs/utils/src/utils/recipe_spec.yaml` (4), `app/tests/test_migrate_recipe_engine_keys.py` (2), `docs/appendix/data_analysis_recipe_structure.yaml:78`, `docs/appendix/viz_factory_components.qmd` (3), `docs/workflows/visualisation_factory.qmd:103`, `docs/workflows/blueprint_architect.qmd:284`, `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:26` | the checker's refusal texts (tombstones), the migration tool's test, the docs' own tombstone note, `legend_position` as a `theme_custom` argument and `theme_legend_position` as a component name, the word optimisation for the L3 layer. They stay. |
| `libs/viz_factory/src/viz_factory/themes/core.py` (7), `assets/scripts/figshare_plot_integration.py:119,178,231` | `legend_position` is the plotnine `theme(...)` argument; `theme_legend_position` is a registered component. They stay. |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:2,24,439,444,547,600,751`, `checked_plot.py:340` | the name and the words of the L3 optimisation layer (`compute_optimisation_layer`), which is real (axis text). They stay. |
| **`libs/viz_factory/src/viz_factory/plot_config_resolver.py:72-73`** | `_VALID_PLOT_DEFAULTS_KEYS` still holds all four keys. **A leftover, not a reason to stay**: the checker refuses these keys, the resolver still accepts them. Plan 5.1 says "the four leave the allowed set". NOT FIXED by me (code outside the brief). |
| **`libs/viz_factory/src/viz_factory/viz_factory.py:284-285`** | the warning text for an unknown key still says "Valid keys: palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation". **Leftover**; plan 5.1 asks for the new set. NOT FIXED (outside the brief). |
| **`app/handlers/blueprint_handlers.py:1716-1717,1742-1744,1799-1803`** | the Blueprint plot-defaults form still reads and WRITES `default_font_family`, `facet_panel_spacing`, `legend_position`, so Blueprint can write a recipe that the checker refuses with PD02. D-0246 decided: fix this form first and alone (a separate task); it is not done in this branch. **Open defect, reported.** |

`spec:` under a plot entry. Commands (same folder):

```
grep -rnE "^\s*-?\s*spec:" app libs/*/src assets scripts config docs --include=*.py --include=*.yaml --include=*.yml --include=*.md --include=*.qmd --include=*.json --exclude-dir=_site --exclude-dir=build --exclude-dir=__pycache__ --exclude-dir=vendor
grep -rnE "\[\"spec\"\]|\.get\(\"spec\"|\['spec'\]|\"spec\" in |'spec' in " app libs/*/src assets scripts --include=*.py --exclude-dir=build --exclude-dir=__pycache__
```

| Hit | Reason |
|---|---|
| `libs/utils/src/utils/recipe_spec.yaml:134` | the checker's refusal text for `spec` |
| `app/tests/test_migrate_recipe_engine_keys.py:41` | test data of the migration tool (old shape on purpose) |
| `libs/test_lab/src/test_lab/aqua_synthesizer.py:145` | a Python variable named `spec`, not a recipe key |
| `app/tests/test_no_old_recipe_keys_read.py:79` | the scanner's own test input |
| `libs/utils/src/utils/engine_keys_migration.py:434,448,799` | the migration tool reads the old `spec` to move it |
| `assets/scripts/migrate_plot_specs.py:223-229` | the older migration tool of `factory_id` (ADR-083). **It reads and WRITES `spec:`**: its output is the old shape and the checker refuses it. Needs a follow-up (run `migrate_recipe_engine_keys.py` after it, or adapt it); not done. |

No recipe, template, retest scenario, gallery bundle or doc under `config/`, `assets/` or `docs/` has `spec:` under a plot.

### 5.2 The orphan recipe files under `config/data_analysis_recipes/` (NOT deleted; they wait for Eve)

They are included by no recipe, so the migration did not reach them:

1. `config/data_analysis_recipes/experimental/test_logic.yaml`: empty (0 bytes). It is the one row of the picture check that changed (rejected before and now, with a longer text because the check now names one more thing it must cover: `engines`).
2. `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml`: a plot in the OLD shape (`title`, `family`, `pattern`, `difficulty`).
3. `config/data_analysis_recipes/pipelines/stress_test_master/plots/final_plot.yaml`: a plot in the OLD shape (`title`, no `ui_label`).
4. `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml`: a bare list of steps (format 0).
5. `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml`: field definitions (`type: numeric`, `is_primary_key`) in the wrangling folder.

(A sixth, `.../wrangling/ResFinder_Abromics_wrangling.yaml`, is in the new shape by design.) None holds a removed `plot_defaults` key or a `spec:` at its root, so the two greps do not find them; they are listed so that the reviewer knows why old words (`title`, `family`, `numeric`) still exist under `config/`.

### 5.3 The three proofs at head 43f06c0d (outputs in `tmpAI/proof_step9/` of the worktree)

- Pictures: `PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" <main .venv python> assets/scripts/recipe_pictures.py --check <main>/tmpAI/engine_keys/picture_baseline_15394ef5 --out tmpAI/proof_step9/pictures` gives **`error-changed: 1, identical: 50`** and `PICTURES NOT IDENTICAL` (exit 1). The one changed row is `test_logic::::` (the empty orphan, item 1 above): stored "the recipe check did not cover: actions, components", now "... actions, components, engines". It is not a picture. This is the expected result.
- Golden baseline: `assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json` gives **`result-identical`** (exit 0).
- Gallery previews: `assets/scripts/gallery_previews.py --out tmpAI/proof_step9/gallery` gives **`identical: 34; size only: 0; differs: 0; new: 0; error: 0`** (exit 0).

### 5.4 Checks of the texts

- `assets/scripts/check_doc_links.py --max 0`: **7 problems before and 7 after, the same lines** (all in rule files I did not touch: `rules_runtime_environment.md:79`, `rules_test_lab.md:64,182`, `rules_verification_testing.md:131` and three more; the saved lists `tmpAI/docs_links_before.txt` and `tmpAI/docs_links_after1.txt` of the worktree are identical). My edits add no broken link.
- `assets/scripts/audit_old_words.py --check`: exit 1 before and after (the baseline was already not zero: 9592 "recipe" hits). After commit 1 the "recipe" count is 9629 (+37, almost all in `recipe_format_spec.md`, where "recipe" is the defined short term of its "Terms" line); in the user docs, READMEs and knowledge files I wrote the full term "data analysis recipe". No other retired word changed. Saved in `tmpAI/old_words_after1.txt`.
- Tests that read texts, one process at a time: `app/tests/test_audit_old_words.py test_build_dep_graph.py test_flag_matrix_doc.py test_decision_compliance_files.py test_blueprint_agent_instructions_shape.py test_decision_ledger.py` and `libs/transformer/tests/test_docs_action_page.py`: **210 passed** (4.7 s). `scripts/audit_deps_verify.py`: PASS (21 load-bearing files carry a block); `scripts/audit_changelog_sync.py`: PASS; `scripts/audit_docs_sync.py`: FAIL on the launch commands of `README.md:118` and others only because the worktree has no `.venv/bin/python` (an environment fact, not a text of mine; not rerun in the main folder).
- `quarto render docs --no-execute`: **exit 0**, 58 pages, 1 min 29 s, no warning (load 2.9). The output folder `docs/_site` is git-ignored.
- All fenced `yaml` blocks of the files I changed in commits 1 and 2 (135 that are not sketches) were read by a YAML loader: one fails, a Quarto `{{< include >}}` line that was there before. The example of section 1 of the spec also passes `check_recipe` (structure only, build profile: 0 errors, 3 advices).
- `@deps`: for every non-test `.py` file changed on the branch (my script `tmpAI/scratch/deps_check.py` of the worktree): every path named in a block exists; two imports that the branch added were missing from a block (`orchestrator.py` to `utils.recipe_tiers`, `engines.py` to `utils.errors`) and are now named; three `consumed_by` lines that the engine entries made untrue were corrected (`data_wrangler.py`, `data_assembler.py`, `viz_factory.py`: the orchestrator and the server no longer import them, the entry files do). 72 other imports in changed files are not named in their blocks but were not added by this branch (older gaps): not changed. Files changed on the branch that never had a block: `assets/scripts/convert_gallery_examples.py`, `gallery_previews.py`, `golden_baseline.py`, `retest_walkthrough.py`, `scripts/audit_data_analysis_recipe_coherence.py` (the new `migrate_recipe_engine_keys.py` now has one).

## 6. Found, outside my task (reported, not fixed)

1. Three places still carry the four removed `plot_defaults` keys as live code (section 5.1): `plot_config_resolver.py:72-73`, `viz_factory.py:284-285` and, as a real defect for a user, the Blueprint plot-defaults form (`blueprint_handlers.py:1716-1803`, which writes keys the checker refuses; D-0246 plans its repair as a first, separate task).
2. `libs/utils/src/utils/errors.py:63`: the default tip of an error says "ensure required keys (input_fields, wrangling, output_fields...)": two of the three are not keys of a recipe.
3. `assets/scripts/debug_bootstrap_viz_yamls.py:170` writes `"output_fields": []`.
4. `assets/scripts/migrate_plot_specs.py:223-229` writes `spec:` (old shape).
5. `libs/viz_factory/tests/test_data/` (218 files; 173 yaml files hold `wrangling:` and a root `plots:`): `libs/viz_factory/tests/debug_runner.py` on one of them stops with "Root-level 'plots:' key is not a valid authoring format" (I ran it). This is not from this branch (the README of the library says these recipes wait for a decision), but `libs/viz_factory/tests/README.md` still shows their form and I did not change it.
6. `docs/UML/data_contract_and_failures.md:55,100` still show a data check on `output_fields` (removed 2026-11-13). Not rewritten: it needs a verified run of the data check to say what the message is now.
7. The exploratory documents `.claude/design/maps_advanced_geo.md:107` and `.claude/design/feature_extension/bioinformatics_viz.md:60` show future plot sketches under `spec:`; they describe features that do not exist; not changed. `.claude/design/home_audit_steps.md:162`, `adr_100_recipe_format_1_draft.md`, `recipe_review_st22_2026-11-11.md`, `viz_rename_impact_2026-11-15.md`, the archives and the `outdated/` folders are records; not changed.
8. `docs/workflows/blueprint_architect.qmd` ("BLUEPRINT never writes Tier 3") says the opposite of the note of 2026-11-15 in spec 7.7 (Blueprint MAY author the plot entry's tier 3). Not from this change; left.
9. `libs/viz_factory/README.md` "Library Integrity Status" (535 tests, 2026-11-14) is old. Not changed.

## 7. Decisions of the brief: how the texts comply

| Decision | Where in the texts | Check |
|---|---|---|
| D-0249 "The rule and spec sentences of plan sections 3.2 and 5.3 may be changed" | rules: section 2 above (the cache-key sentences of `rules_data_engine.md` 1, the four keys in `rules_data_analysis_recipe_structure.md` 10a and `rules_viz_factory.md` 6b and 7, the `spec:` and tier mapping in the six files, the theme sentence in 10c and in the L1 row); spec: DEC50 to DEC57, 4.1, DEC05 | the old and new text in section 2 |
| D-0236 "Format 1 is amended before its first release; no format 2" | spec header, 4.1, DEC57 | the sentence is in the spec |
| D-0250 "a tier is written as its key (`tier1:`), then the optional `data_engine:`, then `steps:` with the list; no outer container" | spec DEC50, 5, 7.3, 7.5, 7.6; all docs and rule examples | the spec example passes `check_recipe` |
| D-0253 "The app-side name `label` becomes `ui_label`" | spec DEC52, 7.7; docs, rules, READMEs, `project_conventions.md` | checker G01 and P01 (section 11 of the spec) |
| D-0240 "The plot engine enters no table key; the tier-2 engine is an argument of the tier-2 key, and each tier's engine is in its own key" | spec DEC54, `rules_data_engine.md` 1, `reproducibility_hash_schema.qmd`, `libs/transformer/README.md`, changelog | the code is `app/modules/cache_keys.py` (read, not changed) |
| D-0239 "The engine names are an open list: a new engine name ships with an app release" | spec DEC05, 4.1, DEC53; `rules_data_engine.md` 3; docs | the words "no library for this engine in this app" are the decided ones |
| D-0255 "it is merged only after the full controls pass (browser gate and golden pictures included)" | not a text rule: golden, pictures and previews ran (5.3); the full controls (browser files, full `app/tests`) are the reviewer's | see section 8 |
| D-0285 "do not run the same tests that also cost time" | I ran only the text-reading tests, the three proofs and the quarto render; no full suite, no browser file, nothing twice | section 5.4 |

## 8. What I did not check

- The full `app/tests`, the browser files and the `libs/*` suites (the brief said not to; the reviewer runs the full controls). My commits change no `.py` line except comment lines (`@deps`) and the new `@deps` block of the migration script (parsed with `ast`; the picture, golden and preview proofs ran after it).
- That each sentence of the knowledge files I did not touch is true (for example `project_conventions.md` sections 10 to 14 and `data_analysis_recipe_data_contract_rules.md` sections 11 to 14 about the orchestrator paths and the join key cast, which look old). I fixed the lines that named the old shape and marked the `output_fields` part of the second file HISTORICAL.
- The examples in the user docs against the full checker (only the YAML syntax of every block, and the spec example against `check_recipe`).
- Blueprint's behaviour as described in `blueprint_architect.qmd` and `blueprint_architect_ux_spec.md`, in a real browser (I wrote from the code and from the step 4, 4c and fix reports).
- ADR text, the UML model, `CLAUDE.md`, the ledger and `tasks.md` (not edited, as told).
- That nothing else in `.claude/design/` (about 60 files) names the old shape: I searched with the old words only, not by reading each file.
