"""
@deps
provides: class:PersonaValidator
consumes: config/ui/templates/*.yaml
consumed_by: app/src/server.py
"""
from pathlib import Path
from typing import Optional
import yaml

# All feature flags that every template must declare
_REQUIRED_FLAGS = [
    "interactivity_enabled",
    "t3_sandbox_enabled",
    "developer_mode_enabled",
    "gallery_enabled",
    "blueprint_enabled",
    "test_lab_enabled",
    "comparison_mode_enabled",
    "session_management_enabled",
    "import_helper_enabled",
    "export_enabled",
    "audit_report_enabled",
    "metadata_ingestion_enabled",
    "data_ingestion_enabled",
]

# Child flags that require their master gate to be True (cascade rules)
_CASCADE_GATES: dict[str, list[str]] = {
    "interactivity_enabled": [
        "t3_sandbox_enabled",
        "comparison_mode_enabled",
        "session_management_enabled",
        "audit_report_enabled",
    ],
    "import_helper_enabled": ["data_ingestion_enabled"],
}


class PersonaValidator:
    """Validates persona template completeness at startup.

    Call validate() before define_server(). Errors are fatal; warnings are logged.
    """

    def validate(self, template: dict, template_path: str) -> list[str]:
        """Return a list of error strings. Empty list means template is valid."""
        errors: list[str] = []
        warnings: list[str] = []

        persona_id = template.get("persona_id", "")

        # Rule 1 (removed 2026-05-02, ADR-054): persona_id must match filename.
        # Removed because persona config files can now be placed anywhere and referenced
        # by absolute path via SPARMVET_PERSONA — filename is no longer coupled to persona_id.

        # Rule 2: persona_id must use hyphens, never underscores
        if "_" in persona_id and persona_id not in (""):
            errors.append(
                f"persona_id '{persona_id}' contains underscores — use hyphens only"
            )

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
        # (Bootloader cascade will suppress them at runtime, but the template itself is misconfigured)
        for master, children in _CASCADE_GATES.items():
            if not features.get(master, False):
                for child in children:
                    if features.get(child, False):
                        warnings.append(
                            f"'{child}=True' has no effect — '{master}=False' "
                            f"(bootloader cascade will suppress it at runtime). Fix the template."
                        )

        # Rule 6: T3 cascade — if t3_sandbox_enabled then its co-flags must ALL be true.
        # These are not parent→child gates (T3 doesn't imply them), but required companions.
        # A misconfigured template where T3 is on but session/comparison/export are off would
        # produce a broken UX (audit nodes but nowhere to save, no scope for export).
        _T3_COMPANIONS = [
            "comparison_mode_enabled",
            "audit_report_enabled",
            "session_management_enabled",
            "export_enabled",
        ]
        if features.get("t3_sandbox_enabled", False):
            missing = [f for f in _T3_COMPANIONS if not features.get(f, False)]
            if missing:
                errors.append(
                    f"t3_sandbox_enabled=True requires these flags to also be True: "
                    f"{', '.join(missing)}. "
                    f"Fix the template or set t3_sandbox_enabled: false."
                )

        # Print warnings (non-fatal)
        for w in warnings:
            print(f"[PersonaValidator] WARNING: {w}")

        return errors

    def validate_file(self, template_path: str) -> list[str]:
        """Load YAML file and validate. Returns error list."""
        path = Path(template_path)
        if not path.exists():
            return [f"Template file not found: {template_path}"]
        try:
            with open(path) as f:
                template = yaml.safe_load(f) or {}
        except Exception as e:
            return [f"Failed to parse template '{template_path}': {e}"]
        return self.validate(template, template_path)
