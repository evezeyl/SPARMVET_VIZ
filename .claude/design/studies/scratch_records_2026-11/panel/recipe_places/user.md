# Recipe places: the USER viewpoint (panel-user, 2026-11-20 night; condensed by the coordinator from its report; read from the brief, not re-checked in code)

People: A uses HOME with the lab's recipes; B also writes recipes in BLUEPRINT; C looks after the common recipes.

## What the screen must say
- Not the words "export" for a recipe (the app already has the results export: "export for production" will be read as that), hash, id, slug, `_imported_`.
- Always: where the file went (place and name); whether a file was replaced or deleted; how many saved sessions will no longer open (D-0362; the app cannot tell a typo from a real change); that the new recipe appears in the list only after a restart (today), or refresh the list; that exports already made keep their own copy of the recipe (D-0389).
- Sentences: (1) name exists, own place: "A recipe named `amr_profile_2026-11-17` already exists in [place]. Nothing was saved. [Replace it] [Save under another name] [Cancel]." (2) name exists in the common place: "The lab already has a recipe with this name. Choose another name, so two different recipes are not mistaken for one." (3) write in the common place: "This app cannot save into the lab recipes. Your file is saved as a draft in [place]. To make it a lab recipe, give it to the person who looks after the lab recipes." (4) hyphen in the name part: "Use letters, digits and underscore. The date is added by the app."

## Words proposed
- Switch: "Show older versions"; help: "Older dated copies of the same recipe. Use them to reproduce an earlier result, not for new work."; each entry tagged "older version"; a session made with an older version shows it even when the switch is off.
- Final save: "Save final version (dated)"; dialog: "This creates `name_2026-11-17` in [place]. Earlier dated versions move to older versions. Drafts are not dated."
- Overwrite, own place only: "Replace the file in [place]"; dialog: "The current file will be replaced. [N] saved sessions made with it will no longer open. Results already exported are not affected. [Replace] [Cancel]", Cancel the default.
- Never "My recipes" on a shared server: `user_data` is one folder per deployment, everyone there sees and replaces everything. Write "Shared drafts of this app".

## The list
Two headings ("Lab recipes", "Drafts / own recipes"; colour alone is not enough); the real file name with the date in words beside it; "2 older versions" beside a recipe that has them; undated names show "no date"; the date is read from the last `_` followed by an ISO date.

## "Remove the old file by hand"
A cannot; B only on a local PC; on a shared server, Galaxy or Posit Connect the user has no folder access (reasoned, not verified); C probably can as the administrator (assumed). So D-0390's same-day correction by hand does not work for A and B: the alternative is the in-app Replace in the own place; for the common place C works outside the app with a written procedure and the app names the path in the refusal.

## Models
- M1 (common read-only; own recipes in `user_data/recipes/`): A sees lab recipes; B saves, replaces, makes a dated final in the own place; a typo in a LAB recipe cannot be fixed by B (copy under a new name = two recipes with the same content); C works by hand on the server; the final save never reaches the common place. Frightening: colleagues' drafts in the list; the same name in both places; a draft taken for a checked recipe.
- M2 (drafts in user data; "Save final version" writes the dated file into the common place only where the deployment allows): B has no final-save button in a scientist deployment (the sentence must say what to do next); C publishes from the maintainer deployment; a same-day typo in a published recipe is refused, so C removes by hand. Without a login "everyone who opens this app can publish": the screen says so.
- M3 (all in one place): nobody can tell lab from own; an overwrite control there reaches lab recipes (contradicts D-0394). Not recommended.

## Recommendation
M2 with M1's storage: drafts in the shared drafts place with Replace there; "Save final version" dated; the common place written only by the maintainer deployment; old versions moved by the app to a subfolder behind the switch (nobody deletes by hand); the list refreshes without a restart, or the screen says so.

## Open for the owner
A second same-day correction in the common place (a suffix would break the sort rule of D-0391); whether drafts of others are visible to A; who "the person who looks after the lab recipes" is (no new configuration variable, D-0340); the bundle import's `_imported_<timestamp>` name breaks the `name_date` pattern.
