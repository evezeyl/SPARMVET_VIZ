# Audit planning review: agenda for 2026-11-12

**Written for:** Eve and the Claude session that reviews the audit plan with her. **Rules of the session:** the design is decided by Eve; Claude
recommends and records; no code, no UML edits before a decision; "never guess, always verify": a claim about the code or the data is checked first.
Meanwhile two builder agents work on the independent parts (`.claude/tasks/next_session_start.md`), so nothing decided here can break their work:
they never touch design files, the audit, or the export.

## 0. To read first (about 20 minutes, in this order)

**Start here: `home_audit_reading_guide.md` section 0** (the order of work, the criteria every decision is judged against, the problem queue: **P1 is now**), then `home_design_first_roadmap_2026-11-12.md`. The order (design, then mechanism, then code, then gating and tests), the **behaviour table** (what each kind of configuration shows and can do, from decided texts, open cells marked) and **5 design questions (Q1-Q5)**. The gating and test-configuration paper (`home_evidence/home_gating_and_test_configs_2026-11-12.md`) is paused until the behaviour table is agreed. Everything else below is background.

1. `home_audit_reading_guide.md` (the map; section 3 is the list of 13 decisions).
2. `home_audit_steps.md` sections 1-5 (rule, words, audit mode, kinds, reach and stage), then 18-20 (the three reviews and D1-D14).
3. `home_audit_first_cut.md` (new, a proposal: a smaller first version, with what it cannot do).
   **Then `home_evidence/home_audit_forensics_2026-11-12.md`**: new facts found in the current design (F1-F13) and, for every undecided item, the options with consequences for the scientist, data scientist, developer, checker, operator and novice, and a recommendation. Read its section 4 first (the path in one table), then section 3 where you want the reasons. The forensics file starts with a status map (section 0: what is DECIDED, CONFIRM, OPEN, and what is only mine) and a list of the places where my proposals reconsider something decided (0.3). Section 3.2b explains the cheaper engine (E) with measured costs; in 3.7 the target is decided (no "Plot to show" anywhere, only Exploration without the sandbox flag) and the **interim** is an open question.
   **Then `home_evidence/home_audit_architect_review_2026-11-12.md`** (the app seen by a software architect): section 0 is the answer in ten lines; section 2 the findings AR1-AR10 (the first: recipe text is Python code); section 4 the undecided items with an architect's view and five new decisions N2-N6.
4. `recipe_review_st22_2026-11-11.md` section 3 (three questions about the ST22 recipe) and its before/after pictures in `tmpAI/recipe_review/`.

To look at in the app (QA group, new): open `1_test_data_ST22_dummy`, tab "QA Canaries": seven plots with the expected numbers in the subtitle; the
"AMR genes per sample" bar at 0 is the sample that used to vanish; the "rows per sample" plot is a defect shown on purpose (#68); the last one (`qa_aggregated_no_key`) is a plot with no `sample_id` in its data (#60).

## 1. Recipe questions (10 minutes; they block the recipe, not the build)

| # | Question | Recommendation |
|---|---|---|
| R1 | What must `ST22_Anchor` answer (#67)? | (a) virulence + MLST + metadata, no ResFinder; status "Detected" moves to the VirulenceFinder step |
| R2 | The 4 samples without usable phenotype in the resistance score plot (#70) | (a) not plotted, with a note "n = 38 of 42" |
| R3 | MLST plot title and the demo filter 2023-2025 | keep the filter, add the years to the title |
| R4 | `virulence_variants`: facets by sequence type give 16 unreadable panels; left unfaceted for now | decide together with R1 |

## 2. The 13 decisions, in an order that unlocks the build

**Group 1: needed for the first cut (decide first, 30 minutes).** For each: the recommendation is in the reading guide; what changes if you say no is in its table.
2 NA rule, 3 reason categories, 5 keys, 9 event log (note: it changes the session format), 11 first check list and thresholds, 12 D1-D14 (new dev dependency `hypothesis`, policy block), 13 legacy names.

**Group 2: shapes the full screen (after the cut is accepted).** 1 stage and reach, 6 reach selector, 7 audit table selector, 8 trial computation, 4 optional caption.

**Group 3: later.** 10 lineage map.

Order of the session: confirm or change the cut (`home_audit_first_cut.md`) > Group 1 > Group 2 > Group 3 > parking lot.

**Group 4: new, from the architect review (decide after the cut; none blocks the builders).** N2 keep or remove `developer_raw_yaml` as an audit kind; N3 trust levels for recipe text from outside (recipe text is Python code, AR1);
N4 how to hold the decided flag rules (one table); N5 architecture rules as tests; N6 stored stages of the original anchors (atomic write, path, clean-up; touches `libs/transformer`, needs your OK). N2 is now about the step type `developer_raw_yaml`: no code creates it, so I recommend keeping it display-only.

**Ask first:** Q1-Q5 of the roadmap (which kinds of configuration are legitimate; the Exploration screen incl. "Raw has no plot (NA)"; preview lists in audit mode; what is exported and saved without audit; the transition for the two features without audit).

## 3. What Claude does with each answer, immediately

- Writes the decision into `home_audit_steps.md` (section 16 "Decided"), `home_audit_reading_guide.md` (section 3 table) and ADR-099.
- Redraws `HOME-AUDIT-LINEAGE` and `HOME-AUDIT-EFFECT` once decision 1 is made; updates the status register in `uml_model_plan.md`; runs `audit_uml_model.py` and `audit_docs_sync.py`.
- Turns the accepted cut into work packages with files, tests and canaries (a new section in the build brief), and files one issue per package under #60 (sub-issues, protocol in brief section 0b).
- Tells the builder agents through an issue comment (never by editing their files) if a decision changes what they build.

## 4. Open items to carry (not for tomorrow unless there is time)

Wording of the reach options and kinds (section 17 of the audit design); a usability test with two or three scientists before the wording is final; what stays of the
existing right panel (open question 5); the importer's verification legs (open question 6); promoting the persona review method (`.claude/workflows/design_review_personas.md`) to the global mentoring repo.

## 5. State of the world this agenda assumes (verified 2026-11-11)

Issues #59, #61, #62, #63 re-demonstrated by running; #65 and #71 fixed and closed with evidence (see their comments); #66-#70 open; recipe fixes and QA canaries committed;
headless 1646 passed (1649 after the seventh canary on 2026-11-12), browser gate 70 passed 3 skipped.
