Status: PROCESSED
Triage:
  PASS — ADR-045 (Two-Category Law): all @render.* functions in home_theater.py, filter_and_audit_handlers.py, export_handlers.py, session_handlers.py are pure readers. All .set() calls are in @reactive.Effect blocks. No violations.
  PASS — ADR-053 (No persona name comparisons): debug print in home_theater.py:1072 reads persona for logging only, no control-flow branching. All feature gating uses bootloader.is_enabled(flag). Test files have persona comparisons but not production code.
  VIOLATION — ADR-078 (Diagnostic Error Discipline): 5 transformer action files silently return unchanged LazyFrame on invalid input instead of raising SPARMVET_DiagnosticError. Affected: regex_extract, mutate (expressions.py), window_agg, shift (analytical.py), split_and_explode (advanced.py). No SPARMVET_DiagnosticError is imported or raised in any action file — actions that validate do raise ValueError/FileNotFoundError but not the specified error type. Task filed: ADR-078-ACTIONS-1.
# Audit Report: ADR Behavioral Compliance
Generated: 2026-05-09
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Routine: 18 — Agent-based

## Result

| ADR | Status | Summary |
|-----|--------|---------|
| ADR-045 Two-Category Law | **PASS** | @render.* are read-only; .set() calls confined to @reactive.Effect |
| ADR-053 No persona name checks | **PASS** | All gates use bootloader.is_enabled(flag); no string comparisons in control flow |
| ADR-078 Diagnostic Error Discipline | **VIOLATION** | 5 actions silently return `lf` on invalid input instead of raising SPARMVET_DiagnosticError |

## ADR-045 — Two-Category Law (PASS)

All four handler files separate rendering from state mutation correctly.

- `home_theater.py`: tier toggle, sub-tab, collapse state all in dedicated @reactive.Effect blocks
- `filter_and_audit_handlers.py`: home_state.set() / _propagation_scratch.set() only in Effect blocks
- `export_handlers.py`: export download yields bytes, never writes reactive state
- `session_handlers.py`: session restore writes home_state.set() only in Effect blocks

## ADR-053 — No Persona Name Comparisons (PASS)

Production handler code is clean. home_theater.py:1072 reads persona for a debug print — no branching.
Test/debug file (app/tests/debug_home_theater.py) uses persona string comparisons — acceptable in non-runtime code.

## ADR-078 — Diagnostic Error Discipline (VIOLATION)

### Pattern: silent pass-through on missing input

```
expressions.py:40  — action_regex_extract: if not source or not pattern or not target: return lf
expressions.py:187 — action_mutate:       if not target or not expr_str: return lf
analytical.py:29   — action_window_agg:   if not col: return lf
analytical.py:64   — action_shift:        if not col: return lf
advanced.py:27     — action_split_and_explode: if not col: return lf
```

### Root cause

No `SPARMVET_DiagnosticError` class is imported or raised in any action file. The pattern adopted at implementation time was: core actions raise `ValueError` (join, sink_parquet — correct), analytical actions silently pass through. ADR-078 requires the diagnostic error type specifically.

### What passes

join, sink_parquet, scan_parquet, fill_nulls, replace_values, rename all raise exceptions on invalid mandatory params (correct intent, wrong error type for some).

### Task filed

ADR-078-ACTIONS-1: Retrofit SPARMVET_DiagnosticError into the 5 silent-pass-through actions, and audit all remaining actions for the same pattern. [sonnet/medium]

## References
- `rules_persona_feature_flags.md` §Anti-Pattern — ADR-053
- `rules_app_structure.md §1` — ADR-045 Two-Category Law
- `.claude/knowledge/architecture_decisions.md` — ADR-078 Diagnostic Error Discipline
- Routine 18 (ADR behavioral compliance) in `.claude/workflows/audit_routine_registry.md`
