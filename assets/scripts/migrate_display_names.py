"""DRY RUN of the names pass: lists what the migration of the display names would change, and what it cannot decide.

The names pass is ONE migration (ledger D-0407 to D-0412, D-0459; task NAMES-UI-LABEL-EVERYWHERE). It waits for the owner's
answers, so in this version the script only PLANS: by default it changes nothing and prints, per file, each change it would make
(file, line, old key path, new key path, the ledger number the rule rests on), a summary per kind of file, and a section
"CANNOT BE DECIDED BY THE SCRIPT" with every place that no decision covers.

The rules it applies (one table, `RULES` in this file, each with the ledger line it rests on):
  recipes (and the files they include, Gallery bundles, templates, test fixtures):
    info.label, info.name, info.ui_title  ->  info.ui_label                       (D-0410)
    the `ui_title` of a group and of a plot entry is removed, its text printed   (D-0409, D-0410)
  deployment files:
    branding.banner.title -> ui_label, branding.banner.subtitle -> description    (D-0411)
    deployment_name is removed, when a banner title takes its place              (D-0411)
  app features files:
    the key `ui_title {text, subtitle, visible}` is removed                       (D-0411)
Whatever else it finds that no decision covers is listed, never changed: a recipe with no name, the `label` of tables, joins and
fields, the `label` of the registries, the format number, saved sessions, the Gallery, `display_name` of app features, and so on.
A key present in the old and in the new spelling, or two old keys for one new key, is a CONFLICT: reported, not overwritten.

It edits the TEXT at the positions the YAML parser reports, so comments, blank lines, key order, quoting and `!include` lines stay
byte for byte outside the changed keys. A second run on a migrated copy finds nothing to change.

Modes:
  (default)   DRY RUN: nothing is written.
  --report F  also write the list as markdown to the file F (never over a file it scans).
  --apply     writes the planned changes, but ONLY on a copy: --root must be given and must not be the repository itself, a folder
              that contains it or a git working tree. On the repository it refuses (exit 3): the pass waits for the owner's answers.

Exit codes: dry run 0 = nothing to change, 1 = something would change; --apply 0 = written; 2 = a conflict or a place that cannot
be placed exists (what could be placed is still planned or written); 3 = refused to run (--apply on the repository, bad --report).

Examples:
  PYTHONPATH=. .venv/bin/python assets/scripts/migrate_display_names.py
  PYTHONPATH=. .venv/bin/python assets/scripts/migrate_display_names.py --report tmpAI/names_dry_run.md
  PYTHONPATH=. .venv/bin/python assets/scripts/migrate_display_names.py --root tmpAI/names_copy --apply
"""

# @deps
# provides: script:migrate_display_names
# consumes: -
# consumed_by: app/tests/test_migrate_display_names.py
# doc: .claude/knowledge/decision_ledger.md (D-0407 to D-0412, D-0459, D-0236), .claude/tasks/tasks.md (NAMES-UI-LABEL-EVERYWHERE), .claude/rules/rules_asset_scripts.md
# @end_deps
import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# (folder under the root, family): what is looked at, and how a file is classified
SCAN = (
    ("config/data_analysis_recipes", "recipe"),
    ("config/deployment", "deployment"),
    ("config/app_features", "app_features"),
    ("assets/gallery_data", "gallery"),
    ("libs/transformer/tests/data", "fixture"),
    ("app/tests/equality/recipes", "fixture"),
    ("libs/viz_gallery/tests/data", "fixture"),
)
KIND_ORDER = ("recipes", "recipe templates", "Gallery bundles", "test fixtures", "deployment files", "deployment templates", "app features files")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
INCLUDE_TAG = "!include"


@dataclass(frozen=True)
class Rule:
    id: str
    place: str                 # recipe.info, recipe.group, recipe.plot, recipe.schema, recipe.join, recipe.field, deployment.top, deployment.banner, app_features.top
    old: str
    new: Optional[str]         # None = the key is removed
    ledger: str                # the ledger line the rule rests on
    words: str                 # words of that line (or of the re-check file), so that the rule can be read against its source
    status: str = "APPLY"      # APPLY = the script plans it; OPEN = the script only lists the places (no decision covers it)
    case: str = ""             # for OPEN: the case number of OPEN_CASES


# One table, one place. A statement that the re-check (tmpAI/coordinator/ledger_words_check/RECHECK_AGAINST_TRANSCRIPT.md) marks as
# added by the relay, or that no decision covers, is OPEN: it is listed and never applied. To apply it after the owner answers,
# change its status here (and its new key) and re-run: nothing else in the script changes.
RULES: List[Rule] = [
    Rule("R01", "recipe.info", "label", "ui_label", "D-0410", "the old keys `info.label`, `info.name` and `info.ui_title` are refused with the new name (re-check rows 2, 9)"),
    Rule("R02", "recipe.info", "name", "ui_label", "D-0410", "the old keys `info.label`, `info.name` and `info.ui_title` are refused with the new name (re-check row 2)"),
    Rule("R03", "recipe.info", "ui_title", "ui_label", "D-0410", "`info.ui_label` replaces the one name key `info.ui_title` of D-0408 (re-check row 2)"),
    Rule("R04", "recipe.group", "ui_title", None, "D-0409", "(1) A group's `ui_title` is removed from the format (option B); D-0410: `ui_title` leaves the recipe format entirely"),
    Rule("R05", "recipe.plot", "ui_title", None, "D-0409", "(2) ... the plot's `ui_title` as the report name goes with it; D-0410: `ui_title` leaves the recipe format entirely"),
    Rule("R06", "deployment.banner", "title", "ui_label", "D-0411", "`title` becomes `ui_label`, `subtitle` becomes `description` (re-check row 3)"),
    Rule("R07", "deployment.banner", "subtitle", "description", "D-0411", "`title` becomes `ui_label`, `subtitle` becomes `description` (re-check row 3)"),
    Rule("R08", "deployment.top", "deployment_name", None, "D-0411", "`deployment_name` is REMOVED; the banner's `ui_label` is the deployment's name (re-check row 4); kept and listed when no banner title can take the name"),
    Rule("R09", "app_features.top", "ui_title", None, "D-0411", "The app features key `ui_title {text, subtitle, visible}` ... is REMOVED (re-check row 1)"),
    Rule("R10", "recipe.schema", "label", "ui_label", "D-0407", "every display key carries the prefix `ui_` in every file kind; the spec says PENDING (M271): not applied", "OPEN", "OC08"),
    Rule("R11", "recipe.join", "label", "ui_label", "D-0407", "every display key carries the prefix `ui_` in every file kind; the spec says PENDING (M271): not applied", "OPEN", "OC08"),
    Rule("R12", "recipe.field", "label", "ui_label", "D-0407", "every display key carries the prefix `ui_` in every file kind; the spec says PENDING (M271): not applied", "OPEN", "OC08"),
    Rule("R13", "app_features.top", "display_name", None, "D-0407", "D-0411 names only `ui_title` of the app features file; D-0412: the key lists are not decided", "OPEN", "OC07"),
]

OPEN_CASES: Dict[str, Dict[str, str]] = {
    "OC01": {"title": "A recipe with no name",
             "words": "D-0408: The check I01 (\"label required\") goes ... the recipe's file name (id) as the fallback. D-0410: the check I01 becomes the check for `info.ui_label`. "
                      "The two lines disagree; the re-check marks the second half as added by the relay (row 11). Must every recipe have `info.ui_label`?"},
    "OC02": {"title": "The key `label` of the registries of steps and plot components (code, not recipes)",
             "words": "D-0407: NOT decided: ... the registries. Renamed to `ui_label` too, or a stated exception? The count is a text match, not a parse."},
    "OC03": {"title": "The recipe format number",
             "words": "D-0236: Format 1 is amended before its first release; no format 2. D-0407: NOT decided: ... the format version. "
                      "Stays 1 with the old keys refused by name, or becomes 2?"},
    "OC04": {"title": "Saved sessions that hold an old name key",
             "words": "D-0407: NOT decided: ... old sessions. Refused, or converted? (D-0312 refuses a session of another format with a plain line.)"},
    "OC05": {"title": "What the Gallery writes in `info`, and where a Gallery description lives",
             "words": "D-0408: NOT decided: what the Gallery generator writes in `info` (Gallery question Q8)."},
    "OC06": {"title": "deployment_name with no banner title to take it",
             "words": "D-0411: `deployment_name` is REMOVED; the banner's `ui_label` is the deployment's name. With no banner title the name would be lost: "
                      "the key is kept and listed. Give the deployment a banner, or accept that the name goes?"},
    "OC07": {"title": "The key `display_name` of app features files",
             "words": "D-0407: every display key carries the prefix; D-0411 names only the app features key `ui_title`; D-0412: the key lists are not decided."},
    "OC08": {"title": "The `label` of tables, joins and input fields of a recipe",
             "words": "D-0407: every display key carries the prefix `ui_` in every file kind. recipe_spec.yaml (label_keys): PENDING (Eve, channel M271, not decided). "
                      "Renamed to `ui_label` or kept?"},
    "OC09": {"title": "Display-like keys that no decision names (for example `info.subtitle`)",
             "words": "D-0408: `info` is the free information block: every key written is shown. No line renames or removes these keys."},
    "OC10": {"title": "Comments that name an old key (a person must reword them)",
             "words": "D-0411: the one pass also covers the documentation and the recipe specification. The script never edits a comment."},
    "OC11": {"title": "A group or a plot with no `ui_label`",
             "words": "D-0409 (3): The invented fallbacks go (a group's description as a tab; a plot's `name`; the plot id in title case). "
                      "A group or plot with no `ui_label` would have no name left."},
    "OC13": {"title": "A removal the script cannot place by text (flow mapping, key on a list line)",
             "words": "The script edits whole lines only; a person must remove this key."},
    "OC14": {"title": "A file that cannot be read",
             "words": "The file is not examined; nothing is changed in it."},
    "CONFLICT": {"title": "A key in the old and in the new spelling, or two old keys for one new key",
                 "words": "Not overwritten: a person chooses which text is kept."},
    "NOTE-NAME": {"title": "Note: the text of a removed deployment_name differs from the banner title",
                  "words": "D-0411 (4): the banner's `ui_label` is the deployment's name; the old name text is not kept."},
    "NOTE-TEXT": {"title": "Note: the text of a removed `ui_title` differs from the `ui_label`",
                  "words": "D-0409: the removed text is kept nowhere (it is printed in the list of changes)."},
}
# the order of the section; a case that is only a note comes last
CASE_ORDER = ["OC01", "OC08", "OC07", "OC09", "OC06", "OC11", "OC13", "OC14", "CONFLICT", "OC02", "OC03", "OC04", "OC05", "OC10", "NOTE-NAME", "NOTE-TEXT"]

DISPLAYISH = {"label", "name", "title", "subtitle", "display_name", "ui_title"}
OLD_WORDS = re.compile(r"\bui_title\b|\bdeployment_name\b|\binfo\.label\b|\bbanner\b.*\b(?:title|subtitle)\b")
COMMENT = re.compile(r"(?:^|\s)#\s?(.*)$")
NAME_KEYS = ("label", "name", "ui_title", "ui_label")
SESSION_NAME_KEYS = {"ui_title", "name", "title", "subtitle", "display_name"}
REGISTRY_LABEL = re.compile(r"""["']label["']\s*:""")


@dataclass
class Change:
    rule: str
    file: str
    line: int
    old: str
    new: Optional[str]
    value: str
    ledger: str
    kind: str = ""


@dataclass
class Case:
    case: str
    file: str
    line: int
    detail: str


@dataclass
class Plan:
    root: Path
    changes: List[Change] = field(default_factory=list)
    cases: List[Case] = field(default_factory=list)
    texts: Dict[Path, str] = field(default_factory=dict)
    kind_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    scanned: Set[Path] = field(default_factory=set)
    unexamined: List[str] = field(default_factory=list)

    @property
    def blocking(self) -> List[Case]:
        return [c for c in self.cases if c.case in ("CONFLICT", "OC13")]


@dataclass
class Doc:
    path: Path
    text: str
    root: Optional[yaml.Node]
    kind: str


# -- small helpers on the YAML node graph ---------------------------------------------------------------------------------

def pairs(node) -> list:
    return list(node.value) if isinstance(node, yaml.MappingNode) else []


def key_text(k) -> Optional[str]:
    return k.value if isinstance(k, yaml.ScalarNode) else None


def find(node, key: str):
    for k, v in pairs(node):
        if key_text(k) == key:
            return k, v
    return None


def is_include(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag == INCLUDE_TAG


def content_end(node) -> int:
    """The index just after the last character of a node's content (PyYAML's end mark of a block collection lies at the next token)."""
    if isinstance(node, yaml.ScalarNode) or getattr(node, "flow_style", False):
        return node.end_mark.index
    children = node.value if isinstance(node, yaml.SequenceNode) else [n for pair in node.value for n in pair]
    return content_end(children[-1]) if children else node.end_mark.index


def after_line(text: str, i: int) -> int:
    j = text.find("\n", i)
    return len(text) if j == -1 else j + 1


def scalar_value(node) -> Optional[str]:
    if isinstance(node, yaml.ScalarNode) and node.tag != INCLUDE_TAG and node.value not in ("", "~", "null"):
        return re.sub(r"\s+", " ", node.value).strip()
    return None


def shown_value(node) -> str:
    text = scalar_value(node)
    if text is not None:
        return text if len(text) <= 90 else text[:87] + "..."
    if isinstance(node, yaml.MappingNode):
        return "a mapping (keys: " + ", ".join(str(key_text(k)) for k, _ in node.value) + ")"
    return "(empty)"


def removal_range(doc: Doc, mapping, k, v) -> Optional[Tuple[int, int]]:
    """The whole lines of a pair of a block mapping, or None when the pair cannot be cut out by lines."""
    if getattr(mapping, "flow_style", False):
        return None
    text = doc.text
    start = text.rfind("\n", 0, k.start_mark.index) + 1
    if text[start:k.start_mark.index].strip():
        return None
    key_line_end = after_line(text, k.end_mark.index)
    e = content_end(v)
    end = e if (e > 0 and text[e - 1] == "\n") else after_line(text, e)
    end = max(end, key_line_end)
    while end > key_line_end:                        # a block scalar swallows the blank lines after it: give them back
        previous = text.rfind("\n", 0, end - 1) + 1
        if text[previous:end].strip():
            break
        end = previous
    return start, end


# -- the plan -------------------------------------------------------------------------------------------------------------

class Builder:
    def __init__(self, root: Path):
        self.root = root
        self.plan = Plan(root=root)
        self.docs: Dict[Path, Optional[Doc]] = {}
        self.edits: Dict[Path, Set[Tuple[int, int, str]]] = {}
        self.seen_changes: Set[Tuple[str, int, str]] = set()
        self.seen_cases: Set[Tuple[str, str, int, str]] = set()
        self.examined: Dict[str, Set[Path]] = {}
        self.included: Set[Path] = set()

    # records
    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def case(self, case: str, doc: Optional[Doc], node, detail: str, file: str = "", line: Optional[int] = None) -> None:
        f = self.rel(doc.path) if doc is not None else file
        if line is None:
            line = node.start_mark.line + 1 if node is not None else 0
        key = (case, f, line, detail)
        if key not in self.seen_cases:
            self.seen_cases.add(key)
            self.plan.cases.append(Case(case, f, line, detail))

    def load(self, path: Path, kind: str) -> Optional[Doc]:
        if path in self.docs:
            return self.docs[path]
        try:
            text = path.read_text(encoding="utf-8")
            doc = Doc(path, text, yaml.compose(text, Loader=yaml.SafeLoader), kind)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            self.docs[path] = None
            self.case("OC14", None, None, f"cannot be read: {str(exc).splitlines()[0] if str(exc) else type(exc).__name__}", self.rel(path))
            return None
        self.docs[path] = doc
        self.plan.scanned.add(path)
        self.examined.setdefault(kind, set()).add(path)
        return doc

    def include(self, doc: Doc, value: str) -> Optional[Doc]:
        target = Path(os.path.normpath(doc.path.parent / value))
        try:
            target.relative_to(self.root)
        except ValueError:
            self.case("OC14", doc, None, f"the include {value} points outside the root and is not followed")
            return None
        if not target.is_file():
            self.case("OC14", doc, None, f"the include {value} was not found")
            return None
        self.included.add(target)
        return self.load(target, doc.kind)

    def mapping_of(self, doc: Doc, node) -> Optional[Tuple[Doc, yaml.MappingNode]]:
        if is_include(node):
            inner = self.include(doc, node.value)
            if inner is not None and isinstance(inner.root, yaml.MappingNode):
                return inner, inner.root
            return None
        if isinstance(node, yaml.MappingNode):
            return doc, node
        return None

    # edits
    def edit(self, doc: Doc, start: int, end: int, new: str) -> None:
        self.edits.setdefault(doc.path, set()).add((start, end, new))

    def change(self, rule: Rule, doc: Doc, k, where: str, value: str) -> None:
        line = k.start_mark.line + 1
        key = (self.rel(doc.path), line, rule.id)
        if key in self.seen_changes:
            return
        self.seen_changes.add(key)
        self.plan.changes.append(Change(rule.id, self.rel(doc.path), line, f"{where}.{rule.old}" if where else rule.old,
                                        (f"{where}.{rule.new}" if where else rule.new) if rule.new else None, value, rule.ledger, doc.kind))

    def apply_place(self, doc: Doc, mapping, place: str, where: str, skip: Set[str] = frozenset(), watch: Set[str] = frozenset()) -> None:
        present = {}
        for k, v in pairs(mapping):
            t = key_text(k)
            if t is not None:
                present.setdefault(t, (k, v))
        rules = [r for r in RULES if r.place == place]
        targets: Dict[Optional[str], List[Rule]] = {}
        for r in rules:
            if r.status == "APPLY" and r.old in present and r.id not in skip:
                targets.setdefault(r.new, []).append(r)
        for new, group in targets.items():
            if new is not None and (new in present or len(group) > 1):
                for r in group:
                    why = f"`{new}` is already written" if new in present else "two old keys name the same new key: " + ", ".join(g.old for g in group)
                    self.case("CONFLICT", doc, present[r.old][0], f"{where}.{r.old} -> {new}: {why}; nothing is changed here")
                continue
            for r in group:
                k, v = present[r.old]
                if new is None:
                    span = removal_range(doc, mapping, k, v)
                    if span is None:
                        self.case("OC13", doc, k, f"{where}.{r.old} ({r.id}) is removed by {r.ledger} but it sits in a flow mapping or shares its line; a person must remove it")
                        continue
                    self.edit(doc, span[0], span[1], "")
                    if r.id in ("R04", "R05"):
                        label = present.get("ui_label")
                        old_text, label_text = scalar_value(v), scalar_value(label[1]) if label else None
                        if old_text is not None and old_text != label_text:
                            self.case("NOTE-TEXT", doc, k, f"{where}.ui_title \"{old_text}\" is removed; ui_label is \"{label_text}\"")
                else:
                    start, end = k.start_mark.index, k.end_mark.index
                    quote = doc.text[start] if doc.text[start] in "\"'" else ""
                    self.edit(doc, start, end, f"{quote}{new}{quote}")
                self.change(r, doc, k, where, shown_value(v))
        for r in rules:
            if r.status == "OPEN" and r.old in present:
                self.case(r.case, doc, present[r.old][0], f"{where}.{r.old}: {shown_value(present[r.old][1])}")
        covered = {r.old for r in rules}
        for name in sorted(watch - covered):
            if name in present:
                self.case("OC09", doc, present[name][0], f"{where}.{name}: {shown_value(present[name][1])}")

    # kinds of file
    def recipe(self, doc: Doc) -> None:
        top = doc.root
        self.apply_place(doc, top, "recipe.top", "", watch=DISPLAYISH - {"description"})
        found = find(top, "info")
        res = self.mapping_of(doc, found[1]) if found else None
        if res is None:
            self.case("OC01", doc, found[0] if found else top, "the recipe has no `info` mapping, so no name")
        else:
            idoc, imap = res
            self.apply_place(idoc, imap, "recipe.info", "info", watch={"subtitle", "title", "display_name"})
            if not any(find(imap, k) for k in NAME_KEYS):
                self.case("OC01", idoc, imap if imap.value else (found[0] if found else imap), "`info` has no name key (label, name, ui_title or ui_label)")
        self.sections(doc, top, "data_schemas", "recipe.schema")
        self.sections(doc, top, "additional_datasets_schemas", "recipe.schema")
        meta = find(top, "metadata_schema")
        if meta is not None:
            res = self.mapping_of(doc, meta[1])
            if res:
                self.schema(res[0], res[1], "recipe.schema", "metadata_schema")
        self.sections(doc, top, "joins", "recipe.join")
        groups = find(top, "analysis_groups")
        res = self.mapping_of(doc, groups[1]) if groups else None
        if res is None:
            return
        for gk, gv in pairs(res[1]):
            r = self.mapping_of(res[0], gv)
            if r is None:
                continue
            gdoc, gmap = r
            where = f"analysis_groups.{key_text(gk)}"
            if find(gmap, "ui_label") is None:
                self.case("OC11", gdoc, gk, f"{where} has no ui_label")
            self.apply_place(gdoc, gmap, "recipe.group", where, watch=DISPLAYISH)
            plots = find(gmap, "plots")
            pres = self.mapping_of(gdoc, plots[1]) if plots else None
            for pk, pv in pairs(pres[1]) if pres else []:
                q = self.mapping_of(pres[0], pv)
                if q is None:
                    continue
                pdoc, pmap = q
                pwhere = f"{where}.plots.{key_text(pk)}"
                if find(pmap, "ui_label") is None:
                    self.case("OC11", pdoc, pk, f"{pwhere} has no ui_label")
                self.apply_place(pdoc, pmap, "recipe.plot", pwhere, watch=DISPLAYISH - {"description"})

    def sections(self, doc: Doc, top, section: str, place: str) -> None:
        found = find(top, section)
        res = self.mapping_of(doc, found[1]) if found else None
        for k, v in pairs(res[1]) if res else []:
            r = self.mapping_of(res[0], v)
            if r:
                if place == "recipe.schema":
                    self.schema(r[0], r[1], place, f"{section}.{key_text(k)}")
                else:
                    self.apply_place(r[0], r[1], place, f"{section}.{key_text(k)}", watch=DISPLAYISH - {"description"})

    def schema(self, doc: Doc, mapping, place: str, where: str) -> None:
        self.apply_place(doc, mapping, place, where, watch=DISPLAYISH - {"description"})
        fields = find(mapping, "input_fields")
        res = self.mapping_of(doc, fields[1]) if fields else None
        for k, v in pairs(res[1]) if res else []:
            r = self.mapping_of(res[0], v)
            if r:
                self.apply_place(r[0], r[1], "recipe.field", f"{where}.input_fields.{key_text(k)}")

    def deployment(self, doc: Doc) -> None:
        top = doc.root
        if not isinstance(top, yaml.MappingNode):
            return
        branding = find(top, "branding")
        bres = self.mapping_of(doc, branding[1]) if branding else None
        banner = find(bres[1], "banner") if bres else None
        ares = self.mapping_of(bres[0], banner[1]) if (bres and banner) else None
        skip: Set[str] = set()
        name = find(top, "deployment_name")
        if name is not None:
            title = next((find(ares[1], k) for k in ("title", "ui_label") if ares and find(ares[1], k)), None)
            if title is None:
                skip.add("R08")
                self.case("OC06", doc, name[0], f"deployment_name \"{scalar_value(name[1])}\" has no banner title to take it; the key is kept")
            elif scalar_value(name[1]) != scalar_value(title[1]):
                banner_title = f"\"{scalar_value(title[1])}\"" if scalar_value(title[1]) else "empty (a hidden banner)"
                self.case("NOTE-NAME", doc, name[0], f"deployment_name \"{scalar_value(name[1])}\" is removed; the banner title is {banner_title}")
        self.apply_place(doc, top, "deployment.top", "", skip=skip, watch={"title", "subtitle", "label", "display_name", "ui_title"})
        if ares:
            self.apply_place(ares[0], ares[1], "deployment.banner", "branding.banner")

    def app_features(self, doc: Doc) -> None:
        if isinstance(doc.root, yaml.MappingNode):
            self.apply_place(doc, doc.root, "app_features.top", "", watch={"title", "subtitle", "label"})

    def comments(self, doc: Doc) -> None:
        for number, line in enumerate(doc.text.splitlines(), 1):
            m = COMMENT.search(line)
            if m and OLD_WORDS.search(m.group(1)):
                self.case("OC10", doc, None, m.group(1).strip()[:110], line=number)


def classify(rel: str, family: str) -> str:
    parts = Path(rel).parts
    name = Path(rel).name
    if family == "gallery":
        return "Gallery bundles"
    if family == "fixture":
        return "test fixtures"
    if family == "deployment":
        return "deployment templates" if "templates" in parts or "template" in name else "deployment files"
    if family == "app_features":
        return "app features files"
    return "recipe templates" if "templates" in parts else "recipes"


def yaml_files(base: Path) -> List[Path]:
    found: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        found += [Path(dirpath) / n for n in sorted(filenames) if n.endswith((".yaml", ".yml"))]
    return found


def session_cases(b: Builder, root: Path) -> None:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if "_sessions" in Path(dirpath).relative_to(root).parts:
            files += [Path(dirpath) / n for n in sorted(filenames) if n.endswith(".json")]
    withkeys = 0
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            b.case("OC04", None, None, "cannot be read as JSON", b.rel(path))
            continue
        found: Set[str] = set()

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in SESSION_NAME_KEYS:
                        found.add(k)
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(data)
        if found:
            withkeys += 1
            b.case("OC04", None, None, "holds the keys " + ", ".join(sorted(found)), b.rel(path))
    b.case("OC04", None, None, f"{len(files)} session file(s) found under a `_sessions` folder, {withkeys} with an old name key. "
           "The session writer's own `label` is the user's label of the session, not a recipe name (app/modules/session_manager.py).", "")


def registry_cases(b: Builder, root: Path) -> None:
    counts = Counter()
    for lib in sorted((root / "libs").glob("*/src")) if (root / "libs").is_dir() else []:
        for path in lib.rglob("*.py"):
            n = len(REGISTRY_LABEL.findall(path.read_text(encoding="utf-8", errors="replace")))
            if n:
                counts[b.rel(path)] = n
    per_lib: Counter = Counter()
    for f, n in counts.items():
        per_lib[Path(f).parts[1]] += n
    detail = (f"{sum(counts.values())} place(s) in {len(counts)} file(s) write a `\"label\"` key in libs/*/src (text match; "
              + ", ".join(f"{lib}: {n}" for lib, n in sorted(per_lib.items())) + ")") if counts else "no libs/*/src folder in this root (0 places)"
    b.case("OC02", None, None, detail)


def build_plan(root: Path) -> Plan:
    root = Path(os.path.abspath(root))
    b = Builder(root)
    masters: List[Tuple[Path, str]] = []
    all_files: List[Tuple[Path, str, str]] = []
    for folder, family in SCAN:
        base = root / folder
        if not base.is_dir():
            continue
        for path in yaml_files(base):
            all_files.append((path, family, classify(str(path.relative_to(root)), family)))
    formats: Counter = Counter()
    gallery_info: Counter = Counter()
    gallery_bundles = 0
    for path, family, kind in all_files:
        doc = b.load(path, kind)
        if doc is None or not isinstance(doc.root, yaml.MappingNode):
            continue
        if family in ("deployment", "app_features"):
            (b.deployment if family == "deployment" else b.app_features)(doc)
        elif find(doc.root, "spec_version") is not None or (family == "gallery" and path.name == "data_analysis_recipe.yaml"):
            b.recipe(doc)
            v = find(doc.root, "spec_version")
            formats[scalar_value(v[1]) if v else "(none)"] += 1
            if family == "gallery":
                gallery_bundles += 1
                info = find(doc.root, "info")
                res = b.mapping_of(doc, info[1]) if info else None
                for k, _ in pairs(res[1]) if res else []:
                    gallery_info[key_text(k)] += 1
    for path, family, kind in all_files:
        doc = b.docs.get(path)
        if doc is not None:
            b.comments(doc)
    for path, family, kind in all_files:
        doc = b.docs.get(path)
        if (doc is not None and family in ("recipe", "fixture", "gallery") and isinstance(doc.root, yaml.MappingNode)
                and find(doc.root, "spec_version") is None and path not in b.included and path.name != "data_analysis_recipe.yaml"):
            b.plan.unexamined.append(b.rel(path))
    b.case("OC03", None, None, "spec_version found in " + (", ".join(f"{k} x{n}" for k, n in sorted(formats.items())) or "no recipe") + " master recipe(s)")
    bundles_meta = len(list((root / "assets/gallery_data").glob("*/example_meta.md"))) if (root / "assets/gallery_data").is_dir() else 0
    b.case("OC05", None, None, f"{gallery_bundles} Gallery bundle(s); keys written in their `info`: "
           + (", ".join(f"{k} x{n}" for k, n in sorted(gallery_info.items())) or "none")
           + f"; {bundles_meta} bundle(s) with an example_meta.md (the guidance text)")
    registry_cases(b, root)
    session_cases(b, root)

    # texts
    for path, edits in b.edits.items():
        doc = b.docs[path]
        text = doc.text
        for start, end, new in sorted(edits, reverse=True):
            text = text[:start] + new + text[end:]
        if text != doc.text:
            b.plan.texts[path] = text
    counts: Dict[str, Dict[str, int]] = {k: {"files": 0, "changes": 0} for k in KIND_ORDER}
    for kind, files in b.examined.items():
        counts[kind]["files"] = len(files)
    for c in b.plan.changes:
        counts[c.kind]["changes"] += 1
    b.plan.kind_counts = counts
    b.plan.changes.sort(key=lambda c: (c.file, c.line, c.rule))
    b.plan.cases.sort(key=lambda c: (CASE_ORDER.index(c.case) if c.case in CASE_ORDER else 99, c.file, c.line))
    return b.plan


# -- output ---------------------------------------------------------------------------------------------------------------

def lines_of(plan: Plan, md: bool, header: str) -> List[str]:
    h1, h2 = ("# ", "## ") if md else ("", "")
    out: List[str] = [h1 + header]
    cases_by: Dict[str, List[Case]] = {}
    for c in plan.cases:
        cases_by.setdefault(c.case, []).append(c)
    placed = plan.changes
    real = {k: [e for e in v if e.file or e.line] for k, v in cases_by.items() if not k.startswith("NOTE")}
    out += ["", h2 + "Summary"]
    out.append(f"{len(plan.changes)} change(s) in {len(plan.texts)} file(s); "
               f"{sum(len(v) for v in real.values())} listed place(s) in {len(real)} open case(s); "
               f"{len(cases_by.get('CONFLICT', []))} conflict(s); {len(cases_by.get('OC13', []))} removal(s) the script cannot place.")
    out.append("")
    out.append(("| " if md else "  ") + f"{'kind of file':<22} {'files read':>10} {'changes':>8}" + (" |" if md else ""))
    for kind in KIND_ORDER:
        n = plan.kind_counts.get(kind, {"files": 0, "changes": 0})
        out.append(("| " if md else "  ") + f"{kind:<22} {n['files']:>10} {n['changes']:>8}" + (" |" if md else ""))
    by_rule = Counter(c.rule for c in placed)
    out.append("")
    out.append("by rule: " + (", ".join(f"{r.id} {r.old}->{r.new or 'REMOVED'} ({r.ledger}) x{by_rule[r.id]}" for r in RULES if r.status == "APPLY") or "-"))
    out += ["", h2 + "Changes the dry run would make"]
    if not placed:
        out.append("nothing to change")
    last = None
    for c in placed:
        if md and c.file != last:
            out.append(f"\n**{c.file}**")
        last = c.file
        action = f"{c.old} -> {c.new}" if c.new else f"{c.old} REMOVED (value: {c.value})"
        out.append(("- " if md else "") + f"{c.file}:{c.line}: {c.rule} {action}  [{c.ledger}]")
    out += ["", h2 + "CANNOT BE DECIDED BY THE SCRIPT"]
    out.append("(listed, never changed; each line is a place a person or the owner decides)")
    for case in [c for c in CASE_ORDER if c in cases_by] + sorted(c for c in cases_by if c not in CASE_ORDER):
        info = OPEN_CASES.get(case, {"title": "(case not named)", "words": ""})
        entries = cases_by[case]
        counted = len([e for e in entries if e.file or e.line])
        out.append("")
        out.append(("### " if md else "") + f"{case}: {info['title']} -- {counted} place(s)")
        if info["words"]:
            out.append(("> " if md else "  ") + info["words"])
        for e in entries:
            where = f"{e.file}:{e.line}: " if e.line else (f"{e.file}: " if e.file else "")
            out.append(("- " if md else "  ") + where + e.detail)
    if plan.unexamined:
        out += ["", f"{len(plan.unexamined)} file(s) read but not examined as a recipe (no spec_version, included by no recipe): "
                + ", ".join(plan.unexamined[:12]) + (" ..." if len(plan.unexamined) > 12 else "")]
    return out


def apply_refusal(root: Path, given: bool) -> Optional[str]:
    waits = ("REFUSED: --apply is not available on the repository. The names pass is ONE migration and waits for the owner's answers "
             "(ledger D-0407 to D-0412; task NAMES-UI-LABEL-EVERYWHERE). It can only be applied to a copy of the files.")
    if not given:
        return waits + " Give --root with the folder of a copy."
    real, project = Path(os.path.realpath(root)), Path(os.path.realpath(PROJECT_ROOT))
    if project.is_relative_to(real):
        return waits + f" {root} is the repository or a folder that contains it."
    if (root / ".git").exists():
        return waits + f" {root} is a git working tree, not a copy."
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=None, help="the folder to read (default: the project root); the folder that holds config/ and assets/gallery_data/")
    parser.add_argument("--report", default=None, help="also write the list as markdown to this file")
    parser.add_argument("--apply", action="store_true", help="write the changes; only on a copy (--root given, not the repository, not a git working tree)")
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(args.root)) if args.root else PROJECT_ROOT
    if args.apply:
        refusal = apply_refusal(root, args.root is not None)
        if refusal:
            print(refusal, file=sys.stderr)
            return 3
    plan = build_plan(root)
    if args.report:
        target = Path(os.path.abspath(args.report))
        if target in plan.scanned or Path(os.path.realpath(target)) in {Path(os.path.realpath(p)) for p in plan.scanned}:
            print(f"REFUSED: --report would overwrite a file the script reads: {target}", file=sys.stderr)
            return 3
    header = ("APPLY" if args.apply else "DRY RUN: nothing is written") + f". Root: {root}"
    for line in lines_of(plan, False, header):
        print(line)
    if args.report:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines_of(plan, True, "Names pass: dry run report (" + header + ")")) + "\n", encoding="utf-8")
        print(f"report written: {target}")
    if args.apply:
        real_root = Path(os.path.realpath(root))
        for path, text in plan.texts.items():
            if not Path(os.path.realpath(path)).is_relative_to(real_root):
                print(f"REFUSED: {path} is outside the root; nothing more is written", file=sys.stderr)
                return 3
            path.write_text(text, encoding="utf-8")
        print(f"applied: {len(plan.texts)} file(s) written")
        return 2 if plan.blocking else 0
    if plan.blocking:
        return 2
    return 1 if plan.texts else 0


if __name__ == "__main__":
    sys.exit(main())
