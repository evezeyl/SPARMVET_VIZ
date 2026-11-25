# UML sync builder report 2026-11-18
E1 done: deleted use case "Clone an example into HOME My view (T3 sandbox)" (AAAAAAGht+PND6fcMzw=) and its association; views gone. COM-REACTIVE-GALLERY has no home_state and no clone arrows: unchanged.
E2 done: documentation note + tags on the 3 "Session Management" WFPanels (UI-HOME AAAAAAGht1mBI0wC9sY=, EXPLORATION AAAAAAGhy9T6CWT7EHs=, AUDIT AAAAAAGhy9UwTWX8qSA=). 3 code tags + 3 test tags added; the two target panels also got the session_management_ui code tag. Note is in the (invisible) documentation field because the panels are stacked with no room.
E3 done: attributes session_import.max_zip_mb and session_import.max_unpacked_mb on "Deployment file" (untyped, like the others, no numbers).
E4 done: text changed, test tag + code tag added; path shortened to filter_and_audit_handlers.py:_clear_filters_on_recipe_change (full path is in the code tag) and the node widened (left 345, width 375) so the text fits.
Audit: 8 violations, none from my tags: 5 PKG_EDGE_MISSING, 2 PKG_EDGE_STALE (PKG-TIERS), 1 TEST_BROKEN test_audited_rows_and_drops_are_exported (UMLArtifact).
Note: the audit reads one value per tag name (last wins), so extra same-name tags are only checked for the last; I checked the others by hand: all symbols and files exist.
Diff stat: 455+/700-, mostly StarUML re-serialisation (label widths/heights rounded), not my edits.
Pictures in tmpAI/panel/uml_sync/pictures (after pictures; before for E1, E4).
