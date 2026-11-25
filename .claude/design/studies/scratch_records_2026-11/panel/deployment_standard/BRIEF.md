# Panel brief: the STRUCTURE of a written deployment standard (coordinator, 2026-11-21)

You recommend; the owner decides. A study: build nothing, change nothing. Read-only in the repository; scratch only under `tmpAI/panel/deployment_standard/<viewpoint>_scratch/`. Never read `tmp.md`. No word limit: as long as needed to be clear and complete, no padding. Plain short sentences; tables for comparisons.

## The owner's order (ledger D-0413, DECIDED), her words
"And I think we will need to write a deployment standard as we are doing for recipes if its not done so we can track of the options for deployment"

The same day she decided (D-0412): app features files and deployment files get a list of allowed keys, as the recipe has; an unknown or old key is refused at start with a plain line naming the key and, when known, the new name. And (D-0399, for the Gallery terms): one source file holds words and meanings; the documentation is generated from it.

What is asked NOW is only the first step: a draft of the STRUCTURE of the document, shown to her as a table. No key list is built before she has seen it.

## Read first
1. `tmpAI/panel/deployment_standard/FACTS.md`: the survey (every key of every deployment and app features file, its readers, what the user sees, where it is documented, how it is checked; environment variables; what documents a deployment today and where texts disagree; how the recipe standard is built; the use cases; the ledger lines). If that file does not exist yet, the same text is at `/home/evezeyl/.claude/projects/-home-evezeyl-Documents-Insync-gdrive-OBSWORK-20-GITS-SPARMVET-VIZ/3ce2c163-5fd7-4610-89a8-e0284a54d740/tool-results/toolu_01XtWJ1SFqyi95fAKHbJV6UA.txt`.
2. The model: `.claude/design/recipe_format_spec.md` (its sections; how one key is described) and `libs/utils/src/utils/recipe_spec.yaml` (its top-level structure).
3. `tmpAI/panel/deployment_io/ORDER.md` (her use cases, her words) and `tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md` (the 13 choices on where recipes and data are read and written, plus fonts; NOT decided: the standard must hold them as OPTIONS and must not decide them).
4. `tmpAI/coordinator/customized_deployments/FACTS.md` (the two customized deployments, readers, tests).
5. Ledger lines, read each before relying on it (`.claude/knowledge/decision_ledger.md`): D-0406 to D-0413 (names: display keys carry `ui_`; the deployment banner keys; `deployment_name` and the app features `ui_title` removed; allowed-key lists), and those FACTS.md section F names.
A small read-only check is allowed where your proposal depends on a fact (give file:line). Do not redo the survey.

## Her standing rules
- An option is judged on merit: correct, sound, useful to the user. "It reconsiders a decision" is INFORMATION in its own column, never a reason to reject an option or to rank it lower.
- Verify, never guess: label each statement RUN, READ (file:line) or REASONED.
- The tool informs; the user chooses. No half fixes and no shims. One way to do each thing. Keep it simple.
- Her vocabulary: "deployment", "app features", "data analysis recipe" (recipe), "user space" (HOME, BLUEPRINT, Gallery, Test Lab); never "persona", "manifest", "profile".
- A deployer may not be a developer.

## The question
Propose the STRUCTURE of the deployment standard, not its content:
1. One document with two parts (deployment, app features) or two documents? Say why. What about the sidebar files (`config/ui/sidebars/`), the palettes file, the environment variables, the theme stylesheet: inside, a part of their own, or outside with a pointer?
2. The pair "written text + machine-readable key list", as the recipe has (`recipe_format_spec.md` + `recipe_spec.yaml`): which file holds what; where each file lives given the library boundaries (the bootloader is in `app/`, the connector in `libs/connector/`, the recipe spec in `libs/utils/`); what is generated from the list (the template file, the README, the documentation page, the flag matrix, the refusal texts) and what stays hand-written.
3. The section list of the written document, in order, each with one line on what it holds and who reads it (a deployer, an author of recipes, a developer).
4. The fields recorded for EVERY key (the columns of the key table). The owner named: meaning, purpose (the kind of name where it is a name), allowed values, default, who sets it, which code reads it, which screen shows it, the options per deployment use case. Add or remove with a reason (for example: required or optional; checked how and refused with which text; since which version; the decision number; what an environment variable overrides; secret or not; relative path base).
5. How the deployment USE CASES appear (local, container, GitHub install, later PyPI, Galaxy/IRIDA, Posit Connect, an automatic pipeline): a matrix use case against key? a worked example file per use case? both? How an OPEN choice (the 13 choices of the deployment study) is shown in the standard so that it is visibly "not decided" and is not mistaken for a rule.
6. How the standard is kept true: the check at start (D-0412), a test that every shipped file passes, a test that every key the code reads is in the list and every key in the list is read (the survey found keys read by nothing and keys set by nothing), the audit of old words, versions of the deployment format (does a deployment file carry a format number?).
7. The order of work after she has seen the structure, in small steps that each leave a working app, and what must wait for the 13 open choices.
Give two or three variants where a real choice exists, and recommend one, on merit.

## Each viewpoint's own weight
- Architect: one source of truth; the library boundaries; what is generated; the check; versions; which ADRs and rules each variant amends (as information).
- Developer: effort and risk as facts for ordering (her rule: build time is no argument against an option); the steps; what a script can do; the tests.
- Deployer who is not a developer (the user viewpoint): can I find, in this document, what I must write for MY case, without reading the rest? Which words do I not understand? What must the standard tell me at the moment I choose between two options? What do I see when my file is refused?

## What to return
A 6-line summary. The proposed table of contents. The table of fields per key. The variants with your recommendation. "To decide first (ranked)". "Not verified". If you have a shell, save your text as `tmpAI/panel/deployment_standard/<viewpoint>.md` with a redirect and return the path plus the summary and "To decide first"; if you cannot write, return the full text.
