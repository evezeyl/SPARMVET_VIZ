# StarUML: how text is shown in a box, and how to keep a diagram readable

Date: 2026-11-26. Status: study (not a decision). Sources are named per fact; "observed" means read from the running StarUML 8.1 (`app.repository`) and not from a document.

## (a) What a box shows

- A box shows: the stereotype (a label, by Stereotype Display), the name, the namespace "(from X)" (Show Namespace), and, when **Show Property** is on, ONE label with all tags and their values (`{status="partial", code="...", ...}`). The **documentation field is never drawn** (observed: the labels of a view are name, namespace, property label only). Source for the options: https://docs.staruml.io/user-guide/formatting-diagram/
- Format menu options that touch text: Change Font (Ctrl+Shift+F), Auto Resize (Ctrl+Shift+R), Word Wrap (Ctrl+Shift+W), Stereotype Display (six modes, Ctrl+Shift+0 to 5: None, Label, Decoration, Decoration with Label, Icon, Icon with Label), Show Visibility / Namespace / Property (Tag, Ctrl+Shift+B) / Type / Multiplicity / Operation Signature, Suppress Attributes / Operations / Receptions / Literals / Columns. Same page.
- Tags: "The Tags can be shown in views by checking Format > Show Property"; a tag can be kept hidden by its `hidden` property. https://docs.staruml.io/working-with-uml-diagrams/class-diagram . The Tag Editor (Model > Tag Editor, Ctrl+T) manages tags; the page does not say anything about drawing them: https://docs.staruml.io/user-guide/user-interface/

## (b) Keep a diagram readable

- Observed: a box is as wide as its widest label. `minWidth` is recomputed only when the diagram is DRAWN (an image request or opening it); until then it is stale. A width set below the true minimum is put back to the minimum at the next draw. So: set the width you want through `app.engine.setProperty(view, 'width', n)` (and `left` to keep the centre), then let one draw confirm it.
- Short name in the box, the detail in documentation (the project's names rule, section (d)). A tag is not a name: do not draw it.
- `app.engine.setAutoResize([views], bool)` and `setStereotypeDisplay` exist in the scripting API: https://docs.staruml.io/developing-extensions/scripting-api/ . Observed: toggling autoResize from a script did not change a width before a draw.
- Layout commands: Format > Layout (Auto, Top to Bottom, Bottom to Top, Left to Right, Right to Left) and Format > Alignment (Align Left/Right/Middle/Top/Bottom/Center) are in https://docs.staruml.io/user-guide/formatting-diagram/ ; script form `app.engine.layoutDiagram(diagram, direction, separations, edgeLineStyle)` (scripting API page). A layout command moves EVERY box of the diagram, so it destroys a hand layout: this project does not use it on a diagram that was arranged by hand (reasoned from what the command does; the project's own rule "never a re-layout" is in `uml_model_plan.md` section 6b).
- Line style (Rectilinear, Oblique, RoundRect, Curve) is a format option of edges, same formatting page.

## (c) Tags on a diagram

- Show Property on = every tag of the element is drawn in one line under the name; the more tags, the wider the box (observed: REQ-CORE components grew from about 400 to 1076 wide when `test` and `counterpart` tags were added).
- Switch it off per view: `app.engine.setProperty(view, 'showProperty', false)`, or Format > Show Property. The tags stay in the model (the audit script reads them from the model; it reads views only to say which diagram shows an element).
- Rule of this project: views of elements that carry tags have Show Property off. Tags show in the Model Explorer and the Tag Editor.

## (d) What this project does

- Names: no line break, at most 45 characters, or tag `longname` with a reason; full text in documentation under "Original box text:". `assets/scripts/audit_uml_model.py` checks it (`uml_model_plan.md` section 6b).
- Changes through `app.engine.setProperty`, never by assigning fields; save with `app.commands.execute('project:save')`.
- Never a picture of REQ-CORE (it hung StarUML twice).

## (e) Not found, open

- The page https://docs.staruml.io/user-guide/formatting-diagram/ gives the names of the options but not their exact effect on size; the scripting API page does not list `wordWrap`, `showProperty`, `suppress*` or `sizeToContent` as documented entries (they exist as fields on the views: observed).
- "What's new" and a few guessed URLs (`/working-with-diagrams/...`, `/whats-new`) returned 404; version 8 differences were not documented in any page I could read.
- Is there a script call that forces a re-measure without a picture? Not found.
