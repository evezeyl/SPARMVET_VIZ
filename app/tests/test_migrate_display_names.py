"""The command `assets/scripts/migrate_display_names.py`: the DRY RUN of the names pass (ledger D-0407 to D-0412, D-0459).

The pass is ONE migration and waits for the owner's answers: in this branch the script lists what it would change, and it
refuses to write on the repository itself. These tests run it on small trees written in `tmp_path` (never on the shipped
files), except two that run the dry run on the real tree and prove that it changes nothing.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_migrate_display_names.py -q
"""

# @deps
# provides: -
# consumes: assets/scripts/migrate_display_names.py (main, build_plan, RULES, OPEN_CASES)
# doc: .claude/knowledge/decision_ledger.md (D-0407 to D-0412, D-0459), .claude/tasks/tasks.md (NAMES-UI-LABEL-EVERYWHERE)
# @end_deps
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("migrate_display_names", ROOT / "assets/scripts/migrate_display_names.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

RECIPE = """# top comment
id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: "My recipe"     # keep this comment
  description: d
  contact: c
data_schemas:
  A:
    label: A
    source: {type: local_tsv, path: a.tsv}
    input_fields:
      id: {type: String, label: Sample}
joins:
  J:
    label: Joined
    ingredients: [A]
analysis_groups:
  g:
    ui_label: G
    ui_title: A longer group name
    plots:
      p_inline:
        ui_label: P
        ui_title: A longer plot name
        # a comment between keys
        target_dataset: A
        mapping: {x: id}
      p_file: !include 'r/plots/p_file.yaml'
"""
RECIPE_AFTER = """# top comment
id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  ui_label: "My recipe"     # keep this comment
  description: d
  contact: c
data_schemas:
  A:
    ui_label: A
    source: {type: local_tsv, path: a.tsv}
    input_fields:
      id: {type: String, ui_label: Sample}
joins:
  J:
    ui_label: Joined
    ingredients: [A]
analysis_groups:
  g:
    ui_label: G
    plots:
      p_inline:
        ui_label: P
        # a comment between keys
        target_dataset: A
        mapping: {x: id}
      p_file: !include 'r/plots/p_file.yaml'
"""
PLOT_FILE = """ui_label: PF
ui_title: >-
  A long title
  on two lines
description: d
target_dataset: A
"""
PLOT_FILE_AFTER = """ui_label: PF
description: d
target_dataset: A
"""
DEPLOYMENT = """deployment_type: filesystem
deployment_name: "X"
default_app_features: "f"
branding:
  theme_css: "a.css"
  banner:
    logo_url: "l.svg"
    title: "T"
    subtitle: "S"   # a comment
  contact: "c@x"
"""
DEPLOYMENT_AFTER = """deployment_type: filesystem
default_app_features: "f"
branding:
  theme_css: "a.css"
  banner:
    logo_url: "l.svg"
    ui_label: "T"
    description: "S"   # a comment
  contact: "c@x"
"""
APP_FEATURES = """name: "f"
display_name: "F name"
ui_title:
  text: "x"
  subtitle: "y"
  visible: true
flags:
  a: true
"""
APP_FEATURES_AFTER = """name: "f"
display_name: "F name"
flags:
  a: true
"""
GALLERY = """id: ex
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: Ex plot
  description: d
data_schemas: {}
analysis_groups:
  example:
    ui_label: Example
    plots:
      ex_plot:
        ui_label: Ex plot
        target_dataset: x
"""
GALLERY_AFTER = GALLERY.replace("  label: Ex plot", "  ui_label: Ex plot")


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", RECIPE)
    write(root, "config/data_analysis_recipes/pipelines/r/plots/p_file.yaml", PLOT_FILE)
    write(root, "config/deployment/demo/d.yaml", DEPLOYMENT)
    write(root, "config/app_features/f.yaml", APP_FEATURES)
    write(root, "assets/gallery_data/ex/data_analysis_recipe.yaml", GALLERY)
    return root


def digest(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def rules_of(plan):
    return sorted(c.rule for c in plan.changes)


# -- the rules, one test each --------------------------------------------------------------------------------------------

def test_every_apply_rule_names_its_ledger_number_and_its_words():
    for rule in tool.RULES:
        assert rule.ledger.startswith("D-0"), rule.id
        assert len(rule.words) >= 12, rule.id
        assert rule.status in ("APPLY", "OPEN"), rule.id
    assert len({r.id for r in tool.RULES}) == len(tool.RULES)


def test_info_label_becomes_ui_label_and_the_comment_stays(tree):
    plan = tool.build_plan(tree)
    assert read(tree, "config/data_analysis_recipes/pipelines/r.yaml") == RECIPE      # a plan writes nothing
    assert plan.texts[tree / "config/data_analysis_recipes/pipelines/r.yaml"] == RECIPE_AFTER
    assert any(c.rule == "R01" and c.old == "info.label" and c.new == "info.ui_label" and c.line == 7 for c in plan.changes)


@pytest.mark.parametrize("old", ["name", "ui_title"])
def test_the_other_old_info_keys_become_ui_label_too(tmp_path, old):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", RECIPE.replace('  label: "My recipe"', f'  {old}: "My recipe"'))
    plan = tool.build_plan(root)
    assert any(c.old == f"info.{old}" and c.new == "info.ui_label" for c in plan.changes)
    assert "  ui_label: \"My recipe\"" in plan.texts[root / "config/data_analysis_recipes/pipelines/r.yaml"]


def test_group_and_plot_ui_title_are_removed_with_their_value_shown(tree):
    plan = tool.build_plan(tree)
    removed = {c.value for c in plan.changes if c.new is None}
    assert "A longer group name" in removed
    assert "A longer plot name" in removed
    assert any(v.startswith("A long title") for v in removed)       # the folded value of the included plot file
    assert plan.texts[tree / "config/data_analysis_recipes/pipelines/r/plots/p_file.yaml"] == PLOT_FILE_AFTER


def test_banner_keys_are_renamed_and_deployment_name_is_removed(tree):
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "config/deployment/demo/d.yaml"] == DEPLOYMENT_AFTER
    assert {"R06", "R07", "R08"} <= set(rules_of(plan))


def test_app_features_ui_title_block_is_removed_and_display_name_is_listed_not_changed(tree):
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "config/app_features/f.yaml"] == APP_FEATURES_AFTER
    assert any(c.case == "OC07" and "display_name" in c.detail for c in plan.cases)


def test_a_gallery_bundle_is_planned_like_a_recipe(tree):
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "assets/gallery_data/ex/data_analysis_recipe.yaml"] == GALLERY_AFTER
    assert plan.kind_counts["Gallery bundles"]["changes"] == 1


def test_counts_per_file_kind(tree):
    plan = tool.build_plan(tree)
    assert plan.kind_counts["recipes"]["changes"] == 7 and plan.kind_counts["recipes"]["files"] == 2
    assert plan.kind_counts["deployment files"]["changes"] == 3
    assert plan.kind_counts["app features files"]["changes"] == 1


# -- what is kept, byte for byte -----------------------------------------------------------------------------------------

def test_a_second_run_on_the_migrated_copy_changes_nothing(tree):
    assert tool.main(["--root", str(tree), "--apply"]) == 0
    after_first = digest(tree)
    plan = tool.build_plan(tree)
    assert plan.changes == [] and plan.texts == {}
    assert tool.main(["--root", str(tree), "--apply"]) == 0
    assert digest(tree) == after_first


def test_apply_on_a_copy_writes_exactly_the_planned_texts(tree):
    plan = tool.build_plan(tree)
    assert len(plan.texts) == 5
    assert tool.main(["--root", str(tree), "--apply"]) == 0
    for path, text in plan.texts.items():
        assert path.read_text(encoding="utf-8") == text


def test_a_file_with_none_of_the_keys_is_not_touched(tmp_path):
    root = tmp_path / "copy"
    text = "id: r\nspec_version: 1\ninfo:\n  ui_label: R\n  description: d\nanalysis_groups:\n  g:\n    ui_label: G\n    plots: {}\n"
    path = write(root, "config/data_analysis_recipes/pipelines/r.yaml", text)
    before = digest(root)
    plan = tool.build_plan(root)
    assert plan.changes == [] and plan.texts == {}
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert digest(root) == before and path.read_text(encoding="utf-8") == text


def test_quotes_of_the_key_and_a_flow_mapping_info_are_kept(tmp_path):
    root = tmp_path / "copy"
    text = "id: r\nspec_version: 1\ninfo: {label: R, description: d}\nx:\n  'label': no\nanalysis_groups: {}\n"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/data_analysis_recipes/pipelines/r.yaml"] == text.replace("{label: R", "{ui_label: R")
    quoted = text.replace("info: {label: R, description: d}", "info:\n  \"label\": R")
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", quoted)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/data_analysis_recipes/pipelines/r.yaml"] == quoted.replace('"label"', '"ui_label"')


def test_an_included_file_shared_by_two_groups_is_changed_once(tmp_path):
    root = tmp_path / "copy"
    recipe = ("id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n"
              "  g1:\n    ui_label: G1\n    plots:\n      p: !include r/p.yaml\n"
              "  g2:\n    ui_label: G2\n    plots:\n      q: !include r/p.yaml\n")
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", recipe)
    write(root, "config/data_analysis_recipes/pipelines/r/p.yaml", "ui_label: P\nui_title: T\n")
    plan = tool.build_plan(root)
    assert len([c for c in plan.changes if c.new is None]) == 1
    assert plan.texts[root / "config/data_analysis_recipes/pipelines/r/p.yaml"] == "ui_label: P\n"


def test_a_removed_block_scalar_leaves_the_blank_line_and_the_comment_after_it(tmp_path):
    root = tmp_path / "copy"
    text = "ui_label: P\nui_title: >-\n  long\n  text\n\n# note for the next key\ndescription: d\n"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml",
          "id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n  g:\n    ui_label: G\n    plots:\n      p: !include r/p.yaml\n")
    write(root, "config/data_analysis_recipes/pipelines/r/p.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/data_analysis_recipes/pipelines/r/p.yaml"] == "ui_label: P\n\n# note for the next key\ndescription: d\n"


def test_a_removed_last_key_of_a_file_without_a_final_newline(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/f.yaml", "name: f\nui_title: {text: a}")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/app_features/f.yaml"] == "name: f\n"      # a flow VALUE is fine: its pair sits in a block mapping
    write(root, "config/app_features/f.yaml", "name: f\nui_title: a")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/app_features/f.yaml"] == "name: f\n"


# -- the dry run writes nothing ------------------------------------------------------------------------------------------

def test_the_dry_run_writes_nothing_on_a_tree(tree, capsys):
    before = digest(tree)
    code = tool.main(["--root", str(tree)])
    out = capsys.readouterr().out
    assert code == 1 and digest(tree) == before
    assert "DRY RUN" in out and "CANNOT BE DECIDED BY THE SCRIPT" in out
    assert "R04" in out and "D-0409" in out


def git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def test_the_dry_run_on_the_real_tree_changes_no_file(capsys):
    scanned = [ROOT / "config", ROOT / "assets/gallery_data"]
    before_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for base in scanned for p in sorted(base.rglob("*")) if p.is_file()}
    before_status = git_status()
    assert tool.main(["--root", str(ROOT)]) in (0, 1, 2)
    capsys.readouterr()
    after_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for base in scanned for p in sorted(base.rglob("*")) if p.is_file()}
    assert after_hashes == before_hashes
    assert git_status() == before_status


# -- --apply works on a copy only ----------------------------------------------------------------------------------------

def test_apply_on_the_repository_itself_is_refused(capsys):
    before = git_status()
    assert tool.main(["--root", str(ROOT), "--apply"]) == 3
    err = capsys.readouterr().err
    assert "waits for the owner" in err and "copy" in err
    assert git_status() == before


def test_apply_without_root_is_refused(capsys):
    before = git_status()
    assert tool.main(["--apply"]) == 3
    assert "--root" in capsys.readouterr().err
    assert git_status() == before


def test_apply_on_a_git_working_tree_is_refused(tree, capsys):
    (tree / ".git").mkdir()
    before = digest(tree)
    assert tool.main(["--root", str(tree), "--apply"]) == 3
    assert digest(tree) == before


def fake_repository(tmp_path, monkeypatch):
    """A stand-in for the repository, so that the guard is tested without ever pointing --apply at the real one."""
    outer = tmp_path / "outer"
    repo = outer / "repo"
    write(repo, "config/app_features/f.yaml", APP_FEATURES)
    write(outer, "config/app_features/g.yaml", APP_FEATURES)
    monkeypatch.setattr(tool, "PROJECT_ROOT", repo)
    return outer, repo


def test_apply_on_the_repository_by_its_own_root_is_refused_even_without_a_git_folder(tmp_path, monkeypatch, capsys):
    outer, repo = fake_repository(tmp_path, monkeypatch)
    before = digest(outer)
    assert tool.main(["--root", str(repo), "--apply"]) == 3
    assert "waits for the owner" in capsys.readouterr().err
    assert digest(outer) == before


def test_apply_on_a_folder_that_contains_the_repository_is_refused(tmp_path, monkeypatch):
    outer, repo = fake_repository(tmp_path, monkeypatch)
    before = digest(outer)
    assert tool.main(["--root", str(outer), "--apply"]) == 3
    assert digest(outer) == before


def test_apply_on_a_sibling_copy_is_allowed(tmp_path, monkeypatch):
    outer, repo = fake_repository(tmp_path, monkeypatch)
    copy = tmp_path / "copy"
    write(copy, "config/app_features/f.yaml", APP_FEATURES)
    assert tool.main(["--root", str(copy), "--apply"]) == 0
    assert read(copy, "config/app_features/f.yaml") == APP_FEATURES_AFTER


# -- the cases the script lists and never resolves -----------------------------------------------------------------------

def case_ids(plan):
    return sorted({c.case for c in plan.cases})


def test_open_rule_never_changes_a_file(tree, monkeypatch):
    rules = [tool.Rule(**{**r.__dict__, "status": "OPEN", "case": "OC99"}) if r.id == "R01" else r for r in tool.RULES]
    monkeypatch.setattr(tool, "RULES", rules)
    plan = tool.build_plan(tree)
    assert not any(c.rule == "R01" for c in plan.changes)
    assert "info.label" not in " ".join(c.old for c in plan.changes)
    assert any(c.case == "OC99" for c in plan.cases)
    assert "ui_label: \"My recipe\"" not in plan.texts[tree / "config/data_analysis_recipes/pipelines/r.yaml"]


def test_the_label_of_a_table_a_join_and_a_field_becomes_ui_label(tree):
    plan = tool.build_plan(tree)
    rules = {c.rule: c for c in plan.changes if c.rule in ("R10", "R11", "R12")}
    assert set(rules) == {"R10", "R11", "R12"}
    assert rules["R10"].line == 12 and rules["R10"].old == "data_schemas.A.label"
    assert rules["R12"].old == "data_schemas.A.input_fields.id.label" and rules["R11"].old == "joins.J.label"
    assert all(c.ledger == "D-0468" for c in rules.values())
    assert not any(c.case == "OC08" for c in plan.cases)


def test_the_label_strings_of_the_python_code_are_counted_and_not_renamed(tmp_path):
    root = tmp_path / "copy"
    write(root, "libs/viz_factory/src/viz_factory/geoms/core.py", 'X = {"label": "a", "label": "b"}\n')
    plan = tool.build_plan(root)
    found = [c for c in plan.cases if c.case == "OC02"]
    assert found and "2 place" in found[0].detail
    assert "DECIDED" in tool.OPEN_CASES["OC02"]["title"] and tool.OPEN_CASES["OC02"]["words"].startswith("D-0468")
    assert (root / "libs/viz_factory/src/viz_factory/geoms/core.py").read_text(encoding="utf-8") == 'X = {"label": "a", "label": "b"}\n'


def test_a_recipe_with_no_name_is_listed(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/a.yaml", "id: a\nspec_version: 1\ninfo:\n  description: d\nanalysis_groups: {}\n")
    write(root, "config/data_analysis_recipes/pipelines/b.yaml", "id: b\nspec_version: 1\ninfo: {}\nanalysis_groups: {}\n")
    write(root, "config/data_analysis_recipes/pipelines/c.yaml", "id: c\nspec_version: 1\ninfo:\nanalysis_groups: {}\n")
    write(root, "config/data_analysis_recipes/pipelines/d.yaml", "id: d\nspec_version: 1\nanalysis_groups: {}\n")
    plan = tool.build_plan(root)
    nameless = sorted(Path(c.file).name for c in plan.cases if c.case == "OC01")
    assert nameless == ["a.yaml", "b.yaml", "c.yaml", "d.yaml"]
    assert plan.changes == []
    assert not plan.blocking                 # an advice, not an error (D-0470)
    assert "WOULD GET THE ADVICE" in "\n".join(tool.lines_of(plan, False, "h"))


def test_a_key_in_old_and_new_spelling_is_a_conflict_and_is_not_overwritten(tmp_path):
    root = tmp_path / "copy"
    both = "id: a\nspec_version: 1\ninfo:\n  label: Old\n  ui_label: New\nanalysis_groups: {}\n"
    two = "id: b\nspec_version: 1\ninfo:\n  label: One\n  name: Two\nanalysis_groups: {}\n"
    write(root, "config/data_analysis_recipes/pipelines/a.yaml", both)
    write(root, "config/data_analysis_recipes/pipelines/b.yaml", two)
    plan = tool.build_plan(root)
    assert plan.changes == [] and plan.texts == {}
    conflicts = [c for c in plan.cases if c.case == "CONFLICT"]
    assert len(conflicts) == 3          # label next to ui_label; label and name for one target (two lines)
    assert tool.main(["--root", str(root), "--apply"]) == 2
    assert read(root, "config/data_analysis_recipes/pipelines/a.yaml") == both


def test_a_removal_in_a_flow_mapping_is_listed_as_not_placeable(tmp_path):
    root = tmp_path / "copy"
    text = ("id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n  g:\n    ui_label: G\n"
            "    plots:\n      p: {ui_label: P, ui_title: T, target_dataset: A}\n")
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", text)
    plan = tool.build_plan(root)
    assert plan.changes == [] and plan.texts == {}
    assert [c.case for c in plan.cases if c.case == "OC13"] == ["OC13"]


def test_a_deployment_name_with_no_banner_to_take_it_is_listed_and_kept(tmp_path):
    root = tmp_path / "copy"
    text = "deployment_type: filesystem\ndeployment_name: \"Only name\"\nbranding:\n  contact: c\n"
    write(root, "config/deployment/local/l.yaml", text)
    plan = tool.build_plan(root)
    assert plan.changes == [] and plan.texts == {}
    assert any(c.case == "OC06" and "Only name" in c.detail for c in plan.cases)


def test_a_deployment_name_that_differs_from_the_banner_title_is_noted(tree):
    plan = tool.build_plan(tree)
    assert any(c.case == "NOTE-NAME" and '"X"' in c.detail and '"T"' in c.detail for c in plan.cases)


def test_a_removed_ui_title_that_differs_from_ui_label_is_counted_as_a_loss_of_text(tree):
    plan = tool.build_plan(tree)
    notes = [c for c in plan.cases if c.case == "NOTE-TEXT"]
    assert len(notes) == 3


def test_info_keys_that_no_decision_renames_are_listed(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml",
          "id: r\nspec_version: 1\ninfo:\n  ui_label: R\n  subtitle: S\n  category: C\nanalysis_groups: {}\n")
    plan = tool.build_plan(root)
    listed = [c for c in plan.cases if c.case == "OC09"]
    assert any("subtitle" in c.detail for c in listed)


def test_the_format_number_and_the_registries_and_sessions_and_gallery_cases_are_always_listed(tree):
    plan = tool.build_plan(tree)
    assert {"OC02", "OC03", "OC04", "OC05"} <= set(case_ids(plan))
    assert "D-0469" in tool.OPEN_CASES["OC03"]["words"] and "D-0471" in tool.OPEN_CASES["OC04"]["words"]


def test_a_saved_session_with_an_old_name_key_is_listed(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", "id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups: {}\n")
    session = write(root, "tmp/user/_sessions/k/t3_20261121.json", json.dumps({"session_key": "k", "ui_title": "x", "label": "mine"}))
    plan = tool.build_plan(root)
    found = [c for c in plan.cases if c.case == "OC04" and c.file.endswith("t3_20261121.json")]
    assert found and "ui_title" in found[0].detail
    assert json.loads(session.read_text(encoding="utf-8"))["ui_title"] == "x"


def test_a_comment_that_names_an_old_key_is_listed(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/deployment/templates/t_template.yaml",
          "# branding.banner: optional {logo_url, title, subtitle} shown in the info panel\ndeployment_type: filesystem\n")
    plan = tool.build_plan(root)
    assert any(c.case == "OC10" and c.line == 1 for c in plan.cases)


def test_a_plot_or_group_without_ui_label_is_listed(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml",
          "id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n  g:\n    plots:\n      p:\n        target_dataset: A\n")
    plan = tool.build_plan(root)
    assert sum(1 for c in plan.cases if c.case == "OC11") == 2


def test_a_file_that_cannot_be_parsed_is_listed_and_does_not_stop_the_run(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/bad.yaml", "id: [unclosed\nspec_version: 1\n")
    write(root, "config/data_analysis_recipes/pipelines/ok.yaml", "id: ok\nspec_version: 1\ninfo:\n  label: O\nanalysis_groups: {}\n")
    plan = tool.build_plan(root)
    assert any(c.case == "OC14" and c.file.endswith("bad.yaml") for c in plan.cases)
    assert any(c.rule == "R01" for c in plan.changes)


def test_an_empty_tree_gives_an_empty_plan(tmp_path, capsys):
    root = tmp_path / "copy"
    root.mkdir()
    assert tool.main(["--root", str(root)]) == 0
    assert "nothing to change" in capsys.readouterr().out


# -- the recipe banner switch (D-0470, D-0472) ---------------------------------------------------------------------------

HIDDEN_FEATURES = "name: hidden\ndisplay_name: H\nui_title:\n  text: \"My banner\"\n  subtitle: \"Line\"\n  visible: false\nflags:\n  a: true\n"
USER_DEPLOYMENT = "deployment_type: filesystem\ndefault_app_features: \"hidden\"\nbranding:\n  theme_css: a.css\n  banner:\n    title: \"T\"\n    subtitle: \"S\"\n"
OTHER_DEPLOYMENT = "deployment_type: filesystem\ndefault_app_features: \"other\"\nbranding:\n  contact: c\n"


@pytest.fixture
def hidden(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/user.yaml", USER_DEPLOYMENT)
    write(root, "config/deployment/a/other.yaml", OTHER_DEPLOYMENT)
    return root


def test_the_switch_key_is_one_constant_and_unset_today():
    assert tool.BANNER_SWITCH_KEY is None


def test_an_app_features_file_that_hides_the_banner_is_kept_and_listed_while_the_key_is_unset(hidden, capsys):
    plan = tool.build_plan(hidden)
    assert plan.texts.get(hidden / "config/app_features/hidden.yaml") is None
    found = [c for c in plan.cases if c.case == "OC15"]
    assert len(found) == 1 and found[0].line == 3
    assert "user.yaml" in found[0].detail and "other.yaml" not in found[0].detail.split("banner of each")[0]
    assert "'T'" in found[0].detail and "no name yet" in found[0].detail
    assert tool.main(["--root", str(hidden), "--apply"]) == 2
    assert "NOT WRITTEN" in capsys.readouterr().err
    assert read(hidden, "config/app_features/hidden.yaml") == HIDDEN_FEATURES


def test_the_facts_for_naming_the_switch_are_listed(hidden):
    plan = tool.build_plan(hidden)
    text = "\n".join(plan.facts)
    assert "hidden.yaml: ui_title sets a mapping (text: My banner, subtitle: Line, visible: false)" in text
    assert "user.yaml: default_app_features = hidden; branding keys: theme_css, banner; banner keys: title, subtitle" in text
    assert "other.yaml: default_app_features = other; branding keys: contact; banner keys: (no banner)" in text


def test_a_visible_true_ui_title_is_removed_with_what_it_set(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/f.yaml", "name: f\nui_title:\n  text: x\n  subtitle: y\n  visible: true\n")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/app_features/f.yaml"] == "name: f\n"
    assert [c.value for c in plan.changes if c.rule == "R09"] == ["a mapping (text: x, subtitle: y, visible: true)"]
    assert not any(c.case == "OC15" for c in plan.cases)


def test_once_the_key_is_named_the_switch_is_written_in_the_deployments_that_use_the_file(hidden, monkeypatch):
    monkeypatch.setattr(tool, "BANNER_SWITCH_KEY", "branding.show_recipe_banner")
    plan = tool.build_plan(hidden)
    assert plan.texts[hidden / "config/app_features/hidden.yaml"] == "name: hidden\ndisplay_name: H\nflags:\n  a: true\n"
    user = plan.texts[hidden / "config/deployment/a/user.yaml"]
    assert user.endswith("  banner:\n    ui_label: \"T\"\n    description: \"S\"\n  show_recipe_banner: false\n")
    assert hidden / "config/deployment/a/other.yaml" not in plan.texts           # it uses another app features file
    assert not any(c.case == "OC15" for c in plan.cases)
    assert tool.main(["--root", str(hidden), "--apply"]) == 0
    assert tool.build_plan(hidden).changes == []                                 # a second run changes nothing


def test_the_switch_is_not_written_where_no_deployment_uses_the_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "BANNER_SWITCH_KEY", "branding.show_recipe_banner")
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/other.yaml", OTHER_DEPLOYMENT)
    plan = tool.build_plan(root)
    assert plan.texts == {} and any(c.case == "OC15" and "nowhere to go" in c.detail for c in plan.cases)


def test_a_switch_that_cannot_be_placed_keeps_the_ui_title(tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "BANNER_SWITCH_KEY", "branding.show_recipe_banner")
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/user.yaml", "deployment_type: filesystem\ndefault_app_features: hidden\n")     # no branding block
    plan = tool.build_plan(root)
    assert hidden_kept(plan, root)
    assert any(c.case == "OC13" for c in plan.cases) and any(c.case == "OC15" for c in plan.cases)


def hidden_kept(plan, root):
    return root / "config/app_features/hidden.yaml" not in plan.texts and not any(c.rule == "R09" for c in plan.changes)


# -- the report ----------------------------------------------------------------------------------------------------------

def test_the_report_is_written_as_markdown_with_the_counts_first(tree, tmp_path):
    report = tmp_path / "out" / "report.md"
    before = digest(tree)
    tool.main(["--root", str(tree), "--report", str(report)])
    text = report.read_text(encoding="utf-8")
    assert text.startswith("# ")
    assert "CANNOT BE DECIDED BY THE SCRIPT" in text and "R04" in text
    assert text.index("## Summary") < text.index("CANNOT BE DECIDED BY THE SCRIPT")
    assert digest(tree) == before


def test_the_report_cannot_overwrite_a_scanned_file(tree, capsys):
    target = tree / "config/app_features/f.yaml"
    before = target.read_text(encoding="utf-8")
    assert tool.main(["--root", str(tree), "--report", str(target)]) == 3
    assert target.read_text(encoding="utf-8") == before


def test_help_names_the_modes_and_the_refusal(capsys):
    with pytest.raises(SystemExit) as stop:
        tool.main(["--help"])
    assert stop.value.code == 0
    out = capsys.readouterr().out
    for word in ("--root", "--apply", "--report", "DRY RUN", "D-0407"):
        assert word in out
