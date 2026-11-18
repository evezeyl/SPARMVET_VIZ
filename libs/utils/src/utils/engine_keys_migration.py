"""Rewrite recipes to the shape of 2026-11-17/18 (engine keys, format 1 amended before its first release, D-0236).

What it writes, rule by rule (the checker `check_recipe_file` is the judge; a rewritten recipe passes it with no old-shape code):
  a. Tiers (D-0250). `wrangling: {tier1: [...], tier2: [...]}` of a table and `steps: {tier1: [...]}` of a join become
     `tier1: {steps: [...]}` and `tier2: {steps: [...]}` at the table or join; `steps: {tier3: [...]}` of a plot entry becomes
     `tier3: {steps: [...]}`. An included fragment (`wrangling: !include f`) becomes one include per tier
     (`tier1: !include f`): a fragment that holds one tier keeps its file name and its root key becomes `steps`; a fragment that
     holds two tiers is split into `<name>_tier1.yaml` and `<name>_tier2.yaml` (PROVISIONAL naming) and the old file is removed.
     A fragment included by several recipes is rewritten once and every includer is updated. An empty tier stays, written
     `tier1: {steps: []}` (the checker accepts an empty tier); a table or a join without `tier1` gets `tier1: {steps: []}` (required).
  b. The plot entry has no `spec:` (D-0237). Its content is written in the entry; a plot whose spec was in its own file
     (`spec: !include plots/p.yaml`) becomes `p: !include plots/p.yaml` and that file holds the WHOLE entry (D-0252). Key order
     written: plot_engine (if there), ui_label, ui_title, description, comment, taxonomy, the content, tier3.
  c. Names (D-0253). `label` becomes `ui_label` at groups and plot entries. The pending places (`info`, tables and joins, the
     entries of `input_fields`) are renamed only when the table `label_keys` of `recipe_spec.yaml` says `ui_label` for them: Eve's
     answer is a one-line change of that table followed by a re-run.
  d. The old `title:` of a plot content (D-0253, D-0255, D-0258; PROVISIONAL reading of the coordinator, not objected to): the text
     is written as the `title` argument of the plot's `labs` layer (added when there is none; set when there is one: today the root
     title is applied after the layers and wins over a labs title, so the picture stays the same) AND as `ui_title` of the entry.
  e. The four dead `plot_defaults` keys are removed; each removal is printed with its old value and the recipe (D-0242, D-0241).
  f. Theme (D-0258). A recipe in which a plot would be drawn with the built-in `theme_bw` (no complete theme named for it, neither
     in the plot nor in `plot_defaults`) gets `theme_bw` written once in `plot_defaults`: a plot theme (L4) wins over it (L2), so one
     line is both the shortest form and the same picture. The built-in itself is removed from the code later.

It edits the TEXT at the positions the YAML parser reports (as `recipe_migration.py` and `strict_form_migration.py` do), so every
comment, blank line and `!include` line stays. Whatever it cannot place it refuses with a plain message and changes nothing there
(D-0050). Every change is an event; nothing is written by `migrate` itself: the caller writes `Result.texts` (`--apply`) or only
prints (`--check`). A second run finds nothing to change.

# @deps
# provides: function:migrate, class:Result, class:Event
# consumes: libs/utils/src/utils/recipe_spec.yaml (label_keys, removed), libs/utils/src/utils/recipe_check.py (spec), libs/utils/src/utils/recipe_migration.py (_content_end)
# consumed_by: assets/scripts/migrate_recipe_engine_keys.py, libs/utils/tests/test_engine_keys_migration.py
# doc: .claude/design/recipe_format_spec.md (4.1), decisions D-0236, D-0237, D-0241, D-0242, D-0250 to D-0253, D-0255, D-0258
# @end_deps
"""
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, List, Optional, Set, Tuple

import yaml

from utils.recipe_check import spec as recipe_spec
from utils.recipe_migration import _content_end

_SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
_ENTRY_ORDER = ("plot_engine", "label", "ui_label", "ui_title", "description", "comment", "taxonomy")
_TIER_KEYS = {"schema": ("tier1", "tier2"), "join": ("tier1", "tier2"), "plot": ("tier3",)}


@dataclass
class Event:
    kind: str          # tier, tier_fragment, plot_entry, plot_file, label, title, removed_key, theme, tier1_added, refused, note
    file: Path
    where: str
    detail: str

    def line(self, shown: Callable[[Path], str]) -> str:
        return f"{shown(self.file)}: {self.where}: {self.detail}" if self.where else f"{shown(self.file)}: {self.detail}"


@dataclass
class Result:
    events: List[Event] = field(default_factory=list)
    texts: Dict[Path, str] = field(default_factory=dict)      # files to write: path -> new text (changed or created)
    created: List[Path] = field(default_factory=list)
    removed: List[Path] = field(default_factory=list)
    originals: Dict[Path, str] = field(default_factory=dict)
    masters: List[Path] = field(default_factory=list)

    @property
    def refused(self) -> List[Event]:
        return [e for e in self.events if e.kind == "refused"]

    @property
    def changed(self) -> List[Path]:
        return [p for p in self.texts if p not in self.created]

    @property
    def would_change(self) -> bool:
        return bool(self.texts or self.removed)


class _Refuse(Exception):
    """A piece the tool cannot place by text; the message is for the person."""


# -- text helpers ------------------------------------------------------------------------------------------------------

def _pairs(node) -> list:
    return list(node.value) if isinstance(node, yaml.MappingNode) else []


def _find(node, key: str):
    for k, v in _pairs(node):
        if isinstance(k, yaml.ScalarNode) and k.value == key:
            return k, v
    return None


def _block(node) -> bool:
    return isinstance(node, yaml.MappingNode) and not node.flow_style


def _ls(text: str, i: int) -> int:
    return text.rfind("\n", 0, i) + 1


def _after_line(text: str, i: int) -> int:
    j = text.find("\n", i)
    return len(text) if j == -1 else j + 1


def _end_line(text: str, node) -> int:
    e = _content_end(node)
    if e > 0 and text[e - 1] == "\n":
        return e
    return _after_line(text, e)


def _pair_end(text: str, key, value) -> int:
    return max(_end_line(text, value), _after_line(text, key.end_mark.index))


def _after_colon(text: str, key) -> int:
    return text.index(":", key.end_mark.index) + 1


def _is_include(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag == "!include"


def _is_null(node) -> bool:
    return isinstance(node, yaml.ScalarNode) and node.tag != "!include" and node.value in ("", "~", "null", "Null", "NULL")


def _src(text: str, node) -> str:
    return text[node.start_mark.index:node.end_mark.index]


def _one_line(text: str, node) -> str:
    """The value as it can stand after `key: ` on one line (the written text when it is one line, else JSON)."""
    s = _src(text, node)
    if isinstance(node, yaml.ScalarNode) and "\n" not in s and (node.style is None or node.style in ("'", '"')):
        return s
    value = yaml.safe_load(s) if isinstance(node, yaml.ScalarNode) else s
    return json.dumps(value if isinstance(value, str) else s, ensure_ascii=False)


def _shift(block: str, delta: int) -> str:
    if delta == 0:
        return block
    out = []
    for line in block.split("\n"):
        if not line.strip():
            out.append(line)
        elif delta > 0:
            out.append(" " * delta + line)
        else:
            out.append(line[min(-delta, len(line) - len(line.lstrip(" "))):])
    return "\n".join(out)


def _flow_value(text: str, node) -> str:
    """A scalar written so that it can stand inside `{...}`."""
    s = _src(text, node)
    if isinstance(node, yaml.ScalarNode) and node.style in ("'", '"'):
        return s
    return json.dumps(node.value if isinstance(node, yaml.ScalarNode) else s, ensure_ascii=False)


def _compose(text: str):
    return yaml.compose(text, Loader=yaml.SafeLoader)


def _valid(text: str) -> None:
    try:
        yaml.compose(text, Loader=yaml.SafeLoader)
    except yaml.YAMLError as exc:
        raise _Refuse(f"the rewritten text is not valid YAML ({str(exc).splitlines()[0][:80]}): this is a fault of the tool, nothing was changed here") from exc


def _apply(text: str, edits: List[Tuple[int, int, str]]) -> str:
    # at the same position a replacement goes first, then an insertion, so that an inserted line lands above what follows
    for start, end, new in sorted(edits, key=lambda e: (-e[0], -e[1])):
        text = text[:start] + new + text[end:]
    return text


def _blocks(text: str, mapping, first_start: int, last_end: Optional[int] = None) -> list:
    """The pairs of a block mapping as contiguous pieces of text: [key text, key node, value node, start, end]. The comment and
    blank lines before a pair belong to it; `last_end` lets the last piece take what follows (the end of a file)."""
    out, start = [], first_start
    for k, v in mapping.value:
        end = _pair_end(text, k, v)
        out.append([k.value, k, v, start, end])
        start = end
    if out and last_end is not None:
        out[-1][4] = last_end
    return out


def _sibling(include: str, name: str) -> str:
    """The include string of a file that sits beside `include` (the same folder, as the recipe writes it)."""
    return str(PurePosixPath(include).with_name(name))


def _nl(text: str) -> str:
    return text if text.endswith("\n") or not text else text + "\n"


# -- classification ----------------------------------------------------------------------------------------------------

def classify(text: str) -> str:
    """What a file is, from its root keys: recipe, tier_fragment, plot_content, input_fields or unknown (never a guess)."""
    try:
        root = _compose(text)
    except yaml.YAMLError:
        return "unknown"
    if not isinstance(root, yaml.MappingNode) or not root.value:
        return "unknown"
    keys = [k.value for k, _ in root.value if isinstance(k, yaml.ScalarNode)]
    if "id" in keys and {"data_schemas", "analysis_groups", "joins"} & set(keys):
        return "recipe"
    if set(keys) <= {"tier1", "tier2", "tier3"}:
        return "tier_fragment"
    if {"target_dataset", "mapping", "layers"} & set(keys):
        return "plot_content"
    if all(isinstance(v, yaml.MappingNode) and _find(v, "type") for _, v in root.value):
        return "input_fields"
    return "unknown"


# -- the unit ----------------------------------------------------------------------------------------------------------

class _Unit:
    def __init__(self, partial_theme: Callable[[str], bool], label_keys: Optional[Dict[str, str]] = None,
                 removed_keys: Optional[List[str]] = None, theme_name: str = "theme_bw") -> None:
        self.partial_theme = partial_theme
        spec = recipe_spec()
        self.label_keys = label_keys if label_keys is not None else dict(spec["label_keys"])
        self.removed_keys = removed_keys if removed_keys is not None else list(spec["removed"]["plot_defaults"])
        self.theme_name = theme_name
        self.result = Result()
        self.texts: Dict[Path, str] = {}
        self.disk: Dict[Path, str] = {}
        self.fragments: Dict[Path, Dict[str, str]] = {}    # old fragment -> {tier: new file name}
        self.plot_files: Dict[Path, Tuple[Path, str]] = {}  # plot file -> (the recipe, the entry) whose content it was

    # reading and writing through the overlay
    def read(self, path: Path) -> str:
        path = Path(os.path.realpath(path))
        if path in self.texts:
            return self.texts[path]
        text = path.read_text(encoding="utf-8")
        self.disk[path] = self.texts[path] = text
        return text

    def put(self, path: Path, text: str) -> None:
        path = Path(os.path.realpath(path))
        if path not in self.disk:
            self.disk[path] = path.read_text(encoding="utf-8") if path.exists() else None   # type: ignore[assignment]
        self.texts[path] = text

    def event(self, kind: str, file: Path, where: str, detail: str) -> None:
        self.result.events.append(Event(kind, Path(file), where, detail))

    # -- containers: wrangling / steps / tier3 -> tier keys ------------------------------------------------------------
    def tier_fragment(self, base: Path, include: str, file: Path, where: str, allowed: Tuple[str, ...]) -> Dict[str, str]:
        """The new file of each tier of an old fragment: {tier: file name}; writes the new files into the overlay (once)."""
        target = Path(os.path.realpath(base / include))
        if target in self.fragments:
            return self.fragments[target]
        if not target.is_file():
            raise _Refuse(f"the include {include} was not found; a person must check it")
        text = self.read(target)
        root = _compose(text)
        if not _block(root):
            raise _Refuse(f"the include {include} is not a block mapping of tiers; a person must rewrite it")
        keys = [k.value for k, _ in root.value]
        if not keys or not set(keys) <= {"tier1", "tier2", "tier3"} or len(set(keys)) != len(keys):
            raise _Refuse(f"the include {include} holds the keys {keys} and not only tiers; a person must rewrite it")
        for tier in keys:
            if tier not in allowed:
                raise _Refuse(f"the fragment {include} holds {tier}, which is not a tier of this place; a person must rewrite it")
        pieces = _blocks(text, root, 0, len(text))
        out: Dict[str, str] = {}
        new_files: Dict[Path, str] = {}
        for key, kn, vn, start, end in pieces:
            piece = text[start:end]
            kpos = kn.start_mark.index - start
            colon = _after_colon(text, kn) - start
            if _is_null(vn):
                piece = piece[:kpos] + "steps" + piece[kpos + len(key):colon] + " []" + piece[colon:]
            else:
                piece = piece[:kpos] + "steps" + piece[kpos + len(key):]
            new_name = target.name if len(pieces) == 1 else f"{target.stem}_{key}{target.suffix}"
            if len(pieces) > 1 and (target.parent / new_name).exists():
                raise _Refuse(f"the file {new_name} already exists beside {target.name}; a person must choose another name")
            _valid(_nl(piece))
            out[key] = new_name
            new_files[target.parent / new_name] = _nl(piece)
        for path, new_text in new_files.items():
            self.put(path, new_text)
            if path != target:
                self.result.created.append(Path(os.path.realpath(path)))
        if len(pieces) > 1:
            self.result.removed.append(target)
            self.event("tier_fragment", file, where, f"{include} holds {len(pieces)} tiers: split into "
                       + ", ".join(_sibling(include, n) for n in out.values()) + f"; {include} removed (provisional naming)")
        else:
            self.event("tier_fragment", file, where, f"{include}: the root key {keys[0]} is now steps (the file name stays)")
        self.fragments[target] = out
        return out

    def convert_container(self, file: Path, base: Path, parent, key: str, role: str, where: str, shown: Optional[Path] = None) -> None:
        """Turn the old container pair `key` of the mapping `parent` (in the text of `file`) into the tier keys.
        `shown` is the file named in the events (the text may be a scratch copy of an entry)."""
        path = Path(os.path.realpath(file))
        shown = shown or path
        text = self.texts[path]
        pair = _find(parent, key)
        kn, vn = pair
        kcol = kn.start_mark.column
        kls = _ls(text, kn.start_mark.index)
        after_colon = _after_colon(text, kn)
        key_line_rest = text[after_colon:_after_line(text, after_colon)].rstrip("\n")
        comment = key_line_rest.strip() if key_line_rest.strip().startswith("#") else ""
        pad = " " * kcol
        allowed = _TIER_KEYS[role]
        required = "tier1" if role in ("schema", "join") else None
        edits: List[Tuple[int, int, str]] = []
        have: Set[str] = set()
        head = f"{pad}{comment}\n" if comment else ""
        if _is_include(vn):
            include = vn.value
            written = _src(text, vn)[len("!include"):].strip()   # keeps the quotes the author wrote
            tiers = self.tier_fragment(base, include, shown, where, allowed)
            lines = ""
            if required and required not in tiers:
                lines += f"{pad}{required}: {{steps: []}}\n"
                self.event("tier1_added", shown, where, "tier1: {steps: []} added (the fragment holds no tier1 and a tier1 is required)")
            for tier in sorted(tiers):
                lines += f"{pad}{tier}: !include {written.replace(include, _sibling(include, tiers[tier]), 1)}\n"
            edits.append((kls, _pair_end(text, kn, vn), head + lines))
            have = set(tiers)
            detail = f"{key}: !include {include} -> " + ", ".join(f"{t}: !include {_sibling(include, tiers[t])}" for t in sorted(tiers))
        elif _block(vn) and vn.value:
            u = vn.value[0][0].start_mark.column - kcol
            if u <= 0:
                u = 2
            for tk, tv in vn.value:
                tier = tk.value
                if tier not in allowed:
                    raise _Refuse(f"{key} holds the key {tier}, which is not a tier of this place; a person must rewrite it")
                if _is_include(tv) or _block(tv) or (isinstance(tv, yaml.MappingNode)):
                    raise _Refuse(f"{key}.{tier} is not a list of steps (an include or a mapping inside the old container); a person must rewrite it")
                have.add(tier)
                tls = _ls(text, tk.start_mark.index)
                colon = _after_colon(text, tk)
                tail = text[colon:_after_line(text, colon)].rstrip("\n")
                if _is_null(tv):
                    keep = " " + tail.strip() if tail.strip().startswith("#") else ""
                    new = f"{pad}{tier}:\n{pad}{' ' * u}steps: []{keep}\n"
                else:
                    new = f"{pad}{tier}:\n{pad}{' ' * u}steps:{tail}\n"
                edits.append((tls, _after_line(text, colon), new))
            edits.append((kls, _after_line(text, kn.end_mark.index), head))
            if required and required not in have:
                first = _ls(text, vn.value[0][0].start_mark.index)
                edits.append((first, first, f"{pad}{required}: {{steps: []}}\n"))
                self.event("tier1_added", shown, where, "tier1: {steps: []} added (there was no tier1 and a tier1 is required)")
            detail = f"{key}: {{{', '.join(sorted(have))}}} -> " + ", ".join(f"{t}: {{steps}}" for t in sorted(have))
        elif isinstance(vn, yaml.MappingNode) and vn.flow_style and vn.value:
            lines = ""
            for tk, tv in vn.value:
                tier = tk.value
                if tier not in allowed:
                    raise _Refuse(f"{key} holds the key {tier}, which is not a tier of this place; a person must rewrite it")
                if isinstance(tv, yaml.MappingNode) or _is_include(tv):
                    raise _Refuse(f"{key}.{tier} is not a list of steps; a person must rewrite it")
                have.add(tier)
                value = "[]" if _is_null(tv) else _src(text, tv)
                lines += f"{pad}{tier}: {{steps: {value}}}\n"
            if required and required not in have:
                lines = f"{pad}{required}: {{steps: []}}\n" + lines
                self.event("tier1_added", shown, where, "tier1: {steps: []} added (there was no tier1 and a tier1 is required)")
            edits.append((kls, _pair_end(text, kn, vn), head + lines))
            detail = f"{key}: {{{', '.join(sorted(have))}}} -> " + ", ".join(f"{t}: {{steps}}" for t in sorted(have))
        elif _is_null(vn) or (isinstance(vn, yaml.SequenceNode) and not vn.value) or (isinstance(vn, yaml.MappingNode) and not vn.value):
            if required:
                edits.append((kls, _pair_end(text, kn, vn), head + f"{pad}{required}: {{steps: []}}\n"))
                detail = f"{key}: (empty) -> {required}: {{steps: []}}"
            else:
                edits.append((kls, _pair_end(text, kn, vn), head))
                detail = f"{key}: (empty) removed (an entry with no tier3 steps has no tier3)"
        else:
            raise _Refuse(f"{key} is not a mapping of tiers (a list of steps was found); a person must rewrite it")
        self.texts[path] = new = _apply(text, edits)
        _valid(new)
        self.event("tier", shown, where, detail)

    def convert_tiers(self, path: Path, parent, role: str, where: str) -> None:
        """One table or join: its container (`wrangling` or `steps`) and the rule that a table and a join have a tier1."""
        path = Path(os.path.realpath(path))
        container = "wrangling" if role == "schema" else "steps"
        try:
            if _find(parent, container) is not None:
                self.convert_container(path, path.parent, parent, container, role, where)
            elif _find(parent, "tier1") is None and _block(parent):
                text = self.texts[path]
                last = parent.value[-1]
                end = _pair_end(text, *last)
                pad = " " * last[0].start_mark.column
                self.texts[path] = new = text[:end] + _nl("") + f"{pad}tier1: {{steps: []}}\n" + text[end:]
                _valid(new)
                self.event("tier1_added", path, where, "tier1: {steps: []} added (the element had no tier and a tier1 is required)")
        except _Refuse as exc:
            self.event("refused", path, where, str(exc))

    # -- the plot entry -------------------------------------------------------------------------------------------------
    def assemble_entry(self, text0: str, base: Path, where: str, path: Path) -> Tuple[str, Optional[str]]:
        """The entry (text at column 0) in the new shape; returns (text, the include path when the content came from a file)."""
        root = _compose(text0)
        if not _block(root):
            raise _Refuse("the plot entry is written on one line; a person must rewrite it")
        blocks = _blocks(text0, root, 0)
        by_key = {b[0]: b for b in blocks}
        has_spec, has_steps = "spec" in by_key, "steps" in by_key
        included: Optional[str] = None
        if not (has_spec or has_steps):
            out = ""
            for key, kn, vn, start, end in blocks:
                piece = text0[start:end]
                if key == "label" and "ui_label" not in by_key:
                    k0 = kn.start_mark.index - start
                    piece = piece[:k0] + "ui_label" + piece[k0 + len("label"):]
                out += _nl(piece)
            return out, None
        content: List[str] = []
        lead = ""
        if has_spec:
            _, skn, svn, sstart, send = by_key["spec"]
            lead = text0[sstart:_ls(text0, skn.start_mark.index)]
            colon = _after_colon(text0, skn)
            rest = text0[colon:_after_line(text0, colon)].rstrip("\n").strip()
            if rest.startswith("#"):
                lead += rest + "\n"
            if _is_include(svn):
                included = svn.value
                target = Path(os.path.realpath(base / included))
                if not target.is_file():
                    raise _Refuse(f"the include {included} was not found; a person must check it")
                if target in self.plot_files and self.plot_files[target] != (path, where):
                    raise _Refuse(f"the file {included} is also the content of another plot entry; a person must decide")
                ftext = self.read(target)
                froot = _compose(ftext)
                if _block(froot) and len(froot.value) == 1 and froot.value[0][0].value == "spec" and _block(froot.value[0][1]):
                    inner_start = _after_line(ftext, froot.value[0][0].end_mark.index)
                    ftext = _shift(ftext[inner_start:], -froot.value[0][1].value[0][0].start_mark.column)
                    froot = _compose(ftext)
                if froot is None:
                    content = []
                elif not _block(froot):
                    raise _Refuse(f"the file {included} is not a mapping; a person must rewrite it")
                else:
                    content = [_nl(ftext[s:e]) for _, _, _, s, e in _blocks(ftext, froot, 0, len(ftext))]
            elif _block(svn):
                inner_start = _after_line(text0, skn.end_mark.index)
                col = svn.value[0][0].start_mark.column
                inner = _shift(text0[inner_start:send], -col)
                iroot = _compose(inner)
                content = [_nl(inner[s:e]) for _, _, _, s, e in _blocks(inner, iroot, 0)]
            elif _is_null(svn) or (isinstance(svn, yaml.MappingNode) and not svn.value):
                content = []
            else:
                raise _Refuse("the spec is written on one line; a person must rewrite it")
            if any(re.search(r"^[^#\n]*!include", piece, re.M) for piece in content):
                raise _Refuse("the plot content holds an include; a person must move it")
        out = _nl(lead) if lead.strip() else ""
        order = []
        label_key = "ui_label" if "ui_label" in by_key else "label"
        for name in _ENTRY_ORDER:
            if name in ("label", "ui_label"):
                if name == label_key and name in by_key:
                    order.append(name)
            elif name in by_key:
                order.append(name)
        for key, kn, vn, start, end in blocks:
            piece = text0[start:end]
            if key in order or key in ("spec", "steps"):
                continue
            order.append(key)          # a key of the entry that is not known: kept after taxonomy, the checker will name it
        for key in order:
            _, kn, vn, start, end = by_key[key]
            piece = text0[start:end]
            if key == "label" and "ui_label" not in by_key:
                k0 = kn.start_mark.index - start
                piece = piece[:k0] + "ui_label" + piece[k0 + len("label"):]
            out += _nl(piece)
        out += "".join(content)
        if has_steps:
            _, _, _, start, end = by_key["steps"]
            out += _nl(text0[start:end])
        _valid(out)
        if included is not None:
            self.plot_files[Path(os.path.realpath(base / included))] = (path, where)
        return out, included

    def move_title(self, text0: str, where: str, path: Path, defaults_labs: bool) -> str:
        """The old `title:` of the content: into the labs layer, and as ui_title; returns the new text."""
        root = _compose(text0)
        tp = _find(root, "title")
        if tp is None:
            return text0
        tkey, tval = tp
        if not isinstance(tval, yaml.ScalarNode):
            raise _Refuse("the title is not a text; a person must move it")
        value = tval.value
        shown = _one_line(text0, tval)
        lp = _find(root, "layers")
        if lp is None or not isinstance(lp[1], yaml.SequenceNode) or lp[1].flow_style:
            raise _Refuse("the plot has no layers list written as a list: the title cannot be placed in a labs layer; a person must move it")
        items = lp[1].value
        labs = [i for i in items if isinstance(i, yaml.MappingNode) and (_find(i, "name") and getattr(_find(i, "name")[1], "value", None) == "labs")]
        note = ""
        text = text0
        if not labs:
            if defaults_labs:
                raise _Refuse("plot_defaults holds a labs layer and this plot has none: a labs layer here would replace it; a person must decide")
            last = items[-1] if items else None
            if last is None:
                raise _Refuse("the layers list is empty; a person must move the title")
            dash_line = _ls(text, last.start_mark.index)
            dash = text.rfind("-", dash_line, last.start_mark.index)
            if dash < 0:
                raise _Refuse("the layers are written in a form the tool cannot extend; a person must move the title")
            dcol = dash - dash_line
            end = _end_line(text, last)
            inner = " " * (dcol + 2)
            text = text[:end] + f"{' ' * dcol}- name: labs\n{inner}params:\n{inner}  title: {shown}\n" + text[end:]
            note = "a labs layer was added at the end of the layers"
        else:
            item = labs[-1]
            params = _find(item, "params")
            if params is None:
                if not _block(item):
                    text = text[:item.end_mark.index - 1] + f", params: {{title: {_flow_value(text, tval)}}}" + text[item.end_mark.index - 1:]
                else:
                    first = item.value[0][0]
                    endi = _pair_end(text, *item.value[-1])
                    pad = " " * first.start_mark.column
                    text = text[:endi] + f"{pad}params:\n{pad}  title: {shown}\n" + text[endi:]
                note = "title added to the labs layer (it had no params)"
            else:
                pv = params[1]
                if _block(pv) and pv.value:
                    old = _find(pv, "title")
                    pcol = pv.value[0][0].start_mark.column
                    if old is not None:
                        a, b = _ls(text, old[0].start_mark.index), _pair_end(text, *old)
                        was = _src(text, old[1])
                        text = text[:a] + f"{' ' * pcol}title: {shown}\n" + text[b:]
                        note = f"the title of the labs layer ({was}) was replaced: the root title is the one drawn today"
                    else:
                        a = _ls(text, pv.value[0][0].start_mark.index)
                        text = text[:a] + f"{' ' * pcol}title: {shown}\n" + text[a:]
                        note = "title added to the labs layer"
                elif isinstance(pv, yaml.MappingNode) and pv.flow_style:
                    old = _find(pv, "title")
                    if old is not None:
                        was = _src(text, old[1])
                        text = text[:old[1].start_mark.index] + _flow_value(text, tval) + text[old[1].end_mark.index:]
                        note = f"the title of the labs layer ({was}) was replaced: the root title is the one drawn today"
                    elif pv.value:
                        text = text[:pv.start_mark.index + 1] + f"title: {_flow_value(text, tval)}, " + text[pv.start_mark.index + 1:]
                        note = "title added to the labs layer"
                    else:
                        text = text[:pv.start_mark.index] + f"{{title: {_flow_value(text, tval)}}}" + text[pv.end_mark.index:]
                        note = "title added to the labs layer"
                elif _is_null(pv) or (isinstance(pv, yaml.MappingNode) and not pv.value):
                    text = text[:pv.start_mark.index] + f" {{title: {_flow_value(text, tval)}}}" + text[pv.end_mark.index:] if _is_null(pv) \
                        else text[:pv.start_mark.index] + f"{{title: {_flow_value(text, tval)}}}" + text[pv.end_mark.index:]
                    note = "title added to the labs layer"
                else:
                    raise _Refuse("the params of the labs layer are written in a form the tool cannot extend; a person must move the title")
        _valid(text)
        root = _compose(text)
        tkey, tval = _find(root, "title")
        a, b = _ls(text, tkey.start_mark.index), _pair_end(text, tkey, tval)
        text = text[:a] + text[b:]
        _valid(text)
        root = _compose(text)
        if _find(root, "ui_title") is None:
            lab = _find(root, "ui_label")
            if lab is not None:
                at = _pair_end(text, *lab)
                pad = " " * lab[0].start_mark.column
            else:
                at, pad = 0, ""
            text = text[:at] + f"{pad}ui_title: {shown}\n" + text[at:]
            _valid(text)
            self.event("title", path, where, f"title {shown} moved: {note}; ui_title written")
        else:
            self.event("title", path, where, f"title {shown} moved: {note}; ui_title was already there and is kept")
        return text

    def convert_entry_steps(self, text0: str, where: str, path: Path, base: Path) -> str:
        root = _compose(text0)
        if _find(root, "steps") is None:
            return text0
        # the entry is worked on as a scratch text in the overlay, so that convert_container can read and write it
        key = Path(os.path.realpath(path)).with_suffix(".entry-scratch")
        self.texts[key] = text0
        try:
            self.convert_container(key, base, root, "steps", "plot", where, shown=path)
            return self.texts[key]
        finally:
            self.texts.pop(key, None)

    def entry(self, path: Path, group_key: str, plot_key: str, defaults_labs: bool) -> None:
        path = Path(os.path.realpath(path))
        where = f"analysis_groups.{group_key}.plots.{plot_key}"
        text = self.texts[path]
        root = _compose(text)
        groups = _find(root, "analysis_groups")
        plots = _find(_find(groups[1], group_key)[1], "plots")
        ekn, evn = _find(plots[1], plot_key)
        if _is_include(evn):
            return                                                   # already a whole entry in its own file (new shape)
        if not _block(evn):
            self.event("refused", path, where, "the plot entry is written on one line; a person must rewrite it")
            return
        eks = _ls(text, ekn.start_mark.index)
        body_start = _after_line(text, ekn.end_mark.index)
        last = evn.value[-1]
        body_end = _pair_end(text, *last)
        col = evn.start_mark.column
        text0 = _shift(text[body_start:body_end], -col)
        had_spec = any(k.value == "spec" for k, _ in evn.value)
        try:
            new0, included = self.assemble_entry(text0, path.parent, where, path)
            new0 = self.convert_entry_steps(new0, where, path, path.parent)
            first = len(self.result.events)
            new0 = self.move_title(new0, where, path, defaults_labs)
            title_events = self.result.events[first:]
            del self.result.events[first:]
        except _Refuse as exc:
            self.event("refused", path, where, str(exc))
            return
        if new0 == text0:
            return
        if included is not None:
            target = Path(os.path.realpath(path.parent / included))
            self.put(target, new0)
            key_text = _src(text, ekn)
            new = text[:eks] + f"{' ' * ekn.start_mark.column}{key_text}: !include {included}\n" + text[body_end:]
            self.texts[path] = new
            _valid(new)
            self.event("plot_file", path, where, f"spec: !include {included} -> {key_text}: !include {included}; the whole entry is now in {included}")
            self.result.events.extend(title_events)
        else:
            new = text[:body_start] + _shift(new0, col) + text[body_end:]
            self.texts[path] = new
            _valid(new)
            self.event("plot_entry", path, where, ("spec removed, the content is written in the entry" if had_spec else "names and keys written"))
            self.result.events.extend(title_events)

    # -- names -----------------------------------------------------------------------------------------------------------
    def rename_key(self, path: Path, keys: List[str], old: str, new: str, where: str) -> None:
        """Rename the key `old` of the mapping found by following `keys` from the root of the text of `path`."""
        path = Path(os.path.realpath(path))
        text = self.texts[path]
        node = _compose(text)
        for part in keys:
            pair = _find(node, part)
            if pair is None:
                return
            node = pair[1]
        pair = _find(node, old)
        if pair is None or _find(node, new) is not None or not isinstance(node, yaml.MappingNode):
            return
        a = pair[0].start_mark.index
        self.texts[path] = text[:a] + new + text[a + len(old):]
        self.event("label", path, where, f"{old} -> {new}")

    def names(self, path: Path) -> None:
        """label -> ui_label at groups (always, D-0253) and, where `label_keys` says so, at the pending places."""
        path = Path(os.path.realpath(path))
        root = _compose(self.texts[path])
        groups = _find(root, "analysis_groups")
        for gk in [k.value for k, _ in _pairs(groups[1])] if groups else []:
            self.rename_key(path, ["analysis_groups", gk], "label", "ui_label", f"analysis_groups.{gk}")
        if self.label_keys.get("info") == "ui_label":
            self.rename_key(path, ["info"], "label", "ui_label", "info")
        schemas = [section_key for section_key in self._schemas(root)]
        joins = self._joins(root)
        if self.label_keys.get("schema") == "ui_label":
            for name in schemas:
                self.rename_key(path, name.split("."), "label", "ui_label", name)
        if self.label_keys.get("join") == "ui_label":
            for name in joins:
                self.rename_key(path, name.split("."), "label", "ui_label", name)
        if self.label_keys.get("field") == "ui_label":
            for name in schemas:
                node = self._element(_compose(self.texts[path]), name)
                fields = _find(node, "input_fields") if node is not None else None
                if fields is None:
                    continue
                if _is_include(fields[1]):
                    target = Path(os.path.realpath(path.parent / fields[1].value))
                    if target.is_file():
                        for slug in [k.value for k, _ in _pairs(_compose(self.read(target)))]:
                            self.rename_key(target, [slug], "label", "ui_label", f"{fields[1].value}.{slug}")
                elif isinstance(fields[1], yaml.MappingNode):
                    for slug in [k.value for k, _ in _pairs(fields[1])]:
                        self.rename_key(path, name.split(".") + ["input_fields", slug], "label", "ui_label", f"{name}.input_fields.{slug}")

    @staticmethod
    def _schemas(root) -> List[str]:
        names = []
        for section in _SCHEMA_SECTIONS:
            pair = _find(root, section)
            names += [f"{section}.{k.value}" for k, _ in _pairs(pair[1])] if pair else []
        if _find(root, "metadata_schema"):
            names.append("metadata_schema")
        return names

    @staticmethod
    def _joins(root) -> List[str]:
        pair = _find(root, "joins")
        return [f"joins.{k.value}" for k, _ in _pairs(pair[1])] if pair else []

    @staticmethod
    def _element(root, name: str):
        node = root
        for part in name.split("."):
            pair = _find(node, part)
            if pair is None:
                return None
            node = pair[1]
        return node if isinstance(node, yaml.MappingNode) else None

    # -- plot_defaults: the dead keys and the theme --------------------------------------------------------------------
    def load(self, path: Path):
        path = Path(os.path.realpath(path))

        class Loader(yaml.SafeLoader):
            pass

        def include(loader, node):
            name = loader.construct_scalar(node)
            target = Path(os.path.realpath(path.parent / name))
            return self.load_file(target)

        Loader.add_constructor("!include", include)
        return yaml.load(self.texts[path], Loader=Loader)

    def load_file(self, target: Path):
        target = Path(os.path.realpath(target))
        text = self.read(target)

        class Loader(yaml.SafeLoader):
            pass

        def include(loader, node):
            return self.load_file(target.parent / loader.construct_scalar(node))

        Loader.add_constructor("!include", include)
        return yaml.load(text, Loader=Loader)

    def _complete_theme(self, content) -> bool:
        if not isinstance(content, dict):
            return False

        def complete(name) -> bool:
            return isinstance(name, str) and name.startswith("theme_") and not self.partial_theme(name)

        if complete(content.get("theme")):
            return True
        return any(isinstance(layer, dict) and complete(layer.get("name")) for layer in (content.get("layers") or []))

    def plot_defaults(self, path: Path) -> None:
        path = Path(os.path.realpath(path))
        recipe_id = path.stem
        try:
            data = self.load(path)
        except (OSError, yaml.YAMLError) as exc:
            self.event("refused", path, "plot_defaults", f"the recipe cannot be read with its includes ({exc}); the theme and the dead keys were not looked at")
            return
        plots = []
        for gid, group in (data.get("analysis_groups") or {}).items():
            for pid, entry in ((group or {}).get("plots") or {}).items():
                content = entry.get("spec") if isinstance(entry, dict) and isinstance(entry.get("spec"), dict) else entry
                plots.append((pid, content))
        defaults = data.get("plot_defaults") or {}
        lacking = [pid for pid, content in plots if not self._complete_theme(content)]
        need_theme = bool(lacking) and not self._complete_theme(defaults)
        text = self.texts[path]
        root = _compose(text)
        pd = _find(root, "plot_defaults")
        dead = [] if pd is None or not _block(pd[1]) else [(k, v) for k, v in pd[1].value if k.value in self.removed_keys]
        if pd is not None and not _block(pd[1]) and not _is_null(pd[1]):
            if any(k in defaults for k in self.removed_keys) or need_theme:
                self.event("refused", path, "plot_defaults", "plot_defaults is written on one line or as an include; a person must rewrite it")
            return
        if not dead and not need_theme:
            return
        edits: List[Tuple[int, int, str]] = []
        for k, v in dead:
            edits.append((_ls(text, k.start_mark.index), _pair_end(text, k, v), ""))
            self.event("removed_key", path, "plot_defaults", f"{k.value} removed (old value {_src(text, v) if not _is_null(v) else 'empty'}) in recipe {recipe_id}")
        if pd is None:
            ag = _find(root, "analysis_groups")
            at = _ls(text, ag[0].start_mark.index)
            while at > 0:                                            # before the comment lines that belong to analysis_groups
                prev = _ls(text, at - 1)
                if text[prev:at].lstrip().startswith("#"):
                    at = prev
                else:
                    break
            edits.append((at, at, f"plot_defaults:\n  theme: {self.theme_name}\n\n"))
        else:
            remaining = [(k, v) for k, v in (pd[1].value if _block(pd[1]) else []) if k.value not in self.removed_keys]
            if not remaining and not need_theme:
                a, b = _ls(text, pd[0].start_mark.index), _pair_end(text, *pd)
                edits = [(a, b, "")]                                   # the whole block went; a blank line after it goes too
                if text[b:b + 1] == "\n":
                    edits = [(a, b + 1, "")]
            elif need_theme:
                if remaining:
                    col = remaining[0][0].start_mark.column
                    at = _ls(text, remaining[0][0].start_mark.index)
                    edits.append((at, at, f"{' ' * col}theme: {self.theme_name}\n"))
                elif _block(pd[1]) and pd[1].value:
                    k0 = pd[1].value[0][0]
                    at = _ls(text, k0.start_mark.index)
                    edits.append((at, at, f"{' ' * k0.start_mark.column}theme: {self.theme_name}\n"))
                else:
                    at = _after_line(text, pd[0].end_mark.index)
                    edits.append((at, at, f"  theme: {self.theme_name}\n"))
        if need_theme:
            self.event("theme", path, "plot_defaults", f"theme: {self.theme_name} written in recipe {recipe_id} (plots drawn with the built-in theme_bw until now: {', '.join(lacking)})")
        self.texts[path] = new = _apply(text, edits)
        _valid(new)

    # -- one recipe ------------------------------------------------------------------------------------------------------
    def master(self, path: Path) -> None:
        path = Path(os.path.realpath(path))
        try:
            _compose(self.read(path))
        except yaml.YAMLError as exc:
            self.event("refused", path, "", f"the file cannot be parsed ({str(exc).splitlines()[0][:80]}); a person must check it")
            return
        self.names(path)
        for section in _SCHEMA_SECTIONS:
            pair = _find(_compose(self.texts[path]), section)
            for key in [k.value for k, _ in _pairs(pair[1])] if pair else []:
                node = _find(_find(_compose(self.texts[path]), section)[1], key)[1]
                if _block(node):
                    self.convert_tiers(path, node, "schema", f"{section}.{key}")
        meta = _find(_compose(self.texts[path]), "metadata_schema")
        if meta is not None and _block(meta[1]):
            self.convert_tiers(path, meta[1], "schema", "metadata_schema")
        joins = _find(_compose(self.texts[path]), "joins")
        for key in [k.value for k, _ in _pairs(joins[1])] if joins else []:
            node = _find(_find(_compose(self.texts[path]), "joins")[1], key)[1]
            if _block(node):
                self.convert_tiers(path, node, "join", f"joins.{key}")
        groups = _find(_compose(self.texts[path]), "analysis_groups")
        defaults = _find(_compose(self.texts[path]), "plot_defaults")
        defaults_labs = False
        if defaults is not None and _block(defaults[1]):
            layers = _find(defaults[1], "layers")
            defaults_labs = bool(layers) and isinstance(layers[1], yaml.SequenceNode) and any(
                isinstance(i, yaml.MappingNode) and _find(i, "name") and getattr(_find(i, "name")[1], "value", None) == "labs" for i in layers[1].value)
        for gk, gv in _pairs(groups[1]) if groups else []:
            plots = _find(gv, "plots") if isinstance(gv, yaml.MappingNode) else None
            for pk in [k.value for k, _ in _pairs(plots[1])] if plots else []:
                self.entry(path, gk.value, pk, defaults_labs)
        self.plot_defaults(path)


def _walk_includes(path: Path, seen: Set[Path]) -> None:
    path = Path(os.path.realpath(path))
    try:
        root = _compose(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return

    def walk(node):
        if _is_include(node):
            target = Path(os.path.realpath(path.parent / node.value))
            if target not in seen and target.is_file():
                seen.add(target)
                _walk_includes(target, seen)
        elif isinstance(node, yaml.MappingNode):
            for _, v in node.value:
                walk(v)
        elif isinstance(node, yaml.SequenceNode):
            for v in node.value:
                walk(v)

    walk(root)


def migrate(paths: List[Path], partial_theme: Callable[[str], bool] = lambda name: False, *,
            label_keys: Optional[Dict[str, str]] = None, theme_name: str = "theme_bw", orphan_fragments: bool = False) -> Result:
    """Plan the rewrite of the recipes under `paths` (files or folders); nothing is written. The caller writes `Result.texts`.

    `partial_theme(name)` says whether a `theme_*` component only sets some properties of the theme (the plot library knows;
    this library does not import it). An old tier fragment that no recipe in `paths` includes is listed and not rewritten, because
    a recipe outside `paths` may include it; with `orphan_fragments` it is rewritten on its own (give every recipe that may
    include it)."""
    unit = _Unit(partial_theme, label_keys=label_keys, theme_name=theme_name)
    files: List[Path] = []
    explicit: Set[Path] = set()
    for item in map(Path, paths):
        if item.is_dir():
            files += sorted(p for p in item.rglob("*.yaml"))
        else:
            files.append(item)
            explicit.add(Path(os.path.realpath(item)))
    masters, others = [], []
    for f in files:
        real = Path(os.path.realpath(f))
        try:
            kind = classify(real.read_text(encoding="utf-8"))
        except OSError as exc:
            unit.event("refused", f, "", f"the file cannot be read ({exc.strerror})")
            continue
        (masters if kind == "recipe" else others).append((real, kind))
    reached: Set[Path] = set()
    for real, _ in masters:
        _walk_includes(real, reached)
    names = {"tier_fragment": "an old tier fragment", "plot_content": "the content of a plot", "unknown": "a file of a kind that cannot be known"}
    for real, kind in others:
        if real in reached or kind == "input_fields":
            continue
        if real in explicit:
            unit.event("refused", real, "", (f"this is {names[kind]}: it is rewritten together with the recipe that includes it, give that recipe (or its folder); nothing changed"
                                              if kind != "unknown" else "the kind of this file cannot be known from its keys; nothing changed"))
        elif kind == "tier_fragment" and orphan_fragments:
            try:
                unit.tier_fragment(real.parent, real.name, real, "", ("tier1", "tier2", "tier3"))
                unit.event("note", real, "", "no recipe in the given paths includes this tier fragment: rewritten on its own (--orphan-fragments)")
            except _Refuse as exc:
                unit.event("refused", real, "", str(exc))
        else:
            unit.event("refused", real, "", f"this is {names[kind]} and no recipe in the given paths includes it: not rewritten")
    for real, _ in masters:
        unit.result.masters.append(real)
        unit.master(real)
    result = unit.result
    for path, text in unit.texts.items():
        if path in result.created:
            result.texts[path] = text
        elif text != unit.disk.get(path, text):
            result.texts[path] = text
    result.originals = {p: t for p, t in unit.disk.items()}
    return result


def format_events(result: Result, shown: Callable[[Path], str] = str) -> List[str]:
    return [e.line(shown) for e in result.events]


def summary(result: Result, shown_dir: Callable[[Path], str] = lambda p: str(p.parent)) -> List[Tuple[str, int]]:
    """Counts by kind of event, for the summary table."""
    counts: Dict[str, int] = {}
    for event in result.events:
        counts[event.kind] = counts.get(event.kind, 0) + 1
    counts["files changed"] = len(result.changed)
    counts["files created"] = len(result.created)
    counts["files removed"] = len(result.removed)
    return sorted(counts.items())
