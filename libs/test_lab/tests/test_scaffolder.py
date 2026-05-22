"""Gate tests for TL-SCAFFOLD-1 — ManifestScaffolder ZIP correctness."""
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


def _load_master(zip_bytes: bytes, project_id: str) -> dict:
    """Extract and parse the master YAML from a ZIP without resolving !include."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        raw = zf.read(f"{project_id}/{project_id}.yaml").decode()
    return yaml.load(raw, Loader=_IncludeIgnoringLoader)


def _zip_names(zip_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        return set(zf.namelist())


class TestZipStructure:
    """Verify ZIP contains all expected fragment files."""

    def test_master_yaml_present(self, samples_tsv, tmp_path):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv], "proj_a")
        assert "proj_a/proj_a.yaml" in _zip_names(zb)

    def test_fragment_files_present(self, samples_tsv, tmp_path):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv], "proj_a")
        names = _zip_names(zb)
        assert "proj_a/proj_a/samples_input_fields.yaml" in names
        assert "proj_a/proj_a/samples_wrangling.yaml" in names
        assert "proj_a/proj_a/samples_output_fields.yaml" in names

    def test_assembly_stub_present_with_two_datasets(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj_b")
        names = _zip_names(zb)
        assert any("assembly/" in n for n in names), "assembly/ stub must be in ZIP"

    def test_no_assembly_with_single_dataset(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv], "proj_single")
        names = _zip_names(zb)
        assert not any("assembly/" in n for n in names)


class TestMasterManifestKeys:
    """Verify master YAML has required top-level keys and correct structure."""

    def test_data_schemas_key_present(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert "data_schemas" in master

    def test_data_schemas_non_empty(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert master["data_schemas"]

    def test_analysis_groups_stub_present(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv], "proj"), "proj")
        assert "analysis_groups" in master

    def test_join_manifests_key_present(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        assert "join_manifests" in master

    def test_metadata_schema_conditional(self, samples_tsv, meta_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        s = ManifestScaffolder()
        without = _load_master(s.scaffold([samples_tsv], "proj"), "proj")
        assert "metadata_schema" not in without, "metadata_schema must not appear without metadata_path"
        with_meta = _load_master(s.scaffold([samples_tsv], "proj", metadata_path=meta_tsv), "proj")
        assert "metadata_schema" in with_meta


class TestIngredientsFormat:
    """Verify join_manifests uses ingredients: [{dataset_id: ...}] format."""

    def test_ingredients_list_format(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        jm = master["join_manifests"]
        assert jm, "join_manifests must be non-empty with two datasets"
        joint = next(iter(jm.values()))
        assert "ingredients" in joint
        ingredients = joint["ingredients"]
        assert isinstance(ingredients, list), "ingredients must be a list"
        assert all("dataset_id" in item for item in ingredients), \
            "each ingredient must have dataset_id key"

    def test_ingredients_contain_all_datasets(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        master = _load_master(ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj"), "proj")
        jm = master["join_manifests"]
        joint = next(iter(jm.values()))
        ids = {item["dataset_id"] for item in joint["ingredients"]}
        assert "samples" in ids
        assert "amr_results" in ids


class TestAssemblyStubQuoting:
    """Verify assembly stub has quoted 'on': key."""

    def test_on_key_is_quoted(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            assembly_files = [n for n in zf.namelist() if "assembly/" in n]
            assert assembly_files, "assembly stub must exist"
            content = zf.read(assembly_files[0]).decode()
        assert "'on':" in content, f"'on': must be quoted in assembly stub. Got:\n{content}"

    def test_assembly_stub_has_tiered_recipe(self, samples_tsv, amr_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv, amr_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            assembly_files = [n for n in zf.namelist() if "assembly/" in n]
            raw = zf.read(assembly_files[0]).decode()
        data = yaml.safe_load(raw)
        assert "recipe" in data
        assert "tier1" in data["recipe"]
        assert "tier2" in data["recipe"]


class TestWranglingFragments:
    """Verify wrangling fragments are tiered and accept TransformationRecipe steps."""

    def test_wrangling_is_tiered(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        zb = ManifestScaffolder().scaffold([samples_tsv], "proj")
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            raw = zf.read("proj/proj/samples_wrangling.yaml").decode()
        yaml_lines = [l for l in raw.splitlines() if not l.startswith("#")]
        data = yaml.safe_load("\n".join(yaml_lines))
        assert "tier1" in data
        assert "tier2" in data

    def test_recipe_steps_injected_into_tier1(self, samples_tsv):
        from test_lab.scaffolder import ManifestScaffolder
        steps = [{"action": "strip_whitespace", "columns": ["sample_id"]}]
        zb = ManifestScaffolder().scaffold([samples_tsv], "proj", recipes={"samples": steps})
        with zipfile.ZipFile(io.BytesIO(zb)) as zf:
            raw = zf.read("proj/proj/samples_wrangling.yaml").decode()
        yaml_lines = [l for l in raw.splitlines() if not l.startswith("#")]
        data = yaml.safe_load("\n".join(yaml_lines))
        assert len(data["tier1"]) == 1
        assert data["tier1"][0]["action"] == "strip_whitespace"
