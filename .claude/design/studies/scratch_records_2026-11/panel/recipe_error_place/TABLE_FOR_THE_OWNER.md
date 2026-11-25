# Saying WHERE a recipe fails: the file and the line (a study; nothing built)

For the owner. Written by the coordinator, 2026-11-20, from a read of the code on dev by a scout (READ only, nothing run). She decides.

Her words: "can we find out where the recipe fails eg line number? that would be good for a person trying to write recipes to see the point where it fails?"

## What a message says today (READ)
| Kind of problem | What the message names today | File of an included fragment | Line |
|---|---|---|---|
| The file is not valid YAML, or a key is written twice | The file; for a fragment, its name | yes | **yes** (the only two cases; a repeated key says both lines) |
| Every other problem of the recipe check (a step that is not a registered action, a join key not declared, a wrong value, about 60 check codes) | The recipe file and a path of keys, for example `joins.figshare_triple_join.tier1.steps[1]` | no (always the main file's name, even when the step sits in an included file) | no |
| A fragment that cannot be found or read | The main file and the fragment's name | yes | no (not the line of the `!include` in the main file) |
| An error while a table is built (a join) | The recipe, the join, the step number, the action | no | no |
| An error while a table's steps run | Only the engine's text reaches the user; the table and the step number are printed to the console, not put in the message | no | no |
| An error in a plot's tier 3 step | The plot, "tier 3", the step number, the action | no | no |

So the app already knows the PATH of almost every problem (which table, which tier, which step). What is missing is turning that path into a file and a line, and, for two engine errors, carrying the path to the message at all.

## What exists in the code that can give a file and a line (READ)
- The reader of the recipe check sees the line of every key while it reads (it uses it for the repeated-key message) and then throws it away. It does not note the line of an `!include`.
- The app's own reader keeps no position at all.
- The migration tools already find, in the TEXT of a recipe and of its fragments, the exact place of a key, a step, the end of a list (written as a block or on one line): this is how they edit recipes without losing comments. No function yet takes a path of keys and returns "file, line".
- The map of a recipe (slice A) holds for each table its path of keys and its steps, but no file and no line.

## Options
| | Option | What the author reads | For | Against |
|---|---|---|---|---|
| L1 | **As today** | `recipe.yaml: joins.X.tier1.steps[1]: [J10] ...` | Nothing to build. | The author must count steps and guess which included file holds them. |
| L2 | **One function "where is this path": given a recipe and a path of keys, it reads the text of the files and returns the file and the line** (the technique of the migration tools). Every message that has a path gets the place added, in the one function that prints a problem. | `recipe.yaml: tier 1 of the join X, step 2 (polars_join): [J10] ... File X_join.yaml, line 14 (included from recipe.yaml, line 52).` | One place to build and to test. Works for every problem that has a path (all check codes, the build errors once they carry their path). Asked only when there is a problem, so no cost when all is well. Serves both readers of a recipe without changing either. The writer of the audit file needs the same function (the line where a tier's `steps` ends) and Blueprint can use it later. | It reads the files a second time: if a file changed between the check and the message, the line could be off (guard: compare the file's hash, else print the path only). A second piece of code that understands `!include` beside the two readers: a test must prove on every shipped recipe that every path of every table, tier and step is found, in the right file. |
| L3 | **The reader keeps the place of every element while it reads** (file and line stored beside the data), and every problem carries it. | Same text as L2. | The line is exactly the one that was read. | The two readers of a recipe (the check's and the app's) must both be changed, and everything that copies or rewrites the recipe in memory (the resolved recipe, the audit copy, the map) must carry the places along or lose them. Much more code touched for the same sentence. |
| L4 | **The map of a recipe carries the places** (each table, tier and step node knows its file and line), filled by L2 or L3 | Same, and the audit dialog and Blueprint's tube map could show "defined in file F" for a node. | The place becomes available wherever the map is used. | Only as an addition to L2 or L3; alone it does not cover the problems found before the map can be built. |

For all: a problem that has no path (the whole file cannot be read) keeps the line the YAML reader gives, as today.

## The two bare engine errors (point 6 of the opening figures; build items, no decision)
A step that names a missing column and a cast that meets a bad value give today only the engine's own text. For any of L2 to L4 they must first carry what the app already knows when it runs them: the table or join, the tier, the step number and the action (her decided rule: name the step, the column and a fix). Then the same "where is this path" gives them a file and a line too. For an error that comes from the data (a bad value), the message names the step that met it and the column and value; the ROW of the data is a separate thing (the engine gives the value, not the row number; finding the row costs a pass over the data).

## Recommendation of the coordinator
**L2 now; L4 as a later addition when the audit dialog or Blueprint wants to show where a node is defined.**
- It gives her sentence for every problem with the least code touched, in one place, with one strong test (every path of every shipped recipe is found in the right file at the right line).
- It is needed anyway: the writer of the audit file (`audit_steps` beside `steps`, decided today) must find the line where a tier's `steps` block ends, in the right file. One function serves both.
- Proposed form of the place, after the plain words: "File `<name>`, line `<n>`" and, for a fragment, "(included from `<main file>`, line `<m>`)". The plain words come first (tier 1 of the join X, step 2), the file and line after, so the message stays readable for someone who does not open the file.

## Points that are hers
1. L1, L2, L3 (and L4 later or not).
2. The form of the sentence (above).
3. Whether the path of keys (`joins.X.tier1.steps[1]`) stays in the message beside the plain words, for people who search by it, or is replaced by them. My view: plain words and the file and line for the reader; the path kept at the end in brackets, because the check codes and the docs use it.
