# Panel brief: one purpose and one rule for names and labels across the whole app (coordinator, 2026-11-21)

You recommend; the owner decides. A study: build nothing, change nothing. Read-only in the repository; scratch only under `tmpAI/panel/names_whole_app/<viewpoint>_scratch/`. Never read `tmp.md`. No word limit: as long as needed to be clear and complete, no padding. Plain short sentences; tables for comparisons.

## Read first, in this order
1. `tmpAI/panel/names_whole_app/ORDER.md`: the owner's words and the order of work.
2. `tmpAI/panel/names_whole_app/FACTS.md`: the survey of every name, label, title and description of the app outside the recipe (deployment and app features files, the fixed texts of the screens, actions and plot components, column names, the export, sessions, the documentation), with five analyses: the kinds of name and which field plays each role; two fields doing one job and one key doing two jobs; the same thing under several words; fields written and never read; the questions a scheme must answer. If that file does not exist yet, the same text is at `/home/evezeyl/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/3ce2c163-5fd7-4610-89a8-e0284a54d740/tool-results/toolu_01WPV6KNAKgVVSeURGierjko.txt`.
3. `tmpAI/panel/name_fields/TABLE_FOR_THE_OWNER.md`: the name fields of a recipe (with corrections 8 to 11 in its section 3).
4. The decisions on names: read each ledger line in `.claude/knowledge/decision_ledger.md` before you rely on it (D-0253, D-0237, D-0360, D-0387, D-0397, D-0405, and those FACTS.md names). The vocabulary rules that exist: `CLAUDE.md` section 1; `.claude/rules/rules_documentation_aesthetics.md` (the Violet Law); `assets/scripts/audit_old_words.py`.
A small read-only check is allowed where your proposal depends on a fact (give file:line). Do not redo the survey.

## The owner's words
On the Gallery names: "the ui_label is aimed to be short - The info.label its the header block and then a title can be abit more long that the short ui_label. But we need to encourage authors to make them coherent ... again we have a purpose of each component problem". Then: "we need the coordinator use agents to comme with suggestions to better homogeneize this across the app - using different agents".

## Her standing rules
- An option is judged on merit: correct, sound, useful to the user. "It reconsiders a decision" is INFORMATION in its own column, never a reason to reject an option or to rank it lower. If your best scheme changes a decided name (for example `ui_label`), propose it and name the decision.
- Verify, never guess: label each statement RUN, READ (file:line) or REASONED.
- The tool informs; the user chooses. No half fixes and no shims: an old key is refused with the new name, not accepted beside it. One way to do each thing.
- Her vocabulary: a "user space" (HOME, BLUEPRINT, Gallery, Test Lab) is not a "code module"; "data analysis recipe" (recipe), "app features", "deployment"; never "persona", "manifest", "profile".

## The question
Propose ONE homogeneous scheme for names across the app: every thing that has a name (a recipe, a group, a plot, a table, a column, an action, a plot component, a panel, a user space, an app features set, a deployment, a Gallery example, a session) gets the SAME kinds of name, each kind with one purpose, one key name and one rule, wherever it is written. Work from the kinds of FACTS.md analysis A: the identity (never shown, unique); the short name (a tab, a list, a button); the longer title (a heading, a banner, a report); the description (one sentence that says what it is for); the meaning or help text (shown on demand); the display name of a column; the text inside a figure.

Answer at least:
1. For each kind: its purpose in one plain sentence; ONE key name everywhere (or say why a file kind needs its own); who writes it; required or optional; a rule for its length and characters, if any, with a number and whether a breach is an error or an advice; what is shown when it is missing (one fallback rule for the whole app).
2. Which things have which kinds (a matrix: thing against kind). Not every thing needs all kinds.
3. The cases FACTS.md and the recipe table found: `info.label` against `info.name` in BLUEPRINT; `ui_label`, `label` and `name` for the short name; `ui_title` of a recipe against `ui_title` of the app features; a group's `ui_title` read by nothing; `description` used as a tab text; the Gallery heading against the example name; the nav item "Blueprint Architect" against the internal value "Wrangle Studio"; dataset, table, schema, collection, join; plot, figure, graph, chart; step, action, node. For each: what the scheme does.
4. The words on screen and in the documentation: ONE word per thing, the list of words it replaces, and where a second word must stay (for example a word of plotnine or Polars).
5. Two or three variants of the scheme where real choices exist (for example: prefix every user-facing key with `ui_`; or plain `label` / `title` / `description` everywhere; or keep today's keys and only fix the collisions), each with what it changes: the recipe format and its version, the checker, the code, the shipped recipes and the 34 Gallery examples, the app features and deployment files, the documentation, the tests. Say for each how the change is made in one pass with the old key refused, as the owner's rules ask.
6. How the scheme is kept true later: one place where the kinds and keys are written (the spec), a check, an audit script, a rule file.
Recommend ONE variant and say why, on merit.

## Each viewpoint's own weight
- Architect: one source of truth for the kinds and keys; the recipe spec (`libs/utils/src/utils/recipe_spec.yaml`), the app features and deployment loaders, the registries of actions and components; how a rename is done without a shim; which ADRs and rules each variant amends (as information); testability.
- Data scientist: what an author of recipes needs to write a good name, title and description; what a reader of a report or a methods section needs to find (which name appears in the export and can be cited); column names against display names and the risk that a display name hides which column was used; reproducibility when a name changes.
- User new to data science: which words on screen I understand; where the same thing has two words and I think they are two things; what a short name, a title and a description must tell me at the moment I choose; where I look for the meaning of a word.
- Developer: effort and risk as facts for ordering (her rule: build time is no argument against an option, delay is fine); the order of small steps that each leave a working app; the size of each variant (count the files and keys from FACTS.md); what can be done by a script; the tests.

## What to return
Start with a 6-line summary. Then the matrix (thing against kind) with the key of your scheme in each cell. Then the table | case | today | in the scheme | what it changes | reconsiders a decision? (number, information only) |. Then the variants and your recommendation. End with "To decide first (ranked)" and "Not verified". If you have a shell, save your text as `tmpAI/panel/names_whole_app/<viewpoint>.md` with a redirect and return the path plus the summary, the matrix and "To decide first"; if you cannot write, return the full text.
