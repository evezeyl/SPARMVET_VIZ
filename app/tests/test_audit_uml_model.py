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
