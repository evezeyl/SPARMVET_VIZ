"""Gate tests for TL-SCAFFOLD-1 — DataAnalysisRecipeScaffolder ZIP correctness."""
import io
import zipfile
import yaml
import pytest
from pathlib import Path


@pytest.fixture
def samples_tsv(tmp_path):
    tsv = tmp_path / "samples.tsv"
    tsv.write_text("sample_id\tspecies\ncnr001\tE. coli\ncnr002\tS. aureus\n")
    return tsv


@pytest.fixture
def amr_tsv(tmp_path):
    tsv = tmp_path / "amr_results.tsv"
    tsv.write_text("sample_id\tgene\tidentity\ncnr001\tblaTEM\t99.5\ncnr002\taac6\t98.0\n")
    return tsv


@pytest.fixture
def meta_tsv(tmp_path):
    tsv = tmp_path / "metadata.tsv"
    tsv.write_text("sample_id\tyear\ncnr001\t2023\ncnr002\t2024\n")
    return tsv


class _IncludeIgnoringLoader(yaml.SafeLoader):
    """SafeLoader that treats !include tags as opaque scalar strings."""
    pass

_IncludeIgnoringLoader.add_constructor(
    '!include',
    lambda loader, node: loader.construct_scalar(node)
)


def _load_master(zip_bytes: bytes, data_analysis_recipe_id: str) -> dict:
    """Extract and parse the master YAML from a ZIP without resolving !include."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        raw = zf.read(f"{data_analysis_recipe_id}/{data_analysis_recipe_id}.yaml").decode()
    return yaml.load(raw, Loader=_IncludeIgnoringLoader)


def _tier1(zip_bytes: bytes, name: str) -> list:
    """The tier1 list of one wrangling fragment of the ZIP (the candidate-key comment line is not YAML content)."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        return yaml.safe_load(zf.read(name).decode())["tier1"]


def _zip_names(zip_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        return set(zf.namelist())


class TestZipStructure:
    """Verify ZIP contains all expected fragment files."""

    def test_master_yaml_present(self, samples_tsv, tmp_path):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj_a")
        assert "proj_a/proj_a.yaml" in _zip_names(zb)

    def test_fragment_files_present(self, samples_tsv, tmp_path):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj_a")
        names = _zip_names(zb)
        assert "proj_a/proj_a/samples_input_fields.yaml" in names
        assert "proj_a/proj_a/samples_wrangling.yaml" in names
        assert not any(n.endswith("_output_fields.yaml") for n in names), "format 1 has no output_fields"

    def test_assembly_stub_present_with_two_datasets(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj_b")
        names = _zip_names(zb)
        assert any("assembly/" in n for n in names), "assembly/ stub must be in ZIP"

    def test_no_assembly_with_single_dataset(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj_single")
        names = _zip_names(zb)
        assert not any("assembly/" in n for n in names)


class TestMasterDataAnalysisRecipeKeys:
    """Verify master YAML has required top-level keys and correct structure."""

    def test_data_schemas_key_present(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert "data_schemas" in master

    def test_data_schemas_non_empty(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert master["data_schemas"]

    def test_analysis_groups_stub_present(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert "analysis_groups" in master

    def test_joins_key_present(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        assert "joins" in master

    def test_metadata_schema_conditional(self, samples_tsv, meta_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        s = DataAnalysisRecipeScaffolder()
        without = _load_master(s.scaffold([samples_tsv], "proj"), "proj")
        assert "metadata_schema" not in without, "metadata_schema must not appear without metadata_path"
        with_meta = _load_master(s.scaffold([samples_tsv], "proj", metadata_path=meta_tsv), "proj")
        assert "metadata_schema" in with_meta


class TestIngredientsFormat:
    """Verify joins uses ingredients: [{dataset_id: ...}] format."""

    def test_ingredients_list_format(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        jm = master["joins"]
        assert jm, "joins must be non-empty with two datasets"
        joint = next(iter(jm.values()))
        assert "ingredients" in joint
        ingredients = joint["ingredients"]
        assert isinstance(ingredients, list), "ingredients must be a list"
        assert all("dataset_id" in item for item in ingredients), \
            "each ingredient must have dataset_id key"

    def test_ingredients_contain_all_datasets(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        master = _load_master(DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        jm = master["joins"]
        joint = next(iter(jm.values()))
        ids = {item["dataset_id"] for item in joint["ingredients"]}
        assert "samples" in ids
        assert "amr_results" in ids


class TestAssemblyStubQuoting:
    """Verify assembly stub has quoted 'on': key."""

    def test_on_key_is_quoted(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            assembly_files = [n for n in zf.namelist() if "assembly/" in n]
            assert assembly_files, "assembly stub must exist"
            content = zf.read(assembly_files[0]).decode()
        assert "'on':" in content, f"'on': must be quoted in assembly stub. Got:\n{content}"

    def test_assembly_stub_has_tiered_steps(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            assembly_files = [n for n in zf.namelist() if "assembly/" in n]
            raw = zf.read(assembly_files[0]).decode()
        data = yaml.safe_load(raw)
        assert "steps" in data
        assert "tier1" in data["steps"]
        assert "tier2" in data["steps"]


class TestWranglingFragments:
    """Verify wrangling fragments are tiered and accept IdTransformation steps."""

    def test_wrangling_is_tiered(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            raw = zf.read("proj/proj/samples_wrangling.yaml").decode()
        yaml_lines = [l for l in raw.splitlines() if not l.startswith("#")]
        data = yaml.safe_load("\n".join(yaml_lines))
        assert "tier1" in data
        assert "tier2" in data

    def test_transformation_steps_injected_into_tier1(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        from utils import action_names
        steps = [{"action": action_names.STR_STRIP_CHARS, "columns": ["sample_id"]}]
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj", steps={"samples": steps})
        assert _tier1(zb, "proj/proj/samples_wrangling.yaml") == steps

    def test_steps_go_to_their_dataset_and_to_no_other(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        from utils import action_names
        steps = [{"action": action_names.STR_STRIP_CHARS, "columns": ["sample_id"]}]
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv, amr_tsv], "proj", steps={"amr_results": steps})
        assert _tier1(zb, "proj/proj/amr_results_wrangling.yaml") == steps
        assert _tier1(zb, "proj/proj/samples_wrangling.yaml") == []

    def test_an_empty_step_list_writes_an_empty_tier1(self, samples_tsv):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        zb = DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj", steps={"samples": []})
        assert _tier1(zb, "proj/proj/samples_wrangling.yaml") == []

    def test_steps_for_a_dataset_that_is_not_scaffolded_are_refused(self, samples_tsv):
        """Steps keyed by a name that matches no file were dropped without a word: the recipe lacked them."""
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        with pytest.raises(ValueError, match="Samples") as error:
            DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj", steps={"Samples": [{"action": "x"}]})
        assert "samples" in str(error.value), "the message names the datasets that exist"

    def test_steps_for_the_metadata_file_are_refused(self, samples_tsv, meta_tsv):
        """The metadata fragment takes no steps; steps keyed by it must not vanish."""
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        with pytest.raises(ValueError, match="metadata"):
            DataAnalysisRecipeScaffolder().scaffold([samples_tsv], "proj", steps={"metadata": [{"action": "x"}]},
                                                    metadata_path=meta_tsv)


class TestNames:
    """The names the scaffolder gives a file and a column are the ones a caller must use for its steps."""

    def test_the_dataset_id_is_the_one_used_in_the_zip(self, tmp_path):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        tsv = tmp_path / "AMR Results-2.tsv"
        tsv.write_text("Sample ID\tgene\nA\tx\n")
        scaffolder = DataAnalysisRecipeScaffolder()
        dataset_id = scaffolder.dataset_id(tsv)
        assert dataset_id == "amr_results_2"
        assert f"proj/proj/{dataset_id}_wrangling.yaml" in _zip_names(scaffolder.scaffold([tsv], "proj"))

    def test_the_field_slugs_are_the_keys_of_the_input_fields(self, tmp_path):
        from test_lab.scaffolder import DataAnalysisRecipeScaffolder
        tsv = tmp_path / "samples.tsv"
        tsv.write_text("Sample ID\tgene\nA\tx\n")
        scaffolder = DataAnalysisRecipeScaffolder()
        assert scaffolder.field_slugs(tsv) == ["sample_id", "gene"]
        assert scaffolder.column_slug("Sample ID") == "sample_id"
        with zipfile.ZipFile(io.BytesIO(scaffolder.scaffold([tsv], "proj"))) as zf:
            fields = yaml.safe_load(zf.read("proj/proj/samples_input_fields.yaml").decode())
        assert list(fields) == scaffolder.field_slugs(tsv)
