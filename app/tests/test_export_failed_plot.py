"""A plot that could not be drawn is written once in the bundle, and the report does not link a picture that is not there (VIZ-STANDARD-1, V7).

# @deps
# consumes: app/handlers/export_handlers.py (failed_plot_stub, plot_report_lines), libs/viz_factory
# @end_deps
"""
import matplotlib
import polars as pl

matplotlib.use("Agg")

from app.handlers.export_handlers import failed_plot_stub, plot_report_lines
from utils.errors import IngestionError
from utils.pipeline_error import PipelineError
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1.0, 2.0], "y": [1.0, 2.0]})


def real_failure():
    plot = VizFactory().render(DF, {"plots": {"p": {"target_dataset": "d", "mapping": {"x": "x", "y": "y"},
                                                    "layers": [{"name": "geom_point", "params": {"size": "big"}}]}}}, "p")
    try:
        plot.save("never.png", verbose=False)
    except Exception as exc:   # noqa: BLE001 - the error the export catches
        return exc
    raise AssertionError("the plot should not draw")


def test_the_stub_says_the_message_once_and_not_the_fix_line_again():
    error = real_failure()
    stub = failed_plot_stub(error)
    assert stub == f"Plot render failed:\n{error}"
    assert stub.count("write a number") == 1
    assert "Fix (" not in stub


def test_an_error_whose_message_does_not_hold_the_fix_still_gets_the_fix_line():
    pe = PipelineError(component="DataIngestor", problem="cannot read", location="x", fix="check the file", who="analyst",
                       category="ingestion", surface="data_import_panel")
    stub = failed_plot_stub(IngestionError("cannot read", pipeline_error=pe))
    assert "Fix (analyst): check the file" in stub


def test_an_error_without_a_record_is_the_message_only():
    assert failed_plot_stub(ValueError("boom")) == "Plot render failed:\nboom"


def test_a_drawn_plot_is_linked_in_the_report():
    lines = plot_report_lines("p", "A plot", "cap", "fig-p", "png", None)
    assert "![cap](_render/p.png){#fig-p width=95%}" in lines


def test_a_plot_that_was_not_drawn_has_no_figure_link_and_says_why():
    error = real_failure()
    lines = plot_report_lines("p", "A plot", "cap", "fig-p", "png", str(error))
    text = "\n".join(lines)
    assert "![" not in text and "_render/" not in text, "a link to a file that is not in the bundle"
    assert "This plot was not drawn." in text and "'size' is not a number" in text
    assert "plots/p_ERROR.txt" in text
    assert lines[0] == "### A plot"
