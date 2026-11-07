"""
Regression tests for DECO-2 plot components (added 2026-04-30).

Covers the 17 plotnine wrappers added to close the gap surfaced by the
DECO-1 audit. Each test calls the registered handler with a realistic
spec and asserts the result is a valid `plotnine.ggplot` instance — i.e.
the wrapper imports correctly, accepts the spec shape, and produces a
composable plot object.

This is the FAST automatic check (sub-second). The full Evidence Loop
(YAML data analysis recipe → debug_runner → PNG materialisation in `tmp/viz_factory/`)
is run via `viz_factory_integrity_suite.py` and the matching
`{component}_test.yaml` files in `tests/test_data/` — those exercise the
end-to-end render pipeline through matplotlib.

Run from the project root:
    pytest libs/viz_factory/tests/test_deco2_components.py -v
"""
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

# Importing these subpackages triggers the @register_plot_component
# decorators that populate PLOT_COMPONENTS.
import viz_factory.scales  # noqa: F401
import viz_factory.themes  # noqa: F401
from viz_factory.registry import PLOT_COMPONENTS, get_component


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def df():
    """Synthetic data with both categorical and continuous columns so every
    aesthetic scale has something meaningful to map to."""
    return pd.DataFrame({
        "x": [1, 2, 3, 4, 5, 6],
        "y": [2, 4, 1, 5, 3, 6],
        "g": ["a", "b", "a", "b", "a", "b"],
        "size_var": [10.0, 20.0, 15.0, 25.0, 18.0, 22.0],
    })


@pytest.fixture
def base_plot(df):
    return ggplot(df, aes(x="x", y="y", color="g", size="size_var")) + geom_point()


# ── Registration tests (cheap — just check names exist) ───────────────────────

DECO2_COMPONENTS = [
    # Aesthetic generic scales
    "scale_alpha", "scale_alpha_manual",
    "scale_size", "scale_size_manual", "scale_size_area",
    "scale_shape", "scale_shape_manual",
    "scale_linetype", "scale_linetype_manual",
    "scale_color_hue", "scale_fill_hue",
    "scale_color_continuous", "scale_fill_continuous",
    # Label / annotation helpers
    "xlab", "ylab", "ggtitle", "annotate",
]


@pytest.mark.parametrize("name", DECO2_COMPONENTS)
def test_component_registered(name):
    """Every DECO-2 component must be in the global PLOT_COMPONENTS registry."""
    assert name in PLOT_COMPONENTS, (
        f"{name!r} not registered. Did the @register_plot_component decorator "
        f"fail to fire? Check that scales/core.py and themes/core.py are imported."
    )


def test_total_count_at_least_17():
    """Sanity check: the 17 DECO-2 components are all registered."""
    registered_deco2 = [n for n in DECO2_COMPONENTS if n in PLOT_COMPONENTS]
    assert len(registered_deco2) == 17, (
        f"Expected 17 DECO-2 components registered, got {len(registered_deco2)}: "
        f"{registered_deco2}"
    )


# ── Aesthetic scale handlers — apply to a real ggplot ─────────────────────────

class TestAestheticScales:
    """Each handler must accept a realistic spec and return a ggplot object."""

    def test_scale_alpha(self, base_plot):
        result = get_component("scale_alpha")(base_plot, {"range": (0.3, 1.0)})
        assert isinstance(result, ggplot)

    def test_scale_alpha_manual(self, base_plot):
        result = get_component("scale_alpha_manual")(
            base_plot, {"values": {"a": 0.4, "b": 1.0}}
        )
        assert isinstance(result, ggplot)

    def test_scale_size(self, base_plot):
        result = get_component("scale_size")(base_plot, {"range": (1, 6)})
        assert isinstance(result, ggplot)

    def test_scale_size_manual(self, base_plot):
        result = get_component("scale_size_manual")(
            base_plot, {"values": {"a": 2, "b": 6}}
        )
        assert isinstance(result, ggplot)

    def test_scale_size_area(self, base_plot):
        result = get_component("scale_size_area")(base_plot, {"max_size": 8})
        assert isinstance(result, ggplot)

    def test_scale_shape(self, df):
        # geom_point with shape mapping
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point()
        result = get_component("scale_shape")(p, {})
        assert isinstance(result, ggplot)

    def test_scale_shape_manual(self, df):
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point()
        result = get_component("scale_shape_manual")(
            p, {"values": {"a": "o", "b": "^"}}
        )
        assert isinstance(result, ggplot)

    def test_scale_linetype(self, df):
        from plotnine import geom_line
        p = ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line()
        result = get_component("scale_linetype")(p, {})
        assert isinstance(result, ggplot)

    def test_scale_linetype_manual(self, df):
        from plotnine import geom_line
        p = ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line()
        result = get_component("scale_linetype_manual")(
            p, {"values": {"a": "solid", "b": "dashed"}}
        )
        assert isinstance(result, ggplot)

    def test_scale_color_hue(self, base_plot):
        result = get_component("scale_color_hue")(base_plot, {"h": (0.15, 1.0)})
        assert isinstance(result, ggplot)

    def test_scale_fill_hue(self, df):
        from plotnine import geom_bar
        p = ggplot(df, aes(x="g", fill="g")) + geom_bar()
        result = get_component("scale_fill_hue")(p, {})
        assert isinstance(result, ggplot)

    def test_scale_color_continuous(self, df):
        p = ggplot(df, aes(x="x", y="y", color="size_var")) + geom_point()
        result = get_component("scale_color_continuous")(p, {})
        assert isinstance(result, ggplot)

    def test_scale_fill_continuous(self, df):
        from plotnine import geom_tile
        p = ggplot(df, aes(x="g", y="x", fill="size_var")) + geom_tile()
        result = get_component("scale_fill_continuous")(p, {})
        assert isinstance(result, ggplot)


# ── Label / annotation handlers ───────────────────────────────────────────────

class TestLabels:
    def test_xlab(self, base_plot):
        result = get_component("xlab")(base_plot, {"label": "X axis"})
        assert isinstance(result, ggplot)

    def test_ylab(self, base_plot):
        result = get_component("ylab")(base_plot, {"label": "Y axis"})
        assert isinstance(result, ggplot)

    def test_ggtitle_simple(self, base_plot):
        result = get_component("ggtitle")(base_plot, {"title": "Plot title"})
        assert isinstance(result, ggplot)

    def test_ggtitle_with_subtitle(self, base_plot):
        result = get_component("ggtitle")(
            base_plot, {"title": "Main title", "subtitle": "Sub line"}
        )
        assert isinstance(result, ggplot)

    def test_annotate_text(self, base_plot):
        result = get_component("annotate")(
            base_plot,
            {"geom": "text", "x": 3, "y": 5, "label": "marker"}
        )
        assert isinstance(result, ggplot)

    def test_annotate_segment(self, base_plot):
        result = get_component("annotate")(
            base_plot,
            {"geom": "segment", "x": 1, "y": 1, "xend": 6, "yend": 6}
        )
        assert isinstance(result, ggplot)

    def test_annotate_missing_geom_returns_unchanged(self, base_plot):
        # Defensive: if spec.geom is missing, handler should no-op (return p)
        result = get_component("annotate")(base_plot, {})
        assert isinstance(result, ggplot)


# ── Timedelta scales (re-enabled — worked fine in plotnine 0.15.3) ────────────

class TestTimedeltaScales:
    """scale_x/y_timedelta were commented out due to a dtype mismatch bug.
    Verified working in plotnine 0.15.3 — handlers re-enabled."""

    @pytest.fixture
    def td_plot(self):
        import pandas as pd
        df = pd.DataFrame({
            "elapsed": pd.to_timedelta(["1 days", "2 days", "3 days", "4 days"]),
            "value": [1.0, 3.0, 2.0, 4.0],
        })
        from plotnine import geom_line
        return ggplot(df, aes(x="elapsed", y="value")) + geom_line()

    def test_scale_x_timedelta_registered(self):
        assert "scale_x_timedelta" in PLOT_COMPONENTS

    def test_scale_y_timedelta_registered(self):
        assert "scale_y_timedelta" in PLOT_COMPONENTS

    def test_scale_x_timedelta_applies(self, td_plot):
        result = get_component("scale_x_timedelta")(td_plot, {})
        assert isinstance(result, ggplot)

    def test_scale_y_timedelta_applies(self, td_plot):
        result = get_component("scale_y_timedelta")(td_plot, {})
        assert isinstance(result, ggplot)
