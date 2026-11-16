"""CATEGORICAL-MIGRATION-1 (Eve, 2026-11-15): the shipped recipes declare `String` for a nominal field and `Enum` for an
ordered one; one `Categorical` field is kept as the documented example.

What must hold: the counts per category of every plot are the ones recorded before the change
(`golden/categorical_counts_before.json`), no value is lost or null (the content hash of every table equals the one before,
`golden/categorical_content_before.json`; only the type text may differ), the `Enum` order is the written one, no join key
has a different type on its two sides, the stress `value` is a number, and no other `Categorical` is declared.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_categorical_migration.py -q
"""
import contextlib
import importlib.util
import io
import json
import re
import shutil
import tempfile
from pathlib import Path

import matplotlib
import polars as pl
import pytest
import yaml

matplotlib.use("Agg")

from app.modules.cache_keys import clear_data_analysis_recipe_cache  # noqa: E402
from app.modules.orchestrator import DataOrchestrator  # noqa: E402
from utils.config_loader import ConfigManager  # noqa: E402
from viz_factory.viz_factory import VizFactory  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "config" / "data_analysis_recipes"
RAW = ROOT / "assets" / "test_data"
GOLDEN = ROOT / "app" / "tests" / "golden"
COUNTS_BEFORE = json.loads((GOLDEN / "categorical_counts_before.json").read_text())
CONTENT_BEFORE = json.loads((GOLDEN / "categorical_content_before.json").read_text())["recipes"]
SUBDIR = {"complex_template": "templates", "retest_tier2": "retest", "retest_top_n_other": "retest"}

# Every `Categorical` that a shipped recipe may still declare: (file name, field), with the reason.
ALLOWED_CATEGORICAL = {
    ("fg_phenotypes_input_fields.yaml", "breakpoint"): "the documented Categorical example (Eve, 2026-11-15)",
    ("Stress_Source_input_fields.yaml", "collection_date"): "date: waits for Eve's answer (list Q5)",
    ("e_coli.yaml", "collection_date"): "date: waits for Eve's answer (list Q5)",
    ("audit.yaml", "submission_date"): "date: waits for Eve's answer (list Q5)",
}


def _load_script():
    spec = importlib.util.spec_from_file_location("golden_baseline", ROOT / "assets" / "scripts" / "golden_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gb = _load_script()


def _recipes_dir(recipe_id, base=RECIPES):
    return base / SUBDIR.get(recipe_id, "pipelines")


def _render(recipe_id, plot_id, base=RECIPES):
    """The plotted table and the drawn figure of one plot."""
    clear_data_analysis_recipe_cache()
    rdir = _recipes_dir(recipe_id, base)
    work = Path(tempfile.mkdtemp(prefix="catmig_"))
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            raw = ConfigManager(str(rdir / f"{recipe_id}.yaml")).raw_config
            orch = DataOrchestrator(rdir, RAW)
            keys = orch.compute_data_analysis_recipe_keys(recipe_id)
            target = dict(gb.plots_of(raw))[plot_id]
            anchor = work / "a.parquet"
            orch.materialize_tier1(recipe_id, target, anchor, keys=keys).collect()
            lf = orch.materialize_tier2(recipe_id, target, anchor, keys=keys)
            plot = VizFactory().render(lf, raw, plot_id)
            fig = plot.draw()
        return plot, fig
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _counts(data: pl.DataFrame, column: str):
    vc = data[column].cast(pl.String).value_counts()
    return sorted([[v if v is not None else "<null>", int(n)] for v, n in zip(vc[column].to_list(), vc["count"].to_list())])


# -- (1) counts per category, per plot, equal before and after --------------------------------

PLOTS = [(r, p) for r, plots in sorted(COUNTS_BEFORE.items()) for p in sorted(plots)]


@pytest.mark.parametrize("recipe_id,plot_id", PLOTS, ids=[f"{r}:{p}" for r, p in PLOTS])
def test_counts_per_category_equal_to_before(recipe_id, plot_id):
    plot, fig = _render(recipe_id, plot_id)
    data = pl.from_pandas(plot.data)
    before = COUNTS_BEFORE[recipe_id][plot_id]
    assert data.height == before["rows"]
    for column, counts in before["counts"].items():
        assert column in data.columns, f"{plot_id}: column {column} vanished"
        assert _counts(data, column) == counts, f"{plot_id}: counts of {column} changed"


# -- (2) no value lost or null: the content of every table equals the one before --------------

def test_every_table_has_the_content_it_had_before():
    """Rows, column names and the content hash of T1, T2 and every plotted table; the type text is not compared."""
    found = gb.build(RECIPES / "pipelines", RAW, sorted(CONTENT_BEFORE), True)["recipes"]
    problems = []
    for recipe_id, kinds in CONTENT_BEFORE.items():
        for kind, tables in kinds.items():
            for name, rec in tables.items():
                now = found[recipe_id][kind].get(name, {})
                got = {"rows": now.get("rows"), "names": [c.split(":")[0] for c in now.get("columns", [])], "sha256": now.get("sha256")}
                if got != rec:
                    problems.append(f"{recipe_id}/{kind}/{name}")
    assert not problems, problems


# -- (3) the Enum --------------------------------------------------------------------------

FG = RECIPES / "pipelines" / "figshare_integration" / "input_fields" / "fg_phenotypes_input_fields.yaml"


def test_the_enum_order_is_written_in_the_recipe():
    field = yaml.safe_load(FG.read_text())["predicted_phenotype"]
    assert field["type"] == "Enum"
    assert field["categories"] == ["S", "I", "R", "NI"]


def test_the_enum_order_is_the_order_of_the_plot_legend_and_levels():
    plot, fig = _render("figshare_integration", "plot_a_phenotype_bar")
    assert plot.data["predicted_phenotype"].cat.categories.tolist() == ["S", "I", "R", "NI"]
    drawn = [t.get_text() for t in fig.findobj(matplotlib.text.Text) if t.get_text() in {"S", "I", "R", "NI"}]
    assert drawn == ["S", "I", "R", "NI"]


def _figshare_copy_with_categories(categories, tmp_path):
    pipelines = tmp_path / "pipelines"
    pipelines.mkdir()
    src = RECIPES / "pipelines"
    shutil.copy(src / "figshare_integration.yaml", pipelines)
    shutil.copytree(src / "figshare_integration", pipelines / "figshare_integration")
    path = pipelines / "figshare_integration" / "input_fields" / FG.name
    text = path.read_text()
    new = re.sub(r"categories: \[.*\]", f"categories: [{', '.join(categories)}]", text)
    assert new != text or categories == ["S", "I", "R", "NI"]
    path.write_text(new)
    return tmp_path


def test_a_value_outside_the_enum_list_is_refused_naming_column_and_value(tmp_path):
    base = _figshare_copy_with_categories(["S", "I", "R"], tmp_path)  # NI is in the data
    with pytest.raises(Exception) as exc:  # noqa: PT011 - the type is the engine's; the text is what the user reads
        _render("figshare_integration", "plot_a_phenotype_bar", base=base)
    message = str(exc.value)
    assert "The column 'predicted_phenotype' is declared as Enum with the values S, I, R" in message and "'NI'" in message
    assert "Suggestion: add the value to `categories`" in exc.value.tip


def test_a_changed_enum_order_changes_the_drawn_order(tmp_path):
    """The test above is not vacuous: another written order gives another drawn order."""
    base = _figshare_copy_with_categories(["NI", "R", "I", "S"], tmp_path)
    plot, _ = _render("figshare_integration", "plot_a_phenotype_bar", base=base)
    assert plot.data["predicted_phenotype"].cat.categories.tolist() == ["NI", "R", "I", "S"]


# -- (4) join keys: the same type on both sides -----------------------------------------------

def _declared_types(raw):
    tables = {}
    for section in ("data_schemas", "additional_datasets_schemas"):
        for name, table in (raw.get(section) or {}).items():
            tables[name] = {f: spec.get("type") for f, spec in (table.get("input_fields") or {}).items()}
    meta = raw.get("metadata_schema") or {}
    if meta.get("input_fields"):
        tables["metadata_schema"] = {f: spec.get("type") for f, spec in meta["input_fields"].items()}
    return tables


def _join_pairs():
    pairs = []
    for sub, rid in [("pipelines", r.stem) for r in sorted((RECIPES / "pipelines").glob("*.yaml"))] + [("retest", r.stem) for r in sorted((RECIPES / "retest").glob("*.yaml"))]:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                raw = ConfigManager(str(RECIPES / sub / f"{rid}.yaml")).raw_config
        except BaseException:  # noqa: BLE001 - a recipe that is broken on purpose
            continue
        types = _declared_types(raw)
        for join_name, join in (raw.get("joins") or {}).items():
            ingredients = [i.get("dataset_id") for i in join.get("ingredients") or []]
            steps = [s for tier in (join.get("steps") or {}).values() for s in tier or []]
            for step in steps:
                if step.get("action") != "polars_join":
                    continue
                left, right = ingredients[0], step.get("right_ingredient")
                on = step.get("on")
                lk = step.get("left_on", on)
                rk = step.get("right_on", on)
                lk = [lk] if isinstance(lk, str) else lk or []
                rk = [rk] if isinstance(rk, str) else rk or []
                for a, b in zip(lk, rk):
                    ta, tb = types.get(left, {}).get(a), types.get(right, {}).get(b)
                    if ta and tb:
                        pairs.append((rid, join_name, left, a, ta, right, b, tb))
    return pairs


def test_no_join_key_changes_type_on_one_side_only():
    pairs = _join_pairs()
    assert len(pairs) > 20  # the shipped recipes do have declared key pairs; the scan is not empty
    assert [p for p in pairs if p[4] != p[7]] == []


# -- (5) the stress value is a number ----------------------------------------------------------

def test_the_stress_value_is_numeric_downstream():
    clear_data_analysis_recipe_cache()
    rdir = RECIPES / "pipelines"
    work = Path(tempfile.mkdtemp(prefix="catmig_"))
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            orch = DataOrchestrator(rdir, RAW)
            keys = orch.compute_data_analysis_recipe_keys("stress_test_master")
            t1 = orch.materialize_tier1("stress_test_master", "Master_Collection", work / "a.parquet", keys=keys).collect()
        assert t1.schema["value"] == pl.Float64
        assert t1["value"].null_count() == 0
        assert 50 < t1["value"].mean() < 51 and (t1["value"] > 50).sum() == 5051
    finally:
        shutil.rmtree(work, ignore_errors=True)


# -- (6) no other Categorical ------------------------------------------------------------------

def _declared_categoricals():
    found, lower = [], []
    roots = [ROOT / "config", ROOT / "assets", ROOT / "app" / "tests" / "equality" / "recipes"]
    for root in roots:
        for path in root.rglob("*.yaml"):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                m = re.search(r"\btype:\s*[\"']?(Categorical|categorical)\b", line)
                if m:
                    (found if m.group(1) == "Categorical" else lower).append((path, lineno))
    return found, lower


def _field_name(path, lineno):
    lines = path.read_text().splitlines()
    indent = len(lines[lineno - 1]) - len(lines[lineno - 1].lstrip())
    for i in range(lineno - 2, -1, -1):
        m = re.match(r"^(\s*)([\w]+):\s*$", lines[i])
        if m and len(m.group(1)) < indent:
            return m.group(2)
    return None


def test_no_shipped_recipe_declares_categorical_except_the_allow_list():
    found, _ = _declared_categoricals()
    names = {(p.name, _field_name(p, n)) for p, n in found}
    assert names == set(ALLOWED_CATEGORICAL), names ^ set(ALLOWED_CATEGORICAL)


def test_the_allow_list_has_a_reason_for_every_entry():
    assert all(ALLOWED_CATEGORICAL.values())
