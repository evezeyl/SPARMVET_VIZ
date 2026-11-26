# Study: how recipes AND data are read and written in every deployment use case (owner's order, channel M430, 2026-11-21, relayed by the review session)

A study. Build nothing, decide nothing. The viewpoints recommend; the owner decides.

## The owner's words (her spelling kept)

"we have to find a better way to read recipes - but also read and write data. Here are some of the possibilities I can think of - and try to describe the usage and how it can affect read/write of both data and recipes. I think we have two usages of the read recipes cases:
- Common recipes eg from a consortium of scientists where a user cannot edit those - only developers and specific users will be able to modify those - means the user will be able to read those but not to write on those. 2. The user has own directory where it can read write - here the user might have some of its data and there it should be able to export recipes but also to import recipes - eg. wants to verify reproducibility.
- static webpage: app is deployed: 1 recipe and data location (which might be updated at a certain frequency) then the app will updated, eg. we have data we want to show the results.
- webpage with exploration case: more or less same case except that the user can see data ... and change between different panels but not write or save anything.
- static pipeline case: the app is run directly as pipeline: a default recipe to use is selected at deployment and the data is passed directly from the pipeline - how exactly unsure but use case will be done by running a pipeline on usegalaxy or IRIDA that uses galaxy under the hood.
- The cases where the user can upload metadata or new data by selecting them in a path it has access to; can be a path that is common to a consortium but also from its own path eg. some of the data might be available from the consortium but the user might have metadata that is sensitive and thus cannot share with the consortium so some data is actually where only the user has access. Access is granted at deployment eg in a usegalaxy environment by the different paths the user has read/write to. In - a path where it should be able to for example load its own recipe for eg. reproducibility incl. audit and where sessions can be saved.
- similar but access is used at deployment eg. IRIDA.
- we have the case of local deployment where user has own user directory with read/write and maybe access to a common directory where recipes and data can be deposited (can be one unique path or several paths).
- we have the case where API can be used to give both the data and the recipe.
Can you have coordinator ask the agents incl. architect agent, data science and user agents at least investigate the different deployment possible (based on what I gave and other cases that I might have missed) and come back with suggestions (after having discussed together) on how to ensure that the different cases both the data and recipes can be read? Would be nice to have one system that allows all the cases - and determine by the deployment configuration file how its done (so each person in charge of deployment can adapt what is done to its needs via the deployment configuration file). A note - in some cases app will be shipped in a container - in some case app can be installed using github repo (eventually later pypi)."

## The order of work (review session's wording)

1. A scout first: how recipes, data, sessions, exports and uploads are found and written TODAY (`data_lookup`, the five locations, the imports directory, the shipped deployment files, the Connect / Galaxy / IRIDA / container notes in the repository). Facts with file:line. The writability of each place by deployment type marked VERIFIED or NOT VERIFIED.
2. Then the architect, scientist and data scientist, user and developer viewpoints, with one round of discussion between them. They must also name the use cases she missed (for example: a read-only container with a mounted volume; several users on one server; a pipeline that hands the data by API; offline use).
3. One table for her: use case / who reads what from where / who may write what where / what the deployment file would say / what breaks today / options with pros and cons / recommendation. Flag first anything that changes a result silently or hides a step from the user.
4. The table also answers her earlier questions in this thread: recipe naming `name_date`; upload refused when the name exists; selector newest per name; the user's own write place; the overwrite button only in the user's own place; the Data Import overwrite (task DATA-IMPORT-OVERWRITE); bundle-imported recipes; where sessions and the audit copy live. The recipe places study (`tmpAI/panel/recipe_places/TABLE_FOR_THE_OWNER.md`, P1 to P11) is folded into this ONE table, not a second one.
5. Check the ledger lines D-0333 and D-0340 (audit folder in the user's own directory) first; tag every point DECIDED / CONFIRM / OPEN.

Low priority. She brings it back to the review session when the table is ready. It replaces the narrower Data Import point b; a and c stay (answered: `tmpAI/coordinator/data_import_questions/ANSWERS_A_AND_B.md`, `tmpAI/panel/data_import_words/TABLE_FOR_THE_OWNER.md`).

## Files of the study (this folder)
`FACTS.md` (the scout's report, saved by the coordinator), then `architect.md`, `scientist.md`, `user.md`, `developer.md`, the discussion round, and `TABLE_FOR_THE_OWNER.md`.
