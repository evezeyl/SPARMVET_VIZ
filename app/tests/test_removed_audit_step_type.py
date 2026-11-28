"""The audit step type `developer_raw_yaml` is removed (AUDIT-RAWYAML-REMOVE-1, Eve 2026-11-12; removal 2026-11-15).

# @deps
# consumes: app/modules/renamed_keys.py, app/modules/audit_places.py, app/modules/session_manager.py, app/modules/bundle_importer.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py
# @end_deps

Before: nothing created such a step, but a session file, an imported bundle or an audit list could still hold one. HOME's
table, plot and bundle ignored it and the exported recipe applied it (42 rows against 22, silently). Now every entry point
refuses it with a message that names the step and says the type was removed:

- the audit list (`audit_copy_for`: the one entry of the audit copy that the table, the plot, the bundle, the export check and the filter dialog read);
- a stored session file and an imported session zip (`SessionManager`);
- the audit record `t3_steps.yaml` of an imported bundle (`import_bundle`);
- the translator has no branch for it any more (an unknown type like any other);
- and no code path knows the name but the one refusal table (`renamed_keys.py`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_removed_audit_step_type.py -q
"""
import io
import json
import re
import zipfile
from pathlib import Path

import polars as pl
import pytest
import yaml

from app.modules.bundle_importer import BundleImportError, import_bundle
from app.modules.session_manager import SESSION_FORMAT_VERSION, LegacySessionError, SessionManager
from app.modules.audit_places import audit_copy_for, place_nodes
from app.tests.test_audit_places import small
from utils.audit_copy import AuditCopyError

REMOVED = "developer_" + "raw_yaml"
REPO = Path(__file__).resolve().parents[2]
FRAGMENT = "- action: cast\n  columns: [Year]\n  dtype: String\n"


def removed_node(reason="old fragment", node_id="n9"):
    return {"id": node_id, "node_type": REMOVED, "params": {"yaml_fragment": FRAGMENT}, "reason": reason, "place": "T3:P"}


def filter_node():
    return {"id": "f1", "node_type": "filter_row", "params": {"column": "id", "op": "ge", "value": 2}, "reason": "keep high", "place": "T3:P"}


FRAME = pl.LazyFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})


# -- the audit list ---------------------------------------------------------------------------------------------------

def test_an_audit_list_with_the_removed_type_is_refused_and_names_the_step():
    with pytest.raises(AuditCopyError) as caught:
        audit_copy_for(small(), [filter_node(), removed_node()])
    text = str(caught.value)
    assert "The audit step 2" in text and "n9" in text and 'reason: "old fragment"' in text and "at Plot P (tier 3)" in text, text
    assert "was removed" in text and "Fix:" in text and "new session" in text, text


def test_the_removed_type_is_never_ignored_even_as_the_only_step():
    with pytest.raises(AuditCopyError, match="The audit step 1"):
        audit_copy_for(small(), [removed_node()])


def test_an_inactive_removed_step_is_not_run_and_is_refused_where_a_file_is_read():
    """One rule for the files (round 3, point 2): a switched-off step of a removed type is refused when a session file, a session zip or a bundle holds it (below).
    The list the audit runs holds the ACTIVE steps only (`place_nodes`), so an inactive step is never applied or ignored in one place and refused in another by accident:
    it is not a step of the audit. Nothing creates an inactive step today (contract 12c, F-07)."""
    assert place_nodes([{**removed_node(), "active": False}, filter_node()]) == [filter_node()]


# -- a stored session file and an imported session zip ------------------------------------------------------------------

def _session(tmp_path, steps=None):
    sm = SessionManager(tmp_path)
    key = "abc123def456:0123456789ab"
    folder = sm.session_dir(key)
    (folder / "assembly.json").write_text(json.dumps({"session_key": key, "data_analysis_recipe_id": "r", "label": "", "schema_version": SESSION_FORMAT_VERSION}))
    ghost = {"session_key": key, "saved_at": "2026-11-15T10:00:00", "schema_version": SESSION_FORMAT_VERSION,
             "audit_pipeline": steps or []}
    (folder / "t3_20261115_100000.json").write_text(json.dumps(ghost))
    return sm, key


def test_a_session_file_with_the_removed_type_is_refused_when_it_is_read(tmp_path):
    sm, key = _session(tmp_path, [filter_node(), removed_node()])
    with pytest.raises(LegacySessionError, match=r"audit step 2 \(.*n9.*was removed"):
        sm.list_t3_ghosts(key)


def test_the_session_panel_lists_such_a_session_with_the_problem_not_silently(tmp_path):
    sm, key = _session(tmp_path, [removed_node()])
    listed = sm.list_all_sessions()
    assert len(listed) == 1 and "was removed" in listed[0].get("legacy_problem", ""), listed


def test_a_session_file_without_the_type_is_read_as_before(tmp_path):
    sm, key = _session(tmp_path, [filter_node()])
    assert sm.list_t3_ghosts(key)[0]["audit_pipeline"] == [filter_node()]


def test_an_imported_session_zip_with_the_removed_type_is_refused_and_nothing_is_extracted(tmp_path):
    source, key = _session(tmp_path / "from", [removed_node()])
    archive = source.export_session_zip(key)
    target = SessionManager(tmp_path / "to")
    with pytest.raises(LegacySessionError, match="removed"):
        target.import_session_zip(archive)
    assert not list(target.root.glob("*")), "a refused import leaves nothing behind"


# -- an imported bundle ------------------------------------------------------------------------------------------------

def _bundle(steps_yaml: dict | None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("b/effective_run.yaml", yaml.safe_dump({"audit_steps_sha256": "x"}))
        if steps_yaml is not None:
            zf.writestr("b/t3_steps.yaml", yaml.safe_dump(steps_yaml))
    return buf.getvalue()


def test_a_bundle_whose_audit_record_holds_the_removed_type_is_refused_before_anything_is_written():
    record = {"steps_by_place": [{"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"}, {"action": REMOVED, "reason": "old"}]}
    with pytest.raises(BundleImportError, match=r"audit step 2 \(.*was removed"):
        import_bundle(_bundle(record), bootloader=None)   # bootloader is never reached


def test_a_bundle_without_the_type_goes_on_to_its_own_checks():
    record = {"steps_by_place": [{"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"}]}
    with pytest.raises(BundleImportError, match="no reproducibility recipe"):
        import_bundle(_bundle(record), bootloader=None)


# -- the code does not know the type any more ---------------------------------------------------------------------------

def test_no_code_path_knows_the_removed_type_but_the_refusal_table():
    found = []
    for root in ("app", "libs"):
        for path in (REPO / root).rglob("*.py"):
            rel = path.relative_to(REPO).as_posix()
            if "/tests/" in rel or ".venv" in rel or "/build/" in rel or path.name.startswith("test_"):
                continue
            if REMOVED in path.read_text(encoding="utf-8") and rel != "app/modules/renamed_keys.py":
                found.append(rel)
    assert not found, found


def test_the_screens_do_not_offer_or_label_the_removed_type():
    from app.handlers import audit_stack
    assert REMOVED not in audit_stack._NODE_META     # FLOW-3: `_REASON_REQUIRED` is gone with the reason boxes (a reason is asked at Add for every step)


# -- the round trip: what the export writes is what the importer's check reads (B1 of the FLOW-3 review) ------------------

def _real_export_record(steps: list[dict]) -> dict:
    """The `t3_steps.yaml` content as the export builds it: place_step_records -> steps_by_place_yaml, through yaml like a real file."""
    from app.modules.audit_places import place_step_records, steps_by_place_yaml

    class _G:
        def has_node(self, _n):
            return False
    records = place_step_records(_G(), steps)
    return yaml.safe_load(yaml.safe_dump({"steps_by_place": steps_by_place_yaml(records)}))


def _node(kind, params, place="T3:p"):
    return {"id": f"i_{kind}", "node_type": kind, "params": params, "place": place, "reason": "r", "created_at": "2026-11-27", "started_from": "subtab_p"}


def test_the_record_the_export_writes_is_accepted_by_the_importer_check():
    record = _real_export_record([_node("filter_row", {"column": "identity", "op": "ge", "value": 90, "na": "remove"}), _node("drop_column", {"column": "x"}, "T1:t")])
    with pytest.raises(BundleImportError, match="no reproducibility recipe"):     # past the audit check, on to the next one
        import_bundle(_bundle(record), bootloader=None)


def test_an_unknown_step_type_in_the_real_shape_is_still_refused_in_plain_words():
    record = _real_export_record([_node("filter_row", {"column": "a", "op": "ge", "value": 1}), _node("mystery", {"column": "a"})])
    with pytest.raises(BundleImportError, match=r"audit step 2 .*does not know"):
        import_bundle(_bundle(record), bootloader=None)


def test_a_filter_step_without_its_column_in_the_real_shape_is_refused():
    record = _real_export_record([_node("filter_row", {"op": "ge", "value": 1})])
    with pytest.raises(BundleImportError, match="needs the column"):
        import_bundle(_bundle(record), bootloader=None)


# -- a complete bundle with an unknown step: nothing is written anywhere (guardrail row "unknown step type", D-0665) -------------

def _full_bundle(record: dict) -> bytes:
    """A bundle that would import if its audit record were fine: effective_run, the reproducibility recipe and a data file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("b/effective_run.yaml", yaml.safe_dump({"audit_steps_sha256": "x"}))
        zf.writestr("b/t3_steps.yaml", yaml.safe_dump(record))
        zf.writestr("b/data_analysis_recipes_reproducibility/tiny.yaml", yaml.safe_dump({"id": "tiny"}))
        zf.writestr("b/data_reproducibility/t.tsv", "a\tb\n1\t2\n")
    return buf.getvalue()


def test_a_complete_bundle_with_an_unknown_step_type_writes_nothing_to_the_recipes_or_the_import_folders(tmp_path):
    """The whole `import_bundle` path with a real (not unreachable) bootloader: after the refusal both folders are empty.
    MUTATION B1: move the audit-record check in `import_bundle` below the writes and this fails (a file is found)."""
    from types import SimpleNamespace
    recipes, imports = tmp_path / "recipes", tmp_path / "imports"
    recipes.mkdir(); imports.mkdir()
    bootloader = SimpleNamespace(data_analysis_recipes_dir=recipes, get_imports_dir=lambda: imports)
    record = _real_export_record([_node("filter_row", {"column": "a", "op": "ge", "value": 1}), _node("mystery", {"column": "a"})])
    with pytest.raises(BundleImportError, match=r"audit step 2 .*does not know"):
        import_bundle(_full_bundle(record), bootloader=bootloader)
    assert list(recipes.rglob("*")) == [] and list(imports.rglob("*")) == [], "a refused bundle leaves nothing behind"
