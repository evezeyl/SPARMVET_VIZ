"""The agent tool `get_field_contract` returns what recipe format 1 has: `input_fields`, no `output_fields`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_agent_tools.py -q
"""
from utils.recipe_factory import minimal_recipe, minimal_schema, write_recipe

from blueprint_arch.agent_tools import _tool_get_field_contract


def test_the_contract_is_the_input_fields_and_has_no_output_fields(tmp_path):
    recipe = minimal_recipe("tiny", schemas={
        "samples": minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id")})
    path = write_recipe(tmp_path / "tiny.yaml", recipe)
    result = _tool_get_field_contract({"schema_id": "samples", "data_analysis_recipe_path": str(path)})
    assert result["status"] == "ok", result
    data = result["data"]
    assert "output_fields" not in data
    assert data["wrangling_tiers"] == ["tier1"]
    assert {f["slug"] for f in data["input_fields"]} == {"sample_id", "year"}
    assert {f["slug"]: f["type"] for f in data["input_fields"]}["year"] == "Int64"


def test_an_unknown_schema_names_the_available_ones(tmp_path):
    recipe = minimal_recipe("tiny", schemas={"samples": minimal_schema("data/samples.tsv", {"sample_id": "String"})})
    path = write_recipe(tmp_path / "tiny.yaml", recipe)
    result = _tool_get_field_contract({"schema_id": "nope", "data_analysis_recipe_path": str(path)})
    assert result["status"] == "error" and "samples" in result["message"]


def test_the_prompt_and_the_module_describe_what_the_tool_returns():
    """The text the agent reads must not promise `output_fields`, which recipe format 1 does not have."""
    from blueprint_arch import agent_tools
    from blueprint_arch.agent_context import build_system_prompt

    prompt = build_system_prompt()
    line = next(l for l in prompt.splitlines() if "get_field_contract" in l)
    assert "output_fields" not in line and "input_fields" in line
    assert "output_fields" not in agent_tools.__doc__.split("Each tool function")[0].replace("recipe format 1 has no output_fields", "")
