import unittest
import sys
from pathlib import Path
from app.src.bootloader import Bootloader

"""
test_ui_app_features_masking.py
-------------------------
Forensic Audit of the App features Reactivity Matrix. 
Ensures feature gating logic correctly masks restricted components for each deployment.
"""


class TestUIAppFeaturesMasking(unittest.TestCase):
    def setUp(self):
        self.bootloader = Bootloader()

    def test_pipeline_static_masking(self):
        """Audit: Does 'pipeline-static' correctly hide restricted features?"""
        self.bootloader.__init__(app_features="pipeline-static")

        restricted = [
            "developer_mode_enabled",      # Tabs Gated?
            "comparison_mode_enabled",     # Comparison Gate?
            "gallery_enabled",             # Gallery Gate?
            "interactivity_enabled"        # Tier 3 Wrangle Studio?
        ]

        for feature in restricted:
            self.assertFalse(self.bootloader.is_enabled(feature),
                             f"Feature {feature} should be MASKED for pipeline-static.")

        print("  [PASS] App features Static Masking Verified (4/4 Restricted Items).")

    def test_developer_access(self):
        """Audit: Does 'developer' have full-spectrum access?"""
        self.bootloader.__init__(app_features="developer")

        enabled_items = [
            "developer_mode_enabled",
            "comparison_mode_enabled",
            "gallery_enabled"
        ]
        for feature in enabled_items:
            self.assertTrue(self.bootloader.is_enabled(feature),
                            f"Feature {feature} should be ENABLED for developer-mode.")
        print("  [PASS] Developer Access Verified (3/3 Admin Items).")

    def test_advanced_exploration_access(self):
        """Audit: Does 'pipeline-exploration-advanced' have correct subset?"""
        self.bootloader.__init__(app_features="pipeline-exploration-advanced")

        self.assertTrue(self.bootloader.is_enabled("comparison_mode_enabled"),
                        "Advanced Exploration MUST include comparison mode.")
        self.assertFalse(self.bootloader.is_enabled("developer_mode_enabled"),
                         "Advanced Exploration must NOT include dev studio tabs.")
        print("  [PASS] Advanced Exploration Subset verified.")


if __name__ == "__main__":
    unittest.main()
