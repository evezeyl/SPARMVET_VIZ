"""group_plot_manager.py
Pure CRUD for analysis_groups in SPARMVET manifests.

Headless — no Shiny imports. All functions take a manifest_path string and
operate directly on the YAML file, preserving !include directives via the
_IncludeLoader/_IncludeDumper pattern (mirrors migrate_plot_specs.py).

Decoupled from the sidebar UI (ADR-082 Q6) so the v2 TubeMap context menu
is a purely additive affordance over the same functions, with no refactor.
"""

# @deps
# provides: func:list_groups_plots, func:create_group, func:delete_group,
#           func:create_plot, func:delete_plot, func:assign_plot,
#           class:_IncludeTag (re-exported for tests)
# consumes: yaml, pathlib, re
# consumed_by: app/handlers/blueprint_handlers.py (bp_groups_inventory_ui + CRUD Effects — BP-GROUPS-1)
# doc: .claude/knowledge/architecture_decisions.md#ADR-082
# @end_deps

import re
from pathlib import Path

import yaml


# ── !include round-trip support ───────────────────────────────────────────

class _IncludeTag:
    """Opaque wrapper for a YAML !include directive — preserved verbatim on round-trip."""
    __slots__ = ("path",)

    def __init__(self, path: str) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"!include {self.path}"


class _IncludeLoader(yaml.SafeLoader):
    pass


_IncludeLoader.add_constructor(
    "!include",
    lambda loader, node: _IncludeTag(loader.construct_scalar(node)),
)


class _IncludeDumper(yaml.Dumper):
    pass


_IncludeDumper.add_representer(
    _IncludeTag,
    lambda dumper, tag: dumper.represent_scalar("!include", tag.path),
)


# ── Internal helpers ──────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_id(value: str) -> str | None:
    """Return an error string if value is not a valid snake_case slug, else None."""
    if not value or not _SLUG_RE.match(value):
        return ("ID must be snake_case: letters/digits/underscores, "
                "start with letter or underscore.")
    return None


def _load(manifest_path: str) -> dict:
    with open(manifest_path, encoding="utf-8") as f:
        return yaml.load(f, Loader=_IncludeLoader) or {}


def _save(manifest_path: str, raw: dict) -> None:
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, Dumper=_IncludeDumper,
                  default_flow_style=False, sort_keys=False, allow_unicode=True)


# ── Public API ────────────────────────────────────────────────────────────

def list_groups_plots(manifest_path: str) -> dict:
    """Return the analysis_groups dict from the manifest.

    spec values are _IncludeTag objects when declared via !include, or dicts
    when inline. Callers handle both forms.
    """
    return _load(manifest_path).get("analysis_groups", {})


def create_group(manifest_path: str, group_id: str, label: str) -> tuple[bool, str]:
    """Add a new empty group to analysis_groups. Returns (success, message)."""
    err = _validate_id(group_id)
    if err:
        return False, err
    raw = _load(manifest_path)
    ag = raw.setdefault("analysis_groups", {})
    if group_id in ag:
        return False, f"Group '{group_id}' already exists."
    ag[group_id] = {"label": label.strip() or group_id, "plots": {}}
    _save(manifest_path, raw)
    return True, f"Group '{group_id}' created."


def delete_group(manifest_path: str, group_id: str) -> tuple[bool, str]:
    """Delete a group. Fails if it still has plots (prevents accidental loss).

    Returns (success, message).
    """
    raw = _load(manifest_path)
    ag = raw.get("analysis_groups", {})
    if group_id not in ag:
        return False, f"Group '{group_id}' not found."
    n = len(ag[group_id].get("plots", {}))
    if n:
        return False, f"Remove all {n} plot(s) from '{group_id}' before deleting the group."
    del ag[group_id]
    _save(manifest_path, raw)
    return True, f"Group '{group_id}' deleted."


def create_plot(manifest_path: str, group_id: str,
                plot_id: str, label: str) -> tuple[bool, str]:
    """Add a plot stub to a group and create its spec file.

    Writes a minimal spec stub to {manifest_dir}/{manifest_stem}/plots/{plot_id}.yaml
    and registers a !include reference in the master manifest.
    Returns (success, message).
    """
    err = _validate_id(plot_id)
    if err:
        return False, err
    raw = _load(manifest_path)
    ag = raw.get("analysis_groups", {})
    if group_id not in ag:
        return False, f"Group '{group_id}' not found."
    grp_plots = ag[group_id].setdefault("plots", {})
    if plot_id in grp_plots:
        return False, f"Plot '{plot_id}' already exists in group '{group_id}'."

    # Create stub spec file (only if absent — never overwrite existing work).
    stem = Path(manifest_path).stem
    spec_dir = Path(manifest_path).parent / stem / "plots"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_file = spec_dir / f"{plot_id}.yaml"
    if not spec_file.exists():
        stub = {"spec": {"target_dataset": "", "mapping": {}, "layers": []}}
        with open(spec_file, "w", encoding="utf-8") as f:
            yaml.dump(stub, f, default_flow_style=False, sort_keys=False)

    rel = f"{stem}/plots/{plot_id}.yaml"
    grp_plots[plot_id] = {"label": label.strip() or plot_id, "spec": _IncludeTag(rel)}
    _save(manifest_path, raw)
    return True, f"Plot '{plot_id}' created in group '{group_id}'."


def delete_plot(manifest_path: str, group_id: str, plot_id: str) -> tuple[bool, str]:
    """Remove a plot entry from a group. Does NOT delete the spec file.

    Returns (success, message).
    """
    raw = _load(manifest_path)
    ag = raw.get("analysis_groups", {})
    if group_id not in ag:
        return False, f"Group '{group_id}' not found."
    plots = ag[group_id].get("plots", {})
    if plot_id not in plots:
        return False, f"Plot '{plot_id}' not found in group '{group_id}'."
    del plots[plot_id]
    _save(manifest_path, raw)
    return True, f"Plot '{plot_id}' removed from group '{group_id}'."


def assign_plot(manifest_path: str, plot_id: str,
                from_group: str, to_group: str) -> tuple[bool, str]:
    """Move a plot from one group to another. Returns (success, message)."""
    if from_group == to_group:
        return False, "Source and target group are the same."
    raw = _load(manifest_path)
    ag = raw.get("analysis_groups", {})
    if from_group not in ag:
        return False, f"Source group '{from_group}' not found."
    if to_group not in ag:
        return False, f"Target group '{to_group}' not found."
    src = ag[from_group].get("plots", {})
    if plot_id not in src:
        return False, f"Plot '{plot_id}' not found in group '{from_group}'."
    tgt = ag[to_group].setdefault("plots", {})
    if plot_id in tgt:
        return False, f"Plot '{plot_id}' already exists in group '{to_group}'."
    tgt[plot_id] = src.pop(plot_id)
    _save(manifest_path, raw)
    return True, f"Plot '{plot_id}' moved from '{from_group}' to '{to_group}'."
