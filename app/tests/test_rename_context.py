"""The context-aware rename keeps code spellings in code and uses words in prose (ADR-091)."""
import importlib.util
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parents[2] / "assets" / "scripts"
_spec = importlib.util.spec_from_file_location("rename_vocabulary", _HERE / "rename_vocabulary.py")
rv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rv)

PAIRS, RULES = rv.load_pairs()
KEEP = [k.lower() for k in RULES["keep_substrings"]]
FORMS = RULES["forms"]
WORDS = ["manifest"]


def _fix(seg, ctx, whole=False):
    return rv.fix_span(seg, ctx, WORDS, PAIRS, KEEP, FORMS, whole)


def test_prose_gets_spaced_words():
    assert _fix("Load the manifest from disk.", "prose") == "Load the data analysis recipe from disk."
    assert _fix("Manifests are listed", "prose") == "Data analysis recipes are listed"


def test_title_case_phrase():
    assert _fix("Import Manifest", "prose") == "Import Data Analysis Recipe"


def test_code_gets_snake_and_flags_get_hyphens():
    assert _fix("manifest", "code") == "data_analysis_recipe"
    assert _fix("--manifest", "prose") == "--data-analysis-recipe"
    assert _fix("manifest_path", "prose") == "data_analysis_recipe_path"
    assert _fix("ManifestNavigator", "code") == "DataAnalysisRecipeNavigator"


def test_external_tool_name_is_kept():
    assert _fix("rsconnect writes manifest.json", "prose") == "rsconnect writes manifest.json"


def test_python_strings_and_comments(tmp_path):
    src = (
        'def f(manifest, manifests_dir):\n'
        '    """Return the manifest id."""\n'
        '    key = cfg["manifest"]  # the manifest key\n'
        '    p.add_argument("--manifest", help="Path to the manifest")\n'
        '    return f"{manifest}/x manifest not found"\n'
    )
    f = tmp_path / "a.py"
    f.write_text(src)
    assert rv.rewrite_context(str(f), WORDS, PAIRS, KEEP, FORMS, False)
    out = f.read_text()
    assert 'def f(data_analysis_recipe, data_analysis_recipes_dir):' in out
    assert '"""Return the data analysis recipe id."""' in out
    assert 'cfg["data_analysis_recipe"]' in out
    assert "# the data analysis recipe key" in out
    assert 'add_argument("--data-analysis-recipe", help="Path to the data analysis recipe")' in out
    assert 'f"{data_analysis_recipe}/x data analysis recipe not found"' in out
    compile(out, "a.py", "exec")


def test_yaml_key_value_and_comment(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text('manifest: foo\nlabel: "Manifest Choice"\n# the manifest of the run\nx: {manifest_path: y}\n')
    rv.rewrite_context(str(f), WORDS, PAIRS, KEEP, FORMS, False)
    out = f.read_text()
    assert out.startswith("data_analysis_recipe: foo\n")
    assert 'label: "Data Analysis Recipe Choice"' in out or 'label: "Data analysis recipe Choice"' in out
    assert "# the data analysis recipe of the run" in out
    assert "data_analysis_recipe_path" in out
    yaml.safe_load(out)


def test_markdown_inline_code_and_fence(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("Set `manifest` in the manifest file.\n\n```yaml\nmanifest: x  # the manifest\n```\n")
    rv.rewrite_context(str(f), WORDS, PAIRS, KEEP, FORMS, False)
    out = f.read_text()
    assert "Set `data_analysis_recipe` in the data analysis recipe file." in out
    assert "data_analysis_recipe: x  # the data analysis recipe" in out


# --- the bare word recipe (phase 8) ---

def _recipe_rewrite(tmp_path, name, content, area_prefix=None):
    f = tmp_path / name
    f.write_text(content)
    rules = dict(RULES)
    if area_prefix:
        rules = {**RULES, "recipe_nouns": [{"prefix": str(f), "noun": area_prefix}]}
    rv.rewrite_context(str(f), ["recipe"], PAIRS, KEEP, FORMS, False, rules)
    return f.read_text()


def test_recipe_key_in_yaml_is_steps(tmp_path):
    out = _recipe_rewrite(tmp_path, "a.yaml", "recipe:\n  - action: cast\n")
    assert out.startswith("steps:\n")


def test_recipe_phrases_become_their_new_names(tmp_path):
    out = _recipe_rewrite(tmp_path, "a.md", "The T3 recipe, the filter recipe builder and a data analysis recipe recipe.\n")
    assert out == "The audit steps, the filter builder and a data analysis recipe.\n"


def test_bare_word_follows_the_area(tmp_path):
    src = "def f(recipe):\n    \"\"\"Apply the recipe.\"\"\"\n    return recipe\n"
    audit = _recipe_rewrite(tmp_path, "audit.py", src, "audit")
    assert "def f(audit_steps):" in audit and "Apply the audit trail." in audit
    ex = _recipe_rewrite(tmp_path, "gal.py", src, "example")
    assert "def f(example):" in ex and "Apply the example." in ex
    default = _recipe_rewrite(tmp_path, "other.py", src)
    assert "def f(steps):" in default


def test_python_dict_key_recipe_is_steps_even_in_an_audit_file(tmp_path):
    out = _recipe_rewrite(tmp_path, "audit.py", 'x = spec.get("recipe")\nrecipe = []\n', "audit")
    assert 'spec.get("steps")' in out and "audit_steps = []" in out


def test_compound_ids_use_their_pairs(tmp_path):
    out = _recipe_rewrite(tmp_path, "a.py", "t3_recipe_by_plot = {}\nTransformationRecipe()\nmake_recipe_node()\n")
    assert "t3_audit_steps_by_plot" in out and "IdTransformation()" in out and "make_audit_step()" in out


def test_yaml_embedded_in_a_python_string_keeps_its_keys(tmp_path):
    src = 'TEXT = f"""id: tiny\njoins:\n  C:\n    recipe: !include \'x.yaml\'\n# the recipe note\n"""\n'
    out = _recipe_rewrite(tmp_path, "emb.py", src)
    assert "    steps: !include 'x.yaml'" in out
    assert "# the step list note" in out


def test_compound_with_bare_recipe_takes_the_noun_of_the_file(tmp_path):
    src = "filtered_recipe = []\nclass MyRecipeBuilder: pass\nkeep_recipes = 1\n"
    steps = _recipe_rewrite(tmp_path, "t.py", src)
    assert "filtered_steps = []" in steps and "class MyStepsBuilder" in steps and "keep_steps = 1" in steps
    audit = _recipe_rewrite(tmp_path, "t2.py", src, "audit")
    assert "filtered_audit_steps = []" in audit


def test_phrase_keeps_the_leading_word(tmp_path):
    out = _recipe_rewrite(tmp_path, "a.md", "Write the assembly recipe and the join recipes.\n")
    assert out == "Write the assembly steps and the join steps.\n"


def test_single_line_embedded_yaml_keeps_its_key(tmp_path):
    out = _recipe_rewrite(tmp_path, "e.py", "lines.append(f\"    recipe: !include '{rel}'\")\n")
    assert "    steps: !include '{rel}'" in out
