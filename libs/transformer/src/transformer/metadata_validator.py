import polars as pl
from typing import Dict, Any
import difflib
from utils.errors import DataAnalysisRecipeError, TransformationError

# @deps
# provides: class:MetadataValidator, method:validate, method:validate_types
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-034
# @end_deps


class MetadataValidator:
    """
    Ensures user-provided data aligns with data analysis recipe contracts (ADR-013, ADR-034).
    Validates column existence, data types, and primary key integrity.
    """

    # Data analysis recipe type name -> Polars dtype. Used by enforce_schema (the cast) and validate_types
    # (the check before a cast), so the two always agree.
    DTYPE_MAP = {
        # canonical data analysis recipe vocabulary (input_fields / output_fields)
        "numeric": pl.Float64,
        "categorical": pl.Categorical,
        "date": pl.Date,
        # aliases / legacy names
        "utf8": pl.Utf8,
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

    def validate_types(self, lf: pl.LazyFrame, contract: Dict[str, Any], context: str = "Input",
                       max_examples: int = 3) -> None:
        """Check that every value can be cast to the type the data analysis recipe declares (issue #11).

        Run this before an uploaded file is written: enforce_schema casts lazily, so a text value
        in a numeric column only fails later, when the data is read. Only numeric and date types
        can fail; 'categorical' and 'utf8' accept anything, so IDs written as digits import as text.
        Raises DataAnalysisRecipeError naming each column and a few offending values.
        """
        if not contract:
            return
        names = lf.collect_schema().names()
        problems = []
        for col, props in contract.items():
            dtype = self.DTYPE_MAP.get(props.get("type", "categorical"))
            if col not in names or dtype is None or dtype in (pl.Categorical, pl.Utf8):
                continue
            bad = (
                lf.select(pl.col(col).cast(pl.Utf8).alias("v"),
                          pl.col(col).cast(dtype, strict=False).alias("c"))
                .filter(pl.col("v").is_not_null() & pl.col("c").is_null())
                .select(pl.col("v"))
            )
            examples = bad.head(max_examples).collect()["v"].to_list()
            if examples:
                shown = ", ".join(repr(v) for v in examples)
                problems.append(f"column '{col}' ({props.get('type')}): {shown}")
        if problems:
            raise DataAnalysisRecipeError(
                f"{context} Values do not match the data analysis recipe types. " + "; ".join(problems),
                tip="Fix these values in the file, or change the column type in the data analysis recipe. "
                    "Columns declared categorical or utf8 accept any text, including digits.",
            )

    def enforce_schema(self, lf: pl.LazyFrame, contract: Dict[str, Any]) -> pl.LazyFrame:
        """
        Force-casts columns and renames according to the data analysis recipe contract.
        Used for atomic cleaning (Layer 1).
        """
        if not contract:
            return lf

        transformed = lf
        for col_name, props in contract.items():
            # 1. Handle Renaming (if 'source_name' is provided)
            # This allows mapping raw headers to standardized internal names
            source = props.get("source_name")
            if source and source in transformed.collect_schema().names() and source != col_name:
                transformed = transformed.rename({source: col_name})

            # 2. Handle Type Casting
            # REMOVED (LEGACY-TYPE-ALIASES-1, Phase 34, 2026-05-22): 'string' and 'character'
            # are no longer accepted. Use 'categorical' (identifiers, repeating values) or
            # 'utf8' (high-cardinality free text). See rules_data_analysis_recipe_structure.md §9.
            _REMOVED_TYPE_ALIASES = {"string", "character"}
            raw_type = props.get("type", "categorical")
            if raw_type in _REMOVED_TYPE_ALIASES:
                raise TransformationError(
                    f"Type alias '{raw_type}' is removed — use 'categorical' (for identifiers "
                    f"and repeating values) or 'utf8' (for high-cardinality free text). "
                    f"Column: '{col_name}'. See rules_data_analysis_recipe_structure.md §9.",
                    tip=f"Replace 'type: {raw_type}' with 'type: categorical' in the data analysis recipe "
                        f"input_fields / output_fields / final_contract for column '{col_name}'."
                )

            target_type = raw_type
            if target_type in self.DTYPE_MAP:
                try:
                    transformed = transformed.with_columns(
                        pl.col(col_name).cast(self.DTYPE_MAP[target_type])
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
