# Archive: Phase 9 Integration, QA & Documentation Sync (100% DONE)

## 🟢 Phase 9: Triple-Source AMR Integration (FIGSHARE DATASET)
>
> Dataset: Chung (2023), CC-BY 4.0, <https://doi.org/10.6084/m9.figshare.21737288.v1>

- [x] **fg_metadata.csv → fg_metadata.tsv** (991 samples, 6 cols) — `libs/transformer/tests/data/`
- [x] **fg_phenotypes.csv → fg_phenotypes.tsv** (18,438 rows, 4 cols) — `libs/transformer/tests/data/`
- [x] **fg_genotypes.csv → fg_genotypes.tsv** (10,840 rows, 7 cols) — `libs/transformer/tests/data/`
- [x] **Pipeline Manifest:** `config/manifests/pipelines/figshare_integration.yaml`
- [x] **Integration Script:** `assets/scripts/figshare_triple_integration.py`
- [x] **Verified Join:** `tmp/integration/figshare_join_check.tsv`
- [x] **Plot A** — Phenotype per Antibiotic: `tmp/integration/plot_A_phenotype_per_antibiotic.png`
- [x] **Plot B** — Gene Family per Host: `tmp/integration/plot_B_gene_family_per_host.png`
- [x] **Plot C** — Resistance Class per Host: `tmp/integration/plot_C_resistance_class_per_host.png`
- [x] **Plot Script:** `assets/scripts/figshare_plot_integration.py`

## 🛡️ Library Integrity & Quality Assurance (NEW MANDATE)

- [x] **Standardize Transformer Integrity:** `transformer_integrity_suite.py` deployed and verified (21/21 actions).
- [x] **Viz Factory Integrity Suite:** `viz_factory_integrity_suite.py` implemented and executed (105/123 components).
- [x] Automated component discovery (123 total).
- [x] 105 components pass 1:1:1 Evidence Loop.
- [x] Materialized `tmp/viz_factory_integrity_report.txt`.
- [x] **Project-Wide Compliance:** Integrity Suite Mandate codified in `project_conventions.md`.

## 🟡 Documentation Dev-to-User Sync (PHASE 11)

- [x] **Audit & Harvest Knowledge/Rules**
- [x] **QMD Content Reorganization** (Created 8 new Dev-to-User root and deep-dive files).
- [x] **Quarto Configuration Sync** (`_quarto.yml` updated).
- [x] **Library READMEs Enforced** (Linked correctly to `docs/`).
- [x] **Docs Registry Generation** (`tmp/docs_registry.txt` materialized).
- [x] **Split-Documentation Strategy Implemented.**
- [x] **Rulebook Homogenization & Test Standardizing**
- [x] Draft 5 definitive rulebooks (`rules_documentation_aesthetics.md`, etc.).
- [x] Rename `libs/` test wrappers (`debug_wrangler.py`, `debug_runner.py`).
- [x] **Surgical Architectural Finalization (Phase 11-C)**
- [x] Apply `.aiignore` Boundary Locks vs EVE_WORK and unauthorized folders.
- [x] Implement Data-Source-Centric logic for Tier 1 vs Tier 2 sharing.
- [x] Establish strict `Engines vs Orchestrators` logic in test suites and docs.
