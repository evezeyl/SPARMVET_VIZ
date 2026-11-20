"""The audit step type `developer_raw_yaml` is removed (AUDIT-RAWYAML-REMOVE-1, Eve 2026-11-12; removal 2026-11-15).

# @deps
# consumes: app/modules/renamed_keys.py, app/modules/t3_audit_engine.py, app/modules/session_manager.py, app/modules/bundle_importer.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py
# @end_deps

Before: nothing created such a step, but a session file, an imported bundle or an audit list could still hold one. HOME's
table, plot and bundle ignored it and the exported recipe applied it (42 rows against 22, silently). Now every entry point
refuses it with a message that names the step and says the type was removed:

- the audit list of a plot (`audited_frame`: the table, the plot, the bundle, the export check, the filter dialog);
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
from app.modules.session_manager import LegacySessionError, SessionManager
from app.modules.t3_audit_engine import AuditStepError, audited_frame

REMOVED = "developer_" + "raw_yaml"
REPO = Path(__file__).resolve().parents[2]
FRAGMENT = "- action: cast\n  columns: [Year]\n  dtype: String\n"


def removed_node(reason="old fragment", node_id="n9"):
    return {"id": node_id, "node_type": REMOVED, "params": {"yaml_fragment": FRAGMENT}, "reason": reason}


def filter_node():
    return {"id": "f1", "node_type": "filter_row", "params": {"column": "x", "op": "ge", "value": 2}, "reason": "keep high"}


FRAME = pl.LazyFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})


# -- the audit list ---------------------------------------------------------------------------------------------------

def test_an_audit_list_with_the_removed_type_is_refused_and_names_the_step():
    with pytest.raises(AuditStepError) as caught:
        audited_frame(FRAME, [filter_node(), removed_node()], "the_plot")
    text = str(caught.value)
    assert "audit step 2 of the plot 'the_plot'" in text and "n9" in text and 'reason: "old fragment"' in text, text
    assert "was removed" in text and "Fix: remove audit step 2" in text, text
    assert caught.value.pipeline_error is not None and "the_plot" in caught.value.pipeline_error.location


def test_the_removed_type_is_never_ignored_even_as_the_only_step():
    with pytest.raises(AuditStepError, match="audit step 1"):
        audited_frame(FRAME, [removed_node()])


def test_an_inactive_removed_step_is_refused_too_like_in_a_session_file():
    """One rule for the list and the files (round 3, point 2): a switched-off step of a removed type is refused, never applied
    or ignored in one place and refused in another. Nothing creates an inactive step today (contract 12c, F-07)."""
    with pytest.raises(AuditStepError, match="audit step 1"):
        audited_frame(FRAME, [{**removed_node(), "active": False}, filter_node()])


# -- a stored session file and an imported session zip ------------------------------------------------------------------

def _session(tmp_path, steps_by_plot=None, flat=None):
    sm = SessionManager(tmp_path)
    key = "abc123def456:0123456789ab"
    folder = sm.session_dir(key)
    (folder / "assembly.json").write_text(json.dumps({"session_key": key, "data_analysis_recipe_id": "r", "label": "", "schema_version": 3}))
    ghost = {"session_key": key, "saved_at": "2026-11-15T10:00:00", "schema_version": 3,
             "t3_audit_steps_by_plot": steps_by_plot or {}, "t3_audit_steps": flat or []}
    (folder / "t3_20261115_100000.json").write_text(json.dumps(ghost))
    return sm, key


def test_a_session_file_with_the_removed_type_is_refused_when_it_is_read(tmp_path):
    sm, key = _session(tmp_path, {"subtab_p": [filter_node(), removed_node()]})
    with pytest.raises(LegacySessionError, match=r"audit step 2 of the plot 'subtab_p'.*n9.*was removed"):
        sm.list_t3_ghosts(key)


def test_the_flat_list_of_an_old_session_file_is_refused_too(tmp_path):
    sm, key = _session(tmp_path, flat=[removed_node()])
    with pytest.raises(LegacySessionError, match="removed"):
        sm.list_t3_ghosts(key)


def test_the_session_panel_lists_such_a_session_with_the_problem_not_silently(tmp_path):
    sm, key = _session(tmp_path, {"subtab_p": [removed_node()]})
    listed = sm.list_all_sessions()
    assert len(listed) == 1 and "was removed" in listed[0].get("legacy_problem", ""), listed


def test_a_session_file_without_the_type_is_read_as_before(tmp_path):
    sm, key = _session(tmp_path, {"subtab_p": [filter_node()]})
    assert sm.list_t3_ghosts(key)[0]["t3_audit_steps_by_plot"] == {"subtab_p": [filter_node()]}


def test_an_imported_session_zip_with_the_removed_type_is_refused_and_nothing_is_extracted(tmp_path):
    source, key = _session(tmp_path / "from", {"subtab_p": [removed_node()]})
    archive = source.export_session_zip(key)
    target = SessionManager(tmp_path / "to")
    with pytest.raises(LegacySessionError, match="removed"):
        target.import_session_zip(archive)
    assert not list(target.root.glob("*")), "a refused import leaves nothing behind"


# -- an imported bundle ------------------------------------------------------------------------------------------------

def _bundle(steps_yaml: dict | None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("b/effective_run.yaml", yaml.safe_dump({"t3_audit_steps_sha256": "x"}))
        if steps_yaml is not None:
            zf.writestr("b/t3_steps.yaml", yaml.safe_dump(steps_yaml))
    return buf.getvalue()


def test_a_bundle_whose_audit_record_holds_the_removed_type_is_refused_before_anything_is_written():
    record = {"t3_steps": {"p": [{"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"}, {"action": REMOVED, "reason": "old"}]}}
    with pytest.raises(BundleImportError, match=r"audit step 2 of the plot 'p'.*was removed"):
        import_bundle(_bundle(record), bootloader=None)   # bootloader is never reached


def test_a_bundle_without_the_type_goes_on_to_its_own_checks():
    record = {"t3_steps": {"p": [{"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"}]}}
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
    assert REMOVED not in audit_stack._NODE_META and REMOVED not in audit_stack._REASON_REQUIRED
