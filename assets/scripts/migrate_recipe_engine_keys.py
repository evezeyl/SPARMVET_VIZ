"""Rewrite data analysis recipes to the shape of the engine keys (format 1 amended before its first release, D-0236).

What it does, for a recipe and every file it includes, as one unit:
  - the tiers become keys of the table, the join or the plot entry: `wrangling: {tier1: [...]}` of a table and `steps: {tier1: [...]}`
    of a join become `tier1: {steps: [...]}`, a plot entry's `steps: {tier3: [...]}` becomes `tier3: {steps: [...]}` (D-0250);
    an included tier fragment becomes one include per tier (`tier1: !include f`); a fragment that holds two tiers is split into
    `<name>_tier1.yaml` and `<name>_tier2.yaml` (PROVISIONAL naming) and the old file is removed;
  - the plot entry has no `spec:`: the content is written in the entry; a plot whose content was in its own file keeps that file,
    which now holds the WHOLE entry (D-0237, D-0252);
  - `label` becomes `ui_label` at groups, plot entries, info, tables, joins and the entries of input_fields (D-0253, D-0410, D-0468);
  - the old plot `title:` is written in the `labs` layer of the plot (PROVISIONAL reading of D-0253); no `ui_title` is written, the key is removed (D-0409);
  - the four dead `plot_defaults` keys are removed and each is printed with its old value (D-0241, D-0242);
  - a recipe whose plots would be drawn with the built-in theme_bw gets `theme_bw` written in `plot_defaults` (D-0258).
It edits the text, so comments, blank lines and `!include` lines stay. It PRINTS every change and a summary table. A file with
nothing to change is not touched. Safe to run twice: the second run changes nothing and says so. What it cannot place it refuses
with a plain message and changes nothing there; a file whose kind cannot be known from its keys is refused, never guessed.

Without --apply nothing is written (--check, the default). Exit code: with --check 0 when there is nothing to change and 1 when
something would change; with --apply 0 when the changes were written; 2 when something was refused (changes that could be placed
are still planned or written, the refused place is left as it was).

Examples:
  PYTHONPATH=. .venv/bin/python assets/scripts/migrate_recipe_engine_keys.py --check config/data_analysis_recipes assets/gallery_data
  PYTHONPATH=. .venv/bin/python assets/scripts/migrate_recipe_engine_keys.py --apply config/data_analysis_recipes/templates/e_coli.yaml
"""

# @deps
# provides: script:migrate_recipe_engine_keys
# consumes: libs/utils/src/utils/engine_keys_migration.py (migrate, format_events, summary), libs/viz_factory/src/viz_factory/plot_config_resolver.py (is_partial_theme: which theme components set only some properties)
# consumed_by: app/tests/test_migrate_recipe_engine_keys.py
# doc: .claude/design/recipe_format_spec.md (section 12, the amendment of 2026-11-17), .claude/knowledge/decision_ledger.md (D-0236, D-0250, D-0255, D-0258)
# @end_deps
import argparse
import os
import sys
from pathlib import Path

from utils.engine_keys_migration import format_events, migrate, summary


def partial_theme_function():
    """`is_partial_theme` of the plot library: which theme_* components only set some properties (it needs the registry)."""
    try:
        from viz_factory.plot_config_resolver import is_partial_theme
    except ImportError as exc:                                  # D-0050: without it the tool cannot judge, so it stops
        raise SystemExit(f"STOPPED: the plot library cannot be imported ({exc}). The tool needs it to tell a complete theme from a partial one. "
                         "Suggestion: run it from the project root with PYTHONPATH=. and the libraries installed (rules_toolchain.md).")
    return is_partial_theme


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="recipe files, or folders searched for *.yaml (a recipe is read together with the files it includes)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="say what would change and change nothing (default)")
    mode.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument("--orphan-fragments", action="store_true",
                        help="also rewrite an old tier fragment that no recipe in the given paths includes (by default it is listed and left, because a "
                             "recipe outside the given paths may include it; use this when you gave every recipe that could)")
    args = parser.parse_args(argv)
    result = migrate([Path(p) for p in args.paths], partial_theme=partial_theme_function(), orphan_fragments=args.orphan_fragments)
    here = Path(os.path.realpath(os.getcwd()))

    def shown(path: Path) -> str:
        try:
            return str(Path(os.path.realpath(path)).relative_to(here))
        except ValueError:
            return str(path)

    for line in format_events(result, shown):
        print(line)
    for path in result.removed:
        print(f"{shown(path)}: REMOVED")
    for path in result.created:
        print(f"{shown(path)}: CREATED")
    print("\nsummary")
    for name, count in summary(result):
        print(f"  {name:<16} {count}")
    if not result.would_change:
        print("nothing to change")
    if args.apply:
        for path, text in result.texts.items():
            path.write_text(text, encoding="utf-8")
        for path in result.removed:
            path.unlink()
        print(f"applied: {len(result.texts)} file(s) written ({len(result.created)} created), {len(result.removed)} removed")
    elif result.would_change:
        print("would change (nothing written; run with --apply)")
    if result.refused:
        return 2
    return 1 if (result.would_change and not args.apply) else 0


if __name__ == "__main__":
    sys.exit(main())
