"""Export bundle records the contact of the recipe and where it came from (EXPORT-CONTACT-1, D-0208)."""
from app.modules.data_analysis_recipe_validator import export_contact_readme_line, export_contact_record


def test_contact_from_the_recipe():
    r = export_contact_record({"contact": "a@lab.org"}, "dep@x.org")
    assert r == {"contact": "a@lab.org", "contact_source": "recipe (info.contact)"}
    assert export_contact_readme_line(r) == "Contact          : a@lab.org (from the recipe (info.contact))"


def test_contact_from_the_deployment_when_the_recipe_has_none():
    r = export_contact_record({"name": "x"}, "dep@x.org")
    assert r == {"contact": "dep@x.org", "contact_source": "deployment (branding.contact)"}
    assert "deployment (branding.contact)" in export_contact_readme_line(r)


def test_neither_gives_explicit_empty_and_a_plain_sentence():
    for info in (None, {}, {"contact": ""}):
        r = export_contact_record(info, None)
        assert r == {"contact": None, "contact_source": None}
        assert "names no contact" in export_contact_readme_line(r)


def test_effective_run_yaml_keeps_the_empty_value_explicit():
    import yaml
    out = yaml.safe_load(yaml.safe_dump(export_contact_record(None, None), sort_keys=False))
    assert "contact" in out and out["contact"] is None


def test_handler_writes_the_keys_and_the_line():
    from pathlib import Path
    src = Path("app/handlers/export_handlers.py").read_text()
    assert '"contact": _contact["contact"]' in src
    assert '"contact_source": _contact["contact_source"]' in src
    assert "export_contact_readme_line(_contact)" in src
