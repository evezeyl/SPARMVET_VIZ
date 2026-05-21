# @deps
# provides: class:ConfigManager, func:_normalise_yaml_boolean_keys
# consumes: utils.deployment_error
# consumed_by: app/modules/orchestrator.py, app/handlers/home_theater.py, app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-041, ADR-078, .claude/rules/rules_manifest_structure.md#7
# @end_deps

import yaml
import os
from pathlib import Path

from utils.deployment_error import DeploymentError, exit_if_errors

_REF = "ADR-041 + .claude/rules/rules_manifest_structure.md"


def _normalise_yaml_boolean_keys(config, manifest_path: str) -> None:
    """Recursively convert boolean True dict keys to the string 'on'.

    Unquoted 'on:' in YAML is parsed as Python True by SafeLoader (YAML boolean
    trap — rules_manifest_structure.md §7). This post-load walk catches the mistake,
    converts the key in place, and warns the manifest author. The DataAssembler has a
    step.get(True) fallback, but correcting the loaded dict here means every downstream
    consumer (assembler, navigator, join_designer) sees a structurally correct config
    without needing their own guards.
    """
    if isinstance(config, dict):
        if True in config:
            print(
                f"  [ConfigManager] WARNING: Unquoted 'on:' key found in manifest "
                f"(YAML boolean trap — always quote as '\"on\":'). "
                f"Auto-corrected for this load; fix the YAML source. "
                f"See rules_manifest_structure.md §7. ({manifest_path})"
            )
            config["on"] = config.pop(True)
        for v in list(config.values()):
            _normalise_yaml_boolean_keys(v, manifest_path)
    elif isinstance(config, list):
        for item in config:
            _normalise_yaml_boolean_keys(item, manifest_path)


class ConfigManager:
    def __init__(self, yaml_path):
        yaml_path = str(yaml_path)
        _include_errors: list[DeploymentError] = []

        def include_constructor(loader, node):
            included_file = loader.construct_scalar(node)
            filename = os.path.join(os.path.dirname(yaml_path), included_file)

            try:
                with open(filename, 'r') as f:
                    content = yaml.load(f, Loader=yaml.SafeLoader)
            except FileNotFoundError:
                _include_errors.append(DeploymentError(
                    component="ConfigManager",
                    problem=f"!include target not found: '{included_file}'",
                    location=f"{yaml_path} — !include {included_file}",
                    fix=(
                        f"Create the missing file at '{filename}' or correct the "
                        f"!include path. Verify the basename mirroring directory "
                        f"exists (rules_manifest_structure.md §1)."
                    ),
                    who="developer",
                    reference=_REF,
                ))
                return {}

            # Defensive Unnesting (ADR-014 Resilience):
            # Fragment files may be authored with a top-level wrapper key so they
            # are valid standalone YAML (e.g. input_fields: {...}).  When !include
            # pulls such a fragment into a position that already provides the key
            # name, the wrapper would become a redundant double-nesting.
            # Example: data_schemas.amr_data.input_fields: !include amr_data.yaml
            #   where amr_data.yaml starts with  input_fields: {...}
            #   Without unnesting → data_schemas.amr_data.input_fields.input_fields: {...}  ← wrong
            #   With unnesting    → data_schemas.amr_data.input_fields: {...}               ← correct
            # This is WHY manifests work even when fragment files have wrapper keys.
            # The ingestor, MetadataValidator, and DataWrangler all rely on this
            # behaviour — do NOT remove it without updating those layers.
            redundant_keys = {"input_fields", "output_fields",
                              "wrangling", "source", "recipe", "spec"}
            if isinstance(content, dict) and len(content) == 1:
                key = list(content.keys())[0]
                if key in redundant_keys:
                    print(
                        f"  [ConfigManager] Auto-unnesting redundant key '{key}' from {included_file}")
                    return content[key]
            return content

        yaml.SafeLoader.add_constructor('!include', include_constructor)

        # Stage 1: file existence + YAML parse
        try:
            with open(yaml_path, 'r') as f:
                self.raw_config = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            exit_if_errors([DeploymentError(
                component="ConfigManager",
                problem=f"Manifest file not found: '{yaml_path}'",
                location=yaml_path,
                fix=(
                    "Verify the manifest path set in the deployment profile "
                    "('default_manifest' key) or the manifest selector dropdown."
                ),
                who="operator",
                reference=_REF,
            )])
            self.raw_config = {}  # unreachable
        except yaml.YAMLError as exc:
            exit_if_errors([DeploymentError(
                component="ConfigManager",
                problem=f"Malformed YAML in manifest: {exc}",
                location=yaml_path,
                fix=(
                    "Open the manifest in a YAML linter and fix the syntax error. "
                    "Common causes: unquoted 'on:' key (YAML boolean trap — use 'on':), "
                    "bad indentation, or a missing !include closing."
                ),
                who="developer",
                reference=_REF,
            )])
            self.raw_config = {}  # unreachable

        # Normalise YAML boolean trap: unquoted 'on:' → Python True key → string 'on' key.
        # Runs after !include constructors have already merged all fragments into raw_config,
        # so one pass covers both the main file and every included fragment.
        _normalise_yaml_boolean_keys(self.raw_config, yaml_path)

        # Stage 2: !include failures collected during parsing
        exit_if_errors(_include_errors)

        # Stage 3: structural validation
        struct_errors: list[DeploymentError] = []

        if not self.raw_config.get("analysis_groups"):
            struct_errors.append(DeploymentError(
                component="ConfigManager",
                problem="Manifest is missing the required 'analysis_groups:' block.",
                location=f"analysis_groups: key in {yaml_path}",
                fix=(
                    "Add an 'analysis_groups:' block with at least one group containing "
                    "at least one plot. See rules_manifest_structure.md §8 for the "
                    "required structure."
                ),
                who="developer",
                reference=_REF,
            ))

        data_schemas = self.raw_config.get("data_schemas", {})
        if not isinstance(data_schemas, dict):
            struct_errors.append(DeploymentError(
                component="ConfigManager",
                problem=f"'data_schemas:' must be a YAML mapping, got {type(data_schemas).__name__}.",
                location=f"data_schemas: key in {yaml_path}",
                fix="Restructure 'data_schemas:' as a YAML mapping of schema_id → schema config.",
                who="developer",
                reference=_REF,
            ))
        else:
            for schema_id, schema_cfg in data_schemas.items():
                if not isinstance(schema_cfg, dict):
                    struct_errors.append(DeploymentError(
                        component="ConfigManager",
                        problem=f"data_schemas.{schema_id} must be a mapping, got {type(schema_cfg).__name__}.",
                        location=f"data_schemas.{schema_id} in {yaml_path}",
                        fix=(
                            f"Ensure 'data_schemas.{schema_id}' is a YAML mapping with at least "
                            f"a 'source:' block containing a 'path:' key."
                        ),
                        who="developer",
                        reference=_REF,
                    ))
                elif not schema_cfg.get("source"):
                    struct_errors.append(DeploymentError(
                        component="ConfigManager",
                        problem=f"data_schemas.{schema_id} is missing the required 'source:' block.",
                        location=f"data_schemas.{schema_id}.source in {yaml_path}",
                        fix=(
                            f"Add a 'source:' block to 'data_schemas.{schema_id}' with at least "
                            f"a 'path:' key pointing to the input TSV/CSV file."
                        ),
                        who="developer",
                        reference=_REF,
                    ))

        exit_if_errors(struct_errors)

        # ADR-003/029b: Flatten analysis_groups into top-level 'plots' for VizFactory
        self.raw_config['plots'] = self.raw_config.get('plots', {})
        groups = self.raw_config.get('analysis_groups', {})
        for g_id, g_spec in groups.items():
            g_plots = g_spec.get('plots', {})
            for p_id, p_spec in g_plots.items():
                # Unnest 'spec' if found (Phase 11-D convention)
                if isinstance(p_spec, dict) and "spec" in p_spec:
                    p_body = p_spec["spec"].copy()
                    if "info" in p_spec:
                        p_body["info"] = p_spec["info"]
                else:
                    p_body = p_spec

                self.raw_config['plots'][p_id] = p_body

        self.defaults = self.raw_config.get('plot_defaults', {})

    def get_plot_config(self, group_name, plot_id):
        """
        Retrieves a plot config and merges it with defaults.
        Specific plot values 'shout louder' (overwrite) defaults.
        """
        # 1. Grab specific plot rules
        group = self.raw_config.get('analysis_groups', {}).get(group_name, {})
        plot_entry = group.get('plots', {}).get(plot_id, {})

        if not plot_entry:
            return None

        # 2. Handle nested spec (Phase 14-D refinement)
        # If 'spec' is present, we treat it as the base and merge 'info' into it
        if "spec" in plot_entry:
            plot_spec = plot_entry["spec"].copy()
            if "info" in plot_entry:
                plot_spec["info"] = plot_entry["info"]
        else:
            plot_spec = plot_entry

        # 3. Merge logic: start with defaults, update with specific specs
        final_config = self.defaults.copy()
        final_config.update(plot_spec)

        return final_config

    def get_metadata_rules(self):
        """Returns the 'Doorman' rules for the Ingestion Layer."""
        return self.raw_config.get('metadata_schema', {})

    def get_data_schemas(self):
        """Returns the dictionary of datasets to ingest for this pipeline."""
        return self.raw_config.get('data_schemas', {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
