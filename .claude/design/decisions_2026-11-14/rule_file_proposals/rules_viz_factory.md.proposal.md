# Proposal: `.claude/rules/rules_viz_factory.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Checked against: ADR-106 (V1 to V10, decided 2026-11-14), ADR-104 points 1, 3, 4 and 7, `viz_plan_for_eve.md` section 5, the seed builder's proposed lines
(`.claude/worktrees/seed-holds/tmpAI/progress.md`, main tree, "Proposed rule lines"), `libs/viz_factory/tests/test_data` (194 old-form recipes),
`recipe_check.py` PD01 (plot_defaults unknown keys fail). Newer fact from the coordinator: on branch `task/viz-field-engine` (NOT merged) the components carry a field `plotnine` (exact 125, modified 44, own 22) and twelve components lost a parameter plotnine refuses.

## 1. Lines 4, 11, 13-19, the Artist Parity Mandate (CHANGES A RULE; approved by Eve as V9)

Today (lines 4, 11, 13-19): `provides: [... rule:plotnine_parity ...]`; `**Authority:** Defines the Artist Pillar standards and Plotnine parity requirements.`; heading `## 1. The Artist Parity Mandate (ADR-036)`; "MUST maintain 1:1 Functional Parity"; Parity Rule "MUST have a corresponding registration"; Maintenance; Verification.

Proposed:
- line 4: `rule:plotnine_components` instead of `rule:plotnine_parity` (run `build_dep_graph.py`).
- line 11: `**Authority:** Defines the Artist Pillar standards: how the visualisation library follows the recipe standard.`
- section 1 replaced by:
```
## 1. The Visualisation Library Follows the Recipe Standard (ADR-106)

> **REPLACED (ADR-106 V9, 2026-11-14):** the "Artist Parity Mandate (ADR-036)" ("1:1 Functional Parity ... MUST") is withdrawn. ADR-036 is the ID sanitation pivot and holds no parity decision; the text existed only in this file (commit `342f7980`, 2026-04-17).

- **Exact, modified, own (V1, V2).** Each component carries a field that says whether it equals the plotnine call (`exact`), states a change (`modified`) or has its own logic (`own`). The help and the checker show it; no component is renamed. An `exact` component equals the direct plotnine call, proved by a test for each; a `modified` one states its change.
- **What is registered is exact; what is missing is listed.** No parity "MUST": plotnine objects that have no component are listed, and a test reports new plotnine objects at an upgrade (V9). Both spellings `color` and `colour` are accepted.
- **Parameters (V3, V4).** Parameter lists are read from plotnine (a compare test first, then reading from plotnine with a hand overlay for descriptions and choices); one strict rule set for layer parameters (unknown, required, shape, allowed values) is shared with the data steps and used by the checker and the engine.
- **No silent path (V5, V6, V7, V8; ADR-104 point 1).** HOME runs the same full check as the gallery. A silent path is an error: one error form ("what, which plot and layer, how to fix"). The factory refuses a plot engine it does not implement; the export records the plotnine version.
- **Verification.** A component is verified by its own test (section 3), not by a count of parity.
```
Why: ADR-106 "Replaces", V1 to V10, "Eve approved the rule-file change with V9". Status of the build (checked 2026-11-15): merged: V5 (`70b01370`); V1 and V8 (`4525fcb1`: the field `plotnine: exact | modified | own` and the engine check). Not built: V2, V3, V4, V6, V7, V9, V10. The bullets are the rule, not the build: do not paste them as "done". If Eve prefers, paste the first three bullets now and the rest as each V is built.

## 2. Section 3, lines 26-32, the 1:1:1 Evidence Loop (CHANGES A RULE)

Today: three items: a YAML recipe in `tests/test_data/`; a TSV; "A Rendered PNG: Materialized during the `viz_factory_integrity_suite.py` execution."
Proposed:
```
## 3. The Evidence Loop (Testing)

No visual component is considered verified without a test of its own, driven by the registry:

1. **The component's YAML example** (its `yaml_example` in the registry) becomes a small generated recipe in format 1 (ADR-106 V10).
2. **A dataset** that provides the minimum required aesthetics.
3. **A render** that succeeds, and for an `exact` component equals the direct plotnine call (V2).

> **TO BE REMOVED (V10, decided 2026-11-14, not built):** the 194 test recipes in `libs/viz_factory/tests/test_data/` (old recipe form) and the dead `viz_factory_integrity_suite.py` still exist on disk until V10 is built.
> Replacement: tests driven by the registry (VIZ-STANDARD-1).
> **Tombstone expires:** two phases after this edit.
```
Why: ADR-106 V10; the 194 recipes hold no `spec_version` (checked 2026-11-15). The tombstone needs a removal task in `tasks.md` (VIZ-STANDARD-1 exists).

## 3. Section 4, the filter contract (CHANGES A RULE; part is NOT BUILT)

Today (about lines 34-45): `Authoritative op list: eq, ne, gt, ge, lt, le, in, not_in, between`; `in`/`not_in` compare as text.
Proposed: add: `An unknown operator or an unknown column is an error with a plain message, never "all rows are drawn" (ADR-104 point 1, ADR-106 V6). \`between\` has four \`closed\` values (\`both\`, \`left\`, \`right\`, \`none\`) (ADR-104 point 4). A filter states its missing-value choice (\`na\`, ADR-103): the filter uses \`modif_filter\` (plan section 7 step 6).`
Kind: CHANGES A RULE. Not built: both silent paths are open until the plot uses `modif_filter` (ADR-106 V6 correction note). Not settled: whether the viz `filters` key itself carries `na` (not verified in `viz_factory.py`).

## 4. Line 110, unknown keys in `plot_defaults` (CHANGES A RULE)

Today: `Unknown keys in plot_defaults emit PipelineError(severity: warning ...) per ADR-079. Non-fatal.`
Proposed: `Unknown keys in plot_defaults fail the checker (PD01, DEC02, ADR-100 point 2).`
Why: `recipe_check.py` (code PD01).

## 5. Section 8, the seed (lines 115-124) (CHANGES A RULE; one point OPEN)

The seed builder's two proposed lines (seed-holds progress note, "Proposed rule lines"), adapted:
- Today (line 120): `- A layer sets its own with \`random_state\` ...; a seed set on the layer wins over the factory's.`
  Proposed: `- A layer sets its own with \`random_state\`; a seed set on the layer wins over the factory's. A seed written in the recipe HOLDS in every view (HOME, results bundle, reproducibility export, gallery); no caller replaces it (ADR-104 point 3, R4).`
- Add after the `random_state: null` bullet (line 123):
  `- Order of precedence, one function (\`plot_config_resolver.resolve_plot_seed\`): a seed pinned by an audit step (L5) > the number written in the recipe > the seed the caller offers when the recipe writes none or null (\`render(..., fallback_random_state=n)\`; HOME draws one per session and plot) > the factory default. The export renders with the seed HOME showed, records the seed it really used (\`seeds_per_plot\`, \`seed_source_per_plot\` in \`effective_run.yaml\`) and writes it into the reproducibility recipe.`
- Line 119 (`DEFAULT_RANDOM_STATE = 0`): OPEN, awaiting Eve (see below).
- Heading `(ADR-090)` becomes `(ADR-090, ADR-104 point 3)`.
Why: ADR-104 point 3 (decided 2026-11-14); `adr_sync_changes.md` section 5 ("default seed 0 is OPEN; a recipe seed holds, ADR-104"). The text is for branch `task/seed-holds` (6 to 7 commits, all mutations caught; not merged at my last read): paste only after the merge. The names `plot_config_resolver.resolve_plot_seed` and `fallback_random_state` exist only on that branch (not found in `libs/viz_factory/src` on 2026-11-15): names to be checked again after the merge.
OPEN, awaiting Eve (records say so): which seed is used when the recipe writes none, HOME's per-session draw (what the code does) or the default 0.

## Not settled
1. The OPEN seed point above.
2. Whether `viz_factory.py` `filters` carries `na` (change 3).
3. Change 1: how much to paste before V2, V3, V4, V6, V7, V9 and V10 are built (V1, V5 and V8 are merged).
