# The audit recipe as a file: options, pros and cons (Q-A13 points 2 and 4, and how the file is written)

For the owner. Written by the coordinator, 2026-11-20, from a survey of the code and one round of two viewpoints (architect with the developer's view, data scientist). Facts: `FACTS.md` in this folder. Nothing is built. The panel recommends; she decides.

## Flag first: what can lose something or change a result without telling
1. **A `#` line can vanish.** The library that reads recipes drops every `#` comment, and three writers of the app drop them today (Blueprint's save, the export's recipe, the bundle import). A reason or a link kept ONLY in a `#` line can be lost silently, and the app cannot read it back.
2. **A shared fragment.** If the audit recipe is written by editing the text of copied files, and one included file is used by two tables, a step written into it lands in BOTH tables, and today's safety check ("the copy minus its audit steps equals the original") would not notice. (READ by the architect.) It needs its own refusal or its own test.
3. **A new key at the top of the recipe rebuilds every table.** Tried on the demo recipe: a new top-level key changed 5 of 5 table keys; the same key under `info:` changed 0 of 5. (RAN by the architect.) So the link to the original must not be a top-level key.
4. **Two meanings of "the recipe changed".** The hash used for sessions today counts every byte: editing only a comment in the original makes the app say "changed" although no table changes. A fingerprint of what the recipe DOES ignores comment edits; then a changed comment is not reported at all. Both are true statements about different things; the user should read which one.
5. **The audit file keeps the original's name.** The id of a recipe is its file name (decided). The audit recipe, in its `audit/` folder, has the same file name and the same id as its original.

## 1. What the audit recipe says about its original (her point 2)

| | Option | For | Against | What the user reads |
|---|---|---|---|---|
| a | A `#` header line only ("fork of X") | Readable by a person. | The app cannot rely on it; lost by three writers (flag 1). | The line, if it survived. |
| b | **A key inside the audit recipe, under `info:`**, allowed only in an audit recipe: the original's name and a fingerprint of what the original does | Travels with the file, also alone in a bundle on another machine. The app reads it. No table is rebuilt (flag 3). | A decision on the recipe format (a new key). The check "copy minus audit steps = original" needs this one named exception. If the original is renamed, the name in the key is old: the app says "original not found". | "This audit recipe is a copy of X." |
| c | The link kept outside the recipe (the log beside the copy, the session) | No change of the recipe format. | The log is optional in the export (decided): a bundle without it loses its original. Two places can disagree. | Depends on the log being there. |
| d | Her "special key": a lasting identity written in every recipe, to which the fork points | Survives a rename of the original. | Says nothing about whether the original changed. Touches every recipe and the format. A hand copy of a recipe duplicates the identity. A top-level key would rebuild every table (flag 3); it would also sit beside her decision that the id is the file name. | "A copy of the recipe with identity ..." |
| e | **b plus the record:** the key in the audit recipe (name and fingerprint) AND the log or run file holding the same, with the byte-exact hash for checking | The recipe describes itself; the record allows an exact check. | Two places; the key in the recipe is the one the app trusts. | See below. |

Which fingerprint: both viewpoints say the fingerprint of **what the recipe does** (the merged content), not of its bytes, in the recipe; the byte-exact hash only in the record file, as a check.
What the user reads in place of a hash (the scientist's sentence): "This audit recipe is a copy of 'X' as it was when the audit started. Since then X has not changed / has changed in what it does / has changed only in comments." Hashes only in the record file, never on screen.
- Both viewpoints: **e** (the architect counts it as b with the record; same thing).

## 2. The form of the reason of an audit step (her point 4)

| | Option | For | Against |
|---|---|---|---|
| a | **The step's `comment` key, as built.** The step is known as an audit step by its id (`audit_...`). | The app reads it back after a reload. It survives every writer. It moves with the step. It stays in the bundle even when the log is left out. It is exactly her free text. Accepted by the check today. | Opening the file, there is no word "AUDIT" next to the reason: one must know that the id marks the step. |
| b | The `comment` key with a marker: `comment: "AUDIT: <reason>"` (her first idea) | Marks itself to a reader. | A second sign for "is an audit step" beside the id; the app must cut the marker off to show the reason; a hand edit of the marker shows a wrong reason; the log holds the reason without the marker, so the two differ. |
| c | A `# AUDIT: <reason>` line above the step, and nothing else | Looks like a comment, as her decision D-0148 allows. | The app cannot read it back; lost by three writers (flag 1). |
| d | **a plus a `# AUDIT` line** written above the step for the human reader; the `comment` key is the source | The app reads the key; a person sees the marker. | Two copies of the reason: a hand edit of one leaves the other stale; the `#` line is lost wherever comments are lost today. |
| e | A new step key `reason` | Clean. | A change of the recipe format with no gain over `comment`. |

- Architect: **a** (the id is the marker; d as a visible extra if she wants it). Scientist: **d** first, then a; with the `comment` key as the source in both.
- The tension with her earlier decision ("the reason can be added as a # comment"): the `comment` key is the form of it that the app can read; whether the `#` line is added too is her choice (a or d).
- Without the log in a bundle, the reason is still there (in the step); who and when are not. The export should say so in one line.

## 3. How the file is written so that the author's comments are kept (follows from her "Comments kept")

| | Way | For | Against |
|---|---|---|---|
| a | **Copy the recipe's files as they are** (the main file and every included file, at the same relative places) into the audit folder, and write each audit step by a text edit at the end of the right list | Comments kept byte for byte. No new library. The technique exists in the migration tools. | There is no "add a step at the end of a list" code yet; it must handle a list written on one line, a missing tier, and above all a file shared by two tables (flag 2). Guard proposed by the architect: after every write, read the files again and require that they give exactly the copy the app holds in memory; a shape that cannot be written safely is refused with its reason, never written another way. The export bundle then holds the files, not one merged file as today. |
| b | A library that keeps comments on a read and write (`ruamel.yaml`) | One way of writing for everything; it would also repair Blueprint's save and the export, which drop comments today against her decision. | A new library: needs her yes (nobody installs anything without it); it may re-layout parts of a file. |
| c | One merged file written by hand | One file. | No code carries the comments of the included files into it. |

- Architect: a, with the refusals; or b if she says yes to the library.
- What stays as built in slice A: the copy in memory remains the model (add a step, remove a step, the equality check); the file is its written form, tied to it by the re-read check.

## Recommendation of the coordinator
1. **The link: e.** A key under `info:` of the audit recipe only, with the original's name and the fingerprint of what it does; the same, plus the byte-exact hash, in the record beside it. The user reads the sentence, never a hash. It is her "fork of original_recipe", with the hash kept where the app needs it. Her "special key in every recipe" (d) is not needed for this and costs a format change in every recipe; I would keep it for the day recipes are renamed often.
2. **The reason: a, and d if she wants to see the word AUDIT in the file.** The `comment` key is the source in both. I would not put the marker inside the text (b).
3. **Writing: a now** (copy the files, write by text edit, refuse what cannot be written safely, re-read after every write), and her yes or no on the library (b) as a separate question, because it would also settle Blueprint's save.

## Points that are hers
1. The link: a, b, c, d or e; and whether a comment-only change of the original is shown as "changed only in comments" (the sentence above) or not at all.
2. The key name and place under `info:` (a format decision): for example `info: audit_of: {recipe: <name>, content: <fingerprint>}`. The name is hers.
3. The reason: a, b, c, d or e.
4. Writing: a or b (the library needs her yes).
5. A step for a table whose steps live in a file shared with another table: refuse with a plain line (my suggestion), or copy that file apart for the audited table.
6. The base of the `audit/` folder: inside the session's folder (`_sessions/<session>/audit/`, one place for everything of a session; my suggestion), or beside the stored tables (`user_data/audit/<session>/`).
