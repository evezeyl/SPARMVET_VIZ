Written by Opus for D-0589
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md`. Every anchor lies outside the D-0588 block and occurs exactly once (fixed-string search, working tree with the D-0588 paste). Her words are copied from the channel block M649.

## BLOCK 1. INSERT AFTER the line `**Open, hers: WHERE is the "not in metadata" line added?**`
`> **ANSWERED by D-0589: recipe-wide**, placement (i) (the review session's reading of her words below): with a metadata file attached, every result table and the metadata receive the ids they lack, with or without a join.`

## BLOCK 2. INSERT AFTER the line that begins `- Lean (Opus, as a lean): (ii): it is her reading of the metadata-only tables`
`  > **Superseded by D-0589** (her words go the other way; kept as history).`

## BLOCK 3. INSERT AFTER the line that begins `- Lean (Sonnet, as a lean): (ii), for the reason of her purpose`
`  > **Superseded by D-0589** (her words go the other way; kept as history).`

## BLOCK 4. REPLACE `## THE CAUSE, AND WHAT WAS FOUND` BY the lines up to END BLOCK 4:
### Added 2026-11-23 (ledger D-0589): the completion is recipe-wide, with or without a join; her use case

**Her words, exact.** "yes we should consider results where no metadata is joined - I think that as long as a metadata file is attached then all the original results should received the ids - whether or not the join - Our pipeline is supposed to work on set where ids are identical both between results and metadata - if not we need to add the ids to tables and metadata respectively even in an abscence of join and need clearly to treat what those missing ids mean ... I think that is our use case ..." [HER WORDS D-0589]

**Decided in her words (she writes "I think").**
- "as long as a metadata file is attached then all the original results should received the ids - whether or not the join".
- **The use case:** "Our pipeline is supposed to work on set where ids are identical both between results and metadata".
- **If not:** "add the ids to tables and metadata respectively even in an abscence of join and need clearly to treat what those missing ids mean".
- The review session's reading: this is placement (i) of the D-0587 sub-section; both leans for (ii) are superseded.

**Consequences, by reading and reasoning (no new numbers).**
- **(a) A result table that no join touches still shows the added lines.** The demo plots that read a table with no metadata join: `amr_heatmap` (ResFinder itself), `qa_l50_integer` (a table made from Quast alone) and the Summary tables' plots [ESTABLISHED: PATHS Q4]. On the demo only ResFinder lacks ids, so `amr_heatmap` gets the 4 added lines; how they are drawn is the run already registered. Quast and Summary hold all 42 and get nothing. The recipe's steps must say how the added lines are treated (the required meaning, D-0574, D-0586).
- **(b) The two metadata-only tables hold a "not in metadata" line WHENEVER the metadata is completed**, not "always". On the demo: never (0 ids outside the metadata). On `left_join_lesson`: 2 [ESTABLISHED: OVERLAP section 1].
- **(c) Keys and places.** The completed metadata reads every result file, and every completed result table reads the metadata file (a stored table's key holds the files it reads [CODE READ `app/modules/cache_keys.py:14-20`]). So a change in any file rebuilds every table below it ("we need to ensure that everystep after a change in a place is recalculated" [HER WORDS D-0560]): a fact, not a cost argument. Her rule of places (D-0553: at most one chosen place on a path; the original parents may all be chosen) holds in one way and not in the other:
  - **(A) The completion reads the FILES as read**, before any place. The first places stay original parents side by side, no place lies below another, and an audit step never changes what is completed.
  - **(B) The completion follows the places** (it reads the tables after their steps): an entity removed at the metadata is no longer added to the results; but a result table's first place then lies below the metadata's, two places on one path.
  - Which one her use case ("identical sets") points to is hers.
- **(d) No cycle** when both completions read the files: the union of the ids is computed once from the files, and each table is completed to it. A cycle appears only if the metadata is completed from completed result tables, which are themselves completed from the completed metadata (both under (B)).
- **(e) "Equal id sets" is the state AFTER the completion**; the data check reports the differences found BEFORE it.
  - Equal in every table only if each result table is completed to the union, and not to the metadata file alone. Otherwise an id found only in another result file reaches the metadata but not the other result tables.
- **(f) "Recipes do not start from the metadata" (D-0586) stands** for the joins.
- **(g) No metadata attached: no completion,** and no id check unless the recipe declares a population. The recipe check reads the metadata block only when present and requires none [CODE READ `libs/utils/src/utils/recipe_check.py:356-357, 381-384`]: today it says nothing there.

**What remains hers, one at a time.**
1. **The completion reads the files as read (A), or follows the places (B)?** (This is the earlier question "which metadata", now for both directions.) On the demo, remove at the metadata one of the 4 ids that ResFinder lacks: with (A) ResFinder keeps its added line for it; with (B) it is no longer added, and ResFinder's first place lies below the metadata's. Lean (Opus, as a lean): (A): no cycle, her rule of places holds, and an audit step never changes what is completed. [Sonnet lean] Neither: say what you meant.
2. **The reference of a result table's completion: the metadata's ids, or the union of all ids (every table identical)?** On the demo: no difference (0 ids outside the metadata). With two result files, an id that only one of them holds: under "the union" it is added, marked, to the other one too. Lean (Opus, as a lean): the union, her use case "ids are identical both between results and metadata". [Sonnet lean] Neither: say what you meant.
3. **Item 2: a line of the metadata with no usable id.** Under the recipe-wide completion it cannot be given to any result table: it has no id to give. Only the metadata holds it, and it never matches. The options (a), (b), (c) of item 2 stand. Neither: say what you meant.
4. **The rest of the list, by title:** the marker's form and name; the block's form and tables; before or after the recipe's tier-1 steps; the log's directory; where the red warning shows; a dummy id; how "data first" is enforced; a recipe with no metadata block (question 13) and her view of D-0588; the count per target; the threshold; the two QA tables (D-0587, her "a)").

---

## THE CAUSE, AND WHAT WAS FOUND
END BLOCK 4
