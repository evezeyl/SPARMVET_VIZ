# To give to gemini

.venv/bin/python -m py_compile app/src/server.py && echo "server OK" && .venv/bin/python -m py_compile app/modules/wrangle_studio.py && echo "wrangle_studio OK" && .venv/bin/python -m py_compile libs/utils/src/utils/blueprint_mapper.py && echo "mapper OK"


# Audit

@contextScopeItemMention Hi, you have instructions in the attached files. After I want you to do an IN-DEPTH audit of the status of our project. You can scakk all files, but EVE_WORK, tmp, tmpAI and files ignored in the .gitignore - are not part of your evaluation, so you do not need to check those. Your task is to write a report in .antigravity/logs with todays date. You must detect any Non reported incomplete tasks and implementations, inconsistencies, errors, buggs, lack of documentation, lack of transparency, anything we should now focus on. Detect legacy items that have been supperseeded, anything that is in the way of making this project a success. Write evertyhing you detected in the report. Be extremely thoughrough and use your thinking abilities to understand how things functionne under the hood, the intempt, and does it fullfill the criteria. You can also propose solutions to fix the problems encountered. You are NOT ALLOWED to modify the code. Only audit and report. . Only audit and report. Do what you need to do an excelent audit even if it is not mentionned here.

# Update

ok, can you please update if necessary: rules, workflows, knowledge (eg. project convetion) artifacts, tasks, implementation plan, architectural decisions, README, daily audit and Docs whith what has been decided since this same task has been executed. 


Please update when and where necessary: rules, workflows, knowledge, artifacts, tasks, implementation plan, architectural decisions, README, daily audit and Docs.

Please document choices made done during this session and what has been done. Update when necessary  rules, workflows, knowledge (eg. project convetion) artifacts, tasks, implementation plan, architectural decisions, README, daily audit and Docs

Please write a concise handoff of what has been done and current state for the next agent.
Please append - do not delete anything.

handoff_active.md

# Initialisation
> Manifest helper 
@Agent: @bioscientist - help me build a manifest for [Research Goal]



> makes it read this context automatically that it needs and then good and flexible

```text
@Agent: @dasharch - SYSTEM INITIALIZATION & TASK DECOMPOSITION.

1. PERMANENT CONTEXT (Read immediately):

- ./.agents/rules/workspace_standard.md (Authority map & VENV enforcement)
- ./.antigravity/tasks/tasks.md (Current execution status)
- ./.antigravity/knowledge/project_conventions.md (Path registry & terminology)

1. MANDATORY SEARCH & RETRIEVAL PROTOCOL:
You are equipped with a modular rule system. Do not guess logic. You MUST identify and read the relevant files from the following directories BEFORE executing a task. Attached file describes this logic. (see PATH_INITIATION.md attached)

Halt and wait for other instructions. 
```

```text
@dasharch - SYSTEM RESET & AUTHORITY ALIGNMENT.

1. MANDATORY KNOWLEDGE SYNC (READ BEFORE ACTION):
To prevent AI Drift and ensure ADR compliance, you MUST read the following files before proposing any logic:
- ./.agents/rules/workspace_standard.md (The Master Index)
- ./.agents/rules/rules_runtime_environment.md (VENV & Command Authority)
- ./.agents/rules/rules_verification_testing.md (@verify Protocol)
- ./.antigravity/knowledge/architecture_decisions.md (ADRs 001-032)
- ./.antigravity/plans/implementation_plan_master.md (Current Roadmap)

2. OPERATIONAL CONSTRAINTS:
- RUNTIME: All execution MUST use `./.venv/bin/python`. Internal python calls or 'os' movements are PROHIBITED.
- CLI MANDATE: All scripts MUST be executed via terminal with `argparse` flags. Hardcoding is FORBIDDEN.
- AGNOSTICISM: Use generic terminology (Project/Collection/Project Manager) per ADR-003 and ADR-029b refactor.
- VIOLET LAW: Documentation must follow the `ComponentName (file_name.py)` standard.

3. IDENTITY & DATA:
- Data paths and system locations MUST be resolved via `config/connectors/local/local_connector.yaml`.
- Metadata and Additional Data are OPTIONAL. Default to Identity Logic if missing.

4. TASK INITIALIZATION:
- Acknowledge that you have read the above files.
- Locate the current active task in ./.antigravity/tasks/tasks.md.
- Summarize the physical state of tmp/ and current project stability.

5. SECONDARY RULE HIERARCHY (READ ON-DEMAND):
Before executing any task, you must cross-reference the following specialized rulebooks if relevant:
- UI/Aesthetics: ./.agents/rules/rules_ui_dashboard.md & rules_documentation_aesthetics.md
- Data Lifecycle: ./.agents/rules/rules_data_engine.md (ADR-024 Tiering)
- Script Governance: ./.agents/rules/rules_asset_scripts.md (For all CLI tools)
- Implementation Workflows: ./.agents/workflows/ (Specific to Transformer or Viz_Factory)

6. DEPENDENCY VERIFICATION:
Before beginning a task, STATE which rulebook you are consulting. If a task involves creating a new plot component, you MUST read ./.agents/workflows/viz_factory_implementation.md first.

FOLLOW VERIFICATION PROTOCOL: Generate a Technical Contract for the next step -> HALT for @verify."
```

# 🛠️ Breaking the "Infinite Thought" Loop

## The "Halt & Report" Command

Type this directly into the chat:

"@dasharch: COMMAND FINISHED. Read the latest content of tmp/test_results.txt (or relevant log) and proceed with the verification summary."

## The Force-Read Signal

If the agent won't stop spinning, provide the "Physical Proof" it's looking for. Copy-paste the last 5 lines of the terminal output into the chat and say:

"Command completed with exit code 0. Here is the output: [PASTE OUTPUT]. Proceed to verify."

## The System Refresh (If the IDE is frozen)

If the UI itself is unresponsive, use the !sync protocol we established. Refresh the page/app and start the next prompt with:

"@dasharch: RE-SYNC. The previous integrity suites have finished. Check ./.antigravity/logs/audit_2026-04-09.md for the result and continue."

# TEMPLATES

### A. The Alignment Prompt (System Reset)

- Use this template to re-seat the IDE Agent when it drifts:

```text
"@Agent: @dasharch - SYSTEM RESET.

Read: 
- workspace standard: ./.agents/rules/workspace_standard.md,
- architecture decisions: ./.antigravity/knowledge/architecture_decisions.md and
- implementation plan: ./.antigravity/plans/implementation_plan_master.md

For any subsequent tasks and prompt, read files that are 
relevant to your tasks execution (as defined in the workspace standard) in 
- ./.agents/rules/
- ./.antigravity/workflows/
- ./.antigravity/plans/
- ./.antigravity/knowledge/
- ./.antigravity/tasks/
- and all the current documentation in ./docs

Current Priority: [Task from ./.antigravity/tasks/tasks.md]. 

Follow Verification Protocol: Generate Contract -> HALT for @verify."

```

### B. The log promt

```text
@Agent: @dasharch - LOG INFORMATION.

Create if not existing, verify and update the log of the todays session
in ./.antigravity/logs/audit_{{YYYY-MM-DD}}.md
Never delete or modify previous information in the log, only append new information.

Update libs/{library_name}/README.md with any new relevant information.

Update User documentation in ./docs with any new relevant information.

Update Project conventions ./antigravity/knowledge/project_conventions.md
with the necessary information.

Update Completed tasks in ./.antigravity/tasks/tasks.md.
```

### C. Consistency Check Prompt

```text
"@Agent: @dasharch - CONSISTENCY CHECK.

Review the current state of the project and identify any inconsistencies, technical debt, or potential pitfalls.
Review the following files for potential inconsistencies:
- ./.agents/rules/
- ./.antigravity/workflows/
- ./.antigravity/plans/
- ./.antigravity/knowledge/
- ./.antigravity/tasks/
- ./docs
```

# Save a good agent when haning - attempt

- Process did finish successfully.Terminate any active background processes or terminal reads that are currently non-responsive.
- Background Mandate: Moving forward, for any script execution you MUST use background execution flags to ensure the UI remains responsive.
- Please resume

----

@Agent: @dasharch - EXECUTION RECOVERY & HYGIENE.

Status: You are currently hanging on terminal I/O. We need to reset the execution stack.

Rules for Recovery:

1. Process Termination: Terminate any active background processes or terminal reads that are currently non-responsive.
2. Background Mandate: Moving forward, for any script execution (Wrangler, Assembler, or Viz Runner), you MUST use background execution flags to ensure the UI remains responsive.
3. Context Purge: Read .antigravity/tasks/tasks.md and move all 100% completed items to the archives/ directory per the Active Visibility Protocol (rules_verification_testing.md). This will clear your active memory.
4. Logic Lock: Confirm you are strictly using ./.venv/bin/python for all future calls.

Current Priority: Resume the Knowledge Capture (FAQ.qmd and Audit Log) we discussed.

HALT and provide a 'System Clear' status before proceeding with the documentation tasks.

# We should be able to get answer which model

What is your exact model ID?
