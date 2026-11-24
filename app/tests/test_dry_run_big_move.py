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
info: {ui_label: R}
metadata_schema:
  ui_label: meta
  source: {type: local_tsv, path: data/meta.tsv}
  null_values: ["-"]
  input_fields:
    sample_id: {type: String, original_name: sample_id, is_entity_id: true}
    year: {type: Int64}
  tier1: {steps: []}
data_schemas:
  genes:
    ui_label: genes
    source: {type: local_tsv, path: data/genes.tsv}
    input_fields:
      sample_id: {type: String}
      gene: {type: String}
    tier1:
      steps:
        - action: polars_group_by
          by: [sample_id]
          named_aggs: {n: "pl.len()"}
  ref:
    ui_label: ref
    source: {type: local_tsv, path: data/ref.tsv}
    input_fields:
      gene: {type: String}
    tier1: {steps: []}
additional_datasets_schemas:
  extra:
    ui_label: extra
    input_fields:
      sample_id: {type: String, is_entity_id: true}
    tier1: {steps: []}
joins:
  J:
    ui_label: J
    ingredients:
      - dataset_id: metadata_schema
      - dataset_id: genes
    tier1: !include r/J.yaml
  Alone:
    ui_label: Alone
    ingredients:
      - dataset_id: metadata_schema
    tier1: {steps: []}
  Fine:
    ui_label: Fine
    ingredients:
      - dataset_id: genes
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_select
          exprs: [sample_id]
        - action: polars_drop
          columns: [x]
"""
J_STEPS = """steps:
  - action: polars_join
    right_ingredient: genes
    'on': [sample_id]
    how: inner
  - action: polars_select
    exprs: [sample_id, gene]
"""
J_REMOVES = J_STEPS + """  - action: polars_drop_nulls
    subset: [sample_id]
"""
GALLERY = """id: g1
spec_version: 1
data_schemas:
  example:
    ui_label: e
    source: {type: local_tsv, path: x.tsv}
    input_fields:
      id: {type: String}
      value: {type: Float64}
    tier1: {steps: []}
"""
META = 'sample_id\tyear\ns1\t2020\n\t2021\n   \t2022\n-\t2023\ns2\t2024\n""\t2025\n'


def build_scratch(root: Path) -> None:
    (root / "config/data_analysis_recipes/r").mkdir(parents=True)
    (root / "config/data_analysis_recipes/r.yaml").write_text(RECIPE, encoding="utf-8")
    (root / "config/data_analysis_recipes/r/J.yaml").write_text(J_STEPS, encoding="utf-8")
    (root / "data").mkdir()
    (root / "data/meta.tsv").write_text(META, encoding="utf-8")
    (root / "assets/gallery_data/g1").mkdir(parents=True)
    (root / "assets/gallery_data/g1/data_analysis_recipe.yaml").write_text(GALLERY, encoding="utf-8")
    (root / "notes.md").write_text("the key is_entity_key here\n", encoding="utf-8")   # the old name in a note: section 2 is done and lists no line


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
    assert "joined table `J`" in s and "keeps only the rows found in both tables" in s and "data table first" in s
    first, only = s.split("Joined tables made from the metadata alone:")
    assert "joined table `Fine`" not in first and "joined table `Alone`" not in first
    assert "joined table `Alone`" in only and "joined table `J`" not in only


def test_keep_only_steps_are_listed_with_their_place_and_a_drop_is_not(scratch):
    s = "\n".join(section(tool.build(scratch), 4))
    assert "table `J`, tier1. The last step of 2 in that stage: `polars_select` keeps only [sample_id, gene]" in s
    assert "table `Fine`, tier1. The first step of 2 in that stage: `polars_select`" in s
    assert "table `genes`, tier1. The only step in that stage: `polars_group_by`" in s
    assert not [l for l in s.splitlines() if l.startswith("- ") and "polars_drop" in l]
    assert "NOT examined" in s


def test_entity_id_not_declared_and_gallery_in_the_annex(scratch):
    lines = tool.build(scratch)
    s = "\n".join(section(lines, 5))
    assert "table `genes`" in s and "a candidate, not a decision" in s and "`sample_id`" in s
    assert "table `ref`" in s and "no id column" in s
    assert "table `metadata_schema`" not in s and "table `extra`" not in s
    assert "g1/data_analysis_recipe.yaml" not in s and "1 have a column named like an id" in s
    annex = "\n".join(lines[next(i for i, l in enumerate(lines) if l.startswith("## Annex")):])
    assert "assets/gallery_data/g1/data_analysis_recipe.yaml" in annex


def test_metadata_lines_exact_and_in_plain_words(scratch):
    s = section(tool.build(scratch), 6)
    found = [(l.split(".tsv:")[1].split(":")[0], l.split("the id cell is ")[1]) for l in s if l.startswith("- ")]
    assert [n for n, _ in found] == ["3", "4", "5", "7"]
    assert found[0][1].startswith("(empty)")
    assert found[1][1].startswith("(only spaces)")
    assert found[2][1].startswith("`-` (a dash, a declared missing-value mark)")
    assert found[3][1].startswith('`""` (two quote marks, read as empty)')
    assert "the metadata's own steps do not remove them" in "\n".join(s)


def test_a_removal_in_a_join_tier_is_seen(scratch):
    (scratch / "config/data_analysis_recipes/r/J.yaml").write_text(J_REMOVES, encoding="utf-8")
    s = "\n".join(section(tool.build(scratch), 6))
    assert "the metadata's own steps do not remove them" in s
    assert "the join `J` removes them" in s and "r/J.yaml:8" in s and "polars_drop_nulls" not in s
    tail = s.split("do not", 1)                  # the tables that do not remove them are named, in whatever order
    assert "`Alone`" in s and "`Fine`" in s and len(tail) == 2
    assert s.index("`Alone`") > s.index("removes them") and s.index("`Fine`") > s.index("removes them")


def test_a_removal_in_the_metadata_own_tier_is_seen(scratch):
    p = scratch / "config/data_analysis_recipes/r.yaml"
    p.write_text(RECIPE.replace("  tier1: {steps: []}\ndata_schemas:", "  tier1:\n    steps:\n      - action: polars_drop_nulls\n        subset: [sample_id]\ndata_schemas:", 1), encoding="utf-8")
    s = "\n".join(section(tool.build(scratch), 6))
    assert "the metadata's own steps remove them" in s


def test_a_tier_file_included_by_two_recipes_names_both(scratch):
    other = RECIPE.replace("id: r\n", "id: r2\n").replace("r/J.yaml", "r/J.yaml")
    (scratch / "config/data_analysis_recipes/r2.yaml").write_text(other, encoding="utf-8")
    s = "\n".join(section(tool.build(scratch), 4))
    line = next(l for l in s.splitlines() if "J.yaml" in l and l.startswith("- "))
    assert "used by 2 recipes" in line and "`config/data_analysis_recipes/r.yaml`" in line and "`config/data_analysis_recipes/r2.yaml`" in line
    assert "table `J`" in line


def test_ledger_tags_are_not_in_the_lines_she_reads(scratch):
    lines = tool.build(scratch)
    assert "[D-" not in "\n".join(section(lines, 6) + section(lines, 4) + section(lines, 3) + section(lines, 5))


def test_the_order_of_the_names_does_not_matter_and_runs_are_equal(scratch):
    assert tool.build(scratch) == tool.build(scratch)


def test_additional_table_with_entity_id(scratch):
    s = "\n".join(section(tool.build(scratch), 7))
    assert "table `extra`" in s and "moved under the data schemas" in s


def test_section_2_is_done_and_lists_no_line_even_when_the_old_name_stands_in_a_file(scratch):
    lines = tool.build(scratch)
    body = section(lines, 2)
    assert any("DONE" in l for l in body)
    assert not [l for l in body if l.startswith("- ")]
    assert not any("the key is_entity_key here" in l for l in lines)


def test_the_entity_id_is_read_from_the_new_name_only(scratch):
    s = "\n".join(section(tool.build(scratch), 7))
    assert "table `extra`" in s
    (scratch / "config/data_analysis_recipes/r.yaml").write_text((scratch / "config/data_analysis_recipes/r.yaml").read_text(encoding="utf-8").replace("is_entity_id", "is_entity_key"), encoding="utf-8")
    assert "table `extra`" not in "\n".join(section(tool.build(scratch), 7))


def test_needs_the_owner_names_the_unresolved_places(scratch):
    lines = tool.build(scratch)
    owner = "\n".join(lines[next(i for i, l in enumerate(lines) if l.startswith("## Needs the owner")):])
    assert "table `ref`: has no id column" in owner and "section 4" in owner
    assert "g1/data_analysis_recipe.yaml" not in owner.split("## 2.")[0]
    assert "The Gallery examples: 0 have no id column and 1 have a column named `id`" in owner.split("## 2.")[0]


def test_header_counts_equal_the_entries_listed(scratch):
    lines = tool.build(scratch)
    counts = {int(l.split(".")[0][2:]): int(l.split(": ")[-1].split(" ")[0]) for l in lines if l.startswith("- ") and l[2].isdigit() and "." in l[:6]}
    assert set(counts) == {1, 2, 3, 4, 5, 6, 7}
    for n in (2, 3, 4, 5, 6, 7):
        entries = [l for l in section(lines, n) if l.startswith("- ")]
        assert counts[n] == len(entries), n
    assert counts[2] == 0 and counts[3] == 2 and counts[6] == 4


def test_first_screen_exists_names_each_decision_and_comes_first(scratch):
    lines = tool.build(scratch)
    i = next(k for k, l in enumerate(lines) if l.startswith("## What needs you"))
    assert i == min(k for k, l in enumerate(lines) if l.startswith("## "))
    end = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("## "))
    screen = "\n".join(lines[i:end])
    assert end - i <= 25
    for words in ("line(s) with no id", "made from the metadata alone", "keep only a fixed list of columns",
                  "declare no entity id", "The Gallery examples declare no entity id", "Only a mechanical rename"):
        assert words in screen, words
    order = [l for l in lines if l.startswith("## ")]
    nums = [l.split(".")[0][3:] for l in order if l[3:4].isdigit()]
    assert nums == ["6", "3", "4", "5", "7", "2", "1"]


def test_nothing_in_the_project_changes_and_report_is_the_only_file(scratch, tmp_path):
    before = snapshot(scratch)
    report = tmp_path / "out" / "report.md"
    assert tool.main(["--project-root", str(scratch), "--report", str(report)]) == 0
    assert snapshot(scratch) == before
    text = report.read_text(encoding="utf-8")
    assert "Nothing was changed. This is a list for the owner to read." in text
    assert tool.main(["--project-root", str(scratch), "--report", str(report)]) == 3      # never overwrites
    assert tool.main(["--project-root", str(scratch), "--report", str(scratch / "inside.md")]) == 3   # not inside the project outside tmpAI/
    assert snapshot(scratch) == before
