"""The engine reads the tier 3 of a plot entry: the table a plot reads (piece A4 of slice A of the HOME audit redesign).

DEC17 (`recipe_format_spec.md`): `tier3: {data_engine?, steps}` on a plot entry is the data of that one plot. After this piece the plot,
its table and the export read ONE table, built by the engine (`DataOrchestrator.materialize_tier3`, name PROVISIONAL): the Tier 2 of
the plot's target (Tier 1 when it has no tier-2 steps) with the plot's own steps applied. Its key is ADR-101: `T3 = key(T2) . [s3]`; an
empty tier 3 adds no part, so the key of the plot IS the key of its table and nothing is built or stored twice.

What is proved, headless, on a staged recipe with two plots on one table (one with tier-3 steps, one without):
- the table: the steps are applied (a filter and a column drop) after the Tier 2, to that plot only; the other plot is untouched;
- the key: its form, the empty part left out, a change of a tier-3 step moves only that plot's key, an upstream change moves it, the
  tier-3 engine is in it and the plot engine is not;
- a step that cannot be applied raises, naming the plot and the step; never skipped;
- HOME's audit nodes apply on top, in the same order as before (`audited_frame`);
- the real export generator (run as `test_export_download_path.py` runs it) reads the T3 table: the plot is drawn from it, the bundle holds
  its `T3_data_<plot>.tsv`, the record holds the plot's key only when tier 3 is not empty;
- a recipe with no tier-3 step: every plot key is the key of its table, on every shipped recipe.

Mutation index (each seen failing, see the report): MUTATION R1 the reader ignores the steps (`return lf` before the loop); MUTATION R2 the
`s3` part is left out of the key of a plot with steps; MUTATION R3 the export reads the Tier 2 of the target instead of the plot's table.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_tier3_reader.py -q
"""
import copy
import io
import re
import zipfile
from pathlib import Path

import polars as pl
import pytest
from PIL import Image

from app.modules.cache_keys import (
    clear_data_analysis_recipe_cache, data_analysis_recipe_keys, load_data_analysis_recipe, plot_tier3_key, tier3_steps)
from app.modules.engine_registry import PlotEngines
from app.modules.orchestrator import DataOrchestrator
from app.modules.t3_audit_engine import AuditStepError, audited_frame
from app.tests.audit_nodes import filter_nodes
from app.tests.test_export_download_path import _download_function, _run
from app.tests.test_table_keys import ROOT, SHIPPED, load_raw
from utils.errors import DataAnalysisRecipeError, TransformationError
from utils.recipe_tiers import plot_entries

HEX = "[0-9a-f]{32}"
T1_FORM = re.compile(rf"^E-{HEX}\.rC-{HEX}\.dC-{HEX}$")
T2_FORM = re.compile(rf"^E-{HEX}\.rC-{HEX}\.dC-{HEX}\.s2-{HEX}$")
T3_FORM = re.compile(rf"^E-{HEX}\.rC-{HEX}\.dC-{HEX}(\.s2-{HEX})?\.s3-{HEX}$")

KEEP_FROM_3 = {"action": "modif_filter", "column": "score", "op": "ge", "value": 3, "na": "remove"}
KEEP_UP_TO_4 = {"action": "modif_filter", "column": "score", "op": "le", "value": 4, "na": "remove"}
KEEP_FROM_2 = {"action": "modif_filter", "column": "score", "op": "ge", "value": 2, "na": "remove"}
DROP_GROUP = {"action": "polars_drop", "columns": ["group"]}
DATA = "sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\t5\n"


class Tier3World:
    """Table T (5 rows, scores 1 to 5, groups A A B B B), the join C that reads it (so a Tier 2 can be tried), and two plots on C:
    `p_steps` (the tier-3 steps given) and `p_plain` (none). `tier2` is the tier-2 list of C."""

    def __init__(self, root: Path, *, tier2=(), tier3=(KEEP_FROM_3, DROP_GROUP), tier3_engine=None, plot_engine_on_entry=None):
        self.root = root
        self.data_dir = root / "data"
        self.data_analysis_recipes_dir = root / "data_analysis_recipes"
        self.anchors = root / "user" / "anchors"
        for d in (self.data_dir, self.data_analysis_recipes_dir, self.anchors):
            d.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "T.tsv"
        self.write_data(DATA)
        self.write(tier2=tier2, tier3=tier3, tier3_engine=tier3_engine, plot_engine_on_entry=plot_engine_on_entry)
        self.orch = DataOrchestrator(self.data_analysis_recipes_dir, self.data_dir)

    def write_data(self, text: str) -> None:
        self.data_file.write_text(text)

    def write(self, *, tier2=(), tier3=(KEEP_FROM_3, DROP_GROUP), tier3_engine=None, plot_engine_on_entry=None, recipe_plot_engine="python-plotnine") -> None:
        import json
        tier2_text = f"    tier2: {{steps: {json.dumps(list(tier2))}}}\n" if tier2 else ""
        engine_line = f"          data_engine: {tier3_engine}\n" if tier3_engine else ""
        plot_engine_line = f"        plot_engine: {plot_engine_on_entry}\n" if plot_engine_on_entry else ""
        tier3_text = f"        tier3:\n{engine_line}          steps: {json.dumps(list(tier3))}\n" if tier3 is not None else ""
        (self.data_analysis_recipes_dir / "tiny.yaml").write_text(f"""id: tiny
info: {{ui_label: Tiny}}
data_engine: python-polars
plot_engine: {recipe_plot_engine}
data_schemas:
  T:
    source: {{type: local_tsv, path: {self.data_file}}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: String, ui_label: Sample, is_entity_id: true}}
      group: {{original_name: group, type: String, ui_label: Group}}
      score: {{original_name: score, type: Int64, ui_label: Score}}
    tier1: {{steps: []}}
joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: []}}
{tier2_text}analysis_groups:
  g:
    ui_label: G
    plots:
      p_steps:
{plot_engine_line}        ui_label: With steps
        description: The plot that has tier-3 steps.
        target_dataset: C
        mapping: {{x: sample_id}}
        layers:
          - name: geom_bar
            params: {{}}
{tier3_text}      p_plain:
        ui_label: Plain
        description: The plot that has none.
        target_dataset: C
        mapping: {{x: group}}
        layers:
          - name: geom_bar
            params: {{}}
""")
        clear_data_analysis_recipe_cache()

    def keys(self):
        return self.orch.compute_data_analysis_recipe_keys("tiny")

    def table(self, plot_id: str) -> pl.DataFrame:
        return self.orch.materialize_tier3("tiny", plot_id, self.anchors, keys=self.keys()).collect()

    def raw(self) -> dict:
        return load_data_analysis_recipe(self.data_analysis_recipes_dir / "tiny.yaml").raw


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def ids(frame: pl.DataFrame) -> list:
    return sorted(frame["sample_id"].to_list())


# =====================================================================================================================
# The table
# =====================================================================================================================


def test_the_steps_of_a_plot_are_applied_to_that_plots_table_and_the_other_plot_is_untouched(tmp_path):
    """MUTATION R1: the reader ignores the steps; this fails (five rows and the column `group` come back)."""
    world = Tier3World(tmp_path)
    with_steps, plain = world.table("p_steps"), world.table("p_plain")
    assert ids(with_steps) == ["s3", "s4", "s5"], "the filter of the tier 3 (score at least 3) ran"
    assert "group" not in with_steps.columns, "the column drop of the tier 3 ran"
    assert ids(plain) == ["s1", "s2", "s3", "s4", "s5"] and "group" in plain.columns, "the plot with no tier-3 steps reads its table as it is"


def test_a_plot_with_no_tier3_steps_reads_exactly_the_tier2_table_and_stores_nothing_for_it(tmp_path):
    """D-0343: a plot with tier-3 steps of its own has its table stored by its key; a plot without reads the Tier 2 (T3 = T2) and adds no file."""
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    plain = world.table("p_plain")
    assert plain.equals(world.orch.materialize_tier2("tiny", "C", world.anchors / "C.parquet", keys=world.keys()).collect())
    assert sorted(p.name for p in world.anchors.iterdir()) == ["C.parquet", "C__T2.parquet"], "p_plain has no file of its own"
    world.table("p_steps")
    stored = sorted(p.name for p in world.anchors.iterdir())
    assert stored == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"], f"only the plot with its own tier-3 steps has a file: {stored}"


def test_the_tier3_runs_after_the_tier2_in_that_order(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2], tier3=[KEEP_UP_TO_4])
    assert ids(world.table("p_steps")) == ["s2", "s3", "s4"], "tier 2 keeps scores 2 to 5, tier 3 keeps up to 4"
    assert ids(world.table("p_plain")) == ["s2", "s3", "s4", "s5"]


def test_the_steps_are_applied_in_the_order_written(tmp_path):
    """A drop first and then a filter on the dropped column cannot run; the other order can: order matters."""
    ok = Tier3World(tmp_path / "ok", tier3=[KEEP_FROM_3, {"action": "polars_drop", "columns": ["score"]}])
    assert ids(ok.table("p_steps")) == ["s3", "s4", "s5"]
    bad = Tier3World(tmp_path / "bad", tier3=[{"action": "polars_drop", "columns": ["score"]}, KEEP_FROM_3])
    with pytest.raises(TransformationError) as error:
        bad.table("p_steps")
    assert "step 2" in str(error.value)


def test_a_tier3_that_removes_every_row_gives_an_empty_table_not_an_error(tmp_path):
    world = Tier3World(tmp_path, tier3=[{**KEEP_FROM_3, "value": 99}])
    assert world.table("p_steps").height == 0
    assert world.table("p_plain").height == 5


def test_an_empty_tier3_steps_list_and_no_tier3_at_all_read_the_table_as_it_is(tmp_path):
    for label, tier3 in (("empty", []), ("absent", None)):
        world = Tier3World(tmp_path / label, tier3=tier3)
        assert ids(world.table("p_steps")) == ["s1", "s2", "s3", "s4", "s5"], label


def test_a_tier3_step_that_cannot_be_applied_raises_naming_the_plot_and_the_step_and_is_never_skipped(tmp_path):
    for label, steps, number, action in (
            ("a column that is not there", [KEEP_FROM_3, {"action": "polars_drop", "columns": ["nope"]}], 2, "polars_drop"),
            ("an action that is not registered", [{"action": "polars_no_such_action"}], 1, "polars_no_such_action"),
            ("a filter on a column that is not there", [{**KEEP_FROM_3, "column": "nope"}], 1, "modif_filter"),
            ("a step with no action", [{"columns": ["group"]}], 1, "None")):
        world = Tier3World(tmp_path / re.sub(r"\W", "_", label), tier3=steps)
        with pytest.raises(TransformationError) as error:
            world.table("p_steps")
        message = str(error.value)
        assert "'p_steps'" in message and f"step {number}" in message and f"'{action}'" in message, (label, message)
        assert world.table("p_plain").height == 5, "the failing plot does not touch the other plot"


def test_a_plot_the_recipe_does_not_name_or_a_plot_with_no_target_is_an_error(tmp_path):
    world = Tier3World(tmp_path)
    with pytest.raises(DataAnalysisRecipeError, match="no plot 'ghost'"):
        world.orch.materialize_tier3("tiny", "ghost", world.anchors, keys=world.keys())
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    recipe.write_text(recipe.read_text().replace("target_dataset: C\n        mapping: {x: group}", "mapping: {x: group}"))
    clear_data_analysis_recipe_cache()
    with pytest.raises(DataAnalysisRecipeError, match="no target_dataset"):
        world.orch.materialize_tier3("tiny", "p_plain", world.anchors, keys=world.keys())


def test_a_tier3_engine_this_app_has_no_library_for_is_refused_also_when_there_are_no_steps(tmp_path):
    for steps in ([], [KEEP_FROM_3]):
        world = Tier3World(tmp_path / str(len(steps)), tier3=steps, tier3_engine="engine-x")
        with pytest.raises(DataAnalysisRecipeError, match="no library for this engine in this app"):
            world.table("p_steps")


def test_the_recipe_in_memory_is_not_changed_by_a_read(tmp_path):
    world = Tier3World(tmp_path)
    before = copy.deepcopy(world.raw())
    world.table("p_steps")
    world.table("p_steps")
    assert world.raw() == before


# =====================================================================================================================
# The key (ADR-101)
# =====================================================================================================================


def test_the_key_of_a_plot_with_steps_is_the_key_of_its_table_and_one_more_labelled_part(tmp_path):
    """MUTATION R2: the `s3` part is left out; this fails."""
    world = Tier3World(tmp_path)
    keys = world.keys()
    key = keys.plot_key_of("p_steps")
    assert T3_FORM.match(key), key
    assert key.startswith(keys.tier2_key_of("C") + ".s3-") and key.count(".") == 3, "T1 key (three parts), then s3"
    assert T1_FORM.match(keys.tier1_key_of("C"))


def test_an_empty_tier3_adds_no_part_so_the_key_of_the_plot_is_the_key_of_its_table(tmp_path):
    """Example, with and without tier-2 steps. The key is the table's: nothing is built or stored twice."""
    no_t2 = Tier3World(tmp_path / "a")
    keys = no_t2.keys()
    assert keys.plot_key_of("p_plain") == keys.tier2_key_of("C") == keys.tier1_key_of("C"), "no tier 2, no tier 3: T3 = T2 = T1"
    assert T1_FORM.match(keys.plot_key_of("p_plain"))
    with_t2 = Tier3World(tmp_path / "b", tier2=[KEEP_FROM_2])
    keys = with_t2.keys()
    assert keys.plot_key_of("p_plain") == keys.tier2_key_of("C") != keys.tier1_key_of("C")
    assert T2_FORM.match(keys.plot_key_of("p_plain"))
    assert T3_FORM.match(keys.plot_key_of("p_steps")) and keys.plot_key_of("p_steps").startswith(keys.tier2_key_of("C") + ".s3-")
    emptied = Tier3World(tmp_path / "c", tier3=[])
    assert emptied.keys().plot_key_of("p_steps") == emptied.keys().tier1_key_of("C"), "an empty list is no part, as an absent tier 3"


def test_a_change_of_a_tier3_step_moves_that_plots_key_and_no_other_key(tmp_path):
    world = Tier3World(tmp_path)
    before = world.keys()
    world.write(tier3=[{**KEEP_FROM_3, "value": 4}, DROP_GROUP])
    after = world.keys()
    assert after.plot_key_of("p_steps") != before.plot_key_of("p_steps")
    assert after.plot_key_of("p_plain") == before.plot_key_of("p_plain")
    assert after.tier1_keys == before.tier1_keys and after.tier2_keys == before.tier2_keys, "no table key moves"
    first = after.plot_key_of("p_steps")
    world.write(tier3=[DROP_GROUP, {**KEEP_FROM_3, "value": 4}])
    assert world.keys().plot_key_of("p_steps") != first, "the order of the steps moves the key"


def test_an_upstream_change_moves_the_key_of_the_plot(tmp_path):
    world = Tier3World(tmp_path)
    base = world.keys()
    world.write(tier2=[KEEP_FROM_2])                 # a tier-2 step of the table the plot reads
    changed_t2 = world.keys()
    assert changed_t2.plot_key_of("p_steps") != base.plot_key_of("p_steps")
    assert changed_t2.plot_key_of("p_plain") != base.plot_key_of("p_plain")
    assert changed_t2.tier1_key_of("C") == base.tier1_key_of("C"), "a tier-2 step does not move a tier-1 key"
    world.write_data(DATA + "s6\tB\t6\n")            # the data file the table reads
    changed_data = world.keys()
    assert changed_data.plot_key_of("p_steps") != changed_t2.plot_key_of("p_steps")
    assert changed_data.plot_key_of("p_plain") != changed_t2.plot_key_of("p_plain")


def test_the_tier3_engine_is_in_the_key_of_the_plot_and_in_no_other_key():
    raw = {"data_engine": "python-polars", "analysis_groups": {"g": {"plots": {"p": {"target_dataset": "C", "tier3": {"steps": [KEEP_FROM_3]}}}}}}
    base = plot_tier3_key(raw, "p", "T2KEY")
    written_same = copy.deepcopy(raw)
    written_same["analysis_groups"]["g"]["plots"]["p"]["tier3"]["data_engine"] = "python-polars"
    assert plot_tier3_key(written_same, "p", "T2KEY") == base, "the engine written on the tier equals the one it inherits: an argument, not text"
    other = copy.deepcopy(raw)
    other["analysis_groups"]["g"]["plots"]["p"]["tier3"]["data_engine"] = "engine-x"
    assert plot_tier3_key(other, "p", "T2KEY") != base
    assert plot_tier3_key(other, "p", "T2KEY").startswith("T2KEY.s3-")


def test_the_plot_engine_is_in_no_key(tmp_path):
    world = Tier3World(tmp_path)
    before = world.keys()
    world.write(plot_engine_on_entry="python-plotnine", recipe_plot_engine="engine-y")
    after = world.keys()
    assert after.plot_keys == before.plot_keys and after.tier1_keys == before.tier1_keys and after.tier2_keys == before.tier2_keys


def test_a_plot_the_recipe_does_not_name_has_no_key_and_a_table_it_does_not_name_gets_the_coarse_key(tmp_path):
    keys = Tier3World(tmp_path).keys()
    with pytest.raises(KeyError, match="no plot 'ghost'"):
        keys.plot_key_of("ghost")
    assert keys.tier2_key_of("Ghost") == keys.coarse_tier1_key


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_every_plot_of_every_shipped_recipe_has_the_key_of_its_table_because_none_has_tier3_steps(path):
    """No shipped recipe writes tier-3 steps (the checker refused them): nothing changes for them, key by key."""
    if load_raw(path) is None:
        pytest.skip("an empty file holds no recipe")
    loaded = load_data_analysis_recipe(path)
    keys = data_analysis_recipe_keys(loaded, {})
    for plot_id, entry in plot_entries(loaded.raw).items():
        assert tier3_steps(loaded.raw, plot_id) == [], (path, plot_id)
        assert keys.plot_key_of(plot_id) == keys.tier2_key_of(entry["target_dataset"]), (path, plot_id)


# =====================================================================================================================
# HOME's audit nodes apply on top, in the same order as before
# =====================================================================================================================


def test_the_audit_nodes_of_my_view_apply_on_top_of_the_plots_table(tmp_path):
    world = Tier3World(tmp_path)
    base = world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())
    nodes = filter_nodes([{"column": "score", "op": "le", "value": 4, "dtype": "Int64", "na": "remove"}])
    assert ids(audited_frame(base, nodes, "p_steps").collect()) == ["s3", "s4"], "the recipe's s3..s5, then the audited score <= 4"


def test_an_audit_node_on_a_column_the_plots_tier3_dropped_is_an_error_naming_the_plot(tmp_path):
    """The audit sees the plot's table after its tier 3: a column the recipe dropped is not there to filter (never skipped)."""
    world = Tier3World(tmp_path)
    base = world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())
    nodes = filter_nodes([{"column": "group", "op": "eq", "value": "A", "dtype": "String", "na": "remove"}])
    with pytest.raises(AuditStepError) as error:
        audited_frame(base, nodes, "p_steps")
    assert "p_steps" in str(error.value)
    plain = world.orch.materialize_tier3("tiny", "p_plain", world.anchors, keys=world.keys())
    assert ids(audited_frame(plain, nodes, "p_plain").collect()) == ["s1", "s2"], "the other plot still has the column"


# =====================================================================================================================
# The export reads the one table (the real generator, as test_export_download_path.py runs it)
# =====================================================================================================================


def _export(tmp_path, monkeypatch, **world_args):
    world = Tier3World(tmp_path, **world_args)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    drawn: dict[str, list] = {}
    real_render = PlotEngines.render

    def recording_render(self, df, recipe, plot_id, **kw):
        collected = df.collect() if hasattr(df, "collect") else df
        drawn[plot_id] = [collected.columns, sorted(collected["sample_id"].to_list()) if "sample_id" in collected.columns else None]
        return real_render(self, df, recipe, plot_id, **kw)

    monkeypatch.setattr(PlotEngines, "render", recording_render)
    notes: list = []
    yielded = _run(_download_function(world, view, notes, monkeypatch))
    return world, view, drawn, zipfile.ZipFile(io.BytesIO(yielded[0])), notes


def test_the_export_draws_each_plot_from_its_table_writes_the_t3_data_and_records_the_plots_key(tmp_path, monkeypatch):
    """MUTATION R3: the export reads the Tier 2 of the target for the plots; the first assertion fails (the plot drew five rows)."""
    world, view, drawn, bundle, notes = _export(tmp_path, monkeypatch)
    names = bundle.namelist()
    assert "EXPORT_NOT_CREATED.txt" not in names and not [t for t, _ in notes if t == "error"], notes
    assert drawn["p_steps"] == [["sample_id", "score"], ["s3", "s4", "s5"]], "the plot is drawn from its table (steps applied, group dropped)"
    assert drawn["p_plain"][1] == ["s1", "s2", "s3", "s4", "s5"] and "group" in drawn["p_plain"][0]
    t3_files = [n for n in names if "/T3_data_" in n and not n.endswith("_ERROR.txt")]
    assert [Path(n).name for n in t3_files] == ["T3_data_p_steps.tsv"], "a T3 data file only for the plot whose table is not the Tier 2"
    table = pl.read_csv(io.BytesIO(bundle.read(t3_files[0])), separator="\t")
    assert sorted(table["sample_id"].to_list()) == ["s3", "s4", "s5"] and table.columns == ["sample_id", "score"]
    readme = bundle.read(next(n for n in names if n.endswith("/README.txt"))).decode()
    assert f"plot p_steps: tier3_key={view.plot_key_of('p_steps')}" in readme
    assert "p_plain: tier3_key" not in readme, "the plot's key is recorded only when its tier 3 is not empty"
    assert "C: tier2_key=none (T2 equals T1)" in readme, "the record keeps its words for a table with no tier-2 steps"
    assert f"C: tier1_key={view.tier1_key_of('C')}" in readme
    picture = next(n for n in names if n.endswith("/plots/p_steps.png"))
    assert Image.open(io.BytesIO(bundle.read(picture))).text["sparmvet:tier3_key"] == view.plot_key_of("p_steps")
    plain_picture = next(n for n in names if n.endswith("/plots/p_plain.png"))
    assert "sparmvet:tier3_key" not in Image.open(io.BytesIO(bundle.read(plain_picture))).text


def test_the_engine_record_names_the_tier3_engine_only_for_a_plot_with_tier3_steps(tmp_path):
    from app.modules.engine_record import engine_record
    raw = Tier3World(tmp_path).raw()
    record = engine_record(raw, list(plot_entries(raw).items()), {})
    assert record["plots"]["p_steps"]["tier3"] == "python-polars"
    assert "tier3" not in record["plots"]["p_plain"], "nothing ran for a plot with no tier-3 steps"
    assert "python-polars" in record["library_versions"]


def test_the_export_of_a_recipe_with_no_tier3_steps_has_no_t3_file_and_no_plot_key(tmp_path, monkeypatch):
    world, view, drawn, bundle, notes = _export(tmp_path, monkeypatch, tier3=None)
    names = bundle.namelist()
    assert not [n for n in names if "T3_data_" in n]
    assert "tier3_key" not in bundle.read(next(n for n in names if n.endswith("/README.txt"))).decode()
    assert drawn["p_steps"][1] == ["s1", "s2", "s3", "s4", "s5"]


def test_the_export_applies_the_audited_steps_on_top_of_the_recipes_tier3(tmp_path, monkeypatch):
    """A plot with recipe steps AND an audited step: the table, the picture and the T3 file hold both, the recipe's first."""
    from types import SimpleNamespace
    home_state = SimpleNamespace(get=lambda: {"t3_audit_steps_by_plot": {"subtab_p_steps": filter_nodes(
        [{"column": "score", "op": "le", "value": 4, "dtype": "Int64", "na": "remove"}])}})
    world = Tier3World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    drawn: dict = {}
    real_render = PlotEngines.render
    monkeypatch.setattr(PlotEngines, "render", lambda self, df, recipe, plot_id, **kw: (
        drawn.__setitem__(plot_id, sorted(df.collect()["sample_id"].to_list())), real_render(self, df, recipe, plot_id, **kw))[1])
    yielded = _run(_download_function(world, view, [], monkeypatch, home_state=home_state,
                                      t3_filter_rows=lambda subtab: [{"column": "score"}] if subtab == "subtab_p_steps" else [],
                                      t3_drop_columns=lambda subtab: []))
    bundle = zipfile.ZipFile(io.BytesIO(yielded[0]))
    assert "EXPORT_NOT_CREATED.txt" not in bundle.namelist()
    assert drawn["p_steps"] == ["s3", "s4"] and drawn["p_plain"] == ["s1", "s2", "s3", "s4", "s5"]
    t3_file = next(n for n in bundle.namelist() if n.endswith("T3_data_p_steps.tsv"))
    assert sorted(pl.read_csv(io.BytesIO(bundle.read(t3_file)), separator="\t")["sample_id"].to_list()) == ["s3", "s4"]


def test_an_export_of_a_plot_whose_tier3_cannot_be_applied_loses_nothing_silently(tmp_path, monkeypatch):
    """The failing plot is not drawn and the bundle says so (the export's own failed-plot path); the other plot is exported."""
    world, view, drawn, bundle, notes = _export(tmp_path, monkeypatch, tier3=[{"action": "polars_drop", "columns": ["nope"]}])
    names = bundle.namelist()
    assert "p_steps" not in drawn and drawn["p_plain"][1] == ["s1", "s2", "s3", "s4", "s5"]
    assert not any(n.endswith("/plots/p_steps.png") for n in names)
    assert [m for t, m in notes if t in ("error", "warning") and "p_steps" in m], notes


def test_a_failure_that_depends_on_a_value_is_named_by_the_plot_and_the_step_when_the_table_is_stored(tmp_path):
    """M3, changed by D-0343: the table of the plot is stored when it is built, so a cast of a value that does not fit shows then, and the app names the plot
    and the first step that fails (`build_failure`), not the engine's bare sentence. A plot without tier-3 steps keeps the error as it is."""
    from app.modules.orchestrator import plot_read_error_text
    world = Tier3World(tmp_path, tier3=(KEEP_FROM_3, {"action": "polars_cast", "columns": ["group"], "dtype": "Int64"}))
    with pytest.raises(TransformationError) as error:
        world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=world.keys())
    text = str(error.value)
    assert "'p_steps'" in text and "step 2 ('polars_cast')" in text and "group" in text, text
    assert "Resolved plan" not in text, "the plan of the engine is left out"
    assert not (world.anchors / "C__T3_p_steps.parquet").exists(), "a table that failed is not stored"
    raw_text = "boom"
    assert plot_read_error_text(world.raw(), "p_plain", ValueError(raw_text)) == raw_text, "a plot without tier-3 steps: the error as it is"


def test_the_propagation_dialogs_column_check_reads_each_plot_own_table_not_the_first_plots_of_the_same_target(tmp_path):
    """L1: two plots on one table with different tier-3 steps (one drops `group`) must not share a schema in the dialog's check."""
    from types import SimpleNamespace
    from app.tests.test_audit_join_key_drops import closure
    world = Tier3World(tmp_path)                      # p_steps drops `group`; p_plain keeps it
    subtabs = ["subtab_p_steps", "subtab_p_plain"]
    check = closure(
        "_column_presence_per_plot",
        _resolve_active_spec=lambda p_id: {"target_dataset": "C", "plot": p_id},
        # an audit step is written at the plot's table: the check asks for T3 explicitly, whatever table the data choice shows (slice B)
        _resolve_active_lf=lambda spec, tier=None: (world.orch.materialize_tier3("tiny", spec["plot"], world.anchors, keys=world.keys())
                                                    if tier == "T3" else pytest.fail(f"the column check read tier {tier!r}, not T3")))
    node = {"params": {"column": "group"}}
    assert check([node], subtabs) == {"subtab_p_steps": "absent", "subtab_p_plain": "present"}
    assert check([node], subtabs[::-1]) == {"subtab_p_steps": "absent", "subtab_p_plain": "present"}, "the order of the plots does not matter"
