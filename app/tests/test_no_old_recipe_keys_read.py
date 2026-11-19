"""No code of the app, the libraries or the scripts reads a recipe key that recipe format 1 does not have (ENGINE-KEYS step 4c).

The recipe shape changed in one step (D-0250, D-0252, D-0253): a tier is its own key (`tier1`, `tier2`, `tier3`, each a mapping with
`steps`), a plot entry is the plot (no `spec`), there is no `wrangling`, `output_fields`, `final_contract` or `pre_plot_wrangling` key.
A reader of an old key does not fail: it finds nothing and skips the step without a word. So the source is scanned: every
`x.get("<old key>")`, `x["<old key>"]` and `"<old key>" in x` of a Python file is listed, and a file that does so by design is named
below with its reason (the tools that REFUSE or REWRITE the old shape, and what reads another format than a recipe).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_no_old_recipe_keys_read.py -q
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_KEYS = {"wrangling", "output_fields", "final_contract", "pre_plot_wrangling", "spec"}

# file -> why it may name an old key (it refuses the key, rewrites it, or reads a format that is not a recipe)
BY_DESIGN = {
    "libs/utils/src/utils/recipe_check.py": "the checker refuses the old keys with the rewrite tool's name",
    "libs/utils/src/utils/engine_keys_migration.py": "the rewrite tool of the amendment of 2026-11-17 reads the old shape",
    "assets/scripts/convert_gallery_examples.py": "reads the OLD COMPACT GALLERY FORM (info, data_path, plots, wrangling) that it converts",
    "assets/scripts/migrate_plot_specs.py": "migrates old plot specs: its input is the old shape",
    "app/modules/data_analysis_recipe_validator.py": "names the old `wrangling` key of an uploaded fragment to tell the user it is not read",
}


def old_key_reads(source: str):
    """(line, key, how) of every get / subscript / `in` that names an old recipe key."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "pop", "setdefault") \
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in OLD_KEYS:
            found.append((node.lineno, node.args[0].value, f".{node.func.attr}()"))
        elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and node.slice.value in OLD_KEYS:
            found.append((node.lineno, node.slice.value, "[...]"))
        elif isinstance(node, ast.Compare) and isinstance(node.left, ast.Constant) and node.left.value in OLD_KEYS \
                and any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
            found.append((node.lineno, node.left.value, "in"))
    return found


def scanned_files():
    for base in ("app", "libs", "assets/scripts", "scripts"):
        for path in sorted((ROOT / base).rglob("*.py")):
            relative = path.relative_to(ROOT).as_posix()
            if "/tests/" in relative or "/build/" in relative or "/.venv/" in relative or relative.startswith("app/tests/"):
                continue
            yield relative, path


def test_no_file_reads_an_old_recipe_key_unless_it_is_named_with_its_reason():
    reads = {}
    for relative, path in scanned_files():
        if relative in BY_DESIGN:
            continue
        found = old_key_reads(path.read_text(encoding="utf-8"))
        if found:
            reads[relative] = found
    assert reads == {}


def test_a_file_named_as_by_design_still_exists_and_still_names_an_old_key():
    """A list of exceptions that is never cleaned hides a new read: an entry that no longer names an old key is an error."""
    stale = []
    for relative in BY_DESIGN:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if not any(f'"{key}"' in text or f"'{key}'" in text or f"`{key}`" in text for key in OLD_KEYS):
            stale.append(relative)
    assert stale == []


# -- the scan itself can fail

def test_the_scan_sees_each_way_of_reading_an_old_key():
    source = (
        "a = x.get('wrangling')\n"
        "b = x['output_fields']\n"
        "c = 'spec' in x\n"
        "d = x.pop('final_contract', None)\n"
        "e = x.get('tier1')\n"          # a key of the new shape
        "f = x['steps']\n"             # `steps` is a key of the new shape
    )
    assert [(line, key) for line, key, _ in old_key_reads(source)] == [(1, "wrangling"), (2, "output_fields"), (3, "spec"), (4, "final_contract")]


def test_a_file_that_reads_the_old_key_is_found_in_the_repository_scan(tmp_path):
    assert old_key_reads("def f(raw):\n    return raw.get('wrangling', {})\n") == [(2, "wrangling", ".get()")]
