import polars as pl
from typing import Dict, Any
import difflib
from utils.errors import ManifestError, TransformationError

# @deps
# provides: class:MetadataValidator, method:validate
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-034
# @end_deps


class MetadataValidator:
    """
    Ensures user-provided data aligns with manifest contracts (ADR-013, ADR-034).
    Validates column existence, data types, and primary key integrity.
    """

    def validate(self, lf: pl.LazyFrame, contract: Dict[str, Any], context: str = "Input") -> None:
        """
        Validates the LazyFrame against the specified contract (input_fields or output_fields).
        Raises ManifestError if mandatory columns are missing.
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

            tip = f"Ensure the {context} file contains the columns defined in the manifest."
            if suggestions:
                tip += f" Hint: Did you mean {list(suggestions.values())}?"

            raise ManifestError(
                f"{context} Validation Failed. Missing columns: {missing}",
                tip=tip
            )

    def enforce_schema(self, lf: pl.LazyFrame, contract: Dict[str, Any]) -> pl.LazyFrame:
        """
        Force-casts columns and renames according to the manifest contract.
        Used for atomic cleaning (Layer 1).
        """
        if not contract:
            return lf

        transformed = lf
        for col_name, props in contract.items():
            # 1. Handle Renaming (if 'source_name' is provided)
            # This allows mapping raw headers to standardized internal names
            source = props.get("source_name")
            if source and source in transformed.columns and source != col_name:
                transformed = transformed.rename({source: col_name})

            # 2. Handle Type Casting
            dtype_map = {
                # canonical manifest vocabulary (input_fields / output_fields)
                "string": pl.Utf8,
                "numeric": pl.Float64,
                "categorical": pl.Categorical,
                "date": pl.Date,
                # aliases / legacy names
                "utf8": pl.Utf8,
                "character": pl.Utf8,
                "float": pl.Float64,
                "int": pl.Int64,
                "integer": pl.Int64,
                "bool": pl.Boolean,
                "boolean": pl.Boolean,
                # cast-action vocabulary (PascalCase, used in wrangling blocks)
                "Int64": pl.Int64,
                "Float64": pl.Float64,
                "String": pl.Utf8,
                "Boolean": pl.Boolean,
                "Date": pl.Date,
                "Categorical": pl.Categorical,
            }

            target_type = props.get("type", "string")
            if target_type in dtype_map:
                try:
                    transformed = transformed.with_columns(
                        pl.col(col_name).cast(dtype_map[target_type])
                    )
                except Exception as e:
                    raise TransformationError(
                        f"Type Casting Failed for column '{col_name}' to '{target_type}'.",
                        tip=f"Check for non-conformant values in the raw data. Error: {str(e)}"
                    )
            else:
                import warnings
                warnings.warn(
                    f"enforce_schema: unrecognised type '{target_type}' for column "
                    f"'{col_name}' — cast skipped. Add it to MetadataValidator.dtype_map.",
                    stacklevel=2,
                )

        return transformed
