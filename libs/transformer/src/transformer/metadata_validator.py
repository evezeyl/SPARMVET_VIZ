import polars as pl
from typing import Dict, Any
import difflib
from utils.errors import DataAnalysisRecipeError, TransformationError

# @deps
# provides: class:MetadataValidator, method:validate
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-034
# @end_deps


class MetadataValidator:
    """
    Ensures user-provided data has the columns a data analysis recipe declares (ADR-034): names the missing ones and
    suggests the closest spelling. The types are not checked or cast here any more: ingestion applies the declared Polars
    types and fails, naming the column and the values, when a value does not fit.
    """

    def validate(self, lf: pl.LazyFrame, contract: Dict[str, Any], context: str = "Input") -> None:
        """
        Validates the LazyFrame against the specified contract (input_fields or output_fields).
        Raises DataAnalysisRecipeError if mandatory columns are missing.
        """
        if not contract:
            return

        # ADR-034: Heuristic Column Presence Check
        data_cols = lf.collect_schema().names()
        expected_cols = list(contract.keys())
        missing = [c for c in expected_cols if c not in data_cols]

        if missing:
            suggestions = {}
            for m in missing:
                matches = difflib.get_close_matches(
                    m, data_cols, n=1, cutoff=0.6)
                if matches:
                    suggestions[m] = matches[0]

            tip = f"Ensure the {context} file contains the columns defined in the data analysis recipe."
            if suggestions:
                tip += f" Hint: Did you mean {list(suggestions.values())}?"

            raise DataAnalysisRecipeError(
                f"{context} Validation Failed. Missing columns: {missing}",
                tip=tip
            )
