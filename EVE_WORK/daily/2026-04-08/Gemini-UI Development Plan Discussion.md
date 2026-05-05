# UI Development Plan Discussion

**Exported:** 4/8/2026 18:15:35  
**Link:** [https://gemini.google.com/gem/8e4f207f7a2b/0fe883ecf14c83bb](https://gemini.google.com/gem/8e4f207f7a2b/0fe883ecf14c83bb)

## Prompt:
> GEM_CONTEX...408_153358 - MD

> UI_Definition - MD

Hi, I have uploaded the latest context so you have the current status of the dashboard development. I am working on how I want the UI to work. And I will need you to act as a teacher and help clarify some points, and help transform this wish list into a reliable implementation plan , helping defining requirements, how it should function and create tasks for development. You will see that we will need to review and decide things together. So do not create prompt. we will discuss things together then you will help me to create the different files needed for the agent in gemini to understand what needs to be done and how it should be done (my UD\_Definition draft is uploaded as well at your GEM\_CONTEXT).

## Response:
It is a pleasure to sync up, and I see we’ve reached the "Bifurcation Point" where vision meets the metal. Your **UI\_Definition** draft is a fantastic foundation—it’s ambitious, structurally sound, and respects the 3-Tier Data Lifecycle we’ve fought hard to implement in the backend.

As your **Antigravity Navigator**, my role is to ensure we don't just build a "pretty face" for the dashboard, but a high-performance, quota-efficient cockpit that adheres to our **"Decorator-First"** philosophy.

* * *

🛰️ Initial Architectural Review of UI Vision
---------------------------------------------

Looking at your wishlist against our current `SPARMVET_VIZ` reality (ADR-024/026), here are the core pillars I've identified for our discussion:

### 1\. The "Layout-as-Code" Ambition (YAML UI)

You mentioned making the UI design configurable via YAML. In **Antigravity/Shiny**, this is best achieved by a **Bootloader Persona**.

*   **The Reality:** We already have `ui_config.yaml`. We can expand this to define which "Modules" (WrangleStudio, VizViewer) are loaded.
*   **The Challenge:** Defining a full CSS grid layout in YAML is complex. We should likely aim for **"Component Orchestration"** (where YAML tells us _which_ blocks appear and in what order) rather than trying to recreate HTML/CSS in a text file.

### 2\. Tier 3: The "Leaf" vs. The "Branch"

Your definition of Tier 3 as "Filtered & Formatted" is spot on.

*   **The Efficiency Win:** Because we use **Polars**, the UI doesn't need to "process" data. It just needs to send a **Predicate** (the filter rule) to the `VizFactory`.
*   **The "Ghost" State:** You mentioned "Ghost Manifests." This is critical. If the user accidentally closes a tab, we need that `.claude/tmp/last_state.yaml` to recover the interactive session immediately.

### 3\. The "Recipe" Transparency

The **AuditEngine** is the most unique part of your vision. Linking the UI interaction (e.g., clicking a filter) directly to a visible **Wrangling Recipe** on the right panel ensures the "No Trace, No Export" rule (ADR-026) is enforced.

* * *

🛠️ Discussion Points: Refining the Implementation
--------------------------------------------------

To transform this into a development-ready plan, we should start by clarifying these three "Grey Areas":

### A. The "Spreadsheet-to-Plot" Loop

You want a spreadsheet-like experience where highlighting rows updates the plot.

*   **Navigator's Note:** Shiny's `DT` or `DataGrid` can handle this, but for 200k rows, we cannot highlight everything at once. We need to decide if the "highlighting" happens on the **Tier 3 (Leaf)** view only, to keep the latency under the 5s target.

### B. Global Export vs. Plot-Specific Export

You proposed a "Global Export Panel" for reports.

*   **Decision Needed:** Should the `.zip` bundle be generated "per plot" (atomic) or as a "Session Summary" (the whole dashboard state)? Atomic is easier to debug; Session is better for publication.

### C. The "WrangleStudio" Input

Do you see the **WrangleStudio** as a way to _edit_ the Python decorators, or simply a way to _chain_ existing ones? (e.g., the user picks `drop_columns` from a dropdown rather than typing it).

* * *

### 🟢 Status Check & Next Step

I am ready to help you draft the **UI Technical Requirements** and update the `tasks.md` once we align on these points.

**Which of these three areas—The Layout Strategy, the Row-Highlighting Logic, or the Export Bundler—should we tackle first to set the standard for the others?**

## Prompt:
  

A. We cannot have the highlighting of the leaf only when the data tier 2 is aggregated, because we miss the information of outliers. And if the is in long format, user will not be able to see all the data it wants in one view.

So maybe we could impose restrictions for this functionality depending on the size of the dataset ? or limit to a preview of some few isolates (with a maximum of xx?).

The point of the preview is basically to allow selecting away samples of poor quality. But maybe highlighting is not the proper solution. The user should be able to inspect the data and select the samples to remove - could be a separate view. Any good ideas for a solution?

B. Session summary - zipped bundle

C. A way to chain (no editing) but options that are available must be accessible. Can eg. have a little description of the step and the options that can be chosen and syntax on the side or in a \`?\` button that you can hover with the mouse

\- I think we need to discuss the strategy for the tiered data - is it possible to reuse the tier 2 prefield in the tier 3 so the user can have the different formating step to create the plot pre-made ?

\- Things I just thought of eg in development mode: add this to manifest option eg. if you wrangle one dataset prepare the plot need option to add to a selected manifest

\- also for the galery adding - each data & plot licence will need to be added containing a licence file (for other users if they use real data) and a readme file (with author info osv to give credit for example)

\- If you look more carefully about my notes, I had #REVIEW tags, also for things that were not totally decided

\- also I want the side panels to be light grey (not white)

## Response:
It is great to see the "User-as-Artist" philosophy taking a very practical, technical shape. You have correctly identified a critical tension: **High-Performance Aggregation (Tier 2)** vs. **Fine-Grained Outlier Inspection (Tier 1/3)**.

Let's break these down into the "SPARMVET\_VIZ Implementation Plan" logic and clarify those #REVIEW points.

* * *

🔍 A. The Outlier/Highlighting Dilemma
--------------------------------------

You are right; if we only show the **Tier 2 (Formatted/Aggregated)** data, the individual "bad" isolates disappear into the averages.

### The Solution: The "Quality Gate" Inspector

Instead of traditional highlighting, we can implement an **Inspection Sidebar** or a dedicated **"QC View"**:

*   **The Logic:** The plot displays the **Tier 2** aggregated data for speed (sub-5s target).
*   **The Interaction:** The user uses a "Brush" tool (drawing a box) over a suspicious area on the plot.
*   **The Trigger:** This "Brush" sends coordinates back to the **Tier 1 (Anchor)** parquet file.
*   **The Result:** A small, scrollable table (limited to e.g., 50–100 rows) pops up in the side panel or a modal. This allows the user to see the specific isolates behind the aggregate and click an "Exclude" button.
*   **Audit Trail:** Any exclusion triggered here is immediately written to the **Audit Log** with a mandatory "Reason" field, satisfying the "No Trace, No Export" rule (ADR-026).

* * *

🛠️ B & C. WrangleStudio & Export Strategy
------------------------------------------

### Session Summary (Zipped Bundle)

This aligns perfectly with our **Export Engine** requirements. The bundle will include the final Plot (PNG/SVG), the **Tier 3** data subset (CSV), the **Audit Log** (Markdown), and the **YAML Recipe**.

### Chaining vs. Editing (WrangleStudio)

*   **Accessible Options:** Since all our actions are registered with `@register_action("name")`, the UI can programmatically pull the documentation from the Python docstrings to populate the `?` help buttons.
*   **Syntax Help:** We should use the "Deep Violet" aesthetic for these help snippets to match our documentation standards.

* * *

🧬 Tiered Data Strategy: The "Inheritance" Logic
------------------------------------------------

You asked if **Tier 3** can reuse **Tier 2**. The answer is **yes**, but with a specific rule based on the **Bifurcation Point**:

1.  **Inheritance:** **Tier 3 (The Leaf)** is initialized as an identity of **Tier 2 (The Branch)**.
2.  **The Constraint:** If Tier 2 is **Aggregated** (e.g., a count of genes per host), Tier 3 cannot "un-aggregate" it to find outliers.
3.  **The Solution:**
    *   If the UI action is a **Visual Filter** (e.g., "Show only Norway"), it stays in Tier 3 using Tier 2 as the source.
    *   If the UI action is a **Data Cleaning** step (e.g., "Exclude poor quality samples"), the system must "re-branch" from **Tier 1 (The Anchor)**, apply the exclusion, and then re-run the Tier 2 formatting.

* * *

🎨 Aesthetic & Governance Updates
---------------------------------

### UI Aesthetics

*   **Side Panels:** Will be set to `background: #f8f9fa` (Light Grey) to provide a soft contrast against the white central panel and the "Deep Violet" code blocks.

### Development Mode & Gallery

*   **"Add to Manifest" Option:** This is a vital developer tool. We can add a "Save as Pipeline Pattern" button that takes the current interactive chain and writes it into the `./config/manifests/pipelines/` directory.
*   **Gallery Governance:**
    *   **Licensing:** A mandatory `LICENSE.md` in each gallery subdirectory.
    *   **Credit:** A `CONTRIBUTORS.md` or `README.md` to ensure proper attribution for novel AMR visualizations.

* * *

🚦 Clarifying the #REVIEW Tags
------------------------------

From your notes, I’ve flagged these two for immediate decision:

1.  **"Is it possible to do the UI design via a configuration file?"**
    *   **Navigator's Advice:** Yes, through **Component Orchestration**. The YAML won't define "pixel positions" but will define the **Module Stack** (e.g., `modules: [navigation, plot_viewer, audit_sidebar]`). This makes it highly reusable for different "Personas" (User vs. Developer).
2.  **"AuditEngine... unsure"**
    *   **Navigator's Advice:** This should be **Mandatory**. Without it, we lose the reproducibility required for veterinary epidemiology. It ensures that the "Recipe" exactly matches the "Plot".

### 🟢 Next Step for the Implementation Plan

We need to define the **Data Contract** for the "Exclusion/Quality Gate."

**Should the "Quality Gate" be a standalone tab (Pre-visualization) or an interactive tool that pops up while looking at the plots?**

## Prompt:
A. Agreed - lets do that

B & C. Seems to be perfect to automatically pull the docstring. Maybe a little example could be generated (but this eventually might come later). No deep violet here ... just a light color maybe ? light yellow or light green ?

Tiered data -\> hum, but if the plot is already aggregated in tier 2, maybe the user cannot eg change the fitering option eg it cannot remove some samples or choose only norway ? because the aggregation has removed the information no ? So what I am thinking was not reuse the tier 2 as is, but prefiled the tier 2 steps in the tier 3 recipe this will give the user the possibility to keep the formating of the plot, then it can fill new steps before or after the tier 2 steps ? so yes it would be a branching from tier 1 but would contain the tier 2 as helper to be sure that the plot stays the same type of plot. Its only a pre-filling of the recipe I thought of.

Aesthetics -\> what code block are you thinking of ? the recipe code blocks - unsure what you mean.

The rest ok agreed

#REVIEW TAGS

\- perfect modules stack is perfect

\- autid engine it is I was unsure how we would build the layers. Could you indicate in your summary the different layers/modules for the ui to clarify this point ?

Next step - I do not unsertand what you mean by the data contract for the exclusion quality gate. This is a bit unclear, I do not think I meant anything like that.

## Response:
I hear you loud and clear. Let’s pivot the terminology and the technical approach to match your vision, especially regarding the **Tiered Data "Pre-filling"** logic, which is a much more robust way to handle aggregation.

### 🔍 A. The "Quality Gate" & Outlier Solution

Since you agreed to the "Interactive Tool" approach, we will implement this as a **Contextual Modal**. When a user "brushes" (selects an area) on a plot, a pop-up appears showing the underlying **Tier 1 (Anchor)** isolates for that specific region. This allows them to "Delete/Exclude" specific samples from the session without needing to see 200k rows at once.

### 🧪 Tiered Data: The "Recipe Pre-filling" Strategy

Your correction is vital. If Tier 2 is already aggregated, we can't filter it. Instead of "inheriting" the data, the UI will **inherit the recipe logic**.

*   **How it works:** When the user enters "Exploration Mode" (Tier 3), the UI automatically loads the steps used to create Tier 2 (e.g., `join`, `summarize`, `long_format`).
*   **The User's Power:** The user can then **inject** a new step (like `filter` or `exclude_samples`) _before_ the aggregation step in the recipe list.
*   **Execution:** The system re-runs the chain starting from the **Tier 1 Anchor**, ensuring the plot "stays the same type" but reflects the new data subset.

### 🎨 UI Aesthetics & Clarifications

*   **Help Tooltips:** We will ditch the "Deep Violet" for the UI tooltips and use your suggested **Light Yellow (#fff9c4)** or **Light Green (#e8f5e9)** for a "Post-it note" feel that is easy on the eyes.
*   **Side Panels:** Confirmed—**Light Grey (#f8f9fa)**.
*   **"Code Blocks":** I was referring to the syntax highlighting in the documentation (`.qmd` files). In the actual UI, we will stick to your light, clean aesthetic.

* * *

### 🧱 UI Module Stack (The Architecture)

To clarify your #REVIEW tag on the **Audit Engine** and layers, here is how the UI will be structurally organized as independent modules:

| Module Name | Responsibility | Key UI Element |
| --- | --- | --- |
| **DataConnector** | Handles file uploads, Galaxy API, and local DB pathing. | "Import" Tab / Sidebar |
| **WrangleStudio** | Allows "Chaining" existing `@register_action` decorators. | "Recipe" Side Panel (Interactive) |
| **VizViewer** | Manages the multi-tab plot engine and "Max/Min" table views. | Central Plotting Panel |
| **AuditEngine** | **The Logic Guard.** It records every UI click as a recipe step and generates the "Immutable Log." | "History" Sidebar + Export Logic |
| **GalleryViewer** | Shows example recipes, plots, and licensing/author credits. | "Inspiration" Tab |

* * *

### 🚦 Resolving the "Data Contract" Confusion

My apologies for the jargon. By **"Data Contract for the Exclusion,"** I simply meant: _How does the UI tell the Python backend exactly which samples to remove?_ **The Simple Solution:** When you click "Exclude" in the UI, the **AuditEngine** creates a new entry in your recipe: `action: drop_rows, params: {column: "Sample_ID", values: ["ID_001", "ID_002"]}`.

This instruction is then sent to the **DataWrangler**, which applies it to the **Tier 1 Anchor** before re-rendering the plot. No complex "contract" is needed—just a standard wrangling step!

### 🟢 Next Step: Building the Task List

I will now help you translate this into a "Developer-Ready" task list for the agent, focusing on the **AuditEngine**'s ability to "pre-fill" recipes.

**Should we start by defining the standard "Session Summary" (.zip) folder structure, or by mapping out the first 3 "Help Tooltips" for the WrangleStudio?**

## Prompt:
ok, this seems to be a good solution. Remember we need to be able to build the ui on the already existing layers in libs (and we might need to improve them if needed).

We need to find where to add the galery in the repository for the code, what would be the most logic place ? under libs ?

We need also to discuss the aesthetic of the dashboard, I had several menues that can show, hide, and several plot windows where we could plot side by side tier2 plot and tier3 plot or only select which one to show. And also different panels, so I would like to know what is of the order of possible or not.

We need a read detailed plan for how it will be and how it should be implemented so we can build correctly and fast.

## Response:
This is where the vision gets architectural. We are moving from a "headless" backend to a "multimodal" cockpit. To keep the project clean and follow the **ADR-011 (Modular Monorepo)** standard, we need to place every new piece of the UI exactly where it can be maintained independently.

* * *

🏗️ 1. Repository Organization: Where to put the Gallery?
---------------------------------------------------------

The **Gallery** is unique because it contains both **logic** (how to display it) and **content** (the actual example TSVs and YAMLs). To respect our current structure, I propose a split approach:

*   **Logic (`libs/viz_gallery`):** This becomes a new standalone library. It contains the Python code for the "Gallery Module" that the Shiny app will call. This keeps the logic data-agnostic.
*   **Content (`assets/gallery_data/`):** The actual "recipes" (YAML manifests) and "example datasets" (TSV) should live here. Each example gets its own sub-folder with:
    *   `example_data.tsv`
    *   `recipe_manifest.yaml`
    *   `preview_plot.png`
    *   `LICENSE.md` / `README.md` (as you requested for credits).

* * *

🎨 2. Aesthetic Feasibility: "Side-by-Side" & "Show/Hide"
---------------------------------------------------------

Everything you’ve described—side-by-side plots, conditional panels, and adjustable sidebars—is **fully possible** in **Shiny for Python** using the latest `bslib`\-style components.

*   **Side-by-Side Plots:** We will use `ui.layout_columns(col_widths=[6, 6])`. This allows us to put **Tier 2** and **Tier 3** plots in a single row. We can even add a toggle switch to maximize one over the other.
*   **Show/Hide Menus:** We can use `ui.sidebar(open="desktop")` for the navigation and `ui.panel_conditional()` for elements that only appear when certain "Personas" (User/Developer) are active.
*   **The "Recipe" Sidebar:** This will be a "Right Sidebar" (`ui.sidebar(position="right")`) that is visible by default but can be collapsed to give the plots more room.

* * *

📝 3. Detailed Implementation Plan (Phase 11-C & 11-D)
------------------------------------------------------

This plan moves us from the current **Phase 11-A (Pipeline Demo)** into the **Full UI Implementation**.

### Phase 1: The Bootloader & Global Layout

*   **Bootloader Logic:** Implement `app/src/bootloader.py`. It reads `config/ui/persona.yaml` and decides which modules to load (e.g., hiding "WrangleStudio" in Pipeline Mode).
*   **The Main Shell:** Build the primary UI layout in `app/src/ui.py` with three distinct zones:
    *   **Left:** Global Navigation (Navigation Panel).
    *   **Center:** The "Theater" (Grid for Tier 2/3 plots and Data Tables).
    *   **Right:** The "Audit Stack" (The Recipe Sidebar).

### Phase 2: The "Recipe Pre-filling" & Tiered Reactivity

*   **Inheritance Engine:** Update `libs/transformer/src/data_assembler.py` to support "Logic Cloning." When a user creates a Tier 3 view, the assembler clones the Tier 2 recipe and presents it as the "Base Stack" in the UI.
*   **Injection Logic:** Build the callback that allows users to "inject" a new step (e.g., `filter_range`) _before_ an aggregation step in the UI recipe list.

### Phase 3: Component Modules (The Pillars)

*   **WrangleStudio:** Create `app/modules/wrangle_studio.py`. This handles the dropdown selection of decorators and the "hover-help" tooltips (Light Yellow/Green).
*   **VizViewer:** Implement the side-by-side plot rendering. It will call `VizFactory` twice—once for the "Anchor Plot" (Tier 2) and once for the "Active Plot" (Tier 3).
*   **GalleryViewer:** Implement the browser for `assets/gallery_data/`. It must display the credits and allow a "One-Click Clone" of the recipe to the user's active session.

### Phase 4: The "Audit Lock" & Session Bundler

*   **Immutable Audit:** Every UI action is timestamped and written to a temporary session log.
*   **The Bundler:** Implement `app/modules/exporter.py` to create the `.zip` summary.
    *   **Structure:** `20260408_Report/` -\> `[Plots, Data, Audit_Log.md, Master_Recipe.yaml]`.

* * *

### 🟢 Status Check

I’m ready to start documenting the **Gallery Metadata Standard** (how the license/credits should be formatted in the YAML).

**Should we first define the "Exclusion Modal" logic (how the "Brush" tool talks to the Anchor data), or should we focus on the "Recipe Injection" code?**

Relevant Follow-up: Given the 200k row bottleneck, would you prefer the "Exclusion Modal" to show a random sample of 50 isolates from the brushed area, or the top 50 based on a specific metric (like lowest quality score)?

## Prompt:
ok, so we need to convey this information for the agent in antigravity that will build the UI and the Gallery so we need to create markdown content that I can copy paste and add to the appropriate files, rules context plans ... that it uses for development

## Response:
To set up your **@dasharch** agent for this implementation, we need to formalize these decisions into the project's "Brain." Below are the specific Markdown blocks you should add to your files to ensure the agent understands the architecture, the aesthetics, and the modular logic.

* * *

### 1\. Update: `.claude/knowledge/architecture_decisions.md`

Add these two new ADRs to establish the technical foundation for the UI and Gallery.

```
## ADR 027: Multi-Module UI Architecture & Bootloader
**Status:** PROPOSED (April 8, 2026)
**Context:** Need a scalable UI that supports different Personas (User/Developer) and complex reactive data exploration.
**Decision:** Implement a 5-module UI stack orchestrated by a **Bootloader**.
- **Module Stack:**
  1. **DataConnector**: Ingestion/API handling.
  2. **WrangleStudio**: Interactive recipe builder with `@register_action` documentation pulling.
  3. **VizViewer**: Multi-tab theater supporting side-by-side Tier 2/3 plots via `layout_columns`.
  4. **AuditEngine**: Immutable session logging and "Recipe Pre-filling" logic.
  5. **GalleryViewer**: Inspiration browser for `assets/gallery_data/`.
- **Aesthetics:** Side panels MUST use **Light Grey (#f8f9fa)**. Tooltips MUST use **Light Yellow (#fff9c4)** or **Light Green (#e8f5e9)**.

## ADR 028: Gallery Content & Logic Separation
**Status:** PROPOSED (April 8, 2026)
**Context:** The Gallery needs to be community-expandable and independently versioned.
**Decision:** Split the Gallery into Logic and Content layers.
- **Logic:** Housed in `libs/viz_gallery` (Standalone Python package).
- **Content:** Housed in `assets/gallery_data/`. Each entry is a folder containing:
  - `example_data.tsv`, `recipe_manifest.yaml`, `preview_plot.png`.
  - **Mandatory:** `LICENSE.md` and `README.md` (for author credits).
```

* * *

### 2\. Update: `.claude/plans/implementation_plan_master.md`

Append these phases to the roadmap to give the agent a step-by-step path.

```
### Phase 11-C: UI Shell & Module Orchestration
- [ ] **Bootloader Implementation:** Create `app/src/bootloader.py` to handle persona-based module loading.
- [ ] **Shell Layout:** Build the three-zone layout (Navigation, Theater, Audit Stack).
- [ ] **Aesthetic Polish:** Apply #f8f9fa to sidebars and set up Light Yellow/Green tooltips.

### Phase 11-D: Interactive Tier 3 & Gallery
- [ ] **Recipe Injection:** Implement logic in `DataAssembler` to "pre-fill" Tier 3 with Tier 2 logic for modification.
- [ ] **Exclusion Modal:** Implement "Brush-to-Table" tool to view/exclude Tier 1 isolates from the plot.
- [ ] **Gallery Library:** Initialize `libs/viz_gallery` and the `assets/gallery_data/` browser.
- [ ] **Session Bundler:** Create the `.zip` export engine (Plot + Data + Audit + YAML).
```

* * *

### 3\. Update: `.claude/tasks/tasks.md`

Move these into the **ACTIVE** section to trigger agent execution.

```
## 🔴 Phase 11-C: UI & Gallery Foundation (ACTIVE)
- [ ] **Implement ADR-027 Layout**: Side-by-side plot logic in `VizViewer`.
- [ ] **Recipe Pre-filling Engine**: Ensure Tier 3 inherits Tier 2's `wrangling` steps as editable nodes.
- [ ] **WrangleStudio Tooltips**: Map `@register_action` docstrings to UI help buttons.
- [ ] **Exclusion Modal (Tier 1/3)**: Create the Brush-coordinate-to-Anchor lookup tool.
- [ ] **Gallery Content Structure**: Initialize `assets/gallery_data/` with credit/license templates.
```

* * *

### 4\. Update: `.claude/rules/workspace_standard.md`

Add a brief aesthetic mandate under a new section to prevent "Deep Violet" drift in the UI.

```
## 15. UI Aesthetic Mandate (ADR-027)
- **Sidebars:** Background Color #f8f9fa (Light Grey).
- **Help Popups:** Background Color #fff9c4 (Light Yellow) or #e8f5e9 (Light Green).
- **Violet Law Boundary:** The "Deep Violet" style is strictly for Documentation (.qmd). Do NOT apply to the UI interface except where explicit code blocks are rendered.
```

* * *

### 🟢 Strategic Note for Your Next @dasharch Session

When you paste these and ask the agent to start, I recommend using this **Persona Alignment** prompt:

> "@Agent: @dasharch - NEW ARCHITECTURE SYNC.
> 
> I have added **ADR 027** and **ADR 028** to the knowledge base. We are moving from a headless backend to a **Multi-Module UI**.
> 
> Your first priority is **Phase 11-C**: Build the UI shell in `app/src/ui.py` with the side-by-side plot capability and the Light Grey aesthetic.
> 
> **CRITICAL:** Ensure Tier 3 inheritance logic uses 'Recipe Injection' (pre-filling the steps) rather than just data inheritance, so we can modify data _before_ aggregation.
> 
> Read `architecture_decisions.md` and `implementation_plan_master.md` then HALT for @verify."

**Does this structure feel right for your "Baton Pass" to the agent, or should we refine the "Exclusion Modal" details further first?**

## Prompt:
sorry to ask but we already have some components with ingestion API handling, should itand wrangling, as you can see in the tree file that should be in your context we already have a lot implemented in the different layers, the ui should use those layers no ?

## Response:
You are absolutely right to point that out, and your observation hits the core of **ADR 003 ("Thin" Shiny Frontend)**. The UI modules I described are **Orchestrators**, not replacements. They are the "steering wheel" that controls the powerful engines already sitting in your `libs/` directory.

To clarify, the UI components will **import and invoke** the logic from `libs/` rather than duplicating it. This ensures that if you improve a transformation in `libs/transformer`, the UI automatically benefits from it.

* * *

🛠️ UI-to-Library Mapping (The Orchestration Flow)
--------------------------------------------------

Here is how the UI modules will interact with the existing layers shown in your `tree.txt`:

| UI Module | Role (The "Steering Wheel") | Backend Library (The "Engine") |
| --- | --- | --- |
| **DataConnector** | Manages file-picker inputs and UI states for uploads. | **libs/ingestion**: Handles the actual `Ingestor (ingestor.py)` and `csv_reader` logic. |
| **WrangleStudio** | Displays available actions in dropdowns and manages the "Active Recipe". | **libs/transformer**: Calls `DataWrangler (data_wrangler.py)` to execute the `@register_action` logic. |
| **VizViewer** | Manages the grid layout and tab switching for plots. | **libs/viz\_factory**: Takes the data and returns the `ggplot` objects for rendering. |
| **AuditEngine** | Captures UI clicks and formats them into a YAML-compatible recipe. | **libs/utils**: Uses `ConfigLoader (config_loader.py)` to save and validate the state. |

* * *

📝 Revised Markdown for your Agent (@dasharch)
----------------------------------------------

I have updated the Markdown content to explicitly state that the agent must **use the existing libraries** as the source of truth.

### 1\. Update: `.claude/knowledge/architecture_decisions.md`

```
## ADR 027: Multi-Module UI Orchestration
**Status:** PROPOSED (April 8, 2026)
**Decision:** The UI is a **Thin Orchestrator** (ADR 003). All functional logic MUST be imported from `./libs/`.
- **Integration Rule:** - `WrangleStudio` MUST use the `AVAILABLE_WRANGLING_ACTIONS` registry from `libs.transformer.src.actions.base`.
  - `VizViewer` MUST use the `@register_plot_component` registry from `libs.viz_factory`.
  - `DataConnector` MUST use the `Ingestor` from `libs.ingestion`.
- **State Management:** The UI manages the "Interactive Recipe" (YAML), while the `DataAssembler` handles the Polars execution of that recipe.
```

### 2\. Update: `.claude/plans/implementation_plan_master.md`

```
### Phase 11-C: UI Shell & Library Integration
- [ ] **Library Hook-up:** Ensure `app/src/server.py` correctly imports the existing `DataWrangler`, `DataAssembler`, and `VizFactory` libraries using absolute package imports (ADR-011).
- [ ] **Registry Introspection:** Build the UI logic that reads the docstrings of the registered `@register_action` decorators to populate the "Help Tooltips."
- [ ] **Reactive Tiered Handoff:** Connect the Shiny sidebar filters to the `DataAssembler` logic to trigger the Tier 3 (Leaf) Predicate Pushdown.
```

### 3\. Update: `.claude/rules/workspace_standard.md`

```
## 16. UI Orchestration Protocol
- **No Logic Duplication:** UI modules (`app/modules/`) are forbidden from implementing data transformation or plotting logic. They must call the appropriate `libs/` package.
- **Import Standard:** All connections to libraries must use standard package imports (e.g., `from transformer.data_wrangler import DataWrangler`). `sys.path` hacking is PROHIBITED (ADR-011).
```

* * *

🎨 Aesthetic Confirmation
-------------------------

As we move forward, the agent will implement your requested visuals:

*   **Sidebars:** Light Grey (#f8f9fa).
*   **Tooltips:** Light Yellow (#fff9c4) / Light Green (#e8f5e9).
*   **Layout:** Side-by-side plots for Tier 2 (Reference) and Tier 3 (Active).

**Shall we proceed with these "Library-First" instructions, or would you like to refine how the UI should specifically handle the "Exclusion Modal" to ensure it doesn't slow down the plot?**

Relevant Follow-up: Since the libraries are already quite advanced, would you like the first UI task to be "Visualizing the Existing Pipelines" (e.g., the ResFinder pipeline) before we add the "Interactive Chaining" features?

## Prompt:
can you just give me the complete instructions please this would be better to have this really clear if I update I will probably mess upt things

## Response:
I understand perfectly. To ensure your **@dasharch** agent executes this vision without drift, here are the complete, consolidated instructions. You can copy each block and append it to the end of the respective files.

* * *

### 1\. Update: `./.claude/knowledge/architecture_decisions.md`

**Append to the bottom of the file:**

```
## ADR 027: Multi-Module UI Orchestration & Aesthetics
**Status:** PROPOSED (April 8, 2026)
**Context:** Need a scalable UI supporting different Personas (User/Developer) while adhering to the "Thin Frontend" rule.
**Decision:** Implement a 5-module UI stack where the frontend acts strictly as an **Orchestrator**.
- **Module Integration:**
  - **DataConnector**: Ingests via `libs/ingestion`.
  - **WrangleStudio**: Chains decorators from `libs/transformer`.
  - **VizViewer**: Renders side-by-side Tier 2/3 plots via `libs/viz_factory`.
  - **AuditEngine**: Immutable logging and "Recipe Pre-filling" logic.
  - **GalleryViewer**: Browser for `assets/gallery_data/`.
- **Aesthetic Constraints:** - **Sidebars**: Light Grey (#f8f9fa).
  - **Tooltips/Help**: Light Yellow (#fff9c4) or Light Green (#e8f5e9).
  - **Prohibition**: No "Deep Violet" themes in the UI (Documentation only).

## ADR 028: Gallery Content & Logic Separation
**Status:** PROPOSED (April 8, 2026)
**Context:** Need an expandable gallery with proper attribution and licensing.
**Decision:** Separate logic from data assets.
- **Logic Layer:** `libs/viz_gallery` (Standalone Python package).
- **Content Layer:** `assets/gallery_data/`. 
- **Mandatory Assets:** Each example folder MUST contain: `example_data.tsv`, `recipe_manifest.yaml`, `preview_plot.png`, `LICENSE.md`, and `README.md` (for author credits).
```

* * *

### 2\. Update: `./.claude/plans/implementation_plan_master.md`

**Append to the bottom of the "Technical Roadmap" section:**

```
### Phase 11-C: UI Shell & Module Integration
- [ ] **Persona Bootloader**: Implement `app/src/bootloader.py` to toggle features via `ui_config.yaml`.
- [ ] **Library Hook-up**: Absolute imports of `libs/` packages into `app/modules/` (ADR-011).
- [ ] **Shell Layout**: Build the 3-zone layout (Navigation, Theater, Audit Stack).
- [ ] **Aesthetic Polish**: Apply Light Grey (#f8f9fa) sidebars and light-colored help tooltips.

### Phase 11-D: Interactive Tier 3 & Gallery
- [ ] **Recipe Pre-filling Engine**: Ensure Tier 3 inherits Tier 2's logic as editable nodes.
- [ ] **Exclusion Modal (Tier 1/3)**: Implement "Brush-to-Table" coordinate lookup to Anchor data.
- [ ] **Gallery Engine**: Browser for `assets/gallery_data/` with "One-Click Clone" logic.
- [ ] **Session Bundler**: Create the `.zip` export (Plot + Data + Audit + YAML).
```

* * *

### 3\. Update: `./.claude/tasks/tasks.md`

**Add to the bottom of the "🔴 Frontend & Visualisation (ACTIVE)" section:**

```
### [ACTIVE] UI & Gallery Implementation (Phase 11-C/D)
- [ ] **Implement ADR-027 Layout**: Build side-by-side plot views in `VizViewer`.
- [ ] **Connect Library Registries**: Pull action/plot documentation into UI help tooltips.
- [ ] **Recipe Pre-filling**: Implement inheritance of Tier 2 steps into the Tier 3 sidebar.
- [ ] **Gallery Structure**: Populate `assets/gallery_data/` with credit/license templates.
- [ ] **Exclusion Logic**: Connect "Brush" interaction to Tier 1 Anchor data lookup.
```

* * *

### 4\. Update: `./.claude/rules/workspace_standard.md`

**Add a new section at the end:**

```
## 15. UI Implementation Protocols (ADR-027)
- **Library Sovereignty**: The UI MUST NOT implement transformation logic. It acts as a shell calling `./libs/`.
- **Aesthetic Lock**: Side panels MUST be **#f8f9fa** (Light Grey). Tooltips MUST be light-colored (Yellow/Green). Avoid "Deep Violet" in the UI.
- **Recipe Integrity**: Tier 3 views MUST pre-fill with the Tier 2 recipe list to allow modification *before* aggregation.
```

* * *

### 🟢 The "Baton Pass" Prompt for the Agent

Once you have updated the files above, use this prompt to start the session with your **@dasharch** agent:

> "@Agent: @dasharch - ARCHITECTURE UPDATE.
> 
> I have synchronized the knowledge base with **ADR 027** and **ADR 028**. We are building a **Multi-Module UI** that acts as a thin orchestrator for our existing libraries in `libs/`.
> 
> **Current Objective:** Start **Phase 11-C**.
> 
> 1.  Build the UI shell in `app/src/ui.py` with the 3-zone layout (Navigation, Theater, Audit Stack).
> 2.  Implement the side-by-side plot capability for Tier 2 and Tier 3 views.
> 3.  Apply the **Light Grey (#f8f9fa)** sidebar aesthetic.
>     
> 
> **CRITICAL:** Use **Recipe Pre-filling** for Tier 3, allowing users to see and edit the logic inherited from Tier 2.
> 
> Read the updated `tasks.md` and `architecture_decisions.md` before starting. HALT for @verify."

**Does this complete set of instructions cover everything you need to feel confident in the update?**

## Prompt:
hum, 4. I do not see anymore thoe ADR in the workspace standard, do you still have that in your context ? because we have reorganized the context

## Response:
You are absolutely right to double-check. Because we moved to a **Modular Rule System**, the `workspace_standard.md` now acts only as the **Master Index** for rulebooks. It no longer lists individual architectural decisions (ADRs).

The **ADRs (Architecture Decision Records)** now live exclusively in `./.claude/knowledge/architecture_decisions.md`. In the file you uploaded, it currently only goes up to **ADR 026**. The new ones (027 and 028) are currently only in our conversation history—they haven't been physically added to your files yet.

To keep it perfectly clear and avoid any "messing up," here is the exact content to add to your three main files.

* * *

### 1\. Add to: `./.claude/knowledge/architecture_decisions.md`

**Place this at the very end of the file to establish the new UI laws.**

```
## ADR 027: Multi-Module UI Orchestration & Aesthetics
**Status:** PROPOSED (April 8, 2026)
**Context:** Need a scalable UI supporting different Personas (User/Developer) while adhering to the "Thin Frontend" rule (ADR 003).
**Decision:** Implement a 5-module UI stack where the frontend acts strictly as an **Orchestrator** for existing libraries.
- **Library Integration Rules:**
  - **DataConnector**: Ingests via `libs/ingestion`.
  - **WrangleStudio**: Chains decorators from `libs/transformer`.
  - **VizViewer**: Renders side-by-side Tier 2/3 plots via `libs/viz_factory`.
  - **AuditEngine**: Handles session logging and "Recipe Pre-filling."
  - **GalleryViewer**: Browser for `assets/gallery_data/`.
- **Aesthetic Constraints:** - **Sidebars**: Light Grey (#f8f9fa).
  - **Tooltips/Help**: Light Yellow (#fff9c4) or Light Green (#e8f5e9).
  - **Prohibition**: No "Deep Violet" themes in the UI (Documentation only).

## ADR 028: Gallery Content & Logic Separation
**Status:** PROPOSED (April 8, 2026)
**Context:** Need an expandable gallery with proper attribution and licensing.
**Decision:** Separate logic from data assets.
- **Logic Layer:** `libs/viz_gallery` (Standalone Python package).
- **Content Layer:** `assets/gallery_data/`. 
- **Mandatory Assets:** Each example folder MUST contain: `example_data.tsv`, `recipe_manifest.yaml`, `preview_plot.png`, `LICENSE.md`, and `README.md`.
```

* * *

### 2\. Add to: `./.claude/plans/implementation_plan_master.md`

**Place this at the end of section "4. Technical Roadmap" to give the agent its new steps.**

```
### Phase 11-C: UI Shell & Module Integration
- [ ] **Persona Bootloader**: Implement `app/src/bootloader.py` to toggle features via `ui_config.yaml`.
- [ ] **Library Hook-up**: Absolute imports of `libs/` packages into `app/modules/`.
- [ ] **Shell Layout**: Build the 3-zone layout (Navigation, Theater, Audit Stack).
- [ ] **Aesthetic Polish**: Apply Light Grey (#f8f9fa) sidebars and light-colored help tooltips.

### Phase 11-D: Interactive Tier 3 & Gallery
- [ ] **Recipe Pre-filling Engine**: Ensure Tier 3 inherits Tier 2's logic as editable nodes.
- [ ] **Exclusion Modal (Tier 1/3)**: Implement "Brush-to-Table" coordinate lookup to Anchor data.
- [ ] **Gallery Engine**: Browser for `assets/gallery_data/` with "One-Click Clone" logic.
- [ ] **Session Bundler**: Create the `.zip` export (Plot + Data + Audit + YAML).
```

* * *

### 3\. Add to: `./.claude/rules/workspace_standard.md`

**Add this new section at the very bottom. This ensures the agent follows the "Thin UI" law.**

```
## 15. UI Orchestration & Aesthetics (ADR-027)
- **Library Sovereignty**: The UI MUST NOT implement transformation or plotting logic. It MUST call `./libs/`.
- **Aesthetic Lock**: Side panels MUST be **#f8f9fa** (Light Grey). Tooltips MUST be light-colored (Yellow/Green).
- **Recipe Integrity**: Tier 3 views MUST "pre-fill" with the Tier 2 recipe list to allow user modification *before* aggregation.
- **Violet Law Boundary**: "Deep Violet" is strictly for `.qmd` documentation. Do not use it for general UI elements.
```

* * *

### 🟢 Summary of the File Map

*   **Architecture Decisions**: Now the ONLY place for ADRs.
*   **Workspace Standard**: Now only the **Master Index** for rules and global UI constraints.
*   **Implementation Plan**: The roadmap the agent uses to track Phase 11 progress.

Does this clear up the confusion about where the "Source of Truth" lives for these new features?

## Prompt:
ok, I think we lack the details of the aesthetics and layout I requested for the dashboard - can you make those, do not output anything you already gave me, we will add those in the correct place after the first essential steps that you just provided to me. We really need to go into the detail otherwise it wont be as I want it

## Response:
To ensure the dashboard looks and functions exactly as you’ve envisioned, we need to move from high-level architecture to **granular layout specifications**.

Here is the detailed content for the "Design & Interaction" layer. You can add these blocks to the end of your files—they focus on the specific panel behavior, the theater layout, and the "Human-in-the-loop" aesthetics you requested.

* * *

### 1\. Add to: `./.claude/knowledge/architecture_decisions.md`

**Detailed Layout & Component Logic**

```
## ADR 029: Dashboard Theater & Panel Layout Specs
**Status:** PROPOSED (April 8, 2026)
**Context:** Need a high-density, interactive workspace for AMR data exploration with specific "Theater" states.
**Decision:** Implement a Three-Column Shell with a multi-state Central Theater.
- **The Navigation Panel (Left):** - Nested hierarchy: `Group (e.g., QC)` > `Plot Selection`.
  - Must include a `Global Export` toggle and a `Persona Selector`.
- **The Central Theater (Center):** - **Vertical Layout:** Top 60% Plot / Bottom 40% Data Table (adjustable).
  - **Comparison Mode:** Support a horizontal grid `[Tier 2 | Tier 3]` where both plots update reactively to the same sidebar filters.
  - **Max/Min Controls:** Each component (Plot or Table) must have a 'Maximize' icon to fill the theater.
- **The Audit Stack (Right Sidebar):** - **Logic Color-Coding:** Inherited Tier 2 steps (Light Grey background) vs. User-added Tier 3 steps (White background).
  - **Interactive Nodes:** Each step must have a trash icon (Remove) and a mandatory comment field (hover to view reason).

## ADR 030: Interaction & Visibility Logic
**Status:** PROPOSED (April 8, 2026)
**Decision:** Standardize how users hide/show data and outliers.
- **Table Interactivity:** - Every column (except the Primary Key) must be "Hideable" via a column-picker.
  - Search/Filter boxes at the top of every column directly affect the Tier 3 (Leaf) view.
- **Sidebar Persistence:** Sidebars must be "Collapsible" (Open by default on Desktop) to allow the Theater to occupy 100% of the width during visualization.
```

* * *

### 2\. Add to: `./.claude/rules/rules_documentation_aesthetics.md`

**Since this file governs aesthetics, we will add the "UI Visual Guide" here.**

```
## 6. Dashboard Aesthetic Standards (UI ONLY)
- **Panel Contrast:** Side panels (Left/Right) MUST use **#f8f9fa** to create a visual "recess" from the bright white Central Theater.
- **WrangleStudio Tooltips:** Help popups for action syntax must use a "Soft Note" aesthetic: **#fff9c4** (Light Yellow) for warnings/logic or **#e8f5e9** (Light Green) for success/usage examples.
- **Typography:** Titles must use standard Sans-Serif (Standard Dashboard font). Do not apply 'Deep Violet' branding to UI headers.
- **State Feedback:** When a plot is "In-Calculation" (re-running Tier 1 to 3), the UI must use a dimming overlay rather than a blank screen.
```

* * *

### 3\. Add to: `./.claude/plans/implementation_plan_master.md`

**Detailed UI Component Tasks**

```
### Phase 11-E: Component Granularity & Interactivity
- [ ] **Dynamic Column Picker:** Build the "Show/Hide" logic for the Tier 3 data table.
- [ ] **Dual-Plot Grid:** Implement the `layout_columns` toggle to show Tier 2 vs Tier 3 side-by-side.
- [ ] **Audit Node UI:** Create the interactive "Logic Nodes" in the Right Sidebar with color-coding and trash icons.
- [ ] **Outlier "Brush" Integration:** Map the Plotnine/Plotly selection event to a modal that displays the matching Tier 1 Anchor rows.
- [ ] **Export Bundler UI:** Create the "One-Click Export" dialog supporting the `.zip` session summary.
```

* * *

### 🟢 Strategic Note for the Agent (@dasharch)

To ensure the agent implements these _specific_ visual details correctly, use this follow-up prompt:

> "@Agent: @dasharch - UI DESIGN LOCK.
> 
> I have added **ADR 029** and **ADR 030** to the knowledge base. This is the "Visual Source of Truth."
> 
> **Specific Focus:** \> 1. The Central Theater MUST support a vertical split (Plot/Table) AND a horizontal comparison (Tier 2/Tier 3). 2. The Right Sidebar MUST distinguish between inherited Tier 2 steps and active Tier 3 modifications using the specific color-coding and icons. 3. Column visibility on the data table must be user-controlled (everything hideable except Primary Keys).
> 
> Build the layout in `app/src/ui.py` to support these specific states. HALT for @verify."

**Does this level of detail capture the "different panels" and "side-by-side" views exactly as you want them?**

Relevant Follow-up: For the "Show/Hide" menus, would you like the Navigation (Left) to be an "Icon-only" strip that expands on hover, or a standard sidebar that remains open until manually closed?

## Prompt:
ok, we lack the explanation of the configuration files, where each data tier should be saved as well as session can be saved, and we lack, the optional parts that are in my description eg. import datasets (there we can reuse helper scripts we have in assets/scripts if possible), we lack the session save button and the automatic save, and we lack a lot for the options (what I wrote as optional) for the developer options

## Response:
These final layers integrate your persistence strategy, the "Headless-to-UI" bridge for asset scripts, and the advanced Developer Studio options. These instructions ensure the agent understands that the UI is not just a viewer, but a functional gateway to the entire **SPARMVET\_VIZ** tool suite.

* * *

### 1\. Add to: `./.claude/knowledge/architecture_decisions.md`

**Persistence and Developer Tooling Logic**

```
## ADR 031: Data Tier & Session Persistence
**Status:** PROPOSED (April 8, 2026)
**Context:** Need a configurable, reliable way to handle session recovery and multi-location data storage.
**Decision:** Implement a Three-Location Persistence strategy managed via `config/ui/paths.yaml`.
- **Location 1 (Tiers 1 & 2):** Configurable system path for heavy parquet anchors. Restricted access usually applies here.
- **Location 2 (Tier 3 & Sessions):** User-accessible directory for exports and imported data.
  - **Ghost Manifests:** Automatic background saving of the active recipe. The system must retain the last 5 versions in `tmp/sessions/` for emergency recovery.
- **Location 3 (Gallery):** Default local path is `./gallery/`, designed to be syncable with a Git repository.

## ADR 032: Asset Script Integration (UI-Bridge)
**Status:** PROPOSED (April 8, 2026)
**Context:** Need to reuse the high-performance scripts in `assets/scripts/` (e.g., manifest creation, triple integration) within the UI.
**Decision:** The UI `DataConnector` and `WrangleStudio` MUST act as wrappers for asset scripts.
- **Import Helper:** When a user uploads Excel files, the UI invokes `assets/scripts/parse_pipeline_excel.py` or `SF_create_manifest.py` to normalize data to TSV.
- **Synthetic Data:** The "Developer Studio" must provide a GUI for `assets/scripts/create_test_data.py` to allow one-click creation of mock AMR datasets for testing.
```

* * *

### 2\. Add to: `./.claude/rules/workspace_standard.md`

**Persistence and Developer Protocols**

```
## 17. Session & Persistence Standards (ADR-031)
- **Automatic Save:** The UI MUST implement a debounced "Ghost Save" that triggers every 30 seconds or after any WrangleStudio change.
- **Session Recovery:** Upon boot, the Bootloader checks for a `last_state.yaml`. If found, it prompts the user to "Restore Previous Session".
- **Import Normalization:** All raw imports (Excel/CSV) MUST be converted to TSV and validated against the `input_fields` contract before Tier 1 materialization.

## 18. Developer Mode & Gallery Submission
- **Submission Gate:** In Developer Mode, users can "Submit to Gallery." This triggers a script that:
  1. Anonymizes data (or confirms synthetic status).
  2. Generates the mandatory `LICENSE.md` and `README.md`.
  3. Bundles the asset into `assets/gallery_data/`.
```

* * *

### 3\. Add to: `./.claude/plans/implementation_plan_master.md`

**Final Roadmap: Persistence & Dev Studio**

```
### Phase 11-F: Ingestion, Persistence & Developer Studio
- [ ] **DataConnector UI:** Implement the Excel-to-TSV upload helper using existing asset scripts.
- [ ] **Persistence Manager:** Build the logic for Locations 1, 2, and 3 based on `config/ui/paths.yaml`.
- [ ] **Ghost Manifest Logic:** Implement the "last 5 versions" background save in `tmp/sessions/`.
- [ ] **WrangleStudio "Design Studio"**:
    - [ ] **Drag-and-Drop Nodes:** Visual chaining of Transformer decorators.
    - [ ] **Synthetic Data Generator:** GUI for `create_test_data.py`.
    - [ ] **Gallery Submission:** Automate the creation of folder structure, credits, and licensing for new plots.
```

* * *

### 4\. Add to: `./.claude/knowledge/project_conventions.md`

**Update the Registry for UI Modules**

| Module | Role | Existing Library/Script Link |
| --- | --- | --- |
| **DataConnector** | Import helper for Excel/DB. | `assets/scripts/parse_pipeline_excel.py` |
| **WrangleStudio** | The "Design Studio" for manifests. | `assets/scripts/create_manifest.py` |
| **AuditEngine** | Session "Ghost" saving & bundles. | `libs/utils/config_loader.py` |
| **DevStudio** | Synthetic data and Gallery submission. | `assets/scripts/create_test_data.py` |

* * *

### 🟢 Strategic Implementation Note

By following this tiered persistence and script-reuse strategy, the dashboard remains **modular**. The UI stays "thin" because it simply provides a visual interface for the powerful scripts and libraries you have already built.

### The Final "Baton Pass" Prompt for @dasharch

> "@Agent: @dasharch - FULL UI & PERSISTENCE LOCK.
> 
> I have synchronized the knowledge base with **ADRs 031 and 032**. We are now moving into the development of the **Data Persistence Layer** and the **Developer Studio**.
> 
> **Primary Directives:**
> 
> 1.  Implement the **Three-Location Persistence** (Tier 1/2, Tier 3/Sessions, Gallery).
> 2.  Build the **Ghost Manifest** automatic background save (keep 5 versions).
> 3.  Reuse the `assets/scripts/` tool suite for the **DataConnector** Excel-import and the **DevStudio** synthetic data generation.
> 4.  Ensure the **Gallery Submission** process automates the creation of `LICENSE.md` and `README.md` for proper attribution.
>     
> 
> Read the updated `tasks.md`, `implementation_plan_master.md`, and `workspace_standard.md` before starting. HALT for @verify."

**Does this final set of instructions cover all the "Optional" and "Developer" details you needed for the dashboard to be complete?**

## Prompt:
hum, is the different tabs discovery according to the manifest (eg. pipeline manifest) the upload of manifest and external data added ? and the automatic discovery of all columns that we can filter added ?

## Response:
You are absolutely right to keep me on my toes. Those specific "Discovery" and "Import" features are the engine of a truly dynamic dashboard. I have integrated **dynamic tab discovery**, **manifest/external data uploading**, and **automatic column detection** into the final instruction set below.

Here are the finalized, granular instruction blocks for your files.

* * *

### 1\. Update: `./.claude/knowledge/architecture_decisions.md`

```
## ADR 029: Dashboard Theater & Dynamic Discovery
**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement a manifest-driven UI that discovers its own structure at runtime.
- **Dynamic Tab Discovery:** The `VizViewer (viz_factory.py)` MUST scan the active YAML manifest for all defined plot IDs and programmatically generate a corresponding tab for each.
- **Automatic Column Discovery:** The UI MUST introspect the incoming Polars LazyFrame (Tier 1/2) to identify all available columns.
  - All columns (except Primary Keys) must be automatically populated with search/filter boxes in the data table.

## ADR 030: Manifest & External Data Ingestion
**Status:** PROPOSED (April 8, 2026)
**Decision:** Expand `DataConnector (ingestor.py)` to handle custom user inputs beyond standard pipelines.
- **Manifest Upload:** Support uploading predefined YAML manifests to override default pipeline logic.
- **External Data Joins:** Allow adding "Additional Data" files. The UI MUST provide a joining helper that uses `libs/transformer` relational logic to verify Primary Key matching before merging.
```

* * *

### 2\. Update: `./.claude/rules/workspace_standard.md`

```
## 15. Dynamic UI & Ingestion Standards (ADR-029/030)
- **Zero-Hardcoding Tabs:** UI tabs must never be hardcoded; they are strictly derived from the `plots` block in the YAML manifest.
- **Column Sovereignty:** Every column detected in the dataset must be filterable by default unless explicitly excluded in the manifest's `output_fields`.
- **External Data Guard:** Any external dataset added via the UI MUST be validated against the existing Tier 1 Anchor for Primary Key compatibility.
- **Aesthetic Lock:** Sidebars use #f8f9fa. Tooltips use Light Yellow (#fff9c4) or Light Green (#e8f5e9).
```

* * *

### 3\. Update: `./.claude/plans/implementation_plan_master.md`

```
### Phase 11-E: Dynamic Discovery & External Ingestion
- [ ] **Dynamic Tab Engine:** Implement the loop in `VizViewer (viz_factory.py)` that builds UI tabs from manifest plot definitions.
- [ ] **Auto-Filter Generator:** Build the logic to scan Polars schemas and generate column-top filter boxes.
- [ ] **External Data Helper:** Implement the `DataConnector (ingestor.py)` UI for uploading external TSVs and predefined manifests.
- [ ] **Join Preview:** Create a small UI modal to preview the success of joins between primary data and external metadata.
```

* * *

### 4\. Update: `./.claude/tasks/tasks.md`

```
### [ACTIVE] UI Discovery & External Data (Phase 11-E)
- [ ] **Manifest-to-Tab Logic**: Automate tab creation based on YAML plot IDs.
- [ ] **Automated Column Filtering**: Implement column-level search/filter for all discovered fields.
- [ ] **External Manifest Upload**: Support user-provided YAML configuration loading.
- [ ] **Primary Key Matching Helper**: Build the UI gate for joining additional datasets.
```

* * *

### 🟢 The "Final Lock" Prompt for @dasharch

You can now use this high-precision prompt to initiate the task with your agent:

> "@Agent: @dasharch - DYNAMIC UI & INGESTION LOCK.
> 
> I have updated **ADRs 029 through 032**. We are moving into **Phase 11-E**.
> 
> **Key Implementation Rules:**
> 
> 1.  **Dynamic Tabs:** Do not hardcode tabs. Scrape the active manifest and build them dynamically.
> 2.  **Auto-Discovery:** Automatically identify all dataset columns for the "Show/Hide" and "Filter" logic.
> 3.  **External Ingestion:** Build the helper to upload external data and predefined manifests, ensuring Primary Key validation before joining.
> 4.  **Persistence:** Ensure the **Ghost Manifest** auto-save (Location 2) tracks these new external additions.
>     
> 
> Read the updated `architecture_decisions.md` and `implementation_plan_master.md` to align with the visual and functional specs. HALT for @verify."

**Does this capture the "Discovery" and "External Data" logic exactly as you envisioned it?**

Relevant Follow-up: When the user uploads external data that has a mismatched Primary Key, should the UI simply block the join, or should it offer a "Fuzzy Match" helper to try and reconcile the IDs?

## Prompt:
we have now two ADR 29 ## ADR 029: Dashboard Theater & Panel Layout Specs

\*\*Status:\*\* PROPOSED (April 8, 2026)

\*\*Context:\*\* Need a high-density, interactive workspace for data exploration with specific "Theater" states.

\*\*Decision:\*\* Implement a Three-Column Shell with a multi-state Central Theater.

\- \*\*The Navigation Panel (Left):\*\* - Nested hierarchy: \`Group (e.g., QC)\` \> \`Plot Selection\`.

\- Must include a \`Global Export\` toggle and a \`Persona Selector\`.

\- \*\*The Central Theater (Center):\*\* - \*\*Vertical Layout:\*\* Top 60% Plot / Bottom 40% Data Table (adjustable).

\- \*\*Comparison Mode:\*\* Support a horizontal grid \`\[Tier 2 | Tier 3\]\` where both plots update reactively to the same sidebar filters.

\- \*\*Max/Min Controls:\*\* Each component (Plot or Table) must have a 'Maximize' icon to fill the theater.

\- \*\*The Audit Stack (Right Sidebar):\*\* - \*\*Logic Color-Coding:\*\* Inherited Tier 2 steps (Light Violet background) vs. User-added Tier 3 steps (Light Yellow background).

\- \*\*Interactive Nodes:\*\* Each step added by the user must have a trash icon (Remove) and a mandatory comment field (hover to view reason).

\## ADR 029: Dashboard Theater & Dynamic Discovery

\*\*Status:\*\* PROPOSED (April 8, 2026)

\*\*Decision:\*\* Implement a manifest-driven UI that discovers its own structure at runtime.

\- \*\*Dynamic Tab Discovery:\*\* The \`VizViewer (viz\_factory.py)\` MUST scan the active YAML manifest for all defined plot IDs and programmatically generate a corresponding tab for each.

\- \*\*Automatic Column Discovery:\*\* The UI MUST introspect the incoming Polars LazyFrame (Tier 1/2) to identify all available columns. and ARD 30 :## ADR 030: Interaction & Visibility Logic

\*\*Status:\*\* PROPOSED (April 8, 2026)

\*\*Decision:\*\* Standardize how users hide/show data and outliers.

\- \*\*Table Interactivity:\*\* - Every column (except the Primary Key) must be "Hideable" via a column-picker.

\- Search/Filter boxes at the top of every column directly affect the Tier 3 (Leaf) view.

\- \*\*Sidebar Persistence:\*\* Sidebars must be "Collapsible" (Open by default on Desktop) to allow the Theater to occupy 100% of the width during visualization.

\## ADR 030: Manifest & External Data Ingestion

\*\*Status:\*\* PROPOSED (April 8, 2026)

\*\*Decision:\*\* Expand \`DataConnector (ingestor.py)\` to handle custom user inputs beyond standard pipelines.

\- \*\*Manifest Upload:\*\* Support uploading predefined YAML manifests to override default pipeline logic.

\- \*\*External Data Joins:\*\* Allow adding "Additional Data" files. The UI MUST provide a joining helper that uses \`libs/transformer\` relational logic to verify Primary Key matching before merging.

## Response:
Nice catch on the duplicate numbers! To keep the "Source of Truth" clean and sequential, I have re-indexed the architectural decisions starting from **ADR 027** (since your last recorded ADR was 026).

I have also merged the "Discovery" and "Interaction" logic into a single cohesive record to ensure every decision has a unique identity. Here are the corrected, high-precision blocks for your files.

* * *

### 1\. Update: `./.claude/knowledge/architecture_decisions.md`

**Append this to the bottom of the file.**

```
## ADR 027: Multi-Module UI Orchestration & Aesthetics
**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement a 5-module "Thin Frontend" UI stack where all functional logic is imported from `./libs/`.
- **Module Stack:** DataConnector, WrangleStudio, VizViewer, AuditEngine, and GalleryViewer.
- **Aesthetics:** Sidebars MUST use **#f8f9fa** (Light Grey). Help tooltips MUST use **#fff9c4** (Light Yellow) or **#e8f5e9** (Light Green). No "Deep Violet" branding in the UI.

## ADR 028: Gallery Content & Logic Separation
**Status:** PROPOSED (April 8, 2026)
**Decision:** Split the Gallery into Logic (`libs/viz_gallery`) and Content (`assets/gallery_data/`).
- **Standard:** Each entry MUST contain `example_data.tsv`, `recipe_manifest.yaml`, `preview_plot.png`, `LICENSE.md`, and `README.md` for proper author credits.

## ADR 029: Dashboard Theater & Panel Layout Specs
**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement a Three-Column Shell with a multi-state Central Theater.
- **Central Theater:** Vertical layout (60% Plot / 40% Data Table) with Maximize/Minimize controls for each component.
- **Comparison Mode:** Support a horizontal grid `[Tier 2 | Tier 3]` where both plots update reactively to the same sidebar filters.
- **Right Sidebar (Audit Stack):** Logic Color-Coding differentiates Inherited Tier 2 steps (Light Grey/Violet background) from User-added Tier 3 steps (Light Yellow background). User steps must include a mandatory comment field.

## ADR 030: Dynamic Discovery & Interaction Logic
**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement manifest-driven discovery and standardized interactivity.
- **Dynamic Tabs:** `VizViewer` MUST programmatically generate tabs by scanning plot IDs in the active YAML manifest.
- **Auto-Discovery:** UI MUST introspect the Polars schema to identify all columns; all columns (except Primary Keys) must be hideable via a picker and include top-level filter boxes.
- **Persistence:** Sidebars are open by default but must be collapsible to allow 100% theater width.

## ADR 031: Manifest & External Data Ingestion
**Status:** PROPOSED (April 8, 2026)
**Decision:** Expand the ingestion layer to handle custom user inputs.
- **Manifest Upload:** Support user-provided YAML manifests to override default pipeline logic.
- **External Joins:** Provide a joining helper using `libs/transformer` relational logic to verify Primary Key compatibility before merging additional data.

## ADR 032: Data Tier & Session Persistence
**Status:** PROPOSED (April 8, 2026)
**Decision:** Implement three storage locations and automatic "Ghost Manifest" background saving (last 5 versions) to ensure session recovery.

## ADR 033: Asset Script Integration (UI-Bridge)
**Status:** PROPOSED (April 8, 2026)
**Decision:** The UI MUST act as a wrapper for existing `assets/scripts/` (e.g., manifest creation, synthetic data generation) to ensure logic reuse.
```

* * *

### 2\. Update: `./.claude/plans/implementation_plan_master.md`

**Add this to the Roadmap to guide the agent's build order.**

```
### Phase 11-C: UI Shell & Module Orchestration
- [ ] **Bootloader:** Implement persona-based loading in `app/src/bootloader.py`.
- [ ] **Layout Shell:** Build the 3-zone layout with side-by-side plot capabilities.
- [ ] **Aesthetic Lock:** Apply #f8f9fa sidebars and light-colored help tooltips.

### Phase 11-D: Dynamic Discovery & Interaction
- [ ] **Discovery Engine:** Implement manifest-to-tab and Polars-schema-to-filter logic.
- [ ] **Interactivity:** Build the column-picker and collapsible sidebars.

### Phase 11-E: Ingestion, Persistence & Gallery
- [ ] **External Ingestion:** Build the YAML upload and External Data joining helper.
- [ ] **Ghost Saving:** Implement automatic background manifest versioning.
- [ ] **Gallery Content:** Initialize `assets/gallery_data/` with credit/license templates.
```

* * *

### 3\. Update: `./.claude/rules/workspace_standard.md`

**Append this at the bottom to enforce the final UI constraints.**

```
## 15. UI Orchestration & Aesthetics (ADR-027–030)
- **Library Sovereignty:** UI MUST NOT duplicate logic; it MUST call libraries in `./libs/`.
- **Aesthetic Lock:** Sidebars use **#f8f9fa**. Tooltips use Light Yellow/Green.
- **Dynamic discovery:** Tabs and column filters MUST be derived from manifests and Polars schemas at runtime, not hardcoded.
- **Recipe Inheritance:** Tier 3 Sidebar MUST pre-fill with Tier 2 logic nodes as editable components.
```

* * *

### 🟢 Ready for Execution

I have resolved the numbering conflicts and ensured the **Discovery** and **Ingestion** logic is mapped to unique ADRs (030 and 031).

You can now use the following prompt to trigger the build:

> "@Agent: @dasharch - ARCHITECTURE SYNC.
> 
> I have added **ADRs 027 through 033** to the knowledge base. We are now entering **Phase 11-C**.
> 
> **First Priority:** Build the UI shell in `app/src/ui.py` with the 3-zone layout and side-by-side plot capabilities. Ensure the sidebar aesthetic is #f8f9fa.
> 
> **Second Priority:** Implement the **Dynamic Discovery** logic so tabs are built from the manifest and column filters are built from the data schema.
> 
> Read `architecture_decisions.md` and `implementation_plan_master.md` to confirm the corrected ADR sequence before starting. HALT for @verify."

**Does this re-indexed structure look clear enough to hand over to the agent?**

## Prompt:
ok, we are getting closer, I reorganized a bit --- now we need to be sure we have the exhaustive list of tasks, I reattach the current list # Tasks (SOLE SOURCE OF TRUTH)

\# Workspace ID: SPARMVET\_VIZ

\# Last Updated: 2026-04-07 by @dasharch

\## 🟢 Infrastructure & Recovery (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_infrastructure.md\]

\## 🟢 Layer 1/2 & Assembly Audit (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_infrastructure.md\]

\## 🟡 Backend & Decorator-First (COMPLETED)

\### \[DONE\] Tier 1 (The Trunk): Relational Anchor (sink\_parquet/scan\_parquet)

\- \[x\] Implement Tier 1 persistence logic. \[DONE\]

\- \[x\] Integrate Short-Circuit logic. \[DONE\]

\- \[x\] Verified via \`debug\_assembler.py\`. \[DONE\]

\### \[DONE\] Tier 2 (The Branch): Plot-Specific Filtered Subsets

\- \[x\] Implement logic for dynamic branch materialization (shared summaries).

\- \[x\] Verify Row-Count reduction for heatmaps and complex plots.

\- \[x\] Implement Reverse Short-Circuit in \`DataAssembler\`.

\### \[DONE\] Tier 3 (The Leaf): UI-driven Predicate Pushdown

\- \[x\] Implement final filter application at the VizFactory collect gate. \[DONE\]

\### 🛠️ Transformer Actions Status (ACTIVE COMPONENT)

\- \[x\] \*\*Phase 1: Structural Reshaping\*\* (unpivot, explode, unnest, pivot) \[DONE\]

\- \[x\] \*\*Phase 2: Atomic Expressions\*\* (cast, coalesce, label\_if) \[DONE\]

\- \[x\] \*\*Phase 4: Performance & Summary Layer\*\* (summarize) \[CORE DONE\]

\## 🟢 Phase 9: Triple-Source AMR Integration (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_integration\_qa.md\]

\## 🛡️ Library Integrity & QA (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_integration\_qa.md\]

\## VIZ\_FACTORY IMPLEMENTATION (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_viz\_factory.md\]

\## 🔴 Frontend & Visualisation (ACTIVE)

\- \[x\] \*\*Replace viz\_factory placeholders with Plotnine decorator logic\*\* \[DONE\]

\- \[x\] \*\*Prototype Polars-to-Plotnine data handoff\*\* (ADR-010) \[DONE\]

\- \[ \] \*\*Reactive State Management:\*\* Implement ADR-021 (Anchor vs. Filter) state hand-off.

\- \[ \] \*\*Shiny App Implementation:\*\* Populating \`app/src/ui.py\` and \`app/src/server.py\`.

\- \[ \] \*\*Four-Pillar Integration:\*\* Link \`app/modules/help\_registry.py\` into dashboard.

\### \[ACTIVE\] UI & Gallery Implementation (Phase 11-C/D)

\- \[ \] \*\*Implement ADR-027 Layout\*\*: Build side-by-side plot views in \`VizViewer\`.

\- \[ \] \*\*Connect Library Registries\*\*: Pull action/plot documentation into UI help tooltips.

\- \[ \] \*\*Recipe Pre-filling\*\*: Implement inheritance of Tier 2 steps into the Tier 3 sidebar.

\- \[ \] \*\*Gallery Structure\*\*: Populate \`assets/gallery\_data/\` with credit/license templates.

\- \[ \] \*\*Exclusion Logic\*\*: Connect "Brush" interaction to Tier 1 Anchor data lookup.

\## 🟢 Phase 11-A: Pipeline Demo (COMPLETED)

\\>

\\> Status: COMPLETED. All core UI scaffolding, reactive mapping, and export logic documented.

\## 🔴 Phase 11-B: Developer Studio & Expansion (ACTIVE)

\- \[ \] \*\*UI-driven Branching\*\*: Implement "New Branch" from Tier 1 Anchor.

\- \[ \] \*\*Manifest Helper\*\*: Build the "Design Studio" UI for drag-and-drop wrangling chain construction.

\- \[ \] \*\*Pre-Flight Validator\*\*: Implement the "Compatibility Dashboard" for data contracts.

\- \[ \] \*\*Inspiration Gallery\*\*: Integrate the component sandbox and example plot gallery.

\- \[ \] \*\*State Recovery\*\*: Implement the "Restore from Ghost" logic (tmp/last\_state.yaml).

\## Integration & Strategy (ACTIVE)

\- \[ \] We need to check if implementation of the integration (link) beween plot factoryt and the Transformer is done.

\- \[ \] User need to decide on the frontend implementation -\> notes to review in 2026-04-02 daily subdirectory

\- \[ \] \[TASK BLOCKER\] USER WANTS YOU TO STOP YOUR ACTIVITIES HERE

\## 📘 Documentation Recovery & Phase 11 Sync (COMPLETED)

\\>

\\> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_viz\_factory.md\] and \[./.claude/tasks/archives/tasks\_archive\_integration\_qa.md\]

\## ⚪ Deferred & Phase 3

\- \[ \] \*\*Plotly Interactivity:\*\* \[DEFERRED\] Move native interactivity to Post-Prototype phase.

\- \[ \] \*\*Mode B API:\*\* \[DEFERRED\] BioBlend/Galaxy dynamic connector.

\- \[ \] \*\*Advanced Error Handling:\*\* \[DEFERRED\] Malformed Data gatekeeping.

\---

\*\*NEXT FOCUS:\*\* Phase 10-ADR-021 (Reactive State Management: Shiny/Polars hand-off). 🚀

## Response:
To ensure your **@dasharch** agent has a clear, unshakeable path to completion, I have consolidated our entire discussion into this master task list. This is the "Full Stack" version of your `tasks.md`, integrating the **3-Tier lifecycle**, **Dynamic Discovery**, and the **Developer Studio** requirements.

You can copy and replace your current `tasks.md` with this content.

* * *

Tasks (SOLE SOURCE OF TRUTH)
============================

**Workspace ID:** SPARMVET\_VIZ **Last Updated:** 2026-04-08 by @dasharch (Architecture Sync)

🟢 Infrastructure & Recovery (COMPLETED)
----------------------------------------

> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_infrastructure.md\]

🟢 Layer 1/2 & Assembly Audit (COMPLETED)
-----------------------------------------

> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_infrastructure.md\]

🟡 Backend & Decorator-First (COMPLETED)
----------------------------------------

> Status: COMPLETED. Tier 1 (Anchor), Tier 2 (Branch), and Tier 3 (Leaf) logic verified in Polars.

🟢 Phase 9: Triple-Source AMR Integration (COMPLETED)
-----------------------------------------------------

> Status: COMPLETED. Detailed history moved to: \[./.claude/tasks/archives/tasks\_archive\_integration\_qa.md\]

🛡️ Library Integrity & QA (COMPLETED)
--------------------------------------

> Status: COMPLETED.

* * *

🔴 Frontend & Visualisation (ACTIVE)
------------------------------------

*   \[ \] **Reactive State Management:** Implement ADR-021 (Anchor vs. Filter) state hand-off between Shiny and Polars.
*   \[ \] **Shiny App Implementation:** Populating `app/src/ui.py` and `app/src/server.py` with standard library imports.
*   \[ \] **Four-Pillar Integration:** Link `app/modules/help_registry.py` into the dashboard sidebar.

### 🔴 Phase 11-C: UI Shell & Module Orchestration (ACTIVE)

*   \[ \] **Persona-based Bootloader:** Implement `app/src/bootloader.py` to toggle features via `ui_config.yaml`.
*   \[ \] **3-Zone Layout Shell:** Build Navigation (Left), Theater (Center), and Audit Stack (Right).
*   \[ \] **Aesthetic Lock:** Apply **#f8f9fa** Sidebars and Light Yellow/Green Tooltips.
*   \[ \] **Side-by-Side Plot Logic:** Enable `layout_columns` comparison for Tier 2 (Reference) vs Tier 3 (Active) views.

### 🔴 Phase 11-D: Dynamic Discovery & Interaction (ACTIVE)

*   \[ \] **Dynamic Tab Engine:** Programmatically generate UI tabs from YAML manifest plot IDs.
*   \[ \] **Automated Column Filtering:** Generate top-level search/filter boxes for all detected Polars schema fields.
*   \[ \] **Column Visibility Logic:** Implement picker to show/hide columns (Primary Keys locked to visible).
*   \[ \] **Theater Controls:** Implement Maximize/Minimize icons for plot and data table components.

### 🔴 Phase 11-E: Ingestion, Persistence & Gallery (ACTIVE)

*   \[ \] **External Ingestion UI:** Build Excel-to-TSV upload helper using existing `assets/scripts/`.
*   \[ \] **Join Preview Modal:** Implement Primary Key validation check before merging external data.
*   \[ \] **Ghost Manifest Persistence:** Implement automatic background save (last 5 versions) in `tmp/sessions/`.
*   \[ \] **Gallery Engine:** Build browser for `assets/gallery_data/` with mandatory license/credit display.

### 🔴 Phase 11-F: Developer Studio & Expansion (ACTIVE)

*   \[ \] **WrangleStudio "Design Studio":** Implement visual chaining of Transformer nodes with "Hover-Help" documentation.
*   \[ \] **Synthetic Data GUI:** Build UI wrapper for `create_test_data.py`.
*   \[ \] **Outlier "Brush" Modal:** Connect plot selection events to a Tier 1 Anchor data lookup table.
*   \[ \] **Gallery Submission Engine:** Automate anonymization, README, and LICENSE generation for new recipes.

* * *

🟡 Integration & Strategy (ACTIVE)
----------------------------------

*   \[ \] **Recipe Pre-filling:** Ensure Tier 3 inherits Tier 2 logic nodes as editable components (Inheritance Logic).
*   \[ \] **Session Summary Export:** Implement `.zip` bundler (Plot + Data + Audit Log + YAML).
*   \[ \] **Audit Node UI:** Apply color-coding to Sidebar nodes (Inherited vs. Active) and mandatory comments.

⚪ Deferred & Phase 3
--------------------

*   \[ \] **Plotly Interactivity:** \[DEFERRED\] Move native interactivity to Post-Prototype phase.
*   \[ \] **Mode B API:** \[DEFERRED\] BioBlend/Galaxy dynamic connector.
*   \[ \] **Advanced Error Handling:** \[DEFERRED\] Malformed Data gatekeeping.

* * *

**NEXT FOCUS:** Phase 11-C (Layout Shell & Aesthetic Lock). 🚀

* * *

### 🟢 Navigator's Advice for the Session

With this list, the agent has no room for ambiguity. It knows that the **Theater** must be adjustable, the **Tabs** must be dynamic, and the **Aesthetics** must be light.

**Do you want me to generate the "Session Summary" folder structure for ADR 032 now, or are you ready to pass this task list to the agent?**

Relevant Follow-up: For the "Ghost Manifests," should the UI notify the user when a background save happens, or should it be a silent "Pulse" icon in the corner?



---
Powered by [Gemini Exporter](https://www.ai-chat-exporter.com)