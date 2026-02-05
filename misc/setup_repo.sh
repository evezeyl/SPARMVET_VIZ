#!/bin/bash

# Repository Scaffolding Script for Fedora 43
# Target: project_root

# 1. Create Directories
mkdir -p libs/bio_wrangling/src \
         libs/bio_wrangling/tests \
         libs/bio_viz_core/src \
         libs/bio_viz_core/tests \
         src/app_shell/tests \
         src/ingestion/tests \
         src/utils/tests \
         tests \
         data \
         config/templates \
         config/species_manifests \
         docs/modules \
         .github/workflows

# 2. Create Files
# libs/bio_wrangling
touch libs/bio_wrangling/src/__init__.py \
      libs/bio_wrangling/src/clean_logicA.py \
      libs/bio_wrangling/src/clean_logicB.py \
      libs/bio_wrangling/src/clean_logicC.py \
      libs/bio_wrangling/tests/test_bio_wrangling.py

# libs/bio_viz_core
touch libs/bio_viz_core/src/__init__.py \
      libs/bio_viz_core/src/plot_factory.py \
      libs/bio_viz_core/src/base.py \
      libs/bio_viz_core/src/geoms.py \
      libs/bio_viz_core/src/bar_logic.py \
      libs/bio_viz_core/src/scatter_logic.py \
      libs/bio_viz_core/tests/test_viz_core.py

# src/app_shell
touch src/app_shell/__init__.py \
      src/app_shell/ui_components.py \
      src/app_shell/tests/test_ui_render.py

# src/ingestion
touch src/ingestion/__init__.py \
      src/ingestion/adapter_A.py \
      src/ingestion/adapter_B.py \
      src/ingestion/adapter_C.py \
      src/ingestion/adapter_D.py \
      src/ingestion/adapter_metadata.py \
      src/ingestion/tests/test_ingestion.py

# src/utils
touch src/utils/__init__.py \
      src/utils/discovery.py \
      src/utils/loaders.py \
      src/utils/schema.py \
      src/utils/tests/test_utils.py

# Root level and other directories
touch tests/test_skeleton_flow.py \
      tests/test_configuration.py \
      pyproject.toml \
      data/mock_bio_data.csv \
      data/mock_metadata.csv \
      config/templates/species_schema.yaml \
      config/species_manifests/ecoli.yaml \
      config/species_manifests/saureus.yaml \
      docs/_quarto.yml \
      docs/index.qmd \
      docs/architecture.qmd \
      docs/contribution_rules.qmd \
      docs/tree.qmd \
      app.py \
      Makefile \
      requirements.txt \
      manifest.json \
      CREDITS.md \
      .gitignore

# .github/workflows
touch .github/workflows/test_suite.yml \
      .github/workflows/lint_and_format.yml \
      .github/workflows/docs_build.yml \
      .github/workflows/deploy-connect.yml

echo "Structure created successfully! (Excluding README and LICENSE)"