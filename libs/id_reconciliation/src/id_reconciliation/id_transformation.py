from __future__ import annotations

import yaml
from pathlib import Path
from .data_structures import IdTransformation

# @deps
# provides: save_transformation, load_transformation
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py
# @end_deps


def save_transformation(id_transformation: IdTransformation, path: Path) -> None:
    """Persist an IdTransformation to YAML."""
    data = {
        "ref_column": id_transformation.ref_column,
        "target_column": id_transformation.target_column,
        "steps": id_transformation.steps,
        "metadata": id_transformation.metadata,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True)


def load_transformation(path: Path) -> IdTransformation:
    """Load an IdTransformation from YAML."""
    with Path(path).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return IdTransformation(
        ref_column=data["ref_column"],
        target_column=data["target_column"],
        steps=data.get("steps", []),
        metadata=data.get("metadata", {}),
    )
