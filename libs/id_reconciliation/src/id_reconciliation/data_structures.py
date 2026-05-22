from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# @deps
# provides: IDPair, MatchResult, PatternSuggestion
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py,
#              libs/id_reconciliation/src/id_reconciliation/matcher.py,
#              libs/id_reconciliation/src/id_reconciliation/pattern_detector.py,
#              libs/id_reconciliation/src/id_reconciliation/recipe.py
# @end_deps


@dataclass
class IDPair:
    ref_id: str
    target_id: str


@dataclass
class MatchResult:
    ref_id: str
    target_id: Optional[str]
    match_type: str  # "exact" | "pattern" | "fuzzy" | "unmatched"
    certainty: float  # 0.0–1.0; exact=1.0, unmatched=0.0
    transform_applied: Optional[str] = None


@dataclass
class PatternSuggestion:
    pattern_type: str  # "prefix_removal" | "suffix_removal" | "case_normalization" | "delimiter" | "regex"
    description: str
    regex_pattern: Optional[str] = None
    example_before: Optional[str] = None
    example_after: Optional[str] = None
    match_count: int = 0


@dataclass
class TransformationRecipe:
    ref_column: str
    target_column: str
    steps: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_yaml(self) -> str:
        import yaml
        return yaml.dump({
            "ref_column": self.ref_column,
            "target_column": self.target_column,
            "steps": self.steps,
            "metadata": self.metadata,
        }, default_flow_style=False, allow_unicode=True)

    @classmethod
    def from_yaml(cls, text: str) -> "TransformationRecipe":
        import yaml
        data = yaml.safe_load(text)
        return cls(
            ref_column=data["ref_column"],
            target_column=data["target_column"],
            steps=data.get("steps", []),
            metadata=data.get("metadata", {}),
        )
