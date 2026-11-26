# Rule text of the big recipe change: 45 passages for your yes (2026-11-19)

This page lists the rule sentences the recipe change rewrites in six rule files. Rule text needs your yes. You can merge with these sentences, or merge without them and bring them later. Six files, 21 changed blocks, 45 passages (R1 to R45): 5, 19, 9, 2, 1 and 9 per file. D-0249 allowed, in the ledger's words: "Plan question 14: yes. The rule and spec sentences of plan sections 3.2 and 5.3 may be changed (the cache-key rule with the engine argument; the removal of the four dead keys; the open engine names in 4.1 and DEC05; the `spec:` change and the tier mapping; the theme rule)." Your words in that line (M256): "13 and 14 are trivial (because of 12 and our principles) - as they are related - so put now".

Four passages wait for you separately, with the `dev` wording: `tmpAI/engine_keys/RULE_PASSAGES_for_eve.md`. The labels (`ui_label`) passages here (R4, R11, R12, R15, R16, R17) are the same subject as its item 1.

## Rule file 1: `.claude/rules/rules_agent_role_bioscientist.md` (5 passages)

**R1.** Under "### 3-A. Wrangling blocks (for `data_schemas`)"
- Now: `wrangling:` / `  tier1:` / `  tier2: []   # Optional; omit if empty`
- New: `tier1:` / `  steps:` / `tier2:` / `  steps: []   # Optional; omit if empty` (the step lines are unchanged)
- Kind: only the example YAML follows the new shape

**R2.** Under "### 3-B. Assembly steps (in `assembly/<name>.yaml`)"
- Now: `steps:` as the first line of the example
- New: `tier1:                                 # a join's tier is its own key: `steps` is the list (the file is included as `tier1: !include <file>`)` / `  steps:`; the six steps and the comment lines are the same, indented two spaces more
- Kind: only the example YAML follows the new shape

**R3.** Under "### 3-C. Plot specs (in `plots/<plot_id>.yaml`)"
- Now: `spec:` / `  target_dataset: AMR_Profile_Joint` / `  mapping:` ... (the example, 2 more indent levels)
- New: `ui_label: "Multi-Resistance by Country"   # the short name of the tab (there is no `spec:` key)` / `target_dataset: AMR_Profile_Joint` / `mapping:` ... (the example without the `spec:` wrapper, 26 lines in the example, 8 shown here: the first 8 lines of the new block)
- Kind: only the example YAML follows the new shape

**R4.** Under "### 3-D. `analysis_groups` (top-level in master data analysis recipe)"
- Now: `    label: "AMR Profiling Insight"`
- New: `    ui_label: "AMR Profiling Insight"`
- Kind: a key or word renamed

**R5.** Same example, plot entry
- Now: `      multi_resistance_by_country:` / `        label: "Multi-Resistance by Country"` / `        spec: !include 2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml`
- New: `      multi_resistance_by_country: !include 2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml   # the file holds the whole plot entry`
- Kind: only the example YAML follows the new shape

## Rule file 2: `.claude/rules/rules_data_analysis_recipe_structure.md` (19 passages)

**R6.** Top of the file, front matter (`deps`, "documents:")
- Now: `  documents: [libs/transformer/src/transformer/data_assembler.py, app/handlers/home_theater.py]`
- New: `  documents: [libs/transformer/src/transformer/data_assembler.py, app/handlers/home_theater.py, libs/utils/src/utils/recipe_spec.yaml, libs/utils/src/utils/recipe_check.py]`
- Kind: added (two file names added to the list)

**R7.** Under "## 2. Directory Taxonomy (Keyword-Driven Organization)", bullet `wrangling/`
- Now: "- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources."
- New: "- `wrangling/`: Defines all Transformation (`tier1`, `tier2`) operations for individual data sources, one file per tier; a tier file holds `steps` (and an optional `data_engine`) and is included as `tier1: !include <file>`."
- Kind: a sentence that states a rule differently (a change of meaning)

**R8.** Same section, bullet `join/`
- Now: "- `join/`: Defines the join steps (`steps:` key only) for joining multiple ingredients into a collection. One file per join block (e.g., `AMR_Profile_Joint.yaml`). Top-level data analysis recipe key: `joins:`."
- New: "- `join/`: Defines the join steps (the `steps` of a tier, included as `tier1: !include <file>`) for joining multiple ingredients into a collection. One file per join block (e.g., `AMR_Profile_Joint.yaml`). Top-level data analysis recipe key: `joins:`."
- Kind: a sentence that states a rule differently (a change of meaning)

**R9.** Same section, bullet `plots/`
- Now: "- `plots/`: Contains visualization specifications for `analysis_groups`. Each file contains a single `spec:` block."
- New: "- `plots/`: Contains the plot entries of `analysis_groups` that are written in their own file. Each file contains the whole plot entry (there is no `spec:` key)."
- Kind: a sentence that states a rule differently (a change of meaning)

**R10.** Under "## 7. Canonical steps syntax (STRICT — No Shorthand)", first example ("### Canonical (ONLY valid format)"; the heading in the file has a check-mark emoji, left out here)
- Now: `steps:` / `  - action: cast` / ... (the 4 steps, indented)
- New: `tier1:` / `  steps:` / `    - action: cast` / ... (the same 4 steps, indented two more)
- Kind: only the example YAML follows the new shape

**R11.** Under "## 8. `analysis_groups` Structure (Data analysis recipe-Driven Home Theater)", first example, group entry
- Now: `    label: "Human-readable group name"`
- New: `    ui_label: "Human-readable group name"`
- Kind: a key or word renamed

**R12.** Same example, plot entry
- Now: `        label: "Human-readable plot name"` / `        spec: !include <basename>/<subdir>/<plot_id>.yaml`
- New: `        ui_label: "Human-readable plot name"` / `        # the plot content is written here (target_dataset, mapping, layers, ...), or the WHOLE entry is in a file:` / `      <other_plot_id>: !include <basename>/<subdir>/<other_plot_id>.yaml`
- Kind: only the example YAML follows the new shape

**R13.** Same section, rules list, first bullet
- Now: "- Each `spec: !include` points to a file in `plots/` subdirectory."
- New: "- Each plot entry written as `!include` points to a file in `plots/` subdirectory."
- Kind: a key or word renamed

**R14.** Same section, rules list, second bullet
- Now: "- The included plot file must contain a single `spec:` root key. `ConfigManager` auto-unnests it."
- New: "- The included plot file holds the whole plot entry (`ui_label`, `target_dataset`, `mapping`, `layers`, ...) and no wrapper key; there is no `spec:` key."
- Kind: a sentence that states a rule differently (a change of meaning)

**R15.** Under "### Visible labels (icons & emoji are encouraged)", the example group entry (the cat emoji in the file is written here as "[cat emoji]")
- Now: `    label: "[cat emoji] Cat"                    # ← Tab shows "[cat emoji] Cat"`
- New: `    ui_label: "[cat emoji] Cat"                 # ← Tab shows "[cat emoji] Cat"`
- Kind: a key or word renamed

**R16.** Same example, plot entry (the example has 9 lines; 8 shown)
- Now: `      miaou:                           # plot_id stays snake_case (unique-id contract)` / `        label: "Miaou [cat emoji]"              # ← Tab shows "Miaou [cat emoji]"` / `        spec: !include cat/miaou.yaml`
- New: `      miaou: !include cat/miaou.yaml   # plot_id stays snake_case (unique-id contract); the file holds the whole entry, e.g. ui_label: "Miaou [cat emoji]" (Tab shows "Miaou [cat emoji]")`
- Kind: only the example YAML follows the new shape

**R17.** Under "### Plot spec file structure (`plots/<plot_id>.yaml`)", the plot example (26 lines; the first 8 of the new block are shown)
- Now: `spec:` / `  target_dataset: <join_id>      # Must match a joins key` / `  mapping:` / `    x: <column> ...` (the old example with the `spec:` wrapper)
- New: `ui_label: "Plot name"            # Required — the short name of the tab` / `ui_title: "Plot Title"           # Optional — the longer name the report uses (else ui_label)` / `target_dataset: <join_id>        # Must match a joins key` / `mapping:` / ... (the example without the wrapper; the `ui_title:` key is new)
- Kind: only the example YAML follows the new shape (it also adds the new key `ui_title:`)

**R18.** Under "## 10. `plot_defaults` Block (ADR-081, BP-COLOR-3, VIZFAC-PLOT-CASCADE-1)", first paragraph
- Now: "...Individual plot specs may override any key. `plot_defaults` participates as **L2** in the five-tier resolution cascade (L5 T3 override > L4 spec > L3 optimisation > L2 plot_defaults > L1 built-ins)..."
- New: "...Individual plot specs may override any key. `plot_defaults` participates as **L2** in the five-tier resolution cascade (L5 T3 override > L4 plot entry > L3 optimisation > L2 plot_defaults > L1 built-ins)..."
- Kind: a key or word renamed

**R19.** Under "### 10a. Allowed keys (authoritative — extend by ADR amendment only)", the yaml block: the lines removed
- Now (removed): `  default_font_family: "Liberation Sans"  # plotnine default font family` / (blank) / `  # Layout` / `  facet_panel_spacing: 0.1    # float 0–1; plotnine default 0.05; increase for dense facets` / `  legend_position:     "right" # "right" | "top" | "bottom" | "left" | "none"` / (blank) / `  # Optimisation toggles (reserved — disabled by default except auto_axis_text)` / `  optimisation:` / `    auto_axis_text: true   # auto-rotate axis labels when text is long (default true)` / `    density_jitter: false  # jitter geom_point on dense scatter (default false)` / `    panel_spacing:  false  # auto-adjust facet panel spacing (default false)` / `    legend_ncol:    false  # auto-set legend column count (default false)`
- New: (nothing in their place)
- Kind: removed

**R20.** Same yaml block: the two lines added
- Now: (nothing in their place)
- New: `  layers:              []                 # layers added to every plot (a theme layer sets font, legend position, panel spacing)` / `  random_state:        0                  # the one seed of the random layers of the recipe`
- Kind: added

**R21.** Same section, the paragraph after the yaml block (new paragraph)
- Now: (none)
- New: "**Removed keys (D-0220, D-0242, 2026-11-17):** `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` did nothing and are not keys of `plot_defaults`. Font, legend position and panel spacing are set through a theme layer in `layers:`; the automatic axis-text adjustment has no switch of its own: an `element_text` layer for an axis overrides it."
- Kind: added

**R22.** Same section, the "Unknown key warning" paragraph
- Now: "**Unknown key warning:** keys not in the list above emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`. Non-fatal — experimental keys are allowed — but the warning prevents silent typos."
- New: the same text, followed by: "Each of the four removed keys is refused with a tombstone text (PD02)." (PD02 is a check code of the recipe checker: the refusal text of a removed key.)
- Kind: added (the warning sentence is unchanged; the last sentence is new)

**R23.** Under "### 10c. `theme` key", first bullet list item
- Now: "- Per-plot `theme:` in the spec overrides this default (L4 wins over L2)."
- New: "- Per-plot `theme:` in the plot entry overrides this default (L4 wins over L2)."
- Kind: a key or word renamed

**R24.** Same section, new bullet
- Now: (none)
- New: "- With no theme in the data analysis recipe, a plot is drawn with plotnine's own default (`theme_gray`): the app injects no theme (D-0258)."
- Kind: added

## Rule file 3: `.claude/rules/rules_data_engine.md` (9 passages)

**R25.** Top of the file, front matter ("documents:")
- Now: `  documents: [libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/actions/]`
- New: `  documents: [libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/actions/, libs/transformer/src/transformer/engine_python_polars.py, app/modules/cache_keys.py, app/modules/engine_registry.py]`
- Kind: added

**R26.** Under "### Tier 1 (The Trunk): Relational Anchor", the "Cache key" bullet
- Now: "- **Cache key:** the Tier 1 parquet is valid only while its `tier1_key` matches (resolved data analysis recipe minus downstream-only parts, plus data hash and engine version; ADR-089). Never reuse an anchor by file name alone."
- New: "- **Cache key:** the Tier 1 parquet is valid only while its `tier1_key` matches (resolved data analysis recipe minus downstream-only parts, plus data hash, engine version and the effective data engine of every table and join; ADR-089). A key contains the engine of what it stores and nothing else: the engine is an argument of the key function, and the plot engine is in no table key (D-0240). Never reuse an anchor by file name alone."
- Kind: a sentence that states a rule differently (a change of meaning)

**R27.** Under "### Tier 2 (The Branch): Plot-Specific Anchor", the "Persistence" bullet
- Now: "...keyed by the chained `tier2_key` (ADR-089); an empty `tier2` means..."
- New: "...keyed by the chained `tier2_key`, which takes the effective data engine of that tier 2 as an argument (ADR-089, D-0240); an empty `tier2` means..." (rest of the bullet unchanged)
- Kind: a sentence that states a rule differently (a change of meaning)

**R28.** Under "## 3. The Tiered Data Analysis Recipe Mandate (ADR-024)", first paragraph
- Now: "To ensure consistency across the 3-Tier Lifecycle, all `wrangling` blocks in YAML data analysis recipes MUST adopt the tiered nesting structure."
- New: "To ensure consistency across the 3-Tier Lifecycle, the tiers of every table and join in YAML data analysis recipes MUST be written as keys of their own (`tier1`, `tier2`), each a mapping with an optional `data_engine` (first key) and `steps`."
- Kind: a sentence that states a rule differently (a change of meaning)

**R29.** Same section, "### Structure Requirement", the `tier1` bullet
- Now: "- **`tier1`**: Required (even if empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. MUST be a Sequential List of actions."
- New: "- **`tier1`**: Required (even if its `steps` are empty). Contains relational foundations (cleaning, joining, column renaming). This is the shared "Trunk" of the data tree. Its `steps` MUST be a Sequential List of actions."
- Kind: a sentence that states a rule differently (a change of meaning)

**R30.** Same section, the `tier2` bullet
- Now: "- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". MUST be a Sequential List of actions."
- New: "- **`tier2`**: Optional. Contains plot-specific transformations (aggregations, reshaping to long format, specific subsetting). This is the "Branch". Its `steps` MUST be a Sequential List of actions."
- Kind: a sentence that states a rule differently (a change of meaning)

**R31.** Same section, new bullet
- Now: (none)
- New: "- **`data_engine`**: Optional, the first key of a tier. The engine that runs the tier; without it the `data_engine` at the top of the data analysis recipe applies. The list of engine names is open: a new name ships with an app release, and an app without its library refuses the value with "no library for this engine in this app" (D-0239)."
- Kind: added

**R32.** Same section, the yaml example (7 lines in the new block; all shown)
- Now: `wrangling:` / `  tier1: [ ...ordered actions... ]` / `  tier2: [ ...ordered actions... ] # Optional: skipped via Identity Logic if omitted`
- New: `tier1:` / `  steps: [ ...ordered actions... ]` / `tier2:                               # Optional: skipped via Identity Logic if omitted` / `  steps: [ ...ordered actions... ]`
- Kind: only the example YAML follows the new shape

**R33.** Under "### Flat List Rejection (LEGACY-FLAT-WRANGLING-1, Phase 34)"
- Now: "The engine rejects flat `wrangling:` lists with a `DataAnalysisRecipeError`. All data analysis recipes must use the tiered structure. If a legacy data analysis recipe is encountered with a flat list, migrate it before running."
- New: "The engine rejects a tier written as a flat list, and the old container `wrangling:`, with a `DataAnalysisRecipeError`. All data analysis recipes must use the tiered structure. If a legacy data analysis recipe is encountered with a flat list, migrate it before running."
- Kind: a sentence that states a rule differently (a change of meaning)

## Rule file 4: `.claude/rules/rules_gallery_standards.md` (2 passages)

**R34.** Under "## 4. VizFactory Layer Format", the "Correct:" example (the new block is 11 lines; 8 shown)
- Now: `plots:` / `  my_plot:` / `    mapping:` / `      x: column_a` / `      y: column_b` / `    layers:` / `      - name: geom_point`
- New: `analysis_groups:` / `  example:` / `    ui_label: Example` / `    plots:` / `      my_plot:` / `        ui_label: My plot      # the plot entry holds the content directly: there is no `spec:` key` / `        mapping:` / `          x: column_a` (3 lines left out: `y:`, `layers:`, `- name: geom_point`, shifted two levels deeper)
- Kind: only the example YAML follows the new shape

**R35.** Same section, the "Wrong (both errors):" example (new block 13 lines; 8 shown)
- Now: `plots:` / `  my_plot:` / `    layers:` / `      - geom: geom_point        # ← wrong key` / `        mapping: {x: column_a}  # ← mapping belongs at plot level`
- New: `analysis_groups:` / `  example:` / `    ui_label: Example` / `    plots:` / `      my_plot:` / `        ui_label: My plot` / `        layers:` / `          - geom: geom_point        # ← wrong key` (5 lines left out, the last being the `mapping:` line that is still present one level deeper)
- Kind: only the example YAML follows the new shape

## Rule file 5: `.claude/rules/rules_test_lab.md` (1 passage)

**R36.** Under "### 4a. What the Bootstrapper generates", table row
- Now: "| `wrangling: tier1: []` / `tier2: []` stubs | Yes | Empty stubs only |"
- New: "| `tier1:` (an `!include` of a file that holds `steps`; a tier is its own key) | Yes | Empty `steps` stub only; no `tier2` (an absent tier 2 means T2 equals T1) |"
- Kind: a sentence that states a rule differently (a change of meaning: no `tier2` stub is written)

## Rule file 6: `.claude/rules/rules_viz_factory.md` (9 passages)

**R37.** Top of the file, front matter ("documents:")
- Now: `  documents: [libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/geoms/core.py, libs/viz_factory/src/viz_factory/themes/core.py, libs/viz_factory/src/viz_factory/registry.py]`
- New: the same list with `, libs/viz_factory/src/viz_factory/engine_python_plotnine.py, libs/viz_factory/src/viz_factory/plot_config_resolver.py` added at the end
- Kind: added

**R38.** Under "### 6b. Data analysis recipe keys", yaml comment
- Now: "# Per-plot override (inside analysis_groups plot spec):"
- New: "# Per-plot override (in the plot entry of analysis_groups):"
- Kind: a key or word renamed

**R39.** Same section, paragraph after "Resolution order"
- Now: "`palette` is one of several `plot_defaults` keys. The authoritative schema (palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation toggles) is documented at `rules_data_analysis_recipe_structure.md §10`. Unknown keys emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`."
- New: "`palette` is one of several `plot_defaults` keys. The authoritative schema (palette, theme, layers, random_state) is documented at `rules_data_analysis_recipe_structure.md §10`. `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` were removed (D-0220, D-0242). Unknown keys emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`. A removed key is refused with a tombstone text (PD02)."
- Kind: a sentence that states a rule differently (a change of meaning: removed keys, refusal text)

**R40.** Under "## 7. Plot Configuration Cascade (designed 2026-05-10, VIZFAC-PLOT-CASCADE-1)", the tier table, row L4
- Now: "| **L4** | Plot `spec:` (`analysis_groups.<grp>.plots.<id>.spec`) | Data analysis recipe author |"
- New: "| **L4** | The plot entry (`analysis_groups.<grp>.plots.<id>`; the entry has no `spec:` key) | Data analysis recipe author |"
- Kind: a key or word renamed

**R41.** Same table, row L3
- Now: "| **L3** | Optimisation layer (computed from data + spec) — **visual/aesthetic only** | None — emitted by VizFactory |"
- New: "| **L3** | Optimisation layer (computed from data + the plot entry) — **visual/aesthetic only** | None — emitted by VizFactory |"
- Kind: a key or word renamed

**R42.** Same table, row L1
- Now: "| **L1** | VizFactory built-in defaults | Developer |"
- New: "| **L1** | VizFactory built-in defaults (`coord_cartesian`, `facet_null`; no theme: a plot with no theme written is drawn with plotnine's own default, `theme_gray`, D-0258) | Developer |"
- Kind: a sentence that states a rule differently (a change of meaning: no theme is injected)

**R43.** Same section, bullet "Names in the cascade"
- Now: "- **Names in the cascade (DECIDED, not built, D-0218)**: the `theme:` key of a plot spec and of `plot_defaults` changes, because it is a component call (D-0214)."
- New: "- **Names in the cascade (DECIDED, not built, D-0218)**: the `theme:` key of a plot entry and of `plot_defaults` changes, because it is a component call (D-0214)." (the rest of the bullet is unchanged)
- Kind: a key or word renamed

**R44.** Same section, bullet "Unknown keys in `plot_defaults`"
- Now: "...per ADR-079. Non-fatal."
- New: "...per ADR-079. Non-fatal. The four removed keys are refused with a tombstone text (PD02)."
- Kind: added

**R45.** Same section, new bullet "The engine (D-0238, D-0239)"
- Now: (none)
- New: "- **The engine (D-0238, D-0239):** the engine of a component is a field of its registry entry (`python-plotnine` for every component today); the plot library is chosen by the `plot_engine` of the plot entry, else of the data analysis recipe; an engine the app has no library for is refused with "no library for this engine in this app". The plot engine is in no table cache key (D-0240)."
- Kind: added

## Final list: the passages to read first (kind "states a rule differently", "removed", "added", or "unsure")

- States a rule differently (13): R7, R8, R9, R14, R26, R27, R28, R29, R30, R33, R36, R39, R42.
- Removed (1): R19.
- Added (10): R6, R20, R21, R22, R24, R25, R31, R37, R44, R45.
- Unsure (0): none. Every passage has a kind.

## Counts

- Changed blocks (`@@` lines) in the diff: 21. Passages covering them: bioscientist 4 blocks (R1 to R5), structure 9 (R6 to R24), data engine 3 (R25 to R33), gallery 1 (R34, R35), test lab 1 (R36), viz factory 3 (R37 to R45). All 21 blocks are covered.
- Passages per file: 5, 19, 9, 2, 1, 9. Total 45.
- Per kind: only the example YAML follows the new shape: R1, R2, R3, R5, R10, R12, R16, R17, R32, R34, R35 (11). A key or word renamed: R4, R11, R13, R15, R18, R23, R38, R40, R41, R43 (10). A sentence that states a rule differently: R7, R8, R9, R14, R26, R27, R28, R29, R30, R33, R36, R39, R42 (13). Removed: R19 (1). Added: R6, R20, R21, R22, R24, R25, R31, R37, R44, R45 (10). Unsure: 0. Total 45.

## Not classified

- Nothing in the diff could not be classified.
- Two points for you, not judgements: the label-to-`ui_label` passages (R4, R11, R12, R15, R16, R17) and the `ui_title:` key in R17 are not named in D-0249's list; RULE_PASSAGES item 1 covers them. The sentence "Each of the four removed keys is refused..." (R22, R44) follows RULE_PASSAGES item 3, which waits for you.
