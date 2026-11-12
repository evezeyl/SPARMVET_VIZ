# Attrition per step and the figure caption (proposal, 2026-11-12)

**Status: MINE, awaiting Eve (CONFIRM).** Replaces the options A/B for the caption count of a plot whose table has no key (review SC2).
**Evidence classes:** verified = run (`tmpAI/architect/attrition_demo.py`, real registered actions on the stored original stage); external = web search (standard mode, not read in full); reasoned.

## The problem
The caption says "n = 38 samples after exclusions". An aggregated plot (counts per country and year) has no key column in its table, and a later step can remove whole groups, so any single number can be wrong. Eve's idea: report **what each step changed, before and after**, instead of one absolute number.

## What the literature and tools do (external)
- **CONSORT** (reporting of randomised trials): a count at each stage and a reason for every drop-off; the reasons add up to the total; the number "analysed" can differ by outcome. (CASRAI summary and the CONSORT 2025 item 22 as quoted by the search result.)
- **Pipeline packages** (`cohortflow`, `selecta`, R): the counts are computed from the same pipeline that produces the analysed data, one row per step ("attrition table"), never typed by hand.
- **Order matters**: a 2022 Nature Communications reproducibility study is reported (search summary; paper not read) to have found that ambiguity in the order of inclusion and exclusion criteria changed the sample size by 26 %. So the order of steps must be recorded, which the audit already does.
- **Derived state** (event sourcing, from knowledge, not searched): store the ordered log of events and derive the numbers from it; nothing derived is stored as truth.

## Proposal
1. **Each step reports its own before and after**, in the unit of its node: entities by key (and rows) when the node has the key, otherwise rows or groups with the words "no key here", and always the **missing values removed**. The step's reason is its reason in the table, so before - removed = after (CONSORT).
2. **Derived, not stored.** The numbers are computed from the stored original stage plus the ordered step list, applying each step to the result of the steps before it. No "before" is kept; when a step is removed the later numbers are recomputed (verified below). Only the original stages (already cached) and the step list are stored. The report holds a snapshot; the import recomputes it to verify.
3. **Per plot:** the plot's flow is the steps that reach it in lineage order (T1, T2, T3 steps). The caption is composed of true statements from that flow: "n = 38 samples after exclusions (4 excluded, step 1; see audit trail)". For a plot without a key, the entity count is given up to the last node that has the key and the caption says so ("38 samples enter this figure, counted before the table is summarised; a later step removed 3 of 9 groups"). The word for the entity comes from the recipe.
4. **Reasoned consequence for stage 2:** an audit step at T1 is appended after the recipe's tier-1 steps, so audit T1 = the stored original T1 plus the steps, not a rebuild from the datasets. The exported forked recipe must give the same table when run from the raw data (the concordance test).

## Verified (real tables, real registered actions)
| Case | Result |
|---|---|
| Plot `QA_ST_with_NA`, step A removes 4 samples, step B `ST != ST10` | A: 42 -> 38 rows and entities. B: 38 -> 36, **all 2 removed rows had a missing value** (the silent drop of issue #63 becomes visible in the report) |
| Same plot with step A removed | B is recomputed: 42 -> 40, again 2 missing values. No stored number to refresh |
| Plot `QA_aggregated_no_key`, T1 step removes 4 samples | 42 -> 38 entities at T1. After the recipe's summarize: 9 groups, **no key column** |
| Same plot, T3 step `country != Norway` | 9 -> 6 groups; the recipe's own count column falls 38 -> 14, which the software cannot know (so the caption must not claim 38 after this step) |
