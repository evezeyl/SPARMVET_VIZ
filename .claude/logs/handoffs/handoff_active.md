# Handoff — Active State (2026-05-09 haiku/sonnet cleanup wave COMPLETE)

**Branch:** dev
**Working tree:** uncommitted changes
**Status:** haiku/sonnet cleanup wave done. All small open tasks from Phase 33 closed. Next: remaining sonnet/medium tasks (INGEST-SANITIZE-1, THEATER-1, UI-TITLE-1, BP-ESCAPE-1, BP-FORMS-1).

---

## What Was Done This Session

### Phase 33 MVP-1 — all BP-AGENT-* tasks closed

| Task | What was delivered |
|---|---|
| BP-AGENT-1 | `agent_adapter.py` + `agent_context.py` in `libs/blueprint_arch/`. `ClaudeCliAdapter` with subprocess isolation, flock, auth probe. `get_agent_adapter()` / `get_agent_config()` in `Bootloader`. |
| BP-AGENT-PARSER-1 | `agent_tool_parser.py` — fenced-block extractor, per-tool schema validation, `ParseResult.format_error_turn()`. |
| BP-AGENT-TOOLS-1 | `agent_tools.py` — 3 MVP-1 tools wrapping registry/navigator APIs. Fixed `!include` string→dict resolution for `get_field_contract`. |
| BP-AGENT-INSTRUCT-1 | `config/ui/agents/blueprint_default.md` — system prompt with tool protocol, Intake Protocol, Manifest Design Rules, AMR domain knowledge. |
| BP-AGENT-PANEL-1 | Already existed in `sidebar_registry.py` and `blueprint_standard_right.yaml`. No change needed. |
| BP-AGENT-CSS-1 | `.bp-agent-*` and `.bp-agent-status-banner` blocks in `config/ui/theme.css`. |
| BP-AGENT-UI-1 | `blueprint_agent_panel_ui` render + `_bp_agent_send` async Effect in `blueprint_handlers.py`. Blueprint right sidebar in `home_theater.py` wired to include agent card when `blueprint_agent_enabled`. Tool-call loop max 3 rounds via `asyncio.to_thread`. |
| BP-FLAG-1 | `manifest_edit_enabled` added to all 8 persona templates. |

### Key lessons / decisions

- `format_error_turn()` is a **method on `ParseResult`**, not a module-level function.
- `bootloader.get_agent_adapter()` and `bootloader.get_agent_config()` — no `blueprint_` prefix.
- `adapter.is_disabled` is an **attribute**, not a method.
- `instructions_file` is read from `bootloader.get_agent_config()` only; `ValueError` raised if absent. No hardcoded fallback.
- CSS: additive only — never change existing `.bp-agent-*` color values; `#f5f5f5` agent bubble is intentional contrast against `#c0c0c0` sidebar.

---

## Files Modified (Phase 33, this session)

- `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` (new)
- `libs/blueprint_arch/src/blueprint_arch/agent_context.py` (new)
- `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py` (new)
- `libs/blueprint_arch/src/blueprint_arch/agent_tools.py` (new)
- `config/ui/agents/blueprint_default.md` (new)
- `config/ui/theme.css` (`.bp-agent-*` status banner added)
- `app/src/bootloader.py` (`get_agent_config` + `get_agent_adapter`)
- `app/handlers/blueprint_handlers.py` (agent reactive state + render + async effect)
- `app/handlers/home_theater.py` (Blueprint right sidebar: added agent card slot)
- All 8 persona templates in `config/ui/templates/` (`manifest_edit_enabled` + `blueprint_agent_enabled` added)
- `.claude/knowledge/architecture_decisions.md` (ADR-076 status updated to MVP-1 IMPLEMENTED)
- `.claude/tasks/tasks.md` (BP-AGENT-UI-1 + others marked [x])

---

## Files Modified (cleanup wave, this append)

- `app/handlers/blueprint_handlers.py` — undo deque + UX-NOTIF-3 notification
- `app/modules/wrangle_studio.py` — legend "● Ref" → "● Add"
- `app/src/ui.py` — TubeMap: palette ref→add, shapes ref→add, layout tightened
- `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py` — classDef ref→add
- `app/src/main.py` — docs_available flag
- `libs/utils/src/utils/gallery_manager.py` — DELETED (duplicate)
- `libs/utils/tests/debug_gallery_submission.py` — import fixed to viz_gallery
- `libs/transformer/tests/debug_wrangler.py` — dated tmpAI subdir auto-creation
- `libs/transformer/tests/debug_assembler.py` — dated tmpAI subdir auto-creation
- `.claude/tasks/tasks.md` — UTILS-RELOC-2, HELP-DOCS-1, BP-UNDO-1, AUDIT-TIMERS-1, TubeMap, UX-NOTIF-3 marked [x]

---

## Next Step (first task in new session)

Remaining sonnet/medium open tasks:
- **INGEST-SANITIZE-1** `[sonnet/medium]` — wire DataSanitizer into IngestorOrchestrator.run()
- **THEATER-1** `[sonnet/medium]` — plot panel collapse/minimize
- **UI-TITLE-1** `[sonnet/medium]` — persona/manifest title resolution
- **BP-ESCAPE-1** `[sonnet/medium]` — YAML escape hatch (read-only + editable)
- **BP-FORMS-1** `[sonnet/high]` — form renderer from ui_schema

---

## Smoke test baseline

`SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py` → 14 passed, 3 skipped.

@dasharch — cleanup wave done. haiku tasks cleared. Next wave is sonnet/medium.
