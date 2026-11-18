"""The rewrite tool of the engine keys (D-0236, D-0237, D-0250 to D-0253, D-0255, D-0258): old recipe shape to the new one.

Each rule is run on a small recipe written to a folder, the files are written like `--apply` does, and the result is judged by
the checker (`check_recipe_file`: no problem at all) and, for the content, by an independent expectation written at the level of
the loaded data (`expected_new`): the tool edits TEXT, the oracle edits the DATA, so a bug in one shows against the other.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_engine_keys_migration.py -q
"""
import copy
import os
import textwrap
from pathlib import Path

import pytest
import yaml

from utils.engine_keys_migration import classify, format_events, migrate, summary
from utils.recipe_loader import check_recipe_file

OLD = """\
id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: R
  description: d
  contact: c
data_schemas:
  A:
    label: A
    description: One row per sample.
    source: {type: local_tsv, path: assets/test_data/a.tsv}
    null_values: []
    strip: true
    input_fields:
      id: {type: String, is_entity_key: true}
      v: {type: Float64, label: A value}
    wrangling:
      tier1: []
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
          theme: theme_bw
          mapping: {x: id}
          layers:
          - {name: geom_col}
"""


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text) if text.startswith("\n") or text.startswith(" ") else text, encoding="utf-8")
    return path


def partial(name):
    return name in ("theme_custom", "theme_legend_position")


def run(paths, apply=True, **kwargs):
    """Plan the rewrite and (like --apply) write it."""
    result = migrate([Path(p) for p in paths], partial_theme=kwargs.pop("partial_theme", partial), **kwargs)
    if apply:
        for path, text in result.texts.items():
            path.write_text(text, encoding="utf-8")
        for path in result.removed:
            path.unlink()
    return result


def read(path):
    return Path(path).read_text(encoding="utf-8")


def errors(path):
    return [(p.code, p.path, p.message) for p in check_recipe_file(path).problems]


def load(path):
    path = Path(os.path.realpath(path))

    class Loader(yaml.SafeLoader):
        pass

    Loader.add_constructor("!include", lambda loader, node: load(path.parent / loader.construct_scalar(node)))
    return yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)


# -- the independent expectation, at the level of the loaded data --------------------------------------------------------------------

DEAD = ("default_font_family", "facet_panel_spacing", "legend_position", "optimisation")


def _complete(name):
    return isinstance(name, str) and name.startswith("theme_") and not partial(name)


def _has_complete(content):
    return isinstance(content, dict) and (_complete(content.get("theme")) or any(
        isinstance(layer, dict) and _complete(layer.get("name")) for layer in content.get("layers") or []))


def expected_new(old: dict) -> dict:
    new = copy.deepcopy(old)

    def tiers(container, names):
        return {k: {"steps": container[k] if container[k] is not None else []} for k in names if k in container}

    for section in ("data_schemas", "additional_datasets_schemas"):
        for table in (new.get(section) or {}).values():
            table.update(tiers(table.pop("wrangling", None) or {}, ("tier1", "tier2")))
            table.setdefault("tier1", {"steps": []})
    for join in (new.get("joins") or {}).values():
        join.update(tiers(join.pop("steps", None) or {}, ("tier1", "tier2")))
        join.setdefault("tier1", {"steps": []})
    for group in (new.get("analysis_groups") or {}).values():
        group["ui_label"] = group.pop("label")
        for pid, entry in group["plots"].items():
            plot = {}
            for key in ("plot_engine", "description", "comment", "taxonomy"):
                if key in entry:
                    plot[key] = entry[key]
            plot["ui_label"] = entry["label"]
            content = copy.deepcopy(entry.get("spec") or {})
            title = content.pop("title", None)
            plot.update(content)
            if title is not None:
                layers = plot.setdefault("layers", [])
                labs = [layer for layer in layers if layer.get("name") == "labs"]
                if labs:
                    labs[-1].setdefault("params", {})["title"] = title
                else:
                    layers.append({"name": "labs", "params": {"title": title}})
                plot["ui_title"] = title
            for container, tier in (entry.get("steps") or {}).items():
                plot[container] = {"steps": tier or []}
            group["plots"][pid] = plot
    for key in DEAD:
        (new.get("plot_defaults") or {}).pop(key, None)
    plots = [p for g in (new.get("analysis_groups") or {}).values() for p in g["plots"].values()]
    if any(not _has_complete(p) for p in plots) and not _has_complete(new.get("plot_defaults")):
        new.setdefault("plot_defaults", {})["theme"] = "theme_bw"
    if "plot_defaults" in new and not new["plot_defaults"]:
        del new["plot_defaults"]
    return new


def check_equals_oracle(path_before_text, path):
    """`path_before_text` is the old text written somewhere else; the migrated `path` must equal the oracle of it."""
    assert load(path) == expected_new(path_before_text)


# -- a. the tiers ---------------------------------------------------------------------------------------------------------------------

def test_a_table_wrangling_with_two_tiers_becomes_two_tier_keys(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", """\
    wrangling:
      # strip first
      tier1:
      - {action: polars_filter, predicate: "pl.col('v') > 0"}   # why
      tier2:
      - {action: polars_sort, by: [id]}
""")
    path = write(tmp_path / "r.yaml", text)
    old = yaml.safe_load(text)
    result = run([path])
    new = read(path)
    assert "wrangling" not in new
    assert "    tier1:\n      steps:\n      - {action: polars_filter" in new
    assert "    tier2:\n      steps:\n      - {action: polars_sort" in new
    assert "# strip first" in new and "# why" in new                                   # comments stay
    assert errors(path) == []
    assert load(path) == expected_new(old)
    assert any(e.kind == "tier" and "wrangling" in e.detail for e in result.events)


def test_a_flow_wrangling_and_an_empty_tier_become_tier_keys(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling: {tier1: [], tier2: [{action: polars_sort, by: [id]}]}\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert "    tier1: {steps: []}\n    tier2: {steps: [{action: polars_sort, by: [id]}]}\n" in new
    assert errors(path) == []
    assert load(path) == expected_new(yaml.safe_load(text))


def test_a_tier_with_only_a_comment_below_it_becomes_an_empty_steps_list(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling:\n      tier1:\n      # removed: nothing to do\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert "    tier1:\n      steps: []\n      # removed: nothing to do\n" in new
    assert errors(path) == []


def test_a_table_with_no_wrangling_gets_an_empty_tier1_because_a_tier1_is_required(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert "    tier1: {steps: []}\n" in read(path)
    assert errors(path) == []
    assert any(e.kind == "tier1_added" for e in result.events)


def test_a_wrangling_with_only_tier2_gets_an_empty_tier1_and_says_so(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling:\n      tier2:\n      - {action: polars_sort, by: [id]}\n")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    new = read(path)
    assert "    tier1: {steps: []}\n    tier2:\n      steps:\n" in new
    assert errors(path) == []
    assert any(e.kind == "tier1_added" for e in result.events)


JOIN_OLD = OLD.replace("analysis_groups:", """\
joins:
  J:
    label: J
    description: all of A
    ingredients:
    - dataset_id: A
    steps:
      tier1:
      - {action: polars_select, columns: [id, v]}
analysis_groups:""").replace("target_dataset: A", "target_dataset: J")


def test_a_join_steps_container_becomes_tier_keys(tmp_path):
    path = write(tmp_path / "r.yaml", JOIN_OLD)
    run([path])
    new = read(path)
    assert "\n    steps:" not in new and "    tier1:\n      steps:\n      - {action: polars_select" in new
    assert errors(path) == []
    assert load(path) == expected_new(yaml.safe_load(JOIN_OLD))


def test_a_plot_entry_steps_container_becomes_tier3(tmp_path):
    text = OLD.replace("        spec:\n", "        steps:\n          tier3:\n          - {action: polars_sort, by: [id]}\n        spec:\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert "        tier3:\n          steps:\n          - {action: polars_sort" in new
    assert "steps:\n          tier3" not in new
    assert load(path) == expected_new(yaml.safe_load(text))
    assert [e for e in errors(path) if e[0] != "P05"] == []                      # P05: the engine does not read tier3 yet (a rule of the checker)


def test_an_empty_tier3_container_is_dropped_with_a_note(tmp_path):
    text = OLD.replace("        spec:\n", "        steps: {}\n        spec:\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "tier3" not in read(path) and "steps: {}" not in read(path)


# included tier fragments

FRAG_OLD = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling: !include r/A_wrangling.yaml\n")


def test_a_fragment_with_one_tier_keeps_its_file_name_and_its_root_key_becomes_steps(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "# the steps of A\ntier1:\n- {action: polars_sort, by: [id]}   # sorted\n")
    path = write(tmp_path / "r.yaml", FRAG_OLD)
    result = run([path])
    assert read(tmp_path / "r" / "A_wrangling.yaml") == "# the steps of A\nsteps:\n- {action: polars_sort, by: [id]}   # sorted\n"
    assert "    tier1: !include r/A_wrangling.yaml\n" in read(path) and "\n    wrangling:" not in read(path)
    assert errors(path) == []
    assert result.created == [] and result.removed == []


def test_a_fragment_with_two_tiers_is_split_into_two_files_and_the_old_file_is_removed(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "# first\ntier1:\n- {action: polars_sort, by: [id]}\n\n# then\ntier2:\n- {action: polars_sort, by: [v]}\n")
    path = write(tmp_path / "r.yaml", FRAG_OLD)
    result = run([path])
    one, two = tmp_path / "r" / "A_wrangling_tier1.yaml", tmp_path / "r" / "A_wrangling_tier2.yaml"
    assert read(one) == "# first\nsteps:\n- {action: polars_sort, by: [id]}\n"
    assert read(two) == "\n# then\nsteps:\n- {action: polars_sort, by: [v]}\n"
    assert not (tmp_path / "r" / "A_wrangling.yaml").exists()
    new = read(path)
    assert "    tier1: !include r/A_wrangling_tier1.yaml\n    tier2: !include r/A_wrangling_tier2.yaml\n" in new
    assert errors(path) == []
    assert sorted(p.name for p in result.created) == ["A_wrangling_tier1.yaml", "A_wrangling_tier2.yaml"]
    assert [p.name for p in result.removed] == ["A_wrangling.yaml"]
    assert any("split" in e.detail and "provisional" in e.detail for e in result.events)


def test_a_fragment_shared_by_two_recipes_is_rewritten_once_and_both_includers_follow(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier1:\n- {action: polars_sort, by: [id]}\ntier2:\n- {action: polars_sort, by: [v]}\n")
    first = write(tmp_path / "r.yaml", FRAG_OLD)
    second = write(tmp_path / "s.yaml", FRAG_OLD.replace("id: r\n", "id: s\n"))
    result = run([tmp_path])
    for path in (first, second):
        assert "    tier1: !include r/A_wrangling_tier1.yaml\n    tier2: !include r/A_wrangling_tier2.yaml\n" in read(path)
    assert errors(first) == [] and errors(second) == []
    assert len([p for p in result.created if p.name.startswith("A_wrangling_tier")]) == 2          # not four
    assert len(result.removed) == 1


def test_a_quoted_include_keeps_its_quotes_and_a_folder_in_its_path(tmp_path):
    write(tmp_path / "r dir" / "A wrangling.yaml", "tier1: []\n")
    path = write(tmp_path / "r.yaml", OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling: !include 'r dir/A wrangling.yaml'\n"))
    run([path])
    assert "    tier1: !include 'r dir/A wrangling.yaml'\n" in read(path)


def test_a_fragment_with_only_tier2_gets_an_empty_tier1_in_the_includer(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier2:\n- {action: polars_sort, by: [id]}\n")
    path = write(tmp_path / "r.yaml", FRAG_OLD)
    run([path])
    assert "    tier1: {steps: []}\n    tier2: !include r/A_wrangling.yaml\n" in read(path)
    assert read(tmp_path / "r" / "A_wrangling.yaml") == "steps:\n- {action: polars_sort, by: [id]}\n"
    assert errors(path) == []


def test_a_join_steps_fragment_with_two_tiers_is_split_like_a_table_fragment(tmp_path):
    write(tmp_path / "r" / "J_steps.yaml", "tier1:\n- {action: polars_select, columns: [id, v]}\ntier2:\n- {action: polars_sort, by: [id]}\n")
    text = JOIN_OLD.replace("    steps:\n      tier1:\n      - {action: polars_select, columns: [id, v]}\n", "    steps: !include r/J_steps.yaml\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "    tier1: !include r/J_steps_tier1.yaml\n    tier2: !include r/J_steps_tier2.yaml\n" in read(path)
    assert errors(path) == []


def test_a_missing_fragment_is_refused_with_a_plain_message_and_the_recipe_is_unchanged_there(tmp_path):
    path = write(tmp_path / "r.yaml", FRAG_OLD)
    result = run([path])
    assert "was not found" in result.refused[0].detail and "wrangling: !include r/A_wrangling.yaml" in read(path)


def test_a_fragment_with_a_foreign_key_is_refused_and_nothing_is_written_for_it(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier1: []\nextra: 1\n")
    path = write(tmp_path / "r.yaml", FRAG_OLD)
    result = run([path])
    assert result.refused and "not only tiers" in result.refused[0].detail
    assert read(tmp_path / "r" / "A_wrangling.yaml") == "tier1: []\nextra: 1\n"
    assert not (tmp_path / "r" / "A_wrangling_tier1.yaml").exists()


# -- b. the plot entry ----------------------------------------------------------------------------------------------------------------

def test_an_inline_spec_is_removed_and_the_content_is_written_in_the_entry_in_the_decided_order(tmp_path):
    text = OLD.replace("        spec:\n", "        comment: why\n        taxonomy: {family: Ranking}\n        spec:\n  ".replace("  ", "", 1) if False else
                       "        # about the content\n        comment: why\n        taxonomy: {family: Ranking}\n        spec:\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert "spec:" not in new
    entry = new[new.index("      p:\n"):]
    order = [entry.index(key) for key in ("ui_label:", "description:", "comment:", "taxonomy:", "target_dataset:", "theme:", "mapping:", "layers:")]
    assert order == sorted(order)
    assert "        # about the content\n" in new                                         # the comment stays
    assert load(path) == expected_new(yaml.safe_load(text))
    assert errors(path) == []


def test_a_plot_whose_spec_is_in_its_own_file_moves_the_whole_entry_into_that_file(tmp_path):
    write(tmp_path / "r" / "plots" / "p.yaml", "# the plot\ntarget_dataset: A\ntheme: theme_bw\nmapping: {x: id}\nlayers:\n- {name: geom_col}\n")
    text = OLD.replace("""        spec:
          target_dataset: A
          theme: theme_bw
          mapping: {x: id}
          layers:
          - {name: geom_col}
""", "        spec: !include r/plots/p.yaml\n")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert "      p: !include r/plots/p.yaml\n" in read(path) and "label:" not in read(path).split("analysis_groups:")[1].replace("ui_label", "")
    assert read(tmp_path / "r" / "plots" / "p.yaml") == ("ui_label: P\ndescription: d\n# the plot\ntarget_dataset: A\ntheme: theme_bw\n"
                                                         "mapping: {x: id}\nlayers:\n- {name: geom_col}\n")
    assert errors(path) == []
    assert any(e.kind == "plot_file" for e in result.events)
    # the unchanged data of the plot is the same, written in the file
    assert load(path) == expected_new(yaml.safe_load(OLD))


def test_a_plot_file_that_still_has_its_spec_root_is_unwrapped(tmp_path):
    write(tmp_path / "r" / "plots" / "p.yaml", "spec:\n  target_dataset: A\n  theme: theme_bw\n  mapping: {x: id}\n  layers:\n  - {name: geom_col}\n")
    text = OLD.replace("""        spec:
          target_dataset: A
          theme: theme_bw
          mapping: {x: id}
          layers:
          - {name: geom_col}
""", "        spec: !include r/plots/p.yaml\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert read(tmp_path / "r" / "plots" / "p.yaml").startswith("ui_label: P\ndescription: d\ntarget_dataset: A\n")
    assert errors(path) == []


def test_a_plot_file_used_by_two_entries_is_refused_for_the_second_and_nothing_breaks_silently(tmp_path):
    write(tmp_path / "r" / "plots" / "p.yaml", "target_dataset: A\ntheme: theme_bw\nmapping: {x: id}\nlayers:\n- {name: geom_col}\n")
    two = OLD.replace("""        spec:
          target_dataset: A
          theme: theme_bw
          mapping: {x: id}
          layers:
          - {name: geom_col}
""", "        spec: !include r/plots/p.yaml\n      q:\n        label: Q\n        description: d\n        spec: !include r/plots/p.yaml\n")
    path = write(tmp_path / "r.yaml", two)
    result = run([path])
    assert len(result.refused) == 1 and "also the content of another plot entry" in result.refused[0].detail
    assert "        spec: !include r/plots/p.yaml\n" in read(path)                       # the second entry is left as it was


def test_a_plot_entry_written_on_one_line_is_refused(tmp_path):
    text = OLD.split("    plots:\n")[0] + "    plots:\n      p: {label: P, spec: {target_dataset: A}}\n"
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert result.refused and "written on one line" in result.refused[0].detail


# -- c. names -------------------------------------------------------------------------------------------------------------------------

def test_label_becomes_ui_label_at_groups_and_plot_entries_only(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    run([path])
    new = read(path)
    assert "    ui_label: G\n" in new and "        ui_label: P\n" in new
    assert "info:\n  label: R\n" in new and "  A:\n    label: A\n" in new and "      v: {type: Float64, label: A value}" in new   # pending: unchanged


def test_the_pending_places_follow_the_label_keys_table_so_her_answer_is_a_one_line_change(tmp_path):
    write(tmp_path / "r" / "fields.yaml", "id: {type: String, is_entity_key: true}\nv: {type: Float64, label: A value}\n")
    text = JOIN_OLD.replace("""    input_fields:
      id: {type: String, is_entity_key: true}
      v: {type: Float64, label: A value}
""", "    input_fields: !include r/fields.yaml\n")
    path = write(tmp_path / "r.yaml", text)
    run([path], label_keys={"info": "ui_label", "schema": "ui_label", "join": "ui_label", "field": "ui_label"})
    new = read(path)
    assert "info:\n  ui_label: R\n" in new and "  A:\n    ui_label: A\n" in new and "  J:\n    ui_label: J\n" in new
    assert read(tmp_path / "r" / "fields.yaml") == "id: {type: String, is_entity_key: true}\nv: {type: Float64, ui_label: A value}\n"


def test_only_the_places_the_table_names_are_renamed(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    run([path], label_keys={"info": "ui_label", "schema": "label", "join": "label", "field": "label"})
    new = read(path)
    assert "info:\n  ui_label: R\n" in new and "  A:\n    label: A\n" in new


def test_inline_fields_are_renamed_when_the_table_says_so(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    run([path], label_keys={"info": "label", "schema": "label", "join": "label", "field": "ui_label"})
    assert "      v: {type: Float64, ui_label: A value}" in read(path)


# -- d. the old title -----------------------------------------------------------------------------------------------------------------

TITLE_OLD = OLD.replace("          target_dataset: A\n", "          target_dataset: A\n          title: Reads per sample\n")


def test_a_title_without_a_labs_layer_adds_one_and_writes_ui_title(tmp_path):
    path = write(tmp_path / "r.yaml", TITLE_OLD)
    result = run([path])
    new = read(path)
    assert "        ui_title: Reads per sample\n" in new and "title: Reads per sample\n    " not in new.replace("ui_title: Reads per sample\n", "")
    assert "        - name: labs\n          params:\n            title: Reads per sample\n" in new
    assert load(path) == expected_new(yaml.safe_load(TITLE_OLD))
    assert errors(path) == []
    assert any(e.kind == "title" and "a labs layer was added" in e.detail for e in result.events)


def test_a_title_with_a_labs_layer_without_title_extends_that_layer(tmp_path):
    text = TITLE_OLD.replace("          - {name: geom_col}\n", "          - {name: geom_col}\n          - name: labs\n            params:\n              x: Sample\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert new.count("name: labs") == 1
    assert "            title: Reads per sample\n            x: Sample\n" in new
    assert load(path) == expected_new(yaml.safe_load(text))
    assert errors(path) == []


def test_a_labs_layer_in_flow_style_gets_the_title_inside_its_braces(tmp_path):
    text = TITLE_OLD.replace("          - {name: geom_col}\n", "          - {name: geom_col}\n          - {name: labs, params: {x: Sample, y: Count}}\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert load(path) == expected_new(yaml.safe_load(text))
    assert errors(path) == []


def test_a_labs_layer_with_other_title_is_replaced_because_the_root_title_is_what_is_drawn_today(tmp_path):
    text = TITLE_OLD.replace("          - {name: geom_col}\n", "          - {name: geom_col}\n          - name: labs\n            params:\n              title: Old labs title\n              x: Sample\n")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    new = read(path)
    assert "Old labs title" not in new
    assert "            title: Reads per sample\n            x: Sample\n" in new
    assert any("Old labs title" in e.detail and "replaced" in e.detail for e in result.events)           # the removed text is printed
    assert load(path) == expected_new(yaml.safe_load(text))


def test_a_quoted_title_keeps_its_quotes_and_a_title_with_a_colon_is_safe(tmp_path):
    text = TITLE_OLD.replace("title: Reads per sample", 'title: "QA: reads, per sample"')
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert load(path)["analysis_groups"]["g"]["plots"]["p"]["ui_title"] == "QA: reads, per sample"
    assert errors(path) == []


def test_a_title_in_a_plot_file_is_moved_in_the_file(tmp_path):
    write(tmp_path / "r" / "p.yaml", "title: Reads per sample\ntarget_dataset: A\ntheme: theme_bw\nmapping: {x: id}\nlayers:\n- {name: geom_col}\n")
    text = OLD.split("        spec:\n")[0] + "        spec: !include r/p.yaml\n"
    path = write(tmp_path / "r.yaml", text)
    run([path])
    content = read(tmp_path / "r" / "p.yaml")
    assert content.startswith("ui_label: P\nui_title: Reads per sample\ndescription: d\n")
    assert "title: Reads per sample\ntarget" not in content and "name: labs" in content
    assert errors(path) == []


def test_a_title_cannot_replace_a_labs_layer_of_plot_defaults_and_is_refused(tmp_path):
    text = TITLE_OLD.replace("analysis_groups:", "plot_defaults:\n  layers:\n  - name: labs\n    params: {x: X}\nanalysis_groups:", 1)
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert result.refused and "would replace it" in result.refused[0].detail
    assert "title: Reads per sample" in read(path)


def test_a_title_with_no_layers_list_is_refused_not_lost(tmp_path):
    text = TITLE_OLD.replace("          layers:\n          - {name: geom_col}\n", "          layers: []\n")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert result.refused and "title" in read(path)


# -- e. plot_defaults ------------------------------------------------------------------------------------------------------------------

def with_defaults(block, base=OLD):
    return base.replace("analysis_groups:", block + "analysis_groups:", 1)


def test_the_four_dead_keys_are_removed_and_every_old_value_is_printed(tmp_path):
    block = ("plot_defaults:\n  default_font_family: Liberation Sans\n  facet_panel_spacing: 0.2\n  legend_position: top\n"
             "  optimisation: {auto_axis_text: false}\n  palette: viridis\n  theme: theme_bw\n")
    path = write(tmp_path / "r.yaml", with_defaults(block))
    result = run([path])
    new = read(path)
    for key in ("default_font_family", "facet_panel_spacing", "legend_position", "optimisation"):
        assert key not in new
    assert "plot_defaults:\n  palette: viridis\n  theme: theme_bw\n" in new
    lines = " | ".join(e.detail for e in result.events if e.kind == "removed_key")
    assert "default_font_family removed (old value Liberation Sans) in recipe r" in lines
    assert "facet_panel_spacing removed (old value 0.2)" in lines and "legend_position removed (old value top)" in lines
    assert "optimisation removed (old value {auto_axis_text: false})" in lines
    assert errors(path) == []


def test_a_plot_defaults_block_that_held_only_dead_keys_is_removed_and_the_font_is_not_turned_into_a_theme(tmp_path):
    block = "plot_defaults:\n  default_font_family: \"Liberation Sans\"\n\n"
    text = OLD.replace("          theme: theme_bw\n", "")
    path = write(tmp_path / "r.yaml", with_defaults(block, text))
    run([path])
    new = read(path)
    assert "Liberation" not in new and "default_font_family" not in new
    assert "plot_defaults:\n  theme: theme_bw\n" in new                                  # the theme rule, not the font
    assert errors(path) == []


def test_a_block_with_only_dead_keys_and_a_plot_theme_disappears(tmp_path):
    block = "plot_defaults:\n  default_font_family: Arial\n"
    path = write(tmp_path / "r.yaml", with_defaults(block))
    run([path])
    assert "plot_defaults" not in read(path) and errors(path) == []


# -- f. the theme ---------------------------------------------------------------------------------------------------------------------

NO_THEME = OLD.replace("          theme: theme_bw\n", "")


def test_a_recipe_with_no_theme_gets_theme_bw_once_in_plot_defaults_and_the_plots_are_listed(tmp_path):
    path = write(tmp_path / "r.yaml", NO_THEME)
    result = run([path])
    new = read(path)
    assert "plot_defaults:\n  theme: theme_bw\n\nanalysis_groups:" in new
    event = [e for e in result.events if e.kind == "theme"]
    assert len(event) == 1 and "recipe r" in event[0].detail and "p" in event[0].detail
    assert load(path) == expected_new(yaml.safe_load(NO_THEME))
    assert errors(path) == []


def test_a_recipe_whose_plots_all_name_a_theme_gets_none(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    result = run([path])
    assert "plot_defaults" not in read(path) and not [e for e in result.events if e.kind == "theme"]


def test_a_recipe_with_a_theme_in_plot_defaults_gets_none_and_keeps_it(tmp_path):
    path = write(tmp_path / "r.yaml", with_defaults("plot_defaults:\n  theme: theme_minimal\n", NO_THEME))
    run([path])
    assert "theme: theme_minimal" in read(path) and "theme_bw" not in read(path)


def test_a_theme_in_one_plot_only_still_gets_the_default_for_the_other_plot(tmp_path):
    two = OLD.replace("    plots:\n      p:", "    plots:\n      q:\n        label: Q\n        description: d\n        spec:\n          target_dataset: A\n          mapping: {x: id}\n          layers:\n          - {name: geom_col}\n      p:")
    path = write(tmp_path / "r.yaml", two)
    result = run([path])
    new = read(path)
    assert "plot_defaults:\n  theme: theme_bw\n" in new and new.count("theme: theme_bw") == 2        # one default, one in plot p (wins over it)
    assert [e for e in result.events if e.kind == "theme"][0].detail.count("q") >= 1 and "p)" not in [e for e in result.events if e.kind == "theme"][0].detail
    assert load(path) == expected_new(yaml.safe_load(two))


def test_only_a_partial_theme_layer_does_not_count_as_a_theme_because_the_base_still_comes_from_the_built_in(tmp_path):
    text = NO_THEME.replace("          layers:\n          - {name: geom_col}\n", "          layers:\n          - {name: geom_col}\n          - {name: theme_custom, params: {}}\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "plot_defaults:\n  theme: theme_bw\n" in read(path)
    # the same layer judged as a COMPLETE theme (a different registry answer) needs no default
    path2 = write(tmp_path / "s.yaml", text.replace("id: r", "id: s"))
    result = run([path2], partial_theme=lambda name: False)
    assert "plot_defaults" not in read(path2) and not [e for e in result.events if e.kind == "theme"]


def test_a_complete_theme_layer_in_the_layers_counts_as_a_theme(tmp_path):
    text = NO_THEME.replace("          layers:\n          - {name: geom_col}\n", "          layers:\n          - {name: geom_col}\n          - {name: theme_minimal, params: {}}\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "plot_defaults" not in read(path)


def test_the_theme_line_goes_above_the_comment_that_belongs_to_analysis_groups(tmp_path):
    text = NO_THEME.replace("analysis_groups:", "# the plots\nanalysis_groups:")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "plot_defaults:\n  theme: theme_bw\n\n# the plots\nanalysis_groups:" in read(path)


def test_a_plot_defaults_block_with_other_keys_gets_the_theme_as_its_first_line(tmp_path):
    path = write(tmp_path / "r.yaml", with_defaults("plot_defaults:\n  palette: viridis\n", NO_THEME))
    run([path])
    assert "plot_defaults:\n  theme: theme_bw\n  palette: viridis\n" in read(path)


# -- the whole run: twice, byte for byte, kinds, refusals, modes -----------------------------------------------------------------------------

def test_a_second_run_changes_nothing_and_says_so(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier1:\n- {action: polars_sort, by: [id]}\ntier2:\n- {action: polars_sort, by: [v]}\n")
    write(tmp_path / "r" / "p.yaml", "title: T\ntarget_dataset: A\nmapping: {x: id}\nlayers:\n- {name: geom_col}\n")
    text = (JOIN_OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling: !include r/A_wrangling.yaml\n")
            .replace("""        spec:
          target_dataset: J
          theme: theme_bw
          mapping: {x: id}
          layers:
          - {name: geom_col}
""", "        spec: !include r/p.yaml\n"))
    path = write(tmp_path / "r.yaml", text)
    first = run([path])
    assert first.would_change
    snapshot = {p: p.read_bytes() for p in tmp_path.rglob("*.yaml")}
    second = run([tmp_path])
    assert not second.would_change and second.events == [] and second.texts == {} and second.removed == []
    assert {p: p.read_bytes() for p in tmp_path.rglob("*.yaml")} == snapshot
    assert errors(path) == []


def test_a_recipe_that_is_already_in_the_new_shape_is_untouched_byte_for_byte(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    run([path])
    migrated = path.read_bytes()
    result = run([path])
    assert result.texts == {} and path.read_bytes() == migrated and not result.would_change


def test_check_mode_writes_nothing(tmp_path):
    path = write(tmp_path / "r.yaml", OLD)
    before = path.read_bytes()
    result = run([path], apply=False)
    assert result.would_change and path.read_bytes() == before
    assert path.resolve() in result.texts                                                    # the plan holds the new text


def test_a_file_with_nothing_to_change_is_not_in_the_plan_even_when_it_is_in_the_folder(tmp_path):
    other = write(tmp_path / "plain.yaml", "just: a file\n")
    write(tmp_path / "r.yaml", OLD)
    result = run([tmp_path], apply=False)
    assert other.resolve() not in result.texts


def test_comments_and_blank_lines_are_kept_everywhere(tmp_path):
    text = OLD.replace("data_schemas:\n", "# the tables\n\ndata_schemas:\n").replace("    plots:\n", "    plots:\n      # the first plot\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    new = read(path)
    assert "# the tables\n\ndata_schemas:" in new and "      # the first plot\n      p:" in new


# lone files and kinds

def test_the_kind_of_a_file_comes_from_its_keys_never_from_a_guess():
    assert classify("id: r\ndata_schemas: {}\n") == "recipe"
    assert classify("tier1: []\ntier2: []\n") == "tier_fragment"
    assert classify("target_dataset: A\nmapping: {}\nlayers: []\n") == "plot_content"
    assert classify("id: {type: String}\nv: {type: Float64}\n") == "input_fields"
    assert classify("hello: world\n") == "unknown" and classify("- a\n- b\n") == "unknown" and classify("a: [\n") == "unknown"


def test_a_lone_file_of_unknown_kind_is_refused_with_a_plain_message_and_not_changed(tmp_path):
    path = write(tmp_path / "x.yaml", "hello: world\nlabel: x\n")
    result = run([path])
    assert result.refused and "cannot be known" in result.refused[0].detail and "nothing changed" in result.refused[0].detail
    assert read(path) == "hello: world\nlabel: x\n" and not result.would_change


@pytest.mark.parametrize("name, text, words", [
    ("frag.yaml", "tier1: []\n", "an old tier fragment"),
    ("plot.yaml", "target_dataset: A\nmapping: {x: id}\nlayers: []\n", "the content of a plot"),
])
def test_a_lone_tier_fragment_or_plot_file_is_refused_because_its_recipe_is_needed(tmp_path, name, text, words):
    path = write(tmp_path / name, text)
    result = run([path])
    assert result.refused and words in result.refused[0].detail and "give that recipe" in result.refused[0].detail
    assert read(path) == text


def test_a_lone_input_fields_file_has_nothing_to_change_and_is_not_a_refusal(tmp_path):
    path = write(tmp_path / "fields.yaml", "id: {type: String}\nv: {type: Float64, label: x}\n")
    result = run([path])
    assert result.refused == [] and not result.would_change


def test_a_fragment_that_no_recipe_in_the_given_folder_includes_is_listed_not_rewritten(tmp_path):
    write(tmp_path / "r.yaml", OLD)
    orphan = write(tmp_path / "old" / "tiers.yaml", "tier1: []\n")
    result = run([tmp_path])
    assert [e.file for e in result.refused] == [orphan.resolve()] and "no recipe in the given paths includes" in result.refused[0].detail
    assert read(orphan) == "tier1: []\n"


def test_a_recipe_that_cannot_be_parsed_is_refused_and_unchanged(tmp_path):
    path = write(tmp_path / "r.yaml", "id: r\ndata_schemas:\n  A: [\n")
    result = run([path])
    assert not result.would_change and read(path) == "id: r\ndata_schemas:\n  A: [\n"


# the independent expectation on a recipe that has every rule at once

EVERYTHING = JOIN_OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling:\n      tier1:\n      - {action: polars_sort, by: [id]}\n").replace(
    "          target_dataset: J\n", "          target_dataset: J\n          title: A title\n").replace(
    "analysis_groups:", "plot_defaults:\n  default_font_family: Arial\n  optimisation: {auto_axis_text: false}\nanalysis_groups:", 1).replace(
    "          theme: theme_bw\n", "")


def test_the_text_rewrite_equals_the_independent_data_level_expectation(tmp_path):
    path = write(tmp_path / "r.yaml", EVERYTHING)
    run([path])
    assert load(path) == expected_new(yaml.safe_load(EVERYTHING))
    assert errors(path) == []


def test_the_summary_counts_every_kind(tmp_path):
    path = write(tmp_path / "r.yaml", EVERYTHING)
    result = run([path], apply=False)
    counts = dict(summary(result))
    assert counts["tier"] == 2 and counts["title"] == 1 and counts["removed_key"] == 2 and counts["theme"] == 1
    assert counts["files changed"] == 1
    assert all(": " in line for line in format_events(result, lambda p: p.name))


# more shapes found in the real recipes

def test_a_block_scalar_description_and_a_file_that_ends_with_a_comment_survive_the_move(tmp_path):
    write(tmp_path / "r" / "p.yaml", "target_dataset: A\ntheme: theme_bw\nmapping: {x: id}\nlayers:\n- {name: geom_col}\n# end of the plot\n")
    text = OLD.replace("        description: d\n        spec:\n", "        description: >-\n          Bars of ids,\n          on two lines.\n        spec: !include r/p.yaml\n", 1)
    text = text.split("        spec: !include r/p.yaml\n")[0] + "        spec: !include r/p.yaml\n"
    path = write(tmp_path / "r.yaml", text)
    run([path])
    moved = read(tmp_path / "r" / "p.yaml")
    assert moved.startswith("ui_label: P\ndescription: >-\n  Bars of ids,\n  on two lines.\ntarget_dataset: A\n") and moved.endswith("# end of the plot\n")
    assert errors(path) == []


def test_two_groups_with_two_plots_keep_their_order_and_each_plot_is_rewritten(tmp_path):
    plot = "{n}:\n        label: {n}\n        description: d\n        spec:\n          target_dataset: A\n          mapping: {{x: id}}\n          layers:\n          - {{name: geom_col}}\n"
    groups = "".join(f"  {g}:\n    label: {g}\n    description: d\n    plots:\n" + "".join("      " + plot.format(n=f"{g}_{i}") for i in (1, 2)) for g in ("g1", "g2"))
    text = OLD.split("analysis_groups:")[0] + "analysis_groups:\n" + groups
    path = write(tmp_path / "r.yaml", text)
    run([path])
    data = load(path)
    assert list(data["analysis_groups"]) == ["g1", "g2"] and list(data["analysis_groups"]["g2"]["plots"]) == ["g2_1", "g2_2"]
    assert data == expected_new(yaml.safe_load(text))
    assert errors(path) == []


def test_a_group_label_is_renamed_even_when_a_plot_of_the_group_is_refused(tmp_path):
    text = OLD.split("    plots:\n")[0] + "    plots:\n      p: {label: P}\n"
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert "    ui_label: G\n" in read(path) and result.refused


def test_a_spec_with_nothing_in_it_leaves_an_entry_with_only_its_names(tmp_path):
    text = OLD.split("        spec:\n")[0] + "        spec:\n"
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "\n        spec:" not in read(path) and "        ui_label: P\n        description: d\n" in read(path)


def test_a_join_with_tier2_in_flow_style_keeps_both_tiers(tmp_path):
    text = JOIN_OLD.replace("    steps:\n      tier1:\n      - {action: polars_select, columns: [id, v]}\n", "    steps: {tier1: [{action: polars_select, columns: [id, v]}], tier2: [{action: polars_sort, by: [id]}]}\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "    tier1: {steps: [{action: polars_select, columns: [id, v]}]}\n    tier2: {steps: [{action: polars_sort, by: [id]}]}\n" in read(path)
    assert load(path) == expected_new(yaml.safe_load(text))


def test_the_container_line_comment_is_kept_as_a_comment_line(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling:   # the cleaning\n      tier1: []\n")
    path = write(tmp_path / "r.yaml", text)
    run([path])
    assert "    # the cleaning\n    tier1:\n      steps: []\n" in read(path)


def test_a_container_that_holds_a_list_is_refused_with_a_plain_message(tmp_path):
    text = OLD.replace("    wrangling:\n      tier1: []\n", "    wrangling:\n    - {action: polars_sort, by: [id]}\n")
    path = write(tmp_path / "r.yaml", text)
    result = run([path])
    assert result.refused and "a list of steps was found" in result.refused[0].detail
    assert "wrangling:" in read(path)


# old tier fragments that no recipe includes

def test_an_orphan_tier_fragment_is_rewritten_on_its_own_only_when_asked(tmp_path):
    write(tmp_path / "r.yaml", OLD)
    orphan = write(tmp_path / "old" / "tiers.yaml", "# kept on purpose\ntier1:\n- {action: polars_sort, by: [id]}\n")
    result = run([tmp_path], apply=False)
    assert result.refused and orphan.resolve() not in result.texts                      # default: listed, left as it was
    result = run([tmp_path], orphan_fragments=True)
    assert read(orphan) == "# kept on purpose\nsteps:\n- {action: polars_sort, by: [id]}\n"
    assert [e for e in result.events if e.kind == "note" and "no recipe in the given paths" in e.detail]
    assert not [e for e in result.refused if e.file == orphan.resolve()]


def test_an_orphan_fragment_with_two_tiers_is_split_when_asked_and_a_foreign_key_still_refuses(tmp_path):
    write(tmp_path / "r.yaml", OLD)
    two = write(tmp_path / "old" / "two.yaml", "tier1: []\ntier2: []\n")
    run([tmp_path], orphan_fragments=True)
    assert not two.exists() and (tmp_path / "old" / "two_tier1.yaml").exists() and (tmp_path / "old" / "two_tier2.yaml").exists()
