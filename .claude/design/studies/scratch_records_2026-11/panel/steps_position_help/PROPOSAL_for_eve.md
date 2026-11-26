# Where an audit step goes in a stage, and help in the audit dialog

Written 2026-11-16 by the coordinator from three viewpoints (data scientist, architect, user). This is a proposal. Nothing is decided and nothing is built. These are the two questions left open from your correction of the intent document (its open points on the position of an audit step and on a help button).

## Question A. Can an audit step go between the recipe's steps, or at the beginning of a stage?

Decided for now (your words, 2026-11-16): "the audit steps can be added at the end of each T1 - T2 - T3 (for now)".

### What would change a result silently

The position inside a stage changes the result in three cases:
- **A value computed from the other rows** (a z-score, an average, a count, a rank). A sample removed at the end of the stage leaves the values of the other samples computed WITH it. In the run on recipe 1 the z-scores of all 14 remaining samples differ (by up to 0.57) from what they would be if the sample had been removed before.
- **A deduplication that keeps the first row.** Which row survives can differ.
- **A recoded value.** The value the user sees at the end does not exist before the recode; a step placed before it would remove nothing.

Where the recipe leaves the column unchanged, the position does not matter: the rows are the same.

### The options

| Option | For | Against | Viewpoints |
|---|---|---|---|
| 1. At the end only, plus one sentence when the position matters | The user removes what the user sees. One place per stage, so the dialog stays short. The way to act earlier already exists: select at T1 instead of T2 ("as early as possible in the lineage", your decision D-0197). | A removal before a z-score INSIDE the same stage cannot be expressed. | All three recommend it. |
| 2. Also at the beginning of a stage | "Remove before the recipe's steps of this stage." | The step would act on a table the user is not looking at: the 28-against-21 confusion again, inside one stage. The beginning of T2 is the same as the end of T1, so it is a second way to do one thing. | Nobody. |
| 3. Between two named steps | Full control. | The user would have to see the table after each step; that view does not exist. The recipe's steps have no name, so a later change of the recipe shifts the position silently. Large build; the way stored tables are named would change. | Nobody for now. |
| 4. The recipe author splits the list | An author who wants a place for an audit step before a calculation puts the calculation in the next stage (the two lists of a table already exist). Nothing new to build. | It is the author's work, not the user's. | Architect: this already works today. |

### The sentence the user viewpoint proposes

Shown only when the stage has a step that computes across samples (an average, a z-score, a rank):

"Your removal comes after the recipe's calculations. Values such as averages or z-scores of the other samples were computed with these samples. Suggestion: to recompute them without these samples, tick the first table instead."

### One thing found on the way

The recipe checker does not check that an audit step is at the end of its list. A hand-edited audit recipe with an audit step in the middle passes today. Suggestion: the checker refuses it, so that "at the end" is a rule the app enforces and not only a habit.

### Recommendation (the coordinator's, not a decision)

Option 1, with the sentence, and the checker rule. Option 4 is the answer for a recipe author who needs an earlier place. Options 2 and 3 only if use shows a real need.

## Question B. A help button in the audit dialog?

Your words: "Investigate if maybe a little additional help button could help the user get more information while doing audit or if the general help is sufficient."

### What exists today

- A help window per workspace shows a text file. The audit dialog is itself a window of that kind: opening the help window from it would close the dialog and lose the step in progress.
- The help text of HOME and the user guide still describe the OLD audit ("Send to Audit", "propagation"). No test keeps a help text true.
- Small pop-up notes beside a control exist and can be reused.

### The options

| Option | For | Against | Viewpoints |
|---|---|---|---|
| 1. One line always visible at the top of the dialog | The user has it at the moment of deciding, with no click. | It must stay one sentence, or it becomes noise. | User: yes, this one. Scientist: the facts of the moment belong in the dialog, not behind a button. |
| 2. A small "?" that opens a short text in place (a pop-up note, not a second window) | Room for the six-line box and the examples. About 20 lines of code. | The user viewpoint: "I would not click it"; what must be seen should not be hidden. | Architect: yes, as an addition. |
| 3. A link to the user guide | Smallest. | It leaves the dialog; the guide is not always built; it lands on old text today. | Nobody. |

All three agree on what belongs where:
- **In the dialog, each shown only when it applies** (your rule: warn only when there is a problem): the count at each place when it differs from the view (28 against 21); the places that keep the samples; "n samples not shown in this plot"; two values that become one; a removed sample that shows as 0 elsewhere.
- **In the general help and the user guide:** the sentence "the place you tick is what you mean", the two examples, "select as early as possible".

The architect adds: one text file is the source for the dialog, the pop-up note and the guide; each claim in it names the test that proves it, and a test fails when a claim has no test. The numbers of the example (28 and 21) stay in the guide; the dialog text must be true for any recipe.

### Recommendation (the coordinator's, not a decision)

Option 1 (one sentence, always visible) plus option 2 (a "?" for the longer text), both read from one file; the facts of the moment as conditional lines in the dialog. The old help text of HOME is corrected when the dialog is built.

## What you are asked

1. An audit step stays at the end of its stage, with the sentence when the stage computes across samples?
2. The checker refuses an audit step that is not at the end of its list?
3. Help: one sentence always visible, plus a "?" for the longer text?

The draft of the help text is in `tmpAI/panel/audit_docs/intent_text_draft.md`.

Not checked: the claim about deduplication is reasoned, not run. The time to compute a table after a step in the middle was not measured.
