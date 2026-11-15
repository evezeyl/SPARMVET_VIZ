# Proposal: `.claude/rules/rules_app_structure.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked by listing `app/modules` and `app/handlers` against the directory map (lines 36-90), `wc -l app/src/server.py` (263), `git log` for the removed `exporter.py` of `app/modules` (deleted in `99a14148`), and reading `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py:501-514`.

## 1. Line 39, server.py size (FACT; and a rule is exceeded)

Today: `│   ├── server.py          # Thin orchestrator only (242 lines; hard limit ~250, see §3).`
Proposed: `│   ├── server.py          # Thin orchestrator only (263 lines on 2026-11-15; hard limit ~250, see §3).`
Why: `wc -l` gives 263. Section 3 says "MUST NOT grow beyond ~250 lines". The file is over the limit; this is a violation to report, not a fact to hide. Eve decides: move code into a handler, or raise the limit (CHANGES A RULE if raised). Not decided here.

## 2. Directory map, `exporter.py` (FACT)

Today (map, `modules/` list): `│   ├── exporter.py             # SubmissionExporter — gallery submission (imported only by tests today, F-20).`
Proposed: delete the line and add a tombstone note under the map: `> **REMOVED (commit 99a14148, "dead submission code removed"; ADR-093, 2026-11-08):** \`app/modules/exporter.py\` (SubmissionExporter) no longer exists. Tombstone expires two phases after this edit (add the task entry).`
Why: the file is not in `app/modules`; `grep` finds no reference to `SubmissionExporter` in `app` or `libs`.

## 3. Directory map, two missing modules (FACT)

Add to the `modules/` list (after `gallery_viewer.py`):
```
│   ├── gallery_examples.py     # check_gallery: the full check of every gallery example with the registries; draws one through the app's own path.
│   ├── gallery_listing.py      # What the gallery lists, and the "not shown, failed the check" block; a failed example is never listed or opened.
```
Why: both files exist in `app/modules` and are not in the map; their module docstrings give these purposes (first lines read).

## 4. Line 46, 71: ADR-089 (no change now)
`cache_keys.py` and the export key check cite ADR-089; ADR-101 replaces the key formula but is NOT BUILT (KEYS-NODE-1). Same marker as `rules_data_engine.md.proposal.md` change 2 if Eve wants it here; otherwise leave.

## 5. Line 109 and 111, navigator API (FACT, and a code point)

Today (line 109): `... \`schema_id → {schema_type, input_fields, wrangling, output_fields, …}\``; (line 111): `| \`load_fields_file(abs_path)\` | \`Path → dict\` | ADR-041 Rich Dict with ADR-014 unnesting |`
Proposed (line 109): `schema_id → {schema_type, input_fields, wrangling, …}`; (line 111): `... | ADR-041 Rich Dict; unwraps a single redundant \`input_fields\` wrapper key |`
Why: `output_fields` is removed (ADR-100 point 5) and ADR-014 is superseded (ADR-100). BUT the code still reads and unwraps `output_fields` (`data_analysis_recipe_navigator.py:12, 63, 131, 505-511`). So the rule text and the code disagree in the other direction: the proposal describes the target; a builder should remove the `output_fields` handling from the navigator (report; not done by me). Eve may prefer to leave the rule line until the code is changed.

## 6. Sections 3, 5, 6, 8 (no change), checked
Handler map, `define_server` contract, ownership matrix: every file named exists (handlers list above matches lines 78-90).

## Not settled
1. server.py over its limit (change 1).
2. Whether to describe the target (change 5) before the navigator code is cleaned.
