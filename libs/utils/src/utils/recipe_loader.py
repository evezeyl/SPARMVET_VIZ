"""Reading a recipe file strictly, and `check_recipe_file` (checks T01, T02, T07, T10, T11, F01).

`ConfigManager` reads a recipe for the app and tolerates what the format refuses (it removes a fragment's wrapper key,
repairs an unquoted `on`, keeps the last of a repeated key). This reader refuses them and reports each as a problem
with its fix, and still returns what it could read so the checker can go on. It keeps nothing silently: the wrapper
stays in the tree so the checker sees the wrong form.

# @deps
# provides: function:load_recipe, function:check_recipe_file
# consumes: libs/utils/src/utils/strict_yaml.py, libs/utils/src/utils/config_loader.py (project_root_of), libs/utils/src/utils/recipe_check.py
# consumed_by: libs/utils/tests/test_recipe_loader.py
# doc: .claude/design/recipe_format_spec.md (sections 5.2, 6.1; checks T01, T02, T07, T10, T11, F01)
# @end_deps
"""
import os
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import yaml

from utils.config_loader import project_root_of
from utils.recipe_check import Problem, Result, check_recipe
from utils.strict_yaml import DuplicateKeyError, _StrictLoader


class _IncludedDict(dict):
    """A mapping that came from an `!include`, kept so a wrapper key can be seen (F01)."""


def _problem(code: str, path: str, message: str, fix: str = "") -> Problem:
    return Problem(code, "E", path, message, fix)


def _walk(node: Any, path: str, problems: List[Problem]) -> Any:
    """Plain copy of the tree; reports F01 (wrapper) and T07 (a boolean key)."""
    if isinstance(node, dict):
        plain = {}
        for key, value in node.items():
            where = f"{path}.{key}" if path else str(key)
            if isinstance(key, bool):
                word = "on" if key else "off"
                problems.append(_problem("T07", where, f"the key {word} was read as the boolean {key}", f"quote it: '{word}'"))
                key = word
                where = f"{path}.{key}" if path else key
            if isinstance(value, _IncludedDict) and len(value) == 1 and key in value:
                problems.append(_problem("F01", where, f"the included file starts with {key}, the key it is included under",
                                         f"remove the line '{key}:' and its indentation: the file holds the {key} themselves"))
            plain[key] = _walk(value, where, problems)
        return plain
    if isinstance(node, list):
        return [_walk(item, f"{path}[{index}]", problems) for index, item in enumerate(node, start=1)]
    return node


def load_recipe(path: Union[str, Path], *, include_root: Optional[Union[str, Path]] = None) -> Tuple[Optional[dict], List[Problem]]:
    """Read a recipe file and its fragments; returns (the recipe or None, the problems of reading it)."""
    path = Path(path)
    problems: List[Problem] = []
    root = os.path.realpath(str(include_root)) if include_root else project_root_of(path)
    base = path.parent

    class Loader(_StrictLoader):
        pass

    def include(loader: yaml.SafeLoader, node: yaml.Node) -> Any:
        name = loader.construct_scalar(node)
        target = os.path.join(base, name)
        resolved = os.path.realpath(target)
        if os.path.isabs(name) or not (resolved == root or resolved.startswith(root + os.sep)):
            what = "an absolute path" if os.path.isabs(name) else "outside the project"
            problems.append(_problem("T11", f"!include {name}", f"the include target is {what}",
                                     f"put the fragment inside the project ({root}) and write its path relative to the recipe"))
            return {}
        try:
            text = Path(resolved).read_text(encoding="utf-8")
        except OSError:
            problems.append(_problem("T02", f"!include {name}", f"the include target {name!r} was not found",
                                     f"create {target} or correct the path"))
            return {}
        try:
            content = yaml.load(text, Loader=Loader)
        except DuplicateKeyError as error:
            problems.append(_problem("T10", f"!include {name}", f"in {name}: {error}", "remove or rename one of the two"))
            return {}
        except yaml.YAMLError as error:
            problems.append(_problem("T01", f"!include {name}", f"{name} is not valid YAML ({_one_line(error)})", "correct the YAML"))
            return {}
        return _IncludedDict(content) if isinstance(content, dict) else content

    Loader.add_constructor("!include", include)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return None, [_problem("T01", str(path), f"the recipe file cannot be read ({error.strerror})", "check the path")]
    try:
        raw = yaml.load(text, Loader=Loader)
    except DuplicateKeyError as error:
        return None, problems + [_problem("T10", str(path.name), str(error), "remove or rename one of the two")]
    except yaml.YAMLError as error:
        return None, problems + [_problem("T01", str(path.name), f"the recipe is not valid YAML ({_one_line(error)})", "correct the YAML at that line")]
    return _walk(raw, "", problems), problems


def _one_line(error: Exception) -> str:
    return " ".join(str(error).split())


def check_recipe_file(path: Union[str, Path], profile: str = "run", **kwargs: Any) -> Result:
    """Read a recipe file strictly, then judge it: the problems of reading come first, then those of `check_recipe`."""
    path = Path(path)
    include_root = kwargs.pop("include_root", None)
    raw, read_problems = load_recipe(path, include_root=include_root)
    if raw is None:
        return Result(problems=read_problems, coverage={"structure"})
    kwargs.setdefault("file_stem", path.stem)
    kwargs.setdefault("base", project_root_of(path))
    if profile == "gallery":
        kwargs.setdefault("bundle_dir", path.parent)
    result = check_recipe(raw, profile, **kwargs)
    result.problems[:0] = read_problems
    return result
