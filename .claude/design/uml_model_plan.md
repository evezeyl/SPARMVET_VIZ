# UML model of SPARMVET_VIZ: plan (TOOLS-UML-3)

**Status:** PROPOSAL for Eve's review (2026-11-07), `[opus/high]`. Nothing is drawn yet.
**Model file:** `docs/UML/app.mdj` (StarUML). **Tool:** `OBSWORK/_bin/staruml/` (usage: `OBSWORK/_HELP/7_StarUML_Modeling_Workflow.md`).
**Findings so far:** `.claude/tasks/uml_findings.md`.

## 1. Goals

1. **Documentation:** one place that shows how the app is built and why.
2. **Understanding:** what a user does and what the code does in response, for users, data analysis recipe authors, operators and developers.
3. **Troubleshooting and discrepancy detection:** every element points to the code, the ADR and the test behind it, so a script can compare the model with the repo.

Not goals: drawing every function, generating code from the model, a diagram for its own sake. A diagram exists only if it answers a question in section 3.

## 2. Decisions

### D1. The model file is the single source of truth; no Mermaid copy

This replaces what I proposed earlier (Mermaid text for every diagram). StarUML is a *modelling* tool: one element, for example `DataOrchestrator`, appears in many diagrams, and renaming it once renames it everywhere. A Mermaid import creates a new element per diagram, so the same class would exist five times, and no script could follow a link from requirement to class to test. Two sources would also drift, which is the problem we want to find, not to add.

- `docs/UML/app.mdj` is JSON, so it is versioned in git and a Python script can read it without StarUML.
- Its diffs are noisy (coordinates, ids). So a script generates a readable text index (`docs/UML/model_index.md`: elements, relations, tags), and reviews read that plus the diagrams.
- Images (`docs/UML/images/*.svg`) are generated, and they carry the trial watermark until the licence is bought. They go into the Quarto docs after that.
- Mermaid stays for small inline diagrams in the docs (`rules_documentation_aesthetics.md`).

### D2. As-built and intended are both in the model, and they are labelled

The rules and ADRs describe what is intended; the code is what exists. They differ. Every element has a `status`: `implemented`, `partial`, `planned` or `deprecated`. Diagrams show `implemented` by default; anything else is visibly marked. A difference is not hidden in a drawing: it goes into the findings register (section 6).

### D3. Every element carries the same tags

StarUML elements have `tags`. These are what makes checking possible:

| Tag | Meaning | Example |
|---|---|---|
| `code` | File, and symbol if any | `app/modules/orchestrator.py:DataOrchestrator` |
| `adr` | Decision behind it | `ADR-089` |
| `rule` | Rule text | `rules_data_engine.md#1` |
| `test` | Test that proves it | `app/tests/test_cache_chain.py` |
| `flag` | App features flag that gates it | `t3_sandbox_enabled` |
| `status` | See D2 | `implemented` |

Checked with a throwaway probe through the bridge (deleted again, not saved): a requirement, a `Satisfy` relation, a tag on a class, a C4 person and a sequence diagram can all be created, and the tag and the relation are readable in the JSON. Tags print on the diagram by default, so views hide them to keep diagrams readable. A test is modelled as an artifact with a `Verify` relation to its requirement; I have not probed that one yet.

Names are the code's names, exactly. Vocabulary follows `CLAUDE.md` section 1: diagrams about use lead with user spaces (HOME, BLUEPRINT, TEST_LAB, GALLERY); diagrams about code lead with code modules.

### D4. Requirements are Eve's to confirm

A requirement says what "correct" means, so it is not mine to decide. I draft them from the ADRs and rules, each naming its source; Eve confirms, changes or deletes. IDs: `REQ-VIZ-<AREA>-nn` (areas: CFG, DATA, REPRO, AUDIT, EXP, UI, BP, GAL, LAB, DEP). SysML relations carry the links: `Satisfy` to the component, `Verify` to the test, `DeriveReqt` between requirements. First drafts in section 5.

### D5. One complete slice first, then the rest

Before drawing about 40 diagrams, one chain from requirement to test is built and checked by the script (section 5). If the method is wrong, we learn it after a few diagrams. Eve reviews each diagram, one at a time (TOOLS-UML-3).

## 3. Diagram catalogue

StarUML provides all of these natively (checked through the bridge, 2026-11-07). "Wave" is the order of work.

| ID | Question it answers | Type | For | Wave |
|---|---|---|---|---|
| **Requirements** | | | | |
| REQ-EXP | What must the export guarantee? | SysML requirement | all | 1 |
| REQ-CFG, REQ-DATA, REQ-AUDIT, REQ-UI | What must configuration, stored data, audit and the UI guarantee? | SysML requirement | all | 2 |
| **Context and users** | | | | |
| CTX-1 | Who and what does the app talk to? | C4 context | all | 2 |
| UC-HOME | What can a scientist do, under which flag? | Use case | user | 1 (export part), 2 |
| UC-BLUEPRINT, UC-GALLERY, UC-TESTLAB, UC-OPERATOR | Same for the other user spaces and for launching | Use case | user, operator | 2, 3 |
| ACT-SCIENTIST | Open, explore, send to audit, export | Activity | user | 2 |
| ACT-AUTHOR | TEST_LAB to BLUEPRINT to GALLERY to HOME (`developer_workflow.md`) | Activity | author | 3 |
| ACT-OPERATOR | Configure and launch; what stops the app | Activity | operator | 2 |
| **Structure** | | | | |
| C4-CONT | Process, files and folders at run time | C4 container | developer, operator | 2 |
| C4-COMP-HOME, C4-COMP-BLUEPRINT | Which handler and module owns what | C4 component | developer | 2, 3 |
| PKG-TIERS | Which library may import which (Tier 1, 2, 3) | Package | developer | 2 |
| CLS-EXPORT | Classes and functions of the export path | Class | developer | 1 |
| CLS-CONFIG, CLS-ENGINE, CLS-VIZ, CLS-CONNECTOR | Core contracts, public parts only | Class | developer | 2, 3 |
| **Behaviour** | | | | |
| SEQ-EXPORT | From click to bundle, with the key check | Sequence | developer | 1 |
| SEQ-LAUNCH | How deployment, app features and data analysis recipe are resolved | Sequence | developer, operator | 2 |
| SEQ-OPEN | Data analysis recipe to Tier 1, Tier 2, plot, with cache keys | Sequence | developer | 2 |
| SEQ-AUDIT | Exploration filter versus send to audit and Apply | Sequence | developer | 2 |
| SEQ-SESSION, SEQ-BLUEPRINT | Save and restore; edit, apply, save | Sequence | developer | 3 |
| STM-STAGE | When is a stored stage valid, rebuilt or removed? | State machine | developer | 2 |
| STM-NODE | Life of an audit step | State machine | developer | 2 |
| STM-VIEW | "Data to show" and "Plot to show" (ADR-086) | State machine | user, developer | 3 |
| STM-STARTUP | Which configuration errors stop the app | State machine | operator | 3 |
| COM-REACTIVE | Which output reads which reactive value (the cause of the blank page and the sidebar bug) | Communication | developer | 2 |
| **Data and configuration** | | | | |
| DM-CONFIG | Deployment, app features, launch variables and precedence | Class | operator, developer | 2 |
| DM-DATA-ANALYSIS-RECIPE | Structure of a data analysis recipe | Class | author | 2 |
| DM-ARTIFACTS | Stored stages and keys, session files, export bundle | Class | developer | 2 |
| **Deployment** | | | | |
| DEP-LOCAL | Local and container | Deployment | operator | 3 |
| DEP-PLATFORMS | Galaxy, IRIDA, Posit Connect; `planned` until checked (#28) | Deployment | operator | 3 |

Model tree: `00 Requirements`, `10 Context and users`, `20 Structure`, `30 Behaviour`, `40 Data and configuration`, `50 Deployment`.

Left out on purpose: timing, parametric, composite structure, BPMN, cloud diagrams (no question needs them). Wireframes could later show the panels of each user space; `ui_panel_map_current.md` covers that today.

## 4. Discrepancy checks

`assets/scripts/audit_uml_model.py` reads the model file, needs no StarUML, runs with the other audits and exits non-zero on a finding. It is tested with planted errors.

| Check | Finds |
|---|---|
| Every `code` tag resolves (file exists, symbol found with `ast`) | Renamed or deleted code, stale model |
| Every `test` tag resolves to an existing test | A claim of verification with nothing behind it |
| Every requirement has at least one `Satisfy` and one `Verify` | Requirements without code or without a test |
| Every `adr` tag exists and is not superseded | Model built on an old decision |
| Every `flag` tag is a real flag; use cases per flag agree with the flag matrix | UI promises a flag does not gate |
| Library dependencies in PKG-TIERS equal the real imports, and obey the tier rule | Forbidden imports; a rule that no longer matches |
| Modules with `@deps` blocks appear in the model (coverage list) | Code the model does not know about |
| Message names in sequence diagrams exist as functions | Sequence drawn from memory |

**What it cannot do:** it checks names, links and structure. It does not prove that the code runs in the order a sequence diagram shows. Behaviour is proven by the tests the model points to.

**Troubleshooting use:** from a symptom, find the use case, follow it to the sequence and the flags, then to the code and the test. If no test exists on that path, that is the first finding.

## 5. Wave 1: the export slice

Why export: it is where "science must be correct" matters most, the rules are precise (`ui_implementation_contract.md` section 7.2), and real tests exist.

Draft requirements for Eve to confirm:

| ID | Requirement | Source | Satisfied by | Verified by |
|---|---|---|---|---|
| REQ-VIZ-EXP-01 | If the data analysis recipe files or the data changed since the view was opened, nothing is exported and the user is told why | contract 7.2 rule 1, ADR-089 | `export_handlers.py` | `test_export_download.py::test_a_data_change_after_the_view_is_opened_blocks_the_export` |
| REQ-VIZ-EXP-02 | Exploration filters are never exported, from any view | contract 7.2 rule 4, issue #25 | `export_handlers.plot_content_rules` | `test_export_download.py::test_exploration_filters_are_never_exported` |
| REQ-VIZ-EXP-03 | Audited steps are always applied to that plot's export and recorded | contract 7.2 rule 4 | `export_handlers.audited_frame` | `test_export_view_consistency.py::test_audited_rows_and_drops_are_exported` |
| REQ-VIZ-EXP-04 | The bundle records the recipe hash, the data hash and the keys of each dataset | contract 7.2 rule 5, ADR-089 | `export_handlers.py` | `test_export_download.py::test_the_bundle_records_the_keys_and_has_the_data` |

Steps, each reviewed by Eve: (1) REQ-EXP, (2) UC-HOME export part, (3) SEQ-EXPORT, (4) CLS-EXPORT, (5) first version of the script on these, with one planted error of each kind. Done when the script passes on the slice and fails on each planted error. Then we decide together whether the method is right before wave 2.

## 6. Findings register

`.claude/tasks/uml_findings.md` lists every difference between model, code and documents: what differs, where, and the decision (change the code, change the document, or change the decision). Findings that need work become issues. Modelling is expected to produce these; they are a result, not a failure.

## 7. Working rules

- StarUML holds the model in memory. Save before `git commit`. After `git checkout` or `git pull` that changes the file, reopen it in StarUML, otherwise the old copy in memory overwrites the new one on the next save.
- Commit after each reviewed diagram: the model file, the index, and nothing else.
- A code change that alters something in the model updates the model in the same commit (same rule as the docs). The script enforces the links.
- Eve and an agent can work in the same open model; only one at a time, because they share one undo history.

## 8. Effort

| Work | Tag |
|---|---|
| This plan, conventions, requirement drafts | `[opus/high]` |
| Wave 1 slice, including the first checks | `[opus/high]` for the requirements, `[sonnet/high]` for the drawing and the script |
| Wave 2 and 3 diagrams, read from the code and verified against it | `[sonnet/high]` |
| Rest of the checks, audit registry entry, docs page | `[sonnet/medium]` |
