# Taken-by report, 2026-11-15 23:30 (records task for Eve; nothing decided by the writer)
Ledger: `tmpAI/panel/adr/ledger.md` (the old one is kept as `ledger_before_2026-11-15_2330.md`). Each line has an ID: L01 to L53 (old lines, plus L27b and L36b added), N01 to N52 (today). Her chat turns are cited as `session #line` (times in UTC; local = UTC + 1 h).

## 1. Counts (107 lines)
- EVE: 104 (53 old lines + 51 today).
- AGENT: 1 (L36b).
- NOT STATED: 2 (L27b, N52).
- Old lines: 55 (53 + L27b + L36b). Today's lines: 52. Today's "asked, not decided": 17 items (A01 to A17, at the end of the ledger).
- How EVE was established. All 52 lines of today were compared with her own turns in the transcript of the review session (cd1b0ac7); none differed from the relay, except that her M124 line 3 ("removed from the recipe") was corrected by her in M125. Old lines L10, L11, L17, L27, L36 and L48 to L53 were also found in her own turns (sessions ad032c0c, 9b22d54e, 92f68895, 3ce2c163). The other old lines rest on records that name her with a date (ADR status lines, `home_audit_steps.md`, the "Eve" date column of `recipe_format_spec.md` 2.1, `tasks.md`, `CLAUDE.md`). I did not re-check each of DEC01 to DEC49 against her turns.

## 2. AGENT choices that are built
- **L36b: `derive_categories` removed "as dead"** (a lookup is a `polars_join`). Made by the session that relayed her Polars rule (M56 point 2), not by her (ADR-100 point 7, corrected 2026-11-14). BUILT in `d63d3f3d` (2026-11-13); gone from the registry; `step_migration.py` says "removed". Not marked PROVISIONAL. Open: point 2.
- **Q1 of the ledger: `Categorical` kept in the migration** (commit `e9ac815f`, 2026-11-13 22:15, an agent, against DEC27). BUILT: 75 `type: Categorical` fields are still in the shipped recipes and test data. Not marked PROVISIONAL. She decided otherwise on 2026-11-15 (N02, N43); the migration to String and Enum was not merged at commit 806dc852.
- **S1 and S3 of the seed (M85, coordinator, PROVISIONAL in the records):** `random_state: null` is refused (`54e6979f`); `plot_defaults.random_state` is the one seed of the recipe (`6f9479e0`). `tasks.md` section 5 lists "S1 to S3" as NOT ANSWERED. They fit N01 but she has not confirmed the mechanism: point 6.
- Self-join runs as written with advice J12 (`af5560a9`, 2026-11-14, an agent, no record of her choice). She decided the same behaviour on 2026-11-15 (N11). The error for the anti-join (N23) is not built.

## 3. Points for Eve (answer by number)
1. **Who decided the "step compiler" (L27b)?** The audit file says "defined 2026-11-12" and names nobody. On 2026-11-12 16:33 UTC you asked "O7 what is the step compiler?". I found no later yes. (a) you, later, after an explanation; (b) an agent, as a design word; (c) you do not remember: then it is open.
2. **Do you confirm that `derive_categories` is removed (L36b)?** The relaying session wrote "removed as dead"; the spec says "read it, then decide". The code already lacks it. (a) yes, remove it; (b) bring it back; (c) open.
3. **Who set the rule "a build on an agent's recommendation is PROVISIONAL" (N52)?** `tasks.md` line 21 says "Eve 2026-11-15". Your chat turns of that day hold no such sentence. The sentence is in the review session's relays (M83, M97, M129). (a) you, in words I did not find; (b) the review session proposed it and you did not object; (c) you do not remember: then it is open.
4. **`column` or `columns` for the input column of `modif_` and `step_` actions?** DEC15 (`columns`, a list) and DEC39 (`column`) are both dated 2026-11-13 in the "Eve" column. The code follows DEC39. (a) DEC15 holds; (b) DEC39 holds; (c) open.
5. **Which export holds the recipe file (L13 against your M131)?** 2026-11-09 (ADR-097): the standard export never holds the recipe or the raw data, it names both. 2026-11-12: recipe and raw data behind one box, off by default. Your M131: one mode exports the results with the recipe and the data used (the data replaceable); the other exports the audit changes. (a) the records are right and you meant "names"; (b) you want the recipe file in the results export, and two decisions change; (c) open. Nothing is changed before you answer.
6. **Do you confirm the two seed builds S1 and S3 (section 2)?** (a) yes, both; (b) no, remove; (c) open.

## 4. Later records of hers that contradict a ledger line (the later wins)
- L34 (DEC27, `categorical` refused): replaced by N02 and N43 (2026-11-15).
- L49 (V1 "no rename", 2026-11-14): replaced by N36 (V1-B, 2026-11-15).
- L04 ("null/random = new each render"): replaced by N01 (0 by default, every seed written).
- L52 ("every operator usable"): narrowed by N06 (no text greater/less in HOME).
- L35 (DEC41, other Polars methods deferred): replaced by her 2026-11-14 order to start them now (ADR-100 note, M77 point 4).
- N38 (her M111) replaces the wording of her M108 (the app follows the lineage to every node); N47 (M125) corrects M124 line 3.
- L13 and L33/L35: not contradicted by a decision but by an open question (points 5 and 4).

## 5. Dates and sources to correct
- L48 to L53 are dated 11-15 in the old ledger; her words are from 2026-11-14 18:33 UTC (the evening; ADR-104 clock-error note). The ledger line dates were left as they were.
- N09 (formulas): the records cite "channel M86", which is the coordinator's question. Her answer is her chat turn cd1b0ac7 #711.
- Decisions of 2026-11-14 that ADR-104 and the ADR review record but the ledger lacks: a seed pinned by an audit step is the same everywhere (M74.1); `between` with its four `closed` values (M74.2); the filter value is typed at the source (D1, M76, M77); the deferred Polars methods start now (M77.4). Not added: they are not from today.

## 6. What this check would not catch
- The "Eve" date column of the spec is taken as a record; a decision made by an agent but entered there by a scribe would pass.
- Relays of 2026-11-14 (M65 to M77) were checked through the ADR texts that quote her, and only M72 against her own turn.
- Where she said "yes" to a proposal, the ledger counts it as reviewed (EVE); it cannot show how closely she read the proposal.
- I read no file named `tmp.md`. Scratch scripts: `tmpAI/panel/adr/eve_turns.py`, `build_ledger.py`.
