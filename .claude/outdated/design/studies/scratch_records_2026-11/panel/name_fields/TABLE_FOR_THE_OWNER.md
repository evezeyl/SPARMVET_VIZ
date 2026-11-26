# The purpose of each name field of a recipe: one table for the owner (2026-11-21; your order with decision D-0405; it also answers Gallery question Q8)

## 0. How to read this
- A scout read the format text, the checker and the code on `dev`. Nothing was run and nothing is changed. Written by the coordinator from its report.
- READ = read at the file and line given. NOT VERIFIED = not found by reading, or only knowable by running.
- Your rule: an option is described on its merit; "reconsiders a decision?" is information in its own column, never an argument.
- Short file names: `spec` = `.claude/design/recipe_format_spec.md`; `check` = `libs/utils/src/utils/recipe_check.py`; `home` = `app/handlers/home_theater.py`; `export` = `app/handlers/export_handlers.py`; `taxonomy` = `libs/viz_gallery/src/viz_gallery/taxonomy.py`; `gallery_manager` = `libs/viz_gallery/src/viz_gallery/gallery_manager.py`.

## 1. Your question, answered first

**"ui_label has to be shown in the ui ? is it not more a ui tag to be able to find the correct recipe ?"**

The plot's `ui_label` IS shown on screen. It is both: the visible name and the tag by which an example is found.
- HOME: the name of the plot's tab inside a group (`home:109-110`), and the name in the list of plots of the audit dialog (`home:114-115`).
- Gallery: the name of the example in the list and in the dropdown (`taxonomy:55-66`; `gallery_manager:142`). The Gallery refuses a second example with the same `ui_label` (`gallery_manager:113-117`).
- BLUEPRINT: the name in the list of plots (`app/handlers/blueprint_handlers.py:2313`) and in the lineage.
- The export report uses it only when `ui_title` is missing (`export:368-373`).

**What `info.label` shows:** the title banner of HOME, above the tabs (`home:1141-1144`), unless the app features set their own title; and one row of HOME's Info panel. It is NOT shown in the Gallery (`taxonomy:58`).

**Are the two ever seen together?** In HOME yes: the banner shows `info.label` and the tabs show the `ui_label`s. In the Gallery only `ui_label` is seen. No code compares the two.

## 2. The table

| Field | What it is for, in the format's words | Where the user sees it | Who writes it | Required? | Short or long (rule; real lengths) | When it is missing | When it differs from a related field |
|---|---|---|---|---|---|---|---|
| The recipe file name, and the top-level `id` | the identity of the recipe | not found on a screen by reading (NOT VERIFIED) | the author | the `id` must equal the file name: refused otherwise (`check:244-245`) | no rule | - | refused |
| `info.label` | "the short name of the recipe" (`spec:367`) | HOME: the title banner (`home:1141-1144`) and a row of the Info panel. Not the Gallery. | the author; BLUEPRINT "new recipe"; the Gallery generator; the Test Lab scaffold | yes: refused when missing (`check:316-317`) | the format says short; no length is checked. Real lengths: 11 to 40 characters in the 16 shipped recipes; 9 to 28 in the Gallery | the recipe is refused | nothing: it is never compared with a `ui_label` |
| `info.description` | "what the recipe answers, for which population, from which data" (`spec:368`) | BLUEPRINT reads it; the screen is NOT VERIFIED. In HOME it is a row of the Info panel. | the author; BLUEPRINT | no; an advice when missing | no rule | an advice that no screen shows (section 4) | - |
| `info.contact` | "who to call when the recipe fails; the load gate shows it" (`spec:370`) | HOME: the message when a recipe is refused, "Contact: ..." (`app/src/bootloader.py:624`). The export README. | the author | no; an advice when missing | no rule | the contact of the deployment, else "not configured" | the recipe's contact wins over the deployment's |
| `info.submission_date` and any other key of `info` | free: "displayed in the Info panel" (`spec:373`) | HOME: a row of the Info panel (`app/modules/data_analysis_recipe_info.py:18-27`) | the author; the Gallery generator writes `submission_date` | no | no rule | no row | no code reads `submission_date` |
| Group `ui_label` | "the short name of the tab" (`spec:484`) | HOME: the group tab (`home:104-105`). BLUEPRINT: the list of groups. | the author; BLUEPRINT | yes (`check:1102-1103`) | short. All 34 Gallery examples say "Example" | the group's `description` is shown as the tab, then the group id | see section 3, point 2 |
| Group `description` | "the question the plots of the group answer" (`spec:486`) | only as the tab text when `ui_label` is missing; no other screen found | the author | no; an advice | no rule | advice | - |
| Group `ui_title` | "a longer name, used by the report and the headings" (`spec:485`) | NOWHERE: no code reads it (section 3, point 1) | the author | no | no rule | - | - |
| Plot `ui_label` | "the short name of the plot's tab" (`spec:497`) | HOME tab and audit dialog; Gallery list and dropdown; BLUEPRINT list and lineage (section 1) | the author; BLUEPRINT | yes (`check:1127-1128`) | short; no length is checked. Gallery: 9 to 28 characters, middle value 17 | HOME shows the plot id; the Gallery refuses the example | it is the Gallery name; `info.label` is not read there |
| Plot `ui_title` | "a longer name used by the report; without it the report uses `ui_label`" (`spec:498`) | ONLY the export report (`export:368-373`). Not HOME, not the Gallery, not BLUEPRINT. | the author | no | 5 found in the shipped recipes, 27 to 32 characters; none in the Gallery | the report uses `ui_label` | the report shows the longer name, HOME the short one |
| Plot `description` | an optional key (`spec:492`) | no screen found (NOT VERIFIED) | the author; the Gallery generator | no; an advice | no rule | advice | - |
| The figure texts: title, axis and legend names | "written only in the `labs` layer" (`spec:179`; your decision D-0253) | inside the picture | the author | no | no rule | no title in the picture | the old `title:` key is refused |
| `labels:` of a collection (display names of columns) | "mapping column to display text"; "shown in the audit dialog" (`spec:69, 474`) | the reader in the audit dialog was NOT FOUND by reading | the author | no | no rule | the column name | - |
| `label` of a table, a join, a schema | required; "stays `label` for now" (`spec:179, 384, 468`) | BLUEPRINT: the list of tables. The export. The lineage. | the author; the Test Lab scaffold | yes | no rule | NOT VERIFIED | your decision D-0360: a table label may be an alias of a column |
| Gallery: the folder name | not in the format | not shown: it is the key of the example | the author | must equal the recipe `id` (`check:1256-1257`) | no rule | - | - |
| Gallery: the `##` heading of `example_meta.md` | not in the format | the heading of the guidance page | the author | a page without a `##` line is an error (`taxonomy:97`) | no rule | error | it is not read as the name and not compared with it (your decision D-0397 rewrites these headings) |
| Gallery: the `name` in the stored list of examples | not in the format | the Gallery list and dropdown | made by the code | - | - | - | always equal to the plot's `ui_label` |
| Deployment: the title in the app features (`ui_title.text`) | not in the recipe format | HOME: it replaces the banner (`home:1139-1142`) | the person who deploys | no | no rule | `info.label` is used | note: the same word `ui_title` is also a recipe key with another meaning |
| Deployment: the text of the recipe selector | - | NOT FOUND by reading | - | - | - | - | - |

## 3. Things the table shows that you may not expect
1. **A group's `ui_title` is read by nothing.** The format says the report and the headings use it. No code does. (A plot's `ui_title` is read, by the export only.)
2. **A group without `ui_label` shows its `description` as the tab.** The format says this fallback "goes" (`spec:490`); the code still has it (`home:105`). Today the checker refuses a group without `ui_label`, so the fallback cannot be reached by a checked recipe.
3. **The longer name `ui_title` never appears in HOME, the Gallery or BLUEPRINT.** It exists only in the export report.
4. **No name field has a length rule or a character rule.** "Short" is only a word in the format.
5. **Two keys are called `ui_title`:** one in a recipe (the longer name of a plot or group), one in the app features (the banner of HOME). They mean different things.
6. **A record is out of date:** the ledger line D-0387 says the code reads `info.label` for the Gallery name; the code now reads the plot's `ui_label`, as you decided.
8. **CORRECTION added 2026-11-21 by a second scout: BLUEPRINT's Info form uses another key, `info.name`.** "New recipe" in BLUEPRINT writes `info.label` (`libs/blueprint_arch/src/blueprint_arch/new_recipe.py:27-28`), but BLUEPRINT's form for the recipe's Info shows and writes `info.name`, in a field labelled "Name" with the hint "Short display name" (`app/handlers/blueprint_handlers.py:2542, 2558, 2571-2572, 2609-2610`). So one thing, the name of the recipe, has two keys in BLUEPRINT today. Because any key of `info` is accepted, the checker does not notice.
9. **CORRECTION:** the message a HOME user sees when a recipe is refused ("Contact: ...") is at `app/handlers/recipe_gate_handlers.py:101`. The line of `app/src/bootloader.py:618-626` given in the table is the message to the person who starts the app.
10. No shipped app features file sets the banner title (`ui_title`), and its validator does not check that key.
11. Two records to reconcile: the format says `ui_label` was renamed on 2026-11-17, the ledger line D-0253 is dated 2026-11-18; and the ledger line D-0360 is marked decided while its own text calls the alias "a proposal, not a rule".
7. In all 34 Gallery examples `info.label` equals the plot's `ui_label` today, because the generator writes both from one value. In the 16 shipped recipes they all differ (read from a search of the files; the plots kept in included files were not all read).

## 4. Gallery question Q8: what `info` is for in a Gallery recipe
- `info.label` is required by the checker and is shown nowhere in the Gallery.
- `info.description` and `info.contact`: when missing, the checker gives an advice. **No screen shows that advice.** HOME shows only five kinds of advice (`app/modules/data_analysis_recipe_validator.py:58`); the others are "for the author's own review" and no screen for them was found. Your decision D-0403 (advices on tags go into one table for you) is not built.
- `info.submission_date` is written by the Gallery generator and read by no code. It would appear only as a row of HOME's Info panel if the recipe were opened in HOME.
- So in a Gallery recipe today `info` is: one required name that the Gallery does not show, plus free text that nothing reads.

Options for Q8 (not chosen; each on what it gives and costs):
| Option | What it gives | What it costs | Reconsiders a decision? |
|---|---|---|---|
| a. Keep `info` as in every recipe; say in the rule that the Gallery does not show it | one format for all recipes; an example can be opened in HOME and has its banner | a required field with no use in the Gallery | no |
| b. Show `info` of the example in the Gallery (for example the description and the date under the picture) | what the author writes is seen; the date gets a use | a place on the Gallery page; text for 34 examples to check | no |
| c. In the Gallery profile, make `info.description` the one-sentence description of the example (the "real description" of your decision D-0397) instead of the heading of `example_meta.md` | one source for the description; the checker can require it | changes where D-0397 puts the description (the heading) | D-0397 |
| d. Drop `submission_date`, or give it a reader (for example "added on" in the list) | no field that nothing reads | a small change to the generator and the 34 recipes | no |

## 5. Where your description and the format differ
- Your words: "the ui_label is aimed to be short - The info.label its the header block and then a title can be abit more long that the short ui_label."
- The format: `info.label` is "the short name of the recipe" (`spec:367`; also `spec:105` and `spec:192`). The longer name is `ui_title`, and only the report uses it.
- The code: HOME's banner shows `info.label`, so it already behaves as a header. The real values are already longer than the tab names (up to 40 characters).
- Also open in the format: whether the key `label` of `info` is renamed at all (`spec:179`: "PENDING").

Options (not chosen):
| Option | What changes on screen | What changes in the recipes | Reconsiders a decision? |
|---|---|---|---|
| A. Keep the format: `info.label` is the short name; tell authors | nothing | nothing | no |
| B. Change the format's sentence: `info.label` is the title of the recipe (the banner of HOME) and may be longer than a tab name | nothing: the banner already shows it | nothing; the 16 shipped recipes already fit | the sentences of the format at `spec:105`, `spec:179`, `spec:192`, `spec:367` (design text, DEC06 and DEC52) |
| C. Keep `info.label` short and add a new key for the banner | the banner changes only where authors write the new key | the 16 shipped recipes need the new key to keep a long banner | no (the naming of the `info` key is still pending) |
| D. Add an advice on length ("a tab name over N characters") | nothing in HOME: advices of this kind are not shown today | none | no |

Option B describes what the code and the shipped recipes already do. Options B and D can be combined. With your decision D-0405 the coherence of `info.label` and `ui_label` is the author's control, as an advice at most.

## 6. To decide (ranked)
1. What `info.label` is: the short name (A), the title of the recipe (B), or short with a new key for the banner (C).
2. What `info` is for in a Gallery recipe (section 4, a to d).
3. Whether a group's `ui_title` gets a reader (the report headings, as the format says) or is removed from the format.
4. Whether any name gets a length advice, and where an author sees advices at all (today: nowhere for most of them).
5. Whether the fallback "group description as the tab" is removed from the code, as the format says.
6. The two meanings of `ui_title` (recipe key and app features key): rename one, or say it in the rule.

## 7. Not verified
The full list of names in the shipped recipes (plots in included files); how the banner and the tabs look together on screen; the text of the Info panel rows; whether the export README shows `info.label`; whether the Gallery preview shows anything of `info`; where BLUEPRINT and HOME show a plot or group description; the recipe selector text; the reader of the collection `labels:` in the audit dialog; the recipe `id` on a screen. The lengths were counted by hand from a search, not by a script.
