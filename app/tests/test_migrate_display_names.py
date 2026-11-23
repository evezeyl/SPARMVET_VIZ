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
DEPLOYMENT_BLOCK = "# X\n" + tool.BLOCK_MARKER_LINE + "\n# Default app features: f\n# Contact: c@x\n"
DEPLOYMENT_AFTER = DEPLOYMENT_BLOCK + """deployment_type: filesystem
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
APP_FEATURES_AFTER = """ui_label: "F name"
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
    assert {"R06", "R07", "R08", "R15"} <= set(rules_of(plan))


def test_app_features_ui_title_block_is_removed_and_display_name_becomes_ui_label_and_name_stays(tree):
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "config/app_features/f.yaml"] == APP_FEATURES_AFTER      # the key `name` is removed (D-0481)
    assert {"R09", "R13", "R16"} <= set(rules_of(plan))
    assert not any(c.case == "OC07" for c in plan.cases)
    assert [c.ledger for c in plan.changes if c.rule == "R13"] == ["D-0480"]


def test_an_app_features_file_with_display_name_and_ui_label_is_a_conflict_and_is_not_changed(tmp_path):
    root = tmp_path / "copy"
    text = "name: f\ndisplay_name: A\nui_label: B\n"
    write(root, "config/app_features/f.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts == {root / "config/app_features/f.yaml": "display_name: A\nui_label: B\n"}      # only the name key goes; the conflict is not overwritten
    assert any(c.case == "CONFLICT" and "display_name" in c.detail for c in plan.cases)


def test_a_gallery_bundle_is_planned_like_a_recipe(tree):
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "assets/gallery_data/ex/data_analysis_recipe.yaml"] == GALLERY_AFTER
    assert plan.kind_counts["Gallery bundles"]["changes"] == 1


def test_counts_per_file_kind(tree):
    plan = tool.build_plan(tree)
    assert plan.kind_counts["recipes"]["changes"] == 7 and plan.kind_counts["recipes"]["files"] == 2
    assert plan.kind_counts["deployment files"]["changes"] == 4          # the banner title, the subtitle, the name, the comment block
    assert plan.kind_counts["app features files"]["changes"] == 3          # the ui_title block, display_name -> ui_label, the name key


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
    assert plan.texts[root / "config/app_features/f.yaml"] == ""      # a flow VALUE is fine: its pair sits in a block mapping
    write(root, "config/app_features/f.yaml", "name: f\nui_title: a")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/app_features/f.yaml"] == ""


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


def test_a_deployment_name_with_no_banner_is_removed_and_goes_into_the_comment_block(tmp_path):
    root = tmp_path / "copy"
    text = "deployment_type: filesystem\ndeployment_name: \"Only name\"\nbranding:\n  contact: c\n"
    write(root, "config/deployment/local/l.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/deployment/local/l.yaml"] == "# Only name\n" + tool.BLOCK_MARKER_LINE + "\n# Contact: c\n" + "deployment_type: filesystem\nbranding:\n  contact: c\n"
    assert not any(c.case == "OC06" for c in plan.cases)


def test_the_comment_block_comes_first_and_an_existing_header_comment_is_kept_below_it(tmp_path):
    root = tmp_path / "copy"
    text = "# Header of the file\n# second line\ndeployment_type: filesystem\ndeployment_name: N\ndefault_data_analysis_recipe: rec\n"
    write(root, "config/deployment/local/l.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/deployment/local/l.yaml"] == (
        "# N\n" + tool.BLOCK_MARKER_LINE + "\n# Default recipe: rec\n# Header of the file\n# second line\ndeployment_type: filesystem\ndefault_data_analysis_recipe: rec\n")
    placed = [b for b in plan.blocks if b.file.endswith("l.yaml")]
    assert len(placed) == 1 and "before the existing leading comment (2 line(s))" in placed[0].placement


def test_an_empty_or_absent_deployment_name_gets_no_block(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/deployment/a/empty.yaml", "deployment_type: filesystem\ndeployment_name: \"\"\ndefault_app_features: f\n")
    write(root, "config/deployment/a/absent.yaml", "deployment_type: filesystem\ndefault_app_features: f\n")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/deployment/a/empty.yaml"] == "deployment_type: filesystem\ndefault_app_features: f\n"      # the key goes, no block
    assert root / "config/deployment/a/absent.yaml" not in plan.texts
    assert plan.blocks == []


def test_a_line_the_file_cannot_fill_is_left_out_and_nothing_is_invented(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/deployment/a/n.yaml", "deployment_name: Only\ndeployment_type: filesystem\n")
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/deployment/a/n.yaml"] == "# Only\n" + tool.BLOCK_MARKER_LINE + "\ndeployment_type: filesystem\n"


def test_the_comment_block_is_written_once_and_a_second_run_changes_nothing(tree):
    assert tool.main(["--root", str(tree), "--apply"]) == 0
    first = read(tree, "config/deployment/demo/d.yaml")
    assert first == DEPLOYMENT_AFTER and first.count(tool.BLOCK_MARKER_LINE) == 1
    plan = tool.build_plan(tree)
    assert plan.changes == [] and plan.blocks == []
    # a file that already holds the block and gets the key back: the block is not written twice
    write(tree, "config/deployment/demo/d.yaml", first + "deployment_name: Y\n")
    plan = tool.build_plan(tree)
    assert plan.texts[tree / "config/deployment/demo/d.yaml"].count(tool.BLOCK_MARKER_LINE) == 1


def test_the_dry_run_prints_every_block_in_full(tree, capsys):
    tool.main(["--root", str(tree)])
    out = capsys.readouterr().out
    assert "COMMENT BLOCKS" in out and "PROVISIONAL" in out and "D-0479" in out
    for line in DEPLOYMENT_BLOCK.splitlines():
        assert line in out
    assert "config/deployment/demo/d.yaml" in out


def test_the_code_places_that_read_a_deployment_name_are_listed_and_not_changed(tmp_path):
    root = tmp_path / "copy"
    write(root, "app/src/bootloader.py", "x = 1\nself.deployment_name = a.get('deployment_name')\n")
    write(root, "libs/connector/src/connector/base.py", "def get_deployment_name(self):\n    return 1\n")
    write(root, "app/tests/test_dep.py", "body = {'deployment_name': 'x'}\n")
    write(root, "libs/other/tests/test_o.py", "nothing here\n")
    write(root, "app/src/server.py", "a = bootloader.app_features_display_name\n")
    write(root, "app/modules/renamed_keys.py", "OLD = {'display_name': 'ui_label'}\n")
    write(root, "docs/ref.qmd", "the `display_name` key\n")
    before = digest(root)
    plan = tool.build_plan(root)
    places = {(c.file, c.line) for c in plan.code_places}
    assert ("app/src/bootloader.py", 2) in places and ("libs/connector/src/connector/base.py", 1) in places and ("app/tests/test_dep.py", 1) in places
    assert not any("test_o.py" in c.file for c in plan.code_places)
    names = {(c.file, c.line, c.key, c.kind) for c in plan.code_places}
    assert ("app/src/server.py", 1, "display_name", "code") in names and ("app/modules/renamed_keys.py", 1, "display_name", "code") in names
    assert ("docs/ref.qmd", 1, "display_name", "doc") in names
    assert digest(root) == before


def test_a_removed_ui_title_that_differs_from_ui_label_is_an_open_case_with_the_full_text(tree):
    plan = tool.build_plan(tree)
    lost = [c for c in plan.cases if c.case == "OC16"]
    assert len(lost) == 1 and "A longer group name" in lost[0].detail          # a group has no figure: its text is still kept nowhere
    notitle = " ".join(c.detail for c in plan.cases if c.case == "OC19")      # the two plots of the tree have no labs layer
    assert "A longer plot name" in notitle and "A long title on two lines" in notitle
    assert any(c.rule == "R05" for c in plan.changes)       # the removal itself stays applied


def test_a_long_removed_title_is_printed_in_full(tmp_path, capsys):
    root = tmp_path / "copy"
    long_text = " ".join(f"word{i}" for i in range(40))
    write(root, "config/data_analysis_recipes/pipelines/r.yaml",
          "id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n  g:\n    ui_label: G\n    plots:\n      p:\n        ui_label: P\n        ui_title: \"" + long_text + "\"\n")
    tool.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert out.count(long_text) >= 2                      # in the list of changes and in the case
    assert "OC19" in out and "no figure title" in out
    assert "1 listed place(s) in 1 open case(s)" in out.split("Summary")[1].split("\n")[1]


# -- safety: nothing is written through a shared file, nothing outside the report, all or nothing -----------------------------

def hardlink_copy(source: Path, target: Path) -> None:
    """What `cp -al` does: every file of the copy is the same file (same inode) as the original."""
    import os
    for path in sorted(source.rglob("*")):
        destination = target / path.relative_to(source)
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            os.link(path, destination)


def test_a_hard_linked_copy_is_refused_and_the_original_keeps_its_bytes(tree, tmp_path, capsys):
    link = tmp_path / "linked"
    hardlink_copy(tree, link)
    before = digest(tree)
    assert tool.main(["--root", str(link), "--apply"]) == 3
    assert "hard link" in capsys.readouterr().err
    assert digest(tree) == before and digest(link) == before


def test_a_write_never_goes_through_a_shared_inode(tmp_path):
    original = tmp_path / "a.yaml"
    original.write_bytes(b"old\n")
    shared = tmp_path / "b.yaml"
    import os
    os.link(original, shared)
    tool.write_atomic(shared, "new\n")
    assert original.read_bytes() == b"old\n" and shared.read_bytes() == b"new\n"
    assert not [p for p in tmp_path.iterdir() if p.name not in ("a.yaml", "b.yaml")]      # no temporary file left


def test_a_mixed_root_writes_nothing_before_it_refuses(tmp_path, capsys):
    import os
    root = tmp_path / "copy"
    write(root, "config/app_features/a.yaml", APP_FEATURES)
    outside = tmp_path / "outside"
    write(outside, "b.yaml", APP_FEATURES)
    (root / "config/app_features").mkdir(parents=True, exist_ok=True)
    os.symlink(outside / "b.yaml", root / "config/app_features/b.yaml")
    assert tool.main(["--root", str(root), "--apply"]) == 3
    assert read(root, "config/app_features/a.yaml") == APP_FEATURES           # the inside file was planned first and is still untouched
    assert (outside / "b.yaml").read_text(encoding="utf-8") == APP_FEATURES
    assert "outside" in capsys.readouterr().err


def test_the_report_cannot_replace_a_tracked_file_in_a_dry_run(tree, capsys):
    target = tree / "README.md"
    target.write_text("keep\n", encoding="utf-8")
    assert tool.main(["--root", str(tree), "--report", str(target)]) == 3
    assert target.read_text(encoding="utf-8") == "keep\n"
    assert "already exists" in capsys.readouterr().err


def test_the_report_inside_the_root_must_be_under_tmpAI(tree, capsys):
    refused = tree / "notes" / "report.md"
    assert tool.main(["--root", str(tree), "--report", str(refused)]) == 3
    assert not refused.exists() and "tmpAI" in capsys.readouterr().err
    allowed = tree / "tmpAI" / "r.md"
    tool.main(["--root", str(tree), "--report", str(allowed)])
    assert allowed.is_file()


def test_the_report_refuses_a_second_write_to_the_same_name(tree, tmp_path):
    report = tmp_path / "out" / "r.md"
    tool.main(["--root", str(tree), "--report", str(report)])
    first = report.read_bytes()
    assert tool.main(["--root", str(tree), "--report", str(report)]) == 3
    assert report.read_bytes() == first


# -- line ends and the byte order mark -----------------------------------------------------------------------------------------

def test_crlf_line_ends_are_kept_byte_for_byte_outside_the_changed_keys(tmp_path):
    root = tmp_path / "copy"
    raw = RECIPE.replace("\n", "\r\n").encode("utf-8")
    path = root / "config/data_analysis_recipes/pipelines/r.yaml"
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert path.read_bytes() == RECIPE_AFTER.replace("\n", "\r\n").encode("utf-8")
    dep = root / "config/deployment/d.yaml"
    dep.parent.mkdir(parents=True)
    dep.write_bytes(DEPLOYMENT.replace("\n", "\r\n").encode("utf-8"))
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert dep.read_bytes() == DEPLOYMENT_AFTER.replace("\n", "\r\n").encode("utf-8")


def test_a_byte_order_mark_is_kept(tmp_path):
    root = tmp_path / "copy"
    path = root / "config/data_analysis_recipes/pipelines/r.yaml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\xef\xbb\xbf" + RECIPE.encode("utf-8"))
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert path.read_bytes() == b"\xef\xbb\xbf" + RECIPE_AFTER.encode("utf-8")
    dep = root / "config/deployment/d.yaml"
    dep.parent.mkdir(parents=True)
    dep.write_bytes(b"\xef\xbb\xbf" + DEPLOYMENT.encode("utf-8"))
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert dep.read_bytes() == b"\xef\xbb\xbf" + DEPLOYMENT_AFTER.encode("utf-8")      # the block comes after the mark


# -- the files read and not examined ---------------------------------------------------------------------------------------------

def test_every_file_read_but_not_examined_is_listed_and_the_ones_with_display_keys_are_named(tmp_path, capsys):
    root = tmp_path / "copy"
    for i in range(15):
        write(root, f"config/data_analysis_recipes/frag/f{i}.yaml", "steps: []\n" if i else "steps: []\nnested:\n  label: L\n")
    plan = tool.build_plan(root)
    assert len(plan.unexamined) == 15
    assert [u for u, _ in plan.unexamined_keys] == ["config/data_analysis_recipes/frag/f0.yaml"]
    tool.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert out.count("config/data_analysis_recipes/frag/f") >= 16 and "f14.yaml" in out
    assert "label" in out.split("not examined")[1]


# -- the words of the script are true ------------------------------------------------------------------------------------------------

def test_the_script_cites_written_lines_only():
    text = Path(tool.__file__).read_text(encoding="utf-8")
    assert "to be written" not in text and "no words of hers" not in text and "not yet written" not in text
    assert "D-0475" in text and "D-0479" in text
    assert "writes nothing except the report file you name" in text


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

HIDDEN_FEATURES = "name: hidden\nui_label: H\nui_title:\n  text: \"My banner\"\n  subtitle: \"Line\"\n  visible: false\nflags:\n  a: true\n"
HIDDEN_NO_NAME = HIDDEN_FEATURES.replace("name: hidden\n", "")
USER_DEPLOYMENT = "deployment_type: filesystem\ndefault_app_features: \"hidden\"\nbranding:\n  theme_css: a.css\n  banner:\n    title: \"T\"\n    subtitle: \"S\"\n"
OTHER_DEPLOYMENT = "deployment_type: filesystem\ndefault_app_features: \"other\"\nbranding:\n  contact: c\n"


@pytest.fixture
def hidden(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/user.yaml", USER_DEPLOYMENT)
    write(root, "config/deployment/a/other.yaml", OTHER_DEPLOYMENT)
    return root


def test_the_switch_key_is_one_constant_and_is_the_accepted_one():
    assert tool.BANNER_SWITCH_KEY == "branding.show_recipe_name"
    assert sum(1 for line in Path(tool.__file__).read_text(encoding="utf-8").splitlines() if "show_recipe_name" in line and "BANNER_SWITCH_KEY" in line) == 1


def test_an_app_features_file_that_hides_the_banner_is_kept_and_listed_while_the_key_is_unset(hidden, capsys, monkeypatch):
    monkeypatch.setattr(tool, "BANNER_SWITCH_KEY", None)
    plan = tool.build_plan(hidden)
    assert plan.texts[hidden / "config/app_features/hidden.yaml"] == HIDDEN_NO_NAME          # only the name key goes; the ui_title is kept
    found = [c for c in plan.cases if c.case == "OC15"]
    assert len(found) == 1 and found[0].line == 3
    assert "user.yaml" in found[0].detail and "other.yaml" not in found[0].detail.split("banner of each")[0]
    assert "'T'" in found[0].detail and "BANNER_SWITCH_KEY is not set" in found[0].detail
    assert tool.main(["--root", str(hidden), "--apply"]) == 2
    assert "NOT WRITTEN" in capsys.readouterr().err
    assert read(hidden, "config/app_features/hidden.yaml") == HIDDEN_NO_NAME


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
    assert plan.texts[root / "config/app_features/f.yaml"] == ""
    assert [c.value for c in plan.changes if c.rule == "R09"] == ["a mapping (text: x, subtitle: y, visible: true)"]
    assert not any(c.case == "OC15" for c in plan.cases)


def test_the_switch_is_written_in_the_one_deployment_that_uses_the_file(hidden):
    plan = tool.build_plan(hidden)
    assert plan.texts[hidden / "config/app_features/hidden.yaml"] == "ui_label: H\nflags:\n  a: true\n"
    user = plan.texts[hidden / "config/deployment/a/user.yaml"]
    assert user.endswith("  banner:\n    ui_label: \"T\"\n    description: \"S\"\n  show_recipe_name: false\n")
    assert hidden / "config/deployment/a/other.yaml" not in plan.texts           # it uses another app features file
    assert not any(c.case == "OC15" for c in plan.cases)
    assert tool.main(["--root", str(hidden), "--apply"]) == 0
    assert tool.build_plan(hidden).changes == []                                 # a second run changes nothing


def test_the_switch_is_not_written_where_no_deployment_uses_the_file(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/other.yaml", OTHER_DEPLOYMENT)
    plan = tool.build_plan(root)
    assert plan.texts == {root / "config/app_features/hidden.yaml": HIDDEN_NO_NAME} and any(c.case == "OC15" and "nowhere to go" in c.detail for c in plan.cases)


def test_a_switch_that_cannot_be_placed_keeps_the_ui_title(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES)
    write(root, "config/deployment/a/user.yaml", "deployment_type: filesystem\ndefault_app_features: hidden\n")     # no branding block
    plan = tool.build_plan(root)
    assert hidden_kept(plan, root)
    assert any(c.case == "OC13" for c in plan.cases) and any(c.case == "OC15" for c in plan.cases)


def test_two_deployments_that_name_the_file_are_not_one_to_one_and_nothing_is_written(hidden):
    write(hidden, "config/deployment/a/second.yaml", USER_DEPLOYMENT)
    plan = tool.build_plan(hidden)
    assert plan.texts[hidden / "config/app_features/hidden.yaml"] == HIDDEN_NO_NAME
    assert not any(c.rule == "R14" for c in plan.changes)
    found = [c for c in plan.cases if c.case == "OC15"]
    assert len(found) == 1 and "not one to one" in found[0].detail and "2 deployments" in found[0].detail
    assert "show_recipe_name" not in plan.texts.get(hidden / "config/deployment/a/user.yaml", "")


def test_a_switch_key_already_written_is_a_conflict_and_the_ui_title_is_kept(hidden):
    write(hidden, "config/deployment/a/user.yaml", USER_DEPLOYMENT + "  show_recipe_name: true\n")
    plan = tool.build_plan(hidden)
    assert any(c.case == "CONFLICT" and "show_recipe_name" in c.detail for c in plan.cases)
    assert plan.texts[hidden / "config/app_features/hidden.yaml"] == HIDDEN_NO_NAME


def hidden_kept(plan, root):
    return plan.texts.get(root / "config/app_features/hidden.yaml") == HIDDEN_NO_NAME and not any(c.rule == "R09" for c in plan.changes)


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


def test_a_name_on_the_first_line_of_a_file_with_a_byte_order_mark_is_removed_and_the_mark_stays_first(tmp_path):
    root = tmp_path / "copy"
    path = root / "config/deployment/d.yaml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\xef\xbb\xbfdeployment_name: N\r\ndeployment_type: filesystem\r\n")
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert path.read_bytes() == b"\xef\xbb\xbf# N\r\n" + tool.BLOCK_MARKER_LINE.encode() + b"\r\ndeployment_type: filesystem\r\n"


# -- the key `name` of the app features files (D-0481), file names (D-0483), write failures ----------------------------------

def test_the_key_name_of_an_app_features_file_is_removed_and_the_rest_is_byte_for_byte(tmp_path):
    root = tmp_path / "copy"
    text = "# header\nname: \"f\"   # the id\nflags:\n  a: true\n"
    write(root, "config/app_features/f.yaml", text)
    plan = tool.build_plan(root)
    assert plan.texts[root / "config/app_features/f.yaml"] == "# header\nflags:\n  a: true\n"
    change = [c for c in plan.changes if c.rule == "R16"]
    assert len(change) == 1 and change[0].ledger == "D-0481" and change[0].new is None and change[0].line == 2
    assert "file name: f" in change[0].value and "DIFFERS" not in change[0].value
    assert not any(c.case == "OC17" for c in plan.cases)


NESTED = """name: top-of-a-recipe
spec_version: 1
id: r
info:
  ui_label: R
data_schemas:
  A:
    source: {type: local_tsv, path: a.tsv}
analysis_groups:
  g:
    ui_label: G
    plots:
      p:
        ui_label: P
        layers:
          - name: geom_bar
            params: {}
"""


def test_a_key_called_name_anywhere_else_is_never_touched(tmp_path):
    root = tmp_path / "copy"
    recipe = write(root, "config/data_analysis_recipes/pipelines/r.yaml", NESTED)
    deployment = write(root, "config/deployment/d/d.yaml", "name: not-an-app-features-file\ndeployment_type: filesystem\nbranding:\n  name: x\n")
    features = write(root, "config/app_features/f.yaml", "name: f\nflags:\n  a: true\nworkspaces:\n  home:\n    left_sidebar:\n      panels:\n        - name: n\n          type: t\nlayers:\n  - name: geom_bar\n")
    plan = tool.build_plan(root)
    assert [c.rule for c in plan.changes if c.file.endswith("r.yaml")] == []
    assert recipe not in plan.texts or "name: top-of-a-recipe" in plan.texts[recipe]
    assert "name: not-an-app-features-file" in plan.texts.get(deployment, deployment.read_text(encoding="utf-8"))
    after = plan.texts[features]
    assert after.startswith("flags:") and after.count("name:") == 2 and "- name: n" in after and "- name: geom_bar" in after
    assert [c.rule for c in plan.changes if c.file.endswith("f.yaml")].count("R16") == 1


def test_a_name_that_differs_from_the_file_name_is_removed_and_listed(tmp_path, capsys):
    root = tmp_path / "copy"
    write(root, "config/app_features/pipeline-x.yaml", "name: pipeline_x\nflags: {}\n")
    write(root, "config/app_features/same.yaml", "name: same\nflags: {}\n")
    plan = tool.build_plan(root)
    listed = [c for c in plan.cases if c.case == "OC17"]
    assert len(listed) == 1 and listed[0].file.endswith("pipeline-x.yaml") and "'pipeline_x'" in listed[0].detail and "'pipeline-x'" in listed[0].detail
    assert any("DIFFERS" in c.value for c in plan.changes if c.rule == "R16")
    assert plan.texts[root / "config/app_features/pipeline-x.yaml"] == "flags: {}\n"
    tool.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert "OC17" in out and "value: pipeline_x; file name: pipeline-x (DIFFERS)" in out


@pytest.mark.parametrize("order", [
    "name: f\ndisplay_name: A\nflags: {}\n",
    "display_name: A\nname: f\nflags: {}\n",
    "display_name: A\nflags: {}\nname: f\n",
])
def test_the_name_rule_and_the_display_name_rule_give_the_same_result_in_any_order_and_a_second_run_changes_nothing(tmp_path, order):
    root = tmp_path / "copy"
    write(root, "config/app_features/f.yaml", order)
    assert tool.main(["--root", str(root), "--apply"]) == 0
    result = read(root, "config/app_features/f.yaml")
    assert "name: f" not in result and "ui_label: A" in result and "display_name" not in result and "flags: {}" in result
    before = digest(root)
    assert tool.build_plan(root).changes == [] and tool.main(["--root", str(root), "--apply"]) == 0
    assert digest(root) == before


def test_the_code_places_of_the_name_key_are_listed_from_the_real_tree_and_not_changed():
    plan = tool.build_plan(ROOT)
    places = {(c.file, c.kind) for c in plan.code_places if c.key == tool.APP_FEATURES_NAME_KEY}
    expected = {rel for rel, _p, _k in tool.APP_FEATURES_NAME_PLACES}
    assert {f for f, _ in places} == expected          # every named file still has a line that matches (a moved line is found by text)
    lines = {(c.file, c.text) for c in plan.code_places if c.key == tool.APP_FEATURES_NAME_KEY}
    assert any(f == "app/src/bootloader.py" and 'config.get("name")' in t for f, t in lines)
    assert any(f == "app/modules/renamed_keys.py" and "persona_id" in t for f, t in lines)
    assert any(f == "app/modules/app_features_validator.py" and "Rule 2" in t for f, t in lines)
    assert any(f == "app/modules/sidebar_validator.py" for f, _ in lines)


def test_the_dry_run_prints_the_code_places_of_the_name_key(tmp_path, capsys):
    root = tmp_path / "copy"
    write(root, "app/modules/renamed_keys.py", '    "persona_id": "name",\n')
    tool.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert "name (app features file) (D-0481" in out and "app/modules/renamed_keys.py:1" in out


# a name like `my-file_2026-11-17.yaml` has both characters in every kind of file (D-0483): nothing in the script restricts either

STAMPED = "my-file_2026-11-17"


def test_hyphens_and_underscores_are_both_free_in_the_file_names_of_every_kind_of_file(tmp_path):
    root = tmp_path / "copy"
    write(root, f"config/data_analysis_recipes/pipelines/{STAMPED}.yaml", RECIPE.replace("id: r", f"id: {STAMPED}"))
    write(root, f"config/data_analysis_recipes/pipelines/{STAMPED}/plots/p_file.yaml", PLOT_FILE)
    write(root, f"config/deployment/demo/{STAMPED}.yaml", DEPLOYMENT)
    write(root, f"config/app_features/{STAMPED}.yaml", APP_FEATURES)
    write(root, f"assets/gallery_data/{STAMPED}/data_analysis_recipe.yaml", GALLERY)
    plan = tool.build_plan(root)
    files = {c.file for c in plan.changes}
    assert {f"config/data_analysis_recipes/pipelines/{STAMPED}.yaml", f"config/deployment/demo/{STAMPED}.yaml",
            f"config/app_features/{STAMPED}.yaml", f"assets/gallery_data/{STAMPED}/data_analysis_recipe.yaml"} <= files
    assert plan.kind_counts["app features files"]["files"] == 1 and plan.kind_counts["deployment files"]["files"] == 1
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert read(root, f"config/app_features/{STAMPED}.yaml") == APP_FEATURES_AFTER
    assert tool.build_plan(root).changes == []


def test_an_app_features_file_with_both_characters_in_its_name_is_matched_by_the_deployment_that_names_it(tmp_path):
    root = tmp_path / "copy"
    write(root, f"config/app_features/{STAMPED}.yaml", HIDDEN_FEATURES.replace("name: hidden", f"name: {STAMPED}"))
    write(root, "config/deployment/a/user.yaml", USER_DEPLOYMENT.replace('"hidden"', f'"{STAMPED}"'))
    plan = tool.build_plan(root)
    assert any(c.rule == "R14" for c in plan.changes) and not any(c.case == "OC15" for c in plan.cases)


def test_a_deployment_is_matched_by_the_file_name_and_not_by_a_name_key(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/app_features/hidden.yaml", HIDDEN_FEATURES.replace("name: hidden", "name: something-else"))
    write(root, "config/deployment/a/user.yaml", USER_DEPLOYMENT)
    plan = tool.build_plan(root)
    assert any(c.rule == "R14" for c in plan.changes)


@pytest.mark.skipif(hasattr(__import__("os"), "geteuid") and __import__("os").geteuid() == 0, reason="root can write anywhere")
def test_a_folder_that_cannot_be_written_is_refused_before_the_first_write(tree, capsys):
    import os
    folder = tree / "config/deployment/demo"
    before = digest(tree)
    os.chmod(folder, 0o555)
    try:
        assert tool.main(["--root", str(tree), "--apply"]) == 3
        err = capsys.readouterr().err
        assert "cannot be written" in err and "nothing is written" in err and "Traceback" not in err
        assert digest(tree) == before                 # no earlier file was written
    finally:
        os.chmod(folder, 0o755)


def test_a_write_that_fails_after_the_check_ends_with_a_plain_message_not_a_traceback(tree, capsys, monkeypatch):
    real = tool.write_atomic
    calls = []

    def flaky(path, text):
        calls.append(path)
        if len(calls) == 2:
            raise PermissionError(13, "Permission denied")
        real(path, text)

    monkeypatch.setattr(tool, "write_atomic", flaky)
    assert tool.main(["--root", str(tree), "--apply"]) == 3
    err = capsys.readouterr().err
    assert "could not be written" in err and "Permission denied" in err and "Already written" in err and str(calls[0]) in err and "Traceback" not in err


# -- the removed plot `ui_title` against the figure title of its `labs` layer (D-0484) -----------------------------------------

def plot_recipe(plot_body: str, include: bool = False) -> str:
    head = "id: r\nspec_version: 1\ninfo:\n  ui_label: R\nanalysis_groups:\n  g:\n    ui_label: G\n    plots:\n"
    if include:
        return head + "      p: !include 'r/plots/p.yaml'\n"
    return head + "      p:\n" + "".join("        " + line + "\n" for line in plot_body.splitlines())


def cases_of(plan, case):
    return [c for c in plan.cases if c.case == case]


LABS = "layers:\n  - name: geom_bar\n  - name: labs\n    params:\n      title: \"{t}\"\n"


def test_a_removed_plot_title_equal_to_the_labs_title_is_listed_as_the_same(tmp_path):
    root = tmp_path / "copy"
    body = 'ui_label: P\nui_title: "Counts per year"\n' + LABS.format(t="Counts per year")
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe(body))
    plan = tool.build_plan(root)
    assert len(cases_of(plan, "OC20")) == 1 and not cases_of(plan, "OC18") and not cases_of(plan, "OC19") and not cases_of(plan, "OC16")
    assert "same as the figure title" in cases_of(plan, "OC20")[0].detail
    assert any(c.rule == "R05" for c in plan.changes)


def test_a_removed_plot_title_that_differs_from_the_labs_title_prints_both_texts_in_full(tmp_path):
    root = tmp_path / "copy"
    body = 'ui_label: P\nui_title: "Counts per year"\n' + LABS.format(t="Counts per year, all farms")
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe(body))
    plan = tool.build_plan(root)
    found = cases_of(plan, "OC18")
    assert len(found) == 1 and "DIFFERS from the figure title" in found[0].detail
    assert "Counts per year" in found[0].detail and "Counts per year, all farms" in found[0].detail
    assert any(c.rule == "R05" for c in plan.changes)       # the removal stays applied


def test_an_included_plot_entry_is_compared_too(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe("", include=True))
    write(root, "config/data_analysis_recipes/pipelines/r/plots/p.yaml", 'ui_label: P\nui_title: A\n' + LABS.format(t="A"))
    plan = tool.build_plan(root)
    assert len(cases_of(plan, "OC20")) == 1 and cases_of(plan, "OC20")[0].file.endswith("r/plots/p.yaml")


@pytest.mark.parametrize("layers", ["layers:\n  - name: geom_bar\n  - name: labs\n    params:\n      x: Year\n",
                                    "layers:\n  - name: geom_bar\n  - name: labs\n",
                                    "layers:\n  - name: geom_bar\n",
                                    ""])
def test_a_plot_with_no_figure_title_is_listed_with_the_removed_text_and_is_not_an_error(tmp_path, layers, capsys):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe('ui_label: P\nui_title: "A very long removed title"\n' + layers))
    plan = tool.build_plan(root)
    found = cases_of(plan, "OC19")
    assert len(found) == 1 and "A very long removed title" in found[0].detail and "no figure title" in found[0].detail
    assert not plan.blocking
    assert tool.main(["--root", str(root), "--apply"]) == 0
    assert "ui_title" not in read(root, "config/data_analysis_recipes/pipelines/r.yaml")


def test_two_labs_layers_the_last_title_counts_and_the_detail_says_so(tmp_path):
    root = tmp_path / "copy"
    body = ('ui_label: P\nui_title: "T1"\nlayers:\n  - name: labs\n    params: {title: "T1"}\n  - name: labs\n    params: {title: "T2"}\n')
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe(body))
    found = cases_of(tool.build_plan(root), "OC18")
    assert len(found) == 1 and "2 labs layers" in found[0].detail and "T2" in found[0].detail


def test_the_summary_counts_the_differing_and_missing_titles_as_cases_to_read_and_the_same_ones_apart(tmp_path, capsys):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe('ui_label: P\nui_title: "A"\n' + LABS.format(t="A")))
    tool.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert "0 listed place(s) in 0 open case(s)" in out.split("Summary")[1].split("\n")[1]
    assert "1 plot title(s) removed: 1 same as the figure title, 0 same except spaces, 0 differ, 0 plot(s) have no figure title" in out


def test_a_plain_name_key_inside_a_nested_mapping_of_an_app_features_file_stays(tmp_path):
    root = tmp_path / "copy"
    features = write(root, "config/app_features/f.yaml", "name: f\nflags:\n  name: keep\n  deeper:\n    name: keep too\n")
    plan = tool.build_plan(root)
    after = plan.texts[features]
    assert "name: keep\n" in after and "name: keep too" in after and not after.startswith("name:")
    assert [c.rule for c in plan.changes if c.file.endswith("f.yaml")].count("R16") == 1


# -- exact comparison of the removed plot title; what the pass does not read (D-0484) --------------------------------------------

@pytest.mark.parametrize("removed, figure", [("Title C ", "Title C"), ("Title  C", "Title C"), ("Title\tC", "Title C")])
def test_a_title_equal_only_after_spaces_are_collapsed_is_its_own_visible_result(tmp_path, capsys, removed, figure):
    root = tmp_path / "copy"
    body = "ui_label: P\nui_title: \"" + removed.replace("\t", "\\t") + "\"\n" + LABS.format(t=figure)
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe(body))
    plan = tool.build_plan(root)
    assert not cases_of(plan, "OC20") and not cases_of(plan, "OC18")
    found = cases_of(plan, "OC21")
    assert len(found) == 1 and "same except spaces" in found[0].detail
    assert f'"{removed}"' in found[0].detail and f'"{figure}"' in found[0].detail
    assert any(c.rule == "R05" for c in plan.changes)
    tool.main(["--root", str(root)])
    assert "1 same except spaces" in capsys.readouterr().out


def test_an_exactly_equal_title_is_still_the_same(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe('ui_label: P\nui_title: "Title C"\n' + LABS.format(t="Title C")))
    plan = tool.build_plan(root)
    assert len(cases_of(plan, "OC20")) == 1 and not cases_of(plan, "OC21")


def test_a_plot_with_only_a_ggtitle_layer_says_no_figure_title_in_a_labs_layer_and_names_the_ggtitle(tmp_path):
    root = tmp_path / "copy"
    body = 'ui_label: P\nui_title: "T"\nlayers:\n  - name: geom_bar\n  - name: ggtitle\n    params:\n      label: "T"\n'
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe(body))
    found = cases_of(tool.build_plan(root), "OC19")
    assert len(found) == 1 and "no figure title in a labs layer" in found[0].detail
    assert "the plot has a ggtitle layer, which this pass does not read: its text is not compared" in found[0].detail


def test_a_plot_without_a_ggtitle_layer_does_not_mention_it(tmp_path):
    root = tmp_path / "copy"
    write(root, "config/data_analysis_recipes/pipelines/r.yaml", plot_recipe('ui_label: P\nui_title: "T"\nlayers:\n  - name: geom_bar\n'))
    found = cases_of(tool.build_plan(root), "OC19")
    assert "no figure title in a labs layer" in found[0].detail and "ggtitle" not in found[0].detail


# -- --apply --in-worktree: the one way to write in a git working tree (the build branch of the names pass) ----------------

def _git_in(path, *args):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": __import__("os").environ["PATH"], "HOME": str(path)}
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, env=env)


@pytest.fixture
def linked_worktree(tmp_path, monkeypatch):
    """A throw-away repository on branch `dev` with a linked worktree on branch `build`; the script is told that the worktree is its own."""
    main = tmp_path / "main"
    write(main, "config/app_features/f.yaml", APP_FEATURES)
    write(main, "config/deployment/demo/d.yaml", DEPLOYMENT)
    _git_in(main, "init", "-q", "-b", "dev")
    _git_in(main, "add", "-A")
    _git_in(main, "commit", "-q", "-m", "init")
    worktree = tmp_path / "wt"
    _git_in(main, "worktree", "add", "-q", "-b", "build", str(worktree))
    monkeypatch.setattr(tool, "PROJECT_ROOT", worktree)
    return main, worktree


def test_in_worktree_writes_in_a_clean_linked_worktree_on_a_build_branch(linked_worktree, capsys):
    main, worktree = linked_worktree
    before_main = digest(main)
    assert tool.main(["--apply", "--in-worktree"]) in (0, 2)
    assert "name:" not in read(worktree, "config/app_features/f.yaml")
    assert digest(main) == before_main                      # the main checkout is untouched


def test_in_worktree_refuses_the_main_checkout(linked_worktree, monkeypatch, capsys):
    main, worktree = linked_worktree
    monkeypatch.setattr(tool, "PROJECT_ROOT", main)
    before = digest(main)
    assert tool.main(["--apply", "--in-worktree"]) == 3
    assert "LINKED git worktree" in capsys.readouterr().err
    assert digest(main) == before


def test_in_worktree_refuses_the_branch_main(linked_worktree, capsys):
    main, worktree = linked_worktree
    _git_in(worktree, "checkout", "-q", "-b", "main")
    before = digest(worktree)
    assert tool.main(["--apply", "--in-worktree"]) == 3
    assert "branch 'main'" in capsys.readouterr().err
    assert digest(worktree) == before


def test_in_worktree_refuses_uncommitted_changes(linked_worktree, capsys):
    main, worktree = linked_worktree
    (worktree / "config/app_features/f.yaml").write_text(APP_FEATURES + "\nextra: 1\n", encoding="utf-8")
    before = digest(worktree)
    assert tool.main(["--apply", "--in-worktree"]) == 3
    assert "uncommitted" in capsys.readouterr().err
    assert digest(worktree) == before


def test_in_worktree_refuses_a_given_root_and_a_dry_run(linked_worktree, capsys):
    main, worktree = linked_worktree
    assert tool.main(["--apply", "--in-worktree", "--root", str(worktree)]) == 3
    assert tool.main(["--in-worktree"]) == 3
    assert "only meaningful with --apply" in capsys.readouterr().err
