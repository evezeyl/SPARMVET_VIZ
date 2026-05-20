"""
Migrate legacy plot specs to canonical grammar-of-graphics format.

Transforms:
  - factory_id  -> explicit geom_* layer (prepended to layers list)
  - flat aes    -> mapping: block
  - heatmap color -> fill in mapping

Rewrite rules match normalise_plot_spec in plot_config_resolver.py exactly,
so pre/post render equivalence is guaranteed by that function's tests.

Usage:
  # Dry run — show what would change, write nothing
  .venv/bin/python assets/scripts/migrate_plot_specs.py --dry-run

  # Apply migrations in-place
  .venv/bin/python assets/scripts/migrate_plot_specs.py --apply

  # Restrict to a specific directory
  .venv/bin/python assets/scripts/migrate_plot_specs.py --apply --root config/manifests/pipelines

  # Also scan tests/ fixtures
  .venv/bin/python assets/scripts/migrate_plot_specs.py --apply --scan-tests
"""

import argparse
import copy
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# !include passthrough — local Loader/Dumper subclass (mirrors persona_validator.py)
# ---------------------------------------------------------------------------

class _IncludeTag:
    """Represents a YAML !include directive. Preserved verbatim on round-trip."""
    __slots__ = ("path",)

    def __init__(self, path: str) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"!include {self.path}"


class _IncludeLoader(yaml.SafeLoader):
    pass


def _include_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> _IncludeTag:
    return _IncludeTag(loader.construct_scalar(node))


_IncludeLoader.add_constructor("!include", _include_constructor)


class _IncludeDumper(yaml.Dumper):
    pass


def _include_representer(dumper: yaml.Dumper, tag: _IncludeTag) -> yaml.Node:
    return dumper.represent_scalar("!include", tag.path)


_IncludeDumper.add_representer(_IncludeTag, _include_representer)


# ---------------------------------------------------------------------------
# Constants matching plot_config_resolver.py exactly
# ---------------------------------------------------------------------------

_FLAT_AESTHETIC_KEYS = ("x", "y", "color", "colour", "fill", "size", "alpha", "shape", "facet_by")

_FACTORY_GEOMS: dict[str, dict] = {
    "heatmap_logic":  {"name": "geom_tile",    "params": {"color": "white", "size": 0.1}},
    "bar_logic":      {"name": "geom_bar",      "params": {}},
    "scatter_logic":  {"name": "geom_point",    "params": {}},
    "boxplot_logic":  {"name": "geom_boxplot",  "params": {}},
    "violin_logic":   {"name": "geom_violin",   "params": {}},
}

_CANONICAL_TOP_KEYS = {
    "target_dataset", "mapping", "layers", "theme", "facet_by",
    "palette", "labels", "guides", "filters", "title", "factory_id",
    "_meta",
} | set(_FLAT_AESTHETIC_KEYS)


# ---------------------------------------------------------------------------
# Core migration logic (mirrors normalise_plot_spec, writes canonical)
# ---------------------------------------------------------------------------

def _migrate_spec(spec: dict) -> tuple[dict, list[str]]:
    """Migrate a single plot spec dict to canonical. Returns (new_spec, change_descriptions)."""
    spec = copy.deepcopy(spec)
    changes: list[str] = []

    # 1. Promote flat aesthetics to mapping
    if "mapping" not in spec:
        mapping = {k: spec[k] for k in _FLAT_AESTHETIC_KEYS if k in spec}
        if mapping:
            spec["mapping"] = mapping
            changes.append(f"promoted flat aes {list(mapping.keys())} -> mapping:")

    # 2. Expand factory_id -> base geom, apply special cases
    factory_id = spec.pop("factory_id", None)
    if factory_id:
        base_geom = copy.deepcopy(_FACTORY_GEOMS.get(factory_id))
        if base_geom:
            mapping = spec.get("mapping", {})

            # bar_logic: geom_col when y is mapped
            if factory_id == "bar_logic" and "y" in mapping:
                base_geom = {"name": "geom_col", "params": {}}

            # heatmap_logic: color -> fill in mapping
            if factory_id == "heatmap_logic" and "color" in mapping:
                spec["mapping"] = dict(mapping)
                spec["mapping"]["fill"] = spec["mapping"].pop("color")
                changes.append("heatmap: remapped color -> fill in mapping")

            existing_layers = spec.get("layers", [])
            existing_geoms = {layer.get("name") for layer in existing_layers}
            if base_geom["name"] not in existing_geoms:
                spec["layers"] = [base_geom] + existing_layers
                changes.append(f"factory_id:{factory_id} -> {base_geom['name']} layer prepended")
            else:
                changes.append(f"factory_id:{factory_id} removed (geom already present)")
        else:
            changes.append(f"factory_id:{factory_id} removed (unknown factory — no geom injected)")

    # 3. Remove flat aes keys that are now in mapping
    mapping = spec.get("mapping", {})
    for k in _FLAT_AESTHETIC_KEYS:
        if k in spec and k in mapping:
            del spec[k]

    return spec, changes


def _has_legacy(obj: object) -> bool:
    """Return True if obj (or any nested structure) has legacy factory_id or flat aes."""
    if isinstance(obj, _IncludeTag):
        return False  # included fragments are migrated separately as standalone files
    if isinstance(obj, dict):
        if "factory_id" in obj:
            return True
        if "mapping" not in obj and any(k in obj for k in _FLAT_AESTHETIC_KEYS):
            return True
        return any(_has_legacy(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_legacy(item) for item in obj)
    return False


def _is_plot_spec(d: dict) -> bool:
    """Heuristic: dict looks like a plot spec (has factory_id or target_dataset)."""
    return "factory_id" in d or "target_dataset" in d or "layers" in d


def _walk_and_migrate(obj: object) -> tuple[object, list[str]]:
    """
    Recursively walk a parsed YAML structure and migrate any inline plot spec dict.
    _IncludeTag objects are left untouched — their files are migrated separately.
    """
    all_changes: list[str] = []

    if isinstance(obj, _IncludeTag):
        return obj, []

    if isinstance(obj, dict):
        if (_is_plot_spec(obj) and
                ("factory_id" in obj or
                 ("mapping" not in obj and any(k in obj for k in _FLAT_AESTHETIC_KEYS)))):
            new_spec, changes = _migrate_spec(obj)
            return new_spec, changes

        new_obj = {}
        for k, v in obj.items():
            new_v, changes = _walk_and_migrate(v)
            new_obj[k] = new_v
            all_changes.extend(changes)
        return new_obj, all_changes

    if isinstance(obj, list):
        new_list = []
        for item in obj:
            new_item, changes = _walk_and_migrate(item)
            new_list.append(new_item)
            all_changes.extend(changes)
        return new_list, all_changes

    return obj, []


# ---------------------------------------------------------------------------
# File-level migration
# ---------------------------------------------------------------------------

def _migrate_file(path: Path, dry_run: bool) -> list[str]:
    """
    Migrate one YAML file. Handles bare spec dicts, spec:-wrapped dicts,
    and master manifests that contain !include tags alongside inline plot specs.
    _IncludeTag values are preserved verbatim — their target files are migrated
    separately when the scanner reaches them.
    Returns list of change descriptions (empty = no change).
    """
    raw = path.read_text(encoding="utf-8")

    try:
        doc = yaml.load(raw, Loader=_IncludeLoader)
    except yaml.YAMLError as exc:
        return [f"PARSE ERROR: {exc}"]

    if not isinstance(doc, dict):
        return []

    if not _has_legacy(doc):
        return []

    # Detect spec: wrapper (standalone plot spec files)
    if "spec" in doc and isinstance(doc.get("spec"), dict) and _is_plot_spec(doc["spec"]):
        old_spec = doc["spec"]
        new_spec, changes = _migrate_spec(old_spec)
        if not changes:
            return []
        new_doc = dict(doc)
        new_doc["spec"] = new_spec
    else:
        new_doc, changes = _walk_and_migrate(doc)
        if not changes:
            return []

    if not dry_run:
        dumped = yaml.dump(
            new_doc,
            Dumper=_IncludeDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(dumped)

    return changes


def _find_plot_yamls(roots: list[Path]) -> list[Path]:
    """Recursively find YAML files that may contain plot specs."""
    found: list[Path] = []
    for root in roots:
        if root.is_file():
            found.append(root)
        else:
            found.extend(sorted(root.rglob("*.yaml")))
    return found


# ---------------------------------------------------------------------------
# Generator patches
# ---------------------------------------------------------------------------

def _patch_create_manifest(path: Path, dry_run: bool) -> list[str]:
    """Patch create_manifest.py: replace factory_id stub with canonical geom form."""
    text = path.read_text(encoding="utf-8")
    old = '''\
                "demo_bar": {
                    "factory_id": "bar_logic",
                    "target_dataset": first_dataset_key,  # Dynamic explicit dataset target
                    "target_col": "Replace_Me",
                    "title": "Replace Me Title"
                }'''
    new = '''\
                "demo_bar": {
                    "target_dataset": first_dataset_key,
                    "mapping": {"x": "Replace_Me"},
                    "layers": [{"name": "geom_bar", "params": {}}],
                    "title": "Replace Me Title"
                }'''
    if old not in text:
        return ["WARNING: create_manifest.py patch target not found — manual review required"]
    if dry_run:
        return ["create_manifest.py:281 — factory_id:bar_logic -> canonical geom_bar stub (dry-run)"]
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return ["create_manifest.py:281 — factory_id:bar_logic -> canonical geom_bar stub"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing any files (default mode)."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Write changes to disk."
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="Root directory to scan for YAML files (default: config/manifests/)."
    )
    parser.add_argument(
        "--scan-tests", action="store_true",
        help="Also scan tests/ directory for legacy fixture YAML files."
    )
    parser.add_argument(
        "--skip-generators", action="store_true",
        help="Skip patching generator scripts (create_manifest.py)."
    )
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("NOTE: Dry-run mode. Pass --apply to write changes.\n")

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Build scan roots
    scan_roots: list[Path] = []
    if args.root:
        scan_roots.append(args.root)
    else:
        scan_roots.append(project_root / "config" / "manifests")

    if args.scan_tests:
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            scan_roots.append(tests_dir)

    yaml_files = _find_plot_yamls(scan_roots)

    total_changed = 0
    total_skipped = 0
    total_errors = 0

    for yaml_path in yaml_files:
        try:
            changes = _migrate_file(yaml_path, dry_run=dry_run)
        except Exception as exc:
            print(f"  ERROR {yaml_path.relative_to(project_root)}: {exc}")
            total_errors += 1
            continue

        if changes:
            has_error = any(c.startswith("PARSE ERROR") for c in changes)
            if has_error:
                total_errors += 1
                print(f"  ERROR {yaml_path.relative_to(project_root)}")
            else:
                total_changed += 1
                rel = yaml_path.relative_to(project_root)
                verb = "Would update" if dry_run else "Updated"
                print(f"  {verb}: {rel}")
            for c in changes:
                print(f"    - {c}")
        else:
            total_skipped += 1

    print(f"\nYAML files: {total_changed} changed, {total_skipped} already canonical"
          + (f", {total_errors} errors" if total_errors else "") + ".")

    # Patch generators
    if not args.skip_generators:
        create_manifest = project_root / "assets" / "scripts" / "create_manifest.py"
        if create_manifest.exists():
            gen_changes = _patch_create_manifest(create_manifest, dry_run=dry_run)
            if gen_changes:
                verb = "Would patch" if dry_run else "Patched"
                rel = create_manifest.relative_to(project_root)
                print(f"\nGenerators:")
                print(f"  {verb}: {rel}")
                for c in gen_changes:
                    print(f"    - {c}")

    if dry_run:
        print("\nDry run complete. Re-run with --apply to write changes.")
    else:
        print(
            "\nMigration complete. Verify render parity:"
            "\n  .venv/bin/python libs/viz_factory/tests/debug_gallery.py "
            "--manifest config/manifests/pipelines/2_test_data_ST22_dummy.yaml "
            "--tmp tmpAI/migrate_verify/ --output_root tmpAI/migrate_verify/plots/"
        )


if __name__ == "__main__":
    main()
