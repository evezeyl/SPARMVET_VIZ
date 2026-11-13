Purpose
-------
This directory is a duplicate of 1_test_data_ST22_dummy, used exclusively to test
the production connector path (data_lookup: by_dataset_id).

In production, a pipeline (Galaxy, IRIDA) writes output files to a known location
and the connector provides that location as raw_data_dir. The ingestor discovers
files by schema ID name — it does NOT use source.path entries from the data analysis recipe.

This directory simulates "pipeline output landed here" by using clean filenames
(schema ID as filename, no date suffix) so the ingestor finds each file by its exact name
directly. The 1_test_data_ST22_dummy directory keeps the original timestamped
filenames and source.path entries for development/data_analysis_recipe testing.

Naming convention
-----------------
Files are named exactly as their schema ID in the data analysis recipe (+ .tsv), so that
ingestor.find_file(schema_id) finds them by the exact name `<schema id>.tsv`:

  Summary.tsv              ← schema: Summary
  Summary_quality.tsv      ← schema: Summary_quality (copy of Summary.tsv)
  Quality_metrics.tsv      ← schema: Quality_metrics
  Detailed_summary.tsv     ← schema: Detailed_summary  (note lowercase s)
  FastP.tsv                ← schema: FastP
  Quast.tsv                ← schema: Quast
  Bracken.tsv              ← schema: Bracken
  ResFinder.tsv            ← schema: ResFinder
  MLST.tsv                 ← schema: MLST  (the file is named after the dataset id: no fuzzy search)
  metadata_schema.tsv      ← schema: metadata_schema
  PlasmidFinder.tsv        ← not in current ST22 data analysis recipe; kept for future use

Schemas not represented (VirulenceFinder, APEC_STEC_virulence_genes) will fail
gracefully with a warning — those schemas depend on external reference data not
produced by the local pipeline.

Launch commands (see EVE_WORK/notes/cheatsheat.md)
---------------------------------------------------
Used with pipeline_test.yaml (data_lookup: by_dataset_id, raw_data → this dir):

  pipeline-static app features:
    SPARMVET_DEPLOYMENT=$ROOT/config/deployment/pipeline_test/pipeline_test.yaml \
    SPARMVET_APP_FEATURES=$ROOT/config/app_features/pipeline-static.yaml \
      $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001

  pipeline-exploration-simple app features:
    SPARMVET_DEPLOYMENT=$ROOT/config/deployment/pipeline_test/pipeline_test.yaml \
    SPARMVET_APP_FEATURES=$ROOT/config/app_features/pipeline-exploration-simple.yaml \
      $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001

Origin
------
Duplicated from 1_test_data_ST22_dummy (same data, different filenames).
Original generation scripts are documented in 1_test_data_ST22_dummy/README.txt.
