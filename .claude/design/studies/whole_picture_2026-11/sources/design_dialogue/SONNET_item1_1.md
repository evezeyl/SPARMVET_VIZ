# SONNET draft, item 1 answered, item 12 confirmed (D-0584, D-0585), 2026-11-23

Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md`. Reading only. Blocks are exact; "begins" means the whole line starts so and is unique. [Opus lean] is left for the check.

## BLOCK 1. REPLACE (item 1 of "The next order")
REPLACE `1. **What is fed for a result-file id that is not in the metadata** (new A). Lean: a line with a marker.`
BY `1. **What is fed for a result-file id that is not in the metadata** (new A). ANSWERED by D-0585: a line is entered in the metadata table (the id, the other values missing) with a marker column named "not in metadata" (her "yes"; the name is the review session's suggestion).`

## BLOCK 2. REPLACE (item 12)
REPLACE `12. **One line to confirm**: her decision to allow no-panel deployments stands (new B).`
BY `12. **One line to confirm**: her decision to allow no-panel deployments stands (new B). CONFIRMED by D-0584 ("yes that was that").`

## BLOCK 3. REPLACE (status of the "reopens" row of the "changed by" table)
REPLACE `One line to confirm with her | TO CONFIRM |` BY `One line to confirm with her | CONFIRMED by D-0584 ("yes that was that") |`

## BLOCK 4. INSERT AFTER the line that begins `| "reopens one of my decision to allow deployements with no panel (static deployements)" |`
`| D-0573, the review session's reading confirmed by her "yes" (kept here): "There is NO marker "not in metadata" in her flow" (check X; the earlier note of the D-0573 section) | an id of a result file in no metadata is entered automatically as a line of the metadata table, the other values missing, with a marker column "not in metadata" | CHANGED by D-0585 |`

## BLOCK 5. INSERT AFTER the line that begins `2. **"The missing ids, 2 sided, are fed automatically": what is fed`
`   > **Answered by D-0585 (2026-11-23):** option (ii): a line is added to the metadata table with a marker. The earlier "no marker" is changed (see the table above). The lean of the text that follows is history.`

## BLOCK 6. INSERT AFTER the line `12. **One line to confirm**: her decision to allow no-panel deployments stands (new B). CONFIRMED by D-0584 ("yes that was that").` (the new sub-section, at the end of the section)

### Added 2026-11-23 (ledger D-0584, D-0585): her purpose; item 12 confirmed; item 1 answered

**Her words, exact.** "the line to confirm first - yes that was that. After my answer : we have done this mechansism so that the data can always use left joints to join with the metadata - limiting lineages problems. It would enter the id that must be added and the rest as missing values -> or I think there was a column that was added with the marker - so those type of missing values can be treated appropriately by the recipe maker. What is what you meant ?" [HER WORDS D-0584]. "1. yes because it cannot be done if the deployement is  static because there is no user to do the fix - the only fix can happen in there is a person surveilling the logs in the static deployements - this must be clear in the documentation. 2. yes" [HER WORDS D-0585]

**Decided in her words.**
- The decision to allow deployments with no panel stands: "yes that was that" [D-0584].
- **The purpose of the whole mechanism:** "so that the data can always use left joints to join with the metadata - limiting lineages problems" [D-0584].
- **An id of a result file that is in no metadata is entered:** the id, the rest as missing values, with a marker column "so those type of missing values can be treated appropriately by the recipe maker" [D-0584]. She answered "1. yes" to the review session's question whether this reverses the earlier "no marker" [D-0585]. The name "not in metadata" is the review session's suggestion; she answered "2. yes" [D-0585].
- **The reason, in her words:** a static deployment has no user to do the fix; "the only fix can happen in there is a person surveilling the logs"; "this must be clear in the documentation" [D-0585]. (The held documentation task D-0583 carries it: the guidelines say early that a static deployment needs a person who reads the log of the ids.)
- **Not in her words:** the identifier of the marker column; whether the recipe must state a meaning for this marker.

**What follows, by reading (no new derivation).**
1. **What a table that starts from the metadata shows for an added line:** one more entity, its metadata values empty (country, source, year), the marker set. A count per entity includes it; a plot by country shows an empty country. The demo tables that start from the metadata are `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit` and `QA_population_zscore` [ESTABLISHED: RECIPES, demo candidates]. On the demo no id is added (0 ids outside the metadata).
2. **With her purpose, those 4 joins would be written data first, metadata second, `left`.** A dry-run candidate of the one big move (D-0525), listed only, not applied. Whether this is a rule, an advice or documentation stays her question 12.
3. **The left join never loses a row only if both completions ran.** What still breaks it: a tier-1 filter that removes every line of an entity (on the demo, 6 entities of `Detailed_summary`); a metadata line with no usable id (it never matches); an id repeated in the metadata (rows multiply [ESTABLISHED: RECIPES G9, G13]); the same id written two ways in the two tables.
4. **A question for her: does the recipe need a stated meaning for "not in metadata", as it does for "not in original data"?** On `left_join_lesson`: 2 ids (`ACC0001`, `ACC0002`) of `sequenced` are in no metadata [ESTABLISHED: OVERLAP section 1]; the metadata (10 ids) gains 2 lines with empty values and the marker. With a required meaning the check asks the recipe to say what such lines are (for example "kept, shown as unknown", or "excluded"); without it they pass as entities with empty values and only the log says so. On the demo: none. Lean (Sonnet, as a lean): required, for the same reason as the first marker. [Opus lean]. Neither: say what you meant.

## BLOCK 7. INSERT AFTER the sub-section of block 6: the NEXT question (item 2, rewritten)
**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`). It can never be matched. With your purpose (data first, metadata second, `left`) it adds no row and is silently ignored; in a table that starts from the metadata all such lines make one entity with no id [POLARS SEMANTICS; ESTABLISHED: D-0570 fact 6]. The app shows the red warning and writes the lines in the log. Should the line (a) stay in the metadata table, the recipe removing it by a visible step as `demo_abromics` does (`demo_abromics.yaml:44-47`); (b) be removed by the app before the recipe reads, said in the warning and the log; (c) nothing? On the demo: none (42 distinct ids); `demo_abromics` as shipped has 3 lines (file lines 5, 6, 11): (a) a red warning "3 lines have no id", then its own step removes them (27 rows); (b) the app removes them first. Lean (Sonnet, as a lean): (a): the app changes no data without the recipe saying so. [Opus lean]. Neither: say what you meant.
