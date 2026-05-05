# TEST_LAB — Data Utility & Testing Suite

**Type:** User space  
**Status:** Partial build (`test_lab_studio.py` exists; most utilities not yet implemented)  
**Last updated:** 2026-05-05

---

## Purpose

TEST_LAB is a collection of small, focused utilities that help users prepare data for the app and test the app itself. It is not a single coherent workflow — it is a toolbox. Each tool solves one specific preparation or validation problem.

Primary audiences:
- **Data stewards** who need to reformat, clean, or anonymise data before loading into HOME.
- **Developers / testers** who need synthetic datasets (with controlled errors and edge cases) to validate the app's behaviour.
- **Manifest authors** who want a boilerplate starting point generated from their actual file structure.

---

## User Functionalities

### Data Reformatting

| Functionality | What the user can do |
|---|---|
| **XLSX → TSV/CSV** | Convert a multi-sheet Excel file to individual TSV or CSV files (one per sheet) |
| **CSV → TSV** | Reformat CSV files to TSV (standardise delimiter) |
| **Bulk reformat** | Process a folder of files in one operation |

### Manifest Scaffolding

| Functionality | What the user can do |
|---|---|
| **Boilerplate manifest from files** | Point TEST_LAB at a set of data files; it reads column names and types and generates a skeleton manifest YAML with correct column references, ready to edit in BLUEPRINT |

### Anonymisation / Synthetic Data

| Functionality | What the user can do |
|---|---|
| **Anonymise real data** | Take a real dataset; keep structure (columns, types, value ranges, factor levels) but replace all IDs and values with synthetic equivalents — safe to share |
| **Control synthetic value ranges** | Set min/max, allowed levels, or ID patterns for each column in the synthetic output |

### Test Dataset Generation

| Functionality | What the user can do |
|---|---|
| **Generate clean test data** | Create a well-formed dataset matching a given schema, for baseline testing |
| **Inject errors / edge cases** | Generate datasets with controlled defects: missing values, wrong types, duplicate IDs, out-of-range values, empty groups, single-row groups, etc. |
| **Named error scenarios** | Save and reload named edge-case scenarios to use as a regression test suite |

### Pattern Matching Helper

| Functionality | What the user can do |
|---|---|
| **ID pattern detection** | Analyse a column and suggest a regex or structural pattern for the IDs (reused by BLUEPRINT's auto-match helper) |
| **Column mapping suggestions** | Given two datasets, suggest which columns likely correspond based on name similarity, type, and value distribution |
| **Wrangling step suggestions** | Given a source and target schema, suggest the minimal sequence of wrangle/tidy steps to get from one to the other |

---

## Non-Goals

- TEST_LAB does not run the main analysis — that is HOME.
- TEST_LAB does not build or edit manifests beyond generating a boilerplate scaffold — that is BLUEPRINT.
- TEST_LAB does not curate or share recipes — that is GALLERY.
- TEST_LAB does not permanently store anonymised data on behalf of the user — it produces files the user downloads.

---

## Key Design Constraints

- **Stateless tools**: each TEST_LAB utility runs to completion and returns a file or a result. No persistent session state between tool invocations (except named test scenarios, which are saved as files).
- **No data leaves the server**: anonymisation and synthetic generation happen server-side; the user downloads the result. Raw data is never sent to an external service.
- **Pattern helper shared with BLUEPRINT**: the ID/column pattern matching logic should be the same component. Design for reuse from the start.
- **Positive inclusion** (ADR-071): TEST_LAB panel is only mounted when `test_lab_enabled` is true in persona config.
- **Audit trail**: file-generation operations should log what was produced (filename, schema, row count, generation parameters) to the session audit log.

---

## Code Modules

| Code module | Role |
|---|---|
| `test_lab_studio.py` | UI and server handlers for all TEST_LAB tools |

---

## Current State

- `test_lab_studio.py` exists as a module stub.
- Synthetic data generation: early experiment exists (referenced in recent commits as "test lab for synthetic data generation").
- Reformatting utilities: not yet built.
- Manifest scaffolding: not yet built.
- Pattern matching helper: not yet built.
- Named test scenarios: not yet built.

---

## Open Questions

- **Pattern helper**: shared component with BLUEPRINT, or separate implementations? Needs a decision before building either (to avoid duplication).
- **Anonymisation fidelity**: how closely should synthetic distributions match the real data? Full distributional match (harder, slower) vs. same types + plausible ranges (simpler, sufficient for most cases)?
- **Test scenario format**: how are named error scenarios stored? A JSON schema + generation params file seems cleanest. Where does it live (session dir? dedicated test_lab dir?)?
- **Boilerplate manifest scope**: should the scaffold include suggested wrangle steps, or only the column references? Starting with column references only keeps scope tight.
- **UI structure**: one tab per tool category, or a single list with a category filter? Start with tabs given the distinct tool types.
