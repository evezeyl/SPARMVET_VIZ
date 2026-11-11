# Recipe review (data scientist): 1_test_data_ST22_dummy

**Written for:** Eve and the next session. **Date:** 2026-11-11. **Method:** `.claude/workflows/design_review_personas.md`, persona 3
(data scientist): run every collection and every plot on the real test data, look at each picture, measure the joins, compare with an
independent computation. Rules: verified = run or read at file:line; reasoned = follows from verified facts, still needs a test.
**Scope not covered:** the numbers of `figshare_integration` and `stress_test_master` (only built and scanned); the Abromics recipe was scanned
and its joins measured, its plots were not looked at one by one.

## 1. Findings

| # | Finding | Evidence | Severity | Class | Issue | Status |
|---|---|---|---|---|---|---|
| 1 | `facet_by` inside `mapping:` gives no panels (documented as equivalent to `facet_wrap`; the Blueprint form writes it; six shipped plots use it). `miaou` pooled three metrics in one violin (false bimodal shape); the Quast boxplot put N50 and total length on one axis | verified: render with both spellings (`tmpAI/recipe_review/facet_check.py`), `plot_config_resolver.py:473,514`, pictures before/after | high (wrong figure) | software bug | #65 | recipe plots fixed with an explicit `facet_wrap`; code fix open |
| 2 | `facet_scales`, `labs`, `coordinate_flip` at the top of a plot spec are dropped without a message (`_meta`) | verified: axis titles of `phenotype_genome_length_fragmentation` stayed `phenotype_count`/`quality_value`; scan of all recipes | medium | guard rail | #66 | recipe plots fixed; warning open |
| 3 | `qc_reads_horizontal_barplot` mapped `x: total_reads, y: sample_id` with `geom_col`: thin vertical lines instead of bars | verified: picture before/after | high (unreadable figure) | recipe | #69 | fixed (`x: sample_id, y: total_reads`, `coord_flip`) |
| 4 | `ST22_Anchor` joins two long tables (ResFinder x VirulenceFinder): rows 42 -> 74 -> 1731 -> 617 (342 distinct sample/gene pairs). `virulence_count` is wrong for 18 of 42 samples (72 for a sample with 9 genes); `virulence_bar` bars are multiplied by the AMR gene count; `virulence_variants` colours by an AMR constant | verified: instrumented joins (`fanout.py`), `diagnose.py`, pictures | high (wrong numbers) | recipe + guard rail | #67, #68 | **waiting for Eve (what must the anchor answer?)** |
| 5 | Samples with only `unknown[...]` phenotypes get a resistance score of 0 (4 of 42); the 6 truly susceptible samples also 0 | verified: recomputed from the raw TSV and from the collection | medium (science) | recipe decision | #70 | **waiting for Eve** |
| 6 | 4 samples have no ResFinder row: they are absent from `amr_heatmap` (absence of evidence drawn as nothing) and show a grey "nan" band in `virulence_variants` | verified: 38 of 42 samples in ResFinder; 31 rows with null status | medium | practice / decision | #67 | follows the decision of #67 |
| 7 | The MLST and year plots show 33 of 42 samples because the demo tier-2 filter keeps 2023-2025; only the year plot says so in its title | verified: collection counts; recipe `MLST_Metadata_wrangling.yaml` | low (demo on purpose) | practice | - | left; say it in the demo or in the other title |
| 8 | `plot_defaults` had two keys the engine ignores (`height`, `show_legend`): a warning on every render | verified: warnings counted 2 per plot before, 0 after | low | recipe | #69 | fixed |
| 9 | `Detailed_summary` could not be built (`hsp_lengthtotal_length` declared categorical, wrangling needs a string) | verified: `SchemaError`, builds (91, 13) after the type fix | medium | recipe | #69 | fixed |
| 10 | `ST22_Anchor` contract: `phenotype` does not exist (engine message at build); `sample_id` declared numeric (rules: categorical key; data is a string) | verified: engine output; collection unchanged after the type fix | low | recipe | #69 | `sample_id` fixed; `phenotype` waits for #67 |
| 11 | Legacy top-level `wrangling:` with a `tier3` join at the end of the recipe | verified: nothing in the engine reads it; every collection byte-identical (hash) after removal | low | recipe | #69 | removed |
| 12 | `extract_primary_keys` returns `[]` (dict-shaped steps) and, once that is fixed, would take the `on:` of `unpivot` steps as join keys | verified: flat-list copy test (`pk_proof.py`) | high (safeguards dead) | software bug | #61 | open (WP2 of the brief, now with the unpivot test) |
| 13 | The recipe data check returned "no problems" while a schema could not be built; `test_render_every_plot` passes with ignored facets and fan-out | verified: baseline 75 passed with the broken schema | medium (checker blind spot) | software bug | #71 | `test_shipped_recipes_hygiene.py` added as guard; the check itself open |
| 14 | Unused material: ingredients `Quality_metrics`, `Detailed_summary`; collections no plot reads (`FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`); plot spec `FastP_reads_boxplot.yaml` mounted by no group | verified: scan (`scan_recipes.py`) | info | practice | #69 | kept (Blueprint material); say so in `info:` or remove on purpose |

The Abromics recipe (the one the local deployment opens first): no unknown keys, no ignored plot keys, every schema builds; its only
row-multiplying join is `MLST x VirulenceFinder` (42 -> 984), which is one-to-many (MLST has one row per sample) and expected.

## 2. What was fixed in the recipe (data unchanged)

Verified by comparing shape and content hash of all six plot-target collections before and after: identical (`snap_before.txt`,
`snap_after.txt`). The change is in what the figures show and in what the engine no longer ignores.

| File | Change |
|---|---|
| `plots/miaou.yaml`, `plots/Quast_assembly_quality_barplot.yaml` | `facet_by` in `mapping` and the dead `facet_scales` replaced by a `facet_wrap` layer (`~metric`, free scales) |
| `plots/FastP_reads_horizontal_barplot.yaml` | horizontal bars: `x: sample_id`, `y: total_reads`, `coord_flip`; dead `coordinate_flip` removed |
| `plots/phenotype_genome_length_dotplot.yaml` | `labs:` (ignored) replaced by a `labs` layer for x and y; the title that was shown is kept (the second title in the old `labs` was never displayed) |
| `1_test_data_ST22_dummy.yaml` | removed `height`, `show_legend` from `plot_defaults`; removed the legacy top-level `wrangling:`/`tier3` block |
| `input_fields/Detailed_summary_input_fields.yaml` | `hsp_lengthtotal_length`: `utf8` |
| `output_fields/ST22_Anchor_final_output_fields.yaml` | `sample_id`: `categorical` |

Guard: `app/tests/test_shipped_recipes_hygiene.py` (21 tests: unknown `plot_defaults` keys, ignored plot-spec keys, every data schema builds,
for every shipped recipe). Mutation check: on the unfixed recipe 3 of them fail.

## 3. Questions for Eve (the recipe cannot be finished without them)

1. **What must `ST22_Anchor` answer?** The recipe says "AMR + Virulence + MLST", the plot spec says "whitelisted virulence genes by sequence type". Options:
   (a) virulence + MLST + metadata, no ResFinder; the "Detected" status moves to the VirulenceFinder step (**recommended**: the plots read virulence;
   AMR already has its own collection and heatmap); (b) keep AMR but reduce ResFinder to one row per sample before the join (loses the gene detail the
   tile plot needs); (c) two collections. Recommendation (a), unless you want AMR genes in that one figure.
2. **Samples without any usable phenotype (4 of 42).** (a) not plotted, with a note "n = 38 of 42" (**recommended**); (b) keep at 0 and say so in the title;
   (c) other.
3. **MLST plot title and demo filter.** Keep the 2023-2025 filter (it makes the T1/T2 toggle visible) and add "2023-2025" to the MLST title, or leave it?

## 4. What the checkers cannot see (rule 7)

`test_render_every_plot` only proves that a plot renders. It does not see: panels that were asked for and not drawn, a mapping that draws thin lines,
a fan-out, a status column that means something else. Of those, the facet class and the join row growth can be tested (#65, #68); the others need a
person to look at the picture. Looking at each picture is therefore part of any recipe change (the before/after PNGs of this review are in
`tmpAI/recipe_review/`).
