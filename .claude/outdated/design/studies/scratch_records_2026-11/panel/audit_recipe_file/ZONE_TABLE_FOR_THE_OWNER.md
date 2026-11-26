# How the audit recipe file tells original steps from audit steps: her zone idea, options, pros and cons

For the owner. Written by the coordinator, 2026-11-20, from one round of two viewpoints (architect with the developer's view, data scientist) with small checks RAN on the code. The question and the facts: `ZONE_question.md` and `FACTS.md` in this folder. Nothing is built. She decides.

Her idea: after each tier list (T1, T2, T3) a zone for the audit steps, with a start and a stop, so that the app knows what is original and cannot be modified, and what the audit added.

## Flag first: what no form can do, and what can go wrong silently
1. **The file alone never PROVES that an original step was not changed by hand.** In every form, if someone removes the markers by hand (or edits an original step), the file is still a valid recipe. Only two things catch it: comparing with the original, or a fingerprint of the original kept in the audit recipe (the key under `info:` she decided today). The scientist suggests that this fingerprint covers each tier's original steps, so that the check can say WHICH tier was touched.
2. **A marker written as a `#` comment is invisible to the app** (the reader drops every `#` line; tried: gone after loading). The text of the file and what the app holds would be two things that can disagree.
3. **A marker written as an item of the list crashes the engine today** and is refused by the check (tried); a one-line hand edit of such a marker would turn original steps into "removable" ones.
4. **A second list beside the original one must be read everywhere the steps are read.** Today two different functions read the steps of a tier (one for tier 1, one for tiers 2 and 3), used in 39 places. A place that forgets the new list would silently skip the audit steps. Guard: ONE helper that returns "original steps, then audit steps", and a test that fails when a reader does not use it.
5. **The keys of the stored tables:** the new list must stay out of the part that describes the original table, or a copy with an empty audit list would get another key than its original. To build and test.

## The forms
| | Form | Told apart from the file alone | What a hand edit can do unseen (without the original or the fingerprint) | Writing the file with her comments kept | Change of the recipe format | What a reader sees |
|---|---|---|---|---|---|---|
| F1 | **As today:** audit steps at the end of the same list, known only by their id `audit_...` | By the id only. | Remove the id: the step looks original. | Insert a step at the end of an existing list; a list written on one line (`steps: []`) must be rewritten. | None. | One list; the audit steps are the last ones, with an odd id. |
| F2 | **Her zone as two marker items in the list** (`audit_start` ... `audit_stop`) | By the markers (and the ids). | Move a marker by one line: original steps become "removable", or audit steps "original". Lose a marker. Two zones. Many refusals to write. | Inside the list, as F1. | A new kind of list item that is not a step; engine and check must learn it (39 places read steps). | A clear zone in the list. |
| F3 | **Her zone as `#` comment lines** | The app cannot see it (flag 2). | Everything. | Easy to write, impossible to read back. | None. | A clear zone, for people only. |
| F4 | **Her zone as structure: a second list `audit_steps` beside `steps` in the same tier.** The brackets of that list are the start and the stop. The engine runs `steps`, then `audit_steps`. | By structure: what is in `steps` is the author's, what is in `audit_steps` is the audit's. The audit list alone can be checked (only filters, drops, removals by key; each with id and `audit_comment`). | Move a step from one list to the other. | A NEW key is added after the original list; the original list is never touched, not even a one-line `steps: []`. A tier that does not exist is created with an empty `steps` and the audit list. | One new key in a tier, allowed ONLY in an audit recipe (tried: an ordinary recipe with it is refused today, as it should stay). | "steps:" then "audit_steps:", each audit step with its reason. The order is written in the file. |
| F5 | **The audit steps in their own file**, beside an untouched copy of the original's files | By file. The original's files are byte for byte the original. | Edit the copy of the original (caught by the fingerprint). | Nothing of the original's text is touched. | A new file kind. | Two things to read together: the pipeline, and a list of audit steps "by place". **It reconsiders her decisions** that the audit recipe is a copy WITH the audit steps added to the recipe (D-0102, D-0148) and that the audit recipe is the recipe of an audit export (D-0324). |

Checked on the shipped recipes (READ and RAN by the architect): all 47 included tier files have the shape "the whole tier in one file" (`tier1: !include file`, the file starts with `steps:`); 10 tiers are written in the main file; none uses an included file for the steps list only. No included file is used by two tables inside one recipe (one file is used by 4 different RECIPES; each audit folder has its own copy, so nothing is shared there). So the shared-file case does not occur in the shipped recipes; it can occur in a recipe of her own.

What F4 removes from the code of slice A: the rule "an audit step must be at the end of its list" (the structure says it) and the position of a step inside the keys.

## The two viewpoints
| Viewpoint | Ranking | Main reason |
|---|---|---|
| Architect | F4 (keeping the ids), F1, F2, then F3 and F5 | The zone as structure needs no marker that can be lost; the writer adds a key and never edits the original list; "at the end" is no longer a rule to check. Only with the one helper and its test (flag 4). |
| Data scientist | F4, F5, F2, F1, F3 | Order is obvious and hard to get wrong; a report lists "the author's pipeline" (`steps`) and "what the audit added" (`audit_steps`) directly. F5 is the strongest on integrity but reconsiders her decisions and is harder to read. With the fingerprint per tier under `info:`. |

## Recommendation of the coordinator
**F4: her zone, written as a second list `audit_steps` beside `steps` in each tier, with the ids and `audit_comment` kept on each audit step.**
- It is her idea (a start and a stop after each tier list), with the brackets of the list as the start and the stop, so there is no marker to lose, move or duplicate.
- An audit step can never sit between two original steps, and the original list is never edited: the app refuses any change to `steps` in an audit recipe by comparing with the original and with the fingerprint.
- Her comments are kept, because the writer only ADDS lines after the original block.
- It carries over to a plot's tier 3 unchanged (the plot recipe, built later).
- What it costs: one new key in the recipe format for audit recipes only; the engine and the keys must learn the second list through ONE helper, with a test that fails if a reader forgets it; the audit steps built in slice A move from the end of `steps` to `audit_steps`.

## Points that are hers
1. **F1, F2, F3, F4 or F5.** (F5 would change three of her decisions.)
2. If F4: the **name of the list** (`audit_steps`), a format decision.
3. The **fingerprint under `info:`**: one for the whole original (as decided today), or also one per tier, so that the app can say which tier was changed by hand. My view: per tier as well; it costs a few lines in the file and makes the refusal precise.
4. A **file shared by two tables** in one recipe (does not occur in the shipped recipes): refuse the audit step with a plain line (my suggestion), or write it for both tables and say so.
5. Still open from the first table: how the file is written (copy the files and edit the text; or the comment-keeping library, which needs her yes) and the base of the `audit/` folder. With F4 the text edit becomes much safer (only additions), so the library is no longer needed for the audit; it stays a separate question for Blueprint's save.
