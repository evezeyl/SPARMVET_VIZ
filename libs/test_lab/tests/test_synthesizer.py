"""Gate tests for TL-SYNTH-1 — AquaSynthesizer two-step flow."""
import yaml
import polars as pl
import pytest
from pathlib import Path

from test_lab.aqua_synthesizer import AquaSynthesizer, _MALFORMED_STRINGS


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


class TestProposeConfig:
    """Verify propose_config correctly inspects source and returns a valid config dict."""

    def test_from_tsv_infers_columns(self, samples_tsv):
        cfg = AquaSynthesizer().propose_config(samples_tsv)
        assert "mode" in cfg
        assert "n_rows" in cfg
        assert "columns" in cfg
        names = [c["name"] for c in cfg["columns"]]
        assert "sample_id" in names
        assert "species" in names

    def test_from_tsv_detects_pk(self, samples_tsv):
        cfg = AquaSynthesizer().propose_config(samples_tsv)
        pk_spec = next((c for c in cfg["columns"] if c.get("is_pk")), None)
        assert pk_spec is not None, "propose_config must detect a PK column"
        assert pk_spec["name"] == "sample_id"

    def test_from_column_names_detects_id(self):
        cfg = AquaSynthesizer().propose_config(["sample_id", "species", "identity"])
        assert len(cfg["columns"]) == 3
        pk = next((c for c in cfg["columns"] if c["name"] == "sample_id"), None)
        assert pk is not None
        assert pk.get("is_pk") is True

    def test_error_injection_block_present(self, samples_tsv):
        cfg = AquaSynthesizer().propose_config(samples_tsv, mode="stress_test")
        assert "error_injection" in cfg
        ei = cfg["error_injection"]
        for key in ("missing_values", "wrong_type", "duplicate_ids",
                    "pk_mismatches", "schema_errors", "malformed_fields"):
            assert key in ei, f"error_injection missing key: {key}"

    def test_primary_key_column_set(self, samples_tsv):
        cfg = AquaSynthesizer().propose_config(samples_tsv)
        assert cfg["primary_key_column"] == "sample_id"


class TestGenerateDemo:
    """Verify demo mode generates clean, well-formed data."""

    def test_generates_correct_row_count(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=25)
        df = s.generate(cfg, seed=42)
        assert df.shape[0] == 25

    def test_pk_column_is_unique(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=50)
        df = s.generate(cfg, seed=42)
        pk_col = cfg["primary_key_column"]
        assert pk_col is not None
        assert df[pk_col].n_unique() == df.height

    def test_pk_has_no_nulls(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=50)
        df = s.generate(cfg, seed=42)
        pk_col = cfg["primary_key_column"]
        assert df[pk_col].null_count() == 0

    def test_output_written_to_tsv(self, samples_tsv, tmp_path):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=10)
        out = tmp_path / "output.tsv"
        s.generate(cfg, out_path=out, seed=42)
        assert out.exists()
        loaded = pl.read_csv(out, separator="\t")
        assert loaded.shape[0] == 10

    def test_float_column_inferred_and_generated(self, amr_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(amr_tsv, n_rows=30)
        float_cols = [c["name"] for c in cfg["columns"] if c.get("dtype") == "float"]
        assert float_cols, "identity column must be inferred as float"
        df = s.generate(cfg, seed=42)
        assert df[float_cols[0]].dtype in (pl.Float32, pl.Float64)


class TestStressTestInjection:
    """Rate accuracy tests — statistical. Use n_rows=1000 to keep variance low."""

    def test_missing_values_rate(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=1000, mode="stress_test")
        cfg["error_injection"]["missing_values"] = {"rate": 0.10, "columns": ["species"]}
        df = s.generate(cfg, seed=42)
        actual_rate = df["species"].null_count() / df.height
        assert abs(actual_rate - 0.10) < 0.05, f"missing_values rate {actual_rate:.3f} outside ±5%"

    def test_duplicate_ids_rate(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=1000, mode="stress_test")
        cfg["error_injection"]["duplicate_ids"] = {"rate": 0.10}
        df = s.generate(cfg, seed=42)
        pk_col = cfg["primary_key_column"]
        dup_count = df.height - df[pk_col].n_unique()
        actual_rate = dup_count / df.height
        assert abs(actual_rate - 0.10) < 0.01, f"duplicate_ids rate {actual_rate:.3f} not within ±1% (exact)"

    def test_wrong_type_rate(self, amr_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(amr_tsv, n_rows=1000, mode="stress_test")
        float_cols = [c["name"] for c in cfg["columns"] if c.get("dtype") == "float"]
        assert float_cols, "amr_tsv must have at least one float column"
        cfg["error_injection"]["wrong_type"] = {"rate": 0.10, "columns": float_cols[:1]}
        df = s.generate(cfg, seed=42)
        col = float_cols[0]
        error_count = df.filter(pl.col(col) == "ERROR").height
        actual_rate = error_count / df.height
        assert abs(actual_rate - 0.10) < 0.05, f"wrong_type rate {actual_rate:.3f} outside ±5%"

    def test_malformed_fields_rate(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=1000, mode="stress_test")
        cfg["error_injection"]["malformed_fields"] = {"rate": 0.10, "columns": ["species"]}
        df = s.generate(cfg, seed=42)
        malformed_set = set(_MALFORMED_STRINGS)
        malformed_count = df.filter(pl.col("species").is_in(list(malformed_set))).height
        actual_rate = malformed_count / df.height
        assert abs(actual_rate - 0.10) < 0.05, f"malformed_fields rate {actual_rate:.3f} outside ±5%"

    def test_schema_errors_adds_unexpected_column(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=20, mode="stress_test")
        cfg["error_injection"]["schema_errors"] = {"rate": 1.0}
        df = s.generate(cfg, seed=42)
        assert "EXTRA_COL_DO_NOT_USE" in df.columns

    def test_pk_mismatches_injects_orphan_ids(self, samples_tsv):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=100, mode="stress_test")
        cfg["error_injection"]["pk_mismatches"] = {"rate": 0.10}
        df = s.generate(cfg, seed=42)
        pk_col = cfg["primary_key_column"]
        orphan_count = df.filter(pl.col(pk_col).str.starts_with("ORPHAN_")).height
        assert abs(orphan_count / df.height - 0.10) < 0.01


class TestScenarioRoundtrip:
    """Verify save/load/list scenario workflow."""

    def test_save_and_load_roundtrip(self, samples_tsv, tmp_path):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=20)
        s.save_config(cfg, "test_scenario", tmp_path)
        loaded = s.load_config("test_scenario", tmp_path)
        assert loaded["mode"] == cfg["mode"]
        assert loaded["n_rows"] == cfg["n_rows"]
        assert len(loaded["columns"]) == len(cfg["columns"])
        assert loaded["columns"][0]["name"] == cfg["columns"][0]["name"]

    def test_list_scenarios(self, samples_tsv, tmp_path):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=10)
        s.save_config(cfg, "scenario_a", tmp_path)
        s.save_config(cfg, "scenario_b", tmp_path)
        names = s.list_scenarios(tmp_path)
        assert "scenario_a" in names
        assert "scenario_b" in names

    def test_yaml_has_mandatory_header(self, samples_tsv, tmp_path):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=10)
        saved = s.save_config(cfg, "header_check", tmp_path)
        content = saved.read_text()
        assert "NOT a pipeline manifest" in content
        assert "synthetic_data_config:" in content

    def test_yaml_root_key_is_synthetic_data_config(self, samples_tsv, tmp_path):
        s = AquaSynthesizer()
        cfg = s.propose_config(samples_tsv, n_rows=10)
        saved = s.save_config(cfg, "root_key_check", tmp_path)
        data = yaml.safe_load(saved.read_text())
        assert "synthetic_data_config" in data, "root key must be synthetic_data_config"
        assert "id" not in data, "pipeline manifest 'id' key must NOT appear at root"

    def test_empty_scenarios_dir_returns_empty_list(self, tmp_path):
        s = AquaSynthesizer()
        assert s.list_scenarios(tmp_path / "nonexistent") == []
