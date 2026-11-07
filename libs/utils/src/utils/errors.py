# libs/utils/src/utils/errors.py
# @deps
# provides: class:SPARMVET_Error, class:IngestionError, class:TransformationError, class:VisualizationError
# consumed_by: libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/viz_factory/src/viz_factory/viz_factory.py
# @end_deps

class SPARMVET_Error(Exception):
    """Base exception class for all SPARMVET_VIZ errors."""

    def __init__(self, message: str, context: str = "General", tip: str = "Check project logs for details."):
        self.message = message
        self.context = context
        self.tip = tip
        super().__init__(self.message)


class IngestionError(SPARMVET_Error):
    """Raised when file ingestion or file system operations fail."""

    def __init__(self, message: str, tip: str = "Verify file path existence and read permissions."):
        super().__init__(message, context="Ingestion", tip=tip)


class TransformationError(SPARMVET_Error):
    """Raised when data wrangling or Polars transformations fail."""

    def __init__(self, message: str, tip: str = "Verify column presence and transformation parameters in YAML."):
        super().__init__(message, context="Transformation", tip=tip)


class VisualizationError(SPARMVET_Error):
    """Raised when VizFactory fails to map data to plot Geoms."""

    def __init__(self, message: str, tip: str = "Verify mapping keys (x, y, fill) exist in the data schema."):
        super().__init__(message, context="Visualization", tip=tip)


class DataAnalysisRecipeError(SPARMVET_Error):
    """Raised when YAML data analysis recipe structure is malformed or missing required keys."""

    def __init__(self, message: str, tip: str = "Check YAML indentation and ensure required keys (input_fields, wrangling, output_fields) are present."):
        super().__init__(message, context="DataAnalysisRecipe", tip=tip)
