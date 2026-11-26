These rule sentences are out of date since the merge of the recipe change; do not follow them blindly; the code and `recipe_format_spec.md` are right until the rule text is changed with the owner's yes.

Source of the list: `tmpAI/engine_keys/RULE_SENTENCES_for_eve_2026-11-19.md` (R1 to R45); the held-back text is in `tmpAI/engine_keys/RULE_FILES_branch_vs_dev_FINAL.diff`. One line each: rule file, section, what the rule says now (old), what the code does (new).

## rules_agent_role_bioscientist.md
- R1, 3-A: example shows `wrangling:` with `tier1:` / `tier2:` inside; code: `tier1:` and `tier2:` are keys of their own, each with `steps:`; no `wrangling:` container.
- R2, 3-B: assembly example starts with `steps:`; code: a join's tier is `tier1:` with `steps:` (file included as `tier1: !include <file>`).
- R3, 3-C: plot example wrapped in `spec:`; code: no `spec:` key; the plot entry holds `ui_label`, `target_dataset`, `mapping`, `layers` directly.
- R4, 3-D: group key `label:`; code: `ui_label:`.
- R5, 3-D: plot entry has `label:` and `spec: !include`; code: `plot_id: !include <file>`, the file holds the whole entry with `ui_label`.

## rules_data_analysis_recipe_structure.md
- R6, front matter: `documents:` lacks `recipe_spec.yaml` and `recipe_check.py`.
- R7, section 2, `wrangling/`: says tier1/tier2 operations; code: one file per tier holding `steps` (optional `data_engine`), included as `tier1: !include <file>`.
- R8, section 2, `join/`: says `steps:` key only; code: the `steps` of a tier, included as `tier1: !include <file>`.
- R9, section 2, `plots/`: says each file holds a single `spec:` block; code: the whole plot entry, no `spec:`.
- R10, section 7: canonical example shows bare `steps:`; code: `tier1:` then `steps:`.
- R11, section 8: group `label:`; code: `ui_label:`.
- R12, section 8: plot entry `label:` + `spec: !include`; code: `ui_label` in the entry, or the whole entry `!include`d.
- R13, section 8 rules: "each `spec: !include` points to a file in plots/"; code: each plot entry written as `!include`.
- R14, section 8 rules: included plot file must have a single `spec:` root key, auto-unnested; code: whole entry, no wrapper, no `spec:`.
- R15, section 8 labels: example group `label:`; code: `ui_label:`.
- R16, section 8 labels: example plot `label:` + `spec: !include`; code: `plot_id: !include`, `ui_label` inside the file.
- R17, plot spec file structure: example starts with `spec:`; code: no wrapper; `ui_label` required, `ui_title` optional (new key).
- R18, section 10: cascade says "L4 spec"; code: L4 is the plot entry.
- R19, 10a: lists `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation` as allowed; code: removed keys (D-0220, D-0242).
- R20, 10a: no `layers` / `random_state` in plot_defaults; code: both exist.
- R21, 10a: no word on the removed keys; code: they are refused with a tombstone text.
- R22, 10a unknown key warning: no word on PD02; code: the four removed keys are refused with the tombstone (PD02).
- R23, 10c: "per-plot theme in the spec"; code: in the plot entry.
- R24, 10c: no word on the default; code: no theme in the recipe means plotnine's `theme_gray`, the app injects none (D-0258).

## rules_data_engine.md
- R25, front matter: `documents:` lacks `engine_python_polars.py`, `cache_keys.py`, `engine_registry.py`.
- R26, Tier 1 cache key: no engine in the key; code: effective data engine of every table and join is in the key, engine is an argument of the key function, plot engine in no table key (D-0240).
- R27, Tier 2 persistence: `tier2_key` without engine; code: it takes the effective engine of that tier 2.
- R28, section 3: says `wrangling` blocks adopt tiered nesting; code: tiers are keys of their own, each a mapping with optional `data_engine` and `steps`.
- R29, section 3, tier1: "MUST be a Sequential List"; code: its `steps` is the list.
- R30, section 3, tier2: same as R29.
- R31, section 3: no `data_engine` key described; code: optional first key of a tier; open engine names; an app without the library refuses (D-0239).
- R32, section 3 yaml: `wrangling:` with `tier1: [..]`; code: `tier1:` / `steps: [..]`, `tier2:` / `steps: [..]`.
- R33, Flat List Rejection: rejects flat `wrangling:` lists; code: rejects a tier written as a flat list and the old container `wrangling:`.

## rules_gallery_standards.md
- R34, section 4 "Correct": top-level `plots:` with `my_plot:` and mapping at that level; code: `analysis_groups` > group (`ui_label`) > `plots` > plot entry (`ui_label`, content directly), no `spec:`.
- R35, section 4 "Wrong": same shape change as R34.

## rules_test_lab.md
- R36, 4a: Bootstrapper writes `wrangling: tier1: []` / `tier2: []` stubs; code: `tier1:` as an `!include` of a file holding empty `steps`, no `tier2` stub (absent tier 2 means T2 equals T1).

## rules_viz_factory.md
- R37, front matter: `documents:` lacks `engine_python_plotnine.py`, `plot_config_resolver.py`.
- R38, 6b: "plot spec" comment; code: plot entry of `analysis_groups`.
- R39, 6b: schema lists default_font_family, facet_panel_spacing, legend_position, optimisation; code: palette, theme, layers, random_state; the four are removed and refused (PD02).
- R40, section 7 table L4: "Plot `spec:`"; code: the plot entry, no `spec:` key.
- R41, section 7 table L3: "data + spec"; code: data + the plot entry.
- R42, section 7 table L1: built-in defaults without detail; code: `coord_cartesian`, `facet_null`, no theme injected (D-0258).
- R43, section 7 names bullet: "plot spec"; code: plot entry.
- R44, section 7 unknown keys: no word on removed keys; code: refused with a tombstone text (PD02).
- R45, section 7: no word on the engine; code: engine is a field of a component's registry entry (`python-plotnine`), chosen by `plot_engine` of the plot entry else the recipe; an engine without a library is refused; the plot engine is in no table cache key (D-0238, D-0239, D-0240).
