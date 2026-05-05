Workspace Structure Definition:

.claude/: The "Instruction Layer" containing your persona (rules), custom tool definitions (skills), and multi-step automation logic (workflows).

.claude/: The "Execution & Memory Layer" where the IDE stores its operational data, including the local embeddings generated via your Ollama MCP and the active brain (context window cache).


# Restarting work from clean state 

## Reinstating the status and scann of the project
@Agent: Persona Shift to @dasharch - Step 1: Documentation Audit.
1. Assume the persona of @dasharch, Lead Architect.
2. Scan the ./docs/ directory (including any subdirectories like /appendix/ or /chats/) to identify the most up-to-date documentation regarding project milestones.
3. List the current 'Project Definition' based solely on these documents.
4. Compare this definition to the implementation_plan.md and tasks.md currently in ./.claude/.
5. Identify specifically which tasks or architectural pillars (Action Registry, YAML Cookbook, etc.) described in the docs are missing from our local planning folders.
6. Stop after this audit and present a summary of the 'Documentation vs. Planning' gaps.


## Initiation repository 
@Agent: Initialize workspace sync. 
1. Map conversation history to ./.claude/conversations/.
2. Confirm Cloud Embedding status (Default) is active for the Memory Bank.
3. Validate that .aiignore is preventing indexing of .venv and other noise.

close and start a new conversation - history was lost
@Agent: History Restoration Protocol.
1. Scan the directory ./.claude/conversations/ for all existing JSON/Markdown chat logs.
2. Re-index these files into the current session's "Past Conversations" sidebar.
3. Confirm that the 'Memory Bank' is pulling context from ./.claude/knowledge/ artifacts.

ask the agent to verify the paths it uses 
@Agent: Generate a 'Workspace Infrastructure Map' for my records. 
Please list every directory and file path you are currently using for data persistence, specifically identifying:

1. Storage Root: Confirm the absolute path for the workspace root.
2. Conversation History: Where are chat logs and summaries being written?
3. Memory Bank: Where are the vector embeddings and project knowledge (blockers/milestones) stored?
4. Logic & Rules: Where are you reading custom agent personas and workflows from?
5. Configuration: Which settings.json or .aiignore files are currently governing your behavior?

For each path, briefly explain its purpose so I can replicate this setup in other repositories.

updating workspace 
@Agent: Initialize SPARMVET_VIZ Workspace Standard.
1. Read the new 'Antigravity Workspace Standard' from ./.claude/rules/.
2. Set ./.claude/conversations/ as your mandatory history source.
3. If the IDE sidebar is not showing past chats, provide a markdown table of the 5 most recent files in ./.claude/conversations/ now so I can resume work.
4. Update ./.claude/knowledge/memory_bank_status.md to reflect that the infrastructure is now standardized.

new test with chat history
@Agent: Initialize SPARMVET_VIZ Workspace Standard.
1. Read the new 'Antigravity Workspace Standard' from ./.claude/rules/.
2. Set ./.claude/conversations/ as your mandatory history source.
3. If the IDE sidebar is not showing past chats, provide a markdown table of the 5 most recent files in ./.claude/conversations/ now so I can resume work.
4. Update ./.claude/knowledge/memory_bank_status.md to reflect that the infrastructure is now standardized.

test again , and lost the conversation again 

@Agent: Standardize Artifact Management for SPARMVET_VIZ.
1. Create the directories ./.claude/plans/ and ./.claude/tasks/ if they do not exist.
2. Generate the initial 'tasks.md' based on our current recovery status.
3. If you have an active implementation plan for the next coding phase, write it to ./.claude/plans/implementation_plan_current.md now.
4. Confirm that all future planning will be file-based and stored in these paths for version control.

Trying to understand why the conversation is lost 

@Agent: Diagnostic Request - History Persistence Failure.
Every time a new chat is created, the previous one disappears from my sidebar. 
1. Identify the absolute path of the 'Session Index' file you use to populate the Sidebar.
2. Are you currently restricted to a single 'active_session.json' instead of a multi-chat 'history_index.json'?
3. Check for permission errors or 'Locked File' warnings in ~/.config/Antigravity/logs/.
4. Provide the exact path you require to be 'writable' so that multiple concurrent chats can be indexed and preserved.
5. Can we solve this by creating a symlink from your expected 'Global History' path to ./.claude/conversations/?

canceled was not finisehd 
@Agent: Permission Override - Diagnostic Mode.
I am granting you explicit READ access to your system config for this task only.
1. Check ~/.config/Antigravity/logs/ for 'File Lock' or 'Permission Denied' errors related to 'conversations'.
2. Identify where the IDE UI expects the 'History Index' to be located. 
3. If the UI is looking in ~/.config/ but I am saving in ./.claude/, explain how I can update the 'Global Workspace' setting to bridge them.
4. Report if your 'Strict Mode' is currently blocking you from seeing these paths so I can adjust my Fedora security settings.

## Plan, task and knowledge managenemt restoration. 


@Agent: Infrastructure Audit - Identify Minimum Global Set.
1. Scan your active process handles: Which files in ~/.config/Antigravity/ are you currently WRITING to for this session?
2. Identify the specific file that populates the 'Past Conversations' sidebar.
3. Confirm if you can function if all files EXCEPT authentication (oauth_creds.json and token files) are mirrored to the local workspace.

4. Create ./.claude/plans/implementation_plan_v1.md and list these 'Critical Global Files' as the baseline for our mirror strategy.
5. Update ./.claude/tasks/tasks.md to reflect: 'Global Dependency Audit' as [IN PROGRESS].