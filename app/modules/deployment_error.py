"""
@deps
provides: class:DeploymentError, function:format_errors_block, function:exit_if_errors
consumes: -
consumed_by: app/modules/persona_validator.py, app/modules/sidebar_validator.py, app/src/server.py, scripts/validate_persona_config.py
doc: .claude/knowledge/architecture_decisions.md#adr-078

Diagnostic Error Discipline (ADR-078).

A `DeploymentError` is a structured error record for any failure surfaced at startup
or configuration time. The fields are designed so an operator who has never opened
the codebase can locate the problem and fix it without reading Python.

Used by validators (persona, sidebar, manifest, ingestion) and bootloader / connector
init paths. Headless-safe — no Shiny imports.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Iterable, NoReturn


@dataclass(frozen=True)
class DeploymentError:
    """Structured error record. All fields are operator-readable strings.

    The five mandatory fields answer the operator's questions in the order they ask:
    WHAT broke, WHERE, WHY, HOW to fix, WHO is responsible.
    """

    component: str
    """Source of the error — class or subsystem name. e.g. 'PersonaValidator',
    'Bootloader', 'IridaConnector'. Helps the operator identify which logs to grep
    and which person owns the surface."""

    problem: str
    """One-sentence statement of what is wrong. Concrete and specific —
    'blueprint_agent_enabled=True requires blueprint_enabled=True' beats
    'invalid configuration'."""

    location: str
    """Where the problem was detected. File path (preferably relative to project
    root) plus key/line if available. e.g. 'config/ui/templates/foo.yaml:23' or
    'features.blueprint_agent_enabled in config/ui/templates/foo.yaml'."""

    fix: str
    """Concrete remediation. Should be actionable without further investigation:
    name the file to edit, the key to change, the value to set. Multi-line allowed
    when alternatives exist."""

    who: str = "operator"
    """Who needs to act: 'operator', 'developer', or 'both'. 'operator' = config
    edit, no code change. 'developer' = code change required. 'both' = config edit
    that also reveals an underlying code/design issue worth raising."""

    reference: str = ""
    """Optional pointer to authoritative documentation: rule file path with section
    anchor, ADR number, or URL. Helps the operator confirm the rule before changing
    anything."""

    related: tuple[str, ...] = field(default_factory=tuple)
    """Optional list of related identifiers (other files, other flags, related
    error IDs). Empty tuple by default — only populate when context genuinely
    helps."""

    def format(self) -> str:
        """Render the error as a labelled block for stdout / log output.

        The format is fixed to make grepping and visual scanning predictable
        across every component that uses this class.
        """
        lines = [
            "[FATAL] " + self.problem,
            f"  Component:  {self.component}",
            f"  Location:   {self.location}",
            f"  Fix:        {self.fix}",
            f"  Who:        {self.who}",
        ]
        if self.reference:
            lines.append(f"  See:        {self.reference}")
        if self.related:
            lines.append(f"  Related:    {', '.join(self.related)}")
        return "\n".join(lines)


def format_errors_block(errors: Iterable[DeploymentError], header: str | None = None) -> str:
    """Format a sequence of errors into a single block suitable for stdout.

    Adds a header line and a separator between errors. Returns the empty string
    if no errors were provided so callers can do `if block: print(block)` safely.
    """
    items = list(errors)
    if not items:
        return ""
    sep = "\n" + ("=" * 72) + "\n"
    head = (header or f"Deployment failed — {len(items)} fatal error(s) detected").strip()
    return (
        sep
        + head
        + sep
        + ("\n\n".join(e.format() for e in items))
        + sep
        + "Fix the errors above and restart. The app cannot start in a contradictory state.\n"
        + "(See ADR-077 for the no-silent-suppression rule and ADR-078 for the\n"
        + " diagnostic-error discipline that produced this output.)\n"
    )


def exit_if_errors(
    errors: Iterable[DeploymentError],
    header: str | None = None,
    code: int = 1,
) -> None:
    """If `errors` is non-empty, print the formatted block to stderr and `sys.exit(code)`.

    A no-op when the iterable is empty — safe to call unconditionally at startup.
    """
    items = list(errors)
    if not items:
        return
    print(format_errors_block(items, header=header), file=sys.stderr)
    sys.exit(code)


def raise_if_errors(
    errors: Iterable[DeploymentError],
    header: str | None = None,
) -> None:
    """Like `exit_if_errors` but raises `DeploymentFailure` instead of `sys.exit`.

    For contexts (e.g. test suites, embedded server) where exiting the process is
    the wrong response. The caller can catch `DeploymentFailure` and decide.
    """
    items = list(errors)
    if not items:
        return
    raise DeploymentFailure(format_errors_block(items, header=header), errors=tuple(items))


class DeploymentFailure(Exception):
    """Aggregated startup failure. Carries the original DeploymentError list."""

    def __init__(self, message: str, errors: tuple[DeploymentError, ...] = ()) -> None:
        super().__init__(message)
        self.errors = errors
