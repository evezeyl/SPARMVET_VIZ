# Session Handoff: @dasharch Project Reconstitution
# Auditor: @dasharch
# Date: 2026-03-21

**Overview & Strategy:**
We have successfully reconstituted the SPARMVET_VIZ project state by reconciling legacy documentation with active code reality. The project has shifted to a **'Decorator-First'** and **'YAML-Only'** strategy. All data contracts and wrangling rules are governed by modular YAML manifests in `./config/manifests/pipelines/`, which map directly to a Python **Action Registry** using the `@register_action` decorator pattern. We have purged all "JSON Schema" and "API Mode B" concepts from the near-term roadmap to focus on a high-scalability "Walking Skeleton" powered by **Polars (LazyFrames)** and **Plotnine**.

**Current Code State:**
The backend architecture is ready, featuring a functional `ConfigManager` and a verified `Action Registry` base. Synthetic assets in `./assets/` (ST22 dummy data) are being used to drive prototype validation without external Galaxy dependencies. Critical discrepancies were resolved: the **Visualization Factory** is being refactored from hardcoded `if-elif` logic into a dynamic `@register_plot` plugin system matching the Transformer layer. We have formally prioritized **Plotnine** as the primary artist for the prototype phase, deferring interactive Plotly features to ensure a stable, Tidy-first data-to-visual hand-off.

**Immediate Next Steps:**
The next Agent should begin at the **'Starting Line'** defined in `tasks.md`. The immediate implementation focus is on building out the core wrangling plugins—specifically **`drop_duplicates`** and **`summarize`** decorators in `libs/transformer/src/actions/core/`. Once these are linked to the active Abromics pipeline YAML, the focus will shift to prototyping the **Polars-to-Plotnine** data hand-off (the 'Lazy vs Eager' execution strategy) and populating the currently empty Shiny frontend (`app/src/ui.py` and `server.py`).
