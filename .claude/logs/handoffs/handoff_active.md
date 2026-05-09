# Handoff — Active State (2026-05-09 Phase 33 MVP-1 COMPLETE)

**Branch:** dev
**Working tree:** uncommitted changes
**Status:** Phase 33 BP-AGENT MVP-1 COMPLETE. All 6 BP-AGENT-* tasks done. Smoke tests 14 passed / 3 skipped.

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

## Next Step (first task in new session)

Read `.claude/tasks/tasks.md` section `🟣 Blueprint Architect — Open Tasks` for the next open item. After MVP-1, the remaining Blueprint IDE tasks are:

- **BP-FORMS-1** `[sonnet/high]` — form renderer from `ui_schema`
- **BP-ESCAPE-1** `[sonnet/medium]` — YAML escape hatch (read-only + editable)
- **BP-UNDO-1** `[haiku/low]` — 20-step undo deque
- **BP-HELP-1** `[sonnet/medium]` — help panel from `__doc__`
- **BP-COLOR-1** `[sonnet/medium]` — color widget

Or pivot to open non-Blueprint items (see `tasks.md` `🟡 Wave 2`).

---

## Smoke test baseline

`SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py` → 14 passed, 3 skipped.

@dasharch — Phase 33 MVP-1 complete. BLUEPRINT AI Agent chat panel live.
