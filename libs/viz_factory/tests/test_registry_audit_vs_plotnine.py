"""Audit of the registry against the installed plotnine (VIZ-REGISTRY-AUDIT-1, ADR-106 V1-B, V9).

Four questions, each answered by running plotnine, not by reading a list:

  A. Is every public plotnine object a registered component, a named non-component, or a named, known gap?
     A new plotnine object at an upgrade fails here until somebody classifies it.
  B. Is every registered name that plotnine does not have one of the 22 own names, each with its verdict?
  C. Does every `exact` component, called through the registry, give the same plot as the direct plotnine call
     (same structure and the same drawn picture on the `yaml_example`; the same object or the same error with no parameter)?
  D. What is a `modified` component to plotnine, run: equal to plotnine when its change is unused, not addable to a plot
     in plotnine at all (an element, a position, a guide), or different. Pinned, so a change shows.

The lists below are the audit result of 2026-11-15, plotnine 0.15.4. They are meant to change: the rename task
(`plotnine_`, `modif_`, `step_`) rewrites them in the same commit.

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/tests/test_every_yaml_example_renders.py, plotnine
# doc: .claude/design/viz_rename_impact_2026-11-15.md, .claude/knowledge/architecture_decisions.md (ADR-106)
# @end_deps
"""
import copy
import hashlib
import inspect
import io
import re
import warnings

import matplotlib
import plotnine
import pytest
from plotnine import aes, ggplot

matplotlib.use("Agg")

import viz_factory  # noqa: F401  (registers the components)
from test_every_yaml_example_renders import NOT_JUDGED, TABLE, layers_of, shape_of
from viz_factory.parameters import accepted_names, canonical_name, is_layer
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS

DF = TABLE.to_pandas()
REGISTERED = set(PLOT_COMPONENTS)
PLOTNINE = set(plotnine.__all__)

# ---- A. what is not registered ------------------------------------------------------------------------------------

# Public plotnine names that are not components of a plot: they build a plot, map a column, save a file or set a session default.
NOT_COMPONENTS = {
    "aes": "the plot's `mapping:` key writes the aesthetic mapping",
    "after_scale": "an expression inside a mapping; a recipe maps columns only",
    "after_stat": "an expression inside a mapping; a recipe maps columns only",
    "stage": "an expression inside a mapping; a recipe maps columns only",
    "arrow": "an argument object of geom_segment and geom_path; a recipe holds data, not objects",
    "as_labeller": "turns a function into a labeller; a recipe holds no function",
    "ggplot": "the plot itself, built by the factory from `target_dataset` and `mapping`",
    "ggsave": "saving a file; the export does it",
    "qplot": "a shortcut that builds a whole plot",
    "save_as_pdf_pages": "saving a file; the export does it",
    "theme_get": "reads the session default theme; the factory keeps none",
    "theme_set": "sets a session default theme; the factory keeps none (a recipe names its theme)",
    "theme_update": "changes a session default theme; the factory keeps none",
}
# Names plotnine spells twice (identity alias, `colour`, `grey`): the other spelling IS registered, this one is not.
SPELLINGS_OF_REGISTERED = {
    "geom_bin2d": "geom_bin_2d", "stat_bin2d": "stat_bin_2d", "theme_grey": "theme_gray",
    **{f"scale_colour_{k}": f"scale_color_{k}" for k in (
        "brewer", "cmap", "cmap_d", "continuous", "discrete", "distiller", "gradient", "gradient2", "gradientn", "hue", "identity", "manual")},
}
# Real gaps: a plotnine component that no registered name covers. Decision of Eve needed on the group (question Q3).
KNOWN_MISSING = {
    "annotation_logticks": "annotation: log ticks on the axes",
    "annotation_stripes": "annotation: alternating stripes",
    "expand_limits": "a layer that widens the scale limits",
    "geom_map": "needs geopandas (not installed)",
    "label_both": "a labeller, the value of facet `labeller`; a recipe writes its name",
    "label_context": "a labeller, the value of facet `labeller`; a recipe writes its name",
    "label_value": "a labeller, the value of facet `labeller`; a recipe writes its name",
    "labeller": "builds a labeller from functions; a recipe holds no function",
    "lims": "scale limits for several aesthetics at once (removes data outside)",
    "stat_pointdensity": "the stat of geom_pointdensity, which is registered",
    "theme": "the plotnine `theme()`; the project offers theme_custom for it",
    "watermark": "a layer that draws an image over the plot",
    "xlim": "scale limits of x (removes data outside)",
    "ylim": "scale limits of y (removes data outside)",
    "scale_stroke": "the stroke scale (the continuous one is registered)",
    "scale_size_radius": "a size scale",
    **{f"scale_{a}_{k}": "datetime, ordinal or desaturate variant" for a in ("alpha", "size") for k in ("datetime", "ordinal")
       if f"scale_{a}_{k}" in PLOTNINE},
    **{f"scale_{a}_{k}": "datetime, ordinal, desaturate, gray or grey variant" for a in ("color", "colour", "fill")
       for k in ("datetime", "ordinal", "desaturate", "gray", "grey") if f"scale_{a}_{k}" in PLOTNINE},
}


def test_every_plotnine_name_is_classified():
    classified = REGISTERED | set(NOT_COMPONENTS) | set(SPELLINGS_OF_REGISTERED) | set(KNOWN_MISSING)
    assert sorted(PLOTNINE - classified) == [], "a plotnine object that is neither registered nor classified: classify it"


def test_the_lists_hold_names_plotnine_has_and_the_registry_lacks():
    for group in (NOT_COMPONENTS, SPELLINGS_OF_REGISTERED, KNOWN_MISSING):
        assert set(group) <= PLOTNINE
        assert not set(group) & REGISTERED, "a name that is registered is still listed as missing"
    assert set(SPELLINGS_OF_REGISTERED.values()) <= REGISTERED


def test_the_numbers_of_the_audit():
    assert len(PLOTNINE) == 232 and len(REGISTERED & PLOTNINE) == 169
    assert (len(NOT_COMPONENTS), len(SPELLINGS_OF_REGISTERED), len(KNOWN_MISSING)) == (13, 15, 35)


def test_a_missing_spelling_is_an_alias_or_the_same_signature_as_the_registered_one():
    import inspect
    for other, registered in SPELLINGS_OF_REGISTERED.items():
        a, b = getattr(plotnine, other), getattr(plotnine, registered)
        if a is b:
            continue
        assert str(inspect.signature(a)) == str(inspect.signature(b)), f"{other} and {registered} differ in plotnine itself"


# ---- B. registered names that plotnine does not have ---------------------------------------------------------------

# name -> (what it is, the plotnine call it makes or None). The verdict of the audit; the evidence is in the design file.
OWN = {
    "facet_rows": ("one-call convenience", "facet_grid(rows=...)"),
    "facet_cols": ("one-call convenience", "facet_grid(cols=...)"),
    "coord_lims": ("one-call convenience", "coord_cartesian(xlim, ylim)"),
    "guide_title": ("one-call convenience", "guides(<aes>=guide_legend(title=...))"),
    "guide_ncol": ("one-call convenience", "guides(<aes>=guide_legend(ncol=...))"),
    "guide_nrow": ("one-call convenience", "guides(<aes>=guide_legend(nrow=...))"),
    "guide_reverse": ("one-call convenience", "guides(<aes>=guide_legend(reverse=...))"),
    "guide_direction": ("one-call convenience", "guides(<aes>=guide_legend(direction=...))"),
    "guide_none": ("one-call convenience", "guides(<aes>=False)"),
    "guide_label": ("broken, cannot work today", "guide_legend(labels=...) which plotnine refuses"),
    "theme_legend_position": ("one-call convenience", "theme(legend_position=...)"),
    "theme_custom": ("one-call convenience", "theme(**settings), with dict -> element conversion"),
    "scale_color_viridis_c": ("one-call convenience", "scale_color_cmap(cmap_name=...)"),
    "scale_color_viridis_d": ("one-call convenience", "scale_color_cmap_d(cmap_name=...)"),
    "scale_fill_viridis_c": ("one-call convenience", "scale_fill_cmap(cmap_name=...)"),
    "scale_fill_viridis_d": ("one-call convenience", "scale_fill_cmap_d(cmap_name=...)"),
    "theme_dashboard": ("project preset", "theme_bw(base_size=14)"),
    "theme_publication": ("project preset", "theme_classic(base_size=11)"),
    "facet_labeller": ("setter on the facet already on the plot", None),
    "facet_margins": ("setter on the facet already on the plot", None),
    "facet_scales": ("setter on the facet already on the plot", None),
    "facet_space": ("setter on the facet already on the plot", None),
}


def test_the_names_that_plotnine_does_not_have_are_the_22_with_a_verdict():
    own_in_registry = {n for n in REGISTERED if not hasattr(plotnine, n)}
    assert own_in_registry == set(OWN)
    assert {n for n, s in COMPONENT_SCHEMAS.items() if s["plotnine"] == "own"} == set(OWN)
    assert len(OWN) == 22


def test_no_plotnine_name_equals_an_own_name_even_under_the_other_spelling():
    """The evidence for 'not a plotnine component under another name': plotnine (this version) has none of them,
    nor the `colour`, `grey` or `bin2d` spelling of them, nor any of its modules defines one."""
    import pkgutil
    def spellings(name):
        return {name, name.replace("color", "colour"), name.replace("colour", "color"), name.replace("gray", "grey"), name.replace("grey", "gray")}
    for name in OWN:
        assert not spellings(name) & PLOTNINE, name
    text = ""
    for module in pkgutil.walk_packages(plotnine.__path__, "plotnine."):
        spec = module.module_finder.find_spec(module.name)
        if spec and spec.origin and spec.origin.endswith(".py"):
            text += open(spec.origin, encoding="utf-8").read()
    for name in OWN:
        assert not re.search(rf"\b(def|class)\s+{name}\b", text), f"plotnine defines {name}"


def test_every_own_component_says_so_and_says_what_it_calls():
    for name, (_, call) in OWN.items():
        description = COMPONENT_SCHEMAS[name]["description"]
        assert "Not in plotnine:" in description, name
        if call:
            assert COMPONENT_SCHEMAS[name].get("wraps"), f"{name} makes the call {call} but does not say what it wraps"


@pytest.mark.parametrize("name, sentence", [
    ("coord_lims", "the same call as coord_cartesian"),
    ("scale_color_viridis_c", "calls scale_color_cmap"),
    ("theme_dashboard", "theme_bw with `base_size` 14"),
    ("theme_publication", "theme_classic with `base_size` 11"),
])
def test_the_stated_call_is_the_call_made(name, sentence):
    assert sentence in COMPONENT_SCHEMAS[name]["description"]


# ---- C. an exact component equals the direct plotnine call ---------------------------------------------------------

def describe(obj, seen=None, depth=0):
    """A plain, comparable picture of a plotnine object (its public attributes, recursively; no addresses)."""
    seen = seen if seen is not None else set()
    if depth > 7:
        return "..."
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple)):
        return [describe(x, seen, depth + 1) for x in obj]
    if isinstance(obj, dict):
        return {str(k): describe(v, seen, depth + 1) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, type) or (callable(obj) and not hasattr(obj, "__dict__")):
        return getattr(obj, "__qualname__", repr(obj))
    if id(obj) in seen:
        return "<cycle>"
    seen.add(id(obj))
    if hasattr(obj, "__dict__"):
        # `environment` holds the frame that built the object: it differs between two identical calls
        return {"__class__": type(obj).__name__, **{k: describe(v, seen, depth + 1) for k, v in sorted(vars(obj).items())
                                                    if not k.startswith("_") and k != "environment"}}
    return re.sub(r"0x[0-9a-f]+", "0x", repr(obj))


def snapshot(p):
    return describe({"layers": p.layers, "scales": list(p.scales), "coord": p.coordinates, "facet": p.facet, "theme": p.theme, "labels": p.labels})


def picture(p):
    buffer = io.BytesIO()
    p.save(buffer, format="png", dpi=40, verbose=False)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def drawn_data(p):
    """The tables the layers draw from, after plotnine has computed its statistics and trained its scales (what is drawn, without drawing)."""
    p._build()
    return [hashlib.sha256(layer.data.to_csv().encode()).hexdigest() for layer in p.layers]


def build(name, params, direct):
    """The example of `name` with `params` on its target layer, through the registry or through plotnine itself."""
    layers = layers_of(name)
    base, mapping = shape_of(name, layers)
    p = ggplot(DF, aes(**mapping))
    for layer in ([{"name": base}] if base else []) + layers:
        if layer["name"] == name:
            spec = copy.deepcopy(params)
            p = p + getattr(plotnine, name)(**spec) if direct else PLOT_COMPONENTS[name](p, spec)
        else:
            p = PLOT_COMPONENTS[layer["name"]](p, copy.deepcopy(layer.get("params") or {}))
    return p


def attempt(function):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return "ok", function()
        except Exception as exc:  # noqa: BLE001 - the error itself is the thing compared
            return "error", f"{type(exc).__name__}: {exc}"


EXACT = sorted(n for n, s in COMPONENT_SCHEMAS.items() if s["plotnine"] == "exact")


def example_params(name):
    return next(layer for layer in layers_of(name) if layer["name"] == name).get("params") or {}


def test_there_are_exact_components_to_audit():
    assert len(EXACT) == 123


@pytest.mark.parametrize("name", EXACT)
def test_exact_with_its_example_gives_the_same_plot_as_plotnine(name):
    through, direct = attempt(lambda: build(name, example_params(name), False)), attempt(lambda: build(name, example_params(name), True))
    assert through[0] == direct[0], (name, through if through[0] == "error" else direct)
    if through[0] == "error":
        assert through[1] == direct[1]
        return
    assert snapshot(through[1]) == snapshot(direct[1]), f"{name}: the registry builds another plot than plotnine"
    if is_layer(getattr(plotnine, name)):
        # a geom or a stat: what it draws is its computed table (the picture of a density costs seconds and adds nothing to it)
        assert attempt(lambda: drawn_data(through[1])) == attempt(lambda: drawn_data(direct[1])), f"{name}: other drawn data than plotnine"
    elif name not in NOT_JUDGED:
        # a scale, theme, coord, facet, guide, label: the effect is on the rendering, so the picture is compared
        assert attempt(lambda: picture(through[1])) == attempt(lambda: picture(direct[1])), f"{name}: another picture than plotnine"


@pytest.mark.parametrize("name", EXACT)
def test_exact_with_no_parameter_gives_the_same_object_or_the_same_error_as_plotnine(name):
    through, direct = attempt(lambda: build(name, {}, False)), attempt(lambda: build(name, {}, True))
    assert through[0] == direct[0]
    if through[0] == "error":
        assert through[1] == direct[1]
    else:
        assert snapshot(through[1]) == snapshot(direct[1])


# no parameter, and plotnine refuses: the parameters plotnine needs are required in the schema too
REQUIRED = {"scale_color_gradientn": "colors", "scale_fill_gradientn": "colors", "scale_color_manual": "values", "scale_fill_manual": "values",
            "scale_alpha_manual": "values", "scale_size_manual": "values", "scale_shape_manual": "values", "scale_linetype_manual": "values"}


def test_the_components_that_need_a_parameter_say_so():
    found = {n: [p for p, d in COMPONENT_SCHEMAS[n]["params"].items() if d["required"]] for n in EXACT}
    assert {n: v[0] for n, v in found.items() if v} == REQUIRED


# defaults plotnine has and the form cannot show (not a plain value): listed, never silent
UNSHOWN_DEFAULTS = {"nan": 36, "{}": 8, "after_stat": 14, "(-inf, inf)": 4}


def test_the_defaults_the_form_does_not_show_are_the_audited_54():
    import inspect
    from viz_factory.parameters import is_layer
    counts = {"nan": 0, "{}": 0, "after_stat": 0, "(-inf, inf)": 0}
    for name in EXACT:
        obj = getattr(plotnine, name)
        if is_layer(obj):
            layer = obj().to_layer()
            defaults = {**layer.stat.DEFAULT_AES, **layer.stat.DEFAULT_PARAMS, **layer.geom.DEFAULT_AES, **layer.geom.DEFAULT_PARAMS}
            defaults = {k.replace("colour", "color"): v for k, v in defaults.items()}
        else:
            defaults = {k: p.default for k, p in inspect.signature(obj).parameters.items() if p.default is not inspect.Parameter.empty}
        for param, definition in COMPONENT_SCHEMAS[name]["params"].items():
            value = defaults.get(param)
            if "default" in definition or value is None:
                continue
            key = "nan" if repr(value) == "nan" else "{}" if value == {} else "after_stat" if "after_stat" in repr(value) else repr(value)
            assert key in counts, f"{name}.{param}: a default the form does not show and the audit does not know: {value!r}"
            counts[key] += 1
    assert counts == UNSHOWN_DEFAULTS


# ---- D. what a modified component is to plotnine -------------------------------------------------------------------

# a plotnine element, position or guide object cannot be added to a plot in plotnine: the component adapts it to a plot step
NOT_ADDABLE = ["element_blank", "element_line", "element_rect", "element_text", "guide_colorbar", "guide_colourbar", "guide_legend",
               "position_dodge", "position_dodge2", "position_fill", "position_identity", "position_jitter", "position_jitterdodge",
               "position_nudge", "position_stack"]
# equal to the direct plotnine call when the change it makes is not used
SAME_WHEN_UNUSED = ["annotate", "facet_grid", "geom_jitter", "geom_sina", "ggtitle", "guides", "scale_alpha", "scale_color_hue", "scale_fill_hue",
                    "scale_size", "scale_size_area", "scale_x_continuous", "scale_y_continuous", "stat_sina", "theme_538", "theme_bw",
                    "theme_classic", "theme_dark", "theme_gray", "theme_light", "theme_linedraw", "theme_matplotlib", "theme_minimal",
                    "theme_seaborn", "theme_tufte", "theme_void", "theme_xkcd", "xlab", "ylab"]
DIFFERENT = ["stat_function", "stat_identity"]


def test_the_three_groups_are_the_modified_components():
    assert sorted(NOT_ADDABLE + SAME_WHEN_UNUSED + DIFFERENT) == sorted(n for n, s in COMPONENT_SCHEMAS.items() if s["plotnine"] == "modified")


@pytest.mark.parametrize("name", NOT_ADDABLE)
def test_plotnine_cannot_add_this_object_to_a_plot_so_an_exact_step_cannot_exist(name):
    obj = getattr(plotnine, COMPONENT_SCHEMAS[name]["wraps"][0]["attr_path"][-1])()
    with pytest.raises(AttributeError, match="__radd__"):
        ggplot(DF, aes("x", "y")) + obj


@pytest.mark.parametrize("name", SAME_WHEN_UNUSED)
def test_modified_with_the_change_unused_gives_the_same_plot_as_plotnine(name):
    params = example_params(name)
    through, direct = attempt(lambda: build(name, params, False)), attempt(lambda: build(name, params, True))
    assert through[0] == direct[0] == "ok", (through, direct)
    assert snapshot(through[1]) == snapshot(direct[1])


@pytest.mark.parametrize("name", DIFFERENT)
def test_these_modified_components_give_another_plot_than_plotnine(name):
    through, direct = attempt(lambda: build(name, example_params(name), False)), attempt(lambda: build(name, example_params(name), True))
    assert through[0] == "ok"
    assert direct[0] == "error" or snapshot(through[1]) != snapshot(direct[1])


def test_no_exact_plotnine_object_is_registered_next_to_a_modified_one_today():
    exact_wrapped = {tuple(s["wraps"][0]["attr_path"]) for s in COMPONENT_SCHEMAS.values() if s["plotnine"] == "exact" and s.get("wraps")}
    with_neighbour = [n for n, s in COMPONENT_SCHEMAS.items()
                      if s["plotnine"] == "modified" and s.get("wraps") and tuple(s["wraps"][0]["attr_path"]) in exact_wrapped]
    assert with_neighbour == []


# ---- the checker must be able to fail ------------------------------------------------------------------------------

def test_the_comparison_sees_a_changed_default():
    """If a wrapper changed a default, the snapshot would differ: the audit is able to fail."""
    a = ggplot(DF, aes("x", "y")) + plotnine.geom_point()
    b = ggplot(DF, aes("x", "y")) + plotnine.geom_point(size=7)
    assert snapshot(a) != snapshot(b)
    assert picture(a) != picture(b)


# ---- the parameters a modified component does not offer -------------------------------------------------------------

# plotnine parameters of the wrapped object that the schema of a modified component does not list (the form does not offer them),
# without `data`, `mapping`, `rescaler` and `oob` (a table or a function: a recipe holds neither). 21 of the 41 modified components that wrap an object.
HIDDEN_IN_FORM_TOTAL = 165
HIDDEN_COMPONENTS = 21
# of those, the ones a recipe cannot pass even when it writes them: the component sends every key it does not know to `theme(...)`, which refuses it
CANNOT_BE_WRITTEN = {
    "theme_matplotlib": ["fname", "rc", "use_defaults"],
    "theme_seaborn": ["context", "font", "font_scale", "style"],
    "theme_tufte": ["ticks"],
    "theme_xkcd": ["length", "randomness", "scale", "stroke_color", "stroke_size"],
}
FUNCTION_OR_TABLE = {"rescaler", "oob", "data", "mapping"}


def hidden_parameters():
    found = {}
    for name, schema in sorted(COMPONENT_SCHEMAS.items()):
        if schema["plotnine"] != "modified" or not schema.get("wraps"):
            continue
        obj = getattr(plotnine, schema["wraps"][0]["attr_path"][-1], None)
        accepted = accepted_names(name, schema) if obj is not None else None
        if accepted is None:
            continue
        declared = {canonical_name(k) if is_layer(obj) else k for k in schema["params"]}
        hidden = sorted(h for h in accepted - declared if h not in FUNCTION_OR_TABLE)
        if hidden:
            found[name] = hidden
    return found


def test_the_modified_components_hide_165_plotnine_parameters_from_the_form():
    found = hidden_parameters()
    assert len(found) == HIDDEN_COMPONENTS
    assert sum(len(v) for v in found.values()) == HIDDEN_IN_FORM_TOTAL


def default_of(name, parameter):
    obj = getattr(plotnine, COMPONENT_SCHEMAS[name]["wraps"][0]["attr_path"][-1])
    if is_layer(obj):
        layer = obj().to_layer()
        defaults = {**layer.stat.DEFAULT_AES, **layer.stat.DEFAULT_PARAMS, **layer.geom.DEFAULT_AES, **layer.geom.DEFAULT_PARAMS}
        return defaults.get(parameter, defaults.get(parameter.replace("color", "colour")))
    default = inspect.signature(obj).parameters[parameter].default
    return None if default is inspect.Parameter.empty else default


def test_a_hidden_parameter_is_written_through_the_component_unless_it_is_one_of_the_listed_themes_settings():
    """plotnine's own default of each hidden parameter is passed through the component and through plotnine: both must work."""
    cannot = {}
    for name, hidden in hidden_parameters().items():
        layers = layers_of(name)
        base, mapping = shape_of(name, layers)
        for parameter in hidden:
            value = default_of(name, parameter)
            def call(direct):
                p = ggplot(DF, aes(**mapping))
                if base:
                    p = PLOT_COMPONENTS[base](p, {})
                spec = {parameter: copy.deepcopy(value)}
                if name == "stat_function":
                    spec["fun"] = lambda x: x
                if direct:
                    return p + getattr(plotnine, COMPONENT_SCHEMAS[name]["wraps"][0]["attr_path"][-1])(**spec)
                return PLOT_COMPONENTS[name](p, spec)
            if attempt(lambda: call(True))[0] == "ok" and attempt(lambda: call(False))[0] == "error":
                cannot.setdefault(name, []).append(parameter)
    assert cannot == CANNOT_BE_WRITTEN


# ---- defects found by the audit, pinned: a fix turns the strict xfail into a failure, then remove the entry ----------

def run_layers(mapping, layers):
    from viz_factory.viz_factory import VizFactory, draw_checked
    figure = draw_checked(VizFactory().render(TABLE, {"plots": {"p": {"target_dataset": "d", "mapping": mapping, "layers": layers}}}, "p"))
    return [t.get_text() for axis in figure.axes for t in axis.get_xticklabels()]


DEFECTS = {
    "theme_seaborn offers base_size and refuses it": ("theme_seaborn", {"base_size": 12}),
    "theme_matplotlib offers base_size and refuses it": ("theme_matplotlib", {"base_size": 12}),
    "theme_seaborn style cannot be reached": ("theme_seaborn", {"style": "whitegrid"}),
    "theme_seaborn context cannot be reached": ("theme_seaborn", {"context": "talk"}),
    "theme_matplotlib rc cannot be reached": ("theme_matplotlib", {"rc": {"axes.grid": True}}),
}


@pytest.mark.parametrize("label", sorted(DEFECTS))
@pytest.mark.xfail(strict=True, reason="defect of the audit: the wrapper sends every key to theme(), which refuses it (not fixed here)")
def test_defect_the_theme_setting_works(label):
    name, params = DEFECTS[label]
    run_layers({"x": "x", "y": "y"}, [{"name": "geom_point"}, {"name": name, "params": params}])


TEXT_AS_LIST = {
    "labels: abc on a continuous scale": ("scale_x_continuous", {"breaks": [10, 50, 90], "labels": "abc"}, {"x": "x", "y": "y"}),
    "limits: abc on a brewer scale": ("scale_color_brewer", {"limits": "abc"}, {"x": "x", "y": "y", "color": "g"}),
    "breaks: abc on a manual scale": ("scale_color_manual", {"values": ["red", "blue", "green"], "breaks": "abc"}, {"x": "x", "y": "y", "color": "g"}),
}


@pytest.mark.parametrize("label", sorted(TEXT_AS_LIST))
@pytest.mark.xfail(strict=True, reason="defect of the audit: a text where a list was meant is read by plotnine as its letters and drawn with no message")
def test_defect_a_text_where_a_list_is_meant_is_refused(label):
    name, params, mapping = TEXT_AS_LIST[label]
    with pytest.raises(Exception):
        run_layers(mapping, [{"name": "geom_point"}, {"name": name, "params": params}])


def test_defect_guide_label_fails_on_every_use_and_says_so():
    with pytest.raises(Exception, match="guide_label cannot work"):
        run_layers({"x": "x", "y": "y", "color": "g"}, [{"name": "geom_point"}, {"name": "guide_label", "params": {"mapping": "color", "labels": ["a"]}}])


# ---- what a description says must be true ---------------------------------------------------------------------------

def test_no_description_says_that_a_null_or_random_seed_is_allowed():
    """The factory refuses `random_state: null` and `random` (a seed is a number); a description must not offer them."""
    wrong = [n for n, s in COMPONENT_SCHEMAS.items()
             if re.search(r"random_state:\s*(null|random)\b[^.]*\b(gives|allows|new|different)", s["description"] + " " + s.get("yaml_example", ""))]
    assert wrong == []
