# Proposal: `.claude/rules/rules_app_features_flags.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked against ADR-098 (BUILT), ADR-099 point 11 (flag cascade, decided 2026-11-12, NOT BUILT), ADR-052/ADR-099 notes (`architecture_decisions.md:1476, 3233`), `grep` of `config` and `app` for an audit flag (no hit: not built), `adr_sync_changes.md` section 5.

## 1. Lines 41-47, the "My view" scratchpad (FACT, marker)

Today (line 41): `├─ (tier toggle "My view" option) ← ADR-085: gated on interactivity_enabled ALONE, not t3_sandbox_enabled`; (lines 47-51): "My view (T3) is a view, not an audit-gated feature ... Without `t3_sandbox_enabled`, 'My view' is a pure scratchpad - filters apply and render there for the session ...".
Proposed: keep the text (it is the built behaviour) and add after line 54 (end of that paragraph) a marker:
`**[Target, NOT BUILT (ADR-099, ADR-105; ADR-099 point 11): audit mode becomes a mode of its own, gated by the sandbox flag. Exploration (table only; one immutable plot) is the only mode without the flag. Until it is built, the paragraph above is true. Exploration filters also change the data table on every view (ADR-098).]**`
Why: ADR-099 header and point 11; ADR-098.

## 2. Lines 43, 60-63, Compare (FACT, marker)
`comparison_mode_enabled` (line 43) becomes a child of the sandbox flag in the target (ADR-099 point 11: "audit mode requires comparison, sessions and export; comparison requires the audit flag"). Same marker, once. Add to the "Cascade Enforcement" section (after the six numbered rules), a proposed rule 7, marked target:
```
7. **TARGET, NOT BUILT (ADR-099 point 11, P1, 2026-11-12):** audit mode requires comparison, sessions and export (the user compares the effect, saves unfinished work, exports what is finished so that others can verify); comparison requires the audit flag. How a violation is handled (fatal like ADR-077, or soft) is not recorded.
```
CHANGES A RULE only when built; the marker records the decision now.
Why: `architecture_decisions.md:5117` (ADR-099 point 11).

## 3. Lines 61-63 (no change)
"Filters accordion absent", "Column selector absent": not changed by any decision read.

## Not settled
1. How a violation of the new cascade (rule 7) is handled: not recorded (soft or fatal).
2. The flag matrix (lines ~110-130) was not re-verified against `config/app_features/*.yaml` in this pass; no decision of 2026-11-14 changes a flag value.
