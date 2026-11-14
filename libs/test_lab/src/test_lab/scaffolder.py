# @deps
# provides: DataAnalysisRecipeScaffolder class (scaffold, dataset_id, column_slug, field_slugs) — generates a data
#           analysis recipe ZIP with data analysis recipe fragments (input_fields, wrangling, assembly) and a master YAML.
#           joins pre-filled with ingredients: format; 'on': quoted; tiered wrangling.
# consumes: polars, pathlib, typing, yaml, re, io, zipfile (stdlib/third-party)
#           test_lab.bootstrapper (DataAnalysisRecipeBootstrapper, IncludeRef, represent_include)
# consumed_by: libs/test_lab/tests/test_scaffolder.py, app/modules/test_lab_studio.py
# @end_deps
import io
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any

import polars as pl
import yaml

from utils import action_names

from test_lab.bootstrapper import DataAnalysisRecipeBootstrapper, IncludeRef, represent_include


yaml.add_representer(IncludeRef, represent_include)


class DataAnalysisRecipeScaffolder:
    """
    Generates a scaffolded data analysis recipe ZIP from TSVs and optional IdTransformation objects.

    Builds on DataAnalysisRecipeBootstrapper schema inference and adds:
    - joins pre-filled with ingredients: format
    - assembly stub YAML with quoted 'on:' key
    - ZIP packaging of all fragments and master YAML
    """

    def __init__(self, cardinality_threshold: int = 15, join_key: str = "sample_id"):
        self._bs = DataAnalysisRecipeBootstrapper(cardinality_threshold)
        self.join_key = join_key

    def scaffold(
        self,
        tsv_paths: List[Path],
        data_analysis_recipe_id: str,
        steps: Optional[Dict[str, Any]] = None,
        metadata_path: Optional[Path] = None,
    ) -> bytes:
        """
        Scaffold a data analysis recipe ZIP from TSV paths.

        Args:
            tsv_paths: Data source TSVs to infer schemas from.
            data_analysis_recipe_id: Data analysis recipe ID and top-level folder name in the ZIP.
            steps: Optional mapping of dataset id (``dataset_id(path)``) → list of recipe
                     steps (format 1: registered actions with their parameters, for example
                     from ``id_reconciliation.recipe_steps``). The steps are written as they
                     are into that dataset's ``tier1:`` list. They are not checked here:
                     this library does not know the action registry.
            metadata_path: Optional dedicated metadata TSV. When provided, a
                           metadata_schema entry is added and included as an ingredient.

        Returns:
            ZIP bytes. Extract to a directory; the master YAML is at
            ``<data_analysis_recipe_id>/<data_analysis_recipe_id>.yaml``.

        Raises:
            ValueError: steps are given for a dataset id that no data file has. Nothing is
                        written then: steps are never dropped without a word.
        """
        steps = steps or {}
        known = [self.dataset_id(p) for p in tsv_paths]
        unknown = sorted(set(steps) - set(known))
        if unknown:
            raise ValueError(
                f"Steps were given for {', '.join(unknown)}, which is not a data file of this scaffold. "
                f"The data files that can take steps are: {', '.join(known)}."
            )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            self._write_zip(zf, tsv_paths, data_analysis_recipe_id, steps, metadata_path)
        buf.seek(0)
        return buf.read()

    def dataset_id(self, tsv_path) -> str:
        """The id this scaffold gives the dataset of a data file: the key of its steps and of its schema."""
        return self._bs._sanitize_name(Path(tsv_path).stem)

    def column_slug(self, column: str) -> str:
        """The name this scaffold gives a column of a file: the key of its input field, the name a step uses."""
        return self._bs._sanitize_name(column)

    def field_slugs(self, tsv_path) -> List[str]:
        """The columns of a data file under the names the scaffolded recipe gives them, in the order of the file."""
        return [self.column_slug(col) for col in pl.read_csv(tsv_path, separator='\t', n_rows=0).columns]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_zip(self, zf, tsv_paths, data_analysis_recipe_id, steps, metadata_path):
        fragments_prefix = f"{data_analysis_recipe_id}/{data_analysis_recipe_id}"
        dataset_ids = []

        for tsv_p in tsv_paths:
            dataset_id = self.dataset_id(tsv_p)
            dataset_ids.append(dataset_id)

            df = pl.read_csv(tsv_p, separator='\t', n_rows=100)
            fields, pk_candidates = self._infer_fields(df)

            self._write_fragment(zf, f"{fragments_prefix}/{dataset_id}_input_fields.yaml", fields)
            self._write_wrangling(zf, f"{fragments_prefix}/{dataset_id}_wrangling.yaml",
                                  pk_candidates, steps.get(dataset_id, []))

        if metadata_path is not None:
            meta_id = self._bs._sanitize_name(Path(metadata_path).stem)
            df_meta = pl.read_csv(metadata_path, separator='\t', n_rows=100)
            meta_fields, meta_pk = self._infer_fields(df_meta)
            self._write_fragment(zf, f"{fragments_prefix}/{meta_id}_input_fields.yaml", meta_fields)
            self._write_wrangling(zf, f"{fragments_prefix}/{meta_id}_wrangling.yaml", meta_pk, [])

        # Assembly stub — one joint per primary dataset (each joined to metadata or the next)
        joins_config = {}
        all_ingredient_ids = list(dataset_ids)
        if metadata_path is not None:
            all_ingredient_ids.append(self._bs._sanitize_name(Path(metadata_path).stem))

        if len(all_ingredient_ids) >= 2:
            join_id = f"{data_analysis_recipe_id}_joint"
            ingredients = [{"dataset_id": ds} for ds in all_ingredient_ids]
            assembly_path = f"{fragments_prefix}/assembly/{join_id}.yaml"
            self._write_assembly_stub(zf, assembly_path, all_ingredient_ids[1:])
            joins_config[join_id] = {
                "ingredients": ingredients,
                "steps": IncludeRef(f"{data_analysis_recipe_id}/assembly/{join_id}.yaml"),
            }
        else:
            joins_config = {}

        master = self._build_master(
            data_analysis_recipe_id, tsv_paths, dataset_ids, metadata_path, joins_config
        )
        master_yaml = yaml.dump(master, sort_keys=False, allow_unicode=True)
        zf.writestr(f"{data_analysis_recipe_id}/{data_analysis_recipe_id}.yaml", master_yaml)

    def _infer_fields(self, df: pl.DataFrame):
        fields = {}
        pk_candidates = []
        for col in df.columns:
            safe_col = self.column_slug(col)
            fields[safe_col] = {
                "type": self._bs._map_dtype(df[col]),
                "label": col.replace('_', ' ').title(),
                "original_name": col,
            }
            if safe_col in ("id", "sample_id", "isolate_id"):
                fields[safe_col]["is_entity_key"] = True
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
                "action": action_names.JOIN,
                "right_ingredient": ds_id,
                "on": [self.join_key],  # yaml.dump will quote 'on' automatically
                "how": "inner",
                "maintain_order": "left_right",
            }
            for ds_id in right_ingredients
        ]
        steps = {"steps": {"tier1": join_steps, "tier2": []}}
        zf.writestr(arcname, yaml.dump(steps, sort_keys=False, allow_unicode=True))

    def _build_master(self, data_analysis_recipe_id, tsv_paths, dataset_ids, metadata_path, joins_config):
        data_schemas = {}
        for tsv_p, dataset_id in zip(tsv_paths, dataset_ids):
            resolved = Path(tsv_p).resolve()
            try:
                source_path = str(resolved.relative_to(Path.cwd().resolve()))
            except ValueError:
                source_path = str(resolved)

            data_schemas[dataset_id] = {
                "source": {"type": "local_tsv", "path": source_path},
                "null_values": [],
                "strip": False,
                "input_fields": IncludeRef(f"{data_analysis_recipe_id}/{dataset_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{data_analysis_recipe_id}/{dataset_id}_wrangling.yaml"),
            }

        master: Dict[str, Any] = {
            "id": data_analysis_recipe_id,
            "spec_version": 1,
            "data_engine": "python-polars",
            "plot_engine": "python-plotnine",
            "info": {
                "label": data_analysis_recipe_id.replace('_', ' ').title(),
                "version": "1.0",
                "description": f"Auto-scaffolded pipeline for {data_analysis_recipe_id}",
            },
            "data_schemas": data_schemas,
        }

        if metadata_path is not None:
            meta_id = self._bs._sanitize_name(Path(metadata_path).stem)
            master["metadata_schema"] = {
                "source": {"type": "local_tsv", "path": str(Path(metadata_path).resolve())},
                "null_values": [],
                "strip": False,
                "input_fields": IncludeRef(f"{data_analysis_recipe_id}/{meta_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{data_analysis_recipe_id}/{meta_id}_wrangling.yaml"),
            }

        master["joins"] = joins_config
        master["analysis_groups"] = {}
        return master
