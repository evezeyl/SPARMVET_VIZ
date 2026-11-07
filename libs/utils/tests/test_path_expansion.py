"""~ and ${VAR} in deployment paths (ADR-091)."""
from utils.path_expansion import expand_deployment_paths, expand_path


def test_home_and_variable_are_expanded(monkeypatch):
    monkeypatch.setenv("HOME", "/home/anna")
    monkeypatch.setenv("PROJECT", "amr")
    assert expand_path("~/data/${PROJECT}/in") == ("/home/anna/data/amr/in", [])
    assert expand_path("$PROJECT/x") == ("amr/x", [])


def test_unset_variable_is_reported_by_name(monkeypatch):
    monkeypatch.delenv("NOPE_VAR", raising=False)
    new, missing = expand_path("/data/${NOPE_VAR}/in")
    assert missing == ["NOPE_VAR"]


def test_plain_path_is_unchanged():
    assert expand_path("assets/test_data/") == ("assets/test_data/", [])


def test_deployment_dict_is_expanded_in_place(monkeypatch):
    monkeypatch.setenv("HOME", "/home/anna")
    cfg = {"project_root": "~/p", "locations": {"cache": "${HOME}/c", "gallery": "gallery/"},
           "deployment_name": "~keep~"}
    assert expand_deployment_paths(cfg, "dep.yaml") == []
    assert cfg["project_root"] == "/home/anna/p" and cfg["locations"]["cache"] == "/home/anna/c"
    assert cfg["deployment_name"] == "~keep~"  # not a path key


def test_unset_variable_gives_an_error_naming_it_and_leaves_the_value(monkeypatch):
    monkeypatch.delenv("NOPE_VAR", raising=False)
    cfg = {"locations": {"cache": "${NOPE_VAR}/c"}}
    errors = expand_deployment_paths(cfg, "dep.yaml")
    assert len(errors) == 1 and "NOPE_VAR" in errors[0].problem and "locations.cache" in errors[0].location
    assert cfg["locations"]["cache"] == "${NOPE_VAR}/c"
