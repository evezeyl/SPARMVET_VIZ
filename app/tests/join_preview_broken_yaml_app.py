"""The app of the broken-YAML case of `test_join_preview_session_alive.py`: the real app with one staged fault.

The recipe loader of the orchestrator is pointed at a real file with broken YAML, so that the real `ConfigManager`
fails the way it does for a user's broken fragment: it prints a [FATAL] block and calls `sys.exit(1)`. Nothing in
shipped code knows about it.
"""
import os
import tempfile
from pathlib import Path

from app.modules import orchestrator

_BROKEN = Path(tempfile.mkdtemp(prefix="broken_yaml_")) / "m.yaml"
_BROKEN.write_text("id: m\nanalysis_groups: [unclosed\n  - : :\n", encoding="utf-8")


_real_loader = orchestrator.load_data_analysis_recipe


def _load_broken_when_armed(path):
    """The test arms the fault by creating the file named in the variable, just before it clicks the preview."""
    flag = os.environ.get("BROKEN_YAML_FLAG")
    if flag and Path(flag).exists():
        from utils.config_loader import ConfigManager
        return ConfigManager(str(_BROKEN))
    return _real_loader(path)


orchestrator.load_data_analysis_recipe = _load_broken_when_armed

from app.src.main import app  # noqa: E402,F401  (imported after the fault is staged)
