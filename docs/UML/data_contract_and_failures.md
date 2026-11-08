# How the app checks your data, and what happens when it does not match

Written for the person running an analysis, not for a developer. It answers the question a
scientist actually asks: "how do I know the plot in front of me is built from the data I think it
is, in the shape the recipe expects?" Backed by `REQ-VIZ-DATA-02` in `REQ-CORE`
(`.claude/design/uml_model_plan.md` section 3); see `quality_goals.md` section 3 for the sibling
goal about stale results. ADR-094 is the decision behind this page.

## The two different things "my data is wrong" can mean

1. **The recipe itself doesn't make sense.** A step list with a typo in an action name, a join
   that references a dataset that doesn't exist, a YAML file that doesn't parse. This has nothing
   to do with your actual data file — it would be wrong for any data.
2. **Your data doesn't match what the recipe expects.** The recipe says there should be a column
   called `sample_id`; your file has `Sample_ID`. The recipe expects a numeric `Year`; your file
   has text in that column. This is specific to the file you loaded today.

Both are checked by the same two functions everywhere in the app — but **HOME and BLUEPRINT use
them differently, on purpose**, because the two spaces have opposite jobs (ADR-094).

## HOME: automatic, before you ever see a broken recipe

HOME is where you run an already-built recipe. You likely did not write it, and in some
deployments there is no BLUEPRINT at all to fix it in. So HOME's check is not a button — it runs
by itself:

- Once, when the app starts (not per session, not per click), every recipe the app can find is
  checked: structure, then data-vs-contract.
- A recipe that fails either check **never appears in HOME's recipe selector** and can never be
  the one that opens automatically. It is simply not an option.
- The "Data analysis recipe Choice" panel in the left sidebar shows, beneath the selector, which
  recipes were left out and why — the problem, and who to contact about it.
- **The app never crashes because of a bad recipe.** Excluding it is not treated as a fatal
  error; everything that did pass the check works normally.

This is deliberately stricter than BLUEPRINT. You cannot "run anyway and see what happens" in
HOME — a recipe that fails the check is not run at all, not run with a warning.

## BLUEPRINT: manual, because errors are the normal state while building

BLUEPRINT is the IDE for building and editing recipes. While you are building one, it being
broken is expected, not exceptional — the whole point is to see what is wrong and fix it. So
BLUEPRINT's left sidebar has a **Validate** panel with a button, "Run validation", that you press
when you want to check. It runs the same two checks as HOME's automatic gate and shows one
combined result:

- **Recipe structure** (four rows: parse errors, invalid action names, invalid component names,
  join key violations).
- **Data vs contract** (one row, plus a detail card per problem).

A data-vs-contract problem shows you exactly where it is and, when the app can guess, what you
probably meant:

```
data_schemas.amr_results.output_fields.Sample_ID
declared column 'Sample_ID' matches no column of the dataset
Did you mean 'sample_id'?
```

**This check is still manual inside BLUEPRINT.** It runs only when you press the button — not
automatically on load or on data swap. That is correct for BLUEPRINT: you are iterating, and a
recipe is not finished yet.

## If a recipe fails and there is nobody to fix it

Some deployments have no BLUEPRINT at all (`blueprint_enabled: false` — a static or
exploration-only deployment). If the one recipe such a deployment names fails the check, a HOME
user genuinely cannot fix it themselves. For that case the rejection message names a contact,
resolved in two steps:

1. The recipe's own `info.contact` field, if the recipe author set one.
2. Otherwise the deployment's own `branding.contact` field.
3. If neither is set, nothing is shown — the app never invents a contact.

Contact resolution works even when the recipe is too badly broken to load normally — it reads
just the `id:`/`info:` part of the file directly, separately from the part that failed.

**This does not replace testing a deployment before release.** Catching a bad recipe during
deployment testing, before any user sees it, is still the first and better line of defense. This
gate is the second line, for drift after release — a data file that changes shape on disk, a
recipe hand-edited on the server after the fact.

## What happens if a recipe gets past both checks and still goes wrong while running

Passing the load gate does not mean nothing can go wrong — a file can disappear between the check
and the moment a plot actually renders, for instance. When that happens during an active HOME
session, the failure is now captured into the session's own "Pipeline Issues" log (visible in the
right sidebar) with what broke and which component it was, instead of only a plain red error on
the plot itself. This is a first, partial step — not every kind of runtime failure is covered yet
(see "What is still open" below).

## What the underlying engine does with a mismatched column, with no check at all

Worth knowing regardless of which check you rely on: what does the engine itself do with a
mismatched column name, with nothing checking at all?

- An `input_fields` slug that matches no real column in your TSV is **silently skipped** — no
  error, no warning, anywhere in the app. The wrangling step that referenced it simply does
  nothing.
- An `output_fields` slug that matches no column after Tier-1 wrangling is also silently dropped
  from the final table — this is the one case the data-vs-contract check exists specifically to
  catch, because nothing else ever will.

Neither of these stops the app or changes the plot's shape in an obviously wrong way — the rest of
the pipeline runs normally on whatever columns *did* match, and you get a plot. It can look
completely plausible while quietly missing or misusing the field you thought it was using. This is
why the data-vs-contract check matters more than it might first appear, and why HOME's gate runs
automatically rather than waiting for someone to remember to press a button.

## How this relates to reproducibility

Reproducibility (`quality_goals.md` section 2) guarantees that the *same* data and the *same*
recipe always give the *same* result — a cache-key match (ADR-089), a seeded random component
(ADR-090). It says nothing about whether that repeatable result is the one you meant to build.
The data-contract check is the other half: it is what tells you, before you trust the number,
whether the recipe actually read the column you think it read. Reproducible-but-wrong is still
wrong — the two checks exist for different failure modes and neither one covers the other.

## What is still open

- If literally every recipe in a deployment fails the gate, the app still stops with an error at
  startup rather than showing a polished empty state — a real, separate, larger piece of work for
  later. The common case this page describes — some recipes valid, some not — is fully safe today;
  this is about the rare, all-fail edge.
- Runtime capture ("What happens if a recipe gets past both checks" above) is wired for the most
  common path (a plot's underlying data failing to materialize) but not yet for every kind of
  mid-session failure (a plot component itself failing to render, a T3 audit-apply failing, an
  upload being rejected). Tracked as `PIPELINE-ERROR-WIRE-2`.
