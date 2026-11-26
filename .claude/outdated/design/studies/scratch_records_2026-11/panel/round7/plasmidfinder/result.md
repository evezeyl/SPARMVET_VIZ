# PlasmidFinder: use, wiring, and the two recipes (data-scientist viewpoint, round 7)

Tags: RUN = I ran it (scripts in this folder), READ = read at file:line or URL, INFERRED = my reasoning, not checked.
Scratch only. No repository file was changed. Everything is under `tmpAI/panel/round7/plasmidfinder/`:
`recipes/` (copy of recipe 1 with the proposal), `pics/` (pictures and tables), `verify.py` (my own Polars check),
`run_engine.py` (runs the project's engine and plot factory), `golden_new.json`, `patch_recipe_yaml.diff`.

## 1. How PlasmidFinder results are used in AMR work

**What a hit is.** PlasmidFinder compares a genome (raw reads, contigs, or a closed plasmid) with a database of
plasmid replicon sequences (the part of a plasmid that makes it copy itself; its type gives the incompatibility group,
for example IncFII, IncX1, Col156). One hit = one replicon type found at one place (one contig, a start and an end),
with the percent identity and the coverage (the share of the reference replicon that the hit covers). The 2014 paper
built the first database from replicon sequences of 559 fully sequenced Enterobacteriaceae plasmids: 116 replicon
sequences at that time, matching all replicons of the 559 plasmids at 80 percent identity or better; in 49 draft genomes
of one Salmonella serovar it found between 0 and 5 different replicons per genome (READ, abstract, PubMed 24777092).

**Thresholds.** The web service says: "By default the %ID = 95" and "the minimum % coverage = 60" (READ, CGE page).
The command-line tool 3.0.2 has 0.90 identity and 0.60 coverage as defaults (READ in a search summary of the PyPI page
and of the Bactopia page; I did not open the pages). So 95/60 on the web, 90/60 on the command line. The shipped test
file is cut at 90/60 (smallest identity 90.14, smallest overlap 61.62, RUN), the command-line default.

**Usual analyses** (what the sources do; item 3 and 4 are the usual surveillance summaries, which I could not find
written as a method in the sources, INFERRED):
1. Replicon types per isolate, next to resistance genes found with ResFinder: Nigeria 2025, Iran 2025, Mexico 2024,
   Egypt 2020 (all READ in the abstracts; the Egypt and Iran papers list the replicons of the isolates that carry a
   given resistance gene, for example IncX3 with blaNDM-5).
2. The replicon types of the isolates that have the resistance, and a conjugation test on those that carry a replicon
   found in other strains (Nigeria 2025, READ abstract).
3. Prevalence of each replicon type in a collection, and its distribution by source, country, year, sequence type.
   Tanzania 2022 reports the prevalence of replicon types and the resistance and virulence genes inside each replicon
   type (READ abstract). By year or country: INFERRED, a usual summary, not read in a source.
4. Link replicon to resistance gene on the SAME contig: Tanzania 2022 (predicted plasmid contigs validated with
   PlasmidFinder) and a Nigeria preprint 2025 (hybrid short and long reads; resistance genes on plasmid contigs, READ
   abstracts).

**Limits.** (a) A replicon is not a whole plasmid. In a benchmark of 377 known plasmids PlasmidFinder had 99 percent
specificity and 50 percent sensitivity to find the contigs of plasmid origin (READ, Robertson and Nash 2018,
abstract). (b) A plasmid can carry several replicons, so a count of hits or of replicon types is not a count of plasmids
(0 to 5 per genome, READ; the Tanzania paper separates "single" and "multiple replicon" types, READ). (c) Short reads
give draft assemblies: plasmids are in pieces, the same plasmid can be split over contigs and different plasmids can be
merged (READ, MOB-suite abstract: "incomplete assembly of plasmids"). So "same contig" is evidence, not proof, that a
gene is on a plasmid. (d) A replicon not in the database is not detected, and the database grows (INFERRED).

**Good practice** (INFERRED from the above): write the threshold and the database version with the result; report
replicon TYPES per isolate (presence), not raw hit counts, when the question is "how many isolates"; keep the isolates
without a hit in the denominator; say that groups with few isolates are noisy.
**Known pitfalls:** counting hits where isolates are meant (in the shipped file 163 hits are 150 sample-and-type pairs,
IncFII(pHN7A8) has 18 hits in 14 samples, RUN); reading a replicon as a plasmid; a join that drops isolates with no hit.

**What I could not check.** The full text of the 2014 paper (PubMed Central blocked my fetch; I read the abstract only);
the output columns as defined by the tool (the sources I reached do not give them; the file's `HSP Length/Total Length`
and `%Overlap` are described below from the data); the current database version; any article that shows replicon by year
or by country as a figure.

**Sources.**
1. Carattoli A. et al. "In silico detection and typing of plasmids using PlasmidFinder and plasmid multilocus sequence
   typing". Antimicrob Agents Chemother 2014;58(7):3895-3903. https://doi.org/10.1128/AAC.02412-14 (PubMed 24777092)
2. Center for Genomic Epidemiology, DTU. PlasmidFinder service, instructions.
   https://cge.food.dtu.dk/services/PlasmidFinder/instructions.php
3. PlasmidFinder 3.0.2 on PyPI, https://pypi.org/project/plasmidfinder/3.0.2/ , and Bactopia tool page,
   https://bactopia.github.io/latest/bactopia-tools/plasmidfinder (search summaries only)
4. Robertson J, Nash JHE. "MOB-suite: software tools for clustering, reconstruction and typing of plasmids from draft
   assemblies". Microb Genom 2018;4(8). https://doi.org/10.1099/mgen.0.000206
5. Sengeruan LP et al. "Plasmid characterization in bacterial isolates of public health relevance in a tertiary
   healthcare facility in Kilimanjaro region, Tanzania". J Glob Antimicrob Resist 2022;30:384-389.
   https://doi.org/10.1016/j.jgar.2022.06.030
6. Rabiu AG et al. "Transmissible antimicrobial resistance in Escherichia coli isolated from household drinking water in
   Ibadan, Nigeria". PLoS One 2025;20(5):e0318969. https://doi.org/10.1371/journal.pone.0318969
7. Haeili M et al. "Emergence of transferable tigecycline and eravacycline resistance gene tet(X4) in Escherichia coli
   isolates from Iran". Sci Rep 2025;15:16581. https://doi.org/10.1038/s41598-025-98206-6
8. Ramadan H et al. "Circulation of emerging NDM-5-producing Escherichia coli among humans and dogs in Egypt".
   Zoonoses Public Health 2020;67(3):324-329. https://doi.org/10.1111/zph.12676
9. Silva-Sanchez J et al. "Molecular characterization of Escherichia coli producing extended-spectrum beta-lactamase
   CTX-M-14 and CTX-M-28 in Mexico". Braz J Microbiol 2024;55(1):309-314. https://doi.org/10.1007/s42770-023-01183-z
10. Ejikeugwu CP et al. Nigeria poultry E. coli, whole-genome sequencing (bioRxiv preprint, not peer reviewed), 2025.
    https://doi.org/10.1101/2025.09.18.677015

(Searched PubMed with general terms only; no project data left this machine.)

## 2. The data, its history, and the plots

### 2.1 The data (RUN: `explore.py`, `explore2.py`)

File: `assets/test_data/1_test_data_ST22_dummy/test_data_PlasmidFinder_20260307_105756.tsv`.
**One row = one PlasmidFinder hit**: a replicon type found at one place (contig, start, end) of one sample.

| Fact | Value |
|---|---|
| Rows, columns | 163 rows, 9 columns: `sample_id`, `Plasmid`, `%Identity`, `%Overlap`, `HSP Length/Total Length`, `Contig`, `Start`, `End`, `Accession` |
| Samples | 41 samples with hits. The metadata file has 42; the one with no hit is `52676003` (Parent, 2024, France) |
| Missing values | none in any column of the hit file or of the metadata (no null, no empty text) |
| Identity | 90.14 to 99.98 (nothing below 90) |
| Overlap | 61.62 to 100.45; 6 values above 100 (an oddity: a coverage cannot pass 100) |
| Thresholds | the 90/60 filter removes 0 rows: the file is already cut there |
| Replicon types | 18 (Inc and Col types); IncFII(pHN7A8) in 14 samples, ColpVC in 3 |
| Hits per sample | 2 to 7 (mean 3.98); distinct types per sample 2 to 6 (mean 3.66) |
| Repeats | 13 sample-and-type pairs have two hits with different reference accessions; 150 distinct pairs for 163 hits |
| Start > End | 76 rows (the hit is on the other strand, INFERRED) |
| Contig names | generated style (`contig00042`) |
| Dummy signs | `%Overlap` does not follow `HSP Length/Total Length` (correlation 0.03; in 60 rows the text says 100 percent and the overlap is lower): the file is synthetic, so use the overlap for the filter only (INFERRED) |

Metadata (42 samples, one row each): Norway 28, Germany 10, France 4; 2022: 9, 2023: 8, 2024: 25; Layer 19, Broiler 13,
Parent 10. Counts of samples WITH hits: Norway 28, Germany 10, France 3; 2022: 9, 2023: 8, 2024: 24.

### 2.2 Was it ever wired? (RUN: `git log`)

**No. It was never wired in recipe 1.** `git log -S"PlasmidFinder"` on the recipe 1 file and its older names gives no
commit that adds a PlasmidFinder schema; the only "plasmid" in recipe 1 is a column of the Summary table.
- 2026-03-07 `f2359fa5`: the data file is added with the other dummy files.
- 2026-04-10 `6915bed1`: a field list `PlasmidFinder.yaml` is put in the recipe 1 folder; no schema includes it.
  `1be7a5eb` (same day, "remove legacy test pipeline manifests") deletes it.
- 2026-04-13 `c01c3592` ("ai comming back to this directory - keep for now") puts it back as
  `wrangling/PlasmidFinder_wrangling.yaml`: still an old field list (`type: numeric`), in the wrong folder.
- 2026-04-23 `7ece43e7` ("feat: add plasmid data pipeline ...") wires the plasmid data into the NEW recipe
  `2_test_data_ST22_dummy`, three days after. No message says why recipe 1 was left out (INFERRED: the work moved to
  recipe 2). 2026-11-07 `de37ed0d` only renamed the file. So: the piece in recipe 1 is a left-over, and recipe 2 already
  has the PlasmidFinder table, one join and one plot (hits counted, not samples).

### 2.3 Proposals (all drawn through the project's engine and plot factory, recipe copy in `recipes/`)

Shared design (her tier rule). Steps that several plots need are in the lower tiers; each plot keeps only its own group
with a filter. The tier 3 container of a plot (`steps.tier3`) has no reader yet (check P05 refuses it), so today the
plot's own part is the plot spec `filters:` (allowed, applied by the plot factory).
- Schema `PlasmidFinder` tier 1: filter 90/60, then the best hit per sample and type (the same rule she decided for the
  AMR genes: highest identity, then highest overlap, tie to the lowest accession). 163 rows become 150.
- Join `PlasmidFinder_with_metadata`, base = the metadata (left join), so all 42 samples stay. **Tier 1** (shared): join,
  year cast, select; 151 rows = 150 pairs + 1 row for the sample with no hit. **Tier 2** (shared by both heatmaps): one row per
  replicon type and group, where group is a country or a year: `n_samples_with_type`, `n_samples_in_group`,
  `percent_of_group`, `group_label` ("Norway (n=28)"), `found_in` ("in 2 of 3"). 18 types x 6 groups = 108 rows.
- Each heatmap then keeps its group: `filters: group_type = country` (or `year`).

**P1. Replicon type by COUNTRY (her heatmap 1).** Question: which replicon types are common to all countries, which are
found in only one, and how big is the share in each? Picture: `pics/plasmid_replicons_by_country.png`.
**P2. Replicon type by YEAR (her heatmap 2).** Same question over time. Picture: `pics/plasmid_replicons_by_year.png`.
**P3. Replicon types per sample, by source.** Question: do the samples of one source carry more types? One bar per
number of types (0 to 6), coloured by source. Picture: `pics/plasmid_types_per_sample.png`.
The "common and unique" view she asked for is built into P1 and P2: the row groups on the right ("in 1 of 3", "in 2 of 3",
"in 3 of 3") say in how many countries (years) the type is found; the groups come from the table, not from the plot.

What one row, one cell, an empty cell mean:
| Plot | One row of the plotted table | One cell or bar | Empty or zero |
|---|---|---|---|
| P1, P2 | one replicon type in one group (108 rows before the filter, 54 after) | the NUMBER in the cell = samples of the group that carry the type (not hits); the COLOUR = that number as a share of the group's samples | 0 is written in the cell: no sample of the group carries the type (a real zero, "not detected"). I chose 0, not blank, because a blank can be read as "not analysed" |
| P3 | one sample (42 rows) | a bar = samples with that number of types | 0 types = the one sample with no hit |

Few samples: the label carries the size ("France (n=4)", "2023 (n=8)") and the colour is a share, so Norway (28) and
France (4) are comparable, and the number is the count. France has 4 samples: one sample moves a cell by 25 percentage
points. The denominator is all samples of the group in the metadata, also the one with no hit (France n=4, not 3).

Pitfalls (each checked):
- **Counting hits where samples are meant.** Recipe 2 counts hits (163); samples with the type are 150 pairs.
- **A join that drops samples.** An inner join (recipe 2) loses the sample with no hit: France would read n=3. I made
  that change in a copy (`bad/`) and my check fails with 18 mismatching cells per heatmap: the check can fail.
- **A join that multiplies rows.** Not here: the metadata has one row per sample (RUN: 42 rows, 42 samples), the join
  is left from the metadata, so a sample gives as many rows as it has hits and no more.
- **A missing metadata value.** None in the shipped data. A missing country or year would be a group of its own
  ("null"); the check on the metadata is in the join description, not in a step.
- **The text "null".** The wide table makes a column for the sample with no hit; I remove the replicon named `null`
  (`modif_filter ne "null"`). A real replicon can never be called `null`.

**Numbers checked** (RUN, `verify.py`, plain Polars from the raw TSV files, no engine, no project code):
- P1: all 54 cells equal (count, group size, percent, in how many groups): 0 mismatches; group sizes France 4, Germany 10,
  Norway 28; the 54 cell counts add up to 150 pairs, 14 zero cells.
- P2: all 54 cells equal: 0 mismatches; sizes 9, 8, 25; sum 150; 5 zero cells.
- P3: all 42 rows equal; the bars by source: 0 types: Parent 1; 2: Parent 3, Broiler 2, Layer 5; 3: Broiler 2, Layer 5;
  4: Parent 3, Broiler 5, Layer 6; 5: Parent 2, Broiler 4, Layer 1; 6: Parent 1, Layer 2. Mean types per sample: Broiler
  3.85 (13), Layer 3.47 (19), Parent 3.40 (10).
- T1: 151 rows expected, 151 built; best-hit rows equal to my own sort-and-first on the 163 hits.
- The numbers in the pictures are the table column `n_samples_with_type`; I read some cells in the pictures against the
  table (IncFII(pHN7A8): Norway 11, Germany 1, France 2 = 14 samples).

**Recommendation: build P1 and P2 together (they are hers, they share one table), and P3 as a third plot.**
Reason: P1 and P2 answer "which replicon types, where and when", count samples, show the size of every group and the zeros,
and give the common-and-unique view; P3 is a cheap extra that answers a different question (load per sample) and
reuses tier 1. One builder, one provisional commit. Honest note: with 3 countries and 3 years the heatmaps are small, and
France (4 samples) and 2023 (8 samples) are thin; the n in the label says so.

Not drawn, noted: replicon and resistance gene on the same contig. The hit files hold the contig of both; 8 pairs of
(sample, contig) match, 7 of the 70 resistance hits. The contig names look generated, so I do not trust that link on
this dummy data (INFERRED); it is a good proposal for real data.

### 2.4 The exact patch (PROVISIONAL; apply to the main tree, not tested there; tested on the copy in `recipes/`)

Checks on the copy: `validate_data_analysis_recipe` gives 0 problems; the descriptions pass the check of
`app/tests/test_descriptions_are_whole.py`; the engine builds the 3 collections and renders the 3 plots.
**Golden baseline** (`app/tests/golden/baseline.json`, recipe 1): 7 NEW entries and none changed (all existing
entries compared equal, RUN): t1 `PlasmidFinder_with_metadata` (151 rows) and `PlasmidFinder_types_per_sample` (151);
t2 the same two (108 and 42 rows); plots `plasmid_replicons_by_country` (54 rows), `plasmid_replicons_by_year` (54),
`plasmid_types_per_sample` (42). Hashes in `golden_new.json`. Regenerate with
`golden_baseline.py --out app/tests/golden/baseline.json` in the same commit and say "new plots, no existing picture
changes". The tests that run over every plot or recipe (`test_render_every_plot`, `test_anchor_determinism`, the checker
and description tests) pick the new collections up by themselves.
Optional hunk: the "best hit per sample and type" step at the end of `PlasmidFinder_wrangling.yaml` (point 3 below);
without it T1 has 164 rows, the two T1 hashes of `golden_new.json` differ, the schema description ("150 rows are left") must be changed, and no heatmap number changes (T2 equal, RUN).

New and replaced files:

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/PlasmidFinder_input_fields.yaml  (NEW)`**

```yaml
sample_id:
  original_name: "sample_id"
  type: String
  label: "Sample ID"
  is_entity_key: true
plasmid_name:
  original_name: "Plasmid"
  type: String
  label: "Replicon type"
identity:
  original_name: "%Identity"
  type: Float64
  label: "Identity %"
overlap:
  original_name: "%Overlap"
  type: Float64
  label: "Overlap % (coverage of the reference replicon)"
contig:
  original_name: "Contig"
  type: String
  label: "Contig"
accession:
  original_name: "Accession"
  type: String
  label: "Reference accession"
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml  (REPLACED: the old-format field list is overwritten; git keeps it)`**

```yaml
# Hits below the usual PlasmidFinder thresholds are not replicons for this analysis. The shipped test file is already
# cut at 90 % identity and 60 % coverage (smallest values in the file: 90.14 and 61.62), so today these two steps remove no row.
tier1:
  - action: modif_filter
    column: identity
    op: ge
    value: 90
    na: remove
  - action: modif_filter
    column: overlap
    op: ge
    value: 60
    na: remove
  # One row per sample and replicon type: the hit with the highest identity, then the highest overlap; a tie goes to the
  # lowest accession (a fixed rule, so the same data always gives the same row, ADR-090). A sample with the same type hit
  # twice (13 cases in the shipped file, always with two different reference accessions) keeps one row.
  - action: polars_sort
    by: [sample_id, plasmid_name, identity, overlap, accession]
    descending: [false, false, true, true, false]
    maintain_order: true
  - action: polars_unique
    subset: [sample_id, plasmid_name]
    keep: first
    maintain_order: true
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_Metadata_tier1.yaml  (NEW)`**

```yaml
# One row per replicon hit, plus one row (empty replicon) for a sample with no hit: a left join FROM the metadata,
# so that every sample stays and can be counted in the denominator of a percentage.
- action: polars_join
  right_ingredient: PlasmidFinder
  'on': [sample_id]
  how: left
  maintain_order: left_right
# TSV numbers are read as Float64: Float64 to Int64 to String, or the label becomes "2022.0".
- action: polars_cast
  columns: [year]
  dtype: Int64
- action: polars_cast
  columns: [year]
  dtype: String
- action: polars_select
  exprs: [sample_id, country, source, year, plasmid_name, identity, overlap, contig, accession]
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_Metadata_wrangling.yaml  (NEW)`**

```yaml
# T1 is the shared table of both plasmid collections (PlasmidFinder_Metadata_tier1.yaml).
tier1: !include '1_test_data_ST22_dummy/wrangling/PlasmidFinder_Metadata_tier1.yaml'

# Shared by the two heatmaps: one row per replicon type and group (a country or a year) with the number of
# samples of the group that carry the type. Each plot keeps its own group with a filter of its own.
tier2:
  # Hits to presence: a sample with two hits of the same type counts once.
  - action: polars_unique
    subset: [sample_id, plasmid_name]
    keep: first
    maintain_order: true
  # Wide: one 0/1 column per replicon type (0 = no hit). The sample with no hit gives the column "null".
  - action: polars_pivot
    'on': [plasmid_name]
    index: [sample_id, country, year]
    values: [plasmid_name]
    aggregate_function: len
    maintain_order: true
  - action: polars_unpivot
    index: [sample_id, country, year]
    variable_name: plasmid_name
    value_name: carries
  # The column "null" only stood for "this sample has no hit": it is not a replicon type.
  - action: modif_filter
    column: plasmid_name
    op: ne
    value: "null"
    na: remove
  - action: polars_unpivot
    index: [sample_id, plasmid_name, carries]
    'on': [country, year]
    variable_name: group_type
    value_name: group_value
  - action: polars_group_by
    by: [group_type, group_value, plasmid_name]
    maintain_order: true
    named_aggs:
      n_samples_with_type: pl.col('carries').sum()
      n_samples_in_group: pl.col('sample_id').n_unique()
  - action: polars_with_columns
    named_exprs:
      percent_of_group: pl.col('n_samples_with_type') / pl.col('n_samples_in_group') * 100
      group_label: pl.concat_str([pl.col('group_value'), pl.lit(' (n='), pl.col('n_samples_in_group').cast(pl.String), pl.lit(')')])
      groups_with_type: (pl.col('n_samples_with_type') > 0).sum().over(['group_type', 'plasmid_name'])
      groups_total: pl.col('group_value').n_unique().over('group_type')
  - action: polars_with_columns
    named_exprs:
      found_in: pl.concat_str([pl.lit('in '), pl.col('groups_with_type').cast(pl.String), pl.lit(' of '), pl.col('groups_total').cast(pl.String)])
  - action: polars_sort
    by: [group_type, plasmid_name, group_value]
    maintain_order: true
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_types_per_sample_wrangling.yaml  (NEW)`**

```yaml
# Same table as PlasmidFinder_with_metadata at tier 1 (one row per hit, plus one row for a sample with no hit).
tier1: !include '1_test_data_ST22_dummy/wrangling/PlasmidFinder_Metadata_tier1.yaml'

# One row per sample with the number of distinct replicon types it carries (0 for the sample with no hit).
tier2:
  - action: polars_group_by
    by: [sample_id, source, country, year]
    maintain_order: true
    named_aggs:
      n_replicon_types: pl.col('plasmid_name').drop_nulls().n_unique()
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/PlasmidFinder_replicon_by_country_heatmap.yaml  (NEW)`**

```yaml
target_dataset: PlasmidFinder_with_metadata
title: "Replicon types by country: share of the samples of each country that carry the type"
mapping:
  x: group_label
  y: plasmid_name
  fill: percent_of_group
  label: n_samples_with_type
filters:
  - {column: group_type, op: eq, value: country}
layers:
- name: geom_tile
  params:
    color: white
    size: 0.4
- name: geom_text
  params:
    size: 7
    color: "#1a1a1a"
- name: scale_fill_gradient
  params:
    low: "#ffffff"
    high: "#6f8ff0"
- name: facet_grid
  params:
    rows: found_in
    scales: free_y
    space: free_y
- name: labs
  params:
    x: "Country (n = samples in the file)"
    y: "Replicon type"
    fill: "% of samples"
    subtitle: "Cell: samples with the type (0 = none). Right: in how many countries the type is found"
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/PlasmidFinder_replicon_by_year_heatmap.yaml  (NEW)`**

```yaml
target_dataset: PlasmidFinder_with_metadata
title: "Replicon types by year: share of the samples of each year that carry the type"
mapping:
  x: group_label
  y: plasmid_name
  fill: percent_of_group
  label: n_samples_with_type
filters:
  - {column: group_type, op: eq, value: year}
layers:
- name: geom_tile
  params:
    color: white
    size: 0.4
- name: geom_text
  params:
    size: 7
    color: "#1a1a1a"
- name: scale_fill_gradient
  params:
    low: "#ffffff"
    high: "#6f8ff0"
- name: facet_grid
  params:
    rows: found_in
    scales: free_y
    space: free_y
- name: labs
  params:
    x: "Year (n = samples in the file)"
    y: "Replicon type"
    fill: "% of samples"
    subtitle: "Cell: samples with the type (0 = none). Right: in how many years the type is found"
```

**`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/PlasmidFinder_types_per_sample_bar.yaml  (NEW)`**

```yaml
target_dataset: PlasmidFinder_types_per_sample
title: "Replicon types per sample, by source"
mapping:
  x: n_replicon_types
  fill: source
layers:
- name: geom_bar
  params: {}
- name: scale_x_continuous
  params:
    breaks_integer: true
- name: labs
  params:
    x: "Distinct replicon types in the sample"
    y: "Samples"
    fill: "Source"
```



Changed file, as a diff (adds the schema, the two collections, the group `Plasmids` with its 3 plots):

```diff
diff --git a/1_test_data_ST22_dummy.yaml b/1_test_data_ST22_dummy.yaml
index 7444fc26..fa08ddca 100644
--- a/1_test_data_ST22_dummy.yaml
+++ b/1_test_data_ST22_dummy.yaml
@@ -116,6 +116,17 @@ data_schemas:
     input_fields: !include '1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml'
     wrangling: !include '1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml'
 
+  PlasmidFinder:
+    label: "PlasmidFinder"
+    description: "One row per replicon hit reported by PlasmidFinder (the shipped file has 163 hits of 41 samples; 150 rows are left after the best-hit rule): hits below 90 % identity or 60 % overlap are removed, then per sample and replicon type only the hit with the highest identity, then the highest overlap, is kept (Gene detection)."
+    source:
+      type: local_tsv
+      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_PlasmidFinder_20260307_105756.tsv
+    null_values: []
+    strip: true
+    input_fields: !include '1_test_data_ST22_dummy/input_fields/PlasmidFinder_input_fields.yaml'
+    wrangling: !include '1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml'
+
 # ── Additional Datasets ───────────────────────────────────────────────────────
 additional_datasets_schemas:
   VirulenceFinder:
@@ -209,6 +220,22 @@ joins:
     - dataset_id: metadata_schema
     steps: !include '1_test_data_ST22_dummy/wrangling/QC_Reads_Anchor_wrangling.yaml'
 
+  PlasmidFinder_with_metadata:
+    label: "PlasmidFinder with metadata"
+    description: "Result (T2): one row per replicon type and group (a country or a year), with the number of samples of the group that carry the type, the number of samples of the group and the share; every sample of the metadata counts in its group, also the sample with no hit. Raw (T1): one row per replicon hit with the sample's source, year and country (left join from the metadata), plus one row with an empty replicon for a sample with no hit."
+    ingredients:
+    - dataset_id: metadata_schema
+    - dataset_id: PlasmidFinder
+    steps: !include '1_test_data_ST22_dummy/wrangling/PlasmidFinder_Metadata_wrangling.yaml'
+
+  PlasmidFinder_types_per_sample:
+    label: "PlasmidFinder types per sample"
+    description: "Result (T2): one row per sample (42) with the number of distinct replicon types it carries (0 for a sample with no hit), its source, country and year. Raw (T1): the same table as PlasmidFinder with metadata, one row per replicon hit plus one row for a sample with no hit."
+    ingredients:
+    - dataset_id: metadata_schema
+    - dataset_id: PlasmidFinder
+    steps: !include '1_test_data_ST22_dummy/wrangling/PlasmidFinder_types_per_sample_wrangling.yaml'
+
   Summary_phenotype_length_fragmentation:
     label: "Summary phenotype length fragmentation"
     description: "Demo: Assembly to prepare plot attempting to link some predicted phenotype categories to some quality metrics. in relation to genome length, and fragmentation (higher number of contigs and lower N50 value)"
@@ -352,6 +379,23 @@ analysis_groups:
         description: "Heatmap with one tile per sample and selected virulence gene, coloured by whether the gene was detected."
         spec: !include '1_test_data_ST22_dummy/plots/integration_plot.yaml'
 
+  Plasmids:
+    label: "Plasmid replicons"
+    description: "Which plasmid replicon types the samples carry, by country and by year."
+    plots:
+      plasmid_replicons_by_country:
+        label: "Replicon types by country"
+        description: "Heatmap with one tile per replicon type and country: the colour is the share of the country's samples that carry the type, the number is how many samples (not hits). 0 means none of the samples of the country carries the type. Panels group the types by in how many countries they are found."
+        spec: !include '1_test_data_ST22_dummy/plots/PlasmidFinder_replicon_by_country_heatmap.yaml'
+      plasmid_replicons_by_year:
+        label: "Replicon types by year"
+        description: "Heatmap with one tile per replicon type and year: the colour is the share of the year's samples that carry the type, the number is how many samples (not hits). 0 means none of the samples of the year carries the type. Panels group the types by in how many years they are found."
+        spec: !include '1_test_data_ST22_dummy/plots/PlasmidFinder_replicon_by_year_heatmap.yaml'
+      plasmid_types_per_sample:
+        label: "Replicon types per sample"
+        description: "Bars count samples (one row per sample, all 42) by the number of distinct replicon types they carry, coloured by source; 0 means no replicon hit."
+        spec: !include '1_test_data_ST22_dummy/plots/PlasmidFinder_types_per_sample_bar.yaml'
+
   Cat 🐱:
     label: "🐱 Cat"
     description: The boss's favourite — violin plots
```

## 3. Recipe 1 and recipe 2

`2_test_data_ST22_dummy` was made on 2026-04-23 (`6eb809ca`, "sequential lineage"); the plasmid part came the same day
(`7ece43e7`). Recipe 1 has existed since 2026-04-10. No deployment names recipe 2: the demo, the web demo and the
pipeline test all start recipe 1 (READ `config/deployment/*`).

### 3.1 Comparison, thing by thing

| Thing | Recipe 2 holds | Recipe 1 | Same, different, or only in 2 |
|---|---|---|---|
| Data files | ResFinder, PlasmidFinder and metadata TSV | the same three files, same paths (`assets/test_data/1_test_data_ST22_dummy/`), no copy; recipe 1 also reads 8 more | **identical files** (READ, both recipes' `source.path`) |
| Resistance table (schema) | `amr_data`: filter identity >= 90, overlap >= 60, plus the column `accession` | `ResFinder`: no filter, no `accession`, adds a `status` column | different; both filters remove 0 rows (RUN), 70 rows in both |
| Metadata schema | capital names `Source`, `Year`, `Country` | lower-case `source`, `year`, `country`; same file | different names only |
| Resistance join | `AMR_Profile_Joint`: inner join, year as text, phenotype in lower case, flag `Multiresistant`, 8 columns, 70 rows | `ResFinder_with_metadata`: left join, 9 columns, 70 rows | same 70 rows and values after lower-casing the phenotype (RUN: equal); **the flag `Multiresistant` is only in 2** (Yes: 46 rows of 16 samples; No: 24 rows of 22 samples) |
| Plasmid table and join | `plasmid_data` (filter 90/60), `Plasmid_Profile_Joint` (inner join, 163 rows) | none (a left-over field list only) | **only in 2** (my patch adds the plasmid piece to 1 in a better form) |
| Plots | `multi_resistance_by_country`, `multi_resistance_by_source`, `plasmid_prevalence_by_country` | 17 plots, none on multi-resistance or plasmids; `amr_heatmap` shows genes by sample | the three are **only in 2** |
| Groups | `AMR_Insight`, `Plasmid_Insight` | 5 groups | only in 2 |
| Doc in folder | `README.md` says "isolates resistant to >= 2 antimicrobial classes"; the formula counts distinct drugs (item A1 of RECIPE-FIXES-1) | none | text is stale |

All 17 plots of recipe 1 and its other collections and schemas are only in recipe 1.

Tests and baselines that name recipe 2 (RUN: `git grep`):
- `app/tests/test_amr_multiresistance_formula.py` (5 tests): the flag of `AMR_Profile_Joint`.
- `app/tests/equality/` (73 tests; 78 collected together with the 5 above): `reference_2_test_data_ST22_dummy.py` (hand-written
  Polars and plotnine reading of recipe 2), `checks.py`, `scenarios.py` (the `clean` scenario runs the shipped recipe),
  `make_dirty_data.py`, `test_recipe_equals_hand_written.py`, `test_findings_open.py`, `open_findings.py`, `FINDINGS.md`
  (F1 is about the flag), `README.md`; 4 staged copies `recipes/2_test_data_ST22_dummy_*.yaml` with 4 folders (192 KB)
  and `data/` with 3 folders of dirty data (84 KB). Recipe 2 is the only recipe with such a hand-written check.
- `test_anchor_determinism.py` and `test_render_every_plot.py`: both list recipe 2 by name (3 plot cases).
- Golden: `baseline.json` recipe 2 block: t1 2, t2 2, plots 3 (hashes `dfcf4e8f...` for both AMR collections and plots,
  `28489f30...` for the plasmid ones); `categorical_content_before.json` and `categorical_counts_before.json`: one block each
  (line 684 in the first).
- Tests that read every recipe by glob (checker, descriptions, seeds, categorical, declared missing values) pass either way.
Docs and rules that name it: `docs/workflows/blueprint_architect.qmd:258` (a Quarto include of its plot file: a render
would fail), `docs/appendix/Standards_yaml.qmd:231`, `.claude/rules/rules_agent_role_bioscientist.md:188,347,349`,
`.claude/rules/workspace_standard.md:110-111`, `.claude/workflows/audit_exclusions.yaml:152`,
`assets/scripts/create_test_deployment.py` (3 lines of help text), `assets/scripts/migrate_plot_specs.py:392`,
`scripts/audit_data_analysis_recipe_coherence.py:30`, `tree.txt`, `.claude/knowledge/dependency_index.md` (generated),
`.claude/tasks/tasks.md` (RECIPE-SCIENCE-1 and GATE-CHECKER-1 text). Audit logs and the archive name it too and are history.
Not related: `assets/test_data/duplicated_1_test_data_ST22_dummy/` is a copy of the DATA (used by the pipeline test
deployment and `libs/transformer/tests/test_all_missing_column.py`); it is not recipe 2.

### 3.2 Path (a): MERGE what recipe 2 adds into recipe 1 (nothing is done now)

What moves:
1. The flag. A new join `ResFinder_multiresistance` in recipe 1 (ingredients metadata and `ResFinder`, left join, the
   phenotype lower-cased, the flag from the same formula, published columns), built from the fragment
   `2_.../assembly/AMR_Profile_Joint.yaml` moved to `1_.../wrangling/ResFinder_Multiresistance_wrangling.yaml`.
   A new join, not a change of `ResFinder_with_metadata`, so no existing hash moves.
2. The two multi-resistance plots move to `1_.../plots/` (column names change to lower case: `Year` to `year`, `Source` to
   `source`, `Country` to `country`) and a group `AMR Insight` in recipe 1.
3. The plasmid piece: not moved; replaced by section 2.4 (it counts samples, keeps all samples, and has the best-hit rule).
   The old `plasmid_prevalence_by_country` plot (hits, by year and country) goes away with recipe 2.
4. Tests: `test_amr_multiresistance_formula.py` and the equality files are re-pointed to the new join and the renamed
   columns (the hand-written reference gets lower-case names; it must be re-written, not adjusted to the engine, by the
   rule of its README); `FINDINGS.md` F1 keeps its text.
5. Golden: recipe 1 gains new entries (the join in t1 and t2 and 2 plots); the recipe 2 block is deleted; the existing
   entries of recipe 1 do not move. Hashes of the moved collection change because the columns are lower case.
6. Then path (b) for what is left (the list below), because nothing is left to keep.
What a reader gains: one recipe to learn, the multi-resistance view in the main demo, the only hand-checked logic
(73 + 5 tests) stays alive on the shipped recipe, one data description. Cost: a medium task (the reference rewrite is the
largest part), and a change of the plot titles and axis names is needed (`Year` is a text label in recipe 2; recipe 1
has `year` as a number: the plots need the label column or a cast step).

### 3.3 Path (b): REMOVE recipe 2 (nothing is done now)

Goes: `2_test_data_ST22_dummy.yaml`, its folder (`assembly` 2, `input_fields` 3, `plots` 3, `wrangling` 2, `README.md`:
11 files); the tests `test_amr_multiresistance_formula.py` and `app/tests/equality/` with its 4 staged recipes, 3 data
folders and `FINDINGS.md`/`README.md` (or the equality scheme is re-built on recipe 1); the entry of recipe 2 in
`test_anchor_determinism.py` and `test_render_every_plot.py` (one string each); the recipe 2 block of the three golden
files (7 entries and 2 blocks); the doc and rule lines listed above (the Quarto include must change or the docs do not
render); `audit_exclusions.yaml:152`; the help text of two scripts; `tree.txt`; the task text. Changes with it: the
dependency index when regenerated.
Lost: the multi-resistance flag and its two plots; the only hand-written equality check of the recipe results (73
tests) and the dirty-data scenarios, unless re-built; the old plasmid plot (replaced by section 2.4). Nothing in the app
changes for a user of the demo (all deployments start recipe 1).

### 3.4 Recommendation

**Merge (a), then remove (b), in that order**, and do the plasmid piece (section 2) first or with it. Reason: recipe 2
is not a duplicate of recipe 1; it holds the multi-resistance science and the equality tests, which are the only checks
that compare the engine with a hand reading. Removing it now would lose both. If she decides that the multi-resistance
flag is not wanted (RECIPE-SCIENCE-1, hits against samples, is still open), then (b) alone is clean and cheaper, and the
equality scheme should be rebuilt on recipe 1.

## 4. Points only Eve can answer

I checked `tmpAI/panel/adr/ledger.md` and `.claude/tasks/tasks.md`: no record decides the plasmid points below. Two
records bear on them: N9 (ledger, "per sample then per duplicate, keep the best identity and coverage", for AMR genes)
and RECIPE-SCIENCE-1 (tasks.md: hits against samples, pending).

1. **Merge or remove recipe 2?** (a) merge the multi-resistance part, then remove; (b) remove now; (c) keep both for
   now. Default: (a). Nothing is touched until she answers. Note the link to point 6.
2. **Colour of the heatmaps.** (a) colour = share of the group's samples, number = count (drawn); (b) colour = count.
   Default (a): a country of 28 samples would always look darker than one of 4 in (b).
3. **Best hit per sample and type in the PlasmidFinder table** (same rule as N9). Default: yes (150 rows, tie to the
   lowest accession); it changes no heatmap number, only T1 (163 to 150 rows). Say no if she wants every hit kept.
4. **Thresholds.** The file is cut at 90 identity and 60 coverage (the command-line default); the web service default is
   95 and 60. Default: keep 90/60 and say it in the description. She may want 95 for the real data.
5. **A sample with no hit counts as "no replicon found", not "not analysed".** The recipe puts it in the group size (France
   n=4). Only she knows whether the pipeline writes no row for a plasmid-free isolate. Default: yes, as drawn.
6. **Hits or samples (RECIPE-SCIENCE-1).** The three recipe 2 plots count hits; mine count samples. If she keeps recipe 2's
   plots, the same choice (rows or samples) is open there. Default: samples, and the plot title says so.
7. **Plot's own part before the tier 3 reader exists.** (a) the plot spec `filters` (drawn; one shared table, 108 rows
   with a `group_type` column that a reader of the table sees); (b) two collections, each with its own tier 2 (a table with
   no `group_type`, the tier 1 shared through one include file, twice the files); (c) wait for the reader and put the
   group filter in `steps.tier3`. Default: (a), and move it to tier 3 when the reader exists.
8. **Golden baseline.** 7 new entries in recipe 1, no old hash changes (checked). Default: regenerate in the commit that
   adds the plots, after she has seen the pictures. Nothing is regenerated now.
9. **The overlap column is not trustworthy in this dummy file** (values above 100, no link to the HSP text). Default:
   keep using it only for the 60 filter; no plot uses it. Tell the data owner if the real files look the same.
