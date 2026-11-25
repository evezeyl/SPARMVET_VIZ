# Blueprint opens a failing recipe: details (architect viewpoint)

Scratch scripts (run from project root with ./.venv/bin/python): probe.py (loaders and checker per failure kind), probe_handlers.py
(the REAL bodies of _do_refresh_blueprint and sync_blueprint_mapper cut out of blueprint_handlers.py by ast, ui stubbed),
probe_tolerant.py (map from the checker's tolerant read), probe_gate.py (HOME gate gap). Broken copies in stage/ and stage_gate/
(copies of 1_test_data_ST22_dummy.yaml; no shipped file touched).

## 1. Silent places (verified by running probe_handlers.py)
- sync_blueprint_mapper, blueprint_handlers.py:915-918 (`if cfg is None: print(...); return`): map and YAML view keep the previous recipe.
  Happens for YAML syntax error and missing include (the only two kinds ConfigManager refuses).
- _do_load_component TubeMap highlight, blueprint_handlers.py:721-729 (`except Exception as _e: print(...)`), followed by
  "Loaded ... step(s)" notification at 731: the component is new, the map is old, and the user is told it worked.
- THIRD: _do_refresh_blueprint, :272-345. (a) a missing include is only printed (:296). (b) build_sibling_map swallows a YAML error
  and returns {} (data_analysis_recipe_navigator.py:82-83), while the regex scan of the text still fills the component selector
  (:307-320; groups non-empty so the load check at :322 is never reached) and _update_dataset_pipelines then says
  "Blueprint: <name> (N component(s))" (n = len(inc_map) when ctx is empty, :961) as type=message: a success text for an unreadable recipe.
  Run result: yaml_syntax -> ctx 0, registry 0, includes 53, selector filled, map and YAML previous. (c) includes_map is set (:300)
  before ctx_map and schema_registry: the three stores are set one after the other, no transaction.
- Fourth (freeze, not stale): wrangle_studio.py:665-668 bare `_CM(path)` inside `except Exception`; ConfigManager raises SystemExit
  (checked: isinstance(SystemExit, Exception) is False) -> session freeze if the recipe was broken on disk after data loaded.
  The test test_blueprint_handlers_call_no_bare_configmanager (app/tests/test_upload_load_never_exits.py:112-117) scans only
  blueprint_handlers.py and only the name `ConfigManager`, so it would not catch this.
- Not silent but poor: Mode B (:755) and _do_refresh_blueprint inline branch (:322) notify; then _update_dataset_pipelines adds
  a second, success-typed notification and clears logic_stack.
- Same value re-selected in stored_data_analysis_recipe_selector does not fire the event (reasoned, not run) and there is no
  reload button (grep): after fixing the file outside the app the user must switch recipe and back.

## 2. What Blueprint shows today, per failure kind (verified, probe.py)
| failure | ConfigManager (what the map/forms use) | checker reader load_recipe | checker code | map possible |
| YAML syntax in the recipe file | refuses (SystemExit) | None | T01 | no: text only (problem has the line) |
| missing !include | refuses | full structure, include = {} | T02 + S06 | yes, 170 of 172 elements |
| unknown action | loads fine, no message | full | ST02 | yes |
| unknown parameter | loads fine, no message | full | ST03 | yes |
| wrong type | loads fine, no message | full | ST07 | yes |
| data file missing | loads fine, no message | full | none from check_recipe; only validate_data_analysis_recipe_data: "dataset cannot be loaded" | yes |
| join refused (right_ingredient not in the join) | loads fine, no message | full | J05 | yes |
Consequence: for 5 of 7 kinds Blueprint opens the recipe and draws everything and says nothing until the user presses Validate.
The stale view is only the 2 that ConfigManager refuses. A YAML error inside a fragment behaves like missing include (T01 on the include, {}).
ConfigManager also "repairs" (wrapper key removed, unquoted `on`, repeated key keeps last: recipe_loader.py docstring), so the
map and the YAML view show a version that differs from the file: a silent change.

## 3. Options
A. Notification + error panel, clear the view (map, YAML, selector, ctx/includes/registry, logic stack) in ONE function called from the
   three places. Effort ~0.5 d (assumed). Risk low. Solves stale. Does NOT show the failing points of the 5 kinds that load, and the
   user still cannot see the recipe: it fails Eve's "must open". In the meantime the user: edits outside the app, switches recipe and
   back, presses Validate (works on the file, probe.py).
B. Fix list from check_recipe_file(path,"build") + validate_data_analysis_recipe_data (Problem has code, path, message, fix), shown
   on open; map drawn from the checker's tolerant load_recipe raw (BlueprintMapper accepts it, probe_tolerant.py). Row click opens
   the fragment: needs one addition in load_recipe, a source file per included node (not there today: grep recipe_loader.py).
   Effort ~2 d (assumed). Risk medium: Blueprint then reads with a different reader than the engine (this is what DEC03 and
   recipe_loader.py describe as the strict one; ConfigManager stays for HOME). YAML syntax error stays text (T01 + file view).
   Meantime: edit text in the YAML view, press validate again (the same function, so the list refreshes).
C. B + broken nodes marked on the map: problem path starts with data_schemas.<id> / joins.<id> / analysis_groups.<g>.plots.<id>,
   so a prefix match gives the node. Needs a change in BlueprintMapper and the cytoscape styling. ~3-4 d (assumed). Risk medium-high
   (UI, not testable without a browser; the prefix-to-node function is testable). Meantime as B.
The fix-list rows are testable without a browser (build rows from a Result; run on the 7 broken copies).

## 4. HOME gate gap (verified, probe_gate.py)
- Gate runs only in Bootloader.__init__ (bootloader.py:182-186; grep: no other caller outside Blueprint's Validate). The recipes list
  is frozen (bootloader.py:360-373 documents it).
- server.py:97-98 active_cfg() -> load_data_analysis_recipe(path) (cache_keys.py:183-204): re-reads on file change, ConfigManager only,
  no checker. Run: gate passes the good copy; one edit of a fragment (what Blueprint's component save at
  blueprint_handlers.py:1149 writes with no check) to an unknown action -> HOME's reader accepts it, the cache refreshes;
  the gate, if run again, rejects it (ST02); the selector list still offers it.
- Other writers into the same folder with no check: :1478-1480 (branch), :2630 (info). New files (BP-NEW-1, bundle import) wait for a
  restart, so they are gated. Only in-place edits of a recipe that passed at start are the gap, valid until restart.
- What HOME does at run time with it (unknown action raises in transformer/registry.py:29; other kinds not run) not checked.
- Blueprint's selector path is hard-coded config/data_analysis_recipes/pipelines (blueprint_handlers.py:~935); HOME's is
  get_location("data_analysis_recipes"): same in shipped deployments, can differ.
- Remedy options (not decided): (1) run the gate when load_data_analysis_recipe misses its cache (same trigger as ADR-089; one place);
  (2) Blueprint calls bootloader re-check of that recipe after every write; (1) is one place, (2) is three call sites.
- Blueprint's Validate also runs scripts/audit_data_analysis_recipe_coherence.py (subprocess): a second checker next to check_recipe
  (DEC03 says one). Not examined further.
