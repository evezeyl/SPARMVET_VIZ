# Architecture Decision Record: Tiered Data Lifecycle (ADR-024)

**Target Component:** libs/transformer & app/server
**Status:** Implemented (Phases 3–4+; in production)

## Context & Problem

The pipeline was suffering from severe memory and processing bottlenecks (e.g., 22-minute render times) during visualization operations. This occurred because the system was attempting to rerun the entire multi-source assembly and wrangling pipeline (Layers 1 and 2) for every single UI interaction or visualization request.

## Decision

We implemented a **Tiered Data Lifecycle** to drastically decouple the heavy relational assembly phase from the lightweight UI exploration phase.

- **Tier 1 (The Anchor)** represents the heavy, one-time generation of the fully joined dataset, strictly materialized to disk via Parquet.
- **Tier 2 (The View)** represents the transient, ultra-fast queries run against the Parquet anchor using Predicate Pushdown and Lazy evaluation. This tier can hold data transformations necessary for the visualization (eg. long format transformation for the plot, aggregation, etc.) but NOT filtering or selection of data (Ensure that this is specified in the documentation. Reason being that raw data actually viewed are from the data tier 1, and that tier 2 is to allow fast plotting). Implement a defensive programming approach to ensure that the data tier 2 operations follow those requirements.

Because this is a fundamental architectural decision, we physically split the codebase logic into `persistence/` (for Tier 1) and `performance/` (for Tier 2) subpackages within the `transformer` library.

Tier 3 is the data that is actually viewed by the user. It is a branch of data in Tier 1 where Tier 2 steps have been pre-implemented. In the UI, the user must have a toogle to switch data view of Tier 3 with or without Tier 2 steps activated. Default Tier step 2 is deactivated.

## Consequences

- **Memory Safety**: We no longer overflow RAM on large datasets (e.g., 200k+ rows).
- **Speed**: UI interactions and VizFactory renderings shifted from minutes to milliseconds.
- **Complexity**: Developers must now manage disk state (`session_anchor.parquet`) and ensure the "Short-Circuit Rule" correctly detects when to skip Tier 1 rebuilds.

## Execution Directives

For the exact operational rules, workflow, and mandate enforcement associated with this ADR, agents MUST refer to the authoritative rulebook:
👉 `[rules_data_engine.md](../../.agents/rules/rules_data_engine.md)`
