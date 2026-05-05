### 🗺️ Workspace Infrastructure Map

| Category | Absolute Path | Purpose & Function |
| :--- | :--- | :--- |
| **1. Storage Root** | `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/` | The **Source of Truth** and top-level context for all agent operations and codebase indexing. |
| **2. Conversation History** | [`.claude/conversations/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/conversations/) | Stores JSON/Markdown logs of every session. This allows the IDE to reconstruct the **"Story of the Code"** and provides searchable history for the agent. |
| **3. Memory Bank (Knowledge)** | [`.claude/knowledge/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/) | Houses distilled project context: `blockers.md` (active frictions), `milestones.md` (roadmap progress), and `memory_bank_status.md` (configuration state). |
| **4. Memory Bank (Embeddings)** | [`.claude/embeddings/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/embeddings/) | The sink for **Cloud/Local Vector Embeddings**. This is used for semantic search across the entire codebase and historical discussions. |
| **5. Logic & Rules** | [`.claude/rules/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/) | Contains permanent behavioral personas ([`dasharch.md`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/dasharch.md)) and the [Antigravity Workspace Standard](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/workspace_standard.md). |
| **6. Automation workflows** | [`.claude/workflows/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/workflows/) | Stores slash commands and multi-step automation scripts (currently empty, but ready for scaling). |
| **7. Persistence Logs** | [`.claude/logs/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/logs/) | Stores **Session Audits** (Cold Memory), which are critical for periodic self-correction and tracking architectural shifts over days/weeks. |

### ⚙️ Governance Files

To replicate this environment's behavior, ensure the following configuration files are present in your root:

1.  **`.aiignore`**: Located in the **Storage Root**. It prevents the agent from wasting context/indexing quota on "noise" (e.g., `.venv/`, `__pycache__/`, `.git/`, and build artifacts).
2.  **`.vscode/settings.json`**: Governs IDE-specific behavior.
3.  **`settings.json` (Work environment backup)**: Found in [`EVE_WORK/configuration_antigravity/`](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/EVE_WORK/configuration_antigravity/), this acts as the "Master Configuration" for your Antigravity setup in this specific workspace.

### 💡 Replicability Tip
When setting up a new repository, create the `.claude/` and `.claude/` folders immediately. By populating `.claude/rules/workspace_standard.md`, you ensure the agent strictly follows your directory structure from the very first prompt.