# Can recipes be versioned? Facts for the panel (scout survey of dev `48cc102e`, READ only, 2026-11-20; digest by the coordinator)

## Her words (2026-11-20, relayed in channel block M405)
"1. ahhh - Well then maybe the original recipe should be reconstructed but the problem is if it needs a new specification --- so I would refuse - I would explain that the original recipe has been modified and that it needs to reanalyze and add the audit steps where they are done - A question - could we track version of the recipes ? that could be a solution then if a recipe is versionned the latest version is proposed but that would allow to reopen a recipe from the old version ... Please have coordinator see if and how this is possible"
DECIDED from the same block (ledger D-0362): a session saved before the author edited the original recipe (same name, other content) is refused with a plain line; reconstructing the old recipe is not decided. Not built: today the app warns and opens (`app/handlers/session_handlers.py:557-564`).

## Decided lines that bear on it (read each in `.claude/knowledge/decision_ledger.md`)
D-0362; D-0317 (a session of another recipe id is refused); D-0186 ("Changing data is not necessary a failure but changing a recipe is."); D-0208 ("The version information stays the git commit during development; a release comes later."); D-0207 (an export whose recipe uses old component names is refused at import, "the app converts nothing": use the updated recipe and reproduce the audit filters, or use the old app version named in the export); D-0328 and D-0339 (an audit recipe carries `info.audit_of: {original_recipe, original_content}`; the user reads a sentence: the original has not changed / changed in what it does / changed only in comments; the fingerprint's computation is not decided); D-0331 (a hand-edited audit recipe is tampering, refused by a hash; not built); D-0333 (an audit record beside the audit recipe with the byte-exact hash; not built); D-0340 (the audit folder inside the session folder; not built); D-0324 (the export of an audit contains the recipe of the audit); D-0354 (an audit recipe is format 1); D-0184 (a recipe is checked when selected, not all at start: the code still checks all at start).

## Identity today
- The file name is the id (ADR-092; `app/modules/data_analysis_recipe_validator.py:436-442` refuses `id:` different from the file stem). One folder is scanned, not its subfolders (`app/src/bootloader.py:414-415`, `glob("*.yaml")`, at start only; a new or removed file needs a restart, `:405-413`). So two files with the same id cannot coexist; two versions side by side need two names or another mechanism.
- `spec_version: 1` is the FORMAT, not the recipe (`libs/utils/src/utils/recipe_check.py:246-256`). The format spec says (`.claude/design/recipe_format_spec.md:266`): the key "is not `info.version`, which stays the author's own version of the recipe's content".
- `info.version` exists in 14 of 16 shipped recipes, free text ('1.0', '1.8', '1.2'); it is shown in the Info panel and written by the Blueprint info form (`app/handlers/blueprint_handlers.py:2545, 2577, 2604`); NO logic reads it. Blueprint-created recipes also get `created` (today's date) and `version` "1.0.0" (`libs/blueprint_arch/src/blueprint_arch/new_recipe.py:16,31,32`). Gallery examples have `submission_date`. The `info:` block is free-form: the checker requires only `label`.

## Content hashes today
- R = `data_analysis_recipe_sha256`: a hash of the raw bytes of the main file and of every `!include` fragment really read (`app/modules/cache_keys.py:327-338, 494, 501`); comments and layout count. Fragments in the mirror folder that nothing includes are not in R.
- A resolved-content hash exists too (`canonical_hash` of the resolved recipe: sorted-key JSON, comments excluded, `cache_keys.py:107-109, 408-417`), today PROVISIONAL as the identity of an audit copy.
- `session_key` = R[:12] + ":" + data hash[:12]. A changed recipe gives a new session folder; the old folders stay on disk.
- Where R is recorded: session files (`assembly.json`, `t3_<time>.json`), the export (`effective_run.yaml`, `report.qmd`, PNG and SVG metadata). The export README has the table keys, not R.

## What already keeps old recipe content
- Session folder: NO recipe text (only hashes and steps).
- Export bundle (reproducibility mode): ONE recipe file written from the resolved recipe (`app/handlers/export_handlers.py:1496-1502`): fragments merged, comments gone. Publication mode: no recipe.
- Bundle import: writes the bundle's recipe into the recipe folder as `<id>_imported_<time>.yaml` with a new id (`app/modules/bundle_importer.py:219-233, 256-276`); it shows in HOME after a restart.
- Blueprint download: a dated zip of the main file and its fragment folder, made by the user, not stored by the app.
- Git: the shipped recipes are tracked in this repository. Nothing says a deployment's recipe folder is under git. D-0208: the app version is the git commit during development.
- The app keeps no backup, snapshot or history of recipe files.
- The audit copy lives in memory only today; the audit folder and record are decided, not built.

## Who writes a recipe file
- Blueprint saves overwrite the file in place (`blueprint_handlers.py:1154-1195, 2588-2625, 1510-1517`); a new recipe refuses an existing name (`:2685-2693`).
- The upload of a YAML overwrites a same-named file silently (`app/handlers/ingestion_handlers.py:44-51`).
- Hand editing and the operator's deployment: no restriction, no check at open.
- An open recipe reloads when its files change (`cache_keys.py:483-506`).

## What refuses or warns on a changed recipe today
- Session restore: another id refused; same id with another R: a warning, then it continues (to become a refusal, D-0362).
- Export: refused when R or the data changed since the view was opened (`export_handlers.py:228-247, 997-1005`).
- Another FORMAT number: refused by the checker and the gate.

## Not found
No `recipe_version` key; no ADR or design note on versions or history of recipes; no stored history of recipe files; no recipe text in a session; no audit record, audit folder or audit-recipe hash check built.
