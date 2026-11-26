# Can a recipe file be left out because of how its include is written? (facts, big recipe change branch `fa7f856b`)

Digest by the coordinator of a scout's read-only survey, 2026-11-18. Every line was READ at the place named; "reasoned" marks an inference. Nothing was run.

## The plain answer

- **The hash of the recipe, the session key, the export and the bundle import are SAFE.** They find the included files through the YAML loader (`libs/utils/src/utils/config_loader.py:67-91`, used by `app/modules/cache_keys.py:220-246`, `session_manager.py:239-245`, `bundle_importer.py:295-328`). An include written without quotes, with single quotes or with double quotes is read the same way. A change in a plot file changes the recipe hash.
- The export's reproducibility recipe is the resolved recipe written as one file (`export_handlers.py:1436-1448`): no include file can be left out of it.
- Blueprint's three scans that missed unquoted includes are repaired (this branch, commit `5892a872`).

## What is left (not repaired; for the task on the private include loader, D-0282)

1. **HOME's watch list of recipe files** (`app/src/bootloader.py:450-491`) still uses a text scan. It finds unquoted, single-quoted and double-quoted includes, also nested ones. It MISSES a path that holds a space (it keeps only the part before the space) and it cuts a path at a `#`. It also takes an `!include` that stands in a comment for a real file. Consequence: a file that is not on the watch list can change, or break, without HOME re-checking the recipe. Silent. No test covers it.
2. **A nested include** (an included file that includes another): the loader resolves its path from the MAIN recipe's folder (`config_loader.py:71`), the watch list from the including file's folder. The two can disagree (reasoned). Whether any shipped recipe nests includes was not determined.
3. **Blueprint's "download recipe" zip** takes the main file and the folder of the same name (`blueprint_handlers.py:1388-1413`): an include outside that folder is not in the zip. Silent.
4. **Blueprint's draft hash** covers the main file only (`blueprint_handlers.py:145-147`).

## How the includes are written today (branch)

Shipped recipes: 31 unquoted (in 4 files; among them the 17 plot files of the demo recipe), 70 single-quoted, 0 double-quoted. The gallery examples hold no include. Writers: the recipe factory and "+ Plot" write unquoted; Blueprint's branch writer writes single-quoted; the rewrite tool keeps the author's form.

## Tests

No test gives the HOME watch list an unquoted include, a path with a space, or a nested include.
