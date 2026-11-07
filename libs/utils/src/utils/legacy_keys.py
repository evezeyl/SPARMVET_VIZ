"""Keys of a data analysis recipe file that were renamed by the configuration rename (ADR-091).

Why: an old recipe must stop with a message that names the new key, never load silently
wrong. Pure module (stdlib and DeploymentError only), used by ConfigManager.
"""
from utils.deployment_error import DeploymentError

# top-level key of a data analysis recipe file, and the key of a join's step list: old -> new
RENAMED_RECIPE_FILE_KEYS = {"join_manifests": "joins"}
RENAMED_JOIN_KEYS = {"recipe": "steps"}

# top-level keys that no code reads any more and that are refused so that no old meaning survives
REMOVED_RECIPE_FILE_KEYS = {
    "type": "it came from the old species idea (species, project, pipeline, audit) and no code reads it; "
            "describe the data analysis recipe under 'info:' instead",
}

# file names of a gallery bundle before the rename: recipe file and text file
LEGACY_GALLERY_FILES = ("recipe_manifest.yaml", "recipe_meta.md")

MIGRATION_HINT = "python assets/scripts/migrate_config_vocabulary.py"
_REF = "ADR-091 (configuration rename), issue evezeyl/SPARMVET_VIZ#27"


def renamed_data_analysis_recipe_file_key_errors(raw: dict, where: str) -> list[DeploymentError]:
    errors = []
    for old, new in RENAMED_RECIPE_FILE_KEYS.items():
        if old in raw:
            errors.append(DeploymentError(
                component="ConfigManager",
                problem=f"The data analysis recipe key '{old}' was renamed to '{new}'.",
                location=f"{old} in {where}",
                fix=f"Rename '{old}' to '{new}', or convert the folder with: {MIGRATION_HINT} --recipes <folder> --apply",
                who="developer", reference=_REF,
            ))
    for old, why in REMOVED_RECIPE_FILE_KEYS.items():
        if old in raw:
            errors.append(DeploymentError(
                component="ConfigManager",
                problem=f"The data analysis recipe key '{old}' was removed: {why}.",
                location=f"{old} in {where}",
                fix=f"Delete the '{old}:' line, or convert the folder with: {MIGRATION_HINT} --recipes <folder> --apply",
                who="developer", reference=_REF,
            ))
    for section in ("joins", *RENAMED_RECIPE_FILE_KEYS):
        for name, spec in (raw.get(section) or {}).items():
            if isinstance(spec, dict):
                for old, new in RENAMED_JOIN_KEYS.items():
                    if old in spec:
                        errors.append(DeploymentError(
                            component="ConfigManager",
                            problem=f"The join key '{old}' was renamed to '{new}'.",
                            location=f"{section}.{name}.{old} in {where}",
                            fix=f"Rename '{old}' to '{new}', or convert the folder with: {MIGRATION_HINT} --recipes <folder> --apply",
                            who="developer", reference=_REF,
                        ))
    return errors
