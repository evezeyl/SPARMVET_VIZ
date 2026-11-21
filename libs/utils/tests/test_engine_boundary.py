"""The engine boundary, stage 0: every use of an engine library is in one list, and every listed file says its engine (D-0455, D-0458).

The list is `utils.engine_boundary.PLACES`. The test walks the source tree of the repository and fails when:
(a) a file imports Polars, plotnine, matplotlib, pandas or mizani and is not in the list (or the list does not name the engine of one of its imports);
(b) a listed file has no `# engine:` line in its first lines, or the line names another engine than the list;
(c) a listed file no longer exists, no longer uses its engine (stale entry), or a names-as-data entry now imports the library;
(d) the list names an engine that is not in `utils.engines.ENGINE_TABLE`.
Imports are read with `ast` (also inside a function and under `TYPE_CHECKING`), never by text search. Tests, the virtual environment,
worktrees, `tmpAI`, `tmp`, `archives` and `EVE_WORK` are not walked. A names-as-data file (no import) cannot be found by this test; the
list holds those by hand.

The checker is a function of a root folder and a list, so that each rule is shown to fail on a small tree built by the test: a check that
cannot fail would prove nothing.

# @deps
# consumes: libs/utils/src/utils/engine_boundary.py, libs/utils/src/utils/engines.py
# doc: .claude/knowledge/decision_ledger.md (D-0455, D-0458)
# @end_deps
"""
import ast
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import pytest

from utils import engine_boundary
from utils.engine_boundary import EnginePlace, LIBRARY_ENGINE, NAMES_AS_DATA, PLACES
from utils.engines import ENGINE_TABLE

REPO = Path(__file__).resolve().parents[3]

# folders that are not walked (the brief of stage 0): tests, the environment, worktrees and scratch
NOT_WALKED = {"tests", ".venv", "venv", ".git", ".claude", "worktrees", "tmpAI", "tmp", "archives", "EVE_WORK", "__pycache__",
              "node_modules", "build", "dist", "site-packages"}
MARK_PREFIX = "# engine:"
MARK_LINES = 5   # the mark is in the header: one of the first lines
MARK = re.compile(r"^# engine: (?P<engines>[a-z][a-z0-9-]*(?:\+[a-z][a-z0-9-]*)*) \((?P<what>[^()\n]+)\)\s*$")
# a names-as-data file must still mention its engine: one word per engine (an entry whose words are gone is stale)
ENGINE_WORDS = {"python-polars": ("polars", "modif_", "lazyframe", "collect_schema", "action_names"),   # the engine's name, its actions (read through utils.action_names), its table type
                "python-plotnine": ("plotnine", "matplotlib", "geom_", "pandas")}


def source_files(root: Path) -> List[Path]:
    """Every .py file under `root` that is not in a folder that is not walked."""
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in NOT_WALKED and not d.endswith(".egg-info"))
        found += [Path(folder) / name for name in sorted(files) if name.endswith(".py")]
    return found


def imports_of(path: Path) -> Dict[str, int]:
    """{library: first line} for every engine library the file imports, at any depth of the file (function, `TYPE_CHECKING`).
    A call of `import_module("polars")` or `__import__("polars")` with the name written out counts too."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: Dict[str, int] = {}

    def note(module: str, line: int) -> None:
        top = module.split(".")[0]
        if top in LIBRARY_ENGINE:
            found.setdefault(top, line)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                note(alias.name, node.lineno)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            note(node.module, node.lineno)
        elif isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if name in ("import_module", "__import__"):
                note(node.args[0].value, node.lineno)
    return found


def marks_of(text: str) -> List[str]:
    """The lines of the file that start with the mark prefix, with their line number: ["3: # engine: ..."]."""
    return [f"{number}: {line}" for number, line in enumerate(text.splitlines(), 1) if line.startswith(MARK_PREFIX)]


def boundary_problems(root: Path, places: Sequence[EnginePlace], engines: Iterable[str]) -> List[str]:
    """What is wrong between the code under `root` and the list `places`, in plain words; [] when they agree."""
    problems: List[str] = []
    known = set(engines)
    by_path = {}
    for place in places:
        if place.path in by_path:
            problems.append(f"{place.path}: listed twice. Keep one entry.")
        by_path[place.path] = place
    # (d) the engines the list names
    for place in places:
        for name in place.engines:
            if name not in known:
                problems.append(f"{place.path}: the list names the engine '{name}', which is not in the engine table (utils.engines.ENGINE_TABLE). "
                                f"Use one of {', '.join(sorted(known))}, or add the engine to the table first.")
        if place.kind not in engine_boundary.KINDS:
            problems.append(f"{place.path}: the kind '{place.kind}' is not one of {', '.join(engine_boundary.KINDS)}.")
        if not place.why.strip() or "(" in place.why or ")" in place.why or "\n" in place.why:
            problems.append(f"{place.path}: the phrase of why must be one short line with no brackets.")
        if place.kind == engine_boundary.ENGINE_LIBRARY:
            libraries = {row.library for row in ENGINE_TABLE if row.engine in place.engines}
            if not any(f"libs/{library}/src/" in place.path for library in libraries):
                problems.append(f"{place.path}: kind engine-library, but the file is not in the library of its engine "
                                f"({', '.join(sorted(libraries))}). Change the kind, or move the file.")
        elif place.stage != engine_boundary.NOT_DECIDED:
            problems.append(f"{place.path}: only the engine's own library may have a stage; for this file write '{engine_boundary.NOT_DECIDED}'.")
    # (a) every use of an engine library is listed
    seen = set()
    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        seen.add(relative)
        try:
            used = imports_of(path)
        except SyntaxError as error:
            problems.append(f"{relative}: the file cannot be read as Python ({error.msg}, line {error.lineno}), so its imports cannot be checked.")
            continue
        place = by_path.get(relative)
        if used and place is None:
            what = ", ".join(f"{library} (line {line})" for library, line in sorted(used.items()))
            problems.append(f"{relative}: imports {what} and is not in the list of engine places (utils/engine_boundary.py). "
                            "Add the file to the list with its engine and its kind, or remove the import.")
        elif used and place is not None:
            missing = sorted({LIBRARY_ENGINE[library] for library in used} - set(place.engines))
            if missing:
                problems.append(f"{relative}: imports a library of {', '.join(missing)}, but the list gives only {'+'.join(place.engines)}. "
                                "Add that engine to the entry and to the mark of the file.")
        # a mark without a list entry
        if place is None and marks_of(path.read_text(encoding="utf-8")):
            problems.append(f"{relative}: has an '# engine:' line but is not in the list. Add it to the list, or remove the line.")
    # (b) and (c) every listed file
    for place in places:
        path = root / place.path
        if place.path not in seen:
            problems.append(f"{place.path}: is in the list but the file does not exist (or is in a folder that is not walked). Remove the entry.")
            continue
        text = path.read_text(encoding="utf-8")
        used = imports_of(path)
        engines_used = {LIBRARY_ENGINE[library] for library in used}
        if place.kind == NAMES_AS_DATA:
            if used:
                problems.append(f"{place.path}: listed as names-as-data (no import) but it imports {', '.join(sorted(used))}. Change its kind.")
            words = [word for name in place.engines for word in ENGINE_WORDS.get(name, ())]
            body = "\n".join(line for line in text.splitlines() if not line.startswith(MARK_PREFIX)).lower()   # the mark itself names the engine
            if words and not any(word in body for word in words):
                problems.append(f"{place.path}: listed as names-as-data of {'+'.join(place.engines)} but the file no longer mentions it "
                                f"(none of the words: {', '.join(words)}). Remove the entry.")
        else:
            stale = sorted(set(place.engines) - engines_used)
            if stale:
                problems.append(f"{place.path}: is in the list for {', '.join(stale)} but the file no longer imports its library. "
                                "Remove the engine from the entry and from the mark, or remove the entry.")
        marks = marks_of(text)
        if not marks:
            problems.append(f"{place.path}: has no '# engine:' line. Add this line near the top: {place.mark}")
            continue
        if len(marks) > 1:
            problems.append(f"{place.path}: has {len(marks)} '# engine:' lines ({'; '.join(marks)}). Keep one.")
            continue
        number, line = marks[0].split(": ", 1)
        found = MARK.match(line)
        if int(number) > MARK_LINES:
            problems.append(f"{place.path}: the '# engine:' line is at line {number}; it belongs in the first {MARK_LINES} lines.")
        if not found:
            problems.append(f"{place.path}: the '# engine:' line is not in the form '# engine: <engine>[+<engine>] (<what>)': {line}")
        elif set(found.group("engines").split("+")) != set(place.engines):
            problems.append(f"{place.path}: the mark names {found.group('engines')} but the list says {'+'.join(place.engines)}. Make them agree.")
    return problems


# -- the real tree ----------------------------------------------------------------------------------------------------------------

def test_the_source_tree_and_the_list_of_engine_places_agree():
    problems = boundary_problems(REPO, PLACES, [row.engine for row in ENGINE_TABLE])
    assert problems == [], "engine boundary:\n  " + "\n  ".join(problems)


def test_the_walk_sees_the_tree_and_leaves_out_what_it_must():
    walked = {path.relative_to(REPO).as_posix() for path in source_files(REPO)}
    assert "libs/utils/src/utils/engines.py" in walked and "app/modules/engine_registry.py" in walked
    assert not any(part in NOT_WALKED for path in walked for part in Path(path).parts)
    assert "libs/utils/tests/test_engine_boundary.py" not in walked


def test_every_library_that_the_list_maps_belongs_to_an_engine_of_the_table():
    # (d) on the mapping of import names to engines
    assert set(LIBRARY_ENGINE.values()) <= {row.engine for row in ENGINE_TABLE}


def test_the_engine_libraries_of_the_table_hold_only_files_that_are_listed_when_they_import_an_engine():
    # the two libraries named by the table are the engine's own place: an import there must be listed too
    for row in ENGINE_TABLE:
        for path in source_files(REPO / "libs" / row.library / "src"):
            if imports_of(path):
                assert path.relative_to(REPO).as_posix() in {place.path for place in PLACES}, path


# -- each rule can fail (a small tree built here) ---------------------------------------------------------------------------------

ENGINES = ("python-polars", "python-plotnine")


def place(path, engines="python-polars", kind=engine_boundary.TABLE_LIBRARY, why="reads tables"):
    return engine_boundary._place(path, engines, kind, why)


def tree(tmp_path, files: Dict[str, str]) -> Path:
    for name, text in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return tmp_path


GOOD = "# engine: python-polars (reads tables)\nimport polars as pl\n"


def test_a_clean_small_tree_has_no_problem(tmp_path):
    root = tree(tmp_path, {"app/a.py": GOOD, "app/b.py": "x = 1\n"})
    assert boundary_problems(root, [place("app/a.py")], ENGINES) == []


def test_a_file_that_imports_an_engine_and_is_not_listed_fails_and_says_what_to_do(tmp_path):
    root = tree(tmp_path, {"app/a.py": GOOD, "app/new.py": "import polars\n"})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert len(problems) == 1 and problems[0].startswith("app/new.py: imports polars (line 1)")
    assert "Add the file to the list with its engine and its kind, or remove the import" in problems[0]


@pytest.mark.parametrize("source", [
    "def f():\n    import polars as pl\n",                                   # inside a function
    "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from polars import LazyFrame\n",   # under TYPE_CHECKING
    "from plotnine.geoms import geom_point\n",                              # a submodule
    "import matplotlib.pyplot as plt\n",
    "import pandas\n",
    "import mizani.palettes\n",
    "import importlib\nm = importlib.import_module('polars')\n",           # the name written out
])
def test_every_way_of_importing_an_engine_library_is_found(tmp_path, source):
    root = tree(tmp_path, {"libs/x/src/x/m.py": source})
    problems = boundary_problems(root, [], ENGINES)
    assert len(problems) == 1 and "is not in the list of engine places" in problems[0]


def test_text_that_only_says_polars_is_not_an_import(tmp_path):
    root = tree(tmp_path, {"app/m.py": '"""Uses polars and plotnine."""\n# import polars\nx = "import pandas"\n'})
    assert boundary_problems(root, [], ENGINES) == []


def test_a_listed_file_whose_engine_is_not_the_one_it_imports_fails(tmp_path):
    root = tree(tmp_path, {"app/a.py": "# engine: python-polars (reads tables)\nimport polars\nimport plotnine\n"})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert len(problems) == 1 and "imports a library of python-plotnine, but the list gives only python-polars" in problems[0]


def test_files_in_tests_and_scratch_folders_are_not_walked(tmp_path):
    root = tree(tmp_path, {f"{folder}/m.py": "import polars\n" for folder in ("app/tests", "tmpAI", "tmp", ".venv/lib", ".claude/worktrees/w", "archives", "EVE_WORK")})
    assert boundary_problems(root, [], ENGINES) == []


def test_a_listed_file_with_no_mark_fails_and_shows_the_line_to_add(tmp_path):
    root = tree(tmp_path, {"app/a.py": "import polars\n"})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert len(problems) == 1 and "has no '# engine:' line" in problems[0] and "# engine: python-polars (reads tables)" in problems[0]


def test_a_mark_that_names_another_engine_than_the_list_fails(tmp_path):
    root = tree(tmp_path, {"app/a.py": "# engine: python-plotnine (draws)\nimport polars\n"})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert len(problems) == 1 and "the mark names python-plotnine but the list says python-polars" in problems[0]


@pytest.mark.parametrize("header, expected", [
    ("# engine: python-polars\nimport polars\n", "is not in the form"),
    ("# engine: python-polars ()\nimport polars\n", "is not in the form"),
    ("# engine: python-polars (a)\n# engine: python-polars (b)\nimport polars\n", "has 2 '# engine:' lines"),
    ("\n\n\n\n\n\n# engine: python-polars (a)\nimport polars\n", "it belongs in the first 5 lines"),
])
def test_a_malformed_or_misplaced_mark_fails(tmp_path, header, expected):
    root = tree(tmp_path, {"app/a.py": header})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert any(expected in problem for problem in problems), problems


def test_a_mark_in_a_file_that_is_not_listed_fails(tmp_path):
    root = tree(tmp_path, {"app/a.py": "# engine: python-polars (reads tables)\nx = 1\n"})
    problems = boundary_problems(root, [], ENGINES)
    assert len(problems) == 1 and "has an '# engine:' line but is not in the list" in problems[0]


def test_a_listed_file_that_no_longer_exists_is_a_stale_entry(tmp_path):
    root = tree(tmp_path, {"app/other.py": "x = 1\n"})
    problems = boundary_problems(root, [place("app/gone.py")], ENGINES)
    assert len(problems) == 1 and "the file does not exist" in problems[0] and "Remove the entry" in problems[0]


def test_a_listed_file_that_no_longer_imports_its_engine_is_a_stale_entry(tmp_path):
    root = tree(tmp_path, {"app/a.py": "# engine: python-polars (reads tables)\nx = 1\n"})
    problems = boundary_problems(root, [place("app/a.py")], ENGINES)
    assert len(problems) == 1 and "no longer imports its library" in problems[0]


def test_a_names_as_data_entry_must_still_mention_its_engine_and_must_not_import_it(tmp_path):
    entry = place("libs/u/src/u/n.py", kind=NAMES_AS_DATA, why="holds the names")
    root = tree(tmp_path, {"libs/u/src/u/n.py": "# engine: python-polars (holds the names)\nNAME = 'polars_join'\n"})
    assert boundary_problems(root, [entry], ENGINES) == []
    root = tree(tmp_path, {"libs/u/src/u/n.py": "# engine: python-polars (holds the names)\nNAME = 'x'\n"})
    assert "no longer mentions it" in boundary_problems(root, [entry], ENGINES)[0]
    root = tree(tmp_path, {"libs/u/src/u/n.py": "# engine: python-polars (holds the names)\nimport polars\n"})
    assert "listed as names-as-data (no import) but it imports polars" in boundary_problems(root, [entry], ENGINES)[0]


def test_an_engine_that_is_not_in_the_engine_table_fails(tmp_path):
    root = tree(tmp_path, {"app/a.py": "# engine: python-pandas (reads tables)\nimport polars\n"})
    problems = boundary_problems(root, [place("app/a.py", engines="python-pandas")], ENGINES)
    assert any("names the engine 'python-pandas', which is not in the engine table" in problem for problem in problems), problems


def test_a_file_in_the_list_twice_and_a_file_that_cannot_be_read_are_told(tmp_path):
    root = tree(tmp_path, {"app/a.py": GOOD, "app/bad.py": "def (:\n"})
    problems = boundary_problems(root, [place("app/a.py"), place("app/a.py")], ENGINES)
    assert any("listed twice" in problem for problem in problems) and any("cannot be read as Python" in problem for problem in problems)


def test_an_engine_library_entry_must_sit_in_the_library_of_its_engine(tmp_path):
    root = tree(tmp_path, {"app/a.py": GOOD})
    problems = boundary_problems(root, [place("app/a.py", kind=engine_boundary.ENGINE_LIBRARY)], ENGINES)
    assert any("kind engine-library, but the file is not in the library of its engine (transformer)" in problem for problem in problems), problems


def test_the_engine_table_names_exist_as_engines_of_the_list():
    assert {name for item in PLACES for name in item.engines} <= {row.engine for row in ENGINE_TABLE}
