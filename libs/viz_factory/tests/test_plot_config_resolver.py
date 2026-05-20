"""Unit tests for plot_config_resolver — five-tier cascade truth table.

Tests assert provenance per key for all five tiers and dedup order for layer
kinds, as specified in .claude/design/plot_config_cascade.md §11.

Run with:
    .venv/bin/python -m pytest libs/viz_factory/tests/test_plot_config_resolver.py -v
"""
from __future__ import annotations

import pytest

from viz_factory.plot_config_resolver import (
    resolve_plot_config,
    compute_optimisation_layer,
    _dedupe_layers,
    _layer_dedup_key,
    normalise_plot_spec,
    _BUILTIN_DEFAULTS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _theme_names(layers: list[dict]) -> list[str]:
    return [l["name"] for l in layers if l.get("name", "").startswith("theme_")]


def _layer_names(layers: list[dict]) -> list[str]:
    return [l["name"] for l in layers]


def _tiers(layers: list[dict], name_prefix: str) -> list[str]:
    return [l.get("_tier", "?") for l in layers if l.get("name", "").startswith(name_prefix)]


# ---------------------------------------------------------------------------
# _layer_dedup_key
# ---------------------------------------------------------------------------

class TestLayerDedupKey:
    def test_geom_returns_none(self):
        assert _layer_dedup_key({"name": "geom_bar"}) is None
        assert _layer_dedup_key({"name": "geom_point"}) is None
        assert _layer_dedup_key({"name": "geom_tile"}) is None

    def test_stat_returns_none(self):
        assert _layer_dedup_key({"name": "stat_summary"}) is None
        assert _layer_dedup_key({"name": "stat_bin"}) is None

    def test_theme_family(self):
        assert _layer_dedup_key({"name": "theme_bw"}) == ("theme", None)
        assert _layer_dedup_key({"name": "theme_minimal"}) == ("theme", None)
        assert _layer_dedup_key({"name": "theme_void"}) == ("theme", None)

    def test_coord_family(self):
        assert _layer_dedup_key({"name": "coord_cartesian"}) == ("coord", None)
        assert _layer_dedup_key({"name": "coord_flip"}) == ("coord", None)

    def test_facet_family(self):
        assert _layer_dedup_key({"name": "facet_null"}) == ("facet", None)
        assert _layer_dedup_key({"name": "facet_wrap"}) == ("facet", None)
        assert _layer_dedup_key({"name": "facet_grid"}) == ("facet", None)

    def test_scale_fill_family(self):
        assert _layer_dedup_key({"name": "scale_fill_manual"}) == ("scale_fill", None)
        assert _layer_dedup_key({"name": "scale_fill_brewer"}) == ("scale_fill", None)

    def test_scale_color_family(self):
        assert _layer_dedup_key({"name": "scale_color_manual"}) == ("scale_color", None)
        assert _layer_dedup_key({"name": "scale_colour_manual"}) == ("scale_color", None)

    def test_scale_x_family(self):
        assert _layer_dedup_key({"name": "scale_x_discrete"}) == ("scale_x", None)

    def test_scale_y_family(self):
        assert _layer_dedup_key({"name": "scale_y_log10"}) == ("scale_y", None)

    def test_element_text_per_target(self):
        x = {"name": "element_text", "params": {"target": "axis_text_x", "rotation": 45}}
        y = {"name": "element_text", "params": {"target": "axis_text_y", "size": 8}}
        assert _layer_dedup_key(x) == ("element_text", "axis_text_x")
        assert _layer_dedup_key(y) == ("element_text", "axis_text_y")

    def test_element_text_no_target(self):
        layer = {"name": "element_text", "params": {}}
        assert _layer_dedup_key(layer) == ("element_text", "")


# ---------------------------------------------------------------------------
# _dedupe_layers
# ---------------------------------------------------------------------------

class TestDedupeLayers:
    def test_geoms_accumulate(self):
        """geom layers are never removed regardless of name collision."""
        layers = [
            {"name": "geom_bar", "params": {}},
            {"name": "geom_text", "params": {}},
        ]
        result = _dedupe_layers(layers)
        names = _layer_names(result)
        assert "geom_bar" in names
        assert "geom_text" in names

    def test_same_geom_accumulates(self):
        """Even two identical geom names both survive."""
        layers = [
            {"name": "geom_point", "params": {"color": "red"}},
            {"name": "geom_point", "params": {"color": "blue"}},
        ]
        result = _dedupe_layers(layers)
        assert len([l for l in result if l["name"] == "geom_point"]) == 2

    def test_theme_dedup_keeps_last(self):
        layers = [
            {"name": "theme_bw",      "params": {}, "_tier": "L1"},
            {"name": "theme_minimal", "params": {}, "_tier": "L2"},
        ]
        result = _dedupe_layers(layers)
        themes = _theme_names(result)
        assert themes == ["theme_minimal"]

    def test_coord_dedup_keeps_last(self):
        layers = [
            {"name": "coord_cartesian", "params": {}},
            {"name": "coord_flip",      "params": {}},
        ]
        result = _dedupe_layers(layers)
        coords = [l["name"] for l in result if l["name"].startswith("coord_")]
        assert coords == ["coord_flip"]

    def test_facet_dedup_keeps_last(self):
        layers = [
            {"name": "facet_null", "params": {}},
            {"name": "facet_wrap", "params": {"facets": "~species"}},
        ]
        result = _dedupe_layers(layers)
        facets = [l["name"] for l in result if l["name"].startswith("facet_")]
        assert facets == ["facet_wrap"]

    def test_element_text_dedup_per_axis(self):
        """x and y element_text deduplicate independently."""
        layers = [
            {"name": "element_text", "params": {"target": "axis_text_x", "rotation": 45, "size": 8}},
            {"name": "element_text", "params": {"target": "axis_text_y", "size": 8}},
            {"name": "element_text", "params": {"target": "axis_text_x", "rotation": 0, "size": 10}},  # overrides
        ]
        result = _dedupe_layers(layers)
        x_layers = [l for l in result if l["name"] == "element_text"
                    and l["params"].get("target") == "axis_text_x"]
        y_layers = [l for l in result if l["name"] == "element_text"
                    and l["params"].get("target") == "axis_text_y"]
        assert len(x_layers) == 1
        assert x_layers[0]["params"]["rotation"] == 0   # last wins
        assert len(y_layers) == 1

    def test_empty_list(self):
        assert _dedupe_layers([]) == []

    def test_order_preserved_for_accumulated(self):
        """Non-deduped layers appear in input order."""
        layers = [
            {"name": "geom_col", "params": {}},
            {"name": "theme_bw", "params": {}},
            {"name": "geom_text", "params": {}},
        ]
        result = _dedupe_layers(layers)
        names = _layer_names(result)
        col_idx = names.index("geom_col")
        text_idx = names.index("geom_text")
        assert col_idx < text_idx


# ---------------------------------------------------------------------------
# normalise_plot_spec
# ---------------------------------------------------------------------------

class TestNormaliseSpec:
    def test_flat_aesthetics_promoted_to_mapping(self):
        spec = {"x": "Year", "fill": "Country", "factory_id": "bar_logic"}
        result = normalise_plot_spec(spec)
        assert result["mapping"]["x"] == "Year"
        assert result["mapping"]["fill"] == "Country"

    def test_explicit_mapping_not_overwritten(self):
        spec = {"x": "Year", "mapping": {"x": "Month"}}
        result = normalise_plot_spec(spec)
        assert result["mapping"]["x"] == "Month"

    def test_bar_logic_injects_geom_bar(self):
        spec = {"factory_id": "bar_logic", "x": "Year"}
        result = normalise_plot_spec(spec)
        assert result["layers"][0]["name"] == "geom_bar"

    def test_bar_logic_injects_geom_col_when_y_present(self):
        spec = {"factory_id": "bar_logic", "x": "Year", "y": "count"}
        result = normalise_plot_spec(spec)
        assert result["layers"][0]["name"] == "geom_col"

    def test_heatmap_logic_remaps_color_to_fill(self):
        spec = {"factory_id": "heatmap_logic", "x": "Year", "color": "value"}
        result = normalise_plot_spec(spec)
        assert "fill" in result["mapping"]
        assert "color" not in result["mapping"]

    def test_heatmap_logic_injects_geom_tile(self):
        spec = {"factory_id": "heatmap_logic", "x": "Year", "y": "Gene"}
        result = normalise_plot_spec(spec)
        assert result["layers"][0]["name"] == "geom_tile"

    def test_no_factory_id_no_geom_injected(self):
        spec = {"x": "Year", "layers": []}
        result = normalise_plot_spec(spec)
        assert result["layers"] == []

    def test_existing_geom_not_duplicated(self):
        spec = {
            "factory_id": "bar_logic",
            "x": "Year",
            "layers": [{"name": "geom_bar", "params": {}}],
        }
        result = normalise_plot_spec(spec)
        geom_bars = [l for l in result["layers"] if l["name"] == "geom_bar"]
        assert len(geom_bars) == 1


# ---------------------------------------------------------------------------
# resolve_plot_config — cascade truth table (§11)
# ---------------------------------------------------------------------------

class TestResolvePlotConfigThemeCascade:
    """Truth-table: theme provenance across tiers."""

    def test_theme_only_l1(self):
        """No L2/L4/L5 theme → L1 theme_bw."""
        result = resolve_plot_config({}, {}, None)
        assert result["theme"] == "theme_bw"
        assert result["_provenance"]["theme"] == "L1"

    def test_theme_l2_overrides_l1(self):
        result = resolve_plot_config({}, {"theme": "theme_dashboard"}, None)
        assert result["theme"] == "theme_dashboard"
        assert result["_provenance"]["theme"] == "L2"

    def test_theme_l4_overrides_l2(self):
        result = resolve_plot_config(
            {"theme": "theme_void"},
            {"theme": "theme_dashboard"},
            None,
        )
        assert result["theme"] == "theme_void"
        assert result["_provenance"]["theme"] == "L4"

    def test_theme_l5_overrides_l4(self):
        result = resolve_plot_config(
            {"theme": "theme_void"},
            {"theme": "theme_dashboard"},
            None,
            aesthetic_override={"theme": "theme_minimal"},
        )
        assert result["theme"] == "theme_minimal"
        assert result["_provenance"]["theme"] == "L5"

    def test_l1_theme_layer_present(self):
        result = resolve_plot_config({}, {}, None)
        assert any(l["name"] == "theme_bw" for l in result["layers"])


class TestResolvePlotConfigPaletteCascade:
    def test_palette_default_none(self):
        result = resolve_plot_config({}, {}, None)
        assert result["palette"] is None
        assert result["_provenance"]["palette"] == "L1"

    def test_palette_l2(self):
        result = resolve_plot_config({}, {"palette": "sparmvet_brand"}, None)
        assert result["palette"] == "sparmvet_brand"
        assert result["_provenance"]["palette"] == "L2"

    def test_palette_l4_overrides_l2(self):
        result = resolve_plot_config(
            {"palette": "viridis"},
            {"palette": "sparmvet_brand"},
            None,
        )
        assert result["palette"] == "viridis"
        assert result["_provenance"]["palette"] == "L4"

    def test_palette_l5_fill_palette(self):
        result = resolve_plot_config(
            {"palette": "viridis"},
            {"palette": "sparmvet_brand"},
            None,
            aesthetic_override={"fill_palette": "nvi_official"},
        )
        assert result["palette"] == "nvi_official"
        assert result["_provenance"]["palette"] == "L5"

    def test_palette_l5_fill_color_injects_scale_layer(self):
        result = resolve_plot_config(
            {},
            {},
            None,
            aesthetic_override={"fill_color": "#ff0000"},
        )
        scale_layers = [l for l in result["layers"] if l["name"] == "scale_fill_manual"]
        assert len(scale_layers) == 1
        assert "#ff0000" in scale_layers[0]["params"]["values"]


class TestResolvePlotConfigL5Mutex:
    def test_fill_color_and_fill_palette_mutex(self):
        """Both supplied → fill_palette wins, _l5_mutex_warn=True."""
        result = resolve_plot_config(
            {},
            {},
            None,
            aesthetic_override={"fill_color": "#ff0000", "fill_palette": "nvi_official"},
        )
        assert result["_l5_mutex_warn"] is True
        assert result["palette"] == "nvi_official"
        # No scale_fill_manual since fill_color was discarded
        scale_layers = [l for l in result["layers"] if l["name"] == "scale_fill_manual"]
        assert len(scale_layers) == 0

    def test_no_mutex_warn_with_only_fill_palette(self):
        result = resolve_plot_config(
            {},
            {},
            None,
            aesthetic_override={"fill_palette": "viridis"},
        )
        assert result["_l5_mutex_warn"] is False

    def test_no_mutex_warn_with_only_fill_color(self):
        result = resolve_plot_config(
            {},
            {},
            None,
            aesthetic_override={"fill_color": "#00ff00"},
        )
        assert result["_l5_mutex_warn"] is False


class TestResolvePlotConfigLayerAccumulation:
    def test_geom_layers_accumulate(self):
        """geom_bar and geom_text both survive — no dedup."""
        raw_spec = {
            "factory_id": "bar_logic",
            "x": "Year",
            "layers": [{"name": "geom_text", "params": {}}],
        }
        result = resolve_plot_config(raw_spec, {}, None)
        names = _layer_names(result["layers"])
        assert "geom_bar" in names
        assert "geom_text" in names

    def test_theme_layers_dedup(self):
        """Only one theme_* layer survives — the highest tier."""
        raw_spec = {"theme": "theme_void"}
        plot_defaults = {"theme": "theme_minimal"}
        result = resolve_plot_config(raw_spec, plot_defaults, None)
        themes = _theme_names(result["layers"])
        assert len(themes) == 1
        assert themes[0] == "theme_void"

    def test_coord_layers_dedup(self):
        """Only the last coord layer survives."""
        raw_spec = {"layers": [{"name": "coord_flip", "params": {}}]}
        result = resolve_plot_config(raw_spec, {}, None)
        coords = [l["name"] for l in result["layers"] if l["name"].startswith("coord_")]
        assert coords == ["coord_flip"]


class TestResolvePlotConfigFactoryId:
    def test_factory_id_recorded_in_provenance(self):
        result = resolve_plot_config({"factory_id": "scatter_logic"}, {}, None)
        assert result["factory_id"] == "scatter_logic"
        assert result["_provenance"]["factory_id"] == "L4"

    def test_no_factory_id_is_none(self):
        result = resolve_plot_config({}, {}, None)
        assert result["factory_id"] is None


class TestResolvePlotConfigFacetBy:
    def test_facet_by_injects_facet_wrap(self):
        result = resolve_plot_config({"x": "Year", "facet_by": "Country"}, {}, None)
        assert result["facet_by"] == "Country"
        facet_layers = [l for l in result["layers"] if l["name"] == "facet_wrap"]
        assert len(facet_layers) >= 1
        assert "Country" in facet_layers[-1]["params"]["facets"]

    def test_facet_wrap_not_duplicated_if_explicit(self):
        spec = {
            "x": "Year",
            "facet_by": "Country",
            "layers": [{"name": "facet_wrap", "params": {"facets": "~Country", "ncol": 3}}],
        }
        result = resolve_plot_config(spec, {}, None)
        facets = [l for l in result["layers"] if l["name"] == "facet_wrap"]
        # dedup keeps only the last facet_wrap
        assert len(facets) == 1


class TestResolvePlotConfigFilters:
    def test_filters_default_empty(self):
        result = resolve_plot_config({}, {}, None)
        assert result["filters"] == []
        assert result["_provenance"]["filters"] == "L1"

    def test_filters_from_spec(self):
        filters = [{"column": "species", "op": "eq", "value": "cat"}]
        result = resolve_plot_config({"filters": filters}, {}, None)
        assert result["filters"] == filters
        assert result["_provenance"]["filters"] == "L4"


class TestResolvePlotConfigUnknownKeys:
    def test_unknown_plot_defaults_key_collected(self):
        result = resolve_plot_config({}, {"palette": "viridis", "unknown_key": "x"}, None)
        assert "unknown_key" in result["_unknown_plot_defaults_keys"]

    def test_known_keys_not_in_unknown_list(self):
        result = resolve_plot_config({}, {"palette": "viridis", "theme": "theme_bw"}, None)
        assert "palette" not in result["_unknown_plot_defaults_keys"]
        assert "theme" not in result["_unknown_plot_defaults_keys"]

    def test_no_unknown_keys_returns_empty_list(self):
        result = resolve_plot_config({}, {"palette": "viridis"}, None)
        assert result["_unknown_plot_defaults_keys"] == []


class TestResolvePlotConfigL5GeomOverrides:
    def test_alpha_stored_in_l5_geom_overrides(self):
        result = resolve_plot_config({}, {}, None, aesthetic_override={"alpha": 0.5})
        assert result.get("_l5_geom_overrides", {}).get("alpha") == 0.5

    def test_shape_stored_in_l5_geom_overrides(self):
        result = resolve_plot_config({}, {}, None, aesthetic_override={"shape": "circle"})
        assert result.get("_l5_geom_overrides", {}).get("shape") == "circle"

    def test_no_aesthetic_override_no_geom_overrides_key(self):
        result = resolve_plot_config({}, {}, None)
        assert "_l5_geom_overrides" not in result


class TestResolvePlotConfigMapping:
    def test_mapping_from_flat_spec(self):
        result = resolve_plot_config({"x": "Year", "fill": "Country"}, {}, None)
        assert result["mapping"]["x"] == "Year"
        assert result["mapping"]["fill"] == "Country"
        assert result["_provenance"]["mapping"] == "L4"

    def test_mapping_l1_when_no_spec(self):
        result = resolve_plot_config({}, {}, None)
        assert result["mapping"] == {}
        assert result["_provenance"]["mapping"] == "L1"


class TestResolvePlotConfigPaletteScope:
    def test_palette_scope_fill(self):
        result = resolve_plot_config({"fill": "Country"}, {}, None)
        assert "fill" in result["palette_scope"]

    def test_palette_scope_empty_when_no_aesthetics(self):
        result = resolve_plot_config({"x": "Year"}, {}, None)
        assert result["palette_scope"] == set()

    def test_palette_scope_excludes_fill_when_scale_fill_present(self):
        spec = {
            "fill": "Country",
            "layers": [{"name": "scale_fill_brewer", "params": {}}],
        }
        result = resolve_plot_config(spec, {}, None)
        assert "fill" not in result["palette_scope"]


class TestResolvePlotConfigElementText:
    def test_element_text_empty_when_no_df(self):
        result = resolve_plot_config({"x": "Year"}, {}, None)
        assert result["element_text"] == {}

    def test_element_text_from_spec_layer(self):
        spec = {
            "x": "Year",
            "layers": [
                {"name": "element_text", "params": {"target": "axis_text_x", "rotation": 45}},
            ],
        }
        result = resolve_plot_config(spec, {}, None)
        assert "axis_text_x" in result["element_text"]
        assert result["element_text"]["axis_text_x"]["rotation"] == 45


class TestResolvePlotConfigProvenanceCompleteness:
    def test_provenance_has_mandatory_keys(self):
        result = resolve_plot_config({}, {}, None)
        for key in ("mapping", "palette", "facet_by", "title",
                    "labels", "guides", "filters", "factory_id", "theme"):
            assert key in result["_provenance"], f"missing provenance key: {key}"

    def test_default_provenance_all_l1(self):
        result = resolve_plot_config({}, {}, None)
        for key in ("mapping", "palette", "facet_by", "title",
                    "labels", "guides", "filters", "factory_id", "theme"):
            assert result["_provenance"][key] == "L1", (
                f"expected L1 for {key}, got {result['_provenance'][key]}"
            )


# ---------------------------------------------------------------------------
# compute_optimisation_layer — L3 axis text heuristics
# ---------------------------------------------------------------------------

class TestComputeOptimisationLayer:
    def _make_df(self, x_vals=None, y_vals=None):
        """Build a minimal pandas DataFrame for testing."""
        import pandas as pd
        data = {}
        if x_vals is not None:
            data["x_col"] = x_vals
        if y_vals is not None:
            data["y_col"] = y_vals
        return pd.DataFrame(data)

    def test_returns_empty_when_df_none(self):
        result = compute_optimisation_layer({}, {"x": "x_col"}, None)
        assert result == []

    def test_returns_empty_when_no_mapping(self):
        import pandas as pd
        df = pd.DataFrame({"x_col": ["a", "b"]})
        result = compute_optimisation_layer({}, {}, df)
        assert result == []

    def test_x_long_labels_rotation_45(self):
        import pandas as pd
        vals = [f"verylongname_{i}" for i in range(5)]  # max_len > 12
        df = pd.DataFrame({"x_col": vals})
        layers = compute_optimisation_layer({}, {"x": "x_col"}, df)
        x_layers = [l for l in layers if l["params"].get("target") == "axis_text_x"]
        assert len(x_layers) == 1
        assert x_layers[0]["params"]["rotation"] == 45

    def test_x_medium_labels_rotation_35(self):
        import pandas as pd
        vals = ["medium7x" for _ in range(5)]  # max_len == 8 (> 6, <= 12)
        df = pd.DataFrame({"x_col": vals})
        layers = compute_optimisation_layer({}, {"x": "x_col"}, df)
        x_layers = [l for l in layers if l["params"].get("target") == "axis_text_x"]
        assert len(x_layers) == 1
        assert x_layers[0]["params"]["rotation"] == 35

    def test_x_many_unique_no_rotation(self):
        import pandas as pd
        # 15 unique values, each short — triggers size adjustment (not rotation)
        vals = [f"ab{i}" for i in range(15)]  # n_unique > 12, max_len <= 6
        df = pd.DataFrame({"x_col": vals})
        layers = compute_optimisation_layer({}, {"x": "x_col"}, df)
        x_layers = [l for l in layers if l["params"].get("target") == "axis_text_x"]
        assert len(x_layers) == 1
        assert "rotation" not in x_layers[0]["params"]
        assert x_layers[0]["params"]["size"] == 8

    def test_numeric_x_no_adjustment(self):
        import pandas as pd
        df = pd.DataFrame({"x_col": list(range(20))})
        layers = compute_optimisation_layer({}, {"x": "x_col"}, df)
        x_layers = [l for l in layers if l["params"].get("target") == "axis_text_x"]
        assert x_layers == []

    def test_layer_kind_is_element_text(self):
        import pandas as pd
        vals = [f"verylongname_{i}" for i in range(3)]
        df = pd.DataFrame({"x_col": vals})
        layers = compute_optimisation_layer({}, {"x": "x_col"}, df)
        for layer in layers:
            assert layer["name"] == "element_text"


class TestL3SuppressedByL4:
    def test_l4_element_text_suppresses_l3_for_same_axis(self):
        """L4 explicit element_text(rotation=0) for x-axis overrides L3 auto-rotation."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        vals = [f"verylongname_{i}" for i in range(5)]  # would trigger L3 rotation=45
        df = pd.DataFrame({"x_col": vals})

        raw_spec = {
            "x": "x_col",
            "layers": [
                {"name": "element_text", "params": {"target": "axis_text_x", "rotation": 0}},
            ],
        }
        result = resolve_plot_config(raw_spec, {}, df)

        x_et = [l for l in result["layers"]
                if l["name"] == "element_text" and l["params"].get("target") == "axis_text_x"]
        assert len(x_et) == 1
        assert x_et[0]["params"]["rotation"] == 0   # L4 wins; L3 deduped away

    def test_l3_survives_when_no_l4_element_text(self):
        """When L4 has no element_text, L3 auto-rotation is kept."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        vals = [f"verylongname_{i}" for i in range(5)]
        df = pd.DataFrame({"x_col": vals})
        raw_spec = {"x": "x_col"}
        result = resolve_plot_config(raw_spec, {}, df)

        x_et = [l for l in result["layers"]
                if l["name"] == "element_text" and l["params"].get("target") == "axis_text_x"]
        assert len(x_et) == 1
        assert x_et[0]["params"]["rotation"] == 45


# ---------------------------------------------------------------------------
# No-aesthetic-override — _l5_mutex_warn defaults
# ---------------------------------------------------------------------------

class TestL5MutexDefault:
    def test_mutex_warn_false_by_default(self):
        result = resolve_plot_config({}, {}, None)
        assert result["_l5_mutex_warn"] is False

    def test_mutex_warn_false_when_override_is_none(self):
        result = resolve_plot_config({}, {}, None, aesthetic_override=None)
        assert result["_l5_mutex_warn"] is False
