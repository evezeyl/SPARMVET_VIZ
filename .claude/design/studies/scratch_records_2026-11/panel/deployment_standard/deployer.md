# Deployment standard, structure: the viewpoint of a deployer who is not a developer (panel-user, 2026-11-21; filed by the coordinator from its report, slightly shortened)

READ = read in the file named. REASONED = its inference. Nothing was run. Its statements about the code come from the survey (`FACTS.md`), not from its own reading of the code. It read: the brief, FACTS.md, `config/deployment/README.md`, the template, `demo-vetinst.yaml`, `config/app_features/pipeline-static.yaml`.

## Summary
1. Today a deployer cannot write a correct file from the documents: the template, the README and the code disagree on facts that decide whether the app starts.
2. Wanted: one entry point "I want to deploy for case X" with a worked example file and the list of keys that case must set.
3. One document with two parts (deployment, app features): the two files are written together and each refers to the other.
4. Every key needs: a plain meaning, the allowed values, what happens when it is left out, what is seen when it is wrong. Code readers and decision numbers go to an appendix.
5. Open choices must look different from rules: a box "NOT DECIDED" with the options side by side; never a default shown as advice.
6. A refused file gives one plain line per problem: the file, the key, what is wrong, what is allowed, the new name when the key was renamed. No traceback.

## Where today's documents would mislead a deployer (READ, against the survey)
| Document | It says | The survey says | What goes wrong |
|---|---|---|---|
| template :36-37 | without `default_app_features` the selector is shown "or defaults to pipeline-static" | the app stops (`bootloader.py:164-178`) | the key is left out; the app does not start |
| template :23 | `deployment_name` is shown in the footer | no screen shows it; removed by D-0411 | time lost |
| template :96-97, `demo-vetinst.yaml:28-29` | `runtime.python_interpreter` | read by nothing | a key that does nothing is copied |
| template :65-67 | `cache` is written by the orchestrator | nothing reads `locations.cache`; data is written under `user_data` | disk space and rights planned for the wrong folder |
| template :36 | five app features names | eight files exist | three are unknown to the reader |
| template :89-93 | IRIDA keys | IRIDA does not start; two keys have no reader | a dead block is copied |
| README :47 | paths are relative to `project_root`, else "CWD" | `branding.theme_css` is relative to the working folder, not to `project_root` | two path rules, one stated; "CWD" is not understood |
| README :36 | "five required location keys" | three must exist on disk, two are only checked for presence | unknown which folder to create first |
| `pipeline-static.yaml:8-9, 29-30` | comments on a "Wrangle Studio" and an audit report export, no flag behind them | - | a flag seems missing |
| `pipeline-static.yaml:38` | the recipe is fixed by `default_data_analysis_recipe` in the deployment | selector hidden and no recipe named: the app stops | the link between the two files must be written in both |

## One document or two
One document, two numbered parts, a short "start here" page in front. Reason: the two files together make one deployment.
- Sidebar files: a short part of their own, pointed to from the app features part; the list of panels in an appendix. The standard must say whether a deployer may write an own sidebar file.
- Palettes file: a part of its own; its first line says "you cannot choose another palette file" (the path is fixed in the code).
- Environment variables: one table on the "start here" page, and "this variable overrides this key" beside each key.
- Theme stylesheet: inside the deployment part, at `branding.theme_css`: "applied after the default stylesheet; holds only the differences".

## Table of contents wanted
| # | Section | Reader |
|---|---|---|
| 0 | Start here: what the two files are, how the app finds them (the four places, in order), the minimum to write | everyone |
| 1 | Choose my case: the use cases, one line each, a link to a worked example and to the keys that case must set | deployer |
| 2 | Minimal files that start | deployer |
| 3 | Deployment file: the keys, grouped by what I want to do (identity, folders, default start, branding, limits, connector, other) | deployer |
| 4 | App features file: the keys, grouped as in the file | deployer |
| 5 | Rules between keys: the combinations that stop the app, one sentence each and what I see | deployer |
| 6 | Environment variables: what each overrides, secret or not, who sets it | deployer, IT |
| 7 | When my file is refused: the refusal lines, how to read one, the old-key to new-key table | deployer |
| 8 | Open choices: boxed, with options | the deciding deployer, the owner |
| 9 | Appendix: code readers, tests, decision numbers, history, the sidebar panel list, format version | developers, authors |

## Fields per key
Needed in the main table: key (full path); meaning in one plain sentence; required or optional; allowed values; if absent, what happens (as a consequence, not a default alone); what I see when it is wrong (the refusal line, or "nothing, no check"); which screen shows it, or "no screen"; who sets it (me, the pipeline, the container image, an environment variable); what an environment variable overrides; the path base (relative to what); must exist on disk, must be writable; secret or not; options per use case; status (in use, being removed, new name).
Not needed in the main table (appendix or the machine-readable list only): which code reads it; the decision number; since which version (only for renamed keys); the test.
"Purpose (the kind of name)": only for keys that hold a name; say which kind (file name, name shown on screen, id) and whether the user sees it.
A key that does nothing today is removed from the standard, or marked plainly "no effect today".

## Use cases and open choices
- Both a matrix (use case against key, generated from the key list: "did I forget a key?") and a worked example per case (what I copy). Each example starts with "Use this if ..." and "What the user of this deployment can and cannot do".
- The survey shows most use cases have NO shipped example file. The standard says "no worked example yet", not a gap.
- An open choice: a box headed "NOT DECIDED. The standard does not choose for you."; the question in one sentence; the options side by side; for each what it means in practice, what must be prepared, what cannot be undone; "until this is decided, do this"; no default in bold and no default value for it in an example file. Every key that depends on an open choice carries "depends on open choice N" beside it.

## At the moment of a choice
Side by side: what the user of my app sees, what is no longer possible, what I must prepare on disk, what is checked at start and what is not. Example: "If you hide the recipe selector, the app opens one data analysis recipe and the user cannot change it. You must then name it in the deployment file. If you do not, the app stops at start and shows: ...". And for an unchecked key: "This key is not checked at start. A typo here is accepted without a message and the default is used." (true today for `deployment_type`, per the survey).

## When my file is refused
Shape: "Deployment file /path/file.yaml, key `branding.banner.title`: this key was renamed. Use `branding.banner.ui_label`." / "..., key `deploymet_type`: unknown key. Allowed keys here: ... (closest: deployment_type)."
Wanted: all problems at once; the full path of the file and which of the four places found it; the key with its full path; what is allowed; the new name, or "removed" with the reason; a section number of the standard; the same text as in the standard (one source); no stack trace, no developer word.
Today (survey): an unknown top-level key is not checked; a typo in `app_features_override` is accepted; an unknown sidebar panel only prints a warning that may never be seen in a container. The standard lists these as "not refused today" until D-0412 is built.

## Words not understood
CWD (say "the folder you start the app from"); project_root; location (say "folder", named by its use); Tier 1/2/3 cache, T3, anchors; Parquet; gate / load gate (say "the check a recipe must pass before it opens"); resolution level (say "where the app looks for your deployment file"); connector, adapter, filesystem / galaxy / irida; ghost save; cascade, validator, WARN / FATAL (say "the app stops" / "the app starts and shows a warning", and where the warning appears); `!include` (say "this line pulls in another file"); flag (fine if defined once); HOME, BLUEPRINT, Test Lab, Gallery (one line each the first time); "provisional" (say "the numbers may change"). The rule that an app features name has no underscore must be stated at the key, with the reason.

## Before I start writing the two files
Where each file goes (a numbered list: "if you are a ..., use place N"); how I check my file before starting the app (a command that only checks and prints the refusal lines: none was found; "this matters more than anything else for a non-developer"); a table of the default values.

## Variants
A. One document ordered by goal, generated reference tables inside. Recommended.
B. Two documents in key order with a short joint guide: simple to maintain, but the pair rule stays in the reader's head.
C. One alphabetical reference table plus a guide: good for a developer; "what must I write for my case" cannot be found.

## To decide first (ranked by this viewpoint)
1. A "check my file" command for a deployer, without a running app.
2. Keys that do nothing today: removed from the shipped files and the template before the standard is written, or listed as "no effect".
3. The facts that decide a start, corrected before the standard copies them (`default_app_features` absent stops the app).
4. One path rule for all path keys.
5. Which keys are checked and which are not, stated until D-0412 is built.
6. Which use cases get a worked example in the first version.
7. Whether a deployer may write an own sidebar file and an own palettes file.
8. A format number inside the deployment file.

## Not verified
Nothing run. Not read by it: the recipe standard, ORDER.md, the deployment study's table, the ledger, the docs pages. Whether a "check only" command exists. The survey's claims on `locations.cache`, IRIDA and `python_interpreter`.
