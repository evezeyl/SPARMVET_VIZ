#!/usr/bin/env python3
"""
make_old_result.py
------------------
Makes the two reference tables of `app/tests/test_resfinder_abromics_fragment.py`: what the OLD actions `derive_categories`,
`drop_duplicates` and `summarize` produced on the ST22 ResFinder data, with the old fragment's own parameters.

The old code is read from git history (the commit before the switch to recipe format 1, d63d3f3d), the old reference
file from the commit that made it (c2d0436f); nothing of the old engine is kept in the repository. The old data wrangler
(`DataWrangler.run`, same commit) first copied the column list of a step from the first of the keys columns, column,
source, source_column, target_column; this script does the same, so that `source_column: ...` and `target_column: ...`
act as they did.

The old fragment cannot run today as it is written:
- its reference file was replaced by another table in commit 1733db7f (the columns it names were gone);
- `drop_duplicates` names the column `cge_gene_symbol`, which no table ever had. The old wrangler refused it. The
  closest real column is `gene`; the second table is made with `gene` (the first is the table before that step).

Writes (tab separated):
  old_after_derive_categories.tsv   the table after step 1 (derive_categories): all rows, one column added
  old_final.tsv                     after drop_duplicates (on `gene`) and summarize

Usage (from the project root, in the project environment):
  ./.venv/bin/python app/tests/golden/resfinder_abromics/make_old_result.py
  ./.venv/bin/python app/tests/golden/resfinder_abromics/make_old_result.py --out-dir tmpAI/old --code-ref d63d3f3d^
"""
import argparse
import subprocess
from pathlib import Path
from typing import Any, Dict, Union

import polars as pl

OLD_FILES = {
    "derive_categories": "libs/transformer/src/transformer/actions/cleaning/advanced.py",
    "drop_duplicates": "libs/transformer/src/transformer/actions/cleaning/core.py",
    "summarize": "libs/transformer/src/transformer/actions/performance/aggregation.py",
}
REFERENCE_FILE = "config/references/amr_phenotypes/test_amr_categories_phenotype.tsv"
RENAMES = {"sample_id": "sample_id", "Gene": "gene", "CGE Predicted Phenotype": "cge_predicted_phenotype"}
# The three steps of the old fragment, with its parameters (the reference file path is filled in).
OLD_STEPS = [
    {"action": "derive_categories", "source_column": "cge_predicted_phenotype", "target_column": "AMR_Categories_Summary",
     "separator": ", ", "lookup_left": "cge_predicted_phenotype", "lookup_right": "Predicted Phenotype",
     "extract_column": "AMR Category (Class)"},
    {"action": "drop_duplicates", "target_column": "gene"},
    {"action": "summarize", "target_column": "AMR_Categories_Summary", "group_by": ["sample_id", "AMR_Categories_Summary"],
     "agg": "count", "new_name": "gene_count"},
]


def git_show(ref: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{ref}:{path}"], check=True, capture_output=True, text=True).stdout


def load_old_actions(code_ref: str) -> dict:
    """The three old functions, exec'd from the source text of the old commit with a registry that only collects them."""
    registry: Dict[str, Any] = {}

    def register_action(name, ui_schema=None):
        def decorator(func):
            registry[name] = func
            return func
        return decorator

    for name, path in OLD_FILES.items():
        source = git_show(code_ref, path)
        start = source.index(f'@register_action("{name}"')
        end = source.find("\n@register_action", start + 5)
        namespace = {"pl": pl, "Dict": Dict, "Any": Any, "Union": Union, "Path": Path, "register_action": register_action}
        exec(source[start:end if end > 0 else None], namespace)  # noqa: S102 - our own history, read here on purpose
    return registry


def old_step(registry: dict, lf: pl.LazyFrame, step: dict) -> pl.LazyFrame:
    """One step as the old data wrangler ran it: the column list is the first of the alias keys, a missing column stops it."""
    rule = dict(step)
    selector = rule.get("columns", rule.get("column", rule.get("source", rule.get("source_column", rule.get("target_column")))))
    selector = [selector] if isinstance(selector, str) else (selector or [])
    rule["columns"] = list(dict.fromkeys(selector))
    names = lf.collect_schema().names()
    if rule["columns"] and not any(c in names for c in rule["columns"]):
        raise RuntimeError(f"old wrangler: column(s) {rule['columns']} not found in {names}")
    return registry[rule["action"]](lf, rule)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--resfinder", type=Path, default=Path("assets/test_data/1_test_data_ST22_dummy/test_data_ResFinder_20260307_105756.tsv"))
    parser.add_argument("--out-dir", type=Path, default=Path("app/tests/golden/resfinder_abromics"))
    parser.add_argument("--code-ref", default="d63d3f3d^", help="the commit with the old actions (default: the one before the removal)")
    parser.add_argument("--reference-ref", default="c2d0436f", help="the commit with the old reference table")
    args = parser.parse_args()

    registry = load_old_actions(args.code_ref)
    reference = args.out_dir / "_old_reference.tsv"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    reference.write_text(git_show(args.reference_ref, REFERENCE_FILE), encoding="utf-8")
    try:
        raw = pl.read_csv(args.resfinder, separator="\t", infer_schema_length=0)
        lf = raw.select(list(RENAMES)).rename(RENAMES).lazy()
        derive = {**OLD_STEPS[0], "reference_file": str(reference)}
        after_derive = old_step(registry, lf, derive)
        after_derive.collect().write_csv(args.out_dir / "old_after_derive_categories.tsv", separator="\t")
        final = old_step(registry, old_step(registry, after_derive, OLD_STEPS[1]), OLD_STEPS[2])
        final.collect().write_csv(args.out_dir / "old_final.tsv", separator="\t")
    finally:
        reference.unlink()
    print(f"wrote {args.out_dir}/old_after_derive_categories.tsv and old_final.tsv")


if __name__ == "__main__":
    main()
