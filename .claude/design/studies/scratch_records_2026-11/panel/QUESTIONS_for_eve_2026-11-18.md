# Questions for Eve, 2026-11-18

19 questions. Each has a default, except question 6. Answer each with one word: a letter, yes or no.
Saying "defaults" accepts every default of part 2 (questions 7 to 19). Part 1 (questions 1 to 6) needs your own word for each item, because it changes the shape of every recipe.
Written by the coordinator's scribe from last night's reports; the defaults are the coordinator's recommendations, not decisions.

---

## PART 1: These free the big build

### 1. Name of the tier container

You decided that a tier is a small block with an optional engine line and the list `steps`. Today the tiers sit inside a container: `steps:` in a join and at a plot, `wrangling:` in a table. Kept as it is, the word `steps` appears twice. Which shape: A, B or C? The answer applies to joins, tables and plots alike.

The same join with one step, three ways:

A (the outer `steps:` stays; the list inside it is `steps:`):
```yaml
steps:
  tier1:
    steps:
      - action: polars_join
        right_ingredient: metadata_schema
```

B (no outer container; the tiers sit at the top):
```yaml
tier1:
  steps:
    - action: polars_join
      right_ingredient: metadata_schema
```

C (the outer `steps:` stays; the inner list has another name, here `actions`; the name is yours):
```yaml
steps:
  tier1:
    actions:
      - action: polars_join
        right_ingredient: metadata_schema
```

- A: keep the outer container. The word `steps` appears twice.
- B: remove the outer container. Shortest. It changes a form you decided earlier (the tier containers), which is why it is asked.
- C: keep the outer container and name the inner list differently. If C, say the word too.

Fact: in every recipe, the containers hold only tier keys. 54 included files start with `tier1:`.

One consequence of B to know: today an included file holds all tiers of a table or a join (it starts with `tier1:`). Without the container there is no single place to hang that include, so with B each tier gets its own include (`tier1: !include ...`) and the file holds that one tier: its engine line and its steps. This fits your words that an included tier says itself which engine it is for. Files that hold two tiers today (tier 1 and tier 2) would be split in two.

Default if you say nothing: B. Why: the containers hold nothing else, and B is the shortest.
Your answer frees: the engine change and one rewrite of all recipes and gallery bundles.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engine_keys_shape/QUESTION_tier_container.md
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engine_keys_shape/scout_containers_title_entry.md (question 1)

### 2. Do the gallery examples take the new shape too?

- A: yes, one shape everywhere (one checker, one reader).
- B: no, the gallery keeps its compact form, and the spec says so.

Fact: 34 gallery bundles have one inline `spec:` and `wrangling: {tier1: []}`. A yes changes all 34.

Default if you say nothing: A. Why: one checker and one reader for every recipe.
Your answer frees: the rewrite of the gallery bundles in the same pass.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engine_keys_shape/before_after_gallery_bundle.md

### 3. When a plot is in its own file, what goes into the file?

- A: only the plot content and its label. Taxonomy and description stay in the recipe entry.
- B: everything of the entry: label, description, taxonomy and the plot content.

Fact: the gallery still finds the taxonomy in an included file, because includes are read when the recipe loads.

Default if you say nothing: B. Why: your decision says an include at entry level is the whole entry.
Your answer frees: the layout of every plot file, and the moves into it.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engine_keys_shape/before_after_plot_file.md

### 4. The `title:` line of the plot files

18 plot files have a `title:` line. What happens to it?

- A: keep it.
- B: remove it and write the title in a labels layer.

Fact: today the title is the plot title unless a labels layer sets one. The export uses it as a fallback label. It is not the entry `label`.

Default if you say nothing: A. Why: no picture changes. We look at it again with the rename.
Your answer frees: nothing now. With B, the 18 files change.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engine_keys_shape/scout_containers_title_entry.md (question 2)

### 5. The rename of the plot components

Question (the report's question 4, shortened): For the 15 objects, is the plotnine original the value in its slot, with the layer form kept as a modified component? Yes or no.

Default if you say nothing: yes.
Why it is here: if you answer now, every recipe is rewritten once, not twice. The rename rewrites every recipe too.
Your answer frees: the rename and the value build (two builds).

This one answer is enough to start the rename. The two neighbouring points (how a legend guide is written, and functions given as values) can wait: the report lists them under "can wait", and the demo needs neither.
The report has nine other questions (safety of some plain values, silent defaults, a session zip that overwrites). None blocks a build; they can be taken after part 1.

More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/recipe_arguments/REPORT_for_eve.md

### 6. May the big build start?

Question: May the big build start once questions 1 to 5 are answered?

- A: yes.
- B: no, wait until you have seen everything.

No default: this one needs your word, because the build rewrites every recipe.

What the build contains (all decided by you on 2026-11-17):
1. A plot entry has no `spec:` key. Its content is written in the entry, or in an included file that is the whole entry.
2. A tier is a small block: an optional engine line first, then the list of steps. Tier 3 at the plot gets the same form. Without an engine line, the recipe's engine at the top applies.
3. Every registered action and plot component carries its engine. The checker refuses a step written under another engine's block. Engine names are an open list.
4. The four plot-default keys that do nothing are removed: `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`. Seven recipes lose their font line; each removed value is printed with the recipe name. Pictures stay the same.
5. The stored tables are rebuilt once (the cache version goes from 4 to 5), and the user is told once in one sentence.
6. The export records, per plot and per tier, the engine, its library version and the theme as applied.

How it is built: as ONE change with ONE rewrite of all recipes. The rewrite must be safe to run twice and must print everything it removes. Tests that fail without the change come first. Full controls after the merge.
Built right after it, as its own small step: the fix of Blueprint's plot-defaults form (today it writes the removed keys, drops the seed and the layers, and writes `theme_light`).

More: channel messages M246 to M256 in /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/agent_channel.md

---

## PART 2: Small, one word each

### 7. Named themes: can a lab add a theme without a release?

This is the theme design note. Its seven questions, shortened, this one first.

a. A lab adds a theme:
- A: by putting one file in a folder. No code, no release. (The values are copied into the recipe, so a changed or deleted file changes no result.)
- B: only with a new release, because a theme is code.
Default A.

b. The shipped themes live in one folder; the lab folder is named in the deployment file. Yes or no. Default yes.

c. A theme file holds the base look and font only; every other setting goes into `theme_custom`. Yes or no. Default yes. (See 14 for why.)

d. "Dashboard" and "Publication" leave the code and become theme files. Yes or no. Default yes.

e. Their wrong descriptions are corrected now. The "Dashboard" text says it is the default theme; the default is `theme_bw`. Yes or no. Default yes.

f. Extra settings on the base theme: see question 14.

g. The axis-text override: see question 13.

Your answer frees: the theme folder, the file format, the Blueprint theme list and the copy into a recipe.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/theme_snippets/DESIGN_NOTE_for_eve.md

### 8. `set_sorted` and `search_sorted` in formulas

Question: Refuse `set_sorted` and `search_sorted`? Each gives a wrong result with no message when misused.

- A: refuse both.
- B: keep both.

Default if you say nothing: A. Why: a wrong result with no message is not allowed. The 20 members that the shipped formulas use stay.
Your answer frees: one entry in the formula list. Nothing else.
Not asked here: `shuffle` and `sample` (not reproducible without a seed). The scientist proposes to refuse them or to require a seed.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/allowlist_need/viewpoint_scientist.md

### 9. May a key be a date or true/false?

A key is the field that joins two tables (for example the sample id).

- A: strict. A key is text or a category only. A date or true/false key is refused.
- B: allowed. Dates and true/false keys are allowed, each with its own rules and message.

Fact: a join of a date with text fails. A date written as text joins only when the text is in the same format.

Default if you say nothing: A. Why: a date is safe as a key only in one written form, and the engine does no parsing.
Your answer frees: the wording pass (the words "entity key", with "sample id" only as the example) and the checker's message. Under B: the message changes per type, and audit filter values need type-aware parsing.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/key_types/viewpoint_scientist.md

### 10. The prefix `numpy.` in plot functions

A function such as `numpy.arcsin(x)` is now accepted, as `np.arcsin(x)` is.

- A: keep it accepted.
- B: refuse it, with the message "write np".

Default if you say nothing: A. Why: the formula spec already uses `numpy.` for smoother formulas, so one spelling is shared. Switching to B is one line and one message.
Your answer frees: nothing blocking.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_night/builder_report.md (task 4)

### 11. Types that crash a formula

Three types crash the Polars engine with an error the app does not catch: `pl.Unknown`, `pl.Binary`, and arrays of unknown. They crash in the decoding member `json_decode`. `pl.Object` is already refused.

Question: refuse all three there too?

- A: yes, refuse them.
- B: no, leave them.

Default if you say nothing: A. Why: the same rule as for `pl.Object`. A crash is not a clear message.
Your answer frees: three entries in the refusal list, and a test for each.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_night/security_review.md (finding 2)

### 12. A division through zero

A function such as `1 / x`, over a range that crosses zero, stops the drawing with an error that does not say what is wrong.

What should happen?
- A: a plain message that says what and where, and the plot is not drawn.
- B: leave it as it is.
- C: the bad points are left out silently. Not recommended: it hides data.

Default if you say nothing: A. Why: no silent error is allowed.
Your answer frees: one change in the drawing code and its message.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_night/builder_report.md (open item 1)

### 13. Axis text in the custom theme loses to the automatic adjustment

An axis-text setting written in `theme_custom` is ignored when the labels are long. The app adjusts them automatically. No message is shown. Example: size 14 was set, the figure shows size 8.

What should happen?
- A: `theme_custom` wins for every plot.
- B: the automatic adjustment stays, and `theme_custom` shows a visible message.

Default if you say nothing: B. Why: no picture changes, and the author is told. No default is given in the source; this is reasoned.
Your answer frees: one rule in the theme code. A makes the open test pass; B adds a message.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/themes/review.md (finding 1)

### 14. Extra settings on a named theme

The checker refuses legend position and panel spacing written on a named theme inside a plot (`theme_bw`). The drawing accepts them.

Which side is right?
- A: refuse them, as the checker and plotnine do. Single settings go in `theme_custom`.
- B: accept them, as the drawing does.

Default if you say nothing: A. Why: plotnine refuses them too, and the layout rule puts single settings in `theme_custom`. No default is given in the source; this is reasoned.
Your answer frees: one change, in the checker or in the drawing.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/theme_snippets/DESIGN_NOTE_for_eve.md (section 3 and question 6)

### 15. The rest of the test-setup branch: merge?

Already merged last night, as you released it: the settings block you accepted and the check file as you saw it.
Still waiting for your look: the gallery package init (a docstring, no code), the check file made simpler because of that init (its final text is in the first "More" file, near the end), and the documentation section you approved. The full controls on a trial copy passed.

- A: yes, merge.
- B: no, wait for my look.

Default if you say nothing: A. Why: the controls passed.
Your answer frees: the test that every library folder has its package file; tests in a worker's folder that test that folder's code.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/worktree_imports/builder_report_set.md
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/controls_trial_imports/REPORT.md

### 16. The interpreter path

The rule says the path to the Python that runs the app comes from the deployment file. No code reads that setting. The shipped deployment files hold a relative path that exists only on the developer machine. The Validate check now uses the Python that runs the app.

Change the rule, or build the setting?
- A: change the rule to "the Python that runs the app".
- B: build the setting: the code reads it, and the deployment files get a real value.

Default if you say nothing: A. Why: it is what the code does now, and it does not depend on one machine.
Your answer frees: a rule text change (A), or a build and new deployment values (B).
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/validate/review.md (point 7)

### 17. The gene list: should a step count the blank cells?

A column holds "gene1, gene2, gene3". The three steps below turn it into one row per gene. They work today.

```yaml
- action: polars_str_split
  columns: [genes]
  by: ','
- action: polars_explode
  columns: [genes]
- action: polars_str_strip_chars
  columns: [genes]
```

The order matters: strip after explode. An empty cell becomes one row with a blank gene. A missing cell becomes one row with no gene. Nothing tells the user how many there were.

Question: should a step report how many empty, missing and repeated cells it met?
- A: no, keep the three steps.
- B: yes, build one step that turns a list column into long rows and reports those counts.

Default if you say nothing: A. Why: the three steps work, and no recommendation is given in the source; this is reasoned.
Your answer frees: B: one new step and its tests.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_night/builder_report.md (gene-list part)

### 18. Keep formulas as text, or study other forms?

Decided: formulas stay as text, with a check.

Do you want the other two forms studied further?
- A: no, keep the text.
- B: study a structure in YAML.
- C: study an own small language.

Default if you say nothing: A. Why: a formula in text is one line. The other two need about five to eight lines per formula and many days of work (estimate). B or C would change how recipe authors write formulas, which needs a new decision. A study changes nothing in the app.
Your answer frees: nothing for A. B or C: a study only.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_safety/REPORT_formula_safety.md (sections 0, 3 and 5)

### 19. Should the export collect plot warnings itself?

A warning about a plot (for example: a font is not installed, another is used) is shown in HOME. The export draws its own pictures and collects no warnings. Such a warning reaches the export's list of issues only if the plot was shown in HOME first.

- A: yes, the export collects the warnings of the pictures it draws and writes them into its record.
- B: no, leave it.

Default if you say nothing: A. Why: the export is what gets published; what changed a picture must be recorded with it.
Your answer frees: one change in the export and its test.
More: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/defaults_layers/builder_report.md

### 20. Export pressed right after a tick: the choice can be lost (found in the night; matters for the demo)

What the user sees: you tick "Also include a reproducibility bundle" (or type the bundle label) and press Export within about a second. The download can leave before the server has received the tick. The bundle then has no reproducibility part and the default label, and nothing on screen says so. Measured by the reviewer (`tmpAI/panel/export_box/REVIEW.md` part 2, Playwright, which is faster than a person):
- The time window: with no pause after the last change, the box was lost in 2 of 8 runs and the label in 3 of 8. With a pause of 300 ms or 1000 ms: 0 of 8 for both. In a warm session (repeated export, 24 trials): 1 lost, at 0 ms; 0 lost at 100 ms and more. So the window is under about 300 ms after the last change.
- Who is most likely to meet it: a person who types a bundle label and clicks Export at once (the label is sent at the click, within milliseconds; not measured with a human). The zip file name has the same problem.
- How often it exists: on `dev` 2 of 12 runs failed, on the branch 3 of 12 (alternating runs; the difference is not proven).

This is a second defect, separate from the redraw that is being fixed (the box no longer unticks when you change the plot tab).

- A: next to the box, show what the server holds ("Reproducibility part: will be included"). The user sees a mismatch before pressing Export.
- B: the download itself carries the choices, so it cannot overtake them. Closes the cause; the most work.
- C: only make the test wait. The defect stays for users.
- D (new): the Export button is greyed until the server confirms that it holds the values. The page marks the button at each change; the server answers after it has applied the change; then the button is enabled. Effort: medium. It closes the race for the box and the label. It needs a small local script (no CDN) and a timeout with a message, so that the button does not stay greyed if the answer is lost. The user sees the button grey for about 0.1 s after a change.
- E (tried, does not cure it): the download waits for the server's lock first. 2 of 12 runs still lost.

Default if you say nothing: A now, B later if wanted. Why: A is small and informs the user (no silent result); C hides a defect.
Coordinator to check: A does not close the race. A user who clicks inside the window still gets the defaults, and the line appears only after the click; the default's reason ("the user sees a mismatch before pressing Export") may not hold for a fast click. Default kept, not changed.
First cause: merged on `dev` as `f288dae4` (the panel redraw is fixed). The README of every bundle now says whether the reproducibility part was included, and the plot format.
Also yours to accept or refuse (agent's choices, PROVISIONAL, not decided by Eve):
- when the chosen export scope no longer exists on the open plot tab, the scope is set back to Global and a notice says so;
- a chosen "Active plot" or "Active group" stays selected when the plot tab changes, and follows the open tab.
More: `tmpAI/panel/export_box/builder_report.md`, `REVIEW.md` and `REVIEW_2.md` in the same folder (review finished)

---

## PART 3: Found tonight, for your information (no answer needed)

Merged tonight on the local `dev` branch (not pushed):
- The decisions of the evening are recorded.
- Tests in a worker's folder now test that folder's code, not the main folder's.
- Formulas: `pl.Object` is refused. `pl.element` and `pl.field` are allowed. The names of `stat_function` agree with the drawing.
- Every registered theme draws (17 themes).
- Two silent losses in the custom theme are now refused with a plain message. Example: "Plot 'p', layer 2 (theme_custom): theme_custom setting 'axis_text_x' names the element 'element_texxt', which does not exist (the elements are element_text, element_line, element_rect, element_blank). Fix: write name: element_text."
- Blueprint's Validate no longer depends on a development machine's folder, and it says when it could not run. Example: "The structure check of the recipe could not run, so the recipe was neither passed nor failed (FileNotFoundError ...). Suggestion: check that the app was installed completely ..."

Themes in short:
- Plain values work on a named theme: font family, font size, legend position and direction, panel spacing, plot margin.
- Anything with an element needs `theme_custom`: grid lines, axis text, titles, strip text, backgrounds, legend title. On a named theme it is refused with a message.

Noted, not fixed:
- Validate on a recipe stored outside the app folder fails with the wrong cause ("installation incomplete").
- Blueprint offers only the recipes of the app folder. HOME reads the deployment's location.
- A rule line says join keys are converted to text. The assembler does not convert them; the build stops instead.
- Test Lab uses `sample_id` when the join key field is left empty.

Built, in review with the full controls (merged only if they pass): a warning when a font is not installed ("The font 'X' is not installed on this machine; 'DejaVu Sans' is used instead", with a suggestion; the plot still draws), and the checker now reads the layers written in the plot defaults (a typo there is caught before any plot is drawn).

---

Source of this list: the decisions and channel messages M246 to M256, and the reports under /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/.
