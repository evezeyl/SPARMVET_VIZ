"""Round-trip truth table for normalise_plot_spec / serialise_plot_spec (BP-PLOT-MODEL-1).

Tests the public seam introduced by ADR-083:
  - normalise_plot_spec: collects gallery/author metadata into _meta; hard-fails on removed
    legacy keys (factory_id, flat aesthetics — ADR-083)
  - serialise_plot_spec: inverse — emits mapping + explicit layers, expands _meta
  - Round-trip render-equivalence: serialise(normalise(raw)) re-normalises to equivalent spec
  - Idempotency of normalise: normalise(normalise(x)) == normalise(x)

Run with:
    .venv/bin/python -m pytest libs/viz_factory/tests/test_plot_spec_roundtrip.py -v
"""
from __future__ import annotations

import pytest

from viz_factory.plot_config_resolver import (
    normalise_plot_spec,
    serialise_plot_spec,
    _CANONICAL_SPEC_KEYS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _geom_names(spec: dict) -> list[str]:
    return [l["name"] for l in spec.get("layers", [])
            if l.get("name", "").startswith(("geom_", "stat_"))]


def _is_render_equivalent(a: dict, b: dict) -> bool:
    """Render-equivalence: same mapping and same geom sequence."""
    if a.get("mapping") != b.get("mapping"):
        return False
    if _geom_names(a) != _geom_names(b):
        return False
    return True


# ---------------------------------------------------------------------------
# normalise_plot_spec — _meta passthrough
# ---------------------------------------------------------------------------

class TestNormaliseMeta:
    def test_unknown_keys_moved_to_meta(self):
        spec = {
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_bar", "params": {}}],
            "family": "Distribution",
            "pattern": "1 Numeric, 1 Categorical",
            "difficulty": "Simple",
        }
        result = normalise_plot_spec(spec)
        assert result["_meta"]["family"] == "Distribution"
        assert result["_meta"]["pattern"] == "1 Numeric, 1 Categorical"
        assert result["_meta"]["difficulty"] == "Simple"
        assert "family" not in result or "family" not in {k for k in result if k != "_meta"}

    def test_existing_meta_merged(self):
        spec = {
            "mapping": {"x": "Year"},
            "_meta": {"author": "Eve"},
            "family": "Distribution",
        }
        result = normalise_plot_spec(spec)
        assert result["_meta"]["author"] == "Eve"
        assert result["_meta"]["family"] == "Distribution"

    def test_no_unknown_keys_no_meta(self):
        spec = {"mapping": {"x": "Year"}, "layers": [{"name": "geom_point", "params": {}}]}
        result = normalise_plot_spec(spec)
        assert "_meta" not in result

    def test_empty_meta_not_attached(self):
        spec = {"mapping": {"x": "Year"}, "layers": [{"name": "geom_point", "params": {}}]}
        result = normalise_plot_spec(spec)
        assert "_meta" not in result

    def test_canonical_keys_not_moved_to_meta(self):
        spec = {
            "target_dataset": "FastP",
            "mapping": {"x": "sample_id", "y": "total_reads"},
            "layers": [{"name": "geom_boxplot", "params": {}}],
            "theme": "theme_light",
            "facet_by": "Country",
            "palette": "sparmvet_brand",
        }
        result = normalise_plot_spec(spec)
        assert "_meta" not in result
        assert result["target_dataset"] == "FastP"

    def test_geom_taxonomy_key_not_canonical(self):
        # 'geom' is a gallery taxonomy field, NOT in _CANONICAL_SPEC_KEYS
        # (it differs from the 'layers' geom layer concept)
        spec = {"mapping": {"x": "Year"}, "geom": "geom_violin"}
        result = normalise_plot_spec(spec)
        assert result.get("_meta", {}).get("geom") == "geom_violin"


# ---------------------------------------------------------------------------
# normalise_plot_spec — idempotency
# ---------------------------------------------------------------------------

class TestNormaliseIdempotency:
    def test_idempotent_canonical_form(self):
        spec = {
            "mapping": {"x": "Year", "fill": "Country"},
            "layers": [{"name": "geom_bar", "params": {}}],
        }
        once = normalise_plot_spec(spec)
        twice = normalise_plot_spec(once)
        assert once == twice

    def test_idempotent_with_meta(self):
        spec = {
            "mapping": {"x": "x_col", "y": "y_col"},
            "layers": [{"name": "geom_point", "params": {}}],
            "family": "Correlation",
        }
        once = normalise_plot_spec(spec)
        twice = normalise_plot_spec(once)
        assert once == twice


# ---------------------------------------------------------------------------
# serialise_plot_spec — correctness
# ---------------------------------------------------------------------------

class TestSerialisePlotSpec:
    def test_mapping_not_flat(self):
        """Serialised form uses mapping: not flat x/y/fill."""
        normalised = normalise_plot_spec({
            "mapping": {"x": "Year", "y": "count"},
            "layers": [{"name": "geom_point", "params": {}}],
        })
        out = serialise_plot_spec(normalised)
        assert "mapping" in out
        assert out["mapping"]["x"] == "Year"
        # flat aesthetic keys must not appear at top level in output
        for aes_key in ("x", "y", "fill", "color", "colour", "size", "alpha", "shape"):
            assert aes_key not in out

    def test_no_factory_id_in_output(self):
        """Serialised canonical spec never contains factory_id."""
        normalised = normalise_plot_spec({
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_bar", "params": {}}],
        })
        out = serialise_plot_spec(normalised)
        assert "factory_id" not in out

    def test_geom_in_layers(self):
        """Layers are preserved through normalise→serialise."""
        normalised = normalise_plot_spec({
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_bar", "params": {}}],
        })
        out = serialise_plot_spec(normalised)
        assert "layers" in out
        assert out["layers"][0]["name"] == "geom_bar"

    def test_meta_expanded_to_top_level(self):
        normalised = normalise_plot_spec({
            "mapping": {"x": "species", "y": "value"},
            "layers": [{"name": "geom_violin", "params": {}}],
            "family": "Distribution",
            "difficulty": "Intermediate",
        })
        out = serialise_plot_spec(normalised)
        assert out["family"] == "Distribution"
        assert out["difficulty"] == "Intermediate"
        assert "_meta" not in out

    def test_no_tier_keys_in_layer_output(self):
        normalised = normalise_plot_spec({
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_bar", "params": {}, "_tier": "L4"}],
        })
        out = serialise_plot_spec(normalised)
        for layer in out.get("layers", []):
            assert "_tier" not in layer

    def test_empty_layers_list_preserved(self):
        spec = {"mapping": {"x": "Year"}, "layers": []}
        out = serialise_plot_spec(normalise_plot_spec(spec))
        assert out.get("layers") == []

    def test_optional_fields_only_when_present(self):
        spec = {"mapping": {"x": "Year"}, "layers": [{"name": "geom_point", "params": {}}]}
        out = serialise_plot_spec(normalise_plot_spec(spec))
        assert "theme" not in out
        assert "facet_by" not in out
        assert "palette" not in out
        assert "filters" not in out

    def test_optional_fields_included_when_set(self):
        spec = {
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_point", "params": {}}],
            "theme": "theme_light",
            "facet_by": "Country",
            "palette": "viridis",
        }
        out = serialise_plot_spec(normalise_plot_spec(spec))
        assert out["theme"] == "theme_light"
        assert out["facet_by"] == "Country"
        assert out["palette"] == "viridis"

    def test_target_dataset_first(self):
        spec = {
            "target_dataset": "FastP",
            "mapping": {"x": "sample_id", "y": "total_reads"},
            "layers": [{"name": "geom_boxplot", "params": {}}],
        }
        out = serialise_plot_spec(normalise_plot_spec(spec))
        assert list(out.keys())[0] == "target_dataset"


# ---------------------------------------------------------------------------
# Round-trip render-equivalence
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_round_trip_canonical_bar(self):
        """serialise(normalise(canonical_spec)) re-normalises to a render-equivalent spec."""
        raw = {
            "mapping": {"x": "Year", "fill": "Country"},
            "layers": [{"name": "geom_bar", "params": {}}],
        }
        step1 = normalise_plot_spec(raw)
        step2 = serialise_plot_spec(step1)
        step3 = normalise_plot_spec(step2)
        assert _is_render_equivalent(step1, step3)

    def test_round_trip_heatmap(self):
        raw = {
            "mapping": {"x": "Gene", "y": "Sample", "fill": "value"},
            "layers": [{"name": "geom_tile", "params": {}}],
        }
        step1 = normalise_plot_spec(raw)
        step2 = serialise_plot_spec(step1)
        step3 = normalise_plot_spec(step2)
        assert _is_render_equivalent(step1, step3)

    def test_round_trip_with_meta(self):
        raw = {
            "mapping": {"x": "sample_id", "y": "total_reads"},
            "layers": [{"name": "geom_boxplot", "params": {}}],
            "family": "Distribution",
            "pattern": "1 Numeric, 1 Categorical",
            "difficulty": "Simple",
        }
        step1 = normalise_plot_spec(raw)
        step2 = serialise_plot_spec(step1)
        step3 = normalise_plot_spec(step2)
        # Render-equivalent
        assert _is_render_equivalent(step1, step3)
        # _meta preserved
        assert step3.get("_meta", {}).get("family") == "Distribution"
        assert step3.get("_meta", {}).get("difficulty") == "Simple"

    def test_round_trip_canonical_already(self):
        """A spec already in canonical form (mapping + layers) is stable."""
        raw = {
            "target_dataset": "FastP",
            "mapping": {"x": "sample_id", "y": "total_reads"},
            "layers": [{"name": "geom_boxplot", "params": {}}],
            "theme": "theme_light",
        }
        step1 = normalise_plot_spec(raw)
        step2 = serialise_plot_spec(step1)
        step3 = normalise_plot_spec(step2)
        assert _is_render_equivalent(step1, step3)
        # Scalar fields preserved
        assert step3.get("theme") == "theme_light"

    def test_round_trip_with_extra_layers(self):
        """Non-geom layers are preserved through the round-trip."""
        raw = {
            "mapping": {"x": "Year", "fill": "Country"},
            "layers": [
                {"name": "geom_bar", "params": {}},
                {"name": "position_dodge", "params": {}},
                {"name": "labs", "params": {"title": "Test Plot"}},
            ],
        }
        step1 = normalise_plot_spec(raw)
        step2 = serialise_plot_spec(step1)
        step3 = normalise_plot_spec(step2)
        # geom_bar still present
        assert "geom_bar" in _geom_names(step3)
        # extra layers still present
        layer_names = [l["name"] for l in step3.get("layers", [])]
        assert "position_dodge" in layer_names
        assert "labs" in layer_names

    def test_serialise_then_normalise_stable(self):
        """Serialising and re-normalising a canonical spec is idempotent; no geom duplication."""
        raw = {
            "mapping": {"x": "Year"},
            "layers": [{"name": "geom_bar", "params": {}}],
        }
        serialised = serialise_plot_spec(normalise_plot_spec(raw))
        assert "factory_id" not in serialised
        # Re-normalising adds nothing new (geom already in layers)
        renormalised = normalise_plot_spec(serialised)
        geom_bars = [l for l in renormalised.get("layers", []) if l["name"] == "geom_bar"]
        assert len(geom_bars) == 1


# ---------------------------------------------------------------------------
# _CANONICAL_SPEC_KEYS completeness
# ---------------------------------------------------------------------------

class TestCanonicalSpecKeys:
    def test_flat_aes_keys_not_canonical(self):
        """Flat aesthetic keys are NOT canonical — ADR-083 removed them; use mapping: block."""
        for k in ("x", "y", "fill", "color", "colour", "size", "alpha", "shape", "label"):
            assert k not in _CANONICAL_SPEC_KEYS, (
                f"flat aes key {k!r} must NOT be in _CANONICAL_SPEC_KEYS"
            )

    def test_factory_id_not_canonical(self):
        """factory_id was removed in ADR-083 and must not be in _CANONICAL_SPEC_KEYS."""
        assert "factory_id" not in _CANONICAL_SPEC_KEYS

    def test_known_structural_keys_in_canonical(self):
        for k in ("target_dataset", "mapping", "layers", "theme", "facet_by",
                  "palette", "labels", "guides", "filters", "title", "_meta"):
            assert k in _CANONICAL_SPEC_KEYS, f"{k!r} missing from _CANONICAL_SPEC_KEYS"

    def test_taxonomy_keys_not_canonical(self):
        for k in ("family", "pattern", "difficulty", "show", "sample_size"):
            assert k not in _CANONICAL_SPEC_KEYS, f"taxonomy key {k!r} should NOT be in _CANONICAL_SPEC_KEYS"
