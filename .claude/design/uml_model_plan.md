# UML model of SPARMVET_VIZ: plan (TOOLS-UML-3)

**Status:** in use (Eve, 2026-11-07). Scope is cut to what helps the demo: 10 work days for fixes, testing and the demo.
**Model file:** `docs/UML/app.mdj` (StarUML). **Tool:** `OBSWORK/_bin/staruml/` (usage: `OBSWORK/_HELP/7_StarUML_Modeling_Workflow.md`).
**Findings:** `.claude/tasks/uml_findings.md`.

## 1. Goals, for now

1. Understand the key points: how the app is built and what a user does on HOME.
2. Find discrepancies between code, rules and documents, so the fixes before the demo are the right ones.

Documentation is a side effect, not the aim. A diagram exists only if it answers a question in section 3. No diagram of every function, no code generation. Eve does not review each diagram: she sees the findings that need a decision.

## 2. Decisions

- **D1. All diagrams are in StarUML; the model file is the single source of truth.** One element appears in many diagrams and is renamed once. The file is JSON, so a script can read it without StarUML. No Mermaid: the existing Mermaid diagrams in 8 `docs/` pages render badly and are replaced by StarUML images later (TOOLS-UML-4, after the licence, because of the trial watermark).
- **D2. The model shows the current truth only.** What exists and what is in force today. No history: no superseded ADRs, no old designs, nothing planned. The ADR log keeps the history as text. An intended thing that is not built is not drawn: it is a finding.
- **D3. Elements carry tags that a script can check:** `code` (file and symbol), `adr` (only the ADR that governs it today), `rule`, `test`, `flag`. Names are the code's names. Views hide the tags, so diagrams stay readable. Vocabulary follows `CLAUDE.md` section 1.
- **D4. Requirements only where they prevent a wrong result.** Drafted from current ADRs and rules, each naming its source. Eve is asked only when sources conflict or none exists.

## 3. Diagrams for the demo

Order follows the common practice: context and containers first, then the key runtime flows, components only where needed, code level left out.

| ID | Question | Type | View |
|---|---|---|---|
| **Architecture** | | | |
| CTX-1 | Who and what does the app talk to? | C4 context | scenarios, logical |
| C4-CONT | What runs, and which files and folders does it use? | C4 container | logical, physical |
| PKG-TIERS | Which library may import which? | Package | development |
| DEP-DEMO | How does the demo run? | Deployment | physical |
| **HOME** | | | |
| UC-HOME | What can a user do, under which flag? | Use case | scenarios |
| C4-COMP-HOME | Which handler and module owns what? | C4 component | logical |
| COM-REACTIVE | Which output reads which reactive value? (cause of the blank page and the sidebar bug) | Communication | process |
| SEQ-LAUNCH | How are deployment, app features and data analysis recipe resolved, and what stops the app? | Sequence | process |
| SEQ-OPEN | Data analysis recipe to Tier 1, Tier 2, plot, with the cache keys | Sequence | process |
| STM-STAGE | When is a stored stage valid, rebuilt or removed? | State machine | process |
| SEQ-AUDIT | Exploration filter against send to audit and Apply | Sequence | process |
| SEQ-EXPORT | From click to bundle, with the key check | Sequence | process |
| **Data** | | | |
| DM-CONFIG | Deployment, app features, launch variables, precedence | Class | logical |
| REQ-CORE | Quality goals and the requirements that protect a correct result | SysML requirement | all |

Three text pages go with them, because no diagram shows them well: **quality goals** (correct science and reproducibility first), **cross-cutting concepts** (configuration, error handling, provenance, security) and **risks and technical debt**. They live next to the model in `docs/UML/`.

**After the demo, if still useful:** BLUEPRINT, GALLERY and TEST_LAB use cases and components, class diagrams of the core, data analysis recipe data model, other platforms. Only if the demo shows those user spaces do they move up.

## 4. Outside check of this plan

Compared with arc42 (12 sections), the C4 model, and Kruchten's 4+1 views with ISO 42010 (each view states who it is for and what concern it answers):

- Starting with architecture, then HOME, is what C4 practice advises: context and containers first, dynamic diagrams for key flows, components selectively, code level optional. My first plan started from one export slice and drew class diagrams too broadly. Changed.
- The first plan was missing, against arc42: quality goals, constraints, cross-cutting concepts and risks. Added above. Security was missing entirely and already gave a finding (F-13).
- All four 4+1 views are covered by the set above; scenarios are UC-HOME and CTX-1.

## 5. Discrepancy checks

`assets/scripts/audit_uml_model.py`, small, run with the other audits, tested with a planted error for each check:

| Check | Finds |
|---|---|
| Every `code` tag resolves (file and symbol) | Renamed or deleted code |
| Every `test` tag resolves | A claim of proof with nothing behind it |
| Every `adr` tag exists and is not superseded | Model built on an old decision |
| Every `flag` tag is a real flag | UI promises a flag does not gate |
| Library arrows in PKG-TIERS equal the real imports | Forbidden imports, a rule that no longer matches |

It checks names and links. It does not prove that the code runs in the order a sequence diagram shows; the tests do that.

## 6. Working rules

- StarUML holds the model in memory. Save before `git commit`. After a `git checkout` or `git pull` that changes the file, reopen it, otherwise the old copy overwrites the new one on the next save.
- Commit the model file by name after each diagram.
- Every difference found goes into the findings register. Findings that need work become issues.
- Tags: `[opus/high]` for this plan and the architecture diagrams, `[sonnet/high]` for the HOME diagrams read from code, `[sonnet/medium]` for the script.

## Sources

[arc42 sections](https://examples.arc42.org/sections/), [C4 model](https://c4model.com/), [C4 modelling guide](https://barkingiguana.com/writing/the-workshop-c4-modelling/), [Kruchten 4+1](https://arxiv.org/pdf/2006.04975), [views and viewpoints](https://btabok.iasaglobal.org/btabok_3/capability-descriptions/views-and-viewpoints/).
