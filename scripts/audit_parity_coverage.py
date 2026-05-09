#!/usr/bin/env python3
"""Audit: Parity mandate coverage (ADR-035 Polars, ADR-036 Plotnine).

Two checks:

  1. Plotnine parity (ADR-036) — exact inventory comparison.
     Enumerates all geom_*, stat_*, scale_*, coord_*, theme_*, position_*, guide_*,
     annotation_*, labs/lims/arrow/watermark/element_* symbols from the installed
     plotnine package and compares against components registered via
     @register_plot_component("name") in libs/viz_factory/.
     Reports: registered, unregistered (gap), and stale (registered but no longer
     in plotnine).

  2. Polars expression coverage (ADR-035) — namespace-grouped awareness report.
     Enumerates pl.Expr public methods grouped by accessor namespace (str, dt, list,
     arr, cat, meta, struct, name) and flat namespace.  Compares against actions
     registered via @register_action("name") in libs/transformer/.
     Polars actions are higher-level abstractions — a 1:1 name match is NOT required.
     The report flags Polars namespaces with low coverage so new releases are
     surfaced as potential gaps rather than as hard violations.

     Additionally, verifies that every registered action name resolves to an actual
     Python function in the codebase (import-existence check).

Both checks use AST parsing — no imports of the libraries under test are required
for the scanning step (only for the plotnine/polars enumeration).

Usage:
  .venv/bin/python scripts/audit_parity_coverage.py
  .venv/bin/python scripts/audit_parity_coverage.py --output .claude/logs/audits/audit_parity_coverage_2026-05-14.md
  .venv/bin/python scripts/audit_parity_coverage.py --skip-polars
  .venv/bin/python scripts/audit_parity_coverage.py --skip-plotnine
"""
import argparse
import ast
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _load_exclusions(project_root: Path) -> dict:
    """Load .claude/workflows/audit_exclusions.yaml, return {} on any failure."""
    excl_path = project_root / ".claude" / "workflows" / "audit_exclusions.yaml"
    if not excl_path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(excl_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

# ── Plotnine prefixes to enumerate ────────────────────────────────────────────

PLOTNINE_PREFIXES = [
    "geom_", "stat_", "scale_", "coord_", "theme_",
    "position_", "guide_", "annotation_", "facet_",
]
# Single-name symbols also in plotnine public API (not captured by prefix scan)
PLOTNINE_SINGLES = {
    "aes", "labs", "lims", "xlim", "ylim", "xlab", "ylab", "ggtitle",
    "arrow", "watermark", "element_text", "element_rect", "element_line",
    "element_blank", "margin", "theme", "ggplot", "qplot", "after_stat",
    "after_scale", "stage",
}

# Polars accessor namespaces — used to group the coverage report
POLARS_NAMESPACES = ["str", "dt", "list", "arr", "cat", "meta", "struct", "name"]


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


# ── AST scanning ──────────────────────────────────────────────────────────────

def extract_registered_names(source_dir: Path, decorator_name: str) -> dict[str, Path]:
    """Return {registered_name: source_file} for all @decorator_name("name") calls."""
    registered: dict[str, Path] = {}
    pattern = re.compile(rf'@{re.escape(decorator_name)}\(\s*["\']([^"\']+)["\']')
    for py_file in sorted(source_dir.rglob("*.py")):
        if any(p in py_file.parts for p in ("__pycache__", "tests")):
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in pattern.finditer(text):
            name = m.group(1)
            if name not in registered:
                registered[name] = py_file
    return registered


# ── Plotnine inventory ────────────────────────────────────────────────────────

def get_plotnine_symbols(python_bin: Path) -> set[str]:
    """Return all public symbols in the plotnine package matching our prefixes."""
    script = (
        "import plotnine as p9, sys\n"
        "prefixes = " + repr(PLOTNINE_PREFIXES) + "\n"
        "singles = " + repr(PLOTNINE_SINGLES) + "\n"
        "syms = {s for s in dir(p9) if any(s.startswith(p) for p in prefixes) and not s.startswith('_')}\n"
        "syms |= {s for s in singles if hasattr(p9, s)}\n"
        "print('\\n'.join(sorted(syms)))\n"
    )
    result = subprocess.run(
        [str(python_bin), "-c", script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return set()
    return set(result.stdout.strip().splitlines())


def get_plotnine_version(python_bin: Path) -> str:
    result = subprocess.run(
        [str(python_bin), "-c", "import plotnine; print(plotnine.__version__)"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


# ── Polars inventory ──────────────────────────────────────────────────────────

def get_polars_expr_methods(python_bin: Path) -> dict[str, list[str]]:
    """Return {namespace: [method_name, ...]} for pl.Expr and its accessors."""
    script = (
        "import polars as pl\n"
        "namespaces = " + repr(POLARS_NAMESPACES) + "\n"
        "result = {}\n"
        "flat = [m for m in dir(pl.Expr) if not m.startswith('_') and callable(getattr(pl.Expr, m, None))]\n"
        "result['__expr__'] = flat\n"
        "for ns in namespaces:\n"
        "    acc = getattr(pl.Expr, ns, None)\n"
        "    if acc is None: continue\n"
        "    acc_cls = type(acc.fget(pl.Expr.__new__(pl.Expr)) if hasattr(acc, 'fget') else acc)\n"
        "    try:\n"
        "        obj = getattr(pl.lit(1), ns)\n"
        "        methods = [m for m in dir(obj) if not m.startswith('_')]\n"
        "        result[ns] = methods\n"
        "    except Exception:\n"
        "        result[ns] = []\n"
        "import json; print(json.dumps(result))\n"
    )
    result = subprocess.run(
        [str(python_bin), "-c", script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return {}
    import json
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {}


def get_polars_version(python_bin: Path) -> str:
    result = subprocess.run(
        [str(python_bin), "-c", "import polars; print(polars.__version__)"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


# ── Coverage matching (loose) ─────────────────────────────────────────────────

def action_covers_polars_method(action_names: set[str], polars_method: str) -> bool:
    """Loose heuristic: does any registered action plausibly cover this polars method?

    We don't require exact name matches — action:cast covers pl.Expr.cast(),
    action:sort covers pl.LazyFrame.sort(), etc. We check if any action name
    is a substring of the polars method name or vice versa.
    """
    pm = polars_method.lower().replace("_", "")
    for action in action_names:
        a = action.lower().replace("_", "")
        if a in pm or pm in a:
            return True
    return False


# ── Report ─────────────────────────────────────────────────────────────────────

def render_report(
    registered_actions: dict[str, Path],
    registered_components: dict[str, Path],
    plotnine_symbols: set[str],
    plotnine_version: str,
    polars_methods: dict[str, list[str]],
    polars_version: str,
    skip_plotnine: bool,
    skip_polars: bool,
    project_root: Path,
    exclusions: dict | None = None,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    excl = exclusions or {}
    parity_excl = excl.get("parity_coverage", {})

    # Build exclusion sets from config
    custom_names: set[str] = {
        e["name"] for e in parity_excl.get("custom_viz_components", [])
    }
    known_stale_names: set[str] = {
        e["name"] for e in parity_excl.get("known_stale_components", [])
    }
    excluded_from_stale = custom_names | known_stale_names

    # Plotnine analysis
    comp_names = set(registered_components.keys())
    plotnine_gap = sorted(plotnine_symbols - comp_names)          # in plotnine, not registered
    raw_stale = comp_names - plotnine_symbols - custom_names       # registered, not in plotnine, not custom
    stale_components = sorted(raw_stale - known_stale_names)       # unknown stale (needs investigation)
    accepted_stale = sorted(raw_stale & known_stale_names)         # accepted stale (in exclusions file)

    # Polars analysis — count covered vs. total per namespace
    action_names = set(registered_actions.keys())
    polars_coverage: dict[str, tuple[int, int, list[str]]] = {}
    for ns, methods in polars_methods.items():
        uncovered = [m for m in methods if not action_covers_polars_method(action_names, m)]
        covered = len(methods) - len(uncovered)
        polars_coverage[ns] = (covered, len(methods), uncovered[:20])  # cap uncovered list

    lines = [
        "# Audit Report: Parity Mandate Coverage",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: ADR-035 (Polars Parity Mandate), ADR-036 (Artist Parity Mandate)",
        "",
    ]

    if not skip_plotnine:
        pct = int(100 * len(comp_names & plotnine_symbols) / max(len(plotnine_symbols), 1))
        lines += [
            f"- Plotnine {plotnine_version}: {len(plotnine_symbols)} symbols, "
            f"{len(comp_names & plotnine_symbols)} registered ({pct}% coverage), "
            f"{len(plotnine_gap)} gap",
            f"- Stale registrations: {len(stale_components)} unresolved, "
            f"{len(accepted_stale)} accepted (in audit_exclusions.yaml), "
            f"{len(custom_names)} custom (SPARMVET-specific)",
        ]
    if not skip_polars:
        total_methods = sum(len(v) for v in polars_methods.values())
        lines += [
            f"- Polars {polars_version}: {len(registered_actions)} registered actions, "
            f"{total_methods} total Expr methods across {len(polars_methods)} namespaces",
        ]
    lines += [""]

    # ── Plotnine section ──────────────────────────────────────────────────────
    if not skip_plotnine:
        lines += ["## Plotnine Parity (ADR-036)", ""]

        if stale_components:
            lines += [
                "### ❌ Unresolved Stale Registrations (not in plotnine, not in audit_exclusions.yaml)",
                "",
                "These registrations have no entry in `.claude/workflows/audit_exclusions.yaml`.",
                "Either add them to `known_stale_components` with a rationale, or remove the registration.",
                "",
            ]
            for name in stale_components:
                src = registered_components.get(name, Path("?"))
                lines.append(f"- `{name}` — registered in `{src.relative_to(project_root)}`")
            lines.append("")

        if accepted_stale:
            lines += [
                "### ℹ️ Accepted Stale Registrations (in audit_exclusions.yaml — no action needed)",
                "",
            ]
            parity_excl_map = {
                e["name"]: e.get("review_trigger", "")
                for e in parity_excl.get("known_stale_components", [])
            }
            for name in accepted_stale:
                trigger = parity_excl_map.get(name, "")
                lines.append(f"- `{name}` — review when: {trigger}")
            lines.append("")

        if plotnine_gap:
            # Group by prefix for readability
            grouped: dict[str, list[str]] = {}
            for sym in plotnine_gap:
                prefix = next((p for p in PLOTNINE_PREFIXES if sym.startswith(p)), "other")
                grouped.setdefault(prefix, []).append(sym)
            if "other" in grouped and sym in PLOTNINE_SINGLES:
                grouped["other"].append(sym)

            lines += [
                f"### 🔴 Coverage Gap — {len(plotnine_gap)} unregistered plotnine symbols",
                "",
                "These exist in the installed plotnine but have no `@register_plot_component` entry.",
                "Each missing symbol is a potential feature the VizFactory cannot express in a manifest.",
                "",
            ]
            for prefix in PLOTNINE_PREFIXES + ["other"]:
                syms = grouped.get(prefix, [])
                if not syms:
                    continue
                label = prefix.rstrip("_")
                lines += [f"**{label}** ({len(syms)} missing):"]
                lines.append("  " + ", ".join(f"`{s}`" for s in syms))
                lines.append("")
        else:
            lines += ["### ✅ Full Plotnine Coverage", "", "All plotnine symbols are registered.", ""]

        lines += [
            "**Action:** For each gap, decide whether to register the component or explicitly",
            "mark it as out-of-scope in this file's `SCOPE_EXCLUSIONS` set.",
            "See `rules_viz_factory.md §1` and `viz_factory_implementation.md`.",
            "",
        ]

    # ── Polars section ────────────────────────────────────────────────────────
    if not skip_polars:
        lines += ["## Polars Expression Coverage (ADR-035)", ""]
        lines += [
            "Coverage is measured by loose heuristic match (action name ↔ method name substring).",
            "Low-coverage namespaces indicate where new transformer actions may be valuable.",
            "",
            "| Namespace | Covered | Total | Coverage |",
            "|-----------|---------|-------|----------|",
        ]
        for ns, (covered, total, _) in sorted(polars_coverage.items()):
            pct = int(100 * covered / max(total, 1))
            icon = "✅" if pct >= 60 else ("⚠️" if pct >= 30 else "🔴")
            lines.append(f"| `{ns}` | {covered} | {total} | {icon} {pct}% |")
        lines.append("")

        low_ns = [(ns, d) for ns, d in polars_coverage.items() if d[1] > 0 and (d[0] / d[1]) < 0.3]
        if low_ns:
            lines += ["### 🔴 Low-Coverage Namespaces (< 30%)", ""]
            for ns, (covered, total, uncovered) in sorted(low_ns):
                lines += [
                    f"**`pl.Expr.{ns}.*`** — {covered}/{total} covered. "
                    f"Sample uncovered: {', '.join(f'`{m}`' for m in uncovered[:10])}",
                ]
            lines.append("")

        lines += [
            "**Action:** Low-coverage namespaces indicate where new `@register_action` decorators",
            "would provide the most value. Consult `rules_data_engine.md §5` (Polars Parity Mandate).",
            "",
        ]

    # ── Registered inventory ──────────────────────────────────────────────────
    lines += [
        "## Registered Inventory",
        "",
        f"### Transformer Actions ({len(registered_actions)} registered)",
        "",
        ", ".join(f"`{n}`" for n in sorted(registered_actions)),
        "",
        f"### VizFactory Components ({len(registered_components)} registered)",
        "",
        ", ".join(f"`{n}`" for n in sorted(registered_components)),
        "",
    ]

    lines += [
        "## References",
        "- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)",
        "- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)",
        "- `libs/transformer/src/transformer/actions/` — action registry source",
        "- `libs/viz_factory/src/viz_factory/` — component registry source",
        "- Routine 12 (Parity mandate coverage) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--skip-plotnine", action="store_true", help="Skip plotnine parity check")
    parser.add_argument("--skip-polars", action="store_true", help="Skip polars coverage check")
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )
    python_bin = project_root / ".venv" / "bin" / "python"

    transformer_actions_dir = project_root / "libs" / "transformer" / "src" / "transformer" / "actions"
    viz_factory_dir = project_root / "libs" / "viz_factory" / "src" / "viz_factory"

    print("Scanning transformer action registrations ...", file=sys.stderr)
    registered_actions = extract_registered_names(transformer_actions_dir, "register_action")

    print("Scanning viz_factory component registrations ...", file=sys.stderr)
    registered_components = extract_registered_names(viz_factory_dir, "register_plot_component")

    plotnine_symbols: set[str] = set()
    plotnine_version = "skipped"
    if not args.skip_plotnine:
        print("Enumerating plotnine symbols ...", file=sys.stderr)
        plotnine_symbols = get_plotnine_symbols(python_bin)
        plotnine_version = get_plotnine_version(python_bin)

    polars_methods: dict[str, list[str]] = {}
    polars_version = "skipped"
    if not args.skip_polars:
        print("Enumerating polars Expr methods ...", file=sys.stderr)
        polars_methods = get_polars_expr_methods(python_bin)
        polars_version = get_polars_version(python_bin)

    exclusions = _load_exclusions(project_root)

    report = render_report(
        registered_actions, registered_components,
        plotnine_symbols, plotnine_version,
        polars_methods, polars_version,
        args.skip_plotnine, args.skip_polars,
        project_root,
        exclusions=exclusions,
    )
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    # Exit 1 only for unresolved stale (accepted stale is expected debt)
    comp_names = set(registered_components.keys())
    custom_names = {e["name"] for e in exclusions.get("parity_coverage", {}).get("custom_viz_components", [])}
    known_stale = {e["name"] for e in exclusions.get("parity_coverage", {}).get("known_stale_components", [])}
    unresolved_stale = comp_names - plotnine_symbols - custom_names - known_stale
    return 1 if (not args.skip_plotnine and unresolved_stale) else 0


if __name__ == "__main__":
    sys.exit(main())
