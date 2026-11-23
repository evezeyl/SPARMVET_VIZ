"""DRY RUN of the one big move: lists, for the owner, every change the move would make to the shipped recipes and their data.

THE SCRIPT WRITES NOTHING EXCEPT ITS REPORT (the file named with --report: a NEW file; inside the project folder only under
tmpAI/). There is no --apply. It never runs the engine and never guesses: where no rule decides, the place is listed under
"needs the owner".

Sections (each line: file, line, what stands there now, what would stand there, the ledger number of the rule):
  1. the names pass (the list of assets/scripts/migrate_display_names.py, reused, not duplicated)           D-0407 to D-0412, D-0468 to D-0484
  2. `is_entity_key` -> `is_entity_id`: every line that holds it, counted per kind of file                  D-0562, D-0567
  3. the joined tables whose FIRST ingredient is the metadata block (and tables whose only one it is)       D-0586
  4. the tier files that end with a polars_select / polars_drop (the fixed column lists)                    D-0586, D-0587
  5. the tables that declare no entity id (a name like sample_id is shown as a CANDIDATE only)              D-0569
  6. the lines of each metadata file whose id cell is empty, only spaces, or a declared null value          D-0569, D-0594
  7. the tables under `additional_datasets_schemas` that declare the entity id                              the owner's earlier point (no ledger number given)

Shipped recipes read: config/data_analysis_recipes (recipes and templates) and assets/gallery_data/*/data_analysis_recipe.yaml.

Examples:
  PYTHONPATH=. ./.venv/bin/python assets/scripts/dry_run_big_move.py --project-root . --report tmpAI/dry_run_big_move_report.md
  PYTHONPATH=. ./.venv/bin/python assets/scripts/dry_run_big_move.py --help
"""

# @deps
# provides: script:dry_run_big_move
# consumes: assets/scripts/migrate_display_names.py (build_plan, lines_of, report_refusal)
# consumed_by: app/tests/test_dry_run_big_move.py
# doc: .claude/knowledge/decision_ledger.md (D-0562, D-0567, D-0569, D-0586, D-0587, D-0594), .claude/rules/rules_asset_scripts.md
# @end_deps
import argparse
import csv
import datetime
import importlib.util
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from utils import action_names

SCRIPT_DIR = Path(__file__).resolve().parent
OLD_KEY = "is_entity_key"
NEW_KEY = "is_entity_id"
METADATA = "metadata_schema"
# the actions that REPLACE the set of columns, as far as libs/utils/src/utils/step_effects.py READINGS tells: a select keeps only its list,
# a group-by keeps only its keys and its aggregates. Pivot, unpivot and similar steps are not in that source and are not examined.
KEEP_ONLY_ACTIONS = (action_names.SELECT, action_names.GROUP_BY)
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "tmpAI", "tmp"}
CANDIDATE = re.compile(r"^(sample_?id|sample|isolate_?id|isolate|accession|id|strain|strain_?id)$", re.I)
DROP_NULLS = action_names.DROP_NULLS
MARKER_WAYS = ("a marker column that exists before this step is not carried unless it is in the list; her two ways (D-0587): add the marker columns "
               "to the list, or treat the marked lines at tier 1 and drop the marker by a visible step; this script does not choose")


def _load_names_tool():
    spec = importlib.util.spec_from_file_location("migrate_display_names", SCRIPT_DIR / "migrate_display_names.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@dataclass
class Report:
    sections: Dict[int, List[str]] = field(default_factory=dict)
    counts: Dict[int, int] = field(default_factory=dict)
    owner: List[str] = field(default_factory=list)

    stat: Dict[str, int] = field(default_factory=dict)
    texts: Dict[str, List[str]] = field(default_factory=dict)

    def add(self, n, line: str, count: Optional[bool] = None) -> None:
        """An entry is a line that starts with '- ' (it is counted); everything else (headings, '* ' summaries, blank lines) is not."""
        self.sections.setdefault(n, []).append(line)
        if count is None:
            count = line.startswith("- ")
        if count and isinstance(n, int):
            self.counts[n] = self.counts.get(n, 0) + 1

    def bump(self, key: str, by: int = 1) -> None:
        self.stat[key] = self.stat.get(key, 0) + by

    def say(self, key: str, text: str) -> None:
        self.texts.setdefault(key, []).append(text)

    def need(self, where: str, why: str) -> None:
        self.owner.append(f"{where}: {why}")


# -- YAML with includes ----------------------------------------------------------------------------------------------------

class Recipes:
    """Reads a recipe as YAML nodes; an `!include` is followed to its file, so that every line number is the line of the file
    where the text stands. Nothing is constructed or run."""

    def __init__(self, root: Path, report: Report):
        self.root = root
        self.report = report
        self.cache: Dict[Path, Optional[Tuple[str, yaml.Node]]] = {}

    def rel(self, p: Path) -> str:
        try:
            return str(p.relative_to(self.root))
        except ValueError:
            return str(p)

    def load(self, path: Path) -> Optional[yaml.Node]:
        if path not in self.cache:
            try:
                text = path.read_text(encoding="utf-8")
                self.cache[path] = (text, yaml.compose(text, Loader=yaml.SafeLoader))
            except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
                self.cache[path] = None
                self.report.need(self.rel(path), f"the file cannot be read as YAML ({type(exc).__name__}); it is not examined")
        entry = self.cache[path]
        return entry[1] if entry else None

    def follow(self, node, cur: Path, master: Path):
        """(node, file) with every `!include` followed; (None, cur) when an included file is missing."""
        for _ in range(12):
            if isinstance(node, yaml.ScalarNode) and node.tag == "!include":
                target = None
                for base in (cur.parent, master.parent, self.root):
                    cand = base / node.value
                    if cand.is_file():
                        target = cand
                        break
                if target is None:
                    self.report.need(f"{self.rel(cur)}:{node.start_mark.line + 1}", f"`!include {node.value}` names a file that was not found")
                    return None, cur
                cur = target
                node = self.load(cur)
                if node is None:
                    return None, cur
            else:
                return node, cur
        return None, cur


def mp(node) -> Dict[str, Tuple[yaml.Node, yaml.Node]]:
    return {k.value: (k, v) for k, v in node.value} if isinstance(node, yaml.MappingNode) else {}


def seq(node) -> list:
    return list(node.value) if isinstance(node, yaml.SequenceNode) else []


def scalar(node) -> Optional[str]:
    return node.value if isinstance(node, yaml.ScalarNode) else None


def flow_text(node) -> str:
    if isinstance(node, yaml.ScalarNode):
        return node.value
    if isinstance(node, yaml.SequenceNode):
        return "[" + ", ".join(flow_text(n) for n in node.value) + "]"
    if isinstance(node, yaml.MappingNode):
        return "{" + ", ".join(f"{k.value}: {flow_text(v)}" for k, v in node.value) + "}"
    return "?"


def truthy(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.value.strip().lower() in ("true", "yes", "on")


# -- discovery -------------------------------------------------------------------------------------------------------------

def recipe_files(root: Path) -> List[Tuple[Path, str]]:
    out: List[Tuple[Path, str]] = []
    base = root / "config/data_analysis_recipes"
    if base.is_dir():
        for p in sorted(base.rglob("*.yaml")):
            kind = "recipe template" if "templates" in p.relative_to(base).parts else "recipe"
            out.append((p, kind))
    gal = root / "assets/gallery_data"
    if gal.is_dir():
        for p in sorted(gal.glob("*/data_analysis_recipe.yaml")):
            out.append((p, "Gallery bundle"))
    return out


def masters(R: Recipes) -> List[Tuple[Path, str, yaml.MappingNode]]:
    found = []
    for path, kind in recipe_files(R.root):
        node = R.load(path)
        if isinstance(node, yaml.MappingNode) and "spec_version" in mp(node):
            found.append((path, kind, node))
    return found


def blocks_of(R: Recipes, master: Path, top: yaml.MappingNode, section: str):
    """[(name, mapping_node, file)] of one section (data_schemas, additional_datasets_schemas); metadata_schema is a block of its own."""
    out = []
    if section == METADATA:
        pair = mp(top).get(METADATA)
        if pair:
            node, f = R.follow(pair[1], master, master)
            if isinstance(node, yaml.MappingNode):
                out.append((METADATA, node, f))
        return out
    pair = mp(top).get(section)
    if pair:
        sec, f = R.follow(pair[1], master, master)
        for name, (_, v) in mp(sec).items():
            node, f2 = R.follow(v, f, master)
            if isinstance(node, yaml.MappingNode):
                out.append((name, node, f2))
    return out


def fields_of(R: Recipes, block: yaml.MappingNode, bfile: Path, master: Path):
    """{slug: (key_node, mapping_node, file)}; None when the block has no readable input_fields."""
    pair = mp(block).get("input_fields")
    if not pair:
        return None
    node, f = R.follow(pair[1], bfile, master)
    if not isinstance(node, yaml.MappingNode):
        return None
    out = {}
    for slug, (k, v) in mp(node).items():
        out[slug] = (k, v, f)
    return out


def entity_fields(fields) -> List[str]:
    return [s for s, (_, v, _) in (fields or {}).items() if isinstance(v, yaml.MappingNode) and OLD_KEY in mp(v) and truthy(mp(v)[OLD_KEY][1])]


# -- sections --------------------------------------------------------------------------------------------------------------

def section_names(root: Path, rep: Report) -> None:
    tool = _load_names_tool()
    plan = tool.build_plan(root)
    header = "Names pass (assets/scripts/migrate_display_names.py)"
    lines = tool.lines_of(plan, True, header)
    for line in lines[1:]:
        rep.add(1, "###" + line if line.startswith("#") else line, count=False)
    rep.counts[1] = len(plan.changes)
    opens = [c for c in plan.cases if c.case in getattr(tool, "OPEN_CASES", {}) and (c.file or c.line)
             and c.case not in getattr(tool, "DECIDED_CASES", ()) and c.case not in getattr(tool, "ADVICE_CASES", ())]
    if opens:
        rep.stat["names_open"] = len(opens)
        rep.need("section 1", f"{len(opens)} place(s) listed by the names pass under 'CANNOT BE DECIDED BY THE SCRIPT' (read them in section 1)")


def tracked_files(root: Path) -> List[Path]:
    if (root / ".git").exists():
        try:
            out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True, timeout=60).stdout
            return [root / p for p in out.decode("utf-8", "replace").split("\0") if p]
        except (OSError, subprocess.SubprocessError):
            pass
    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        files += [Path(dp) / f for f in fn]
    return files


def kind_of_file(rel: str) -> str:
    if rel.endswith("recipe_spec.yaml") and "libs/utils" in rel:
        return "the specification (recipe_spec.yaml)"
    if rel.startswith("config/data_analysis_recipes/") or rel.startswith("assets/gallery_data/"):
        return "input_fields file" if "input_fields" in rel else "recipe or template file"
    if rel.startswith(".claude/rules/"):
        return "rules"
    if rel.endswith((".md", ".qmd", ".txt")):
        return "docs and design notes"
    if rel.endswith(".py"):
        return "tests" if ("/tests/" in rel or rel.startswith("tests/") or "/test_" in rel or rel.split("/")[-1].startswith("test_")) else "code"
    return "other"


def section_entity_key(root: Path, rep: Report) -> None:
    per_kind: Counter = Counter()
    lines: List[Tuple[str, int, str, str]] = []
    for p in tracked_files(root):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if OLD_KEY not in text:
            continue
        rel = str(p.relative_to(root))
        for n, line in enumerate(text.splitlines(), 1):
            if OLD_KEY in line:
                lines.append((rel, n, kind_of_file(rel), line.strip()))
                per_kind[kind_of_file(rel)] += 1
    rep.add(2, "The column mark `is_entity_key` would be renamed `is_entity_id` everywhere it is written. This is a text rename: the lines are listed, none is changed. Lines per kind of file:")
    for k, n in sorted(per_kind.items()):
        rep.add(2, f"* {k}: {n} line(s) in {len({a for a, _, c, _ in lines if c == k})} file(s)")
    rep.add(2, "")
    for rel, n, k, text in lines:
        rep.add(2, f"- {rel}:{n} ({k}): `{OLD_KEY}` becomes `{NEW_KEY}` [D-0562, D-0567]. Now: `{text[:140]}`")
    rep.stat["rename_lines"] = len(lines)


# -- the joins that start from the metadata ----------------------------------------------------------------------------------

HOW_WORDS = {"left": "keeps every row of the first table", "inner": "keeps only the rows found in both tables",
             "semi": "keeps the rows of the first table that have a match", "anti": "keeps the rows of the first table that have no match",
             "full": "keeps every row of both tables", "right": "keeps every row of the second table", "cross": "pairs every row with every row"}


def join_kinds(R: Recipes, tier_node, jfile: Path, master: Path) -> List[str]:
    tier, f = R.follow(tier_node, jfile, master)
    steps_pair = mp(tier).get("steps") if isinstance(tier, yaml.MappingNode) else None
    if steps_pair is None:
        return []
    steps, f = R.follow(steps_pair[1], f, master)
    kinds = []
    for st in seq(steps):
        m = mp(st)
        action = scalar(m["action"][1]) if "action" in m else None
        if action and "join" in action:
            how = scalar(m["how"][1]) if "how" in m else None
            right = scalar(m["right_ingredient"][1]) if "right_ingredient" in m else "?"
            words = HOW_WORDS.get(how, f"kind `{how}`") if how else "the kind of join is not written (the engine's default applies)"
            kinds.append(f"a join with `{right}` that {words} ({R.rel(f)}:{st.start_mark.line + 1})")
    return kinds


def ingredients_of(R: Recipes, node, f: Path, master: Path) -> List[str]:
    pair = mp(node).get("ingredients")
    ings = []
    for item in seq(R.follow(pair[1], f, master)[0]) if pair else []:
        if isinstance(item, yaml.MappingNode):
            ids = mp(item).get("dataset_id")
            ings.append(scalar(ids[1]) if ids else "?")
        else:
            ings.append(scalar(item) or "?")
    return ings


def joins_of(R: Recipes, path: Path, top):
    jp = mp(top).get("joins")
    if not jp:
        return
    joins, jf = R.follow(jp[1], path, path)
    for name, (k, v) in mp(joins).items():
        node, f = R.follow(v, jf, path)
        if isinstance(node, yaml.MappingNode):
            yield name, k, node, f


def section_joins(R: Recipes, rep: Report) -> None:
    rep.add(3, "In these joined tables the FIRST table is the metadata. The rule (D-0586) is that a recipe does not start from the metadata: "
               "the table is to be rewritten with the data table first; the metadata is then added to it, keeping every row of the data table. "
               "The rewriting is written by hand and shown in a second dry run (it depends on the completion of the ids, which is not built). "
               "Each line gives the joined table, its tables in order, and what its join steps do today.")
    rep.add(3, "")
    only_meta: List[str] = []
    for path, kind, top in masters(R):
        for name, k, node, f in joins_of(R, path, top):
            ings = ingredients_of(R, node, f, path)
            if not ings:
                continue
            where = f"{R.rel(f)}:{k.start_mark.line + 1}"
            if ings[0] == METADATA and len(ings) > 1:
                kinds = join_kinds(R, mp(node)["tier1"][1], f, path) if "tier1" in mp(node) else []
                rep.add(3, f"- {where}: recipe `{R.rel(path)}`, joined table `{name}`. Tables in order: {', '.join(ings)}. Join steps today: "
                           + ("; ".join(kinds) if kinds else "none found in its tier 1") + ". [D-0586]")
                rep.bump("joins_first_meta")
            elif ings == [METADATA]:
                only_meta.append(f"- {where}: recipe `{R.rel(path)}`, joined table `{name}` is made from the metadata alone: it joins nothing. The rule does not touch it; the owner's point. [D-0586]")
    rep.add(3, "")
    rep.add(3, "Joined tables made from the metadata alone:")
    for line in only_meta:
        rep.add(3, line)
    if not only_meta:
        rep.add(3, "* none")
    rep.stat["joins_only_meta"] = len(only_meta)
    if only_meta:
        rep.need("section 3", f"{len(only_meta)} joined table(s) are made from the metadata alone: the rule does not touch them (the owner's point)")


# -- the steps that keep only a list of columns ------------------------------------------------------------------------------

def tiers_of(R: Recipes, path: Path, top: yaml.MappingNode):
    """Every (table, tier_name, steps_node, file) of a recipe: metadata, data schemas, additional tables, joins."""
    def one(name, node, f):
        for t in ("tier1", "tier2", "tier3"):
            if isinstance(node, yaml.MappingNode) and t in mp(node):
                tn, tf = R.follow(mp(node)[t][1], f, path)
                sp = mp(tn).get("steps") if isinstance(tn, yaml.MappingNode) else None
                if sp:
                    sn, sf = R.follow(sp[1], tf, path)
                    yield name, t, sn, sf
    for sec in (METADATA, "data_schemas", "additional_datasets_schemas"):
        for name, node, f in blocks_of(R, path, top, sec):
            yield from one(name, node, f)
    for name, _, node, f in joins_of(R, path, top):
        yield from one(name, node, f)


def position_words(k: int, n: int) -> str:
    if n == 1:
        return "the only step of the tier"
    if k == 1:
        return f"the FIRST step of {n}"
    if k == n:
        return f"the LAST step of {n}"
    return f"step {k} of {n}"


def section_select(R: Recipes, rep: Report) -> None:
    rep.add(4, "A step that keeps only the listed columns (`polars_select`), or that rebuilds the table from its group columns and its totals "
               "(`polars_group_by`), does not carry any other column that exists before it. A marker column (D-0586, D-0587) added before such a step "
               "would be lost at that step, wherever the step stands in the tier (first, last or between). Each line says where. "
               "What this section does NOT cover: a step that only removes named columns (`polars_drop`) keeps all the others and is not listed; "
               "other steps that rebuild the columns (pivot, unpivot and similar) are NOT examined here, because no reliable list in the project says which actions do it "
               "(libs/utils/src/utils/step_effects.py reads only the select and the group-by).")
    rep.add(4, "")
    seen = set()
    for path, kind, top in masters(R):
        for name, tier, steps, f in tiers_of(R, path, top):
            items = seq(steps)
            for k, st in enumerate(items, 1):
                m = mp(st)
                action = scalar(m["action"][1]) if "action" in m else None
                if action not in KEEP_ONLY_ACTIONS:
                    continue
                key = (f, st.start_mark.line)
                if key in seen:
                    continue
                seen.add(key)
                if action == action_names.SELECT:
                    node = (m.get("exprs") or m.get("columns") or (None, None))[1]
                    what = "keeps only " + (flow_text(node) if node is not None else "(no column list found: read the step)")
                    rep.bump("select_" + ("first" if k == 1 and len(items) > 1 else "last" if k == len(items) and len(items) > 1 else "only" if len(items) == 1 else "middle"))
                else:
                    by = m.get("by")
                    aggs = m.get("named_aggs")
                    names = [x.value for x, _ in aggs[1].value] if aggs and isinstance(aggs[1], yaml.MappingNode) else []
                    what = f"rebuilds the table from the group columns {flow_text(by[1]) if by else '(not found)'} and the totals {names or '(not found)'}"
                    rep.bump("group_by")
                rep.add(4, f"- {R.rel(f)}:{st.start_mark.line + 1}: recipe `{R.rel(path)}`, table `{name}`, {tier}, {position_words(k, len(items))}: `{action}` {what}. [D-0586, D-0587]")
    rep.say("select_ways", MARKER_WAYS)
    rep.need("section 4", "which of her two ways (D-0587) each of these steps takes is not decided by any rule")


# -- the entity id -----------------------------------------------------------------------------------------------------------

def section_entity_missing(R: Recipes, rep: Report) -> None:
    rep.add(5, "Tables that have no column marked as the entity id (`is_entity_key` today). Where a column is named like an id (for example `sample_id`) "
               "it is shown as a candidate: a name only, not a decision. A table with no such column is a table with no id column. "
               "The Gallery examples are counted here and listed in the annex at the end.")
    rep.add(5, "")
    for path, kind, top in masters(R):
        gallery = kind == "Gallery bundle"
        for sec in (METADATA, "data_schemas", "additional_datasets_schemas"):
            for name, node, f in blocks_of(R, path, top, sec):
                where = f"{R.rel(f)}:{node.start_mark.line + 1}"
                fields = fields_of(R, node, f, path)
                if fields is None:
                    line, owner = f"recipe `{R.rel(path)}`, table `{name}`: no readable list of columns, nothing can be declared there. [D-0569]", "has no readable list of columns: the owner decides what it is"
                    cands = None
                elif entity_fields(fields):
                    continue
                else:
                    cands = [s for s in fields if CANDIDATE.match(s)]
                    if cands:
                        line = f"recipe `{R.rel(path)}`, table `{name}`: no id declared; a column named {', '.join('`' + c + '`' for c in cands)} exists: a candidate, not a decision. [D-0569]"
                        owner = f"no id declared; candidate by name: {', '.join(cands)}"
                    else:
                        line = f"recipe `{R.rel(path)}`, table `{name}`: no id declared and no column with an id-like name (no id column). [D-0569]"
                        owner = "has no id column: a reference table, or a declaration for the owner"
                if gallery:
                    rep.add("annex", f"- {where}: {line}")
                    rep.bump("gallery_cand" if cands else "gallery_noid")
                else:
                    rep.add(5, f"- {where}: {line}")
                    rep.bump("tables_cand" if cands else "tables_noid")
                    rep.need(where, f"table `{name}`: {owner}")
                    if cands:
                        rep.say("cand_recipes", R.rel(path))
    rep.add(5, "")
    rep.add(5, f"* Gallery examples with no id declared: {rep.stat.get('gallery_noid', 0)} have no id column, {rep.stat.get('gallery_cand', 0)} have a column named like an id (annex).")


# -- the metadata lines with no usable id ------------------------------------------------------------------------------------

def readers_of_metadata(R: Recipes, path: Path, top) -> List[str]:
    return [name for name, _, node, f in joins_of(R, path, top) if METADATA in ingredients_of(R, node, f, path)]


def removals_by_table(R: Recipes, master: Path, top, id_names: List[str]) -> Dict[str, List[str]]:
    """{table: [file:line (what)]} for every table that reads the metadata (the metadata itself and the joins that list it), in every tier."""
    readers = set(readers_of_metadata(R, master, top)) | {METADATA}
    found: Dict[str, List[str]] = {t: [] for t in readers}
    for table, tier, steps, f in tiers_of(R, master, top):
        if table not in readers:
            continue
        for st in seq(steps):
            m = mp(st)
            action = scalar(m["action"][1]) if "action" in m else None
            if action == DROP_NULLS:
                subset = m.get("subset")
                names = [scalar(n) for n in seq(subset[1])] if subset else []
                if not subset or any(n in id_names for n in names) or (subset and scalar(subset[1]) in id_names):
                    found[table].append(f"{R.rel(f)}:{st.start_mark.line + 1} which drops the rows with a missing value in {flow_text(subset[1]) if subset else 'any column'}")
            elif action == action_names.FILTER:
                col = scalar(m["column"][1]) if "column" in m else None
                na = scalar(m["na"][1]) if "na" in m else None
                if col in id_names and na == "remove":
                    found[table].append(f"{R.rel(f)}:{st.start_mark.line + 1} a filter on `{col}` that removes the rows with no value")
    return found


def describe_cell(raw: str, nulls: set) -> str:
    if raw == "":
        return "(empty)"
    if raw.strip() == "":
        return "(only spaces)"
    if raw == '""':
        return "(two quote marks, read as empty)"
    if raw.strip() == "-":
        return "(a dash, a declared missing-value mark)" if "-" in nulls else "(a dash)"
    if raw in nulls or raw.strip() in nulls:
        return "(a declared missing-value mark)"
    return ""


def section_metadata_lines(R: Recipes, rep: Report) -> None:
    rep.add(6, "For each recipe with a metadata table: the lines of its data file where the id cell is empty, only spaces, or a missing-value mark that the recipe declares. "
               "The file is read as text, not by the engine; each cell is shown as written in the file. Then it says which steps of the recipe already remove such lines. "
               "The move (D-0569) would remove these lines from the metadata itself.")
    rep.add(6, "")
    for path, kind, top in masters(R):
        blocks = blocks_of(R, path, top, METADATA)
        if not blocks:
            continue
        _, node, f = blocks[0]
        rname = R.rel(path)
        src = mp(node).get("source")
        spath = scalar(mp(src[1]).get("path", (None, None))[1]) if src and isinstance(src[1], yaml.MappingNode) else None
        if not spath:
            rep.add(6, f"* recipe `{rname}`: the metadata table names no data file; nothing to read. [D-0569, D-0594]")
            rep.need(rname, "the metadata table names no data file: the file cannot be found by the recipe's own words")
            continue
        data = (R.root / spath).resolve() if not Path(spath).is_absolute() else Path(spath)
        if not data.is_file():
            rep.add(6, f"* recipe `{rname}`: the data file `{spath}` was not found in this tree; not read. [D-0569, D-0594]")
            rep.need(rname, f"the metadata data file `{spath}` does not exist in this tree")
            continue
        fields = fields_of(R, node, f, path) or {}
        ids = entity_fields(fields)
        basis = "the declared id"
        if not ids:
            ids = [s for s in fields if CANDIDATE.match(s)][:1]
            basis = "a candidate by name, no id is declared"
        if not ids:
            rep.add(6, f"* recipe `{rname}`: no id column found in the metadata table; lines not examined. [D-0569, D-0594]")
            rep.need(rname, "the metadata table has no id column: nothing to check for empty ids")
            continue
        slug = ids[0]
        fm = mp(fields[slug][1]) if isinstance(fields[slug][1], yaml.MappingNode) else {}
        colname = scalar(fm["original_name"][1]) if "original_name" in fm else slug
        nulls = set()
        for holder in (fm.get("null_values"), mp(node).get("null_values")):
            if holder:
                nulls |= {scalar(n) for n in seq(holder[1]) if scalar(n) is not None}
        shown = R.rel(data) if data.is_relative_to(R.root) else str(data)
        try:
            raw_lines = data.read_text(encoding="utf-8").splitlines()
            bad = []
            with data.open(encoding="utf-8", newline="") as fh:
                reader = csv.reader(fh, delimiter="\t")
                header = next(reader, None)
                if header is None or colname not in header:
                    rep.add(6, f"* `{shown}`: the column `{colname}` is not in the header; not examined. [D-0569, D-0594]")
                    rep.need(shown, f"the id column `{colname}` is not in the header")
                    continue
                idx = header.index(colname)
                while True:
                    before = reader.line_num
                    try:
                        row = next(reader)
                    except StopIteration:
                        break
                    start = before + 1
                    cell = row[idx] if idx < len(row) else ""
                    if not row:
                        bad.append((start, "(blank line)"))
                    elif cell.strip() == "" or cell in nulls or cell.strip() in nulls:
                        parts = raw_lines[start - 1].split("\t") if start - 1 < len(raw_lines) else []
                        raw = parts[idx] if idx < len(parts) else ""
                        words = describe_cell(raw, nulls)
                        bad.append((start, (f"`{raw}` " if raw.strip() else "") + words if words else f"`{raw}`"))
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            rep.add(6, f"* `{spath}`: could not be read as text ({type(exc).__name__}); not examined. [D-0569, D-0594]")
            rep.need(spath, f"the metadata file could not be read ({type(exc).__name__})")
            continue
        removal = removals_by_table(R, path, top, [slug, colname])
        own = removal.pop(METADATA, [])
        removers = {t: v for t, v in removal.items() if v}
        keepers = [t for t, v in removal.items() if not v]
        parts_ = ["the metadata's own steps do not remove them" if not own else "the metadata's own steps remove them (" + "; ".join(own) + ")"]
        if removers:
            parts_.append("the join" + ("s " if len(removers) > 1 else " ") + ", ".join(f"`{t}` removes them ({'; '.join(v)})" if len(removers) == 1 else f"`{t}` ({'; '.join(v)})" for t, v in removers.items())
                          + ("" if len(removers) == 1 else " remove them"))
        if keepers:
            parts_.append("the join" + ("s " if len(keepers) > 1 else " ") + ", ".join(f"`{t}`" for t in keepers) + " do not" if len(keepers) > 1 else "the join `" + keepers[0] + "` does not")
        rep.add(6, f"* recipe `{rname}`, file `{shown}`, id column `{colname}` ({basis}), missing-value marks declared: {sorted(nulls) or 'none'}: "
                   f"{len(bad)} line(s) with no usable id. Who removes them today: " + "; ".join(parts_) + ". [D-0569, D-0594]")
        for n, cell in bad:
            rep.add(6, f"- {shown}:{n}: the id cell is {cell}. [D-0569]")
        if bad:
            rep.bump("meta_bad", len(bad))
            rep.bump("meta_files")
            rep.say("meta_bad", f"{len(bad)} line(s) of `{shown}` have no usable id. Today: " + "; ".join(parts_) + ".")
        if bad and (keepers or not (own or removers)):
            rep.need(shown, f"{len(bad)} metadata line(s) have no usable id and not every table that reads the metadata removes them ("
                            + ("does not: " + ", ".join(keepers) if keepers else "no step removes them") + "): how the removal is written is the move's design")


def section_additional(R: Recipes, rep: Report) -> None:
    rep.add(7, "Tables registered under `additional_datasets_schemas` that declare an entity id. The owner's earlier point: they are to be moved under the data schemas (listed only).")
    rep.add(7, "")
    for path, kind, top in masters(R):
        for name, node, f in blocks_of(R, path, top, "additional_datasets_schemas"):
            ids = entity_fields(fields_of(R, node, f, path))
            if ids:
                rep.add(7, f"- {R.rel(f)}:{node.start_mark.line + 1}: recipe `{R.rel(path)}`, table `{name}` declares the entity id ({', '.join(ids)}) under `additional_datasets_schemas`.")


# -- output ----------------------------------------------------------------------------------------------------------------

TITLES = {
    1: "The names pass (mechanical)",
    2: "`is_entity_key` becomes `is_entity_id` (mechanical, D-0562, D-0567)",
    3: "Joined tables that start from the metadata (D-0586)",
    4: "Steps that keep only a list of columns (D-0586, D-0587)",
    5: "Tables with no entity id declared (D-0569)",
    6: "Metadata lines with no usable id (D-0569, D-0594)",
    7: "Tables under `additional_datasets_schemas` that declare the entity id",
}
ORDER = (6, 3, 4, 5, 7, 2, 1)       # what needs her first; the long mechanical lists last
INTRO_LAST = {2: "A mechanical rename: no decision for her; listed so that she can see every place.",
              1: "The names pass is a mechanical migration of the display-name keys (the list of assets/scripts/migrate_display_names.py, reused as it is)."}


def git_commit(root: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "(no git commit)"


def first_screen(rep: Report) -> List[str]:
    st, tx = rep.stat, rep.texts
    out = ["## What needs you", ""]
    n = 1
    if st.get("meta_bad"):
        out.append(f"{n}. " + " ".join(tx.get("meta_bad", [])) + " The move would remove them from the metadata itself: do you want that? (section 6)")
        n += 1
    if st.get("joins_only_meta"):
        out.append(f"{n}. {st['joins_only_meta']} joined table(s) are made from the metadata alone; the rule 'do not start from the metadata' does not touch them. What do you want for them? (section 3)")
        n += 1
    if st.get("joins_first_meta"):
        out.append(f"{n}. {st['joins_first_meta']} joined table(s) start from the metadata and are to be rewritten by hand with the data table first; the rewriting is shown in a second dry run. Nothing to decide now. (section 3)")
        n += 1
    keep = sum(st.get(k, 0) for k in ("select_first", "select_last", "select_middle", "select_only", "group_by"))
    if keep:
        out.append(f"{n}. {keep} step(s) keep only a fixed list of columns ({st.get('select_first', 0)} first in their tier, {st.get('select_last', 0)} last, "
                   f"{st.get('select_middle', 0) + st.get('select_only', 0)} elsewhere or alone, {st.get('group_by', 0)} group-by) and would not carry a marker column. "
                   "For each, which of your two ways (add the marker to the list, or drop it by a visible step)? (section 4)")
        n += 1
    if st.get("tables_cand") or st.get("tables_noid"):
        out.append(f"{n}. {st.get('tables_cand', 0)} table(s) of {len(set(tx.get('cand_recipes', [])))} recipe(s) declare no entity id, but a column named like an id exists (a candidate, not a decision); "
                   f"{st.get('tables_noid', 0)} table(s) have no id column at all (reference tables). Which column is the id of each? (section 5)")
        n += 1
    if st.get("gallery_cand") or st.get("gallery_noid"):
        out.append(f"{n}. The Gallery examples declare no entity id: {st.get('gallery_noid', 0)} have no id column, {st.get('gallery_cand', 0)} have a column named `id`. Do they need one? (section 5, annex)")
        n += 1
    out.append(f"{n}. Tables under `additional_datasets_schemas` that declare the entity id: {rep.counts.get(7, 0)}; to be moved under the data schemas (your earlier point). (section 7)")
    n += 1
    if st.get("names_open"):
        out.append(f"{n}. {st['names_open']} place(s) of the names pass that no decision covers. (section 1, 'cannot be decided')")
    out += ["", f"Only a mechanical rename, no decision: the names pass ({rep.counts.get(1, 0)} changes) and `is_entity_key` to `is_entity_id` ({rep.counts.get(2, 0)} lines)."]
    return out


def build(root: Path) -> List[str]:
    rep = Report()
    R = Recipes(root, rep)
    section_names(root, rep)
    section_entity_key(root, rep)
    section_joins(R, rep)
    section_select(R, rep)
    section_entity_missing(R, rep)
    section_metadata_lines(R, rep)
    section_additional(R, rep)
    for n in range(2, 8):
        rep.counts.setdefault(n, 0)
    out = ["# Dry run of the big move", "",
           f"Date: {datetime.date.today().isoformat()}. Commit of the worktree: {git_commit(root)}. Root: {root}", "",
           "Nothing was changed. This is a list for the owner to read.", ""]
    out += first_screen(rep)
    out += ["", "## Count per section", ""]
    extra = {3: f" ({rep.stat.get('joins_first_meta', 0)} start from the metadata, {rep.stat.get('joins_only_meta', 0)} are made from it alone)",
             5: f" (and {rep.stat.get('gallery_noid', 0) + rep.stat.get('gallery_cand', 0)} Gallery examples in the annex)"}
    unit = {1: "change(s)", 2: "line(s)", 3: "joined table(s)", 4: "step(s)", 5: "table(s)", 6: "metadata line(s) with no usable id", 7: "table(s)"}
    for n in ORDER:
        out.append(f"- {n}. {TITLES[n]}: {rep.counts.get(n, 0)} {unit[n]}{extra.get(n, '')}")
    for n in ORDER:
        if n in (1, 2):
            continue
        out += ["", f"## {n}. {TITLES[n]}", ""]
        out += rep.sections.get(n, []) or ["nothing found"]
    out += ["", "## Needs the owner (every place where no rule decides)", ""]
    grouped = [x for x in rep.owner if not x.startswith("assets/gallery_data/")]
    out += [f"- {x}" for x in grouped] if grouped else ["- nothing"]
    if rep.stat.get("gallery_noid") or rep.stat.get("gallery_cand"):
        out.append(f"- The Gallery examples: {rep.stat.get('gallery_noid', 0)} have no id column and {rep.stat.get('gallery_cand', 0)} have a column named `id`, none declared as the entity id (the full list is in the annex).")
    for n in (2, 1):
        out += ["", f"## {n}. {TITLES[n]}", "", INTRO_LAST[n], ""]
        out += rep.sections.get(n, []) or ["nothing found"]
    out += ["", "## Annex: the Gallery examples with no entity id declared", ""]
    out += rep.sections.get("annex", []) or ["nothing found"]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=".", help="the folder to read (default: the current folder); it holds config/ and assets/")
    parser.add_argument("--report", default=None, help="write the list as markdown to this NEW file (it must not exist; inside the project folder only under tmpAI/)")
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(args.project_root))
    tool = _load_names_tool()
    target = Path(os.path.abspath(args.report)) if args.report else None
    if target is not None:
        refusal = tool.report_refusal(target, root)
        if refusal:
            print(refusal, file=sys.stderr)
            return 3
    lines = build(root)
    print("\n".join(lines[:30]))
    if target is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"report written: {target}")
    else:
        print("(no --report given: the full list was not written anywhere)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
