"""Find links and file paths in the documents that point to files that do not exist.

Checks, in the tracked .md and .qmd files (records are skipped: logs, archives, `outdated/` folders, the change log, the dated evidence files, generated output):
  1. markdown links [text](relative/path) - the target must exist, relative to the document;
  2. file paths written in backticks (`app/src/bootloader.py`, `.claude/rules/x.md`) - the path
     must exist from the repository root. Paths with <>, *, {} or ... are patterns and are skipped.

Why: a rename moves files; every document that names one must follow (ADR-091).

Examples:
  .venv/bin/python assets/scripts/check_doc_links.py
  .venv/bin/python assets/scripts/check_doc_links.py --root ~/work/SPARMVET_VIZ_retest   # another copy
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SKIP_PREFIXES = (".claude/tasks/config_rename_", ".claude/tasks/outdated/", ".claude/knowledge/archive/", ".claude/design/home_evidence/", ".claude/knowledge/architecture_decisions.md", ".claude/knowledge/changelog.md", "docs/_freeze/", ".claude/logs/", ".claude/tasks/archives/", ".claude/conversations/",
                 ".claude/baselines/", "_book/", "docs/_site/", "tmp/", "tmpAI/")
PLACEHOLDER = re.compile(r"YYYY|MMDD|NAME|\bfoo\b|my_new|\{path\}|<[^>]+>")  # a pattern or an example, not a real path
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]{1,5})`")
ROOTS = ("app/", "libs/", "config/", "docs/", ".claude/", "assets/", "scripts/")


def tracked(root: Path):
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
    # a folder called outdated holds records of what was; they name files that are gone on purpose
    return [f for f in out.split("\n") if f.endswith((".md", ".qmd")) and not f.startswith(SKIP_PREFIXES) and "/outdated/" not in f]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."), help="repository copy to check (default: here)")
    ap.add_argument("--max", type=int, default=0, help="print at most N problems (0: all)")
    args = ap.parse_args()
    root = args.root.resolve()
    problems = []
    for f in tracked(root):
        text = (root / f).read_text(encoding="utf-8", errors="ignore")
        for n, line in enumerate(text.split("\n"), 1):
            for tgt in LINK.findall(line):
                if tgt.startswith(("http", "#", "mailto:", "/")):
                    continue
                path = tgt.split("#")[0]
                if path and not PLACEHOLDER.search(path) and not (root / f).parent.joinpath(path).exists() and not (root / path).exists():
                    problems.append((f, n, "link", tgt))
            for p in TICK.findall(line):
                if p.startswith(ROOTS) and not re.search(r"[<>*{}]|\.\.\.", p) and not PLACEHOLDER.search(p) and not (root / p).exists():
                    problems.append((f, n, "path", p))
    for f, n, kind, tgt in (problems[:args.max] if args.max else problems):
        print(f"{f}:{n}: {kind} -> {tgt}")
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
