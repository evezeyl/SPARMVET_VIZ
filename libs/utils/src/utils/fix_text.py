"""How a fix is shown to a person: `Fix: write 3`, but a text that already starts with `Suggestion:` is shown as it is.

Eve's form for every text a user reads is "what happened, then Suggestion: ...". A fix that starts with `Suggestion:`
already says what it is, so a `Fix:` label before it reads "Fix: Suggestion: ..." (found 2026-11-16). One function, used wherever a
fix is printed: the factory's error form, the checker's problem text, the load gate and upload reports, the alerts
panel of HOME. (`app/src/bootloader.py` and `DataAnalysisRecipeProblem.__str__` already follow the same rule for a tip.)

# @deps
# provides: function:fix_label, function:fix_prefix, function:with_fix, constant:SUGGESTION
# consumed_by: libs/utils/src/utils/pipeline_error.py, app/src/bootloader.py, app/handlers/blueprint_handlers.py, libs/utils/src/utils/recipe_check.py, libs/viz_factory/src/viz_factory/errors.py, app/modules/data_analysis_recipe_validator.py, app/handlers/home_theater.py, app/handlers/audit_stack.py, app/tests/test_suggestion_label.py
# doc: .claude/design/recipe_format_spec.md (P5, section 15)
# @end_deps
"""
SUGGESTION = "Suggestion:"


def fix_prefix(fix: str, who: str = "") -> str:
    """The label before a fix: `Fix: ` or `Fix (<who>): `; empty when the fix starts with `Suggestion:` (or is empty)."""
    if not fix or fix.startswith(SUGGESTION):
        return ""
    return f"Fix ({who}): " if who else "Fix: "


def fix_label(fix: str, who: str = "") -> str:
    """`Fix: <fix>` (or `Fix (<who>): <fix>`), or the fix alone when it starts with `Suggestion:`; empty for an empty fix."""
    return fix_prefix(fix, who) + fix if fix else ""


def with_fix(problem: str, fix: str, label: str = "Fix") -> str:
    """One sentence for a reader that shows a problem and its fix as one text: `<what happens>. <fix>`, with exactly one period.

    The one function behind every such reader of an advice or a checker problem (the command line `Problem.text()`, HOME's
    gate notes, Blueprint's Validate, the upload reports): none builds the sentence itself, so a text can neither lose the
    period before `Suggestion:` nor carry two. A fix that starts with `Suggestion:` is shown as it is; any other fix gets `label`
    ("Fix", or "Tip" where a screen says so). A problem that already ends with a period, `!` or `?` is not given another.
    """
    problem = problem.rstrip()
    if not fix:
        return problem
    if problem[-1:] not in (".", "!", "?"):
        problem += "."
    return f"{problem} {fix if fix.startswith(SUGGESTION) else f'{label}: {fix}'}"
