"""The export record `effective_run.yaml` names the engines that were used (D-0248).

It holds, under the key `engines`: the engine per table and per join and per tier, the engine per plot, the theme as it was applied
per plot, and the versions of the libraries behind the engines used. The Publication export carries no recipe, so this record is
the only place the engine is written.

One source: the record is made from the values the run used. The engine of a tier is `utils.engines.tier_engine` (the function the
orchestrator chooses the entry with), the engine of a plot is `plot_entry` (the dispatcher's own function), the theme is read from
the plot that was drawn, the versions from the installed libraries.

The real generator of `export_bundle_download` runs without a browser (the harness of `test_export_download_path.py`) on a real
orchestrator and a real tiny recipe; the pure builder and the dispatcher's record are tested on their own too.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_engine_record.py -q
"""
import io
import zipfile

import pytest
import yaml

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.engine_record import NOT_RUN, engine_record, failed_plot_record
from app.modules.engine_registry import REGISTRY, PlotEngines, data_entry, plot_entry
from app.tests.test_cache_chain import FILTER_A, World
from app.tests.test_export_download_path import _download_function, _fresh_cache, _run  # noqa: F401  (the autouse fixture too)
from utils import engines
from utils.engines import PlotEngineEntry

OLD_KEYS = {
    "_about", "generated", "data_analysis_recipe_sha256", "data_batch_hash", "t3_audit_steps_sha256", "engine_fingerprint",
    "containerized", "image_ref", "uv_lock_sha256", "git_commit", "release_version", "contact", "contact_source",
    "software_versions", "data_source_paths", "seeds_per_plot", "seed_source_per_plot", "seeds_per_layer",
    "seeds_added_to_recipe", "t3_translation_skipped",
}


def effective_run(tmp_path, monkeypatch, edit=None, steps_tier2=(), world_hook=None):
    world = World(tmp_path)
    if steps_tier2:
        world.write_data_analysis_recipe(steps_tier2=list(steps_tier2))
    if edit:
        recipe = world.data_analysis_recipes_dir / "tiny.yaml"
        text = recipe.read_text()
        changed = edit(text)
        assert changed != text, "the edit changed nothing: the test would prove nothing"
        recipe.write_text(changed)
        clear_data_analysis_recipe_cache()
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch))
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    name = next(n for n in archive.namelist() if n.endswith("/effective_run.yaml"))
    return yaml.safe_load(archive.read(name).decode())


def add_plot(text: str, plot_id: str, extra: str = "") -> str:
    """A second plot `plot_id` in the group, reading the same join; `extra` is more lines of its entry."""
    return text.rstrip("\n") + f"\n      {plot_id}:\n        ui_label: {plot_id}\n        target_dataset: C\n{extra}        mapping: {{x: group}}\n        layers:\n          - name: geom_bar\n            params: {{}}\n"


# --- what the real export writes ------------------------------------------------------------------------------------------------


def test_the_record_of_a_run_names_the_engine_of_each_tier_of_each_table_and_join_and_of_each_plot(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch)
    record = run["engines"]
    assert record["recipe_default"] == {"data_engine": "python-polars", "plot_engine": "python-plotnine"}
    assert record["tables"]["C"] == {"kind": "join", "tier1": "python-polars", "tier2": NOT_RUN}
    assert record["tables"]["T"] == {"kind": "table", "tier1": "python-polars"}          # the ingredient of the join: its tier 1 ran
    assert record["plots"]["p"]["plot_engine"] == "python-plotnine" and record["plots"]["p"]["drawn"] is True


def test_the_tier2_engine_is_recorded_when_the_join_has_tier2_steps(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch, steps_tier2=[FILTER_A])
    assert run["engines"]["tables"]["C"]["tier2"] == "python-polars"


def test_the_versions_of_the_libraries_of_the_engines_used_are_recorded_as_installed(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch)
    versions = run["engines"]["library_versions"]
    assert versions == {"python-polars": engines.engine_versions("python-polars"),
                        "python-plotnine": engines.engine_versions("python-plotnine")}
    assert set(versions["python-polars"]) == {"polars", "transformer"} and versions["python-polars"]["polars"] != "unknown"


def test_a_plot_with_its_own_engine_and_one_with_its_own_theme_are_recorded_as_such(tmp_path, monkeypatch):
    def edit(text):
        text = add_plot(text, "q", "        plot_engine: python-plotnine\n")
        return text.replace("          - name: geom_bar\n            params: {}\n      q:",
                            "          - name: geom_bar\n            params: {}\n          - name: theme_bw\n            params: {base_size: 14}\n      q:")
    run = effective_run(tmp_path, monkeypatch, edit)
    plots = run["engines"]["plots"]
    assert plots["q"]["plot_engine"] == "python-plotnine"
    assert {"component": "theme_bw", "params": {"base_size": 14}, "from": "the plot entry"} in plots["p"]["theme"]["components"]
    assert plots["p"]["theme"]["plotnine_default"]["applies"] is False
    assert plots["q"]["theme"]["components"] == [] or all(not c["component"].startswith("theme_") for c in plots["q"]["theme"]["components"])


def test_a_plot_with_no_theme_records_the_default_of_plotnine_honestly(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch)
    theme = run["engines"]["plots"]["p"]["theme"]
    assert theme["plotnine_default"] == {"applies": True, "name": "theme_gray"}
    assert [c for c in theme["components"] if c["component"].startswith("theme_")] == []


def test_a_plot_that_failed_is_recorded_without_a_theme_and_the_record_is_still_written(tmp_path, monkeypatch):
    def edit(text):
        return text.rstrip("\n") + ("\n      bad:\n        ui_label: bad\n        target_dataset: C\n        mapping: {x: group}\n"
                                    "        layers:\n          - name: geom_not_a_component\n            params: {}\n")
    run = effective_run(tmp_path, monkeypatch, edit)
    plots = run["engines"]["plots"]
    assert plots["bad"]["drawn"] is False and plots["bad"]["theme"] is None
    assert plots["bad"]["plot_engine"] == "python-plotnine" and "geom_not_a_component" in plots["bad"]["not_drawn_because"]
    assert plots["p"]["drawn"] is True and plots["p"]["theme"] is not None      # the plot next to it is untouched


def test_a_plot_engine_the_app_has_no_library_for_is_recorded_as_written_and_not_drawn_and_has_no_versions(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch, lambda text: text.replace("        target_dataset: C\n", "        plot_engine: r-ggplot2\n        target_dataset: C\n"))
    record = run["engines"]
    assert record["plots"]["p"]["plot_engine"] == "r-ggplot2" and record["plots"]["p"]["drawn"] is False
    assert "r-ggplot2" not in record["library_versions"], "versions of an engine the app does not have are not invented"
    assert "python-plotnine" not in record["library_versions"], "no plot was drawn by it, so it is not an engine used"


def test_the_record_adds_one_key_and_changes_none_of_the_others(tmp_path, monkeypatch):
    run = effective_run(tmp_path, monkeypatch)
    assert OLD_KEYS <= set(run) and set(run) - OLD_KEYS == {"engines"}


def test_the_record_is_the_same_when_the_same_export_is_made_twice(tmp_path, monkeypatch):
    first = effective_run(tmp_path / "one", monkeypatch)
    second = effective_run(tmp_path / "two", monkeypatch)
    assert first["engines"] == second["engines"]


# --- the pure builder -----------------------------------------------------------------------------------------------------------


RAW = {
    "data_engine": "python-polars", "plot_engine": "python-plotnine",
    "data_schemas": {"A": {"tier1": {"steps": []}}, "B": {"tier1": {"data_engine": "engine-x", "steps": []}}},
    "joins": {"J": {"ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}], "tier1": {"steps": []},
                    "tier2": {"data_engine": "engine-y", "steps": [FILTER_A]}}},
}


def test_the_engine_of_every_tier_is_the_one_the_orchestrator_chooses_the_entry_with():
    """One source: the record never reads the recipe text a second time; it asks `tier_engine`, as `data_entry` does."""
    plots = [("p", {"target_dataset": "J"})]
    record = engine_record(RAW, plots, {"p": {"plot_engine": "python-plotnine", "drawn": True, "theme": None}})
    assert record["tables"]["J"] == {"kind": "join", "tier1": engines.tier_engine(RAW, RAW["joins"]["J"], "tier1"),
                                     "tier2": engines.tier_engine(RAW, RAW["joins"]["J"], "tier2")}
    assert record["tables"]["B"]["tier1"] == "engine-x" == engines.tier_engine(RAW, RAW["data_schemas"]["B"], "tier1")
    for table in ("A", "B"):
        assert "tier2" not in record["tables"][table], "a join reads the tier 1 of its ingredients, their tier 2 did not run"
    assert data_entry(RAW, RAW["data_schemas"]["A"], "tier1", where="x").engine == record["tables"]["A"]["tier1"]


def test_a_table_plotted_directly_records_both_its_tiers_and_is_not_overwritten_as_an_ingredient():
    raw = {**RAW, "data_schemas": {"A": {"tier1": {"steps": []}, "tier2": {"steps": [FILTER_A]}}, "B": {"tier1": {"steps": []}}}}
    plots = [("pa", {"target_dataset": "A"}), ("pj", {"target_dataset": "J"})]
    drawn = {p: {"plot_engine": "python-plotnine", "drawn": True, "theme": None} for p, _ in plots}
    assert engine_record(raw, plots, drawn)["tables"]["A"] == {"kind": "table", "tier1": "python-polars", "tier2": "python-polars"}
    assert engine_record(raw, plots[::-1], drawn)["tables"]["A"] == {"kind": "table", "tier1": "python-polars", "tier2": "python-polars"}


def test_a_recipe_that_names_no_engine_records_none_never_a_default():
    record = engine_record({"data_schemas": {"A": {"tier1": {"steps": []}}}}, [("p", {"target_dataset": "A"})],
                           {"p": {"plot_engine": None, "drawn": False, "theme": None}})
    assert record["recipe_default"] == {"data_engine": None, "plot_engine": None}
    assert record["tables"]["A"]["tier1"] is None and record["library_versions"] == {}


def test_a_plot_with_no_target_reads_no_table_and_an_empty_export_has_an_empty_record():
    assert engine_record(RAW, [], {})["tables"] == {} and engine_record(RAW, [], {})["plots"] == {}
    record = engine_record(RAW, [("p", {})], {"p": {"plot_engine": "python-plotnine", "drawn": True, "theme": None}})
    assert record["tables"] == {}


def test_a_plot_that_was_never_attempted_is_recorded_as_not_drawn_not_left_out():
    record = engine_record(RAW, [("p", {"target_dataset": "J", "plot_engine": "engine-z"})], {})
    assert record["plots"]["p"] == {"plot_engine": "engine-z", "drawn": False, "theme": None,
                                    "not_drawn_because": "it was not attempted in this export"}


def test_the_failed_plot_record_holds_the_engine_as_written_and_the_first_line_of_the_error():
    record = failed_plot_record(RAW, {"plot_engine": "python-plotnine"}, ValueError("first line\nsecond line"))
    assert record == {"plot_engine": "python-plotnine", "drawn": False, "theme": None, "not_drawn_because": "first line"}
    assert failed_plot_record(RAW, {}, ValueError("x"))["plot_engine"] == "python-plotnine"      # the recipe's, as the dispatcher reads it


def test_the_versions_are_those_of_the_engines_that_appear_in_the_record_only():
    record = engine_record(RAW, [("p", {"target_dataset": "J"})], {"p": {"plot_engine": "python-plotnine", "drawn": True, "theme": None}})
    assert set(record["library_versions"]) == {"python-polars", "python-plotnine"}      # engine-x and engine-y have no row: no invented versions


# --- the dispatcher gives the record of a plot it drew --------------------------------------------------------------------------


def test_the_dispatcher_records_the_engine_it_used_and_the_theme_of_the_plot_it_drew():
    import polars as pl
    recipe = {"plot_engine": "python-plotnine", "plots": {"p": {"mapping": {"x": "x"}, "layers": [{"name": "geom_bar", "params": {}}]}}}
    dispatcher = PlotEngines()
    plot = dispatcher.render(pl.DataFrame({"x": ["a", "b"]}), recipe, "p")
    record = dispatcher.record_of(plot, recipe, "p")
    assert record["plot_engine"] == plot_entry(None, recipe, "p").engine and record["drawn"] is True
    assert record["theme"]["plotnine_default"]["applies"] is True


def test_the_record_of_an_engine_that_says_nothing_of_its_theme_says_so(monkeypatch):
    monkeypatch.setitem(REGISTRY, "python-recorder", PlotEngineEntry(engine="python-recorder", factory=dict))
    recipe = {"plot_engine": "python-recorder", "plots": {"p": {}}}
    record = PlotEngines().record_of(object(), recipe, "p")
    assert record == {"plot_engine": "python-recorder", "drawn": True,
                      "theme": {"recorded": False, "reason": "the engine python-recorder does not say which theme it applied"}}


def test_a_theme_that_cannot_be_read_from_a_drawn_plot_is_told_in_the_record_and_the_plot_stays_drawn(monkeypatch):
    def broken(plot):
        raise RuntimeError("no steps")
    monkeypatch.setitem(REGISTRY, "python-recorder", PlotEngineEntry(engine="python-recorder", factory=dict, applied_theme=broken))
    record = PlotEngines().record_of(object(), {"plot_engine": "python-recorder", "plots": {"p": {}}}, "p")
    assert record["drawn"] is True and record["theme"]["recorded"] is False and "RuntimeError: no steps" in record["theme"]["reason"]


def test_a_table_plotted_directly_records_the_engine_its_own_tier1_names_not_the_recipes():
    record = engine_record(RAW, [("pb", {"target_dataset": "B"})], {"pb": {"plot_engine": "python-plotnine", "drawn": True, "theme": None}})
    assert record["tables"]["B"] == {"kind": "table", "tier1": "engine-x", "tier2": NOT_RUN}


def test_the_dispatcher_records_the_engine_of_the_plot_entry_not_the_recipes(monkeypatch):
    monkeypatch.setitem(REGISTRY, "python-recorder", PlotEngineEntry(engine="python-recorder", factory=dict))
    recipe = {"plot_engine": "python-plotnine", "plots": {"p": {"plot_engine": "python-recorder"}}}
    assert PlotEngines().record_of(object(), recipe, "p")["plot_engine"] == "python-recorder"
