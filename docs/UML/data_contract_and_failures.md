# How the app checks your data, and what happens when it does not match

Written for the person running an analysis, not for a developer. It answers the question a
scientist actually asks: "how do I know the plot in front of me is built from the data I think it
is, in the shape the recipe expects?" Backed by `REQ-VIZ-DATA-02` in `REQ-CORE`
(`.claude/design/uml_model_plan.md` section 3); see `quality_goals.md` section 3 for the sibling
goal about stale results.

## The two different things "my data is wrong" can mean

1. **The recipe itself doesn't make sense.** A step list with a typo in an action name, a join
   that references a dataset that doesn't exist, a YAML file that doesn't parse. This has nothing
   to do with your actual data file — it would be wrong for any data.
2. **Your data doesn't match what the recipe expects.** The recipe says there should be a column
   called `sample_id`; your file has `Sample_ID`. The recipe expects a numeric `Year`; your file
   has text in that column. This is specific to the file you loaded today.

These need two different checks, and until 2026-11-08 only the first one actually ran anywhere in
the app.

## Where to run the check

BLUEPRINT's left sidebar has a **Validate** panel with one button, "Run validation". Click it with
a data analysis recipe loaded. It runs both checks and shows one combined result:

- **Recipe structure** (four rows: parse errors, invalid action names, invalid component names,
  join key violations) — always ran.
- **Data vs contract** (one row, plus a detail card per problem) — wired in 2026-11-08.

A data-vs-contract problem shows you exactly where it is and, when the app can guess, what you
probably meant:

```
data_schemas.amr_results.output_fields.Sample_ID
declared column 'Sample_ID' matches no column of the dataset
Did you mean 'sample_id'?
```

## What you must know before trusting a result

**This check is not automatic.** It runs only when you press the button. Loading a data analysis
recipe, uploading data, or running an analysis in HOME does **not** trigger it. If you never click
Validate, a mismatched column can still slip through silently — see the next section for exactly
what "silently" means.

**Run it after every data swap, not just once.** The check reads the file that is currently
assigned to each dataset. If you replace the underlying TSV without re-running Validate, the old
result stays unchecked.

## What happens if you skip the check and a column is wrong

This is the part worth knowing even if you always remember to click Validate: what does the engine
itself do with a mismatched column name, with no check running at all?

- An `input_fields` slug that matches no real column in your TSV is **silently skipped** — no
  error, no warning, anywhere in the app. The wrangling step that referenced it simply does
  nothing.
- An `output_fields` slug that matches no column after Tier-1 wrangling is also silently dropped
  from the final table — this is the one case the data-vs-contract check exists specifically to
  catch, because nothing else ever will.

Neither of these stops the app or changes the plot's shape in an obviously wrong way — the rest of
the pipeline runs normally on whatever columns *did* match, and you get a plot. It can look
completely plausible while quietly missing or misusing the field you thought it was using. This is
why the data-vs-contract check matters more than it might first appear: it is the only thing
standing between a renamed column and a published figure built on the wrong data.

## How this relates to reproducibility

Reproducibility (`quality_goals.md` section 2) guarantees that the *same* data and the *same*
recipe always give the *same* result — a cache-key match (ADR-089), a seeded random component
(ADR-090). It says nothing about whether that repeatable result is the one you meant to build.
The data-contract check is the other half: it is what tells you, before you trust the number,
whether the recipe actually read the column you think it read. Reproducible-but-wrong is still
wrong — the two checks exist for different failure modes and neither one covers the other.

## What is still open

- The check is manual, not automatic. Auto-running it on every data analysis recipe load or data
  upload was considered and deliberately left out of the 2026-11-08 fix: the recipe-structure half
  runs as a subprocess and can take up to 30 seconds, so firing it on every upload would make the
  app feel slow. If this becomes a real problem in practice, it is a separate, smaller follow-up —
  not a reason to distrust the check that exists today.
- There is no equivalent check inside HOME itself (only in BLUEPRINT) — a HOME user who did not
  build the recipe has no button of their own to confirm the data matches. Today the expectation
  is that whoever builds or imports a recipe in BLUEPRINT validates it before handing it to a HOME
  user; there is no enforcement of that handoff.
