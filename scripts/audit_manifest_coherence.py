#!/usr/bin/env python3
"""Audit: Manifest coherence — static validation of pipeline manifests.

Goes beyond manifest integrity (does it assemble?) to verify four structural
contracts WITHOUT running the assembler:

  1. Input field coverage — every slug declared in `input_fields` must match
     an actual column header in the source TSV.  Catches silent skip-on-mismatch
     bugs (the engine drops unmatched fields with no error).

  2. Action name validity — every `action:` value in `wrangling` and assembly
     `recipe` blocks must be registered via @register_action("name") in the
     transformer library.  Catches typos and stale action names.

  3. Component name validity — every `name:` value inside plot `layers:` blocks
     must be registered via @register_plot_component("name") in viz_factory.

  4. Join key symmetry — for every `action: join` step, both `'on'` (or
     `left_on` / `right_on`) values must appear as declared field slugs in the
     schemas being joined.  Catches quoted-boolean traps and spelling mismatches.

This audit is STATIC — it reads YAML and TSV headers only.  It does not run
any Python code from the manifest or transformer library.

Usage:
  .venv/bin/python scripts/audit_manifest_coherence.py
  .venv/bin/python scripts/audit_manifest_coherence.py --output .claude/logs/audits/audit_manifest_coherence_2026-05-14.md
  .venv/bin/python scripts/audit_manifest_coherence.py --manifest config/manifests/pipelines/2_test_data_ST22_dummy.yaml
  .venv/bin/python scripts/audit_manifest_coherence.py --skip-tsv       # skip TSV column checks (faster)
  .venv/bin/python scripts/audit_manifest_coherence.py --skip-join      # skip join key symmetry
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# ── YAML loading with !include support ────────────────────────────────────────

def _load_yaml_with_includes(path: Path) -> object:
    """Load a YAML file, resolving !include directives relative to the file's directory."""
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml not installed. Run: .venv/bin/pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    class _IncludeLoader(yaml.SafeLoader):
        pass

    def _include_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> object:
        include_path = Path(loader.name).parent / loader.construct_scalar(node)  # type: ignore[arg-type]
        if not include_path.exists():
            return f"__MISSING_INCLUDE__:{include_path}"
        return _load_yaml_with_includes(include_path)

    _IncludeLoader.add_constructor("!include", _include_constructor)

    try:
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, Loader=_IncludeLoader)
    except Exception as exc:
        return f"__PARSE_ERROR__:{exc}"


# ── AST scanning for registered names ─────────────────────────────────────────

def _extract_registered_names(source_dir: Path, decorator_name: str) -> set[str]:
    pattern = re.compile(rf'@{re.escape(decorator_name)}\(\s*["\']([^"\']+)["\']')
    names: set[str] = set()
    for py_file in sorted(source_dir.rglob("*.py")):
        if any(p in py_file.parts for p in ("__pycache__", "tests")):
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except OSError:
            continue
        names.update(m.group(1) for m in pattern.finditer(text))
    return names


# ── TSV header reading ─────────────────────────────────────────────────────────

def _read_tsv_columns(tsv_path: Path) -> list[str] | None:
    """Return column names from TSV header row, or None if file missing."""
    if not tsv_path.exists():
        return None
    try:
        with open(tsv_path, encoding="utf-8") as f:
            header = f.readline().rstrip("\n")
        sep = "\t" if "\t" in header else ","
        return [c.strip() for c in header.split(sep)]
    except OSError:
        return None


# ── Deep walk helpers ─────────────────────────────────────────────────────────

def _walk_actions(obj: object, depth: int = 0) -> list[str]:
    """Recursively collect all `action:` values from a nested structure."""
    if depth > 20:
        return []
    actions = []
    if isinstance(obj, dict):
        if "action" in obj and isinstance(obj["action"], str):
            actions.append(obj["action"])
        for v in obj.values():
            actions.extend(_walk_actions(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            actions.extend(_walk_actions(item, depth + 1))
    return actions


def _walk_layer_names(obj: object, depth: int = 0) -> list[str]:
    """Collect all `name:` values inside `layers:` blocks."""
    if depth > 20:
        return []
    names = []
    if isinstance(obj, dict):
        if "layers" in obj and isinstance(obj["layers"], list):
            for layer in obj["layers"]:
                if isinstance(layer, dict) and "name" in layer:
                    names.append(str(layer["name"]))
        for k, v in obj.items():
            if k != "layers":
                names.extend(_walk_layer_names(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            names.extend(_walk_layer_names(item, depth + 1))
    return names


def _walk_join_steps(obj: object, depth: int = 0) -> list[dict]:
    """Collect all join action step dicts."""
    if depth > 20:
        return []
    joins = []
    if isinstance(obj, dict):
        if obj.get("action") == "join":
            joins.append(obj)
        for v in obj.values():
            joins.extend(_walk_join_steps(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            joins.extend(_walk_join_steps(item, depth + 1))
    return joins


def _collect_all_field_slugs(manifest: dict) -> set[str]:
    """Return union of all input_fields and output_fields slugs across all schemas."""
    slugs: set[str] = set()
    schemas = manifest.get("data_schemas", {})
    if isinstance(schemas, dict):
        for schema in schemas.values():
            if not isinstance(schema, dict):
                continue
            for fields_key in ("input_fields", "output_fields"):
                fields = schema.get(fields_key, {})
                if isinstance(fields, dict):
                    slugs.update(fields.keys())
    return slugs


# ── Per-manifest analysis ─────────────────────────────────────────────────────

def analyse_manifest(
    manifest_path: Path,
    project_root: Path,
    registered_actions: set[str],
    registered_components: set[str],
    skip_tsv: bool,
    skip_join: bool,
) -> dict:
    """Return a result dict for a single manifest."""
    result: dict = {
        "path": str(manifest_path.relative_to(project_root)),
        "parse_error": None,
        "missing_includes": [],
        "tsv_violations": [],    # {schema_id, slug, source_path, message}
        "action_violations": [], # {context, action_name}
        "component_violations": [],  # {context, name}
        "join_violations": [],   # {context, key, message}
    }

    raw = _load_yaml_with_includes(manifest_path)
    if isinstance(raw, str) and raw.startswith("__PARSE_ERROR__"):
        result["parse_error"] = raw[len("__PARSE_ERROR__:"):]
        return result
    if not isinstance(raw, dict):
        result["parse_error"] = f"Unexpected YAML root type: {type(raw).__name__}"
        return result

    manifest = raw

    # Collect all declared field slugs (used for join key validation)
    all_slugs = _collect_all_field_slugs(manifest)

    schemas = manifest.get("data_schemas", {})
    if not isinstance(schemas, dict):
        schemas = {}

    # ── Check 1: Input fields vs TSV columns ─────────────────────────────────
    if not skip_tsv:
        for schema_id, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            source = schema.get("source", {})
            if not isinstance(source, dict):
                continue
            tsv_rel = source.get("path")
            if not tsv_rel:
                continue

            # path may be relative to project root or to manifest dir
            for base in (project_root, manifest_path.parent):
                tsv_path = (base / tsv_rel).resolve()
                if tsv_path.exists():
                    break
            else:
                result["tsv_violations"].append({
                    "schema_id": schema_id,
                    "slug": "(source file)",
                    "message": f"Source TSV not found: `{tsv_rel}`",
                })
                continue

            tsv_cols = _read_tsv_columns(tsv_path)
            if tsv_cols is None:
                result["tsv_violations"].append({
                    "schema_id": schema_id,
                    "slug": "(source file)",
                    "message": f"Could not read TSV columns: `{tsv_path.name}`",
                })
                continue

            tsv_col_set = set(tsv_cols)
            input_fields = schema.get("input_fields", {})
            if isinstance(input_fields, dict):
                for slug in input_fields:
                    if slug not in tsv_col_set:
                        result["tsv_violations"].append({
                            "schema_id": schema_id,
                            "slug": slug,
                            "message": f"input_fields slug `{slug}` not in TSV columns",
                        })

    # ── Check 2: Action names ─────────────────────────────────────────────────
    all_actions = _walk_actions(manifest)
    for action_name in all_actions:
        # Skip engine-internal actions
        if action_name in ("sink_parquet", "scan_parquet"):
            continue
        if action_name not in registered_actions:
            result["action_violations"].append({
                "action_name": action_name,
                "context": manifest_path.name,
            })

    # ── Check 3: Component names in layers ────────────────────────────────────
    all_component_names = _walk_layer_names(manifest)
    for name in all_component_names:
        if name not in registered_components:
            result["component_violations"].append({
                "name": name,
                "context": manifest_path.name,
            })

    # ── Check 4: Join key symmetry ────────────────────────────────────────────
    if not skip_join and all_slugs:
        join_steps = _walk_join_steps(manifest)
        for step in join_steps:
            # `on` key — may be True (YAML boolean trap) or a string
            on_val = step.get("on") or step.get(True)  # 'on' parses as True in YAML
            if on_val is True:
                result["join_violations"].append({
                    "context": manifest_path.name,
                    "key": "on",
                    "message": "Join key `on` parsed as boolean True — must be quoted as `'on'`",
                })
                on_val = None

            for key_val in filter(None, [
                on_val,
                step.get("left_on"),
                step.get("right_on"),
            ]):
                keys = [key_val] if isinstance(key_val, str) else (key_val if isinstance(key_val, list) else [])
                for k in keys:
                    if isinstance(k, str) and k not in all_slugs:
                        result["join_violations"].append({
                            "context": manifest_path.name,
                            "key": k,
                            "message": f"Join key `{k}` not declared in any schema's input_fields or output_fields",
                        })

    return result


# ── Report ─────────────────────────────────────────────────────────────────────

def render_report(
    results: list[dict],
    project_root: Path,
    skip_tsv: bool,
    skip_join: bool,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")

    parse_errors = [r for r in results if r["parse_error"]]
    tsv_fails = [r for r in results if r["tsv_violations"]]
    action_fails = [r for r in results if r["action_violations"]]
    component_fails = [r for r in results if r["component_violations"]]
    join_fails = [r for r in results if r["join_violations"]]

    overall_pass = not any([parse_errors, tsv_fails, action_fails, component_fails, join_fails])

    lines = [
        "# Audit Report: Manifest Coherence",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: ADR-013 (Manifest Data Contract), ADR-041 (Unified Manifest Standard), rules_manifest_structure.md §7",
        "",
        f"- Manifests assessed: {len(results)}",
        f"- Parse errors: {len(parse_errors)}",
    ]
    if not skip_tsv:
        lines.append(f"- Manifests with input_fields/TSV mismatches: {len(tsv_fails)}")
    lines += [
        f"- Manifests with invalid action names: {len(action_fails)}",
        f"- Manifests with invalid component names: {len(component_fails)}",
    ]
    if not skip_join:
        lines.append(f"- Manifests with join key violations: {len(join_fails)}")
    lines += ["", f"## Result: {'✅ PASS' if overall_pass else '❌ FAIL'}", ""]

    # Parse errors — highest priority
    if parse_errors:
        lines += ["## ❌ Parse Errors (cannot analyse)", ""]
        for r in parse_errors:
            lines += [f"### `{r['path']}`", f"```", r["parse_error"], "```", ""]

    # Action name violations
    if action_fails:
        lines += ["## ❌ Invalid Action Names", ""]
        lines += [
            "These action names appear in `action:` keys but are NOT registered via `@register_action()`.",
            "This means the wrangling step will be silently skipped at runtime.",
            "",
        ]
        for r in action_fails:
            lines += [f"### `{r['path']}`"]
            for v in r["action_violations"]:
                lines.append(f"- `action: {v['action_name']}` — not registered in transformer")
            lines.append("")

    # Component name violations
    if component_fails:
        lines += ["## ❌ Invalid Component Names", ""]
        lines += [
            "These `name:` values in plot `layers:` blocks are NOT registered via `@register_plot_component()`.",
            "They will cause a `VisualizationError` at runtime.",
            "",
        ]
        for r in component_fails:
            lines += [f"### `{r['path']}`"]
            for v in r["component_violations"]:
                lines.append(f"- `name: {v['name']}` — not registered in viz_factory")
            lines.append("")

    # Join key violations
    if not skip_join and join_fails:
        lines += ["## ❌ Join Key Violations", ""]
        for r in join_fails:
            lines += [f"### `{r['path']}`"]
            for v in r["join_violations"]:
                lines.append(f"- {v['message']}")
            lines.append("")

    # TSV field mismatches
    if not skip_tsv and tsv_fails:
        lines += ["## ⚠️ Input Fields / TSV Column Mismatches", ""]
        lines += [
            "These `input_fields` slugs do not match any column name in the source TSV.",
            "The engine will silently skip unmatched fields — this produces missing columns downstream.",
            "",
        ]
        for r in tsv_fails:
            lines += [f"### `{r['path']}`"]
            for v in r["tsv_violations"]:
                lines.append(f"- `{v['schema_id']}` → `{v['slug']}`: {v['message']}")
            lines.append("")

    # Per-manifest summary matrix
    lines += [
        "## Per-Manifest Summary",
        "",
        "| Manifest | Parse | Actions | Components | Join Keys | TSV Fields |",
        "|----------|-------|---------|------------|-----------|------------|",
    ]
    for r in results:
        def icon(violations: list) -> str:
            return "✅" if not violations else f"❌ {len(violations)}"
        parse_icon = "✅" if not r["parse_error"] else "❌"
        tsv_icon = ("⬜ skip" if skip_tsv else icon(r["tsv_violations"]))
        join_icon = ("⬜ skip" if skip_join else icon(r["join_violations"]))
        lines.append(
            f"| `{Path(r['path']).name}` "
            f"| {parse_icon} "
            f"| {icon(r['action_violations'])} "
            f"| {icon(r['component_violations'])} "
            f"| {join_icon} "
            f"| {tsv_icon} |"
        )
    lines += [""]

    lines += [
        "## Fix Guidance",
        "",
        "**Invalid action name:** Check `rules_persona_bioscientist.md §8` for the authoritative list.",
        "If the action genuinely does not exist, file an `[ENHANCEMENT REQUEST]` in `tasks.md`.",
        "",
        "**Invalid component name:** Scan `libs/viz_factory/src/viz_factory/` for `@register_plot_component`.",
        "If missing, follow `viz_factory_implementation.md` to add it.",
        "",
        "**Join key YAML trap:** `on:` without quotes parses as boolean `True`.",
        "Always write `'on': column_name` (single-quoted key).",
        "",
        "**Input field slug mismatch:** Run `head -1 <source.tsv>` to see actual column names.",
        "Update the `input_fields` slug to match exactly (case-sensitive).",
        "",
        "## References",
        "- `rules_manifest_structure.md §7` — Canonical recipe syntax, YAML boolean trap",
        "- `rules_persona_bioscientist.md §8` — Registered action names (authoritative list)",
        "- `rules_persona_bioscientist.md §3-A/B` — Wrangling and assembly canon",
        "- Routine 13 (Manifest coherence) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def _load_exclusions(project_root: Path) -> dict:
    excl_path = project_root / ".claude" / "workflows" / "audit_exclusions.yaml"
    if not excl_path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(excl_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--manifest", default=None, help="Single manifest YAML to check")
    parser.add_argument("--skip-tsv", action="store_true", help="Skip TSV column header checks")
    parser.add_argument("--skip-join", action="store_true", help="Skip join key symmetry checks")
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )

    transformer_actions_dir = project_root / "libs" / "transformer" / "src" / "transformer" / "actions"
    viz_factory_dir = project_root / "libs" / "viz_factory" / "src" / "viz_factory"

    exclusions = _load_exclusions(project_root)
    # Build accepted join keys per manifest from exclusions config
    accepted_join_keys: dict[str, set[str]] = {}
    for entry in exclusions.get("manifest_coherence", {}).get("known_assembly_keys", []):
        mname = entry.get("manifest", "")
        key = entry.get("key", "")
        if mname and key:
            accepted_join_keys.setdefault(mname, set()).add(key)

    print("Scanning registered action names ...", file=sys.stderr)
    registered_actions = _extract_registered_names(transformer_actions_dir, "register_action")

    print("Scanning registered component names ...", file=sys.stderr)
    registered_components = _extract_registered_names(viz_factory_dir, "register_plot_component")

    manifests_dir = project_root / "config" / "manifests" / "pipelines"
    if args.manifest:
        manifest_paths = [project_root / args.manifest]
    else:
        manifest_paths = sorted(
            p for p in manifests_dir.glob("*.yaml")
            if not p.name.startswith("_")
        )

    results = []
    for manifest_path in manifest_paths:
        print(f"Checking {manifest_path.name} ...", file=sys.stderr)
        result = analyse_manifest(
            manifest_path, project_root,
            registered_actions, registered_components,
            args.skip_tsv, args.skip_join,
        )
        # Filter accepted join key violations
        accepted = accepted_join_keys.get(manifest_path.name, set())
        if accepted:
            result["join_violations"] = [
                v for v in result["join_violations"]
                if v.get("key") not in accepted
            ]
        results.append(result)

    report = render_report(results, project_root, args.skip_tsv, args.skip_join)
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    has_failures = any(
        r["parse_error"] or r["action_violations"] or r["component_violations"] or
        (not args.skip_tsv and r["tsv_violations"]) or
        (not args.skip_join and r["join_violations"])
        for r in results
    )
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
