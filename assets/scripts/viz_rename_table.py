"""The rename table of the plot components and a dry count of what the rename would touch (VIZ-REGISTRY-AUDIT-1).

Decision of Eve (2026-11-15, same as the Polars names, ADR-106 V1-B): a component that is exactly a plotnine object is
named `plotnine_<name>`; one with a documented change `modif_<name>`; one that is the project's own (a composite, a
convenience over one or several calls, a setter) `step_<name>`. The registry field `plotnine` (exact / modified / own)
says which; the prefix must agree with it.

This script changes NOTHING. It reads the registry and prints:

  table    every registered component: old name, proposed new name, class, registry field (all rows);
  count    how many tracked files and occurrences of an old name there are, by group of files, and how many of them
           the script can rewrite by itself (a recipe line `name: <old>`) and how many it cannot decide alone;
  hard     for each kind of occurrence that cannot be decided alone, a count and example lines.

The count is a dry run: a line is counted, never rewritten.

Examples:
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py table
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py table --format tsv > tmpAI/viz_rename_table.tsv
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py count --root .
  PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py hard --root . --examples 3

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py
# doc: .claude/design/viz_rename_impact_2026-11-15.md
# @end_deps
"""
import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

import viz_factory  # noqa: F401  (registers the components)
from viz_factory.registry import COMPONENT_SCHEMAS

PREFIX = {"exact": "plotnine_", "modified": "modif_", "own": "step_"}
# Words that are also ordinary English: counted only where they are certainly a component (a recipe `name:` line or a quoted string).
WORDS = {"labs", "guides", "annotate"}
SKIP_SUFFIXES = (".png", ".jpg", ".jpeg", ".svg", ".parquet", ".whl", ".woff", ".woff2", ".ico", ".pdf", ".zip", ".mdj", ".gz", ".xlsx", ".tsv", ".csv")


def component_class(name: str) -> str:
    """The family of a component, from its plotnine name."""
    for family in ("geom", "stat", "scale", "coord", "facet", "position", "theme", "element", "guide"):
        if name.startswith(family + "_") or name == family + "s":
            return "guide" if name == "guides" else family
    return {"labs": "label", "xlab": "label", "ylab": "label", "ggtitle": "label", "annotate": "annotation"}.get(name, "other")


def rows():
    out = []
    for old, schema in sorted(COMPONENT_SCHEMAS.items()):
        kind = schema["plotnine"]
        out.append({"old": old, "new": PREFIX[kind] + old, "class": component_class(old), "field": kind})
    return out


def print_table(fmt: str) -> None:
    data = rows()
    columns = ("old", "new", "class", "field")
    if fmt == "tsv":
        print("\t".join(columns))
        for r in data:
            print("\t".join(r[c] for c in columns))
        return
    print("| old name | new name | class | registry field |\n|---|---|---|---|")
    for r in data:
        print(f"| `{r['old']}` | `{r['new']}` | {r['class']} | {r['field']} |")
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
    if re.match(r"config/data_analysis_recipes/.*/plots/.*\.ya?ml$", p) or re.match(r"config/data_analysis_recipes/[^/]+/[^/]+/plots/", p):
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
    if p.startswith(("config/ui/agents", "libs/blueprint_arch/src")) or p == "app/modules/wrangle_studio.py" or p == "app/handlers/blueprint_handlers.py":
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
    return [f for f in listing if f and not f.endswith(SKIP_SUFFIXES)]


def classify_line(line: str, path: str, old: str) -> str:
    """What kind of occurrence of `old` this line holds (decided alone, or one of the hard kinds)."""
    escaped = re.escape(old)
    if path.endswith((".yaml", ".yml")):
        if re.search(rf"^\s*(-\s*)?name:\s*[\"']?{escaped}[\"']?\s*(#.*)?$", line) or re.search(rf"\{{\s*name:\s*[\"']?{escaped}[\"']?\s*[,}}]", line):
            return "decided: recipe line `name: <component>` (also in the flow form `{name: <component>, ...}`)"
        if re.match(rf"^\s*(-\s*)?theme:\s*[\"']?{escaped}[\"']?\s*(#.*)?$", line):
            return "decided with context: the `theme:` key of a plot spec or of plot_defaults (a component name; any other `theme:` is read first)"
        key = re.match(r"^\s*(-\s*)?([A-Za-z_]+):", line)
        if key and key.group(2) in ("description", "label", "comment", "title", "note", "text"):
            return "hard: written text inside a recipe (description, label, comment)"
        if key and key.group(2) in ("expression", "fun", "formula", "regex", "pattern"):
            return "hard: inside a formula or expression"
        if key:
            return f"hard: value of the key `{key.group(2)}` (a parameter value or a taxonomy field, not a component call)"
        return "hard: recipe comment or continuation line"
    if path.endswith(".json"):
        return "hard: a JSON field (the gallery index)"
    if path.endswith(".py"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return "hard: Python comment"
        if re.search(rf"[\"']{escaped}[\"']", line):
            return "code: a quoted name in Python (a registration, a list, a test; read each one)"
        if re.search(rf"\b{escaped}\b", line) and re.search(r"\bimport\b|\bfrom\b|\)\s*$|\(", line):
            return "code: a plotnine function call or import (plotnine's own name, stays)"
        return "hard: Python docstring or text"
    return "hard: prose in a document"


def count(root: Path, examples: int, show_hard: bool) -> None:
    names = sorted(COMPONENT_SCHEMAS, key=len, reverse=True)
    pattern = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z0-9_])")
    per_group = collections.defaultdict(lambda: {"files": set(), "lines": 0, "kinds": collections.Counter()})
    samples = collections.defaultdict(list)
    for path in tracked_files(root):
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        for number, line in enumerate(text.split("\n"), 1):
            for match in pattern.finditer(line):
                old = match.group(1)
                kind = classify_line(line, path, old)
                if old in WORDS and kind.startswith("hard: prose"):
                    kind = "skipped: an ordinary English word in prose"
                    continue
                entry = per_group[group_of(path)]
                entry["files"].add(path)
                entry["lines"] += 1
                entry["kinds"][kind] += 1
                key = (group_of(path), kind)
                example = f"{path}:{number}: {line.strip()[:150]}"
                if kind.startswith(("hard", "code", "decided with")) and len(samples[key]) < examples and example not in samples[key]:
                    samples[key].append(example)
    print("| group of files | files | occurrences | decided alone (recipe `name:` line) | to read or decide |\n|---|---|---|---|---|")
    total = collections.Counter()
    for group, entry in sorted(per_group.items(), key=lambda kv: -kv[1]["lines"]):
        decided = sum(v for k, v in entry["kinds"].items() if k.startswith("decided: "))
        other = entry["lines"] - decided
        print(f"| {group} | {len(entry['files'])} | {entry['lines']} | {decided} | {other} |")
        total["files"] += len(entry["files"])
        total["lines"] += entry["lines"]
        total["decided"] += decided
    print(f"| TOTAL | {total['files']} | {total['lines']} | {total['decided']} | {total['lines'] - total['decided']} |")
    if show_hard:
        print("\nKinds that the script cannot decide alone, by group (count, then examples):\n")
        kinds = collections.defaultdict(collections.Counter)
        for group, entry in per_group.items():
            for kind, n in entry["kinds"].items():
                if not kind.startswith("decided: "):
                    kinds[kind][group] += n
        for kind, by_group in sorted(kinds.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"- {kind}: {sum(by_group.values())} lines ({', '.join(f'{g}: {n}' for g, n in by_group.most_common(4))})")
            shown = 0
            for (group, k), lines in samples.items():
                if k == kind and shown < examples:
                    for example in lines[: examples - shown]:
                        print(f"    {example}")
                        shown += 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("table", "count", "hard"), help="table: every component, old -> new; count: dry count by group of files; hard: count plus examples of what cannot be decided alone")
    parser.add_argument("--root", default=".", help="repository root for count and hard (default: the current directory)")
    parser.add_argument("--format", choices=("md", "tsv"), default="md", help="format of the table (default: md)")
    parser.add_argument("--examples", type=int, default=2, help="example lines per kind in `hard` (default: 2)")
    args = parser.parse_args(argv)
    if args.mode == "table":
        print_table(args.format)
    else:
        count(Path(args.root).resolve(), args.examples, show_hard=args.mode == "hard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
