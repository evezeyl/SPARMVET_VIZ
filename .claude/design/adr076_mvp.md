# ADR-076 MVP-1 Scope — BLUEPRINT AI Agent Helper

**Status:** SCOPED 2026-05-09 — implementation not yet started
**Authority:** ADR-076 §1–§11. This document narrows that ADR to a Phase-1 minimum that is shippable, demoable, and gives concrete signal on whether the agent surface is worth investing further in.

**Why scope an MVP:** ADR-076 spans 11 sections, 9 implementation tasks, and three adapter backends. Built end-to-end without slicing it down, it is a 4–6 week sink before anyone uses it. MVP-1 strips it to a single read-only conversational loop that proves the architectural seams are right. If MVP-1 lands and the conversational tempo + tool surface feel useful, MVP-2 adds `propose_manifest_diff` and the apply gate.

---

## In scope (MVP-1)

| Area | What ships |
|---|---|
| **Adapters** | `AgentAdapter` protocol; `ClaudeCliAdapter` with §11 subprocess isolation + auth probe; `DisabledAdapter` fallback. **No** `ClaudeApiAdapter`, **no** `LocalModelAdapter`. |
| **Tools** | Three read-only tools: `get_available_actions`, `get_available_components`, `get_field_contract`. **No** `get_data_schema_summary`, `get_current_manifest_section`, `validate_manifest_fragment`, `propose_manifest_diff`. |
| **Tool-call mechanism** | JSON-in-fenced-block protocol (ADR-076 §10.1) + `agent_tool_parser.py`. |
| **System prompt** | `config/ui/agents/blueprint_default.md` — registry-derived action summary, manifest structure rules, tool-call format instructions. Built once at session start; not regenerated mid-session. |
| **Per-turn context** | `active_workspace`, `current_manifest_section`. **Omits** `last_validation_error`, `row_counts` (no validator tool, no data tool). |
| **Persona flag** | `blueprint_agent_enabled` (Group D, fatal cascade per ADR-077) wired through bootloader and PersonaValidator. `developer` + `qa` only. |
| **Persona config block** | `blueprint_agent: { backend, instructions_file }` only. **No** `model`, `api_key_env`, `endpoint`, `gallery_awareness` keys (those gate the deferred backends/features). |
| **Chat panel UI** | Conversation log + submit input + single-flight gate + cold-start greeting + adapter-status banner. **No** decision-summary accordion, **no** pending-diff preview, **no** Apply/Reject buttons, **no** data-visibility toggle. |
| **Sidebar registration** | `blueprint_agent_chat` panel type in `app/modules/sidebar_registry.py`; mounted in BLUEPRINT right sidebar of `developer` + `qa` templates. |
| **CSS** | Minimal `.bp-agent-*` block in `config/ui/theme.css` (conversation bubbles, input, status banner). |
| **Subprocess isolation** | `agent_sessions/{uuid}/.cwd-marker` per session, POSIX `flock` single-flight. |
| **Two-Category Law** | Adapters + tools + parser + context builder live in `libs/blueprint_arch/`. Shiny wiring in `app/handlers/blueprint_handlers.py`. |

---

## Out of scope (deferred to MVP-2+)

| Deferred | Reason |
|---|---|
| `propose_manifest_diff` tool + diff renderer + Apply/Reject gate | The whole point of MVP-1 is to prove the read-only conversational seam works. Apply gate is the Phase-2 risk surface — diff serialisation, in-memory manifest mutation, DAG invalidation. |
| Decision-summary accordion | Depends on applied-diff history. Empty without `propose_manifest_diff`. |
| `validate_manifest_fragment` tool | Nothing to validate without diff proposals. |
| `get_data_schema_summary` + data visibility toggle | Adds the AquaSynthesizer reuse path + privacy UX. Not needed to prove the conversation loop. Defer until MVP-2 along with `propose_manifest_diff`. |
| `get_current_manifest_section` tool | Nice-to-have for context; agent can ask the user to paste sections in MVP-1. Re-evaluate after MVP-1 usage. |
| `ClaudeApiAdapter` + `LocalModelAdapter` | Multi-user / air-gapped deployments. Single-user `claude_cli` proves the protocol first. |
| `BP-AGENT-REPORT-1` (per-session bundle) | `conversation.jsonl` will already exist as a side-effect of `claude_cli` subprocess working dir. Formal Quarto report + `manifest_sha256.txt` is meaningful only once a manifest fragment has been applied. |
| Token-by-token streaming | ADR-076 §9 — buffered for all backends. |
| `gallery_awareness` flag implementation | Reserved flag stays false. |
| `full_sample` data visibility mode | Gated by `developer` persona only — no value without a data tool. |

---

## MVP-1 implementation tasks

Subset of the 9 tasks listed in ADR-076 §Consequences. Order matters — each gate must close before the next starts.

| Order | Task ID | Effort | Done when |
|---|---|---|---|
| 1 | `BP-AGENT-FLAG-1` | `[haiku/low]` | Flag in 8 templates, `developer`+`qa` only true. PersonaValidator Rule 7 fatal cascade verified. |
| 2 | `BP-AGENT-1` (scoped) | `[sonnet/high]` | `AgentAdapter` protocol + `ClaudeCliAdapter` (with §11 isolation + auth probe) + `DisabledAdapter`. No `ClaudeApiAdapter`/`LocalModelAdapter` stubs. Headless test: drive a session via Python script with a fake project dir. |
| 3 | `BP-AGENT-PARSER-1` | `[sonnet/medium]` | Fenced-block extractor, JSON validator, dispatch table for the three MVP tools. Unit tests for happy path + malformed marker + invalid JSON. |
| 4 | `BP-AGENT-TOOLS-1` (scoped) | `[sonnet/medium]` | `get_available_actions`, `get_available_components`, `get_field_contract` only. Each wraps an existing `manifest_navigator` / registry call. Unit tests against the live ST22 manifest. |
| 5 | `BP-AGENT-INSTRUCT-1` (scoped) | `[sonnet/medium]` | `blueprint_default.md` — registry summary + structure rules + tool-call format + explicit *no propose_manifest_diff* instruction. Read by adapter at session start. |
| 6 | `BP-AGENT-PANEL-1` | `[haiku/low]` | `blueprint_agent_chat` registered in `sidebar_registry.py`; added to BLUEPRINT `right_sidebar.panels` of `developer_template.yaml` + `qa_template.yaml`. |
| 7 | `BP-AGENT-UI-1` (scoped) | `[sonnet/medium]` | Conversation log + submit input + cold-start greeting + adapter-status banner + single-flight gate. **No** decision accordion, **no** Apply gate, **no** data toggle. Reduces this task from `high` to `medium`. |
| 8 | `BP-AGENT-CSS-1` | `[haiku/low]` | `.bp-agent-*` block — conversation bubbles, input row, status banner. |

Tasks dropped from MVP-1: `BP-AGENT-REPORT-1`.

Estimated calendar: 2–3 focused sessions (Sonnet) for BP-AGENT-1/PARSER-1/TOOLS-1; one session for INSTRUCT-1 + UI-1; one session for PANEL-1/CSS-1/FLAG-1. Roughly **1 week of focused work** vs. 4–6 weeks for the full ADR-076.

---

## Acceptance criteria (when MVP-1 is "done")

1. `qa` persona launches with the BLUEPRINT chat panel visible. `pipeline-static` does not.
2. With Claude Code installed and logged in: opening the chat panel shows the cold-start greeting; submitting "what actions can I use in tier1?" produces a buffered response that includes a tool call to `get_available_actions` and the agent's interpretation of the result.
3. With Claude Code missing or logged out: the panel renders the "agent unavailable" banner with the cause, and submitting is disabled.
4. Two concurrent submits within the same session: the second is blocked by the single-flight gate (UI message + backend `flock`).
5. `from blueprint_arch.agent_adapter import ClaudeCliAdapter` works headlessly. A debug script can drive a full turn loop without Shiny.
6. PersonaValidator rejects a template with `blueprint_agent_enabled: true` and `blueprint_enabled: false` (ADR-077 fatal cascade).
7. The 97-test baseline still passes.
8. No emoji in any new `.py` files (rules_code_quality.md §1).
9. New files carry `@deps` blocks; `build_dep_graph.py` runs clean.

---

## What MVP-1 deliberately leaves unproven

- **Whether `propose_manifest_diff` is reliable enough to ship.** That is MVP-2's job. MVP-1 only proves the conversation channel, the tool-call protocol, and the persona/flag/cascade plumbing.
- **Whether scientists find the agent useful.** MVP-1 is `developer` + `qa` only. Scientist personas (`advanced`, `independent`) are switched on in MVP-3 once the apply gate exists.
- **Multi-user safety.** `claude_cli` is single-user by design. MVP-2 adds `ClaudeApiAdapter` for Posit Connect / Galaxy / IRIDA.

---

## Promotion criteria — MVP-1 → MVP-2

Open MVP-2 only when **all** of:

- MVP-1 acceptance criteria pass on the `qa` persona for at least one full session of real usage by the maintainer (not just smoke tests).
- The fenced-block protocol misparse rate is below 1 in 20 turns on real conversations (instrumented via the parser's error counter).
- The conversational tempo (turn latency, buffered responses) is judged acceptable by the maintainer in actual manifest-design work.

If any of those fail: iterate on MVP-1 (better system prompt, parser hardening) before adding the apply gate.
