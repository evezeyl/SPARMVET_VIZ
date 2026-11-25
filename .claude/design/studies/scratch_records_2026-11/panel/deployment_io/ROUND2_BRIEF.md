# Deployment study, the one discussion round (coordinator, 2026-11-21)

The owner asked that the viewpoints "come back with suggestions (after having discussed together)". This is that one round. You recommend; she decides. Read-only; build nothing; never read `tmp.md`.

## Read
The four first-round texts in `tmpAI/panel/deployment_io/`: `architect.md`, `scientist.md`, `developer.md`, `user.md` (a digest). You know `ORDER.md`, `FACTS.md`, `BRIEF.md`. Read the other three viewpoints in full before you answer.

## Where you agree (do not repeat it)
All four recommend named places in the deployment file (design A), with "shared" and "own" as the words on screen and as ready-made templates (design B), and reject keeping the five keys as the final state (design C). Nobody proposes an authentication system: without a login the "own" place is shared by all users of one process, and the screen says so.

## Where you differ: answer each point, from your seat, in this order
1. **The same recipe name or table in two places.** Architect and developer: refuse, name both places, no search order. Data scientist: refuse unless the bytes are identical. User: show both entries with their labels and let the user choose; or let the deployment file say which wins and show that. Which ONE rule do you support after reading the others, and what does the user see? Consider the owner's own case: a consortium recipe that a user copied into the own place and changed (the decided file name is `name_date`).
2. **Nothing writable** (static web page, read-only container). Today the opening of a recipe stops. Options: (a) the app requires one writable place and stops at start with a plain message; (b) the app keeps the stored tables and the session in memory or in the system temp folder for the session, and says "nothing is saved here"; (c) the deployment file chooses. What does each cost and risk; which do you support?
3. **The access words.** Architect: `read | add | replace` per place. User: three words on screen (shared, mine, this session only). Data scientist: plus `private` and `may_export_data`. Give the smallest set of words in the deployment file that still says everything needed, and the mapping to the screen words.
4. **Private data.** Is a `private` mark on a place needed now, and what exactly must it prevent (stored tables of private data in a shared `user_data`; data files copied into a reproducibility export; a session that stores the server path)? What is the least that makes the owner's case safe: consortium data shared, sensitive metadata only in the user's place?
5. **Confinement.** May a recipe's `source.path`, or HOME's Data Import, read or write outside the declared places? What happens to the shipped recipes whose `source.path` points into `assets/test_data/`?
6. **Migration.** Architect: replace the five `locations` keys in one scripted pass, old keys refused, no alias. Developer: small steps that each merge alone. Is there one order that satisfies both the owner's rule "no half fixes and no shims" and "each step leaves a working app"? Name the first three steps.
7. **API and connectors.** Architect: nothing in the app talks to Galaxy, IRIDA or an API; a provider pulls into a local read place before the app reads; opt-in. Does that cover the owner's cases ("the data is passed directly from the pipeline"; "API can be used to give both the data and the recipe")? What must be recorded so that a figure stays reproducible when the source is an API?
8. **D-0340** says "no new configuration variable for now" for the audit folder. Does the design reconsider it, reinterpret it, or respect it? Say it in one sentence the owner can confirm or refuse.
9. Anything in another viewpoint's text that you think is wrong or would change a result silently. Quote the sentence.

## What to return
For each point: your position in two to five sentences, and whether you changed your mind after reading the others. Then: "Still open between us" (what one round did not settle). Plain short sentences; no padding; no length limit. If you have a shell, save your text as `tmpAI/panel/deployment_io/<viewpoint>_round2.md` and return the path plus the text of your points 1 to 3; if you cannot write, return the full text.
