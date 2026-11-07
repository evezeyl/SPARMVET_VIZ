#!/usr/bin/env python3
# DEPRECATED (naming-standard migration to rules_verification_testing.md §1,
# date not recorded — found undated/untasked 2026-11-07, DOC-RECHECK-2):
# use libs/viz_factory/tests/debug_gallery.py instead.
# Removal task: LEGACY-MATERIALIZE-SHIM-REMOVE-1
# @deps
# provides: script:materialize_data_analysis_recipe_plots (DEPRECATED SHIM)
# consumes: libs/viz_factory/tests/debug_gallery.py (delegates all work)
# doc: libs/viz_factory/tests/debug_gallery.py
# @end_deps
"""
materialize_data_analysis_recipe_plots.py — DEPRECATED SHIM

The canonical headless art audit tool is now:
  libs/viz_factory/tests/debug_gallery.py

This script is a thin forwarding shim kept for backward compatibility
with any documented commands. It delegates all work to debug_gallery.py.

Removal task: LEGACY-MATERIALIZE-SHIM-REMOVE-1 (.claude/tasks/tasks.md).

Usage (preferred):
  .venv/bin/python libs/viz_factory/tests/debug_gallery.py --data-analysis-recipe <path>

Usage (legacy, via this shim):
  .venv/bin/python assets/scripts/materialize_data_analysis_recipe_plots.py --data-analysis-recipe <path>
"""
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
gallery_script = project_root / "libs/viz_factory/tests/debug_gallery.py"

if not gallery_script.exists():
    print(f"❌ Cannot find debug_gallery.py at {gallery_script}")
    sys.exit(1)

print(f"⚠️  This script is a shim. Delegating to: {gallery_script}")
result = subprocess.run([sys.executable, str(gallery_script)] + sys.argv[1:])
sys.exit(result.returncode)
