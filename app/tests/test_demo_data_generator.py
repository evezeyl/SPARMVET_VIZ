"""The demo data generator writes one common set of sample ids, from a written seed (DATA-IDS-FIX-1, ledger D-0205).

Her decision: "The same set of ids is used across all the datasets of the recipes, so there is a logical
correspondence: the datasets reflect analyses on the same samples". The generator
(`assets/scripts/generate_demo_data.py`) must therefore (a) give every table ids of ONE set, (b) give the MLST
table one row per sample and scheme, (c) give the same files for the same seed, byte for byte.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_demo_data_generator.py -q
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "assets" / "scripts" / "generate_demo_data.py"
_spec = importlib.util.spec_from_file_location("generate_demo_data", SCRIPT)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def _run(out_dir, *extra):
    return gen.main(["--out-dir", str(out_dir), *extra])


def _read(out_dir, name):
    return gen.read_tsv(Path(out_dir) / gen.OUTPUT_NAMES[name])


def _ids(out_dir, name):
    header, rows = _read(out_dir, name)
    column = header.index("sample_id")
    return [r[column] for r in rows]


def test_the_same_seed_writes_the_same_files_byte_for_byte(tmp_path):
    assert _run(tmp_path / "a", "--seed", "7") == 0
    assert _run(tmp_path / "b", "--seed", "7") == 0
    for filename in gen.OUTPUT_NAMES.values():
        assert (tmp_path / "a" / filename).read_bytes() == (tmp_path / "b" / filename).read_bytes()


def test_another_seed_writes_other_files(tmp_path):
    _run(tmp_path / "a", "--seed", "7")
    _run(tmp_path / "b", "--seed", "8")
    name = gen.OUTPUT_NAMES["metadata"]
    assert (tmp_path / "a" / name).read_bytes() != (tmp_path / "b" / name).read_bytes()


@pytest.mark.parametrize("seed", [1, 2, 3, 20261117])
def test_every_id_of_every_table_is_in_the_one_common_set(tmp_path, seed):
    _run(tmp_path, "--seed", str(seed))
    common = {i for i in _ids(tmp_path, "metadata") if i not in gen.NO_ID_MARKERS}
    assert len(common) == 27
    for name in ("mlst", "resfinder"):
        assert set(_ids(tmp_path, name)) <= common, name
    # the metadata has one row per sample of the set (no repeat)
    meta_ids = [i for i in _ids(tmp_path, "metadata") if i not in gen.NO_ID_MARKERS]
    assert len(meta_ids) == len(set(meta_ids))


def test_mlst_has_one_row_per_sample_and_scheme_and_resfinder_may_have_several(tmp_path):
    _run(tmp_path, "--seed", "5")
    header, rows = _read(tmp_path, "mlst")
    keys = [(r[header.index("sample_id")], r[header.index("Scheme")]) for r in rows]
    assert len(keys) == len(set(keys)) == 15
    res_ids = _ids(tmp_path, "resfinder")
    assert len(res_ids) > len(set(res_ids))


def test_the_metadata_lines_without_an_id_are_kept_on_purpose_and_can_be_turned_off(tmp_path):
    _run(tmp_path / "a", "--seed", "5")
    no_id = [i for i in _ids(tmp_path / "a", "metadata") if i in gen.NO_ID_MARKERS]
    assert sorted(no_id) == sorted(gen.NO_ID_MARKERS)
    _run(tmp_path / "b", "--seed", "5", "--metadata-lines-without-id", "0")
    assert not [i for i in _ids(tmp_path / "b", "metadata") if i in gen.NO_ID_MARKERS]
    assert len(_ids(tmp_path / "b", "metadata")) == 27


def test_the_smallest_set_still_works(tmp_path):
    assert _run(tmp_path, "--n-samples", "1", "--metadata-lines-without-id", "0", "--mlst-share", "1") == 0
    assert len(_ids(tmp_path, "metadata")) == 1
    assert set(_ids(tmp_path, "mlst")) == set(_ids(tmp_path, "metadata"))


def test_no_messy_value_in_the_id_or_scheme_column_and_none_when_asked(tmp_path):
    _run(tmp_path, "--seed", "9", "--messy-fraction", "1")
    header, rows = _read(tmp_path, "mlst")
    assert {r[header.index("Scheme")] for r in rows} == {"ecoli_achtman_4"}
    assert all(r[0].startswith("SYN_") for r in rows)
    _run(tmp_path / "clean", "--seed", "9", "--messy-fraction", "0")
    header, rows = _read(tmp_path / "clean", "mlst")
    assert not any(v in gen.MESSY_VALUES for r in rows for v in r[2:3])


def test_files_that_exist_are_not_replaced_without_overwrite(tmp_path):
    _run(tmp_path, "--seed", "1")
    before = (tmp_path / gen.OUTPUT_NAMES["metadata"]).read_bytes()
    with pytest.raises(SystemExit):
        _run(tmp_path, "--seed", "2")
    assert (tmp_path / gen.OUTPUT_NAMES["metadata"]).read_bytes() == before
    assert _run(tmp_path, "--seed", "2", "--overwrite") == 0
    assert (tmp_path / gen.OUTPUT_NAMES["metadata"]).read_bytes() != before


@pytest.mark.parametrize("bad", [["--messy-fraction", "2"], ["--n-samples", "0"], ["--mlst-share", "0"]])
def test_bad_arguments_are_refused(tmp_path, bad):
    with pytest.raises(SystemExit):
        _run(tmp_path, *bad)


def test_help_runs():
    with pytest.raises(SystemExit) as stop:
        gen.main(["--help"])
    assert stop.value.code == 0


def test_the_check_names_a_foreign_id_and_a_repeated_sample_and_scheme():
    """The check itself must be able to fail: break the tables once."""
    tables = {
        "metadata": (["sample_id", "Source"], [["SYN_1", "a"], ["", "b"]]),
        "mlst": (["sample_id", "Scheme"], [["SYN_1", "s"], ["SYN_1", "s"], ["SYN_9", "s"]]),
        "resfinder": (["sample_id", "Gene"], [["SYN_1", "x"], ["SYN_1", "y"]]),
    }
    problems = gen.check_one_set(tables, ["SYN_1"])
    assert any("mlst" in p and "SYN_9" in p for p in problems)
    assert any("repeated" in p and "SYN_1" in p for p in problems)
    assert not any(p.startswith("metadata") or p.startswith("resfinder") for p in problems)
