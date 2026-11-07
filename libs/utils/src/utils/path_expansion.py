"""Expand ~ and ${VAR} in the paths of a deployment file (ADR-091).

Why: a deployment file shared by several people or machines names their folders with
~ or ${HOME}. Python leaves an unset ${VAR} in the text, so without a check a typo would
become a folder called "${HOMEE}"; here an unresolved reference is an error that names it.
Pure module: stdlib and DeploymentError only.
"""
import os
import re

from utils.deployment_error import DeploymentError

_LEFTOVER = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?|\$\{[^}]*\}?")
# Keys of a deployment file that hold file system paths: (top-level key, optional sub-key)
PATH_KEYS = (("project_root", None), ("locations", "*"), ("irida", "local_cache"),
             ("runtime", "python_interpreter"), ("branding", "theme_css"))


def expand_path(value: str) -> tuple[str, list[str]]:
    """Return (expanded text, names of the variables that could not be resolved)."""
    out = os.path.expandvars(os.path.expanduser(value))
    return out, [m.group(1) or m.group(0) for m in _LEFTOVER.finditer(out)]


def expand_deployment_paths(config: dict, where: str) -> list[DeploymentError]:
    """Expand the path values of a deployment dict in place; return one error per problem."""
    errors: list[DeploymentError] = []

    def one(container: dict, key: str, label: str):
        value = container.get(key)
        if not isinstance(value, str):
            return
        new, missing = expand_path(value)
        if missing:
            errors.append(DeploymentError(
                component="Bootloader",
                problem=f"{label} uses the variable(s) {', '.join(sorted(set(missing)))}, which are not set.",
                location=f"{label} in {where}",
                fix="Set the variable before starting the app, or write the path without it.",
                who="operator",
                reference="ADR-091 (configuration rename), issue evezeyl/SPARMVET_VIZ#27",
            ))
        else:
            container[key] = new

    for top, sub in PATH_KEYS:
        node = config.get(top)
        if sub is None:
            one(config, top, top)
        elif isinstance(node, dict):
            for key in (list(node) if sub == "*" else [sub]):
                one(node, key, f"{top}.{key}")
    return errors
