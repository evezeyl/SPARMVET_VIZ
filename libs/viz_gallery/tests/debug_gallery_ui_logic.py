
from app.src.bootloader import bootloader
from pathlib import Path
import json
import yaml
import argparse


def test_gallery_filtering():
    print("--- 🔬 HEADLESS GALLERY UI FILTER TEST ---")

    index_path = bootloader.get_location("gallery") / "gallery_index.json"
    if not index_path.exists():
        print(f"❌ Index not found at {index_path}")
        return

    with open(index_path, "r") as f:
        idx = json.load(f)

    pivot = idx["pivot"]
    registry = idx["registry"]

    print(f"Index loaded. Total recipes: {len(registry)}")

    # Simulated Filters
    sel_families = ["Distribution"]
    sel_patterns = ["1 Numeric"]
    sel_difficulties = ["Simple", "Advanced"]

    print(
        f"Applying Filters: Family={sel_families}, Pattern={sel_patterns}, Difficulty={sel_difficulties}")

    # Logic Mirror (from server.py)
    family_matches = set()
    for f in sel_families:
        family_matches.update(pivot["by_family"].get(f, []))
    print(f"Family matches: {len(family_matches)}")

    pattern_matches = set()
    for p in sel_patterns:
        pattern_matches.update(pivot["by_pattern"].get(p, []))
    print(f"Pattern matches: {len(pattern_matches)}")

    diff_matches = set()
    for d in sel_difficulties:
        diff_matches.update(pivot["by_difficulty"].get(d, []))
    print(f"Difficulty matches: {len(diff_matches)}")

    final_ids = family_matches.intersection(
        pattern_matches).intersection(diff_matches)
    print(f"Final Intersection: {final_ids}")

    if not final_ids:
        print("⚠️ No matches found for these filters.")
    else:
        for rid in final_ids:
            entry = registry[rid]
            print(f"✅ Match: {entry['name']} ({rid})")
            # Verify Path Resolution
            path = Path(entry['path'])
            if path.exists():
                print(f"   [OK] Data analysis recipe exists: {path}")
                # Verify metadata
                md_path = path.parent / "recipe_meta.md"
                if md_path.exists():
                    print(f"   [OK] Metadata exists: {md_path}")
                else:
                    print(f"   [FAIL] Metadata MISSING: {md_path}")
            else:
                print(f"   [FAIL] Data analysis recipe NOT FOUND: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Headless Gallery UI Logic Test")
    args = parser.parse_args()
    test_gallery_filtering()


if __name__ == "__main__":
    main()
