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


def test_spaces_only_recipe_contact_is_absent_and_the_deployment_applies():
    r = export_contact_record({"contact": "   "}, " dep@x.org ")
    assert r == {"contact": "dep@x.org", "contact_source": "deployment (branding.contact)"}


def test_spaces_only_everywhere_is_no_contact():
    assert export_contact_record({"contact": "  "}, "  ") == {"contact": None, "contact_source": None}


def test_written_value_is_stripped():
    assert export_contact_record({"contact": "  a@lab.org\n"}, None)["contact"] == "a@lab.org"


def test_a_newline_inside_the_contact_stays_one_readme_line_and_yaml_keeps_the_text():
    r = export_contact_record({"contact": "Eve Z\n  eve@x.org"}, None)
    assert r["contact"] == "Eve Z\n  eve@x.org"
    line = export_contact_readme_line(r)
    assert "\n" not in line and line == "Contact          : Eve Z eve@x.org (from the recipe (info.contact))"
