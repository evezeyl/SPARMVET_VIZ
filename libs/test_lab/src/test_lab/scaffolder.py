# @deps
# provides: ManifestScaffolder class (scaffold) — generates a project ZIP with manifest
#           fragments (input_fields, wrangling, output_fields, assembly) and a master YAML.
#           join_manifests pre-filled with ingredients: format; 'on': quoted; tiered wrangling.
# consumes: polars, pathlib, typing, yaml, re, io, zipfile (stdlib/third-party)
#           test_lab.bootstrapper (ManifestBootstrapper, IncludeRef, represent_include)
#           id_reconciliation.data_structures (TransformationRecipe)
# consumed_by: libs/test_lab/tests/test_scaffolder.py
# @end_deps
import io
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any

import polars as pl
import yaml

from test_lab.bootstrapper import ManifestBootstrapper, IncludeRef, represent_include

try:
    from id_reconciliation.data_structures import TransformationRecipe
except ImportError:
    TransformationRecipe = None  # type: ignore[assignment,misc]


yaml.add_representer(IncludeRef, represent_include)


class ManifestScaffolder:
    """
    Generates a scaffolded project ZIP from TSVs and optional TransformationRecipe objects.

    Builds on ManifestBootstrapper schema inference and adds:
    - join_manifests pre-filled with ingredients: format
    - assembly stub YAML with quoted 'on:' key
    - ZIP packaging of all fragments and master YAML
    """

    def __init__(self, cardinality_threshold: int = 15, join_key: str = "sample_id"):
        self._bs = ManifestBootstrapper(cardinality_threshold)
        self.join_key = join_key

    def scaffold(
        self,
        tsv_paths: List[Path],
        project_id: str,
        recipes: Optional[Dict[str, Any]] = None,
        metadata_path: Optional[Path] = None,
    ) -> bytes:
        """
        Scaffold a project manifest ZIP from TSV paths.

        Args:
            tsv_paths: Data source TSVs to infer schemas from.
            project_id: Manifest ID and top-level folder name in the ZIP.
            recipes: Optional mapping of sanitized dataset_id → TransformationRecipe.
                     Steps are injected into that dataset's tier1: wrangling block.
            metadata_path: Optional dedicated metadata TSV. When provided, a
                           metadata_schema entry is added and included as an ingredient.

        Returns:
            ZIP bytes. Extract to a directory; the master YAML is at
            ``<project_id>/<project_id>.yaml``.
        """
        recipes = recipes or {}
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            self._write_zip(zf, tsv_paths, project_id, recipes, metadata_path)
        buf.seek(0)
        return buf.read()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_zip(self, zf, tsv_paths, project_id, recipes, metadata_path):
        fragments_prefix = f"{project_id}/{project_id}"
        dataset_ids = []

        for tsv_p in tsv_paths:
            dataset_id = self._bs._sanitize_name(Path(tsv_p).stem)
            dataset_ids.append(dataset_id)

            df = pl.read_csv(tsv_p, separator='\t', n_rows=100)
            fields, pk_candidates = self._infer_fields(df)

            self._write_fragment(zf, f"{fragments_prefix}/{dataset_id}_input_fields.yaml", fields)
            self._write_wrangling(zf, f"{fragments_prefix}/{dataset_id}_wrangling.yaml",
                                  pk_candidates, recipes.get(dataset_id, []))
            self._write_fragment(zf, f"{fragments_prefix}/{dataset_id}_output_fields.yaml", fields)

        if metadata_path is not None:
            meta_id = self._bs._sanitize_name(Path(metadata_path).stem)
            df_meta = pl.read_csv(metadata_path, separator='\t', n_rows=100)
            meta_fields, meta_pk = self._infer_fields(df_meta)
            self._write_fragment(zf, f"{fragments_prefix}/{meta_id}_input_fields.yaml", meta_fields)
            self._write_wrangling(zf, f"{fragments_prefix}/{meta_id}_wrangling.yaml", meta_pk, [])
            self._write_fragment(zf, f"{fragments_prefix}/{meta_id}_output_fields.yaml", meta_fields)

        # Assembly stub — one joint per primary dataset (each joined to metadata or the next)
        join_manifests_config = {}
        all_ingredient_ids = list(dataset_ids)
        if metadata_path is not None:
            all_ingredient_ids.append(self._bs._sanitize_name(Path(metadata_path).stem))

        if len(all_ingredient_ids) >= 2:
            join_id = f"{project_id}_joint"
            ingredients = [{"dataset_id": ds} for ds in all_ingredient_ids]
            assembly_path = f"{fragments_prefix}/assembly/{join_id}.yaml"
            self._write_assembly_stub(zf, assembly_path, all_ingredient_ids[1:])
            join_manifests_config[join_id] = {
                "ingredients": ingredients,
                "recipe": IncludeRef(f"{project_id}/assembly/{join_id}.yaml"),
                "final_contract": {},
            }
        else:
            join_manifests_config = {}

        master = self._build_master(
            project_id, tsv_paths, dataset_ids, metadata_path, join_manifests_config
        )
        master_yaml = yaml.dump(master, sort_keys=False, allow_unicode=True)
        zf.writestr(f"{project_id}/{project_id}.yaml", master_yaml)

    def _infer_fields(self, df: pl.DataFrame):
        fields = {}
        pk_candidates = []
        for col in df.columns:
            safe_col = self._bs._sanitize_name(col)
            fields[safe_col] = {
                "type": self._bs._map_dtype(df[col]),
                "label": col.replace('_', ' ').title(),
                "original_name": col,
            }
            if safe_col in ("id", "sample_id", "isolate_id"):
                fields[safe_col]["is_primary_key"] = True
            if df[col].n_unique() == len(df):
                pk_candidates.append(safe_col)
        return fields, pk_candidates

    def _write_fragment(self, zf, arcname: str, content: dict):
        zf.writestr(arcname, yaml.dump(content, sort_keys=False, allow_unicode=True))

    def _write_wrangling(self, zf, arcname: str, pk_candidates, tier1_steps):
        pk_hint = (
            f"# Candidate PK: {', '.join(pk_candidates)} (100% unique)\n"
            if pk_candidates
            else ""
        )
        body = yaml.dump({"tier1": tier1_steps, "tier2": []}, sort_keys=False)
        zf.writestr(arcname, pk_hint + body)

    def _write_assembly_stub(self, zf, arcname: str, right_ingredients: List[str]):
        """Write a tiered assembly stub with join steps for each right ingredient."""
        join_steps = [
            {
                "action": "join",
                "right_ingredient": ds_id,
                "on": self.join_key,  # yaml.dump will quote 'on' automatically
                "how": "inner",
            }
            for ds_id in right_ingredients
        ]
        recipe = {"recipe": {"tier1": join_steps, "tier2": []}}
        zf.writestr(arcname, yaml.dump(recipe, sort_keys=False, allow_unicode=True))

    def _build_master(self, project_id, tsv_paths, dataset_ids, metadata_path, join_manifests_config):
        data_schemas = {}
        for tsv_p, dataset_id in zip(tsv_paths, dataset_ids):
            resolved = Path(tsv_p).resolve()
            try:
                source_path = str(resolved.relative_to(Path.cwd().resolve()))
            except ValueError:
                source_path = str(resolved)

            data_schemas[dataset_id] = {
                "source": {"type": "local_tsv", "path": source_path},
                "input_fields": IncludeRef(f"{project_id}/{dataset_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{project_id}/{dataset_id}_wrangling.yaml"),
                "output_fields": IncludeRef(f"{project_id}/{dataset_id}_output_fields.yaml"),
            }

        master: Dict[str, Any] = {
            "id": project_id,
            "type": "pipeline",
            "info": {
                "display_name": project_id.replace('_', ' ').title(),
                "version": "1.0",
                "description": f"Auto-scaffolded pipeline for {project_id}",
            },
            "data_schemas": data_schemas,
        }

        if metadata_path is not None:
            meta_id = self._bs._sanitize_name(Path(metadata_path).stem)
            master["metadata_schema"] = {
                "source": {"type": "local_tsv", "path": str(Path(metadata_path).resolve())},
                "input_fields": IncludeRef(f"{project_id}/{meta_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{project_id}/{meta_id}_wrangling.yaml"),
                "output_fields": IncludeRef(f"{project_id}/{meta_id}_output_fields.yaml"),
            }

        master["join_manifests"] = join_manifests_config
        master["analysis_groups"] = {}
        return master
