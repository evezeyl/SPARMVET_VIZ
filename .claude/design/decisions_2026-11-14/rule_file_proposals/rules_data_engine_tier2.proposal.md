# Proposal for `.claude/rules/rules_data_engine.md` section 1 (Tier 2, Persistence)

Status: PROPOSAL, not applied (rule file; Eve decides). Reason: since RECIPE-DATASET-TIER2-1 (issue 77, merge eafc570c) a table that a plot reads directly runs its own tier 2, so "per join" is no longer true.

Current line 27: "Stored as one Parquet per join with a non-empty `tier2` ..."

Proposed: "Stored as one Parquet per table with a non-empty `tier2` (`<name>__T2.parquet`; a table is a join, or a data schema that a plot reads directly), keyed by the chained `tier2_key` (ADR-089); an empty `tier2` means T2 equals T1 and nothing is stored. The list is read in one place, `utils.recipe_tiers.tier2_steps`. `DataOrchestrator.materialize_tier2()` reads the stored file when its key matches, otherwise recomputes it from the valid Tier 1."
