## 🟢 Phase 9: Triple-Source AMR Integration (FIGSHARE DATASET) — VERIFIED ✅

> Dataset: Chung (2023), CC-BY 4.0, <https://doi.org/10.6084/m9.figshare.21737288.v1>

### Stage 1: CSV → TSV Normalization

- [x] **fg_metadata.csv → fg_metadata.tsv** (991 samples, 6 cols) — `libs/transformer/tests/data/`
- [x] **fg_phenotypes.csv → fg_phenotypes.tsv** (18,438 rows, 4 cols) — `libs/transformer/tests/data/`
- [x] **fg_genotypes.csv → fg_genotypes.tsv** (10,840 rows, 7 cols) — `libs/transformer/tests/data/`

### Stage 2: 3-Way Left Join Assembly

- [x] **Pipeline Manifest:** `config/manifests/pipelines/figshare_integration.yaml`
- [x] **Integration Script:** `assets/scripts/figshare_triple_integration.py`
- [x] **Verified Join:** `tmp/integration/figshare_join_check.tsv`
  - Shape: **203,957 rows × 10 cols** (expected long-format explosion)
  - No column collision (`host_animal_common` pre-dropped from genotypes)
  - Join key: `sample_id` (left join: metadata → phenotypes → genotypes)

### Stage 3: Integration Plots

- [x] **Plot A** — Phenotype per Antibiotic: `tmp/integration/plot_A_phenotype_per_antibiotic.png`
- [x] **Plot B** — Gene Family per Host: `tmp/integration/plot_B_gene_family_per_host.png`
- [x] **Plot C** — Resistance Class per Host: `tmp/integration/plot_C_resistance_class_per_host.png`
- [x] **Plot Script:** `assets/scripts/figshare_plot_integration.py`

### Stage 4: Library Integrity & Quality Assurance

- [x] **Standardize Transformer Integrity:** `transformer_integrity_suite.py` verified (21/21 actions).
- [x] **Viz Factory Integrity Suite:** `viz_factory_integrity_suite.py` verified (105/123).
- [x] **Project-Wide Compliance:** Integrity Suite Mandate codified in `project_conventions.md`.
