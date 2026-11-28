# Cheatsheet: the words you type, and what they do

Pin this file. Written 2026-11-28 from `CLAUDE.md` section 4.3 and `my-mentoring/mentoring.md` section 4.

## In this project (SPARMVET_VIZ)
| You type | What happens |
|---|---|
| `-coordinate` | This session becomes the COORDINATOR (plans, orders, dispatches agents, reviews reports, merges; it writes no code). A guard hook enforces it. Any model can coordinate; you choose the model in the drop-down. Rules: `.claude/workflows/agent_dispatch_howto.md`. |
| `-solo` | Leaves coordinator mode: a normal session again. |
| `-researcher <persona>` | A research session as one persona: `scientist`, `architect`, `developer`, `user` or `statistician`. One round, at most 250 words plus sources, written to `tmpAI/panel/<topic>/<persona>.md`. It edits no repository file. |
| `-handoff` | The session writes its state (done, open, next) to `.claude/logs/handoffs/handoff_active.md`. Use it before you close a session. |
| `-update-all` | Updates rules, workflows, knowledge, tasks, plan, ADRs, README and docs, and records the decisions. |
| `-review` | A review session like the one we have worked in: relays your decisions, asks you one question at a time. Instructions: `.claude/workflows/review_session.md`. |

## From your mentoring rules (any repository)
| You type | What happens |
|---|---|
| `-learn <topic>` | Queues the topic for the digest; no explanation in the work chat. |
| `-explain <topic>` | Explains now, short first. |
| `-digest` | Writes a digest entry for the work since the last one. |
| `-tutor` | This session becomes the learning session (read-only except the digest). |
| `-quiz <topic>` | One assessment exercise. |
| `-deep <topic>` | A dedicated learning session. |
| `-commit <draft>` | Reviews your commit message against the staged diff. |
| `-issue <draft>` | Reviews your issue draft. |
| `-sessionname` | Lists live sessions (name, tab title, folder). |

## Starting, continuing, closing a session
- A new session starts from files, not from chat. Read order for a new coordinator: `tmpAI/coordinator/STATE_NOW.md` first.
- New session or compact? `.claude/workflows/agent_dispatch_howto.md` section 8.
- A long chat costs more with every turn (the whole chat is re-read each turn). A fresh session that starts from a short file is cheaper.

## Commands you may want
- Start the demo deployment: `PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/demo/202612_demo_deployment.yaml ./.venv/bin/shiny run app/src/main.py --port 8000`
- Fast check of the code (seconds, no quota): `./.venv/bin/ruff check libs app --select E9,F821,F402,B017,B023`
- Headless tests: `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q`
- Who is alive (session names, to message them): `~/Documents/Insync/gdrive/OBSWORK/20_GITS/my-mentoring/bin/sessions.py` (or type `-sessionname`)
- Your demo notes: `USER_DIRECTORY/cheatsheet_demo.md` and `202611_demo_requirement.md` in this folder
