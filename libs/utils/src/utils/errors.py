# libs/utils/src/utils/errors.py
# @deps
# provides: class:SPARMVET_Error, class:IngestionError, class:TransformationError, class:VisualizationError, class:DataAnalysisRecipeError
# consumes: libs/utils/src/utils/pipeline_error.py (PipelineError — type hint + optional carried instance, ADR-079/ADR-094)
# consumed_by: libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/ingestion/src/ingestion/ingestor.py, app/handlers/home_theater.py (reads .pipeline_error)
# doc: .claude/knowledge/architecture_decisions.md#ADR-079, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
"""
Found 2026-11-08 (ADR-094, PIPELINE-ERROR-WIRE-2): every raise site in the 4 library files
above already built a rich PipelineError (problem, fix, who, category, evidence) and then
discarded it in favour of a plain SPARMVET_Error subclass carrying only message+tip -- ADR-079's
own "to_pipeline_error() adapter, opt-in" migration path was never implemented, so nothing
catching these exceptions could ever reach the richer fields. Fixed here by having
SPARMVET_Error optionally carry the original PipelineError instance directly (no information
lost, no new exception type, no change to any existing constructor call that doesn't pass it) --
a Shiny-layer catch point reads `getattr(exc, "pipeline_error", None)` instead of
`isinstance(exc, PipelineError)`, which can never be true for these library exceptions.
"""
from typing import Optional

from utils.pipeline_error import PipelineError


class SPARMVET_Error(Exception):
    """Base exception class for all SPARMVET_VIZ errors."""

    def __init__(self, message: str, context: str = "General", tip: str = "Check project logs for details.",
                 pipeline_error: Optional[PipelineError] = None):
        self.message = message
        self.context = context
        self.tip = tip
        self.pipeline_error = pipeline_error
        super().__init__(self.message)


class IngestionError(SPARMVET_Error):
    """Raised when file ingestion or file system operations fail."""

    def __init__(self, message: str, tip: str = "Verify file path existence and read permissions.",
                 pipeline_error: Optional[PipelineError] = None):
        super().__init__(message, context="Ingestion", tip=tip, pipeline_error=pipeline_error)


class TransformationError(SPARMVET_Error):
    """Raised when data wrangling or Polars transformations fail."""

    def __init__(self, message: str, tip: str = "Verify column presence and transformation parameters in YAML.",
                 pipeline_error: Optional[PipelineError] = None):
        super().__init__(message, context="Transformation", tip=tip, pipeline_error=pipeline_error)


class VisualizationError(SPARMVET_Error):
    """Raised when VizFactory fails to map data to plot Geoms."""

    def __init__(self, message: str, tip: str = "Verify mapping keys (x, y, fill) exist in the data schema.",
                 pipeline_error: Optional[PipelineError] = None):
        super().__init__(message, context="Visualization", tip=tip, pipeline_error=pipeline_error)


class DataAnalysisRecipeError(SPARMVET_Error):
    """Raised when YAML data analysis recipe structure is malformed or missing required keys."""

    def __init__(self, message: str, tip: str = "Check YAML indentation and ensure required keys (input_fields, wrangling, output_fields) are present.",
                 pipeline_error: Optional[PipelineError] = None):
        super().__init__(message, context="DataAnalysisRecipe", tip=tip, pipeline_error=pipeline_error)
