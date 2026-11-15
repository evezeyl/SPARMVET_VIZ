# Proposal: `.claude/rules/ui_implementation_contract.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. The filter row (line 279) was already changed on 2026-11-15 (commits `f8636ff4`, `22a0dc14`); this proposal checks the rest of the file.
Checked against: ADR-098 (BUILT 2026-11-11, `architecture_decisions.md:5013-5036`), ADR-099/105 (target, NOT BUILT: stage 2), ADR-103, ADR-104 point 4, ADR-100 point 5, `tasks.md:49` (OPERATORS-SCREENS-1 open), `libs/viz_factory/src/viz_factory/viz_factory.py:195-196` (`between` with `closed`).
Principle used: this file describes what the app does (built) plus what Eve decided as target when marked. I mark target-only statements as such and correct what the built code or an accepted ADR contradicts.

## 1. Section 4, lines 95-99, "T1/T2 tier isolation invariant" (FACT; contradicted by ADR-098)

Today (lines 95-99): `**ADR-085 ... T1/T2 tier isolation invariant.** T1 and T2 are permanently pure in every configuration: no exploration filter (applied_filters) and no audit-committed node ... may ever render there. Both are only applied when tier_toggle.get() == "T3". ...`
Proposed:
```
**Tier isolation (ADR-085, narrowed by ADR-098, 2026-11-11):** audit-committed nodes (`_t3_filter_rows()`/`_t3_drop_columns()`) are applied only on "My view" (and the right pane of Compare). Exploration filters (`applied_filters`) change the data TABLE on every view (Raw, Result, My view) and the PLOTS only on My view; they are never written to Parquet and never exported. The plots of Raw and Result are the recipe's plots. Any new render function that reads either MUST apply the same gate; see `app/handlers/home_theater.py` `_group_plot_handler` / `home_data_preview` for the reference pattern.
```
Why: the banner at line 93 already says this for the table at line 88; lines 95-99 contradict it. ADR-098 decision 1 and 2 ("Supersedes: ADR-085 decision 1 ... for exploration filters").

## 2. Section 8, lines 262-264 and 268-273 (FACT; same reason)

Today (lines 262-264): `Row filters ... They affect the "My view" (T3) plot and data preview only - T1 and T2 never reflect applied_filters or any T3 audit node (ADR-085 tier-isolation invariant, §4/§5 above).`
Proposed: `Row filters live in the left sidebar (Home mode only). They preview on every data view and on the "My view" plot only (ADR-098); T1 and T2 plots never reflect them, and no audit node shows outside "My view" (section 4).`
Today (lines 268-269): `applied_filters: committed ... Consumed by @render.plot handlers and home_data_preview, but only when tier_toggle.get() == "T3" ("My view").`
Proposed: `applied_filters: committed ... Consumed by home_data_preview on every view and by @render.plot handlers on "My view" only (ADR-098).`
Today (line 273): `Renders on every tier's button bar, but only has a visible effect on "My view" per the tier-isolation invariant.`
Proposed: `Renders on every tier's button bar; it changes the table on every view and the plot on "My view" (ADR-098).`

## 3. Section 8, line 279 and the lines after it (FACT; a TARGET point marked)

Line 279 is current for what is built. Two additions:
- After the sentence on `closed` (line 279): `**[Decided 2026-11-14 (ADR-104 point 4), NOT BUILT (OPERATORS-SCREENS-1): HOME offers the four values \`both\`, \`left\`, \`right\`, \`none\` of \`closed\`, and the export carries all of them. Today only \`both\` and \`none\` are offered.]**`
- Today (line 286): `... VizFactory supports: eq, ne, gt, ge, lt, le, in, not_in.`
  Proposed: `... VizFactory supports: eq, ne, gt, ge, lt, le, in, not_in, between (with closed; viz_factory.py:195).`
Why: `viz_factory.py:195-196` handles `between`; `rules_viz_factory.md` section 4 already lists it.
- Lines 281-282 ("Ops for discrete columns", "Ops for numeric columns"): ADR-104 point 4 says comparisons on text and dates are to be offered (task OPERATORS-SCREENS-1, not built). Add after them: `**[Target, NOT BUILT (ADR-104 point 4): every operator the engine has is usable from the screens, including comparisons on text and dates and Boolean filters.]**`

## 4. Section 12 (lines 446-449) banner (FACT, small)
Line 449 says the plain exploration layer "is available in 'My view' even without `t3_sandbox_enabled`". After ADR-098 it also acts on the data tables of every view. Add: `(and on the data tables of every view, ADR-098)`.

## 5. Section 12g, "Per-Plot Audit Scoping & Join-Key Propagation" (lines 652-780 region) (CHANGES A RULE as a marker; target NOT BUILT)

Today: the section is the active rule: per-plot stacks, a propagation dialog with "This plot only / All plots / All plots except", `plot_scope`, linked ids.
Proposed: add this banner directly under the section heading, and change nothing else until stage 2 is built:
```
> **TO BE REPLACED (ADR-105, 2026-11-12, confirmed 2026-11-14; ADR-099 point 4 superseded):** the propagation dialog ("this plot / all plots / all except") and `plot_scope` are replaced by the user ticking, from a list, every node of the lineage where the field exists; the only automatic placement is "remove these entities from all tables". Steps are written at T1 or T2 of a table or at T3 of a plot. **NOT BUILT** (STAGE2-SPEC-1, RECIPE-GRAPH-UTILS-1): until it is, the code does what this section says.
```
Why: ADR-105 "Supersedes ... ADR-098 points 7 and 8 ...; ADR-049 (propagation dialog, `plot_scope`)"; NOT BUILT. No deletion: the section stays active.

## 6. Section 12g.2, lines 680-691, YAML example (FACT)

Today: the `joins:` example with `action: join`, `on: sample_id`, `on: [sample_id, gene_id]` (unquoted `on`).
Proposed:
```yaml
joins:
  bigtable:
    steps:
      tier1:
        - action: polars_join
          right_ingredient: other
          'on': [sample_id]            # -> {sample_id} added
          how: inner
          maintain_order: left_right
        - action: polars_join
          right_ingredient: third
          left_on: [sample_id]
          right_on: [sample_id]        # -> already in set
          how: inner
          maintain_order: left_right
        - action: polars_join
          right_ingredient: fourth
          'on': [sample_id, gene_id]   # -> {sample_id, gene_id} added
          how: inner
          maintain_order: left_right
```
Why: `join` is not a registered action (`polars_join` is); an unquoted `on` is refused (check T07); `steps` holds `tier1` (S07/J07; shipped `AMR_Profile_Joint.yaml`).

## 7. Section 7.2 and 12d, keys (no change now)
The export key check (7.2 rule 1, 5) and the session key (12d) use the ADR-089 model. ADR-101 replaces it (NOT BUILT, KEYS-NODE-1). Leave until built; same marker as in `rules_data_engine.md.proposal.md` change 2 if Eve wants one.

## 8. Section 12e (no change)
Already carries a REMOVED banner (ADR-093) with the legacy marker; its tombstone expiry is not stated ("kept only so a reader ... understands"); add "Tombstone expires" is a legacy-rule question, listed as not settled.

## Not settled
1. Section 12e has a REMOVED banner without "Tombstone expires".
2. Whether section 12a ("BLUEPRINT never authors T3" via ADR-082 point 4, in the header of 12a and in `rules_ui_dashboard.md`) holds: ADR-100 OPEN list ("Whether Blueprint may author a plot entry's tier 3"). No text proposed.
3. Whether "My view" / "Compare" wording (ADR-086) stays after ADR-099/105 are built; target replaces it, nothing built, no change proposed.
