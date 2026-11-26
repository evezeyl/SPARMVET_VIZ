"""The one list of browser test files (`assets/scripts/list_browser_tests.py`): each rule on small made-up files, and the real tree.

# @deps
# consumes: assets/scripts/list_browser_tests.py
# doc: .claude/rules/rules_verification_testing.md#8
# @end_deps

What is proved:
- each rule alone marks a file as a browser file: a function (test or fixture) that takes `page`, `shiny_app`, `browser` or `context`; an import of `playwright`; a call
  of `create_app_fixture`; one level of helpers (a function imported from a helper file that takes such an argument, or `helper.function(...)` of an imported helper module);
- a file that only holds the WORD "page" (in a string, a comment, a variable, a `page: Path` argument) is headless; so is a file that imports a helper function that takes no
  browser argument;
- on the real tree: the files the script calls headless have no function that takes a browser argument and no import of playwright (checked here by a plainer `ast` walk of
  our own), every file that does is in the browser list, and the lists are not empty; the command line prints the same counts.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_list_browser_tests.py -q
"""
import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "assets" / "scripts" / "list_browser_tests.py"
_spec = importlib.util.spec_from_file_location("list_browser_tests", SCRIPT)
lbt = importlib.util.module_from_spec(_spec)
sys.modules["list_browser_tests"] = lbt
_spec.loader.exec_module(lbt)


def make(tmp_path: Path, files: dict) -> Path:
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def kinds(tmp_path: Path, files: dict) -> dict:
    browser, headless = lbt.classify(make(tmp_path, files))
    return {**{str(p): "browser" for p in browser}, **{str(p): "headless" for p in headless}}


@pytest.mark.parametrize("arg", ["page", "shiny_app", "browser", "context"])
def test_a_test_or_a_fixture_that_takes_a_browser_argument_is_a_browser_file(tmp_path, arg):
    got = kinds(tmp_path, {"t/test_a.py": f"def test_x({arg}):\n    pass\n", "t/test_b.py": f"import pytest\n@pytest.fixture\ndef ready({arg}):\n    yield\n"})
    assert got == {"t/test_a.py": "browser", "t/test_b.py": "browser"}


def test_an_import_of_playwright_and_a_call_of_create_app_fixture_make_a_browser_file(tmp_path):
    got = kinds(tmp_path, {"t/test_a.py": "from playwright.sync_api import sync_playwright\n", "t/test_b.py": "import playwright\n",
                           "t/test_c.py": "from shiny.pytest import create_app_fixture\napp = create_app_fixture('x')\n"})
    assert set(got.values()) == {"browser"} and len(got) == 3


def test_a_file_that_only_holds_the_word_page_is_headless(tmp_path):
    got = kinds(tmp_path, {"t/test_a.py": "def test_x():\n    page = 'the page and the browser'  # a page, shiny_app, playwright\n    assert page\n",
                           "t/test_b.py": "from pathlib import Path\n\ndef _text_of(page: Path):\n    return page.read_text()\n\ndef test_x(tmp_path):\n    pass\n",
                           "t/test_c.py": "'''uses the browser and a page'''\ndef test_x(browser_like, pages):\n    pass\n"})
    assert set(got.values()) == {"headless"} and len(got) == 3


def test_one_level_of_helpers_a_function_that_takes_page(tmp_path):
    files = {"t/helper.py": "def wait_shiny(page):\n    pass\n\ndef plain(x):\n    return x\n",
             "t/test_name.py": "from helper import wait_shiny\n\ndef test_x():\n    wait_shiny(None)\n",
             "t/test_module.py": "import helper\n\ndef test_x():\n    helper.wait_shiny(None)\n",
             "t/test_dotted.py": "from t import helper as h\n\ndef test_x():\n    h.wait_shiny(None)\n",
             "t/test_relative.py": "from .helper import wait_shiny\n",
             "t/test_plain.py": "from helper import plain\n\ndef test_x():\n    plain(1)\n",
             "t/test_plain_module.py": "import helper\n\ndef test_x():\n    helper.plain(1)\n",
             "t/test_fixture.py": "from conftest import shiny_app\n\ndef test_x():\n    pass\n",
             "t/conftest.py": "shiny_app = object()\n"}
    got = kinds(tmp_path, files)
    for name in ("test_name", "test_module", "test_dotted", "test_relative", "test_fixture"):
        assert got[f"t/{name}.py"] == "browser", name
    for name in ("test_plain", "test_plain_module"):
        assert got[f"t/{name}.py"] == "headless", name


def test_folders_that_are_not_ours_are_not_read_and_a_file_that_does_not_parse_is_headless(tmp_path):
    got = kinds(tmp_path, {".venv/lib/test_x.py": "def test_x(page):\n    pass\n", "tmpAI/test_y.py": "def test_y(page):\n    pass\n",
                           "t/test_broken.py": "def test_z(:\n"})
    assert got == {"t/test_broken.py": "headless"}


def test_the_command_line_prints_the_lists_and_the_ignore_arguments(tmp_path):
    root = make(tmp_path, {"t/test_a.py": "def test_x(page):\n    pass\n", "t/test_b.py": "def test_y():\n    pass\n"})
    run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), *a], capture_output=True, text=True, check=True)
    assert run("--browser").stdout.split() == ["t/test_a.py"]
    assert run("--headless-ignores").stdout.split() == ["--ignore=t/test_a.py"]
    assert "1 browser files, 1 headless files" in run().stdout
    assert "--project-root" in run("--help").stdout


# -- the real tree ---------------------------------------------------------------------------------------------------

def _plain_walk(path: Path) -> bool:
    """Our own plainer reading, written separately from the script: True when the file has a function with a browser argument (and a Playwright or Shiny annotation, or none) or
    imports playwright."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if any(n.split(".")[0] == "playwright" for n in names):
                return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                if a.arg in lbt.BROWSER_ARGS and (a.annotation is None or any(w in ast.unparse(a.annotation) for w in ("Page", "Browser", "Context", "ShinyAppProc"))):
                    return True
    return False


def test_on_the_real_tree_no_headless_file_asks_for_a_browser_and_every_one_that_does_is_listed():
    browser, headless = lbt.classify(ROOT)
    assert len(browser) > 20 and len(headless) > 100
    assert not set(browser) & set(headless)
    for path in headless:
        assert not _plain_walk(ROOT / path), f"{path} is called headless but asks for a browser"
    for path in lbt.test_files(ROOT):
        if _plain_walk(path):
            assert path.relative_to(ROOT) in browser, f"{path} asks for a browser and is not in the list"
    for known in ("app/tests/test_shiny_smoke.py", "app/tests/test_every_app_features_starts.py", "app/tests/test_demo_walk_audit.py", "app/tests/test_home_mode_row_browser.py"):
        assert Path(known) in browser, known
    for known in ("app/tests/test_home_view_choices.py", "app/tests/test_list_browser_tests.py", "libs/utils/tests/test_recipe_check.py", "app/tests/test_export_report_texts.py"):
        assert Path(known) in headless, known


def test_the_command_line_on_the_real_tree_agrees_with_the_function():
    browser, headless = lbt.classify(ROOT)
    out = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(ROOT), "--browser"], capture_output=True, text=True, check=True)
    assert out.stdout.split() == [str(p) for p in browser]
    assert f"{len(browser)} browser files, {len(headless)} headless files" in out.stderr
