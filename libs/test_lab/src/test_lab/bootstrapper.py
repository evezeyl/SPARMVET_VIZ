# @deps
# provides: DataAnalysisRecipeBootstrapper class (bootstrap, id_cleaning_steps) — infers TSV schemas
#           and writes data analysis recipe YAML fragments (analysis_groups, joins, tiered wrangling)
# consumes: polars, pathlib, typing, yaml, re (stdlib/third-party)
# consumed_by: libs/test_lab/tests/test_bootstrapper.py
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


class DataAnalysisRecipeBootstrapper:
    """
    Logic for inferring data schemas from TSVs and bootstrapping data analysis recipe YAMLs.
    Follows the structure of recipe format 1 (input_fields, wrangling; no output_fields).
    """

    def __init__(self, cardinality_threshold: int = 15):
        self.cardinality_threshold = cardinality_threshold

    def _map_dtype(self, series: pl.Series) -> str:
        """The Polars dtype name to write for a column (recipe format 1: types are Polars names).

        A text column with few distinct values is suggested as `Categorical`, else `String`; the author can change it.
        """
        dtype = series.dtype
        if dtype.is_integer():
            return "Int64"
        if dtype.is_float():
            return "Float64"
        if isinstance(dtype, pl.Boolean):
            return "Boolean"
        if isinstance(dtype, pl.Date):
            return "Date"
        if isinstance(dtype, pl.Datetime):
            return "Datetime"
        if isinstance(dtype, pl.Time):
            return "Time"
        # Check cardinality for categorical suggestion
        return "Categorical" if series.n_unique() <= self.cardinality_threshold else "String"

    def _sanitize_name(self, name: str) -> str:
        return re.sub(r'[^\w]', '_', name.lower()).strip('_')

    def bootstrap(
        self,
        tsv_paths: List[Path],
        data_analysis_recipe_id: str,
        out_dir: Path,
        metadata_path: Optional[Path] = None,
        id_cleaning_steps: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ):
        """
        Creates a data analysis recipe folder and populates it with data analysis recipe fragments.

        Args:
            tsv_paths: Data source TSVs to infer schemas from.
            data_analysis_recipe_id: Data analysis recipe ID and output folder name.
            out_dir: Root directory for output.
            metadata_path: Optional dedicated metadata TSV. When provided, a
                ``metadata_schema`` block is added to the master data analysis recipe.
            id_cleaning_steps: Optional per-dataset wrangling steps to inject
                into ``tier1:``. Keyed by dataset_id (sanitized stem). Valid
                actions: ``polars_str_strip_chars``, ``polars_cast`` (String only),
                ``polars_str_replace_all``.
        """
        data_analysis_recipe_dir = out_dir / data_analysis_recipe_id
        data_analysis_recipe_dir.mkdir(parents=True, exist_ok=True)

        fragments_dir = data_analysis_recipe_dir / data_analysis_recipe_id  # Subfolder for fragments
        fragments_dir.mkdir(parents=True, exist_ok=True)

        id_cleaning_steps = id_cleaning_steps or {}
        datasets_config = {}

        for tsv_p in tsv_paths:
            dataset_id = self._sanitize_name(tsv_p.stem)
            # Peek for inference
            df = pl.read_csv(tsv_p, separator='\t', n_rows=100)

            # 1. Infer Fields
            fields = {}
            pk_candidates = []
            for col in df.columns:
                safe_col = self._sanitize_name(col)
                fields[safe_col] = {
                    "type": self._map_dtype(df[col]),
                    "label": col.replace('_', ' ').title(),
                    "original_name": col
                }
                if safe_col in ["id", "sample_id", "isolate_id"]:
                    fields[safe_col]["is_entity_key"] = True
                # Annotate high-uniqueness columns as PK candidates
                if df[col].n_unique() == len(df):
                    pk_candidates.append(safe_col)

            # Write Fragment: input_fields
            input_fields_file = fragments_dir / f"{dataset_id}_input_fields.yaml"
            with open(input_fields_file, 'w') as f:
                yaml.dump(fields, f, sort_keys=False)

            # Write Fragment: wrangling (tiered, ADR-024 §3)
            tier1_steps = id_cleaning_steps.get(dataset_id, [])
            wrangling_file = fragments_dir / f"{dataset_id}_wrangling.yaml"
            pk_hints = (
                f"# Candidate PK: {', '.join(pk_candidates)} (100% unique)\n"
                if pk_candidates
                else ""
            )
            with open(wrangling_file, 'w') as f:
                f.write(f"{pk_hints}")
                yaml.dump({"tier1": tier1_steps, "tier2": []}, f, sort_keys=False)

            # Prefer a project-relative path; fall back to absolute for files outside cwd.
            resolved = Path(tsv_p).resolve()
            try:
                source_path = str(resolved.relative_to(Path.cwd().resolve()))
            except ValueError:
                source_path = str(resolved)

            # Add to master config
            datasets_config[dataset_id] = {
                "source": {
                    "type": "local_tsv",
                    "path": source_path,
                },
                # No default for missing values (spec 7.3): the author states what means missing in this file
                "null_values": [],
                "strip": False,
                "input_fields": IncludeRef(f"{data_analysis_recipe_id}/{dataset_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{data_analysis_recipe_id}/{dataset_id}_wrangling.yaml"),
            }

        # Write Master Data Analysis Recipe
        master_data_analysis_recipe: Dict[str, Any] = {
            "id": data_analysis_recipe_id,
            "spec_version": 1,
            "data_engine": "python-polars",
            "plot_engine": "python-plotnine",
            "info": {
                "label": data_analysis_recipe_id.replace('_', ' ').title(),
                "version": "1.0",
                "description": f"Auto-bootstrapped pipeline for {data_analysis_recipe_id}"
            },
            "data_schemas": datasets_config,
        }

        # metadata_schema only when a metadata file was explicitly supplied
        if metadata_path is not None:
            meta_id = self._sanitize_name(metadata_path.stem)
            master_data_analysis_recipe["metadata_schema"] = {
                "source": {"type": "local_tsv", "path": str(metadata_path)},
                "null_values": [],
                "strip": False,
                "input_fields": IncludeRef(f"{data_analysis_recipe_id}/{meta_id}_input_fields.yaml"),
                "wrangling": IncludeRef(f"{data_analysis_recipe_id}/{meta_id}_wrangling.yaml"),
            }

        master_data_analysis_recipe["joins"] = {}
        master_data_analysis_recipe["analysis_groups"] = {}

        master_file = data_analysis_recipe_dir / f"{data_analysis_recipe_id}.yaml"
        with open(master_file, 'w') as f:
            yaml.dump(master_data_analysis_recipe, f, sort_keys=False)

        return master_file
