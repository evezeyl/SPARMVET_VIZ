# Opus checks `OVERLAP_AND_POPULATION.md` (v1)

**What I read.**
- The file.
- The ledger lines D-0568 (in full), D-0050, D-0543, D-0549, D-0564.
- The code at `app/modules/data_analysis_recipe_validator.py:485-545`, `app/src/bootloader.py:431-451` and `libs/utils/src/utils/recipe_check.py:337-348`.
- A search for `population` in `libs/*/src` and `app`, and for the `entity:` block in the recipes.

**My count.** One read-only count, registered first: RR13 in `RUN_REGISTER_opus_recipes.md`, output `opus3_rr13.out`. No engine and no build.

## 1. The overlap table: my count AGREES, number for number

- **How I read it.** I used the recipe's own declarations: the declared entity field and its `original_name`, the `source.path`, `strip` and `null_values`.
- **The metadata:** 42 rows, 42 ids, no null.
- **The ten tables that declare the entity id:** 0 ids outside the metadata, raw, stripped and lower-cased alike.
- **Metadata ids with no line in the file:** 4 of 42 in ResFinder (70 rows, 38 ids), 0 in the others.
- **Rows:** Detailed_summary 280, VirulenceFinder 1315, the others 42. APEC declares no id. [Opus RR13]

So the right column and the right file were read, with the recipe's strip and null rules.

The other recipes I did not count; I accept them as the Sonnet agent's read only, tagged so.

## 2. The data check, as read from the code

**The facts are true.**
- The data check builds each table on its own and reports per dataset; it compares no two tables [CODE READ `data_analysis_recipe_validator.py:485-545`].
- The HOME gate runs the structure check, then the data check. Any problem from either rejects the recipe. Advices come only from `checker_advices`, which reads no data [CODE READ `bootloader.py:431-451`].
- So "inform without refusing" for a data finding needs a new channel.

**The options are fair, with three things missing (O1, O2).**

- **O1.** Add to option (a): "Under (a), your second remedy cannot be used. A refused recipe does not open in HOME, so no audit step can delete the ids ("OR delete the id where there is no metadata in the respective parent tables via audit", D-0568). (a) also refuses, at its next opening, a recipe whose metadata is replaced later by an incomplete file." Reason (D-0532): she named two remedies, and (a) removes one of them.
- **O2.** Quote where they bear:
  - At (b) and (c): "No silent error that is the rule." [D-0050]; her own "an inner join would hide this" [D-0568].
  - At the lean: "Our job is to try to give as clear information as possible - so the user has elements it needs to be able to make a good decision" [D-0543].

## 3. The population

**The facts are true.**
- `entity.population` is read only by the check (E01, E02) [CODE READ `recipe_check.py:337-348`].
- No other code reads it: the one other hit of the word `population` is a statistics tip in `polars_aggregations.py:58`.
- No demo recipe declares an `entity` block. The only recipe that declares one is `templates/left_join_lesson.yaml`. [search]

**The reasoning: AGREE.** A table of the analysed entities as the base of the per-entity join:
- gives zeros that mean "analysed, zero hits";
- keeps the never-analysed entities of the metadata out;
- starts the join from a data table, with the metadata second, and needs no new key;
- still leaves the false zero at the data table's own place (1 of 3 paths covered).

What is missing:

- **O3.** Her words exact: in section 3, replace "Her words "the join should not start with the metadata" are then followed to the letter" with "Her words "the join should not start with the medata" [D-0564] are then followed to the letter".
- **O4. Where it fits in the catalogue.** The addendum's (c2) mixes two things:
  - the base of the join is a table of the analysed entities: this works today, with no new key;
  - a completion read from the declared population: this does not exist.
  Name the first "(a2) a table of the analysed entities as the base (candidate (a) with the table of (f2) as its base; the `entity` block optional, and only checked)". Keep the second inside (c): "(c) with the declared population as its source".
- **O5. "Analysed" is relative to one analysis.** Add to section 3, "What it needs": "The population must list the entities that THIS analysis ran on. A read-quality table such as `FastP` lists the sequenced entities; an AMR run can fail for a sequenced entity, and its 0 would then mean "not analysed" again. The right table is a manifest of the analysis, or one of its own result files with one row per analysed entity." [REASONED]
- **O6. The retest.** Add to retest 1 the "Expected": "The demo cannot show the gain: every metadata id is in `FastP`, `Quast` and `Summary` (42 of 42). The scratch copy needs one entity in the metadata that was never analysed. Expected: with (a2) it is absent; with A it shows 0." [Opus RR13; REASONED]

**O7, a consequence for the committed `CAUSE_AND_SOLUTIONS_ZEROS.md`** (to be applied when the addendum goes in, D-0532: not softened). Its sentences "So in every form with zeros the metadata is the side whose rows stay" (half page) and "So in every form with zeros (A, B, C, E) the metadata is the kept side ... Only D follows your direction fully, and D has no zeros" (the question) are no longer true once (a2) is a candidate. Replace them with:

"In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros."

## 4. The half page and the wording

- Her words in the half page are exact: "the metadata is supposed to cover all the ids of the result files" and "yes the app check could be good - to identify those that have no metadata - good idea" [D-0568].
- The one inexact quotation (D-0564) is O3.
- Leans are marked as leans.
- No cost, effort or delay argument.
- Nothing is decided for her.

## 5. Closing line

**I agree with `OVERLAP_AND_POPULATION.md` with these 7 replacements, O1 to O7:**
- O1: option (a) blocks her second remedy.
- O2: D-0050 and D-0543 quoted where they bear.
- O3: D-0564 exact.
- O4: (a2) and (c) named apart.
- O5: "analysed" is relative to one analysis.
- O6: the retest needs a never-analysed entity.
- O7: the sentence of the committed cause file on "every form with zeros".

Open between us: nothing, if the Sonnet agent accepts them. O7 changes the committed `CAUSE_AND_SOLUTIONS_ZEROS.md`, so it needs the coordinator's go.
