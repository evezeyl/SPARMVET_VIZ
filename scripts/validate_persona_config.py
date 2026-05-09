#!/usr/bin/env python3
"""
validate_persona_config.py — CLI runner for PersonaValidator + SidebarValidator (ADR-073).

Validates one or all persona templates for feature-flag consistency and sidebar slot
registry correctness. Intended for CI use (--strict) and developer diagnostics.

Usage:
    ./.venv/bin/python scripts/validate_persona_config.py --persona developer
    ./.venv/bin/python scripts/validate_persona_config.py --all
    ./.venv/bin/python scripts/validate_persona_config.py --all --strict

Exit codes:
    0  — all templates valid (no errors; warnings may be present)
    1  — one or more templates have errors (or warnings in --strict mode)
"""

import argparse
import sys
from pathlib import Path

# Ensure project root on sys.path (works when run from any directory)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.modules.persona_validator import PersonaValidator
from app.modules.sidebar_validator import SidebarValidator
from app.modules.deployment_error import DeploymentError, format_errors_block

_TEMPLATES_DIR = _project_root / "config" / "ui" / "templates"

# ── Thin warning collector ────────────────────────────────────────────────────

class _WarningCollector:
    """Intercepts print() calls from validators to count and buffer warnings."""
    def __init__(self):
        self._warnings: list[str] = []
        self._original_print = None

    def __enter__(self):
        import builtins
        self._original_print = builtins.print
        collector = self

        def _patched(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            if "WARNING" in msg or "NOTE" in msg:
                collector._warnings.append(msg)
            collector._original_print(*args, **kwargs)

        builtins.print = _patched
        return self

    def __exit__(self, *_):
        import builtins
        builtins.print = self._original_print

    @property
    def count(self) -> int:
        return len(self._warnings)


# ── Validation helpers ────────────────────────────────────────────────────────

def _validate_template(path: Path, strict: bool) -> tuple[int, int]:
    """Validate one template. Returns (error_count, warning_count)."""
    pv = PersonaValidator()
    sv = SidebarValidator()

    with _WarningCollector() as wc:
        pv_errors = pv.validate_file(str(path))            # list[DeploymentError]
        sv_errors_raw = sv.validate_file(str(path))        # list[str] — legacy, retrofit pending

    # Normalise legacy SidebarValidator strings into DeploymentError shape so the
    # operator sees the same format regardless of source. Full retrofit tracked
    # as DIAG-VALIDATE-SIDEBAR-1 (ADR-078 Phase C).
    sv_errors = [DeploymentError(
        component="SidebarValidator",
        problem=msg,
        location=str(path),
        fix=(
            "Check workspaces.<ws>.left_sidebar.panels and right_sidebar.panels in "
            "the persona template. Each panel type must exist in PANEL_REGISTRY "
            "(app/modules/sidebar_registry.py). See ui_implementation_contract.md §11."
        ),
        who="operator",
        reference="ADR-073 + .claude/rules/ui_implementation_contract.md §11",
    ) for msg in sv_errors_raw]

    errors = pv_errors + sv_errors
    warnings = wc.count

    if errors:
        print(format_errors_block(errors), file=sys.stderr)

    return len(errors), warnings


def _discover_templates() -> list[Path]:
    if not _TEMPLATES_DIR.exists():
        print(f"Templates directory not found: {_TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)
    return sorted(_TEMPLATES_DIR.glob("*_template.yaml"))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--persona", "-p",
        metavar="ID",
        help="Validate a single persona by ID (e.g. developer) or path to a template YAML.",
    )
    group.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_templates",
        help="Validate all templates found in config/ui/templates/.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (for CI). Exit 1 if any warnings are present.",
    )
    args = parser.parse_args()

    if args.all_templates:
        templates = _discover_templates()
        if not templates:
            print("No templates found.", file=sys.stderr)
            sys.exit(1)
    else:
        # Accept path or shortname
        candidate = Path(args.persona)
        if candidate.exists():
            templates = [candidate.resolve()]
        else:
            templates = [_TEMPLATES_DIR / f"{args.persona}_template.yaml"]
            if not templates[0].exists():
                print(
                    f"Template not found: {templates[0]}\n"
                    f"(Also tried: {args.persona})",
                    file=sys.stderr,
                )
                sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for path in templates:
        print(f"\n{'=' * 60}")
        print(f"Validating: {path.name}")
        print(f"{'=' * 60}")
        errs, warns = _validate_template(path, strict=args.strict)
        total_errors += errs
        total_warnings += warns
        status = "PASS" if errs == 0 else "FAIL"
        print(f"  → {status}  errors={errs}  warnings={warns}")

    print(f"\n{'─' * 60}")
    print(f"Total: {len(templates)} template(s)  errors={total_errors}  warnings={total_warnings}")

    if total_errors > 0:
        print("RESULT: FAIL (errors present)", file=sys.stderr)
        sys.exit(1)

    if args.strict and total_warnings > 0:
        print("RESULT: FAIL (--strict: warnings treated as errors)", file=sys.stderr)
        sys.exit(1)

    print("RESULT: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
