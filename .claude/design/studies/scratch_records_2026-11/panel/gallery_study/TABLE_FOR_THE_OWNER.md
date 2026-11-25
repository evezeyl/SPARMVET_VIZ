# The study of the Gallery: one table for the owner (coordinator, 2026-11-20 night)

## READ THIS FIRST: recheck against the code, 2026-11-21 morning (a scout read `dev`; nothing was run)

Q1 is DECIDED by the owner on 2026-11-21: options B and C together (the 13 names take the words of the headings; the headings become real descriptions; one line in the list; no line above the heading). Q2 is DECIDED by the owner on 2026-11-21 (D-0398): the geom filter lists all geom and stat layers of an example; a new typed axis 'Chart type' in plain words with several values per example. Q3 is DECIDED by the owner on 2026-11-21 (D-0399): the recipe spec holds the words and their meanings; the cheatsheet and the documentation are generated from it. Q4 is DECIDED by the owner on 2026-11-21 (D-0400): option A, a key of recipe, data and the plotnine version kept with each picture (a stale picture shown in the existing notice; the redraw automation is a low-priority task after the Gallery work). Q5 is DECIDED by the owner on 2026-11-21 (D-0401): all 34 examples are verified critically by the data scientist, the statistician and a user new to data science; corrections follow her reading. Q6 is DECIDED by the owner on 2026-11-21 (D-0402): three typed tags (data pattern, sample size, difficulty) are checked against the recipe and the data. Q7 is DECIDED by the owner on 2026-11-21 (D-0404): the meaning of each filter term is shown on hover or click of a small mark, from the spec, and in the documentation. Q9 is DECIDED by the owner on 2026-11-21 (D-0405): info.label and the plot's ui_label may differ; no check enforces equality. Q8 is STILL OPEN: it is answered by the table of the purpose of each name field, which she ordered. Three things the study says are no longer true, because they were built in the evening of 2026-11-20:
- The Gallery's "silent stale list" (flag 3 below) is gone: at start the app rebuilds the list of examples and rewrites it when a name, a tag or the presence of a picture changed (`libs/viz_gallery/src/viz_gallery/gallery_manager.py:187-214`). What remains: a CHANGED picture is not noticed (question Q4).
- The name of a Gallery example comes only from the plot's `ui_label` (`taxonomy.py:55-66`), as you decided.
- Two Gallery examples with the same name or plot id: the later one is left out with a reason (`gallery_manager.py:105-118`). This rule is PROVISIONAL, not yours. Today no two of the 34 examples have the same name, so "two examples with the same name" is no longer an open point.

Facts to keep in mind when you answer:
- Q1: the name is the plot's `ui_label`; the heading is the first line of `example_meta.md`; 13 of them differ and no code compares them.
- Q2: the "primary geom" is the first geom or stat layer written; the checker does not verify it.
- Q3: the code reads the allowed tag values from `libs/utils/src/utils/recipe_spec.yaml:189-205`. The cheatsheet file is read by nothing.
- Q4: a tool that redraws and compares the pictures exists (`assets/scripts/gallery_previews.py`), run by hand; the check at start does not compare pictures.
- Q6: today a tag is checked only as a word of the list.
- Q8: `info.label` is required; advice on a missing contact is not shown in the Gallery; `submission_date` is written and never read.
- Q9: the code does not compare `info.label` with `ui_label`.
- The data sample of an example is now built by the same code as its picture.
- Not checked in this recheck: the content of the examples and texts (Q5), the counts "11 of 34" and "all 34", and which three links have no page (that needs the network).

Her order: D-0388. Sources: `MAP_part1.md`, `MAP_part2.md` (scout; 26 gaps B1 to B26), `architect.md` (ran checks: 34 recipes load, index equals a rebuild, all 34 pictures identical to a fresh drawing; reproduced the stale index), `scientist.md` (read all 34 mappings, layers, column types and data; `sci/dump.txt`), `user.md`. Nothing is built or changed. The panel recommends; she decides. Still to do of her order: the UML of the Gallery (part b), the status notes of ADR-037/061/063 (part e, after her choices).

## Flagged first
1. Three examples teach something wrong (content, user space GALLERY): `heatmap_correlation` is not a correlation matrix (diagonal not 1, A-B differs from B-A); `tile_simple` draws 100 rows into 16 tiles without aggregation (one raw value shown per tile); `dumbbell` shows a continuous colour bar of years 2015 to 2023 for two years.
2. The tags are not reliable: sample size against the cheatsheet's own numbers (10 or 15 per group tagged medium+; 60 rows tagged large); the data pattern in at least 7 examples; the family differs for the same kind of plot; "proportion" on two plots that draw counts; difficulty against the cheatsheet's rule in 4; `ridgeline_advanced` is a faceted density.
3. A stale list is silent (reproduced): after a name or a taxonomy value of an example changes, the check at start answers "unchanged" and the old list stays until a script is run by hand.
4. Nothing proves a picture belongs to its recipe: today all 34 are identical to a fresh drawing (run twice), but no stamp of recipe and data is kept; a picture out of date would not be noticed.
5. Guidance texts hold pasted sentences that are wrong for their example, and slang that says nothing ("Gourmet", "Staple").

## Defects that follow from what is already decided (can be built without a new decision)
| # | What (GALLERY) | Fix proposed | Decision behind it |
|---|---|---|---|
| F1 | The name is read from `info.label` | Read the plot entry's `ui_label` in one function, no fallback | D-0387 |
| F2 | The stale list | The check at start compares the whole index and rewrites it on any difference (0.76 s for 34 examples, already run at every start) | ADR-037 kept; rule section 5 |
| F3 | Two examples may carry the same name or plot id unnoticed | Run the existing set check on the examples; the later one is left out with its reason | D-0039 (standard recipes, checked) |
| F4 | The data sample tab reads the file by another path than the picture | Read it through the same function | one source |
| F5 | Rule file, README, docs, design page out of date (B3, B4, B7 to B14, B17, B19 to B23) | Texts corrected from the code | D-0350 (texts follow the ledger and the code) |
| F6 | Mapped columns are not checked against the data file | The Gallery check reads the file's header | the load gate does it for HOME |

## Her decisions
| # | Question | Options | Recommendation |
|---|---|---|---|
| Q1 | The 13 headings that differ from the name (list in `MAP_part1.md`; e.g. "Bar Simple" / "Bar Chart") | A keep both as they are; B keep the headings, change the 13 names to the better words; C keep the names, make each heading a real description ("Bar Chart: compare counts across categories"); D show the name in a small line above the heading; (generating the heading from the name is excluded by her words) | User: C, possibly with D. Architect: D (name shown above, heading free) or equal by a check. Coordinator: D now (no text to write, nothing looks like a mistake), C when the texts are revised (Q5) |
| Q2 | The primary geom of an example with several geoms (11 of 34): today "the first written" | A keep the first, and say so; B derive all geoms and file the example under each (keeps "derived"); C the author names the primary geom and the check verifies it is a layer (reverses "derived", D-0034/D-0039: flagged) | Scientist: B or C. Architect: A (B and C reopen decided points). Coordinator: B (a user who filters on boxplot finds the violin-with-boxplot; still derived) |
| Q3 | Where the allowed taxonomy values and their meanings live | A the recipe spec holds values and meanings, the cheatsheet is generated from it and a test keeps it equal; B two files kept equal by a test; C as today | All: A |
| Q4 | Proof that a picture is current | A a stamp of recipe and data kept with the picture, compared at start, "picture out of date" shown in the existing notice; B a test that redraws all 34 and compares; C draw at start (reconsiders ADR-037/ADR-093: flagged) | Architect and scientist: A plus B |
| Q5 | The content of the examples (flags 1, 2, 5) | A correct the three wrong examples now, revise tags and texts in a second pass; B all in one pass; C leave for later and avoid them in the demo | Coordinator: A; for the demo a list of sound examples |
| Q6 | Which tags a check verifies | Checkable: the pattern against mapping and column types (needs a written counting rule; no value exists for count-only plots or dates), the sample size against the rows (per group), the number of geoms against the difficulty rule. Author's judgement: family, what it shows, the guidance text | Scientist: check the three checkable ones; she confirms the counting rules when proposed |
| Q7 | The filter panel explains its terms | One short line under each filter heading (sample size in numbers, "change", "faceted", "matrix", what the primary geom is) | User: yes |
| Q8 | `info` in a Gallery recipe (nothing of it is shown; `submission_date` unread; the advice on the missing contact fires on all 34 and is never seen) | say in the spec what `info` is for in an example; show or drop the advice | to propose with the spec text |
| Q9 | Must `info.label` equal the plot's `ui_label` in an example | free; an error; an advice | Architect: her choice; coordinator: an advice |

## Recipe rules the Gallery lacks (part d), to add to the recipe spec after her choices
The first-layer (or all-layers) rule for the geom; the counting rule of the data pattern and the missing values (count-only, date); sample size per group; one plot per example (clear today); the name (`ui_label`) and what `info` is for; the heading must exist; duplicate names refused; the picture's stamp; the group is only a container. The new ADR "Gallery examples are recipes" announced in the spec was never written: it is the place to record this, with status notes on ADR-037, 061, 063.

## Not verified
The screen (no viewpoint ran the app); all guidance texts against their plots (3 read in part); fonts on another machine for the picture comparison; whether taxonomy terms were renamed in the refactor (the terms of cheatsheet and spec are equal today in both directions).
