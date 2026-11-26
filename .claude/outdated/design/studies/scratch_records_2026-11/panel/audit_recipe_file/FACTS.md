# The audit recipe as a file: facts for the panel (scout survey of dev, READ only, 2026-11-20; digest by the coordinator)

## Two open questions (Q-A13 points 2 and 4; NOT decided)
**Point 2, what the audit recipe says about its original.** Her words: "I do not think audit should store the original hash (at least not from the user point of view) but its necessary for the app to know which recipe - then yes it can store the hash but it needs to be clear that: Audit recipe is a fork of original_recipe with hash - eventually add a key for the recipes to allow a special key that can make the link between audit and original recipes - Coordinator can ask architect to check and if necessary data scientist agent."
**Point 4, the form of the reason of an audit step.** She said the reason goes "in the comments", told apart from the author's comments: "we can have comment: AUDIT - and then the comment to allow differentiation between comments in the text for example ... or you add different types of comments - coordinator can have architect agent find out what would be best".
Her standing rule: study, not effort.

## DECIDED (ledger, taken by the owner)
- D-0102, D-0143, D-0040: two recipes, the original_recipe (never edited in the audit; the reference) and the audit_recipe (a copy that carries the audit steps; the source of truth of the audit; the export). The copy minus its audit steps must equal the original, else block. An event log beside it.
- D-0146: audit steps are added at the end of each T1, T2 or T3 list.
- D-0148: "The audit export exports the audit recipe with the steps of the audit added to the recipe; the reason can be added as a # comment."
- D-0026: the reason is free text, required, hashtag convention.
- D-0083, D-0189, D-0315: who (initials) and when live in a log beside the copy; the log is always written in the session, optional in the export; removed steps are not kept in the exported steps.
- D-0319: the audit recipe lives in an `audit/` folder (the base folder is not fixed). D-0320: the audit copy KEEPS the author's comments; no exception to "every writer keeps comments" (also D-0174 for Blueprint). D-0321: the number at the end of a step id counts the order of creation.
- D-0322 (her words "A : for now yes only filter and drops"): the check of an audit recipe refuses any audit step that is not a filter, a drop or a removal by key.
- D-0317: a session saved against a different recipe is refused on restore.
- D-0007 / ADR-092: the id of a recipe equals its file name.
- D-0187, D-0188, D-0192: if the audit was used, the export uses the audit recipe and the data, hashed.
## CONFIRM (design text, no ledger line)
- Header of the copy: "the original's file-set hash and the recipe format version" (`.claude/design/home_stage2_mechanism_spec.md:122`, an agent's proposal).
- Place: `user_data/audit/<session_key>/` (`home_audit_steps.md:246-247`) or `_sessions/<session key>/audit/<recipe id>.yaml` (the mechanism page, an agent's proposal).
- When the original is edited after an audit started: a notice, the export refused, the user chooses "re-base" (design pages; not built).
## OPEN
- Whether the export also holds the original recipe file. The two questions above.

## How recipes are read and written today
- The library is PyYAML. It drops every `#` comment on load; no parsed recipe holds them. `ruamel.yaml` (a library that keeps comments on a round trip) is NOT installed; installing it needs the owner's yes (task BP-COMMENTS-1, not started). No agent installs anything.
- Writers that KEEP comments do it by editing the TEXT of the file: the migration tools (`libs/utils/src/utils/recipe_migration.py`, `strict_form_migration.py`, `engine_keys_migration.py`: positions from `yaml.compose`, then text edits) and Blueprint's branch write (text insertion, `data_analysis_recipe_navigator.py:884-918`). Tests check that comments survive there.
- Writers that DROP comments today (they dump parsed data): Blueprint's component save and info save (`blueprint_handlers.py:1184`, `:2617`), the group and plot save, the export's reproducibility recipe (`export_handlers.py:1497-1500`: ONE resolved file, includes merged, no comments), the bundle import. This contradicts D-0174 and D-0320 and is a known open task.
- A recipe is a main file plus included fragment files (`!include`). "The resolved recipe" is one dict with the includes merged; the loader does not keep which file an element came from (the Blueprint navigator finds it again by re-reading the text).
- The audit copy today (`libs/utils/src/utils/audit_copy.py`, in memory only) is a copy of the RESOLVED dict. Its header, name, folder and the author's comments are "not decided and not built".

## An audit step today
- A step dict = the operation (action and its arguments) + `id` + `comment`. The id has the form `audit_<8 hex>_<k>`; a step is recognised as an audit step by its id, never by its comment. The reason is stored in the `comment` KEY (`audit_copy.py:207-208`).
- The checker: `comment` is a legal key on EVERY step of every recipe (it is also the AUTHOR's note on an ordinary step: "why, not what"); it must be text. `id` is legal only in the checker's "audit" profile and must have the audit form. Any other key on a step is refused, so who and when cannot be step keys without a format change.
- Keys of the stored tables: an audit step enters the key as its operation only, without id and comment ("without reasons, dates or initials"). A `#` comment never enters any key. (A finding beside the question: the `comment` key of an ORDINARY step does enter the table key today, against the format spec line 916; a task.)

## What identifies a recipe today
- The id = the file name (checked). No other identity exists: no uuid, parent, origin or fork key; an unknown top-level key is refused; a new key is a format change (a new format version). An earlier private key `_t3_origin` was removed because the format refuses unknown keys. `info:` allows label, description, subtitle, contact, version (the AUTHOR's version), comment; in practice the checker does not refuse other keys under `info:` (against the spec; Blueprint writes `info.name`, `author`, `tags`).
- Two hashes exist: (1) the FILE-SET hash (`data_analysis_recipe_sha256`: the bytes of the main file and of every included file; ANY byte counts, also a comment, a space, a moved line); it makes the session key and the export's "did the recipe change" check. (2) the keys of the stored tables: they follow what the recipe DOES (the resolved content), not the bytes; a comment edit changes no table key.
- So today a comment-only edit of the original changes the file-set hash: the session warns "saved against a different data analysis recipe version", the export refuses "changed since this view was opened", yet no table changes.
- Where a user sees a hash today: the export's `effective_run.yaml`, the refusal file, picture metadata, the session card (the short session key). The export README and report show the recipe's id, name and path, not its hash.
- The audit run already refuses to run when the copy minus its audit steps differs from the original as re-read from disk (`audit_run.py:298-301`).

## Facts that bear on the options
Point 2 (the link to the original):
- A `#` header line is read by people only; the app cannot rely on it (the loader drops it).
- A key INSIDE the recipe needs a format decision (which key, where, allowed only in an audit recipe or in every recipe) and makes "the copy minus its audit steps equals the original" need a named exception for that key.
- The link can also live OUTSIDE the recipe: in the log file beside the copy, in the session record, in the export's run file.
- "Which original": the id alone (the file name) does not say which CONTENT; the file-set hash says the exact bytes but breaks on a comment edit; a hash of the resolved content says what the recipe does and survives comment edits; a stable key written once in every recipe (her "special key") would survive a rename and an edit but then says nothing about whether the original changed.
- The audit recipe file, if named after the recipe, has the same id as its original (id = file name) in another folder.
Point 4 (the reason):
- A `# ...` line can only be written and read at text level; the app reading the copy gets no `#` line. If the reason lived only there, the app would not know it after a reload (the log would have to be the source).
- The `comment` key is read by the app, legal today, already separate from the author's `#` comments, and told apart from an author's `comment` key by the step's audit id. A marker inside it ("AUDIT: ...") is possible.
- Keeping the author's comments (D-0320) means the copy cannot be a dump of the resolved dict. Ways that exist: (a) copy the recipe's FILES as they are (main and fragments, byte for byte) into the audit folder and insert each audit step by a text edit at the end of the right list (the technique the migration tools and Blueprint's branch write already use); (b) a comment-keeping library (not installed; needs her yes); (c) one merged file written at text level (the fragments' comments would have to be carried into it; no code does this today).
