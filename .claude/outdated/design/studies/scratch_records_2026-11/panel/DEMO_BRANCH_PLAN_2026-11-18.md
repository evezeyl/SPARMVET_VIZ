# A demo branch: the plan (asked in the review session's message of 11:33), and the estimate for the big recipe change

Coordinator, 2026-11-18. A plan for Eve's yes. Nothing is cut yet. No dates.

## 1. What it is

A second copy of the app in its own folder, frozen at a commit that Eve has tested. She presents from it. The work goes on in `dev` without touching it.
In git words: a branch `demo` and a worktree (a second working folder of the same repository) at `/home/evezeyl/work/SPARMVET_VIZ_demo`, outside the synced folder so that the sync tool does not touch it while she presents. (A folder inside `.claude/worktrees/` would also work; the place is her choice.)

## 2. How it is cut

1. Eve says "HOME and GALLERY are settled" and names the commit, or says "today's `dev`".
2. Before the cut, on that commit: the full controls pass (automatic tests, browser tests, every app features starts, tables identical, gallery pictures identical), and a reviewer runs HER demo path in a browser with screenshots.
3. The coordinator runs: `git branch demo <commit>` then `git worktree add /home/evezeyl/work/SPARMVET_VIZ_demo demo`.
4. A tag marks the cut: `demo-cut-1` (an annotated tag: a name for that exact commit).
5. Its own deployment file with its OWN data and session folders, so that nothing she did while testing in the main folder shows up in the demo, and the reverse. A builder writes it as `config/deployment/demo/demo_presentation.yaml` (copy of the local one; `user_data` and the session folder point inside the demo folder; clean at the cut). This file is the only thing added on the demo branch.

## 3. How Eve starts it

From the demo folder (one line, written into a small text file `START_DEMO.txt` at the cut, with the real app features she chooses):

```
cd /home/evezeyl/work/SPARMVET_VIZ_demo
PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" SPARMVET_DEPLOYMENT=config/deployment/demo/demo_presentation.yaml SPARMVET_APP_FEATURES=<the app features she presents> /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.venv/bin/shiny run app/src/main.py --port 8010
```

Why the long first part: the libraries are installed from the MAIN folder. Without that line the demo folder would run its own screens with the main folder's libraries, which change every day. The line makes the demo folder use its own libraries (the section "Working in a git worktree" of `docs/appendix/python_environment.qmd`). A reviewer proves it at the cut: the app prints where each library was loaded from.
Port 8010, so that it never collides with the app she runs from the main folder on 8000.
One Python environment is shared (the main `.venv`). If a package is upgraded there between the cut and the presentation, the demo changes. So: no package upgrade in that time, or the demo gets its own environment (her choice; default: no upgrade).

## 4. How a fix is copied into it

Only a fix she asks for. The fix is first built, reviewed and merged in `dev` as usual. Then the coordinator copies that one commit: `git cherry-pick -x <commit>` inside the demo folder (the `-x` writes into the message which commit it came from). After each copy: the browser tests of the area touched, and her demo path again. A new tag: `demo-cut-2`, and so on.
If a fix cannot be copied cleanly (because `dev` has moved, for example after the big recipe change), a builder makes the same small fix on the demo branch by hand, and a reviewer compares the two.

## 5. What must not change in it

- No merge of `dev` into `demo`. Only single copied commits.
- No recipe rewritten, no data file replaced, no change of the deployment file after the cut.
- Nothing from the big recipe change, unless she chose "demo after the big change" (then the cut is made after it).
- No direct work in the demo folder by any agent except the copy of a fix she asked for.
- The demo branch is never merged back. After the presentation it is kept as a tag and its folder is removed.

## 6. How it is checked before the presentation

The day before, and again one hour before:
1. `git status` in the demo folder is clean and the commit is the last tag.
2. The app starts with the line of section 3; it prints its libraries from the demo folder.
3. A reviewer runs her demo path in a browser (the steps she gave), with screenshots, on the demo folder.
4. Her session folder is clean (or holds exactly what she prepared).
5. The recipes she shows open with no rejected recipe in the list.

## 7. What Eve gives

- Her demo path in a few lines (which recipes, what she clicks).
- The app features she presents with (`developer`, `standalone`, ...).
- The place of the demo folder, if not the one above.
- Her choice: demo before or after the big recipe change.

## 8. The estimate for the big recipe change, from the times measured today

Times are the working time of the agents, taken from today's runs on this machine while other test runs were going on. They are not calendar time, and a step that comes back from review with a finding runs again.

| Step | What | State | Measured or expected |
|---|---|---|---|
| 0 | Picture comparison and the reference pictures | done | 6 minutes |
| 1 | Format rules and their tests (the checker knows the new shape) | done | 60 minutes |
| 2 | The rewrite tool | done | 52 minutes together with step 3 (measured) |
| 3 | The rewrite of every recipe, fragment, plot file and bundle | done | (with step 2) |
| 4 | Every reader and writer: HOME, Export, Blueprint, Gallery, Test Lab writers, scripts (about 20 files) | not started | the largest step: expected 2 to 4 hours of building, in two or three workers one after the other |
| 5 | The engine field in both libraries and the engine checks | not started | expected 1 to 2 hours |
| 6 | Cache keys | not started | expected under 1 hour |
| 7 | The export record (engine, versions, theme per plot) | not started | expected under 1 hour |
| 8 | Format text, rules, docs | not started | expected 1 to 2 hours |
| 9 | Final checks by the builder; then the review of the whole diff; then the full controls | not started | review 1 to 1.5 hours; one full control run takes about 1.5 hours on this machine when it is busy (measured today: automatic tests 35 minutes, browser tests 25 minutes, plus the rest) |

Sum of what remains: about 9 to 15 hours of agent work if nothing comes back, and experience of this week says that one or two steps do come back. Only one worker can work on that branch at a time, so the steps cannot be done side by side.
What can lengthen it: the pictures not staying identical after step 4 (each difference must be explained); Blueprint's writers (they must write the new shape or Blueprint makes recipes the checker refuses); her answers on the three `label` places (a one-line change and a re-run once she answers); the rename of the plot components if she wants it in the same merge (it needs her ten answers and would add about a third).
What does not depend on it: the HOME fixes of today (switching recipes, the Export button, the export warnings) are built on `dev` and can be tested by her while the big change continues on its branch.

So, as evidence for her choice "demo before or after": HOME and GALLERY can be settled on today's shape within the small fixes listed; the big change is at step 2 of 9 and its largest step has not started.
