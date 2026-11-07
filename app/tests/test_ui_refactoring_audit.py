import unittest
import polars as pl
from pathlib import Path
from app.modules.orchestrator import DataOrchestrator
import os

"""
app/tests/test_ui_refactoring_audit.py
--------------------------------------
Headless UI Logic Audit. 
Ensures the DataOrchestrator can handle the refactored relational 
data analysis recipe structures (ADR-012b, ADR-024) without regression.
"""


class TestUIRefactoringAudit(unittest.TestCase):
    def setUp(self):
        self.data_analysis_recipes_dir = Path("config/data_analysis_recipes/pipelines")
        self.raw_data_dir = Path("assets/test_data/1_test_data_ST22_dummy")
        self.orchestrator = DataOrchestrator(
            self.data_analysis_recipes_dir, self.raw_data_dir)
        self.output_dir = Path("tmp/app_logic_audit")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def test_st22_curiosity_logic(self):
        """Audit: Can the UI load and assemble the Phenotype Curiosity pipeline?"""
        data_analysis_recipe_id = "1_test_data_ST22_dummy"
        collection_id = "Summary_phenotype_length_fragmentation"
        output_path = self.output_dir / "st22_curiosity.parquet"

        # Execute Tier 1 Materialization (UI Logic Path)
        lf = self.orchestrator.materialize_tier1(
            data_analysis_recipe_id, collection_id, output_path)
        df = lf.collect()

        self.assertGreater(
            len(df), 0, "Materialized dataset should not be empty")
        self.assertIn("quality_metric", df.columns,
                      "Should contain unpivoted metrics")
        self.assertIn("phenotype_count", df.columns,
                      "Should contain joined phenotype stats")
        print(f"  [PASS] ST22 Curiosity Logic Verified ({len(df)} rows).")

    def test_st22_anchor_logic(self):
        """Audit: Can the UI handle the primary ST22 Anchor integration?"""
        data_analysis_recipe_id = "1_test_data_ST22_dummy"
        collection_id = "ST22_Anchor"  # The heavy join
        output_path = self.output_dir / "st22_anchor.parquet"

        lf = self.orchestrator.materialize_tier1(
            data_analysis_recipe_id, collection_id, output_path)
        df = lf.collect()

        self.assertGreater(len(df), 0, "Anchor should contain joined data")
        self.assertIn("sequence_type", df.columns)
        print(f"  [PASS] ST22 Anchor Logic Verified ({len(df)} rows).")


if __name__ == "__main__":
    unittest.main()
