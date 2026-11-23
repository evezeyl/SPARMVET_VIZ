"""A build that fails says which table, which tier and which step (opening-build, D-0326, D-0327; D-0176).

Polars raises its own error when a stored table is computed: it names a column or a value but neither the table nor the step, and it
carries the plan of the query. `build_failure` finds the first step that fails (a prefix of the steps at a time, after a failure only)
and the orchestrator raises the plain error. Two bare engine errors were seen on the shipped data: a tier 2 step that names a column
that is not there, and a tier 1 cast of a value that does not fit (the file declares text, the step casts to a number).

What is proved, on a staged recipe built in the test (a table T, a join C that reads it, a plot P; no shipped recipe changes):
- a tier-2 step that names a missing column: the error names the tier, the table, the step number and its action, and the column;
- a tier-1 cast of a value that does not fit, in a source table: the error names the table, the tier and the step, never the join that read it;
- the same cast written in the join: the error names the join;
- a tier-3 step: the plot, the step; and nothing is stored for a table that failed (no file, no key that could be served);
- the engine's plan ("Resolved plan") is left out of every message; a build that works is not run twice (the prefixes are tried only after a failure);
- `first_failing_step` finds the first step by halving: with N steps it builds a few prefixes, not N.

Mutation index (each seen failing): MUTATION F1 the orchestrator re-raises the bare engine error (no explanation) -> the first four tests fail;
MUTATION F2 `first_failing_step` returns the last step -> the step numbers fail.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_build_failure_names.py -q
"""
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.build_failure import first_failing_step, short_engine_text
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.errors import TransformationError

DATA = "sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\tabc\n"   # the last score is not a number
CAST_SCORE = {"action": "polars_cast", "columns": ["score"], "dtype": "Float64"}
DROP_NOPE = {"action": "polars_drop", "columns": ["no_such_column"]}
KEEP_ALL = {"action": "modif_filter", "column": "sample_id", "op": "ne", "value": "never", "na": "keep"}


class World:
    """A table T (score declared as TEXT, so the file is read), the join C that reads it, the plot P on C. Each tier takes the steps given."""

    def __init__(self, root: Path, *, t1=(), c1=(), c2=(), p3=(), data=DATA):
        self.root = root
        self.data_dir = root / "data"
        self.recipes = root / "recipes"
        self.anchors = root / "anchors"
        for d in (self.data_dir, self.recipes, self.anchors):
            d.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "T.tsv").write_text(data)
        tier3 = f"        tier3: {{steps: {json.dumps(list(p3))}}}\n" if p3 else ""
        (self.recipes / "tiny.yaml").write_text(f"""id: tiny
info: {{ui_label: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
    source: {{type: local_tsv, path: {self.data_dir / 'T.tsv'}}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: String, ui_label: Sample, is_entity_id: true}}
      group: {{original_name: group, type: String, ui_label: Group}}
      score: {{original_name: score, type: String, ui_label: Score}}
    tier1: {{steps: {json.dumps(list(t1))}}}
joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: {json.dumps(list(c1))}}}
    tier2: {{steps: {json.dumps(list(c2))}}}
analysis_groups:
  g:
    ui_label: G
    plots:
      P:
        ui_label: P
        target_dataset: C
        mapping: {{x: group}}
        layers:
          - name: geom_bar
            params: {{}}
{tier3}""")
        clear_data_analysis_recipe_cache()
        self.orch = DataOrchestrator(self.recipes, self.data_dir)

    def keys(self):
        return self.orch.compute_data_analysis_recipe_keys("tiny")

    def tier1(self):
        return self.orch.materialize_tier1("tiny", "C", self.anchors / "C.parquet", keys=self.keys())

    def tier2(self):
        return self.orch.materialize_tier2("tiny", "C", self.anchors / "C.parquet", keys=self.keys())

    def tier3(self):
        return self.orch.materialize_tier3("tiny", "P", self.anchors, keys=self.keys())

    def stored(self) -> list:
        return sorted(p.name for p in self.anchors.iterdir())


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def test_a_tier2_step_that_names_a_missing_column_is_named_by_table_tier_and_step(tmp_path):
    world = World(tmp_path, c2=[KEEP_ALL, DROP_NOPE])
    with pytest.raises(TransformationError) as error:
        world.tier2()
    text = str(error.value)
    assert "tier 2 of the table 'C'" in text and "step 2 ('polars_drop')" in text and "no_such_column" in text, text
    assert "Resolved plan" not in text and "\n" not in text, "the plan of the engine is left out and the message is one line"
    assert "'C'" in error.value.tip
    assert "C__T2.parquet" not in world.stored(), "a table that failed is not stored"


def test_a_tier1_cast_of_a_value_that_does_not_fit_is_named_by_the_source_table_and_the_step(tmp_path):
    world = World(tmp_path, t1=[KEEP_ALL, CAST_SCORE])
    with pytest.raises(TransformationError) as error:
        world.tier1()
    text = str(error.value)
    assert "tier 1 of the table 'T'" in text and "step 2 ('polars_cast')" in text, text
    assert "abc" in text and "score" in text, "the engine's own words (the column and the value) are kept"
    assert "Resolved plan" not in text
    assert world.stored() == [], "nothing is stored for a table that failed"


def test_the_same_cast_in_the_join_is_named_by_the_join(tmp_path):
    world = World(tmp_path, c1=[KEEP_ALL, CAST_SCORE])
    with pytest.raises(TransformationError) as error:
        world.tier1()
    text = str(error.value)
    assert "tier 1 of the join 'C'" in text and "step 2 ('polars_cast')" in text, text
    assert world.stored() == []


def test_a_tier3_cast_of_a_value_that_does_not_fit_is_named_by_the_plot_and_the_step(tmp_path):
    world = World(tmp_path, p3=[KEEP_ALL, CAST_SCORE])
    with pytest.raises(TransformationError) as error:
        world.tier3()
    text = str(error.value)
    assert "tier 3 of the plot 'P'" in text and "step 2 ('polars_cast')" in text, text
    assert not any("T3" in name for name in world.stored()), "the table of a plot whose build failed is not stored"


def test_a_recipe_that_works_is_not_explained_or_run_twice(tmp_path, monkeypatch):
    import app.modules.orchestrator as orchestrator
    calls = []
    monkeypatch.setattr(orchestrator, "first_failing_step", lambda *a, **k: calls.append(1))
    world = World(tmp_path, data=DATA.replace("abc", "5"), t1=[CAST_SCORE], c2=[KEEP_ALL], p3=[KEEP_ALL])
    assert world.tier3().collect().height == 5
    assert calls == [], "the steps are tried again only after a failure"


def test_first_failing_step_finds_the_first_step_by_halving():
    built = []

    def prefix(k):
        built.append(k)
        return pl.LazyFrame({"x": [1, 2]}).with_columns(pl.col("x").cast(pl.String).cast(pl.Int64) if k < 7 else pl.col("x").cast(pl.Int64).cast(pl.String).cast(pl.Int64) * pl.col("missing"))

    found = first_failing_step(prefix, 12)
    assert found is not None and found[0] == 7
    assert len(built) <= 6, f"halving, not one build per step: {built}"
    assert first_failing_step(lambda k: pl.LazyFrame({"x": [1]}), 5) is None, "no step fails: no answer"
    assert first_failing_step(lambda k: pl.LazyFrame({"x": [1]}), 0) is None, "no steps: no answer"


def test_the_engine_sentence_loses_its_plan_and_stays_short():
    class Boom(Exception):
        pass

    text = short_engine_text(Boom('"nope" not found\n\nResolved plan until failure:\n\n\t---> FAILED HERE\n' + "x" * 1000))
    assert text == '"nope" not found'
    assert len(short_engine_text(Boom("y" * 2000))) <= 410
