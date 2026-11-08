#!/usr/bin/env python3
"""Audit: UML model vs code discrepancy check.

Reads docs/UML/app.mdj (StarUML, JSON) and checks every tag an element carries against the
repository, with no need for StarUML to be running. Plan: .claude/design/uml_model_plan.md
section 5.

Checks:
  - code      file[:symbol] exists; symbol is defined in the file (class, function or
              module-level name, found with ast)
  - test      same as code, for a test file; symbol may use :: (pytest style)
  - adr       the ADR exists in architecture_decisions.md and its heading is not marked
              HISTORICAL or REMOVED
  - flag      the flag name is a real key in the flags: block of a shipped app features file
              (or a top-level field, for a dotted name like data_analysis_recipe_selector.visible)
  - status    is one of implemented, partial, planned

Usage:
  .venv/bin/python assets/scripts/audit_uml_model.py
  .venv/bin/python assets/scripts/audit_uml_model.py --project-root /path/to/project --output report.md
"""
import argparse
import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

MODEL_FILE = "docs/UML/app.mdj"
ADR_FILE = ".claude/knowledge/architecture_decisions.md"
APP_FEATURES_DIR = "config/app_features"
VALID_STATUS = {"implemented", "partial", "planned"}
# code/test paths that are not Python files: existence is the only check
_NON_PY_OK = (".yaml", ".toml", ".md", ".qmd", "Dockerfile")


def find_project_root(start: Path) -> Path:
    cur = start
    for _ in range(6):
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return start.parents[3]


def walk_tagged_elements(node, out, seen=None):
    """Yield (element_name, element_type, {tag_name: value}) for every element with tags."""
    if seen is None:
        seen = set()
    if isinstance(node, dict):
        eid = node.get("_id")
        if node.get("_type") == "Tag" and False:
            pass
        tags = node.get("tags")
        if tags and isinstance(tags, list) and eid not in seen:
            tag_map = {t.get("name"): t.get("value") for t in tags if isinstance(t, dict) and t.get("name")}
            if tag_map:
                out.append((node.get("name") or "(unnamed)", node.get("_type") or "?", tag_map))
                if eid:
                    seen.add(eid)
        for v in node.values():
            walk_tagged_elements(v, out, seen)
    elif isinstance(node, list):
        for v in node:
            walk_tagged_elements(v, out, seen)


def _py_symbol_exists(path: Path, symbol: str) -> bool:
    """True if `symbol` is a module-level class, function, assigned name, or a string literal
    in the file (the last case covers a Shiny widget id, e.g. ui.input_select("my_id", ...))."""
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return False
    for n in ast.walk(tree):
        if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == symbol:
            return True
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == symbol:
                    return True
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == symbol:
            return True
        if isinstance(n, ast.Constant) and n.value == symbol:
            return True
    return False


def check_code_ref(project_root: Path, ref: str, allow_dirs: bool = False) -> str | None:
    """Return an error string, or None if the reference resolves."""
    sep = "::" if "::" in ref else (":" if ":" in ref and not ref.startswith("http") else None)
    if sep:
        path_part, symbol = ref.split(sep, 1)
    else:
        path_part, symbol = ref, None
    path = project_root / path_part
    if not path.exists():
        return f"path not found: {path_part}"
    if symbol is None:
        return None
    if path.is_dir():
        return None  # a folder reference names no symbol
    if not path.suffix == ".py":
        return None  # non-Python file: existence is enough
    if not _py_symbol_exists(path, symbol):
        return f"'{symbol}' not found in {path_part}"
    return None


def adr_errors(project_root: Path, adr_id: str) -> str | None:
    adr_path = project_root / ADR_FILE
    if not adr_path.exists():
        return f"{ADR_FILE} not found"
    text = adr_path.read_text(encoding="utf-8")
    m = re.search(rf"^##\s*{re.escape(adr_id)}\b.*$", text, re.MULTILINE)
    if not m:
        return f"{adr_id} has no '## {adr_id}' heading"
    # section text: from this heading to the next '## ' heading
    start = m.end()
    nxt = text.find("\n## ", start)
    section = text[start:nxt if nxt != -1 else len(text)]
    if re.search(r"\*\*(HISTORICAL|REMOVED|SUPERSEDED)", section):
        return f"{adr_id} is marked historical/removed/superseded"
    return None


def _load_app_features_flags(project_root: Path) -> tuple[set[str], set[str]]:
    """Return (flag_names, top_level_field_names) across every shipped app features file."""
    flags: set[str] = set()
    fields: set[str] = set()
    af_dir = project_root / APP_FEATURES_DIR
    if not _YAML_AVAILABLE or not af_dir.exists():
        return flags, fields

    class _Loader(yaml.SafeLoader):
        pass

    _Loader.add_constructor("!include", lambda loader, node: None)
    for f in af_dir.glob("*.yaml"):
        try:
            data = yaml.load(f.read_text(encoding="utf-8"), _Loader) or {}
        except yaml.YAMLError:
            continue
        flags |= set((data.get("flags") or {}).keys())
        fields |= set(data.keys())
        sel = data.get("data_analysis_recipe_selector")
        if isinstance(sel, dict):
            fields |= {f"data_analysis_recipe_selector.{k}" for k in sel}
    return flags, fields


def flag_error(name: str, flags: set[str], fields: set[str]) -> str | None:
    if name in flags or name in fields:
        return None
    return f"'{name}' is not a flag or field in any shipped app features file"


def _find_elements(node, type_name: str, out: list):
    if isinstance(node, dict):
        if node.get("_type") == type_name:
            out.append(node)
        for v in node.values():
            _find_elements(v, type_name, out)
    elif isinstance(node, list):
        for v in node:
            _find_elements(v, type_name, out)


def _pkg_scan_dir(project_root: Path, code_tag: str) -> Path | None:
    """The directory a PKG-TIERS package's `code` tag implies should be import-scanned."""
    path = Path(code_tag)
    if path.name == "pyproject.toml":
        return project_root / path.parent / "src"
    full = project_root / path
    if full.is_dir():
        return full
    # a file reference (e.g. app/src/main.py) stands for its top-level package directory
    return project_root / Path(path.parts[0])


def check_pkg_tiers(project_root: Path) -> tuple[list[dict], dict]:
    """Compare PKG-TIERS's dependency arrows against a live scan of real cross-package
    imports. Catches the two drift directions a hand-maintained diagram accumulates:
    an arrow for an import that was since removed, and a real import never drawn.
    `.claude/design/uml_model_plan.md` section 5 flagged this as not yet checked."""
    model_path = project_root / MODEL_FILE
    if not model_path.exists():
        return [], {"pkg_tiers_packages": 0, "pkg_tiers_model_edges": 0, "pkg_tiers_real_edges": 0}
    model = json.loads(model_path.read_text(encoding="utf-8"))

    packages = []
    _find_elements(model, "UMLPackage", packages)
    pkg_by_id = {p["_id"]: p.get("name") for p in packages}
    names = set(pkg_by_id.values())
    if not names:
        return [], {"pkg_tiers_packages": 0, "pkg_tiers_model_edges": 0, "pkg_tiers_real_edges": 0}

    code_by_name = {}
    for p in packages:
        for t in p.get("tags") or []:
            if t.get("name") == "code":
                code_by_name[p.get("name")] = t.get("value")

    deps = []
    _find_elements(model, "UMLDependency", deps)
    model_edges = set()
    for d in deps:
        src_id = (d.get("source") or {}).get("$ref")
        tgt_id = (d.get("target") or {}).get("$ref")
        if src_id in pkg_by_id and tgt_id in pkg_by_id:
            model_edges.add((pkg_by_id[src_id], pkg_by_id[tgt_id]))

    name_pattern = re.compile(
        r"^\s*(?:from|import)\s+(" + "|".join(re.escape(n) for n in names) + r")\b",
        re.MULTILINE,
    )
    real_edges = set()
    for name, code_tag in code_by_name.items():
        scan_dir = _pkg_scan_dir(project_root, code_tag)
        if scan_dir is None or not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            try:
                text = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for m in name_pattern.finditer(text):
                target = m.group(1)
                if target != name:
                    real_edges.add((name, target))

    violations = []
    for edge in sorted(model_edges - real_edges):
        violations.append({
            "check": "PKG_EDGE_STALE", "element": "PKG-TIERS",
            "detail": f"model draws {edge[0]} -> {edge[1]}, but no live import of '{edge[1]}' "
                      f"was found under {code_by_name.get(edge[0])}",
        })
    for edge in sorted(real_edges - model_edges):
        violations.append({
            "check": "PKG_EDGE_MISSING", "element": "PKG-TIERS",
            "detail": f"a live import of '{edge[1]}' exists under {code_by_name.get(edge[0])}, "
                      f"but PKG-TIERS draws no {edge[0]} -> {edge[1]} arrow",
        })
    counts = {
        "pkg_tiers_packages": len(names),
        "pkg_tiers_model_edges": len(model_edges),
        "pkg_tiers_real_edges": len(real_edges),
    }
    return violations, counts


def run_checks(project_root: Path):
    """Return (violations: list[dict], counts: dict)."""
    model_path = project_root / MODEL_FILE
    violations = []
    counts = {"elements_with_tags": 0, "code": 0, "test": 0, "adr": 0, "flag": 0, "status": 0}

    if not model_path.exists():
        violations.append({"check": "MODEL_MISSING", "detail": f"{MODEL_FILE} not found"})
        return violations, counts

    try:
        model = json.loads(model_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append({"check": "MODEL_INVALID", "detail": f"{MODEL_FILE} is not valid JSON: {exc}"})
        return violations, counts

    elements = []
    walk_tagged_elements(model, elements)
    counts["elements_with_tags"] = len(elements)

    af_flags, af_fields = _load_app_features_flags(project_root)
    seen_refs: dict[str, str] = {}  # dedupe identical checks across elements

    for name, etype, tags in elements:
        status = tags.get("status")
        if status is not None:
            counts["status"] += 1
            if status not in VALID_STATUS:
                violations.append({
                    "check": "STATUS_INVALID", "element": name, "type": etype,
                    "detail": f"status '{status}' is not one of {sorted(VALID_STATUS)}",
                })

        for key in ("code", "test"):
            ref = tags.get(key)
            if ref is None:
                continue
            counts[key] += 1
            cache_key = f"{key}:{ref}"
            if cache_key in seen_refs:
                err = seen_refs[cache_key]
            else:
                err = check_code_ref(project_root, ref)
                seen_refs[cache_key] = err
            if err:
                violations.append({
                    "check": f"{key.upper()}_BROKEN", "element": name, "type": etype,
                    "detail": f"{key}='{ref}': {err}",
                })

        adr = tags.get("adr")
        if adr:
            counts["adr"] += 1
            cache_key = f"adr:{adr}"
            if cache_key in seen_refs:
                err = seen_refs[cache_key]
            else:
                err = adr_errors(project_root, adr)
                seen_refs[cache_key] = err
            if err:
                violations.append({"check": "ADR_BROKEN", "element": name, "type": etype, "detail": err})

        flag = tags.get("flag")
        if flag:
            counts["flag"] += 1
            err = flag_error(flag, af_flags, af_fields)
            if err:
                violations.append({"check": "FLAG_BROKEN", "element": name, "type": etype, "detail": err})

    pkg_violations, pkg_counts = check_pkg_tiers(project_root)
    violations.extend(pkg_violations)
    counts.update(pkg_counts)

    return violations, counts


def render_report(violations, counts, project_root: Path) -> tuple[str, int]:
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        "# Audit Report: UML Model vs Code",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Model file: {MODEL_FILE}",
        "Rule: every code/test/adr/flag/status tag in the model resolves against the repository "
        "(.claude/design/uml_model_plan.md section 5)",
        "",
        f"- Elements with tags: {counts.get('elements_with_tags', 0)}",
        f"- code tags checked: {counts.get('code', 0)}",
        f"- test tags checked: {counts.get('test', 0)}",
        f"- adr tags checked: {counts.get('adr', 0)}",
        f"- flag tags checked: {counts.get('flag', 0)}",
        f"- status tags checked: {counts.get('status', 0)}",
        f"- PKG-TIERS packages scanned: {counts.get('pkg_tiers_packages', 0)}, "
        f"model edges: {counts.get('pkg_tiers_model_edges', 0)}, "
        f"live-import edges: {counts.get('pkg_tiers_real_edges', 0)}",
        f"- Violations: {len(violations)}",
        "",
    ]
    if not violations:
        lines += ["## Result: ✅ PASS", "", "No discrepancy found between the model and the repository.", ""]
    else:
        lines += ["## Result: ❌ FAIL", ""]
        by_check: dict[str, list] = {}
        for v in violations:
            by_check.setdefault(v["check"], []).append(v)
        for check, items in sorted(by_check.items()):
            lines.append(f"### {check} ({len(items)})")
            for it in items:
                where = f"`{it['element']}` ({it['type']})" if "type" in it else (f"`{it['element']}`" if "element" in it else "")
                lines.append(f"- {where}: {it['detail']}" if where else f"- {it['detail']}")
            lines.append("")
        lines += [
            "**Fix:** update the model element's tag in StarUML to match the repository, or fix the "
            "repository if the model is right and the code/docs have drifted. See the findings "
            "register `.claude/tasks/uml_findings.md` for the convention.",
            "",
        ]
    lines += [
        "## References",
        "- `.claude/design/uml_model_plan.md` section 5 — the discrepancy checks this audit implements",
        "- `.claude/tasks/uml_findings.md` — differences found between the model and the repository",
    ]
    return "\n".join(lines), (1 if violations else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else find_project_root(Path(__file__).resolve().parent)

    violations, counts = run_checks(project_root)
    report, exit_code = render_report(violations, counts, project_root)
    print(report)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {out}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
