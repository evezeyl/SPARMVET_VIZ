@Agent: @dasharch - SYSTEM INITIALIZATION & TASK DECOMPOSITION.

1. PERMANENT CONTEXT (Read immediately):

- ./.claude/rules/workspace_standard.md (Authority map & VENV enforcement)
- ./.claude/tasks/tasks.md (Current execution status)
- ./.claude/knowledge/project_conventions.md (Path registry & terminology)

1. MANDATORY SEARCH & RETRIEVAL PROTOCOL:
You are equipped with a modular rule system. Do not guess logic. You MUST identify and read the relevant files from the following directories BEFORE executing a task. Attached file describes this logic. (PATHTS INITIATION)

2. HEADLESS-FIRST UI TESTING MANDATE:
UI testing is strictly gated. For every UI component task:

- Step 1: Create a sub-task in tasks.md for a Headless Unit Test.
- Step 2: Implement/Fix the component logic.
- Step 3: Execute a headless test using the relevant library debugger (e.g., debug_ingestor.py, debug_wrangler.py).
- Step 4: Materialize results to tmp/Manifest_test/ and output df.glimpse().
- Step 5: HALT for @verify. Only after sign-off may you proceed to the Visual/Reactive UI check.

1. INITIAL ALIGNMENT:
Review tasks.md. Decompose the next UI-related task into granular "Headless-First" sub-tasks. List the specific rulebooks from ./.claude/rules/ you intend to read to complete these sub-tasks.

HALT for @verify after listing your plan.
