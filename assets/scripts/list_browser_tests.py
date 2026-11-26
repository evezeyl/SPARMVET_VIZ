#!/usr/bin/env python3
# @deps
# provides: script:list_browser_tests
# consumes: every test_*.py of the project (read with ast, never run)
# consumed_by: .claude/rules/rules_verification_testing.md (section 8), .claude/rules/rules_toolchain.md, app/tests/test_list_browser_tests.py
# doc: .claude/rules/rules_verification_testing.md#8
# @end_deps
"""list_browser_tests.py - the one agreed list of the browser test files of the project.

A browser test starts the app and drives it with Playwright; it is slow and runs one process at a time, so the headless run must leave it out and the browser
run must hold exactly those files. Three builders once guessed the list by hand and their headless totals differed by dozens of tests: this script decides, by
reading every `test_*.py` with `ast` (nothing is imported or run), and prints the same answer to everyone.

A file is a BROWSER file when any of these holds:
  1. a function (a test or a fixture) takes one of the arguments `page`, `shiny_app`, `browser`, `context` (an annotation must name a Playwright or Shiny type:
     `page: Path` is a file);
  2. it imports `playwright`;
  3. it calls `create_app_fixture`;
  4. one level of helpers: it imports a browser fixture by name (`shiny_app`, `page`, ...) or imports, from another file of the project (a helper such as `browser_view` or `gate_stage`, `conftest`, or another test file),
     a function that takes one of those arguments, or imports such a helper module and calls `module.function(...)` of it.
A file that only contains the WORD "page" in a string or a comment is not a browser file: only arguments, imports and calls count.
Every other test file is HEADLESS.

Usage:
  python assets/scripts/list_browser_tests.py                       # the two counts and what decided
  python assets/scripts/list_browser_tests.py --browser             # the browser files, one per line (for `pytest $(...)`)
  python assets/scripts/list_browser_tests.py --headless-ignores    # `--ignore=<file>` for every browser file, on one line (for the headless run)
The files are paths relative to the project root; the counts go to standard error when a list is printed. No path is fixed: `--project-root` (default: the
current folder).
"""
import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

BROWSER_ARGS = {"page", "shiny_app", "browser", "context"}
SKIP_DIRS = {".venv", ".git", "node_modules", "__pycache__", ".pytest_cache", "build", "dist", "tmp", "tmpAI", ".claude", "site-packages"}


def _skipped(path: Path, root: Path) -> bool:
    return any(part in SKIP_DIRS or part.endswith(".egg-info") for part in path.relative_to(root).parts[:-1])


def _tree(path: Path) -> Optional[ast.Module]:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def _is_browser_type(annotation: Optional[ast.expr]) -> bool:
    """No annotation counts (a fixture request); an annotation must name a Playwright or Shiny type: `page: Path` is a file, not a browser page."""
    if annotation is None:
        return True
    text = ast.unparse(annotation)
    return any(word in text for word in ("Page", "Browser", "Context", "ShinyAppProc"))


def _browser_functions(tree: ast.Module) -> Set[str]:
    """Names of the functions of a module that take a browser argument."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            if any(x.arg in BROWSER_ARGS and _is_browser_type(x.annotation) for x in a.posonlyargs + a.args + a.kwonlyargs):
                found.add(node.name)
    return found


def _module_file(module: str, level: int, here: Path, root: Path) -> Optional[Path]:
    """The project file a module name stands for: dotted from the root, relative to the importing file, or a sibling file (the tests folder is on the path)."""
    parts = module.split(".") if module else []
    candidates: List[Path] = []
    if level:
        base = here.parent
        for _ in range(level - 1):
            base = base.parent
        candidates.append(base.joinpath(*parts))
    else:
        candidates.append(root.joinpath(*parts))
        candidates.append(here.parent.joinpath(*parts))
    for c in candidates:
        for option in (c.with_suffix(".py"), c / "__init__.py"):
            if parts and option.is_file():
                return option
    return None


class Classifier:
    """Reads files once and decides; `why(path)` is the reason a file is a browser file, or None."""

    def __init__(self, root: Path):
        self.root = root
        self._trees: Dict[Path, Optional[ast.Module]] = {}
        self._funcs: Dict[Path, Set[str]] = {}

    def tree(self, path: Path) -> Optional[ast.Module]:
        if path not in self._trees:
            self._trees[path] = _tree(path)
        return self._trees[path]

    def funcs(self, path: Path) -> Set[str]:
        if path not in self._funcs:
            t = self.tree(path)
            self._funcs[path] = _browser_functions(t) if t else set()
        return self._funcs[path]

    def why(self, path: Path) -> Optional[str]:
        tree = self.tree(path)
        if tree is None:
            return None
        direct = self.funcs(path)
        if direct:
            return f"a function takes a browser argument ({sorted(direct)[0]})"
        helper_modules: Dict[str, Path] = {}      # local name -> helper file (`import x as y`, `from pkg import module`)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] == "playwright":
                        return "it imports playwright"
                    target = _module_file(alias.name, 0, path, self.root)
                    if target and target != path:
                        helper_modules[alias.asname or alias.name.split(".")[-1]] = target
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.split(".")[0] == "playwright":
                    return "it imports playwright"
                source = _module_file(module, node.level, path, self.root)
                for alias in node.names:
                    if source and source != path and alias.name in BROWSER_ARGS:
                        return f"it imports the fixture {alias.name} from {source.name}"
                    if source and source != path and alias.name in self.funcs(source):
                        return f"it imports {alias.name} from {source.name}, which takes a browser argument"
                    sub = _module_file((module + "." if module else "") + alias.name, node.level, path, self.root)
                    if sub and sub != path:
                        helper_modules[alias.asname or alias.name] = sub
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if name == "create_app_fixture":
                return "it calls create_app_fixture"
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in helper_modules:
                if f.attr in self.funcs(helper_modules[f.value.id]):
                    return f"it calls {f.value.id}.{f.attr}, which takes a browser argument"
        return None


def test_files(root: Path) -> List[Path]:
    return sorted(p for p in root.rglob("test_*.py") if p.is_file() and not _skipped(p, root))


def classify(root: Path) -> Tuple[Dict[Path, str], List[Path]]:
    """`({browser file: reason}, [headless files])`, both relative to `root`, sorted."""
    root = root.resolve()
    c = Classifier(root)
    browser: Dict[Path, str] = {}
    headless: List[Path] = []
    for path in test_files(root):
        reason = c.why(path)
        if reason:
            browser[path.relative_to(root)] = reason
        else:
            headless.append(path.relative_to(root))
    return browser, headless


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=".", help="the project folder to read (default: the current folder)")
    what = parser.add_mutually_exclusive_group()
    what.add_argument("--browser", action="store_true", help="print the browser test files, one per line")
    what.add_argument("--headless-ignores", action="store_true", help="print `--ignore=<file>` for every browser file, on one line")
    args = parser.parse_args(argv)
    root = Path(args.project_root)
    if not root.is_dir():
        print(f"not a folder: {root}", file=sys.stderr)
        return 2
    browser, headless = classify(root)
    counts = f"{len(browser)} browser files, {len(headless)} headless files ({len(browser) + len(headless)} test files)"
    if args.browser:
        print("\n".join(str(p) for p in browser))
        print(counts, file=sys.stderr)
    elif args.headless_ignores:
        print(" ".join(f"--ignore={p}" for p in browser))
        print(counts, file=sys.stderr)
    else:
        print(counts)
        for p, why in browser.items():
            print(f"  browser: {p}  ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
