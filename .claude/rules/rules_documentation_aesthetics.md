---
trigger: always_on
deps:
  provides: [rule:violet_law, rule:quarto_mermaid_standards, rule:css_theme_standards, rule:doc_sync]
  documents: [docs/]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# Documentation & Aesthetics Standards (rules_documentation_aesthetics.md)

**Authority:** Enforced on all Human-Facing Artifacts & Code Mirrors

This rulebook merges documentation strategies and aesthetic constraints into a unified "Dev-to-User" architecture.

## 1. The Code-Documentation Synchronization Mandate

**CRITICAL:** Documentation and code MUST be kept in sync.

- Any changes in code logic, function signatures, class naming, or broad refactoring MUST be actively reflected in the appropriate user documentation (`docs/*.qmd`) and the relevant library `README.md`.
- No refactoring or renaming task is considered [DONE] until its documentation footprint has been updated.

## 2. The Split-Documentation Strategy

- **Primary Guides (`foundations/`, `workflows/`):** Compressed, technical, focused on "Why" and "Flow". Provide rapid high-level overviews for developers.
- **Appendix Galleries (`appendix/`):** Step-by-step exhaustive user manuals focused on "Copy-Paste" recipes and "How-To". Example: All pipelines and visual components MUST include concrete YAML usage examples ("Recipes") for non-programmers.

## 3. The Violet Law (Documentation Standard ONLY)

Agents MUST use the explicit 'Violet' standard format when referring to architectural components in **HUMAN-FACING DOCUMENTATION ONLY** (`.qmd` files, README 'Key Components' lists).

- **Format:** `ComponentName (file_name.py)`
- **Examples:** `DataWrangler (data_wrangler.py)`, `VizFactory (viz_factory.py)`.
- **PROHIBITION:** The Violet standard MUST NOT be used for functional variable names, filenames, class definitions, or docstrings within the actual execution logic.

## 4. Documentation DRY Rule

- **No Source Repetition:** Never repeat source code or data content. Use Quarto's `{{< include path/to/script.py >}}` derivative or relative links.
- **Master Source:** `docs/` is the absolute source of truth for the human reader at project end.

## 5. Visual & Aesthetic Standards

- **Inline Code Blocks:** Use the 'Deep Violet' CSS theme for all **DOCUMENTATION** inline code blocks (`background: #3a2a4d`, `color: #e0cffc`).
- **Mermaid Diagrams:** Large interactive diagrams must be wrapped in a `::: {.lightbox}` div to enable click-to-zoom in Quarto formatting.
- **Plotting Themes:** Functional plotting themes in `libs/viz_factory/` MUST use standard descriptive names (e.g., `theme_minimal`, `theme_dashboard`). Do NOT use 'violet' as a prefix for functional logic.
