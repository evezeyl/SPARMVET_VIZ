---
trigger: always_on
deps:
  provides: [rule:verify_protocol, rule:tmpAI_tmp_segregation, rule:debug_script_mandate]
  documents: [libs/transformer/tests/debug_assembler.py, libs/viz_factory/tests/debug_gallery.py, tmpAI/, tmp/]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# Verification & Testing Protocols (rules_verification_testing.md)

**Authority:** Governs the testing patterns, naming standardization, and the @verify operational gate.

## 1. Standardized Test Naming & Architecture

To ensure automated test suites are logically homogenous, all libraries MUST strictly adopt the following naming schema in their `tests/` directories:

- **Component Debuggers (The Engines):** `libs/{lib}/tests/debug_{component}.py`
  - *Purpose:* Specialized runners for isolated logic (e.g., `debug_wrangler.py` for Layer 1 decorators).
- **Global Library Wrapper (The Orchestrator):** `libs/{lib}/tests/{lib}_integrity_suite.py`
  - *Purpose:* A high-level runner that programmatically discovers actions and dispatches them to the appropriate 'Engine' for verification.
  - *Command:* The Orchestrator MUST use the Engines to perform the actual execution; it does not contain the testing logic itself.

## 2. CLI Mandate (argparse Authority)

Every executable Python script within `./libs/` test folders and `./assets/scripts/` MUST be controllable via the command line interface.

- **Rule:** Scripts must use the `argparse` standard library.
- **Rule:** Scripts must provide an explicit docstring mapped to the `--help` argument, describing exactly what the script accomplishes.
- **Rule:** Hardcoding paths in the execution blocks is strictly FORBIDDEN. All paths (data, data analysis recipe, output) must receive CLI arguments (with optional transparent defaults).

## 3. The @verify Protocol & Phase-Gating (Evidence Loop)

No task is considered [DONE] without passing the @verify gate, which creates a standalone proof-of-concept limit for operations.
**Phase-Gating Mandate:** UI testing (`app/src/main.py`) is STRICTLY PROHIBITED until the corresponding Headless Audit has passed.

1. **The Contract:** For a new function `[name]`, pre-define its dataset (`name_test.tsv`) and data analysis recipe (`name_data_analysis_recipe.yaml`).
2. **CLI Execution:** Execute test logic via the standard `argparse` CLI runner depending on the operational engine.
3. **Evidence Generation & Path Standard:**
   - **For Automatic Library Testing (e.g. implementation of new decorator):** Results MUST be saved in `tmp/{lib}/`.
   - **For Data analysis recipe Testing:** Headless results MUST be strictly routed to `tmp/data_analysis_recipe_test/{data_analysis_recipe_basename}/`.
   - Resulting tables are saved as `USER_debug_view.tsv` (via `.collect()`) and Plots to `USER_debug_{plot}.png`.
4. **Console Glimpse (Proof of Life):** Output `df.glimpse()` to standard output, and present the plot PNG path.
5. **The Halt:** Agents MUST halt autonomous execution and declare: "Data/Plot ready in tmp/... Waiting for @verify."
6. **Transparency Mandate:** Every @verify result MUST list the exact file paths used for Data, Data Analysis Recipes, and Resulting Artifacts.

## 4. Active Visibility Protocol (Skeletal-Archive)

To prevent context-window saturation and maintain a clean active roadmap, the following protocol is mandatory:

- **100% DONE Gate**: Only 100% completed [x] items may be moved to archives. ANY task that is either in-progress [ ] or [DEFERRED] MUST remain in the main tasks.md under its original logical header to ensure immediate visibility.
- **Skeleton Retention**: The main `tasks.md` MUST retain the original Header but replace the completed checklist items with a skeletal pointer: `> Status: COMPLETED. Detailed history moved to: [Archive Path]`.
- **Naming Standard**: Archive files use the `tasks_archive_[unit_name].md` convention.

## 5. Conflict Guardrails (Sync-or-Stop)

- **@sync**: If the Agent detects a discrepancy between the user's intent (chat) and the physical codebase structure, it must halt and ask to `@sync`.
- Project Rules and Architecture Decisions (ADRs) unconditionally overrule generic conversational prompts. Modify them only through Double-Confirmation with the user.

## 6. Dual-Directory Output Segregation (Agent vs User)

Two distinct temporary directories exist at the project root. Their purposes are **strictly non-interchangeable**:

| Directory | Owner | Purpose | Consent required? |
| --- | --- | --- | --- |
| `./tmpAI/` | Agent | Agent-internal testing, scratch scripts, intermediate logs, debug runs that the agent initiates autonomously. | **No** — agent may read and write freely without halting for user approval. |
| `./tmp/` | User | Outputs the user must review: `@verify` evidence, `USER_debug_*.tsv/png` artifacts, Data analysis recipe test results. | **Yes** — agent must halt and declare paths per the `@verify` protocol before the user proceeds. |

**Rules:**

- Any test script, log, or artifact that is **agent-internal** (exploratory run, import check, intermediate debug, CI-style headless validation not yet ready for user review) MUST be written to `./tmpAI/`. Sub-directory structure mirrors `./tmp/`: `tmpAI/{lib}/` for library tests, `tmpAI/data_analysis_recipe_test/{data_analysis_recipe_basename}/` for data analysis recipe tests.
- `./tmp/` is **reserved exclusively for `@verify` outputs** — results the agent declares to the user as ready for inspection. Writing agent-internal scratch to `./tmp/` is a protocol violation.
- Both directories are persistent and git-ignored. Neither is scanned by the embedding engine.
- When promoting an agent-internal result to user-review status (i.e., the test passed headlessly and is ready for `@verify`), the agent MUST copy the artifact from `./tmpAI/` to `./tmp/` and then declare the `./tmp/` path per section 3.

## 7. Failure Test Mandate (ADR-034)

To ensure the Diagnostic Layer remains robust, every significant component (Ingestion, Transformer, VizFactory) MUST include at least one "Automated Failure Test" in its integrity suite.

- **Rule**: Developers must provide a "Malformed Data analysis recipe" that intentionally triggers a `SPARMVET_Error`.
- **Validation**: The test passes only if the system catches the specific error and returns the appropriate `tip` suggested in the diagnostic registry.

## 8. Shiny App Headless Testing (Playwright)

### When to use Playwright vs unit tests

| Concern | Use |
|---|---|
| Pure logic (filter operators, connectors, decorators) | pytest unit tests (`app/tests/test_filter_operators.py`, `libs/*/tests/`) |
| App startup, reactive rendering, UI navigation, widget interaction | Playwright smoke tests (`app/tests/test_shiny_smoke.py`) |

Playwright tests are slower (~35 s for the full smoke suite) and require a running app process. Reserve them for integration-level checks: does the app boot, does the filter form render after a column change, do dynamic tabs appear.

### Infrastructure

- **conftest.py**: `app/tests/conftest.py` uses `shiny.pytest.create_app_fixture(app_path, scope="module")` to start the app once per test module. Import this fixture in any new test file.
- **Playwright packages**: `playwright==1.59.0`, `pytest-playwright==0.7.2` installed in `.venv`. Chromium headless shell at `~/.cache/ms-playwright/`.
- **pyproject.toml** (root): test extras declared under `[project.optional-dependencies] test`.

### How to add new smoke tests

1. Import the module-scoped app fixture from conftest:
   ```python
   from .conftest import app  # re-export or use pytest plugin auto-discovery
   ```
2. Always call `_wait_shiny(page)` after any navigation or reactive trigger before asserting on rendered output. It waits for `document.documentElement.classList.contains('shiny-busy')` to clear.
3. Set app features via env var at test-collection time, NOT via a UI selector — no `#app_features_selector` element exists in the rendered app. Use `SPARMVET_APP_FEATURES=qa` (see below).
4. After changing `fb_col` (filter column selector), call `_wait_shiny(page)` before interacting with `fb_op` or `fb_value` — `filter_form_ui` re-renders reactively after every column change.

### App features requirement for deterministic tests

All Playwright smoke tests MUST run under `SPARMVET_APP_FEATURES=qa`.

- `qa` app features: all feature flags ON, `ghost_save` OFF — prevents session persistence side-effects between test runs.
- Tests that require Gallery (`developer` or `qa` only) are automatically skipped for other app features files; this is expected and tracked as 2 app features skipped in the baseline.

```bash
PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
```

### Common pitfalls

- **Emoji tab labels**: use `.nav-link:has-text('AMR')` style selectors, not role-based Playwright selectors. The tab text contains emoji (e.g., "💊 AMR and ☠️ Virulence") so partial text matching is more robust.
- **Dynamic tabs signal**: wait for `.nav-link:has-text('Quality Control')` as the sentinel that `dynamic_tabs` has fully rendered before navigating to a specific tab.
- **fb_op reset**: if `fb_op` shows the wrong operator after changing `fb_col`, it means `_wait_shiny()` was not called after the column change. Always wait before inspecting operator or value widgets.
- **No runtime app features selector**: `#app_features_selector` does not exist as a rendered UI element. Setting `SPARMVET_APP_FEATURES` at launch is the only mechanism.

### Test baseline (checked 2026-11-06)

There are no known broken tests or libs. Removed on 2026-11-06 because they were broken and superseded:
`app/tests/test_reactive_shell.py` (app features switching is gone, ADR-053; the Apply gate logic is covered by
`test_session_manager.py::test_gatekeeper_blocked`; a UI-level test is open as AUDIT-GATE-UI-1), the app features
benchmark scripts, and the `libs/test_lab/tests` demos that imported the old `test_lab.reconciler` and the
old `AquaSynthesizer` API (covered by `libs/id_reconciliation/tests`, `test_synthesizer.py`,
`test_bootstrapper.py` and the new `test_extractor.py`).

Headless baseline (fast, about 25 s for everything but the browser tests):

```bash
PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests \
  --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py \
  --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q
```

Browser tests (about 4 minutes; the first three run under the `qa` app features, `test_every_app_features_starts.py` launches each shipped app features by itself):

```bash
PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest \
  app/tests/test_shiny_smoke.py app/tests/test_shiny_smoke_blueprint.py app/tests/test_export_download.py \
  app/tests/test_every_app_features_starts.py -q
```

## 9. Edge Cases and Clean-up (added 2026-11-06, Eve)

Science must be correct: what the user sees and does is what the export contains.

- **Edge cases in every test set.** A test file is not complete with the normal path only. Add the
  cases around it: empty input, nothing to do, the thing removed (not only added), a corrupt or
  missing stored file, a change that touches only one stage, two items that must stay separate.
- **Tests must be able to fail.** Break the code once (disable the new behaviour) and see a test
  fail; restore it.
- **Do not leave things that should be gone.** When a change makes a stored artifact invalid (a cache
  file, a stored stage, a generated file), remove it at the moment the change is detected, not only
  when it is next read. A leftover that cannot be served today can be served by a later bug.
- **The export holds what the user validated.** The export is the Result plus the steps the user sent to audit (with a reason); exploration (filters tried in T1/T2/My view) is a sandbox and is never exported. Any new view of the data needs the same source in the export bundle, and the keys/hashes used must be recorded in it.

