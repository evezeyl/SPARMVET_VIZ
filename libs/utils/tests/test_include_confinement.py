"""`!include` may not reach outside the project (check T11; spec sections 6.1 and 15).

The loader, not the checker, must refuse: the include runs while the file is read. Before this, `../..` and an
absolute path read any YAML file the user could read.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_include_confinement.py -q
"""
import os
import textwrap

import pytest

from utils.config_loader import ConfigManager

RECIPE = """
id: main
analysis_groups:
  g:
    label: G
    plots:
      p:
        label: P
        spec: {target_dataset: s, mapping: {x: a}, layers: [{name: geom_point}]}
data_schemas:
  s:
    source: {type: local_tsv, path: a.tsv}
    input_fields: !include '%s'
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text))
    return path


def recipe(path, include):
    return write(path, RECIPE % include)


def test_an_include_inside_the_recipe_folder_works(tmp_path):
    write(tmp_path / "main" / "fields.yaml", "a: {type: String}\n")
    main = recipe(tmp_path / "main.yaml", "main/fields.yaml")
    assert ConfigManager(main).raw_config["data_schemas"]["s"]["input_fields"] == {"a": {"type": "String"}}


def test_a_parent_include_is_refused_when_there_is_no_project_marker(tmp_path, capsys):
    write(tmp_path / "outside.yaml", "a: {type: String}\n")
    main = recipe(tmp_path / "recipes" / "main.yaml", "../outside.yaml")
    with pytest.raises(SystemExit):
        ConfigManager(main)
    assert "outside" in capsys.readouterr().err


def test_an_absolute_include_is_refused(tmp_path, capsys):
    target = write(tmp_path / "elsewhere" / "x.yaml", "a: {type: String}\n")
    main = recipe(tmp_path / "recipes" / "main.yaml", str(target))
    with pytest.raises(SystemExit):
        ConfigManager(main)
    assert "absolute" in capsys.readouterr().err


def test_the_project_root_is_the_nearest_folder_with_a_pyproject(tmp_path):
    """The shipped Abromics recipe includes a fragment of `assets/` from `config/...`: allowed inside the project."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    write(tmp_path / "assets" / "ref" / "fields.yaml", "a: {type: String}\n")
    main = recipe(tmp_path / "config" / "recipes" / "main.yaml", "../../assets/ref/fields.yaml")
    assert ConfigManager(main).raw_config["data_schemas"]["s"]["input_fields"] == {"a": {"type": "String"}}


def test_an_include_that_leaves_the_project_is_refused(tmp_path, capsys):
    project = tmp_path / "project"
    (project).mkdir()
    (project / "pyproject.toml").write_text("[project]\nname='x'\n")
    write(tmp_path / "other" / "x.yaml", "a: {type: String}\n")
    main = recipe(project / "config" / "main.yaml", "../../other/x.yaml")
    with pytest.raises(SystemExit):
        ConfigManager(main)
    assert "!include" in capsys.readouterr().err


def test_a_symlink_that_leaves_the_project_is_refused(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname='x'\n")
    outside = write(tmp_path / "other" / "x.yaml", "a: {type: String}\n")
    (project / "config").mkdir()
    os.symlink(outside, project / "config" / "link.yaml")
    main = recipe(project / "config" / "main.yaml", "link.yaml")
    with pytest.raises(SystemExit):
        ConfigManager(main)


def test_the_caller_can_name_the_root(tmp_path):
    write(tmp_path / "shared" / "fields.yaml", "a: {type: String}\n")
    main = recipe(tmp_path / "recipes" / "main.yaml", "../shared/fields.yaml")
    with pytest.raises(SystemExit):
        ConfigManager(main)
    assert ConfigManager(main, include_root=tmp_path).raw_config["data_schemas"]["s"]["input_fields"] == {"a": {"type": "String"}}


def test_a_missing_include_inside_the_root_still_says_not_found(tmp_path, capsys):
    main = recipe(tmp_path / "main.yaml", "main/missing.yaml")
    with pytest.raises(SystemExit):
        ConfigManager(main)
    assert "not found" in capsys.readouterr().err
