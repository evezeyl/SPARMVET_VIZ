# Design review by personas (reusable method)

**Purpose:** before a design is built, review it from several points of view, each with its own question, method and
evidence. Written 2026-11-11 from the HOME audit review (`home_audit_steps.md` sections 18-20), where each point of view
found different real problems. Reuse it for any design that affects results, data or the user's decisions.

**How to call it:** "review as <persona>" or "run the persona review on <design>". One persona at a time, findings written
down before the next one starts. Order used: Scientist, Data scientist, Developer, Checker (last, on the final text), then
Novice user with real people.

## Rules for every persona

1. **Never guess, always verify.** (Eve, 2026-11-11.) A claim about the code is checked in the code, a claim about the data on
   the real data, a claim about behaviour by running it. Say what was run.
2. **Label the evidence** of every finding: **verified** (run, or read at `file:line`), **reasoned** (follows from the design
   or the data, still needs a test), **external** (cited source with link), **assumed** (not checked: say so, never present it
   as a fact).
3. **Run, do not only read.** Small scripts in the scratchpad are fine and expected (for example: apply the filter engine to a
   frame with nulls). A finding that can be demonstrated is demonstrated.
4. **Search outside the project** when the question is general (statistics practice, reporting guidelines, human factors, how
   other fields solve it). Cite the source. Say when a search found nothing instead of filling the gap.
5. **Separate the finding from the decision.** The persona reports, with a remedy and a class (software bug, guard rail,
   practice to teach, design change). The decision is Eve's.
6. **File what is real.** A verified bug gets an issue at once (standing rule). A design finding goes to the design file with
   its evidence class.
7. **Check the checkers.** An audit that passes proves only what it checks (example: the UML audit passed while two ADRs shared
   one number, and while diagrams disagreed). Name what an audit cannot see, and add the check when it can be automated.
8. **Stop rule:** stop a persona when its question is answered with evidence, not when ideas run out; write down what was not
   covered.

## Findings table (use it every time)

| # | Finding | Evidence class | Evidence (command, file:line, link) | Severity | Remedy | Class | Issue | Status |
|---|---|---|---|---|---|---|---|---|

Classes: software bug | guard rail (inform, warn, confirm with a reason) | practice to teach (help, docs) | design change.

## 1. The Checker (consistency)

**Question:** do all the files, diagrams, ADRs, rules, tests and the code say the same thing? **Method:**
- list every artefact that mentions the topic (grep for the words, the flags, the ids); read the model file, not only the pictures;
- compare names, numbers, plot ids, flags, defaults, statuses across them; check ADR numbers and references (a new check in
  `audit_docs_sync.py` now catches duplicate ADR numbers);
- check the diagram text against the design text, and both against the code and the real recipe;
- list what is out of date and mark it (as built, pending, replaced when built) instead of deleting history;
- re-run the audits (`audit_uml_model.py`, `audit_docs_sync.py`) and state what they do not check.

**Found on 2026-11-11:** a second ADR with the number of an existing one (ADR-087); a plot id written as a file name; a claim
that two data schemas were plot targets when one was not mounted; "workspace", "mode", "rebuilt", "copied" used for the same
thing; a diagram sketch that put alerts in the wrong sidebar (checked against `sidebar_registry.py`).

## 2. The Scientist (the person who publishes the result)

**Question:** can I trust this figure and defend it to a reviewer? **Method:** walk one realistic job from start to export
("one sample is bad: remove it everywhere") on the real recipe; ask at each step what I would not know; ask what a reviewer
would ask (which samples, why, how many, before/after); look for silent changes (rows, samples, NA, rounding); check the
reporting guidelines (ARRIVE, CONSORT) and the literature on flexible analysis (Simmons, Nelson, Simonsohn 2011).

**Found:** a sample removed with "all plots" stays in every plot whose data has no such column; nothing says which plots changed;
a table can end with different sample sets than the others.

## 3. The Data scientist (statistical and data validity)

**Question:** is the transformation correct on messy data, and does the order of operations change the science? **Method:**
write the awkward cases and run them against the engine: missing values and NaN with every operator; integer columns with
non-integer thresholds; IDs with whitespace and case; long format where an entity can vanish; statistics computed over all
samples (z-score, percentile, rank, top-N, pivot, summaries) followed by a removal; ties, empty results, zero rows; types that
differ between stages (Year 2022.0 and "2022"); compare against an independent reference implementation.

**Found (all verified by running):** `v >= 90.5` keeps 90 on an integer column; `!=` and none-of drop rows with a missing value
silently; a sample vanished from a long table after a value filter; `'S2'` removal leaves `' S2'` and `'s2'`.

## 4. The Software developer (architecture and how the information reaches the user)

**Question:** how would I build this so that it is correct, testable and does not drift, and so that the user gets the
information they need at the moment of the decision? **Method:** list the duplicated logic (the same analysis written several
times); find places where two stores can disagree; check "one code path" claims for structure; check layers and the
cross-panel rules; ask what can be tested without a browser; look for the point of no return and put the strongest check there;
look up human-factors evidence before adding warnings (warning fatigue); plan the build order so the risky logic comes first and
the screen last.

**Found:** seven features would each parse the recipe (-> one recipe graph); a step list and an event log would disagree (-> one
event log); the hash and the executed steps could differ (-> a step compiler); one overloaded dialog (-> three steps and an
effect preview); no check before the export (-> a pre-export review); the guarantees were not executable (-> property tests).

## 5. Proposed personas (not yet used; use when the topic needs them)

| Persona | Question | Typical method |
|---|---|---|
| **Novice user** | can someone who did not write this use it correctly the first time? | 2-3 people, think-aloud, real warning texts, the real recipe; record where they hesitate or click through |
| **Maintainer / operator** | can this be deployed, configured, migrated and debugged? | list config keys, failure messages, format versions and migrations, performance on large data, what a log shows after a failure |
| **Teacher** | can the idea be said in one sentence and shown in one picture? | write the help text and the one-page summary first; if it does not fit, the design is too complicated |
| **Security and privacy** | what leaves the machine, what is stored, who can change a record? | the export contents, sessions, logs, secrets, who the "author" is |
| **Release / QA** | what must be retested, and how do we know it passed? | the impact table, the test plan items, mutation checks, the full gate |

## Evidence that this works

On 2026-11-11 the four personas found, between them, two verified engine bugs (#62, #63), one verified key bug that disabled the
join-key safeguards (#61), a duplicate ADR number, and a design change that makes the audit testable. None of these was found by
the existing audits. The method costs time: use it for designs that affect results or decisions, not for cosmetic changes.
