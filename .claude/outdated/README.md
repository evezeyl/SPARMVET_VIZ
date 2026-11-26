# `.claude/outdated/`: what is no longer the source of truth

Created 2026-11-26, by the owner's order (channel block M704): one actualised source of truth; what is old, deprecated or not needed is moved here, and the history stays reachable.

- Nothing here is current. Nothing here is a rule, a decision or an instruction. Do not follow a path or a statement found here without checking the live files: the ledger (`.claude/knowledge/decision_ledger.md`), the ADR log, the rules and the code.
- The tree mirrors the old paths under `.claude/`: `.claude/design/studies/x` is now `.claude/outdated/design/studies/x`.
- The history of a file is in git: `git log --follow <path>`.
- `manifests/` holds one manifest per wave: the list of what was kept, updated or moved, with the reason and what replaces it. A moved folder has its own `README.md` that says why.
- A one-line pointer file stays at an old path only while a live file still cites that path; it is removed when the citing file is actualised.
- Only files that no open task of `.claude/tasks/tasks.md` names as its source or waits on are moved here. A folder that an open task still waits on stays in the live tree until the task is done (wave 1 fix round, 2026-11-26).
- The archive is not scanned by `assets/scripts/audit_old_words.py` nor by `assets/scripts/build_dep_graph.py`.
