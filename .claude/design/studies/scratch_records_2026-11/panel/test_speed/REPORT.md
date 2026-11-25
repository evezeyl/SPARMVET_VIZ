# Speed of the tests: PARTIAL report (the study was stopped at 13:20 by the clock on 2026-11-18, usage limit)

Written down by the coordinator from the builder's last message (the builder could not save the file itself). Nothing is committed. Branch `task/test-speed` is clean at `69795f05`. The local copy worktree is removed. The builder's own run was stopped.

## Eve's two questions, what is known so far

1. "Is it limited by my read write?": not shown. The synced folder is on the same disk as the home folder (not a network disk). No process of the sync tool was running at 13:12, so no cost of syncing could be measured. The comparison "inside the synced folder against a local copy" is NOT done.
2. "Can the tests be made faster?": probably yes with parallel runs (`pytest-xdist` 3.8.0 is installed), but NO parallel run has been timed yet.

## Measured (under load from other sessions)

- Earlier full runs: headless 31 to 36 minutes (10435 to 10499 tests); browser about 25 minutes for about 140 tests.
- Slowest browser tests in those logs: `test_shiny_seed_places.py` (150, 115, 93, 50 seconds), `test_export_download.py` (108, 61, 35, 30 seconds), `test_shiny_session_restore.py` (36 seconds).
- The builder's own serial headless run: started 13:12 at load 5.2 (18.8 at 13:16), stopped at 13:19 at 68% after 7 minutes 50. A GUESS from that, not a measurement: the whole headless suite may take 12 to 13 minutes at that load, so the 31 to 36 minutes of the earlier runs were probably taken while much else was running.
- The machine: 12 cores, 30 GB memory, about 11 GB free at the time.

## Found by reading the tests (not run)

- 168 test files in `app/tests`, 135 in `libs`. 30 use a browser: 8 share one app per file through the common fixture, 13 start their own app. Ports are free or random, none is fixed.
- Fixed waits: 35 `wait_for_timeout` calls (46 seconds if each runs once) and 14 `time.sleep` (18 seconds).
- What stands in the way of parallel runs:
  - the default deployment writes sessions and stored tables to `tmp/UI_TEST/` inside the checkout: two apps at once would share them; each needs its own data folder;
  - `app/tests/gate_stage.py` writes a staged recipe into the shipped recipes folder and `assets/test_data/` (used by two browser test files): must stay one at a time;
  - `test_ui_app_features_masking.py:18` sets an environment variable directly;
  - browser tests write to fixed `tmpAI/browser_*` folders;
  - the app's bootloader is one shared object: not checked.

## Not measured yet

Time per folder; the 40 slowest headless tests; the synced folder against a local copy; parallel runs with 4, 6 and 8 workers and with the "one file per worker" setting; two browser files at once; how many runs the machine carries; the rule "which tests per change".

## Next commands (one run at a time, `uptime` before each, on a quiet machine)

1. Serial with timings: `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q --durations=0`
2. The same with `-n 4`, `-n 6`, `-n 8`, and `-n 8 --dist loadfile`; compare passed, skipped, expected failures and failures with the serial run.
3. A local copy: `git worktree add --detach /home/evezeyl/work/SPARMVET_VIZ_speed_copy dev`; run `libs/utils/tests` and `app/tests/test_export_provenance.py` twice each, alternating, there and in the worktree; remove the copy.
4. `-n 2` on three browser files, each with its own data folder.

Files on disk from the stopped run: `serial.log` (partial), `serial.meta`, `headless_args.txt` in this folder.
