# Proposal: the texts of a plot layer that plotnine evaluates (PLOT-TEXT-RUNS-CODE-1, 2026-11-16)

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Source decision: the one already taken (Eve 2026-11-13 and 2026-11-15; FORMULA-SAFETY-1; ADR-099 point 14; recipe format spec section 15): a text of a recipe must not be able to run code. Built in this task: check PS06, `libs/utils/src/utils/plot_text_check.py`. Evidence: `decisions_2026-11-14/evidence/plot_text_code_execution_2026-11-16.md`.
No rule file states anything that is now false. The one change proposed is an addition, so that an agent that writes plot specs knows the rule.

## 1. `rules_viz_factory.md`: one bullet (in the list of the replaced section 1 of `rules_viz_factory.md.proposal.md`, after "No silent path")

Old line: (none; the bullet does not exist)

New line:
```
- **A text of a layer is data, never code (PS06).** plotnine evaluates three kinds of text a layer can hold: the `formula` of a smoother, a facet variable that is not a column, and the function string of `stat_function`. The recipe checker (PS06) and the factory read each as syntax and refuse what is outside the allowed form: a smoother formula over `x` and `y` with numbers, model-formula operators, `I`, `C`, `bs`, `cr`, `cc`, `te`, `center`, `standardize`, `scale` and the math names of `MATH_FUNCTIONS`; a facet variable that is a column of the data; a math lambda. A new component that takes such a text must be added to `utils/plot_text_check.py` with a test. A computed facet is made first by a recipe step.
```
Why: the rule exists in the spec (section 15) and in the code; the agents' rule file should say it. Source: Eve's decision above.

## 2. `rules_agent_role_bioscientist.md`, section 3-C (plot specs): one line after "`position` and `labels` as flat keys are NOT supported."

Old line: (none)

New line:
```
A smoother `formula` is a model formula over `x` and `y` (`y ~ x + I(x**2)`, `y ~ np.log(x)`); a facet is the name of a column. Anything else is refused by check PS06; make a computed value with a recipe step (`polars_with_columns`) first.
```
Why: so that a recipe is not written with an expression that the checker will refuse. Source: same.

## Row text for `RULE_FILE_CHANGES.md` (to be numbered, e.g. R129 and R130)

| R129 | rules_viz_factory.md | (new bullet, section 1 as proposed) | (none) | "A text of a layer is data, never code (PS06)": the allowed forms of a smoother formula, a facet variable, a function string | A plot text that plotnine evaluates could run code (found 2026-11-16); the check is built. | proposal file plot_text_safety.proposal.md, change 1 | proposed |
| R130 | rules_agent_role_bioscientist.md | section 3-C, after the `position`/`labels` line | (none) | one line: a smoother formula over `x` and `y`; a facet is a column name; PS06 | Same. | proposal file plot_text_safety.proposal.md, change 2 | proposed |
