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
    "default_manifest": "default_data_analysis_recipe",
    "prefer_discovery": "data_lookup (by_dataset_id or data_analysis_recipe_paths)",
    "data_ingestion_enabled": "app_features_override: {data_ingestion_enabled: ...}",
}

# keys removed from a deployment file: old -> what to know now (names pass, D-0479)
REMOVED_DEPLOYMENT_KEYS = {
    "deployment_name": "a deployment has no name key; the banner's ui_label is what the user sees. A description of the file may be written "
                       "as a comment at the top of it",
}

# keys of the banner block (branding.banner) of a deployment file: old -> new (D-0411)
RENAMED_BANNER_KEYS = {
    "title": "ui_label",
    "subtitle": "description",
}

# keys of the locations block of a deployment file: old -> new
RENAMED_LOCATION_KEYS = {
    "curated_data": "cache",
    "user_sessions": "user_data",
    "manifests": "data_analysis_recipes",
}

# top-level keys of an app features file: old -> new
RENAMED_APP_FEATURES_KEYS = {
    "display_name": "ui_label",
    "features": "flags",
    "manifest_selector": "data_analysis_recipe_selector",
    "theme_css": "branding.theme_css in the deployment file",
    "ui_banner": "branding.banner in the deployment file",
}

# top-level keys removed from an app features file: old -> what to know now (names pass, D-0411, D-0481)
REMOVED_APP_FEATURES_KEYS = {
    "name": "the id of an app features file is its file name; write ui_label for the name shown to the user",
    "persona_id": "the id of an app features file is its file name; write ui_label for the name shown to the user",
    "ui_title": "the banner of a recipe is its info.ui_label; to hide it write show_recipe_name: false in the branding block of the deployment file",
}

# keys inside the flags block of an app features file: old -> new
RENAMED_FLAG_KEYS = {
    "show_persona_badge": "show_app_features_badge",
    "manifest_edit_enabled": "data_analysis_recipe_edit_enabled",
}

# flags that were retired: old -> what to use now (no silent alias, ADR-077)
RETIRED_FLAG_KEYS = {
    "wrangle_studio_enabled": "blueprint_enabled (it now controls the Blueprint Architect tab, its panels and its state)",
    "developer_mode_enabled": "blueprint_enabled for the Blueprint Architect and test_lab_enabled for the Test Lab",
}

# names of shipped app features files: old -> new
RENAMED_APP_FEATURES_NAMES = {
    "project-independent": "standalone",
}

# panel types in the sidebar slot lists of an app features file: old -> new
RENAMED_PANEL_TYPES = {
    "project_info": "data_analysis_recipe_info",
}

# keys written into saved sessions (assembly.json, t3_*.json): old -> new
RENAMED_SESSION_KEYS = {
    "manifest_id": "data_analysis_recipe_id",
    "manifest_sha256": "data_analysis_recipe_sha256",
    "t3_recipe": "t3_audit_steps",
    "t3_recipe_by_plot": "t3_audit_steps_by_plot",
    "t3_recipe_sha256": "t3_audit_steps_sha256",
}

MIGRATION_HINT = "python assets/scripts/migrate_config_vocabulary.py"

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
            problem=f"The deployment key '{old}' was removed: {why}.",
            location=f"{old} in {where}",
            fix=f"Delete the key '{old}' from {where}.",
            who="operator",
            reference=_REF,
        )
        for old, why in REMOVED_DEPLOYMENT_KEYS.items()
        if old in config
    ] + [
        DeploymentError(
            component="Bootloader",
            problem=f"The banner key '{old}' was renamed to '{new}'.",
            location=f"branding.banner.{old} in {where}",
            fix=f"Rename the key '{old}' to '{new}' in the banner block of {where}.",
            who="operator",
            reference=_REF,
        )
        for old, new in RENAMED_BANNER_KEYS.items()
        if old in ((config.get("branding") or {}).get("banner") or {})
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
    for old, why in REMOVED_APP_FEATURES_KEYS.items():
        if old in config:
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=f"The app features key '{old}' was removed: {why}.",
                location=f"{old} in {where}",
                fix=f"Delete the key '{old}' from {where}.",
                who="operator",
                reference=_REF,
            ))
    selector = config.get("data_analysis_recipe_selector") or {}
    for old in ("fixed_data_analysis_recipe", "fixed_manifest"):
        if old in selector:
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=f"The key '{old}' no longer exists: an app features file names no recipe.",
                location=f"data_analysis_recipe_selector.{old} in {where}",
                fix="Delete it and set default_data_analysis_recipe in the deployment file "
                    "(or SPARMVET_DATA_ANALYSIS_RECIPE for one run).",
                who="operator", reference=_REF,
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
    for old, use in RETIRED_FLAG_KEYS.items():
        if old in flags:
            errors.append(DeploymentError(
                component="AppFeaturesValidator",
                problem=f"The flag '{old}' was retired; it is read by nothing any more.",
                location=f"{old} in {where}",
                fix=f"Delete '{old}' from {where}. Use {use}.",
                who="operator",
                reference=_REF,
            ))
    return errors


def legacy_session_problem(raw: dict, where: str) -> str | None:
    """A message naming the fix when a stored session uses keys from before the rename, else None."""
    old = [k for k in RENAMED_SESSION_KEYS if k in raw]
    if not old:
        return None
    pairs = ", ".join(f"'{k}' is now '{RENAMED_SESSION_KEYS[k]}'" for k in old)
    return (f"{where} was saved before the configuration rename ({pairs}). "
            f"Convert it with: {MIGRATION_HINT} --sessions <sessions folder> --apply, or delete it.")


# Audit steps. A step the app cannot apply is refused with a plain message and never skipped in silence (Eve, 2026-11-15; PLOT-TABLE-ORDER-1).
# Refused: a type that is not known, a type that was removed (AUDIT-RAWYAML-REMOVE-1, Eve 2026-11-12, removed 2026-11-15; nothing creates it
# any more; the tombstone expires with Phase 40) and a step that lacks what it needs to run. One rule for the audit list, a stored session
# file, an imported session zip and the audit record of an imported bundle; `active` does not matter (nothing creates an inactive step today).
# `random_seed` is the seed pin the export adds to its audit record; it is known, and it is not a data step.
KNOWN_AUDIT_STEP_TYPES = ("filter_row", "exclusion_row", "drop_column", "aesthetic_override", "random_seed")
REMOVED_AUDIT_STEP_TYPES = {
    "developer_raw_yaml": "it held a raw fragment of a recipe, and no screen created it any more",
}
_STEP_NEEDS = {"filter_row": ("column", "op", "value"), "exclusion_row": ("column", "op", "value"), "drop_column": ("column",)}
_NEEDS_WORDS = {"column": "the column", "op": "the operator", "value": "the value"}

# What the user can do in the app (first); a maintainer's pointer to the file comes after it.
FIX_IN_APP = "start a new session from the recipe and record the filter or the column removal again with the filter dialog"


def audit_step_defect(step, type_key: str = "node_type", flat: bool = False) -> str | None:
    """Why the app cannot apply this audit step, in a few words, or None when it can.

    `type_key` is `node_type` in a session file and in the audit list and `action` in the `t3_steps.yaml` of a bundle, where the
    parameters sit in the step itself (`flat`).
    """
    if not isinstance(step, dict):
        return "it is not a step (a mapping with a type and parameters)"
    kind = step.get(type_key)
    if kind in REMOVED_AUDIT_STEP_TYPES:
        return f"it has the type '{kind}', which was removed: {REMOVED_AUDIT_STEP_TYPES[kind]}"
    if kind not in KNOWN_AUDIT_STEP_TYPES:
        return f"it has the type {kind!r}, which this app does not know, so it cannot be applied"
    params = step if flat else (step.get("params") or {})
    missing = [k for k in _STEP_NEEDS.get(kind, ()) if params.get(k) is None or params.get(k) == ""]
    if missing:
        return f"a {kind} step needs {' and '.join(_NEEDS_WORDS[k] for k in missing)} and it has none, so it cannot be applied"
    return None


def refused_audit_step_problem(steps_by_plot: dict, where: str, type_key: str = "node_type", flat: bool = False) -> str | None:
    """A message naming the first audit step of `{plot: [step, ...]}` that the app cannot apply, else None.

    The user's action in the app comes first; the pointer for a maintainer (where the step is in the file) after it.
    """
    for plot, steps in (steps_by_plot or {}).items():
        number = 0
        for step in steps or []:
            if isinstance(step, dict) and step.get(type_key) in ("aesthetic_override", "random_seed"):
                continue
            number += 1
            defect = audit_step_defect(step, type_key, flat)
            if defect:
                reason = f', reason: "{step["reason"]}"' if isinstance(step, dict) and step.get("reason") else ""
                ident = f"id {step.get('id', '?')}" if isinstance(step, dict) and step.get("id") else "no id"
                return (f"{where} cannot be read: the audit step {number} of the plot '{plot}' ({ident}{reason}) is refused, {defect}. "
                        f"The file is refused as a whole, nothing of it is used. Fix: {FIX_IN_APP}. For a maintainer: the step is "
                        f"entry {number} of the list of the plot '{plot}' in `t3_audit_steps_by_plot` (the step list of the file); "
                        f"taking that entry out makes the file readable again.")
    return None


def refused_audit_step_in_ghost(raw: dict, where: str) -> str | None:
    """`refused_audit_step_problem` for a stored session file: the per-plot lists and the flat legacy list."""
    by_plot = raw.get("t3_audit_steps_by_plot")
    if isinstance(by_plot, dict) and by_plot:
        problem = refused_audit_step_problem(by_plot, where)
        if problem:
            return problem
    flat = raw.get("t3_audit_steps")
    return refused_audit_step_problem({"(all plots, old file)": flat}, where) if isinstance(flat, list) else None
