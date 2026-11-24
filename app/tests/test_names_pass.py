"""The names pass (D-0409, D-0410, D-0411, D-0468, D-0474, D-0479 to D-0482, D-0484, D-0497): `ui_label` is the one name key.

Covers: each old name is refused with the new name (recipe check, deployment file, app features file); the export and HOME show the
same `ui_label` (no invented fallback); the recipe banner and its switch; the export writes the app features file as `Web Demo (web-demo)`;
and a search that shows no removed key or fallback is left in code, shipped recipes, Gallery bundles, templates, deployment and app
features files.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_names_pass.py -q
"""

# @deps
# provides: -
# consumes: libs/utils/src/utils/recipe_check.py, app/modules/renamed_keys.py, app/modules/recipe_banner.py, app/src/bootloader.py, app/handlers/export_handlers.py, app/handlers/home_theater.py
# doc: .claude/knowledge/decision_ledger.md (D-0409, D-0410, D-0411, D-0468, D-0474, D-0479 to D-0484, D-0497), .claude/tasks/tasks.md (NAMES-UI-LABEL-EVERYWHERE)
# @end_deps
import copy
import re
from pathlib import Path

import pytest
import yaml

from app.modules import renamed_keys as rk
from app.modules.recipe_banner import recipe_banner_title
from app.src.bootloader import Bootloader
from utils.recipe_check import check_recipe

REPO = Path(__file__).resolve().parents[2]

CATALOGS = {
    "actions": {"polars_join": {"context": ["assembly"], "params": {
        "right_ingredient": {"widget": "string", "required": True}, "how": {"widget": "enum", "options": ["left", "inner"], "required": True},
        "on": {"widget": "string", "required": False}, "left_on": {"widget": "string", "required": False}, "right_on": {"widget": "string", "required": False}}}},
    "components": {"geom_col"}, "component_arguments": {"geom_col": {"fill", "color"}}, "themes": {"theme_bw"}, "old_action_names": {},
}


def valid():
    """A small recipe that passes the check: one change per case."""
    def table(sid):
        return {"ui_label": sid, "description": "One row per sample.", "source": {"type": "local_tsv", "path": f"assets/test_data/{sid}.tsv"},
                "null_values": [], "strip": True,
                "input_fields": {"id": {"type": "String", "is_entity_id": True, "ui_label": "Id"}, "v": {"type": "Float64", "ui_label": "Value"}},
                "tier1": {"steps": []}}
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"ui_label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {"A": table("a"), "B": table("b")},
        "joins": {"AB": {"ui_label": "AB", "description": "One row per sample, A with B.",
                         "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                         "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]}}},
        "analysis_groups": {"g": {"ui_label": "G", "description": "Question.", "plots": {
            "p": {"ui_label": "P", "description": "Drawn.", "target_dataset": "AB", "mapping": {"x": "id", "y": "v"}, "layers": [{"name": "geom_col"}]}}}},
    }


def check(raw):
    return check_recipe(raw, "run", catalogs=CATALOGS, file_stem="r")


def problems(raw):
    return [(p.code, p.severity, p.path, p.message, p.fix) for p in check(raw).problems]


def with_(change):
    raw = valid()
    change(raw)
    return raw


# -- the recipe check: ui_label everywhere, every old name refused with the new name ------------------------------------------

def test_the_valid_recipe_of_the_names_pass_has_no_problem():
    assert problems(valid()) == []


OLD_NAMES = [
    ("info.label", lambda r: r["info"].update(label="x"), "I03", "info.label"),
    ("info.name", lambda r: r["info"].update(name="x"), "I03", "info.name"),
    ("info.display_name", lambda r: r["info"].update(display_name="x"), "I03", "info.display_name"),
    ("info.ui_title", lambda r: r["info"].update(ui_title="x"), "I03", "info.ui_title"),
    ("schema label", lambda r: r["data_schemas"]["A"].update(label="x"), "S01", "data_schemas.A.label"),
    ("join label", lambda r: r["joins"]["AB"].update(label="x"), "J01", "joins.AB.label"),
    ("input field label", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(label="x"), "FD01", "input_fields.v.label"),
    ("group label", lambda r: r["analysis_groups"]["g"].update(label="x"), "G01", "analysis_groups.g.label"),
    ("group ui_title", lambda r: r["analysis_groups"]["g"].update(ui_title="x"), "G01", "analysis_groups.g.ui_title"),
    ("plot label", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(label="x"), "P01", "plots.p.label"),
    ("plot ui_title", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(ui_title="x"), "P01", "plots.p.ui_title"),
]


@pytest.mark.parametrize("name, change, code, path", OLD_NAMES, ids=[o[0] for o in OLD_NAMES])
def test_an_old_name_is_refused_and_the_new_name_is_told(name, change, code, path):
    found = [p for p in problems(with_(change)) if p[0] == code and p[2].endswith(path)]
    assert found, (name, problems(with_(change)))
    code_, severity, _, message, fix = found[0]
    assert severity == "E"
    assert "ui_label" in (message + fix), (name, message, fix)


def test_the_old_name_at_the_top_of_a_recipe_is_told_as_info_ui_label():
    found = [p for p in problems(with_(lambda r: r.update(name="x"))) if p[0] == "T03"]
    assert found and "info.ui_label" in found[0][4]


def test_a_table_or_a_join_without_a_name_is_refused():
    assert any(p[0] == "S03" for p in problems(with_(lambda r: r["data_schemas"]["A"].pop("ui_label"))))
    assert any(p[0] == "J02" for p in problems(with_(lambda r: r["joins"]["AB"].pop("ui_label"))))


def test_an_old_label_is_not_also_told_as_missing():
    codes = [p[0] for p in problems(with_(lambda r: (r["data_schemas"]["A"].pop("ui_label"), r["data_schemas"]["A"].update(label="x"))))]
    assert "S01" in codes and "S03" not in codes


def test_a_recipe_without_info_ui_label_gets_an_advice_not_an_error():
    found = problems(with_(lambda r: r["info"].pop("ui_label")))
    assert [(p[0], p[1]) for p in found] == [("I01", "A")]
    assert "file name" in found[0][3]
    assert check(with_(lambda r: r["info"].pop("ui_label"))).ok


def test_an_empty_info_ui_label_gets_the_same_advice():
    assert [(p[0], p[1]) for p in problems(with_(lambda r: r["info"].update(ui_label="")))] == [("I01", "A")]


def test_info_that_is_not_a_mapping_is_still_an_error():
    assert ("I01", "E") in [(p[0], p[1]) for p in problems(with_(lambda r: r.update(info="text")))]


def test_info_subtitle_stays_a_free_key_of_info():
    assert problems(with_(lambda r: r["info"].update(subtitle="a line", study="x"))) == []


def test_a_group_and_a_plot_need_a_ui_label_and_nothing_else_names_them():
    assert any(p[0] == "G01" for p in problems(with_(lambda r: r["analysis_groups"]["g"].pop("ui_label"))))
    assert any(p[0] == "P01" for p in problems(with_(lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("ui_label"))))


# -- the deployment file and the app features file: old keys refused with the new names ---------------------------------------

def test_the_old_banner_keys_of_a_deployment_are_refused_with_the_new_names():
    errors = rk.renamed_deployment_key_errors({"branding": {"banner": {"title": "T", "subtitle": "S", "logo_url": "x"}}}, "dep.yaml")
    text = " ".join(e.problem + " " + e.fix for e in errors)
    assert "'title' was renamed to 'ui_label'" in text and "'subtitle' was renamed to 'description'" in text
    assert len(errors) == 2


def test_the_new_banner_keys_are_not_refused():
    assert rk.renamed_deployment_key_errors({"branding": {"banner": {"ui_label": "T", "description": "S", "logo_url": "x"}}}, "dep.yaml") == []


def test_deployment_name_is_refused_as_removed():
    errors = rk.renamed_deployment_key_errors({"deployment_name": "X"}, "dep.yaml")
    assert len(errors) == 1 and "deployment_name" in errors[0].problem and "removed" in errors[0].problem


@pytest.mark.parametrize("old, new", [("display_name", "ui_label")])
def test_a_renamed_app_features_key_is_refused_with_the_new_name(old, new):
    errors = rk.renamed_app_features_key_errors({old: "x"}, "f.yaml")
    assert len(errors) == 1 and f"renamed to '{new}'" in errors[0].problem


@pytest.mark.parametrize("old", ["name", "persona_id", "ui_title"])
def test_a_removed_app_features_key_is_refused_as_removed(old):
    errors = rk.renamed_app_features_key_errors({old: "x"}, "f.yaml")
    assert len(errors) == 1 and "was removed" in errors[0].problem and old in errors[0].problem


def test_a_shipped_app_features_file_is_not_refused():
    for path in (REPO / "config/app_features").glob("*.yaml"):
        config = yaml.safe_load(path.read_text())
        assert rk.renamed_app_features_key_errors(config, str(path)) == [], path
        assert config.get("ui_label"), path


def test_the_shipped_deployments_are_not_refused():
    for path in (REPO / "config/deployment").glob("*/*.yaml"):
        assert rk.renamed_deployment_key_errors(yaml.safe_load(path.read_text()), str(path)) == [], path


_COUNT = [0]


def _boot(tmp_path, monkeypatch, branding=None, extra=None, features="qa"):
    locations = {}
    for k in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (tmp_path / k).mkdir(exist_ok=True)
        locations[k] = str(tmp_path / k)
    body = {"deployment_type": "filesystem", "default_app_features": features, "locations": locations}
    if branding is not None:
        body["branding"] = branding
    body.update(extra or {})
    _COUNT[0] += 1
    path = tmp_path / f"dep_{_COUNT[0]}.yaml"            # the bootloader caches a deployment by its path: one file per boot
    path.write_text(yaml.safe_dump(body))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(path))
    monkeypatch.delenv("SPARMVET_APP_FEATURES", raising=False)
    monkeypatch.chdir(REPO)
    return Bootloader


def test_the_bootloader_stops_on_an_old_banner_key(tmp_path, monkeypatch):
    boot = _boot(tmp_path, monkeypatch, branding={"banner": {"title": "T"}})
    with pytest.raises(SystemExit):
        boot()


def test_the_bootloader_stops_on_deployment_name(tmp_path, monkeypatch):
    boot = _boot(tmp_path, monkeypatch, extra={"deployment_name": "X"})
    with pytest.raises(SystemExit):
        boot()


# -- the switch of the recipe banner (D-0474) -------------------------------------------------------------------------------------

def test_the_switch_is_true_when_absent_and_follows_the_file(tmp_path, monkeypatch):
    assert _boot(tmp_path, monkeypatch)().show_recipe_name() is True
    assert _boot(tmp_path, monkeypatch, branding={"show_recipe_name": True})().show_recipe_name() is True
    assert _boot(tmp_path, monkeypatch, branding={"show_recipe_name": False})().show_recipe_name() is False


def test_the_switch_must_be_true_or_false(tmp_path, monkeypatch):
    boot = _boot(tmp_path, monkeypatch, branding={"show_recipe_name": "no"})
    with pytest.raises(SystemExit):
        boot()


def test_the_banner_shows_the_ui_label_of_the_recipe():
    assert recipe_banner_title({"ui_label": "My recipe", "subtitle": "a line"}, "r") == "My recipe"


def test_the_banner_does_not_read_info_subtitle_or_the_old_keys():
    assert recipe_banner_title({"subtitle": "a line", "label": "old", "name": "old"}, "file_stem") == "file_stem"


def test_the_banner_names_a_recipe_without_ui_label_by_its_file_name():
    for info in (None, {}, {"ui_label": ""}, {"ui_label": "   "}, "text"):
        assert recipe_banner_title(info, "file_stem") == "file_stem"


def test_the_switch_false_hides_the_banner_whatever_the_recipe_says():
    assert recipe_banner_title({"ui_label": "My recipe"}, "r", show=False) is None
    assert recipe_banner_title(None, "r", show=False) is None


def test_no_banner_when_nothing_can_name_the_recipe():
    assert recipe_banner_title(None, "") is None


# -- the export writes the app features file as "ui_label (file name)" (D-0497) ---------------------------------------------------

def test_the_export_text_for_web_demo_is_the_label_with_the_file_name(monkeypatch):
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(REPO / "config/deployment/demo/web-demo.yaml"))
    monkeypatch.delenv("SPARMVET_APP_FEATURES", raising=False)
    monkeypatch.chdir(REPO)
    b = Bootloader()
    assert b.app_features_label_with_id == "Web Demo (web-demo)" and b.app_features_id == "web-demo"


def _boot_features(monkeypatch, features):
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(REPO / "config/deployment/local/local.yaml"))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", features)
    monkeypatch.setenv("SPARMVET_DATA_ANALYSIS_RECIPE", "1_test_data_ST22_dummy")
    monkeypatch.chdir(REPO)
    return Bootloader()


def test_the_export_text_for_every_shipped_app_features_file(monkeypatch):
    for path in sorted((REPO / "config/app_features").glob("*.yaml")):
        label = yaml.safe_load(path.read_text())["ui_label"]
        b = _boot_features(monkeypatch, path.stem)
        assert b.app_features_label_with_id == f"{label} ({path.stem})", path.stem


def test_a_file_without_ui_label_is_written_by_its_file_name(tmp_path, monkeypatch):
    file = tmp_path / "my_features.yaml"
    config = yaml.safe_load((REPO / "config/app_features/qa.yaml").read_text().replace("!include ", ""))
    config.pop("ui_label")
    config.pop("workspaces", None)
    file.write_text(yaml.safe_dump(config))
    b = _boot_features(monkeypatch, str(file))
    assert b.app_features_label_with_id == "my_features"      # an underscore in the file name is allowed (D-0483)


# -- the export and HOME show the same name (D-0409) ----------------------------------------------------------------------------------

def _demo_raw():
    from app.modules.cache_keys import load_data_analysis_recipe
    return load_data_analysis_recipe(REPO / "config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml").config.raw_config


def test_the_report_names_each_plot_and_each_group_as_home_does():
    from app.handlers.export_handlers import export_plot_groups, plot_report_name
    from app.handlers.home_theater import group_tab_label, plot_tab_label
    raw = _demo_raw()
    groups = export_plot_groups(raw)
    assert [g for g, _ in groups] == [group_tab_label(gid, g) for gid, g in raw["analysis_groups"].items()]
    seen = 0
    for gid, g in raw["analysis_groups"].items():
        for pid, entry in g["plots"].items():
            assert plot_report_name(entry, pid) == plot_tab_label(pid, entry) == entry["ui_label"]
            seen += 1
    assert seen == sum(len(p) for _, p in groups) > 10


def test_the_report_is_built_by_group_and_keeps_an_empty_group():
    from app.handlers.export_handlers import export_plot_groups
    raw = {"analysis_groups": {"a": {"ui_label": "First", "plots": {"p1": {"ui_label": "P one", "mapping": {}}, "gone": {}}},
                               "b": {"ui_label": "Second", "plots": {}}}}
    assert export_plot_groups(raw) == [("First", [("p1", {"ui_label": "P one", "mapping": {}})]), ("Second", [])]


def test_a_recipe_with_no_group_falls_back_to_the_root_plots_without_a_group_name():
    from app.handlers.export_handlers import export_plot_groups
    assert export_plot_groups({"plots": {"p": {"ui_label": "P"}}}) == [(None, [("p", {"ui_label": "P"})])]
    assert export_plot_groups({}) == []


def test_no_name_is_invented_for_a_group_or_a_plot():
    from app.handlers.export_handlers import plot_report_name
    from app.handlers.home_theater import group_tab_label, plot_list_label, plot_tab_label
    entry = {"ui_label": "Real", "description": "a description", "name": "a name", "ui_title": "a title"}
    assert plot_report_name(entry, "some_plot_id") == plot_tab_label("some_plot_id", entry) == plot_list_label("some_plot_id", entry) == "Real"
    assert group_tab_label("g", {"ui_label": "Real", "description": "a description"}) == "Real"
    with pytest.raises(KeyError):                               # no `description`, no id in title case
        group_tab_label("some_group", {"description": "text"})
    with pytest.raises(KeyError):
        plot_tab_label("some_plot_id", {"name": "x"})
    # a plot the recipe does not have (an old audit step) is named by its id as written, not by a text made from it
    assert plot_report_name(None, "some_plot_id") == "some_plot_id"
    assert plot_list_label("some_plot_id", None) == "some_plot_id"


# -- the search: nothing removed is left anywhere ----------------------------------------------------------------------------------------

DATA_ROOTS = ["config", "assets/gallery_data", "app/tests/equality", "assets/template_data_analysis_recipes"]
# files that name an old key on purpose: the refusal tables, the specification (its `renamed` table), the migration tools and the checks of this pass
ON_PURPOSE = {
    "app/modules/renamed_keys.py", "libs/utils/src/utils/recipe_spec.yaml", "libs/utils/src/utils/engine_keys_migration.py",
    "libs/utils/src/utils/recipe_migration.py", "libs/utils/src/utils/contract_migration.py", "libs/utils/src/utils/strict_form_migration.py",
    "assets/scripts/migrate_display_names.py", "assets/scripts/migrate_recipe_engine_keys.py", "assets/scripts/migrate_recipe_format.py",
    "assets/scripts/convert_gallery_examples.py", "app/modules/app_features_validator.py",
}


def _files(roots, suffixes):
    for root in roots:
        base = REPO / root
        if base.exists():
            yield from (p for p in sorted(base.rglob("*")) if p.is_file() and p.suffix in suffixes and "__pycache__" not in p.parts)


def _rel(p):
    return str(p.relative_to(REPO))


def test_no_shipped_yaml_holds_a_removed_key():
    bad = []
    for p in _files(DATA_ROOTS, {".yaml", ".yml"}):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for no, line in enumerate(text.splitlines(), 1):
            code = line.split("#", 1)[0]
            if re.match(r"^\s*(-\s+)?(ui_title|deployment_name|display_name):", code):
                bad.append(f"{_rel(p)}:{no}: {line.strip()}")
    assert not bad, "\n".join(bad[:20])


def test_no_shipped_recipe_names_anything_with_the_old_label_keys():
    bad = []
    for p in _files(["config/data_analysis_recipes", "assets/gallery_data", "app/tests/equality"], {".yaml"}):
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "data_schemas" not in raw:
            continue
        info = raw.get("info") or {}
        bad += [f"{_rel(p)}: info.{k}" for k in ("label", "name", "display_name", "ui_title") if k in info]
        for section in ("data_schemas", "additional_datasets_schemas", "joins"):
            for key, body in (raw.get(section) or {}).items():
                if isinstance(body, dict) and "label" in body:
                    bad.append(f"{_rel(p)}: {section}.{key}.label")
        if isinstance(raw.get("metadata_schema"), dict) and "label" in raw["metadata_schema"]:
            bad.append(f"{_rel(p)}: metadata_schema.label")
        for gid, group in (raw.get("analysis_groups") or {}).items():
            if isinstance(group, dict):
                bad += [f"{_rel(p)}: {gid}.{k}" for k in ("label", "ui_title") if k in group]
                for pid, entry in (group.get("plots") or {}).items():
                    if isinstance(entry, dict):
                        bad += [f"{_rel(p)}: {pid}.{k}" for k in ("label", "ui_title") if k in entry]
    assert not bad, "\n".join(bad[:20])


def test_no_code_reads_or_writes_a_removed_name():
    patterns = {
        "ui_title": re.compile(r"ui_title"),
        "deployment_name": re.compile(r"deployment_name"),
        "get_deployment_name": re.compile(r"get_deployment_name"),
        "display_name key": re.compile(r"""["']display_name["']|\bdisplay_name:"""),
        "app_features_display_name": re.compile(r"app_features_display_name"),
        "info label": re.compile(r"""info\.get\(["']label["']|info\[["']label["']\]|info\.label\b"""),
        "label_keys": re.compile(r"label_keys"),
        "title-case fallback": re.compile(r"""replace\(["']_["'], ["'] ["']\)\.title\(\)"""),
    }
    allowed = {"title-case fallback": {"libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py",
                                       "libs/test_lab/src/test_lab/bootstrapper.py", "libs/test_lab/src/test_lab/scaffolder.py",
                                       "assets/scripts/create_data_analysis_recipe.py", "assets/scripts/SF_create_data_analysis_recipe.py",
                                       "assets/scripts/convert_gallery_examples.py", "libs/utils/src/utils/recipe_factory.py"}}
    bad = []
    for p in list((REPO / "app").rglob("*.py")) + list((REPO / "libs").rglob("*.py")) + list((REPO / "assets/scripts").glob("*.py")):
        rel = _rel(p)
        parts = p.relative_to(REPO).parts
        if rel in ON_PURPOSE or "tests" in parts or "__pycache__" in parts or "build" in parts:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for name, rx in patterns.items():
            if rel in allowed.get(name, ()):
                continue
            for no, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    bad.append(f"{rel}:{no}: [{name}] {line.strip()[:120]}")
    assert not bad, "\n".join(bad[:30])


def test_the_report_has_no_plot_id_in_title_case_fallback():
    text = (REPO / "app/handlers/export_handlers.py").read_text()
    assert '.replace("_", " ").title()' not in text
