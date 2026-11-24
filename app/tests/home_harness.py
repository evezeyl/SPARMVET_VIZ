"""home_harness.py - the real `home_theater.define_server`, run headless with every part a fake except the recipe, the orchestrator and the keys.

# @deps
# consumes: app/handlers/home_theater.py (define_server), app/tests/test_tier3_reader.py (Tier3World)
# consumed_by: app/tests/test_home_reads_the_plots_table.py, app/tests/test_home_view_choices.py, app/tests/test_filters_change_the_table_not_the_plot.py, app/tests/test_left_sidebar_redraw_wiring.py
# @end_deps

`Home` registers what HOME registers (the render functions by output id, the readers it hands to the filter handlers, the effects by name) so
that a test can call them without a browser. The mode, the data choice and the source table are real `reactive.Value`s: a test sets them
(inside `reactive.isolate()`) and calls the render function again. `flags` is the set of app features flags that are on.
`ViewWorld` is a recipe with two source tables (T with a tier-1 step, M), a join J of them with a tier-2 step, and four plots: on a table
(`p_table`), on a join (`p_join`), on a join with its own tier-3 steps (`p_steps`), and `p_nojoin_t2` (a plot on T, a table without tier-2 steps).
"""
import json
from types import SimpleNamespace
from unittest import mock

import polars as pl
from shiny import reactive, render, ui

import app.handlers.home_theater as home_theater
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_tier3_reader import Tier3World

DATA_T = "sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\t5\n"
DATA_M = "sample_id\tsite\ns1\tx\ns2\tx\ns3\ty\ns4\ty\ns5\ty\n"


class ViewWorld(Tier3World):
    """T (5 rows; its tier 1 keeps score <= 4), M (5 rows), J = T joined with M (tier 2 keeps score >= 2); plots `p_table` (on T, no tier 2),
    `p_join` (on J), `p_steps` (on J, own tier-3 steps: score >= 3 and drop `site`)."""

    def __init__(self, root):
        super().__init__(root)
        (self.data_dir / "M.tsv").write_text(DATA_M)
        self.write_view_recipe()
        self.orch = DataOrchestrator(self.data_analysis_recipes_dir, self.data_dir)

    def write_view_recipe(self, extra_source: str = ""):
        from app.modules.cache_keys import clear_data_analysis_recipe_cache
        (self.data_analysis_recipes_dir / "tiny.yaml").write_text(f"""id: tiny
info: {{ui_label: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
    source: {{type: local_tsv, path: {self.data_file}}}
    null_values: []
    strip: false
    completion: {{marker: T_not_in_original_data, meaning: no result for this entity}}
    input_fields:
      sample_id: {{original_name: sample_id, type: String, ui_label: Sample, is_entity_id: true}}
      group: {{original_name: group, type: String, ui_label: Group}}
      score: {{original_name: score, type: Int64, ui_label: Score}}
    tier1: {{steps: [{json.dumps({"action": "modif_filter", "column": "score", "op": "le", "value": 4, "na": "remove"})}]}}
  M:
    source: {{type: local_tsv, path: {self.data_dir / "M.tsv"}}}
    null_values: []
    strip: false
    completion: {{marker: M_not_in_original_data, meaning: no result for this entity}}
    input_fields:
      sample_id: {{original_name: sample_id, type: String, ui_label: Sample, is_entity_id: true}}
      site: {{original_name: site, type: String, ui_label: Site}}
    tier1: {{steps: []}}
joins:
  J:
    ingredients:
      - dataset_id: T
      - dataset_id: M
    tier1: {{steps: [{json.dumps({"action": "polars_join", "right_ingredient": "M", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"})}]}}
    tier2: {{steps: [{json.dumps({"action": "modif_filter", "column": "score", "op": "ge", "value": 2, "na": "remove"})}]}}
analysis_groups:
  g:
    ui_label: G
    plots:
      p_table:
        ui_label: On a table
        target_dataset: T
        mapping: {{x: group}}
        layers: [{{name: geom_bar, params: {{}}}}]
      p_jitter:
        ui_label: With a random layer
        target_dataset: J
        mapping: {{x: group, y: score}}
        layers: [{{name: geom_point, params: {{position: jitter}}}}]
      p_join:
        ui_label: On a join
        target_dataset: J
        mapping: {{x: group}}
        layers: [{{name: geom_bar, params: {{}}}}]
      p_steps:
        ui_label: With steps
        target_dataset: J
        mapping: {{x: sample_id}}
        layers: [{{name: geom_bar, params: {{}}}}]
        tier3:
          steps: {json.dumps([{"action": "modif_filter", "column": "score", "op": "ge", "value": 3, "na": "remove"},
                              {"action": "polars_drop", "columns": ["site"]}])}
""")
        clear_data_analysis_recipe_cache()


class Home:
    """`define_server` with fakes. `readers` holds what HOME hands to the filter handlers and the export; `outputs` the render functions by id."""

    def __init__(self, world, monkeypatch, *, view="T3", mode="exploration", flags=("interactivity_enabled",), subtab="subtab_p_join",
                 recipe="tiny", source=None, home_state=None, inputs=None, session_manager=None, input_=None):
        self.world = world
        self.readers, self.outputs, self.effects, self.drawn, self.notes = {}, {}, {}, {}, []
        self.drawn_kw = {}         # plot id -> the keyword arguments of the last draw (the aesthetic override, i.e. the Reshuffle pin)
        self.filter_effects = {}
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(reactive, "Calc", lambda fn: fn)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: (self.outputs.setdefault(fn.__name__, fn) and fn) if fn else (lambda f: f))
        for name in ("plot", "text", "data_frame", "download"):
            monkeypatch.setattr(render, name, lambda fn=None, **k: fn if fn is not None else (lambda f: f))
        def effect(fn=None, *, priority=0):
            """Used bare (`@reactive.Effect`) or with arguments (`@reactive.Effect(priority=10)`)."""
            def keep(f):
                return self.effects.setdefault(f.__name__, f) and f
            return keep if fn is None else keep(fn)
        monkeypatch.setattr(reactive, "Effect", effect)
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        monkeypatch.setattr(home_theater, "define_filter_audit_server", lambda *a, **kw: self.readers.update(kw))
        monkeypatch.setattr(home_theater, "define_export_server", lambda *a, **kw: self.readers.update({"export": kw}))
        self.cfg = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml").config
        self.flags = set(flags)
        bootloader = mock.MagicMock()
        bootloader.get_location.side_effect = (
            lambda key: world.data_analysis_recipes_dir if key == "data_analysis_recipes" else world.root / "user")
        bootloader.get_default_data_analysis_recipe_or_none.return_value = recipe
        bootloader.get_default_data_analysis_recipe.return_value = recipe
        bootloader.is_enabled.side_effect = lambda flag: flag in self.flags
        bootloader.config = {}
        bootloader.has_usable_data_analysis_recipe = True
        bootloader.rejected_data_analysis_recipes = {}
        bootloader.discovered_data_analysis_recipes = {recipe: world.data_analysis_recipes_dir / "tiny.yaml"}
        self.mode, self.view, self.source = reactive.Value(mode), reactive.Value(view), reactive.Value(source)
        self.subtab = reactive.Value(subtab)
        self.home_state = reactive.Value(home_state if home_state is not None else {})
        self.applied = None
        self.inputs = dict(inputs or {})

        def record(fn, key):
            self.outputs[key or fn.__name__] = fn
            return fn

        def output(*a, **k):
            if a and callable(a[0]):
                return record(a[0], None)
            return lambda fn: record(fn, k.get("id"))

        monkeypatch.setattr(home_theater, "show_draw_errors", lambda figure, **kw: figure)
        factory = mock.MagicMock()
        factory.default_random_state = 0

        def draw(lf, recipe_dict, plot_id, **kw):
            self.drawn[plot_id] = lf.collect()
            self.drawn_kw[plot_id] = kw
            return "figure"
        factory.render.side_effect = draw
        self._output = output
        self.bootloader = bootloader
        home_theater.define_server(
            input_ if input_ is not None else mock.MagicMock(), output, mock.MagicMock(),
            bootloader=bootloader, wrangle_studio=mock.MagicMock(), dev_studio=mock.MagicMock(),
            orchestrator=world.orch, viz_factory=factory, gallery_viewer=mock.MagicMock(),
            current_app_features=mock.MagicMock(), anchor_path=mock.MagicMock(), tier1_anchor=lambda: pl.DataFrame().lazy(),
            active_cfg=lambda: self.cfg, active_collection_id=lambda: "J",
            safe_input=lambda i, k, d: self.inputs.get(k, recipe if k == "data_analysis_recipe_id" else d),
            active_home_subtab=self.subtab, home_mode=self.mode, data_view=self.view, source_table=self.source,
            home_state=self.home_state, session_manager=session_manager or mock.MagicMock(), notification_log=reactive.Value([]))
        self.filters_applied = self.readers["applied_filters"]
        self.filters_pending = self.readers["_pending_filters"]

    def filter_handlers(self, monkeypatch) -> dict:
        """Run the REAL `define_filter_audit_server` with the readers HOME hands it: its outputs join `self.outputs`, its effects `self.effects`.
        Returns the effects by name (the filter handlers' own: `_clear_filters_on_view_change`, `_filter_apply`...)."""
        from app.handlers import filter_and_audit_handlers as handlers
        monkeypatch.setattr(handlers, "bootloader", self.bootloader)
        def effect(fn=None, *, priority=0):
            """The stand-in of `reactive.Effect`: used bare (`@reactive.Effect`) or with arguments (`@reactive.Effect(priority=10)`)."""
            def keep(f):
                return self.filter_effects.setdefault(f.__name__, f) and f
            return keep if fn is None else keep(fn)
        monkeypatch.setattr(reactive, "Effect", effect)
        kw = {k: v for k, v in self.readers.items() if k != "export"}
        self.filter_effects = {}
        handlers.define_filter_audit_server(mock.MagicMock(), self._output, mock.MagicMock(), **kw)
        return self.filter_effects

    def entry(self, plot_id: str) -> dict:
        return self.cfg.raw_config["analysis_groups"]["g"]["plots"][plot_id]

    def read(self, plot_id: str, tier=None):
        with reactive.isolate():
            return self.readers["_resolve_active_lf"](self.entry(plot_id), tier).collect()

    def plot(self, plot_id: str):
        """Call the plot render function of `plot_id` and return the rows it handed to the drawing factory."""
        self.drawn.pop(plot_id, None)
        with reactive.isolate():
            self.outputs[f"plot_group_{plot_id}"]()
        return self.drawn[plot_id]

    def set(self, *, mode=None, view=None, source=None, subtab=None):
        with reactive.isolate():
            if mode is not None:
                self.mode.set(mode)
            if view is not None:
                self.view.set(view)
            if source is not None:
                self.source.set(source)
            if subtab is not None:
                self.subtab.set(subtab)


def ids(frame: pl.DataFrame) -> list:
    return sorted(frame["sample_id"].to_list())
