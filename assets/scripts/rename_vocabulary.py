"""Build the mapping table for the configuration rename (ADR-091) from the rules file.

Read-only in this form: it finds every token and every tracked path that contains a retired
word (persona, manifest, recipe, profile), proposes the new name from
assets/scripts/rename_vocabulary_rules.yaml, and writes a Markdown table that Eve reviews
before any file is changed. Tokens whose new name depends on the context are marked
CONTEXT; tokens that still contain a retired word after the rules are marked UNMAPPED and
must be zero before the table is approved.

The audit exclusions of assets/scripts/audit_old_words.py (history, the two AI agent files)
are respected.

Examples:
  .venv/bin/python assets/scripts/rename_vocabulary.py --out .claude/tasks/config_rename_mapping.md
  .venv/bin/python assets/scripts/rename_vocabulary.py --unmapped
"""

import argparse
import importlib.util
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
RULES = HERE / "rename_vocabulary_rules.yaml"
_spec = importlib.util.spec_from_file_location("audit_old_words", HERE / "audit_old_words.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)

TOKEN = re.compile(r"[A-Za-z0-9_\-]*(?:persona|manifest|recipe|profile|connector_(?:config|path|template|cache)|sparmvet_connector|local_connector)[A-Za-z0-9_\-]*", re.I)
RETIRED = re.compile(r"persona|manifest|recipe|profile|connector_(?:config|path|template|cache)|sparmvet_connector", re.I)
CONTEXT = "STEPS_OR_RECIPE_BY_CONTEXT"


def camel(snake: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in snake.split("_") if p)


def forms(old: str, new: str):
    """The pair in snake, Camel and UPPER spelling."""
    yield old, new
    if "_" in old or True:
        yield camel(old), camel(new) if new != CONTEXT else CONTEXT
    yield old.upper(), new.upper() if new != CONTEXT else CONTEXT


def load_pairs():
    rules = yaml.safe_load(RULES.read_text())
    pairs = []
    for old, new in rules["pairs"]:
        pairs.extend(forms(old, new))
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs, rules


def _substitute(text: str, pairs) -> str:
    """Apply all pairs in ONE pass (longest first), so a new name is never rewritten again."""
    table = dict(pairs)
    rx = re.compile("|".join(re.escape(o) for o, _ in pairs))
    return rx.sub(lambda m: table[m.group(0)], text)


def transform(token: str, pairs, keep):
    """Return (new_token, status) with status auto, CONTEXT, keep or UNMAPPED."""
    marks = {}
    masked = token
    for i, k in enumerate(keep):
        for m in list(re.finditer(re.escape(k), masked, re.I)):
            tag = f"\x00{len(marks)}\x00"
            marks[tag] = m.group(0)
            masked = masked.replace(m.group(0), tag, 1)
    out = _substitute(masked, pairs)
    for tag, val in marks.items():
        out = out.replace(tag, val)
    if out == token:
        return out, "keep"
    if "REMOVE_" in out:
        return out, "REMOVE"
    if CONTEXT in out:
        return out, "CONTEXT"
    leftover = out
    for val in marks.values():
        leftover = leftover.replace(val, "")
    # the new term contains the word recipe on purpose
    leftover = re.sub(r"data_analysis_recipe|DataAnalysisRecipe|DATA_ANALYSIS_RECIPE", "", leftover)
    return out, ("UNMAPPED" if RETIRED.search(leftover) else "auto")


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.split("\n") if f and not audit.is_excluded(f) and f != "tree.txt"]


def new_path(path: str, pairs, keep, rules):
    p = path
    for old, new in rules["paths"].items():
        if old == "drop_suffix":
            continue
        if p.startswith(old + "/") or p == old:
            p = new + p[len(old):]
    parts = p.split("/")
    out = []
    for seg in parts:
        seg2, _ = transform(seg, pairs, keep)
        out.append(seg2)
    p = "/".join(out)
    if p.startswith("config/app_features/") and p.endswith("_template.yaml"):
        p = p[: -len("_template.yaml")] + ".yaml"
    # deployment files: the folder already says deployment, so the suffix is dropped
    if p.startswith("config/deployment/"):
        p = p.replace("_deployment_template.yaml", "_template.yaml").replace("_deployment.yaml", ".yaml")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", metavar="PATH", help="write the Markdown mapping table here")
    ap.add_argument("--unmapped", action="store_true", help="print only the UNMAPPED tokens and exit 1 if any")
    args = ap.parse_args()

    pairs, rules = load_pairs()
    keep = [k.lower() for k in rules["keep_substrings"]]
    files = tracked_files()

    count: Counter = Counter()
    where: dict = defaultdict(Counter)
    for f in files:
        try:
            text = Path(f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            text = ""
        for tok in TOKEN.findall(text):
            count[tok] += 1
            where[tok][f] += 1

    rows = []
    for tok, n in count.items():
        new, status = transform(tok, pairs, keep)
        if status == "keep" and new == tok:
            pass
        rows.append((tok, n, new, status))
    unmapped = sorted(r for r in rows if r[3] == "UNMAPPED")

    path_rows = []
    for f in files:
        if RETIRED.search(f):
            np_ = new_path(f, pairs, keep, rules)
            path_rows.append((f, np_, "auto" if np_ != f else "keep"))

    if args.unmapped:
        for r in unmapped:
            print(f"{r[1]:>5}  {r[0]}  ->  {r[2]}")
        print(f"{len(unmapped)} unmapped")
        return 1 if unmapped else 0

    by_status = Counter(r[3] for r in rows)
    lines = ["# Rename mapping table (generated)", "",
             "Generated by `assets/scripts/rename_vocabulary.py` from `assets/scripts/rename_vocabulary_rules.yaml`.",
             "Eve approves the rules and this table before any file is changed (task CONFIG-MAPPING-1).", "",
             f"- distinct tokens: {len(rows)}   occurrences: {sum(count.values())}",
             f"- by status: " + ", ".join(f"{k} {v}" for k, v in sorted(by_status.items())),
             f"- tracked paths to rename: {sum(1 for p in path_rows if p[2] == 'auto')} of {len(path_rows)} paths containing a retired word", "",
             "Status: `auto` the rules decide; `CONTEXT` the bare word `recipe` or `recipes`, decided by the area it is in (see below); `keep` a domain term; `UNMAPPED` needs a rule.", ""]
    lines += ["## Tokens that need a decision by context", "",
              "| token | count | main places |", "|---|---|---|"]
    for tok, n, new, st in sorted((r for r in rows if r[3] == "CONTEXT"), key=lambda r: -r[1]):
        places = ", ".join(f"{k.split('/')[0]}/{k.split('/')[1] if '/' in k else ''}:{v}" for k, v in where[tok].most_common(3))
        lines.append(f"| `{tok}` | {n} | {places} |")
    lines += ["", "## Unmapped", ""]
    lines += [f"- `{r[0]}` ({r[1]}) -> `{r[2]}`" for r in unmapped] or ["none"]
    lines += ["", "## Tokens (all)", "", "| old | count | new | status |", "|---|---|---|---|"]
    for tok, n, new, st in sorted(rows, key=lambda r: (-r[1], r[0])):
        lines.append(f"| `{tok}` | {n} | `{new}` | {st} |")
    lines += ["", "## Paths", "", "| old path | new path | status |", "|---|---|---|"]
    for old, new, st in sorted(path_rows):
        lines.append(f"| `{old}` | `{new}` | {st} |")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
        print(f"wrote {args.out}: {len(rows)} tokens, {len(unmapped)} unmapped, {len(path_rows)} paths")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
