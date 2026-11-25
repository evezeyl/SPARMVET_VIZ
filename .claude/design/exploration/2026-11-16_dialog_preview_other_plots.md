Exploration report. Nothing in it is decided unless a ledger number is given. Status: Nothing is decided and nothing is built (as written in the report). Written: 2026-11-16. Source: .claude/design/studies/scratch_records_2026-11/panel/dialog_preview/PROPOSAL_for_eve.md. Copied here on 2026-11-17.

Paths inside the body that point to tmpAI/ working files are local (not in git) and stay as written.

---

# Can the user check the other plots and tables while the audit dialog is open?

Written 2026-11-16 by the coordinator from three viewpoints (data scientist, architect, user). This is a proposal. Nothing is decided and nothing is built. Your question is in message M185 of the channel.

The facts and the measured times are in `.claude/design/studies/scratch_records_2026-11/panel/dialog_preview/facts_and_times.md`.

## The short answer

Yes, for three of the five things "check the other plots and tables" can mean, inside the dialog you already decided (a window with Apply and Cancel, one candidate step, nothing saved before Apply). One of the five would change what you decided, and all three viewpoints say: not now.

## The times, measured on recipe 1 (in brackets: with ten times the rows)

| What | Time |
|---|---|
| The candidate step computed at all the places that can take it | about 2 s (3 s) |
| The counts of rows and samples at all 73 places, once that is done | 0.01 s |
| The first 100 rows of the table at one place | under 0.1 s |
| One plot drawn | 0.2 s for a small one; 3 s for the slowest (30 s) |
| All 17 plots, before and after | about 16 s (65 s) |

Counts and tables are cheap at any size. Drawing plots is what costs. While a plot is drawn the app waits, so a slow plot freezes the screen for that time.

One recipe was measured, on a machine that was doing other work.

## The five meanings

| What the user could do | Decided already? | Cost | Risk | Viewpoints |
|---|---|---|---|---|
| 1. See, for each place, the rows and the samples before and after | Yes (counts before and after along the lineage) | 2 to 3 s when the dialog opens or a tick changes | Low | All three: needed. But a count alone ("42 to 21") says how many, not which. |
| 2. Click a place and see its table, before and after | Written only for a removed column, not for a row filter | Under 0.1 s per click | Medium: it looks like the data table of HOME | All three: yes, cheap and useful. Show the rows that WOULD BE REMOVED, not the first 100 rows, which can hide them. |
| 3. See a plot before and after | The open plot: yes. Other plots: nothing written | 0.2 to 3 s per plot (30 s on large data) | Medium to high: it looks like the saved figure | Scientist: wait for the other plots. Architect and user: one plot at a time, on a click, never all at once. |
| 4. Leave the dialog open and walk through HOME, which shows "what it would look like" | No. It contradicts four written sentences: the dialog is a window that blocks; "the plots change only at Apply"; two views, not three | Each view its own time; a large change in HOME's code | The highest: two versions of one plot on screen; a candidate taken for a saved result | All three: not now. |
| 5. See the recipe as a picture with the places marked | The picture of the recipe is not built yet | Same as 1 | Low | Nice, later, when the picture exists. The list is enough to decide. |

## What all three ask for, whatever you choose

- Every preview carries the words "Preview, not saved. Nothing changes until you press Apply", inside the table or the picture itself.
- Per place: rows AND samples, before and after; the samples that stay with an empty value; a line for a place where nothing changes ("No change here: the column is missing").
- A plain sentence beside the numbers, for example: "removes 21 samples: all of Norway".
- What is shown as a preview and what Apply writes come from one and the same computation, with a test that they are equal.

## One point that touches a decision of yours

"No draft" (your decision of 2026-11-12) means: when the dialog is closed, the ticks are not kept. A user who closes the dialog to look at a plot in HOME, and opens it again, finds every place ticked again. The user viewpoint expects the ticks to be kept and would be surprised.

Suggestion: keep the decision, and let the dialog say it when it opens: "Nothing is remembered when you close this window. Your ticks start again from all places." The previews of points 2 and 3 are what makes closing the dialog unnecessary.

## Recommendation (the coordinator's, not a decision)

In this order, each one complete before the next:
1. The counts per place, with rows, samples, the samples that stay with an empty value, and the plain sentence.
2. The preview of the open plot (already written in the design).
3. The table of the rows that would be removed, at a place the user clicks.
4. Another plot, one at a time, on a click, with the time it took last time shown before the click.
5. The marks on the picture of the recipe, when that picture exists.

Not now: the dialog left open while the user walks through HOME.

## What you are asked

1. Is the order above what you want?
2. The table preview for a row filter (point 2 of the table): yes? It is not in the written design; it changes no decision.
3. Other plots on a click (point 3): now, or later?
4. "No draft": keep it, with the sentence on opening?

Not checked: the real screen (no browser was used); how long the app's own plot drawing takes on the screen; more than one recipe.
