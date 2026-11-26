# Names across the app: the viewpoint of the user new to data science (panel-user, 2026-11-21; filed by the coordinator from its report; its weight is the words ON SCREEN and in the documentation)

Labels: READ = read at file:line (taken from FACTS.md and the name fields table); REASONED = its judgement from the user's seat. Nothing was run. The ledger lines were not opened by this viewpoint.

## Summary
1. "A short name is what I click, a title is what heads a page, a description is one sentence saying what it is for, help is what I open when I am unsure."
2. The worst confusion is not the keys but the words: one user space has seven names (Blueprint Architect, Wrangle Studio, Flight Deck, Recipe Editor, Surgeon, Blueprint, BLUEPRINT), and a newcomer thinks they are seven tools.
3. One silent failure: BLUEPRINT's Info form has a field "Name" ("Short display name") that writes `info.name`, but HOME's banner reads `info.label` (`app/handlers/blueprint_handlers.py:2571-2572, 2609-2610`; `app/handlers/home_theater.py:1143`). "I type a name and the banner does not change."
4. The moment of choosing (a recipe, a Gallery example, a session) is where names matter most and where the screen shows least: a Gallery list with one line, and a session box that says "Describe this session" but is used as the name.
5. Recommended: one set of screen words, one short name, one title, one description for every thing that has them, and the same fallback everywhere. It prefers the `ui_` prefix for keys (variant A) only because it makes "shown on screen" true; the words on screen matter more than the key names.
6. Where a foreign word must stay (plotnine's `labs`, Polars action names, T1 / T2 / T3), the screen says what it means on one hover, from one source.

## The kinds, as this user reads them
| Kind | One sentence | Word on screen | Length (its proposal; an advice, not an error) | When missing (one rule for the whole app) |
|---|---|---|---|---|
| Id | the unique name the app uses; I never need to read it | "id" | letters, digits, `_` | an error |
| Short name | what I click: a tab, a list item, a button | "name" | up to 30 characters (the 34 Gallery names run 9 to 28) | show the id and give an advice; never show a description in its place |
| Title | the heading of a page or a report | "title" | up to 80 | show the short name |
| Description | one sentence: what it is for, which data, which question | "description" | one sentence, up to 160 | show nothing, give an advice |
| Help | the meaning, shown only when I ask | "?" or "i" | free | no mark |
| Display name of a column | the column as I read it in a table or on an axis | "display name" | up to 30 | the real column name |
| Text in the plot | title, axes, legend inside the picture | "plot text" (the key `labs` stays: it is plotnine's) | free | no text |

Why "name" and not "label" on screen: "label" makes this user think of an axis label or a tag on a sample; eight jobs hide under `label` today. Where a message must quote a key it says both: "give each example its own short name (ui_label)". Today it says only "give each example its own ui_label" (`libs/viz_gallery/src/viz_gallery/gallery_manager.py:113-117`).

## Matrix: thing against kind (keys of its variant A; "-" = not needed)
| Thing | Id | Short name | Title | Description | Help | Display name | Plot text |
|---|---|---|---|---|---|---|---|
| Recipe | `id` (= file name) | `info.ui_label` | `info.ui_title` | `info.ui_description` | help file | - | - |
| Group | key | `ui_label` | `ui_title` (needs a reader) | `ui_description` | - | - | - |
| Plot | key | `ui_label` | `ui_title` | `ui_description` | - | - | `labs` layer |
| Table, schema, join | key | `ui_label` | - | `ui_description` | - | - | - |
| Column | the field key | - | - | - | - | `ui_label` (pending) | - |
| Action | its registered name | `ui_label` | - | `ui_description` | action help | - | - |
| Plot component | registered name | `ui_label` | - | `ui_description` | help | - | - |
| Panel of a sidebar | `type` | `ui_label` (today read by nothing) | - | - | - | - | - |
| User space | internal value | nav name | banner | - | help file | - | - |
| App features set | `name` | `ui_label` (today `display_name`) | - | - | - | - | - |
| Deployment | file path | `ui_label` (today `deployment_name`, shown nowhere) | banner title | - | - | - | - |
| Gallery example | folder = recipe `id` | plot `ui_label` | - | plot `ui_description` | `example_meta.md` | - | - |
| Session | session key | `ui_label` | - | optional note | - | - | - |
| Export bundle | time and name | the name I type | report title | - | README | - | - |

## The cases
| Case | Today | In the scheme | What changes for the user | Reconsiders a decision? (information) |
|---|---|---|---|---|
| `info.label` against `info.name` in BLUEPRINT | the form writes one, HOME reads the other; the checker accepts both | one key for the recipe name; the old one refused with the new name in the message | "I stop typing a name that nothing shows." The strongest case. | none |
| The short name: `ui_label`, `label`, `name`, `display_name` | four keys in different files | one key wherever a short name exists | "name" on screen whatever the key | the pending question on `label` keys; D-0253; D-0360 for the column |
| `ui_title` of a recipe against `ui_title` of the app features | two meanings; no shipped file sets the second | remove or rename the app features key | the banner always names my recipe | none |
| A group's `ui_title`, read by nothing | the format says the report uses it | give it a reader, or take it out of the format | "I would write a title and see nothing" | none |
| `description` used as a tab text | `home_theater.py:105` | removed; the tab shows the short name, then the id | a sentence as a tab name looks like a bug | none |
| Gallery heading against example name | two texts, not compared | name = short name; description = one sentence | at the moment of choosing I need the name and a sentence | D-0397 (one line in the list); D-0405 |
| "Blueprint Architect" against "Wrangle Studio" | the nav shows the first; the internal value is the second (`home_theater.py:1825-1839`) | the screen says "Blueprint" everywhere | one place, one word | the owner's glossary page (`Terminology.qmd:33`) |
| dataset, table, schema, collection, join | five words | "table" for what I see; "table definition (schema)" once; "join" stays; "dataset" and "collection" leave the screen | "I think a collection is a folder of tables" | none |
| plot, figure, graph, chart | "figure" in the report, "graph" in the lineage, "chart" proposed for the new filter | "plot" everywhere | one picture, one word | D-0398 ("Chart type" would read "Plot type") |
| step, action, node | "node" in the audit list, "transformation node" in the help | "step" for what I add; "action" for the kind I pick; "node" never on screen | "A step uses one action", said once | none |

## One word per thing, on screen and in the documentation
| Thing | The word | Replaces | A second word stays where |
|---|---|---|---|
| The recipe | "data analysis recipe" (short: "recipe") | pipeline, manifest | "pipeline" only for the data pipeline outside the app |
| The BLUEPRINT user space | "Blueprint" | Blueprint Architect, Flight Deck, Recipe Editor, Surgeon, Wrangle Studio | nowhere |
| The Gallery | "Gallery"; its panels "Examples" and "Filters" | Inspiration, Explorer, "Taxonomy", template | nowhere |
| Test Lab | "Test Lab" | Dev Studio, LAB | internal only |
| The notes panel | "Alerts" or "Notification Log": the owner decides ("Alerts" sounds like a problem) | the other | - |
| The picture | "plot" | figure, graph, chart | "figure" in plotnine's documentation |
| A group | "group", shown as a tab | analysis group | the key `analysis_groups` |
| A table | "table" | dataset, collection | T1 / T2 / T3 with a hover |
| A step | "step" | node, transformation node | "action" = the kind of step |
| The zip for others | "export bundle" | results bundle, reproducibility bundle, reimport bundle | nowhere |
| The session zip | "session file" | "Export Active Session" | nowhere |
| The info panels | "Recipe info" and "Deployment" | "Info" twice on one screen | nowhere |
| The primary key | "entity key" with a hover | PK, slug, primary key | nowhere |
| A name that stands for a column | "display name", with the real column in a hover | alias | nowhere |

Buttons: six buttons read "Apply" today with six different consequences (filter, audit, BLUEPRINT form, join, import, style). Suggestion: the button carries its object: "Apply filter", "Apply audit step".

## The variants for the keys (what the user sees is the same in all three)
| | A: `ui_label`, `ui_title`, `ui_description` wherever a screen shows it | B: plain `label`, `title`, `description` everywhere | C: keep today's keys, fix only the collisions |
|---|---|---|---|
| For this user | the prefix tells an author "this appears on screen" | `label` keeps its many jobs, and plotnine uses `labs` | the smallest change; the `info.name` and `ui_title` collisions are fixed |
| Condition | no `ui_` key unless a screen really shows it | - | `description` stays ambiguous |
| How | one pass; the old key refused with the new name; the 34 Gallery examples and the shipped recipes rewritten by a script | the same | the same, fewer files |
It recommends A on merit; if the owner prefers C, the words on screen above apply unchanged.

## What the screen must carry at the moment of choosing
- The recipe selector: the name plus the description sentence.
- The Gallery list: the name and beside it one sentence "what it shows, for which data". (D-0397 says one line; this user would still need the sentence.)
- The session box: "Name this session (short)". Today: "Describe this session…" (`app/handlers/session_handlers.py:224-226`), and the card shows the recipe id, not the name (`:258`).
- A display name: "Display name: <x> (column: <real name>)", so that the user sees which column was used.
- HOME's top: say which banner is the installation's and which is the recipe's.
- The deployment template says the deployment name is "shown in app footer" (line 22); no footer was found. A deployer is told something false.

## Keeping it true
One place for the words and their meanings (the spec, as decided for the Gallery terms), read by the hover for every term; the audit of retired words gets the words above; advices (length, a missing description) shown in one list in BLUEPRINT's "Validate".

## To decide first (ranked by this viewpoint)
1. The one word on screen for the Blueprint user space, and "Wrangle Studio" out of every text a user reads.
2. `info.label` and `info.name`: one key for the recipe name; the title a second key or the same.
3. A group's `ui_title`: a reader or removal; the app features `ui_title`: removal or a new name.
4. Plot, figure, chart: "plot" everywhere.
5. Variant A, B or C for the keys.
6. Where advices are shown.

## Not verified
Nothing was run; screen texts are from reading. The recipe selector text; whether tabs cut long names; the Info panel rows; the content of "Alerts". The length numbers are its proposal, not measured.
