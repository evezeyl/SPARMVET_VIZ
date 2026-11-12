# Recipe review (data scientist): 1_test_data_ST22_dummy

**Written for:** Eve and the next session. **Date:** 2026-11-11. **Method:** `.claude/workflows/design_review_personas.md`, persona 3
(data scientist): run every collection and every plot on the real test data, look at each picture, measure the joins, compare with an
independent computation. Rules: verified = run or read at file:line; reasoned = follows from verified facts, still needs a test.
**Scope not covered:** the numbers of `figshare_integration` and `stress_test_master` (only built and scanned); the Abromics recipe was scanned
and its joins measured, its plots were not looked at one by one.

## 1. Findings

| # | Finding | Evidence | Severity | Class | Issue | Status |
|---|---|---|---|---|---|---|
| 1 | `facet_by` inside `mapping:` gives no panels (documented as equivalent to `facet_wrap`; the Blueprint form writes it; six shipped plots use it). `miaou` pooled three metrics in one violin (false bimodal shape); the Quast boxplot put N50 and total length on one axis | verified: render with both spellings (`tmpAI/recipe_review/facet_check.py`), `plot_config_resolver.py:473,514`, pictures before/after | high (wrong figure) | software bug | #65 | **fixed** in the recipe (explicit `facet_wrap`) and in the resolver (mapping.facet_by honoured, mutation-checked); `virulence_variants` kept unfaceted until Eve decides (#67) |
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
| 13 | The recipe data check returned "no problems" while a schema could not be built; `test_render_every_plot` passes with ignored facets and fan-out | verified: baseline 75 passed with the broken schema | medium (checker blind spot) | software bug | #71 | **fixed**: the check runs the wrangling on one row (types, not values); `test_render_every_plot` now asserts panels; hygiene and canary tests added |
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

## 2b. QA canaries (added the same day)

A group **QA Canaries** in this recipe (7 plots, 6 new collections; the seventh, `QA_aggregated_no_key`, was added on 2026-11-12: a plot whose data is an aggregate without `sample_id`, the fixture for the audit reach, #60) for catching errors better. Each isolates one failure mode, its correct numbers are
computed from the raw tsv files in `app/tests/test_qa_canaries.py` (not through the engine) and are written in the plot subtitle, so a person looking
at the picture can see a wrong one. Map of canaries to failure modes and to the work packages that use them: `.claude/tasks/home_exploration_build_brief.md`
section 0b. Think-through behind the choice (data scientist and developer): every canary has a known answer that is independent of the code under test;
the failure modes are the ones this review actually found (a sample vanishing from a long table, a missing value filled or dropped, `2022.0`, an integer
threshold, panels not drawn, rows multiplied by a join); T1 and T2 differ on purpose in one of them so that stage-dependent behaviour can be tested; one
canary is an EXHIBIT of a known defect (#68) so that a future check has something real to flag. Mutation-checked: an inner join instead of a left join and
a direct cast of the year to text both make the right test fail. Trade-off: the group is visible to every user of this recipe; a separate recipe file would
keep the demo clean and is a small change if you prefer it.

## 3. Questions for Eve (the recipe cannot be finished without them)

1. **What must `ST22_Anchor` answer?** The recipe says "AMR + Virulence + MLST", the plot spec says "whitelisted virulence genes by sequence type". Options:
   (a) virulence + MLST + metadata, no ResFinder; the "Detected" status moves to the VirulenceFinder step (**recommended**: the plots read virulence;
   AMR already has its own collection and heatmap); (b) keep AMR but reduce ResFinder to one row per sample before the join (loses the gene detail the
   tile plot needs); (c) two collections. Recommendation (a), unless you want AMR genes in that one figure.
   Related: the plot spec of `virulence_variants` says "facetted by sequence type"; now that `facet_by` in `mapping` works, that gives 16 panels too small to read
   with this table, so the setting was left out (comment in `plots/integration_plot.yaml`). Decide together with this question: facets with free scales, no facets, or another layout.
2. **Samples without any usable phenotype (4 of 42).** (a) not plotted, with a note "n = 38 of 42" (**recommended**); (b) keep at 0 and say so in the title;
   (c) other.
3. **MLST plot title and demo filter.** Keep the 2023-2025 filter (it makes the T1/T2 toggle visible) and add "2023-2025" to the MLST title, or leave it?

## 4. What the checkers cannot see (rule 7)

`test_render_every_plot` only proves that a plot renders. It does not see: panels that were asked for and not drawn, a mapping that draws thin lines,
a fan-out, a status column that means something else. Of those, the facet class and the join row growth can be tested (#65, #68); the others need a
person to look at the picture. Looking at each picture is therefore part of any recipe change (the before/after PNGs of this review are in
`tmpAI/recipe_review/`).

## 5. Steps for tomorrow (recipe review, in this order)

Nothing below is done yet; each step waits for the answer named in it. The scripts used for the verification are in `tmpAI/recipe_review/`
(not committed): `forensics_data.py`, `fanout.py`, `diagnose.py`, `canary_check.py`, `render.py` (pictures), `scan_recipes.py`.

1. **Answer R1-R4** (agenda `home_audit_review_agenda_2026-11-12.md`, section 1): anchor (#67), score of samples without phenotype (#70), MLST title, `virulence_variants` layout.
2. **R1, if (a):** in `1_test_data_ST22_dummy`: move the constant `status: Detected` from `wrangling/ResFinder_wrangling.yaml` to `wrangling/VirulenceFinder_wrangling.yaml`; take ResFinder out of the `ST22_Anchor` ingredients and join steps; correct `output_fields/ST22_Anchor_final_output_fields.yaml` (no `gene`, no `phenotype`; `status` from the virulence step); check that `virulence_count` equals the number of distinct genes per sample (the fan-out is gone) and that the table has 342 (sample, gene) rows before sorting; add the test (raw-file oracle, like `test_qa_canaries.py`); render `virulence_bar` and `virulence_variants` and **look at them**.
3. **R4:** if panels are wanted for `virulence_variants`, an explicit `facet_wrap` layer with `scales: free`; render, look; if not, delete the comment left in `plots/integration_plot.yaml`.
4. **R2, if (a):** in `assembly/Summary_phenotype_length_fragmentation_assembly.yaml` give a sample with only unknown phenotypes a missing score (not 0) and leave it out of the plot; subtitle "n = 38 of 42 samples (4 without a usable phenotype)"; test on the raw numbers (6 samples truly at 0, 4 not plotted).
5. **R3:** years in the title of `plots/MLST_counts_bar.yaml`.
6. **Add the missing canary (forensics F1):** a collection with counts per year aggregated in T2 (no `sample_id`) and its plot, with a raw-file oracle and a mutation check; it is the fixture for the reach tests of the audit.
7. **Verify:** `test_shipped_recipes_hygiene.py`, `test_qa_canaries.py`, `test_render_every_plot.py`, the recipe data check, the headless suite; the browser gate (read #72 first: a red gate is a question); look at every changed picture next to its "before" in `tmpAI/recipe_review/`.
8. **Close:** comment and close #67 and #70 with evidence; tick the rest of #69 (the information item is yours: keep or remove the unused collections and `FastP_reads_boxplot.yaml`); update the statuses in section 1 of this file; separate commits for the recipe change and for the tests.
9. **Later, when #66 and #68 are built:** promote `scan_recipes.py` and `fanout.py` to committed audit scripts (they find ignored keys and row-multiplying joins in every shipped recipe).

## 3b. What an AMR data scientist would do with R1-R4 (2026-11-12; proposals, awaiting Eve; these are test recipes)
**Method:** reasoned from AMR surveillance practice (my knowledge, not looked up), plus one check on the data (verified).
**Habits that apply to every table of a recipe:** (1) the table states its **grain** ("one row = one virulence gene found in one sample"), the description decided on 2026-11-12; (2) the **denominator** is every sample that was sequenced, taken from the metadata or the pipeline summary, not from the tool's own output; (3) three kinds of "nothing" are kept apart and each is written in the recipe: *not detected* (analysed, no hit: a real zero), *not analysed or the tool failed* (missing), *undeterminable* (a category such as "unknown" or "Non Determined"); (4) every missing value is treated by an explicit step with a sentence in the description, never by the join or the plot.
**Verified on the data:** 4 of 42 samples have no ResFinder row (40503315, 52676003, 75442817, 87836481), all 4 passed the quality module. The pipeline's own summary lists AMR genes for 3 of them (for example 52676003: aadA5, dfrA17, sul2) and only a virulence gene for 40503315. So "absent from ResFinder" means "none detected" for one and "table incomplete" for the others: the recipe cannot tell which, and a plot must not draw both as blank.
| Q | Proposal | Why |
|---|---|---|
| R1 `ST22_Anchor` | (a) virulence + MLST + metadata, no ResFinder; AMR keeps its own table. The "Detected" status is written in the VirulenceFinder step; samples with no virulence hit stay, as "none detected". Description: one row = one virulence gene in one sample | Two long tables joined on the sample give gene x gene rows (the 72 for a sample with 9 genes). If a sample-level view is wanted, summarise each long table to one row per sample first, then join |
| R2 samples without usable phenotype | (a) not plotted, caption "n = 38 of 42" | "Unknown" must never be coded as susceptible (0). The six truly susceptible samples stay at 0. Better still: show them as a separate grey "no prediction" group, so nothing is drawn as nothing |
| R3 MLST title | keep the year filter (it makes T1/T2 visible), say in the title "2023-2025, 33 of 42 samples" and in the table description | A subset must never be silent |
| R4 `virulence_variants` | tiles gene x sequence type with the share of isolates carrying the gene and n per sequence type; sequence types with fewer than 3 isolates grouped as "other" (the action `top_n_other` exists) | 16 panels are unreadable and a share from one isolate misleads |

**Eve, 2026-11-12:** R1-R4 as proposed in 3b are agreed ("seems good"). "Not detected" is a good result and a category: count the samples with no resistance gene detected. Valid only when the sample was analysed (the four samples above show why the population table must be the reference). Applied in task RECIPE-ST22-FIX-1, tests first.
