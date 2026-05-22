"""Gate tests for TL-ANON-1 — Anonymiser single-file and batch flow."""
import yaml
import polars as pl
import pytest
from pathlib import Path

from test_lab.anonymiser import Anonymiser


@pytest.fixture
def metadata_tsv(tmp_path):
    tsv = tmp_path / "metadata.tsv"
    tsv.write_text(
        "sample_id\tname\taddress\tspecies\n"
        "S001\tJane Doe\tOslo\tE. coli\n"
        "S002\tJohn Smith\tBergen\tS. aureus\n"
        "S003\tAnna Hansen\tTromso\tE. coli\n"
    )
    return tsv


@pytest.fixture
def results_tsv(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text(
        "sample_id\tgene\tidentity\n"
        "S001\tblaTEM\t99.5\n"
        "S002\taac6\t98.0\n"
        "S003\tblaTEM\t97.2\n"
    )
    return tsv


class TestAnonymiseSingleFile:
    """Verify single-file anonymisation output."""

    def test_ids_replaced_not_original(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(metadata_tsv, id_column="sample_id")
        assert "sample_id" not in anon_df.columns
        assert "anon_sample_id" in anon_df.columns
        for val in ("S001", "S002", "S003"):
            assert val not in anon_df["anon_sample_id"].to_list()

    def test_personal_cols_stripped_from_output(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            personal_columns=["name", "address"],
        )
        assert "name" not in anon_df.columns
        assert "address" not in anon_df.columns
        assert "species" in anon_df.columns

    def test_personal_cols_present_in_mapping(self, metadata_tsv):
        _, mapping_df = Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            personal_columns=["name", "address"],
        )
        assert "name" in mapping_df.columns
        assert "address" in mapping_df.columns
        assert "original_sample_id" in mapping_df.columns
        assert "anon_sample_id" in mapping_df.columns

    def test_roundtrip_via_join(self, metadata_tsv):
        anon_df, mapping_df = Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            personal_columns=["name", "address"],
        )
        restored = anon_df.join(
            mapping_df.select(["original_sample_id", "anon_sample_id"]),
            on="anon_sample_id",
            how="inner",
        )
        assert set(restored["original_sample_id"].to_list()) == {"S001", "S002", "S003"}

    def test_sequential_pattern_default(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(metadata_tsv, id_column="sample_id")
        anon_ids = anon_df["anon_sample_id"].to_list()
        assert all(v.startswith("ANON_") for v in anon_ids)

    def test_hash_pattern(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(
            metadata_tsv, id_column="sample_id", pattern="hash"
        )
        anon_ids = anon_df["anon_sample_id"].to_list()
        assert all(v.startswith("ANON_") for v in anon_ids)
        assert len(set(anon_ids)) == 3

    def test_custom_pattern(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            pattern="SUBJ_{:05d}",
        )
        anon_ids = sorted(anon_df["anon_sample_id"].to_list())
        assert all(v.startswith("SUBJ_") for v in anon_ids)

    def test_custom_prefix(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            pattern="sequential",
            prefix="PATIENT",
        )
        anon_ids = anon_df["anon_sample_id"].to_list()
        assert all(v.startswith("PATIENT_") for v in anon_ids)

    def test_row_count_preserved(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(metadata_tsv, id_column="sample_id")
        assert anon_df.height == 3

    def test_non_id_cols_preserved(self, metadata_tsv):
        anon_df, _ = Anonymiser().anonymise(metadata_tsv, id_column="sample_id")
        assert "species" in anon_df.columns
        species = set(anon_df["species"].to_list())
        assert species == {"E. coli", "S. aureus"}


class TestAnonymiseBatch:
    """Verify multi-file consistency: same original_id → same anon_id."""

    def test_same_id_same_anon_across_files(self, metadata_tsv, results_tsv):
        result = Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
        )
        meta_anon = dict(
            zip(
                result["metadata.tsv"]["anon_sample_id"].to_list(),
                result["mapping"]["original_sample_id"].to_list(),
            )
        )
        res_anon_ids = set(result["results.tsv"]["anon_sample_id"].to_list())
        meta_anon_ids = set(result["metadata.tsv"]["anon_sample_id"].to_list())
        assert res_anon_ids == meta_anon_ids

    def test_all_files_in_result(self, metadata_tsv, results_tsv):
        result = Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
        )
        assert "metadata.tsv" in result
        assert "results.tsv" in result
        assert "mapping" in result

    def test_mapping_covers_all_ids(self, metadata_tsv, results_tsv):
        result = Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
        )
        original_ids = set(result["mapping"]["original_sample_id"].to_list())
        assert original_ids == {"S001", "S002", "S003"}

    def test_personal_cols_stripped_in_batch(self, metadata_tsv, results_tsv):
        result = Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
            personal_columns=["name", "address"],
        )
        assert "name" not in result["metadata.tsv"].columns
        assert "name" in result["mapping"].columns

    def test_batch_config_returned(self, metadata_tsv, results_tsv):
        result = Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
        )
        cfg = result["config"]
        assert "id_column" in cfg
        assert "files_anonymised" in cfg
        assert len(cfg["files_anonymised"]) == 2


class TestOutputFiles:
    """Verify written file structure and YAML audit record."""

    def test_writes_anonymised_tsv(self, metadata_tsv, tmp_path):
        Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            out_dir=tmp_path / "out",
        )
        assert (tmp_path / "out" / "anonymised_metadata.tsv").exists()

    def test_writes_mapping_tsv(self, metadata_tsv, tmp_path):
        Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            out_dir=tmp_path / "out",
        )
        assert (tmp_path / "out" / "mapping_sample_id.tsv").exists()

    def test_writes_config_yaml(self, metadata_tsv, tmp_path):
        Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            out_dir=tmp_path / "out",
        )
        assert (tmp_path / "out" / "anonymisation_config.yaml").exists()

    def test_config_yaml_not_pipeline_manifest(self, metadata_tsv, tmp_path):
        Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            out_dir=tmp_path / "out",
        )
        config_path = tmp_path / "out" / "anonymisation_config.yaml"
        content = config_path.read_text()
        assert "NOT a pipeline manifest" in content
        data = yaml.safe_load(content)
        assert "anonymisation_config" in data
        assert "id" not in data

    def test_config_yaml_records_columns(self, metadata_tsv, tmp_path):
        Anonymiser().anonymise(
            metadata_tsv,
            id_column="sample_id",
            personal_columns=["name", "address"],
            out_dir=tmp_path / "out",
        )
        data = yaml.safe_load((tmp_path / "out" / "anonymisation_config.yaml").read_text())
        cfg = data["anonymisation_config"]
        assert cfg["id_column"] == "sample_id"
        assert "name" in cfg["personal_columns"]
        assert "address" in cfg["personal_columns"]

    def test_batch_writes_all_anonymised_files(self, metadata_tsv, results_tsv, tmp_path):
        Anonymiser().anonymise_batch(
            [metadata_tsv, results_tsv],
            id_column="sample_id",
            out_dir=tmp_path / "out",
        )
        assert (tmp_path / "out" / "anonymised_metadata.tsv").exists()
        assert (tmp_path / "out" / "anonymised_results.tsv").exists()
        assert (tmp_path / "out" / "mapping_sample_id.tsv").exists()
        assert (tmp_path / "out" / "anonymisation_config.yaml").exists()

    def test_deanon_recipe_is_valid_yaml(self, metadata_tsv):
        recipe_yaml = Anonymiser().build_deanon_recipe(
            "sample_id", "mapping_sample_id.tsv"
        )
        parsed = yaml.safe_load(recipe_yaml)
        assert isinstance(parsed, list)
        step = parsed[0]
        assert step["action"] == "join"
        assert "anon_sample_id" in (step.get("left_on", "") + step.get("right_on", ""))
