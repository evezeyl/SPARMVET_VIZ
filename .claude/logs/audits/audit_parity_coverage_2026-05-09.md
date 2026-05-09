Status: PROCESSED
Triage:
  FIXED — theme_legend_position, theme_publication: both added to custom_viz_components in audit_exclusions.yaml. Both are SPARMVET-specific components, not standard plotnine exports. Script re-run after fix: ✅ PASS (no unresolved stale registrations).
  INFO — 54 plotnine symbols unregistered (75% coverage): informational per ADR-036. Many missing are UK spelling aliases (scale_colour_*) or internal helpers (theme_get, theme_set, aes, ggplot). No immediate action — these are low-value additions.
  INFO — Polars coverage low across all namespaces: informational per ADR-035. The heuristic match (substring) is intentionally loose; true parity gaps require domain judgment. No immediate action.
# Audit Report: Parity Mandate Coverage
Generated: 2026-05-09T23:18:07
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-035 (Polars Parity Mandate), ADR-036 (Artist Parity Mandate)

- Plotnine 0.15.3: 222 symbols, 168 registered (75% coverage), 54 gap
- Stale registrations: 0 unresolved (2 fixed → added to custom_viz_components), 20 accepted, 3 custom
- Polars 1.40.1: 63 registered actions

## Plotnine Parity (ADR-036)

### Previously Unresolved (now fixed in audit_exclusions.yaml)

- theme_legend_position → custom_viz_components
- theme_publication → custom_viz_components

### Coverage Gap — 54 symbols (informational)

Most notable gaps:
- `geom_bin2d` (only missing geom)
- UK spelling aliases: `scale_colour_*` (33 scale aliases)
- Theme internals: `theme_get`, `theme_set`, `theme_update` (not user-facing)
- Grammar helpers: `aes`, `ggplot`, `lims` (engine-internal, not manifest-expressible)

## Polars Coverage (ADR-035)

| Namespace | Covered | Total | Coverage |
|-----------|---------|-------|----------|
| `__expr__` | 44 | 208 | 21% |
| `arr` | 14 | 31 | 45% |
| `cat` | 1 | 6 | 16% |
| `dt` | 5 | 47 | 10% |
| `list` | 16 | 43 | 37% |
| `meta` | 2 | 17 | 11% |
| `name` | 2 | 10 | 20% |
| `str` | 6 | 49 | 12% |
| `struct` | 2 | 5 | 40% |

Coverage is heuristic (substring match) — actual functional parity is higher than percentages suggest. Low-coverage namespaces (`dt`, `str`, `cat`) are candidates for new actions when manifest authors request them.

## References
- Routine 12 (Parity mandate coverage) in `.claude/workflows/audit_routine_registry.md`
- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)
- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)
