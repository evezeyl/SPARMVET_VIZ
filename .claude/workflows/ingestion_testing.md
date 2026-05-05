---
description: Unified Workflow for Ingestion Testing
---
# 📥 Ingestion Testing Workflow

This workflow defines the mandatory verification step for ingestion functionality.

## 1. Engine

The engine for ingestion testing is `debug_ingestor.py`.

## 2. Protocol

Follow the Universal Evidence Loop:

1. Define the YAML configuration targeting ingestion schemas. This manifest MUST adhere strictly to the structural standards defined in `[rules_manifest_structure.md](../rules/rules_manifest_structure.md)`.
2. Run `debug_ingestor.py` using CLI argparse.
3. **Artifact Routing**:
   - Materialize headless results into `tmp/Manifest_test/{manifest_basename}/`.
   - If doing automatic library testing (e.g. testing core ingestion components), output to `tmp/ingestion/`.
4. Output a `df.glimpse()` before requesting `@verify`.
