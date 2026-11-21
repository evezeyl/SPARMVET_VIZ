# BLUEPRINT-REVIEW-1, step 5: the Claude AI agent in BLUEPRINT, planned against existing

Written 2026-11-21 by a worker of BLUEPRINT-REVIEW-1 (D-0395). It builds nothing and decides nothing. Labels as in `04_what_blueprint_must_be.md` (read, read-1, run, document, reading of this review). No model was called in this review.

## Summary (10 lines)

1. The owner's words: "we had also claude ai agent integrated" and "We had only planned to add - not all was build - will be integrated in CLI and via API" (`ORDER.md`). There is no other ledger line on the agent.
2. Planned (ADR-076): a chat helper in BLUEPRINT's right panel that interviews the user, reads the registry and the recipe, and proposes changes that the user applies; three backends (Claude Code CLI, Claude API, a local model) behind one interface.
3. Built (MVP-1, May 2026): the interface, the CLI backend, a disabled fallback, three read-only tools, the instructions file, the chat panel, the switch `blueprint_agent_enabled` (on in `developer` and `qa`).
4. Not built: the API backend, the local backend, the tool that proposes a change, the Apply gate for the agent's proposals, the data summary tool, the session report.
5. New finding, by running the code paths without calling a model: the chat cannot work today. The panel calls the adapter with an argument it does not accept, never opens a session, and builds the prompt with the instructions file in the place of the recipe.
6. Even if those calls were fixed: the recipe context fails to read every shipped recipe (`!include` is not read), and the CLI is started with a `--system` flag that the installed Claude Code (2.1.291) does not list.
7. The prompt tells the model it has seven tools, four of which do not exist, including the "only path" to propose a change.
8. The switch mistake noted in step 1 is real: turning the agent off also removes most of BLUEPRINT (Joint Designer, groups, "+ New", Validate, plot defaults).
9. Security: with the CLI backend, Claude Code's own tools (read files, write files, run commands) are not restricted; the model could read any file the user can read. The API backend would have no such tools.
10. The open choices A to E of the options document are restated below; the API backend (A) and the protection of the app (B) come before any write tool; the role file (D) comes before the proposal tool.

---

## 1. Her words and what is recorded

| Source | What it says | Status |
|---|---|---|
| `ORDER.md` (M421) | "and we had also claude ai agent integrated"; step 5: "We had only planned to add - not all was build - will be integrated in CLI and via API" | her words |
| Ledger | No DECIDED line on the agent's design. D-0395 is this review. D-0263 ("Any child process the app starts uses `sys.executable`") concerns Python child processes, not the `claude` binary | read (grep of the ledger) |
| `.claude/design/adr076_mvp2_backend_options.md` section 1a | Records "Eve's follow-up (2026-11-09)": only the one recipe of the session may change; read the app's code, never write it; "a single file to adjust ... what the agent may and may not do"; `claude_cli` "will likely be Eve-only", `claude_api` for other developers; the feature "fully switchable off with zero effect on Blueprint" | document, not a ledger line: in this file these are not counted as her decisions |
| `spaces/BLUEPRINT.md`, Open Questions | Bracketed answers attributed to her in the design file: "AI advises - ... Never blocking - but encouraging discussion"; "I think we should have a definition file fo[r]..." | document (locked in ADR-082 §2a, "decided with Eve"), not a ledger line |

---

## 2. What was planned

| Piece | Where planned | What it says |
|---|---|---|
| One interface, three backends | ADR-076 §1 | `claude_cli` (phase 1, local login, single user), `claude_api` (phase 2, `ANTHROPIC_API_KEY`, multi-user, Posit Connect, Galaxy), `local` (phase 3, an Ollama-like endpoint, offline), and `disabled` |
| "The agent never modifies the manifest directly" | ADR-076 key principle | Every change through one tool (`propose_manifest_diff` in the ADR; `propose_data_analysis_recipe_diff` in the code's prompt), shown as a diff, applied by the user's click |
| Seven tools | ADR-076 §3 | `get_available_actions`, `get_available_components`, `get_field_contract`, `get_data_schema_summary`, `get_current_manifest_section`, `validate_manifest_fragment`, `propose_manifest_diff` |
| Data visibility switch | ADR-076 §4 | off / schema summary (default: column names, types, counts, top 20 values; "No raw rows ever") / full sample (first 5 rows, developer setup only) |
| Panel parts | ADR-076 §5 | conversation, decision summary, pending diff, Apply, Reject, data visibility switch; one request at a time |
| Session report | ADR-076 §7 | `conversation.jsonl`, `report.qmd`, a hash of the recipe fragment, under `agent_sessions/<uuid>/`, "git-ignored" |
| CLI isolation | ADR-076 §11 | one working folder per session, a lock, `--continue` inside that folder, a login probe at start |
| MVP-1 scope | `adr076_mvp.md` | CLI + disabled only; the three read-only tools; instructions file; chat panel without Apply; switch on in `developer` and `qa` only. Promotion to MVP-2 after "at least one full session of real usage by the maintainer", a tool-call parse error rate below 1 in 20, an acceptable tempo |
| MVP-2 options | `adr076_mvp2_backend_options.md` (2026-11-09, "OPTIONS FOR REVIEW") | Decisions A to E (section 5 below); a proposed order: run MVP-1 once, then the API backend and a role file, then the proposal tool, then CLI hardening, then the split of the instructions |
| Advise, never block | ADR-082 §2a (document) | "advise-only, NEVER blocking", Socratic; `spaces/BLUEPRINT.md` says "advises and enforces good practices" (contradiction L11 of `02`) |

---

## 3. What exists in the code

| Piece | State | Evidence | Label |
|---|---|---|---|
| Interface `AgentAdapter` | built | `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:59-74` | read-1 |
| `DisabledAdapter` | built | `agent_adapter.py:80-110` | read |
| `ClaudeCliAdapter` | built: a folder per session under `<project root>/agent_sessions/`, a lock, a login probe (`claude --version`, then `claude -p "ok"` with a 30 s timeout) | `agent_adapter.py:133-195`, `:196-224` | read |
| The command line | first turn `claude --output-format text --system <prompt> -p <message>`; later turns `claude --continue --output-format text -p <message>`; no `--allowedTools` or `--disallowedTools` | `agent_adapter.py:270-282` | read |
| `--system` flag | not listed by the installed CLI, whose help lists `--system-prompt` and `--append-system-prompt`; whether the CLI rejects `--system` was not run (it would call the model) | `agent_adapter.py:273` | read; run: `claude --help` (version 2.1.291) |
| `claude_api`, `local` | not built: the factory returns `DisabledAdapter("Backend ... is not implemented in Phase 1")`; no `anthropic` dependency in any `pyproject.toml` | `agent_adapter.py:398-403`; grep of `pyproject.toml` files | read |
| Choice of backend | `blueprint_agent.backend` in the app features file: `claude_cli` in `developer`, `disabled` in `qa` ("QA mocks the adapter"); model `claude-opus-4-7` written but unused (stale name, the options document says) | `config/app_features/developer.yaml`, `qa.yaml` (`blueprint_agent:` block) | read |
| The switch | `blueprint_agent_enabled`: on in `developer`, `qa`; off elsewhere; fatal without `blueprint_enabled` (ADR-077) | `config/app_features/*.yaml` lines 11 to 29 | read |
| Where the adapter is made | `Bootloader.get_agent_adapter()` builds it once, `DisabledAdapter` when the switch is off | `app/src/bootloader.py:1010-1040` | read |
| Tools that exist | three: `get_available_actions`, `get_available_components`, `get_field_contract` (the last returns `input_fields` and the tiers, no `output_fields`, D-0075) | `agent_tools.py:39`, `:64`, `:140`, `:205` | read |
| `get_field_contract` path | reads the recipe at any path the model gives (`data_analysis_recipe_path` argument); no check that it is the session's recipe | `agent_tools.py:234-260` | read |
| Tool-call parser | fenced JSON blocks, at most 3 rounds | `agent_tool_parser.py`; `H:1864` (`for _round in range(3)`) | read |
| Instructions file | `config/ui/agents/blueprint_default.md` (202 lines): prefixed action names; old plot names (`geom_bar`, line 162); a contact rule ("never invent a contact", line 169) | the file | read (grep) |
| Prompt builder | instructions + action registry summary + the active recipe (path, tables and their source paths, groups, plot ids) + the tool-call protocol | `agent_context.py:34-66`, `:123-160` | read |
| The protocol text lists 7 tools | four do not exist (`get_data_schema_summary`, `get_current_data_analysis_recipe_section`, `validate_data_analysis_recipe_fragment`, `propose_data_analysis_recipe_diff`, "THE ONLY PATH to propose changes"); it also says "One column per mutate step" (old action name) | `agent_context.py:164-217` (list at 187-194, "mutate" at 212) | read |
| Chat panel | conversation, input, Send, status banner; in the right sidebar through the slot `blueprint_agent_chat` (gate `blueprint_agent_enabled`) | `H:1774-1830`; `config/ui/sidebars/blueprint_standard_right.yaml`; `app/modules/sidebar_registry.py:59-62` | read |
| Session report | only `conversation.jsonl` and `session_meta.json` (the prompt and context) in the session folder; no `report.qmd` | `agent_adapter.py:213-216`, `:362-368` | read |
| `agent_sessions/` in git | not ignored | run: `git check-ignore -v agent_sessions/x/session_meta.json` (no match) |
| Tests | the adapter at start (`app/tests/test_agent_adapter_at_startup.py`), the instructions shape, the three tools (`libs/blueprint_arch/tests/test_agent_tools.py`, which calls `build_system_prompt()` with no argument). No test sends a message through the panel's handler | grep of `app/tests`, `libs/blueprint_arch/tests` | read |

### 3.1 What happens today when a user presses Send (developer setup)

Traced by reading `H:1829-1911`, with the calls checked by running the same functions (no model called):

1. The handler makes a session id itself (`_get_or_create_session`, `H:1697-1702`); it never calls `adapter.start_session`, so the CLI adapter has no such session (read).
2. It builds the prompt with `build_system_prompt(instructions_file)` (`H:1859`). The first positional argument of that function is the **recipe path** (run: `inspect.signature(build_system_prompt)` gives `(data_analysis_recipe_path=None, *, instructions_file=None, project_root=None)`). Result (run: the same call in a one-liner): the instructions are not in the prompt; the "Active Data Analysis Recipe" section is the instructions file read as YAML, with "parse error"; no recipe is given.
3. It calls `adapter.send_message(session_id, message, system_prompt=system_prompt)` through `asyncio.to_thread` (`H:1865-1870`). `send_message` takes `(session_id, message, tools=None)` and no `system_prompt` (run: `inspect.signature(ClaudeCliAdapter.send_message)`). Reading of this review: Python raises a TypeError, the `except` at `H:1904-1910` shows "[Agent error: ...]" in the conversation. Not run in the app.
4. Had the call gone through: `send_message` returns an `AgentResponse` object while the handler passes it to the parser as text (`H:1871`, read); and the CLI adapter would answer "Session not found" (step 1).
5. Had the recipe been given: the recipe context reads the main file with `yaml.safe_load`, which does not read `!include`; for every shipped recipe it gives "could not determine a constructor for the tag '!include'" (run: `_build_data_analysis_recipe_context` on `1_Abromics_general_pipeline.yaml`, `1_test_data_ST22_dummy.yaml`, `2_test_data_ST22_dummy.yaml`, `3_test_no_joins.yaml`).

Reading of this review, not decided: MVP-1 is recorded as "IMPLEMENTED" with "Smoke tests: 14 passed" (ADR-076 status), but no test covers a message through the handler, and the promotion criterion "one full session of real usage" cannot have been met with this wiring. When it broke is not known (not traced in git).

### 3.2 The switch mistake (from step 1, confirmed)

`if not bootloader.is_enabled("blueprint_agent_enabled"): return` at `H:1690-1691` ends the registration of the handler. Everything after it registers only with the agent switch on: the plot-defaults form, the chat, the Joint Designer, the groups and plots inventory, the info form, "+ New", Validate, the draft status, the import error panel (read-1: `H:1716` to `H:2933`). So in `standalone` (BLUEPRINT on, agent off) these are empty. ADR-076 promised "Existing BLUEPRINT IDE behaviour is unchanged when the flag is off" and the options document states the kill switch is "already built, confirmed"; the code says otherwise (contradictions L18, L20 of `02`).

---

## 4. Planned against existing, one table

| Planned | Exists | Gap |
|---|---|---|
| CLI backend | built | wiring broken (3.1); `--system` not a listed flag; native tools unrestricted |
| API backend | no | the whole adapter; a dependency (`anthropic`); the key handling (E) |
| Local backend | no | not started; no option studied since ADR-076 |
| 7 tools | 3 | the proposal tool, the data summary, the recipe section reader, the fragment check |
| Proposal and Apply gate | no | the central safety piece of ADR-076 |
| Data visibility switch | no | and no data tool, so nothing data-related is sent today |
| Decision summary, session report | no | only the conversation log |
| Role file (what the agent may do) | no | options document §5 |
| Advise, never block | instructions text only | nothing blocks, because nothing writes |
| Switch off with no effect | no | 3.2 |
| A model name that exists | written `claude-opus-4-7` | the options document names `claude-sonnet-5-5`, `claude-opus-5-5` (document) |
| `agent_sessions/` git-ignored | no | run |

---

## 5. The open choices A to E, in plain words

From `adr076_mvp2_backend_options.md` (document). Unranked except where one blocks another. The document's own recommendations are given as its recommendations, not as decisions.

### A. How to build the API backend

| Option | In plain words | Pros | Cons |
|---|---|---|---|
| A1 | The app talks to the Claude API directly with Anthropic's Python library and hands it the exact list of tools | Smallest piece of new code; the model can only use the tools listed (no hidden tools); works from any deployment over HTTPS; native tool calls instead of parsing text | The app keeps the conversation itself; each call is paid with API credits; a new dependency |
| A2 | Use the Claude Agent SDK (the library under Claude Code) | Ready-made loop and long-conversation handling if the agent grows | Harder to prove that only the listed tools can run (the document found no clear documentation); more to learn |
| A3 | Keep only the CLI and harden it | Uses the existing login (no API cost on a subscription) | Single user; a deployment would bill at API rates anyway when a key is set; login problems reported in containers (document) |

The document recommends A1 and a policy: the CLI only on the maintainer's own machine, the API for everyone else (document; her follow-up is recorded there, not in the ledger).

### B. How to make sure the agent cannot change the app

| Option | In plain words | Pros | Cons |
|---|---|---|---|
| B1 | Use the API backend for anything that proposes a change | No hidden tools exist there, by construction | Needs A built |
| B2 | Start the CLI with flags that switch off its own tools (`--disallowedTools` or an empty allow list) | One line, cheap | Reported to be unreliable in some CLI versions in non-interactive mode (document) |
| B3 | A test that asks the agent to write outside its folder and checks that it fails | Proves the protection instead of trusting a flag | A test that calls a model (cost, network) |
| (with all) | The proposal tool accepts only the one recipe of the session as target | The check runs in the app's code, not in the model | Needs the proposal tool and D |

### C. Where the "good practice" knowledge lives

| Option | In plain words | Pros | Cons |
|---|---|---|---|
| C1 | Grow the one instructions file | Simple | Drifts from the rule files written for the same job |
| C2 | Two files: one of shared rules and data-science practice, one of domain knowledge (for example AMR) | A deployment swaps the domain file; the rules stay one | A small change to how the prompt is built (a list of files) |
| C3 | Generate the rules part from the existing rule file (`rules_agent_role_bioscientist.md`) | One source of truth | A generation step to keep simple |

The document recommends C2 now, C3 later.

### D. One file that says what the agent may do and which role it plays

| Option | In plain words | Pros | Cons |
|---|---|---|---|
| D1 | A small YAML per agent role (allowed tools, write scope "the session's recipe only", read scope "registry and field lists only", allowed backends, default model), checked by the app before each tool call | Change the agent's rights without touching code; a stricter role for another deployment is one more file | A new file format to check; must fail closed (no file or a bad file means no agent) |
| D2 | No role file: rights written in code | Nothing new | Every change of rights is a code change; not what the follow-up asks (document) |

The document uses the word "agent role", not "persona" (ADR-091 retired "persona" for the app's setups).

### E. Where the API key is kept

| Option | In plain words | Pros | Cons |
|---|---|---|---|
| E1 | An environment variable (`ANTHROPIC_API_KEY`), read at start, a clear error if missing, as the IRIDA token is read today | Same on every machine and deployment; already the documented rule | A key in a shell profile is plain text |
| E2 | E1, plus a small start script on the maintainer's machine that reads the key from KDE Wallet and sets the variable | The key is not in a file in plain text | Only for a desktop; the app never knows the wallet |

The document recommends E1 now, E2 as an optional convenience.

### Choices the document does not list (found in this review)

| # | Choice | Options |
|---|---|---|
| F | Repair MVP-1 before anything else | fix the panel's calls (3.1), the recipe context (`!include`), the CLI flag, the prompt's tool list, then run one real session as the MVP promotion criterion asks / leave MVP-1 as it is and build A1 directly |
| G | What the agent switch gates | only the chat (as planned) / as built |
| H | Whether the agent is shown to scientists' setups | after the proposal tool and Apply gate exist (`adr076_mvp.md` MVP-3) / earlier, read-only |
| I | The local (offline) backend | keep in the plan / drop / study when an offline deployment asks |
| J | The session folder | under the project root (as built, not git-ignored) / the user's data location of the deployment / git-ignore it |

### What blocks what

| Choice | Blocks | Why |
|---|---|---|
| F (repair) | the MVP-1 to MVP-2 promotion | "one full session of real usage" cannot happen while every message fails |
| A (API backend) | B1, E | B1 is a property of A; only the API needs a key |
| B (protection) | any write tool; showing the CLI agent on real recipes and data | the CLI's own tools can read and write files |
| D (role file) | the proposal tool's scope check | the options document: the check "needs somewhere to read `write_scope` from" |
| The proposal tool and Apply gate | H (scientists), the session report | ADR-076: the report and the decision summary are built from applied proposals |
| G (switch) | none; it is independent and touches the rest of BLUEPRINT | - |
| C | none | content only |

---

## 6. Privacy and security points to decide (not decided)

What would leave the machine, by backend, as the code is written today (if the wiring of 3.1 worked):

| What | CLI (as built) | API (planned) | Label |
|---|---|---|---|
| The user's typed text | sent | sent | read |
| The instructions file | sent (when the call is fixed) | sent | read |
| The action and component registry summary (names, descriptions) | sent | sent | read |
| The recipe's path, table names, source file paths, group and plot ids and labels | sent in the prompt | sent | read (`agent_context.py:123-160`) |
| The recipe's steps and declared fields | sent when the model calls `get_field_contract`; for any path the model names | same unless the path is pinned | read (`agent_tools.py:234-260`) |
| The recipe's `info.contact` | not read by the prompt builder; but the CLI's own file tools could read the whole recipe file | not sent unless a tool sends it | read; reading of this review |
| Data rows | not sent by the app's tools (no data tool); the CLI's own tools could read the data files | not sent today; planned "schema summary" sends column statistics and up to 20 top values per text column (values may be sample ids); "full sample" sends 5 rows | read; document (ADR-076 §4) |
| Any file the user can read | possible through the CLI's own Read and Bash tools (no flag restricts them) | not possible: only the listed tools | read; document (options §3b) |
| A call at app start | yes: the login probe sends "ok" to the model when the app starts with the agent on | no (the adapter would only read the key) | read (`agent_adapter.py:175-180`) |
| Copies kept on the machine | `agent_sessions/<uuid>/` (prompt, context, conversation) under the project root, not git-ignored; the CLI may keep its own history (not checked) | the conversation log, if kept | read; run |

Points to decide:

1. Which backends may run with real (non-synthetic) data, and on which deployments.
2. Whether the CLI backend is allowed at all without a proven restriction of its own tools (B2 plus B3).
3. Whether `get_field_contract` and any later tool are pinned to the session's recipe.
4. Whether the data summary may include top values of text columns (sample ids, farm names) and whether "full sample" exists.
5. Whether the recipe's `contact` and `author` fields may be sent.
6. Where the session folder lives, how long it is kept, and whether it is git-ignored.
7. Whether the login probe at start (a model call, up to 40 s with no message, task AGENT-PROBE-1, document) stays.
8. Whether the user is told, in the panel, what is sent and to whom.

---

## Not verified

- No model was called: the failure of 3.1 step 3 is read from the signatures, not seen in the app; whether the CLI accepts `--system` is not known.
- When the wiring broke (which commit) was not traced.
- The CLI's own history location and retention were not checked.
- `agent_tool_parser.py` was not read line by line.
- The bootloader's handling of `instructions_file` beyond `get_agent_config()` was not traced.
- The external sources listed in the options document (CLI flag bugs, Agent SDK permissions) were not re-checked.

## To decide (for the guide)

| # | Choice | Options in short | Blocks |
|---|---|---|---|
| F | Repair the MVP-1 wiring first | repair and run one real session / skip to the API backend | promotion to MVP-2 |
| G | What the agent switch gates | the chat only / as built | - |
| A | API backend | A1 Anthropic library / A2 Agent SDK / A3 CLI only | B1, E |
| B | Protection of the app and of files | B1 API for proposals / B2 CLI flags / B3 a proving test (combinable) | any write tool; CLI on real data |
| C | Good-practice text | C1 one file / C2 two files / C3 generated | - |
| D | Role file | D1 YAML role file checked in code / D2 rights in code | the proposal tool's scope |
| E | API key | E1 environment variable / E2 plus a wallet start script | - |
| H | Scientists' setups | after the Apply gate / earlier read-only | - |
| I | Local backend | keep / drop / later | - |
| J | Session folder | project root / user's data location / git-ignore | - |
| P1-P8 | The privacy points of section 6 | as listed | B, H |
