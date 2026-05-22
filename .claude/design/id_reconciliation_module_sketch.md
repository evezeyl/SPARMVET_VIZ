# ID Reconciliation Library — Module Structure Sketch

> **HISTORICAL (superseded by TL-IDLIB-TESTS-1, 2026-05-22):**
> This was the pre-build architecture sketch. The library has been built and is in production.
> Authoritative structure is in `rules_test_lab.md §8` and the actual source files.
> Key divergence from this sketch: `PatternSuggestion`, `detect_patterns`, `apply_pattern`,
> and `suggest_regex` live in `libs/utils/src/utils/id_patterns.py`, not in `data_structures.py`.

**File:** `libs/id_reconciliation/`  
**Status:** HISTORICAL — library built 2026-05-22  
**Purpose:** Pure utility library for validating & transforming ID alignment across multiple data files.

---

## Module Layout

```
libs/id_reconciliation/
├── pyproject.toml                          # Depends on: polars, utils only
├── src/
│   └── id_reconciliation/
│       ├── __init__.py                     # Public API exports
│       ├── core.py                         # Main orchestrator
│       ├── matcher.py                      # Matching engines (exact, fuzzy, pattern)
│       ├── pattern_detector.py             # Pattern suggestion & application
│       ├── recipe.py                       # Transformation recipe format & persistence
│       └── data_structures.py              # MatchResult, PatternSuggestion, etc.
└── tests/
    ├── conftest.py
    └── test_*.py                           # Unit tests for each module
```

---

## Data Structures (data_structures.py)

```python
@dataclass
class IDPair:
    """Single (left_id, right_id) match."""
    left_id: str
    right_id: str
    certainty: float  # 0.0–1.0
    match_type: str  # "exact" | "pattern" | "fuzzy" | "manual" | "unmatched"
    transformation_steps: list[str]  # ["remove_prefix('sample_')", "extract_delimiter('_', 0)"]

@dataclass
class PatternSuggestion:
    """A suggested transformation rule."""
    pattern: str  # e.g., "remove_prefix"
    params: dict  # e.g., {"prefix": "sample_"}
    applied_to: str  # "source" | "target"
    expected_matches: int  # How many unmatched IDs would this rule fix?
    expected_certainty: float  # 0.8–0.99 for pattern matches

@dataclass
class MatchResult:
    """Result of a pairwise matching operation."""
    source_ids: list[str]
    target_ids: list[str]
    matched_pairs: list[IDPair]  # All pairs (100%, <100%, unmatched)
    unmatched_source: list[str]
    unmatched_target: list[str]
    transformation_history: list[str]  # Audit trail
    summary: dict  # {"total_source": 455, "matched": 452, "unmatched_source": 3, ...}

@dataclass
class TransformationRecipe:
    """Reusable recipe for ID transformation."""
    metadata: dict
      # {"source_file": "...", "target_file": "...", 
      #  "source_id_column": "...", "target_id_column": "...",
      #  "created_at": "...", "verified_by": "..."}
    
    transformation_steps: list[dict]
      # [{"step": 1, "action": "remove_prefix", "pattern": "sample_", "applied_to": "source"}, ...]
    
    match_summary: dict
      # {"total_source": 455, "total_target": 454, "matched": 452, ...}
    
    audit_log: list[str]
      # ["Step 1: Removed 'sample_' prefix from 455 IDs", ...]
    
    many_to_many_pairs: list[tuple]  # [(left_id, [right_id_1, right_id_2]), ...]
      # Detected but user confirmed ("suppressed")

class TransformationRecipe:
    @classmethod
    def from_yaml(cls, filepath: str) -> "TransformationRecipe": ...
    
    def to_yaml(self, filepath: str) -> None: ...
    
    def apply_to_ids(self, ids: list[str], which_side: str) -> list[str]:
        """Apply transformation steps to a list of IDs."""
        ...
```

---

## Public API (core.py & __init__.py)

### Main Orchestrator

```python
class IDReconciliationEngine:
    """Main entry point for ID matching & recipe generation."""
    
    def __init__(self, verbose: bool = False):
        ...
    
    # === PHASE 1: Pre-Check ===
    def precheck_compatibility(self, file_metadata: list[dict]) -> PreCheckResult:
        """
        Analyze 2+ files to determine format compatibility & suggest matching order.
        
        Args:
            file_metadata: [
                {"filepath": "...", "id_column": "...", "sample_ids": [...10 samples...]},
                ...
            ]
        
        Returns:
            PreCheckResult(
                compatible_groups: [["file_A", "file_B"], ["file_C", "file_D"]],
                suggested_order: ["A→B", "AB→C", "ABC→D"],
                format_analysis: {
                    "file_A": "clean_ids (no delimiters, consistent prefix)",
                    "file_B": "clean_ids_variant (slight case variation)",
                    "file_C": "delimiter_based (IDs within '_'-separated fields)",
                    ...
                }
            )
        """
        ...
    
    # === PHASE 2: Pairwise Matching ===
    def match_pair(self, 
                   source_ids: list[str],
                   target_ids: list[str],
                   source_name: str = "source",
                   target_name: str = "target") -> MatchResult:
        """
        Match two sets of IDs with pattern detection & certainty scoring.
        
        Returns:
            MatchResult with:
            - matched_pairs (list[IDPair]): all matches (100%, <100%, unmatched)
            - unmatched_source: IDs from source with no target match
            - unmatched_target: IDs from target with no source match
            - transformation_history: audit trail of patterns applied
        """
        ...
    
    # === PHASE 3: Pattern Detection ===
    def suggest_patterns(self, 
                        source_ids: list[str],
                        target_ids: list[str],
                        unmatched_source: list[str]) -> list[PatternSuggestion]:
        """
        Suggest transformation rules to match remaining unmatched IDs.
        
        Detects & ranks:
        - Prefix/suffix removal
        - Delimiter extraction
        - Case normalization
        - Substring extraction
        - Regex patterns
        
        Returns:
            [
                PatternSuggestion("remove_prefix", {"prefix": "sample_"}, "source", 
                                 expected_matches=3, expected_certainty=0.95),
                ...
            ]
            Sorted by: (expected_matches DESC, expected_certainty DESC, simplicity ASC)
        """
        ...
    
    # === PHASE 4: Apply Transformation ===
    def apply_pattern(self,
                     match_result: MatchResult,
                     pattern: PatternSuggestion) -> MatchResult:
        """
        Apply a pattern to the match result & return updated matches.
        
        Re-runs matching after transformation, updates audit log.
        """
        ...
    
    # === PHASE 5: Recipe Generation ===
    def generate_recipe(self,
                       source_file: str,
                       target_file: str,
                       source_id_column: str,
                       target_id_column: str,
                       final_match_result: MatchResult,
                       verified_by: str = "user") -> TransformationRecipe:
        """
        Generate a reusable transformation recipe from final match result.
        
        Stores:
        - Transformation steps applied
        - Match summary
        - Audit log
        - Detected many-to-many pairs (if any)
        """
        ...

# === Utility Functions (lower-level) ===

def detect_many_to_many(matched_pairs: list[IDPair]) -> list[tuple]:
    """
    Identify any many-to-many relationships in matched pairs.
    
    Returns: [(left_id, [right_id_1, right_id_2, ...]), ...]
    """
    ...

def format_match_table(match_result: MatchResult, 
                      max_rows: int = 100) -> str:
    """
    Format MatchResult as a readable side-by-side table (text/markdown).
    
    Used by TEST_LAB UI to display results.
    """
    ...

def apply_recode_step(ids: list[str],
                     action: str,  # "trim_whitespace", "extract_substring", etc.
                     params: dict) -> tuple[list[str], str]:
    """
    Apply a single data cleaning action to a set of IDs.
    
    Returns: (cleaned_ids, audit_message)
    
    Actions:
    - "trim_whitespace": no params
    - "remove_special_chars": no params
    - "extract_substring": {"start": 0, "end": 4} or {"delimiter": "_", "position": 0}
    - "case_normalize": {"to": "upper"|"lower"}
    - "regex_replace": {"pattern": r"...", "replacement": "..."}
    """
    ...
```

---

## How TEST_LAB & BLUEPRINT Integrate

### TEST_LAB (test_lab_studio.py)

```python
from id_reconciliation import IDReconciliationEngine

class TestLabStudio:
    def __init__(self, session_id: str):
        self.engine = IDReconciliationEngine(verbose=True)
    
    @render.ui
    def id_reconciliation_tool_ui(self):
        """Render the ID Reconciliation Tool panel."""
        return ui.div(
            ui.h3("ID Reconciliation"),
            ui.input_file("upload_files", "Upload data files (2–6)", multiple=True),
            ui.output_ui("precheck_results"),
            ui.output_ui("pairwise_matcher"),
        )
    
    @reactive.Effect
    def _run_precheck(self):
        files = input.upload_files()
        if not files:
            return
        
        file_metadata = [{"filepath": f.name, "id_column": "auto-detect", ...} for f in files]
        result = self.engine.precheck_compatibility(file_metadata)
        # Display suggestion to user
    
    def _handle_pairwise_match(self, source_file, target_file):
        """User selects a pair to match."""
        source_ids = self._load_ids(source_file, column="auto")
        target_ids = self._load_ids(target_file, column="auto")
        
        match_result = self.engine.match_pair(source_ids, target_ids)
        # Display in side-by-side table
        
        # Offer pattern suggestions
        patterns = self.engine.suggest_patterns(source_ids, target_ids, 
                                                match_result.unmatched_source)
        # User verifies matches, applies patterns, etc.
        
        # Generate recipe
        recipe = self.engine.generate_recipe(
            source_file, target_file, "id", "id",
            final_match_result, verified_by="eve"
        )
        recipe.to_yaml(f"user_sessions/{session_id}/recipe_{source_file}_{target_file}.yaml")
```

### BLUEPRINT (Manifest Scaffolding)

```python
from id_reconciliation import IDReconciliationEngine, TransformationRecipe

class WrangleStudio:
    def scaffold_manifest_from_files(self, uploaded_files: list[str]) -> str:
        """
        Generate a boilerplate manifest from uploaded data files.
        
        Step 1: ID Reconciliation (PREREQUISITE)
        """
        engine = IDReconciliationEngine()
        
        # Pre-check compatibility
        file_metadata = [...]
        precheck = engine.precheck_compatibility(file_metadata)
        
        # Run all pairwise matches (assume user has already verified via TEST_LAB tool)
        # OR: call reconciliation inline & prompt user in UI
        
        # Load or generate recipes
        recipes = [TransformationRecipe.from_yaml(recipe_file) 
                   for recipe_file in self._find_saved_recipes(uploaded_files)]
        
        # Apply recipes to build join graph
        join_manifests = self._build_join_recipes(recipes)
        
        # Generate boilerplate manifest
        manifest_yaml = self._generate_manifest_boilerplate(join_manifests)
        
        return manifest_yaml
```

---

## Dependencies & Imports

### pyproject.toml

```toml
[project]
name = "id_reconciliation"
version = "0.1.0"
dependencies = [
    "polars>=1.0",
    "utils",  # Only utils from SPARMVET libs (Tier 1 base)
]

[project.optional-dependencies]
dev = ["pytest", "pytest-cov"]
```

**Rule:** Zero imports from other domain libs (transformer, ingestion, viz_factory, etc.).  
Only stdlib, polars, and utils (Tier 1).

---

## Testing Strategy

```python
# tests/test_core.py

def test_exact_match():
    """100% exact matches should not require user verification."""
    engine = IDReconciliationEngine()
    result = engine.match_pair(
        source_ids=["S001", "S002"],
        target_ids=["S001", "S002"]
    )
    assert all(p.certainty == 1.0 for p in result.matched_pairs)

def test_pattern_suggestion():
    """Engine suggests prefix removal when IDs differ by prefix."""
    engine = IDReconciliationEngine()
    result = engine.match_pair(
        source_ids=["sample_S001", "sample_S002"],
        target_ids=["S001", "S002"]
    )
    # First match should be exact on transformed IDs
    # Pattern suggestion should appear
    patterns = engine.suggest_patterns(
        result.source_ids,
        result.target_ids,
        result.unmatched_source
    )
    assert any(p.pattern == "remove_prefix" and p.params["prefix"] == "sample_" 
               for p in patterns)

def test_many_to_many_detection():
    """Many-to-many relationships should be flagged."""
    engine = IDReconciliationEngine()
    # Scenario: S001 → exists in target as both S001 and S001_QC_pass
    ...

def test_recipe_persistence():
    """Recipe should be saveable & loadable."""
    recipe = TransformationRecipe(...)
    recipe.to_yaml("/tmp/recipe.yaml")
    loaded = TransformationRecipe.from_yaml("/tmp/recipe.yaml")
    assert loaded == recipe

def test_recode_workflow():
    """User should be able to clean IDs via recode actions."""
    cleaned_ids, msg = apply_recode_step(
        ["sample_S001", "sample_S002"],
        "remove_special_chars",
        {}
    )
    assert cleaned_ids == ["sample_S001", "sample_S002"]  # No special chars anyway
    
    # Extraction example
    cleaned_ids, msg = apply_recode_step(
        ["toolA-S001", "toolB-S002"],
        "extract_substring",
        {"delimiter": "-", "position": 1}
    )
    assert cleaned_ids == ["S001", "S002"]
```

---

## API Surface Summary (for user review)

**Core Classes:**
- `IDReconciliationEngine` — main orchestrator
- `IDPair` — single matched pair with certainty
- `MatchResult` — result of pairwise matching
- `PatternSuggestion` — suggested transformation rule
- `TransformationRecipe` — reusable recipe (persisted as YAML)

**Main Methods:**
- `precheck_compatibility(file_metadata)` → PreCheckResult
- `match_pair(source_ids, target_ids)` → MatchResult
- `suggest_patterns(source_ids, target_ids, unmatched)` → list[PatternSuggestion]
- `apply_pattern(match_result, pattern)` → MatchResult
- `generate_recipe(...)` → TransformationRecipe

**Utility Functions:**
- `detect_many_to_many(matched_pairs)` → list[tuple]
- `format_match_table(match_result)` → str (for UI display)
- `apply_recode_step(ids, action, params)` → tuple[list[str], str]

**No external dependencies:** Only polars + utils (Tier 1).

---

## Open Design Questions (for Eve's review)

1. **Progressive matching batch size** — should the preview batch be 100 rows, 200 rows, random sampling, or stratified sampling? Currently unspecified.

2. **Fuzzy matching algorithm** — should we use Levenshtein distance, token-based similarity (e.g., token_set_ratio from fuzzywuzzy), or something else? Not detailed in sketch.

3. **Pattern ranking heuristics** — current idea is (expected_matches DESC, expected_certainty DESC, simplicity ASC). Should complexity/risk factor in?

4. **Recode action extensibility** — the action set is hardcoded (trim, extract, regex, etc.). Should users be able to define custom actions? Or JSON-based action definitions?

5. **Recipe reuse caching** — when user imports the same file types again, should TEST_LAB auto-detect & suggest applying the saved recipe? Or always run fresh matching?

6. **Integration with Manifest Scaffolding UI** — should recipes be generated inside TEST_LAB (standalone), or should BLUEPRINT call the engine inline & prompt user for verification? Currently assuming both are possible.

