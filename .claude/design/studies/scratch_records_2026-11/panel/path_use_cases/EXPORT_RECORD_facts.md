# Does the export record which data file was really read? (scout, read only, 2026-11-18; saved by the coordinator)

Every line was READ in the code of `dev`; nothing was run.

1. The real path of each data file: PARTLY. Written in `README.txt` ("Data source paths", `export_handlers.py:2026-2028, 2077-2079`) and in `effective_run.yaml` (`data_source_paths`, `export_handlers.py:1529`). Not in `report.qmd`, not in the picture metadata (`export_handlers.py:351-362, 386-397`). The path is the one the engine located (`orchestrator.get_source_files` -> `locate_dataset_file`, `orchestrator.py:72-89, 411-422`), not the recipe's text.
2. A hash per file: NO. Only the combined `data_batch_hash` is written (`export_handlers.py:199, 1518`). The per-file hashes are computed inside it (`session_manager.py:209-223`) and stored only in the session's `assembly.json` (`session_manager.py:294`), which is not copied into the bundle (not searched exhaustively).
3. The origin (recipe default, upload, deposit by id, imported bundle), the upload time, the uploaded file name: NO. Nothing found in `app/` outside tests.
4. When the recipe's path is ignored (deposit by id, imported bundle): the README and `effective_run.yaml` show the file really located. The recipe copy in the reproducibility bundle may still hold the unused `source.path` (`export_handlers.py:1422-1429`; `build_mode2_recipe` NOT read).
5. A dataset with no located file is left OUT of the hash (`orchestrator.py:420-421`), not marked missing.
6. Open risk, reasoned, not run: the upload writes to the recipe's `source.path` whenever it is set (`data_import_handlers.py:325-328`) with no look at the lookup mode; in the by-id mode the engine ignores that path. Whether the upload can be reached in that mode was not checked.
7. Tests: the engine side is tested (`test_dataset_lookup_one.py:90-192`, `test_bundle_importer.py:260-269`, `test_cache_chain.py:210`). NOT tested: that the path in the README equals the file read in the by-id and import modes; the upload target against the lookup mode.

Not checked: `build_mode2_recipe`; the full upload block (`data_import_handlers.py:142-300`); the full text of `test_export_provenance.py`.
