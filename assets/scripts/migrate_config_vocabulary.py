"""Convert files written before the configuration rename (ADR-091) to the new names.

What it converts, each only when you ask for it and only with --apply:
  --recipes DIR    data analysis recipe YAML files: join_manifests: -> joins:, recipe: -> steps:
  --sessions DIR   saved sessions (assembly.json, t3_*.json): manifest_id, manifest_sha256,
                   t3_recipe, t3_recipe_by_plot, t3_recipe_sha256 -> their new names
  --gallery DIR    gallery bundles: recipe_manifest.yaml -> data_analysis_recipe.yaml,
                   recipe_meta.md -> example_meta.md (and the keys inside the YAML)

Without --apply nothing is written; the script lists what it would change. A file that
is already converted is left alone, so it is safe to run twice.

Examples:
  .venv/bin/python assets/scripts/migrate_config_vocabulary.py --recipes config/data_analysis_recipes
  .venv/bin/python assets/scripts/migrate_config_vocabulary.py --sessions tmp/UI_TEST/user --apply
  .venv/bin/python assets/scripts/migrate_config_vocabulary.py --gallery assets/gallery_data --apply
"""

import argparse
import json
import re
from pathlib import Path

SESSION_KEYS = {
    "manifest_id": "data_analysis_recipe_id",
    "manifest_sha256": "data_analysis_recipe_sha256",
    "t3_recipe": "t3_audit_steps",
    "t3_recipe_by_plot": "t3_audit_steps_by_plot",
    "t3_recipe_sha256": "t3_audit_steps_sha256",
}
_KEY_LINE = re.compile(r"^(?P<ind>\s*-?\s*)(?P<key>join_manifests|recipe)(?P<rest>\s*:.*)$")
_RENAME = {"join_manifests": "joins", "recipe": "steps"}


def convert_recipe_text(text: str) -> str:
    out = []
    for line in text.split("\n"):
        m = _KEY_LINE.match(line)
        out.append(f"{m['ind']}{_RENAME[m['key']]}{m['rest']}" if m else line)
    return "\n".join(out)


def convert_session_json(node):
    """Rename the old keys at any depth; values are never touched."""
    if isinstance(node, dict):
        return {SESSION_KEYS.get(k, k): convert_session_json(v) for k, v in node.items()}
    if isinstance(node, list):
        return [convert_session_json(v) for v in node]
    return node


def run(args) -> int:
    changed = 0
    verb = "converted" if args.apply else "would convert"
    if args.recipes:
        for f in sorted(Path(args.recipes).rglob("*.yaml")):
            text = f.read_text(encoding="utf-8")
            new = convert_recipe_text(text)
            if new != text:
                changed += 1
                print(f"{verb} {f}")
                if args.apply:
                    f.write_text(new, encoding="utf-8")
    if args.sessions:
        for f in sorted(list(Path(args.sessions).rglob("assembly.json")) + list(Path(args.sessions).rglob("t3_*.json"))):
            data = json.loads(f.read_text(encoding="utf-8"))
            new = convert_session_json(data)
            if new != data:
                changed += 1
                print(f"{verb} {f}")
                if args.apply:
                    f.write_text(json.dumps(new, indent=2), encoding="utf-8")
    if args.gallery:
        for d in sorted(p for p in Path(args.gallery).iterdir() if p.is_dir()):
            old_yaml, old_meta = d / "recipe_manifest.yaml", d / "recipe_meta.md"
            if old_yaml.exists():
                changed += 1
                print(f"{verb} {d.name}: recipe_manifest.yaml -> data_analysis_recipe.yaml")
                if args.apply:
                    old_yaml.write_text(convert_recipe_text(old_yaml.read_text(encoding="utf-8")), encoding="utf-8")
                    old_yaml.rename(d / "data_analysis_recipe.yaml")
            if old_meta.exists():
                changed += 1
                print(f"{verb} {d.name}: recipe_meta.md -> example_meta.md")
                if args.apply:
                    old_meta.rename(d / "example_meta.md")
    print(f"{changed} item(s) {verb}." + ("" if args.apply else " Run again with --apply to write."))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipes", metavar="DIR", help="folder of data analysis recipe YAML files")
    ap.add_argument("--sessions", metavar="DIR", help="folder of saved sessions (assembly.json, t3_*.json)")
    ap.add_argument("--gallery", metavar="DIR", help="gallery folder (one bundle per subfolder)")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: only list them)")
    args = ap.parse_args()
    if not (args.recipes or args.sessions or args.gallery):
        ap.error("give at least one of --recipes, --sessions, --gallery")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
