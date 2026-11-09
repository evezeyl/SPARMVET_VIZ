# ADR-076 MVP-2 Options — API Backend, Sandboxing, and Instructions Content

**Status:** OPTIONS FOR REVIEW (2026-11-09) — nothing in this document is implemented yet.
**Authority:** Narrows ADR-076 and `adr076_mvp.md` to the three concrete decisions Eve raised
when she got Claude API credits. Read `adr076_mvp.md` first — this picks up exactly where it
leaves off (MVP-2).

**Why this document exists:** Eve asked for "a solution where we can use agents via API and
agents via CLI," a place to put best-practice instructions for the agent, and a guarantee that
the agent "will not be allowed to modify anything to the app code — only create new manifests."
This is not a greenfield design — ADR-076 already answered most of it. What follows is (1) a
status check against the real code, so the decision is grounded in what exists, not what the
ADR assumed would exist, and (2) the few things ADR-076 did not resolve, with options.

---

## 1. Status check — what ADR-076 already decided, verified against the code today

| Question | Already decided? | Evidence |
|---|---|---|
| One protocol, swappable backends | **Yes** | `AgentAdapter` Protocol in `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` — `start_session` / `send_message` / `end_session`. `make_adapter(backend, project_root, instructions_file)` is the single factory call site. |
| CLI backend | **Built** | `ClaudeCliAdapter` — subprocess `claude -p` in an isolated `agent_sessions/{uuid}/` dir, POSIX flock single-flight, auth probe at init, falls back to `DisabledAdapter` on failure. |
| API backend | **Scoped, not built** | `make_adapter()` line 399-403: `claude_api` and `local` both return `DisabledAdapter("not implemented in Phase 1")`. ADR-076 §1 names it `ClaudeApiAdapter` (Phase 2) and even already names the config keys (`model`, `api_key_env`) — they're sitting unused in `developer.yaml` / `qa.yaml` today. |
| Where instructions live | **Built** | `config/ui/agents/blueprint_default.md`, loaded via `blueprint_agent.instructions_file` in the app features file, assembled by `agent_context.build_system_prompt()` into: (1) your instructions file, (2) a live-generated summary of registered actions/components, (3) the active data analysis recipe's current structure, (4) the tool-call protocol. This already is "a place to put the instructions" — nothing new to build here, only content to add. |
| "Agent cannot touch app code, only proposes manifest/recipe content" | **Decided in principle, not enforced in code yet** | ADR-076 calls this a "non-negotiable" invariant, routed through one tool: `propose_data_analysis_recipe_diff`. **That tool does not exist.** `agent_tools.py` only has the three read-only tools (`get_available_actions`, `get_available_components`, `get_field_contract`). Today the agent cannot write anything at all — it can only talk and read the registry/contracts. `adr076_mvp.md` confirms this was deliberate: MVP-1 is read-only by design, MVP-2 is where the diff/apply tool was always meant to land. |

**Bottom line:** this is Phase/MVP-2 of a plan that already exists. The three things Eve is
asking for are the three things MVP-2 was always going to need. Nothing here requires picking a
new architecture — it requires finishing the one already on paper, plus closing one gap ADR-076
didn't anticipate (§3 below).

**There is already a task waiting for this exact moment:** `.claude/tasks/tasks.md` line 215,
`[@user] BLUEPRINT-AGENT-API-1`, logged 2026-11-07 with a note to revisit "around 2026-11-14
when Claude API credits are available." This document is that revisit, five days early.

---

## 1a. Refinements from Eve's follow-up (2026-11-09) — narrower than §1–4 first assumed

Five more specific requirements came in after the first pass. Each tightens one of the
decisions below rather than opening a new one:

1. The agent may change **only the one recipe currently being built in the active session** —
   not "any file under `config/data_analysis_recipes/`" as §3a first proposed. Narrower scope,
   §3a revised below.
2. It may **read** the app's code (to know what's registered) but must **never write** it —
   "we do not want the app to suddenly stop working." This was already the `@bioscientist`
   agent role's rule (`rules_agent_role_bioscientist.md` §0-B, "Scan-Only Mode for `libs/` —
   never modify `.py` files"); the Blueprint Agent should inherit the same discipline, enforced
   the same way the API backend already enforces it structurally (§3b).
3. A single file to adjust, easily, what the agent may and may not do, and which role it plays
   — see new §5 (Decision D) below.
4. `claude_cli` will likely be Eve-only; `claude_api` is for other developers too — this
   sharpens Decision A's recommendation into a policy, not just a preference (§2 revised).
5. Whether `claude_cli` can even work in a deployed context at all, and confirmation that the
   feature must be fully switchable off with zero effect on Blueprint when it is — the second
   half is already true today (§6 below); the first half is answered in §2.

---

## 2. Decision A — How to build `ClaudeApiAdapter`

Three real options. All satisfy "agents via API" — they differ in control, reliability, and
what they cost to build and maintain.

### Option A1 — `anthropic` Python SDK, direct `messages.create()` calls (what ADR-076 §1/§10 already specified)

You own the loop: a `messages` list you append to each turn, `tools=[...]` passed explicitly
on every call, native `tool_use` / `tool_result` content blocks instead of the fenced-block
regex parser the CLI backend needs.

- **Internal resources needed:** new `ClaudeApiAdapter` class in `agent_adapter.py` (same
  Protocol, so nothing else in the app changes); a `pyproject.toml` dependency declaration.
- **External resources needed:** `anthropic` PyPI package; `ANTHROPIC_API_KEY` env var (Eve's
  credits); a model id — the config currently says `claude-opus-4-7`, which is stale (current
  family: Sonnet 5.5 `claude-sonnet-5-5`, Opus 5.5 `claude-opus-5-5`). Sonnet 5.5 is the right
  default for this task (manifest design is not the hardest reasoning tier); Opus 5.5 as an
  optional override for a harder session.
- **Pros:** Smallest amount of new machinery. No hidden tool access — the model can only call
  what you hand it in `tools=`, which is the strongest answer to Decision B below. Works from
  any deployment (Posit Connect, Galaxy, IRIDA) since it's plain HTTPS, no local CLI/auth
  dependency, no per-user Claude Code login. Matches what ADR-076 already named.
  Streaming is available later without changing the Protocol (§9 of ADR-076 already noted this).
- **Cons:** You write and maintain your own turn-state management (no `--continue` convenience);
  you're responsible for context-window bookkeeping if a session runs long; no free local-login
  reuse — API usage bills against Eve's credits per call.
- **Verdict:** This is the one ADR-076 already chose. Nothing found while researching this
  changes that call.

### Option A2 — Claude Agent SDK (the same harness Claude Code runs on, as a Python/TS library)

Gives you a prebuilt agentic loop, its own permission/hook system, and tool-definition
ergonomics, instead of the raw Messages API.

- **Internal resources needed:** same adapter slot, different implementation; more surface
  area to learn (the SDK's own session/hook model) than A1.
- **External resources needed:** the Agent SDK package; still needs `ANTHROPIC_API_KEY`.
- **Pros:** If the agent's scope grows later (multi-step autonomous work, not just one
  conversational turn), the SDK's loop and context-compaction machinery save you from
  reinventing them.
- **Cons:** Research during this session found no clear documentation of how strictly the
  SDK's own permission/hook system can be locked down to "only these N tools, nothing else,
  ever" — the general guidance found was that scope is *easier* to guarantee when you write the
  loop yourself (Option A1) than when you rely on a framework's permission layer. For a task
  this narrow (read 3 things, propose one diff), the SDK's main value — managing an open-ended
  multi-step loop — isn't needed yet.
- **Verdict:** Worth re-opening only if the agent's job grows past "interview, inspect, propose
  one diff" into something genuinely open-ended. Not now.

### Option A3 — Keep using the CLI backend, but harden it

Not a new backend — a note that "CLI" and "API" are not just a convenience choice, they're also
a cost/control tradeoff: CLI reuses Eve's existing Claude Code login (free against whatever
plan she's on), API spends the new credits per call. Both are worth keeping, exactly as
ADR-076 designed, for different deployment shapes (CLI = single-user/desktop, API = multi-user).
This option is about making the CLI path safer, not replacing it — see Decision B.

**Recommendation for Decision A:** Build **A1** (`anthropic` SDK, direct). It is the smallest
change, it is the one already named in the ADR, and — importantly — it is also the cleanest
answer to Decision B, below.

### A4 — Can `claude_cli` work in a deployment at all? (Eve's direct question)

Checked this explicitly. The Claude Code CLI **does** support non-interactive, API-key-only
auth (`ANTHROPIC_API_KEY` env var, or `--bare` mode for scripted use) — so technically, yes, it
could run inside a Galaxy/Posit Connect/IRIDA container without an interactive login. But three
things make this the wrong tool for that job rather than a real option:

- The moment `ANTHROPIC_API_KEY` is set, the CLI **bills at pay-as-you-go API rates, not the
  subscription** — so you gain none of the "reuse the login, it's free" advantage that makes
  `claude_cli` attractive for Eve's own machine. You'd be paying API prices for the clunkier
  mechanism.
- Current bug reports (2026, headless/VPS/container setups) describe the CLI's login wizard
  still appearing in some non-interactive environments even with the key set — an unreliable
  foundation for something that must not break.
- It's still a subprocess-per-turn design with the single-flight flock from §11 of ADR-076 —
  fine for one developer, awkward for concurrent users on a shared deployment.

**Policy, not just preference:** `claude_cli` is Eve's personal, local, interactive-login,
single-user backend — never declared in any app features file shared with other developers or
any deployment template. `claude_api` is the only backend ever enabled for multi-user or
deployed contexts. Worth making this an enforced rule later (the app features validator could
refuse `backend: claude_cli` outside a template explicitly marked local-only), the same
fail-fast philosophy ADR-077 already applies to other contradictory configs — but that
enforcement is a small follow-up, not a blocker to building A1.

---

## 3. Decision B — Enforcing "the agent may not touch app code"

This is the part ADR-076 under-specified, and it's worth being precise about, since it's the
constraint Eve cares most about.

### 3a. The mechanism ADR-076 already relies on: propose-before-apply

The intended safety net is entirely in **your own Python code**, not in the model's good
behaviour: `propose_data_analysis_recipe_diff` is the only tool that can suggest a change, it
returns a diff, the UI renders it, and nothing is written until the human clicks Apply. This
part is sound and matches the pattern already trusted elsewhere in the app (T3 audit gate,
BLUEPRINT IDE Apply gate) — but **it isn't built yet** (§1 table, last row). Building it is
MVP-2's real centerpiece, independent of which backend you pick.

The one thing worth adding beyond what ADR-076 wrote — and narrower than a first pass of this
document proposed: **pin the proposed `target` to the one recipe bound to this session, not
to a directory allowlist.** "Any file under `config/data_analysis_recipes/`" is too wide — it
would let the agent propose changes to a *different* recipe than the one the user opened it to
work on. The Layer 3 per-turn context (`agent_context.build_turn_context`) already carries
`current_data_analysis_recipe_section`; `start_session()` already receives the active recipe
path. The check is: `propose_data_analysis_recipe_diff`'s `target` must resolve to exactly that
path (or a file it legitimately `!include`s), or the tool returns an error instead of a diff.
That check lives in `agent_tools.py`, runs in your code, and holds regardless of what the model
decides to try — the system prompt's "safety rules" section is a courtesy to the model, not a
control.

**Read code, never write it.** The three existing read tools already only expose *registry
metadata* (`get_available_actions`/`get_available_components`: names, categories, tags, param
schemas from `ui_schema` — not source) and *resolved field contracts* — never raw `.py` source,
never a path under `libs/` or `app/`. That's the right boundary already, and it matches the
rule the `@bioscientist` agent role already lives under (`rules_agent_role_bioscientist.md`
§0-B): "Scan-Only Mode for `libs/` — never modify `.py` files," with any needed Python change
filed as a `@dasharch` handoff instead of attempted directly. The Blueprint Agent should be
held to the same line, for the same reason Eve just gave it independently: a change that can
stop the app from running is a different class of risk than a change to one recipe file, and
the agent should never be in a position to make the first kind, full stop — not "discouraged
from," not "warned against in the prompt," literally no tool that can do it.

### 3b. A risk ADR-076 did not anticipate: the CLI backend's hidden native tools

This is a genuine finding from this session, not something already documented anywhere in the
repo. `ClaudeCliAdapter.send_message()` invokes `claude -p "<message>"` — but that command does
not run a bare chat completion. It runs **the actual Claude Code CLI**, which comes with its
own built-in tools (Read, Write, Edit, Bash, …) completely separate from the three tools your
own fenced-block protocol defines. Nothing in today's subprocess call restricts those native
tools. The isolated `agent_sessions/{uuid}/` working directory limits the blast radius for
*relative* paths, but does not stop an absolute-path `Read`/`Write`, nor a `Bash cd ..`.

Checked whether this is fixable with CLI flags: `--disallowedTools "Bash,Write,Edit"` is the
documented mechanism, and it's real — but current GitHub issue reports on Claude Code describe
version-specific bugs where `--disallowedTools` / `--permission-mode` interactions don't
reliably hold in headless `-p` mode (one report: `bypassPermissions` mode skips
`--allowedTools` enforcement entirely in `-p`; another: `dontAsk` mode denies Write regardless
of config). This isn't a reason to abandon the CLI backend — it's a reason not to rely on CLI
tool-flags as the *only* guarantee for a constraint Eve considers non-negotiable.

**Three ways to close this, not mutually exclusive:**

| Option | What it does | Internal cost | External cost |
|---|---|---|---|
| **B1 — Prefer the API backend for anything touching real data analysis recipes** | The Messages API has **no implicit tools at all** — the model can only call what's in your `tools=` list (the 3 read tools + `propose_data_analysis_recipe_diff`). There is no hidden Write/Bash to restrict, because none exists. This is a property of the mechanism, not a configuration you have to get right. | None beyond building A1. | None beyond A1. |
| **B2 — Harden the CLI backend's subprocess call anyway** | Add `--disallowedTools "Bash,Write,Edit,NotebookEdit"` (or an explicit `--allowedTools` allowlist of nothing, since this backend doesn't need the model's native tools at all) to the `cmd` list in `send_message()`. Cheap, and worth doing regardless — defence in depth, even with known enforcement bugs in some versions. | Small — one line in `agent_adapter.py`; a test that asserts the flag is present in the constructed command. | None. |
| **B3 — Verify, don't just configure** | After B2, add a smoke test that actually tries to get the agent to write a file outside `agent_sessions/` and asserts it fails, rather than trusting the flag alone (the GitHub issues above are exactly "the flag didn't do what the docs say"). | One Playwright/headless test. | None. |

**Recommendation for Decision B:** Do B1 as the real guarantee — route anything that proposes
changes to a live data analysis recipe through the API backend, where the absence of hidden
tools is structural, not configured. Do B2+B3 as well for the CLI backend, since it's cheap and
it's the backend that reuses Eve's existing login — but document it as "defence in depth," not
as the guarantee, given the known version-specific enforcement bugs.

---

## 4. Decision C — Where the data-science / ADR best-practice knowledge lives

The *mechanism* is done (`instructions_file` → `build_system_prompt()`, §1 table). What's
missing is content, and a decision about how much of it to hand-write versus reuse.

`config/ui/agents/blueprint_default.md` today covers: the tool-call protocol, data analysis
recipe syntax rules (canonical `action:` keys, join key quoting, two-step casts), and some AMR
domain knowledge. It does **not** yet cover general data-cleaning judgment (when to filter vs.
drop-null vs. recode) or plot-choice judgment (which geom fits which data pattern — the same
judgment `rules_gallery_standards.md`'s taxonomy and `rules_viz_factory.md` already encode for
humans).

Two sources already exist in this repo that were written for almost exactly this job:

- **`.claude/rules/rules_agent_role_bioscientist.md`** — the `@bioscientist` persona. Scoped to
  YAML only, forbidden from touching `.py` files, required to interview before generating YAML,
  required to use only registered actions/components, required to file an Enhancement Request
  rather than invent a key. This is the same role, just written for a Claude Code session
  talking to Eve instead of an LLM talking to a scientist end-user.
- **`rules_gallery_standards.md` / `rules_viz_factory.md`** — the taxonomy of chart families,
  data patterns, and geoms already used to classify every gallery example. This is the
  plot-choice judgment the Blueprint Agent needs and doesn't have yet.

**Options:**

| Option | Approach | Tradeoff |
|---|---|---|
| **C1 — Hand-write more into `blueprint_default.md`** | Keep one file, grow it. | Simple, but two sources of truth drift apart over time (the `@bioscientist` rule changes, the agent's prompt doesn't, or vice versa). |
| **C2 — Split into composable instruction layers** | `build_system_prompt()` already concatenates sections — add a second file (e.g. `config/ui/agents/data_science_practices.md`) that extracts/condenses the relevant parts of `rules_agent_role_bioscientist.md` + the gallery taxonomy, loaded alongside the domain-specific file. `instructions_file` could become a list instead of one path. | A little more plumbing (one function signature change), but keeps the content modular — a future AMR-specific deployment swaps the domain file without touching the rules layer. |
| **C3 — Generate the rules layer from the existing `.md` rule file** | A small script extracts the parts of `rules_agent_role_bioscientist.md` that are safe/useful as agent-facing prompt text (skip the meta-instructions aimed at a Claude Code session, like "file a handoff," keep the YAML construction rules) and writes it into the agent's instructions file at build time or startup. | One source of truth, but adds a generation step that needs to stay simple enough not to become its own maintenance burden. |

**Recommendation for Decision C:** **C2** now, **C3** later if drift becomes a real problem. Two
files is cheap, keeps the content's purpose clear (one file = ADR/rules/data-science judgment,
reusable across deployments; one file = domain knowledge, swappable per deployment), and doesn't
require inventing a generation pipeline before you know if the agent's actual conversations need
more of this content or different content.

---

## 5. Decision D — one file to adjust what the agent may do, and which role it plays

Eve asked for "a file where we can adjust what it can do and not do in an easy manner and what
'persona' it has." Worth naming carefully: **this repo already retired "persona" as a word for
app-level config** (ADR-091 — what used to be called a persona is now an "app features" file,
specifically to stop that word meaning two different things). What Eve means here is a
different, legitimate concept — the agent's own role/character, the same idea as `@dasharch`
and `@bioscientist` in `.claude/rules/`, which CLAUDE.md §4 already calls **"Agent Roles."**
Using "agent role" here keeps the vocabulary distinction ADR-091 was for.

**Proposed shape** — one small YAML per role, separate from the prose instructions file,
because the instructions file is what the *model* reads and this file is what *your code*
enforces — two different jobs that shouldn't live in the same artifact:

```yaml
# config/ui/agents/roles/recipe_builder.yaml
role: recipe_builder
instructions_file: config/ui/agents/blueprint_default.md
allowed_tools:
  - get_available_actions
  - get_available_components
  - get_field_contract
  - propose_data_analysis_recipe_diff      # once built, §3a
write_scope: session_recipe_only            # enforced in agent_tools.py — see §3a
read_scope: registry_and_contracts          # never raw .py source, never app/ or libs/ paths
backend_allowed: [claude_api, claude_cli]   # which backends may run this role at all
model_default: claude-sonnet-5-5
```

**Where it's enforced, not just declared:** `call_tool()` in `agent_tools.py` checks the
requested tool name against the active role's `allowed_tools` before dispatching — a tool not
listed there returns an error to the model, the same way an unregistered tool name already does
today. `write_scope` is read by the `propose_data_analysis_recipe_diff` handler to decide what
`target` values it will accept (§3a). Editing this one YAML — adding or removing a line —
changes what the agent can do without touching any Python. A second role file (say, a
read-only "recipe reviewer" with an empty `write_scope` and no `propose_*` tool at all) is then
just a second small file, not a code change.

This also answers "what if we want a stricter or looser role for a different deployment" —
the `blueprint_agent:` config block gains one new key, `role: recipe_builder`, pointing at one
of these files, the same pattern already used for `instructions_file` today.

---

## 6. Decision E — getting and storing the API key securely

The project already has a working answer for exactly this problem, used today for the IRIDA
connector (`SPARMVET_IRIDA_TOKEN`): **secrets are environment variables, injected at launch,
never written into any config file, validated early with a clear error if missing.**
`libs/connector/src/connector/irida.py` is the reference implementation — it reads
`os.environ.get("SPARMVET_IRIDA_TOKEN")` and raises a structured `DeploymentError` (ADR-078:
what broke, where, why, how to fix, who's responsible) if it's absent, rather than failing
deep inside a request. `ClaudeApiAdapter` should do exactly the same thing for
`ANTHROPIC_API_KEY`, which is also already the documented convention in
`rules_app_features_flags.md` line 240 (adapter init fails, falls back to `DisabledAdapter`,
if the var is unset) — so this is also not a new pattern, just finishing a path already paved.
This single mechanism — plain env var — is also the only one that works identically on Eve's
own machine *and* every deployment target (Galaxy/Posit Connect/IRIDA containers, which have
no desktop session to hold a wallet secret anyway), which matters since ADR-071's deployment
rule already requires "credentials via environment variables or KDE Wallet only" and env var is
the one of those two that's portable.

**For Eve's own machine specifically**, a plain env var exported from a shell profile is
already compliant with that rule and needs nothing new. If she'd rather not have the raw key
sitting in a dotfile in plaintext, the optional upgrade is KDE Wallet (Fedora 43 KDE, already
in `toolbox.md`) via the `keyring` package's KWallet backend — but the right place for that is
a tiny **launch-time wrapper** (a shell function or a few lines in whatever script starts the
app) that does `export ANTHROPIC_API_KEY=$(python -c 'import keyring; print(keyring.get_password("sparmvet", "anthropic_api_key"))')`
and then starts the app normally. The app code itself never needs to know KWallet exists — it
only ever reads `os.environ["ANTHROPIC_API_KEY"]`, exactly as it does for `SPARMVET_IRIDA_TOKEN`
today. That keeps `libs/blueprint_arch/` free of a new runtime dependency (Two-Category Law) and
keeps the one `api_key_env` contract identical across every deployment shape — KWallet is purely
a convenience for how the env var gets set on Eve's desktop, not a second code path.

**Recommendation:** env var now (zero new code beyond what `ClaudeApiAdapter` needs anyway);
KDE Wallet as an optional five-minute convenience script for Eve's own machine whenever she
wants it, never as something the app itself depends on.

---

## 7. The kill switch Eve asked for — already built, confirmed

"This functionality can be deactivated, nobody can use it, and not using it should not break
Blueprint" is not a new requirement to design — it's already true today, and worth confirming
explicitly rather than assuming:

- `blueprint_agent_enabled` is a Group D flag with a **fatal** cascade on `blueprint_enabled`
  (ADR-077) — a template that gets this wrong refuses to start with a clear error, it never
  silently half-works.
- `make_adapter()` defaults to `DisabledAdapter` on any failure — missing flag, missing
  binary, missing key, unimplemented backend — and `DisabledAdapter` returns sentinel values
  for every call, so nothing downstream needs a special case for "agent is off."
- The sidebar panel (`blueprint_agent_chat`) simply isn't mounted when the flag is off or the
  adapter is disabled — confirmed in ADR-076's own "Consequences": *"No app-wide refactor
  required — the agent is purely additive. Existing BLUEPRINT IDE behaviour is unchanged when
  the flag is off."*

**The one thing to carry forward**, not change: the new role-capability file from §5 must keep
this same discipline — no role file present, or a role file that fails to parse, degrades to
`DisabledAdapter` exactly like a missing API key does today. Nothing added here should weaken
the existing fail-closed default.

---

## 8. What this means for `adr076_mvp.md`'s own promotion criteria

`adr076_mvp.md` §"Promotion criteria — MVP-1 → MVP-2" asks for "at least one full session of
real usage by the maintainer" on the read-only MVP-1 before MVP-2 (diff/apply + API backend)
starts. Worth checking honestly: has that happened? If not, the cheapest sequencing is:

1. Run MVP-1 as it stands (CLI backend, read-only) for one real data analysis recipe session —
   costs nothing, uses the existing CLI login, and tells you whether the conversational tempo
   and the 3-tool surface are actually useful before investing further.
2. If that feels worth continuing, build, in roughly this order:
   a. `ClaudeApiAdapter` (§2, Option A1) + `ANTHROPIC_API_KEY` read the same way
      `SPARMVET_IRIDA_TOKEN` is read today (§6).
   b. The `recipe_builder` agent-role file (§5) and wire `agent_tools.call_tool()` to check
      `allowed_tools` before dispatch — cheap, and everything after this depends on it existing.
   c. `propose_data_analysis_recipe_diff`, scoped to the session-bound recipe only (§3a), plus
      the existing Apply-gate UI pattern.
   d. CLI hardening flags as defence in depth (§3b, B2/B3) — not the guarantee, just cheap
      insurance for Eve's own local sessions.
   e. The instructions split (§4, C2).

(a) and (b) have no dependency on each other and can happen in parallel. (c) depends on (b)
existing (the scope check needs somewhere to read `write_scope` from) and is the step that turns
"a chatbot that reads the registry" into "an agent that can actually help build a data analysis
recipe" — the one with the most payoff per unit of effort once (a)+(b) are in place.

---

## Sources consulted (external, this session)

- [Claude Agent SDK vs Direct API: When to Reach for Each](https://blogsite-seven-weld.vercel.app/blog/claude-agent-sdk-vs-direct-api-when-to-use)
- [what is claude agent sdk vs claude api](https://mindstudio.ai/blog/what-is-claude-agent-sdk-vs-claude-api)
- [Claude Agent SDK: Build Agents on Claude Code's Harness](https://www.morphllm.com/claude-agent-sdk)
- [permission-mode dontAsk denies write/edit regardless of allowedTools permissions (issue)](https://claudeissues.com/issue/74567-permission-mode-dontask-denies-write-edit-regardless-of-allowedtools-permissions)
- [PreToolUse hooks and --allowedTools not enforced in headless -p mode (issue)](https://claudeissues.com/issue/33343-pretooluse-hooks-and-allowedtools-not-enforced-in-headless-p-mode)
- [Configure disallowedTools in Claude (2026)](https://claude-skills-guide-3lc.pages.dev/claude-code-disallowedtools-security-configuration/)
- [Claude Code docs — headless mode](https://docs.claude.com/en/docs/claude-code/headless)
- [Claude Code in CI/CD and Headless Automation](https://hidekazu-konishi.com/entry/claude_code_cicd_and_headless_automation.html)
- [BUG: Cannot authenticate Claude Code on headless remote server (VPS)](https://claudeissues.com/issue/65506-bug-cannot-authenticate-claude-code-on-headless-remote-server-vps)
