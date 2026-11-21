# engine: python-plotnine (the table of old plot component names and the plotnine names that replace them)
"""The rename table of the plot components, a dry count of what the rename would touch, and the code that reads the shape of a name.

Decision of Eve (2026-11-15, same as the Polars names, ADR-106 V1-B): a component that is exactly a plotnine object is
named `plotnine_<name>`; one with a documented change `modif_<name>`; one that is the project's own (a composite, a
convenience over one or several calls, a setter) `step_<name>`. The registry field `plotnine` (exact / modified / own)
says which; the prefix must agree with it.

This script changes NOTHING. It reads the registry and the tracked files and prints:

  table    every registered component: old name, proposed new name, family, registry field, prefix (all rows);
  count    every occurrence of an old component name in the tracked files, in THREE separate counts per group of files:
             MUST CHANGE  a recipe line `name: <component>`, a `theme:` key, a component name written as a string in code or tests;
             STAYS        a direct plotnine call or import (plotnine's own name), the value of a `stat` / `position` / `geom` parameter,
                          history files (logs, archives, old conversations), kept as they were;
             READ         a name inside a sentence, a comment, a docstring or a message: a person reads it (also every rule file);
  sample   a random sample of occurrences of each class, to judge the classification by eye (`--per-class`, `--seed`);
  sites    every place in the code that tests a component name by its start or its parts (`startswith("geom_")`,
           `.split("_")`, a prefix string, a regular expression with the family names), found by parsing the Python files
           under libs/, app/ and assets/scripts/, with file:line;
  report   table, count and sites in one run (the command that regenerates every number of the impact document).

The document `.claude/design/viz_rename_impact_2026-11-15.md` and this script are left out of the count (they name every old name).
A line is counted once per name on it. The count is a dry run: nothing is rewritten.

Examples:
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py report --root .
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py table --format tsv > tmpAI/viz_rename_table.tsv
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py count --root .
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py sample --root . --per-class 30 --seed 1
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py sites --root .

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py
# doc: .claude/design/viz_rename_impact_2026-11-15.md
# @end_deps
"""
import argparse
import ast
import collections
import io
import random
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import viz_factory  # noqa: F401  (registers the components)
from viz_factory.registry import COMPONENT_SCHEMAS

PREFIX = {"exact": "plotnine_", "modified": "modif_", "own": "step_"}
FAMILIES = ("geom", "stat", "scale", "theme", "facet", "coord", "guide", "position", "element")
# Words that are also ordinary English: a hit in prose is not counted (they are certain only in a recipe or a quoted string).
WORDS = {"labs", "guides", "annotate"}
SKIP_SUFFIXES = (".png", ".jpg", ".jpeg", ".svg", ".parquet", ".whl", ".woff", ".woff2", ".ico", ".pdf", ".zip", ".mdj", ".gz", ".xlsx", ".tsv", ".csv")
EXCLUDED = {"assets/scripts/viz_rename_table.py", ".claude/design/viz_rename_impact_2026-11-15.md"}
CODE_ROOTS = ("libs/", "app/", "assets/scripts/")
MUST, STAYS, READ = "MUST CHANGE", "STAYS", "READ"
PARAMETER_KEYS = {"stat", "position", "geom"}


def component_family(name: str) -> str:
    """The family of a component, from its plotnine name."""
    for family in FAMILIES:
        if name.startswith(family + "_"):
            return family
    if name == "guides":
        return "guide"
    return {"labs": "label", "xlab": "label", "ylab": "label", "ggtitle": "label", "annotate": "annotation"}.get(name, "other")


def rows():
    out = []
    for old, schema in sorted(COMPONENT_SCHEMAS.items()):
        kind = schema["plotnine"]
        out.append({"old": old, "new": PREFIX[kind] + old, "family": component_family(old), "field": kind, "prefix": PREFIX[kind]})
    return out


def print_table(fmt: str) -> None:
    data = rows()
    columns = ("old", "new", "family", "field", "prefix")
    if fmt == "tsv":
        print("\t".join(columns))
        for r in data:
            print("\t".join(r[c] for c in columns))
        return
    print("| old name | new name | family | registry field (exact / modified / own) | prefix that follows |\n|---|---|---|---|---|")
    for r in data:
        print(f"| `{r['old']}` | `{r['new']}` | {r['family']} | {r['field']} | `{r['prefix']}` |")
    counts = collections.Counter(r["field"] for r in data)
    print(f"\n{len(data)} components: " + ", ".join(f"{counts[k]} {k} -> `{PREFIX[k]}`" for k in PREFIX))


def group_of(path: str) -> str:
    """The group of files a path belongs to (the groups of the impact list)."""
    p = path
    if p.startswith(".claude/rules/"):
        return "rule files (listed, never edited by the rename)"
    if p.startswith((".claude/logs/", ".claude/conversations/", ".claude/tasks/archives", ".claude/tasks/outdated", ".claude/design/outdated")):
        return "history: logs, archives (kept as they were)"
    if p.startswith(".claude/"):
        return "records: design, knowledge, tasks, workflows"
    if re.match(r"config/data_analysis_recipes/.*/plots/.*\.ya?ml$", p):
        return "plot spec files"
    if p.startswith("config/data_analysis_recipes/pipelines"):
        return "pipeline recipes (outside plots/)"
    if p.startswith("config/data_analysis_recipes/templates"):
        return "template recipes"
    if p.startswith("config/data_analysis_recipes/retest"):
        return "retest recipes"
    if p.startswith("config/data_analysis_recipes"):
        return "other recipes in config"
    if p.startswith("assets/gallery_data"):
        return "gallery recipes and index"
    if p.startswith(("config/ui/agents", "libs/blueprint_arch/src")) or p in ("app/modules/wrangle_studio.py", "app/handlers/blueprint_handlers.py"):
        return "Blueprint pickers, forms and the agent tool"
    if p.startswith("libs/viz_factory/src"):
        return "viz library code (registration and name logic)"
    if p.startswith("libs/viz_factory/tests"):
        return "viz library tests"
    if "/tests/" in p or p.startswith("app/tests"):
        return "other tests"
    if p.startswith("docs/") or p.endswith(".qmd") or "README" in p:
        return "docs pages and READMEs"
    if p.startswith(("libs/", "app/")):
        return "other code (libs, app)"
    if p.startswith(("assets/scripts", "scripts")):
        return "scripts"
    return "other"


def tracked_files(root: Path):
    listing = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout.split("\n")
    return [f for f in listing if f and not f.endswith(SKIP_SUFFIXES) and f not in EXCLUDED]


def name_pattern():
    names = sorted(COMPONENT_SCHEMAS, key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z0-9_])")


def recipe_line(line: str, old: str):
    """(class, kind) when the line is a recipe line that names `old` as a component, or a `theme:` key holding it; else None."""
    escaped = re.escape(old)
    if re.search(rf"^\s*(-\s*)?name:\s*[\"']?{escaped}[\"']?\s*(#.*)?$", line) or re.search(rf"\{{\s*name:\s*[\"']?{escaped}[\"']?\s*[,}}]", line):
        return MUST, "a recipe line `name: <component>` (block or flow form)"
    if re.match(rf"^\s*(-\s*)?theme:\s*[\"']?{escaped}[\"']?\s*(#.*)?$", line):
        return MUST, "the `theme:` key of a plot spec or of plot_defaults (a component name; a `theme:` elsewhere is read first)"
    key = re.match(rf"^\s*(-\s*)?({'|'.join(PARAMETER_KEYS)}):\s*[\"']?{escaped}[\"']?\s*(#.*)?$", line)
    if key:
        return STAYS, f"the value of the parameter `{key.group(2)}` (plotnine's own object; proposal Q5)"
    return None


def classify_text_line(line: str, path: str, old: str):
    """Class and kind of an occurrence in a yaml, json or document line."""
    if path.startswith(".claude/rules/"):
        return READ, "a rule file (listed, edited only after Eve's yes)"
    if group_of(path).startswith("history"):
        return STAYS, "a history file, kept as it was"
    if path.endswith(".md") and re.match(r"^>\s.*\u2699\ufe0f?\s*" + re.escape(old) + r"\b", line):
        return STAYS, "the tag strip of a gallery example (generated from the `geom` taxonomy field; proposal Q5)"
    found = recipe_line(line, old) if path.endswith((".yaml", ".yml", ".md", ".qmd", ".txt")) else None
    if found:
        return found
    if path.endswith(".json") and re.search(rf"\"geom\"\s*:\s*\"{re.escape(old)}\"", line):
        return STAYS, "the `geom` field of the gallery index (the exact plotnine function name; proposal Q5)"
    if path.endswith((".yaml", ".yml")):
        key = re.match(r"^\s*(-\s*)?([A-Za-z_]+):", line)
        if key and key.group(2) in ("expression", "fun", "formula", "regex", "pattern"):
            return READ, "a name inside a formula or expression"
        if key and key.group(2) in ("description", "label", "comment", "title", "note", "text", "reason"):
            return READ, "written text in a recipe (description, label, comment)"
        if key:
            return READ, f"the value of the key `{key.group(2)}`"
        return READ, "a recipe comment or continuation line"
    return READ, "prose"


def python_spans(text: str):
    """Spans of a Python file: comments, string constants (with their role), identifiers and imports, to classify a name by where it is."""
    spans = []  # (start, end, kind, extra); positions are (line, col)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docstrings.add(first.value)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            role = "doc" if node in docstrings else "plain"
            parent = parents.get(node)
            if isinstance(parent, ast.Dict):
                for key, value in zip(parent.keys, parent.values):
                    if value is node and isinstance(key, ast.Constant) and key.value in PARAMETER_KEYS:
                        role = "parameter"
            if isinstance(parent, ast.keyword) and parent.arg in PARAMETER_KEYS:
                role = "parameter"
            holder = parents.get(parent)
            if isinstance(parent, ast.List) and isinstance(holder, ast.Dict):
                for key, value in zip(holder.keys, holder.values):
                    if value is parent and isinstance(key, ast.Constant) and key.value == "attr_path":
                        role = "plotnine"  # `wraps` names the plotnine object itself
            spans.append(((node.lineno, node.col_offset), (node.end_lineno, node.end_col_offset), "string", (role, node.value)))
        elif isinstance(node, (ast.Name, ast.Attribute)):
            spans.append(((node.lineno, node.col_offset), (node.end_lineno, node.end_col_offset), "identifier", None))
        elif isinstance(node, (ast.ImportFrom, ast.Import)):
            spans.append(((node.lineno, node.col_offset), (node.end_lineno, node.end_col_offset), "import", None))
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.COMMENT:
            spans.append((token.start, token.end, "comment", None))
    return spans


def classify_python(spans, line_no: int, col: int, line: str, old: str):
    """Class and kind of an occurrence in Python: by the innermost thing that contains it."""
    position = (line_no, col)
    inside = [span for span in spans if span[0] <= position < span[1]]
    # the innermost: the shortest in lines, then in columns
    best = min(inside, key=lambda span: (span[1][0] - span[0][0], span[1][1] - span[0][1] if span[1][0] == span[0][0] else 0), default=None)
    if best is None:
        return READ, "Python text outside a string or identifier"
    _, _, kind, extra = best
    if kind == "comment":
        return READ, "a Python comment"
    if kind in ("import", "identifier"):
        return STAYS, "a direct plotnine call or import (plotnine's own name)"
    role, value = extra
    if role == "doc":
        return READ, "a docstring"
    if role == "plotnine":
        return STAYS, "the `wraps` entry that names the plotnine object itself"
    if role == "parameter":
        return STAYS, "the value of a `stat` / `position` / `geom` parameter (plotnine's own object; proposal Q5)"
    if "\n" in value:
        for value_line in value.split("\n"):
            found = recipe_line(value_line, old) if old in value_line else None
            if found:
                return found[0], "recipe text inside a string: " + found[1]
        return READ, "text inside a multi-line string"
    if value.strip() == old:
        return MUST, "a component name written as a whole string (a registration, a list, an assertion)"
    found = recipe_line(value, old)
    if found:
        return found
    return READ, "a name inside a sentence or message"


def occurrences(root: Path):
    """Every occurrence of an old name: (path, line number, line text, old name, class, kind)."""
    pattern = name_pattern()
    for path in tracked_files(root):
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if not pattern.search(text):
            continue
        spans = python_spans(text) if path.endswith(".py") else None
        for number, line in enumerate(text.split("\n"), 1):
            for match in pattern.finditer(line):
                old = match.group(1)
                if path.endswith(".py") and spans is not None:
                    klass, kind = classify_python(spans, number, match.start(), line, old)
                    if path.startswith(".claude/") or group_of(path).startswith("history"):
                        klass, kind = (STAYS, "a history file, kept as it was") if group_of(path).startswith("history") else (klass, kind)
                else:
                    klass, kind = classify_text_line(line, path, old)
                if old in WORDS and klass == READ and kind in ("prose", "a name inside a sentence or message", "a docstring", "a Python comment"):
                    continue
                yield path, number, line, old, klass, kind


def count(root: Path) -> None:
    per_group = collections.defaultdict(lambda: {"files": set(), MUST: 0, STAYS: 0, READ: 0})
    kinds = collections.defaultdict(collections.Counter)
    for path, _, _, _, klass, kind in occurrences(root):
        entry = per_group[group_of(path)]
        entry["files"].add(path)
        entry[klass] += 1
        kinds[klass][kind] += 1
    print("| group of files | files with a name | MUST CHANGE | STAYS | READ by a person | all |\n|---|---|---|---|---|---|")
    total = collections.Counter()
    all_files = set()
    for group, entry in sorted(per_group.items(), key=lambda kv: -(kv[1][MUST] + kv[1][STAYS] + kv[1][READ])):
        line_total = entry[MUST] + entry[STAYS] + entry[READ]
        print(f"| {group} | {len(entry['files'])} | {entry[MUST]} | {entry[STAYS]} | {entry[READ]} | {line_total} |")
        total.update({MUST: entry[MUST], STAYS: entry[STAYS], READ: entry[READ]})
        all_files |= entry["files"]
    print(f"| TOTAL | {len(all_files)} | {total[MUST]} | {total[STAYS]} | {total[READ]} | {total[MUST] + total[STAYS] + total[READ]} |")
    print("\nBy kind of occurrence:\n")
    for klass in (MUST, STAYS, READ):
        print(f"- {klass}: {total[klass]}")
        for kind, n in kinds[klass].most_common():
            print(f"    - {n}: {kind}")


def sample(root: Path, per_class: int, seed: int) -> None:
    by_class = collections.defaultdict(list)
    for item in occurrences(root):
        by_class[item[4]].append(item)
    rng = random.Random(seed)
    for klass in (MUST, STAYS, READ):
        items = by_class[klass]
        print(f"\n## {klass}: {per_class} of {len(items)} occurrences (seed {seed})\n")
        for index, (path, number, line, old, _, kind) in enumerate(rng.sample(items, min(per_class, len(items))), 1):
            print(f"{index:2}. {path}:{number}: `{old}` [{kind}] | {line.strip()[:110]}")


SITE_PREFIX = re.compile(rf"^({'|'.join(FAMILIES)})_([a-z_0-9]*_)?$")
SITE_REGEX = re.compile(rf"\(\?:?({'|'.join(FAMILIES)})|\^({'|'.join(FAMILIES)})|\b({'|'.join(FAMILIES)})\|")


def find_sites(root: Path):
    """(path, line, call, detail) for every test of a component name by its start or its parts, under libs/, app/, assets/scripts/."""
    found = set()
    for path in subprocess.run(["git", "ls-files", *CODE_ROOTS], cwd=root, capture_output=True, text=True, check=True).stdout.split():
        if not path.endswith(".py") or path in EXCLUDED:
            continue
        try:
            tree = ast.parse((root / path).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                strings = [c.value for a in node.args for c in ast.walk(a) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
                attr = node.func.attr
                if attr in ("startswith", "removeprefix", "lstrip") and any(re.match(rf"^({'|'.join(FAMILIES)})_", s) for s in strings):
                    found.add((path, node.lineno, f".{attr}()", ", ".join(sorted(set(strings)))))
                if attr in ("split", "rsplit", "partition") and strings[:1] == ["_"]:
                    found.add((path, node.lineno, f".{attr}(\"_\")", "splits a name into its parts"))
                if attr in ("match", "search", "fullmatch", "compile", "sub", "findall") and any(SITE_REGEX.search(s) for s in strings):
                    found.add((path, node.lineno, f"re.{attr}", next(s for s in strings if SITE_REGEX.search(s))[:60]))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and SITE_PREFIX.match(node.value):
                found.add((path, node.lineno, "prefix string", node.value))
            elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice) and isinstance(node.slice.upper, ast.Constant) and isinstance(node.slice.lower, type(None)):
                pass
    return sorted(found)


def print_sites(root: Path) -> None:
    by_line = collections.OrderedDict()
    for path, line, call, detail in find_sites(root):
        by_line.setdefault((path, line), [])
        what = f"{call} {detail}"
        # a `.startswith("theme_")` already names its prefix: do not list the same string twice
        if call == "prefix string" and any(call2.startswith((".startswith", ".removeprefix", ".lstrip")) and detail in d2 for call2, d2 in
                                           (w.split(" ", 1) for w in by_line[(path, line)])):
            continue
        by_line[(path, line)].append(what)
    # a second pass: drop prefix strings that a `.startswith()` of the same line names
    for key, whats in by_line.items():
        starts = " ".join(w for w in whats if w.startswith("."))
        by_line[key] = [w for w in whats if not (w.startswith("prefix string") and w.split(" ", 2)[2] in starts)]
    print("| file:line | what it does with a name |\n|---|---|")
    for (path, line), what in by_line.items():
        print(f"| `{path}:{line}` | {'; '.join(what)} |")
    files = {path for path, _ in by_line}
    production = [key for key in by_line if "/tests/" not in key[0] and not key[0].startswith("assets/scripts")]
    print(f"\n{len(by_line)} lines in {len(files)} files; {len(production)} lines in {len({p for p, _ in production})} production files (the rest in tests and scripts)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("table", "count", "sample", "sites", "report"),
                        help="table: every component, old -> new; count: dry count in three classes; sample: lines to judge the classification; "
                             "sites: code that tests a name by its start; report: table, count and sites in one run")
    parser.add_argument("--root", default=".", help="repository root (default: the current directory)")
    parser.add_argument("--format", choices=("md", "tsv"), default="md", help="format of the table (default: md)")
    parser.add_argument("--per-class", type=int, default=30, help="lines per class in `sample` (default: 30)")
    parser.add_argument("--seed", type=int, default=1, help="seed of the sample (default: 1)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.mode == "table":
        print_table(args.format)
    elif args.mode == "count":
        count(root)
    elif args.mode == "sample":
        sample(root, args.per_class, args.seed)
    elif args.mode == "sites":
        print_sites(root)
    else:
        print("## Table\n")
        print_table("md")
        print("\n## Count\n")
        count(root)
        print("\n## Sites that test a name by its start\n")
        print_sites(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
