"""Unit tests for PipelineError and make_render_payload (ADR-079).

Run with:
    .venv/bin/python -m pytest libs/utils/tests/test_pipeline_error.py -v
"""
from __future__ import annotations

import pytest

from utils.pipeline_error import PipelineError, make_render_payload, _format_evidence_md


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _minimal() -> PipelineError:
    return PipelineError(
        component="DataWrangler",
        problem="Column 'species' not found in dataset.",
        location="config/manifests/pipelines/test.yaml :: tier1 step 2",
        fix="Add 'species' to input_fields or correct the action column name.",
        who="manifest_author",
        category="wrangling",
        surface="notification",
    )


def _full() -> PipelineError:
    return PipelineError(
        component="DataIngestor",
        problem="Uploaded file has mismatched schema.",
        location="upload: results_2026.tsv",
        fix="Ensure the TSV contains columns: sample_id, species, value.",
        who="data_provider",
        category="ingestion",
        surface="data_import_panel",
        evidence={
            "sample_rows": [{"sample_id": "S1", "species": "cat"}, {"sample_id": "S2", "species": "dog"}],
            "expected_schema": {"sample_id": "String", "species": "String", "value": "Float64"},
            "actual_schema": {"sample_id": "String", "species": "String"},
            "offending_value": "missing 'value' column",
        },
        severity="error",
        plot_scope=("amr_bar", "amr_heatmap"),
        reference="ADR-079",
        related=("step_1",),
    )


# ---------------------------------------------------------------------------
# Construction & validation
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_minimal_fields(self):
        err = _minimal()
        assert err.component == "DataWrangler"
        assert err.severity == "error"
        assert err.plot_scope == ()
        assert err.timestamp == ""
        assert err.evidence is None

    def test_full_fields(self):
        err = _full()
        assert err.plot_scope == ("amr_bar", "amr_heatmap")
        assert err.reference == "ADR-079"
        assert len(err.evidence["sample_rows"]) == 2

    def test_frozen(self):
        err = _minimal()
        with pytest.raises(Exception):
            err.component = "Other"  # type: ignore[misc]

    def test_invalid_who(self):
        with pytest.raises(ValueError, match="who must be one of"):
            PipelineError(
                component="X", problem="p", location="l", fix="f",
                who="unknown_persona", category="wrangling", surface="notification",
            )

    def test_invalid_category(self):
        with pytest.raises(ValueError, match="category must be one of"):
            PipelineError(
                component="X", problem="p", location="l", fix="f",
                who="analyst", category="bad_category", surface="notification",
            )

    def test_invalid_surface(self):
        with pytest.raises(ValueError, match="surface must be one of"):
            PipelineError(
                component="X", problem="p", location="l", fix="f",
                who="analyst", category="wrangling", surface="toast",
            )

    def test_invalid_severity(self):
        with pytest.raises(ValueError, match="severity must be one of"):
            PipelineError(
                component="X", problem="p", location="l", fix="f",
                who="analyst", category="wrangling", surface="notification",
                severity="critical",
            )

    def test_warning_severity(self):
        err = PipelineError(
            component="X", problem="p", location="l", fix="f",
            who="analyst", category="wrangling", surface="notification",
            severity="warning",
        )
        assert err.severity == "warning"

    @pytest.mark.parametrize("who", ["analyst", "data_provider", "manifest_author", "developer", "operator"])
    def test_all_valid_who(self, who):
        err = PipelineError(
            component="X", problem="p", location="l", fix="f",
            who=who, category="wrangling", surface="notification",
        )
        assert err.who == who

    @pytest.mark.parametrize("cat", ["ingestion", "wrangling", "assembly", "visualization", "t3_apply", "blueprint_edit"])
    def test_all_valid_categories(self, cat):
        err = PipelineError(
            component="X", problem="p", location="l", fix="f",
            who="analyst", category=cat, surface="notification",
        )
        assert err.category == cat

    @pytest.mark.parametrize("surface", ["plot_overlay", "notification", "audit_panel", "data_import_panel", "blueprint_inline"])
    def test_all_valid_surfaces(self, surface):
        err = PipelineError(
            component="X", problem="p", location="l", fix="f",
            who="analyst", category="wrangling", surface=surface,
        )
        assert err.surface == surface


# ---------------------------------------------------------------------------
# format()
# ---------------------------------------------------------------------------

class TestFormat:
    def test_error_tag(self):
        out = _minimal().format()
        assert out.startswith("[ERROR]")

    def test_warning_tag(self):
        err = PipelineError(
            component="X", problem="p", location="l", fix="f",
            who="analyst", category="wrangling", surface="notification",
            severity="warning",
        )
        assert err.format().startswith("[WARN]")

    def test_contains_mandatory_fields(self):
        out = _minimal().format()
        assert "DataWrangler" in out
        assert "wrangling" in out
        assert "manifest_author" in out
        assert "notification" in out

    def test_optional_fields_present_when_set(self):
        out = _full().format()
        assert "ADR-079" in out
        assert "amr_bar" in out
        assert "step_1" in out

    def test_optional_fields_absent_when_empty(self):
        out = _minimal().format()
        assert "See:" not in out
        assert "Plots:" not in out
        assert "Related:" not in out
        assert "Evidence:" not in out


# ---------------------------------------------------------------------------
# to_audit_row()
# ---------------------------------------------------------------------------

class TestToAuditRow:
    def test_required_keys(self):
        row = _minimal().to_audit_row()
        for key in ("timestamp", "severity", "category", "component", "problem",
                    "location", "who", "fix", "surface", "plot_scope", "reference", "has_evidence"):
            assert key in row, f"missing key: {key}"

    def test_plot_scope_is_list(self):
        row = _full().to_audit_row()
        assert isinstance(row["plot_scope"], list)
        assert row["plot_scope"] == ["amr_bar", "amr_heatmap"]

    def test_has_evidence_flag(self):
        assert _minimal().to_audit_row()["has_evidence"] is False
        assert _full().to_audit_row()["has_evidence"] is True

    def test_stable_key_set(self):
        row = _minimal().to_audit_row()
        assert set(row.keys()) == {
            "timestamp", "severity", "category", "component", "problem",
            "location", "who", "fix", "surface", "plot_scope", "reference", "has_evidence",
        }


# ---------------------------------------------------------------------------
# with_timestamp()
# ---------------------------------------------------------------------------

class TestWithTimestamp:
    def test_returns_pipeline_error(self):
        result = _minimal().with_timestamp()
        assert isinstance(result, PipelineError)

    def test_timestamp_is_iso(self):
        import re
        ts = _minimal().with_timestamp().timestamp
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts)

    def test_other_fields_unchanged(self):
        original = _minimal()
        stamped = original.with_timestamp()
        assert stamped.component == original.component
        assert stamped.surface == original.surface
        assert stamped.who == original.who

    def test_original_timestamp_empty(self):
        assert _minimal().timestamp == ""


# ---------------------------------------------------------------------------
# make_render_payload()
# ---------------------------------------------------------------------------

class TestMakeRenderPayload:
    def test_required_keys(self):
        payload = make_render_payload(_minimal())
        for key in ("title", "body_md", "evidence_md", "fix_md", "severity",
                    "surface", "plot_scope", "timestamp", "who", "who_label",
                    "category", "component"):
            assert key in payload, f"missing key: {key}"

    def test_title_format(self):
        payload = make_render_payload(_minimal())
        assert "DataWrangler" in payload["title"]
        assert "wrangling" in payload["title"]

    def test_body_md_contains_problem(self):
        payload = make_render_payload(_minimal())
        assert "species" in payload["body_md"]

    def test_location_in_body_md(self):
        payload = make_render_payload(_minimal())
        # location is embedded in body_md (not a top-level payload key)
        assert "Location" in payload["body_md"]

    def test_fix_md_contains_fix(self):
        payload = make_render_payload(_minimal())
        assert "input_fields" in payload["fix_md"]

    def test_who_label_mapping(self):
        cases = {
            "analyst": "Analyst",
            "data_provider": "Data Provider",
            "manifest_author": "Manifest Author",
            "developer": "Developer",
            "operator": "Operator",
        }
        for who, label in cases.items():
            err = PipelineError(
                component="X", problem="p", location="l", fix="f",
                who=who, category="wrangling", surface="notification",
            )
            assert make_render_payload(err)["who_label"] == label

    def test_evidence_md_empty_when_none(self):
        payload = make_render_payload(_minimal())
        assert payload["evidence_md"] == ""

    def test_evidence_md_populated_when_present(self):
        payload = make_render_payload(_full())
        assert payload["evidence_md"] != ""

    def test_plot_scope_is_list(self):
        payload = make_render_payload(_full())
        assert isinstance(payload["plot_scope"], list)
        assert "amr_bar" in payload["plot_scope"]

    def test_reference_in_fix_md(self):
        payload = make_render_payload(_full())
        assert "ADR-079" in payload["fix_md"]


# ---------------------------------------------------------------------------
# _format_evidence_md() — evidence size caps
# ---------------------------------------------------------------------------

class TestFormatEvidenceMd:
    def test_sample_rows_capped_at_5(self):
        rows = [{"col": f"v{i}"} for i in range(10)]
        md = _format_evidence_md({"sample_rows": rows})
        # Count data rows (excluding header and separator)
        data_lines = [l for l in md.split("\n") if l.startswith("| v")]
        assert len(data_lines) == 5

    def test_truncation_notice_shown(self):
        rows = [{"col": f"v{i}"} for i in range(10)]
        md = _format_evidence_md({"sample_rows": rows})
        assert "5 more rows truncated" in md

    def test_no_truncation_notice_at_exactly_5(self):
        rows = [{"col": f"v{i}"} for i in range(5)]
        md = _format_evidence_md({"sample_rows": rows})
        assert "truncated" not in md

    def test_schema_diff_table_rendered(self):
        evidence = {
            "expected_schema": {"col_a": "String"},
            "actual_schema": {"col_a": "Float64"},
        }
        md = _format_evidence_md(evidence)
        assert "Expected" in md
        assert "Actual" in md
        assert "col_a" in md

    def test_schema_columns_capped_at_50(self):
        expected = {f"col_{i}": "String" for i in range(60)}
        actual = {f"col_{i}": "Float64" for i in range(60)}
        md = _format_evidence_md({"expected_schema": expected, "actual_schema": actual})
        # The caps are applied at 50 keys each before union-sort
        assert md.count("| `col_") <= 50

    def test_scalar_keys_rendered(self):
        md = _format_evidence_md({"offending_value": "bad_value", "file_path": "upload.tsv"})
        assert "offending_value" in md
        assert "file_path" in md
        assert "bad_value" in md

    def test_empty_evidence_returns_empty(self):
        assert _format_evidence_md({}) == ""

    def test_unknown_keys_rendered_as_scalar(self):
        md = _format_evidence_md({"my_custom_key": 42})
        assert "my_custom_key" in md
        assert "42" in md
