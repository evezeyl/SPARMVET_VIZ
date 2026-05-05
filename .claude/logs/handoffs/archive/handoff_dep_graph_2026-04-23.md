# Handoff: Dependency Tracking System (`@deps`) — 2026-04-23

**Author:** @dasharch (Claude Sonnet 4.6)
**Type:** Infrastructure — new system, not a bug fix or feature
**Status:** Pilot complete (12 files annotated). Ready to extend.

---

## What was built and why

### Problem

When modifying a file in this project (e.g. `orchestrator.py`, an action decorator, a rule file),
there was no reliable way to know which other files needed to be checked or updated. The result
was silent divergence — `debug_assembler.py` drifting from `orchestrator.py`, action renames
not propagating to rule §8 tables, manifests using stale key names.

### Solution: `@deps` annotation blocks

Every significant file now carries a structured annotation block in its natural comment syntax.
The annotation declares:
- **what the file provides** (registered names, classes, rules)
- **what it consumes** (from other files, by file path or semantic tag)
- **what mirrors it** (files that must stay behaviourally in sync — highest risk coupling)
- **what documents it** (the rule/ADR that governs its interface)
- **what is consumed by it** (explicit backlinks)

This is a file-local system: the information lives IN the file, not in a separate index.
The index (`dependency_index.md`) is auto-generated from the annotations, not hand-maintained.

---

## Files created/modified

| File | Role |
|---|---|
| `.agents/rules/workspace_standard.md` §5 | **Specification** — format, keywords, usage commands, scope |
| `assets/scripts/build_dep_graph.py` | **Scanner + emitter** — greps `@deps` blocks, builds `dep_graph.json`, regenerates `dependency_index.md` |
| `assets/dep_graph.html` | **Interactive viewer** — standalone Cytoscape HTML, no server needed. Open in browser. Loads `tmp/dep_graph.json`. Colour palette mirrors the TubeMap (`_CY_COLOURS` in `blueprint_mapper.py`). |
| `.antigravity/knowledge/dependency_index.md` | **Auto-generated index** — do NOT edit by hand. Run `build_dep_graph.py` to refresh. |
| `tmp/dep_graph.json` | **Cytoscape elements** — generated output, re-created on each run |

### Annotated files (pilot — extend as needed)

| File | Coupling types demonstrated |
|---|---|
| `app/modules/orchestrator.py` | `provides`, `mirrors`, `consumes`, `consumed_by` |
| `libs/transformer/tests/debug_assembler.py` | `mirrors` (sync pair with orchestrator) |
| `libs/transformer/src/transformer/data_assembler.py` | `provides`, `consumed_by`, `doc` |
| `libs/transformer/src/transformer/data_wrangler.py` | `provides`, `consumed_by`, `doc` |
| `libs/transformer/src/transformer/actions/cleaning/expressions.py` | `provides` (action registration) |
| `libs/ingestion/src/ingestion/ingestor.py` | `provides`, `consumed_by`, `doc` |
| `libs/viz_factory/tests/debug_gallery.py` | `consumes`, `consumed_by`, `doc` |
| `config/manifests/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml` | `provides`, `consumes`, `include_parent` |
| `.agents/rules/rules_manifest_structure.md` | `provides` (rules), `documents`, `consumed_by` |
| `.agents/rules/rules_persona_bioscientist.md` | `provides` (rules), `documents`, `consumes` |

---

## How agents use this system

### Before modifying any file

```bash
# 1. Read the file's @deps block
grep -A 10 "@deps" path/to/the/file.py

# 2. Find everything that consumes what this file provides
grep -r "consumes:.*DataAssembler" . --include="*.py" --include="*.yaml" --include="*.md"

# 3. Find everything that mirrors this file (must stay in sync)
grep -r "mirrors:.*orchestrator" . --include="*.py"
```

### After adding @deps to a new file / changing annotations

```bash
.venv/bin/python assets/scripts/build_dep_graph.py
# → refreshes tmp/dep_graph.json and .antigravity/knowledge/dependency_index.md
```

### Interactive exploration

Open `assets/dep_graph.html` in a browser. Either:
- Use "Load JSON" button → select `tmp/dep_graph.json`
- Or serve the project root with `python3 -m http.server` and the HTML auto-loads the JSON

Features:
- Click a node → highlights its direct dependencies and dependents
- Filter by file name substring (search bar)
- Filter by coupling type (consumes / mirrors / documents / include_parent / consumed_by)
- Fit button resets the view
- Edge colours: red = mirrors (sync risk), grey = consumes, orange = documents, blue = include_parent, dashed = consumed_by

---

## 7 coupling types

| Keyword | What it means | Required action when source changes |
|---|---|---|
| `provides:` | Names/contracts this file exports | Find all `consumes:` and `consumed_by:` referencing these names |
| `consumes:` | Names/contracts from another file this file depends on | If provider renames/removes: update this file |
| `mirrors:` | Must stay **behaviourally in sync** with this file | Read both files together; any logic change in one → change in other |
| `documents:` | This file is the human description of that file's interface | Update when the documented file's interface changes |
| `doc:` | The rule/ADR governing this file | Read before changing; update after if interface changed |
| `include_parent:` | This file is `!include`-d by that manifest | Moving/renaming this file breaks that manifest |
| `consumed_by:` | Backlink: these files depend on this one | Grep these before changing this file's interface |

---

## What to annotate going forward

Add `@deps` blocks to:
- Any new Python module that registers actions or components
- Any new core library module
- Any new debug script
- Any new rule file (use frontmatter `deps:` key)
- Assembly recipe files (`# @deps` block with `provides:`, `consumes:`, `include_parent:`)

Do NOT annotate: test data TSVs, one-off utility scripts, generated files.

---

## Known limitations / next steps

- **Semantic tags** (`action:cast`, `dataset:foo`) appear in `consumes:` but currently produce no graph edges — they are human-readable reminders only. A future enhancement could build a separate "action registry" node layer to make these visual.
- **`consumed_by: any YAML manifest`** in action files is too broad to resolve to graph edges. As manifests get annotated, these will become specific.
- **The remaining action files** (`core.py`, `analytical.py`, `advanced.py`, `relational/joins.py`, etc.) are not yet annotated. Add `@deps` blocks to them when they are next modified.
- The viewer auto-loads JSON only when served via HTTP (not `file://`). For local use without a server, use the Load JSON button.
