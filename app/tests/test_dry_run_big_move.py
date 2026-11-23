"""The command `assets/scripts/dry_run_big_move.py`: the DRY RUN of the one big move (ledger D-0562, D-0569, D-0586, D-0587, D-0594).

Runs on a small scratch project built in `tmp_path` (never on the shipped files). Each section must list exactly the expected
lines, and the script must change no file of the project.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_dry_run_big_move.py -q -n 0
"""

# @deps
# provides: -
# consumes: assets/scripts/dry_run_big_move.py (main, build)
# doc: .claude/knowledge/decision_ledger.md (D-0562, D-0569, D-0586, D-0587, D-0594)
# @end_deps
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("dry_run_big_move", ROOT / "assets/scripts/dry_run_big_move.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

RECIPE = """id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info: {label: R}
metadata_schema:
  label: meta
  source: {type: local_tsv, path: data/meta.tsv}
  null_values: ["-"]
  input_fields:
    sample_id: {type: String, original_name: sample_id, is_entity_key: true}
    year: {type: Int64}
  tier1: {steps: []}
data_schemas:
  genes:
    label: genes
    source: {type: local_tsv, path: data/genes.tsv}
    input_fields:
      sample_id: {type: String}
      gene: {type: String}
    tier1: {steps: []}
  ref:
    label: ref
    source: {type: local_tsv, path: data/ref.tsv}
    input_fields:
      gene: {type: String}
    tier1: {steps: []}
additional_datasets_schemas:
  extra:
    label: extra
    input_fields:
      sample_id: {type: String, is_entity_key: true}
    tier1: {steps: []}
joins:
  J:
    label: J
    ingredients:
      - dataset_id: metadata_schema
      - dataset_id: genes
    tier1: !include r/J.yaml
  Alone:
    label: Alone
    ingredients:
      - dataset_id: metadata_schema
    tier1: {steps: []}
  Fine:
    label: Fine
    ingredients:
      - dataset_id: genes
      - dataset_id: metadata_schema
    tier1: {steps: []}
"""
J_STEPS = """steps:
  - action: polars_join
    right_ingredient: genes
    'on': [sample_id]
    how: inner
  - action: polars_select
    exprs: [sample_id, gene]
"""
META = "sample_id\tyear\ns1\t2020\n\t2021\n   \t2022\n-\t2023\ns2\t2024\n"


def build_scratch(root: Path) -> None:
    (root / "config/data_analysis_recipes/r").mkdir(parents=True)
    (root / "config/data_analysis_recipes/r.yaml").write_text(RECIPE, encoding="utf-8")
    (root / "config/data_analysis_recipes/r/J.yaml").write_text(J_STEPS, encoding="utf-8")
    (root / "data").mkdir()
    (root / "data/meta.tsv").write_text(META, encoding="utf-8")
    (root / "notes.md").write_text("the key is_entity_key here\n", encoding="utf-8")


def snapshot(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def section(lines, n):
    start = next(i for i, l in enumerate(lines) if l.startswith(f"## {n}. "))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


@pytest.fixture
def scratch(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    build_scratch(root)
    return root


def test_joins_from_the_metadata_are_listed_and_the_others_not(scratch):
    s = "\n".join(section(tool.build(scratch), 3))
    assert "table `J`" in s and "how=inner" in s and "to be rewritten with the data table first" in s
    assert "table `Fine`" not in s.split("Tables whose ONLY")[0]
    only = s.split("Tables whose ONLY")[1]
    assert "table `Alone`" in only and "table `J`" not in only


def test_fixed_column_list_is_listed_without_choosing(scratch):
    s = "\n".join(section(tool.build(scratch), 4))
    assert "table `J`" in s and "polars_select" in s and "[sample_id, gene]" in s
    assert "her two ways" in s


def test_entity_id_not_declared(scratch):
    s = "\n".join(section(tool.build(scratch), 5))
    assert "table `genes`" in s and "CANDIDATE" in s and "sample_id" in s
    assert "table `ref`" in s and "no id column" in s
    assert "table `metadata_schema`" not in s and "table `extra`" not in s


def test_metadata_lines_with_no_usable_id(scratch):
    s = section(tool.build(scratch), 6)
    lines = [l for l in s if l.startswith("  - ")]
    assert [l.split(":")[1] for l in lines] == ["3", "4", "5"] or [l.split(".tsv:")[1].split(":")[0] for l in lines] == ["3", "4", "5"]
    assert "no step of the recipe removes a missing id" in "\n".join(s)


def test_additional_table_with_entity_id(scratch):
    s = "\n".join(section(tool.build(scratch), 7))
    assert "table `extra`" in s and "to be moved under the data schemas" in s


def test_entity_key_rename_counts_per_kind(scratch):
    s = "\n".join(section(tool.build(scratch), 2))
    assert "recipe or template file: 2 line(s)" in s
    assert "docs and design notes: 1 line(s)" in s


def test_needs_the_owner_names_the_unresolved_places(scratch):
    lines = tool.build(scratch)
    owner = "\n".join(lines[next(i for i, l in enumerate(lines) if l.startswith("## Needs the owner")):])
    assert "table `ref` has no id column" in owner and "section 4" in owner


def test_removing_step_is_seen(scratch):
    p = scratch / "config/data_analysis_recipes/r.yaml"
    p.write_text(RECIPE.replace("  tier1: {steps: []}\ndata_schemas:", "  tier1:\n    steps:\n      - action: polars_drop_nulls\n        subset: [sample_id]\ndata_schemas:", 1), encoding="utf-8")
    s = "\n".join(section(tool.build(scratch), 6))
    assert "polars_drop_nulls" in s and "none: no step" not in s


def test_nothing_in_the_project_changes_and_report_is_the_only_file(scratch, tmp_path):
    before = snapshot(scratch)
    report = tmp_path / "out" / "report.md"
    assert tool.main(["--project-root", str(scratch), "--report", str(report)]) == 0
    assert snapshot(scratch) == before
    text = report.read_text(encoding="utf-8")
    assert "Nothing was changed. This is a list for the owner to read." in text
    assert tool.main(["--project-root", str(scratch), "--report", str(report)]) == 3      # never overwrites
    assert tool.main(["--project-root", str(scratch), "--report", str(scratch / "inside.md")]) == 3   # not inside the project outside tmpAI
    assert snapshot(scratch) == before
