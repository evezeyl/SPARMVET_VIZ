"""
@deps
provides: class:AppFeaturesValidator
consumes: config/app_features/*.yaml, app/modules/deployment_error.py
consumed_by: app/src/server.py (validate_file with the deployment's app_features_override, D-0018), scripts/validate_app_features_config.py, scripts/audit_app_features_flags.py, app/tests/test_app_features_validator.py
doc: .claude/knowledge/architecture_decisions.md#adr-077, #adr-078, .claude/rules/rules_app_features_flags.md (Rule 6, D-0018)
"""
from pathlib import Path
from typing import Optional
import yaml

from app.modules.deployment_error import DeploymentError

# All feature flags that every template must declare
_REQUIRED_FLAGS = [
    "interactivity_enabled",
    "t3_sandbox_enabled",
    "gallery_enabled",
    "blueprint_enabled",
    "test_lab_enabled",
    "comparison_mode_enabled",
    "session_management_enabled",
    "import_helper_enabled",
    "export_enabled",
    "metadata_ingestion_enabled",
    "data_ingestion_enabled",
    "data_analysis_recipe_edit_enabled",
    "blueprint_agent_enabled",
]

# Child flags that require their master gate to be True — soft cascade.
# These are SILENTLY SUPPRESSED by the bootloader and produce a Rule 5 WARNING.
# Reason: there are many legacy templates with these inconsistencies and the
# silent suppression preserves backward-compatible behaviour.
_CASCADE_GATES: dict[str, list[str]] = {
    "interactivity_enabled": [
        "t3_sandbox_enabled",
        "comparison_mode_enabled",
        "session_management_enabled",
    ],
    "import_helper_enabled": ["data_ingestion_enabled"],
}

# Group D cascades — FATAL. The bootloader does NOT silently suppress these:
# the user's flag value passes through unchanged and Rule 7 raises a fatal
# error at startup if a template declares the child on while the master is off.
# Reason: these flags gate advanced/IDE features where silent divergence between
# YAML intent and runtime state is more harmful than a hard failure.
# (ADR-075 data_analysis_recipe_edit_enabled, ADR-076 blueprint_agent_enabled.)
_FATAL_CASCADE_GATES: dict[str, list[str]] = {
    "blueprint_enabled": [
        "data_analysis_recipe_edit_enabled",
        "blueprint_agent_enabled",
    ],
}


class AppFeaturesValidator:
    """Validates app features file completeness at startup.

    Call validate() before define_server(). Errors are fatal; warnings are logged.
    """

    def validate(self, template: dict, template_path: str,
                 flag_overrides: Optional[dict] = None) -> list[DeploymentError]:
        """Return a list of DeploymentError records. Empty list means template is valid.

        flag_overrides is the deployment's app_features_override block: the flag rules are
        checked on the RESOLVED flags (file plus override), the same ones the app runs with
        (Bootloader.flags), so an override cannot break a rule unseen (D-0018).

        Errors carry full operator-facing context (component, problem, location,
        fix, who, reference). Warnings are still printed inline for missing-flag
        and soft-cascade cases — they do not block startup.
        """
        errors: list[DeploymentError] = []
        warnings: list[str] = []

        file_features = template.get("flags", {})
        overrides = dict(flag_overrides or {})
        features = {**file_features, **overrides}

        # Rule 3: all required feature flags must be present (warn if missing, use defaults)
        for flag in _REQUIRED_FLAGS:
            if flag not in features:
                warnings.append(
                    f"Feature flag '{flag}' missing from template '{template_path}' — defaulting to False"
                )

        # Rule 4 (removed, ADR-091): an app features file names no data analysis recipe; the deployment does,
        # and the bootloader stops the app if the selector is hidden and no data analysis recipe is named.

        # Rule 6 (D-0018): the audit (t3_sandbox_enabled) requires comparison, sessions and
        # export; comparison requires the audit. FATAL, never silently rewritten.
        def _where(*flags: str) -> str:
            from_override = [f for f in flags if f in overrides]
            where = f"flags in {template_path}"
            if from_override:
                where += " and app_features_override of the deployment (" + ", ".join(from_override) + ")"
            return where

        _T3_COMPANIONS = [
            "comparison_mode_enabled",
            "session_management_enabled",
            "export_enabled",
        ]
        if features.get("t3_sandbox_enabled", False):
            for companion in _T3_COMPANIONS:
                if not features.get(companion, False):
                    errors.append(DeploymentError(
                        component="AppFeaturesValidator",
                        problem=(
                            f"t3_sandbox_enabled is true but {companion} is false: "
                            "the audit requires comparison, sessions and export"
                        ),
                        location=_where("t3_sandbox_enabled", companion),
                        fix=(
                            f"Set {companion}: true, or set t3_sandbox_enabled: false. "
                            "Both flags must agree."
                        ),
                        who="operator",
                        reference=".claude/rules/rules_app_features_flags.md (Rule 6) + D-0018",
                        related=("t3_sandbox_enabled", companion),
                    ))
        if features.get("comparison_mode_enabled", False) and not features.get("t3_sandbox_enabled", False):
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=(
                    "comparison_mode_enabled is true but t3_sandbox_enabled is false: "
                    "comparison requires the audit"
                ),
                location=_where("comparison_mode_enabled", "t3_sandbox_enabled"),
                fix=(
                    "Set t3_sandbox_enabled: true (with session_management_enabled and "
                    "export_enabled), or set comparison_mode_enabled: false. Both flags must agree."
                ),
                who="operator",
                reference=".claude/rules/rules_app_features_flags.md (Rule 6) + D-0018",
                related=("comparison_mode_enabled", "t3_sandbox_enabled"),
            ))

        # Rule 5: child flags must not be True when their master gate is False
        # (Soft cascade — bootloader will silently suppress at runtime; warn so operator knows.)
        # A flag that a fatal rule below already names is not warned about as well: the output says one thing (D-0018).
        fatal_flags = {f for e in errors for f in e.related}
        for master, children in _CASCADE_GATES.items():
            if not features.get(master, False):
                for child in children:
                    if features.get(child, False) and child not in fatal_flags:
                        warnings.append(
                            f"'{child}=True' has no effect — '{master}=False' "
                            f"(bootloader cascade will suppress it at runtime). Fix the template."
                        )

        # Rule 7: Group D FATAL cascades — child must NOT be True while master is False.
        # No silent suppression (ADR-077). YAML state and runtime state must match.
        for master, children in _FATAL_CASCADE_GATES.items():
            if not features.get(master, False):
                for child in children:
                    if features.get(child, False):
                        errors.append(DeploymentError(
                            component="AppFeaturesValidator",
                            problem=f"'{child}=True' requires '{master}=True'",
                            location=f"features.{child} in {template_path}",
                            fix=(
                                f"Edit the template — either set '{child}: false' "
                                f"(simplest), or set '{master}: true' if you intend to "
                                f"give this app features access to the parent feature. "
                                f"Both flags must agree."
                            ),
                            who="operator",
                            reference=(
                                ".claude/rules/rules_app_features_flags.md "
                                "§Cascade-D (Rules 4–5) + ADR-076 §6 + ADR-077"
                            ),
                            related=(master,),
                        ))

        # Print warnings (non-fatal)
        for w in warnings:
            print(f"[AppFeaturesValidator] WARNING: {w}")

        return errors

    def validate_file(self, template_path: str,
                      flag_overrides: Optional[dict] = None) -> list[DeploymentError]:
        """Load YAML file and validate. Returns DeploymentError list.

        flag_overrides: the deployment's app_features_override block (see validate()).

        Supports !include in app features files (paths relative to the template file).
        Uses a SafeLoader subclass to avoid polluting the global constructor registry.
        """
        path = Path(template_path)
        if not path.exists():
            return [DeploymentError(
                component="AppFeaturesValidator",
                problem="App features file file not found",
                location=template_path,
                fix=(
                    "Set SPARMVET_APP_FEATURES to an existing template id "
                    "(e.g. 'developer', 'pipeline-static') OR provide an absolute "
                    "path to your custom template file. Available built-in templates "
                    "live under config/app_features/."
                ),
                who="operator",
                reference=".claude/rules/rules_app_features_flags.md (app features resolution)",
            )]
        try:
            class _Loader(yaml.SafeLoader):
                pass

            def _include(loader: yaml.SafeLoader, node: yaml.Node):
                rel = loader.construct_scalar(node)
                abs_path = path.parent / rel
                try:
                    with open(abs_path) as inc_f:
                        return yaml.safe_load(inc_f) or {}
                except FileNotFoundError:
                    return {}

            _Loader.add_constructor("!include", _include)
            with open(path) as f:
                template = yaml.load(f, Loader=_Loader) or {}
        except Exception as e:
            return [DeploymentError(
                component="AppFeaturesValidator",
                problem=f"Failed to parse app features file YAML: {type(e).__name__}",
                location=template_path,
                fix=(
                    "The file is not valid YAML. Check for: tab vs space indentation, "
                    "unquoted special characters (':', '#', '@'), missing colons after "
                    "keys, mismatched brackets. Try `python -c 'import yaml; "
                    f"yaml.safe_load(open(\"{template_path}\"))'` to see the parse error.\n"
                    f"Original error: {e}"
                ),
                who="operator",
                reference=".claude/rules/rules_app_features_flags.md",
            )]
        return self.validate(template, template_path, flag_overrides)
