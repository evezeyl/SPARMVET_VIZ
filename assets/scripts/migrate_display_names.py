"""DRY RUN of the names pass: lists what the migration of the display names would change, and what it cannot decide.

The names pass is ONE migration (ledger D-0407 to D-0412, D-0459; task NAMES-UI-LABEL-EVERYWHERE). It waits for the owner's
answers, so in this version the script only PLANS: by default it changes nothing and prints, per file, each change it would make
(file, line, old key path, new key path, the ledger number the rule rests on), a summary per kind of file, and a section
"CANNOT BE DECIDED BY THE SCRIPT" with every place that no decision covers.

The rules it applies (one table, `RULES` in this file, each with the ledger line it rests on):
  recipes (and the files they include, Gallery bundles, templates, test fixtures):
    info.label, info.name, info.ui_title  ->  info.ui_label                       (D-0410)
    the `ui_title` of a group and of a plot entry is removed, its text printed   (D-0409, D-0410)
    the `label` of tables, joins and input fields -> ui_label                     (D-0468)
  deployment files:
    branding.banner.title -> ui_label, branding.banner.subtitle -> description    (D-0411)
    deployment_name is removed, when a banner title takes its place              (D-0411)
  app features files:
    the key `ui_title {text, subtitle, visible}` is removed, what it set is printed (D-0411, D-0470);
    a `visible: false` would move to ONE switch key of the deployment file; that key has no name yet (D-0472),
    so `BANNER_SWITCH_KEY` is unset, such a file keeps its `ui_title` and the case is listed
Whatever else it finds that no decision covers is listed, never changed: the banner switch, `display_name` of app features, a name
that has nowhere to go, `info.subtitle`, the Gallery generator, and so on. Decided points that need no change are listed with their
counts (registries not renamed, format number 1, old sessions refused); a recipe with no name is listed as "would get the advice".
A key present in the old and in the new spelling, or two old keys for one new key, is a CONFLICT: reported, not overwritten.

It edits the TEXT at the positions the YAML parser reports, so comments, blank lines, key order, quoting and `!include` lines stay
byte for byte outside the changed keys. A second run on a migrated copy finds nothing to change.

Modes:
  (default)   DRY RUN: nothing is written.
  --report F  also write the list as markdown to the file F (never over a file it scans).
  --apply     writes the planned changes, but ONLY on a copy: --root must be given and must not be the repository itself, a folder
              that contains it or a git working tree. On the repository it refuses (exit 3): the pass waits for the owner's answers.

Exit codes: dry run 0 = nothing to change, 1 = something would change; --apply 0 = written; 2 = a conflict, a place that cannot
be placed or a banner switch with no key name exists (what could be placed is still planned or written); 3 = refused to run (--apply on the repository, bad --report).

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
    Rule("R10", "recipe.schema", "label", "ui_label", "D-0468", "her words: 2.I think yes because we need to differentiate the recipe and the python code. (the review session's reading, not hers: the display keys `label` of RECIPE files (`info`, table, join, field) become `ui_label`)"),
    Rule("R11", "recipe.join", "label", "ui_label", "D-0468", "her words: 2.I think yes because we need to differentiate the recipe and the python code. (the review session's reading, not hers: the display keys `label` of RECIPE files (`info`, table, join, field) become `ui_label`)"),
    Rule("R12", "recipe.field", "label", "ui_label", "D-0468", "her words: 2.I think yes because we need to differentiate the recipe and the python code. (the review session's reading, not hers: the display keys `label` of RECIPE files (`info`, table, join, field) become `ui_label`)"),
    Rule("R13", "app_features.top", "display_name", None, "D-0407", "D-0411 names only `ui_title` of the app features file; D-0412: the key lists are not decided", "OPEN", "OC07"),
    Rule("R14", "deployment.switch", "ui_title.visible: false", None, "D-0472", "her words: I should sit in the deployement H1; NOT decided: the name of the key and its place inside the deployment file", "OPEN", "OC15"),
]

# The ONE constant of the recipe banner switch (D-0470, D-0472): the dotted path of its key in a deployment file, for example
# "branding.<name>" or "<name>". UNSET until the owner names it: while it is None the script refuses to write that key, keeps the
# `ui_title` of an app features file that says `visible: false` and lists the case (OC15). Set it, and the pass writes
# `<key>: false` at the end of that block of every deployment that names the app features file as its `default_app_features`.
BANNER_SWITCH_KEY: Optional[str] = None

OPEN_CASES: Dict[str, Dict[str, str]] = {
    "OC01": {"title": "A recipe with no name: would get the advice",
             "words": "D-0470 (trial; her words: ok, we can try H1 and C - worse case we change after): a recipe name in `info.ui_label` is OPTIONAL, the file name is the fallback where a name is shown, "
                      "a missing name is an ADVICE, not an error (the review session's reading of option C). D-0408 and D-0410 disagreed on the check I01; D-0470 modifies D-0410."},
    "OC02": {"title": "DECIDED, not renamed: the `\"label\"` strings of the Python code (action forms, registries)",
             "words": "D-0468: the review session's reading (not her words): the `\"label\"` strings of the Python code are not recipe keys and are not renamed by this pass. Counted by text match, not a parse."},
    "OC03": {"title": "DECIDED: the recipe format number stays 1",
             "words": "D-0469 (her words: we are still in development so the same format can stay): the recipe format number stays 1. The count shows the spec_version of every master recipe."},
    "OC04": {"title": "DECIDED: old session files are refused, not converted",
             "words": "D-0471 (the review session's reading, resting on D-0312; no words of hers confirm this point): old session files are refused with a plain line, no conversion. The script lists where a session holds a name key and never touches a session."},
    "OC05": {"title": "What the Gallery writes in `info`, and where a Gallery description lives",
             "words": "D-0408: NOT decided: what the Gallery generator writes in `info` (Gallery question Q8). The KEY of a Gallery bundle is renamed like any recipe's "
                      "(D-0407: `ui_` in every file kind; D-0468: the `label` of recipe files); what `info` is for in an example is open."},
    "OC06": {"title": "deployment_name with no banner title to take it",
             "words": "D-0411: `deployment_name` is REMOVED; the banner's `ui_label` is the deployment's name. With no banner title the name would be lost: "
                      "the key is kept and listed. Give the deployment a banner, or accept that the name goes?"},
    "OC07": {"title": "The key `display_name` of app features files",
             "words": "D-0407: every display key carries the prefix; D-0411 names only the app features key `ui_title`; D-0412: the key lists are not decided."},
    "OC09": {"title": "Display-like keys that no decision names (for example `info.subtitle`)",
             "words": "D-0408: `info` is the free information block: every key written is shown. No line renames or removes these keys."},
    "OC10": {"title": "Comments that name an old key (a person must reword them)",
             "words": "D-0411: the one pass also covers the documentation and the recipe specification. The script never edits a comment."},
    "OC11": {"title": "A group or a plot with no `ui_label`",
             "words": "D-0409 (3): The invented fallbacks go (a group's description as a tab; a plot's `name`; the plot id in title case). "
                      "A group or plot with no `ui_label` would have no name left."},
    "OC13": {"title": "A removal or an insertion the script cannot place by text (flow mapping, key on a list line, no block to receive it)",
             "words": "The script edits whole lines only; a person must make this change."},
    "OC14": {"title": "A file that cannot be read",
             "words": "The file is not examined; nothing is changed in it."},
    "OC15": {"title": "The on/off switch of the recipe banner: its key has no name yet",
             "words": "D-0470: ONE switch stays (show the recipe name: yes or no; no text override). D-0472 (her words: I should sit in the deployement H1): it sits in the DEPLOYMENT file; the key's name "
                      "and its place are NOT decided. The script cannot write it: such an app features file keeps its `ui_title` until BANNER_SWITCH_KEY is set."},
    "CONFLICT": {"title": "A key in the old and in the new spelling, or two old keys for one new key",
                 "words": "Not overwritten: a person chooses which text is kept."},
    "NOTE-NAME": {"title": "Note: the text of a removed deployment_name differs from the banner title",
                  "words": "D-0411 (4): the banner's `ui_label` is the deployment's name; the old name text is not kept."},
    "NOTE-TEXT": {"title": "Note: the text of a removed `ui_title` differs from the `ui_label`",
                  "words": "D-0409: the removed text is kept nowhere (it is printed in the list of changes)."},
}
# the order of the sections; the decided ones, the advice and the notes are not open
CASE_ORDER = ["OC15", "OC07", "OC09", "OC06", "OC11", "OC13", "OC14", "CONFLICT", "OC05", "OC10", "OC01", "OC02", "OC03", "OC04", "NOTE-NAME", "NOTE-TEXT"]
DECIDED_CASES = ("OC02", "OC03", "OC04")
ADVICE_CASES = ("OC01",)
BLOCKING_CASES = ("CONFLICT", "OC13", "OC15")

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
    facts: List[str] = field(default_factory=list)     # what the owner needs to name the banner switch (D-0472)

    @property
    def blocking(self) -> List[Case]:
        return [c for c in self.cases if c.case in BLOCKING_CASES]


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
        return "a mapping (" + ", ".join(f"{key_text(k)}: {scalar_value(v) if scalar_value(v) is not None else '(empty)'}" for k, v in node.value) + ")"
    return "(empty)"


def is_false(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag.endswith(":bool") and node.value.lower() in ("false", "no", "off", "n")


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
        self.deployments: List[Tuple[Doc, Optional[str], Optional[yaml.MappingNode], str]] = []   # doc, default_app_features, branding block, what its banner shows

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
        default = find(top, "default_app_features")
        shows = "no banner"
        if ares:
            shows = "; ".join(f"{label} {scalar_value(v[1])!r}" for label, names in (("title", ("title", "ui_label")), ("line", ("subtitle", "description")), ("logo", ("logo_url",)))
                              for v in [next((find(ares[1], n) for n in names if find(ares[1], n)), None)] if v and scalar_value(v[1])) or "an empty banner"
        branding_keys = ", ".join(str(key_text(k)) for k, _ in pairs(bres[1])) if bres else "(no branding block)"
        banner_keys = ", ".join(str(key_text(k)) for k, _ in pairs(ares[1])) if ares else "(no banner)"
        self.plan.facts.append(f"{self.rel(doc.path)}: default_app_features = {scalar_value(default[1]) if default else '(none)'}; "
                               f"branding keys: {branding_keys}; banner keys: {banner_keys}; the banner shows: {shows}")
        self.deployments.append((doc, scalar_value(default[1]) if default else None, bres[1] if bres else None, shows))

    def app_features(self, doc: Doc) -> None:
        top = doc.root
        if not isinstance(top, yaml.MappingNode):
            return
        found_name = find(top, "name")
        name = (scalar_value(found_name[1]) if found_name else None) or doc.path.stem
        ui = find(top, "ui_title")
        skip: Set[str] = set()
        if ui is None:
            self.plan.facts.append(f"{self.rel(doc.path)}: does not set ui_title (the recipe banner is shown)")
        else:
            self.plan.facts.append(f"{self.rel(doc.path)}: ui_title sets {shown_value(ui[1])}")
            visible = find(ui[1], "visible") if isinstance(ui[1], yaml.MappingNode) else None
            if visible is not None and is_false(visible[1]):
                self.banner_switch(doc, name, ui, skip)
        self.apply_place(doc, top, "app_features.top", "", skip=skip, watch={"title", "subtitle", "label"})

    def banner_switch(self, doc: Doc, name: str, ui, skip: Set[str]) -> None:
        """An app features file that hides the recipe banner (`ui_title.visible: false`): the switch moves to the deployment file (D-0472)."""
        users = [d for d in self.deployments if d[1] == name]
        facts = (f"ui_title.visible is false, so HOME shows no recipe banner today; deployments that name this file as default_app_features: "
                 + (", ".join(self.rel(d[0].path) for d in users) or "none")
                 + "; the banner of each deployment shows: " + ("; ".join(f"{self.rel(d[0].path)}: {d[3]}" for d in users) or "-"))
        skip.add("R09")
        if BANNER_SWITCH_KEY is None:
            self.case("OC15", doc, ui[0], facts + ". NOT WRITTEN: the key of the switch has no name yet (D-0472); this ui_title is kept")
            return
        if not users:
            self.case("OC15", doc, ui[0], facts + ". NOT WRITTEN: no deployment names this file as its default, so the switch has nowhere to go; this ui_title is kept")
            return
        parts = BANNER_SWITCH_KEY.split(".")
        planned = []
        for d_doc, _default, branding, _shows in users:
            parent = d_doc.root if len(parts) == 1 else (branding if len(parts) == 2 and parts[0] == "branding" else None)
            if parent is None or getattr(parent, "flow_style", False) or not parent.value:
                self.case("OC13", d_doc, None, f"the switch `{BANNER_SWITCH_KEY}` cannot be placed by text: the block that should hold it is missing, empty or in flow style", line=1)
                return self.keep_ui_title(doc, ui, facts)
            if find(parent, parts[-1]):
                self.case("CONFLICT", d_doc, find(parent, parts[-1])[0], f"`{BANNER_SWITCH_KEY}` is already written; nothing is changed here")
                return self.keep_ui_title(doc, ui, facts)
            col = parent.value[0][0].start_mark.column
            pos = after_line(d_doc.text, content_end(parent.value[-1][1]))
            lead = "\n" if pos == len(d_doc.text) and not d_doc.text.endswith("\n") else ""
            planned.append((d_doc, pos, f"{lead}{' ' * col}{parts[-1]}: false\n", parent.value[0][0]))
        skip.discard("R09")
        for d_doc, pos, text, anchor in planned:
            self.edit(d_doc, pos, pos, text)
            self.plan.changes.append(Change("R14", self.rel(d_doc.path), anchor.start_mark.line + 1, f"{self.rel(doc.path)}: ui_title.visible: false",
                                            BANNER_SWITCH_KEY, "false", "D-0472", d_doc.kind))

    def keep_ui_title(self, doc: Doc, ui, facts: str) -> None:
        self.case("OC15", doc, ui[0], facts + ". NOT WRITTEN: the switch could not be placed in every deployment; this ui_title is kept")

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
    pending_app: List[Doc] = []
    for path, family, kind in all_files:
        doc = b.load(path, kind)
        if doc is None or not isinstance(doc.root, yaml.MappingNode):
            continue
        if family == "deployment":
            b.deployment(doc)
        elif family == "app_features":
            pending_app.append(doc)          # after every deployment is read: the banner switch needs to know which deployment uses it
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
    for doc in pending_app:
        b.app_features(doc)
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
    def section_of(case: str) -> str:
        return "decided" if case in DECIDED_CASES else "advice" if case in ADVICE_CASES else "note" if case.startswith("NOTE") else "open"
    real = {k: [e for e in v if e.file or e.line] for k, v in cases_by.items() if section_of(k) == "open"}
    out += ["", h2 + "Summary"]
    out.append(f"{len(plan.changes)} change(s) in {len(plan.texts)} file(s); "
               f"{sum(len(v) for v in real.values())} listed place(s) in {len(real)} open case(s); "
               f"{len(cases_by.get('CONFLICT', []))} conflict(s); {len(cases_by.get('OC13', []))} change(s) the script cannot place; "
               f"{len([e for e in cases_by.get('OC01', []) if e.file])} recipe(s) would get the advice (no name).")
    out.append("")
    if md:
        out += ["| kind of file | files read | changes |", "|---|---:|---:|"]
    else:
        out.append(f"  {'kind of file':<22} {'files read':>10} {'changes':>8}")
    for kind in KIND_ORDER:
        n = plan.kind_counts.get(kind, {"files": 0, "changes": 0})
        out.append(f"| {kind} | {n['files']} | {n['changes']} |" if md else f"  {kind:<22} {n['files']:>10} {n['changes']:>8}")
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
    def block(section: str, heading: str, intro: str) -> None:
        out.extend(["", h2 + heading])
        out.append(intro)
        for case in [c for c in CASE_ORDER if c in cases_by] + sorted(c for c in cases_by if c not in CASE_ORDER):
            if section_of(case) != section:
                continue
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

    block("open", "CANNOT BE DECIDED BY THE SCRIPT", "(listed, never changed; each line is a place a person or the owner decides)")
    out += ["", h2 + "Facts to name the recipe banner switch (D-0472)",
            "(per deployment file: its default app features file and the keys of its `branding` block; per app features file: what its `ui_title` sets today. "
            "The list of allowed deployment keys does not exist yet: D-0412 asks for it, it comes with the deployment standard; today the only refusal tables are "
            "app/modules/renamed_keys.py and the readers app/src/bootloader.py:591, 874, 877-879)"]
    out += [("- " if md else "  ") + f for f in plan.facts]
    block("advice", "WOULD GET THE ADVICE (no recipe name)", "(not an error, D-0470: the file name is shown where a name is needed)")
    block("decided", "DECIDED, nothing for the script to change (counts only)", "(D-0468, D-0469, D-0471)")
    block("note", "Notes on the changes above", "(consequences of rules that are applied)")
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
    if any(c.case == "OC15" for c in plan.cases):
        print("NOT WRITTEN: an app features file hides the recipe banner (ui_title.visible: false) and the key of the switch that replaces it has no name yet "
              "(D-0472: it sits in the deployment file; name and place not decided). That ui_title is kept. Name it in BANNER_SWITCH_KEY and run again.", file=sys.stderr)
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
