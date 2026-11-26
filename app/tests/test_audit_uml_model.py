"""The UML model audit checks every tag of an element, not only the last one of a name."""
import importlib.util
import json
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "audit_uml_model", Path(__file__).resolve().parents[2] / "assets" / "scripts" / "audit_uml_model.py"
)
audit = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(audit)


def _run(tmp_path, tags):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "UML").mkdir(parents=True)
    (tmp_path / "good.py").write_text("def present():\n    pass\n")
    model = {"_type": "Project", "ownedElements": [
        {"_id": "e1", "_type": "UMLClass", "name": "El",
         "tags": [{"_type": "Tag", "name": n, "value": v} for n, v in tags]}]}
    (tmp_path / "docs" / "UML" / "app.mdj").write_text(json.dumps(model))
    return audit.run_checks(tmp_path)


def _broken(violations, kind):
    return [v for v in violations if v["check"] == f"{kind}_BROKEN"]


def test_first_code_tag_broken_is_reported(tmp_path):
    v, c = _run(tmp_path, [("code", "good.py:gone"), ("code", "good.py:present")])
    assert len(_broken(v, "CODE")) == 1 and "gone" in _broken(v, "CODE")[0]["detail"]
    assert c["code"] == 2


def test_second_code_tag_broken_is_reported(tmp_path):
    v, c = _run(tmp_path, [("code", "good.py:present"), ("code", "good.py:gone")])
    assert len(_broken(v, "CODE")) == 1 and "gone" in _broken(v, "CODE")[0]["detail"]
    assert c["code"] == 2


def test_two_good_code_tags_both_counted(tmp_path):
    v, c = _run(tmp_path, [("code", "good.py:present"), ("code", "good.py")])
    assert _broken(v, "CODE") == []
    assert c["code"] == 2


def test_test_tags_every_one_checked(tmp_path):
    v, c = _run(tmp_path, [("test", "good.py:gone"), ("test", "good.py:present")])
    assert len(_broken(v, "TEST")) == 1
    v, c = _run(tmp_path / "b", [("test", "good.py:present"), ("test", "good.py:gone")])
    assert len(_broken(v, "TEST")) == 1 and c["test"] == 2


def test_two_good_test_tags_both_counted(tmp_path):
    v, c = _run(tmp_path, [("test", "good.py:present"), ("test", "good.py")])
    assert _broken(v, "TEST") == [] and c["test"] == 2


def test_single_tag_behaves_as_before(tmp_path):
    v, c = _run(tmp_path, [("code", "good.py:gone")])
    assert len(_broken(v, "CODE")) == 1 and c["code"] == 1
    v, c = _run(tmp_path / "ok", [("code", "good.py:present")])
    assert _broken(v, "CODE") == [] and c["code"] == 1


# ---- the names rule: one line, at most 45 characters, exception tag `longname` with a reason ----

def _names_model(*elements, diagram_name="DG-X A diagram whose own name is far longer than the limit of forty-five characters"):
    """A made-up model: a package holding the given elements, a diagram showing the first one through a view."""
    owned = [dict(e) for e in elements]
    view = {"_id": "v1", "_type": "FCProcessView", "model": {"$ref": owned[0]["_id"]}, "left": 0, "top": 0}
    return {"_type": "Project", "_id": "p0", "name": "P", "ownedElements": [
        {"_id": "k1", "_type": "FCFlowchart", "name": "Flowchart", "ownedElements": owned,
         "ownedDiagrams": [{"_id": "d1", "_type": "FCFlowchartDiagram", "name": diagram_name, "ownedViews": [view]}]}]}


def _el(eid, name, tags=None):
    e = {"_id": eid, "_type": "FCProcess", "name": name}
    if tags is not None:
        e["tags"] = [{"_type": "Tag", "name": n, "value": v} for n, v in tags]
    return e


def _names(model):
    v, c = audit.check_names(model)
    return v, c


def test_names_a_correct_model_passes_and_diagram_and_view_names_are_not_element_names():
    # the diagram name above is longer than the limit on purpose: diagrams and views are exempt
    v, c = _names(_names_model(_el("e1", "a" * audit.NAME_MAX_LENGTH), _el("e2", "Short name")))
    assert v == []
    assert c["names_checked"] >= 2 and c["names_excused"] == 0


def test_names_a_line_break_is_a_finding_that_names_id_type_owner_and_diagram():
    v, _ = _names(_names_model(_el("e1", "first line\nsecond line")))
    assert [x["check"] for x in v] == ["NAME_LINE_BREAK"]
    detail = v[0]["detail"]
    assert "id e1" in detail and "owner Flowchart" in detail and "diagram DG-X" in detail
    assert v[0]["type"] == "FCProcess"


def test_names_a_name_one_character_over_the_limit_is_a_finding_and_at_the_limit_passes():
    v, _ = _names(_names_model(_el("e1", "x" * (audit.NAME_MAX_LENGTH + 1))))
    assert [x["check"] for x in v] == ["NAME_TOO_LONG"]
    assert str(audit.NAME_MAX_LENGTH + 1) in v[0]["detail"] and "id e1" in v[0]["detail"]
    v, _ = _names(_names_model(_el("e1", "x" * audit.NAME_MAX_LENGTH)))
    assert v == []


def test_names_the_exception_tag_with_a_reason_excuses_the_length_and_is_counted():
    long = "test_" + "a" * 60
    v, c = _names(_names_model(_el("e1", long, [("longname", "test identifier")])))
    assert v == [] and c["names_excused"] == 1


def test_names_the_exception_tag_without_a_reason_is_a_finding_and_the_length_still_fails():
    long = "x" * 60
    v, c = _names(_names_model(_el("e1", long, [("longname", "  ")])))
    assert sorted(x["check"] for x in v) == ["NAME_EXCEPTION_NO_REASON", "NAME_TOO_LONG"]
    assert c["names_excused"] == 0


def test_names_the_exception_tag_never_excuses_a_line_break():
    v, _ = _names(_names_model(_el("e1", "a\nb", [("longname", "screen text")])))
    assert [x["check"] for x in v] == ["NAME_LINE_BREAK"]


def test_names_run_checks_reports_the_findings_and_the_counts(tmp_path):
    (tmp_path / "docs" / "UML").mkdir(parents=True)
    model = _names_model(_el("e1", "one\ntwo"), _el("e2", "y" * 80), _el("e3", "fine"))
    (tmp_path / "docs" / "UML" / "app.mdj").write_text(json.dumps(model))
    v, c = audit.run_checks(tmp_path)
    assert {x["check"] for x in v} == {"NAME_LINE_BREAK", "NAME_TOO_LONG"}
    assert c["names_checked"] >= 3
    report, code = audit.render_report(v, c, tmp_path)
    assert code == 1 and "NAME_TOO_LONG" in report and "NAME_LINE_BREAK" in report


def test_names_the_real_model_has_no_name_finding():
    root = Path(__file__).resolve().parents[2]
    model = json.loads((root / "docs" / "UML" / "app.mdj").read_text(encoding="utf-8"))
    v, c = audit.check_names(model)
    assert v == [], v[:5]
    assert c["names_checked"] > 1000
