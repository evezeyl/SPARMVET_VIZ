# @deps
# provides: ManifestBootstrapper class (bootstrap) — infers TSV schemas and writes manifest YAML fragments
# consumes: polars, pathlib, typing, yaml, re (stdlib/third-party)
# consumed_by: libs/test_lab/tests/debug_sdk.py
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import re


class IncludeRef:
    """Wrapper for !include tags."""

    def __init__(self, path: str):
        self.path = path


def represent_include(dumper, data):
    return dumper.represent_scalar('!include', data.path, style='')


yaml.add_representer(IncludeRef, represent_include)


class ManifestBootstrapper:
    """
    Logic for inferring data schemas from TSVs and bootstrapping manifest YAMLs.
    Follows the mandatory 3-block structure (input_fields, wrangling, output_fields).
    """

    def __init__(self, cardinality_threshold: int = 15):
        self.cardinality_threshold = cardinality_threshold

    def _map_dtype(self, series: pl.Series) -> str:
        """Maps Polars dtype to user-friendly dashboard types."""
        dtype = series.dtype
        if dtype.is_integer():
            return "integer"
        elif dtype.is_float():
            return "float"
        elif isinstance(dtype, pl.Boolean):
            return "boolean"
        elif dtype.is_temporal():
            return "date"
        else:
            # Check cardinality for categorical suggestion
            unique_count = series.n_unique()
            if unique_count <= self.cardinality_threshold:
                return "categorical"
            return "string"

    def _sanitize_name(self, name: str) -> str:
        return re.sub(r'[^\w]', '_', name.lower()).strip('_')

    def bootstrap(self, tsv_paths: List[Path], project_id: str, out_dir: Path):
        """
        Creates a project folder and populates it with manifest fragments.
        """
        project_dir = out_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        fragments_dir = project_dir / project_id  # Subfolder for fragments
        fragments_dir.mkdir(parents=True, exist_ok=True)

        datasets_config = {}

        for tsv_p in tsv_paths:
            dataset_id = self._sanitize_name(tsv_p.stem)
            # Peek for inference
            df = pl.read_csv(tsv_p, separator='\t', n_rows=100)

            # 1. Infer Fields
            fields = {}
            for col in df.columns:
                safe_col = self._sanitize_name(col)
                fields[safe_col] = {
                    "type": self._map_dtype(df[col]),
                    "label": col.replace('_', ' ').title(),
                    "original_name": col
                }
                if safe_col in ["id", "sample_id", "isolate_id"]:
                    fields[safe_col]["is_primary_key"] = True

            # Write Fragment: input_fields
            input_fields_file = fragments_dir / \
                f"{dataset_id}_input_fields.yaml"
            with open(input_fields_file, 'w') as f:
                yaml.dump(fields, f, sort_keys=False)

            # Write Fragment: wrangling
            wrangling_file = fragments_dir / f"{dataset_id}_wrangling.yaml"
            with open(wrangling_file, 'w') as f:
                f.write("# Define atomic actions here\n[]\n")

            # Write Fragment: output_fields (Identity by default)
            output_fields_file = fragments_dir / \
                f"{dataset_id}_output_fields.yaml"
            with open(output_fields_file, 'w') as f:
                yaml.dump(fields, f, sort_keys=False)

            # Add to master config
            datasets_config[dataset_id] = {
                "source": {
                    "type": "local_tsv",
                    "path": str(Path(tsv_p).resolve().relative_to(Path.cwd().resolve()))
                },
                "input_fields": IncludeRef(f"{project_id}/{dataset_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{project_id}/{dataset_id}_wrangling.yaml"),
                "output_fields": IncludeRef(f"{project_id}/{dataset_id}_output_fields.yaml")
            }

        # Write Master Manifest
        master_manifest = {
            "id": project_id,
            "type": "pipeline",
            "info": {
                "display_name": project_id.replace('_', ' ').title(),
                "version": "1.0",
                "description": f"Auto-bootstrapped pipeline for {project_id}"
            },
            "data_schemas": datasets_config,
            "metadata_schema": {
                "source": {"type": "local_tsv", "path": "FILL_ME"},
                "input_fields": [],
                "wrangling": [],
                "output_fields": []
            },
            "join_manifests": {},
            "plotting": {}
        }

        master_file = project_dir / f"{project_id}.yaml"
        with open(master_file, 'w') as f:
            yaml.dump(master_manifest, f, sort_keys=False)

        return master_file
