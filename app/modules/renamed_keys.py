"""Names that were renamed by the configuration rename (ADR-091) and must fail loudly.

Why: an old launch variable or an old key must not work silently (ADR-077, ADR-088) and
must not be ignored silently either: the operator gets a message that names the new one.
Pure module: no Shiny, no I/O. Used by the bootloader at startup and by the validators.
"""
from app.modules.deployment_error import DeploymentError

# old environment variable -> new environment variable (None: removed, no replacement)
RENAMED_ENV_VARS = {
    "SPARMVET_PERSONA": "SPARMVET_APP_FEATURES",
    "SPARMVET_PROFILE": "SPARMVET_DEPLOYMENT",
    "SPARMVET_CONNECTOR": None,
}

# keys of a deployment file: old -> new
RENAMED_DEPLOYMENT_KEYS = {
    "default_persona": "default_app_features",
    "prefer_discovery": "data_lookup (by_dataset_id or manifest_paths)",
    "data_ingestion_enabled": "app_features_override: {data_ingestion_enabled: ...}",
}

# keys of the locations block of a deployment file: old -> new
RENAMED_LOCATION_KEYS = {
    "curated_data": "cache",
    "user_sessions": "user_data",
}

# top-level keys of an app features file: old -> new
RENAMED_APP_FEATURES_KEYS = {
    "persona_id": "name",
    "features": "flags",
}

# keys inside the flags block of an app features file: old -> new
RENAMED_FLAG_KEYS = {
    "show_persona_badge": "show_app_features_badge",
}

_REF = "ADR-091 (configuration rename), issue evezeyl/SPARMVET_VIZ#27"


def renamed_env_var_errors(environ) -> list[DeploymentError]:
    errors = []
    for old, new in RENAMED_ENV_VARS.items():
        if not environ.get(old):
            continue
        if new is None:
            problem = f"The environment variable {old} was removed."
            fix = (f"Unset {old}. The development fallback is config/deployment/local/local.yaml; "
                   "to use another deployment file set SPARMVET_DEPLOYMENT.")
        else:
            problem = f"The environment variable {old} was renamed to {new}."
            fix = f"Set {new} with the same value and unset {old}."
        errors.append(DeploymentError(
            component="Bootloader", problem=problem,
            location=f"{old} is set in the environment", fix=fix,
            who="operator", reference=_REF,
        ))
    return errors


def renamed_deployment_key_errors(config: dict, where: str) -> list[DeploymentError]:
    return [
        DeploymentError(
            component="Bootloader",
            problem=f"The deployment key '{old}' was renamed to '{new}'.",
            location=f"{old} in {where}",
            fix=f"Rename the key '{old}' to '{new}' in {where}.",
            who="operator",
            reference=_REF,
        )
        for old, new in RENAMED_DEPLOYMENT_KEYS.items()
        if old in config
    ] + [
        DeploymentError(
            component="Bootloader",
            problem=f"The location '{old}' was renamed to '{new}'.",
            location=f"locations.{old} in {where}",
            fix=f"Rename the location '{old}' to '{new}' in {where}.",
            who="operator",
            reference=_REF,
        )
        for old, new in RENAMED_LOCATION_KEYS.items()
        if old in (config.get("locations") or {})
    ]


def renamed_app_features_key_errors(config: dict, where: str) -> list[DeploymentError]:
    errors = []
    for old, new in RENAMED_APP_FEATURES_KEYS.items():
        if old in config:
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=f"The app features key '{old}' was renamed to '{new}'.",
                location=f"{old} in {where}",
                fix=f"Rename the key '{old}' to '{new}' in {where}.",
                who="operator",
                reference=_REF,
            ))
    flags = config.get("flags", config.get("features", {})) or {}
    for old, new in RENAMED_FLAG_KEYS.items():
        if old in flags:
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=f"The flag '{old}' was renamed to '{new}'.",
                location=f"{old} in {where}",
                fix=f"Rename the flag '{old}' to '{new}' in {where}.",
                who="operator",
                reference=_REF,
            ))
    return errors
