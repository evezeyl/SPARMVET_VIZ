"""
Automated tests for viz_factory COMPONENT_SCHEMAS (ADR-075).

Verifies that @register_plot_component(ui_schema=...) correctly populates
COMPONENT_SCHEMAS, and that the 7 annotated components from BP-SCHEMA-1 have:
  - Required structural fields
  - Comprehensive params covering the plotnine constructor surface
  - allow_extra_params: True (forward compat with plotnine updates)
  - wraps: [...] linking back to the plotnine function

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/viz_factory/tests/test_component_schemas.py -v
"""
import pytest

# Importing viz_factory runs its __init__.py, which imports all sub-packages
# (geoms, scales, themes, etc.), triggering all @register_plot_component decorators.
import viz_factory  # noqa: F401

from viz_factory.registry import COMPONENT_SCHEMAS

# ── Constants ──────────────────────────────────────────────────────────────────

# Components annotated with ui_schema in BP-SCHEMA-1
ANNOTATED_COMPONENTS = [
    "geom_boxplot", "geom_point", "geom_line", "geom_bar",
    "geom_histogram", "geom_tile", "labs",
]

SEMANTIC_CATEGORIES = {
    "distribution", "correlation", "comparison", "evolution",
    "part-to-whole", "ranking", "annotation", "uncertainty",
}

COMMON_AESTHETIC_PARAMS = {"alpha", "fill", "colour", "size", "linetype"}


# ── Registration ───────────────────────────────────────────────────────────────

class TestRegistration:

    def test_component_schemas_registry_is_populated(self):
        assert isinstance(COMPONENT_SCHEMAS, dict)
        assert len(COMPONENT_SCHEMAS) >= 7, \
            f"Expected >= 7 annotated components, got {len(COMPONENT_SCHEMAS)}"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_annotated_component_in_registry(self, comp_name):
        assert comp_name in COMPONENT_SCHEMAS, \
            f"'{comp_name}' missing from COMPONENT_SCHEMAS; was ui_schema kwarg omitted?"


# ── Structure ──────────────────────────────────────────────────────────────────

class TestSchemaStructure:

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_has_required_top_level_keys(self, comp_name):
        schema = COMPONENT_SCHEMAS[comp_name]
        for key in ("label", "category", "context", "params"):
            assert key in schema, f"Component '{comp_name}' schema missing key '{key}'"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_context_is_plot(self, comp_name):
        ctx = COMPONENT_SCHEMAS[comp_name]["context"]
        assert "plot" in ctx, f"'{comp_name}' must declare 'plot' context"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_allow_extra_params_is_true(self, comp_name):
        assert COMPONENT_SCHEMAS[comp_name].get("allow_extra_params") is True, \
            f"'{comp_name}' must set allow_extra_params: True for plotnine forward compat"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_has_wraps_field(self, comp_name):
        schema = COMPONENT_SCHEMAS[comp_name]
        assert "wraps" in schema, f"'{comp_name}' missing 'wraps' field"
        assert isinstance(schema["wraps"], list) and len(schema["wraps"]) > 0

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_params_is_nonempty_dict(self, comp_name):
        params = COMPONENT_SCHEMAS[comp_name]["params"]
        assert isinstance(params, dict) and len(params) > 0, \
            f"'{comp_name}' must have at least one param in ui_schema"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_each_param_has_widget_and_label(self, comp_name):
        for pname, pdef in COMPONENT_SCHEMAS[comp_name]["params"].items():
            assert "widget" in pdef, f"'{comp_name}.{pname}' missing 'widget'"
            assert "label" in pdef, f"'{comp_name}.{pname}' missing 'label'"


# ── Semantic correctness ───────────────────────────────────────────────────────

class TestSemanticCorrectness:

    def test_categories_are_semantic_not_geom(self):
        """Category must describe visualization purpose, not just say 'geom'."""
        for name in ANNOTATED_COMPONENTS:
            cat = COMPONENT_SCHEMAS[name].get("category")
            assert cat in SEMANTIC_CATEGORIES, \
                f"'{name}' has non-semantic category '{cat}' (should be in {sorted(SEMANTIC_CATEGORIES)})"

    def test_geom_boxplot_is_distribution(self):
        assert COMPONENT_SCHEMAS["geom_boxplot"]["category"] == "distribution"

    def test_geom_point_is_correlation(self):
        assert COMPONENT_SCHEMAS["geom_point"]["category"] == "correlation"

    def test_geom_bar_is_comparison(self):
        assert COMPONENT_SCHEMAS["geom_bar"]["category"] == "comparison"

    def test_geom_line_is_evolution(self):
        assert COMPONENT_SCHEMAS["geom_line"]["category"] == "evolution"

    def test_labs_is_annotation(self):
        assert COMPONENT_SCHEMAS["labs"]["category"] == "annotation"


# ── Parameter coverage — key plotnine kwargs must be present ──────────────────

class TestParameterCoverage:

    def test_geom_boxplot_core_params(self):
        params = COMPONENT_SCHEMAS["geom_boxplot"]["params"]
        for key in ("alpha", "fill", "colour", "size", "width", "notch",
                    "linetype", "position", "stat"):
            assert key in params, f"geom_boxplot missing param '{key}'"

    def test_geom_boxplot_has_outlier_controls(self):
        params = COMPONENT_SCHEMAS["geom_boxplot"]["params"]
        for key in ("outlier_colour", "outlier_shape", "outlier_size"):
            assert key in params, f"geom_boxplot missing outlier param '{key}'"

    def test_geom_point_core_params(self):
        params = COMPONENT_SCHEMAS["geom_point"]["params"]
        for key in ("alpha", "colour", "fill", "size", "shape", "stroke", "na_rm"):
            assert key in params, f"geom_point missing param '{key}'"

    def test_geom_line_has_linetype_controls(self):
        params = COMPONENT_SCHEMAS["geom_line"]["params"]
        for key in ("linetype", "lineend", "linejoin"):
            assert key in params, f"geom_line missing param '{key}'"

    def test_geom_bar_has_stat_options(self):
        params = COMPONENT_SCHEMAS["geom_bar"]["params"]
        assert "stat" in params
        assert "options" in params["stat"]
        assert "count" in params["stat"]["options"]
        assert "identity" in params["stat"]["options"]

    def test_geom_bar_has_position_options(self):
        params = COMPONENT_SCHEMAS["geom_bar"]["params"]
        assert "position" in params
        assert "options" in params["position"]
        for pos in ("stack", "dodge", "fill"):
            assert pos in params["position"]["options"], \
                f"geom_bar position options missing '{pos}'"

    def test_geom_histogram_has_binning_params(self):
        params = COMPONENT_SCHEMAS["geom_histogram"]["params"]
        assert "bins" in params
        assert "binwidth" in params

    def test_geom_tile_has_size_params(self):
        params = COMPONENT_SCHEMAS["geom_tile"]["params"]
        assert "width" in params
        assert "height" in params

    def test_labs_covers_all_standard_aesthetics(self):
        params = COMPONENT_SCHEMAS["labs"]["params"]
        for aes in ("title", "subtitle", "caption", "x", "y",
                    "fill", "colour", "size", "shape", "alpha"):
            assert aes in params, f"labs missing standard aesthetic param '{aes}'"

    def test_all_geoms_have_alpha(self):
        """Every geom should expose alpha (opacity) control."""
        geom_names = [c for c in ANNOTATED_COMPONENTS if c.startswith("geom_")]
        for name in geom_names:
            assert "alpha" in COMPONENT_SCHEMAS[name]["params"], \
                f"'{name}' missing 'alpha' param"


# ── Wraps field correctness ────────────────────────────────────────────────────

class TestWrapsField:

    @pytest.mark.parametrize("comp_name", [c for c in ANNOTATED_COMPONENTS if c != "labs"])
    def test_wraps_references_plotnine(self, comp_name):
        wraps = COMPONENT_SCHEMAS[comp_name]["wraps"]
        assert any(w.get("lib") == "plotnine" for w in wraps), \
            f"'{comp_name}' wraps must reference plotnine lib"

    @pytest.mark.parametrize("comp_name", [c for c in ANNOTATED_COMPONENTS if c != "labs"])
    def test_wraps_attr_path_matches_component_name(self, comp_name):
        wraps = COMPONENT_SCHEMAS[comp_name]["wraps"]
        for w in wraps:
            if w.get("lib") == "plotnine":
                path = w.get("attr_path", [])
                assert comp_name in path, \
                    f"'{comp_name}' wraps attr_path should contain '{comp_name}'"
