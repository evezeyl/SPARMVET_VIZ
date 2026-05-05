#!/usr/bin/env python3
# @deps
# provides: script:create_test_deployment
# consumes: config/deployment/local/ (writes deployment profile YAML)
# doc: docs/workflows/connector.qmd, .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
create_test_deployment.py
-------------------------
Scaffolds a SPARMVET deployment profile YAML for local development and testing.

The generated file follows the ADR-048 deployment profile schema and is placed in
config/deployment/local/ for use as a dev fallback (Profile Resolution Level 4).

Usage:
  ./.venv/bin/python assets/scripts/create_test_deployment.py \\
      --manifest_id 2_test_data_ST22_dummy \\
      --deployment_file my_test_run.yaml \\
      --description "AMR ST22 test run for local dev"

  # Optional overrides (defaults to standard test data paths):
  ./.venv/bin/python assets/scripts/create_test_deployment.py \\
      --manifest_id 2_test_data_ST22_dummy \\
      --deployment_file custom.yaml \\
      --description "Custom test" \\
      --project_root /data/my_pipeline \\
      --persona pipeline-exploration-simple

See docs/workflows/connector.qmd for the full deployment profile schema (ADR-048).
"""
import argparse
import yaml
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--manifest_id", required=True,
                        help="ID of the manifest to lock at startup (e.g., 2_test_data_ST22_dummy).")
    parser.add_argument("--deployment_file", required=True,
                        help="Output filename (e.g., local_test.yaml). Written to config/deployment/local/.")
    parser.add_argument("--description", required=True,
                        help="Human-readable description of this test deployment.")
    parser.add_argument("--project_root", required=False, default=".",
                        help="Project root path (default: '.' — repository root).")
    parser.add_argument("--persona", required=False, default="developer",
                        choices=["pipeline-static", "pipeline-exploration-simple",
                                 "pipeline-exploration-advanced",
                                 "project-independent", "developer"],
                        help="Default persona for this deployment (default: developer).")
    args = parser.parse_args()

    out_dir = Path("config/deployment/local")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_name = args.deployment_file
    if not out_name.endswith((".yaml", ".yml")):
        out_name += ".yaml"
    out_path = out_dir / out_name

    # ADR-048 deployment profile schema
    profile = {
        "deployment_type": "filesystem",
        "deployment_name": args.description,
        "project_root": args.project_root,
        "locations": {
            "raw_data":     "assets/test_data/",
            "manifests":    "config/manifests/pipelines/",
            "curated_data": "tmp/UI_TEST/parquet_data/",
            "user_sessions": "tmp/UI_TEST/user/",
            "gallery":      "assets/gallery_data/",
        },
        "default_manifest": f"{args.manifest_id}.yaml",
        "default_persona": args.persona,
        "runtime": {
            "python_interpreter": "./.venv/bin/python",
        },
    }

    with open(out_path, "w") as f:
        yaml.dump(profile, f, sort_keys=False, default_flow_style=False)

    print(f"Deployment profile written: {out_path}")
    print(f"  manifest  : {args.manifest_id}")
    print(f"  persona   : {args.persona}")
    print(f"  project   : {args.project_root}")
    print()
    print("To use: set SPARMVET_PROFILE env var, or place at ~/.sparmvet/profile.yaml.")
    print("See docs/workflows/connector.qmd for the full profile schema (ADR-048).")


if __name__ == "__main__":
    main()
