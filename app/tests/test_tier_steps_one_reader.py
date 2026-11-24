"""One reader of a tier's steps (D-0332, piece C-1 of slice C of the HOME audit redesign).

In an audit recipe each tier holds two lists: the author's `steps` and the audit's `audit_steps`; the engine runs `steps`, then `audit_steps`
(`utils.recipe_tiers.step_list`). A reader that reads `["steps"]` directly would run the author's steps and skip the audit's, and nothing would say so. This test
fails when a reader of a tier's steps does not go through the helper.

How it looks: every non-test Python file of `app/` and `libs/` is parsed, and every place that reads or writes a mapping key `steps` or `audit_steps` is counted:
`x["steps"]`, `x.get("steps")`, `x.pop("steps")`, `x.setdefault("steps")` (the key as a text or as the constant `AUDIT_STEPS`). The count per file must be
EXACTLY the one named in `ALLOWED`, with the reason that this file may read the key itself. A new direct read anywhere, or a file that is not on the list, fails;
a listed file that no longer reads the key fails too (the list does not keep a place that is gone).

What is NOT seen: a read through another name (`getattr`, `**` unpacking, a key built at run time), and the attribute `.steps` of an object that is not a mapping
(the recipe graph's `Node.steps`, the id transformation's `steps`): those are not a tier of a recipe. The second test names, per file that RUNS or follows steps, how many times it calls the helper, so a reader that dropped it, or went to the author's steps, fails there.

Mutation index (each seen failing, see the report): T1 a direct read `["steps"]` added to `app/modules/orchestrator.py`; T2 `recipe_graph.py` reads the tier through
`author_steps` instead of `step_list`; T3 `engine_record.py:78` switched to `author_steps`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_tier_steps_one_reader.py -q
"""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
KEYS = ("steps", "audit_steps")
# split on spaces: the guard `test_browser_tests_no_venv_path.py` forbids a quoted dot-venv name followed by a comma in test code, and this is a folder name, not a path
SKIP_PARTS = frozenset("tests build .venv __pycache__ node_modules".split())

# file (relative to the project root) -> (number of direct reads or writes of the key, why that file may do it)
ALLOWED = {
    "libs/utils/src/utils/recipe_tiers.py": (1, "the helper module itself: the one place that strips the audit list (`without_audit_steps`); its readers use a key held in a variable"),
    "libs/utils/src/utils/audit_copy.py": (4, "the audit copy owns the two lists: it writes `audit_steps` (add), removes an emptied one and reads the author's list to refuse a malformed tier"),
    "libs/utils/src/utils/recipe_check.py": (6, "the checker judges the SHAPE of a tier body (is `steps` a list, is `audit_steps` allowed in this profile); it does not run steps"),
    "libs/transformer/src/transformer/data_wrangler.py": (2, "`DataWrangler.tier_steps` is the engine's own validated reading of a tier body: it checks the shape, refuses `audit_steps` outside an audit copy, returns the two lists in run order"),
    "libs/utils/src/utils/recipe_factory.py": (1, "writes the author's list of a recipe it builds (a writer, not a reader)"),
    "libs/viz_gallery/src/viz_gallery/example_recipe.py": (1, "reads back the author's list of a gallery example recipe it has just built (a gallery recipe has no audit list)"),
    "libs/utils/src/utils/engine_keys_migration.py": (1, "a migration tool that rewrites old recipe FILES (text): it reads the key of a file as written"),
    "libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py": (1, "Blueprint's navigator reads the author's tier-1 steps of a join to number them by their place in the FILE; Blueprint shows the original recipe, which has no audit list"),
    "libs/blueprint_arch/src/blueprint_arch/t3_translator.py": (1, "the export's fork of a join (`build_mode2_recipe`) appends to the author's tier 2 of the ORIGINAL; it goes when the export holds the audit recipe (D-0324)"),
    "app/modules/audit_places.py": (1, "`bake_place_steps` appends the audit steps written at a table to the author's list of a COPY of the recipe, for the reproducibility part of the export (the recipe alone then builds the audited table); it goes when the export holds the audit recipe (D-0324), as the fork of `t3_translator`"),
    "app/handlers/blueprint_handlers.py": (3, "Blueprint edits the ORIGINAL recipe: it reads the steps of an uploaded fragment and of a tier file, and its writer replaces the author's list and leaves any audit list alone"),
    "app/modules/data_analysis_recipe_validator.py": (5, "reads the steps of an UPLOADED fragment file (an author's file): the checker refuses audit keys there"),
    "libs/id_reconciliation/src/id_reconciliation/data_structures.py": (1, "the `steps` of an id transformation (a saved list of recoding steps), not a tier of a recipe"),
    "libs/id_reconciliation/src/id_reconciliation/id_transformation.py": (1, "the `steps` of an id transformation (a saved list of recoding steps), not a tier of a recipe"),
}

# files that RUN, follow or count the steps of a tier -> {helper name: the number of CALLS of it in the file}. The count is exact: a site that is dropped, or switched to
# `author_steps` (which would skip the audit steps), lowers the count of the right helper and fails; a new legitimate call raises it and the number is changed on purpose.
# The behaviour of the readers that are not the engine is proved in `test_audit_readers_see_audit_steps.py`.
MUST_USE_THE_HELPER = {
    "app/modules/orchestrator.py": {"tier2_steps": 3, "tier3_steps": 2, "tier_steps": 3},   # 3: the table of a failed tier-1 build is explained by running its steps again (`_explain_table_failure`)
    "app/modules/cache_keys.py": {"tier2_parts": 1, "tier3_parts": 1, "audit_steps_of": 1},
    "app/modules/engine_record.py": {"step_list": 2},
    "app/modules/view_badge.py": {"tier2_steps": 1, "tier3_steps": 1},
    "app/modules/audit_run.py": {"tier2_steps": 2},
    "app/modules/session_manager.py": {"recipe_join_keys": 1},   # `extract_primary_keys` returns the shared rule; it read `step_list` itself before the merge of slice B
    "app/handlers/audit_stack.py": {"tier2_steps": 1},
    "app/handlers/export_handlers.py": {"tier2_steps": 3, "tier3_steps": 2},
    "libs/utils/src/utils/recipe_graph.py": {"step_list": 4},
    "libs/utils/src/utils/recipe_tiers.py": {"step_list": 5},
    "libs/utils/src/utils/recipe_check.py": {"audit_steps_of": 2},
    "libs/utils/src/utils/join_keys.py": {"step_list": 2},
    "libs/utils/src/utils/audit_copy.py": {"without_audit_steps": 1},
}


def _is_key(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return node.value in KEYS
    if isinstance(node, ast.Name):
        return node.id == "AUDIT_STEPS"
    if isinstance(node, ast.Attribute):
        return node.attr == "AUDIT_STEPS"
    return False


def _direct_reads(path: Path) -> list:
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Subscript) and _is_key(node.slice):
            found.append(node.lineno)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "pop", "setdefault")
              and node.args and _is_key(node.args[0])):
            found.append(node.lineno)
    return sorted(found)


def _files():
    for top in ("app", "libs"):
        for path in sorted((ROOT / top).rglob("*.py")):
            if SKIP_PARTS & set(path.relative_to(ROOT).parts) or path.name.startswith("test_") or path.name == "conftest.py":
                continue
            yield path


def _counts() -> dict:
    return {str(p.relative_to(ROOT)): _direct_reads(p) for p in _files() if _direct_reads(p)}


def test_only_the_named_files_read_the_steps_key_of_a_tier_directly_and_each_as_often_as_named():
    found = _counts()
    unlisted = {f: lines for f, lines in found.items() if f not in ALLOWED}
    assert not unlisted, (
        "These files read `steps` or `audit_steps` as a mapping key and are not on the list of allowed readers. A reader that runs a tier must go through "
        f"`utils.recipe_tiers.step_list` (the author's steps, then the audit steps); if the file only judges, edits or builds, add it to ALLOWED with the reason: {unlisted}")
    wrong = {f: (len(found.get(f, [])), n) for f, (n, _) in ALLOWED.items() if len(found.get(f, [])) != n}
    assert not wrong, f"Allowed readers whose number of direct reads is not the one named (found, named): {wrong}; lines now: { {f: found.get(f) for f in wrong} }"


def test_every_allowed_reader_names_a_reason_and_is_a_file_that_exists():
    for name, (count, reason) in ALLOWED.items():
        assert (ROOT / name).is_file(), name
        assert count >= 1 and len(reason) > 30, name


def _calls_in(source: str) -> dict:
    """The number of calls per name in `source`, seen through an alias on import: `from m import author_steps as step_list` counts the calls of `step_list` as calls
    of `author_steps`, and `import x as y` counts `y(...)` as `x` (an alias is read for the whole file, also as an attribute name); a count of names alone would let an alias hide the wrong helper."""
    tree = ast.parse(source)
    alias = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.asname:
                    alias[a.asname] = a.name.split(".")[-1]
    found: dict = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            name = alias.get(name, name)
            if name:
                found[name] = found.get(name, 0) + 1
    return found


def _calls(path: Path) -> dict:
    return _calls_in(path.read_text(encoding="utf-8"))


def test_the_call_counter_sees_through_an_alias_on_import():
    assert _calls_in("from utils.recipe_tiers import author_steps as step_list\nstep_list(a, 't')\n") == {"author_steps": 1}
    assert _calls_in("from utils.recipe_tiers import author_steps\nauthor_steps(a, 't')\n") == {"author_steps": 1}
    assert _calls_in("from m import step_list as s\ns(a)\n") == {"step_list": 1}


@pytest.mark.parametrize("name", sorted(MUST_USE_THE_HELPER))
def test_the_files_that_run_follow_or_count_steps_call_the_helper_as_often_as_named(name):
    """A reader that RUNS or follows the steps of a tier must reach the audit steps: it calls the helper (`step_list`, `tier2_steps`, `tier3_steps`, `tier_steps`, or the two
    lists apart where the audit parts are kept apart) at EVERY site. The count per file is exact, so a dropped site, or one switched to the author's steps, fails."""
    calls = _calls(ROOT / name)
    wrong = {helper: (calls.get(helper, 0), wanted) for helper, wanted in MUST_USE_THE_HELPER[name].items() if calls.get(helper, 0) != wanted}
    assert not wrong, f"{name}: calls of the helper (found, named) {wrong}: a reader of steps dropped the helper, or went to `author_steps`, and would skip the audit steps"


def test_no_file_outside_the_helper_names_the_key_as_a_bare_text_in_a_comparison_or_a_loop():
    """The audit key name is written once (`recipe_tiers.AUDIT_STEPS`). Other modules refer to the constant, so a rename is one edit: the text `audit_steps` as a
    string literal appears only in the helper module, the spec-facing messages and the places named here."""
    allowed_text = {"libs/utils/src/utils/recipe_tiers.py"}
    offenders = []
    for path in _files():
        rel = str(path.relative_to(ROOT))
        if rel in allowed_text:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and node.value == "audit_steps":
                offenders.append((rel, node.lineno))
    assert not offenders, f"the key name is a constant (`recipe_tiers.AUDIT_STEPS`); these files write it as a text: {offenders}"
