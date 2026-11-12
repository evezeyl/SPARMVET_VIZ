# HOME: design first, then mechanism, then code (roadmap and the design to agree)

**Written for:** Eve, to review. **Written:** 2026-11-12, after your correction: my gating paper described how the code works today and proposed to start with gating; the order must be **(1) agree how the app should work, (2) then change the code to work like that, (3) then gate and test it**.
**Status:** a proposed order, a behaviour table made only from what is decided (open cells marked), and the design questions in design terms. No code, configuration or diagram is changed.
**Words:** DECIDED / CONFIRM / OPEN / MINE as in `home_evidence/home_audit_forensics_2026-11-12.md` section 0.

## 1. The order (what has to be fixed and decided first)

| Stage | What | Result | Depends on |
|---|---|---|---|
| **1. Behaviour design** | How HOME works for the user in each kind of configuration: what is on the screen, what can change a plot, the data or an export, what is saved, what the texts say. Section 3 is the table; section 4 the questions | a **behaviour table you agree**, written into the design files and ADR-099, with the diagrams made consistent | nothing (it is decided in large part already) |
| **2. Mechanism design** | How the app does it: the audit engine (overlay or forked recipe), keys and cache, the order of building (D14), who may bring recipe text into the app, how the code is cut | decisions in the architect review (N2-N6), forensics 3.2 | stage 1 |
| **3. Build plan** | work packages in an order that never leaves a configuration in a state that breaks your rules; what users of each configuration see between steps | an updated build brief | stages 1 and 2 |
| **4. Code** | the builders | | stage 3 |
| **5. Gating and test configurations** | which configurations exist, how each control follows them, the files the tests use. **Derived from stage 1**: the behaviour table says what each configuration shows; the gating and the files only implement it | the gating paper, rewritten after stage 1 | stage 1 |
| **6. Tests** | one test per row of the behaviour table, per configuration; the science invariant | | stages 4, 5 |

**What already goes on in parallel, and why it is safe:** the engine fixes #62, #61 and the NA information (#63 step 1) are verified errors in today's engine and do not depend on the design (brief WP1-WP3a). The preview lists per dataset (WP4) are DECIDED design (`home_preview_filters.md`); WP4 deliberately leaves the strip untouched.
**What I paused:** the capability resolver, the test-configuration files, the rule about companion flags (Rule 6), the filing of the two small defects, and the engine choice. They are stage 2 or 5 and wait for stage 1.

## 2. What the gating paper still gives (as input, not as a plan)

Its verified facts describe the code **as built today**, which the design will replace: the strip offers My view without an audit; a notice is gated by a proxy flag; the Export panel names "steps sent to audit" in a configuration without audit; the validator forbids audit without Compare, which the decided design allows. They tell the build plan (stage 3) what has to change. They are not decisions. The paper now carries a banner saying so.

## 3. The behaviour to agree: what the user sees and can do, by kind of configuration

Four kinds of configuration, described by what the user can do (the flags that make them come later, in stage 5):
**A. Fixed view** (no interaction) · **B. Exploration only** (the user can look: preview filters, no audit) · **C. Exploration and audit mode** · **D. as C, with the Compare toggle**.
Sessions and export are separate add-ons; their meaning in each kind is in rows 11-12.
`[source]` = decided text; **[OPEN n]** = a question of section 4; `(today)` = how the code works now, to be replaced.

| # | Area | A. Fixed view | B. Exploration only | C. Exploration + audit mode | D. C + Compare |
|---|---|---|---|---|---|
| 1 | **Header strip** | none; the Result is shown | "Data: Raw \| Result"; no "Plot to show", no My view, no Compare [`home_preview_filters` 2; UI-HOME-EXPLORATION] `(today: B has "Data to show" with My view and "Plot to show")` | the same strip, plus the **mode switch** "Exploration \| Audit mode" at the left of the group tabs [ADR-099 point 2] | as C |
| 2 | **Plot** | the recipe's Result plot | the Result plot, **never changed by a preview filter**; on Raw: **[OPEN 2]** | Exploration: as B. Audit mode: the **audit plot** (audit T3) with a badge saying which steps apply [steps 3] | audit mode: original Result plot \| audit plot, on/off toggle [steps 3] |
| 3 | **Data table** | Result (T2), read-only | original Raw (T1) or Result (T2) with the preview filters of that view [preview 3] | Exploration: as B. Audit mode: the audit table; selector audit T1/T2/T3 [CONFIRM, question 7] | as C |
| 4 | **Filters panel** | absent | the shared form with **"Add to preview"** and Reset; its header names the view and dataset [preview 2] | Exploration: as B. Audit mode: the same form with **"Create audit step"**; columns of the audit T2 [steps 3] | as C |
| 5 | **Preview lists** | n/a | per view and dataset; cleared when the view or the recipe changes; never saved or exported [preview 4] | Exploration: as B. Audit mode: kept, not applied; shown or hidden? **[OPEN 3]** | as C |
| 6 | **Hide columns** | absent | hides columns in the table only [preview 3] | Exploration: as B. Audit mode: a drop is an audit step, plot level, with a warning [steps 9] | as C |
| 7 | **Notices and badges** | none | badge "Viewing Raw/Result, N preview filter(s) on, not saved" [preview 7]; the text of a notice such as "Exploration only": **[OPEN 2]** | Exploration: as B. Audit mode: "N audit steps active" on the plot and in the export [CONFIRM, D10] | as C |
| 8 | **Right sidebar** | absent | **absent** ("without the flag the whole right sidebar is absent") [UI-HOME-EXPLORATION] | the Pipeline Audit panel: step list, Undo last, Revert to step N, Remove all, lineage chain, what is affected [steps 3] | as C |
| 9 | **New audit step** | absent | absent | the three-step dialog: what, check, why; Apply and Cancel; reason required [ADR-099 point 3] | as C |
| 10 | **What can change a plot, the data or an export** | nothing | **nothing** [preview 1] | **only an audit step**, with a reason, recorded, removable [steps 1] | as C |
| 11 | **Export** (when the add-on is on) | the bundle of the Result; what its panel says about filters: **[OPEN 4]** | the bundle of the Result; "exploration is never exported" [preview 3]; the exact text **[OPEN 4]** | Result + audited steps with reasons, original and audit data, attrition table, coverage check, forked recipe, after a pre-export review [steps 11, CONFIRM D5] | as C |
| 12 | **Saved in a session** (when the add-on is on) | n/a | what is saved when there is nothing to record? **[OPEN 4]** (the contract 7.1 says "applied filters", the exploration design says never; no code saves them) | the step list is the source of truth (+ event log, CONFIRM); restoring recomputes [steps 11] | as C |
| 13 | **Help text** | short | explains preview vs audit and why filters clear on a view change [preview 8] | adds "Before you audit" [steps 19] | as C |

The invariant of row 10 is the science rule: **in A and B nothing can change a plot, the data or an export.** Everything else in the table follows from it.
Where the table says "as C" the decided design says nothing different; the pictures `UI-HOME-EXPLORATION`, `UI-HOME-AUDIT` and `HOME-VIEW-MATRIX` already show kinds B and C (the matrix lacks A and D as columns, a small gap to close in stage 1).

## 4. The design questions (stage 1), each in design terms

### Q1. Which kinds of configuration are legitimate, and what may depend on what? **DECIDED 2026-11-12 (Eve): option (a)** - audit needs export, Compare and sessions (the user compares the effect, saves unfinished work, exports what is finished so others can verify).
The design needs to say whether audit mode may exist **without** export or without sessions, and whether Compare may be off.
**Why it is a design question:** an audit step changes a figure; the project rule is that every step is recorded and exported. A configuration where steps can be made but cannot leave the session would let a figure exist that nobody can reproduce.
| Option | Science | User | Consequence |
|---|---|---|---|
| (a) audit needs export and sessions (+ Compare, as built) | every audited figure is exportable and restorable | fewer kinds (only C+D with everything) | no audit without Compare, against the decided "Off: the audited plot uses the full width" |
| (b) **audit needs export; sessions and Compare optional** | every audited figure is exportable | audit without Compare is allowed (as designed); sessions optional with a stated consequence | needs row 12 settled: what happens to steps without sessions |
| (c) audit independent; the missing add-ons are warnings (your principle: inform and warn, block only the technical) | the operator is told | most kinds | allows an audit that cannot be exported if the operator accepts the warning |
**Recommendation: (b)**, because it keeps the one thing the science needs (steps can be exported) and nothing else. It also decides which configurations are valid, which stage 5 then implements.

### Q2. What does the Exploration screen show, in words?
- **Raw and the plot:** the decided texts say "Raw has no plot (NA)" in three places (`home_preview_filters` 3, UI-HOME-EXPLORATION, HOME-VIEW-MATRIX); today the plot stays visible on Raw. (a) the plot area is empty or collapsed with a short message on Raw (the literal decided text); (b) the Result plot stays, a badge says "the plot shows Result". (a) avoids a plot beside a table of another stage; (b) keeps the layout still. **Recommendation: (a)**, because it is what you decided and it cannot mislead.
- **Notices:** which sentences, and in which kind of configuration (for example "Exploration only: filters are not saved" in B). One sentence per kind, written once in the design.

### Q3. Preview lists while audit mode is on (row 5)
(a) hidden, kept in memory, shown again in Exploration; (b) shown greyed "not applied"; (c) applied (rejected by the design). **Recommendation: (a)** (your rule: not active, hidden).

### Q4. What is exported and saved when there is no audit (rows 11-12)
- The Export panel in kinds A and B: say "exploration filters are never exported" and nothing about audit (today the text names "steps sent to audit").
- The session in kind B: the contract (7.1) says applied filters are saved; the exploration design says preview lists are never saved; the code saves none. **Recommendation: the exploration design wins** (never saved), and the contract is corrected in stage 3. Then a session in B holds only the recipe and data reference.

### Q5. The transition: what does each kind show between now and the target?
The decided sequencing keeps the old strip until audit mode exists. In between, kind B (the two features without audit) offers My view and a plot that a preview filter changes unrecorded, against row 10. Design options for the **path**:
| Option | Kind B in between | Kinds C and D in between | Risk |
|---|---|---|---|
| (a) as decided: nothing removed until audit mode | breaks row 10 | as today | none new; the rule is broken for the length of the build |
| (b) **the target strip for B first** (it has no audit to wait for); C and D unchanged | follows rows 1, 2, 10 | as today | the header-strip code is frozen by brief S3: needs your yes; no rework later because it is the final screen of B |
| (c) all kinds at once | | cannot: audited steps are made in My view until audit mode exists | rejected |
**Recommendation: (b)**, because it makes your rule true for every configuration that has no audit, early and without rework. This is a build-plan decision (stage 3), but it needs your design answer now because it shows what B users see.

### Q6. The audit behaviour (already designed; the order I suggest you answer them in)
The 13 questions of the reading guide split into **behaviour** and **mechanism**. Behaviour first: 1 stage and reach (with 6 the reach selector), 2 the NA rule (its text is decided, its default for #63 is not), 3 reason categories, 4 caption, 7 audit table selector, 11 first checks and thresholds. Mechanism later (stage 2): 8 trial computation, 9 event log, 10 lineage map, 12 D1-D14, 13 legacy names. My analysis of each is in forensics 3.3-3.8; none is repeated here.

### Q7. Who may bring recipe text into the app? (behaviour, decided in stage 1, mechanism in stage 2)
A recipe is code (architect review AR1). The design should say, in user words: may a bundle or a session from another person be imported in every configuration that has Export, only in some, or only by an operator? Options and consequences are in architect review 3.1 (a to d). **Not urgent for the behaviour table, but it must be answered before the audit build makes audit states into recipes.**

## 5. What happens to my earlier papers

| Paper | New role |
|---|---|
| `home_evidence/home_gating_and_test_configs_2026-11-12.md` | stage 5, **paused**; banner added; its verified facts are input to stage 3; its questions Q1, Q2, Q7 are now Q3, Q2 and Q5 here; Q3-Q6 and Q8 wait |
| `home_evidence/home_audit_forensics_2026-11-12.md` | the status map (section 0) and the options for the audit behaviour (3.3-3.8) belong to stage 1; the engine options (3.2) to stage 2 |
| `home_evidence/home_audit_architect_review_2026-11-12.md` | stage 2 (N2-N6, AR findings); AR1 touches Q7 |

## 6. What I propose to do next, once you have read this

1. You answer or correct Q1-Q5 in this file (they are short). Q6 and Q7 can wait.
2. I write the agreed behaviour table into `home_preview_filters.md` and `home_audit_steps.md`, update ADR-099, correct the contract (7.1), and add the missing columns (A and D) to `HOME-VIEW-MATRIX` (after your OK for the UML edit, as always).
3. Only then: stage 2 (mechanism), stage 3 (build plan), and the gating and test configurations derived from the table.
