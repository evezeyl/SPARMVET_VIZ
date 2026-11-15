"""Make the deliberately dirty copy of the data of `2_test_data_ST22_dummy`, and the staged recipes that read it.

(EQUALITY-CHECK-1, PROVISIONAL.) The shipped test data is clean: the filters of the recipe remove no row, no value is
missing, every sample id matches. This script writes small synthetic edits of the three shipped files that the recipe
reads, so that the equality test (`test_recipe_equals_hand_written.py`) exercises what a real, messy data set does.

It writes, under --out-dir (default `app/tests/equality`):
  data/dirty/      the three files of the recipe with the defects listed in `data/dirty/EDITS.md`
  data/emptied/    the same three files, but the plasmid filter removes every row (an emptied table)
  data/fractional_year/  the shipped values, except that one sample has Year 2023.5 (not a whole year)
  recipes/         staged copies of the shipped recipe that read those files (the shipped recipe is not changed)

Only the columns the recipe declares are written (the other columns, with the long sequences, are not read by the
recipe). The edits are chosen with a fixed seed, so a second run gives the same bytes.

Run:
  ./.venv/bin/python app/tests/equality/make_dirty_data.py            # writes the files
  ./.venv/bin/python app/tests/equality/make_dirty_data.py --help
"""
import argparse
import csv
import random
import re
import shutil
from pathlib import Path

RECIPE_ID = "2_test_data_ST22_dummy"
SOURCE_DIR = "assets/test_data/1_test_data_ST22_dummy"
FILES = {
    "metadata": "test_metadata_20260307_105756.tsv",
    "amr": "test_data_ResFinder_20260307_105756.tsv",
    "plasmid": "test_data_PlasmidFinder_20260307_105756.tsv",
}
# The columns the recipe declares (`original_name` of the input_fields), in the file's order.
COLUMNS = {
    "metadata": ["sample_id", "Source", "Year", "Country"],
    "amr": ["sample_id", "Gene", "Predicted Phenotype", "%Identity", "%Overlap", "Accession"],
    "plasmid": ["sample_id", "Plasmid", "%Identity", "%Overlap", "Accession"],
}
# Staged recipes: scenario name -> (recipe id, data folder, the recipe's null_values)
SCENARIOS = {
    "dirty": ("2_test_data_ST22_dummy_dirty", "dirty", '[""]'),
    "emptied": ("2_test_data_ST22_dummy_emptied", "emptied", '[""]'),
    "fractional_year": ("2_test_data_ST22_dummy_fractional_year", "fractional_year", '[""]'),
    # the shipped recipe's own rule (no text means missing) on the dirty data: an empty number cell cannot be read
    "dirty_no_null_text": ("2_test_data_ST22_dummy_dirty_no_null_text", "dirty", "[]"),
}


def read_rows(path: Path, columns: list[str]) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [{c: row[c] for c in columns} for row in reader]


def write_rows(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[c] for c in columns])


class Picker:
    """Chooses distinct rows or samples with the fixed seed and remembers what each role was given."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.used_samples: set[str] = set()
        self.log: list[str] = []

    def sample(self, role: str, candidates: list[str]) -> str:
        pool = sorted(set(candidates) - self.used_samples)
        chosen = self.rng.choice(pool)
        self.used_samples.add(chosen)
        self.log.append(f"- {role}: sample `{chosen}`")
        return chosen


def row_picker(rng: random.Random, rows: list[dict], taken: set[int], log: list[str], table: str):
    def pick(role: str, where=lambda r: True) -> dict:
        pool = [i for i, r in enumerate(rows) if i not in taken and where(r)]
        index = rng.choice(pool)
        taken.add(index)
        log.append(f"- {table} row {index + 2} of the file ({role}): sample `{rows[index]['sample_id']}`")
        return rows[index]

    return pick


def make_dirty(clean: dict[str, list[dict]], seed: int) -> tuple[dict[str, list[dict]], list[str]]:
    dirty = {name: [dict(r) for r in rows] for name, rows in clean.items()}
    meta, amr, plasmid = dirty["metadata"], dirty["amr"], dirty["plasmid"]
    picker = Picker(seed)
    picker.log.append("## Sample roles (the metadata row and the ResFinder rows named below are edited)")
    log: list[str] = []
    in_both = sorted({r["sample_id"] for r in amr} & {r["sample_id"] for r in plasmid} & {r["sample_id"] for r in meta})
    amr_count: dict[str, int] = {}
    for r in amr:
        amr_count[r["sample_id"]] = amr_count.get(r["sample_id"], 0) + 1
    two_rows = [s for s in in_both if amr_count.get(s, 0) == 2]
    single = [s for s in in_both if amr_count.get(s, 0) == 1]

    s_country_missing = picker.sample("Country missing in the metadata (grouping column)", in_both)
    s_year_missing = picker.sample("Year missing in the metadata", in_both)
    s_key_missing = picker.sample("sample_id missing in one metadata row (join key)", in_both)
    s_key_dup = picker.sample("repeated key in the metadata (two rows, different Source and Country)", in_both)
    s_country_spaces = picker.sample("Country with stray spaces", in_both)
    s_source_blank = picker.sample("Source is only spaces", in_both)
    s_country_na = picker.sample("Country is the text NA (Namibia)", in_both)
    s_country_lower = picker.sample("Country in lower case (norway)", in_both)
    s_case = picker.sample("two phenotypes written in different case and with spaces (one class)", two_rows)
    s_null_phenotype = picker.sample("one of two phenotypes missing", two_rows)
    s_gone = picker.sample("only ResFinder row is below the identity threshold (sample gone from the table)", single)

    mrow = {r["sample_id"]: r for r in meta}
    mrow[s_country_missing]["Country"] = ""
    mrow[s_year_missing]["Year"] = ""
    mrow[s_key_missing]["sample_id"] = ""
    twin = dict(mrow[s_key_dup])
    twin["Source"] = "Layer" if twin["Source"] != "Layer" else "Broiler"
    twin["Country"] = "Germany" if twin["Country"] != "Germany" else "France"
    meta.append(twin)
    mrow[s_country_spaces]["Country"] = "  " + mrow[s_country_spaces]["Country"] + " "
    mrow[s_source_blank]["Source"] = "   "
    mrow[s_country_na]["Country"] = "NA"
    mrow[s_country_lower]["Country"] = "norway"

    # --- ResFinder
    log.append("")
    log.append("## Rows (line number in the written file, header is line 1)")
    taken: set[int] = set()
    protected = {s_case, s_null_phenotype, s_gone}
    pick = row_picker(picker.rng, amr, taken, log, "ResFinder")
    free = lambda r: r["sample_id"] not in protected  # noqa: E731
    for index, row in enumerate(amr):
        if row["sample_id"] == s_gone:
            row["%Identity"] = "80"
            taken.add(index)
            log.append(f"- ResFinder row {index + 2} of the file (the only row of the sample, identity 80): sample `{s_gone}`")
    case_rows = [i for i, r in enumerate(amr) if r["sample_id"] == s_case]
    amr[case_rows[0]]["Predicted Phenotype"] = "Kanamycin"
    amr[case_rows[1]]["Predicted Phenotype"] = " kanamycin "
    taken.update(case_rows[:2])
    log.append(f"- ResFinder rows {case_rows[0] + 2} and {case_rows[1] + 2}: phenotype `Kanamycin` and ` kanamycin ` (one class)")
    null_rows = [i for i, r in enumerate(amr) if r["sample_id"] == s_null_phenotype]
    amr[null_rows[0]]["Predicted Phenotype"] = "tetracycline"
    amr[null_rows[1]]["Predicted Phenotype"] = ""
    taken.update(null_rows[:2])
    log.append(f"- ResFinder rows {null_rows[0] + 2} and {null_rows[1] + 2}: phenotype `tetracycline` and an empty one")
    for role, column, value in (
        ("identity exactly 90 (tie at the threshold)", "%Identity", "90"),
        ("identity exactly 90 (second tie)", "%Identity", "90"),
        ("identity just below 90", "%Identity", "89.9999"),
        ("identity just above 90", "%Identity", "90.0001"),
        ("overlap exactly 60 (tie)", "%Overlap", "60"),
        ("overlap exactly 60 (second tie)", "%Overlap", "60"),
        ("overlap just below 60", "%Overlap", "59.9999"),
        ("overlap just above 60", "%Overlap", "60.0001"),
        ("identity missing", "%Identity", ""),
        ("overlap missing", "%Overlap", ""),
        ("identity is NaN", "%Identity", "nan"),
        ("overlap is NaN", "%Overlap", "NaN"),
        ("identity with spaces", "%Identity", " 95.5 "),
    ):
        pick(role, free)[column] = value
    pick("sample_id missing (left key of the join)", free)["sample_id"] = ""
    pick("gene missing", free)["Gene"] = ""
    pick("phenotype in capitals", free)["Predicted Phenotype"] = "SULFISOXAZOLE"
    for _ in range(2):
        amr.append({"sample_id": "99999991", "Gene": "sul1", "Predicted Phenotype": "ampicillin",
                    "%Identity": "95", "%Overlap": "80", "Accession": "X02340"})
    log.append("- ResFinder: 2 rows appended for sample `99999991`, which is not in the metadata")

    # --- PlasmidFinder
    taken = set()
    pick = row_picker(picker.rng, plasmid, taken, log, "PlasmidFinder")
    for role, column, value in (
        ("identity exactly 90 (tie)", "%Identity", "90"),
        ("identity exactly 90 (second tie)", "%Identity", "90"),
        ("identity just below 90", "%Identity", "89.9999"),
        ("identity just above 90", "%Identity", "90.0001"),
        ("overlap exactly 60 (tie)", "%Overlap", "60"),
        ("overlap just below 60", "%Overlap", "59.9999"),
        ("overlap just above 60", "%Overlap", "60.0001"),
        ("identity missing", "%Identity", ""),
        ("overlap missing", "%Overlap", ""),
        ("overlap is NaN", "%Overlap", "nan"),
    ):
        pick(role)[column] = value
    pick("plasmid name missing (fill column of the plot)")["Plasmid"] = ""
    pick("plasmid name with spaces")["Plasmid"] = " IncFII "
    pick("plasmid name in lower case")["Plasmid"] = "incfii"
    pick("sample_id missing (left key of the join)")["sample_id"] = ""
    index = picker.rng.choice([i for i in range(len(plasmid)) if i not in taken])
    plasmid.append(dict(plasmid[index]))
    log.append(f"- PlasmidFinder row {index + 2} copied as a last row (an exact repeated row)")
    for _ in range(2):
        plasmid.append({"sample_id": "99999992", "Plasmid": "IncFII", "%Identity": "96", "%Overlap": "88",
                        "Accession": "AP001918"})
    log.append("- PlasmidFinder: 2 rows appended for sample `99999992`, which is not in the metadata")
    log.append("")
    log.append("## Metadata-only samples (kept from the shipped data)")
    amr_ids = {r["sample_id"] for r in clean["amr"]}
    pl_ids = {r["sample_id"] for r in clean["plasmid"]}
    only = sorted(r["sample_id"] for r in clean["metadata"] if r["sample_id"] not in amr_ids)
    log.append(f"- in the metadata and not in ResFinder: {', '.join(only)}")
    only = sorted(r["sample_id"] for r in clean["metadata"] if r["sample_id"] not in pl_ids)
    log.append(f"- in the metadata and not in PlasmidFinder: {', '.join(only)}")
    return dirty, picker.log + log


def stage_recipe(repo: Path, out_dir: Path, new_id: str, data_folder: str, null_values: str) -> None:
    """Copy the shipped recipe and its folder, point it at the staged data, state `null_values: [""]`."""
    shipped = repo / "config/data_analysis_recipes/pipelines"
    target = out_dir / "recipes"
    target.mkdir(parents=True, exist_ok=True)
    text = (shipped / f"{RECIPE_ID}.yaml").read_text(encoding="utf-8")
    text = text.replace(f"id: {RECIPE_ID}", f"id: {new_id}")
    text = text.replace(f"!include {RECIPE_ID}/", f"!include {new_id}/")
    rel_data = (out_dir / "data" / data_folder).relative_to(repo).as_posix()
    text = text.replace(SOURCE_DIR, rel_data)
    # The shipped recipe says `null_values: []` (no text is missing). Missing cells in a number column cannot be read
    # without a null text, so most staged recipes say that the empty text is a missing value (after the strip).
    text = text.replace("null_values: []", f"null_values: {null_values}")
    text = re.sub(r"# @deps.*?# @end_deps\n", "", text, flags=re.S)
    (target / f"{new_id}.yaml").write_text(
        f"# STAGED COPY of {RECIPE_ID}.yaml (EQUALITY-CHECK-1): reads app/tests/equality/data/{data_folder}; "
        f"null_values is {null_values}.\n# Made by app/tests/equality/make_dirty_data.py. Do not edit by hand.\n" + text,
        encoding="utf-8")
    folder = target / new_id
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(shipped / RECIPE_ID, folder, ignore=shutil.ignore_patterns("README.md"))
    for path in folder.rglob("*.yaml"):
        body = re.sub(r"# @deps.*?# @end_deps\n", "", path.read_text(encoding="utf-8"), flags=re.S)
        path.write_text(body, encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    parser = argparse.ArgumentParser(
        description="Write the dirty and emptied copies of the data of 2_test_data_ST22_dummy and the staged recipes "
                    "that read them (EQUALITY-CHECK-1). The shipped data and recipe are only read.",
        epilog="The result is committed; run again only to reproduce it (the same seed gives the same files).")
    parser.add_argument("--seed", type=int, default=20261115, help="seed of the random choice of rows (default 20261115)")
    parser.add_argument("--source-dir", default=str(repo / SOURCE_DIR), help="folder of the shipped data files")
    parser.add_argument("--out-dir", default=str(here), help="folder that receives data/ and recipes/ (default: this folder)")
    args = parser.parse_args()
    out_dir = Path(args.out_dir).resolve()
    clean = {name: read_rows(Path(args.source_dir) / FILES[name], COLUMNS[name]) for name in FILES}

    dirty, log = make_dirty(clean, args.seed)
    for name, rows in dirty.items():
        write_rows(out_dir / "data/dirty" / FILES[name], COLUMNS[name], rows)
    (out_dir / "data/dirty/EDITS.md").write_text(
        "# Edits of the dirty data (generated by make_dirty_data.py, seed %d)\n\n" % args.seed
        + "\n".join(log) + "\n", encoding="utf-8")

    emptied = {name: [dict(r) for r in rows] for name, rows in clean.items()}
    for row in emptied["plasmid"]:
        row["%Identity"] = "50"
    for name, rows in emptied.items():
        write_rows(out_dir / "data/emptied" / FILES[name], COLUMNS[name], rows)
    (out_dir / "data/emptied/EDITS.md").write_text(
        "# Emptied data (generated by make_dirty_data.py)\n\nThe shipped values, declared columns only, except that\n"
        "every PlasmidFinder row has identity 50: the plasmid filter (identity >= 90) removes every row.\n",
        encoding="utf-8")

    fractional = {name: [dict(r) for r in rows] for name, rows in clean.items()}
    fractional["metadata"][0]["Year"] = "2023.5"
    for name, rows in fractional.items():
        write_rows(out_dir / "data/fractional_year" / FILES[name], COLUMNS[name], rows)
    (out_dir / "data/fractional_year/EDITS.md").write_text(
        "# Fractional year (generated by make_dirty_data.py)\n\nThe shipped values, declared columns only, except that\n"
        "the first metadata row (sample `%s`) has Year 2023.5.\n" % clean["metadata"][0]["sample_id"], encoding="utf-8")

    for new_id, folder, null_values in SCENARIOS.values():
        stage_recipe(repo, out_dir, new_id, folder, null_values)
    print(f"written under {out_dir}")


if __name__ == "__main__":
    main()
