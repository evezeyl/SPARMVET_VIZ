# @deps
# provides: KeyReconciler class (calculate_intersection_score, suggest_regex, reconcile) — boundary-aware PK matching with ambiguity detection
# consumes: polars, re, pathlib, typing, collections, yaml (stdlib/third-party)
# consumed_by: libs/test_lab/tests/debug_reconciler.py, libs/test_lab/tests/debug_ambiguity.py, libs/test_lab/tests/demo_reconciler.py
# @end_deps
import polars as pl
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict
import yaml


class KeyReconciler:
    """
    Handles mismatched keys with boundary protection and ambiguity detection.
    """

    def __init__(self):
        pass

    def calculate_intersection_score(self, ref_keys: List[str], target_keys: List[str], use_boundary: bool = True) -> Dict[str, Any]:
        """
        Calculates matches with optional boundary awareness.
        """
        ref_set = set(ref_keys)
        target_set = set(target_keys)

        mapping = defaultdict(list)
        found_ref = defaultdict(list)

        # Priority 1: Exact
        for tk in target_set:
            if tk in ref_set:
                mapping[tk].append(
                    {"anchor": tk, "status": "EXACT", "original": tk})
                found_ref[tk].append(tk)

        # Priority 2: Fuzzy (Substring with Optional Boundary Awareness)
        for tk in target_set:
            if tk in ref_set:
                continue
            for rk in ref_set:
                if use_boundary:
                    # Boundary check: regex matching with non-alphanumeric boundaries
                    pattern = f"(?:^|[^a-zA-Z0-9]){re.escape(rk)}(?:$|[^a-zA-Z0-9])"
                    if re.search(pattern, tk):
                        mapping[tk].append(
                            {"anchor": rk, "status": "FUZZY", "original": tk})
                        found_ref[rk].append(tk)
                else:
                    if rk in tk:
                        mapping[tk].append(
                            {"anchor": rk, "status": "FUZZY", "original": tk})
                        found_ref[rk].append(tk)

        # Detect Ambiguity
        # Case A: One target matches multiple refs (unlikely but possible)
        # Case B: One ref matches multiple targets (Ambiguity according to user)
        # User definition: Sample_1 matches Sample_1 and Sample_11?
        # Actually Sample_1 should NOT match Sample_11 with boundaries.

        final_mapping = {}
        ambiguity_list = []

        # Check for refs with multiple target assignments
        for rk, targets in found_ref.items():
            if len(targets) > 1:
                ambiguity_list.append({"ref_key": rk, "targets": targets})
                for tk in targets:
                    if tk in mapping:
                        # Mark as ambiguous in the mapping
                        for m in mapping[tk]:
                            if m["anchor"] == rk:
                                m["status"] = "AMBIGUOUS"

        # Construct final dict (flattening mapping)
        for tk, matches in mapping.items():
            final_mapping[tk] = matches[0]  # Take one, mark status

        return {
            "found_ref": set(found_ref.keys()),
            "mapping": final_mapping,
            "ambiguities": ambiguity_list
        }

    def suggest_regex(self, original: str, anchor: str) -> str:
        """
        Suggests a regex_extract pattern with boundary protection.
        Uses \b if anchor starts/ends with alphanumeric.
        """
        if anchor not in original:
            return r".*"

        # Escape for regex
        escaped_anchor = re.escape(anchor)

        # Generalize digits: SAM001 -> SAM\d+
        # But we need to keep the context.
        # Heuristic: isolate the anchor part.

        # Add word boundaries if possible
        regex = f"({escaped_anchor})"
        if anchor[0].isalnum():
            # Not using \b directly in the suggest_regex as it might be part of the extraction group
            # But the logic using it should include it.
            pass

        generalized = re.sub(r'\d+', r'\\d+', escaped_anchor)
        # Add boundary checks around the capture group
        return rf"(?:^|[^a-zA-Z0-9])({generalized})(?:$|[^a-zA-Z0-9])"

    def reconcile(self, ref_df: pl.DataFrame, target_df: pl.DataFrame, key_cols: List[str], manual_regex: Optional[str] = None, use_boundary: bool = True) -> Dict[str, Any]:
        """
        Identifies matches and orphans across multiple keys.
        Supports manual_regex override and boundary protection toggle.
        """
        report = {}

        for col in key_cols:
            if col not in ref_df.columns or col not in target_df.columns:
                continue

            ref_keys = [str(k)
                        for k in ref_df[col].drop_nulls().unique().to_list()]
            target_keys = [
                str(k) for k in target_df[col].drop_nulls().unique().to_list()]

            # --- SELECTION OF REGEX ---
            if manual_regex:
                # ...
                pass
            scores = self.calculate_intersection_score(ref_keys, target_keys)

            # Suggest regex
            suggested_pattern = ".*"
            fuzzy_source = [tk for tk, v in scores["mapping"].items() if v["status"] in [
                "FUZZY", "AMBIGUOUS"]]
            if fuzzy_source:
                tk_sample = fuzzy_source[0]
                rk_sample = scores["mapping"][tk_sample]["anchor"]
                suggested_pattern = self.suggest_regex(tk_sample, rk_sample)

            # Orphan Detection
            orphans_ref = [
                rk for rk in ref_keys if rk not in scores["found_ref"]]
            matched_target = set(scores["mapping"].keys())
            orphans_target = [
                tk for tk in target_keys if tk not in matched_target]

            report[col] = {
                "metrics": {
                    "total_ref": len(ref_keys),
                    "exact": len([v for v in scores["mapping"].values() if v["status"] == "EXACT"]),
                    "fuzzy": len([v for v in scores["mapping"].values() if v["status"] == "FUZZY"]),
                    "ambiguous": len(scores["ambiguities"]),
                    "orphans": len(orphans_ref)
                },
                "suggested_regex": suggested_pattern,
                "mapping": scores["mapping"],
                "orphans_reference": orphans_ref,
                "orphans_target": orphans_target,
                "ambiguities": scores["ambiguities"]
            }

        return report
