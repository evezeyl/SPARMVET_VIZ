---
description: Unified Workflow for Transformer Translation and Assembly Testing
---
# ⚙️ Transformer Testing Workflow

This workflow establishes the phase-gate for transformer/assembly interactions.

## 1. Engine

The primary orchestration engine is `debug_assembler.py`.
*(Note: atomic Layer 1 decorators may use `debug_wrangler.py` but must follow the exact same Evidence Loop rules).*

## 2. Protocol

Follow the Universal Evidence Loop:

1. Define the input data and data analysis recipe YAML.
2. Run `debug_assembler.py` using CLI.
3. **Artifact Routing**:
   - Materialize headless outputs strictly to `tmp/data_analysis_recipe_test/{data_analysis_recipe_basename}/`.
   - If doing automatic library testing (e.g. extending an assembler function), output to `tmp/transformer/`.
4. Present `df.glimpse()` prior to requesting `@verify`.
