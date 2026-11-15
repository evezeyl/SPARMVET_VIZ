# Proposal: `.claude/rules/rules_ui_dashboard.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked against ADR-086 (header, lines 4170-4176: "describes the app as built"; target replaced by ADR-099/105), ADR-098, ADR-100 point 9 and OPEN list, `ui_implementation_contract.md:467` (the T3 wording reworded 2026-11-12), `adr_sync_changes.md` section 5 (this file: line 72, section 7, section 1 T3 scope).

## 1. Line 13, T3 scope (CHANGES A RULE; sync with the contract)

Today (line 13): `... It is NOT a wrangling sandbox - no action-picker UI, and no importing of recipe content from elsewhere (not even Gallery, ADR-093). Wrangling belongs in T1/T2 data analysis recipes.`
Proposed: `... In audit mode T3 shows no action-picker UI: the user adds filters, drops and removals by key. A recipe may declare any registered action in its own tier-3 list; the engine runs it like any step and the recipe maker is responsible for good practice (reshaping early is better) (ADR-099 point 16; ADR-100 point 9, reader NOT BUILT). No importing of recipe content from elsewhere (not even Gallery, ADR-093). Wrangling belongs in T1/T2 data analysis recipes.`
CHANGES A RULE (a recipe may carry tier-3 actions).
Why: the same sentence is already reworded in `ui_implementation_contract.md:467` (Eve, ADR-099 point 16, 2026-11-12), so the two files disagree today.

## 2. Line 72, "Plot vs data view (ADR-086)" (FACT, marker only)

Today: the bullet states the two header choices as the rule.
Proposed: append: `**[ADR-086 describes the app as built. Its target is replaced by ADR-099 points 1 and 2, P2 and ADR-105 (Exploration has one immutable plot, the Result; My view and Compare move to audit mode). NOT BUILT; until it is, this bullet is true.]**`
Why: ADR-086 header (lines 4172-4173).

## 3. Section 7, line 188, "BLUEPRINT never authors T3" (no text; OPEN)
ADR-100's OPEN list: "Whether Blueprint may author a plot entry's tier 3. Record 1: ADR-082 point 4 and ADR-099 header: BLUEPRINT never authors T3. Record 2: `home_audit_steps.md` 5a point 15 and DEC17." The Blueprint form is not decided. No change is proposed; Eve decides first.

## 4. Line 82, ADR-036 (no change)
`ID Sanitation ... (ADR-036)`: ADR-036 is the ID sanitation pivot (ADR-106 "Corrects a citation"), so the citation here is correct. Checked.

## 5. Section 6, "Test tiers" and commands (no change)
Not run; the numbers ("12 smoke tests", "~35 s") are not checked here. The browser duration is treated in `rules_verification_testing.md.proposal.md`.

## Not settled
1. Change 3 (Blueprint and tier 3).
2. The smoke test count in section 6 (not verified).
