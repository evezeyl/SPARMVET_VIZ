# Control of slice C piece 1 (4 fix commits after f3efe931) and task/line-endings 0d4d7154

Files in this folder: headless.out, time_hash.out, pins.py/pins.out, keys.out/keys_head.json/keys_dev.json, le_*.out, scratch_repo/, mut/ (scratch copy for mutations).
Method: pytest with PYTHONPATH = worktree + its libs/*/src (pp.sh of slice_c1_final), cwd worktree; mutations only in `mut/` (git archive HEAD).

## PART 1: FIT TO MERGE
`git diff --stat f3efe931..HEAD`: only app/modules/cache_keys.py (+ 3 test files + a comment line in recipe_spec.yaml). No file under app/handlers, app/src; no other app/modules file. Browser suite not rerun (justified).

### fc9bccd0 (verdict follows content) cache_keys.py:395-405: at the cause, no weakened guard, no shim.
- Hash: `canonical_hash(raw_config)` and `canonical_hash(original_raw)` (both). `LoadedDataAnalysisRecipe.raw` is `config.raw_config` (cache_keys.py:374), the same dict the builds read, and `original_raw` is the original's own `raw` by reference, so a change of either is seen. Ran: changing the ORIGINAL after a verdict is judged again (scratch test, passes; fails when the original half is removed from the hash).
- Calls: once per read_source / _materialize_tier1 / materialize_tier2 / materialize_tier3 (orchestrator.py:203,293,444,537); the walk `audit_step_places(loaded.raw)` already runs on each call, so the hash is the same order of cost. Time (loaded system, load 6-12): demo_abromics 5.3 kB JSON: two hashes 0.32 ms (integrity_errors 1.04 ms); 1_Abromics 8.2 kB: 0.53 ms (1.77 ms). Cheap.
- Escape: only content that is not JSON-visible (`default=str` turns an object to its text). `table_parts`/`coarse_parts` of the LoadedDataAnalysisRecipe are computed once at construction (cache_keys.py:415) and are not refreshed if raw is changed by hand afterwards: the keys could be stale for a hand-changed copy. Not new, no live path (audit_run builds new copies), but the "judged again" claim covers the guard only, not the keys. LOW, note.
- Mutations: verdict cached by object again (`"problems" not in verdict`) -> `test_the_verdict_on_an_audit_copy_follows_its_content_not_the_object` FAILS (DID NOT RAISE, test_read_source.py:393). Original dropped from the hash -> NO test in the repo fails (55 passed): the "original" half is not pinned by the shipped test (my scratch test did catch it). LOW: add a case that changes the original.

### 59bc7311 (join keys pinned): 
- The pinned set is read in the test by `_keys_read_independently` (own walk, join actions only, on/left_on/right_on/by; does not call recipe_join_keys). I also walked the whole resolved tree of all shipped recipes (pins.py): 0 differences with the 9 pinned entries; grep of the join steps of 1_test_data_ST22_dummy and 2_test_data_ST22_dummy agrees (on sample_id; left_on VF_gene / right_on Gene_name; the `by:` of non-join steps is NOT counted, and the test would catch it).
- Mutations: join-action filter dropped -> 2 pinned cases fail (Source etc. appear); right keys forgotten -> 3 fail; tier2 dropped -> nothing fails (no shipped recipe has a join in tier2: not covered). The test keeps the tautology (finding 3 of the earlier control) gone.
- Stale docstring: join_keys.py:298-303 says "a test holds the two equal ... the walk is written once more", but session_manager.extract_primary_keys now returns the shared rule (session_manager.py:125-133). Comment only, LOW.

### 9f232977 (alias, venv guard): 
- `_calls_in` maps an `as` name back to the imported name. Mutations: alias map removed -> the new self-test fails; in the real engine_record.py `from ... import author_steps as step_list` -> the per-file count test FAILS (`{'step_list': (0, 2)}`). Not seen: `x = author_steps` (assignment alias) and `module.alias` attribute use. LOW.
- Guard `test_browser_tests_no_venv_path.py`: 2 passed; `SKIP_PARTS = frozenset("tests build .venv ...".split())` is a workaround of the regex, with its reason in the comment; acceptable (it is a folder name).
### f8e7d830: comment AU04 only (recipe_spec.yaml:60). Fine.

### Run counts (headless, one run, -n 4, same ignores as the earlier control (30 browser files), load 6-12 at start): 12681 passed, 14 skipped, 31 xfailed, 0 failed in 612 s. Earlier: 1 failed, 12668 passed: +13 passed = the repaired test + 12 new cases. (headless.out)
### Keys: 54 recipes, 334 keys, head vs dev 0ed7f88e (fresh git archive): identical (keys.out); also identical to the earlier dev 3bfb0050 dump.
### Merge: `git merge-tree --write-tree 0ed7f88e task/slice-c-audit-form` rc 0, no conflict (merge-base 3bfb0050; dev has docs-only commits since).

## PART 2: task/line-endings 0d4d7154 : FIT TO MERGE
- Scans `git ls-files` (all tracked, suffixes of .gitattributes: tsv csv yaml yml json; my own count: 691 files). Blob read with `git cat-file --batch ":path"` (the INDEX, not HEAD: equal on a clean tree; "committed" in the message is exact only when nothing is staged: LOW) and the working copy, reported apart with two different messages.
- Pinned list `INSIDE_VALUE_CR` holds the 2 files with (CR, CRLF) = (20, 10) in blob and working copy; fails when a file is gone from tracking, gains or loses a CR. I checked independently: only these 2 tracked files have CR, in blob and working copy (le_blobs.out, le_cr_files.out). Mutation (extra CRLF in a pinned file, scratch repo): `AssertionError: libs/transformer/tests/data/fg_metadata.tsv: (CR, CRLF) counts in the commit are (21, 11), pinned (20, 10)`.
- Failure text for a committed CRLF under libs/ (scratch repo, le_fail.out): `the COMMITTED blob holds CR (commit it with LF, D-0349): ['libs/x/committed_crlf.tsv']; only the WORKING COPY holds CR (the commit is right; repair with `git checkout -- <file>`): ['assets/y/copy_only.tsv']`.
- Test file: 4 passed in the worktree.
- In the MAIN checkout after the merge: the blob of assets/test_data/STRESS/STRESS_data.tsv has no CR, the working copy has 10001 lines with CR (as you said). Scan of the main working copy: STRESS_data.tsv plus the 2 pinned files. Expected: `test_no_tracked_data_file_holds_crlf` FAILS naming only STRESS_data.tsv with "repair with `git checkout -- <file>`"; the pinned test passes. I did not touch that file. After the merge `.gitattributes` (-text) will also make git status show it.
- Note (LOW): the blob read is by name with `:path`, a file name with a newline would break the parse; none exist.

## Findings by weight (none blocks)
1. LOW: no test fails if the original is dropped from the hash (cache_keys.py:398-399).
2. LOW: table_parts/coarse_parts not refreshed on a hand-changed copy (cache_keys.py:415).
3. LOW: join_keys.py:298-303 docstring stale; tier2 join keys not covered by a shipped recipe; alias via assignment not seen.
4. LOW: `:path` reads the index, message says "committed".

## NOT covered
Browser suite (no screen code changed); golden/pictures (cache_keys.py only changes the guard cache, keys identical); the timing is under load, not idle; D-0297/D-0332/D-0349 text compared only through behaviour (key drop refusal tests were not rerun by hand, they are in the suite and passed); a Windows checkout of the line-endings test.
