"""
@deps
provides: class:PersonaValidator
consumes: config/ui/templates/*.yaml, app/modules/deployment_error.py
consumed_by: app/src/server.py
doc: .claude/knowledge/architecture_decisions.md#adr-077, #adr-078
"""
from pathlib import Path
from typing import Optional
import yaml

from app.modules.deployment_error import DeploymentError

# All feature flags that every template must declare
_REQUIRED_FLAGS = [
    "interactivity_enabled",
    "t3_sandbox_enabled",
    "wrangle_studio_enabled",
    "developer_mode_enabled",
    "gallery_enabled",
    "blueprint_enabled",
    "test_lab_enabled",
    "comparison_mode_enabled",
    "session_management_enabled",
    "import_helper_enabled",
    "export_enabled",
    "metadata_ingestion_enabled",
    "data_ingestion_enabled",
    "manifest_edit_enabled",
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
# (ADR-075 manifest_edit_enabled, ADR-076 blueprint_agent_enabled.)
_FATAL_CASCADE_GATES: dict[str, list[str]] = {
    "blueprint_enabled": [
        "manifest_edit_enabled",
        "blueprint_agent_enabled",
    ],
}


class PersonaValidator:
    """Validates persona template completeness at startup.

    Call validate() before define_server(). Errors are fatal; warnings are logged.
    """

    def validate(self, template: dict, template_path: str) -> list[DeploymentError]:
        """Return a list of DeploymentError records. Empty list means template is valid.

        Errors carry full operator-facing context (component, problem, location,
        fix, who, reference). Warnings are still printed inline for missing-flag
        and soft-cascade cases — they do not block startup.
        """
        errors: list[DeploymentError] = []
        warnings: list[str] = []

        persona_id = template.get("persona_id", "")

        # Rule 1 (removed 2026-05-02, ADR-054): persona_id must match filename.

        # Rule 2: persona_id must use hyphens, never underscores
        if "_" in persona_id and persona_id not in (""):
            errors.append(DeploymentError(
                component="PersonaValidator",
                problem=f"persona_id '{persona_id}' contains underscores",
                location=f"persona_id in {template_path}",
                fix="Replace underscores with hyphens. e.g. 'pipeline_static' → 'pipeline-static'.",
                who="operator",
                reference=".claude/rules/rules_persona_feature_flags.md (persona naming)",
            ))

        features = template.get("features", {})

        # Rule 3: all required feature flags must be present (warn if missing, use defaults)
        for flag in _REQUIRED_FLAGS:
            if flag not in features:
                warnings.append(
                    f"Feature flag '{flag}' missing from template '{template_path}' — defaulting to False"
                )

        # Rule 4: manifest_selector.visible=false → fixed_manifest should be non-null in production
        ms = template.get("manifest_selector", {})
        if ms.get("visible") is False:
            if not ms.get("fixed_manifest"):
                # Warning only: null is the dev/template default; operators fill this at deployment
                warnings.append(
                    f"manifest_selector.visible=false in '{template_path}' "
                    f"but fixed_manifest is null — operator must set a fixed_manifest path before deploying"
                )

        # Rule 5: child flags must not be True when their master gate is False
        # (Soft cascade — bootloader will silently suppress at runtime; warn so operator knows.)
        for master, children in _CASCADE_GATES.items():
            if not features.get(master, False):
                for child in children:
                    if features.get(child, False):
                        warnings.append(
                            f"'{child}=True' has no effect — '{master}=False' "
                            f"(bootloader cascade will suppress it at runtime). Fix the template."
                        )

        # Rule 6: T3 cascade — if t3_sandbox_enabled then its co-flags must ALL be true.
        _T3_COMPANIONS = [
            "comparison_mode_enabled",
            "session_management_enabled",
            "export_enabled",
        ]
        if features.get("t3_sandbox_enabled", False):
            missing = [f for f in _T3_COMPANIONS if not features.get(f, False)]
            if missing:
                errors.append(DeploymentError(
                    component="PersonaValidator",
                    problem=(
                        "t3_sandbox_enabled=True but required companion flags are False: "
                        + ", ".join(missing)
                    ),
                    location=f"features in {template_path}",
                    fix=(
                        "Either set ALL of these to true: " + ", ".join(missing)
                        + " — or set t3_sandbox_enabled: false. "
                        "The T3 sandbox cannot function without comparison/audit/session/export."
                    ),
                    who="operator",
                    reference=".claude/rules/rules_persona_feature_flags.md §Cascade-T3 (Rule 6)",
                    related=tuple(missing),
                ))

        # Rule 7: Group D FATAL cascades — child must NOT be True while master is False.
        # No silent suppression (ADR-077). YAML state and runtime state must match.
        for master, children in _FATAL_CASCADE_GATES.items():
            if not features.get(master, False):
                for child in children:
                    if features.get(child, False):
                        errors.append(DeploymentError(
                            component="PersonaValidator",
                            problem=f"'{child}=True' requires '{master}=True'",
                            location=f"features.{child} in {template_path}",
                            fix=(
                                f"Edit the template — either set '{child}: false' "
                                f"(simplest), or set '{master}: true' if you intend to "
                                f"give this persona access to the parent feature. "
                                f"Both flags must agree."
                            ),
                            who="operator",
                            reference=(
                                ".claude/rules/rules_persona_feature_flags.md "
                                "§Cascade-D (Rules 4–5) + ADR-076 §6 + ADR-077"
                            ),
                            related=(master,),
                        ))

        # Print warnings (non-fatal)
        for w in warnings:
            print(f"[PersonaValidator] WARNING: {w}")

        return errors

    def validate_file(self, template_path: str) -> list[DeploymentError]:
        """Load YAML file and validate. Returns DeploymentError list.

        Supports !include in persona templates (paths relative to the template file).
        Uses a SafeLoader subclass to avoid polluting the global constructor registry.
        """
        path = Path(template_path)
        if not path.exists():
            return [DeploymentError(
                component="PersonaValidator",
                problem="Persona template file not found",
                location=template_path,
                fix=(
                    "Set SPARMVET_PERSONA to an existing template id "
                    "(e.g. 'developer', 'pipeline-static') OR provide an absolute "
                    "path to your custom template file. Available built-in templates "
                    "live under config/ui/templates/."
                ),
                who="operator",
                reference=".claude/rules/rules_persona_feature_flags.md (persona resolution)",
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
                component="PersonaValidator",
                problem=f"Failed to parse persona template YAML: {type(e).__name__}",
                location=template_path,
                fix=(
                    "The file is not valid YAML. Check for: tab vs space indentation, "
                    "unquoted special characters (':', '#', '@'), missing colons after "
                    "keys, mismatched brackets. Try `python -c 'import yaml; "
                    f"yaml.safe_load(open(\"{template_path}\"))'` to see the parse error.\n"
                    f"Original error: {e}"
                ),
                who="operator",
                reference=".claude/rules/rules_persona_feature_flags.md",
            )]
        return self.validate(template, template_path)
