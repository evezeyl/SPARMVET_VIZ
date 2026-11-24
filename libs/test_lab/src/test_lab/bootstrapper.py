# engine: python-polars (reads data files with Polars to write a first recipe)
# @deps
# provides: DataAnalysisRecipeBootstrapper class (bootstrap, id_cleaning_steps) — infers TSV schemas
#           and writes data analysis recipe YAML fragments (analysis_groups, joins, a tier file per table: tier1: !include, D-0250)
# consumes: polars, pathlib, typing, yaml, re (stdlib/third-party), libs/utils/src/utils/engines.py
# consumed_by: libs/test_lab/tests/test_bootstrapper.py
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import re

from utils.engines import DATA_ENGINE, PLOT_ENGINE
from utils.recipe_check import spec as recipe_spec

# The names of a column that the bootstrapper marks `is_entity_id` (PROVISIONAL, as before: by name, the author corrects it).
ENTITY_ID_NAMES = ("id", "sample_id", "isolate_id")
# The completion block of the specification (marker suffix and starting sentence): a table that declares an entity id gets one (D-0574).
COMPLETION_SPEC = recipe_spec()["completion"]


class IncludeRef:
    """Wrapper for !include tags."""

    def __init__(self, path: str):
        self.path = path


def represent_include(dumper, data):
    return dumper.represent_scalar('!include', data.path, style='')


yaml.add_representer(IncludeRef, represent_include, Dumper=yaml.SafeDumper)


class DataAnalysisRecipeBootstrapper:
    """
    Logic for inferring data schemas from TSVs and bootstrapping data analysis recipe YAMLs.
    Follows the structure of recipe format 1: a table has `ui_label`, `source`, `null_values`, `strip`, `input_fields` and `tier1`
    (D-0250: the tier is its own key, here an `!include` of a file that holds `steps`); no `wrangling`, no `output_fields`.
    A tier 2 is not written: an absent tier 2 means that the table of tier 2 equals the table of tier 1.
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

    def write_table_files(self, fragments_dir: Path, table_id: str, tsv_path: Path, tier1_steps: List[Dict[str, Any]]):
        """Write the two files of one table: its `input_fields` and its tier 1 (`steps`, D-0250).

        The names are `<table_id>_input_fields.yaml` and `<table_id>_wrangling.yaml`. Returns the candidate-key hint line
        (empty when no column is unique), which the tier file starts with as a comment.
        """
        df = pl.read_csv(tsv_path, separator='\t', n_rows=100)
        fields = {}
        pk_candidates = []
        for col in df.columns:
            safe_col = self._sanitize_name(col)
            fields[safe_col] = {
                "type": self._map_dtype(df[col]),
                "ui_label": col.replace('_', ' ').title(),
                "original_name": col
            }
            if safe_col in ENTITY_ID_NAMES:
                fields[safe_col]["is_entity_id"] = True
            # Annotate high-uniqueness columns as PK candidates
            if df[col].n_unique() == len(df):
                pk_candidates.append(safe_col)

        with open(fragments_dir / f"{table_id}_input_fields.yaml", 'w') as f:
            yaml.safe_dump(fields, f, sort_keys=False)

        with open(fragments_dir / f"{table_id}_wrangling.yaml", 'w') as f:
            if pk_candidates:
                f.write(f"# Candidate PK: {', '.join(pk_candidates)} (100% unique)\n")
            yaml.safe_dump({"steps": tier1_steps}, f, sort_keys=False)

    @staticmethod
    def source_path(path) -> str:
        """The path a recipe names a data file by: relative to the project (the working folder) when the file is inside it,
        else absolute (the recipe checker refuses an absolute path, so the author must move the file into the project)."""
        resolved = Path(path).resolve()
        try:
            return str(resolved.relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(resolved)

    def declares_entity_id(self, tsv_path: Path) -> bool:
        """True when `write_table_files` marks a column of this file `is_entity_id` (the same rule, by the name of the column): the table then needs a
        `completion` block in the master recipe (D-0574)."""
        header = pl.read_csv(tsv_path, separator='\t', n_rows=1).columns
        return any(self._sanitize_name(col) in ENTITY_ID_NAMES for col in header)

    @staticmethod
    def table_block(recipe_id: str, table_id: str, source_path: str, label: str, entity_id: bool = False, metadata: bool = False) -> Dict[str, Any]:
        """The table entry of the master recipe: the keys in the order of the specification, the two files included.

        `entity_id`: the table declares an entity id, so it takes part in the completion of the ids and states what an added line means (the starting
        sentence of the specification: the author replaces it with what an added line means for the table); `metadata`: it is the metadata table, whose id is
        `metadata_schema`. The marker of every table carries its table id (`<table id>_not_in_original_data`, the owner's pattern): two tables never share a
        marker (E06), and the ids of the tables of one run are distinct."""
        block: Dict[str, Any] = {
            "ui_label": label,
            "source": {"type": "local_tsv", "path": source_path},
            # No default for missing values (spec 7.3): the author states what means missing in this file
            "null_values": [],
            "strip": False,
        }
        if entity_id:
            owner = "metadata_schema" if metadata else table_id
            block["completion"] = {"marker": f"{owner}_{COMPLETION_SPEC['marker_suffix']}", "meaning": COMPLETION_SPEC["starting_meaning"]}
        block["input_fields"] = IncludeRef(f"{recipe_id}/{table_id}_input_fields.yaml")
        block["tier1"] = IncludeRef(f"{recipe_id}/{table_id}_wrangling.yaml")
        return block

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
            id_cleaning_steps: Optional per-dataset recipe steps (format 1: registered
                actions with their parameters, for example from
                ``id_reconciliation.recipe_steps``) to write into ``tier1:``. Keyed by
                dataset_id (sanitized stem). The steps are written as they are. They are
                not checked here: this library does not know the action registry.

        Raises:
            ValueError: steps are given for a dataset id that no data file has. Nothing
                is written then: steps are never dropped without a word.
        """
        id_cleaning_steps = id_cleaning_steps or {}
        known = [self._sanitize_name(Path(p).stem) for p in tsv_paths]
        unknown = sorted(set(id_cleaning_steps) - set(known))
        if unknown:
            raise ValueError(
                f"Steps were given for {', '.join(unknown)}, which is not a data file of this bootstrap. "
                f"The data files that can take steps are: {', '.join(known)}."
            )

        data_analysis_recipe_dir = out_dir / data_analysis_recipe_id
        data_analysis_recipe_dir.mkdir(parents=True, exist_ok=True)

        fragments_dir = data_analysis_recipe_dir / data_analysis_recipe_id  # Subfolder for fragments
        fragments_dir.mkdir(parents=True, exist_ok=True)

        datasets_config = {}

        for tsv_p in tsv_paths:
            dataset_id = self._sanitize_name(tsv_p.stem)
            self.write_table_files(fragments_dir, dataset_id, tsv_p, id_cleaning_steps.get(dataset_id, []))

            # Add to master config
            datasets_config[dataset_id] = self.table_block(
                data_analysis_recipe_id, dataset_id, self.source_path(tsv_p), dataset_id.replace('_', ' ').capitalize(),
                entity_id=self.declares_entity_id(tsv_p))

        # Write Master Data Analysis Recipe
        master_data_analysis_recipe: Dict[str, Any] = {
            "id": data_analysis_recipe_id,
            "spec_version": 1,
            "data_engine": DATA_ENGINE,
            "plot_engine": PLOT_ENGINE,
            "info": {
                "ui_label": data_analysis_recipe_id.replace('_', ' ').title(),
                "version": "1.0",
                "description": f"Auto-bootstrapped pipeline for {data_analysis_recipe_id}"
            },
            "data_schemas": datasets_config,
        }

        # metadata_schema only when a metadata file was explicitly supplied
        if metadata_path is not None:
            meta_id = self._sanitize_name(metadata_path.stem)
            self.write_table_files(fragments_dir, meta_id, metadata_path, [])
            master_data_analysis_recipe["metadata_schema"] = self.table_block(
                data_analysis_recipe_id, meta_id, self.source_path(metadata_path), "Metadata",
                entity_id=self.declares_entity_id(metadata_path), metadata=True)

        master_data_analysis_recipe["joins"] = {}
        master_data_analysis_recipe["analysis_groups"] = {}

        master_file = data_analysis_recipe_dir / f"{data_analysis_recipe_id}.yaml"
        with open(master_file, 'w') as f:
            yaml.safe_dump(master_data_analysis_recipe, f, sort_keys=False)

        return master_file
