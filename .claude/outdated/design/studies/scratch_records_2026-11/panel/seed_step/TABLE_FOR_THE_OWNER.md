# A reshuffle as an audit step: where the seed is written, and how the app knows a plot can be reshuffled

For the owner. Written by the coordinator, 2026-11-20, from a read of the code on dev and one round of two viewpoints (architect with the developer's view, data scientist), with small checks RAN. Facts and the question: `QUESTION_and_FACTS.md` in this folder. Not critical now (her words); nothing is built. She decides.

Decided already: Reshuffle is offered only in Audit mode (D-0341); a seed fixed in the recipe holds (D-0052); every seed that is used is written in the recipe or the audit recipe (D-0056); in an audit recipe the author's part is never touched and the audit's part sits beside it (D-0332).

## Flag first: what is wrong or silent today
1. **The export writes the chosen seed INTO the author's layer** of the copied recipe. With the audit recipe as the recipe of an audit export, that breaks "the copy minus what the audit added equals the original" (tried: the integrity check reports it). It cannot stay.
2. **A reshuffle leaves no real trace of the choice.** A click stores a pinned number in the session: no reason of the user, no date, not an audit step; the export invents a reason text. Choosing the arrangement that looks best is a choice a reader should see.
3. **An audit pin beats a seed the author wrote.** Only the button hides itself when the author wrote a seed; a pin that is already stored would still win over the author's number. Against her rule that a seed fixed in the recipe holds. The check must refuse an audit seed on a plot whose layer has the author's seed.
4. **A seed changes the picture and no table.** The list of affected plots ("table changed" / "picture changed", decided) would say "the same" for a plot whose only change is the seed, unless the seed is counted for the picture. Tests would not catch it.
5. The pin applies to every random layer of the plot, also to a layer added later; the figure does not say so.

## Where the audited seed is written
| | Way | For | Against |
|---|---|---|---|
| W1 | Into the author's layer (as the export does today) | The recipe alone gives the picture. | Changes the author's part (flag 1); erases a seed the author wrote. Both viewpoints: reject. |
| W2 | **A place of its own on the plot, beside the author's layers**, in the same spirit as `audit_steps` beside `steps`: for example `audit_seed: {id: audit_..., seed: N, audit_comment: "..."}` | The author's layers are never touched. Removing it gives the original back, so the equality check works. The drawing already prefers an audit pin, so a rerun from the bundle gives the same picture. It enters no key of a stored table (a seed changes no table). "Remove step" removes it like any audit step. | A second kind of audit addition beside the lists of steps: the functions that list, strip and remove audit additions must cover it; one more key in the format, for audit recipes only. |
| W3 | As an item of the plot's tier 3 `audit_steps` | One list for everything the audit adds to a plot. | Wrong place: the items of that list run through the data engine and enter the key of the plot's table; a seed there would rebuild the table and say "table changed" although no row changed. And an audit step is only a filter or a drop (decided). Both viewpoints: reject. |
| W4 | Only in the audit record, not in the recipe | Nothing new in the recipe. | The audit recipe alone would not give the picture; against "the audit recipe is the truth of an audit export". Reject. |

## How the app knows "this plot can be reshuffled"
| | Way | For | Against |
|---|---|---|---|
| K1 | **As today: one list in the shared library**, proven by the test that draws every component twice | One place. Already right, and proven by a test. Whether a layer is random depends also on its arguments (a jitter position inside another layer; a bootstrap summary), which a function can judge and a yes/no field cannot. | The list is kept by hand (the test catches a missing one). |
| K2 | A field on the registration of each plot component ("random", with the name of its seed argument); the UI and the check read the field | Declared where the component is declared; her idea. Blueprint could show "this component takes a seed" from it. | A yes/no field cannot express "random only with these arguments"; it would need a small grammar of conditions. The shared library cannot import the plot library, so the list must be handed over. |
| K3 | Both: the field is declared, the test proves the field against the drawing | Declared and proven. | Two places to keep in step. |
- For table actions the mechanism she describes exists already: the registration of the rank action carries a readable rule "when the method is random, a seed is required", and the sample action requires a seed. An audit step cannot be one of these (only filters and drops), so nothing is needed there now.
- Architect: K1. Scientist: K3. Both: W2.

## The flow "try, then keep" (both viewpoints agree)
- A reshuffle that is TRIED is not in the audit recipe: the tried number stays in the session, as today.
- When she is happy she KEEPS it: that writes the audit seed with HER reason (the same dialog as any audit step), the date and initials in the log.
- "Remove step" takes it away; the plot returns to the recipe's arrangement.
- The report says it in words, for example: "The arrangement of the points was chosen in the audit (seed N; the recipe's arrangement uses seed 0)", and Compare shows the original beside it.
- One seed per plot, said to apply to all its random layers (a seed per layer adds choices nobody can defend, and an index of a layer is fragile).

## Recommendation of the coordinator
**W2 and K1 now; the registration field (K3) when Blueprint wants to show "this component takes a seed".**
- W2 is her own sentence: the right place is not the audit steps after the original recipe, it is the plot.
- K1 already does what she asks ("the reshuffle option appears when it is possible based on the recipe"): the button appears only for a plot with a random layer and no seed written by the author. A field would add a second place for the same fact, and it cannot say "random only with these arguments".
- To build with it, whatever she chooses: the export stops writing into the author's layer; the check refuses an audit seed where the author wrote one; a seed counts as "picture changed, table the same".

## Points that are hers
1. W1, W2, W3 or W4; and the name of the key if W2 (`audit_seed`).
2. K1, K2 or K3.
3. May the audit change a seed the AUTHOR wrote on a layer? (Decided rule says it holds; then the button is absent and a line says "the recipe fixes the arrangement of this plot".) And does a seed written once for the whole recipe (`plot_defaults`) count as "written by the author"? Today it does: no button.
4. One seed per plot (my view), or one per random layer.
5. A second "keep" on the same plot: it replaces the first (one audit seed per plot; the log keeps both), or it is refused until the first is removed.
6. Whether the number of tries is shown or recorded (the scientist suggests showing it, because it reveals choosing by eye; my view: not now).
7. A note on the figure's line in the report when the jittered axis is numeric (jitter then moves the values a reader sees).

## Records to correct with this (need her yes: a rule file)
- `.claude/rules/rules_viz_factory.md` section 8 says "`random_state: null` gives a different arrangement on every render"; the code refuses it (a seed is a number), as she decided on 2026-11-15.
- The task SEED-HOLDS-1 is marked open; the code has it built (a scribe can mark it once a reviewer has confirmed).
