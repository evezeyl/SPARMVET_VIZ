"""The command `assets/scripts/migrate_recipe_engine_keys.py`: modes, exit codes, what it prints, and the real plot library's answer
on what a partial theme is (the library tests use a stand-in for that answer).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_migrate_recipe_engine_keys.py -q
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("migrate_recipe_engine_keys", ROOT / "assets/scripts/migrate_recipe_engine_keys.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

OLD = """id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info: {label: R, description: d, contact: c}
data_schemas:
  A:
    label: A
    description: One row per sample.
    source: {type: local_tsv, path: assets/test_data/a.tsv}
    null_values: []
    strip: true
    input_fields:
      id: {type: String, is_entity_id: true}
    wrangling: {tier1: []}
plot_defaults:
  default_font_family: Arial
analysis_groups:
  g:
    label: G
    description: d
    plots:
      p:
        label: P
        description: d
        spec:
          target_dataset: A
          title: Ids
          mapping: {x: id}
          layers:
          - {name: geom_col}
"""


@pytest.fixture
def recipe(tmp_path):
    path = tmp_path / "r.yaml"
    path.write_text(OLD, encoding="utf-8")
    return path


def test_help_names_the_modes_the_exit_codes_and_every_rule(capsys):
    with pytest.raises(SystemExit) as stop:
        tool.main(["--help"])
    assert stop.value.code == 0
    text = capsys.readouterr().out
    for word in ("--check", "--apply", "Exit code", "ui_label", "plot_defaults", "theme_bw", "tier1: !include", "title"):
        assert word in text


def test_check_changes_nothing_prints_every_change_and_exits_1(recipe, capsys):
    before = recipe.read_bytes()
    assert tool.main(["--check", str(recipe)]) == 1
    out = capsys.readouterr().out
    assert recipe.read_bytes() == before
    assert "default_font_family removed (old value Arial) in recipe r" in out
    assert "title Ids moved" in out and "theme: theme_bw written" in out and "summary" in out and "would change (nothing written" in out


def test_the_default_mode_is_check(recipe):
    before = recipe.read_bytes()
    assert tool.main([str(recipe)]) == 1 and recipe.read_bytes() == before


def test_apply_writes_exits_0_and_a_second_apply_changes_nothing_and_says_so(recipe, capsys):
    assert tool.main(["--apply", str(recipe)]) == 0
    assert "applied: 1 file(s) written" in capsys.readouterr().out
    written = recipe.read_bytes()
    assert b"wrangling" not in written and b"ui_label: P" in written and b"theme: theme_bw" in written
    assert tool.main(["--apply", str(recipe)]) == 0
    assert "nothing to change" in capsys.readouterr().out
    assert recipe.read_bytes() == written
    assert tool.main(["--check", str(recipe)]) == 0


def test_a_refusal_exits_2_and_leaves_what_it_could_not_place(tmp_path, capsys):
    path = tmp_path / "x.yaml"
    path.write_text("hello: world\n", encoding="utf-8")
    assert tool.main(["--apply", str(path)]) == 2
    out = capsys.readouterr().out
    assert "cannot be known" in out and path.read_text() == "hello: world\n"


def test_check_and_apply_cannot_be_given_together(recipe):
    with pytest.raises(SystemExit) as stop:
        tool.main(["--check", "--apply", str(recipe)])
    assert stop.value.code == 2


def test_the_plot_library_decides_what_a_partial_theme_is(tmp_path):
    """theme_custom only sets properties, so a plot with it alone still takes the built-in base: the default is written."""
    text = OLD.replace("          title: Ids\n", "").replace("          - {name: geom_col}\n", "          - {name: geom_col}\n          - {name: theme_custom, params: {}}\n")
    partial = tmp_path / "partial.yaml"
    partial.write_text(text, encoding="utf-8")
    complete = tmp_path / "complete.yaml"
    complete.write_text(text.replace("id: r\n", "id: complete\n").replace("theme_custom", "theme_minimal"), encoding="utf-8")
    assert tool.main(["--apply", str(partial), str(complete)]) == 0
    assert "theme: theme_bw" in partial.read_text() and "theme: theme_bw" not in complete.read_text()


def test_a_folder_is_searched_and_the_files_a_recipe_includes_are_rewritten_with_it(tmp_path, capsys):
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "w.yaml").write_text("tier1:\n- {action: polars_sort, by: [id]}\n", encoding="utf-8")
    (tmp_path / "r.yaml").write_text(OLD.replace("wrangling: {tier1: []}", "wrangling: !include r/w.yaml"), encoding="utf-8")
    assert tool.main(["--apply", str(tmp_path)]) == 0
    assert (tmp_path / "r" / "w.yaml").read_text() == "steps:\n- {action: polars_sort, by: [id]}\n"
    assert "tier1: !include r/w.yaml" in (tmp_path / "r.yaml").read_text()


def test_an_old_fragment_that_no_recipe_includes_is_left_unless_the_flag_is_given(tmp_path, capsys):
    (tmp_path / "r.yaml").write_text(OLD, encoding="utf-8")
    orphan = tmp_path / "old.yaml"
    orphan.write_text("tier1: []\n", encoding="utf-8")
    assert tool.main(["--apply", str(tmp_path)]) == 2
    assert orphan.read_text() == "tier1: []\n" and "no recipe in the given paths includes it" in capsys.readouterr().out
    assert tool.main(["--apply", "--orphan-fragments", str(tmp_path)]) == 0
    assert orphan.read_text() == "steps: []\n"
