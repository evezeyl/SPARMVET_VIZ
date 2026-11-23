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

SCRIPT_DIR = Path(__file__).resolve().parent
OLD_KEY = "is_entity_key"
NEW_KEY = "is_entity_id"
METADATA = "metadata_schema"
SELECT_ACTIONS = ("polars_select", "polars_drop")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "tmpAI", "tmp"}
CANDIDATE = re.compile(r"^(sample_?id|sample|isolate_?id|isolate|accession|id|strain|strain_?id)$", re.I)
DROP_NULLS = "polars_drop_nulls"
MARKER_WAYS = ("would drop a marker column unless the marker columns are added to the list, or the marked lines are treated at "
               "tier 1 and the marker dropped by a visible step (her two ways, D-0587; this script does not choose)")


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

    def add(self, n: int, line: str, count: bool = True) -> None:
        self.sections.setdefault(n, []).append(line)
        if count:
            self.counts[n] = self.counts.get(n, 0) + 1

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
    rep.add(2, "A text rename, listed and not applied. Counts per kind of file:", count=False)
    for k, n in sorted(per_kind.items()):
        rep.add(2, f"- {k}: {n} line(s) in {len({a for a, _, c, _ in lines if c == k})} file(s)", count=False)
    rep.add(2, "")
    for rel, n, k, text in lines:
        rep.add(2, f"- {rel}:{n}: `{OLD_KEY}` -> `{NEW_KEY}` ({k}) [D-0562, D-0567]  now: `{text[:140]}`")


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
            kinds.append(f"{action} with {right}, how={how if how else '(not written: the default)'} ({R.rel(f)}:{st.start_mark.line + 1})")
    return kinds


def section_joins(R: Recipes, rep: Report) -> None:
    only_meta: List[str] = []
    for path, kind, top in masters(R):
        joins_pair = mp(top).get("joins")
        if not joins_pair:
            continue
        joins, jf = R.follow(joins_pair[1], path, path)
        for name, (k, v) in mp(joins).items():
            node, f = R.follow(v, jf, path)
            if not isinstance(node, yaml.MappingNode):
                continue
            ing_pair = mp(node).get("ingredients")
            ings = []
            for item in seq(R.follow(ing_pair[1], f, path)[0]) if ing_pair else []:
                if isinstance(item, yaml.MappingNode):
                    ids = mp(item).get("dataset_id")
                    ings.append(scalar(ids[1]) if ids else "?")
                else:
                    ings.append(scalar(item) or "?")
            if not ings:
                continue
            where = f"{R.rel(f)}:{k.start_mark.line + 1}"
            if ings[0] == METADATA and len(ings) > 1:
                kinds = join_kinds(R, mp(node)["tier1"][1], f, path) if "tier1" in mp(node) else []
                rep.add(3, f"- {where}: recipe `{R.rel(path)}` ({kind}), table `{name}`: ingredients in order {ings}; join steps: "
                           + ("; ".join(kinds) if kinds else "none found in its tier 1")
                           + " -> to be rewritten with the data table first and a left join on the metadata; the rewriting is written by hand and shown in a second dry run [D-0586]")
            elif ings == [METADATA]:
                only_meta.append(f"- {where}: recipe `{R.rel(path)}` ({kind}), table `{name}`: its only ingredient is the metadata (it joins nothing): not touched by the rule; the owner's point")
    rep.add(3, "")
    rep.add(3, "Tables whose ONLY ingredient is the metadata:", count=False)
    for line in only_meta:
        rep.add(3, line, count=False)
    if not only_meta:
        rep.add(3, "none", count=False)
    if only_meta:
        rep.need("section 3", f"{len(only_meta)} table(s) have the metadata as their only ingredient: the rule does not touch them (the owner's point)")


def tiers_of(R: Recipes, path: Path, top: yaml.MappingNode):
    """Every (label, tier_name, steps_node, file) of a recipe: metadata, data schemas, additional tables, joins, plot tier3."""
    for sec in (METADATA, "data_schemas", "additional_datasets_schemas"):
        for name, node, f in blocks_of(R, path, top, sec):
            for t in ("tier1", "tier2", "tier3"):
                if t in mp(node):
                    tn, tf = R.follow(mp(node)[t][1], f, path)
                    sp = mp(tn).get("steps") if isinstance(tn, yaml.MappingNode) else None
                    if sp:
                        sn, sf = R.follow(sp[1], tf, path)
                        yield name, t, sn, sf
    jp = mp(top).get("joins")
    if jp:
        joins, jf = R.follow(jp[1], path, path)
        for name, (_, v) in mp(joins).items():
            node, f = R.follow(v, jf, path)
            for t in ("tier1", "tier2", "tier3"):
                if isinstance(node, yaml.MappingNode) and t in mp(node):
                    tn, tf = R.follow(mp(node)[t][1], f, path)
                    sp = mp(tn).get("steps") if isinstance(tn, yaml.MappingNode) else None
                    if sp:
                        sn, sf = R.follow(sp[1], tf, path)
                        yield name, t, sn, sf


def section_select(R: Recipes, rep: Report) -> None:
    seen = set()
    for path, kind, top in masters(R):
        for name, tier, steps, f in tiers_of(R, path, top):
            items = seq(steps)
            if not items:
                continue
            last = items[-1]
            m = mp(last)
            action = scalar(m["action"][1]) if "action" in m else None
            if action not in SELECT_ACTIONS:
                continue
            key = (f, last.start_mark.line)
            if key in seen:
                continue
            seen.add(key)
            colsnode = (m.get("exprs") or m.get("columns") or m.get("cols") or (None, None))[1]
            cols = flow_text(colsnode) if colsnode is not None else "(no column list found: read the step)"
            rep.add(4, f"- {R.rel(f)}:{last.start_mark.line + 1}: recipe `{R.rel(path)}`, table `{name}`, {tier}: ends with `{action}`, {'drops' if action == 'polars_drop' else 'publishes'} {cols}: {MARKER_WAYS} [D-0586, D-0587]")
    rep.need("section 4", "which of her two ways (D-0587) each fixed column list takes is not decided by any rule")


def section_entity_missing(R: Recipes, rep: Report) -> None:
    for path, kind, top in masters(R):
        for sec in (METADATA, "data_schemas", "additional_datasets_schemas"):
            for name, node, f in blocks_of(R, path, top, sec):
                where = f"{R.rel(f)}:{node.start_mark.line + 1}"
                fields = fields_of(R, node, f, path)
                if fields is None:
                    rep.add(5, f"- {where}: recipe `{R.rel(path)}`, table `{name}` ({sec}): no readable input_fields; nothing can be declared there [D-0569]")
                    rep.need(where, f"table `{name}` has no readable input_fields: the owner decides what it is")
                    continue
                if entity_fields(fields):
                    continue
                cands = [s for s in fields if CANDIDATE.match(s)]
                if cands:
                    rep.add(5, f"- {where}: recipe `{R.rel(path)}`, table `{name}` ({sec}): no field marked `{OLD_KEY}`; CANDIDATE (a name only, not a decision): {', '.join(cands)} [D-0569]")
                    rep.need(where, f"table `{name}`: which field is the entity id is the recipe maker's declaration (candidate by name: {', '.join(cands)})")
                else:
                    rep.add(5, f"- {where}: recipe `{R.rel(path)}`, table `{name}` ({sec}): no field marked `{OLD_KEY}`; no id column (no field with an id-like name) [D-0569]")
                    rep.need(where, f"table `{name}` has no id column: reference table or a declaration to be made by the owner")


def removes_missing_ids(R: Recipes, master: Path, top, id_names: List[str]) -> List[str]:
    found = []
    for sec_name, tier, steps, f in tiers_of(R, master, top):
        if sec_name != METADATA:
            continue
        for st in seq(steps):
            m = mp(st)
            action = scalar(m["action"][1]) if "action" in m else None
            if action == DROP_NULLS:
                subset = m.get("subset")
                names = [scalar(n) for n in seq(subset[1])] if subset else []
                if not subset or any(n in id_names for n in names) or (subset and scalar(subset[1]) in id_names):
                    found.append(f"{R.rel(f)}:{st.start_mark.line + 1} (`{DROP_NULLS}`, subset {flow_text(subset[1]) if subset else 'not written: all columns'})")
            elif action == "modif_filter":
                col = scalar(m["column"][1]) if "column" in m else None
                na = scalar(m["na"][1]) if "na" in m else None
                if col in id_names and na == "remove":
                    found.append(f"{R.rel(f)}:{st.start_mark.line + 1} (`modif_filter` on `{col}` with na: remove)")
    return found


def section_metadata_lines(R: Recipes, rep: Report) -> None:
    for path, kind, top in masters(R):
        blocks = blocks_of(R, path, top, METADATA)
        if not blocks:
            continue
        _, node, f = blocks[0]
        where = R.rel(f)
        src = mp(node).get("source")
        spath = scalar(mp(src[1]).get("path", (None, None))[1]) if src and isinstance(src[1], yaml.MappingNode) else None
        if not spath:
            rep.add(6, f"- recipe `{R.rel(path)}`: the metadata block names no `source.path`; no file to read [D-0569, D-0594]", count=False)
            rep.need(R.rel(path), "the metadata block has no source.path: the data file cannot be found by the recipe's own words")
            continue
        data = (R.root / spath).resolve() if not Path(spath).is_absolute() else Path(spath)
        if not data.is_file():
            rep.add(6, f"- recipe `{R.rel(path)}`: the data file `{spath}` was not found; not read [D-0569, D-0594]", count=False)
            rep.need(R.rel(path), f"the metadata data file `{spath}` does not exist in this tree")
            continue
        fields = fields_of(R, node, f, path) or {}
        ids = entity_fields(fields)
        basis = "declared entity id"
        if not ids:
            ids = [s for s in fields if CANDIDATE.match(s)][:1]
            basis = "CANDIDATE by name (no field is marked)"
        if not ids:
            rep.add(6, f"- recipe `{R.rel(path)}`: no id field found in the metadata block; lines not examined [D-0569, D-0594]", count=False)
            rep.need(R.rel(path), "the metadata block has no id field: nothing to check for empty ids")
            continue
        slug = ids[0]
        fnode = fields[slug][1]
        fm = mp(fnode) if isinstance(fnode, yaml.MappingNode) else {}
        colname = scalar(fm["original_name"][1]) if "original_name" in fm else slug
        nulls = set()
        for holder in (fm.get("null_values"), mp(node).get("null_values")):
            if holder:
                nulls |= {scalar(n) for n in seq(holder[1]) if scalar(n) is not None}
        try:
            with data.open(encoding="utf-8", newline="") as fh:
                reader = csv.reader(fh, delimiter="\t")
                header = next(reader, None)
                if header is None or colname not in header:
                    rep.add(6, f"- `{R.rel(data) if data.is_relative_to(R.root) else data}`: the column `{colname}` is not in the header; not examined [D-0569, D-0594]", count=False)
                    rep.need(R.rel(data) if data.is_relative_to(R.root) else str(data), f"the id column `{colname}` is not in the header")
                    continue
                idx = header.index(colname)
                bad = []
                for row in reader:
                    cell = row[idx] if idx < len(row) else ""
                    if not row:
                        bad.append((reader.line_num, "(blank line)"))
                    elif cell.strip() == "" or cell in nulls or cell.strip() in nulls:
                        bad.append((reader.line_num, cell))
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            rep.add(6, f"- `{spath}`: could not be read as text ({type(exc).__name__}); not examined [D-0569, D-0594]", count=False)
            rep.need(spath, f"the metadata file could not be read ({type(exc).__name__})")
            continue
        drops = removes_missing_ids(R, path, top, [slug, colname])
        dshow = "; ".join(drops) if drops else "none: no step of the recipe removes a missing id"
        shown = R.rel(data) if data.is_relative_to(R.root) else str(data)
        rep.add(6, f"- recipe `{R.rel(path)}`, `{shown}`, id column `{colname}` ({basis}), null values declared: {sorted(nulls) or 'none'}: {len(bad)} line(s) with no usable id; own step that removes missing ids: {dshow} [D-0569, D-0594]", count=False)
        for n, cell in bad:
            rep.add(6, f"  - {shown}:{n}: id cell as written: `{cell!r}` -> would be removed from the metadata [D-0569]")
        if bad and not drops:
            rep.need(shown, f"{len(bad)} metadata line(s) have no usable id and no step of the recipe removes them: how the removal is written is the move's design")


def section_additional(R: Recipes, rep: Report) -> None:
    for path, kind, top in masters(R):
        for name, node, f in blocks_of(R, path, top, "additional_datasets_schemas"):
            fields = fields_of(R, node, f, path)
            ids = entity_fields(fields)
            if ids:
                rep.add(7, f"- {R.rel(f)}:{node.start_mark.line + 1}: recipe `{R.rel(path)}`, table `{name}` declares the entity id ({', '.join(ids)}) under `additional_datasets_schemas`: the owner's earlier point: to be moved under the data schemas (listed only)")


# -- output ----------------------------------------------------------------------------------------------------------------

TITLES = {
    1: "The names pass",
    2: "`is_entity_key` becomes `is_entity_id` (D-0562, D-0567)",
    3: "The joins that start from the metadata (D-0586)",
    4: "The fixed column lists (D-0586, D-0587)",
    5: "The entity id is not declared (D-0569)",
    6: "Metadata lines with no usable id (D-0569, D-0594)",
    7: "Tables under `additional_datasets_schemas` that declare the entity id",
}


def git_commit(root: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "(no git commit)"


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
    for n in range(1, 8):
        rep.counts.setdefault(n, 0)
    out = [f"# Dry run of the big move", "",
           f"Date: {datetime.date.today().isoformat()}. Commit of the worktree: {git_commit(root)}. Root: {root}", "",
           "Nothing was changed. This is a list for the owner to read.", "", "## Count per section", ""]
    for n in range(1, 8):
        unit = "metadata line(s) with no usable id" if n == 6 else "change(s)" if n == 1 else "line(s)" if n == 2 else "place(s)"
        if n == 6:
            c = sum(1 for line in rep.sections.get(6, []) if line.startswith("  - "))
        else:
            c = rep.counts[n]
        out.append(f"- {n}. {TITLES[n]}: {c} {unit}")
    for n in range(1, 8):
        out += ["", f"## {n}. {TITLES[n]}", ""]
        lines = rep.sections.get(n, [])
        out += lines if lines else ["nothing found"]
    out += ["", "## Needs the owner (every place where no rule decides)", ""]
    out += [f"- {x}" for x in rep.owner] if rep.owner else ["nothing"]
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
    print("\n".join(lines[:16]))
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
