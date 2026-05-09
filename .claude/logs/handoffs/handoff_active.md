# Handoff — Active State (2026-05-09 Phase 33 in progress)

**Branch:** dev
**Working tree:** uncommitted changes
**Status:** Phase 31 COMPLETE. Phase 33 BP-AGENT MVP in progress (33-B done, 33-C through 33-H open).

---

## What Was Done This Session

### Phase 31 closed

Export provenance cluster (EXPORT-HASH-2, EXPORT-VERSION-1, EXPORT-IMG-META-1, EXPORT-AUDIT-COMPLETE-1) and unified import panel (IMPORT-UI-1) delivered and verified.

### Phase 33 — BP-AGENT-1 done

Two new headless-safe modules in `libs/blueprint_arch/`:

| File | What it provides |
|---|---|
| `agent_adapter.py` | `AgentAdapter` Protocol, `ClaudeCliAdapter` (subprocess isolation, flock, auth probe), `DisabledAdapter`, `make_adapter()` |
| `agent_context.py` | `build_system_prompt()` (Layer 1), `build_turn_context()` (Layer 3) |

Bootloader gains `get_agent_config()` + `get_agent_adapter()` (cached, fallback-safe).

Auth probe tested OK on dev machine (`claude` installed + logged in).

---

## Files Modified

- `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` (new)
- `libs/blueprint_arch/src/blueprint_arch/agent_context.py` (new)
- `app/src/bootloader.py` (two new methods + @deps update)
- `.claude/knowledge/project_conventions.md` (§17 added)
- `.claude/plans/implementation_plan_master.md` (Phase 31 COMPLETED, Phase 33 added)
- `.claude/tasks/tasks.md` (BP-AGENT-1 marked done)
- `.claude/logs/audits/audit_2026-05-09b.md` (new)
- `.claude/logs/handoffs/handoff_active.md` (this file)

---

## Next Step

**BP-AGENT-PARSER-1** `[sonnet/medium]` — `agent_tool_parser.py`:
- Fenced-block extractor for `<!-- AGENT_TOOL_CALL --> ... <!-- /AGENT_TOOL_CALL -->` markers
- JSON validation + per-tool schema dispatch
- Returns structured error string on parse failure (for agent to retry)
- Must be headless-safe (no Shiny imports)
- Location: `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py`

Then in order: BP-AGENT-TOOLS-1 → BP-AGENT-INSTRUCT-1 → BP-AGENT-PANEL-1 → BP-AGENT-UI-1 → BP-AGENT-CSS-1.

---

## Smoke test baseline

`SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py` → 14 passed, 3 skipped.

@dasharch — Phase 33 adapter layer closed.
