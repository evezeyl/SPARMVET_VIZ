"""A step the app cannot apply is refused with a plain message, never skipped in silence (PLOT-TABLE-ORDER-1, review round 3).

# @deps
# consumes: app/modules/renamed_keys.py, app/modules/t3_audit_engine.py, app/modules/session_manager.py, app/modules/bundle_importer.py
# @end_deps

Eve's rule. A step is refused when its type is not one of the known ones (`filter_row`, `exclusion_row`, `drop_column`,
`aesthetic_override`; the seed pin `random_seed` is known to the report and the bundle record), or when it lacks what it needs
to run (the column, the operator, the value). Every entry point refuses it with the step (number, plot, what is missing)
and, first, what the user can do in the app; a maintainer's pointer to the file comes after. Entry points: the audit list
(`audited_frame`), a stored session file, an imported session zip, the `t3_steps.yaml` of an imported bundle.

Decided here (point 2 of the round): a step that is switched off (`active: false`) is refused all the same, in every entry
point. Nothing in the app creates an inactive step today (`ui_implementation_contract.md` 12c, F-07: deletion is real removal),
so such a step can only come from a hand-edited or foreign file; one rule for list and files is the simpler one.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_step_refused_not_skipped.py -q
"""
import io
import json
import zipfile

import polars as pl
import pytest
import yaml

from app.modules.bundle_importer import BundleImportError, import_bundle
from app.modules.session_manager import LegacySessionError, SessionManager
from app.modules.t3_audit_engine import AuditStepError, audit_failures, audited_frame

REMOVED = "developer_" + "raw_yaml"
FRAME = pl.LazyFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})

GOOD_FILTER = {"id": "f1", "node_type": "filter_row", "params": {"column": "x", "op": "ge", "value": 2}, "reason": "keep high"}
BAD_STEPS = {
    "an unknown type": {"id": "u", "node_type": "mystery_step", "params": {"column": "x"}, "reason": "r"},
    "a name like the removed one": {"id": "s", "node_type": REMOVED + "2", "params": {}, "reason": "r"},
    "a filter without a column": {"id": "n", "node_type": "filter_row", "params": {"op": "ge", "value": 2}, "reason": "r"},
    "a filter without an operator": {"id": "o", "node_type": "filter_row", "params": {"column": "x", "value": 2}, "reason": "r"},
    "a filter without a value": {"id": "v", "node_type": "filter_row", "params": {"column": "x", "op": "ge"}, "reason": "r"},
    "an exclusion without a value": {"id": "e", "node_type": "exclusion_row", "params": {"column": "x", "op": "not_in"}, "reason": "r"},
    "a drop without a column": {"id": "d", "node_type": "drop_column", "params": {}, "reason": "r"},
    "a step without a type": {"id": "t", "params": {"column": "x"}, "reason": "r"},
}


# -- the audit list ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(BAD_STEPS))
def test_the_audit_list_refuses_a_step_it_cannot_apply(name):
    with pytest.raises(AuditStepError) as caught:
        audited_frame(FRAME, [GOOD_FILTER, BAD_STEPS[name]], "the_plot")
    text = str(caught.value)
    assert "audit step 2 of the plot 'the_plot'" in text, text
    assert "cannot be applied" in text or "was removed" in text, text
    assert "Fix:" in text and "new session" in text, "the user is told what to do in the app"
    assert caught.value.pipeline_error is not None


def test_the_message_says_what_is_missing():
    with pytest.raises(AuditStepError, match=r"needs the operator"):
        audited_frame(FRAME, [BAD_STEPS["a filter without an operator"]])
    with pytest.raises(AuditStepError, match=r"needs the column"):
        audited_frame(FRAME, [BAD_STEPS["a drop without a column"]])
    with pytest.raises(AuditStepError, match=r"the type 'mystery_step'"):
        audited_frame(FRAME, [BAD_STEPS["an unknown type"]])


def test_a_value_of_zero_or_false_is_a_value():
    step = {"id": "z", "node_type": "filter_row", "params": {"column": "x", "op": "ge", "value": 0}, "reason": "r"}
    assert audited_frame(FRAME, [step]).collect().height == 4


def test_known_steps_pass_and_style_steps_are_not_data_steps():
    style = {"id": "a", "node_type": "aesthetic_override", "params": {"alpha": 0.5}}
    assert audited_frame(FRAME, [style, GOOD_FILTER]).collect().height == 3


def test_a_switched_off_bad_step_is_refused_too_one_rule_everywhere():
    with pytest.raises(AuditStepError, match="audit step 1"):
        audited_frame(FRAME, [{**BAD_STEPS["an unknown type"], "active": False}, GOOD_FILTER])


def test_the_export_check_finds_every_plot_with_a_step_it_cannot_apply():
    failing = audit_failures([("a", lambda: FRAME, [BAD_STEPS["an unknown type"]]), ("ok", lambda: FRAME, [GOOD_FILTER]),
                              ("b", lambda: FRAME, [BAD_STEPS["a drop without a column"]])])
    assert [p for p, _ in failing] == ["a", "b"]


# -- a stored session file and an imported session zip ------------------------------------------------------------------

def _session(tmp_path, steps):
    sm = SessionManager(tmp_path)
    key = "abc123def456:0123456789ab"
    folder = sm.session_dir(key)
    (folder / "assembly.json").write_text(json.dumps({"session_key": key, "data_analysis_recipe_id": "r", "label": ""}))
    ghost = {"session_key": key, "saved_at": "2026-11-15T10:00:00", "tier_toggle": "T3",
             "t3_audit_steps_by_plot": {"subtab_p": steps}, "t3_audit_steps": []}
    (folder / "t3_20261115_100000.json").write_text(json.dumps(ghost))
    return sm, key


@pytest.mark.parametrize("name", sorted(BAD_STEPS))
def test_a_session_file_refuses_a_step_the_app_cannot_apply(tmp_path, name):
    sm, key = _session(tmp_path, [GOOD_FILTER, BAD_STEPS[name]])
    with pytest.raises(LegacySessionError) as caught:
        sm.list_t3_ghosts(key)
    text = str(caught.value)
    assert "audit step 2 of the plot 'subtab_p'" in text, text
    assert text.index("new session") < text.index("t3_audit_steps_by_plot"), "the app action comes first, the maintainer's pointer after"


def test_a_session_file_with_good_steps_is_read(tmp_path):
    sm, key = _session(tmp_path, [GOOD_FILTER, {"id": "a", "node_type": "aesthetic_override", "params": {"alpha": 0.5}}])
    assert len(sm.list_t3_ghosts(key)) == 1


def test_an_inactive_bad_step_in_a_session_file_is_refused_like_the_list(tmp_path):
    sm, key = _session(tmp_path, [{**BAD_STEPS["an unknown type"], "active": False}])
    with pytest.raises(LegacySessionError):
        sm.list_t3_ghosts(key)


@pytest.mark.parametrize("name", ["an unknown type", "a name like the removed one", "a filter without a column"])
def test_an_imported_session_zip_refuses_it_and_extracts_nothing(tmp_path, name):
    source, key = _session(tmp_path / "from", [BAD_STEPS[name]])
    target = SessionManager(tmp_path / "to")
    with pytest.raises(LegacySessionError, match="audit step 1"):
        target.import_session_zip(source.export_session_zip(key))
    assert not list(target.root.glob("*"))


# -- an imported bundle ------------------------------------------------------------------------------------------------

def _bundle(steps: list) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("b/effective_run.yaml", yaml.safe_dump({"t3_audit_steps_sha256": "x"}))
        zf.writestr("b/t3_steps.yaml", yaml.safe_dump({"t3_steps": {"p": steps}}))
    return buf.getvalue()


BUNDLE_BAD = {
    "an unknown type": {"action": "mystery_step", "reason": "r"},
    "a name like the removed one": {"action": REMOVED + "2", "reason": "r"},
    "a filter without a column": {"action": "filter_row", "op": "ge", "value": 2, "reason": "r"},
    "a drop without a column": {"action": "drop_column", "reason": "r"},
}


@pytest.mark.parametrize("name", sorted(BUNDLE_BAD))
def test_an_imported_bundle_refuses_a_step_the_app_cannot_apply(name):
    good = {"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"}
    with pytest.raises(BundleImportError, match=r"audit step 2 of the plot 'p'") as caught:
        import_bundle(_bundle([good, BUNDLE_BAD[name]]), bootloader=None)
    assert "new session" in str(caught.value)


def test_a_bundle_record_may_hold_the_seed_pin_and_style_steps():
    record = [{"action": "filter_row", "column": "x", "op": "ge", "value": 2, "reason": "r"},
              {"action": "random_seed", "seed": 5, "layers": [0], "reason": "pinned"},
              {"action": "aesthetic_override", "reason": ""}]
    with pytest.raises(BundleImportError, match="no reproducibility recipe"):   # it goes on to its own checks
        import_bundle(_bundle(record), bootloader=None)
